

全局变量演示：
加载错误
```sh
python .\wrapper.py .\global\init_error.json .\global\global.wasm
```

执行错误
```
python .\wrapper.py .\global\runtime_error.json .\global\global.wasm
```

局部变量演示：
```
python .\wrapper.py .\local\local.json .\local\local.wasm
```

数组演示：
```
python .\wrapper.py .\array\array.json .\array\array.wasm
```