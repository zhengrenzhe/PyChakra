# -*- coding:utf-8 -*-

import os
import sys

sys.path.append(os.path.abspath(
    os.path.join(os.path.abspath(__file__), '../..')))

from src.chakra import ChakraHandle  # noqa: E402

ck = ChakraHandle("../binaries/ChakraCore/lib/libChakraCore.dylib")

print(ck.eval_js_file(os.path.abspath(os.path.join(
    'test/js/thirdparty/react.production.min.js'))))
print(ck.eval_js_file(os.path.abspath(os.path.join('test/js/es6.js'))))
