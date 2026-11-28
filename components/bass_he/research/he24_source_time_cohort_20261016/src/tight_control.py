"""HE24 diagnostic: tighten HE23 Newton stopping *without changing original code*.
The default HE23 3e-12 is NEVER relaxed. Independent optical/energy gates remain.
This is a controlled perturbation of nonlinear-solver accuracy, not a new physics model.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, sys, time

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--he23-root',type=pathlib.Path,required=True)
    p.add_argument('--native',type=pathlib.Path,required=True)
    p.add_argument('--out',type=pathlib.Path,required=True)
    p.add_argument('--tolerance',type=float,default=3e-14)
    p.add_argument('--cases',default='0:4:8,0:4:16,0:4:32')
    a=p.parse_args()
    if not(0<a.tolerance<=3e-12):raise ValueError('do not relax original Newton tolerance')
    digest=hashlib.sha256(a.native.read_bytes()).hexdigest()
    if digest!='981ad6dde18be7951c6b0200a49e6482b0e6fae644437197375bdd18ced5eafe':
        raise RuntimeError('source mismatched')
    sys.path.insert(0,str(a.he23_root/'src'))
    import he22_contract,he22_coupled
    from run_native import run_case
    from he22_native_client import OWNER_SOURCE_SHA
    old=he22_coupled.solve_midpoint
    def strict(*args,**kwargs):
        return old(*args,**{**kwargs,'tolerance':a.tolerance})
    he22_coupled.solve_midpoint=strict
    a.out.mkdir(parents=True,exist_ok=False)
    results=[]
    for s in a.cases.split(','):
        q,m,n=map(float,s.split(':'));m=int(m);n=int(n)
        if n>64 or m>16 or abs(q)>.005:raise ValueError('scope')
        out=a.out/f'q{q:+.4f}_m{m}_n{n}';out.mkdir()
        start=time.perf_counter()
        try:
            r=run_case((str(a.native),m,n,q,20.,str(out/'native_calls'),OWNER_SOURCE_SHA))
            rec={'status':'PASS_SCOPED','result':r}
        except Exception as e:
            rec={'status':'HOLD','error':repr(e)}
        rec['elapsed_s']=time.perf_counter()-start
        (out/'RESULT.json').write_text(json.dumps(rec,indent=2,allow_nan=False)+'\n')
        results.append({'q':q,'m':m,'n':n,'status':rec['status'], 'T_K':rec.get('result',{}).get('temperature_final_K'),
             'energy_defect':rec.get('result',{}).get('energy_defect'), 'native_evaluator_calls':rec.get('result',{}).get('native_evaluator_calls')})
        print(q,m,n,rec['status'],rec['elapsed_s'],results[-1],flush=True)
        if rec['status']!='PASS_SCOPED':break
    record={'schema':'HE24.tight_newton_control.v1','original_tolerance':3e-12,'tighter_tolerance':a.tolerance,
            'original_energy_gate_unchanged':True,'original_microphysics_unchanged':True,
            'binary_sha256':digest,'cases':results}
    (a.out/'SUMMARY.json').write_text(json.dumps(record,indent=2)+'\n')
    if any(x['status']!='PASS_SCOPED' for x in results):raise SystemExit(1)
if __name__=='__main__':main()
