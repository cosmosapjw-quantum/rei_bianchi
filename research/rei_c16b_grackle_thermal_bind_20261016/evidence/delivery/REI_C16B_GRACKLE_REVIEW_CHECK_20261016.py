import importlib.util,sys,json,math,hashlib,re
from pathlib import Path
import numpy as np
here=Path('/root/REI_C16B_GRACKLE_THERMAL_20261016_001/research/rei_c16b_grackle_thermal_bind_20261016');spec=importlib.util.spec_from_file_location('review_reference',here/'reference.py');ref=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ref;spec.loader.exec_module(ref)
def at_time(data,t):
 if 'dense_segments' in data:return ref.dense_state(data,t)
 row=min(data['history'],key=lambda row:abs(row[0]-t))
 if abs(row[0]-t)>128*np.finfo(float).eps*max(t,1):return None
 return np.array(row[1:])
checks=json.loads((here/'evidence/reference/point_checks.json').read_text());point={'checks':len(checks),'failures':sum(not v['pass_'] for v in checks),'max_relative':max(v['relative_error'] for v in checks)}
records=json.loads((here/'evidence/reference/trajectory_summary.json').read_text());result={'point':point,'trajectories':{},'native':{},'pulse':{}}
for case in records:
 if not case.get('required_smooth_family'):continue
 name=case['case'];tight=json.loads((here/f'evidence/reference/{name}_radau_tight.json').read_text());base=json.loads((here/f'evidence/reference/{name}_radau.json').read_text());vals=[]
 for comparison in case['comparisons']:
  rows=[json.loads(line) for line in Path(comparison['native_history_path']).read_text().splitlines()];r0=rows[0];initial=ref.native_state(r0);physics=ref.Physics(r0['nh'],r0['nhe'],r0['tcmb'],r0['actual_delta_energies_ev']);maximum=(0.,0.,None);fixed=0.;tightening=0.;tight_count=0
  for row in rows:
   t=row['time_s'];v=at_time(tight,t);assert v is not None;n=ref.native_state(row);scaleN=max(sum(initial[4:])+v[7+ref.INTEGRALS.index('source_n_per_h')],1e-8);tr=physics.point(v[:7])['temperature'];ti=physics.point(initial)['temperature'];terms=[float(max(abs(n[:3]-v[:3]))),abs(n[3]-v[3])/max(initial[3],v[3]),abs(row['temperature']-tr)/max(ti,tr),float(sum(abs(n[4:]-v[4:7])))/scaleN];err=max(terms)
   if err>maximum[0]:maximum=(err,t,['fractions','thermal','temperature','photons'][terms.index(err)])
   if abs(t/rows[-1]['time_s']*32-round(t/rows[-1]['time_s']*32))<1e-9:fixed=max(fixed,err)
   b=at_time(base,t)
   if b is not None:tightening=max(tightening,ref.error_norm(initial,v[:7],b[:7],physics,v[7+ref.INTEGRALS.index('source_n_per_h')]));tight_count+=1
  vals.append({'n':comparison['n'],'maximum':maximum,'fixed_t32_max':fixed,'tightening_max_at_available_common_times':tightening,'tightening_comparisons':tight_count,'matches_report':abs(maximum[0]-comparison['max_common_time_error'])<1e-13,'raw_sha_matches':hashlib.sha256(Path(comparison['native_history_path']).read_bytes()).hexdigest()==comparison['history_source_sha256']})
 result['trajectories'][name]=vals
maxinv=(0.,'');maxtxn=(0.,'');histories=0;rowscount=0
for f in (here/'evidence/native').rglob('*.summary.json'):
 d=json.loads(f.read_text());raw=f.with_suffix('').with_suffix('.jsonl');histories+=1
 for line in raw.read_text().splitlines():
  r=json.loads(line);rowscount+=1;v=r['invariants']['max_normalized']
  if v>maxinv[0]:maxinv=(v,str(raw.relative_to(here)))
  for x in r['transaction_checks']:
   if x[2]>maxtxn[0]:maxtxn=(x[2],str(raw.relative_to(here)))
  assert 1<=r['temperature']<=1e6 and r['w']>0 and 0<=r['fractions'][0]<=1 and min(r['fractions'][1:])>=0 and sum(r['fractions'][1:])<=1 and all(v>=0 and math.isfinite(v) for v in r['photons'])
result['native']={'histories':histories,'saved_rows':rowscount,'max_cumulative_normalized':maxinv,'max_transaction_normalized':maxtxn}
for name in ['pulse_early','pulse_delayed']:
 stem=here/'evidence/native/pulse_repair'/f'{name}_n32';rows=[json.loads(l) for l in stem.with_suffix('.jsonl').read_text().splitlines()];end=rows[-1];co=[json.loads(l) for l in stem.with_suffix('.cohorts.jsonl').read_text().splitlines()];roundoff=max(max(abs(v[0])/(128*np.finfo(float).eps*v[1]) if v[1] else 0.,abs(v[2])/(128*np.finfo(float).eps*v[3]) if v[3] else 0.) for v in end['emission_roundoff']);sn=math.fsum(c['number'] for c in co);su=math.fsum(c['energy_ev'] for c in co)
 result['pulse'][name]={'cohorts':len(co),'cursor':end['source_cursor'],'accepted':end['accepted_steps'],'source_number':sn,'source_energy':su,'count_match':sn==end['source_n'],'energy_residual':su-end['source_u'],'mean_emission_age':math.fsum(c['number']*c['emission_age_at_observation'] for c in co)/sn,'roundoff_max_fraction_of_128eps':roundoff}
log=(here/'evidence/native/focused_tests.log').read_text();result['focused_tests']=[list(map(int,m)) for m in re.findall(r'test result: ok\. (\d+) passed; (\d+) failed',log)]
out=Path('/root/REI_C16B_GRACKLE_REVIEW_DATA_20261016.json');out.write_text(json.dumps(ref.serializable(result),indent=2)+'\n');print(json.dumps(ref.serializable(result),indent=2))
