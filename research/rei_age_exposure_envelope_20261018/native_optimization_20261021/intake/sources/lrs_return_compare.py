"""Frozen root contract: compare saved LRS JSON; do not run native binaries."""
from pathlib import Path
import json, math, hashlib, argparse
P=Path(__file__).resolve().parents[1]/'intake/backups'
A=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--new-evidence',type=Path,default=P/'extracted/run/evidence',help='Directory containing the 19 new case directories')
parser.add_argument('--baseline-evidence',type=Path,default=P/'c10_selected/coder/v2/evidence',help='Directory containing C10 v2 replay and paired cache directories')
parser.add_argument('--output',type=Path,default=A/'compare_ncp_return.json',help='Output JSON path')
args=parser.parse_args()
NEW=args.new_evidence.resolve()
OLD=args.baseline_evidence.resolve()
OUTPUT=args.output.resolve()
EXPECTED={f'{mode}_{method}_n{n}' for mode,methods in [('fixed',{'radau':[2,4,8,16],'ssprk':[8,16,32]}),('birth',{'radau':[4,8,16],'ssprk':[4,8,16]}),('disabled',{'radau':[4,8,16],'ssprk':[4,8,16]})] for method,levels in methods.items() for n in levels}
EXPECTED_CONTROLS={f'paired_{mode}_0_cell-cache' for mode in ['fixed','birth','disabled']}
EXPECTED_SOURCE_SUFFIXES={'adapter/src/lib.rs','adapter/src/main.rs','native_owner/rust/rei_microphysics/src/axbi_native_rhs.rs'}
PHYSICAL=['N','completed','config','failure','initial','k_ref20','method','mode','native_rhs_attempts_including_fd_replay','records','schema']
WORK=['charged_rhs_attempts','occupied_cell_preparations','node_visits']
CLONES=['cached_prepared_node_clones','cached_prepared_state_clones']
TIMES='exclusive_evaluation_times_and_inclusive_jacobian'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def compare(x,y):
    stats={'numeric_leaves':0,'finite_numeric_leaves':0,'non_numeric_leaves':0,'dict_containers':0,'list_containers':0,'structural_differences':0,'mismatch_count':0,'max_abs_difference':0,'max_relative_difference':0}
    issues=[];zeros=[]
    def issue(r):stats['mismatch_count']+=1;issues.append(r)
    def walk(a,b,path):
        if isinstance(a,(int,float)) and not isinstance(a,bool) and isinstance(b,(int,float)) and not isinstance(b,bool):
            stats['numeric_leaves']+=1
            if not math.isfinite(a) or not math.isfinite(b):issue({'path':path,'reason':'nonfinite','baseline':str(a),'new':str(b)});return
            stats['finite_numeric_leaves']+=1
            ab=abs(a-b);rel=ab/max(abs(a),abs(b)) if max(abs(a),abs(b)) else 0
            stats['max_abs_difference']=max(stats['max_abs_difference'],ab);stats['max_relative_difference']=max(stats['max_relative_difference'],rel)
            if a!=b:issue({'path':path,'baseline':a,'new':b,'abs_difference':ab,'relative_difference':rel})
            if a==0 and b==0 and math.copysign(1,a)!=math.copysign(1,b):zeros.append({'path':path,'baseline_sign':math.copysign(1,a),'new_sign':math.copysign(1,b)})
        elif isinstance(a,dict) and isinstance(b,dict):
            stats['dict_containers']+=1
            if set(a)!=set(b):stats['structural_differences']+=1;issue({'path':path,'keys_baseline':sorted(a),'keys_new':sorted(b)})
            for k in sorted(set(a)&set(b)):walk(a[k],b[k],path+'/'+k)
        elif isinstance(a,list) and isinstance(b,list):
            stats['list_containers']+=1
            if len(a)!=len(b):stats['structural_differences']+=1;issue({'path':path,'length_baseline':len(a),'length_new':len(b)})
            for i,(u,v) in enumerate(zip(a,b)):walk(u,v,path+'/'+str(i))
        else:
            stats['non_numeric_leaves']+=1
            if type(a)!=type(b) or a!=b:issue({'path':path,'baseline':a,'new':b,'baseline_type':type(a).__name__,'new_type':type(b).__name__})
    walk(x,y,'')
    return {'stats':stats,'representative_differing_paths':issues[:30],'signed_zero_differences':zeros}
