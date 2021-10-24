(module
  (type (;0;) (func))
  (type (;1;) (func (param i32 i32)))
  (type (;2;) (func (result i32)))
  (type (;3;) (func (param i32 i32) (result i32)))
  (func $__wasm_call_ctors (type 0))
  (func $mod (type 1) (param i32 i32)
    (local i32 i32 i32 i32 i32 i32 i32)
    global.get 0
    local.set 2
    i32.const 16
    local.set 3
    local.get 2
    local.get 3
    i32.sub
    local.set 4
    local.get 4
    local.get 0
    i32.store offset=12
    local.get 4
    local.get 1
    i32.store offset=8
    i32.const 100
    local.set 5
    i32.const 0
    local.set 6
    local.get 6
    local.get 5
    i32.store offset=1076
    local.get 4
    i32.load offset=8
    local.set 7
    local.get 4
    i32.load offset=12
    local.set 8
    local.get 8
    local.get 7
    i32.store offset=8
    return)
  (func $__original_main (type 2) (result i32)
    (local i32 i32 i32 i32 i32 i32 i32 i64 i64 i32 i32 i32 i32 i32)
    global.get 0
    local.set 0
    i32.const 16
    local.set 1
    local.get 0
    local.get 1
    i32.sub
    local.set 2
    local.get 2
    global.set 0
    local.get 2
    local.set 3
    i32.const 8
    local.set 4
    local.get 3
    local.get 4
    i32.add
    local.set 5
    i32.const 0
    local.set 6
    local.get 6
    i64.load offset=1032
    local.set 7
    local.get 5
    local.get 7
    i64.store
    local.get 6
    i64.load offset=1024
    local.set 8
    local.get 3
    local.get 8
    i64.store
    local.get 2
    local.set 9
    i32.const 100
    local.set 10
    local.get 9
    local.get 10
    call $mod
    i32.const 0
    local.set 11
    i32.const 16
    local.set 12
    local.get 2
    local.get 12
    i32.add
    local.set 13
    local.get 13
    global.set 0
    local.get 11
    return)
  (func $main (type 3) (param i32 i32) (result i32)
    (local i32)
    call $__original_main
    local.set 2
    local.get 2
    return)
  (memory (;0;) 2)
  (global (;0;) (mut i32) (i32.const 66624))
  (global (;1;) i32 (i32.const 1040))
  (global (;2;) i32 (i32.const 1024))
  (global (;3;) i32 (i32.const 1080))
  (global (;4;) i32 (i32.const 1024))
  (global (;5;) i32 (i32.const 66624))
  (global (;6;) i32 (i32.const 0))
  (global (;7;) i32 (i32.const 1))
  (export "memory" (memory 0))
  (export "__wasm_call_ctors" (func $__wasm_call_ctors))
  (export "mod" (func $mod))
  (export "arrg" (global 1))
  (export "__original_main" (func $__original_main))
  (export "main" (func $main))
  (export "__main_void" (func $__original_main))
  (export "__dso_handle" (global 2))
  (export "__data_end" (global 3))
  (export "__global_base" (global 4))
  (export "__heap_base" (global 5))
  (export "__memory_base" (global 6))
  (export "__table_base" (global 7))
  (data (;0;) (i32.const 1024) "\01\00\00\00\02\00\00\00c\00\00\00\04\00\00\00")
  (data (;1;) (i32.const 1040) "\01\00\00\00\03\00\00\00\04\00\00\00\05\00\00\00\06\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00"))
