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
import re
import json
import threading
from os import path
from sys import platform


try:
    unicode
except NameError:
    unicode = str

try:
    bytes
except NameError:
    bytes = str

try:
    _RLock = threading._CRLock
except AttributeError:
    _RLock = threading._RLock

preferredEncoding = None
lib_path = None

def getpreferredencoding():
    global preferredEncoding

    if preferredEncoding is None:
        import locale
        preferredEncoding = locale.getpreferredencoding(False)

    return preferredEncoding


def get_lib_path():
    global lib_path

    if lib_path:
        return lib_path

    else:
        root = path.dirname(__file__)

        if platform == "darwin":
            lib_path = path.join(root, "libs/osx/libChakraCore.dylib")

        elif platform.startswith("linux"):
            lib_path = path.join(root, "libs/linux/libChakraCore.so")

        elif platform == "win32":
            from platform import architecture
            if architecture()[0].startswith("64"):
                lib_path = path.join(root, "libs/windows/x64/ChakraCore.dll")
            else:
                lib_path = path.join(root, "libs/windows/x86/ChakraCore.dll")

        if lib_path:
            return lib_path

    raise RuntimeError("ChakraCore not support your platform: %s, detail see: https://github.com/Microsoft/ChakraCore",
                       platform)


def point(obj):
    return ctypes.byref(obj)


