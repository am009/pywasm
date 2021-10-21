from typing import Dict, List
from elftools.dwarf.constants import DW_ATE_signed, DW_ATE_signed_char, DW_ATE_unsigned
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
    for elem in user_rule['global']:
        if 'location' not in elem:
            log.fatalln(f"Error: No location in rule: {elem}")
        val_die, type_die, CU = get_global_variable_by_name(
            dwarf_info, elem['location'])
        if val_die is None:
            log.fatalln(
                f"Error: Unable to find a variable matching location: {elem['location']}")
        rule = {}  # location type check_func info(name, decl_file, decl_line)
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
        where, rule['location'] = decode_location_g(variable_loc, type_die)
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

    return safe_rule


def decode_location_g(loc_exprs: List[DWARFExprOp], type_die: DIE):
    """
    decode global variable location.
    """
    if type_die.tag == 'DW_TAG_base_type':
        var_size = type_die.attributes['DW_AT_byte_size'].value
    else:
        raise Exception("Unimplemented")
    for loc in loc_exprs:
        if loc.op_name == 'DW_OP_addr':
            return 'memory', [loc.args[0], loc.args[0] + var_size]


def get_global_variable_by_name(dwarf_info: DWARFInfo, loc_info: Dict):
    '''

    return (location, type, info)
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
        log.fatalln(f"Error: location entry not recognized: {loc_info}")
    return None, None, None


# ===========Hooks==========

def post_memory_store(user_rule: Dict, memory, addr_begin, addr_end, is_init=False):
    """
    在内存修改后，根据用户规则，检测对应变量是否满足要求。
    内存初始化后调用时，is_init==True，addr_begin和addr_end是任意值（-1）
    """
    if user_rule is None:
        return
    # if range overlap
    for rule in user_rule['memory']:
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
            if not user_func(new_val): # check fail
                if is_init:
                    log.println("After Memory initilization: ")
                raise Exception(f'Safe-rt: Runtime rule violation: Variable {rule["info"]["name"]} = {new_val} (defined at {rule["info"]["decl_file"]}:{rule["info"]["decl_line"]}) does not match rule "{rule["check_func"]}"')


signed_decode = {1: num.LittleEndian.i8, 2: num.LittleEndian.i16,
                 4: num.LittleEndian.i32, 8: num.LittleEndian.i64}
unsigned_decode = {1: num.LittleEndian.u8, 2: num.LittleEndian.u16,
                   4: num.LittleEndian.u32, 8: num.LittleEndian.u64}
encoding2func = {DW_ATE_signed: signed_decode, DW_ATE_unsigned: unsigned_decode,
                 DW_ATE_signed_char: {1: num.LittleEndian.i8}}


def decode_by_type(type: DIE, data):
    if type.tag == 'DW_TAG_base_type':
        signed, size = (
            type.attributes['DW_AT_encoding'].value, type.attributes['DW_AT_byte_size'].value)
        func = encoding2func[signed][size]
        num = func(data)
        return num
    else:
        raise Exception(f"Unimplemented type decode: {type.tag}")
