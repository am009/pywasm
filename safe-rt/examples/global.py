import json

with open('global.json', 'rb') as f:
    rule = json.load(f)

print(rule)
check_func = rule['global'][0]['check_func']
check_func = eval(check_func)
print(check_func(12))

import pywasm
# pywasm.on_debug()

runtime = pywasm.load('./global.wasm')
r = runtime.exec('add', [10])
print(r) # 55
