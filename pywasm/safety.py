from typing import Dict, List
from elftools.dwarf.constants import DW_ATE_signed, DW_ATE_signed_char, DW_ATE_unsigned, DW_ATE_unsigned_char, DW_ATE_signed_char
from elftools.dwarf.die import DIE
from elftools.dwarf.dwarfinfo import DWARFInfo
from elftools.dwarf.dwarf_expr import DWARFExprParser, DWARFExprOp


from . import binary
from . import log
from . import num


def convert_user_rule(module: binary.Module, user_rule):

    safe_rule = None
    if user_rule is None:
        return safe_rule
    dwarf_info = module.dwarf_info  # type: DWARFInfo
    if dwarf_info is None:
        raise AssertionError("Cannot use safe rule without module DWARF info.")
    safe_rule = {}

    dwarf_expr_parser = DWARFExprParser(dwarf_info.structs)

    # global
    global_rules = []
    memory_rules = []
    if 'global' in user_rule:
        for elem in user_rule['global']:
            if 'location' not in elem:
                log.fatalln(f"Error: No location in rule: {elem}")
            val_die, type_die, CU = get_global_variable_by_name(
                dwarf_info, elem['location'])
            if val_die is None:
                log.fatalln(
                    f"Error: Unable to find a variable matching location: {elem['location']}")
            # location type check_func info(name, decl_file, decl_line)
            rule = {}
            # info
            line_prog = dwarf_info.line_program_for_CU(CU)
            decl_file_ind = val_die.attributes['DW_AT_decl_file'].value
            decl_file = line_prog['file_entry'][decl_file_ind-1].name
            rule['info'] = {"name": val_die.attributes['DW_AT_name'].value.decode(),
                            "decl_file": decl_file.decode(),
                            "decl_line": val_die.attributes['DW_AT_decl_line'].value, }
            # location
            loc_expr = val_die.attributes['DW_AT_location'].value
            variable_loc = dwarf_expr_parser.parse_expr(loc_expr)
            where, rule['location'] = decode_location(variable_loc, type_die)
            # type
            rule['type'] = type_die
            # check_func
            rule['check_func'] = elem['check_func']
            if where == 'memory':
                memory_rules.append(rule)
            elif where == 'global':
                global_rules.append(rule)
        if len(global_rules) > 0:
            safe_rule['global'] = global_rules
        if len(memory_rules) > 0:
            safe_rule['memory'] = memory_rules

    if 'local' in user_rule:
        local_rules = {}
        prologue_funcs = []  # waited to decode fbreg info
        for elem in user_rule['local']:
            func_name = elem['location']['function']
            func_die, val_die, type_die, CU = get_local_variable_by_name(
                dwarf_info, elem['location'])
            if val_die is None:
                log.fatalln(
                    f"Error: Unable to find a variable matching location: {elem['location']}")

            rule = {}
            line_prog = dwarf_info.line_program_for_CU(CU)
            decl_file_ind = val_die.attributes['DW_AT_decl_file'].value
            decl_file = line_prog['file_entry'][decl_file_ind-1].name
            rule['info'] = {"function": func_name,
                            "name": val_die.attributes['DW_AT_name'].value.decode(),
                            "decl_file": decl_file.decode(),
                            "decl_line": val_die.attributes['DW_AT_decl_line'].value, }
            rule['type'] = type_die
            rule['check_func'] = elem['check_func']
            # location
            loc_expr = val_die.attributes['DW_AT_location'].value
            variable_loc = dwarf_expr_parser.parse_expr(loc_expr)
            where, rule['location'] = decode_location(variable_loc, type_die)
            # decode info in val_die
            prologue_end = get_prologue_end(line_prog, func_die)
            if prologue_end is None:
                log.fatalln(
                    f"Error: Unable to find a prologue_end for function: {func_name}")
            prologue_funcs.append((func_die, prologue_end))
            if prologue_end not in local_rules:
                local_rules[prologue_end] = []
            local_rules[prologue_end].append(rule)
        # decode prologues for prologue_funcs
        prologue_dict = {}
        for func_die, prologue_end in prologue_funcs:
            # func_name = func_die.attributes['DW_AT_name'].value.decode()
            loc_expr = func_die.attributes['DW_AT_frame_base'].value
            variable_loc = parse_dwarf_expr(dwarf_expr_parser, loc_expr)
            assert variable_loc[0].op_name == 'DW_OP_WASM_location'
            assert variable_loc[1].op_name == 'DW_OP_stack_value'
            prologue_dict[prologue_end] = variable_loc[0].args
        safe_rule['prologue'] = prologue_dict
        safe_rule['local'] = local_rules
        safe_rule['watch'] = []
    return safe_rule


