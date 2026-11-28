#!/usr/bin/env python3
"""Two-process, deterministic midpoint/whole evaluator with bounded CPU threading.

Exactly the pre-existing source eval is launched for each independent domain.
The processes never share writable outputs and both exit/statuses are recorded.
"""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,time
def run(root:Path):
    root=root.resolve()
    if not (root/"inputs/FIXED_REFERENCE.npz").exists():
        raise ValueError("MISSING_SOURCE_REFERENCE")
    for kind in ("mid","whole"):
        if (root/"results"/(kind+"_jets.json")).exists():
            raise ValueError("REFUSE_OVERWRITE_EXISTING_CERTIFICATE")
        for extension in ("stdout","stderr"):
            if (root/"evidence"/(kind+"."+extension)).exists():
                raise ValueError("REFUSE_OVERWRITE_EXISTING_LOG")
    env=dict(os.environ)
    env.update({"PYTHONPATH":str(root/"src"),
                "OMP_NUM_THREADS":"1","OPENBLAS_NUM_THREADS":"1",
                "MKL_NUM_THREADS":"1","NUMEXPR_NUM_THREADS":"1"})
    processes=[];outputs=[]
    started=time.perf_counter()
    try:
        for kind in ("mid","whole"):
            out=(root/"evidence"/(kind+".stdout")).open("xb")
            err=(root/"evidence"/(kind+".stderr")).open("xb")
            outputs.extend([out,err])
            proc=subprocess.Popen([sys.executable,str(root/"src/run_evaluations.py"),kind],
                                  cwd=root,env=env,stdout=out,stderr=err)
            processes.append((kind,proc))
        status={name:proc.wait() for name,proc in processes}
    finally:
        for f in outputs:f.close()
    result={
      "schema":"he18.c7.two_process_evaluation.v1",
      "wall_s":time.perf_counter()-started,
      "exitcodes":status,
      "max_scientific_workers":2,
      "thread_caps":{"OMP":1,"OPENBLAS":1,"MKL":1,"NUMEXPR":1},
      "result_sha256":{},
      "all_pass":all(x==0 for x in status.values()),
      "no_native_Codex":True}
    for kind in status:
        p=root/"results"/(kind+"_jets.json")
        if p.exists():
            result["result_sha256"][kind]=hashlib.sha256(p.read_bytes()).hexdigest()
        else:result["all_pass"]=False
    target=root/"evidence/PARALLEL_EVALUATION.json"
    if target.exists():raise ValueError("REFUSE_OVERWRITE_PARALLEL_RECORD")
    target.write_text(json.dumps(result,indent=2)+"\n")
    if not result["all_pass"]:raise RuntimeError("SOURCE_INTERVAL_EVALUATION_FAILED")
    return result
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--runtime",required=True,type=Path)
    a=p.parse_args()
    print(json.dumps(run(a.runtime),indent=2))
