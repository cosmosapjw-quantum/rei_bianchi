"""Independent finite-result scalar audit. No author audit/science imports.

Reads completed per-task execution records from normal and interrupted/recovery
batch folders. Runtime recovery admission remains a separately reviewed ledger;
this script does not upgrade a partial/failed launcher to a successful launcher.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse, hashlib, json, math, os
ROOT=Path(__file__).resolve().parents[1]
SCIENCE_CODE={'code/task_worker.py','code/prolate_fast.py','code/direct_stream.py','code/force_integral.py','code/overlap_integral.py','code/integration_native.py','code/state_io.py','code/sphere_adapter.py','code/fast_observables.py','code/optimized_solver.py','code/native_backend.py','CONTRACT.json'}
DIRECT=('L_O_bar','L_B_bar','p_x_bar','dipole_x','norm_g','norm_b')
FORCE=('L_O_bar','L_B_bar','T_A','T_B','gap')
OVERLAP=('overlap','normalized_overlap','left_domain_overlap','right_domain_overlap','directional_difference_abs','self_norm_left','self_norm_right','max_self_norm_error_abs')
def load(path):return json.loads(path.read_text())
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def finite(x):assert type(x) in (int,float) and math.isfinite(x);return x
def close(a,b):return abs(a-b)<=64*2**-53*max(1,abs(a),abs(b))
def checked(path,spec):assert path.is_file() and not path.is_symlink() and path.stat().st_size==spec['bytes'] and digest(path)==spec['sha256']
def collect():
    docs=[];seen={};attempts=[];source_checks=[]
    baseline=load(ROOT/'evidence/MAIN3_MPI/RUN_IDENTITY.json')
    pinned={k:v for k,v in baseline['code']['files'].items() if k in SCIENCE_CODE or k.startswith('reference/') or k.startswith('native/')}
    for batch in sorted((ROOT/'evidence').glob('*MPI')):
        if not (batch/'RUN_IDENTITY.json').is_file():continue
        run=load(batch/'RUN_IDENTITY.json');manifest=load(batch/'MANIFEST_INPUT.json')
        assert digest(batch/'MANIFEST_INPUT.json')==run['manifest_sha256']
        for k,v in pinned.items():assert run['code']['files'][k]==v,(batch,k)
        assert run['selected_backend']==baseline['selected_backend']
        source_checks.append({'batch':str(batch.relative_to(ROOT)),'run_identity_sha256':digest(batch/'RUN_IDENTITY.json'),'science_source_pins_equal_MAIN':True,'normal_summary_present':(batch/'BATCH_SUMMARY.json').is_file()})
        expected={x['task_id']:x for x in manifest['tasks']};assert len(expected)==len(manifest['tasks'])
        for ep in sorted(batch.glob('*/TASK_EXECUTION.json')):
            e=load(ep);folder=ep.parent;tid=e['task_id'];assert tid==folder.name and tid in expected
            attempts.append({'folder':str(folder.relative_to(ROOT)),'status':e['status'],'task_id':tid,'kind':expected[tid]['parameters']['kind']})
            if e['status']!='WORKER_RESULT_PASS':continue
            assert e['returncode']==0 and e['code_sha256']==run['code']['sha256']
            assert e['selected_backend']==run['selected_backend']
            for filename,spec in e['artifacts'].items():checked(folder/filename,spec)
            task=load(folder/'TASK_INPUT.json');result=load(folder/'RESULT.json');data=load(folder/'DATA.json')
            assert task==expected[tid] and result['task_id']==data['task_id']==tid
            assert digest(folder/'TASK_INPUT.json')==result['input_sha256']==e['task_sha256']
            assert result['status']=='PASS' and result['parameters']==data['parameters']==task['parameters']
            assert digest(folder/'RESULT.json')==e['worker_result_sha256']
            assert result['evidence_file']=='DATA.json' and digest(folder/'DATA.json')==result['evidence_sha256']
            assert (folder/'DATA.json').stat().st_size==result['evidence_bytes']
            assert result['code_identity_sha256']==run['code']['sha256'] and result['selected_backend']==run['selected_backend']
            assert result['new_eigenstates']==data['new_eigenstates']
            if 'state_sha256' in result:
                assert result['state_file']=='STATE.npz';checked(folder/'STATE.npz',{'sha256':result['state_sha256'],'bytes':result['state_bytes']})
            semantic=canonical(task['parameters']);assert semantic not in seen,('DUPLICATE_COMPLETED_SEMANTIC_TASK',seen.get(semantic),str(folder))
            seen[semantic]=str(folder)
            docs.append({'data':data,'result':result,'folder':str(folder.relative_to(ROOT)),'result_sha256':digest(folder/'RESULT.json'),'data_sha256':digest(folder/'DATA.json'),'execution_sha256':digest(ep)})
    return docs,attempts,source_checks

def reference(doc):return {'folder':doc['folder'],'result_sha256':doc['result_sha256'],'state_sha256':doc['result']['state_sha256']}
def overlap_numbers(v):
    values={k:finite(v[k]) for k in OVERLAP};left=values['left_domain_overlap'];right=values['right_domain_overlap'];nl=values['self_norm_left'];nr=values['self_norm_right']
    assert min(nl,nr)>0
    mean=(left+right)/2;normal=mean/math.sqrt(nl*nr);direction=abs(left-right);norm=max(abs(nl-1),abs(nr-1))
    for key,want in [('overlap',mean),('normalized_overlap',normal),('directional_difference_abs',direction),('max_self_norm_error_abs',norm)]:assert close(values[key],want),(key,values[key],want)
    assert v['phase_factor_suggestion']==(1 if mean>=0 else -1)
    return {'left':left,'right':right,'normalized':normal,'direction':direction,'norm':norm,'phase':1 if mean>=0 else -1}

def evaluate():
    c=load(ROOT/'CONTRACT.json');docs,attempts,sources=collect();selected={};failures=[]
    checks=[]
    def check(name,value,limit):
        finite(value);ok=value<=limit;checks.append({'name':name,'value':value,'limit':limit,'pass':ok})
        if not ok:failures.append(name)
    for doc in docs:
        p=doc['data']['parameters']
        if p['kind']=='bridge' or p['kind']=='prolate' and p['tier']==0 and p['profile']=='base':
            R=p['R'];assert R not in selected;selected[R]=reference(doc)
    frozen=ROOT/'frozen/R16_base';parent=load(ROOT/'provenance/PARENT_INPUTS.json')
    for name in ('RESULT.json','STATE.npz','TASK_INPUT.json'):checked(frozen/name,parent[str((frozen/name).relative_to(ROOT))])
    old=load(frozen/'RESULT.json');selected[16]={'folder':'frozen/R16_base','result_sha256':digest(frozen/'RESULT.json'),'state_sha256':old['state_sha256']}
    assert set(selected)==set(c['continuation']['grid'])
    expected={(a,b,m) for a,b in c['continuation']['edges'] for m in c['continuation']['sectors']};groups={x:{} for x in expected}
    native={};completed_refs={}
    for doc in docs:
        p=doc['data']['parameters'];v=doc['data']['value']
        if p['kind']!='overlap':continue
        group=(v['R_left'],v['R_right'],v['m']);q=v['order'];assert group in expected
        assert q==p['order'] and v['m']==p['sector']
        assert p['left']==selected[v['R_left']] and p['right']==selected[v['R_right']]
        assert q in c['continuation']['orders']+c['continuation']['fallback_orders'] and q not in groups[group]
        groups[group][q]=overlap_numbers(v);native[(group,q)]=v
        completed_refs[doc['folder']]={'execution_sha256':doc['execution_sha256'],'result_sha256':doc['result_sha256'],'data_sha256':doc['data_sha256']}
    edge_rows=[];phase={0:1,1:1};chain={0:[{'R':16,'phase':1}],1:[{'R':16,'phase':1}]}
    for left,right,m in sorted(expected):
        allorders=sorted(groups[(left,right,m)]);initial=c['continuation']['orders'];extra=c['continuation']['fallback_orders']
        assert allorders in (initial,initial+extra),((left,right,m),allorders)
        seq=[groups[(left,right,m)][q] for q in allorders[-3:]]
        delta=[max(abs(b[k]-a[k]) for k in ('left','right','normalized')) for a,b in zip(seq,seq[1:])]
        prefix=f'{left}_{right}_m{m}'
        for i,x in enumerate(delta):check(prefix+f'.increment{i+1}',x,c['continuation']['tolerance'])
        direction=max(x['direction'] for x in seq);norm=max(x['norm'] for x in seq);mag=abs(seq[-1]['normalized'])
        check(prefix+'.direction',direction,c['continuation']['tolerance']);check(prefix+'.selfnorm',norm,c['continuation']['tolerance'])
        check(prefix+'.minimum_overlap_shortfall',max(0,c['continuation']['minimum_overlap']-mag),0)
        check(prefix+'.cauchy_schwarz_excess',max(0,mag-1),c['continuation']['tolerance'])
        phase[m]*=seq[-1]['phase'];chain[m].append({'R':right,'phase':phase[m]})
        edge_rows.append({'edge':[left,right],'m':m,'orders':allorders,'signed_normalized_overlap':seq[-1]['normalized'],'increments':delta,'max_direction':direction,'max_selfnorm':norm,'cumulative_phase':phase[m]})
    cases={}
    for doc in docs:
        p=doc['data']['parameters'];v=doc['data']['value']
        if p['kind']!='parity':continue
        index=p['index'];assert type(index)is int and index in range(4) and index not in cases
        case=c['parity_cases'][index];assert p['case']==case
        if case['kind']=='overlap':
            assert p['left']==selected[case['edge'][0]] and p['right']==selected[case['edge'][1]]
            assert (v['R_left'],v['R_right'],v['m'],v['order'])==(*case['edge'],case['sector'],case['order'])
            overlap_numbers(v);ref=native[((case['edge'][0],case['edge'][1],case['sector']),case['order'])];keys=OVERLAP
        else:
            assert p['state']==selected[case['R']]
            if case['R']==16:ref=old['operators']['direct'][str(case['order'])]
            else:
                sd=[d for d in docs if 'state_sha256'in d['result'] and reference(d)==p['state']];assert len(sd)==1
                ref=sd[0]['data']['value'][case['kind']][str(case['order'])]
            keys=DIRECT if case['kind']=='direct' else FORCE
        deltas={k:abs(finite(v[k])-finite(ref[k])) for k in keys}
        check(f'parity{index}.raw',max(deltas.values()),c['raw_criteria']['native_reference_operator_abs'])
        row={'case_index':index,'case':case,'deltas':deltas,'raw_max':max(deltas.values())}
        if case['kind']!='overlap':
            row['Q_O_delta']=deltas['L_O_bar']/case['R'];row['Q_B_delta']=deltas['L_B_bar']*case['R']**2
            check(f'parity{index}.Q_O',row['Q_O_delta'],c['scaled_criteria']['Q_O_native_parity_abs']);check(f'parity{index}.Q_B',row['Q_B_delta'],c['scaled_criteria']['Q_B_native_parity_abs'])
        else:assert v['phase_factor_suggestion']==ref['phase_factor_suggestion']
        cases[index]=row;completed_refs[doc['folder']]={'execution_sha256':doc['execution_sha256'],'result_sha256':doc['result_sha256'],'data_sha256':doc['data_sha256']}
    assert set(cases)==set(range(4))
    return {'schema':'bass-he-c2d-independent-followup-recalculation-v1','pass':not failures,'failures':failures,'contract_sha256':digest(ROOT/'CONTRACT.json'),'edge_sector_count':len(edge_rows),'overlap_completed_evaluations':sum(len(x) for x in groups.values()),'minimum_absolute_normalized_overlap':min(abs(x['signed_normalized_overlap']) for x in edge_rows),'maximum_increment':max(v for x in edge_rows for v in x['increments']),'maximum_directional_difference':max(x['max_direction'] for x in edge_rows),'maximum_selfnorm_error':max(x['max_selfnorm'] for x in edge_rows),'phase_chains':chain,'edge_rows':edge_rows,'parity_rows':[cases[i] for i in range(4)],'checks':checks,'completed_result_identities':completed_refs,'batch_source_checks':sources,'observed_per_task_execution_attempts':attempts,'new_physical_evaluations':0,'scope':'Independent scalar recomputation over completed identity-verified task artifacts; runtime partial/recovery admission and wall/attempt ledger must pass separate review.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output');a=p.parse_args();v=evaluate()
    with (ROOT/a.output).open('x') as f:json.dump(v,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v[k] for k in ('pass','failures','edge_sector_count','overlap_completed_evaluations','minimum_absolute_normalized_overlap','maximum_increment','maximum_directional_difference','maximum_selfnorm_error','parity_rows')},indent=2))
