#include <iostream>
#include <string>
using namespace std;

int main() 
{
    string a = "47987389079739480";
    cout<<"Before sorting: "<<a<<endl;
    int len = a.length();
    for (int i=1; i<len; i++)
    {
        char key = a[i];
        int j = 0;
        while(j<i)
        {
            if (a[j]>key)
            {
                a[i] = a[j];
                a[j] = key;
                key = a[i];
            }
            j++;
        }
    }
    cout<<"After sorting: "<<a<<endl;
}