class Runtime:

    def _acquire(self):
        if self._lock:
            self._lock.acquire()
        self.set_current_runtime()

    def _release(self):
        if self._lock:
            self._lock.release()

    def enable_lock(self):
        lock = getattr(self.chakraCore, '_lock', None)
        if isinstance(lock, _RLock):
            return

        self.chakraCore._lock = _RLock()

    def disable_lock(cls):
        lock = getattr(self.chakraCore, '_lock', None)
        if lock is None:
            return

        self.chakraCore._lock = None
        try:
            lock._release_save()
        except:
            pass

    def set_current_runtime(self):
        runtime = id(self)
        if self._current_runtime != runtime:
            self.chakraCore._current_runtime = runtime
            self.JsSetCurrentContext(self.context)

    def __init__(self, threading=False):
        # load dynamic library
        if platform == "win32":
            self.chakraCore = ctypes.windll[get_lib_path()]
        else:
            self.chakraCore = ctypes.cdll[get_lib_path()]

        if not hasattr(self.chakraCore, "_current_runtime"):
            self.chakraCore._current_runtime = None
            self.chakraCore._lock = None

            # call DllMain manually on non-Windows
            if platform != "win32":
                # Attach process
                self.chakraCore.DllMain(0, 1, 0)
                # Attach main thread
                self.chakraCore.DllMain(0, 2, 0)

        # whether to use threading
        if threading:
            # apply enable to all Runtime() which load the same ChakraCore binary
            self.enable_lock()

        # create chakra runtime and context
        self.runtime = ctypes.c_void_p()
        self.JsCreateRuntime(0, 0, point(self.runtime))

        self.context = ctypes.c_void_p()
        self.JsCreateContext(self.runtime, point(self.context))

        # get some references
        self._acquire()

        self.__global = ctypes.c_void_p()
        undefined = ctypes.c_void_p()
        self.JsGetGlobalObject(point(self.__global))
        self.JsGetUndefinedValue(point(undefined))

        self._release()

        # get JSON.stringify reference, and create its called arguments array
        self.__jsonStringify = self.eval("JSON.stringify", raw=True)[1]

        self.__callFunctionArgs = (ctypes.c_void_p * 2)()
        self.__callFunctionArgs[0] = undefined

    def __del__(self):
        self.JsDisposeRuntime(self.runtime)

    def __getattr__(self, name):
        return getattr(self.chakraCore, name)

    def eval(self, js_string, raw=False):
        js_string = self.__check_js_string(js_string)

        self._acquire()

        if platform == "win32":
            js_source = ctypes.c_wchar_p("")
            js_script = ctypes.c_wchar_p(js_string)

            result = ctypes.c_void_p()
            err = self.JsRunScript(js_script, 0, js_source, point(result))

        else:
            js_source = ctypes.c_void_p()
            self.JsCreateString("", 0, point(js_source))

            js_script = ctypes.c_void_p()
            js_string = ctypes.create_string_buffer(js_string.encode("UTF-16"))
            self.JsCreateExternalArrayBuffer(js_string, len(js_string), 0, 0, point(js_script))

            result = ctypes.c_void_p()
            err = self.JsRun(js_script, 0, js_source, 0x02, point(result))

        try:
            # eval success
            if err == 0:
                if raw:
                    return True, result
                else:
                    return self.__js_value_to_py_value(result)

            return self.__get_error(err)

        finally:
            self._release()

    def __check_js_string(self, js_string):
        if not isinstance(js_string, unicode):

            if hasattr(js_string, "tobytes"):
                js_string = js_string.tobytes()

            if isinstance(js_string, (bytes, bytearray)):
                encoding = getpreferredencoding()

                try:
                    js_string = js_string.decode(encoding)
                except UnicodeDecodeError:
                    err = True

                    if encoding != "UTF-8":
                        try:
                            js_string = js_string.decode("UTF-8")
                        except UnicodeDecodeError:
                            pass
                        else:
                            err = False

                    if err:
                        raise

            else:
                raise TypeError("js_string must be a string object, not %s" % type(js_string).__name__)

        return js_string

    def __call_js_function(self, js_function, *js_args):
        js_args_len = len(js_args)

        if js_args_len == 1:
            # the most commonly used
            call_function_args = self.__callFunctionArgs
            call_function_args[1] = js_args[0]
        else:
            call_function_args = (ctypes.c_void_p * (js_args_len + 1))()
            call_function_args[0] = self.__callFunctionArgs[0]
            for n, js_arg in enumerate(js_args):
                call_function_args[n + 1] = js_arg

        result = ctypes.c_void_p()
        err = self.JsCallFunction(js_function, point(call_function_args), 2, point(result))
        call_function_args[1] = None

        return result, err

    def __js_value_to_py_value(self, js_value):
        # value => json
        result, err = self.__call_js_function(self.__jsonStringify, js_value)

        if err == 0:
            result = self.__js_value_to_str(result)
            if result == "undefined":
                result = None
            else:
                # json => value
                result = json.loads(result)
            return True, result

        return self.__get_error(err)

    def eval_file(self, js_file):
        if not hasattr(js_file, "read"):
            js_file = open(js_file, "rb")
        js_string = js_file.read()
        return self.eval(js_string)

    def get_variable(self, name, raw=False):
        ok, result = self.eval(name, raw=raw)
        if ok:
            return result
        return None

    def set_variable(self, name, value):
        name = self.__check_js_string(name)

        if isinstance(value, ctypes.c_void_p) or isinstance(value, tuple) and "c_void_p" in str(value):
            set_variable = self.eval(u"(raw => %s = raw)" % name, raw=True)[1]

            self._acquire()
            _, err = self.__call_js_function(set_variable, value)
            self._release()

            if err == 0:
                return True, None
            else:
                return self.__get_error(err)

        else:
            return self.eval(u"%s = %s" % (name, value))

    def __get_error(self, err):
        # js exception or other error
        if err == 196609:
            err = self.__get_exception()

        return False, err

    def __get_exception(self):
        exception = ctypes.c_void_p()
        self.JsGetAndClearException(point(exception))

        return self.__js_value_to_str(exception)

    def __js_value_to_str(self, js_value):
        js_value_ref = ctypes.c_void_p()
        self.JsConvertValueToString(js_value, point(js_value_ref))

        if platform == "win32":
            result = ctypes.c_wchar_p()
            result_len = ctypes.c_size_t()
            self.JsStringToPointer(js_value_ref, point(result), point(result_len))

            return result.value

        else:
            str_len = ctypes.c_size_t()
            self.JsCopyString(js_value_ref, 0, 0, point(str_len))

            result = ctypes.create_string_buffer(str_len.value)
            self.JsCopyString(js_value_ref, point(result), str_len.value, 0)

            return result.value.decode("UTF-8")
