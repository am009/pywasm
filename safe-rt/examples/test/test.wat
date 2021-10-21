(module
  (type (;0;) (func (param i32)))
  (type (;1;) (func))
  (type (;2;) (func (result i32)))
  (type (;3;) (func (param i32 i32) (result i32)))
  (type (;4;) (func (param i32) (result i32)))
  (import "env" "exame" (func $exame (type 0)))
  (import "wasi_snapshot_preview1" "proc_exit" (func $__wasi_proc_exit (type 0)))
  (func $__wasm_call_ctors (type 1)
    call $emscripten_stack_init)
  (func $use_func (type 0) (param i32)
    (local i32 i32 i32 i32 i32 i32 i32 i32)
    global.get 0
    local.set 1
    i32.const 16
    local.set 2
    local.get 1
    local.get 2
    i32.sub
    local.set 3
    local.get 3
    global.set 0
    local.get 3
    local.get 0
    i32.store offset=12
    local.get 3
    i32.load offset=12
    local.set 4
    i32.const 1
    local.set 5
    local.get 4
    local.get 5
    i32.add
    local.set 6
    local.get 6
    call $exame
    i32.const 16
    local.set 7
    local.get 3
    local.get 7
    i32.add
    local.set 8
    local.get 8
    global.set 0
    return)
  (func $__original_main (type 2) (result i32)
    (local i32 i32 i32 i32 i32 i32 i32 i32 i32 i32)
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
    i32.const 0
    local.set 3
    local.get 2
    local.get 3
    i32.store offset=12
    i32.const 8
    local.set 4
    local.get 2
    local.get 4
    i32.add
    local.set 5
    local.get 5
    local.set 6
    local.get 6
    call $use_func
    i32.const 0
    local.set 7
    i32.const 16
    local.set 8
    local.get 2
    local.get 8
    i32.add
    local.set 9
    local.get 9
    global.set 0
    local.get 7
    return)
  (func $main (type 3) (param i32 i32) (result i32)
    (local i32)
    call $__original_main
    local.set 2
    local.get 2
    return)
  (func $_start (type 1)
    block  ;; label = @1
      i32.const 1
      i32.eqz
      br_if 0 (;@1;)
      call $__wasm_call_ctors
    end
    call $__original_main
    call $exit
    unreachable)
  (func $_Exit (type 0) (param i32)
    local.get 0
    call $__wasi_proc_exit
    unreachable)
  (func $libc_exit_fini (type 1)
    (local i32)
    i32.const 0
    local.set 0
    block  ;; label = @1
      i32.const 0
      i32.const 0
      i32.le_u
      br_if 0 (;@1;)
      loop  ;; label = @2
        local.get 0
        i32.const -4
        i32.add
        local.tee 0
        i32.load
        call_indirect (type 1)
        local.get 0
        i32.const 0
        i32.gt_u
        br_if 0 (;@2;)
      end
    end
    call $_fini)
  (func $exit (type 0) (param i32)
    call $_fini
    call $libc_exit_fini
    call $_fini
    local.get 0
    call $_Exit
    unreachable)
  (func $_fini (type 1))
  (func $stackSave (type 2) (result i32)
    global.get 0)
  (func $stackRestore (type 0) (param i32)
    local.get 0
    global.set 0)
  (func $stackAlloc (type 4) (param i32) (result i32)
    (local i32 i32)
    global.get 0
    local.get 0
    i32.sub
    i32.const -16
    i32.and
    local.tee 1
    global.set 0
    local.get 1)
  (func $emscripten_stack_init (type 1)
    i32.const 5243920
    global.set 2
    i32.const 1028
    i32.const 15
    i32.add
    i32.const -16
    i32.and
    global.set 1)
  (func $emscripten_stack_get_free (type 2) (result i32)
    global.get 0
    global.get 1
    i32.sub)
  (func $emscripten_stack_get_end (type 2) (result i32)
    global.get 1)
  (func $__errno_location (type 2) (result i32)
    i32.const 1024)
  (table (;0;) 2 2 funcref)
  (memory (;0;) 256 256)
  (global (;0;) (mut i32) (i32.const 5243920))
  (global (;1;) (mut i32) (i32.const 0))
  (global (;2;) (mut i32) (i32.const 0))
  (export "memory" (memory 0))
  (export "main" (func $main))
  (export "__indirect_function_table" (table 0))
  (export "_start" (func $_start))
  (export "__errno_location" (func $__errno_location))
  (export "stackSave" (func $stackSave))
  (export "stackRestore" (func $stackRestore))
  (export "stackAlloc" (func $stackAlloc))
  (export "emscripten_stack_init" (func $emscripten_stack_init))
  (export "emscripten_stack_get_free" (func $emscripten_stack_get_free))
  (export "emscripten_stack_get_end" (func $emscripten_stack_get_end))
  (elem (;0;) (i32.const 1) func $__wasm_call_ctors))
