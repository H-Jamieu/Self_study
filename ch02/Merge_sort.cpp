#include <iostream>
#include <string>
#include <vector>
using namespace std;

void merge(int p, int q, int r, int AQ[])
{
    
    //length of left and right array
    int n1 = q-p+1;
    int n2 = r-q;

    int L[n1+1]; 
    int R[n2+1];

    //initilize Left and Righet array
    for(int i = 0; i<n1; i++)
    {
        L[i] = AQ[i+p];
    }

    
    for(int i = 0; i<n2; i++)
    {
        R[i] = AQ[i+q+1];
    }

    //Assign inf to value at n+1 position
    L[n1] = 1000000;
    R[n2] = 1000000;

    int i = 0;
    int j = 0;

    for(int k=p; k<r; k++)
    {
        if(L[i] < R[j])
        {
            AQ[k] = L[i];
            i++;
        }
        else
        {
            AQ[k] = R[j];
            j++;
        }
    }

}

void merge_sort(int p1, int q1, int ARR[])
{
    if (q1>p1)
    {
        auto half = p1 + (q1 - p1)/2;
        merge_sort(p1, half, ARR);
        merge_sort(half+1, q1, ARR);
        merge(p1, half, q1, ARR);
    }
    else
        return;
}


int main() 
{
    int A[10] = {3,2,5,7,18,23,52,21,45,68};
    cout<<"Array before sort:"<<endl;

    for (int i = 0; i < 10; i++)
    {
        cout << A[i] << " ";
    }
    cout<<endl;
        
    merge_sort(0,9,A);

    cout<<"Array after sort:"<<endl;
    for (auto x = std::begin(A)-1; x != std::end(A)-1; )
    {
        std::cout <<*++x<< ' ';
    }
    cout<<endl;
}

