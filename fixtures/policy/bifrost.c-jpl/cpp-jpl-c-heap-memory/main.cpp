typedef unsigned long size_t;
void *malloc(size_t);

void init_runtime() {
    (void)malloc(8);
}

void worker() {
    (void)malloc(8);
}

void my_malloc(size_t size) {
    (void)size;
}
