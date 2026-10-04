#include "helper.h"

void throws_exception() {
  throw 1;
}

void catches_exception() {
  try {
    throws_exception();
  } catch (...) {
  }
}

void no_exception() {
  int value = 0;
  (void)value;
}
