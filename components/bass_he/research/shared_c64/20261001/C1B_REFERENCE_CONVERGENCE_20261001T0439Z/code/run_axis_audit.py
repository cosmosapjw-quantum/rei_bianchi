"""Independent one-axis refinements after actual angular acceptance; no R grid."""
from pathlib import Path
import json,subprocess,sys,time,os
from evidence_io import atomic_json,sha256
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'evidence/AXIS_EXECUTION.json'
if out.exists():raise FileExistsError(out)
a=json.loads((ROOT/'evidence/B_l72.json').read_text());b=json.loads((ROOT/'evidence/B_l96.json').read_text())
assert max(b['vs_C1_prolate']['energy_abs'])<1e-5 and b['vs_C1_prolate']['L_O_abs']<1e-5
assert abs(a['direct']['L_O_over_minus_i_hbar']-b['direct']['L_O_over_minus_i_hbar'])<2e-6
base=[sys.executable,'-u',str(ROOT/'code/run_centered.py')]
commands=[('B_l96_h80',base+['B_l96_h80','--lmax','96','--elements','80']),
          ('B_l96_p5',base+['B_l96_p5','--lmax','96','--degree','5']),
          ('B_l96_q22',base+['B_l96_q22','--lmax','96','--quadrature','22']),
          ('B_l96_tail32',base+['B_l96_tail32','--lmax','96','--rmax','32','--tail-base','B_l96']),
          ('PROLATE_TAIL_ONLY',[sys.executable,'-u',str(ROOT/'code/run_prolate_tail.py')])]
start=time.perf_counter();runs=[]
for tag,cmd in commands:
    logfile=ROOT/f'evidence/{tag}_STDOUT.txt'
    with logfile.open('x') as f:
        t=time.perf_counter();p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=90,check=False)
    rec={'tag':tag,'command':cmd,'exit_code':p.returncode,'seconds':time.perf_counter()-t,'stdout_sha256':sha256(logfile)}
    runs.append(rec);print(json.dumps(rec),flush=True)
    if p.returncode!=0:
        atomic_json(out,{'status':'FAIL','runs':runs});raise SystemExit(p.returncode)
atomic_json(out,{'status':'PASS_EXECUTION_ONLY','runs':runs,'elapsed_seconds':time.perf_counter()-start,'driver_sha256':sha256(__file__)})
