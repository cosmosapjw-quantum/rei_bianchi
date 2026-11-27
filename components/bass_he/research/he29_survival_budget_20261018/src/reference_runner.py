"""Complete HE29 reference-only NCP lane; no transport reruns or physics edits.

Exactly four model/table pairs are allowed. New adaptive references are NOT_RUN
until the user-authorized host executes this file. Six saved-point comparisons
qualify rebuilt binaries only at those points, not global implementation parity.
"""
from __future__ import annotations
import argparse
from dataclasses import asdict
import json,math,os,platform,sys,time,traceback
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
sys.path.insert(0,str(ROOT.parent/'he28_strip_refinement_20261018/src'))
from execution import atomic_json,digest,manifest,verify_manifest,run_process
from refined_source import GridSpec,RefinedSourceModel
from native import NativeOwner,SOURCE_COMMIT,_FIELDS
from reference import solve_reference
from reference_contract import OWNER,JOBS,THREADS,check_result,admit_pair,same_model
import numpy as np
import scipy


def validate_job(r,nodes):
    if type(r) is not int or type(nodes) is not int or (r,nodes) not in JOBS:
        raise ValueError('HE29_UNDECLARED_REFERENCE_JOB')


def response_error(got,expected):
    if len(got)!=len(expected) or not got:raise ValueError('HE29_SAVED_POINT_WIDTH')
    worst=0.
    for a,b in zip(got,expected):
        if not (math.isfinite(a) and math.isfinite(b)):raise ValueError('HE29_SAVED_POINT_NONFINITE')
        if b==0:
            if a!=0:raise ValueError('HE29_SAVED_STRUCTURAL_ZERO')
        else:worst=max(worst,abs(a-b)/abs(b))
    if worst>5e-13:raise ValueError('HE29_SAVED_POINT_PARITY')
    return worst


def qualify_owner(owner,input_root):
    d=json.loads((Path(input_root)/'SAVED_NATIVE_POINTS.json').read_text())
    if d['owner_source']!=SOURCE_COMMIT or len(d['points'])!=6:
        raise ValueError('HE29_SAVED_POINT_IDENTITY')
    handshake=d['handshake'].split('\t')
    response_error([owner.n_h0,owner.n_he0],list(map(float,handshake[2:])))
    errors=[]
    for item in d['points']:
        x=list(map(float,item['request'].split('\t')))
        if len(x)!=11:raise ValueError('HE29_SAVED_REQUEST_SCHEMA')
        expected=list(map(float,item['response'].split('\t')[1:]))
        got=owner.point(x[0],x[1:5],x[5:8],x[8:11])
        flat=[]
        for key in _FIELDS:flat.extend(np.asarray(got[key],dtype=float).reshape(-1).tolist())
        errors.append(response_error(flat,expected))
    return {'scope':'six_saved_native_points_only','points':6,'max_relative_nonzero_error':max(errors),
      'binary_byte_identity':owner.binary_sha256==d['original_binary_sha256'],
      'original_binary_sha256':d['original_binary_sha256'],'upstream_grackle_equivalence':'HOLD'}


def check_sources(binary=None,receipt=None):
    parents=json.loads((ROOT/'provenance/PARENT_SHA256.json').read_text())
    inputs=json.loads((ROOT/'provenance/INPUT_SHA256.json').read_text())
    verify_manifest(parents,REPO);verify_manifest(inputs,ROOT)
    state={'owner_source':OWNER,'parent_sources':parents,'input_sources':inputs,
      'source_files':manifest(sorted((ROOT/'src').glob('*.py')),ROOT),
      'numerical_thread_environment':dict(THREADS),
      'runtime':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'platform':platform.platform()}}
    if binary is not None:
        d=json.loads(Path(receipt).read_text())
        server='research/he25_proper_birth_20261016/src/owner_server.rs'
        if (d.get('owner_source')!=OWNER or d.get('binary_sha256')!=digest(binary)
            or d.get('server_source_sha256')!=parents[server]):
            raise ValueError('HE29_NATIVE_BUILD_IDENTITY')
        state.update(binary_sha256=digest(binary),build_receipt=d)
    return state


def parent_comparisons(input_root,r,nodes,table_hash,ref):
    validate_job(r,nodes)
    if nodes!=512:return []  # different table is a distinct finite model
    out=[]
    for n in (32,64):
        folder=Path(input_root)/f'study/m8_r{r}_n{n}'
        d=json.loads((folder/'RESULT.json').read_text());i=json.loads((folder/'IDENTITY.json').read_text())
        t=json.loads((folder/'TABLE.json').read_text())
        if d['status']!='SCOPED_NATIVE_COMPLETED' or d['source_table_sha256']!=t['source_table_sha256']:
            raise ValueError('HE29_PARENT_TABLE_RECORD')
        original={**i['spec'],'source_table_nodes':i['source_table_nodes'],'table':d['source_table_sha256']}
        same_model(original,dict(m=8,strips=r,q=0.,angles=4,source_table_nodes=nodes,table=table_hash))
        if i['owner_source']!=OWNER or i['numerical_thread_environment']!=THREADS:
            raise ValueError('HE29_PARENT_PHYSICS_ENVIRONMENT')
        old=d['results']['transport'];check_result(old)
        out.append({'transport_n':n,'temperature_error_K':abs(old['temperature_K']-ref['temperature_K']),
          'absolute_fraction_difference':max(abs(a-b) for a,b in zip(old['gas_final'][:3],ref['gas_final'][:3])),
          'original_result_sha256':digest(folder/'RESULT.json'),
          'interpretation':'empirical same-table comparison, not certified continuum error'})
    return out


