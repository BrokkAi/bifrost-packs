#include <stdio.h>
#include "helpers.h"

int bad_stdio() {
  return printf("%s", "x");
}
int near_miss() {
  return helper_output();
}
