#include <signal.h>
#include "helpers.h"

void bad_signal() {
  signal(2, nullptr);
}
void near_miss() {
  helper_signal();
}
