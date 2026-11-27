"""Exact-campaign terminal claim quarantine; no native execution or numerical edits."""
from __future__ import annotations
import argparse
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat

HERE=Path(__file__).resolve().parent
NEW=HERE.parent
CAMPAIGN=NEW/'runtime/W1_CAMPAIGN'
OBSERVATION=NEW/'runtime/RESIDUAL_CLAIMS_OBSERVED.json'
QUARANTINE=NEW/'runtime/W1_CLAIMS_QUARANTINE_20261002_v1'
RUNNER_SHA='37f2b99abb6d2f6951243c88feccfb16225cc109eb70748221c905a8c8d9fe29'
OBSERVATION_SHA='8cb35493fab8f3d228b792dbdae97f8d7204d06ff83705da496844b5bcaad3e3'
PREPARED_SHA='e85c2fa451d00a32f7d129d55e82f45ffee71342af0fd39d1b9ac81b4d84a4a9'
SESSION_FILE_SHA='ea905e595d1ed1623bf981a4af807740fb322faf34e43e58c167b61cb351f4e7'
SESSION_SHA='aafdbe4ae61da1f4a961111df391a6b19e7d120ad307c9a27eb5096016eb71d8'
TILES=(2,4,5,6,7,15)
MAX_BYTES=16*1024*1024

class ReconciliationError(ValueError):pass

def sha(data):return hashlib.sha256(data).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def seal(value,key):return {**value,key:sha(canonical(value))}
def source_sha():return sha(Path(__file__).read_bytes())
def regular(path):
    path=Path(path)
    if not stat.S_ISREG(path.lstat().st_mode) or path.stat().st_size>MAX_BYTES:raise ReconciliationError('bounded nonsymlink regular file required')
    data=path.read_bytes()
    if len(data)>MAX_BYTES:raise ReconciliationError('file grew past cap')
    return data

