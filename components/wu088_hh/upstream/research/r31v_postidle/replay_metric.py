#!/usr/bin/env python3
"""Existing R31U snapshot replay and conditional-metric research; no H kernels."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.linalg import eigh
from metric_controls import diagnose, whiten, uncertainty_envelope

EXPECTED = '565a9ee6d831f5f9e3e69010270f5319aa3328432950efcfda81cfabf325c079'


def insert(base, col, row, ionic):
    a=np.array(base,dtype=np.complex128,copy=True)
    a[:47,47:]=col;a[47:,:47]=row;a[47:,47:]=ionic
    return a


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    if args.out.exists():raise FileExistsError(args.out)
    if hashlib.sha256(args.input.read_bytes()).hexdigest()!=EXPECTED:
        raise ValueError('R31U input snapshot identity mismatch')
    with np.load(args.input,allow_pickle=False) as f:
        d={k:f[k] for k in f.files}
    dt=4/float(d['velocity']);q=d['direct_Q']
    o=insert(d['direct_O'],(d['z0_od_O']+d['z4_od_O'])/2,
             (d['z0_od_O_row']+d['z4_od_O_row'])/2,(d['z0_ion_O']+d['z4_ion_O'])/2)
    dv=insert(d['direct_D'],(d['z0_od_D_col']+d['z4_od_D_col'])/2,
              (d['z0_od_D_row']+d['z4_od_D_row'])/2,(d['z0_ion_D']+d['z4_ion_D'])/2)
    dot=insert(d['direct_dotO'],(d['z4_od_O']-d['z0_od_O'])/dt,
               (d['z4_od_O_row']-d['z0_od_O_row'])/dt,(d['z4_ion_O']-d['z0_ion_O'])/dt)
    r=dot-dv-dv.conj().T
    reduced_o=q.conj().T@o@q;reduced_r=q.conj().T@r@q
    result=diagnose(reduced_o,reduced_r)
    spectrum=eigh(reduced_r,reduced_o,eigvals_only=True)
    result['generalized_eigenvalue_radius']=float(max(abs(spectrum)))
    result['spectral_crosscheck_gap']=abs(result['eta']-result['generalized_eigenvalue_radius'])
    w=whiten(reduced_o,reduced_r)
    result['minimum_frobenius_connection_correction']=float(np.linalg.norm(w,'fro')/2)
    result['unwhitened_max_entry_half_residual']=float(np.max(np.abs(reduced_r))/2)
    # A basis-coordinate change is a congruence, not a physical new state.
    rng=np.random.default_rng(20260928);invariance=[]
    for _ in range(64):
        a=rng.normal(size=reduced_o.shape)+1j*rng.normal(size=reduced_o.shape)
        u=np.linalg.qr(a)[0];t=u@np.diag(rng.uniform(.5,2,size=len(u)))
        test=diagnose(t.conj().T@reduced_o@t,t.conj().T@reduced_r@t)['eta']
        invariance.append(abs(test-result['eta']))
    # Conditional bound validation on synthetic Hermitian data, not an assigned
    # error bar for the HH input. Off-diagonal perturbations do not commute.
    violations=0;max_roundoff_overshoot=0.;max_relative_slack=0.
    for _ in range(1000):
        a=rng.normal(size=(4,4))+1j*rng.normal(size=(4,4));r0=a+a.conj().T
        a=rng.normal(size=(4,4))+1j*rng.normal(size=(4,4));s=a+a.conj().T
        a=rng.normal(size=(4,4))+1j*rng.normal(size=(4,4));e=a+a.conj().T
        eo=float(rng.uniform(0,.8));er=float(rng.uniform(0,1))
        s*=eo/np.linalg.norm(s,2);e*=er/np.linalg.norm(e,2)
        eta=float(np.linalg.norm(r0,2));lo,hi=uncertainty_envelope(eta,eo,er)
        truth=diagnose(np.eye(4)+s,r0+e)['eta']
        overshoot=max(0.,lo-truth,truth-hi);max_roundoff_overshoot=max(max_roundoff_overshoot,overshoot)
        violations+=overshoot>1e-11*max(1.,hi)
        max_relative_slack=max(max_relative_slack,(hi-truth)/max(1.,hi))
    output={'schema':'WU088_R31V_METRIC_RESEARCH_V1','source_snapshot_sha256':EXPECTED,
        'representation':'R31U instantaneous z=2 construction, existing neutral block; binary64 diagnostic',
        'reduced_dimension':int(q.shape[1]),'velocity_atomic_units':float(d['velocity']),
        'time_interval_atomic_units':dt,'instantaneous':result,
        'general_linear_coordinate_trials':64,'max_eta_invariance_difference':max(invariance),
        'synthetic_conditional_envelope_trials':1000,'envelope_violations':int(violations),
        'maximum_roundoff_overshoot':max_roundoff_overshoot,
        'native_kernel_calls':0,'new_heavy_scientific_nodes':0,'trajectory_runs':0,
        'uniform_time_bound':'NOT_ESTABLISHED','HH_input_error_enclosure':'NOT_ESTABLISHED',
        'repair_applied_to_source':False,'scientific_gate_changed':False}
    with args.out.open('x') as f:json.dump(output,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(output,indent=2))
    return 0


if __name__=='__main__':raise SystemExit(main())
