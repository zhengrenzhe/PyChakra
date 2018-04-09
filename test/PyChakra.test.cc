#include "../src/interfaces.h"
#include <iostream>

using namespace std;

int main(){
    auto runtime = CreateRuntime();
    auto context = CreateContext(runtime);
    Eval_JS_File(context, "/Users/droiz/Code/personal/PyChakra/test/thirdparty/react.production.min.js");

    auto res = Eval_JS(context, "(()=>React)();");

    cout << res;

    return 0;
}
