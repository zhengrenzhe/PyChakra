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

preferredEncoding = None

def getpreferredencoding():
    global preferredEncoding

    if preferredEncoding is None:
        import locale
        preferredEncoding = locale.getpreferredencoding(False)

    return preferredEncoding


def get_lib_path():
    root = path.dirname(__file__)

    if platform == "darwin":
        return path.join(root, "libs/osx/libChakraCore.dylib")

    if platform.startswith("linux"):
        return path.join(root, "libs/linux/libChakraCore.so")

    if platform == "win32":
        from platform import architecture
        if architecture()[0].startswith("64"):
            return path.join(root, "libs/windows/x64/ChakraCore.dll")
        else:
            return path.join(root, "libs/windows/x86/ChakraCore.dll")

    raise RuntimeError("ChakraCore not support your platform: %s, detail see: https://github.com/Microsoft/ChakraCore",
                       platform)


def point(obj):
    return ctypes.byref(obj)


is_js_variable_name = re.compile(u"""
^
[\$a-zA-Z_][\$\da-zA-Z_]{0,254}
(?:\.[\$a-zA-Z_][\$\da-zA-Z_]{0,254})*
$
""", re.VERBOSE).match


class Runtime:

    __current_runtime = None
    __lock = threading.RLock()

    def _acquire(self):
        if self.__lock:
            self.__lock.acquire()

        self.set_current_runtime(self)

    def _release(self):
        if self.__lock:
            self.__lock.release()

    @classmethod
    def enable_lock(cls):
        if isinstance(cls.__lock, threading.RLock):
            return

        cls.__lock = threading.RLock()

    @classmethod
    def disable_lock(cls):
        if cls.__lock is None:
            return

        lock, cls.__lock = cls.__lock, None
        try:
            lock._release_save()
        except:
            pass

    @classmethod
    def set_current_runtime(cls, runtime):
        if not isinstance(runtime, cls):
            raise TypeError("runtime must be a Runtime object, not %s" % type(runtime).__name__)

        _id = id(runtime)
        if cls.__current_runtime != _id:
            cls.__current_runtime = _id
            runtime.JsSetCurrentContext(runtime.context)

    def __init__(self):
        # load dynamic library
        if platform == "win32":
            self.chakraCore = ctypes.windll[get_lib_path()]
        else:
            self.chakraCore = ctypes.cdll[get_lib_path()]

            # call DllMain manually on non-Windows
            # Attach process
            self.chakraCore.DllMain(0, 1, 0)
            # Attach main thread
            self.chakraCore.DllMain(0, 2, 0)

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

        self.__jsonStringifyArgs = (ctypes.c_void_p * 2)()
        self.__jsonStringifyArgs[0] = undefined

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

    def __check_js_variable_name(self, name):
        name = self.__check_js_string(name)
        if is_js_variable_name(name) is None:
            raise ValueError("variable name illegal: %r" % str(name))
        return name

    def __js_value_to_py_value(self, js_value):
        self.__jsonStringifyArgs[1] = js_value

        # value => json
        result = ctypes.c_void_p()
        err = self.JsCallFunction(self.__jsonStringify, point(self.__jsonStringifyArgs), 2, point(result))

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
        js_string = open(js_file, "rb").read()
        return self.eval(js_string)

    def get_variable(self, name, raw=False):
        name = self.__check_js_variable_name(name)
        ok, result = self.eval(name, raw=raw)
        if ok:
            return result
        return None

    def set_variable(self, name, value):
        name = self.__check_js_variable_name(name)

        if isinstance(value, ctypes.c_void_p) or isinstance(value, tuple) and "c_void_p" in str(value):
            object_name, _, property_name = name.rpartition(u".")

            self._acquire()

            if object_name:
                ok, result = self.eval(object_name, raw=True)
                if ok:
                    result_str = self.__js_value_to_str(result)
                    ok = result_str not in ("undefined", "null")
                    if ok:
                        object = result
                    err_msg = "TypeError: %r is %s, Unable to set property %r of it" % (str(object_name), result_str, str(property_name))
                else:
                    err_msg = result
                if not ok:
                    return False, err_msg

            else:
                object = self.__global

            property_name = property_name.encode("UTF-8")
            propertyId = ctypes.c_void_p()
            err = self.JsCreatePropertyId(property_name, len(property_name), point(propertyId))
            if err == 0:
                err = self.JsSetProperty(object, propertyId, value, 0)

            self._release()

            if err == 0:
                return True, None
            else:
                return False, err_msg

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
