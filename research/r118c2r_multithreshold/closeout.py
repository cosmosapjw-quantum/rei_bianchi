import json,hashlib,re
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;I=D.parents[1]
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def j(p):return json.loads(p.read_text())
a=j(D/'RESULTS.json');b=j(D/'SPECTRAL_CHECK.json');v=j(D/'VISIBILITY.json')
assert all(int((D/f).read_text())==0 for f in ('green.exit','band_test.exit','audit.exit','spectral_check.exit','visibility.exit','full_tests.exit'))
tests=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored',(D/'full_tests.log').read_text())
assert sum(int(x[1]) for x in tests)==336 and all(x[0]=='ok' for x in tests)
assert a['status']=='SCOPED_COUPLED_MULTITHRESHOLD'
for name in ('q64','q128','q64tight','q128tight'):
 r=a['cases'][name];assert r['status']=='COMPLETE' and r['z_end']==4
 assert r['max_gate']<1 and r['abs_increment_sum']<=1e-8 and r['accepted']<=80000
 assert r['max_increment_ratio']<=1
 print(name,r['accepted'],r['terminal']['x_HeIII'],r['terminal']['temperature_K'],r['terminal']['Gamma_HeII'],r['tau'],r['rhs'],r['max_gate'],r['abs_increment_sum'],flush=True)
assert b['status']=='PASS_SCOPED_ALL_SPECIES_V6_ENDPOINT' and len(b['cases'])==4
assert v['status']=='PASS_SCOPED_REEVALUATED_C2N_RESPONSE' and len(v['results'])==5
old=j(I/'research/r118c2q_coupled_split/RESULTS.json')
old_z=old['cases']['q64tight']['z_end']
p=Path(a['cases']['q64tight']['segments'][0]['raw_path'])/'history.csv'
assert sha(p)==a['cases']['q64tight']['segments'][0]['hashes']['history.csv']
r=np.genfromtxt(p,names=True,delimiter=',');i=int(np.flatnonzero(r['zbar']<=old_z)[0]);n=int(r['accepted'][i])
assert n<80000
pair=dict(standard=a['comparisons_to_q128']['q64'],tight=a['matched_tight'],time_q64=a['time_refinement'],time_q128=a['time128'])
res=dict(status='PASS_SCOPED_V6_MULTITHRESHOLD_MATCHED_TIME_FREQUENCY',parent='25dd72f4fa74420fcbdbc3c624330095552f9901',full_rust_tests=336,full_trajectories=4,accepted_total=sum(x['accepted'] for x in a['cases'].values()),prior_cap_z=old_z,prior_cap_steps=80000,new_first_below_cap_z=float(r['zbar'][i]),new_steps_at_prior_cap=n,max_E_gate=max(x['max_gate'] for x in a['cases'].values()),max_abs_increment_sum=max(x['abs_increment_sum'] for x in a['cases'].values()),max_native_rate_gap=max(max(x['max_native_gamma_relative'],x['max_native_heat_relative']) for x in b['cases'].values()),comparison=pair,results=a,spectral=b,visibility=v,production_admission='HOLD_ANISOTROPIC_REACTIVATION_AND_CONTINUUM',native_subagent='NOT_RUN',files={p.name:sha(p) for p in D.iterdir() if p.is_file() and p.name not in ('ACCEPTANCE.json','closeout.log')})
(D/'ACCEPTANCE.json').write_text(json.dumps(res,indent=2)+'\n')
print('matched tight',pair['tight']['fields']['x_HeIII'],pair['tight']['fields']['Gamma_HeII'])
print('time q64',pair['time_q64']['fields']['x_HeIII'],'time q128',pair['time_q128']['fields']['x_HeIII'])
print('ACCEPTANCE',res['status'],res['accepted_total'],res['max_native_rate_gap'])
