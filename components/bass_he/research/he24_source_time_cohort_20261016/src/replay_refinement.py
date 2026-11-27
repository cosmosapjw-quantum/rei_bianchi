"""Lightweight HE24 independent HE23 native binary replay. No new Rust compilation.
Uses pinned raw source, exact original native RHS executable and fresh output directories.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, os, pathlib, sys, tempfile, time

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--he23-root',type=pathlib.Path,required=True)
    p.add_argument('--native',type=pathlib.Path,required=True)
    p.add_argument('--out',type=pathlib.Path,required=True)
    p.add_argument('--cases',type=str,default='0:4:2,0:4:4,0:4:8,0:4:16,0:4:32,0:4:64,0:16:8,0:16:16,0:16:32')
    a=p.parse_args()
    native=a.native.resolve(); root=a.he23_root.resolve();out=a.out.resolve()
    expected='981ad6dde18be7951c6b0200a49e6482b0e6fae644437197375bdd18ced5eafe'
    if sha256(native)!=expected:raise ValueError('original Rust binary SHA mismatch')
    sys.path.insert(0,str(root/'src'))
    from run_native import run_case
    from he22_native_client import OWNER_SOURCE_SHA
    entries=[]
    out.mkdir(parents=True,exist_ok=False)
    cases=[]
    for s in a.cases.split(','):
        qs,ms,ns=s.split(':');q=float(qs);m=int(ms);n=int(ns)
        if n>64 or m>16 or abs(q)>0.005 or n<2 or m<4:
            raise ValueError('HE24 bounded scope violated')
        cases.append((q,m,n))
    for q,m,n in cases:
        runpath=out/f'q{q:+.4f}_m{m}_n{n}'
        runpath.mkdir()
        now=time.perf_counter()
        try:
            result=run_case((str(native),m,n,q,20.,str(runpath/'native_calls'),OWNER_SOURCE_SHA))
            record={'status':'PASS_SCOPED','result':result,'elapsed_s':time.perf_counter()-now}
        except Exception as ex:
            record={'status':'HOLD_FIRST_FAILURE','error':repr(ex),'elapsed_s':time.perf_counter()-now}
        (runpath/'STATUS.json').write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n')
        print(f'{q=:.4f} {m=} {n=} {record["status"]} {record["elapsed_s"]:.2f}s',flush=True)
        entries.append((q,m,n,record))
        if record['status']!='PASS_SCOPED': break
    summary={'schema':'BASS_HE.HE24.native_replay.v1','source_owner':OWNER_SOURCE_SHA,'binary_sha256':expected,
             'he23_execution_parent':'45b940f1d190713eb4c15bd5560112b6c542c9e4','results':[
                 {'q':q,'m':m,'n':n,'status':r['status'], 'T_K':r.get('result',{}).get('temperature_final_K'),
                   'xHII':r.get('result',{}).get('gas_final',[None])[0],
                   'max_implicit_residual':r.get('result',{}).get('max_newton_error'),
                   'n_native':r.get('result',{}).get('native_evaluator_calls'),
                   'number_defect':r.get('result',{}).get('number_defect'),
                   'energy_defect':r.get('result',{}).get('energy_defect')}
                 for q,m,n,r in entries],
             'claim':'HE23 prescribed emissivity, source-age and original Rust point source, NOT upstream Grackle or cosmological EoR'}
    (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2,sort_keys=True,allow_nan=False)+'\n')
    if any(r['status']!='PASS_SCOPED' for _,_,_,r in entries):sys.exit(1)
if __name__=='__main__':main()
