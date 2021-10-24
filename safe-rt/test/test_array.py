import unittest
import os
import json

import pywasm


class TestArray(unittest.TestCase):

    def setUp(self):
        self.dir = os.path.dirname(os.path.realpath(__file__))

    def test_global_init(self):
        rule = '''  {
                        "global": [{
                            "location": { "name": "arrg" },
                            "check_func": "lambda x: False not in [i%2==1 for i in x]"
                        }]
                    }'''
        rule = json.loads(rule)
        option = pywasm.Option()
        option.user_rule = rule
        module_path = os.path.join(self.dir, 'array.wasm')
        with self.assertRaisesRegex(Exception, r'Variable arrg = \[1, 3, 4, 5, 6, 0, 0, 0, 0, 0\]'):
            runtime = pywasm.load(module_path, opts=option)

    def test_global_mod(self):
        rule = '''  {
                        "global": [{
                            "location": { "name": "arrg" },
                            "check_func": "lambda x: x[9] < 100"
                        }]
                    }'''
        rule = json.loads(rule)
        option = pywasm.Option()
        option.user_rule = rule
        module_path = os.path.join(self.dir, 'array.wasm')
        runtime = pywasm.load(module_path, opts=option)
        with self.assertRaisesRegex(Exception, r'Variable arrg = \[1, 3, 4, 5, 6, 0, 0, 0, 0, 100\]'):
            r = runtime.exec('main', [0, 0])

    def test_local(self):
        rule = '''  {
                        "local": [{
                            "location": { "function": "main", "name": "arr" },
                            "check_func": "lambda x: False not in [i < 100 for i in x]"
                        }]
                    }'''
        rule = json.loads(rule)
        option = pywasm.Option()
        option.user_rule = rule
        module_path = os.path.join(self.dir, 'array.wasm')
        runtime = pywasm.load(module_path, opts=option)
        with self.assertRaisesRegex(Exception, r'Variable arr = \[1, 2, 100, 4\]'):
            r = runtime.exec('main', [0, 0])


if __name__ == '__main__':
    unittest.main()
