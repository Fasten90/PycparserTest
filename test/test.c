#include "stdio.h"


int my_test_func(int var1, int var2)
{
	int result = 0;
	
	if (var2 != 0)
	{
		result = var1/var2;
	}
	
	return result;
}

int main(void)
{
	int var = 5;
	
	/* In first test, pycparser will die on va_args at printf() */
	printf("Print variable value: %d\r\n", var);
	
	int var2 = 2;
	
	int var3 = var / var2;
	
	int var4 = my_test_func(var3, 15);
	
	return var4;
}
