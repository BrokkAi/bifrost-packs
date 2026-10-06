#include "helpers.h"

void positive(Context *context) {
  setjmp(context);
  longjmp(context, 1);
  sigsetjmp(context, 0);
  siglongjmp(context, 1);
}

void near_miss(Context *context) {
  my_setjmp(context);
}
