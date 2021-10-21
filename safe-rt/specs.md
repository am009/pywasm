

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

```
"location": { "function": "afunc", "name": "aint" },
```
