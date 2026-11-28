#define _GNU_SOURCE
/* Host containment only. No floating-point computation or native kernel edit. */
#include <errno.h>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/seccomp.h>
#include <stddef.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/prctl.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <sys/xattr.h>
#include <unistd.h>

#if defined(__x86_64__)
#define HOST_ARCH AUDIT_ARCH_X86_64
#elif defined(__aarch64__)
#define HOST_ARCH AUDIT_ARCH_AARCH64
#else
#error Unsupported host architecture
#endif

static void fail(const char *message) { perror(message); _exit(125); }
static unsigned long long number(const char *s) {
    char *end = NULL; errno = 0;
    if (!s[0] || s[0] < '0' || s[0] > '9') { errno = EINVAL; fail("integer argument"); }
    unsigned long long n = strtoull(s, &end, 10);
    if (errno || !end || *end) { errno = EINVAL; fail("integer argument"); }
    return n;
}
static void limit(int which, rlim_t amount) {
    struct rlimit bound = { amount, amount };
    if (setrlimit(which, &bound)) fail("setrlimit");
}
static void no_descendants(void) {
    /* Check architecture, reject x32 on x86-64, reject all creation syscalls. */
    struct sock_filter code[] = {
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, arch)),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, HOST_ARCH, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),
#if defined(__x86_64__)
        BPF_JUMP(BPF_JMP | BPF_JGE | BPF_K, 0x40000000U, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),
#endif
#ifdef __NR_fork
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_fork, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EPERM),
#endif
#ifdef __NR_vfork
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_vfork, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EPERM),
#endif
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_clone, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EPERM),
#ifdef __NR_clone3
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_clone3, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EPERM),
#endif
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW)
    };
    struct sock_fprog program = { (unsigned short)(sizeof(code) / sizeof(code[0])), code };
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)) fail("no_new_privs");
    if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &program)) fail("seccomp_nofork");
}
int main(int argc, char **argv) {
    if (argc < 9 || argv[7][0] != '-' || argv[7][1] != '-' || argv[7][2]) {
        fprintf(stderr, "usage: guarded_exec parent_pid memory_bytes file_bytes cpu_seconds nofork reserved -- absolute_program [args]\n");
        return 125;
    }
    unsigned long long parent = number(argv[1]), memory = number(argv[2]);
    unsigned long long files = number(argv[3]), cpu = number(argv[4]);
    unsigned long long nofork = number(argv[5]), reserved = number(argv[6]);
    if (!parent || parent > INT32_MAX || memory < 16ULL * 1024 * 1024 ||
        !files || !cpu || nofork > 1 || reserved || argv[8][0] != '/') {
        errno = EINVAL; fail("bounded arguments");
    }
    if (prctl(PR_SET_PDEATHSIG, SIGKILL)) fail("PDEATHSIG");
    /* Parent might have died before prctl. Check the explicitly recorded parent. */
    if ((unsigned long long)getppid() != parent) { errno = ESRCH; fail("parent changed"); }
    struct stat st;
    if (stat(argv[8], &st) || !S_ISREG(st.st_mode) || (st.st_mode & (S_ISUID | S_ISGID))) {
        errno = EACCES; fail("ordinary executable required");
    }
    char capability[1];
    ssize_t capabilities = getxattr(argv[8], "security.capability", capability, sizeof(capability));
    if (capabilities >= 0 || errno == ERANGE || (errno != ENODATA && errno != ENOTSUP)) {
        errno = EACCES; fail("file capabilities forbidden");
    }
    limit(RLIMIT_AS, (rlim_t)memory);
    limit(RLIMIT_CORE, 0);
    limit(RLIMIT_FSIZE, (rlim_t)files);
    limit(RLIMIT_CPU, (rlim_t)cpu);
    if (nofork) no_descendants();
    execv(argv[8], argv + 8);
    fail("execv");
}
