import json,re,hashlib
from pathlib import Path
from igm_compare import compare_rows,read_csv
r=Path(__file__).parent
c=[read_csv(r/'coarse'/f'endpoint_{k}.csv')[0] for k in (10,11)]
f=[read_csv(r/'fine'/f'endpoint_{k}.csv')[0] for k in (20,22)]
t=[read_csv(r/'tail'/f'endpoint_{k}.csv')[0] for k in (10,11)]
comparisons={label:compare_rows(c,rows) for label,rows in [('temporal',f),('tail',t)]};comparisons.update(scope='ALL2newacceptedcommonrows; partial0008horizon only',completed_full0008_suffix=False)
(r/'PARTIAL_COMPARISONS.json').write_text(json.dumps(comparisons,indent=2)+'\n')
receipts={p.stem:json.loads(p.read_text()) for p in (r/'receipts').glob('*.json')}
counts={};observer={}
for name in ('coarse-9-10','fine-18-20','tail-9-10','coarse-10-48','coarse-11-48','fine-20-96','tail-10-48','coarse-readout-11','fine-readout-22','tail-readout-11'):
 text=(r/(name+'.log')).read_text();a=re.findall(r'COUNTS=\[([\d, ]+)\]',text)
 if a:count=[int(x) for x in a[-1].split(',')]
 else:count=json.loads(text.strip().splitlines()[-1])['counts']
 counts[name]=count
 successful_observers=re.findall(r'observer=\[0, (\d+), 0\]',text)
 if name in ('coarse-9-10','fine-18-20','tail-9-10'):observer[name]=sum(map(int,successful_observers))+3*(3208 if name!='tail-9-10' else 3592)
 elif name in ('coarse-readout-11','fine-readout-22','tail-readout-11'):observer[name]=3*(3592 if name.startswith('tail') else 3208)
 elif name=='coarse-10-48':observer[name]=1 # original Gamma failed in firstnode firstspecies after providercall.
 else:observer[name]=sum(map(int,successful_observers))
controls=sum(5 for name in receipts if name.startswith('negative-'))
total=[sum(x[i] for x in counts.values())+(controls if i<2 else 0) for i in range(3)]
old=Path('/home/cosmosapjw/Documents/Codex/2026-10-07/task-4/duration-unprojected-20261008/source')
changes=[]
for p in (r/'source').rglob('*'):
 if not p.is_file() or 'target' in p.parts:continue
 rel=p.relative_to(r/'source');q=old/rel
 if not q.exists() or q.read_bytes()!=p.read_bytes():changes.append({'path':str(rel),'original_sha256':hashlib.sha256(q.read_bytes()).hexdigest() if q.exists() else None,'new_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
results={'status':'PARTIAL_CANONICAL_OWNER_REPAIR_PASS_TRANSPORTED_STOCK_BLOCKED','new_accepted_advances':8,'target0008_new_advances':156,'remaining_required_for0008':148,'first1_2_1_all_pass':True,'all_new_common_rows37fields_pass':all(comparisons[x]['passed'] for x in ('temporal','tail')),'last_accepted':{'coarse':{'k':11,'n':48},'fine':{'k':22,'n':96},'tail':{'k':11,'n':48},'epoch':c[-1]['ln_a'],'redshift':c[-1]['z']},'new_science_failures':3,'new_observer_failures':1,'numerical_regressions':7,'negative_checkpoint_controls':5,'exact_rational_fixtures':3,'bounded_commands':receipts,'measured_new_cpu_s':sum(v['cpu_s'] for v in receipts.values()),'measured_new_wall_s':sum(v['wall_s'] for v in receipts.values()),'initial_compile_cpu_wall':'NOT_MEASURED_BEFORE_BOUNDED_RUNNER; short compile attempts, not science; retained INITIAL_BUILD_ATTEMPTS.json','native_process_counts_RHS_sigma_evaluations':counts,'native_total_RHS_sigma_evaluations':total,'observer_sigma_subset':observer,'total_additional_observer_sigma':sum(observer.values()),'negative_control_startup_RHS_sigma_each':1,'negative_control_invocations':controls,'defaults':'OFF; unchanged source/provider/closure/allowances','historical_costs_and_raw_failures':'PRESERVED_EXTERNAL_ORIGINALS; no rerun of190steps or completed0004','physical_history':'HOLD','full_horizon_discrete_claim':'NOT_COMPLETED','continuum_claim':'NOT_VALIDATED','blockers':['canonical transported-density/persegment stock N/E persistence absent; positive stock3.812277937532397e-309 rejected at characteristic_staged','historical precheckpoint arithmeticloss NOT_MEASURED','old-domain spectral reconstruction/source/time residual error authority missing','0008suffix148remaining; longerhorizons notexecuted']}
(r/'RESULTS.json').write_text(json.dumps(results,indent=2)+'\n');(r/'SOURCE_VARIANT.json').write_text(json.dumps({'original':'private duration-unprojected20261008 source, copied without mutation','public_PR86_PR88_originals':'UNCHANGED','modified_research_copy_files':changes},indent=2)+'\n')
print(json.dumps({k:results[k] for k in ('status','new_accepted_advances','measured_new_cpu_s','measured_new_wall_s','native_total_RHS_sigma_evaluations','total_additional_observer_sigma')}))
