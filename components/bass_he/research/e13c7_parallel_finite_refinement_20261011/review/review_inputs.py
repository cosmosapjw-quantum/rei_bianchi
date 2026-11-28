#!/usr/bin/env python3
"""Read-only independent input/partition review; imports no project modules."""
from pathlib import Path
from fractions import Fraction as F
import csv
import hashlib
import json
import time
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent/'BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1'
SP = ('HI', 'HeI', 'HeII')
MOM = ['Z_eV','QN','QE_eV']+[p+'_'+s+('_eV' if p!='A' else '') for p in ('A','B','H') for s in SP]
EPS = F.from_float(1.602176634e-12)
expected_kernel = {
 'directed_interval.py':'ce4a44b11d1c0a3a5c52861033fa817a587bca9a5b852fab48329213b9a732e5',
 'local_enclosure.py':'fade8983b7db8974c479ac4473424b7d572e8f7a0f09c042669fb3c40c32e370',
 'path_enclosure.py':'c424c8b980ece05618e427e4373f13a41fe7b4d02a8ddd4a0b3fa7da30109d73'}
checks = {}
failures = []

def check(name, condition, detail=None):
 row=checks.setdefault(name, {'passed':0,'failed':0})
 row['passed' if condition else 'failed']+=1
 if not condition:failures.append({'check':name,'detail':detail})

def h(path):
 d=hashlib.sha256()
 with Path(path).open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):d.update(chunk)
 return d.hexdigest()