def classify(r):
    expected=set(PHYSICAL)|{'wall_s','native_evaluation'}
    ev=r['native_evaluation'];pr=ev['profile']
    return {'physical_keys':PHYSICAL,'timing_only_top_level':['wall_s'],'evaluation_keys':sorted(ev),'profile_work_keys':WORK,'profile_clone_keys':CLONES,'profile_timing_only_keys':[TIMES],'profile_control_keys':['timings_enabled'],'unclassified_top_level_keys':sorted(set(r)-expected),'missing_top_level_keys':sorted(expected-set(r)),'unclassified_evaluation_keys':sorted(set(ev)-{'mode','profile'}),'unclassified_profile_keys':sorted(set(pr)-set(WORK+CLONES+[TIMES,'timings_enabled']))}
def pair(op,np):
    old,new=load(op),load(np);oi,ni=load(op.parent/'inputs.json'),load(np.parent/'inputs.json')
    one={'baseline_raw_path':str(op),'new_raw_path':str(np),'baseline_raw_sha256':sha(op),'new_raw_sha256':sha(np),'baseline_binary_sha256':oi.get('binary_sha256'),'new_binary_sha256':ni.get('executable_sha256'),'baseline_actual_argv':oi['argv'],'new_actual_argv':ni['argv'],'baseline_mode':old['native_evaluation']['mode'],'new_mode':new['native_evaluation']['mode'],'physical':compare({k:old[k] for k in PHYSICAL},{k:new[k] for k in PHYSICAL}),'classification':{'baseline':classify(old),'new':classify(new)},'evaluation':{'mode':{'baseline':old['native_evaluation']['mode'],'new':new['native_evaluation']['mode']},'work':compare({k:old['native_evaluation']['profile'][k] for k in WORK},{k:new['native_evaluation']['profile'][k] for k in WORK}),'clones':{k:{'baseline':old['native_evaluation']['profile'][k],'new':new['native_evaluation']['profile'][k]} for k in CLONES},'timing_only':{'baseline':old['native_evaluation']['profile'][TIMES],'new':new['native_evaluation']['profile'][TIMES]},'timings_enabled':{'baseline':old['native_evaluation']['profile']['timings_enabled'],'new':new['native_evaluation']['profile']['timings_enabled']}},'top_level_timing_only':{'baseline_wall_s':old['wall_s'],'new_wall_s':new['wall_s']}}
    mapped={}
    for ok,ov in oi['source_sha256'].items():
        suffix=ok.split('/baseline/')[-1];nk=next((k for k in ni['source_sha256'] if k.endswith(suffix)),None)
        mapped[suffix]={'baseline':ov,'new':ni['source_sha256'].get(nk),'equal':ov==ni['source_sha256'].get(nk)}
    one['declared_source_files']=mapped
    return one
validation=[]
def check_set(label,actual,expected):
    if actual!=expected:validation.append({'kind':label,'missing':sorted(expected-actual),'unexpected':sorted(actual-expected)})
check_set('new_matrix_cases',{p.parent.name for p in NEW.glob('*/raw.json')},EXPECTED)
check_set('baseline_replay_cases',{p.parent.name[len('replay_'):] for p in OLD.glob('replay_*/raw.json')},EXPECTED)
check_set('baseline_cache_controls',{p.parent.name for p in OLD.glob('paired_*_0_cell-cache/raw.json')},EXPECTED_CONTROLS)
for name in sorted(EXPECTED):
    for label,directory,eval_mode in [('new',NEW/name,'CellCache'),('baseline',OLD/('replay_'+name),'CellBorrowed')]:
        for filename in ['raw.json','inputs.json']:
            if not (directory/filename).is_file():validation.append({'kind':'missing_input','side':label,'path':str(directory/filename)})
        if (directory/'raw.json').is_file():
            raw=load(directory/'raw.json')
            actual=f"{raw.get('mode')}_{raw.get('method')}_n{raw.get('N')}"
            if actual!=name or raw.get('native_evaluation',{}).get('mode')!=eval_mode:validation.append({'kind':'case_identity','side':label,'path':str(directory),'expected_case':name,'actual_case':actual,'expected_evaluation':eval_mode,'actual_evaluation':raw.get('native_evaluation',{}).get('mode')})
