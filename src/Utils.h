#pragma once

#include "ChakraCore.h"
#include <memory>
#include <stdio.h>

std::unique_ptr<char[]> JsValueRefToStr(JsValueRef* JsValue);

constexpr const char* ErrorType(JsErrorCode errCode)
{
    switch (errCode) {
    case JsErrorScriptException:
        return "JsErrorScriptException";
    case JsNoError:
        return "JsNoError";
    case JsErrorInvalidArgument:
        return "JsErrorInvalidArgument";
    default:
        return "Other Error";
    }
}

#define ErrorCheck(cmd)                                                                   \
    do {                                                                                  \
        JsErrorCode errCode = cmd;                                                        \
        if (errCode != JsNoError) {                                                       \
            printf("Host Error: %s, at %s:%d\n", ErrorType(errCode), __FILE__, __LINE__); \
            if (errCode == JsErrorScriptException) {                                      \
                                                                                          \
                JsValueRef exception;                                                     \
                JsGetAndClearException(&exception);                                       \
                                                                                          \
                JsPropertyIdRef id;                                                       \
                JsCreatePropertyId("message", sizeof("message") - 1, &id);                \
                                                                                          \
                JsValueRef value;                                                         \
                JsGetProperty(exception, id, &value);                                     \
                                                                                          \
                auto exceptionEsg = JsValueRefToStr(value);                               \
                printf("JS Exception: %s\n", exceptionEsg.get());                         \
            }                                                                             \
            return nullptr;                                                               \
        }                                                                                 \
    } while (0)

std::unique_ptr<char[]> JsValueRefToStr(JsValueRef JsValue)
{
    JsValueRef JsValueString;
    ErrorCheck(JsConvertValueToString(JsValue, &JsValueString));

    size_t strLength;
    // get value size
    ErrorCheck(JsCopyString(JsValueString, nullptr, 0, &strLength));

    auto result = std::make_unique<char[]>(strLength + 1);
    // write actually value
    ErrorCheck(JsCopyString(JsValueString, result.get(), strLength + 1, nullptr));

    result.get()[strLength] = 0;
    return result;
}
