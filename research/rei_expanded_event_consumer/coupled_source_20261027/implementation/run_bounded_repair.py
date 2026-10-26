"""Bounded targeted repair runner. Invoke only after root repair GO."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "PREEXEC_REPAIR_MANIFEST.json"
OUTPUT = HERE / "attempt02"
CHILD_CPU_HARD_S = 0.8
WALL_HARD_S = 8.0
MEMORY_BYTES = 512 * 1024 * 1024


def cpu_of_pid(pid):
    try:
        fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")",1)[1].split()
        return (int(fields[11])+int(fields[12]))/os.sysconf("SC_CLK_TCK")
    except (FileNotFoundError, ProcessLookupError):
        return None


def limits():
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_BYTES,MEMORY_BYTES))
    resource.setrlimit(resource.RLIMIT_CPU, (1,1))


def main():
    manifest=json.loads(MANIFEST.read_text())
    for item in manifest["inputs"]:
        path=ROOT/item["path"]
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual!=item["sha256"]:
            raise ValueError(f"frozen input differs: {item['path']}")
    if OUTPUT.exists():
        raise FileExistsError("attempt02 already exists; preserve raw run")
    OUTPUT.mkdir()
    env=os.environ.copy()
    env.update({"OPENBLAS_NUM_THREADS":"1","MKL_NUM_THREADS":"1",
                "OMP_NUM_THREADS":"1","NUMEXPR_NUM_THREADS":"1","VECLIB_MAXIMUM_THREADS":"1",
                "PYTHONHASHSEED":"0"})
    cmd=[sys.executable,str(HERE/"check_coupled_photo_repair.py")]
    t0=time.perf_counter(); c0=time.process_time()
    before=resource.getrusage(resource.RUSAGE_CHILDREN)
    stop_reason=None
    with (OUTPUT/"stdout.json").open("wb") as stdout, (OUTPUT/"stderr.log").open("wb") as stderr:
        child=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=stdout,stderr=stderr,preexec_fn=limits)
        while child.poll() is None:
            if time.perf_counter()-t0>WALL_HARD_S:
                stop_reason="WALL_LIMIT"
            elif (cpu_of_pid(child.pid) or 0)>CHILD_CPU_HARD_S:
                stop_reason="CHILD_CPU_LIMIT"
            if stop_reason:
                child.kill()
                break
            time.sleep(.01)
        exit_code=child.wait()
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    child_cpu=(after.ru_utime-before.ru_utime)+(after.ru_stime-before.ru_stime)
    receipt={"status":"COMPLETED" if exit_code==0 and not stop_reason else "FAILED",
             "exit_code":exit_code,"stop_reason":stop_reason,"command":cmd,
             "input_manifest":str(MANIFEST.relative_to(ROOT)),
             "child_CPU_s":child_cpu,"wrapper_CPU_s":time.process_time()-c0,
             "wall_s":time.perf_counter()-t0,"child_max_RSS_KiB":after.ru_maxrss,
             "limits":{"child_CPU_s":CHILD_CPU_HARD_S,"wall_s":WALL_HARD_S,
                       "address_space_MiB":512,"BLAS_workers":1},
             "stdout":"stdout.json","stderr":"stderr.log",
             "science_claim":"PENDING_INDEPENDENT_REVIEW"}
    (OUTPUT/"RESOURCE_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt,indent=2))
    return 0 if receipt["status"]=="COMPLETED" else 1


if __name__=="__main__":
    sys.exit(main())
