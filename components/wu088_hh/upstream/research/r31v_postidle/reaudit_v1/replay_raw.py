from pathlib import Path
import json, hashlib, statistics, sys, math
import argparse
if not __debug__: raise RuntimeError("optimized Python is not admitted for this audit")
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
if args.out.exists(): raise FileExistsError(args.out)
repo=Path(__file__).resolve().parents[3]
p=repo/'research/r31v_postidle/evidence/ncp_host/20260928T132239Z_r31v'
sys.path.insert(0,str(repo/'research/r31v_postidle'))
import controls, m3_postidle as driver
raw=json.loads((p/'m3b_132.json').read_text()); prep=json.loads((p/'reference_prepare.json').read_text())
ret=json.loads((p/'RETURN.json').read_text())
source=json.loads((p/'SOURCE_BUILD_AUDIT.json').read_text())
checks={}; hashes={}
for key in ('benchmark','reference_prepare','host','source_build','grant','review','commands'):
 row=ret[key]['inventory'] if key=='host' else ret[key]
 f=repo/row['path']; b=f.read_bytes(); actual=hashlib.sha256(b).hexdigest()
 hashes[str(f.relative_to(repo))]={'sha256':actual,'bytes':len(b)}
 checks['return_bound_'+key]=(len(b)==row['bytes'] and actual==row['sha256'])
checks['same_workload']=controls.workload_identity([tuple(x) for x in raw['pair_set']]*11)==raw['workload']
checks['same_context_prepare_benchmark']=raw['numeric_context']==prep['numeric_context']
checks['context_hash']=controls.digest_json(raw['numeric_context'])==raw['reference_context_sha256']
cache=controls.ReferenceCache(p/'reference_cache',raw['numeric_context']); cache_rows=[]
for pair in raw['pair_set']:
 arr=cache.read(pair)
 cache_rows.append({'pair':pair,'components':{k:{'dtype':str(v.dtype),'shape':list(v.shape)} for k,v in arr.items()}})
checks['cache_payloads_validated']=len(cache_rows)==12
checks['benchmark_cache_only']=len(raw['reference_events'])==12 and all(r['event']=='CACHE_READ' for r in raw['reference_events'])
checks['prep_explicit_references']=len(prep['reference_events'])==12 and all(r['event']=='EXPLICIT_REFERENCE_COMPUTE' for r in prep['reference_events'])
rows=[]; stats=[]; root_negative=[]; cpu_scopes=[]
for cfg in raw['configs']:
 label=f"{cfg['processes']}x{cfg['threads_per_process']}"; rates=[]; cpu=[]
 for i,row in enumerate(cfg['repetitions'],1):
  driver._validate_measurement_row(row,cfg['processes'])
  worker_rows=list(row['workers'].values())
  assert sum(r['tasks_completed'] for r in worker_rows)==132
  assert math.isclose(sum(r['cpu_seconds'] for r in worker_rows), row['sum_worker_cpu_seconds'],rel_tol=1e-14)
  assert all(r['observed_affinity']==cfg['planned_affinity'][r['process_index']] and r['observed_openmp_team']==cfg['threads_per_process'] for r in worker_rows)
  rate=row['tasks_completed']/row['batch_wall_seconds']; assert rate==row['steady_state_pairs_per_second'];rates.append(rate);cpu.append(row['sum_worker_cpu_seconds'])
  d=row['ancestor_cpu_deltas'];leaf=raw['initial_resources']['cgroup_path'];ancestor='/sys/fs/cgroup/user.slice/user-0.slice';cgroot='/sys/fs/cgroup'
  diff=(d[cgroot]['usage_usec']-d[leaf]['usage_usec'])/1e6
  if diff<0: root_negative.append({'layout':label,'rep':i,'root_minus_leaf_cpu_seconds':diff})
  cpu_scopes.append({'layout':label,'rep':i,'root_minus_leaf_cpu_seconds':diff,'user_ancestor_minus_leaf_observed_seconds':(d[ancestor]['usage_usec']-d[leaf]['usage_usec'])/1e6,'scope':'ASYNCHRONOUS_COUNTER_DIFFERENCE_NOT_A_RIGOROUS_INTERFERENCE_BOUND'})
  rows.append({'layout':label,'rep':i,'wall':row['batch_wall_seconds'],'rate':rate,'cpu':row['sum_worker_cpu_seconds'],'runtime_exactness_claim':row['all_exact']})
 mean=statistics.mean(rates);sd=statistics.stdev(rates);med=statistics.median(rates)
 assert med==cfg['median_pairs_per_second']
 stats.append({'layout':label,'rates':rates,'median':med,'mean':mean,'sample_sd':sd,'cv':sd/mean,'throughput_per_allocated_logical_slot':med/(cfg['processes']*cfg['threads_per_process']),'cpu_seconds_per_task_mean':statistics.mean(cpu)/132})
med={s['layout']:s['median'] for s in stats}
checks['all_12_rows_revalidated']=len(rows)==12
checks['native_dispatch_accounting']=12+sum(c['processes'] for c in raw['configs'])+sum(r['tasks_completed'] for c in raw['configs'] for r in c['repetitions'])==1726
old_manifest=json.loads((repo/'research/r31v_postidle/FILE_MANIFEST.json').read_text())
manifest_mismatches=[]
for f,row in old_manifest['files'].items():
 b=(repo/'research/r31v_postidle'/f).read_bytes()
 if hashlib.sha256(b).hexdigest()!=row['sha256']:manifest_mismatches.append(f)
result={'schema':'WU088_R31V_RAW_REAUDIT_V1','source_run':'20260928T132239Z_r31v','raw_hashes':hashes,'checks':checks,'statistics':stats,'rows':rows,
 'comparisons':{'32x2_over_30x2_gain':med['32x2']/med['30x2']-1,'32x2_over_64x1_gain':med['32x2']/med['64x1']-1,'32x2_over_4x16_gain':med['32x2']/med['4x16']-1,'30x2_slot_efficiency_gain_over_32x2':(med['30x2']/60)/(med['32x2']/64)-1},
 'negative_root_minus_leaf':root_negative,'cpu_scopes':cpu_scopes,
 'historical_manifest_mismatches_current_code':manifest_mismatches,
 'new_scientific_nodes':0,'native_calls_this_audit':0,
 'native_call_count_5178':'DERIVED_FROM_SOURCE_DISPATCH_NOT_INDEPENDENT_HARDWARE_CALL_COUNTER',
 'exactness_scope':'RUNTIME_REPORTED_SUMMARIES_AND_REFERENCE_CACHE_VALIDATED; CANDIDATE_ARRAYS_NOT_PERSISTED_FOR_ALL_TIMED_TASKS',
 'host_isolation_independently_verified':False,'production_admitted':False,
 'input_checkout_identity':'RECORDED_SEPARATELY_BY_CALLER; NO_RUNTIME_RESTORE_CLAIM'}
assert all(checks.values()),checks
args.out.parent.mkdir(parents=True,exist_ok=True)
with args.out.open('x') as f: f.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps({'checks':checks,'statistics':stats,'comparisons':result['comparisons'],'negative_root_minus_leaf_count':len(root_negative),'historical_manifest_mismatches':manifest_mismatches},indent=2))
