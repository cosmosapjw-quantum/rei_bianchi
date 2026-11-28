import json,pathlib,hashlib
root=pathlib.Path(__file__).resolve().parent;base=pathlib.Path('/workspace/scratch/67b7545a589e/central_delta/base');prior=base.parent/'result';result=root/'result';reapplied=root/'reapplied'
ids={'HE-EXCHANGE','HE-EXP-PAIR','HE-CLOSURE','HE-EXP-CLOSURE'}
def load(p):return json.loads(p.read_text())
b=load(base/'DAG.json');p=load(prior/'DAG.json');r=load(result/'DAG.json');bc=load(base/'status/CURRENT_STATUS.json');pc=load(prior/'status/CURRENT_STATUS.json');rc=load(result/'status/CURRENT_STATUS.json');ob=load(result/'status/HE_EXP_EVENT03_20261027.json')
bi={x['id']:x for x in b['nodes']};pi={x['id']:x for x in p['nodes']};ri={x['id']:x for x in r['nodes']};bc={x['id']:x for x in bc};pc={x['id']:x for x in pc};rc={x['id']:x for x in rc}
checks={}
checks['88_ids_preserved']=len(bi)==88 and bi.keys()==ri.keys();checks['only_four_dag_nodes_changed']={k for k in bi if bi[k]!=ri[k]}==ids
checks['only_status_observation_changed']=all({k:v for k,v in bi[i].items() if k!='status_observation'}=={k:v for k,v in ri[i].items() if k!='status_observation'} for i in ids)
checks['84_status_rows_unchanged']=all(bc[i]==rc[i] for i in bi if i not in ids);checks['target_rows_observation_only']=all({k:v for k,v in bc[i].items() if k!='observation'}=={k:v for k,v in rc[i].items() if k!='observation'} for i in ids)
checks['all_prior_target_observations_preserved']=all(ob['previous_observations'][i]==pi[i]['status_observation'] for i in ids)
checks['all_prior_target_plans_preserved']=all((result/('node_plans/'+i+'.md')).read_bytes().startswith((prior/('node_plans/'+i+'.md')).read_bytes()) for i in ids)
checks['prior_historical_status_exact']=(result/'status/HE_EXP_FINITE_DRIFT_20261027.json').read_bytes()==(prior/'status/HE_EXP_FINITE_DRIFT_20261027.json').read_bytes()
checks['contracts_match_dag']=all(load(result/('contracts/'+i+'.json'))==ri[i] for i in ids)
checks['top_level_unchanged']={k:v for k,v in b.items() if k!='nodes'}=={k:v for k,v in r.items() if k!='nodes'}
checks['claim_ceiling']=r['global_physical_completion'] is None and r['L4_ready'] is False
files=sorted(p.relative_to(result) for p in result.rglob('*') if p.is_file());checks['reapply_file_set_and_bytes']=files==sorted(p.relative_to(reapplied) for p in reapplied.rglob('*') if p.is_file()) and all((result/p).read_bytes()==(reapplied/p).read_bytes() for p in files)
report={'status':'PASS' if all(checks.values()) else 'FAIL','base_head':'5abe0d19df95db730e3e33bae0373c81ba37ce89','source_commit':'86306233ce74f5da73b862ec360d5f2ad5c679ca','checks':checks,'payload_files':len(files),'changed_nodes':sorted(ids),'unchanged_nodes':84,'scientific_executions':0,'publication_performed':False,'executor':{'requested':'lower-tier mechanical executor','observed_model':'not independently observable'}}
(root/'MECHANICAL_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
