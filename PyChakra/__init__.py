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
import json
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

        # get JSON.stringify reference, and create its called arguments array
        self.__jsonStringify = self.eval("JSON.stringify", raw=True)[1]

        undefined = ctypes.c_void_p()
        self.chakraCore.JsGetUndefinedValue(point(undefined))

        self.__jsonStringifyArgs = (ctypes.c_void_p * 2)()
        self.__jsonStringifyArgs[0] = undefined

    def __del__(self):
        self.chakraCore.JsDisposeRuntime(self.runtime)

    def eval(self, js_string, raw=False):
        if sys.platform == "win32":
            js_source = ctypes.c_wchar_p("")
            js_script = ctypes.c_wchar_p(js_string)

            result = ctypes.c_void_p()
            err = self.chakraCore.JsRunScript(js_script, 0, js_source, point(result))

        else:
            js_source = ctypes.c_void_p()
            self.chakraCore.JsCreateString("", 0, point(js_source))

            js_script = ctypes.c_void_p()
            js_string = ctypes.create_string_buffer(js_string.encode("UTF-16"))
            self.chakraCore.JsCreateExternalArrayBuffer(js_string, len(js_string), 0, 0, point(js_script))

            result = ctypes.c_void_p()
            err = self.chakraCore.JsRun(js_script, 0, js_source, 0x02, point(result))

        # eval success
        if err == 0:
            if raw:
                return True, result
            else:
                return self.__js_value_to_py_value(result)

        return self.__get_error(err)

    def __js_value_to_py_value(self, js_value):
        self.__jsonStringifyArgs[1] = js_value

        # value => json
        result = ctypes.c_void_p()
        err = self.chakraCore.JsCallFunction(self.__jsonStringify, point(self.__jsonStringifyArgs), 2, point(result))

        if err == 0:
            result = self.__js_value_to_str(result)
            if result == "undefined":
                result = None
            else:
                # json => value
                result = json.loads(result)
            return True, result

        return self.__get_error(err)

    def get_variable(self, name):
        result = self.eval("(() => %s)()" % name)
        if result[0]:
            return result[1]
        return None

    def set_variable(self, name, value):
        return self.eval("var %s = %s" % (name, value))

    def __get_error(self, err):
        # js exception or other error
        if err == 196609:
            err = self.__get_exception()

        return False, err

    def __get_exception(self):
        exception = ctypes.c_void_p()
        self.chakraCore.JsGetAndClearException(point(exception))

        return self.__js_value_to_str(exception)

    def __js_value_to_str(self, js_value):
        js_value_ref = ctypes.c_void_p()
        self.chakraCore.JsConvertValueToString(js_value, point(js_value_ref))

        if sys.platform == "win32":
            result = ctypes.c_wchar_p()
            result_len = ctypes.c_size_t()
            self.chakraCore.JsStringToPointer(js_value_ref, point(result), point(result_len))

            return result.value

        else:
            str_len = ctypes.c_size_t()
            self.chakraCore.JsCopyString(js_value_ref, 0, 0, point(str_len))

            result = ctypes.create_string_buffer(str_len.value)
            self.chakraCore.JsCopyString(js_value_ref, point(result), str_len.value, 0)

            return result.value.decode("UTF-8")
