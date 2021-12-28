# pywasm-safe

通过拓展WebAssembly虚拟机的运行时环境，允许用户对源码中的变量增加额外的约束条件，使得在运行时，程序数据偏离正常范围时能够发出警报，甚至终止程序，以阻止攻击者对程序漏洞的利用。

### 使用

在用户使用时，除了生成的WebAssembly模块，只需要提供对应的规则文件。运行时加载模块时同时加载规则文件，并根据规则做出对应的监控，在模块执行违反规则时及时检测到，并提示用户。

用户首先将需要运行的代码通过编译器编译为WebAssembly模块，编译时需要开启调试信息选项，然后再根据源码中需要监控的变量编写规则文件。

其中动态规则监控的主要功能是支持全局变量和局部变量的监控。全局变量规则的例子：
```
{
    "global": [{  
        "location": { "name": "aint" },  
        "check_func": "lambda x:x>0 and x < 256"  
    }]  
}
```

这个例子中，用户在提供的模块中，使用C语言定义了名为“aint”的全局变量，并想要监控该变量的值，保证运行过程中该变量的值始终在大于0，小于256的范围内。该用户只需要编写上述的规则文件，在“global”对应的规则列表中添加一个规则，并在“location”中给出变量名，在“check_func”对应的字符串中给出对应检查函数的匿名函数表达式，即可实现监控。在真实执行中，用户提供的检查函数将在每次变量被修改时执行，检查返回值是否为“True”。返回值为“False”时即说明规则被违反。

对于局部变量监控功能，一个用户规则文件的实例如下：
```
{
    "local": [{
        "location": { "function": "main", "name": "hello" },
        "check_func": "lambda x:x>0 and x < 256"
    }]
}
```

在这个例子中，用户在C语言生成的二进制WebAssembly模块中包含了“main”函数，定义了名为“hello”的局部变量，并想要监控该变量的值，保证运行过程中该变量的值始终在大于0，小于256的范围内。这个场景对应着上述的规则文件，在“local”对应的规则列表中添加一个规则，并在“location”中给出变量名，在“check_func”对应的字符串中给出对应检查函数的匿名函数表达式，即可实现监控。在真实执行中，用户提供的检查函数将在每次变量被修改时执行，检查返回值是否为“True”。返回值为“False”时即说明规则被违反。

local规则和global规则都可以添加任意多个，同时存在并生效。它们之间并没有互斥关系

### 实现

局部变量监测功能需要在函数初始化栈指针后获取栈指针的值，从而根据偏移得到栈上局部变量的位置。函数开头的初始化部分代码被称为prologue。因此需要通过查看代码和源码的对应表，知道何时函数的prologue执行结束。而对应表中指定指令是通过指令在二进制文件中的偏移得到的，因此在解析文件时就需要对每个指令保存它在源模块中对应的偏移。

WebAssembly模块的内存默认全部初始化为0。WebAssembly模块可以内部的Data段，设置内存的初始内容。在内存初始化后，模块执行前，也可能出现全局变量违反用户定义的规则的情况。这种情况我们也需要捕获。

本次项目考虑到Python语言使用上的方便与实现的便捷性，使用Python语言编写。基于开源的WebAssembly运行时pywasm拓展实现。

由于WebAssembly的设计考量，虽然于传统的二进制可执行文件类似，但指令和数据是分开的，指令并没有映射到内存中，因此运行时也没有类似PC/IP这种指令位置寄存器。DWARF标准作为传统的调试信息标准，内部的数据定位指令时，都是通过指令所在的内存地址定位。为了兼容这一点，WebAssembly的DWARF标准定义当标准中引用到WebAssembly指令的地址时，一律表示为WebAssembly指令在二进制模块文件中Code段内部的偏移。

