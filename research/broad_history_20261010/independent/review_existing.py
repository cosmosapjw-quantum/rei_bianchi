"""Reviewer probes of existing functions and recorded evidence; no model changes."""
import hashlib, json, math, shutil, sys, tempfile
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import model, run_campaign
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
result={'scope':'REI-ACCEL01 recorded reduced campaign only','checks':{},'hashes':{}}
for filename in ['model.py','run_campaign.py','reference.py','SCIENTIFIC_CONTRACT.md','EXTERNAL_SOURCE_CONTRACT.md','EXTERNAL_SOURCE_CONTRACT.json','tests/test_history.py','evidence/RUN001/CAMPAIGN.json','evidence/RUN001/model_as_run.py','evidence/RUN001/run_campaign_as_run.py','evidence/RUN002/CAMPAIGN.json','evidence/REFERENCE_EXECUTION.json']:
 result['hashes'][filename]=sha(HERE/filename)
result['hashes']['../physical_provider_20261010/background.py']=sha(model.BG_PATH)
campaign=json.loads((HERE/'evidence/RUN002/CAMPAIGN.json').read_text())
rows={}
for name,r in campaign['cases'].items():
 p=HERE/r.get('reused_from','evidence/RUN002/'+name)
 h=dict(np.load(p/'history.npz'))
 checks={'data_sha_matches':sha(p/'history.npz')==r['data_sha256'], 'summary_matches_recomputation':model.summarize(h)==r['summary'],'finite':all(np.isfinite(a).all() for a in h.values()),'Q_bounded':bool(min(h['Q'])>=0 and max(h['Q'])<=1),'nonnegative_counters':all(min(h[k])>=0 for k in ['Nrec','Nemit','Nexcess','tau','t_s']),'z_endpoints':bool(h['z'][0]==20 and h['z'][-1]==4),'producer_model_match':r['identity']['model_sha256']==sha(HERE/'model.py')}
 checks['pass']=all(checks.values());rows[name]=checks
 result['hashes'][str((p/'history.npz').relative_to(HERE))]=sha(p/'history.npz')
 result['hashes'][str((p/'COMPLETE.json').relative_to(HERE))]=sha(p/'COMPLETE.json')
result['checks']['recorded_cases']=rows
parity={}
for mag in ['001','005','01']:
 p=dict(np.load(HERE/f'evidence/RUN002/rp{mag}_n16384/history.npz'));m=dict(np.load(HERE/f'evidence/RUN002/rm{mag}_n16384/history.npz'))
 parity[mag]={k:float(np.max(np.abs(p[k]-m[k]))) for k in ['Q','tau','Nrec','Nemit','H_s']}
 parity[mag]['b_odd_error']=float(np.max(np.abs(p['b']+m['b'])))
result['checks']['shear_parity']=parity
scalar_errors=[]; count=0
for B in [0.,1e-16,1e-10,.1,1.,3.,100.]:
 for h in [0.,1e-16,1e-5,.1,1.,100.]:
  for A in [0.,B,math.nextafter(B,0.),math.nextafter(B,math.inf)]:
   for q in [0.,.8,1.]:
    count+=1
    try:
     o=model.advance_constant(q,A,B,h)
     if any(not math.isfinite(v) or v<0 for v in o.values()) or o['q']>1: scalar_errors.append([q,A,B,h,o])
    except Exception as e:scalar_errors.append([q,A,B,h,type(e).__name__,str(e)])
