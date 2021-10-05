import os
from io import BytesIO
from wasm import (
    decode_module,
    format_instruction,
    format_lang_type,
    format_mutability,
    SEC_UNK,
    SEC_GLOBAL,
    SEC_ELEMENT,
    SEC_DATA
)
from elftools.dwarf.dwarfinfo import DWARFInfo, DwarfConfig, DebugSectionDescriptor 
from elftools.dwarf.descriptions import describe_form_class

section_names = ('.debug_info', '.debug_aranges', '.debug_abbrev',
                '.debug_str', '.debug_line', '.debug_frame',
                '.debug_loc', '.debug_ranges', '.debug_pubtypes',
                '.debug_pubnames', '.debug_addr', '.debug_str_offsets')

import sys
with open(sys.argv[1], 'rb') as raw:
     raw = raw.read()

data = {i: None for i in section_names}
mod_iter = iter(decode_module(raw))
header, header_data = next(mod_iter) # module header
offset = 8

for cur_sec, cur_sec_data in mod_iter:
    len_dict = cur_sec_data.get_decoder_meta()['lengths']
    size = len_dict['id'] + len_dict['payload_len'] + cur_sec_data.payload_len
    # 在真正的数据之前的size
    name = None
    if cur_sec_data.id == SEC_UNK:
        name = cur_sec_data.name.tobytes().decode()
        print(f"Custom Section: {name}")
        # 是debug info节
        if name in section_names:
            # Custom Section的在payload之前的部分的大小
            payload_header_size = len_dict['id'] + len_dict['payload_len'] + len_dict['name'] + len_dict['name_len']
            stream = BytesIO()
            payload_data = cur_sec_data.payload.tobytes()
            stream.write(payload_data)
            # 'stream name global_offset size address'
            data[name] = DebugSectionDescriptor(stream, name, offset+payload_header_size, len(payload_data), 0)
    else:
        print(f"Section ID: {cur_sec_data.id}")
    
    offset += size

print('\n\n============Decode Start===============')

(debug_info_sec_name, debug_aranges_sec_name, debug_abbrev_sec_name,
    debug_str_sec_name, debug_line_sec_name, debug_frame_sec_name,
    debug_loc_sec_name, debug_ranges_sec_name, debug_pubtypes_name,
    debug_pubnames_name, debug_addr_name, debug_str_offsets_name) = section_names

dwarfinfo = DWARFInfo(config=DwarfConfig(
                    little_endian=True,
                    default_address_size=4,
                    machine_arch='wasm'),
                debug_info_sec=data[debug_info_sec_name],
                debug_aranges_sec=data[debug_aranges_sec_name],
                debug_abbrev_sec=data[debug_abbrev_sec_name],
                debug_frame_sec=data[debug_frame_sec_name],
                eh_frame_sec=None,
                debug_str_sec=data[debug_str_sec_name],
                debug_loc_sec=data[debug_loc_sec_name],
                debug_ranges_sec=data[debug_ranges_sec_name],
                debug_line_sec=data[debug_line_sec_name],
                debug_pubtypes_sec=data[debug_pubtypes_name],
                debug_pubnames_sec=data[debug_pubnames_name],
                # debug_addr_sec=data[debug_addr_name],
                # debug_str_offsets_sec=data[debug_str_offsets_name],
                )


def lpe_filename(line_program, file_index):
    # Retrieving the filename associated with a line program entry
    # involves two levels of indirection: we take the file index from
    # the LPE to grab the file_entry from the line program header,
    # then take the directory index from the file_entry to grab the
    # directory name from the line program header. Finally, we
    # join the (base) filename from the file_entry to the directory
    # name to get the absolute filename.
    lp_header = line_program.header
    file_entries = lp_header["file_entry"]

    # File and directory indices are 1-indexed.
    file_entry = file_entries[file_index - 1]
    dir_index = file_entry["dir_index"]

    # A dir_index of 0 indicates that no absolute directory was recorded during
    # compilation; return just the basename.
    if dir_index == 0:
        return file_entry.name.decode()

    directory = lp_header["include_directory"][dir_index - 1]
    return os.path.join(directory, file_entry.name).decode()

def die_info_rec(die, indent_level='  '):
    """ A recursive function for showing information about a DIE and its
        children.
    """
    print(indent_level + 'DIE tag=%s' % die.tag)
    child_indent = indent_level + '  '
    for child in die.iter_children():
        die_info_rec(child, child_indent)

def pc_info_rec(CU):
    for DIE in CU.iter_DIEs():
        if DIE.tag == 'DW_TAG_subprogram':
            try:
                lowpc = DIE.attributes['DW_AT_low_pc'].value
            except KeyError:
                continue
            highpc_attr = DIE.attributes['DW_AT_high_pc']
            highpc_attr_class = describe_form_class(highpc_attr.form)
            if highpc_attr_class == 'address':
                highpc = highpc_attr.value
            elif highpc_attr_class == 'constant':
                highpc = lowpc + highpc_attr.value
            else:
                print('Error: invalid DW_AT_high_pc class:',
                        highpc_attr_class)
                continue
            print(f'    lowpc: {hex(lowpc)}, highpc: {hex(highpc)}')

def line_pro_rec(CU):
    print('  line program:')
    line_program = dwarfinfo.line_program_for_CU(CU)
    if line_program is None:
        print('  DWARF info is missing a line program for this CU')
        return
    # The line program, when decoded, returns a list of line program
    # entries. Each entry contains a state, which we'll use to build
    # a reverse mapping of filename -> #entries.
    lp_entries = line_program.get_entries()
    for lpe in lp_entries:
        # We skip LPEs that don't have an associated file.
        # This can happen if instructions in the compiled binary
        # don't correspond directly to any original source file.
        if not lpe.state or lpe.state.file == 0:
            continue
        filename = lpe_filename(line_program, lpe.state.file)
        print(f'    offset: {hex(lpe.state.address)}, line: {lpe.state.line}, name: {filename}')

for CU in dwarfinfo.iter_CUs():
    print('Found a compile unit at offset %s, length %s' % (
        CU.cu_offset, CU['unit_length']))
    top_DIE = CU.get_top_DIE()
    print('  Top DIE with tag=%s' % top_DIE.tag)
    # We're interested in the filename...
    print('  name=%s' % top_DIE.get_full_path())

    die_info_rec(top_DIE)
    # continue
    pc_info_rec(CU)
    line_pro_rec(CU)