def run_case(args):
    validate_job(args.strips,args.table_nodes)
    out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic()
    try:
        state=check_sources(args.binary,args.receipt)
        state.update(m=8,r=args.strips,q=0.,angles=4,table_nodes=args.table_nodes)
        if any(os.environ.get(k)!=v for k,v in THREADS.items()):
            raise ValueError('HE29_SINGLE_THREAD_ENV_REQUIRED')
        atomic_json(out/'IDENTITY.json',state)
        with NativeOwner(args.binary,evidence_path=out/'native.jsonl.gz',
                         expected_binary_sha256=state['binary_sha256']) as owner:
            point_check=qualify_owner(owner,ROOT/'inputs')
            atomic_json(out/'SAVED_POINT_PARITY.json',point_check)
            model=RefinedSourceModel(owner,GridSpec(m=8,angles=4,q=0.,strips=args.strips),
                    tabulate=True,source_table_nodes=args.table_nodes,max_table_bytes=2*1024**3,max_table_wall_s=600.)
            atomic_json(out/'TABLE.json',{'source_table_sha256':model.source_table_sha256,
                         'diagnostics':model.source_table_diagnostics})
            # Reject a mismatched table before expensive adaptive integrations.
            if args.table_nodes==512:
                folder=ROOT/'inputs'/f'study/m8_r{args.strips}_n64'
                old=json.loads((folder/'RESULT.json').read_text())
                if old['source_table_sha256']!=model.source_table_sha256:
                    raise ValueError('HE29_REBUILT_TABLE_DIFFERS_FROM_PARENT')
            outputs={};counts={}
            for method in ('Radau','DOP853'):
                before=owner.calls;timer=time.monotonic()
                r=solve_reference(model,rtol=1e-10,atol=1e-12,method=method)
                check_result(r);outputs[method]=r;counts[method]=owner.calls-before
                atomic_json(out/(method+'.json'),{'result':r,'native_calls':counts[method],'wall_s':time.monotonic()-timer})
            admission=admit_pair(outputs['Radau'],outputs['DOP853'])
            comparisons=parent_comparisons(ROOT/'inputs',args.strips,args.table_nodes,model.source_table_sha256,outputs['Radau'])
            calls=owner.calls
        atomic_json(out/'RESULT.json',{'status':'REFERENCE_COMPLETED_SCOPED','results':outputs,
             'comparison':admission,'comparisons':comparisons,'table_sha256':model.source_table_sha256,
             'point_qualification':point_check,'native_calls':calls,'method_calls':counts,
             'wall_s':time.monotonic()-start,'continuum_convergence':'HOLD','transport_replays':0})
    except BaseException as exc:
        atomic_json(out/'FAILURE.json',{'status':'HOLD_FIRST_FAILURE','error':repr(exc),
          'traceback':traceback.format_exc(),'wall_s':time.monotonic()-start})
        raise


def run_campaign(args):
    out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    check_sources(args.binary,args.receipt)
    atomic_json(out/'DESIGN.json',{'jobs':JOBS,'integration_rtol':1e-10,'integration_atol_scaled':1e-12,
       'per_case_wall_s':args.case_wall_s,'concurrency':1,'stop_on_first_failure':True,
       'reason':'same-r/same-table error separation; no repeats of completed transport'})
    rows=[]
    for r,nodes in JOBS:
        name=f'm8_r{r}_table{nodes}'
        argv=[sys.executable,str(Path(__file__).resolve()),'case','--out',str(out/name),
              '--binary',str(Path(args.binary).resolve()),'--receipt',str(Path(args.receipt).resolve()),
              '--strips',str(r),'--table-nodes',str(nodes)]
        info=run_process(argv,out/(name+'_process'),args.case_wall_s)
        rows.append(dict(case=name,**info))
        if info['returncode']!=0 or info['timed_out']:break
    summary={'completed':sum(x['returncode']==0 and not x['timed_out'] for x in rows),'started':len(rows),
          'requested':4,'records':rows,'transport_replays':0,'continuous_spectral_convergence':'HOLD'}
    atomic_json(out/'SUMMARY.json',summary)
    print(json.dumps(summary,indent=2))
    if summary['completed']!=4:raise SystemExit(1)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['preflight','case','campaign'])
    ap.add_argument('--out',required=True);ap.add_argument('--binary');ap.add_argument('--receipt')
    ap.add_argument('--strips',type=int,default=2);ap.add_argument('--table-nodes',type=int,default=512)
    ap.add_argument('--case-wall-s',type=float,default=3600.)
    args=ap.parse_args()
    if not math.isfinite(args.case_wall_s) or not 0<args.case_wall_s<=3600:
        ap.error('case wall budget must be finite, positive and <=3600s')
    if args.mode=='preflight':
        out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
        atomic_json(out/'PREFLIGHT.json',check_sources())
    else:
        if not args.binary or not args.receipt:ap.error('binary and receipt required')
        if args.mode=='case':run_case(args)
        else:run_campaign(args)
if __name__=='__main__':main()
