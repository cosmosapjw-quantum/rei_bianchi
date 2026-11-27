#define _GNU_SOURCE
#define _POSIX_C_SOURCE 200809L
#include "worker_spawn.h"
#include <errno.h>
#include <signal.h>
#include <spawn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

extern char **environ;
static volatile sig_atomic_t interrupted;
static void signal_note(int sig) { interrupted = sig; }

static int absolute_regular(const char *path, int executable) {
    struct stat st;
    return path && path[0] == '/' && strnlen(path, 4097) <= 4096 &&
        stat(path, &st) == 0 && S_ISREG(st.st_mode) &&
        access(path, executable ? X_OK : R_OK) == 0;
}

static int filtered(const char *s) {
    const char *prefix[] = {"OMPI_", "PMI_", "PMIX_", "MPI_", "MPICH_", "I_MPI_", "HYDRA_", NULL};
    const char *names[] = {"OMP_NUM_THREADS=", "OMP_THREAD_LIMIT=", "OPENBLAS_NUM_THREADS=",
        "MKL_NUM_THREADS=", "MKL_DYNAMIC=", "NUMEXPR_NUM_THREADS=", "VECLIB_MAXIMUM_THREADS=",
        "BLIS_NUM_THREADS=", "GOTO_NUM_THREADS=", NULL};
    for (int i = 0; prefix[i]; ++i) if (!strncmp(s, prefix[i], strlen(prefix[i]))) return 1;
    for (int i = 0; names[i]; ++i) if (!strncmp(s, names[i], strlen(names[i]))) return 1;
    return 0;
}

static void free_environment(char **env) {
    if (env) { for (size_t i = 0; env[i]; ++i) free(env[i]); free(env); }
}

static char **child_environment(void) {
    const char *fixed[] = {"OMP_NUM_THREADS=1", "OMP_THREAD_LIMIT=1", "OPENBLAS_NUM_THREADS=1",
        "MKL_NUM_THREADS=1", "MKL_DYNAMIC=FALSE", "NUMEXPR_NUM_THREADS=1",
        "VECLIB_MAXIMUM_THREADS=1", "BLIS_NUM_THREADS=1", "GOTO_NUM_THREADS=1", NULL};
    size_t n = 0, bytes = 0, used = 0;
    for (; environ[n]; ++n) {
        size_t length = strnlen(environ[n], 65537);
        if (n >= 4096 || length > 65536 || bytes + length > 1048576) return NULL;
        bytes += length;
    }
    char **out = calloc(n + 10, sizeof(*out));
    if (!out) return NULL;
    for (size_t i = 0; i < n; ++i) if (!filtered(environ[i])) {
        out[used] = strdup(environ[i]);
        if (!out[used++]) { free_environment(out); return NULL; }
    }
    for (size_t i = 0; fixed[i]; ++i) {
        out[used] = strdup(fixed[i]);
        if (!out[used++]) { free_environment(out); return NULL; }
    }
    return out;
}

static double monotonic_seconds(void) {
    struct timespec now;
    if (clock_gettime(CLOCK_MONOTONIC, &now)) return -1;
    return (double)now.tv_sec + (double)now.tv_nsec / 1000000000.0;
}

static int reap_blocking(pid_t pid, int *status) {
    pid_t answer;
    do { answer = waitpid(pid, status, 0); } while (answer == -1 && errno == EINTR);
    return answer == pid ? 0 : -1;
}

