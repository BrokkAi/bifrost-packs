#include <locale.h>
#include "helpers.h"

int bad_locale() {
  return setlocale(LC_ALL, "C") != 0;
}
int near_miss() {
  return helper_locale();
}
