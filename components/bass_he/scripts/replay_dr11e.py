#!/usr/bin/env python3
"""Durable DR11D replay with DR11E real anchors; no downstream transport.

Each invocation executes one finite stage, or one branch of the rho stage.
Artifacts are immutable; a completed output is not silently overwritten.
"""
from __future__ import annotations
import argparse,hashlib,json,os,signal,sys,time,traceback
from pathlib import Path
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import numpy as np
from bass_he.spectral import find_exceptional_point
from bass_he.sturm_geometry import contour_geometry

from bass_he.replay_contract import (BRANCHES, CONTROL_PAIR, CONTROL_SEED, DEPTH, FRACTIONS, PANELS,
    SOURCE_DELTA, SOURCE_REL_LIMIT, EP_DISTANCE_LIMIT, RESIDUAL_LIMIT, SHEET_GAP_MIN, panel_limit)

DEPENDENCIES=('bass_he/sturm_anchor.py','bass_he/sturm_geometry.py','bass_he/geometry.py',
              'bass_he/spectral.py','arseny_reimpl/term_complex.py','arseny_reimpl/term_real.py')
def enc(x):
 if isinstance(x,(complex,np.complexfloating)):return {'complex':[float(x.real),float(x.imag)]}
 if isinstance(x,np.ndarray):return x.tolist()
 if isinstance(x,np.generic):return x.item()
 raise TypeError(type(x).__name__)
def decode(x):
 if isinstance(x,dict):return complex(*x['complex']) if set(x)=={'complex'} else {k:decode(v) for k,v in x.items()}
 if isinstance(x,list):return [decode(v) for v in x]
 return x

def identity():return {k:hashlib.sha256((ROOT/'src'/k).read_bytes()).hexdigest() for k in DEPENDENCIES}

def save(path,obj):
 path=Path(path)
 data=(json.dumps(obj,indent=2,sort_keys=True,default=enc,allow_nan=False)+'\n').encode()
 with path.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())

def alarm(*_):raise TimeoutError('preregistered individual numerical call exceeded 120 s')

def bounded(fn,*args,**kwargs):
 signal.signal(signal.SIGALRM,alarm);signal.alarm(120);t=time.perf_counter()
 try:r=fn(*args,**kwargs);return r,time.perf_counter()-t
 finally:signal.alarm(0)

def geo(ep,rho,n):
 r,t=bounded(contour_geometry,ep,rho,panels=n);r['elapsed_seconds']=t
 return r

