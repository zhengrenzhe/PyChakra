# -*- coding:utf-8 -*-

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(__file__, '../..'))
sys.path.append(ROOT)

from PyChakra import Runtime  # noqa:E402

react = 'test/js/react.production.min.js'
react_domserver = 'test/js/react-dom-server.browser.production.min.js'
es6 = 'test/js/es6.js'

react = os.path.join(ROOT, react)
react_domserver = os.path.join(ROOT, react_domserver)
es6 = os.path.join(ROOT, es6)


class TestPyChakra(unittest.TestCase):

    def chakra(self):
        chakra = Runtime()

        res1 = chakra.eval(open(react).read())
        self.assertEqual(True, res1[0])
        self.assertEqual(None, res1[1])

        res2 = chakra.eval(open(react_domserver).read())
        self.assertEqual(True, res2[0])
        self.assertEqual(None, res2[1])

        res3 = chakra.eval(open(es6).read())
        self.assertEqual(True, res3[0])
        self.assertEqual(
            {u'__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED': {u'ReactCurrentOwner': {u'current': None}},
             u'version': u'16.3.1', u'Children': {}}, res3[1])

        res4 = chakra.eval("typeof ReactDOMServer.renderToStaticMarkup")
        self.assertEqual(True, res4[0])
        self.assertEqual("function", res4[1])

        res5 = chakra.set_variable("foo", "'bar'")
        self.assertEqual(True, res5[0])

        res6 = chakra.get_variable("foo")
        self.assertEqual("bar", res6)

        res7 = chakra.eval("(() => 2)();")
        self.assertEqual(True, res7[0])
        self.assertEqual(2, res7[1])

        res8 = chakra.eval("(() => a)()")
        self.assertEqual(False, res8[0])
        self.assertEqual("ReferenceError: 'a' is not defined", res8[1])


if __name__ == '__main__':
    suite = unittest.TestSuite()

    tests = [TestPyChakra("chakra")]
    suite.addTests(tests)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(len(result.failures))
