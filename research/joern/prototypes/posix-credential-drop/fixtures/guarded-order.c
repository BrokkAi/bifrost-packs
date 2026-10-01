/* Analyzer input only. Never execute this credential-changing fixture. */
#include <grp.h>
#include <sys/types.h>
#include <unistd.h>

int drop_guarded(uid_t uid, gid_t gid) {
    if (setgroups(0, (gid_t *)0) == -1) return -1;
    if (setgid(gid) == -1) return -1;
    if (setuid(uid) == -1) return -1;
    return 0;
}
