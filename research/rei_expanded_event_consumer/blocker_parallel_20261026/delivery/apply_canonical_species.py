"""Apply frozen two-ID semantic mirrors only after root's canonical-adoption GO.
No science imports/execution or external mutation. Writes canonical_patch copies.
GO JSON requires authorized=true, action='apply_two_species_canonical', and
admitted_node_ids exactly HE-EXP-SPECIES/REC-EXP-SPECIES.
Requires released ADMISSION.json plus independent review/VALIDATION.json.
"""
import time
START=time.perf_counter()
import copy
import datetime
import hashlib
import json
import pathlib
import re
import resource
import signal
import sys
UNIT=pathlib.Path(__file__).resolve().parents[1]
BASE=UNIT/'recovery/canonical_base'
OUT=UNIT/'canonical_patch'
IDS={'HE-EXP-SPECIES','REC-EXP-SPECIES'}
STATUS='IMPLEMENTATION_VERIFIED_SCOPED_SPECIES_PROJECTION'
RETURN='returns/REI_SPECIES_PROJECTION_20261026.json'
PREFIX='research/rei_expanded_event_consumer/blocker_parallel_20261026/'
PINS={'DAG.json':'f898e3130242e108c05bfc75751cb5d268654019',
'contracts/HE-EXP-SPECIES.json':'4b30e6118a2acd61c23127b8a3f67cc03d665fa8',
'contracts/REC-EXP-SPECIES.json':'40a9f4d385d438076de262958972b58f767ccc23',
'node_plans/HE-EXP-SPECIES.md':'f04a9cae12a44d12d9d1bd04a2e57d08ca3524cf',
'node_plans/REC-EXP-SPECIES.md':'b7dda39d53d99df257ee468561206d036d26fec5',
'status/CURRENT_STATUS.json':'37b0687df054c9d82711eca3072b5981b8ea9db7'}
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def enc(v):return (json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
def read(name):return json.loads((UNIT/name).read_text())
def evidence(name):
    b=(UNIT/name).read_bytes()
    return {'path':PREFIX+name,'bytes':len(b),'sha256':sha(b)}
def check():
    assert time.process_time()<5 and time.perf_counter()-START<10,'MECHANICAL_PHASE_CAP'
def signal_cap(s,f):raise RuntimeError('MECHANICAL_PHASE_CAP_SIGNAL:'+str(s))
def apply(go):
    assert go['authorized'] is True and go['action']=='apply_two_species_canonical'
    assert set(go['admitted_node_ids'])==IDS
    assert not OUT.exists(),'NO_OVERWRITE_CANONICAL_OUTPUT'
    for name,pin in PINS.items():assert blob((BASE/name).read_bytes())==pin,name
    review=read('review/VALIDATION.json');admission=read('ADMISSION.json')
    assert set(review['canonical_decision']['closed_existing_nodes'])==IDS
    assert review['decision']=='PASS_SCOPED_PARALLEL_COMPONENTS_AND_TWO_CANONICAL_SPECIES_NODES'
    assert review.get('blocking_findings')==[]
    assert admission, 'ROOT_ADMISSION_REQUIRED'
    results=read('implementation/attempt01/TEST_RESULTS.json')
    assert results['passed'] is True and results['pass_count']==results['total']==25
    actual=read('implementation/attempt01/SPECIES_PROJECTION.json')
    execution=read('implementation/attempt01/RECEIPT.json')
    manifest=read('species/INPUT_MANIFEST.json')
    # This is structural evidence reuse, never a species/rate calculation.
    assert len(actual['historical21'])==21 and len(actual['atomic_targets'])==7
    assert len(actual['extensions'])==71
    assert actual['physical_provider_admitted'] is False
    common={'unit_id':'REI-PARALLEL-BLOCKERS-20261026',
      'current_scoped_state':STATUS,'consumer_repo':'cosmosapjw-quantum/rei_bianchi',
      'authoritative_identity_lead':'cosmosapjw-quantum/WU088_HH',
      'input_pins':manifest['inputs'],
      'execution_results':evidence('implementation/attempt01/TEST_RESULTS.json'),
      'species_results':evidence('implementation/attempt01/SPECIES_PROJECTION.json'),
      'execution_receipt':evidence('implementation/attempt01/RECEIPT.json'),
      'measured_execution':{k:execution[k] for k in ['exit_code','whole_child_CPU_s','whole_child_wall_s','wrapper_CPU_s_separate','new_execution_planning_CPU_debit_s']},
      'independent_review':evidence('review/VALIDATION.json'),
      'independent_decision':review['decision'],'root_admission':evidence('ADMISSION.json'),
      'root_admission_decision':admission.get('decision',admission.get('status')),
      'source_commit':None,'source_commit_status':'PENDING_ACTUAL_PUBLICATION_ACK; no future/self-referential hash',
      'physical_provider_admitted':False,'numeric_rates_admitted':False,
      'full_differential_provider_count':actual['full_differential_provider_count'],
      'thermal_heat':None,'automatic_normalization_conversion':False,
      'electron_pools_interchangeable':False,'L4_ready':False,'global_physical_completion':None}
    he=copy.deepcopy(common)
    he.update({'scope':'Seven isotope targets and requested charge labels projected into WU identity inventory; thermal/fast electron pools distinct. Unsupported full-law pairs remain INPUT_PENDING with null rate.',
      'actual_counts':{'isotope_targets':len(actual['atomic_targets']),'atomic_charge_states':actual['atomic_charge_states'],'neutron_material_states':actual['neutron_material_states']},
      'selected_pair_queries':actual['selected_pair_queries'],
      'pass_next':'Owner selects an admitted pair for HE-EXCHANGE; no admitted physical pair inferred.'})
    rec=copy.deepcopy(common)
    rec.update({'scope':'Exact ordered21 historical nucleus/charge labels and REC indices through HE crosswalk;71 source-referenced extensions UNADMITTED. No isotope-rate equality, complete-state equivalence or normalization substitution.',
      'actual_counts':{'historical_ordered_material_labels':len(actual['historical21']),'unadmitted_extensions':len(actual['extensions'])},
      'REC_state_convention':actual['REC_state_convention'],'state_partition_map':None,
      'pass_next':'Owner supplies a source-bound channel for REC-EXP-SPECTRAL; physical source/channel admission not inferred.'})
    obs={'HE-EXP-SPECIES':he,'REC-EXP-SPECIES':rec}
    ret={'schema':'REI_TWO_SPECIES_CANONICAL_RETURN_V1','unit_id':'REI-PARALLEL-BLOCKERS-20261026',
      'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'base_commit':'a5db4bac9dafadae29685bbea3cec7f43ab990b2','observations':obs,
      'completion_delta':{'baseline':27,'after':29,'total':88,'remaining':59,
        'closed_existing_ids':sorted(IDS),'new_nodes':0,'physical_completion':None},
      'integration_branch':'research/rei-parallel-blockers-20261026',
      'central_branch_adoption':'PENDING_SEPARATE_PUBLICATION; not implied by integration branch',
      'other_blocker_families_open':7,'preserved_global_gates':{'L4_ready':False,'N6':'HOLD','global_physical_completion':None}}
    old=json.loads((BASE/'DAG.json').read_text());new=copy.deepcopy(old)
    assert len(old['nodes'])==88 and len(old['authorities'])==15 and len(old['integration_edges'])==17
    wrappers={}
    for n in new['nodes']:
        if n['id'] in IDS:
            assert n==json.loads((BASE/('contracts/'+n['id']+'.json')).read_text())
            assert n['lead_repo']=='cosmosapjw-quantum/WU088_HH'
            n['current_status']=STATUS
            n['status_observation']={'source_file':RETURN,'json_pointer':'/observations/'+n['id'],'value':obs[n['id']]}
            wrappers[n['id']]=n
    assert set(wrappers)==IDS
    assert [n['id'] for n in old['nodes']]==[n['id'] for n in new['nodes']]
    changed={a['id'] for a,b in zip(old['nodes'],new['nodes']) if a!=b};assert changed==IDS
    for a,b in zip(old['nodes'],new['nodes']):
        assert a['contract']==b['contract']
        if a['id'] in IDS:
            aa={k:v for k,v in a.items() if k not in {'current_status','status_observation'}}
            bb={k:v for k,v in b.items() if k not in {'current_status','status_observation'}}
            assert aa==bb
        else:assert a==b
    assert {k:v for k,v in old.items() if k!='nodes'}=={k:v for k,v in new.items() if k!='nodes'}
    assert new['L4_ready'] is False and new['global_physical_completion'] is None
    files={'DAG.json':enc(new),RETURN:enc(ret)}
    rowsold=json.loads((BASE/'status/CURRENT_STATUS.json').read_text());rows=copy.deepcopy(rowsold)
    assert len(rows)==88
    for row in rows:
        if row['id'] in IDS:
            row['current_status']=STATUS;row['observation']=wrappers[row['id']]['status_observation']
    assert {a['id'] for a,b in zip(rowsold,rows) if a!=b}==IDS
    for a,b in zip(rowsold,rows):
        if a['id'] in IDS:assert {k:v for k,v in a.items() if k not in {'current_status','observation'}}=={k:v for k,v in b.items() if k not in {'current_status','observation'}}
        else:assert a==b
    files['status/CURRENT_STATUS.json']=enc(rows)
    for nodeid,wrapper in wrappers.items():
        files['contracts/'+nodeid+'.json']=enc(wrapper)
        name='node_plans/'+nodeid+'.md';text=(BASE/name).read_text()
        match=re.search(r'```json\n(.*?)\n```',text,re.S);assert match and json.loads(match.group(1))==next(n for n in old['nodes'] if n['id']==nodeid)
        out=text[:match.start(1)]+enc(wrapper).decode().rstrip('\n')+text[match.end(1):]
        out,count=re.subn(r'(?m)^Current status: `[^`]*`$', 'Current status: `'+STATUS+'`',out);assert count==1
        # Apart from the current header and embedded wrapper, all plan bytes persist.
        def masked(t):
            t=re.sub(r'```json\n.*?\n```','JSON_WRAPPER',t,flags=re.S)
            return re.sub(r'(?m)^Current status: `[^`]*`$','CURRENT_HEADER',t)
        assert masked(text)==masked(out)
        assert json.loads(re.search(r'```json\n(.*?)\n```',out,re.S).group(1))==wrapper
        files[name]=out.encode()
    assert set(files)==set(PINS)|{RETURN}
    check()
    OUT.mkdir()
    mapping=[]
    for name,data in files.items():
        check();path=OUT/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        mapping.append({'path':'canonical_patch/'+name,'git_path':'research/orchestration_expansion_20261025/'+name,'bytes':len(data),'sha256':sha(data)})
    validation={'status':'pass_scoped_mechanical_only','changed_existing_node_ids':sorted(changed),
      'nodes':88,'nested_contracts_preserved':88,'other_nodes_semantically_unchanged':86,
      'authority_snapshots_preserved':15,'integration_edges_preserved':17,
      'all_three_JSON_mirrors_and_plan_JSON_headers_agree':True,
      'base_identity_receipt':'recovery/CANONICAL_BASE_RECEIPT.json','files':mapping,
      'source_science_execution':0,'external_writes':0,'L4_ready':False,'global_physical_completion':None}
    (UNIT/'delivery/CANONICAL_PATCH_VALIDATION.json').write_bytes(enc(validation))
    return validation
def main():
    go=json.loads(pathlib.Path(sys.argv[1]).read_text())
    receipt=UNIT/'delivery/CANONICAL_PACKAGE_RECEIPT.json';assert not receipt.exists()
    signal.signal(signal.SIGXCPU,signal_cap);signal.signal(signal.SIGALRM,signal_cap)
    resource.setrlimit(resource.RLIMIT_CPU,(5,6));signal.setitimer(signal.ITIMER_REAL,max(.001,10-(time.perf_counter()-START)))
    result=None;error=None
    try:result=apply(go);check()
    except BaseException as ex:error=type(ex).__name__+': '+str(ex)
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);cpu=time.process_time();wall=time.perf_counter()-START
        record={'phase':'CANONICAL','status':'failed' if error else 'completed','error':error,
          'incremental_CPU_s':cpu,'incremental_wall_s':wall,'phase_caps':{'CPU_s':5,'wall_s':10},
          'failed_attempts_charged':True,'scientific_evaluations':0,'external_writes':0,
          'metadata_overhead_unmeasured':'UNKNOWN_NOT_ZERO'}
        receipt.write_bytes(enc(record));print(json.dumps(record))
    return 1 if error else 0
if __name__=='__main__':sys.exit(main())

