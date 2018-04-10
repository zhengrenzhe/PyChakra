#include "Utils.h"
#include <string>

class ChakraHandle {
private:
    JsRuntimeHandle runtime;
    JsContextRef context;
    int callTimes = 0;

public:
    ChakraHandle()
    {
        JsCreateRuntime(JsRuntimeAttributeNone, nullptr, &runtime);
        JsCreateContext(runtime, &context);
        JsSetCurrentContext(context);
    }

    ~ChakraHandle()
    {
        printf("%s\n", "will delete");
    }

    std::unique_ptr<char[]> Eval_JS(const char* script, const char* sourceUrl = "")
    {
        JsValueRef JsSourceUrl;
        JsCreateString(sourceUrl, strlen(sourceUrl), &JsSourceUrl);

        JsValueRef JsScript;
        JsCreateExternalArrayBuffer((void*)script, strlen(script), nullptr, nullptr, &JsScript);

        JsValueRef result;
        JsRun(JsScript, callTimes++, JsSourceUrl, JsParseScriptAttributeNone, &result);

        return JsValueRefToStr(result);
    }

    void Eval_JS_File(const char* path)
    {
        printf("%s\n", path);
    }
};

char* ConvertJsValueRefToStr(JsValueRef* JsStr);

JsRuntimeHandle* CreateRuntime()
{
    static JsRuntimeHandle runtime;

    ErrorCheck(JsCreateRuntime(JsRuntimeAttributeNone, nullptr, &runtime));

    return &runtime;
}

JsContextRef* CreateContext(JsRuntimeHandle* runtime)
{
    static JsContextRef context;

    ErrorCheck(JsCreateContext(*runtime, &context));
    ErrorCheck(JsSetCurrentContext(context));

    return &context;
}

char* Eval_JS(JsContextRef* context, const char* script)
{
    static int ct = 0;

    JsValueRef sourceUrl;
    ErrorCheck(JsCreateString("kkk", strlen("kkk"), &sourceUrl));

    JsValueRef scriptSource;
    ErrorCheck(JsCreateExternalArrayBuffer((void*)script, strlen(script), nullptr,
        nullptr, &scriptSource));

    JsValueRef result;
    ErrorCheck(JsRun(scriptSource, ct++, sourceUrl, JsParseScriptAttributeNone,
        &result));

    JsValueRef resultJSString;
    ErrorCheck(JsConvertValueToString(result, &resultJSString));

    char* resultSTR = ConvertJsValueRefToStr(&resultJSString);

    return resultSTR;
}

char* ConvertJsValueRefToStr(JsValueRef* JsStr)
{
    char* resultSTR = nullptr;
    size_t stringLength;
    ErrorCheck(JsCopyString(*JsStr, nullptr, 0, &stringLength));
    resultSTR = (char*)malloc(stringLength + 1);
    ErrorCheck(JsCopyString(*JsStr, resultSTR, stringLength + 1, nullptr));
    resultSTR[stringLength] = 0;
    return resultSTR;
}

char* Eval_JS_File(JsContextRef* context, const char* path)
{
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
