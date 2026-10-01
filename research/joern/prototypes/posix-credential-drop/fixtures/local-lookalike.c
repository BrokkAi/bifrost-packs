/* Analyzer input only. These definitions are local lookalikes, not libc calls. */
static int setgroups(unsigned long count, const void *groups) {
    (void)count;
    (void)groups;
    return 0;
}

static int setgid(unsigned long gid) {
    (void)gid;
    return 0;
}

static int setuid(unsigned long uid) {
    (void)uid;
    return 0;
}

int lookalike_credential_setup(void) {
    if (setgroups(0, 0) != 0) return -1;
    if (setgid(1000) != 0) return -1;
    return setuid(1000);
}
