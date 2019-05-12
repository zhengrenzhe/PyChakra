# -*- coding: utf-8 -*-
#
#  ___         ___  _           _
# | _ \ _  _  / __|| |_   __ _ | |__ _ _  __ _
# |  _/| || || (__ | ' \ / _` || / /| '_|/ _` |
# |_|   \_, | \___||_||_|\__,_||_\_\|_|  \__,_|
#       |__/
#
# PyChakra is a Python binding to Microsoft Chakra JavaScript engine.


import ctypes
import platform
import sys
from os import path


def get_lib_path():
    root = path.dirname(__file__)

    if sys.platform == "darwin":
        return path.join(root, "libs/osx/libChakraCore.dylib")

    if sys.platform.startswith("linux"):
        return path.join(root, "libs/linux/libChakraCore.so")

    if sys.platform == "win32":
        if platform.architecture()[0].startswith("64"):
            return path.join(root, "libs/windows/x64/ChakraCore.dll")
        else:
            return path.join(root, "libs/windows/x86/ChakraCore.dll")

    raise RuntimeError("ChakraCore not support your platform: %s, detail see: https://github.com/Microsoft/ChakraCore",
                       sys.platform)


def point(obj):
    return ctypes.byref(obj)


class Runtime:

    def __init__(self):
        # load dynamic library
        self.chakraCore = ctypes.CDLL(get_lib_path())

        # create chakra runtime and context
        self.runtime = ctypes.c_void_p()
        self.chakraCore.JsCreateRuntime(0, 0, point(self.runtime))

        self.context = ctypes.c_void_p()
        self.chakraCore.JsCreateContext(self.runtime, point(self.context))

        self.chakraCore.JsSetCurrentContext(self.context)

        # call DllMain manually on non-Windows
        if sys.platform != "win32":
            # Attach process
            self.chakraCore.DllMain(0, 1, 0)
            # Attach main thread
            self.chakraCore.DllMain(0, 2, 0)

    def __del__(self):
        self.chakraCore.JsDisposeRuntime(self.runtime)

    def eval(self, js_string):
        js_source = ctypes.c_void_p()
        self.chakraCore.JsCreateString("", len(""), point(js_source))

        js_script = ctypes.c_void_p()
        js_string = ctypes.create_string_buffer(js_string.encode('UTF-16'))
        self.chakraCore.JsCreateExternalArrayBuffer(js_string, len(js_string), 0, 0, point(js_script))

        result = ctypes.c_void_p()
        err = self.chakraCore.JsRun(js_script, 0, js_source, 0x02, point(result))

        # eval success
        if err == 0:
            return True, self.__js_value_to_str(result)

        # js exception
        elif err == 196609:
            return False, self.__get_exception()

        # other error
        else:
            return False, result

    def get_variable(self, name):
        result = self.eval("(() => %s)()" % name)
        if result[0]:
            return result[1]
        return None

    def set_variable(self, name, value):
        return self.eval("var %s = %s" % (name, value))

    def __get_exception(self):
        exception = ctypes.c_void_p()
        self.chakraCore.JsGetAndClearException(point(exception))

        exception_id = ctypes.c_void_p()
        id_str = b"message"
        self.chakraCore.JsCreatePropertyId(id_str, len(id_str), point(exception_id))

        value = ctypes.c_void_p()
        self.chakraCore.JsGetProperty(exception, exception_id, point(value))

        return self.__js_value_to_str(value)

    def __js_value_to_str(self, js_value):
        js_value_ref = ctypes.c_void_p()
        self.chakraCore.JsConvertValueToString(js_value, point(js_value_ref))

        str_len = ctypes.c_size_t()
        self.chakraCore.JsCopyString(js_value_ref, 0, 0, point(str_len))

        result = ctypes.create_string_buffer(str_len.value + 1)

        self.chakraCore.JsCopyString(js_value_ref, point(result), str_len.value + 1, 0)

        # set last byte as '\0'
        _ = (ctypes.c_char * str_len.value).from_address(ctypes.addressof(result))
        _ = '\0'

        # python 2.X
        if sys.version_info.major == 2:
            return str(result.value)
        else:
            return str(result.value, encoding="utf-8")
