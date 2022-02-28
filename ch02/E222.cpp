#include <iostream>
#include <string>
using namespace std;

int main() 
{
    int A[10] = {3,2,5,7,18,23,52,21,45,68};
    cout<<"Array before sort:"<<endl;
    for (auto x = std::begin(A)-1; x != std::end(A)-1; )
    {
        std::cout <<*++x<< ' ';
    }
    cout<<endl;
    for (int j=0; j<9; j++)
    {
        int min = 9999999;
        int mid;
        int i;
        //Assume no numebr will larger than 5 billion
        i = j;
        while(i<10)
        {
            if (min>A[i])
            {
                min = A[i];
                mid = i;
            }
            i++;
        }

        A[mid] = A[j];
        A[j] = min;
    }
    cout<<"Array after sort:"<<endl;
    for (auto x = std::begin(A)-1; x != std::end(A)-1; )
    {
        std::cout <<*++x<< ' ';
    }
    cout<<endl;
}