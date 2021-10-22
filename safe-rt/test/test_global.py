import unittest
import os
import json

import pywasm


class TestGlobal(unittest.TestCase):

    def setUp(self):
        self.dir = os.path.dirname(os.path.realpath(__file__))

    def test_memory_init(self):
        rule = '''{
                    "global": [{
                        "location": { "name": "b" },
                        "check_func": "lambda x:x>0 and x < 256"
                    }]
                }'''
        rule = json.loads(rule)
        option = pywasm.Option()
        option.user_rule = rule
        with self.assertRaisesRegex(Exception, 'b = 0') as cm:
            pywasm.load('./global.wasm', opts=option)

    def test_memory_store(self):
        rule = '''{
                    "global": [{
                        "location": { "name": "b" },
                        "check_func": "lambda x:x>=0 and x < 256"
                    }]
                }'''
        rule = json.loads(rule)
        option = pywasm.Option()
        option.user_rule = rule
        runtime = pywasm.load('./global.wasm', opts=option)
        with self.assertRaisesRegex(Exception, 'b = 560') as cm:
            r = runtime.exec('mod', [560])


if __name__ == '__main__':
    unittest.main()