def measure(ep,frac,cache_dir=None):
 rho=frac*ep['R'].real
 def one(n):
  if cache_dir is None:return geo(ep,rho,n)
  cache_dir.mkdir(parents=True,exist_ok=True)
  key=dict(ep=ep,rho=float(rho),panels=n,source_sha256=identity())
  name=hashlib.sha256(json.dumps(key,sort_keys=True,default=enc).encode()).hexdigest()+'.json'
  path=cache_dir/name
  if path.exists():
   old=decode(json.loads(path.read_text()))
   if old['key']!=key:raise RuntimeError('immutable geometry cache key mismatch')
   return old['result']
  result=geo(ep,rho,n);save(path,dict(key=key,result=result))
  return result
 a=one(32);b=one(64)
 rel=abs(a['delta']-b['delta'])/b['delta'];lim=panel_limit(frac)
 ok=rel<=lim and all(np.isfinite(v['delta']) and v['delta']>0 and v['max_spectral_residual']<=RESIDUAL_LIMIT and v['minimum_normalized_sheet_gap']>SHEET_GAP_MIN for v in (a,b))
 return dict(fraction=frac,rho=rho,panel32=a,panel64=b,relative_32_64=rel,threshold=lim,passed=bool(ok))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--stage',required=True,choices=('control','endpoints','d0','rho','closeout'))
 ap.add_argument('--out',type=Path,required=True);ap.add_argument('--branch',choices=BRANCHES)
 args=ap.parse_args();out=args.out;out.mkdir(parents=True,exist_ok=True)
 suffix='_'+args.branch if args.stage=='rho' and args.branch else ''
 dest=out/(args.stage+suffix+'.json')
 if dest.exists():raise FileExistsError(f'immutable result already exists: {dest}')
 rec=dict(stage=args.stage,source_sha256=identity(),physical_probability_run=False,
          independent_review=False,started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
 start=time.perf_counter()
 def read(name):
  obj=decode(json.loads((out/name).read_text()))
  if obj['source_sha256']!=rec['source_sha256']:raise RuntimeError('dependency identity changed across stages')
  if obj['status']!='PASS':raise RuntimeError(f'upstream stage not passed: {name}')
  return obj
 try:
  if args.stage=='control':
   ep,t=bounded(find_exceptional_point,*CONTROL_PAIR,CONTROL_SEED,depth=DEPTH)
   g=geo(ep,0.,64);relative=abs(g['delta']-SOURCE_DELTA)/SOURCE_DELTA
   rec.update(ep=ep,geometry=g,relative_to_source=relative,status='PASS' if relative<=SOURCE_REL_LIMIT and g['max_spectral_residual']<=RESIDUAL_LIMIT else 'FAIL')
  elif args.stage=='endpoints':
   read('control.json');rows={}
   for name,(a,b,R) in BRANCHES.items():
    ep,t=bounded(find_exceptional_point,a,b,R,depth=DEPTH)
    rows[name]=dict(ep=ep,distance=abs(ep['R']-R),elapsed_seconds=t)
   rec.update(rows=rows,status='PASS' if all(x['distance']<=EP_DISTANCE_LIMIT and x['ep']['certificate']['simple_fold'] for x in rows.values()) else 'FAIL')
  elif args.stage=='d0':
   eps=read('endpoints.json')['rows'];rows={}
   for name in BRANCHES:rows[name]=measure(eps[name]['ep'],0.,out/'case_cache')
   rec.update(rows=rows,status='PASS' if all(x['passed'] for x in rows.values()) else 'FAIL')
  elif args.stage=='rho':
   if not args.branch:raise ValueError('--branch required for rho stage')
   read('d0.json');ep=read('endpoints.json')['rows'][args.branch]['ep']
   rows=[measure(ep,f,out/'case_cache') for f in FRACTIONS[1:]]
   rec.update(branch=args.branch,rows=rows,status='PASS' if all(x['passed'] for x in rows) else 'FAIL')
  else:
   c=read('control.json');e=read('endpoints.json');z=read('d0.json')
   rr={name:read('rho_'+name+'.json') for name in BRANCHES}
   summaries=[]
   for name in BRANCHES:
    probes=[z['rows'][name]]+rr[name]['rows']
    summaries.append(dict(branch=name,deltas64=[p['panel64']['delta'] for p in probes],
                         relative_32_64=[p['relative_32_64'] for p in probes],
                         max_spectral_residual=max(p[n]['max_spectral_residual'] for p in probes for n in ('panel32','panel64')),
                         minimum_normalized_sheet_gap=min(p[n]['minimum_normalized_sheet_gap'] for p in probes for n in ('panel32','panel64')),
                         max_anchor_energy_basis_difference=max(p[n]['real_anchor'][ab]['energy_basis_difference'] for p in probes for n in ('panel32','panel64') for ab in ('a','b'))))
   rec.update(status='PASS',source_control_relative_error=c['relative_to_source'],branches=summaries,
       actions_computed=56,endpoint_reconstructions=7,source_controls=1,
       claim='FINITE_BASIS_AND_FINITE_CF_STRAIGHT_LINE_GEOMETRY_VALIDATED_CANDIDATE',
       PROMOTE='HOLD_INDEPENDENT_REVIEW_UNAVAILABLE',
       downstream={'Eq55':'NOT_RUN','P_rot':'NOT_RUN','Eq50':'NOT_RUN','Eq54':'NOT_RUN','continuum_ionization':'NOT_ADMITTED'})
 except Exception:
  rec.update(status='FAILED_OR_BLOCKED',traceback=traceback.format_exc())
 rec['elapsed_seconds']=time.perf_counter()-start;save(dest,rec)
 print(json.dumps({k:rec[k] for k in ('stage','status','elapsed_seconds')},sort_keys=True),flush=True)
 if args.stage=='closeout':print(json.dumps(rec,indent=2,default=enc))
 return 0 if rec['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
