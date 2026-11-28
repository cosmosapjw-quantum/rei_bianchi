#!/usr/bin/env python3
"""Read-only replay of the preserved R31U point; not a new HH solver/node."""
from __future__ import annotations
import argparse, hashlib, json, os, tempfile
from pathlib import Path
import numpy as np
from metric_cell import diagnose, pullback, affine_endpoint_diagnostic

EXPECTED='565a9ee6d831f5f9e3e69010270f5319aa3328432950efcfda81cfabf325c079'

def insert(base,col,row,ionic):
    # Explicitly the same binary64 *diagnostic* representation as R31V replay.
    # The immutable long-double source snapshot is never rewritten.
    a=np.array(base,dtype=np.complex128,copy=True)
    a[:47,47:]=col;a[47:,:47]=row;a[47:,47:]=ionic
    return a

def compute(path):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED:raise ValueError('snapshot SHA-256 mismatch')
    with np.load(path,allow_pickle=False) as f:d={k:f[k] for k in f.files}
    v=float(d['velocity'])
    if not np.isfinite(v) or v<=0:raise ValueError('positive finite atomic velocity required')
    dt=4/v;q=d['direct_Q']
    if q.shape!=(49,25):raise ValueError('fixed retained subspace identity/shape required')
    o=insert(d['direct_O'],(d['z0_od_O']+d['z4_od_O'])/2,(d['z0_od_O_row']+d['z4_od_O_row'])/2,(d['z0_ion_O']+d['z4_ion_O'])/2)
    conn=insert(d['direct_D'],(d['z0_od_D_col']+d['z4_od_D_col'])/2,(d['z0_od_D_row']+d['z4_od_D_row'])/2,(d['z0_ion_D']+d['z4_ion_D'])/2)
    dot=insert(d['direct_dotO'],(d['z4_od_O']-d['z0_od_O'])/dt,(d['z4_od_O_row']-d['z0_od_O_row'])/dt,(d['z4_ion_O']-d['z0_ion_O'])/dt)
    ro=q.conj().T@o@q;rd=q.conj().T@conn@q;rod=q.conj().T@dot@q
    res=rod-rd-rd.conj().T
    diag=diagnose(ro,res)
    direct=diagnose(q.conj().T@d['direct_O']@q,q.conj().T@(d['direct_dotO']-d['direct_D']-d['direct_D'].conj().T)@q)
    ionic=affine_endpoint_diagnostic(d['z0_ion_O'],d['z4_ion_O'],
              d['z0_ion_D'],d['z4_ion_D'],dt)
    ionic.update(full_HH_interval_bound=False,
       scope='DEFINED_LINEAR_2X2_IONIC_SUBBLOCK_ONLY_NOT_THE_COUPLED_HH_TRAJECTORY',
       minimum_endpoint_overlap_eigenvalue=float(min(
           np.linalg.eigvalsh(d['z0_ion_O']).min(),np.linalg.eigvalsh(d['z4_ion_O']).min())))
    rng=np.random.default_rng(20260929);trials=[]
    for _ in range(32):
        a=rng.normal(size=(25,25))+1j*rng.normal(size=(25,25));u=np.linalg.qr(a)[0]
        t=u@np.diag(rng.uniform(.7,1.4,size=25))
        td=.1*(rng.normal(size=(25,25))+1j*rng.normal(size=(25,25)))
        tx=pullback(ro,rd,rod,t,td);new=diagnose(tx['O'],tx['R'])
        trials.append({'eta_difference':abs(new['eta_svd']-diag['eta_svd']),
                       'residual_covariance_gap':float(np.linalg.norm(tx['R']-t.conj().T@res@t,2))})
    return {'schema':'WU088_R31W_EXISTING_POINT_REPLAY_V1','source_snapshot_sha256':EXPECTED,
      'source_bytes':len(raw),'reduced_dimension':25,'fixed_Q_bytes_sha256':hashlib.sha256(q.tobytes()).hexdigest(),
      'source_dtypes':{k:str(d[k].dtype) for k in d},'diagnostic_dtype':'complex128; not a production precision change',
      'velocity_atomic_units':v,'endpoint_time_separation_atomic_units':dt,
      'hybrid_point':diag,'direct_point':direct,'ionic_affine_subblock':ionic,
      'max_raw_entry_defect':float(np.max(np.abs(dot-conn-conn.conj().T))),
      'neutral_point_dotO_max_entry':float(np.max(np.abs(d['direct_dotO'][:47,:47]))),
      'time_dependent_frame_trials':32,'max_eta_frame_difference':max(x['eta_difference'] for x in trials),
      'max_residual_frame_covariance_gap':max(x['residual_covariance_gap'] for x in trials),
      'trials':trials,'snapshot_changed':hashlib.sha256(Path(path).read_bytes()).hexdigest()!=EXPECTED,
      'affine_cell_bound_instantiated':False,
      'missing_cell_inputs':['complete neutral O/D endpoints in one common coordinate field',
           'continuous neutral provider derivative contract or genuinely affine complete O/D',
           'fixed-rank common subspace on the whole cell; Q(z=2) alone is insufficient',
           'independent source-error and arithmetic enclosures for a physical certificate'],
      'HH_uniform_time_bound':'NOT_ESTABLISHED','HH_transition_error_bound':'NOT_ESTABLISHED',
      'HH_source_error_enclosure':'NOT_ESTABLISHED','new_native_pair_evaluations':0,
      'new_heavy_scientific_nodes':0,'HH_trajectory_runs':0,'production_admitted':False,
      'interpretation':'Stored hybrid point only. No H-skip, dephasing, repair or propagation admitted.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    result=compute(a.input);payload=(json.dumps(result,indent=2,allow_nan=False)+'\n').encode()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=a.out.parent,prefix='.'+a.out.name+'.')
    try:
        with os.fdopen(fd,'wb') as f:f.write(payload);f.flush();os.fsync(f.fileno())
        os.link(tmp,a.out)
    finally:Path(tmp).unlink(missing_ok=True)
    print(json.dumps({k:result[k] for k in ['source_snapshot_sha256','velocity_atomic_units','endpoint_time_separation_atomic_units','max_raw_entry_defect','neutral_point_dotO_max_entry','max_eta_frame_difference','max_residual_frame_covariance_gap','affine_cell_bound_instantiated']},indent=2))
    print('hybrid eta',result['hybrid_point']['eta_svd'],'witness',result['hybrid_point']['witness_rate'],'direct eta',result['direct_point']['eta_svd'])
    return 0
if __name__=='__main__':raise SystemExit(main())
