

## location

### 全局变量

只指定名字，不指定函数

```json
{
    "global": [{
        "location": { "name": "aint" },
        "check_func": "lambda x:x>0 and x < 256"
    }]
}
```

转换后
```json
{
    "global": [{
        "location": { "memory": 1024 },
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
```json
{
    "memory": [{
        "location": [1024, 1028], // 起始地址，结束地址(不含) 。TODO 通过object类型，表示复杂的范围
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
TODO 是否有global域的全局变量？
```
"location": { "global": 3 }
```

### 局部变量

同时指定名字和函数


```json
{
    "local": [{
        "location": { "function": "main", "name": "hello" },
        "check_func": "lambda x:x>0 and x < 256"
    }]
}
```
转换后：
```json
{
    "prologue": {
        "func_name1": ["wasm-local", 2],
        "funcname2": ["wasm-local", 3]
    },
    "local": {"func_name1": [{
        "location": ["fbreg", 8], // ["local", 8]
        "type": "<DIE>",
        "check_func": "lambda x:x<0 and x<256",
        "info": {
            "function": "func_name1",
            "name": "aint",
            "decl_file": "xxx.c",
            "decl_line": 4
        }
    }],
    "funcname2":[{
        // ...
    }]}
}
```
设计考量：因为直接在指令执行时判断当前函数，方便直接通过`in`判断当前函数是不是在dict内，以及方便取出规则。
prologue每个函数只有一个，而local监控每个函数可能有多个，所以单独拿出来。