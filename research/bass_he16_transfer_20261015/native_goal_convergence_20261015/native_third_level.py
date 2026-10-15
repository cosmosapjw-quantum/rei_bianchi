"""Third independent tolerance level for AXBI short native convergence.

Separate immutable plan/output directory; earlier six runs remain unchanged.
Not a scientific admission or source error enclosure.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import hashlib
from pathlib import Path
import time

import native_probe as pilot

LABEL="ultra"
LOCAL_TARGET=1e-6

def run(binary,base,jobs,execute):
    if jobs not in (1,2):
        raise ValueError("At most two native workers")
    orig=pilot.TARGETS.get(LABEL)
    pilot.TARGETS[LABEL]=LOCAL_TARGET
    try:
        pre=pilot.preflight(binary,base,allow_prepared=execute)
        configs={case:pilot.conf(q,LOCAL_TARGET) for case,q in pilot.CASE_Q.items()}
        cfg_sha={f"{case}_{LABEL}.cfg":hashlib.sha256(val.encode()).hexdigest()
                 for case,val in configs.items()}
        if execute:
            frozen=json.loads((base/"PLAN.json").read_text())
            if frozen["binary_sha256"]!=pilot.BINARY_SHA or frozen["configs"]!=cfg_sha or frozen["jobs"]!=jobs or frozen["source_sha256"]!=pilot.SOURCE_SHA:
                raise ValueError("Frozen third-tier native contract changed")
            if (base/"runs").exists() or any((base/"receipts").iterdir()):
                raise FileExistsError("Already attempted third-tier contract")
            if any((base/"configs"/f"{case}_{LABEL}.cfg").read_text()!=content for case,content in configs.items()):
                raise ValueError("Third-tier config was edited after planning")
        else:
            (base/"configs").mkdir(parents=True)
            (base/"receipts").mkdir()
            for case,content in configs.items():
                (base/"configs"/f"{case}_{LABEL}.cfg").write_text(content)
            (base/"PLAN.json").write_text(json.dumps({
                "schema":"he18.axbi.native_refinement_level3.v1",
                "source_sha256":pilot.SOURCE_SHA,
                "binary_sha256":pilot.BINARY_SHA,
                "target":LOCAL_TARGET,
                "z_end":pilot.END_ZBAR,
                "jobs":jobs,"configs":cfg_sha,
                "scientific_admission":"EXPLORATORY_NONAUTHORITATIVE",
                "resource":pre
            },indent=2)+"\n")
            print(json.dumps({"status":"PLAN_ONLY","configs":cfg_sha},indent=2))
            return
        started=time.perf_counter()
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            futures=[ex.submit(pilot.one_run,binary,base,case,LABEL) for case in pilot.CASE_Q]
            receipts=[f.result() for f in futures]
        summary={"schema":"he18.axbi.native_refinement_level3_runs.v1",
                 "wall_s":time.perf_counter()-started,
                 "successes":sum(x["status"]=="EXIT_ZERO" for x in receipts),
                 "receipts":receipts,"scientific_admission":"NOT_ISSUED"}
        (base/"RUN_SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n")
        print(json.dumps({"successes":summary["successes"],"wall_s":summary["wall_s"],
                          "statuses":[(x["case"],x["status"],x["elapsed_s"],
                                       x["result"].get("rows")) for x in receipts]},indent=2))
    finally:
        if orig is None:pilot.TARGETS.pop(LABEL,None)
        else:pilot.TARGETS[LABEL]=orig

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--binary",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--jobs",type=int,default=2)
    p.add_argument("--execute",action="store_true")
    args=p.parse_args()
    run(args.binary,args.out,args.jobs,args.execute)
