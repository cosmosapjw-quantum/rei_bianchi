#!/usr/bin/env python3
"""Three new-input representation controls only. No sweep and no benchmarking."""
from __future__ import annotations
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np
from scipy.linalg import expm
from radiation_flow import RadiationFlow,solve_three_state

CASES=((.0013,.00011,-.00023),(-.0021,-.00017,.00037),(.0007,.00009,.00013))
GATE=1e-8 # predeclared absolute dimensionless comparison, same parent pilot gate

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--owner-root',type=Path,required=True)
    ap.add_argument('--owner-lock',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args(); lock=json.loads(a.owner_lock.read_text())
    for p,h in lock['files'].items():
        if sha(a.owner_root/p)!=h:raise ValueError('OWNER_HASH_MISMATCH:'+p)
    if a.out.exists():raise FileExistsError('Completed controls are immutable; inspect existing receipt, do not repeat.')
    a.out.mkdir(parents=True)
    sys.path.insert(0,str(a.owner_root/'matter_radiation_20261021'))
    from component_pilot import ComponentReduced
    model=ComponentReduced();flow=RadiationFlow(model.mat)
    records=[]
    for i,targets in enumerate(CASES):
        ref,rd,rm=model.solve(*targets)
        sol,full,d,im=solve_three_state(model,targets,flow)
        delta={k:float(np.max(abs(d[k]-rd[k]))) for k in ('s_over_H','b','E0','E2','signed_Pi_m','signed_Pi_r')}
        state_delta=float(np.max(abs(full-ref.y)))
        y0,_=model.initial(*targets)
        direct=np.stack([expm(float(b)*model.mat)@y0[3:] for b in full[1]],axis=1)
        direct_delta=float(np.max(abs(full[3:]-direct)))
        positive=float(d['sampled_min_angular_brightness'].min())
        passed=max(delta.values())<=GATE and state_delta<=GATE and direct_delta<=1e-13 and positive>0
        np.savez_compressed(a.out/f'control_{i}.npz',x=sol.t,reference_state=ref.y,three_state=sol.y,reconstructed_state=full,
                            **{'new_'+k:d[k] for k in d},**{'reference_'+k:rd[k] for k in rd})
        records.append({'targets_signed_half':list(targets),'initial':im,'reference_nfev':int(ref.nfev),'new_nfev':int(sol.nfev),
                        'max_abs_difference':delta,'full_state_max_abs':state_delta,'spectral_vs_direct_expm_max_abs':direct_delta,
                        'minimum_sampled_brightness':positive,'status':'PASS_SCOPED' if passed else 'FAIL'})
    result={'schema':'PHYS75_THREE_STATE_CONTROLS_V1','status':'PASS_SCOPED' if all(z['status']=='PASS_SCOPED' for z in records) else 'FAIL',
            'owner_files':lock['files'],'code_sha256':sha(Path(__file__).with_name('radiation_flow.py')),
            'new_inputs':3,'actual_IVPs':6,'historical_sweep_replays':0,'benchmark_runs':0,'state_count_before':8,'state_count_after':3,
            'rtol':3e-11,'atol':3e-13,'sample_count_per_history':65,'comparison_absolute_gate':GATE,
            'spectral_eigenvector_condition':flow.condition,'eigen_residual':flow.residual,'cases':records,
            'scope':'Same finite L8 collisionless equations; changed adaptive dimension. No uniform time/angular/roundoff certificate or measured speedup.'}
    (a.out/'RESULT.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result,indent=2))
    return 0 if result['status']=='PASS_SCOPED' else 1
if __name__=='__main__':raise SystemExit(main())
