"""Bounded recovery-only IEEE64 readback; never executes scientific code."""
from pathlib import Path
import csv, datetime, hashlib, json, math, struct, time
BASE=Path('/workspace/scratch/6af5e9e6c737/resume_20261020')
OUT=BASE/'coder'
SANDBOX=BASE/'restored_c10/REI_LRS_V14_VIGILODE_C10_20261019T141050Z/repo_payload/research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019'
NCP=BASE/'restored_c11/REI_LRS_V14_VIGILODE_NCP_C11_20261019T171038Z/committed_tree_09bfe94/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019/ncp_20261019T171038Z'
J=lambda p:json.loads(p.read_text())
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def numeric(x):return isinstance(x,(int,float)) and not isinstance(x,bool)
def compare(a,b):
 result={'numeric_leaves':0,'timing_leaves_skipped':0,'nonfinite_leaves':[],'packed_ieee64_mismatches':[],'structural_mismatches':[],'negative_zero_pairs':0,'positive_zero_pairs':0}
 def walk(x,y,path=''):
  if isinstance(x,dict) and isinstance(y,dict):
   if x.keys()!=y.keys():result['structural_mismatches'].append([path,'keys'])
   for k in sorted(x.keys() & y.keys()):walk(x[k],y[k],path+'/'+k)
  elif isinstance(x,list) and isinstance(y,list):
   if len(x)!=len(y):result['structural_mismatches'].append([path,'length'])
   for i,(u,v) in enumerate(zip(x,y)):walk(u,v,f'{path}[{i}]')
  elif numeric(x) and numeric(y):
   if any(t in path.lower() for t in ('wall','elapsed','utc','seconds')):
    result['timing_leaves_skipped']+=1;return
   result['numeric_leaves']+=1
   u,v=float(x),float(y)
   if not (math.isfinite(u) and math.isfinite(v)):result['nonfinite_leaves'].append(path)
   if struct.pack('>d',u)!=struct.pack('>d',v):result['packed_ieee64_mismatches'].append(path)
   if u==v==0.0:
    if math.copysign(1,u)==math.copysign(1,v)==-1:result['negative_zero_pairs']+=1
    if math.copysign(1,u)==math.copysign(1,v)==1:result['positive_zero_pairs']+=1
  elif x!=y and not any(t in path.lower() for t in ('wall','elapsed','utc','seconds')):result['structural_mismatches'].append([path,'value',x,y])
 walk(a,b);return result
start=time.monotonic();sm=J(SANDBOX/'receipts/MATRIX_RECEIPT.json');nm=J(NCP/'payload/evidence/MATRIX_RECEIPT.json');records={};outcomes={}
for c in sm['cases']:
 name=f"{c['mode']}/{c['method']}/{c['N']}"
 sdir=SANDBOX/'receipts'/Path(c['receipt']).name
 if not (sdir/'raw.json').exists():sdir=SANDBOX/'receipts/final_source_n4'
 ndir=NCP/'payload/evidence'/f"{c['mode']}_{c['method']}_n{c['N']}"
 records[name]=compare(J(sdir/'raw.json'),J(ndir/'raw.json'))
 o=J(ndir/'outcome.json');outcomes[name]={'exit_code':o['exit_code'],'truncated':o['truncated'],'stdout_sha256_matches':SHA(ndir/'stdout.txt')==o['stdout_sha256'],'stderr_sha256_matches':SHA(ndir/'stderr.txt')==o['stderr_sha256'],'stdout_sha256':SHA(ndir/'stdout.txt'),'stderr_sha256':SHA(ndir/'stderr.txt')}
def csvphysics(p):
 with p.open() as f:return {f"{r['mode']}/{r['method']}/{r['N']}":{k:float(v) for k,v in r.items() if k not in ('mode','method','N','native_rhs','native_wall_s','process_wall_s')} for r in csv.DictReader(f)}
endpoint=compare(csvphysics(SANDBOX/'analysis/ENDPOINTS_AND_COST.csv'),csvphysics(NCP/'payload/analysis_r2/ENDPOINTS_AND_COST.csv'))
sa=J(SANDBOX/'analysis/MATRIX_ANALYSIS.json');na=J(NCP/'payload/analysis_r2/MATRIX_ANALYSIS.json')
fd={s:compare(sa[s],na[s]) for s in ('refinement','empirical_comparisons')}
result={'scope':'Recovery readback of completed sandbox and NCP evidence; no scientific execution','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'timing_exclusion':'same path substring filter as published host_compare.py: wall, elapsed, utc, seconds','raw_records':records,'raw_totals':{k:sum(v[k] for v in records.values()) for k in ('numeric_leaves','timing_leaves_skipped','negative_zero_pairs','positive_zero_pairs')},'endpoint':endpoint,'finite_difference':fd,'outcomes':outcomes,'matrix':{'cases':len(nm['cases']),'completed':sum(c['status']=='COMPLETED' for c in nm['cases']),'overall_exit_code':nm['overall_exit_code'],'native_rhs':sum(c['native_rhs'] for c in nm['cases']),'native_wall_s':nm['incremental_native_wall_s']},'archived_host_compare_bytes_equal':(OUT/'HOST_COMPARE_RECOVERED.json').read_bytes()==(NCP/'NCP_VS_SANDBOX.json').read_bytes(),'wall_s':time.monotonic()-start}
all_comparisons=[*records.values(),endpoint,*fd.values()]
result['pass']=all(not x[k] for x in all_comparisons for k in ('nonfinite_leaves','packed_ieee64_mismatches','structural_mismatches')) and all(x['exit_code']==0 and x['truncated'] is False and x['stdout_sha256_matches'] and x['stderr_sha256_matches'] for x in outcomes.values()) and result['raw_totals']['timing_leaves_skipped']==38 and result['matrix']=={'cases':19,'completed':19,'overall_exit_code':0,'native_rhs':38840,'native_wall_s':15.824811033} and result['archived_host_compare_bytes_equal']
(OUT/'RECOVERY_NUMERIC_READBACK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('raw_records','outcomes')},indent=2))
raise SystemExit(0 if result['pass'] else 1)
