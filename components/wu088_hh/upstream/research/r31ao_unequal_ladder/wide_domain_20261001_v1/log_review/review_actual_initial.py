"""Independent exact receipt arithmetic and identity inspection; no solver run."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib,json

HERE=Path(__file__).resolve().parent
NEW=HERE.parent
BASE=NEW.parent
RUNTIME=NEW/'runtime'

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')
def digest(x):return hashlib.sha256(x).hexdigest()
def sha(path):return digest(Path(path).read_bytes())
def load(path):return json.loads(Path(path).read_text())
def seal_check(value,key):
    assert value[key]==digest(canonical({k:v for k,v in value.items() if k!=key})),key
def interval(part):
    assert set(part)=={'lower_mantissa','upper_mantissa','exponent2'}
    lo,hi,e=(int(part[k]) for k in ('lower_mantissa','upper_mantissa','exponent2'))
    assert lo<=hi
    return Q(lo)*Q(2)**e,Q(hi)*Q(2)**e

def main():
    buildpath=RUNTIME/'build_log_cached/BUILD.json';build=load(buildpath)
    seal_check(build,'manifest_sha256');seal_check(build['source'],'sha256') if False else None
    assert build['source']['sha256']==digest(canonical(build['source']['files']))
    reviewed=load(HERE/'SOURCE_REVIEW.json')
    assert build['source']['sha256']==reviewed['reviewed_driver_source_identity']
    for path,h in build['source']['files'].items():assert sha(BASE/path)==h,path
    assert sha(buildpath.parent/build['binary'])==build['binary_sha256']
    assert sha(buildpath.parent/'frozen107_generated.hpp')==build['generated_header_sha256']
    assert sha(Path(build['backend_provenance']))==build['backend_provenance_sha256']
    for item in list(build['linkage']['libraries'].values())+build['linkage']['system_libraries']:
        assert sha(Path(item['path']))==item['sha256'],item['path']
    npz=BASE/'production_solver_20261001_v1/inputs/FROZEN_INPUTS.npz'
    assert sha(npz)==build['archive_sha256']
    records={};identities={str(buildpath.relative_to(BASE)):sha(buildpath)}
    plans={'CENTRAL':BASE/'native_execution_20261001_v1/runtime/pilot_plans/CENTRAL_PLAN.json',
           'W1':BASE/'production_solver_20261001_v1/runtime/endpoint_cutoff_probe_capped/W1_PLAN.json'}
    for label,path in plans.items():
        plan=load(path);seal_check(plan,'plan_sha256');seal_check(plan['tasks'][0],'task_sha256')
        receiptpath=RUNTIME/('LOG2_'+label+'.json');r=load(receiptpath);seal_check(r,'result_sha256')
        w=r['wrapper'];native=r if r['accepted'] else json.loads(r['native_stdout'])
        assert w['native_execution_observed'] is True
        assert w['build_manifest_sha256']==build['manifest_sha256']
        assert w['binary_sha256']==build['binary_sha256'] and w['build_source']==build['source']
        assert w['physical_window']==plan['window']
        for key,tok in plan['window'].items():
            q=Q(tok);assert q.numerator&(q.numerator-1)==0 and q.denominator&(q.denominator-1)==0
            assert w['log2_window'][key]==q.numerator.bit_length()-q.denominator.bit_length()
        assert native['task_sha256']==r['task_sha256']==plan['tasks'][0]['task_sha256']
        assert native['plan_sha256']==r['plan_sha256']==plan['plan_sha256']
        assert native['archive_sha256']==build['archive_sha256']==plan['archive_sha256']
        assert native['input_record_sha256']==build['input_record_sha256']==plan['input_record_sha256']
        assert native['build_source_sha256']==build['source']['sha256']
        assert native['index']==0 and native['precision_bits']==128
        assert native['accepted_component_radius_exp']==-48
        for claim in ['endpoint_included','normalization_applied','full_domain_integral','scientific_admission','production_admission']:
            assert native[claim] is False
        limits=w['native_limits']
        assert native['dispatched_evaluations']<=limits['max_evaluations']
        assert native['integration_calls']<=limits['max_integration_calls']
        assert type(w['elapsed_wall_ns']) is int and 0<w['elapsed_wall_ns']<(limits['wall_seconds']+5)*10**9
        expected_command=[str(buildpath.parent/build['binary']),'0',*[plan['window'][k] for k in ('l_t','T_t','l_u','T_u')],
                          *[str(limits[k]) for k in ('precision_bits','radius_exp','relative_goal','max_evaluations','max_integration_calls','wall_seconds','queued_panels','degree_limit')],r['task_sha256'],r['plan_sha256']]
        assert w['command']==expected_command
        if r['accepted']:
            assert r['status']=='RADIUS_MET' and r['flint_status']==w['returncode']==0
            bounds={part:interval(r['rectangle'][part]) for part in ('real','imag')}
            radii={part:(hi-lo)/2 for part,(lo,hi) in bounds.items()}
            assert all(0<=rad<=Q(2)**-48 for rad in radii.values())
        else:
            assert w['returncode']==r['returncode']==2 and r['reason']=='NONZERO_NATIVE_EXIT'
            assert native['status']=='INTEGRATOR_NO_CONVERGENCE' and native['flint_status']==2
            assert native['rectangle'] is None and native['accepted'] is False
            assert digest(r['native_stdout'].encode())==w['native_stdout_sha256']
            assert digest(r['native_stderr'].encode())==w['native_stderr_sha256']
            bounds=None;radii={}
        records[label]={'accepted':r['accepted'],'native_status':native['status'],'rectangle':r.get('rectangle'),
                        'component_radius':{k:str(v) for k,v in radii.items()},'elapsed_wall_ns':w['elapsed_wall_ns'],
                        'dispatched_evaluations':native['dispatched_evaluations'],'integration_calls':native['integration_calls'],
                        'native_callback_calls':native['callback_calls'],'native_callback_refusals':native['callback_refusals'],
                        'flint_status':native['flint_status'],'raw_success_stdout_retrieved':False}
        identities[str(path.relative_to(BASE))]=sha(path);identities[str(receiptpath.relative_to(BASE))]=sha(receiptpath)
    logresult=load(RUNTIME/'LOG2_CENTRAL.json');comparisons={}
    for mode in ['baseline','cached','refined_cached']:
        path=BASE/f'native_execution_20261001_v1/runtime/pilots_{mode}/CENTRAL.json'
        old=load(path);seal_check(old,'result_sha256')
        for key in ['archive_sha256','input_record_sha256','index','plan_sha256','task_sha256','precision_bits','accepted_component_radius_exp']:
            assert old[key]==logresult[key],key
        overlaps={}
        for part in ['real','imag']:
            lo,hi=interval(old['rectangle'][part]);a,b=interval(logresult['rectangle'][part])
            overlaps[part]=max(lo,a)<=min(hi,b);assert overlaps[part]
        comparisons[mode]={'same_target_binding':True,'component_overlap':overlaps,
                           'serialized_rectangle_bit_equal':old['rectangle']==logresult['rectangle']}
        identities[str(path.relative_to(BASE))]=sha(path)
    result={'schema':'WU088_LOG2_ACTUAL_INITIAL_INDEPENDENT_REVIEW_V1','status':'PASS_SCOPED_RECEIPT_AND_ENCLOSURE_REVIEW',
            'review_script_sha256':sha(__file__),'evidence_sha256':identities,'build_source_identity':build['source']['sha256'],
            'build_manifest_sha256':build['manifest_sha256'],'native_binary_sha256':build['binary_sha256'],
            'source_files_checked':len(build['source']['files']),'records':records,'same_central_target_comparisons':comparisons,
            'reviewer_new_integral_runs':0,'reviewed_actual_invocations':2,'reviewed_accepted_invocations':1,
            'scope':'Exact receipt/source/build/plan identity, serialized radius and overlap review; existing executions not repeated.',
            'limitations':['Overlap is consistency evidence, not independently recomputed HH integration.',
                           'Central result covers only [1,2]^2 of one unnormalized primitive.',
                           'W1 remains rejected; its runtime/counters cannot be represented as accepted integration.',
                           'Successful raw stdout was not retained separately; its digest is wrapper provenance, not independently recovered raw bytes.',
                           'Elapsed time is one workspace native process launch/wait measurement, not baseline speedup or NCP benchmark.'],
            'scientific_admission':False,'production_admission':False}
    path=HERE/'ACTUAL_INITIAL_REVIEW.json'
    with path.open('x') as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'review_path':str(path),'sha256':sha(path),'records':records,'overlap':comparisons},sort_keys=True))

if __name__=='__main__':main()
