"""Bounded HERE campaign of independent, non-repeated B1 jobs."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
JOBS = [("base", c, 128, 24, 257) for c in ("F", "M", "B", "B0", "B_F", "M_F")]
JOBS += [("time", c, 256, 24, 257) for c in ("B", "B_F")]
JOBS += [("angle", c, 128, 48, 257) for c in ("B", "B_F")]
JOBS += [("energy", c, 128, 24, 513) for c in ("B", "B_F")]


def main():
    logroot = ROOT/"execution_logs/RUN001"
    logroot.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy()
    env.update(OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
    def run(job):
        group, case, nt, nm, ne = job
        name = f"{group}_{case}_t{nt}_mu{nm}_e{ne}"
        out = ROOT/"runs"/name
        cmd = [sys.executable, "-u", str(ROOT/"b1_transport.py"), "--case", case,
               "--nsteps", str(nt), "--nmu", str(nm), "--nenergy", str(ne), "--out", str(out)]
        start = time.perf_counter()
        with (logroot/(name+".stdout.txt")).open("w") as stdout, (logroot/(name+".stderr.txt")).open("w") as stderr:
            p = subprocess.run(cmd, cwd=ROOT, env=env, stdout=stdout, stderr=stderr, timeout=120)
        rec = dict(name=name, group=group, case=case, command=cmd, exit_code=p.returncode,
                   process_wall_seconds=time.perf_counter()-start, output=str(out.relative_to(ROOT)))
        (logroot/(name+".execution.json")).write_text(json.dumps(rec, indent=2)+"\n")
        return rec
    start = time.perf_counter()
    records = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(run,j) for j in JOBS]
        for future in as_completed(futures):
            r = future.result()
            records.append(r)
            print(json.dumps(r), flush=True)
    manifest = dict(status="COMPLETED" if all(r["exit_code"]==0 for r in records) else "HAS_FAILURE",
                    wall_seconds=time.perf_counter()-start, concurrent_independent_jobs=3,
                    scientific_worker_threads=1, NCP_jobs=0, rust_invocations=0,
                    driver_sha256=hashlib.sha256((ROOT/"b1_transport.py").read_bytes()).hexdigest(),
                    jobs=sorted(records,key=lambda x:x["name"]))
    (logroot/"CAMPAIGN.json").write_text(json.dumps(manifest,indent=2)+"\n")
    if manifest["status"]!="COMPLETED":
        raise SystemExit(1)


if __name__=="__main__":
    main()
