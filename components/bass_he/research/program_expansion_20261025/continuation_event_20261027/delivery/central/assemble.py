"""Mechanically append EVENT03 observations to the frozen DRIFT02 candidate."""
import copy, json, pathlib, shutil, sys
root=pathlib.Path(__file__).resolve().parent
prior=pathlib.Path('/workspace/scratch/67b7545a589e/central_delta/result')
out=pathlib.Path(sys.argv[1])
ids=['HE-EXCHANGE','HE-EXP-PAIR','HE-CLOSURE','HE-EXP-CLOSURE']
contrib={
 'HE-EXCHANGE':'Conditional raw reactive number, momentum, kinetic energy and full second-moment stress contributions for a supplied 2-to-2 event.',
 'HE-EXP-PAIR':'WU R4 source-only intake; provider method, spin and state ownership boundaries remain explicit and physical binding remains open.',
 'HE-CLOSURE':'Conditional reactive population count and centered heat contribution; heat capacity remains separate and no automatic thermalization is assumed.',
 'HE-EXP-CLOSURE':'Population-derived internal energy witness has a single owner; product birth pool remains UNASSIGNED.'}
statuspath='status/HE_EXP_EVENT03_20261027.json'
source='86306233ce74f5da73b862ec360d5f2ad5c679ca';tree='1d84872e4314d37d8596ed1eaaa441e90b4410ff'
def load(path):return json.loads(path.read_text())
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
dag=load(prior/'DAG.json'); rows=load(prior/'status/CURRENT_STATUS.json'); index={n['id']:n for n in dag['nodes']}; previous={i:copy.deepcopy(index[i]['status_observation']) for i in ids}
ob={'schema_version':1,'unit_id':'HE-EXP-EVENT-03','observation_date':'2026-10-27','scope':'Scoped conditional nonrelativistic reactive 2-to-2 moments and source-only R4 inventory; no physical promotion.', 'publication_status':'LOCAL_PREPARED_NOT_PUBLISHED','publication_performed':False,'source_intake':{'repository':'cosmosapjw-quantum/BASS_HE','source_commit':source,'source_tree':tree,'source_publication_status':'LOCAL_PREPARED_NOT_PUBLISHED','source_published':False,'task_path':'research/program_expansion_20261025/continuation_event_20261027','inventory':{'exact_identity_records':104,'provider_variants':138,'saved_event_references':155,'source_only':True},'conditional_assumptions':'Nonrelativistic two massive reactants and two massive products with fixed conserved compositional mass, explicit internal energies and supplied full axisymmetric CM angular moments.','validation':{'distinct_test_methods':22,'process_count':1,'outcomes':['PASS'],'cpu_s':0.20865536699999998,'wall_s':0.20785328000056325,'caps':{'cpu_s':4,'wall_s':15},'repairs_used':0,'independent_review':'PASS_SCOPED_CONDITIONAL_EVENT03'},'local_dag':{'scoped_products_complete':4,'physical_dependencies_open':3,'total_nodes':7},'inherited_HE101':{'C8':'PARTIAL_EXPORT','delivery':'19/20','repair_reserve':0,'new_old_START_count':0},'physical_provider_admitted':False,'production_status':'NOT_APPROVED','activation':False,'physical_allocation':'UNALLOCATED','global_physical_completion':None,'L4_ready':False},'previous_observations':previous,'observations':{}}
for i in ids:
 ob['observations'][i]={'unit_id':'HE-EXP-EVENT-03','current_scoped_state':index[i]['current_status'],'scoped_contribution':contrib[i],'source_intake':{'source_file':statuspath,'json_pointer':'/source_intake'},'previous_observation':{'source_file':statuspath,'json_pointer':'/previous_observations/'+i},'source_repository':'cosmosapjw-quantum/BASS_HE','source_commit':source,'source_tree':tree,'source_publication_status':'LOCAL_PREPARED_NOT_PUBLISHED','source_published':False,'publication_performed':False,'physical_provider_admitted':False,'production_status':'NOT_APPROVED','activation':False,'physical_allocation':'UNALLOCATED'}
 index[i]['status_observation']={'source_file':statuspath,'json_pointer':'/observations/'+i,'value':copy.deepcopy(ob['observations'][i])}
for row in rows:
 if row['id'] in ids:row['observation']=copy.deepcopy(index[row['id']]['status_observation'])
dump(out/'DAG.json',dag);dump(out/'status/CURRENT_STATUS.json',rows);dump(out/statuspath,ob)
(out/'status').mkdir(parents=True,exist_ok=True);shutil.copyfile(prior/'status/HE_EXP_FINITE_DRIFT_20261027.json',out/'status/HE_EXP_FINITE_DRIFT_20261027.json')
for i in ids:
 dump(out/('contracts/'+i+'.json'),index[i])
 p=out/('node_plans/'+i+'.md');p.parent.mkdir(parents=True,exist_ok=True)
 old=(prior/('node_plans/'+i+'.md')).read_text()
 p.write_text(old+'\n## HE-EXP-EVENT-03 observation\n\n'+contrib[i]+' Source is locally prepared and unpublished; physical inputs remain open. See `'+statuspath+'#/observations/'+i+'`.\n')
