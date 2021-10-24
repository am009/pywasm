import unittest
import os
import json

import pywasm


class TestUnsigned(unittest.TestCase):
    """
    测试是否能正常判断并解码unsigned的值，通过测试接近上限的数字
    """

    def setUp(self):
        self.dir = os.path.dirname(os.path.realpath(__file__))

    def test_global_init(self):
        rule = '''  {
                        "global": [{
                            "location": { "name": "gc" },
                            "check_func": "lambda x: x == 255"
                        }]
                    }'''
        rule = json.loads(rule)
        option = pywasm.Option()
        option.user_rule = rule
        module_path = os.path.join(self.dir, 'unsigned.wasm')
        # with self.assertRaisesRegex(Exception, r'Variable arrg = \[1, 3, 4, 5, 6, 0, 0, 0, 0, 0\]'):
        runtime = pywasm.load(module_path, opts=option)
        r = runtime.exec('main', [0, 0])

    def test_global_mod(self):
        rule = '''  {
                        "local": [{
                            "location": { "function": "main", "name": "lc" },
                            "check_func": "lambda x: x == 15535 or x == 65535"
                        }]
                    }'''
        rule = json.loads(rule)
        option = pywasm.Option()
        option.user_rule = rule
        module_path = os.path.join(self.dir, 'unsigned.wasm')
        runtime = pywasm.load(module_path, opts=option)
        # with self.assertRaisesRegex(Exception, r'Variable arrg = \[1, 3, 4, 5, 6, 0, 0, 0, 0, 100\]'):
        r = runtime.exec('main', [0, 0])


if __name__ == '__main__':
    unittest.main()