for name in sorted(EXPECTED_CONTROLS):
    directory=OLD/name
    for filename in ['raw.json','inputs.json']:
        if not (directory/filename).is_file():validation.append({'kind':'missing_control_input','path':str(directory/filename)})
    if (directory/'raw.json').is_file():
        raw=load(directory/'raw.json');mode=name.split('_')[1]
        if (raw.get('mode'),raw.get('method'),raw.get('N'),raw.get('native_evaluation',{}).get('mode'))!=(mode,'radau',16,'CellCache'):validation.append({'kind':'cache_control_identity','path':str(directory),'expected_mode':mode,'actual_mode':raw.get('mode'),'actual_method':raw.get('method'),'actual_N':raw.get('N'),'actual_evaluation':raw.get('native_evaluation',{}).get('mode')})
OUTPUT.parent.mkdir(parents=True,exist_ok=True)
if validation:
    incomplete={'schema':'rei_lrs_frozen_saved_output_comparison.v2','status':'INCOMPLETE_INPUTS','native_execution':False,'root_escalation_required':True,'input_discrepancies':validation}
    OUTPUT.write_text(json.dumps(incomplete,indent=2));print(json.dumps(incomplete,indent=2));raise SystemExit(2)
rows=[]
for op in sorted(OLD.glob('replay_*/raw.json')):
    name=op.parent.name[len('replay_'):];r=pair(op,NEW/name/'raw.json');r['case']=name;rows.append(r)
controls=[]
for op in sorted(OLD.glob('paired_*_0_cell-cache/raw.json')):
    old=load(op);name=f"{old['mode']}_{old['method']}_n{old['N']}";r=pair(op,NEW/name/'raw.json');r['case']=name;controls.append(r)
def totals(items):
    stats={}
    for r in items:
        for k,v in r['physical']['stats'].items():
            stats[k]=max(stats.get(k,0),v) if k.startswith('max_') else stats.get(k,0)+v
    return {'cases':len(items),'physical_stats':stats,'signed_zero_differences':sum(len(r['physical']['signed_zero_differences']) for r in items),'work_counter_mismatches':sum(r['evaluation']['work']['stats']['mismatch_count'] for r in items),'classification_gaps':[r['case'] for r in items if any(c[k] for c in r['classification'].values() for k in ['unclassified_top_level_keys','missing_top_level_keys','unclassified_evaluation_keys','unclassified_profile_keys'])],'source_hash_mismatches':[r['case'] for r in items if set(r['declared_source_files'])!=EXPECTED_SOURCE_SUFFIXES or any(not v['equal'] for v in r['declared_source_files'].values())]}
result={'schema':'rei_lrs_frozen_saved_output_comparison.v1','native_execution':False,'baseline_archive_sha256':'492681e5ed7f1f53820b3bdcf24f397cfedbb6dac20a1d6dd917c7a9e2aa866e','new_archive_sha256':'b1cb2ce21c14626794c69585822a29ed016206769ec1dd217ae59ec3f70f53bd','baseline':'C10 v2 binary3eeda61...106a;19 actual cell-borrowed replay outputs; three RadauN16 actual cell-cache outputs supplemental','rules':{'physical_keys':PHYSICAL,'numeric':'finite exact numeric observations, no solver PASS inference; signed zero differences preserved separately','wall_s':'timing only','native_evaluation':'all keys classified separately; modes/clones expected to differ across borrowed/cache','dt_s':'physical; no broad suffix exclusion'},'aggregate19':totals(rows),'aggregate_cache_controls':totals(controls),'replay19':rows,'same_mode_cache_controls':controls,'caveats':['The full19 baseline is borrowed, not cached.','Three recorded source-file hashes match across hosts; full frozen source closure is independent reviewer responsibility.','No borrowed N2 argv or executable provenance is invented for new borrowed smoke.','No speedup or scientific admission issued.','Do not retroactively label C10 as bitwise-verified based on this JSON comparison.']}
result['schema']='rei_lrs_frozen_saved_output_comparison.v2'
result['status']='SAVED_OUTPUT_COMPARISON_COMPLETE'
result['validated_expected_matrix_cases']=sorted(EXPECTED)
result['validated_expected_cache_controls']=sorted(EXPECTED_CONTROLS)
result['input_directories']={'new_evidence':str(NEW),'baseline_evidence':str(OLD)}
result['root_escalation_required']=any(r['physical_stats']['mismatch_count']>0 or r['signed_zero_differences']>0 or r['work_counter_mismatches']>0 or r['classification_gaps'] or r['source_hash_mismatches'] for r in [result['aggregate19'],result['aggregate_cache_controls']])
OUTPUT.write_text(json.dumps(result,indent=2))
print(json.dumps({k:result[k] for k in ['aggregate19','aggregate_cache_controls','root_escalation_required']},indent=2))

