#!/usr/bin/env python3
"""Fail-closed terminal artifact validation; no scientific provider/native import."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np

AS_RUN={'driver_as_run.py':'driver_sha','base_driver_as_run.py':'base_sha','fixed_grid_as_run.py':'grid_factory_sha','characteristics_as_run.py':'characteristics_sha','events_as_run.py':'events_sha','GRID.json':'grid_sha'}
FILES=['IDENTITY.json','RESULT.json','FIRST_FAILURE.json','history.npz','LAST_ACCEPTED.npz','EVENTS.json',*AS_RUN]
GAS_KEYS=['xHII','xHeII','xHeIII','xHeI','T_K']
EV=1.602176634e-12;KB=1.380649e-16;FHE=.24/(4*.76)

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def require(value,message):
    if not value:raise ValueError(message)
def verify_hashes(root,hashes):
    for name,expected in hashes.items():
        require(not Path(name).is_absolute() and '..' not in Path(name).parts,'UNSAFE_MANIFEST_PATH')
        require(sha(Path(root)/name)==expected,'STALE_ARTIFACT:'+name)
def npz(path):
    with np.load(path,allow_pickle=False) as f:return {k:f[k].copy() for k in f.files}

def gas_values(physical):
    h,he1,he2,w=physical[:4]
    temp=2*w*EV/(3*KB*(1+FHE+h+FHE*(he1+2*he2)))
    return np.array([h,he1,he2,1-he1-he2,temp])

def validate_payload(result,failure,history,last,boundaries):
    require(result['status']=='FAILED_PRESERVED','TERMINAL_FAILURE_REQUIRED')
    require(failure==result['failure'],'FAILURE_RESULT_MISMATCH')
    require(failure['type']=='TimeoutError' and failure['message']=='DECLARED_WALL_BUDGET_EXCEEDED','ONLY_DECLARED_WALL_BUDGET_RESUMABLE')
    checks=result['checks']
    require(checks['whole_interval'] is False,'ALREADY_COMPLETE')
    for key in ('sampled_positive','accepted_positive','accepted_finite','accepted_gas_domain','energy_ledger','number_ledger'):
        require(checks.get(key) is True,'PREVIOUS_GATE_FAILED:'+key)
    n=result['n_nodes'];u=history['u'];states=history['scaled_states'];scales=history['scales'];lastu=float(last['u'])
    require(0<lastu<1 and np.isfinite(lastu),'LAST_U_NOT_INTERIOR')
    require(lastu==failure['last_accepted_u'],'LAST_U_FAILURE_MISMATCH')
    require(scales.shape==(n+10,) and np.isfinite(scales).all() and (scales>0).all(),'INVALID_SCALES')
    require(np.array_equal(last['scales'],scales),'LAST_SCALES_MISMATCH')
    expected=np.linspace(0.,1.,129);prefix=expected[expected<=lastu]
    require(np.array_equal(u,prefix),'EPOCH_PREFIX_GAP_DUPLICATE_OR_OVERLAP')
    require(len(result['history'])==len(u),'JSON_PREFIX_LENGTH')
    require(states.shape==(len(u),n+10) and np.isfinite(states).all(),'HISTORY_STATE_SHAPE_FINITE')
    require(last['scaled_y'].shape==(n+10,) and np.isfinite(last['scaled_y']).all(),'LAST_STATE_SHAPE_FINITE')
    for v in np.vstack([states,last['scaled_y']]):
        phys=v*scales;h,he1,he2,hei,temp=gas_values(phys)
        require(np.isfinite(phys).all() and 0<=h<=1 and he1>=0 and he2>=0 and hei>=0 and 1<=temp<=1e6,'INVALID_SAVED_GAS')
        require((phys[4:4+n]>=0).all(),'INVALID_SAVED_PHOTONS')
    if lastu==u[-1]:require(np.array_equal(last['scaled_y'],states[-1]),'OVERLAP_STATE_MISMATCH')
    for key in ('q','mu','weights'):
        require(history[key].shape==(n,) and np.isfinite(history[key]).all(),'SAVED_GRID_SHAPE_FINITE:'+key)
    require((history['q']>0).all() and (history['weights']>0).all() and (abs(history['mu'])<=1).all(),'SAVED_GRID_DOMAIN')
    b=np.asarray(boundaries);seg=result['completed_segments']
    require(b.ndim==1 and len(b)>2 and b[0]==0. and b[-1]==1. and np.isfinite(b).all() and (np.diff(b)>0).all(),'EVENT_BOUNDARIES_INVALID')
    require(type(seg) is int and 0<=seg<len(b)-1 and failure['completed_segments']==seg,'COMPLETED_SEGMENT_MISMATCH')
    require(b[seg]<=lastu<b[seg+1],'LAST_STATE_NOT_CURRENT_SEGMENT')
    return dict(resume_u=lastu,resume_segment=seg,prefix_samples=len(u),remaining_samples=129-len(u),end_time_s=None)

def terminal_checkpoint(root):
    root=Path(root);identity=read(root/'IDENTITY.json');result=read(root/'RESULT.json');failure=read(root/'FIRST_FAILURE.json');events=read(root/'EVENTS.json')
    require('continuation' not in identity,'ONLY_ONE_CONTINUATION_PHASE_ALLOWED')
    args=identity['args'];grid=read(root/'GRID.json')
    require(identity['grid_kind']=='fixed_q_composite_gauss' and identity['grid_order']==2 and args['energy']==768 and args['angle']==2 and args['shear']==0. and args['rtol']==1e-11 and args['max_step']==1/256 and args['max_wall_seconds']==5400.,'ONLY_ORIGINAL_GAUSS2_FINE_RESUMABLE')
    require(grid['order']==2 and grid['n_energy']==768 and grid['n_mu']==2 and grid['arrays_sha256']==identity['grid_arrays_sha256'],'GRID_IDENTITY_MISMATCH')
    verify_hashes(root,{name:identity[key] for name,key in AS_RUN.items()})
    data,last=npz(root/'history.npz'),npz(root/'LAST_ACCEPTED.npz')
    decision=validate_payload(result,failure,data,last,events['boundaries'])
    require(len(events['boundaries'])-1==identity['segment_count'] and len(events['events'])==identity['event_count'],'EVENT_COUNT_MISMATCH')
    require(all(np.array_equal(data[k],grid[j]) for k,j in [('q','q_eV'),('mu','mu0'),('weights','weights')]),'GRID_ARRAY_MISMATCH')
    return identity,result,events,data,last,decision

def make_manifest(root):
    root=Path(root).resolve();identity,result,events,data,last,decision=terminal_checkpoint(root)
    return dict(schema='rei.q1a.single_wall_continuation.v1',original_directory=str(root),original_files_sha256={name:sha(root/name) for name in FILES},
      original_identity_sha256=sha(root/'IDENTITY.json'),original_result_sha256=sha(root/'RESULT.json'),decision=decision,
      maximum_additional_wall_seconds=600.,maximum_additional_phases=1,original_phase_status='FAILED_PRESERVED',
      validator_sha256=sha(__file__),production_execution='NOT_AUTHORIZED_BY_MANIFEST',comparison='UNSUPPORTED_UNTIL_INDEPENDENT_CONTINUATION_CHAIN_REVIEW')

def load_manifest(path,expected_sha):
    path=Path(path);require(sha(path)==expected_sha,'MANIFEST_SHA_MISMATCH');manifest=read(path)
    require(manifest['schema']=='rei.q1a.single_wall_continuation.v1' and manifest['maximum_additional_wall_seconds']==600. and manifest['maximum_additional_phases']==1,'MANIFEST_SCOPE')
    require(sha(__file__)==manifest['validator_sha256'],'VALIDATOR_BYTES_CHANGED')
    root=Path(manifest['original_directory']);require(set(manifest['original_files_sha256'])==set(FILES),'INCOMPLETE_TERMINAL_HASH_CHAIN');verify_hashes(root,manifest['original_files_sha256'])
    checkpoint=terminal_checkpoint(root);require(checkpoint[-1]==manifest['decision'],'MANIFEST_DECISION_CHANGED')
    return manifest,checkpoint

def main():
    parser=argparse.ArgumentParser();parser.add_argument('terminal_run',type=Path);parser.add_argument('output_manifest',type=Path);args=parser.parse_args()
    value=make_manifest(args.terminal_run)
    with args.output_manifest.open('x') as h:json.dump(value,h,indent=2,allow_nan=False);h.write('\n')
    print(json.dumps(dict(manifest=str(args.output_manifest),sha256=sha(args.output_manifest),decision=value['decision']),indent=2))
if __name__=='__main__':main()
