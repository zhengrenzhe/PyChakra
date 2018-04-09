#include "ChakraCore.h"
#include "fail_check.h"
#include <string>

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

char* Eval_JS(JsContextRef* context, const char* script){
    JsValueRef sourceUrl;
    FAIL_CHECK(JsCreateString("kkk", strlen("kkk"), &sourceUrl));

    JsValueRef scriptSource;
    FAIL_CHECK(JsCreateExternalArrayBuffer((void *)script, strlen(script), nullptr, nullptr, &scriptSource));

    JsValueRef result;
    FAIL_CHECK(JsRun(scriptSource, 0, sourceUrl, JsParseScriptAttributeNone, &result));

    JsValueRef resultJSString;
    FAIL_CHECK(JsConvertValueToString(result, &resultJSString));

    char *resultSTR = nullptr;
    size_t stringLength;
    FAIL_CHECK(JsCopyString(resultJSString, nullptr, 0, &stringLength));
    resultSTR = (char*) malloc(stringLength + 1);
    FAIL_CHECK(JsCopyString(resultJSString, resultSTR, stringLength + 1, nullptr));
    resultSTR[stringLength] = 0;

    return resultSTR;
}

char* Eval_JS_File(JsContextRef* context, const char* path){
    int c;
    std::string str;
    FILE* file = fopen(path, "r");
    if (file) {
        while ((c = getc(file)) != EOF)
            str += (char)c;
        fclose(file);
    }

    return Eval_JS(context, str.c_str());
}