def runner():
    path=HERE/'runner.py'
    if sha(regular(path))!=RUNNER_SHA:raise ReconciliationError('frozen runner changed')
    spec=importlib.util.spec_from_file_location('wu088_claim_reconcile_runner',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def claim_entries(observation,base=NEW,quarantine=QUARANTINE):
    claims=observation.get('claims')
    if type(claims) is not list or len(claims)!=len(TILES):raise ReconciliationError('exact six observed claims required')
    result=[]
    for tile,entry in zip(TILES,claims):
        expected='runtime/W1_CAMPAIGN/raw/%02d.json.claim'%tile
        if entry.get('path')!=expected or type(entry.get('data')) is not str or not entry['data'].isdigit():
            raise ReconciliationError('observed claim path/data mismatch')
        payload=entry['data'].encode('ascii')
        if sha(payload)!=entry.get('sha256'):raise ReconciliationError('observed claim digest mismatch')
        path=base/expected
        actual=regular(path)
        if actual!=payload or sha(actual)!=entry['sha256']:raise ReconciliationError('claim bytes differ from observed evidence')
        if path.stat().st_mtime_ns!=entry['mtime_ns']:raise ReconciliationError('claim mtime changed after observation')
        result.append({'tile_id':tile,'source':str(path),'destination':str(quarantine/path.name),'sha256':sha(actual),
                       'size':len(actual),'mtime_ns':path.stat().st_mtime_ns,'data':entry['data']})
    found=sorted(p.name for p in (base/'runtime/W1_CAMPAIGN/raw').glob('*.claim'))
    if found!=['%02d.json.claim'%i for i in TILES]:raise ReconciliationError('unknown, missing or unresolved claim set')
    return result

def snapshot():
    result={}
    for path in sorted(CAMPAIGN.rglob('*')):
        if path.is_symlink():raise ReconciliationError('campaign symlink refused')
        if path.is_file() and not path.name.endswith('.claim'):
            result[str(path.relative_to(CAMPAIGN))]={'sha256':sha(regular(path)),'size':path.stat().st_size}
    return result

def verified_plan(*,owned_lock=None):
    lock=CAMPAIGN/'RUN.claim'
    if os.path.lexists(lock):
        if owned_lock is None or regular(lock)!=owned_lock:raise ReconciliationError('live or unresolved campaign RUN.claim')
    elif owned_lock is not None:raise ReconciliationError('reconciliation ownership lost')
    r=runner()
    observation_raw=regular(OBSERVATION)
    if sha(observation_raw)!=OBSERVATION_SHA:raise ReconciliationError('observation artifact changed')
    observation=r.context()['d'].parse_json(observation_raw)
    entries=claim_entries(observation)
    permitted_claims={Path(entry['source']) for entry in entries}
    if owned_lock is not None:permitted_claims.add(lock)
    if set(CAMPAIGN.rglob('*.claim'))!=permitted_claims:raise ReconciliationError('unknown or unresolved claim outside observed set')
    ctx,m,plans=r.load_prepared(CAMPAIGN,PREPARED_SHA);d=ctx['d']
    raw_session=regular(CAMPAIGN/'sessions/000/RESULT.json')
    if sha(raw_session)!=SESSION_FILE_SHA:raise ReconciliationError('pinned completed session bytes changed')
    session=d.parse_json(raw_session);r.selfhash(d,session,'result_sha256',SESSION_SHA)
    if session['status']!='COMPLETE_COMPACT_INTERIOR_RADIUS_MET' or session['prepared_sha256']!=PREPARED_SHA or session['new_dispatched_tiles']!=list(range(1,16)) or session['new_dispatch_count']!=15 or session['accepted_tile_ids']!=list(range(16)) or session['total_native_dispatch_count']!=15 or session['error'] is not None:
        raise ReconciliationError('campaign terminal completion mismatch')
    norm0=r.normalize(ctx,m['grid'],plans[0],0,r.read(r.IMPORTED),origin='imported',receipt_path=r.IMPORTED)
    imported=r.sealed({'schema':'WU088_REUSED_RANGE_TILE_V1','prepared_sha256':PREPARED_SHA,**m['imported_tile'],
        'normalized_record_sha256':norm0['record_sha256']},'import_sha256')
    if d.parse_json(regular(CAMPAIGN/'IMPORTED_TILE00.json'))!=imported or d.parse_json(regular(CAMPAIGN/'normalized/00.json'))!=norm0:
        raise ReconciliationError('imported tile zero changed')
    records=[norm0];returns=[];evidence=[]
    for i in range(1,16):
        ap=CAMPAIGN/'attempts'/('%02d'%i);rp=CAMPAIGN/'raw'/('%02d.json'%i)
        dispatch=d.parse_json(regular(ap/'DISPATCH.json'));r.selfhash(d,dispatch,'dispatch_sha256')
        expected=r.sealed({'schema':'WU088_W1_TILE_DISPATCH_V1','tile_id':i,'prepared_sha256':PREPARED_SHA,
            'validator_source_sha256':RUNNER_SHA,'plan_sha256':plans[i]['plan_sha256'],'native_cap_charged':200000,
            'native_execution_requested':True},'dispatch_sha256')
        if dispatch!=expected:raise ReconciliationError('dispatch identity changed')
        ret=d.parse_json(regular(ap/'RETURN.json'));r.selfhash(d,ret,'return_sha256')
        if ret['tile_id']!=i or ret['dispatch_sha256']!=dispatch['dispatch_sha256'] or ret['status']!='ACCEPTED' or ret['worker_returncode']!=0 or ret['timed_out'] is not False or ret['error'] is not None:
            raise ReconciliationError('terminal worker return mismatch')
        payload=regular(rp);native=d.parse_json(payload)
        norm=r.normalize(ctx,m['grid'],plans[i],i,payload,receipt_path=rp)
        if ret['raw_receipt_sha256']!=sha(payload) or ret['normalized_record_sha256']!=norm['record_sha256'] or d.parse_json(regular(CAMPAIGN/'normalized'/('%02d.json'%i)))!=norm:
            raise ReconciliationError('raw/normalized/return binding mismatch')
        host=native['wrapper']['process_host']
        if host['native_wait_completed'] is not True or host['timed_out'] is not False or host['native_execution_evidence']!='SOURCE_BOUND_NATIVE_STDOUT':
            raise ReconciliationError('native terminal completion missing')
        worker_out=regular(ap/'worker.stdout');worker_err=regular(ap/'worker.stderr')
        if d.parse_json(worker_out)!={'status':'NATIVE_RECEIPT_WRITTEN','tile_id':i} or worker_err!=b'':
            raise ReconciliationError('worker terminal stream mismatch')
        if i in TILES:
            observed=observation['claims'][TILES.index(i)]
            if observed['return']!=ret or observed['host']!=host or observed['worker_stdout'].encode()!=worker_out or observed['worker_stderr'].encode()!=worker_err:
                raise ReconciliationError('observed terminal evidence differs from current evidence')
        records.append(norm);returns.append(ret)
        evidence.append({'tile_id':i,'return_sha256':ret['return_sha256'],'raw_receipt_sha256':sha(payload),
            'normalized_record_sha256':norm['record_sha256'],'worker_returncode':0,'native_wait_completed':True})
    if sorted(session['tile_returns'],key=lambda v:v['tile_id'])!=returns:raise ReconciliationError('session and individual terminal returns differ')
    collected=ctx['c'].collect(m['grid'],records)
    if d.parse_json(regular(CAMPAIGN/'COLLECTED.json'))!=collected or session['collection_sha256']!=collected['result_sha256']:
        raise ReconciliationError('exact final collection mismatch')
    return seal({'schema':'WU088_EXACT_COMPLETED_CLAIM_QUARANTINE_PLAN_V1','reconciler_source_sha256':source_sha(),
        'runner_source_sha256':RUNNER_SHA,'observation_file_sha256':OBSERVATION_SHA,'prepared_sha256':PREPARED_SHA,
        'session_result_sha256':SESSION_SHA,'collection_sha256':collected['result_sha256'],'quarantine':str(QUARANTINE),
        'claims':entries,'terminal_evidence':evidence,'immutable_campaign_snapshot':snapshot(),
        'actual_native_executions':0,'claim_bytes_preserved':True,'numerical_files_modified':False,
        'root_cause':'UNDETERMINED','root_cause_closed':False,'scope':'B22_EXACT_TERMINAL_CLAIMS_ONLY'},'plan_sha256')

def atomic_archive(source,destination):
    """Linux same-filesystem atomic rename with no replacement of any destination."""
    source=Path(source);destination=Path(destination)
    if source.parent.stat().st_dev!=destination.parent.stat().st_dev:raise ReconciliationError('same filesystem required')
    libc=ctypes.CDLL(None,use_errno=True)
    rename=libc.renameat2;rename.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint];rename.restype=ctypes.c_int
    if rename(-100,os.fsencode(source),-100,os.fsencode(destination),1)!=0:
        err=ctypes.get_errno();raise OSError(err,os.strerror(err),str(source))
    for parent in (source.parent,destination.parent):
        fd=os.open(parent,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(fd)
        finally:os.close(fd)

def apply(plan_path,expected_sha):
    r=runner();provided=r.context()['d'].parse_json(regular(plan_path));r.selfhash(r.context()['d'],provided,'plan_sha256',expected_sha)
    if provided!=verified_plan():raise ReconciliationError('reviewed plan no longer matches exact terminal evidence')
    if os.path.lexists(QUARANTINE):raise ReconciliationError('quarantine exists; partial or completed reconciliation requires inspection')
    lock=CAMPAIGN/'RUN.claim';owned=('CLAIM_RECONCILIATION:'+source_sha()).encode()
    fd=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        os.write(fd,owned);os.fsync(fd)
        if provided!=verified_plan(owned_lock=owned):raise ReconciliationError('campaign changed under ownership')
        QUARANTINE.mkdir(exist_ok=False);r.write_new(QUARANTINE/'PLAN.json',provided)
        moved=[]
        for entry in provided['claims']:
            source=Path(entry['source']);destination=Path(entry['destination'])
            if sha(regular(source))!=entry['sha256']:raise ReconciliationError('claim changed before atomic archive')
            atomic_archive(source,destination)
            if sha(regular(destination))!=entry['sha256'] or os.path.lexists(source):raise ReconciliationError('archived claim readback mismatch')
            moved.append(entry);r.write_new(QUARANTINE/('MOVED_%02d.json'%entry['tile_id']),entry)
        if snapshot()!=provided['immutable_campaign_snapshot']:raise ReconciliationError('immutable campaign bytes changed')
        if list((CAMPAIGN/'raw').glob('*.claim')):raise ReconciliationError('residual unknown claim after archive')
        receipt=seal({'schema':'WU088_EXACT_COMPLETED_CLAIM_QUARANTINE_RECEIPT_V1','plan_sha256':expected_sha,
            'reconciler_source_sha256':source_sha(),'claims':moved,'archived_claim_count':len(moved),
            'immutable_campaign_snapshot_unchanged':True,'numerical_files_modified':False,'actual_native_executions':0,
            'root_cause':'UNDETERMINED','root_cause_closed':False,'scope':'B22_EXACT_TERMINAL_CLAIMS_ONLY'},'receipt_sha256')
        r.write_new(QUARANTINE/'RECEIPT.json',receipt);return receipt
    finally:
        os.close(fd)
        if regular(lock)==owned:lock.unlink()
        else:raise ReconciliationError('reconciliation RUN.claim ownership changed; preserved')

def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='action',required=True)
    p=sub.add_parser('plan');p.add_argument('--output',required=True)
    p=sub.add_parser('apply');p.add_argument('--plan',required=True);p.add_argument('--plan-sha256',required=True)
    args=ap.parse_args()
    if args.action=='plan':
        result=verified_plan();runner().write_new(args.output,result)
    else:result=apply(args.plan,args.plan_sha256)
    print(json.dumps({'status':'PLAN_WRITTEN' if args.action=='plan' else 'EXACT_CLAIMS_QUARANTINED','identity':result.get('plan_sha256',result.get('receipt_sha256')),'actual_native_executions':0}))
if __name__=='__main__':main()
