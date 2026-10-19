#!/usr/bin/env python3
"""Run only the two missing BR03 native crossed-grid histories."""
import argparse, csv, datetime, hashlib, json, os, pathlib, subprocess, time
p=argparse.ArgumentParser()
p.add_argument("--binary",required=True,type=pathlib.Path)
p.add_argument("--output",required=True,type=pathlib.Path)
p.add_argument("--timeout",type=float,default=300.0)
p.add_argument("cases",nargs="*",choices=["ap_n16_r4","ap_n64_r4"])
a=p.parse_args()
cases=a.cases or ["ap_n16_r4","ap_n64_r4"]
binary=a.binary.resolve()
assert binary.is_file() and os.access(binary,os.X_OK),binary
bhash=hashlib.sha256(binary.read_bytes()).hexdigest()
a.output.mkdir(parents=True,exist_ok=True)
results=[]
for name in cases:
    nt=16 if name=="ap_n16_r4" else 64
    command=[str(binary),"SIGNED_MINUS","121",str(nt),"0","8e12","false","false","2","4","1e-12","4"]
    target=a.output/(name+".csv"); receipt=a.output/(name+".json")
    assert not target.exists() and not receipt.exists(),name
    live=a.output/(name+".running.csv"); err=a.output/(name+".running.stderr")
    start=time.monotonic();timed_out=False
    with live.open("xb") as stdout, err.open("xb") as stderr:
        try:
            done=subprocess.run(command,stdout=stdout,stderr=stderr,timeout=a.timeout,check=False)
            code=done.returncode
        except subprocess.TimeoutExpired:
            timed_out=True;code=-9
        stdout.flush();os.fsync(stdout.fileno());stderr.flush();os.fsync(stderr.fileno())
    wall=time.monotonic()-start
    rawerr=err.read_text()
    with live.open() as inp: rows=list(csv.DictReader(inp))
    if timed_out: status="RESOURCE_LIMIT_WALL";failure="BOUNDED_WALL_BUDGET_EXHAUSTED"
    elif code==0 and len(rows)==nt:status="COMPLETED";failure=None
    elif code==2 and "WorkLimit" in rawerr:status="RESOURCE_LIMIT_CX";failure="NUMERICAL_WORK_BUDGET_EXHAUSTED_NOT_PHYSICAL_NO_SOLUTION"
    else:status="EXECUTION_FAILED";failure="NONZERO_EXIT_OR_INCOMPLETE_ROWS"
    os.replace(live,target);os.replace(err,a.output/(name+".stderr"))
    r={"name":name,"command":command,"exit_code":code,"wall_s":wall,"rows":len(rows),"planned_rows":nt,
       "status":status,"failure_class":failure,"stderr":rawerr,"binary_sha256":bhash,
       "csv_sha256":hashlib.sha256(target.read_bytes()).hexdigest(),"final":rows[-1] if rows else None,
       "completed_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
       "physics":"Unmodified BR03 native driver; only Nt and birth refinement selected by existing arguments"}
    temp=a.output/(name+".receipt.tmp")
    temp.write_text(json.dumps(r,indent=2)+"\n");os.replace(temp,receipt)
    results.append({k:r[k] for k in ["name","status","rows","wall_s","csv_sha256"]})
    print(json.dumps(results[-1]),flush=True)
(a.output/"CAMPAIGN_RECEIPT.json").write_text(json.dumps({"status":"REQUESTED_CASES_RECORDED","results":results},indent=2)+"\n")
if any(r["status"]!="COMPLETED" for r in results):raise SystemExit(2)
