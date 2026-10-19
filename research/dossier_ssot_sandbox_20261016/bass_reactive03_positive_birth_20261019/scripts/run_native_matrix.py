#!/usr/bin/env python3
"""Run independent bounded BASS histories; preserve raw failed attempts and exits."""
from pathlib import Path
import argparse, concurrent.futures, csv, hashlib, json, os, subprocess, time

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_BINARY=ROOT/'ap/target/release/examples/ap_native_driver'
CASES={
 'off_gl2_n32':dict(n=32,r='off'),
 'off_gl4_n32':dict(n=32,r='off',gl=4),
 'ap_n16_r2':dict(n=16,r=2),
 'ap_n32_r2':dict(n=32,r=2),
 'ap_n64_r2':dict(n=64,r=2),
 'ap_n128_r2':dict(n=128,r=2),
 'ap_n32_r1':dict(n=32,r=1),
 'ap_n32_r4':dict(n=32,r=4),
 'ap_n32_r8':dict(n=32,r=8),
 'ap_n32_r2_spectrum':dict(n=32,r=2,split=True),
 'ap_n32_r2_opacity8':dict(n=32,r=2,opacity=8),
 'ap_n32_r2_plus':dict(n=32,r=2,case='SIGNED_PLUS'),
 'ap_cx_worklimit':dict(n=32,r=2,cx=1e-14),
}
def run_one(name,out,binary):
 c=CASES[name];path=out/name
 if path.with_suffix('.json').exists() or path.with_suffix('.csv').exists():
  raise FileExistsError(path)
 args=[str(binary),c.get('case','SIGNED_MINUS'),'121',str(c['n']),'0','8e12',
       str(c.get('split',False)).lower(),'false',str(c.get('gl',2)),
       str(c.get('opacity',4)),str(c.get('cx',1e-12)),str(c['r'])]
 t=time.monotonic()
 with path.with_suffix('.running.csv').open('x') as stdout,path.with_suffix('.running.stderr').open('x') as stderr:
  p=subprocess.run(args,stdout=stdout,stderr=stderr)
  stdout.flush();os.fsync(stdout.fileno());stderr.flush();os.fsync(stderr.fileno())
 path.with_suffix('.running.csv').rename(path.with_suffix('.csv'))
 path.with_suffix('.running.stderr').rename(path.with_suffix('.stderr'))
 elapsed=time.monotonic()-t
 with path.with_suffix('.csv').open() as f: rows=list(csv.DictReader(f))
 error=path.with_suffix('.stderr').read_text()
 status='COMPLETED' if p.returncode==0 and len(rows)==c['n'] else 'EXECUTION_FAILED'
 failure=None
 if 'Cx(WorkLimit)' in error:
  status='RESOURCE_LIMIT_CX';failure='NUMERICAL_WORK_BUDGET_EXHAUSTED_NOT_PHYSICAL_NO_SOLUTION'
 elif 'NoForwardProgress' in error:
  failure='FLOATING_POINT_CLOCK_RESOLUTION'
 elif p.returncode: failure='NUMERICAL_OR_IMPLEMENTATION_FAILURE_REQUIRES_DIAGNOSIS'
 rec={'name':name,'command':args,'exit_code':p.returncode,'wall_s':elapsed,'rows':len(rows),
      'planned_rows':c['n'],'status':status,'failure_class':failure,'stderr':error,
      'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
      'csv_sha256':hashlib.sha256(path.with_suffix('.csv').read_bytes()).hexdigest(),
      'final':rows[-1] if rows else None}
 with path.with_suffix('.running.json').open('x') as f:
  f.write(json.dumps(rec,indent=2)+'\n');f.flush();os.fsync(f.fileno())
 path.with_suffix('.running.json').rename(path.with_suffix('.json'))
 print(json.dumps({k:rec[k] for k in ('name','status','exit_code','rows','wall_s')}),flush=True)
 return rec

def main():
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('cases',nargs='*');p.add_argument('--workers',type=int,default=2);p.add_argument('--binary',type=Path,default=DEFAULT_BINARY)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 names=a.cases or list(CASES)
 if any(n not in CASES for n in names):raise ValueError('unknown case')
 if not 1<=a.workers<=3:raise ValueError('bounded workers')
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as e:
  results=list(e.map(lambda n:run_one(n,a.output,a.binary),names))
 unexpected=[x for x in results if x['status']!='COMPLETED' and not(x['name']=='ap_cx_worklimit' and x['status']=='RESOURCE_LIMIT_CX')]
 if unexpected:raise SystemExit(2)
if __name__=='__main__':main()
