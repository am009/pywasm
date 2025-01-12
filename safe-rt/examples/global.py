import json
import pywasm
# pywasm.on_debug()

# 加载规则文件
with open('example.json', 'rb') as f:
    rule = json.load(f)

# print(rule)
# check_func = rule['global'][0]['check_func']
# check_func = eval(check_func)
# print(check_func(12))

option = pywasm.Option()
option.user_rule = rule
# 加载二进制模块 规则不满足时，此时也可能会报错
runtime = pywasm.load('./example.wasm', opts=option)
try:
    # 执行函数
    r = runtime.exec('mod', [560])
except Exception as e:
    print(e.args[0])
    r = 'error'
print(r) # 55
