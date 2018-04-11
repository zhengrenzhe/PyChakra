# -*- coding: utf-8 -*-

#  ___         ___  _           _
# | _ \ _  _  / __|| |_   __ _ | |__ _ _  __ _
# |  _/| || || (__ | ' \ / _` || / /| '_|/ _` |
# |_|   \_, | \___||_||_|\__,_||_\_\|_|  \__,_|
#       |__/

"""
PyChakra is a Python binding to Microsoft Chakra Javascript engine.
"""


from sys import platform
from os import path
import ctypes as _ctypes


class ChakraHandle():

    def __init__(self):

        # load chakra binary
        base_path = path.abspath(path.dirname(__file__))
        lib_name = None

        if platform == "darwin":
            lib_name = "libChakraCore.dylib"
        elif platform.startswith("linux"):
            lib_name = "libChakraCore.so"
        elif platform == "win32":
            lib_name = "ChakraCore.dll"

        if not lib_name:
            raise RuntimeError("not support your platform: %s", platform)

        binary_path = "%s/%s" % (base_path, lib_name)
        if not path.exists(binary_path):
            raise RuntimeError("chakra binary not fount in %s", base_path)

        chakraCore = _ctypes.CDLL(binary_path)

        # create chakra runtime and context
        runtime = _ctypes.c_void_p()
        chakraCore.JsCreateRuntime(0, 0, point(runtime))

        context = _ctypes.c_void_p()
        chakraCore.JsCreateContext(runtime, point(context))

        chakraCore.JsSetCurrentContext(context)

        if platform != 'win32':
            chakraCore.DllMain(0, 1, 0)
            chakraCore.DllMain(0, 2, 0)

        self.__runtime = runtime
        self.__context = context
        self.__chakraCore = chakraCore

    def __del__(self):
        self.__chakraCore.JsDisposeRuntime(self.__runtime)

    def eval_js(self, script, source=""):
        """
            Eval javascript string

            Examples:
                .eval_js("(()=>2)()") // (True, '2')
                .eval_js("(()=>2)()") // (False, "'a' is not defined")

            Parameters:
                script(str): javascript code string
                source(str?): code path (optional)

            Returns:
                (bool, result)
                bool: indicates whether javascript is running successfully.
                result: if bool is True, result is the javascript running
                            return value.
                        if bool is False and result is string, result is the
                            javascript running exception
                        if bool is False and result is number, result is the
                            chakra internal error code
        """

        chakraCore = self.__chakraCore

        js_source = _ctypes.c_void_p()
        chakraCore.JsCreateString(source, len(source), point(js_source))

        js_script = _ctypes.c_void_p()
        script = _ctypes.create_string_buffer(script.encode('UTF-16'))
        chakraCore.JsCreateExternalArrayBuffer(
            script, len(script), 0, 0, point(js_script))

        result = _ctypes.c_void_p()
        err = chakraCore.JsRun(js_script, 0, js_source, 0x02, point(result))

        # no error
        if err == 0:
            return (True, self.__js_value_to_str(result))

        # js exception
        elif err == 196609:
            return (False, self.__get_exception())

        # other error
        else:
            return (False, err)

    def eval_js_file(self, file_path):
        """
            Eval javascript from local file

            Examples:
                .eval_js_file("/Users/test/test.js")

            Parameters:
                script(path): javascript file absolute path

            Returns:
                (bool, result)
                bool: indicates whether javascript is running successfully.
                result: if bool is True, result is the javascript running
                            return value.
                        if bool is False and result is string, result is the
                            javascript running exception
                        if bool is False and result is number, result is the
                            chakra internal error code
        """

        if not path.exists(file_path):
            raise RuntimeError("No such file or directory: %s", file_path)

        with open(file_path, 'r') as file:
            data = file.read()
            return self.eval_js(data, file_path)

    def __get_exception(self):
        exception = _ctypes.c_void_p()
        self.__chakraCore.JsGetAndClearException(point(exception))

        id = _ctypes.c_void_p()
        id_str = "message"
        self.__chakraCore.JsCreatePropertyId(id_str, len(id_str), point(id))

        value = _ctypes.c_void_p()
        self.__chakraCore.JsGetProperty(exception, id, point(value))

        return self.__js_value_to_str(value)

    def __js_value_to_str(self, js_value):
        js_value_ref = _ctypes.c_void_p()
        self.__chakraCore.JsConvertValueToString(js_value, point(js_value_ref))

        str_len = _ctypes.c_size_t()
        self.__chakraCore.JsCopyString(js_value_ref, 0, 0, point(str_len))

        result = _ctypes.create_string_buffer(str_len.value + 1)

        self.__chakraCore.JsCopyString(js_value_ref, point(
            result), str_len.value + 1, 0)

        # pylint: disable=W0612
        last_byte = _ctypes.c_char * str_len.value
        last_byte = last_byte.from_address(_ctypes.addressof(result))
        last_byte = '\0'  # noqa: F841

        return result.value


def point(any):
    return _ctypes.byref(any)
