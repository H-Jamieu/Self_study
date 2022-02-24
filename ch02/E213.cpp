#include <iostream>
#include <string>
using namespace std;

int main()
{
    string A = "kwjeckjub";
    int idx = 4;
    cout<<"Searching "<<idx<<"th charactor in "<< A << endl;
    int len = A.length();
    if (idx>len)
    {
        cout<<"Find NIL"<<endl;
    }
    else
    {
        cout<<"Find "<<A[idx-1]<<endl;
    }
}