int ncp64_run_worker(const char *python, const char *worker, const char *manifest,
                     int task_index, int timeout_seconds) {
    if (!absolute_regular(python, 1) || !absolute_regular(worker, 0) ||
        !absolute_regular(manifest, 0) || task_index < 0 || task_index >= 100000 ||
        timeout_seconds < 1 || timeout_seconds > 86410) return 1100;
    char index[32];
    if (snprintf(index, sizeof(index), "%d", task_index) < 0) return 1100;
    char *argv[] = {(char *)python, (char *)worker, "--manifest", (char *)manifest,
                    "--task-index", index, NULL};
    char **env = child_environment();
    if (!env) return 1101;
    posix_spawnattr_t attr;
    if (posix_spawnattr_init(&attr)) { free_environment(env); return 1102; }
    posix_spawn_file_actions_t actions;
    if (posix_spawn_file_actions_init(&actions)) {
        posix_spawnattr_destroy(&attr); free_environment(env); return 1102;
    }
    sigset_t empty, defaults;
    sigemptyset(&empty); sigemptyset(&defaults);
    sigaddset(&defaults, SIGTERM); sigaddset(&defaults, SIGINT);
    /* GNU/Linux glibc >=2.34: do not pass MPI sockets or unrelated descriptors. */
    int error = posix_spawn_file_actions_addclosefrom_np(&actions, 3);
    if (!error) error = posix_spawnattr_setsigmask(&attr, &empty);
    if (!error) error = posix_spawnattr_setsigdefault(&attr, &defaults);
    if (!error) error = posix_spawnattr_setpgroup(&attr, 0);
    if (!error) error = posix_spawnattr_setflags(&attr,
        POSIX_SPAWN_SETPGROUP | POSIX_SPAWN_SETSIGMASK | POSIX_SPAWN_SETSIGDEF);
    struct sigaction action, old_term, old_int;
    memset(&action, 0, sizeof(action)); action.sa_handler = signal_note;
    sigemptyset(&action.sa_mask); interrupted = 0;
    int term_set = 0, int_set = 0;
    if (!error) { error = sigaction(SIGTERM, &action, &old_term); term_set = !error; }
    if (!error) { error = sigaction(SIGINT, &action, &old_int); int_set = !error; }
    pid_t pid = -1;
    double start = monotonic_seconds();
    if (start < 0) error = EIO;
    if (!error) error = posix_spawn(&pid, python, &actions, &attr, argv, env);
    posix_spawn_file_actions_destroy(&actions);
    posix_spawnattr_destroy(&attr); free_environment(env);
    int answer = 1103, status = 0;
    if (error) fprintf(stderr, "ncp64 spawn/setup refused: %d\n", error);
    else {
        double terminating_at = -1;
        int stop_status = 0;
        for (;;) {
            pid_t got = waitpid(pid, &status, WNOHANG);
            if (got == pid) {
                answer = stop_status ? stop_status : WIFEXITED(status) ? WEXITSTATUS(status) :
                    WIFSIGNALED(status) ? 128 + WTERMSIG(status) : 1104;
                break;
            }
            if (got < 0 && errno != EINTR) {
                kill(-pid, SIGKILL); (void)reap_blocking(pid, &status); answer = 1104; break;
            }
            double now = monotonic_seconds();
            if (now < 0) {
                kill(-pid, SIGTERM); kill(-pid, SIGKILL);
                (void)reap_blocking(pid, &status); answer = 1105; break;
            }
            if (terminating_at < 0 && (interrupted || now - start >= timeout_seconds)) {
                stop_status = interrupted ? 128 + interrupted : 124;
                kill(-pid, SIGTERM); terminating_at = now;
            }
            if (terminating_at >= 0 && now - terminating_at >= 5.0) {
                kill(-pid, SIGKILL); (void)reap_blocking(pid, &status); answer = stop_status; break;
            }
            struct timespec pause = {0, 20000000};
            while (nanosleep(&pause, &pause) && errno == EINTR) {
                if (interrupted) break;
            }
        }
    }
    /* A successful leader is not success if its own group still has members.
       Separate backend groups are owned and cleaned by the Python worker. */
    if (pid > 0 && (kill(-pid, 0) == 0 || errno == EPERM)) {
        kill(-pid, SIGKILL);
        if (answer == 0) answer = 1106;
    }
    if (int_set) sigaction(SIGINT, &old_int, NULL);
    if (term_set) sigaction(SIGTERM, &old_term, NULL);
    return answer;
}
