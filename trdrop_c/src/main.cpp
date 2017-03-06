#include "trdrop.h"
#include <iostream>

int main(int argc, char const* argv[])
{
    std::cout << "Hello World from the command line interface of trdrop."
              << '\n';
    trdrop::print_hello_from_lib();
    return 0;
}