"""Create-only bounded validation/plot execution; never imports science."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]


def now():return datetime.now(timezone.utc).isoformat()


def save(path,obj):
    temporary=path.with_name(path.name+".tmp")
    with temporary.open("x",encoding="utf-8") as handle:
        json.dump(obj,handle,indent=2,sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.link(temporary,path)
    temporary.unlink()
    descriptor=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(descriptor)
    finally:os.close(descriptor)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=["validate","plot"],required=True)
    parser.add_argument("--source-commit",required=True)
    parser.add_argument("--output",required=True)
    parser.add_argument("--saved-json")
    args=parser.parse_args()
    before=resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu0,wall0=time.process_time(),time.perf_counter()
    actual=subprocess.check_output(["git","-c","core.preloadIndex=false","-c","index.threads=1","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    if actual!=args.source_commit:raise SystemExit("source commit differs from authorized pin")
    if subprocess.check_output(["git","-c","core.preloadIndex=false","-c","index.threads=1","status","--porcelain","--untracked-files=no"],cwd=ROOT,text=True).strip():
        raise SystemExit("tracked working tree is dirty; freeze source before execution")
    output=Path(args.output).resolve()
    output.mkdir(parents=True,exist_ok=False)
    cpu_cap,wall_cap=(12,40) if args.mode=="validate" else (8,20)
    env=os.environ.copy()
    env.update({name:"1" for name in ["OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"]})
    env.update(PYTHONDONTWRITEBYTECODE="1",MPLCONFIGDIR=str(ROOT.parent.parent.parent.parent/"he09_mplconfig"),MPLBACKEND="Agg")
    if args.mode=="validate":
        command=[sys.executable,"-B",str(ROOT/"scripts/validate_once.py"),"--saved-json",str(output/"SAVED_PLOT_DATA.json"),"--report-json",str(output/"TEST_REPORT.json")]
    else:
        if not args.saved_json:raise SystemExit("plot requires saved validation JSON")
        command=[sys.executable,"-B",str(ROOT/"scripts/plot_saved.py"),"--saved-json",str(Path(args.saved_json).resolve()),"--output",str(output)]
    files=list((ROOT/"src").glob("*.py"))+list((ROOT/"tests").glob("*.py"))+list((ROOT/"scripts").glob("*.py"))
    source_hashes={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(files)}
    receipt={"mode":args.mode,"start":now(),"source_commit":actual,"source_tree":subprocess.check_output(["git","-c","core.preloadIndex=false","-c","index.threads=1","rev-parse","HEAD^{tree}"],cwd=ROOT,text=True).strip(),"command":command,"limits":{"child_cpu_s":cpu_cap,"wall_s":wall_cap,"address_space_bytes":512*1024**2,"single_thread":True},"source_sha256":source_hashes,"scientific_suite_runs_authorized":1 if args.mode=="validate" else 0}
    save(output/"START.json",receipt)
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU,(cpu_cap,cpu_cap))
        resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
        resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    with (output/"stdout.log").open("x") as stdout,(output/"stderr.log").open("x") as stderr:
        process=subprocess.Popen(command,cwd=ROOT,env=env,stdout=stdout,stderr=stderr,preexec_fn=limits,start_new_session=True)
        timed_out=False
        try:exitcode=process.wait(timeout=wall_cap)
        except subprocess.TimeoutExpired:
            timed_out=True
            import signal
            os.killpg(process.pid,signal.SIGKILL)
            exitcode=process.wait()
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    child_cpu=(after.ru_utime+after.ru_stime)-(before.ru_utime+before.ru_stime)
    controller_cpu=time.process_time()-cpu0
    wall=time.perf_counter()-wall0
    receipt.update(finish=now(),exit_code=exitcode,timed_out=timed_out,child_cpu_s=child_cpu,controller_cpu_s=controller_cpu,total_observed_cpu_s=child_cpu+controller_cpu,wall_s=wall,peak_child_rss_kib=after.ru_maxrss,cpu_cap_met=child_cpu+controller_cpu<=cpu_cap,wall_cap_met=wall<=wall_cap,scientific_calls_in_plot=0 if args.mode=="plot" else None)
    receipt["status"]="PASS" if exitcode==0 and receipt["cpu_cap_met"] and receipt["wall_cap_met"] else "FAIL"
    save(output/"RESOURCE_RESULT.json",receipt)
    print(json.dumps({key:receipt[key] for key in ["mode","status","exit_code","child_cpu_s","controller_cpu_s","total_observed_cpu_s","wall_s","peak_child_rss_kib"]}))
    sys.exit(0 if receipt["status"]=="PASS" else 1)
