struct Context;
int setjmp(Context *context);
void longjmp(Context *context, int value);
int sigsetjmp(Context *context, int value);
void siglongjmp(Context *context, int value);
int my_setjmp(Context *context);
