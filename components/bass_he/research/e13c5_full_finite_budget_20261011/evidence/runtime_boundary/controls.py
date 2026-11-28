#!/usr/bin/env python3
"""Synthetic boundary controls for the saved-budget wrapper. NOT PHYSICS."""
import argparse
import hashlib
import gzip
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import time
import zipfile

def digest(p):
    b=Path(p).read_bytes()
    return {"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}

def load(path):
    spec=importlib.util.spec_from_file_location("ncp_budget_under_test",path)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def jsonfile(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,sort_keys=True,indent=2)+"\n")

def fixture(root,behavior):
    package=root/"package"
    (package/"code").mkdir(parents=True)
    (package/"dependencies").mkdir()
    (package/"baseline").mkdir()
    jsonfile(package/"SCIENTIFIC_CONTRACT.json",{"synthetic":True})
    plain_csv=b"mode,node,width\nOFF,101,1/2\n"
    compressed=gzip.compress(plain_csv,compresslevel=9,mtime=0)
    projection={"schema":"synthetic_only","value":"7/4","physics":False,
                "ranking_artifact":{"file":"WIDTH_RANKINGS.csv.gz","bytes":len(compressed),
                                    "sha256":hashlib.sha256(compressed).hexdigest(),"rows":1,"format":"SYNTHETIC_CSV"}}
    projection_bytes=(json.dumps(projection,sort_keys=True,separators=(",",":"))+"\n").encode()
    (package/"baseline/NUMERICAL_PROJECTION.json").write_bytes(projection_bytes)
    source="""import json, pathlib, sys, time, gzip, hashlib
a=sys.argv[1:]
def arg(k): return pathlib.Path(a[a.index(k)+1])
out=arg('--out')
behavior=BEHAVIOR
if behavior=='failure': raise SystemExit(19)
if behavior=='timeout': time.sleep(2)
if behavior=='input_tamper': arg('--paths').write_text('changed')
if behavior=='lock_tamper':
    p=pathlib.Path(__file__).parent.parent/'RUN_LOCK.json'
    x=json.loads(p.read_text()); x['limits']['minimum_free_disk_bytes']=1; p.write_text(json.dumps(x))
if behavior=='source_tamper':
    p=pathlib.Path(__file__); p.write_text(p.read_text()+'\\n# changed\\n')
out.mkdir()
csv=b'mode,node,width\\nOFF,101,1/2\\n'
if behavior=='csv_mismatch': csv=csv.replace(b'1/2',b'3/4')
gz=gzip.compress(csv,compresslevel=1 if behavior=='gzip_variant' else 9,mtime=0)
(out/'WIDTH_RANKINGS.csv.gz').write_bytes(gz)
value={'schema':'synthetic_only','value':'7/4','physics':False,
       'ranking_artifact':{'file':'WIDTH_RANKINGS.csv.gz','bytes':len(gz),
       'sha256':hashlib.sha256(gz).hexdigest(),'rows':1,'format':'SYNTHETIC_CSV'}}
if behavior=='gzip_identity_mismatch': value['ranking_artifact']['sha256']='0'*64
if behavior=='wrong_projection': value['value']='9/4'
(out/'NUMERICAL_PROJECTION.json').write_text(json.dumps(value,sort_keys=True,separators=(',',':'))+'\\n')
status='SYNTHETIC_PASS' if behavior!='wrong_status' else 'SYNTHETIC_FAIL'
(out/'RESULTS.json').write_text(json.dumps({**value,'status':status,'synthetic':True}))
"""
    source=source.replace("BEHAVIOR",repr(behavior))
    (package/"code/full_finite_budget.py").write_text(source)
    raw=b"synthetic raw\n"
    dep=package/"dependencies/fixture.tar.gz"
    with tarfile.open(dep,"w:gz") as t:
        info=tarfile.TarInfo("input/raw.txt");info.size=len(raw)
        t.addfile(info,io.BytesIO(raw))
    files={str(p.relative_to(package)):digest(p) for p in package.rglob("*") if p.is_file()}
    normalized={**projection,"ranking_artifact":{k:v for k,v in projection["ranking_artifact"].items() if k not in ("bytes","sha256")}}
    semantic=hashlib.sha256(json.dumps(normalized,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    lock={"files":files,
          "dependencies":{"pr20":{"path":"dependencies/fixture.tar.gz","format":"tar.gz","regular_files":1,"unpacked_bytes":len(raw)}},
          "input_map":{"paths":{"dependency":"pr20","member":"input/raw.txt","bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}},
          "expected_projection":{**digest(package/"baseline/NUMERICAL_PROJECTION.json"),"canonical_sha256":hashlib.sha256(projection_bytes[:-1]).hexdigest(),"semantic_sha256":semantic},
          "expected_ranking_content":{"bytes":len(plain_csv),"sha256":hashlib.sha256(plain_csv).hexdigest()},
          "expected_budget_status":"SYNTHETIC_PASS",
          "limits":{"minimum_free_disk_bytes":0,"minimum_available_memory_bytes":0,"child_wall_seconds":0.15 if behavior=="timeout" else 10,"child_address_space_bytes":268435456,"child_cpu_seconds":5}}
    jsonfile(package/"RUN_LOCK.json",lock)
    return package

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--runner",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    runner=load(args.runner)
    start=time.monotonic()
    checks=[]
    specs=[
      ("verify_only","success",False,"VERIFY_ONLY_READY",None,0),
      ("fresh_success","success",True,"PASS_SCOPED_SAVED_FULL_FINITE_BUDGET_PARITY",None,1),
      ("child_failure","failure",True,"FAIL_STOP_PRESERVE","BUDGET_CHILD_FAILED",1),
      ("projection_mismatch","wrong_projection",True,"FAIL_STOP_PRESERVE","NUMERICAL_SEMANTIC_PROJECTION_PARITY_FAILURE",1),
      ("gzip_variant_same_csv","gzip_variant",True,"PASS_SCOPED_SAVED_FULL_FINITE_BUDGET_PARITY",None,1),
      ("csv_content_mismatch","csv_mismatch",True,"FAIL_STOP_PRESERVE","RANKING_CONTENT_PARITY_FAILURE",1),
      ("gzip_identity_mismatch","gzip_identity_mismatch",True,"FAIL_STOP_PRESERVE","RANKING_GZIP_IDENTITY_MISMATCH",1),
      ("result_status_mismatch","wrong_status",True,"FAIL_STOP_PRESERVE","BUDGET_STATUS_FAILURE",1),
      ("extracted_input_tamper","input_tamper",True,"FAIL_STOP_PRESERVE","FILE_IDENTITY_MISMATCH",1),
      ("lock_metadata_tamper","lock_tamper",True,"FAIL_STOP_PRESERVE","RUN_LOCK_CHANGED_DURING_RUN",1),
      ("locked_source_tamper","source_tamper",True,"FAIL_STOP_PRESERVE","FILE_IDENTITY_MISMATCH",1),
      ("timeout_preserve","timeout",True,"FAIL_STOP_PRESERVE","BUDGET_CHILD_FAILED",1),
      ("wrong_lock_before","success",True,"FAIL_STOP_PRESERVE","RUN_LOCK_IDENTITY_MISMATCH",0),
      ("wrong_dependency_before","success",True,"FAIL_STOP_PRESERVE","FILE_IDENTITY_MISMATCH",0)]
    for name,behavior,execute,status,error,count in specs:
        case=args.out/"cases"/name
        package=fixture(case,behavior)
        runner.LOCK_SHA256=runner.sha(package/"RUN_LOCK.json")
        if name=="wrong_lock_before":
            with (package/"RUN_LOCK.json").open("a") as f:f.write(" ")
        if name=="wrong_dependency_before":
            with (package/"dependencies/fixture.tar.gz").open("ab") as f:f.write(b"changed")
        exit_code=runner.run(package,case/"OUT",execute,"SYNTHETIC_NOT_NCP")
        r=json.loads((case/"OUT/RUN_RECEIPT.json").read_text())
        ok=r["status"]==status and r["budget_invocations"]==count and r["physics_invocations"]==0
        ok=ok and exit_code==(0 if status.startswith(("VERIFY_","PASS_")) else 1)
        if error:ok=ok and error in r.get("error","")
        if behavior=="gzip_variant":
            ok=ok and r.get("parity",{}).get("raw_projection_file_parity") is False
            ok=ok and r.get("parity",{}).get("semantic_projection_parity") is True
            ok=ok and r.get("parity",{}).get("ranking",{}).get("uncompressed_content_parity") is True
        if not execute:ok=ok and not (case/"OUT/WORK").exists() and not (case/"OUT/BUDGET").exists()
        if count:ok=ok and (case/"OUT/stdout.log").is_file() and (case/"OUT/stderr.log").is_file()
        checks.append({"id":name,"pass":ok,"actual_status":r["status"],"error":r.get("error"),"budget_invocations":count,"synthetic":True})
    case=args.out/"cases/collision"
    package=fixture(case,"success")
    out=case/"OUT";out.mkdir();(out/"sentinel.txt").write_text("preserve")
    try:
        runner.run(package,out,True,"SYNTHETIC_NOT_NCP")
        ok=False
    except ValueError as exc:
        ok="FRESH_OUTPUT_DIRECTORY_REQUIRED" in str(exc) and (out/"sentinel.txt").read_text()=="preserve"
    checks.append({"id":"existing_output_preserved","pass":ok,"synthetic":True})
    for name,kind in [("tar_traversal","traversal"),("tar_symlink","symlink"),("tar_hardlink","hardlink")]:
        case=args.out/"cases"/name;case.mkdir(parents=True)
        arc=case/"bad.tar.gz"
        with tarfile.open(arc,"w:gz") as t:
            info=tarfile.TarInfo("../escaped.txt" if kind=="traversal" else "link")
            if kind=="traversal": info.size=1;t.addfile(info,io.BytesIO(b"x"))
            else:
                info.type=tarfile.SYMTYPE if kind=="symlink" else tarfile.LNKTYPE
                info.linkname="../escaped.txt";t.addfile(info)
        try:
            runner.extract_dependency(arc,case/"OUT","tar.gz",1,1)
            ok=False
        except ValueError:ok=not (case/"escaped.txt").exists()
        checks.append({"id":name,"pass":ok,"synthetic":True})
    case=args.out/"cases/zip_symlink";case.mkdir(parents=True)
    arc=case/"bad.zip"
    with zipfile.ZipFile(arc,"w") as z:
        info=zipfile.ZipInfo("link");info.create_system=3;info.external_attr=0o120777<<16
        z.writestr(info,"../escaped.txt")
    try:
        runner.extract_dependency(arc,case/"OUT","zip",1,14)
        ok=False
    except ValueError:ok=not (case/"escaped.txt").exists()
    checks.append({"id":"zip_symlink","pass":ok,"synthetic":True})
    case=args.out/"cases/short_member";case.mkdir(parents=True)
    try:
        runner.copy_regular(io.BytesIO(b"ab"),case/"raw.txt",3)
        ok=False
    except ValueError as exc:
        ok="ARCHIVE_MEMBER_SIZE_MISMATCH" in str(exc) and not (case/"raw.txt").exists()
    checks.append({"id":"short_member_preserves_partial_and_blocks_final","pass":ok,"synthetic":True})
    case=args.out/"cases/post_write_truncation";case.mkdir(parents=True)
    original_replace=runner.os.replace
    def truncate_after_replace(src,dst):
        original_replace(src,dst)
        Path(dst).write_bytes(b"ab")
    try:
        runner.os.replace=truncate_after_replace
        runner.copy_regular(io.BytesIO(b"abc"),case/"raw.txt",3)
        ok=False
    except ValueError as exc:
        ok="PERSISTED_MEMBER_IDENTITY_MISMATCH" in str(exc)
    finally:
        runner.os.replace=original_replace
    checks.append({"id":"post_write_truncation_detected","pass":ok,"synthetic":True})
    result={"schema":"bass-he-e13c5-ncp-budget-boundary-controls-v1","runner_identity":digest(args.runner),
            "controller_identity":digest(Path(__file__)),"checks":checks,
            "check_count":len(checks),"passed":sum(x["pass"] for x in checks),
            "failed":sum(not x["pass"] for x in checks),"wall_seconds":time.monotonic()-start,
            "all_cases":"SYNTHETIC_NOT_PHYSICS_NOT_NCP","actual_budget_science_replays":0,
            "new_coefficients":0,"native_runs":0,"gas_advances":0,
            "test_lock_injection":"Module constant overwritten only in this synthetic in-process test. Production source has no fixture or bypass flag."}
    jsonfile(args.out/"RESULTS.json",result)
    print(json.dumps({k:result[k] for k in ("check_count","passed","failed","wall_seconds")}))
    return 0 if result["failed"]==0 else 1

if __name__=="__main__":raise SystemExit(main())

