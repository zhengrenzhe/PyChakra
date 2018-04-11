# -*- coding: utf-8 -*-

import sys
import ctypes as _ctypes


class ChakraHandle():

    def __init__(self, lib_path):
        chakraCore = _ctypes.CDLL(lib_path)

        runtime = _ctypes.c_void_p()
        chakraCore.JsCreateRuntime(0, 0, point(runtime))

        context = _ctypes.c_void_p()
        chakraCore.JsCreateContext(runtime, point(context))

        chakraCore.JsSetCurrentContext(context)

        if sys.platform != 'win32':
            chakraCore.DllMain(0, 1, 0)
            chakraCore.DllMain(0, 2, 0)

        self.runtime = runtime
        self.context = context
        self.chakraCore = chakraCore

    def eval_js(self, script, source=""):
        chakraCore = self.chakraCore

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
            return(True, js_value_to_str(chakraCore, result))

        # js exception
        elif err == 196609:
            return(False, get_exception(chakraCore))

        # other error
        else:
            return(False, err)

    def eval_js_file(self, path):
        with open(path, 'r') as file:
            data = file.read()
            return self.eval_js(data, path)


def point(any):
    return _ctypes.byref(any)


def get_exception(chakraCore):
    exception = _ctypes.c_void_p()
    chakraCore.JsGetAndClearException(point(exception))

    id = _ctypes.c_void_p()
    chakraCore.JsCreatePropertyId("message", len("message"), point(id))

    value = _ctypes.c_void_p()
    chakraCore.JsGetProperty(exception, id, point(value))

    return js_value_to_str(chakraCore, value)


def js_value_to_str(chakraCore, js_value):
    js_value_ref = _ctypes.c_void_p()
    chakraCore.JsConvertValueToString(js_value, point(js_value_ref))

    str_len = _ctypes.c_size_t()
    chakraCore.JsCopyString(js_value_ref, 0, 0, point(str_len))

    result = _ctypes.create_string_buffer(str_len.value + 1)

    chakraCore.JsCopyString(js_value_ref, point(
        result), str_len.value + 1, 0)

    # pylint: disable=W0612
    resultSTRLastByte = (
        _ctypes.c_char * str_len.value).from_address(_ctypes.addressof(result))
    resultSTRLastByte = '\0'  # noqa: F841

    return result.value
