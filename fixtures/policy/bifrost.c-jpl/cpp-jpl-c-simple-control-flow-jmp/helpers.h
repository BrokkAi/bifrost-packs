struct Context;
int setjmp(Context *);
void longjmp(Context *, int);
int sigsetjmp(Context *, int);
void siglongjmp(Context *, int);
int my_setjmp(Context *);
