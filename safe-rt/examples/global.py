import json

with open('global.json', 'rb') as f:
    rule = json.load(f)

print(rule)
check_func = rule['global'][0]['check_func']
check_func = eval(check_func)
print(check_func(12))

import pywasm
# pywasm.on_debug()
option = pywasm.Option()
option.user_rule = rule
runtime = pywasm.load('./global.wasm', opts=option)
try:
    r = runtime.exec('mod', [560])
except Exception as e:
    print(e.args[0])
    r = 'error'
print(r) # 55
