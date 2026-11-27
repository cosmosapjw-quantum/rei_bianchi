"""HE24 opt-in finite frozen-cell source timing A/B on actual HE23 coupled owner.

The original HE23 source/chemistry files, binary and tolerances are immutable.
An isolated wrapper substitutes only the *newborn* within-cell absorption factor:
 N_new_surv=N_new * phi1(-lambda*dt), rather than N_new*exp(-lambda*dt).
Already-existing photons retain HE23 exp(-tau) survival. This is exact only
for a uniform-in-proper-time newborn source and gas/frequency frozen inside
one chemical substep. It is NOT full MD14, PR150 or global physical history.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,sys,time
import numpy as np
try:
    from source_age_bias import phi1_minus
except ImportError:
    from .source_age_bias import phi1_minus

EXPECTED_BIN='981ad6dde18be7951c6b0200a49e6482b0e6fae644437197375bdd18ced5eafe'

def activate(he23_src):
    sys.path.insert(0,str(he23_src))
    import he22_contract as hc
    import he22_coupled as hcou
    from he21_photo import neutral,sigma_cm2,C_CM_S,EV_ERG,BIND_EV,admissible
    old_map=hc.photomap
    old_step=hcou.solve_midpoint
    state={'prior_count':0,'new_count':0,'calls':0,'steps':0,'max_ledger':0.}
    def new_map(gas,counts,energy,nH_cm3,dt_s):
        gas=np.asarray(gas,dtype=float);n=np.asarray(counts,dtype=float)
        energy=np.asarray(energy,dtype=float)
        if not(admissible(gas) and n.ndim==1 and energy.shape==n.shape
            and np.isfinite(n).all() and (n>=0).all() and np.isfinite(energy).all()
            and (energy>0).all() and np.isfinite(dt_s) and dt_s>0 and np.isfinite(nH_cm3) and nH_cm3>0):
            raise ValueError('HE24_PHOTO_INPUT_DOMAIN')
        frac=neutral(gas)
        if (frac < 0).any():raise ValueError('HE24_ABSORBER_NEGATIVE')
        lam=C_CM_S*nH_cm3*sigma_cm2(energy)*frac[None,:]
        all_lam=lam.sum(axis=1);tau=all_lam*dt_s
        split=state['prior_count']
        if not(0<=split<=len(n)):raise RuntimeError('HE24_SOURCE_AGE_OWNERSHIP')
        fresh=np.zeros_like(n);fresh[split:]=n[split:]
        old=n-fresh
        ph=phi1_minus(tau)
        surviving=old*np.exp(-tau)+fresh*ph
        lost=(old*(-np.expm1(-tau)) + fresh*(1-ph))
        shares=np.divide(lam,all_lam[:,None],out=np.zeros_like(lam),where=all_lam[:,None]>0)
        ev=lost[:,None]*shares
        species=ev.sum(axis=0)
        heat=np.sum(ev*(energy[:,None]-BIND_EV[None,:]),axis=0)
        if (heat < -1e-20).any():raise ArithmeticError('HE24_NEGATIVE_PHOTOHEAT')
        gamma=np.divide(species,dt_s*frac,out=np.zeros(3),where=frac>0)
        power=np.divide(heat*EV_ERG,dt_s*frac,out=np.zeros(3),where=frac>0)
        if ((frac==0)&(species>0)).any():raise ArithmeticError('HE24_UNOWNED_EVENT')
        incoming=float(np.dot(n,energy));final=float(np.dot(surviving,energy))
        absorbed=float(np.dot(species,BIND_EV)+heat.sum())
        state['calls']+=1
        state['max_ledger']=max(state['max_ledger'],abs(incoming-final-absorbed))
        return hc.PhotoMap(surviving,species,heat,gamma,power,
            float(n.sum()-surviving.sum()-species.sum()),incoming-final-absorbed,incoming)
    def step(gas0, photons0, energy, nh, dt, native, *args, **kw):
        size=len(photons0)
        prior=state['prior_count']
        if size<prior:raise RuntimeError('HE24_UNEXPECTED_PHOTON_PRUNING')
        state['new_count']=size-prior
        r=old_step(gas0,photons0,energy,nh,dt,native,*args,**kw)
        state['prior_count']=size
        state['steps']+=1
        return r
    hc.photomap=new_map
    hcou.solve_midpoint=step
    return state

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--he23-root',type=pathlib.Path,required=True)
    p.add_argument('--native',type=pathlib.Path,required=True)
    p.add_argument('--out',type=pathlib.Path,required=True)
    p.add_argument('--cases',type=str,default='0:4:2,0:4:4,0:4:8,0:4:16,0:4:32')
    a=p.parse_args()
    if hashlib.sha256(a.native.read_bytes()).hexdigest()!=EXPECTED_BIN:
        raise ValueError('HE24_WRONG_NATIVE_BIN')
    a.out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(a.he23_root/'src'))
    from run_native import run_case
    from he22_native_client import OWNER_SOURCE_SHA
    # Isolated process per case prevents accidental reuse of prior-count state.
    import subprocess
    cases=[]
    for ss in a.cases.split(','):
        q,ms,ns=ss.split(':');q=float(q);m=int(ms);n=int(ns)
        if abs(q)>.005 or m>16 or n>64:raise ValueError('HE24_SCOPE_LIMIT')
        cases.append((q,m,n))
    if len(cases)!=1:
        raise ValueError('use one case per process for strict frozen state')
    q,m,n=cases[0]
    state=activate(a.he23_root/'src')
    tag=f'q{q:+.4f}_m{m}_n{n}'
    start=time.perf_counter()
    try:
        r=run_case((str(a.native),m,n,q,20.,str(a.out/'native_calls'),OWNER_SOURCE_SHA))
        rec={'status':'PASS_SCOPED','result':r}
    except Exception as err:
        rec={'status':'HOLD','exception_type':type(err).__name__,'error':str(err)}
    rec.update(schema='HE24.continuous_newborn_frozen_opacity.v1',
            elapsed_s=time.perf_counter()-start,case=tag,
            original_native_binary_sha256=EXPECTED_BIN,
            frozen_cell_approximation='newborn uniform proper-time emission, E and gas opacity frozen endpoint',
            source_timing_only_perturbation=True,
            activated_steps=state['steps'],kernel_calls=state['calls'],max_photo_ledger=state['max_ledger'])
    (a.out/'RESULT.json').write_text(json.dumps(rec,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(tag,rec['status'], 'elapsed',rec['elapsed_s'],'T',rec.get('result',{}).get('temperature_final_K'),
          'maxledger',state['max_ledger'],'rhs',rec.get('result',{}).get('native_evaluator_calls'),flush=True)
    if rec['status']!='PASS_SCOPED':raise SystemExit(1)
if __name__=='__main__':main()
