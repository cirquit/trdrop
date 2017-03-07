#include "catch.hpp"

unsigned int factorial(unsigned int n)
{
    return n <= 1 ? n : factorial(n - 1) * n;
}

TEST_CASE("Factorials are computed correctly", "[factorial]")
{
    REQUIRE(factorial(1) == 1);
    REQUIRE(factorial(2) == 2);
    REQUIRE(factorial(3) == 6);
    SECTION(" fac(6) is serious buisness ")
    {
        REQUIRE(factorial(6) == 720);
    }
}

SCENARIO("Factorials are computed correctly in the bdd style", "[temp]")
{
    GIVEN("A simple example which works")
    {
        int x = 3;
        WHEN("fac(x) is calculated")
        {
            int y = factorial(x);
            THEN("x should be 6")
            {
                REQUIRE(y == 6);
            }
        }
    }
}