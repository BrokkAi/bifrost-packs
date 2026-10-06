#include "helpers.h"

void positive() {
  semBCreate(0, 0);
  taskLock();
}

void near_miss() {
  user_lock();
}
