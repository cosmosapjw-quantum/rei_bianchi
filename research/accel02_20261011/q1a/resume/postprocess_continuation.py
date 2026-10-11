#!/usr/bin/env python3
"""Bind two-phase evidence before unchanged saved-state moment reconstruction.

Writes a deliberately unsupported-by-legacy-comparator status. Independent
review must explicitly admit operator-equivalent restart provenance first.
"""
from __future__ import annotations
import argparse,importlib.util,json,sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import checkpoint as cp

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def verify_chain(run):
    run=Path(run);identity=cp.read(run/'IDENTITY.json');result=cp.read(run/'RESULT.json')
    chain=cp.read(run/'CONTINUATION.json');manifest=cp.read(run/'CONTINUATION_MANIFEST.json');pred=run/'predecessor'
    cp.require(chain['schema']=='rei.q1a.executed_continuation_chain.v1','CHAIN_SCHEMA')
    cp.require(cp.sha(cp.__file__)==manifest['validator_sha256'],'CURRENT_VALIDATOR_BYTES_CHANGED')
    cp.require(cp.sha(run/'CONTINUATION.json')==identity['continuation']['chain_sha256']==result['continuation']['chain_sha256'],'CHAIN_BINDING')
    cp.require(cp.sha(run/'CONTINUATION_MANIFEST.json')==chain['manifest_sha256'],'MANIFEST_BINDING')
    cp.require(chain['original_files_sha256']==manifest['original_files_sha256'],'PREDECESSOR_HASH_CHAIN')
    cp.verify_hashes(pred,chain['original_files_sha256'])
    pi,pr,pe,ph,pl,pd=cp.terminal_checkpoint(pred)
    cp.require({k:v for k,v in identity.items() if k!='continuation'}==pi,'ORIGINAL_OPERATOR_IDENTITY_CHANGED')
    cp.require(cp.sha(run/'resume_driver_as_run.py')==chain['resume_driver_sha256']==identity['continuation']['resume_driver_sha256'],'RESUME_DRIVER_BINDING')
    cp.require(cp.sha(run/'resume_checkpoint_as_run.py')==chain['resume_validator_sha256']==identity['continuation']['resume_validator_sha256']==manifest['validator_sha256'],'RESUME_VALIDATOR_BINDING')
    cp.require(chain['original_driver_sha256']==pi['driver_sha'],'ORIGINAL_DRIVER_BINDING')
    cp.require(chain['extra_bdf_initializations']==1 and chain['solver_internal_state_restored'] is False and chain['tolerance_changes'] is False and chain['physics_changes'] is False,'CONTINUATION_SCOPE')
    cp.require(0<chain['additional_wall_budget_s']<=600. and chain['start_u']==pd['resume_u'] and chain['start_segment']==pd['resume_segment'] and chain['prefix_samples']==pd['prefix_samples'],'CONTINUATION_BOUNDARIES')
    start=cp.read(run/'CONTINUATION_START.json')
    cp.require(cp.sha(run/'CONTINUATION_START.json')==result['continuation']['start_evidence_sha256'],'CONTINUATION_START_BINDING')
    import hashlib
    cp.require(start['u']==pd['resume_u'] and start['segment']==pd['resume_segment'] and start['scaled_state_sha256']==hashlib.sha256(np.asarray(pl['scaled_y'],dtype='<f8').tobytes()).hexdigest(),'CONTINUATION_START_STATE_BINDING')
    cp.require(start['row']['time_s']==pd['resume_u']*result['history'][-1]['time_s'],'CONTINUATION_START_TIME_BINDING')
    cp.require(result['max_endpoint_energy_ledger']>=abs(start['row']['energy_ledger_scaled']) and result['max_endpoint_number_ledger']>=abs(start['row']['number_ledger_scaled']),'CONTINUATION_START_LEDGER_OMITTED')
    h=cp.npz(run/'history.npz');k=pd['prefix_samples']
    cp.require(np.array_equal(h['u'][:k],ph['u']) and np.array_equal(h['scaled_states'][:k],ph['scaled_states']),'PREFIX_OVERWRITTEN')
    cp.require(result['history'][:k]==pr['history'],'JSON_PREFIX_OVERWRITTEN')
    for key in ('scales','q','mu','weights'):cp.require(np.array_equal(h[key],ph[key]),'SAVED_COORDINATE_CHANGED:'+key)
    for key in ('rhs_calls','jac_calls','max_local_number','max_local_energy','max_endpoint_energy_ledger','max_endpoint_number_ledger','max_energy_ledger','max_number_ledger','max_one_sided_relative_energy_shift'):
        cp.require(result[key]>=pr[key],'PRIOR_ACCUMULATOR_LOST:'+key)
    cp.require(result['min_accepted_photon_energy']<=pr['min_accepted_photon_energy'],'PRIOR_PHOTON_MINIMUM_LOST')
    for key in cp.GAS_KEYS:
        cp.require(result['accepted_gas_min'][key]<=pr['accepted_gas_min'][key] and result['accepted_gas_max'][key]>=pr['accepted_gas_max'][key],'PRIOR_GAS_EXTREMA_LOST:'+key)
    cp.require(result['continuation']['original_raw_files_unchanged'] is True,'ORIGINAL_ARTIFACT_MUTATION')
    return chain,manifest

def main():
    parser=argparse.ArgumentParser();parser.add_argument('run',type=Path);parser.add_argument('--n1',type=Path,required=True)
    parser.add_argument('--preflight',type=Path,default=HERE.parent/'evidence/PREFLIGHT.json');args=parser.parse_args()
    output=args.run/'CONTINUATION_MOMENTS.json'
    if output.exists():raise FileExistsError(output)
    chain,manifest=verify_chain(args.run)
    original=load('q1a_unmodified_postprocess',HERE.parent/'postprocess.py')
    value=original.moments(args.run,args.n1,args.preflight)
    for name in ['CONTINUATION_START.json','CONTINUATION.json','CONTINUATION_MANIFEST.json','resume_driver_as_run.py','resume_checkpoint_as_run.py',*[f'predecessor/{k}' for k in chain['original_files_sha256']]]:
        value['saved_file_sha256'][name]=cp.sha(args.run/name)
    value['identity_checks']['explicit_continuation_chain_verified']=True
    value['continuation']=dict(chain_sha256=cp.sha(args.run/'CONTINUATION.json'),wrapper_sha256=cp.sha(__file__),extra_bdf_initializations=1,solver_internal_state_restored=False,
       original_operator_driver_sha256=chain['original_driver_sha256'],continuation_driver_sha256=chain['resume_driver_sha256'],
       comparison_supported=False,time_convergence_inherited=False)
    value['status']='POSTPROCESSED_CONTINUATION_PENDING_CHAIN_REVIEW'
    with output.open('x') as h:json.dump(value,h,indent=2,allow_nan=False);h.write('\n')
    print(json.dumps({k:v for k,v in value.items() if k not in ('history','saved_file_sha256')},indent=2))
if __name__=='__main__':main()