常规的WebAssembly运行时并不需要与DWARF这种调试信息交互，因此在解析指令时也没有维护与保留相关的偏移信息。因此在已有的运行时基础上，我们需要理解二进制模块解析的相关代码，以做出修改维护保留该信息。首先需要修改指令表示的类，增加一个保存偏移的成员变量。在模块解析时，从Code段解析开始，维护一个偏移值，并在实例化指令对象时保存相关的偏移信息，以便后续DWARF解析模块使用。


### DWARF

DWARF将调试信息组织成树状结构，分为编译单元-函数-参数和局部变量这几个层次，在每个节点上通过节点的属性表示各种信息。此外，它还通过设计虚拟机和指令，压缩表示指令和源码的对应关系，以减小调试信息的空间占用。

由于本项目使用Python语言开发，因此使用了pyelftools开源模块解析DWARF调试信息。

首先，当二进制WebAssembly模块文件被解析，实例化为对应的对象时，同时解析模块内存的DWARF相关数据，构建DWARF调试信息对象，并作为模块对象的成员变量保存。DWARF数据分为多个不同的数据段，封装在WebAssembly模块的“Custom”段中，包括最重要的“.debug_info”段，保存指令和源码位置映射信息的“.debug_line”段，保存模块内指令范围的“.debug_ranges”等等。需要在解析时将它们依次收集起来，封装成Python的BytesIO对象，最终调用pyelftools模块中的DWARFInfo类的构造函数，传入这些信息。

其次，由于用户只在规则文件中给出了变量名，并没有给出变量的类型。该模块需要基于规则文件中的变量名，查询DWARF信息获取对应的变量类型，对应在内存中的大小，保存在内部规则对象中，以便后续模块解析变量时使用。若发现用户自定义规则被违反，在告诉用户规则信息和变量名的同时，可以同时打印变量的值，以便用户对照规则分析问题。此外，为了支持更多样的变量监控功能，还需要支持对数组类型的解析。

该模块还需要提供变量的源码行号的解析功能。也将相关信息保存了内部规则对象中。当执行时，若发现用户自定义规则被违反，在告诉用户规则信息和变量名的同时，可以同时告知用户变量定义所在的位置，以便用户进一步分析问题。

局部变量监测功能需要在函数初始化栈指针后获取栈指针的值，从而根据偏移得到栈上局部变量的位置。每个函数开头的初始化部分代码被称为prologue。一个代码调试器在面对用户对函数下断点的时一般也需要根据调试信息，在函数的prologue结束后的位置下断点。因此调试信息中源码和指令的对应关系表中也包含了这一信息。当函数执行到prologue后时，我们才可以开始检测函数的局部变量是否违反规则，这样才能保证结果的准确性。


### 内部规则

用户自定义的规则在内部模块使用时，会利用调试信息解析子模块将用户规则转换为内部使用的规则格式。一个规则对象的表示：
```
{
    "memory": [{
        "location": [1024, 1028],
        "type": "<DIE>",
        "check_func": "lambda x:x<0 and x<256",
        "info": {
            "name": "aint",
            "decl_file": "xxx.c",
            "decl_line": 4
        }
    }]
}
```

该实例是对于全局变量的监控规则的表示。由于全局变量被放置在全局内存中，在实际执行时只需要监控对应的内存范围是否被修改即可。“location”成员中保存的是需要监控的内存起始地址和结束地址。“type”成员变量中保存的是变量的类型，表示为pyelftools模块中的Debug Info Entry对象，便于之后的变量值解析。“info”成员变量中保存的是变量名，变量所在的文件和行号，便于出现规则违反时利用这些信息生成保存信息。

对于局部变量的监控功能，内部的表示格式与全局变量也并不相同：
```
{
    "watch": [(addr, addr+size, rule)] 
    "prologue": {
        95: ["wasm-local", 2],
        44: ["wasm-local", 3]
    },
    "local": {95: [{
        "location": ["fbreg", 8], # ["local", 8]
        "type": "<DIE>",
        "check_func": "lambda x:x<0 and x<256",
        "info": {
            "function": "func_name1",
            "name": "aint",
            "decl_file": "xxx.c",
            "decl_line": 4
        }
    }]
}
```

