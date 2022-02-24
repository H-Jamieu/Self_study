#include <iostream>
#include <string>
using namespace std;

int main() 
{
    int a[3] = {0,1,1};
    int b[3] = {0,1,1};
    int c[4] = {0,0,0,0};
    int len = (sizeof(a)/sizeof(*a));
    int step = 0;
    for (int i=len; i>0; i--)
    {
        int res = a[i-1] + b[i-1] + step;
        c[i] = res%2;
        step = min(max(res-1,0),1);
    }
    c[0] = step;
    for (auto x = std::begin(c)-1; x != std::end(c)-1; )
    {
        std::cout <<*++x<< ' ';
    }
    cout<<endl;
}

int min(int a, int b)
{
    if (a < b){
        return a;
    }
    return b;
}

int max(int a, int b)
{
    if (a > b){
        return a;
    }
    return b;
}
