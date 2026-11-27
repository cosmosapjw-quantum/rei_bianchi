#ifndef NCP64_WORKER_SPAWN_H
#define NCP64_WORKER_SPAWN_H
/* Returns child exit status, 128+signal, 124 watchdog, or 1100+ shim failure. */
int ncp64_run_worker(const char *python, const char *worker, const char *manifest,
                     int task_index, int timeout_seconds);
#endif