虽然局部变量也是保存在内存中，但是它随着函数的创建而产生，分配在函数使用的栈空间上。一个函数的创建，我们只需要监控函数的栈空间分配完成的情况，即prologue结束时的位置，当需要监控的函数执行到prologue结束的位置时，我们此时需要获取函数的栈指针，根据调试信息中局部变量相对于栈指针的偏移，计算出局部变量的内存地址范围，并加入监控中。

因此系统会利用调试信息解析模块，将用户规则进行处理。“prologue”成员变量中保存的是prologue结束的指令偏移到栈指针位置的映射。在这个例子中95是func_name1的prologue结束的指令偏移。当系统发现当前执行的指令偏移是“prologue”成员变量中的某个值时，说明当前已经执行到需要监控的函数，此时恰好取出栈指针所在的位置，并从“local”成员变量中利用指令偏移取出对应的规则列表。计算出需要监控的变量位置时，将变量在内存中的地址区间和对应的规则对象动态加入“watch”成员变量中，此后系统只需要监控“watch”成员变量中的内存位置，当对应的内存位置被修改后，检查规则是否满足。

### 测试框架

本节基于模块的功能，展示了多个使用实例。此外，本系统基于unitest模块实现测试框架，运行实例全部集成在测试框架内，可以通过“python -m unittest”命令一键执行测试用例。

为了方便修改与使用，这里使用了Makefile工具调用Clang编译器将C源码编译为WebAssembly二进制模块文件。当修改源码后只需要直接执行“make”命令即可自动编译更新对应的WebAssembly二进制模块。


=============================================

# pywasm: A WebAssembly interpreter written in pure Python.

[![Build Status](https://travis-ci.org/mohanson/pywasm.svg?branch=master)](https://travis-ci.org/mohanson/pywasm)

A WebAssembly interpreter written in pure Python.

The wasm version currently in use is: [WebAssembly Core Specification, W3C Recommendation, 5 December 2019](https://www.w3.org/TR/wasm-core-1/). Just like Firefox or Chrome does.

# Installation

```sh
$ pip3 install pywasm
```

# Some simple examples

1. First we need a wasm module! Grab our `./examples/fib.wasm` file and save a copy in a new directory on your local machine. Note: `fib.wasm` was compiled from `./examples/fib.c` by [WasmFiddle](https://wasdk.github.io/WasmFiddle/).

2. Now, compile and instantiate WebAssembly modules directly from underlying sources. This is achieved using the `pywasm.load` method.

```py
import pywasm
# pywasm.on_debug()

runtime = pywasm.load('./examples/fib.wasm')
r = runtime.exec('fib', [10])
print(r) # 55
```

A brief description for `./examples`

| File                | Description                                  |
|---------------------|----------------------------------------------|
| ./examples/add.wasm | Export i32.add function                      |
| ./examples/env.wasm | Call python/native function in wasm          |
| ./examples/fib.wasm | Fibonacci, which contains loop and recursion |
| ./examples/str.wasm | Export a function which returns string       |
| ./examples/sum.wasm | Equal difference series summation            |

Of course there are some more complicated examples!

- Zstandard decompression algorithm: [https://github.com/dholth/zstdpy](https://github.com/dholth/zstdpy)
- Run AssemblyScript on pywasm: [https://github.com/mohanson/pywasm_assemblyscript](https://github.com/mohanson/pywasm_assemblyscript)

# Test

```sh
$ python3 ./test/test_spec.py
```

Tested in the following environments:

- Python >= 3.6

# Thanks

- [wagon](https://github.com/go-interpreter/wagon)
- [warpy](https://github.com/kanaka/warpy)

# License

[MIT](./LICENSE)
