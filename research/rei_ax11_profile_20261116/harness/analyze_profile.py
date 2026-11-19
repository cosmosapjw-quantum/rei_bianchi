#!/usr/bin/env python3
"""Analyze original-source finite native data in cloud; no new evolution."""
from pathlib import Path
import csv,json,statistics,hashlib,sys,gzip,shutil
root=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(exist_ok=True,parents=True)
results=root/'results';components=['HII','HeII','HeIII','thermal','photon_N_L1','photon_U_L1']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(out/n).write_text(json.dumps(v,indent=2)+'\n')
windows={};errors={};cost={};comparisons=[]
for d in sorted(results.iterdir()):
 if not d.is_dir():continue
 s=json.loads((d/'window_summary.json').read_text());windows[d.name]=s
 cost[d.name]={'fresh_evolution_wall_s':s['fresh_evolution_wall_s'],'process_wall_s':s['process_wall_s'],
     'wall_per_tentative_s':s['fresh_evolution_wall_s']/s['delta_counts']['attempts'],
     'wall_per_accepted_s':s['fresh_evolution_wall_s']/s['delta_counts']['accepted']}
 cp=d/'raw/error_components.csv'
 if cp.exists():
  rows=list(csv.DictReader(cp.open()));parts={}
  for outcome in sorted(set(x['outcome'] for x in rows)):
   rr=[x for x in rows if x['outcome']==outcome];vv=[[float(x[k]) for k in components] for x in rr if x['components_available']=='true']
   parts[outcome]={'rows':len(rr),'available_rows':len(vv),'unavailable_rows':len(rr)-len(vv),
     'controlling_component_count_including_exact_ties':{k:sum(v[i]==max(v) for v in vv) for i,k in enumerate(components)},
     'component_min_median_max':{k:[min(v[i] for v in vv),statistics.median(v[i] for v in vv),max(v[i] for v in vv)] for i,k in enumerate(components)} if vv else {},
     'metric_min_max':[min(map(max,vv)),max(map(max,vv))] if vv else None}
  errors[d.name]={'input':'results/'+d.name+'/raw/error_components.csv','sha256':sha(cp),
                 'a_start':s['a_start'],'a_end':s['a_end'],'groups':parts}
  bg=next(csv.reader((d/'raw/background_timing.csv').open()))
  cost[d.name]['background']={'calls':int(bg[1]),'hits':int(bg[2]),'misses':int(bg[3]),'failures':int(bg[4]),'inclusive_seconds':int(bg[5])*1e-9,'hit_fraction':int(bg[2])/int(bg[1])}
  cost[d.name]['inclusive_scopes']={x[0]:{'calls':int(x[1]),'seconds':int(x[2])*1e-9} for x in csv.reader((d/'raw/driver_timing.csv').open())}
  evidence=out/'native_components';evidence.mkdir(exist_ok=True)
  (evidence/(d.name+'.csv.gz')).write_bytes(gzip.compress(cp.read_bytes(),mtime=0))
 for file in ['window_summary.json','checkpoint.start.txt','checkpoint.end.txt']:
  e=out/'native_receipts'/d.name;e.mkdir(exist_ok=True,parents=True);shutil.copyfile(d/file,e/file)
 if 'original' not in d.name:
  case,window,mode,rep=d.name.split('_');reference=results/f'{case}_{window}_original_{rep}'
  check={fn:{'original':sha(reference/fn),'candidate':sha(d/fn),'equal':sha(reference/fn)==sha(d/fn)} for fn in ['raw/state_trace.bin','history.csv','abundances.csv','ledgers.csv','feedback.csv','spectra.csv']}
  assert all(x['equal'] for x in check.values()),d.name
  comparisons.append({'original':reference.name,'candidate':d.name,'status':'BIT_IDENTICAL_STATES_AND_BYTES_ALL_FIVE_TABLES','files':check,
       'evolution_wall_speed_ratio_observed':windows.get(reference.name,json.loads((reference/'window_summary.json').read_text()))['fresh_evolution_wall_s']/s['fresh_evolution_wall_s']})
receipt=json.loads((root/'NATIVE_JOB_RECEIPT.json').read_text())
summary={'status':'NATIVE_BOUNDED_PROFILE_ACCEPTED_SCOPED','original_DAG':'10/17','expansion_DAG':'28/88','AX11_complete':False,
 'number_windows':len(windows),'new_accepted_states_counted_with_repetitions':sum(x['delta_counts']['accepted'] for x in windows.values()),
 'new_tentative_trials':sum(x['delta_counts']['attempts'] for x in windows.values()),'new_RHS_calls':sum(x['delta_counts']['rhs_evaluations'] for x in windows.values()),
 'native_job_wall_s_including_first_failed_test':receipt['wall_elapsed_s'],'native_cpu_s_including_failed_test':sum(x['cpu_s'] for x in receipt['records']),
 'original_cumulative_cost':'UNKNOWN unchanged','native_child_process_starts_including_failed_test':len(receipt['records']),
 'tested_native_windows':windows,'implementation_matches':comparisons,
 'scientific_result_scope':'Measured actual local controllers and original-IC/plateau source kernels; not full-history global abundance error or AX11 convergence',
 'timer_scope':'inclusive and nested; background includes setup/read/checkpoint paths. Do not sum shares. Native monitor peakRSS is direct process only; build descendant peak not measured.'}
save('ERROR_COMPONENT_PROFILE.json',{'components':components,'local_floors':{'fraction':1e-5,'thermal_eV_per_H':1e-6,'photon_N_per_H':1e-8,'photon_U_eV_per_H':1e-8},'windows':errors})
save('KERNEL_COST_PROFILE.json',{'timing_scope':'inclusive, nested, non-additive','windows':cost})
save('SAME_ACCURACY_BENCHMARK.json',{'status':'PASS_SCOPED','same_compiler':'rustc1.99.0 b940084d7; same native host and releasecodegenunits1','comparisons':comparisons,'variation':'PLUS plateau has2 repetitions; initial instruments and ZERO have1 each. Do not claim negative instrumentation overhead from unmatched wall variation.'})
save('PROFILE_OUTCOME.json',summary)
save('NATIVE_JOB_RECEIPT.json',receipt)
print(json.dumps({k:v for k,v in summary.items() if k not in ['tested_native_windows','implementation_matches']},indent=2))