def read(path):return json.loads(Path(path).read_bytes())
def canon(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
def cap(x):return F.from_float(float(x))
def pair(x):
 a,b=F(x['lo']),F(x['hi'])
 if a>b:raise ValueError('inverted interval')
 return a,b
def decode(x):return {a:{k:pair(v) for k,v in b.items()} for a,b in x.items()}
def combine(seq):
 out={}
 for m in seq:
  for kind,values in m.items():
   for k,v in values.items():
    old=out.setdefault(kind,{}).get(k,(F(0),F(0)))
    out[kind][k]=(old[0]+v[0],old[1]+v[1])
 return out
def metrics(x):
 weight=pair(x['weight'])
 check('old_point_positive_weight',weight[0]==weight[1] and weight[0]>0,x['node'])
 w=weight[0]
 out={'absolute':{k:pair(x['weighted_reduction'][k]) for k in ['P_final','anchor']+MOM},
      'correction':{k:tuple(v*w for v in pair(x['cumulative_correction'][k])) for k in MOM}}
 out['correction']['P_final']=tuple(v*w for v in pair(x['segments'][-1]['DP']))
 out['correction']['energy_eV']=tuple(v*w/EPS for v in pair(x['segments'][-1]['energy_endpoint_minus_captured_erg']))
 for kind in out:
  for prefix in ('A','B','H'):
   suffix='_eV' if prefix!='A' else ''
   out[kind][prefix+'_total'+suffix]=tuple(sum(out[kind][prefix+'_'+s+suffix][j] for s in SP) for j in (0,1))
  check('17_metrics_per_kind',len(out[kind])==17,(x['node'],kind))
 return out

def main():
 start=time.perf_counter()
 lock=read(ROOT/'SOURCE_LOCK.json')
 identities={}
 for name,pin in lock['files'].items():
  p=ROOT/name
  observed={'bytes':p.stat().st_size,'sha256':h(p)}
  identities[name]=observed
  check('source_pin_actual_bytes',observed==pin,name)
 for name,digest in expected_kernel.items():check('unchanged_kernel',identities['code/vendor/'+name]['sha256']==digest,name)
 plan=read(ROOT/'inputs/WORK_PLAN.json')
 index=read(ROOT/'inputs/INPUT_INDEX.json')['records']
 stage_rows=list(csv.DictReader((ROOT/'inputs/source/OFF_STAGES.csv').open()))
 stages={int(x['step']):x for x in stage_rows}
 check('two_unique_stages',len(stages)==len(stage_rows)==2)
 nodes=list(csv.DictReader((ROOT/'inputs/source/OFF_NODES.csv').open()))
 node_rows={(int(x['step']),int(x['node'])):x for x in nodes}
 check('node_capture_coverage',len(node_rows)==len(nodes)==4880)
 for s in stage_rows:
  for which in ('old','new'):
   x,y,z=[cap(s[which+'_'+a]) for a in ('x','y','z')]
   check('stage_endpoint_simplex',0<=x<=1 and y>=0 and z>=0 and y+z<=1,(s['step'],which))
 control={}
 source_rows=list(csv.DictReader((ROOT/'inputs/source/OFF_SEGMENTS.csv').open()))
 for r in source_rows:
  key=['OFF',int(r['step']),int(r['node']),int(r['segment'])]
  control.setdefault(key[2],[]).append({'key':key,'row':r,'stage':stages[key[1]],'node_row':node_rows[key[1],key[2]],'mask':{s:float(r['e_mid'])>=cut for s,cut in zip(SP,(13.6,24.59,54.42))},'source_on':float(r['source_on'])==1.0})
 for values in control.values():values.sort(key=lambda x:tuple(x['key']))
 check('complete_source_control_coverage',len(source_rows)==4884 and set(control)==set(range(2440)))
 groups={k:set(plan[k]) for k in ('prior_admitted_nodes','zero_nodes','local_primary_nodes','ncp_nodes')}
 check('partition_counts',[len(groups[k]) for k in groups]==[6,95,8,2331])
 check('partition_complete',set.union(*groups.values())==set(range(2440)))
 check('partition_disjoint',sum(map(len,groups.values()))==len(set.union(*groups.values())))
 check('prior_six_exact',groups['prior_admitted_nodes']=={0,101,102,410,413,700})
 check('zero_nodes_exact',groups['zero_nodes']==set(range(2345,2440)))
 check('local_eight_exact',groups['local_primary_nodes']=={105,106,409,414,1162,1620,1976,2344})
 bulk_masks={}
 zero_hashes={}
 sums={'old_local_eight':None,'old_ncp_2331':None}
 paths=[]
 offset=0
 with (ROOT/'inputs/OFF_OLD_PATHS.jsonl').open('rb') as stream:
  for raw in stream:
   x=json.loads(raw);node=x['node'];paths.append(node)
   c=control[node];record=index[str(node)]
   check('old_path_identity',x['mode']=='OFF' and 0<=node<2440,node)
   check('index_actual_line_bytes',record['offset']==offset and record['bytes']==len(raw) and record['old_line_sha256']==hashlib.sha256(raw).hexdigest(),node)
   check('input_semantic_binding',record['path_input_sha256']==hashlib.sha256(b'bass-he-e13c7-path-input-v1\n'+canon({'controls':c,'old_path':x})).hexdigest(),node)
   check('ordered_control_keys', [v['key'] for v in c]==[v['key'] for v in x['segments']]==record['keys'],node)
   check('initial_photon_exact_zero',cap(c[0]['row']['f0'])==0,node)
   for a,b in zip(c,x['segments']):
    r,s=a['row'],a['stage']
    check('old_mask_source_same_target',a['mask']==b['mask'] and a['source_on']==b['source_on'],a['key'])
    check('positive_time_stage_domain',cap(r['h'])>0 and cap(r['a'])+cap(r['h'])==cap(r['b']) and cap(s['s0'])<=cap(r['a'])<cap(r['b'])<=cap(s['s1']),a['key'])
    check('zero_outflow',cap(r['outn'])==cap(r['oute'])==0,a['key'])
    check('nonnegative_frozen_data',all(cap(r[k])>=0 for k in ['f0','q']+['lambda_'+sp for sp in SP]),a['key'])
    check('inactive_lambda_zero',all(a['mask'][sp] or cap(r['lambda_'+sp])==0 for sp in SP),a['key'])
    check('constant_positive_original_weight',cap(r['weight'])>0 and pair(x['weight'])==(cap(r['weight']),cap(r['weight'])),a['key'])
   for a,b in zip(c,c[1:]):
    check('time_photon_eta_weight_exact_stitch',all(cap(a['row'][ka])==cap(b['row'][kb]) for ka,kb in [('b','a'),('n','f0'),('eta','eta'),('weight','weight')]),[a['key'],b['key']])
   m=metrics(x)
   if node in groups['zero_nodes']:
    check('zero_all_34_old_endpoints',all(v==(F(0),F(0)) for kind in m.values() for v in kind.values()),node)
    check('zero_source_off_and_capture',all(not a['source_on'] and all(cap(a['row'][k])==0 for k in ['f0','q','n','u','red','qn','qe','outn','oute']+['A_'+s for s in SP]+['B_'+s for s in SP]) for a in c),node)
    zero_hashes[str(node)]=record['path_input_sha256']
   for label,group in [('old_local_eight','local_primary_nodes'),('old_ncp_2331','ncp_nodes')]:
    if node in groups[group]:sums[label]=m if sums[label] is None else combine([sums[label],m])
   if node in groups['ncp_nodes']:
    check('bulk_no_events_two_source_on',len(c)==2 and all(a['source_on'] and cap(a['row']['anchored'])==0 for a in c),node)
    check('bulk_constant_mask',c[0]['mask']==c[1]['mask'],node)
    mask=''.join('1' if c[0]['mask'][s] else '0' for s in SP)
    bulk_masks[mask]=bulk_masks.get(mask,0)+1
   offset+=len(raw)
 check('all_original_paths_once',paths==list(range(2440)))
 check('index_coverage_complete',set(index)==set(map(str,range(2440))))
 budget=read(ROOT/'inputs/PREDECESSOR_BUDGET.json')
 for label,actual in sums.items():
  expected=decode(budget[label])
  for kind in actual:
   for q,v in actual[kind].items():check('direct_saved_endpoint_sum',v==expected[kind][q],(label,kind,q))
 prior=read(ROOT/'inputs/predecessor/PRIOR_SIX_BUDGET.json')
 k4=read(ROOT/'inputs/predecessor/E13C6_ADMITTED_ENCLOSURES.json')
 reconstructed_prior=combine([decode(prior['K2'])]+[decode(p['new_raw_weighted']) for p in k4['paths']])
 check('prior_six_direct_bridge',reconstructed_prior==decode(prior['prior_six'])==decode(budget['prior_six']))
 combined=combine([reconstructed_prior,sums['old_local_eight'],sums['old_ncp_2331']])
 expected_full=decode(k4['new_full_OFF'])
 for kind in combined:
  for q,v in combined[kind].items():check('E13C6_full_exact_partition_bridge',v==expected_full[kind][q]==decode(budget['E13C6_full'])[kind][q],(kind,q))
 zeros=read(ROOT/'inputs/EXACT_ZERO_CERTIFICATES.json')
 check('zero_certificate_coverage',set(zeros['nodes'])==groups['zero_nodes'] and len(zeros['checks'])==95)
 for row in zeros['checks']:
  check('zero_certificate_input_binding',row['path_input_sha256']==zero_hashes[str(row['node'])],row['node'])
 check('bulk_active_species_partition',bulk_masks=={'100':691,'110':918,'111':722},bulk_masks)
 result={'schema':'bass-he-e13c7-independent-input-review-v1','reviewer':'e13c7_intake','candidate_modules_imported':0,'scientific_kernel_invocations':0,'status':'PASS_STATIC_SAME_TARGET_PARTITION' if not failures else 'HOLD','observed_utc':datetime.now(timezone.utc).isoformat(),'source_lock_sha256':h(ROOT/'SOURCE_LOCK.json'),'source_identities':identities,'checks':checks,'checks_passed':sum(v['passed'] for v in checks.values()),'checks_failed':sum(v['failed'] for v in checks.values()),'failures':failures,'bulk_masks':bulk_masks,'partition_counts':{k:len(v) for k,v in groups.items()},'direct_full_bridges':34,'elapsed_seconds':time.perf_counter()-start,'limitations':['No new coefficient evaluations, quadrature or ODE solve','This review confirms fixed captured targets and exact saved-data partitioning, not physical/continuum correctness','Final local scientific and heavy readiness decisions await completed candidate evidence.']}
 (HERE/'STATIC_INPUT_REVIEW.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({k:result[k] for k in ('status','source_lock_sha256','checks_passed','checks_failed','elapsed_seconds')}))
 if failures:print(json.dumps(failures))
 return 1 if failures else 0

if __name__=='__main__':raise SystemExit(main())
