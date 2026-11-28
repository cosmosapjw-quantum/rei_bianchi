"""Scalar-only collection of immutable C2c results; never invokes a solver."""
import argparse,copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'code'))
from mpi_batch import atomic_create,json_bytes
from scaled_audit import quartet_audit

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def documents():
    docs=[]
    for folder in sorted((ROOT/'evidence').glob('*MPI')):
        summary=folder/'BATCH_SUMMARY.json'
        if not summary.exists():continue
        batch=json.loads(summary.read_bytes())
        for execution in batch['tasks']:
            if execution['status']!='WORKER_RESULT_PASS':continue
            taskdir=folder/execution['task_id'];result=taskdir/'RESULT.json'
            if digest(result)!=execution['artifacts']['RESULT.json']['sha256']:raise RuntimeError('RESULT_IDENTITY_MISMATCH')
            r=json.loads(result.read_bytes());path=taskdir/r['evidence_file']
            if path.stat().st_size!=r['evidence_bytes'] or digest(path)!=r['evidence_sha256']:raise RuntimeError('DATA_IDENTITY_MISMATCH')
            d=json.loads(path.read_bytes());d['path']=str(path.relative_to(ROOT));d['folder']=str(taskdir.relative_to(ROOT));d['result']=r;docs.append(d)
    return docs

def state_ref(doc):
    folder=ROOT/doc['folder'];r=doc['result']
    return {'folder':doc['folder'],'state_sha256':r['state_sha256'],'result_sha256':digest(folder/'RESULT.json')}

def audit_states(docs,contract):
    rows=[];selected={};needs=[]
    for R in contract['new_R']:
        tiers=[]
        for tier in (0,1):
            found=[d for d in docs if d['parameters']['kind']=='prolate' and d['parameters']['R']==R and d['parameters']['tier']==tier]
            if not found:continue
            if len(found)!=4:tiers.append({'tier':tier,'pass':False,'reason':'INCOMPLETE_QUARTET','available':[d['parameters']['profile'] for d in found]});continue
            vals={};refs={}
            for d in found:
                name=d['parameters']['profile'];v=copy.deepcopy(d['value']);ref=state_ref(d)
                for extra in docs:
                    if extra['parameters']['kind']=='operator_refinement' and extra['parameters']['state']==ref:
                        for lane in ('direct','force'):v[lane].update(extra['value'][lane])
                vals[name]=v;refs[name]=ref
            audit=quartet_audit(vals,contract);tiers.append({'tier':tier,'audit':audit,'pass':audit['pass'],'states':refs})
        passing=[x for x in tiers if x['pass']]
        chosen=passing[-1] if passing else None
        if chosen:selected[str(R)]=chosen['states']['base']
        rows.append({'R':R,'tiers':tiers,'pass':chosen is not None,'selected_tier':None if chosen is None else chosen['tier']})
        if not passing:needs.append(R)
    return {'rows':rows,'all_new_R_numerical_gates_pass':all(x['pass'] for x in rows),'selected_states':selected,'unresolved_R':needs}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    c=json.loads((ROOT/'CONTRACT.json').read_bytes());docs=documents();out=audit_states(docs,c)
    out.update({'contract_sha256':digest(ROOT/'CONTRACT.json'),'input_data_sha256':{d['path']:digest(ROOT/d['path']) for d in docs},'new_eigensolves_performed_by_analysis':0,'full_C2_closed':False})
    atomic_create(args.output,json_bytes(out));print(json.dumps({'all_new_R_numerical_gates_pass':out['all_new_R_numerical_gates_pass'],'unresolved_R':out['unresolved_R'],'rows':out['rows']},indent=2))

if __name__=='__main__':main()
