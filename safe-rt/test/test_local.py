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
        runtime = pywasm.load('./local.wasm', opts=option)
        with self.assertRaisesRegex(Exception, 'hello = 0') as cm:
            r = runtime.exec('main', [])

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
        runtime = pywasm.load('./local.wasm', opts=option)
        with self.assertRaisesRegex(Exception, 'hello = 100') as cm:
            r = runtime.exec('main', [])


if __name__ == '__main__':
    unittest.main()
