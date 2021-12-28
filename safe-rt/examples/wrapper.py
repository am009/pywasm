import json
import pywasm
import sys
# pywasm.on_debug()

# 加载规则文件
with open(sys.argv[1], 'rb') as f:
    rule = json.load(f)

# print(rule)
# check_func = rule['global'][0]['check_func']
# check_func = eval(check_func)
# print(check_func(12))

option = pywasm.Option()
option.user_rule = rule
# 加载二进制模块 规则不满足时，此时也可能会报错
try:
    runtime = pywasm.load(sys.argv[2], opts=option)
except Exception as e:
    print(str(e))
    exit(0)
    raise e
try:
    # 执行函数
    r = runtime.exec('main', [0, 0])
except Exception as e:
    print(e.args[0])
    r = 'error'
print(r) # 55
