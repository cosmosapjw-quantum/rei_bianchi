"""Subprocess timing/resource wrapper; /usr/bin/time is absent in this sandbox."""
from pathlib import Path
import hashlib
import json
import os
import resource
import subprocess
import sys
import time

root=Path(__file__).resolve().parents[1]
name=sys.argv[1]
command=[str(root/"target/release/photon_bench"), *sys.argv[2:]]
start=time.perf_counter()
with (root/f"evidence/{name}.log").open("w") as output:
    completed=subprocess.run(command,stdout=output,stderr=subprocess.STDOUT,check=False)
usage=resource.getrusage(resource.RUSAGE_CHILDREN)
record={"command":command,"exit_code":completed.returncode,"wall_seconds":time.perf_counter()-start,
        "child_user_seconds":usage.ru_utime,"child_system_seconds":usage.ru_stime,
        "child_maxrss_kib":usage.ru_maxrss,"affinity":sorted(os.sched_getaffinity(0)),
        "cpu_quota":Path('/sys/fs/cgroup/cpu.max').read_text().strip(),
        "load_average":os.getloadavg(),
        "binary_sha256":hashlib.sha256((root/"target/release/photon_bench").read_bytes()).hexdigest()}
(root/f"evidence/{name}_PROCESS.json").write_text(json.dumps(record,indent=2)+"\n")
print(json.dumps(record))
sys.exit(completed.returncode)
