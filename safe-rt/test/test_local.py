import unittest
import os
import json

import pywasm


class TestLocal(unittest.TestCase):

    def setUp(self):
        self.dir = os.path.dirname(os.path.realpath(__file__))

    def test_local_init(self):
        rule = '''  {
                        "local": [{
                            "location": { "function": "main", "name": "hello" },
                            "check_func": "lambda x: x > 0 and x < 256"
                        }]
                    }'''
        rule = json.loads(rule)
        option = pywasm.Option()
        option.user_rule = rule
        module_path = os.path.join(self.dir, 'local.wasm')
        runtime = pywasm.load(module_path, opts=option)
        with self.assertRaisesRegex(Exception, 'hello = 0 in Function main') as cm:
            r = runtime.exec('main', [0,0])
        # print(cm.exception)

    def test_local_store(self):
        rule = '''  {
                        "local": [{
                            "location": { "function": "main", "name": "hello" },
                            "check_func": "lambda x: x >= 0 and x < 99"
                        }]
                    }'''
        rule = json.loads(rule)
        option = pywasm.Option()
        option.user_rule = rule
        module_path = os.path.join(self.dir, 'local.wasm')
        runtime = pywasm.load(module_path, opts=option)
        with self.assertRaisesRegex(Exception, 'hello = 100 in Function main') as cm:
            r = runtime.exec('main', [0,0])
        # print(cm.exception)

if __name__ == '__main__':
    unittest.main()
