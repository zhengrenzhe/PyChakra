# -*- coding:utf-8 -*-

import sys
from ctypes import CDLL, c_void_p, byref, create_string_buffer, c_size_t, \
    c_char, addressof


class ChakraHandle():

    def __init__(self, lib_path):
        chakraCore = CDLL(lib_path)

        runtime = c_void_p()
        chakraCore.JsCreateRuntime(0, 0, byref(runtime))

        context = c_void_p()
        chakraCore.JsCreateContext(runtime, byref(context))

        chakraCore.JsSetCurrentContext(context)

        if sys.platform != 'win32':
            chakraCore.DllMain(0, 1, 0)
            chakraCore.DllMain(0, 2, 0)

        self.runtime = runtime
        self.context = context
        self.chakraCore = chakraCore

    def eval_js(self, script, source=""):
        chakraCore = self.chakraCore

        js_source = c_void_p()
        chakraCore.JsCreateString(source, len(source), byref(js_source))

        js_script = c_void_p()
        script = create_string_buffer(script.encode('UTF-16'))
        chakraCore.JsCreateExternalArrayBuffer(
            script, len(script), 0, 0, byref(js_script))

        result = c_void_p()
        err = chakraCore.JsRun(js_script, 0, js_source, 0x02, byref(result))

        if err == 0:
            return(True, js_value_to_str(chakraCore, result))

        # js exception
        elif err == 196609:
            return(False, get_exception(chakraCore))

        else:
            return(False, err)

    def eval_js_file(self, path):
        with open(path, 'r') as file:
            data = file.read()
            return self.eval_js(data, path)


def get_exception(chakraCore):
    exception = c_void_p()
    chakraCore.JsGetAndClearException(byref(exception))

    id = c_void_p()
    chakraCore.JsCreatePropertyId("message", len("message"), byref(id))

    value = c_void_p()
    chakraCore.JsGetProperty(exception, id, byref(value))

    return js_value_to_str(chakraCore, value)


def js_value_to_str(chakraCore, js_value):
    js_value_ref = c_void_p()
    chakraCore.JsConvertValueToString(js_value, byref(js_value_ref))

    str_len = c_size_t()
    chakraCore.JsCopyString(js_value_ref, 0, 0, byref(str_len))

    result = create_string_buffer(str_len.value + 1)

    chakraCore.JsCopyString(js_value_ref, byref(
        result), str_len.value + 1, 0)

    # pylint: disable=W0612
    resultSTRLastByte = (
        c_char * str_len.value).from_address(addressof(result))
    resultSTRLastByte = '\0'  # noqa: F841

    return result.value
