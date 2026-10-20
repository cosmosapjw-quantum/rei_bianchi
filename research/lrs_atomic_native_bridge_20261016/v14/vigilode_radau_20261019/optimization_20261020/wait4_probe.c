#define _GNU_SOURCE
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <time.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr,"usage: wait4_probe OUTCOME_JSON COMMAND [ARG...]\n"); return 2; }
    struct timespec begin,end;
    clock_gettime(CLOCK_MONOTONIC,&begin);
    pid_t pid=fork();
    if(pid<0){perror("fork");return 2;}
    if(pid==0){execvp(argv[2],argv+2);perror("execvp");_exit(127);}
    int status;struct rusage usage;
    while(wait4(pid,&status,0,&usage)<0){if(errno==EINTR)continue;perror("wait4");return 2;}
    clock_gettime(CLOCK_MONOTONIC,&end);
    int code=WIFEXITED(status)?WEXITSTATUS(status):128+WTERMSIG(status);
    FILE *out=fopen(argv[1],"w");if(!out){perror("fopen");return 2;}
    double wall=(end.tv_sec-begin.tv_sec)+(end.tv_nsec-begin.tv_nsec)*1e-9;
    fprintf(out,"{\"exit_code\":%d,\"actual_ru_maxrss_kb\":%ld,\"process_wall_s\":%.9f,\"method\":\"small C parent fork-exec-wait4\"}\n",code,usage.ru_maxrss,wall);
    if(fclose(out)){perror("fclose");return 2;}
    return code;
}
