# -*- coding:utf-8 -*-

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(__file__, '../..'))
sys.path.append(ROOT)

from PyChakra import ChakraHandle  # noqa:E402

react = 'test/js/react.production.min.js'
react_domserver = 'test/js/react-dom-server.browser.production.min.js'
es6 = 'test/js/es6.js'

react = os.path.join(ROOT, react)
react_domserver = os.path.join(ROOT, react_domserver)
es6 = os.path.join(ROOT, es6)


class TestPyChakra(unittest.TestCase):

    def chakra(self):
        chakra = ChakraHandle()

        res1 = chakra.eval_js_file(react)
        self.assertEqual(True, res1[0])
        self.assertEqual("undefined", res1[1])

        res2 = chakra.eval_js_file(react_domserver)
        self.assertEqual(True, res2[0])
        self.assertEqual("undefined", res2[1])

        res3 = chakra.eval_js_file(es6)
        self.assertEqual(True, res3[0])
        self.assertEqual("[object Object]", res3[1])

        res4 = chakra.eval_js("typeof ReactDOMServer.renderToStaticMarkup")
        self.assertEqual(True, res4[0])
        self.assertEqual("function", res4[1])


if __name__ == '__main__':
    suite = unittest.TestSuite()

    tests = [TestPyChakra("chakra")]
    suite.addTests(tests)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(not result)
