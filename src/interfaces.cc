#include "ChakraCore.h"
#include "fail_check.h"

JsRuntimeHandle* CreateRuntime(){
    static JsRuntimeHandle runtime;

    FAIL_CHECK(JsCreateRuntime(JsRuntimeAttributeNone, nullptr, &runtime));

    return &runtime;
}

JsContextRef* CreateContext(JsRuntimeHandle* runtime){
    static JsContextRef context;

    FAIL_CHECK(JsCreateContext(*runtime, &context));
    FAIL_CHECK(JsSetCurrentContext(context));

    return &context;
}


// int main()
// {
//     JsRuntimeHandle runtime;
//     JsContextRef context;
//     JsValueRef result;
//     unsigned currentSourceContext = 0;

//     // Your script; try replace hello-world with something else
//     const char* script = "(()=>{return Date.now();})()";

//     // Create a runtime.
//     FAIL_CHECK(JsCreateRuntime(JsRuntimeAttributeNone, nullptr, &runtime));

//     // Create an execution context.
//     FAIL_CHECK(JsCreateContext(runtime, &context));

//     // Now set the current execution context.
//     FAIL_CHECK(JsSetCurrentContext(context));

//     JsValueRef fname;
//     FAIL_CHECK(JsCreateString("sample", strlen("sample"), &fname));

//     JsValueRef scriptSource;
//     FAIL_CHECK(JsCreateExternalArrayBuffer((void*)script, (unsigned int)strlen(script),
//         nullptr, nullptr, &scriptSource));
//     // Run the script.
//     FAIL_CHECK(JsRun(scriptSource, currentSourceContext++, fname, JsParseScriptAttributeNone, &result));

//     // Convert your script result to String in JavaScript; redundant if your script returns a String
//     JsValueRef resultJSString;
//     FAIL_CHECK(JsConvertValueToString(result, &resultJSString));

//     // Project script result back to C++.
//     char *resultSTR = nullptr;
//     size_t stringLength;
//     FAIL_CHECK(JsCopyString(resultJSString, nullptr, 0, &stringLength));
//     resultSTR = (char*) malloc(stringLength + 1);
//     FAIL_CHECK(JsCopyString(resultJSString, resultSTR, stringLength + 1, nullptr));
//     resultSTR[stringLength] = 0;

//     printf("Result -> %s \n", resultSTR);
//     free(resultSTR);

//     // Dispose runtime
//     FAIL_CHECK(JsSetCurrentContext(JS_INVALID_REFERENCE));
//     FAIL_CHECK(JsDisposeRuntime(runtime));

//     return 0;
// }