def get_prologue_end(lineprog, func_die):
    lowpc = func_die.attributes['DW_AT_low_pc'].value
    highpc = func_die.attributes['DW_AT_high_pc'].value
    for entry in lineprog.get_entries():
        if (state := entry.state) is None:
            continue
        if not (lowpc <= state.address and state.address < highpc):
            continue
        # within function
        if state.prologue_end:
            return state.address
    return None


def get_size_by_type(die: DIE):
    """
    Get size of a DW_AT_type Debug Info Entry.
    Used by decode_var_type to decide if the address points into an variable.
    """
    if die.tag == 'DW_TAG_base_type':
        return die.attributes['DW_AT_byte_size'].value
    elif die.tag in ('DW_TAG_pointer_type', 'DW_TAG_subroutine_type'):
        return 4
    elif die.tag == 'DW_TAG_array_type':
        ele_size = get_size_by_type(die.get_DIE_from_attribute('DW_AT_type'))
        for child in die.iter_children():
            if child.tag == 'DW_TAG_subrange_type':
                ele_count = child.attributes['DW_AT_count'].value
        return ele_size * ele_count
    elif die.tag == 'DW_TAG_typedef':
        return get_size_by_type(die.get_DIE_from_attribute('DW_AT_type'))
    else:
        raise Exception("Unknown type tag: ", die.tag)
        return 4


# used by parse_dwarf_expr
op2name = {0x0: "wasm-local", 0x1: "wasm-global",
           0x2: "wasm-operand-stack", 0x3: "wasm-global"}


def parse_dwarf_expr(dwarf_expr_parser, expr):
    """
    decode variable location expression
    additional support for DW_OP_WASM_location(0xED)
    .. seealso:: https://yurydelendik.github.io/webassembly-dwarf/#DWARF-expressions-and-location-descriptions
    """
    exps = []
    if expr[0] == 0xED:
        exps.append(DWARFExprOp(expr[1], 'DW_OP_WASM_location', [
                    op2name[expr[1]], expr[2]]))  # TODO check wasm-global 0x1 uleb 0x3 u32
        expr = expr[3:]
    exps += dwarf_expr_parser.parse_expr(expr)
    return exps


def decode_location(loc_exprs: List[DWARFExprOp], type_die: DIE):
    """
    decode global variable location.
    """
    var_size = get_size_by_type(type_die)
    for loc in loc_exprs:
        if loc.op_name == 'DW_OP_addr':
            return 'memory', [loc.args[0], loc.args[0] + var_size]
        elif loc.op_name == 'DW_OP_fbreg':
            return 'stack_memory', ['fbreg', loc.args[0]]


def get_global_variable_by_name(dwarf_info: DWARFInfo, loc_info: Dict):
    '''
    find global variable in DWARF info.
    return (variable_die, type_die, CU)
    '''
    if 'name' in loc_info:
        name = loc_info['name']
        for CU in dwarf_info.iter_CUs():  # Compilation Unit
            cu_die = CU.get_top_DIE()
            for die in cu_die.iter_children():
                if die.tag == 'DW_TAG_variable':  # Global Variables
                    variable_name = die.attributes['DW_AT_name'].value
                    if variable_name == name.encode():
                        variable_type = die.get_DIE_from_attribute(
                            'DW_AT_type')
                        return (die, variable_type, CU)
    else:
        log.fatalln(f"Error: unable to decode location entry: {loc_info}")
    return None, None, None


