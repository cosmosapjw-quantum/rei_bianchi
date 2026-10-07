#!/usr/bin/env python3
"""Read-only, no-integration replay of every retained 37-field table comparison."""
import argparse,csv,hashlib,importlib.util,json,pathlib,re,sys
sys.dont_write_bytecode=True
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[1]
spec=importlib.util.spec_from_file_location('igm_compare',ROOT/'tools/igm_compare.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
checks=[]
def check(a,b,factor,saved,label):
 r=c.compare_rows(c.read_csv(a),c.read_csv(b),allowance_factor=factor)
 assert len(r['fields'])==37,(label,len(r['fields']))
 # All native comparison keys, including every field's maximum and global budgets.
 for key,value in r.items():assert value==saved[key],(label,key,value,saved[key])
 checks.append({'comparison':label,'fields':37,'numerical_verdict':r['passed'],'replay':'EXACT'})
for folder in ['short-hhe-coupling','short-hhe-midpoint']:
 p=D/folder/'results';a=json.loads((p/'ASSESSMENT.json').read_text())
 for key,saved in a['temporal'].items():
  mode,g,x,y=re.fullmatch(r'(phases|endpoint)_g(\d)_(\d+)_to_(\d+)',key).groups()
  check(p/f'B_{mode}_m{x}_g{g}.csv',p/f'B_{mode}_m{y}_g{g}.csv',.1,saved,folder+'/'+key)
 for key,saved in a['spectral'].items():
  mode,m=key.split('_m');check(p/f'B_{mode}_m{m}_g2.csv',p/f'B_{mode}_m{m}_g4.csv',1.,saved,folder+'/'+key)
 for name,values in a['step_budgets'].items():
  rows=c.read_csv(p/name)
  assert all(max(r[k] for r in rows)==v for k,v in values.items()),name
p=D/'short-hhe-midpoint/results';a=json.loads((p/'REFINEMENT_ASSESSMENT.json').read_text())
for key,saved in a['temporal'].items():
 g,x,y=re.fullmatch(r'g(\d)_(\d+)_to_(\d+)',key).groups();check(p/f'B_phases_m{x}_g{g}.csv',p/f'B_phases_m{y}_g{g}.csv',.1,saved,'refinement/'+key)
for key,saved in a['spectral'].items():
 m=key[1:];check(p/f'B_phases_m{m}_g2.csv',p/f'B_phases_m{m}_g4.csv',1.,saved,'refinement/'+key)
for key,saved in a['reference'].items():
 m,g,ref=re.fullmatch(r'm(\d+)_g(\d)_(baseline|companion)',key).groups();reference=D/'short-hhe-coupling/results/reference_tighter.csv' if ref=='baseline' else p/'reference_companion.csv';check(p/f'B_phases_m{m}_g{g}.csv',reference,1.,saved,'reference/'+key)
for key,values in a['step_budgets'].items():
 rows=c.read_csv(p/f'B_phases_{key}_steps.csv');assert all(max(r[k] for r in rows)==v for k,v in values.items()),key
status=json.loads((p/'REFERENCE_COMPANION_STATUS.json').read_text());check(D/'short-hhe-coupling/results/reference_tighter.csv',p/'reference_companion.csv',.1,status['reference_retightening'],'reference/pair_tightening')
# Fixed-grid identity, original/addendum failures and honest peak-array qualification remain explicit.
add=json.loads((D/'short-hhe-midpoint/TEMPORAL_REFINEMENT_ADDENDUM.json').read_text());assert hashlib.sha256((p/'grid_bits.csv').read_bytes()).hexdigest()==add['grid_bits_gauss4_sha256']
r=json.loads((D/'short-hhe-midpoint/RESULTS.json').read_text());assert r['status']=='PARTIAL' and r['refinement']['status']=='PARTIAL' and r['refinement']['finest_32_to64_pass'];assert r['reference_peak_array_accounting']=='UNVERIFIED'
result={'status':'PASS_SAVED_COMPARISON_REPLAY','comparisons':len(checks),'fields_per_comparison':37,'histories_integrated':0,'numerical_scope':'BE PARTIAL; midpoint selected finest-pair accuracy PASS, aggregate PARTIAL; historical failures are expected and reproduced.','checks':checks}
parser=argparse.ArgumentParser();parser.add_argument('--output',type=pathlib.Path);args=parser.parse_args()
if args.output:args.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
