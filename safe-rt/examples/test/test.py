

import pywasm
pywasm.on_debug()
option = pywasm.Option()

debug_info = None

def back_trace(config, target_addr):
    # main -> use_func -> exame
    store = config.store
    parent_conf = config.parent_conf
    parent_frame = parent_conf.frame # use_func
    use_func_sp = parent_frame.local_list[3].i32() # local 3
    print(f"use_func sp: {use_func_sp} {hex(use_func_sp)}")
    # 需要func_sp > target_addr, 小于说明还需要回溯
    assert use_func_sp < target_addr
    parent_conf = parent_conf.parent_conf
    parent_frame = parent_conf.frame
    main_sp = parent_frame.local_list[2].i32() # main DW_AT_frame_base local 2
    assert main_sp < target_addr
    # _start sp
    parent_conf = parent_conf.parent_conf
    parent_frame = parent_conf.frame
    start_sp = parent_conf.store.global_list[0].value.i32() # _start global 0
    assert start_sp < target_addr # global 0 是全局的sp，所以遇到了sp在global的，基本上就是_start函数，可以回到前一个函数了。
    # 回到main函数
    diff = target_addr - main_sp # fbreg + 9

    print("-------------")

    print(target_addr)

def my_load(name: str, imps, opts):
    from pywasm import binary, Runtime
    with open(name, 'rb') as f:
        module = binary.Module.from_reader(f)
        global debug_info
        debug_info = module.dwarf_info
        return Runtime(module, imps, opts)

runtime = my_load('./test.wasm', imps={'wasi_snapshot_preview1': {'proc_exit': lambda w,x:0}, "env":{"exame": back_trace} }, opts=option)
r = runtime.exec('_start', [0,0])
print(r) # 55