def get_local_variable_by_name(dwarf_info: DWARFInfo, loc_info: Dict):
    '''
    find local variable in DWARF info.
    return (func_die, val_die, type_die, CU)
    '''
    if 'name' in loc_info:
        var_name = loc_info['name']
        func_name = loc_info['function']
        for CU in dwarf_info.iter_CUs():  # Compilation Unit
            cu_die = CU.get_top_DIE()
            for func in cu_die.iter_children():
                if func.tag != 'DW_TAG_subprogram':
                    continue
                for die in func.iter_children():
                    variable_name = die.attributes['DW_AT_name'].value
                    function_name = func.attributes['DW_AT_name'].value
                    if function_name == func_name.encode() and \
                            variable_name == var_name.encode():
                        variable_type = die.get_DIE_from_attribute(
                            'DW_AT_type')
                        return (func, die, variable_type, CU)
    else:
        log.fatalln(f"Error: unable to decode location entry: {loc_info}")
    return None, None, None, None


# ===========Hooks==========

def post_memory_store(user_rule: Dict, memory, addr_begin, addr_end, is_init=False):
    """
    在内存修改后，根据用户规则，检测对应变量是否满足要求。
    内存初始化后调用时，is_init==True，addr_begin和addr_end是任意值（-1）
    """
    if user_rule is None:
        return
    # if range overlap
    for rule in user_rule.get('memory', []):
        # {'info': {}, 'location': [1024, 1028], 'type': DIE, 'check_func': 'lambda'}
        is_overlap = False or is_init
        loc = rule['location']
        if not is_overlap:
            if isinstance(loc, list):
                if loc[0] < addr_end and addr_begin < loc[1]:  # overlap
                    is_overlap = True
            else:
                raise Exception(f"Unimplemented loc decode: {loc}")
        if is_overlap:
            new_val = decode_by_type(rule['type'], memory.data[loc[0]: loc[1]])
            user_func = eval(rule['check_func'])
            if not user_func(new_val):  # check fail
                if is_init:
                    log.println("After Memory initilization: ")
                raise Exception(
                    f'Safe-rt: Runtime rule violation: Variable {rule["info"]["name"]} = {new_val} (defined at {rule["info"]["decl_file"]}:{rule["info"]["decl_line"]}) does not match rule "{rule["check_func"]}"')

    for watch in user_rule.get('watch', []):
        if not(watch[0] < addr_end and addr_begin < watch[1]):  # not overlap
            continue
        data = watch[2]
        new_val = decode_by_type(data['type'], memory.data[watch[0]: watch[1]])
        user_func = eval(data['check_func'])
        if not user_func(new_val):
            raise Exception(
                f'Safe-rt: Runtime rule violation: Variable {data["info"]["name"]} = {new_val} in Function {data["info"]["function"]} (defined at {data["info"]["decl_file"]}:{data["info"]["decl_line"]}) does not match rule "{data["check_func"]}"')


signed_decode = {1: num.LittleEndian.i8, 2: num.LittleEndian.i16,
                 4: num.LittleEndian.i32, 8: num.LittleEndian.i64}
unsigned_decode = {1: num.LittleEndian.u8, 2: num.LittleEndian.u16,
                   4: num.LittleEndian.u32, 8: num.LittleEndian.u64}
encoding2func = {DW_ATE_signed: signed_decode, DW_ATE_unsigned: unsigned_decode,
                 DW_ATE_signed_char: signed_decode, DW_ATE_unsigned_char: unsigned_decode,
                 DW_ATE_signed_char: {1: num.LittleEndian.i8}}


def decode_by_type(type: DIE, data):
    if type.tag == 'DW_TAG_base_type':
        signed, size = (
            type.attributes['DW_AT_encoding'].value, type.attributes['DW_AT_byte_size'].value)
        func = encoding2func[signed][size]
        return func(data)
    elif type.tag == 'DW_TAG_typedef':
        return decode_by_type(type.get_DIE_from_attribute('DW_AT_type'), data)
    # TODO add test
    elif type.tag == 'DW_TAG_pointer_type':
        func = num.LittleEndian.u32
        return func(data)
    elif type.tag == 'DW_TAG_array_type':
        sub_type = type.get_DIE_from_attribute('DW_AT_type')
        for child in type.iter_children():
            if child.tag == 'DW_TAG_subrange_type':
                ele_count = child.attributes['DW_AT_count'].value
        size = len(data)
        assert size % ele_count == 0
        ele_size = size // ele_count
        result = []
        for ind in range(0, size, ele_size):
            val = decode_by_type(sub_type, data[ind:ind+ele_size])
            result.append(val)
        return result
    else:
        raise Exception(f"Unimplemented type decode: {type.tag}")