result['checks']['scalar_boundary_probes']={'count':count,'errors':scalar_errors}
resume={}
config=model.default_config()
_,old=run_campaign.execute_case('flrw',config,16384,HERE/'evidence/RUN002')
resume['matching_checkpoint_reused']=old==json.loads((HERE/'evidence/RUN002/flrw_n16384/COMPLETE.json').read_text())
with tempfile.TemporaryDirectory(dir=HERE/'independent') as tmp:
 root=Path(tmp);folder=root/'flrw_n16384';shutil.copytree(HERE/'evidence/RUN002/flrw_n16384',folder)
 try:run_campaign.execute_case('flrw',{**config,'r':.01},16384,root)
 except RuntimeError as e:resume['config_mismatch_rejected']=str(e).startswith('RESUME_IDENTITY_OR_DATA_MISMATCH')
 else:resume['config_mismatch_rejected']=False
 with (folder/'history.npz').open('ab') as f:f.write(b'reviewer-corruption-probe')
 try:run_campaign.execute_case('flrw',config,16384,root)
 except RuntimeError as e:resume['data_mismatch_rejected']=str(e).startswith('RESUME_IDENTITY_OR_DATA_MISMATCH')
 else:resume['data_mismatch_rejected']=False
result['checks']['checkpoint_resume']=resume
for r in [0.,.01,-.01,.05,-.05,.1,-.1]:
 bg=model.make_background({**config,'r':r})
 assert abs(model.coefficients(0.,{**config,'r':r},bg)['s_over_H']-r)<1e-15
result['checks']['initial_s_over_H_matches_r']=True
comparison=json.loads((HERE/'evidence/RUN002/INDEPENDENT_COMPARISON.json').read_text())
for name in ['validate_campaign.py','evidence/RUN002/INDEPENDENT_COMPARISON.json','evidence/RUN002/flrw_reference_fine.npz','evidence/RUN002/rp01_reference_fine.npz','evidence/RUN002/flrw_BASS_CELLS.csv','evidence/RUN002/rp01_BASS_CELLS.csv']:
 result['hashes'][name]=sha(HERE/name)
assert all(sha(HERE/k)==v for k,v in comparison['source_hashes'].items())
for c in comparison['results']:
 name=c['case']; d=HERE/'evidence/RUN002'/f'{name}_n16384/history.npz'; f=HERE/'evidence/RUN002'/f'{name}_reference_fine.npz'
 assert sha(d)==c['primary_data_sha256'] and sha(f)==c['reference_data_sha256']
 h=dict(np.load(d));ref=dict(np.load(f))
 assert np.array_equal(h['x'],ref['x'])
 assert float(np.max(abs(h['Q']-ref['Q'])))==c['comparison']['max_abs_Q']
 assert float(np.max(abs(h['tau']-ref['tau'])))==c['comparison']['max_abs_tau']
for c in comparison['BASS_exports']:
 path=HERE/'evidence/RUN002'/c['file'];assert sha(path)==c['sha256']
 data=np.genfromtxt(path,delimiter=',',names=True)
 assert all(data['t1_s']>data['t0_s'])
 name=c['file'].split('_BASS')[0]
 h=dict(np.load(HERE/'evidence/RUN002'/f'{name}_n16384/history.npz'))
 assert abs(sum(data['delta_tau'])-h['tau'][-1])<1e-16
receipt=json.loads((HERE/'evidence/REFERENCE_EXECUTION.json').read_text())
assert receipt['producer_hashes_before']==receipt['producer_hashes_after']
assert all(sha(HERE/k)==v for k,v in receipt['producer_hashes_after'].items())
assert all(sha(HERE/'evidence'/k)==v for k,v in receipt['output_sha256'].items())
result['checks']['direct_reference_comparison']={'source_hashes_match':True,'results':[{'case':c['case'],'metrics':c['comparison'],'limits':c['limits'],'pass':c['pass']} for c in comparison['results']]}
result['checks']['reference_execution_hashes_match']=True
result['checks']['direct_grid_Q_tau_differences_recomputed']=True
result['checks']['BASS_exports_hashes_cell_times_tau_sums_verified']=True
result['review_script_sha256']=sha(__file__)
(HERE/'independent/EXISTING_EVIDENCE_PROBES.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'cases':len(rows),'all_case_checks':all(r['pass'] for r in rows.values()),'scalar_count':count,'scalar_errors':len(scalar_errors),'resume':resume}))
