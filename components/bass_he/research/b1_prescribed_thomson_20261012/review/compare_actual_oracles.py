"""Compare saved B1 results with independent exact/direct-matrix oracles.

No time evolution, history integration, or full suite is launched. One actual
candidate collision-stage call is checked on the saved B state and full
production energy grid. The complete error arrays are saved separately.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.linalg import expm

from b1_independent_oracles import (
    collisionless_quadrupole, backward_lrs, direct_axisym_collision_matrix,
    planck_occupation,
)

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT))
import b1_transport as candidate

begin=time.perf_counter()
names=['B0','F','M','M_F','B','B_F']
states={}
identities={}
receipts={}
for case in names:
    p=ROOT/f'runs/base_{case}_t128_mu24_e257/result.npz'
    with np.load(p,allow_pickle=False) as z:
        states[case]={k:z[k].copy() for k in z.files}
    raw=p.read_bytes()
    identities[str(p.relative_to(ROOT))]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
    receipts[case]=json.loads(p.with_name('RECEIPT.json').read_text())
    if receipts[case]['status']!='EXECUTED_SCOPED_PYTHON':
        raise ValueError('RESULT_NOT_COMPLETED')

b0=states['B0']
guard=(b0['y']>=.1*(1-1e-14))&(b0['y']<=10*(1+1e-14))
y=b0['y'][guard]
oracle_q2=[]
oracle_ib=[]
oracle_quad_residual=[]
for b in b0['b']:
    got=collisionless_quadrupole(planck_occupation,y,float(b),256)
    control=collisionless_quadrupole(planck_occupation,y,float(b),128)
    oracle_q2.append(got['q2'])
    oracle_ib.append(y**3*got['monopole_mu_integral']/2)
    oracle_quad_residual.append(got['q2']-control['q2'])
oracle_q2=np.asarray(oracle_q2)
oracle_ib=np.asarray(oracle_ib)
oracle_quad_residual=np.asarray(oracle_quad_residual)
actual_q2=b0['q2'][:,guard]
actual_ib=b0['Ibar_y3'][:,guard]
qerr=actual_q2-oracle_q2
iberr=actual_ib/oracle_ib-1
mu0,g=backward_lrs(b0['mu'],float(b0['b'][-1]))
final_screen_exact=.5*planck_occupation(g[:,None]*y[None,:])
screen_actual=b0['final_screen'][:,guard,:]
screen_rel=screen_actual/final_screen_exact[...,None]-1
iq=np.unravel_index(np.argmax(abs(qerr)),qerr.shape)
ii=np.unravel_index(np.argmax(abs(iberr)),iberr.shape)

null_results={}
for case in ['F','M','M_F']:
    ss=states[case]
    if not np.array_equal(ss['y'],b0['y']):
        raise ValueError('BASE_ENERGY_GRIDS_DIFFER')
    f0=.5*planck_occupation(y)
    null_results[case]={
        'max_abs_q2_all_snapshots_guard':float(np.max(abs(ss['q2'][:,guard]))),
        'max_pL_max_all_snapshots_guard':float(np.max(ss['pL_max'][:,guard])),
        'max_abs_Qbar_over_I_all_snapshots_guard':float(np.max(abs(ss['Qbar_over_I'][:,guard]))),
        'max_final_screen_relative_to_isotropic_initial':float(np.max(abs(ss['final_screen'][:,guard,:]/f0[None,:,None]-1))),
        'max_U_over_I_before_axisymmetry_reduction':receipts[case]['diagnostics']['max_screen_U_over_I'],
        'max_V_over_I_before_axisymmetry_reduction':receipts[case]['diagnostics']['max_screen_V_over_I'],
    }

# Dense matrix oracle, applied to the actual final B state.
bb=states['B']
f=bb['final_screen']
frozen=dict(np.load(ROOT/'inputs/B1_FROZEN_PROJECTED_INPUTS.npz',allow_pickle=False))
depth=float(frozen['depth_B'].reshape(128,-1).sum(axis=1)[-1])
matrix=direct_axisym_collision_matrix(bb['mu'],bb['wmu'])
dense=expm(depth*matrix)@np.concatenate([f[...,0],f[...,1]],axis=0)
dense=np.stack([dense[:len(bb['mu'])],dense[len(bb['mu']):]],axis=-1)
bridge=candidate.LRSBridge(len(bb['mu']),bb['lny'],8)
candidate_stage=bridge.scatter(f,depth)
stage_rel=candidate_stage[:,guard,:]/dense[:,guard,:]-1
stage_abs=candidate_stage[:,guard,:]-dense[:,guard,:]
dense_trace=(bb['wmu']@(dense[...,0]+dense[...,1]))
trace_before=(bb['wmu']@(f[...,0]+f[...,1]))

for p in [ROOT/'b1_transport.py',ROOT/'native/python_thomson.py',ROOT/'native/upstream_polarization.py',
          ROOT/'inputs/B1_FROZEN_PROJECTED_INPUTS.npz',HERE/'b1_independent_oracles.py',Path(__file__)]:
    raw=p.read_bytes(); identities[str(p.relative_to(ROOT))]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}

rawpath=HERE/'B1_ACTUAL_ORACLE_COMPARISON_ARRAYS.npz'
np.savez_compressed(rawpath,y=y,u=b0['u'],z_mean=b0['z_mean'],beta=b0['b'],
    exact_q2=oracle_q2,candidate_q2=actual_q2,q2_error=qerr,
    exact_Ibar_y3=oracle_ib,candidate_Ibar_y3=actual_ib,Ibar_relative_error=iberr,
    oracle_GL256_minus_GL128_q2=oracle_quad_residual,
    final_B0_screen_relative_error=screen_rel,
    collision_candidate_minus_dense_guard=stage_abs,
    collision_candidate_relative_to_dense_guard=stage_rel)
raw=rawpath.read_bytes()
finalreport=[]
for jj in b0['report_indices']:
    k=int(np.flatnonzero(np.flatnonzero(guard)==jj)[0])
    finalreport.append({'y':float(b0['y'][jj]),'q2_candidate':float(actual_q2[-1,k]),
                       'q2_exact':float(oracle_q2[-1,k]),'q2_error':float(qerr[-1,k]),
                       'Ibar_relative_error':float(iberr[-1,k]),
                       'pL_max_candidate':float(b0['pL_max'][-1,jj])})

null_pass=all(v['max_abs_q2_all_snapshots_guard']<2e-12 and v['max_pL_max_all_snapshots_guard']<2e-12 for v in null_results.values())
collision_pass=float(np.max(abs(stage_rel)))<2e-12
result={
  'role':'INDEPENDENT_THEORY_ORACLE_ASSISTANT_NOT_DECISION_REVIEWER',
  'status':'SAVED_RESULTS_COMPARED_NO_NEW_FULL_SUITE',
  'command':'python3 /workspace/scratch/7fd51143e473/b1_research_20261012/review/compare_actual_oracles.py',
  'candidate_backend':'EXPLICIT_EXISTING_BASS_PYTHON',
  'native_rust_calls':0,
  'new_full_transport_executions':0,
  'new_targeted_candidate_collision_stage_calls':bridge.collision.calls,
  'new_upstream_energy_slice_calls':bridge.collision.upstream_energy_slice_calls,
  'input_identities':identities,
  'scope':{'case':'B0 exact all guarded energies and all 33 saved times; F/M/M_F nulls; one saved-B collision stage',
           'n_guarded_energies':len(y),'n_saved_times':len(b0['b']),
           'guarded_y_min':float(y.min()),'guarded_y_max':float(y.max()),
           'oracle_angular_nodes':256,'candidate_angular_nodes':len(b0['mu'])},
  'B0':{'q2_max_abs_error':float(np.max(abs(qerr))),
        'q2_worst':{'saved_time_index':int(iq[0]),'z_mean':float(b0['z_mean'][iq[0]]),'y':float(y[iq[1]]),
                    'actual':float(actual_q2[iq]),'exact':float(oracle_q2[iq])},
        'Ibar_y3_max_relative_error':float(np.max(abs(iberr))),
        'Ibar_y3_worst':{'saved_time_index':int(ii[0]),'z_mean':float(b0['z_mean'][ii[0]]),'y':float(y[ii[1]])},
        'final_screen_max_relative_error':float(np.max(abs(screen_rel))),
        'max_pL_all_snapshots_guard':float(np.max(b0['pL_max'][:,guard])),
        'oracle_GL128_GL256_q2_max_abs':float(np.max(abs(oracle_quad_residual))),
        'final_report_y':finalreport,
        'per_saved_time_max_q2_error':np.max(abs(qerr),axis=1).tolist(),
        'acceptance_note':'Observed discretization errors. No new absolute B0 science threshold invented; owner must assess with target response and paired refinements.'},
  'isotropic_nulls':null_results,
  'isotropic_nulls_within_existing_2e_minus12_symmetry_scale':null_pass,
  'one_actual_B_collision_stage':{
      'state':'base_B_t128_mu24_e257 final_screen',
      'depth':'last coarse B cell; independent probe on final saved state, not chronological continuation',
      'depth_value':depth,'dense_matrix_shape':list(matrix.shape),
      'max_abs_guard':float(np.max(abs(stage_abs))),
      'max_relative_guard':float(np.max(abs(stage_rel))),
      'dense_trace_conservation_max_relative_all_energy':float(np.max(abs(dense_trace/trace_before-1))),
      'candidate_upstream_calls':bridge.collision.upstream_energy_slice_calls,
      'within_existing_2e_minus12_operator_scale':collision_pass,
      'reference_independence':'Direct axisymmetric moment generator plus scipy expm; candidate packing, kernel eigenprojection, and three-term exponential not shared. Same physical Thomson kernel and angular quadrature are shared.'},
  'raw_arrays':{'path':str(rawpath.relative_to(ROOT)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},
  'claim_limits':['No native Rust execution/parity','No final PROMOTE decision',
                 'B0 oracle does not itself bound the small paired history response',
                 'Finite grid and time refinement differences are not rigorous enclosures'],
  'wall_seconds':time.perf_counter()-begin,
}
out=HERE/'B1_ACTUAL_ORACLE_COMPARISON.json'
out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps({k:result[k] for k in ['status','scope','B0','isotropic_nulls',
      'isotropic_nulls_within_existing_2e_minus12_symmetry_scale','one_actual_B_collision_stage',
      'raw_arrays','wall_seconds']},indent=2))
assert null_pass and collision_pass
