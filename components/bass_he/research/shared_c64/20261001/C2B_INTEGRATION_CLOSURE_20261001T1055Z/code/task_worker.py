"""One pinned frozen-state integration task; no eigensolver is invoked."""
import argparse,hashlib,json,resource,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for d in ('reference','code'):sys.path.insert(0,str(ROOT/d))
from mpi_batch import atomic_create,json_bytes,code_identity,backend_identity

def frozen_pair(name,index):
    if not isinstance(name,str) or Path(name).name!=name or name not in {p.split('/')[0] for p in index}:raise ValueError('unknown frozen state')
    for fn in ('STATE.npz','RESULT.json','TASK_INPUT.json'):
        rel=name+'/'+fn;p=ROOT/'frozen'/rel;record=index[rel]
        if p.is_symlink() or p.stat().st_size!=record['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=record['sha256']:raise RuntimeError('FROZEN_INPUT_IDENTITY_MISMATCH')
    meta=json.loads((ROOT/'frozen'/name/'RESULT.json').read_bytes());record=index[name+'/STATE.npz']
    if meta['state_sha256']!=record['sha256'] or meta['state_bytes']!=record['bytes'] or meta['status']!='PASS':raise RuntimeError('PARENT_STATE_RESULT_MISMATCH')
    from state_io import load_pair
    return load_pair(ROOT/'frozen'/name/'STATE.npz'),meta,record

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--task-json',type=Path,required=True);ap.add_argument('--output-dir',type=Path,required=True);ap.add_argument('--backend',choices=('native','reference'),required=True);args=ap.parse_args()
    raw=args.task_json.read_bytes();task=json.loads(raw);p=task['parameters']
    if set(p)!={'kind','states','order','method','sector'} or not isinstance(p['states'],list):raise ValueError('invalid integration parameters')
    if type(p['order'])is not int or p['order']<2 or type(p['sector'])is not int or p['sector']not in (0,1):raise ValueError('invalid order/sector')
    index=json.loads((ROOT/'inputs/FROZEN_IDENTITY.json').read_bytes());identity=code_identity();native=backend_identity(args.backend)
    started=time.perf_counter();pairs=[];metas=[];inputs={}
    for name in p['states']:
        pair,meta,pin=frozen_pair(name,index);pairs.append(pair);metas.append(meta);inputs[name]=pin
    backend='native' if args.backend=='native' and not p['method'].endswith('_python') else 'python'
    from force_integral import torque
    from overlap_integral import pair_overlap
    if p['kind']=='force':
        if len(pairs)!=1 or p['method']not in ('balanced','original','balanced_python'):raise ValueError('invalid force task')
        value=torque(*pairs[0],p['order'],backend=backend,variant=p['method'].replace('_python',''))
        direct=metas[0]['operators']['direct']['24'];value['direct_force_O_abs']=abs(value['L_O_bar']-direct['L_O_bar']);value['direct_force_B_abs']=abs(value['L_B_bar']-direct['L_B_bar'])
    elif p['kind']=='overlap':
        if len(pairs)!=2 or p['method']not in ('resolved','original','resolved_python'):raise ValueError('invalid overlap task')
        left,right=pairs[0][p['sector']],pairs[1][p['sector']]
        if p['method']=='original':
            from continuation_original import pair_overlap as original
            value=original(left,right,p['order'])
        else:value=pair_overlap(left,right,p['order'],backend=backend)
    else:raise ValueError('unknown integration kind')
    data={'task_id':task['task_id'],'parameters':p,'value':value,'frozen_state_identities':inputs,'new_eigensolves':0}
    artifact=args.output_dir/'DATA.json';atomic_create(artifact,json_bytes(data))
    elapsed=time.perf_counter()-started
    if code_identity()!=identity or backend_identity(args.backend)!=native:raise RuntimeError('SOURCE_OR_NATIVE_CHANGED_DURING_TASK')
    result={'status':'PASS','task_id':task['task_id'],'input_sha256':hashlib.sha256(raw).hexdigest(),'parameters':p,'backend':args.backend,'selected_backend':native,'code_identity_sha256':identity['sha256'],'evidence_file':artifact.name,'evidence_bytes':artifact.stat().st_size,'evidence_sha256':hashlib.sha256(artifact.read_bytes()).hexdigest(),'elapsed_seconds':elapsed,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'new_eigensolves':0,'claim_scope':'execution PASS only; scientific gates separately evaluated'}
    atomic_create(args.output_dir/'RESULT.json',json_bytes(result));print(json.dumps({'task_id':task['task_id'],'seconds':elapsed,'max_rss_kib':result['max_rss_kib']}),flush=True)
if __name__=='__main__':main()
