#include "ChakraCore.h"
#include "interfaces.cc"

JsRuntimeHandle* CreateRuntime();
JsContextRef* CreateContext(JsRuntimeHandle*);
char* Eval_JS(JsContextRef*, const char*);
char* Eval_JS_File(JsContextRef*, const char*);
