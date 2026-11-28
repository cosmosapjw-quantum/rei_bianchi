/* C-only test harness, not the MPI production entry point. */
#include "worker_spawn.h"
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <limits.h>
int main(int argc, char **argv) {
    if (argc != 6) return 2;
    char *end; errno=0; long task=strtol(argv[4],&end,10);
    if(errno || *end || task<0 || task>INT_MAX) return 2;
    errno=0; long seconds=strtol(argv[5],&end,10);
    if(errno || *end || seconds<1 || seconds>INT_MAX) return 2;
    int rc=ncp64_run_worker(argv[1],argv[2],argv[3],(int)task,(int)seconds);
    printf("{\"shim_status\":%d}\n",rc);
    return rc ? 2 : 0;
}
