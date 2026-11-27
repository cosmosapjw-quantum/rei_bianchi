import datetime, json, os, resource, subprocess, sys, time
from pathlib import Path
root=Path(__file__).resolve().parent
attempt="attempt_001"
env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1",MKL_NUM_THREADS="1",NUMEXPR_NUM_THREADS="1")
def limits():
 resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
 resource.setrlimit(resource.RLIMIT_CPU,(30,30))
t=time.perf_counter()
p=subprocess.run([sys.executable,str(root/'run_oracle.py'),attempt],env=env,
                 capture_output=True,text=True,preexec_fn=limits,timeout=90)
record={"returncode":p.returncode,"stdout":p.stdout,"stderr":p.stderr,
        "wall_s":time.perf_counter()-t,"child_CPU_user_s":resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime,
        "child_CPU_system_s":resource.getrusage(resource.RUSAGE_CHILDREN).ru_stime,
        "child_maxRSS_KiB":resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        "utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "CPU_limit_seconds":30,"address_space_limit_bytes":512*1024**2}
with open(root/'LAUNCH_RECEIPT.json','x') as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps(record))
sys.exit(p.returncode)

