#include "../src/interfaces.h"
#include <iostream>

using namespace std;

int main()
{
    // auto runtime = CreateRuntime();
    // auto context = CreateContext(runtime);
    // auto res = Eval_JS_File(context, "/Users/droiz/Code/personal/PyChakra/test/js/es6.js");

    auto cc = ChakraHandle();

    // cc.Eval_JS("(()=>12)()");
    cc.Eval_JS_File("/Users/droiz/Code/personal/PyChakra/test/js/es6.js");

    // if (res) {
    //     cout << res;
    // }

    return 0;
}
