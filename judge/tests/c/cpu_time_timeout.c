#include <stdio.h>
int main()
{
    int a = 0;
    int i = 0;
    for(i = 0; i < 9999999999;i++)
    {
        a += i;
    }
    printf("%d", a);
    return 0;
}