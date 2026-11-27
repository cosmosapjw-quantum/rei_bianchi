import copy, importlib.util, json
from pathlib import Path
path=Path('/workspace/scratch/0b54847633d9/c2c_anchor_audit_staging.py')
spec=importlib.util.spec_from_file_location('audit_staging',path)
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
c=json.loads(Path('BASS_HE_C2C_SMALL_R_SCALED_20261001_v1/CONTRACT.json').read_text())
R=c['spherical_anchor']['R']; obs={}; quality={}; L=.0005
for label in ['l72','l96']:
 cfg=c['spherical_anchor']['configurations'][label]
 row={'L_O_over_minus_i_hbar':L,'L_center_over_minus_i_hbar':L-R*.9/3,'p_x_over_minus_i_hbar':.9,'dipole_x':.3,'origin_shift_center_to_O':R/3,'origin_center':'B'}
 identities=[{'state_sha256':str(m)*64,'state_bytes':10+m} for m in [0,1]]
 obs[label]={'R':R,'sectors':[0,1],'new_eigensolves':0,'energies':[-4.,-1.],'phase_probes':[1.,1.], 'direct':{str(q):copy.deepcopy(row) for q in [14,22,30]},'states':identities}
 quality[label]=[]
 for m in [0,1]:
  meta={'origin_center':'B','origin_shift_center_to_O':R/3,'nuclear_positions':[-R,0.], 'angular_lmax':cfg['lmax'],'degree':cfg['degree'],'rmax':cfg['rmax'],'radial_quadrature':cfg['quadrature']}
  quality[label].append({'energy':[-4.,-1.][m],'phase_probe':1.,'residual':1e-12,'mass_norm':1.,'metadata':meta,**identities[m]})
p={'R':R,'energies':[-4.,-1.],'direct':{'32':{'L_O_bar':L}}}
passed=a.evaluate_anchors(obs,p,c,state_values=quality);assert passed['accepted'],passed
missing=a.evaluate_anchors(obs,p,c);assert missing['status']=='UNKNOWN' and not missing['accepted']
bad=copy.deepcopy(p);bad['direct']['32']['L_O_bar']=.002
failed=a.evaluate_anchors(obs,bad,c,state_values=quality);assert failed['status']=='FAIL' and not failed['accepted']
q=copy.deepcopy(quality);q['l96'][0]['mass_norm']=1.01
assert a.evaluate_anchors(obs,p,c,state_values=q)['status']=='FAIL'
badobs=copy.deepcopy(obs);badobs['l72']['direct']['30']['dipole_x']=float('nan')
assert a.evaluate_anchors(badobs,p,c,state_values=quality)['status']=='UNKNOWN'
additional=copy.deepcopy(obs['l72']);additional['direct']={str(q):copy.deepcopy(additional['direct']['30']) for q in [40,48]}
merged=a.merge_observation_values(obs['l72'],additional)
assert sorted(merged['direct'])==['14','22','30','40','48']
mergedobs=copy.deepcopy(obs);mergedobs['l72']=merged
assert a.evaluate_anchors(mergedobs,p,c,state_values=quality)['accepted']
partial=copy.deepcopy(obs);partial['l72']['direct']={'40':copy.deepcopy(obs['l72']['direct']['30']),'48':copy.deepcopy(obs['l72']['direct']['30'])}
assert a.evaluate_anchors(partial,p,c,state_values=quality)['status']=='UNKNOWN'
json.dumps(passed,allow_nan=False)
print(json.dumps({'status':'PASS','manufactured_scalar_cases':8,'physical_solves':0,'physical_integrals':0,'status_semantics':['PASS','FAIL','UNKNOWN']},indent=2))
