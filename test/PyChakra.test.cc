#include "../src/interfaces.h"
#include <iostream>

int main(){
    auto runtime = CreateRuntime();
    auto context = CreateContext(runtime);

    return 0;
}
