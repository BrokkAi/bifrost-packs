#include "helper.h"

void init_runtime(void) {
  (void)malloc(8);
}

void runtime_init(void) {
  (void)calloc(1, 8);
}

void worker(void) {
  (void)malloc(8);
  (void)calloc(1, 8);
}

void my_malloc(size_t size) { (void)size; }
