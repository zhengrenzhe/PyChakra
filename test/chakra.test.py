# -*- coding:utf-8 -*-

import os
import sys

ROOT = os.path.abspath(os.path.join(__file__, '../..'))
sys.path.append(ROOT)

from PyChakra import ChakraHandle  # noqa:E402

ck = ChakraHandle(os.path.join(
    ROOT, 'binaries/ChakraCore/lib/libChakraCore.dylib'))

react_path = os.path.join(ROOT, 'test/js/thirdparty/react.production.min.js')
js_path = os.path.join(ROOT, 'test/js/es6.js')

print(ck.eval_js_file(react_path))
print(ck.eval_js_file(js_path))
