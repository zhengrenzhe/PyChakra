import sys
import os.path
from ctypes import *


chakraCore = CDLL("../binaries/ChakraCore/lib/libChakraCore.dylib")

script = create_string_buffer("(()=>{return b;})()".encode('UTF-16'))
fileName = "sample.js"

runtime = c_void_p()
# Create Javascript Runtime.
chakraCore.JsCreateRuntime(0, 0, byref(runtime))

context = c_void_p()
# Create an execution context.
chakraCore.JsCreateContext(runtime, byref(context))

# Now set the current execution context.
chakraCore.JsSetCurrentContext(context)

fname = c_void_p()
# create JsValueRef from filename
chakraCore.JsCreateString(fileName, len(fileName), byref(fname))

scriptSource = c_void_p()
# Create ArrayBuffer from script source
chakraCore.JsCreateExternalArrayBuffer(
    script, len(script), 0, 0, byref(scriptSource))

jsResult = c_void_p()
# Run the script.
pco = chakraCore.JsRun(scriptSource, 0, fname, 0x02, byref(jsResult))

if pco != 0:
    exception = c_void_p()
    chakraCore.JsGetAndClearException(byref(exception))
    id = c_void_p()
    # idname = c_void_p()
    # create JsValueRef from filename
    # chakraCore.JsCreateString("message", byref(idname))
    chakraCore.JsCreatePropertyId("message", len("message"), byref(id))
    value = c_void_p()
    chakraCore.JsGetProperty(exception, id, byref(value))
    print("CAL")

# Convert script result to String in JavaScript; redundant if script returns a String
resultJSString = c_void_p()
chakraCore.JsConvertValueToString(value, byref(resultJSString))

stringLength = c_size_t()
# Get buffer size needed for the result string
chakraCore.JsCopyString(resultJSString, 0, 0, byref(stringLength))

# buffer is big enough to store the result
resultSTR = create_string_buffer(stringLength.value + 1)

# Get String from JsValueRef
chakraCore.JsCopyString(resultJSString, byref(
    resultSTR), stringLength.value + 1, 0)

# Set `null-ending` to the end
resultSTRLastByte = (
    c_char * stringLength.value).from_address(addressof(resultSTR))
resultSTRLastByte = '\0'

print("Result from ChakraCore: ", resultSTR.value)

# Dispose runtime
chakraCore.JsDisposeRuntime(runtime)
