#include "ChakraCore.h"
#include <string>

char* ConvertJsValueRefToStr(JsValueRef *JsStr);

#define FAIL_CHECK(cmd)                                 \
    do                                                  \
    {                                                   \
        JsErrorCode errCode = cmd;                      \
        if (errCode != JsNoError)                       \
        {                                               \
            printf("Error %d at '%s'\n", errCode, #cmd);\
            JsValueRef except; \
            bool hasExcept; \
            JsHasException(&hasExcept); \
            printf("hasExcept: %d %d\n", hasExcept, true); \
            auto clCode = JsGetAndClearException(&except); \
            printf("clCode: %d %d \n", clCode, JsNoError); \
            JsHasException(&hasExcept); \
            printf("hasExcept: %d %d\n", hasExcept, true); \
            JsPropertyIdRef messageName; \
            const char* id = "message"; \
            auto cco = JsCreatePropertyId(id, sizeof(id)-1, &messageName); \
            printf("cco: %d %d \n", cco, JsNoError); \
            JsValueRef messageValue; \
            auto jco = JsGetProperty(except, messageName, &messageValue); \
            printf("jco: %d %d \n", jco, JsNoError); \
            JsValueRef resultJSString; \
            auto cs = JsConvertValueToString(messageValue, &resultJSString); \
            printf("cs %d %d \n", cs, JsNoError); \
            size_t length; \
            auto cpc = JsCopyString(resultJSString, nullptr, 0, &length); \
            printf("cpc: %d %d \n", cpc, JsErrorInvalidArgument); \
            char * RES = (char *)malloc(length+1); \
            auto cpc2 = JsCopyString(resultJSString, RES, length+1, nullptr); \
            RES[length] = 0; \
            printf("cpc2: %d %d \n", cpc2, JsErrorInvalidArgument); \
            printf("Exception: %s", RES); \
            return nullptr;                             \
        }                                               \
    } while(0)

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
    static int ct = 0;

    JsValueRef sourceUrl;
    FAIL_CHECK(JsCreateString("kkk", strlen("kkk"), &sourceUrl));

    JsValueRef scriptSource;
    FAIL_CHECK(JsCreateExternalArrayBuffer((void *)script, strlen(script), nullptr, nullptr, &scriptSource));

    JsValueRef result;
    FAIL_CHECK(JsRun(scriptSource, ct++, sourceUrl, JsParseScriptAttributeNone, &result));

    JsValueRef resultJSString;
    FAIL_CHECK(JsConvertValueToString(result, &resultJSString));

    char *resultSTR = ConvertJsValueRefToStr(&resultJSString);

    return resultSTR;
}

char* ConvertJsValueRefToStr(JsValueRef *JsStr){
    char *resultSTR = nullptr;
    size_t stringLength;
    FAIL_CHECK(JsCopyString(*JsStr, nullptr, 0, &stringLength));
    resultSTR = (char*) malloc(stringLength + 1);
    FAIL_CHECK(JsCopyString(*JsStr, resultSTR, stringLength + 1, nullptr));
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
