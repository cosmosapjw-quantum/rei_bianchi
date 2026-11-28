#!/usr/bin/env python3
"""One-shot R31P local handoff for direct midpoint source materialization.

This script does not evaluate interpolation.  It only creates durable direct
midpoint H(B160/B192), OD192, JVP192 and ionic providers for the preregistered
R31J midpoint sentinels.
"""
from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,time,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts'),str(ROOT/'vendor/orchestration')]
from wu088_hh.r31p import MIDPOINTS,H_ORDERS,h_folder_name,midpoint_plan,interpolation_contract
from wu088_hh.backup import dual_backup,digest
from heavy_numerics_v2 import pending_delta_hashes


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atomic_json(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n');os.replace(tmp,path)
def target(remote,prefix,name):return remote.rstrip('/')+('' if remote.endswith(':') else '/')+prefix.strip('/')+'/'+name

def deterministic_state_seal(folder:Path,out:Path):
    out.parent.mkdir(parents=True,exist_ok=True);tmp=out.with_suffix('.tmp.zip')
    volatile={'RUN.lock','RUN_STATE.json'}
    members=sorted(p for p in folder.rglob('*') if p.is_file() and p.name not in volatile and not p.name.endswith('.tmp'))
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as zf:
        for p in members:
            zi=zipfile.ZipInfo(str(p.relative_to(folder)));zi.date_time=(2026,9,27,0,0,0);zi.external_attr=(0o100644<<16);zi.compress_type=zipfile.ZIP_DEFLATED
            zf.writestr(zi,p.read_bytes())
    os.replace(tmp,out);return sha(out),out.stat().st_size

def backup_seal(seal:Path,receipt:Path,drive,dropbox,prefix):
    s,n=digest(seal)
    if receipt.exists():
        old=json.loads(receipt.read_text())
        if old.get('source_sha256')==s and old.get('source_bytes')==n and old.get('dual_raw_readback_verified') is True:return old
        raise RuntimeError('existing H seal backup receipt mismatch')
    dest={'google_drive':target(drive,prefix,seal.name),'dropbox':target(dropbox,prefix,seal.name)}
    r=dual_backup(seal,dest,receipt)
    if not r['dual_raw_readback_verified']:raise RuntimeError('H seal dual backup incomplete')
    return r

def _verify_seal_scientific_payload(seal:Path,folder:Path):
    required=[folder/'IDENTITY.json',folder/'RESULTS.json',folder/'ASSEMBLED.npz',*sorted(folder.glob('pair_??_??.npz'))]
    with zipfile.ZipFile(seal,'r') as zf:
        names=set(zf.namelist())
        for p in required:
            rel=str(p.relative_to(folder))
            if rel not in names:raise RuntimeError(f'durable H seal missing scientific payload: {rel}')
            if hashlib.sha256(zf.read(rel)).hexdigest()!=sha(p):raise RuntimeError(f'durable H seal scientific payload drift: {rel}')
    return True

def reuse_or_restore_backed_seal(seal:Path,receipt:Path,folder:Path,*,rclone_bin='rclone'):
    old=json.loads(receipt.read_text())
    if old.get('dual_raw_readback_verified') is not True:raise RuntimeError('existing H seal receipt is not dual-readback verified')
    expected=(str(old.get('source_sha256')),int(old.get('source_bytes',-1)))
    seal.parent.mkdir(parents=True,exist_ok=True)
    if seal.is_file() and digest(seal)==expected:
        _verify_seal_scientific_payload(seal,folder)
        return old,expected
    tmp=seal.with_suffix('.restore.tmp')
    providers=old.get('providers') or {}
    errors=[]
    for provider in ('google_drive','dropbox'):
        target_path=(providers.get(provider) or {}).get('destination')
        if not target_path:continue
        try:
            tmp.unlink(missing_ok=True)
            cp=subprocess.run([rclone_bin,'copyto',str(target_path),str(tmp)],capture_output=True,text=True,timeout=300)
            if cp.returncode:raise RuntimeError(f'copyto exit={cp.returncode}: {cp.stderr[-1200:]}')
            if digest(tmp)!=expected:raise RuntimeError('restored H seal SHA/size mismatch')
            os.replace(tmp,seal)
            _verify_seal_scientific_payload(seal,folder)
            return old,expected
        except Exception as exc:
            errors.append(f'{provider}: {exc}')
    tmp.unlink(missing_ok=True)
    raise RuntimeError('cannot restore existing dual-backed H seal: '+' | '.join(errors))

def verify_h_state(folder:Path):
    pairs=sorted(folder.glob('pair_??_??.npz'))
    if len(pairs)!=144:raise RuntimeError(f'H state has {len(pairs)} pair files, expected 144')
    events=folder/'events.jsonl'
    if not events.is_file():raise RuntimeError('H state lacks events.jsonl')
    rows=[json.loads(x) for x in events.read_text().splitlines() if x.strip()]
    event_map={}
    for r in rows:
        if 'ia' not in r:continue
        key=(int(r['ia']),int(r['ib']));h=str(r['sha256'])
        if key in event_map and event_map[key]!=h:raise RuntimeError(f'H event hash drift at {key}')
        event_map[key]=h
    if len(event_map)!=144:raise RuntimeError(f'H event ledger has {len(event_map)} unique coordinates')
    for p in pairs:
        ia,ib=(int(x) for x in p.stem.split('_')[1:3])
        if event_map.get((ia,ib))!=sha(p):raise RuntimeError(f'H pair hash mismatch: {p.name}')
    rp,ap,ip=folder/'RESULTS.json',folder/'ASSEMBLED.npz',folder/'IDENTITY.json'
    if not all(p.is_file() for p in (rp,ap,ip)):raise RuntimeError('H state lacks final aggregate/result/identity')
    result=json.loads(rp.read_text())
    if result['sha256']!=sha(ap) or result['identity_sha256']!=sha(ip):raise RuntimeError('H final result identity mismatch')
    if pending_delta_hashes(folder):raise RuntimeError('H state still has unacknowledged deltas')
    return {'pair_count':144,'assembled_sha256':sha(ap),'results_sha256':sha(rp),'identity_sha256':sha(ip),'n':int(result['n']),'z':float(result['z'])}

def run_cmd(cmd,*,env=None,allowed=(0,),capture=False):
    t=time.perf_counter();p=subprocess.run(cmd,env=env,text=True,capture_output=capture);wall=time.perf_counter()-t
    if p.returncode not in allowed:
        tail=((p.stdout or '')+'\n'+(p.stderr or ''))[-6000:] if capture else ''
        raise RuntimeError(f'command failed rc={p.returncode}: {cmd}\n{tail}')
    return p,wall

def ack_pending(folder:Path,receipts:Path,drive,dropbox,prefix):
    if not pending_delta_hashes(folder):return
    receipts.mkdir(parents=True,exist_ok=True)
    cmd=[sys.executable,str(ROOT/'scripts/backup_pending.py'),'--folder',str(folder),'--drive',drive,'--dropbox',dropbox,'--prefix',prefix,'--receipts',str(receipts)]
    run_cmd(cmd)

def h_complete(folder:Path):return len(list(folder.glob('pair_??_??.npz')))==144 and (folder/'RESULTS.json').is_file() and (folder/'ASSEMBLED.npz').is_file()

def close_h_basis(*,work:Path,runtime:Path,z:int,n:int,profile:Path,regression:Path,drive:str,dropbox:str,out:Path):
    folder=runtime/'completion/mixed_h/wide_hybrid12'/h_folder_name(n,float(z))
    receipts=out/'delta_receipts'/f'z{z}_B{n}';prefix=f'BASS_DERIVATION_DOSSIERS_20260912/WU088_HH_R31P_MIDPOINT_DIRECT/H_z{z}/B{n}'
    attempts=0;compute_wall=0.0
    while True:
        attempts+=1
        if attempts>20:raise RuntimeError(f'H z={z} B{n} did not close within 20 bounded invocations')
        if folder.exists():ack_pending(folder,receipts,drive,dropbox,prefix)
        if h_complete(folder):break
        cmd=[sys.executable,str(ROOT/'scripts/run_tuned_heavy.py'),'--runtime',str(runtime),'--tuning-profile',str(profile),'--regression',str(regression),
             '--n',str(n),'--g','80','--z',repr(float(z)),'--gamma-scale','unit','--max-new-pairs','12','--max-wall-seconds','600','--execution-lane','local']
        p,wall=run_cmd(cmd,allowed=(0,74));compute_wall+=wall
        if folder.exists():ack_pending(folder,receipts,drive,dropbox,prefix)
    state=verify_h_state(folder);state['bounded_invocations']=attempts;state['wrapper_compute_wall_seconds']=compute_wall
    seal=out/'h_seals'/f'R31P_H_z{z}_B{n}_PAIR_STATE.zip';receipt=out/'h_seals'/f'R31P_H_z{z}_B{n}_DUAL_BACKUP_RECEIPT.json'
    if receipt.exists():
        br,(ss,nb)=reuse_or_restore_backed_seal(seal,receipt,folder)
    else:
        ss,nb=deterministic_state_seal(folder,seal)
        br=backup_seal(seal,receipt,drive,dropbox,prefix+'/final')
    state.update(seal=str(seal),seal_sha256=ss,seal_bytes=nb,backup=br['status'])
    return state

def main():
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--runtime',type=Path,required=True)
    p.add_argument('--cp4-root',type=Path);p.add_argument('--tuning-profile',type=Path,default=ROOT/'evidence/host_5900x/HOST_TUNING_PROFILE.json')
    p.add_argument('--regression',type=Path,default=ROOT/'evidence/host_5900x/SCIENCE_RESOLUTION_NATIVE_REGRESSION.json')
    p.add_argument('--drive',default=os.environ.get('GDRIVE_RCLONE_REMOTE'));p.add_argument('--dropbox',default=os.environ.get('DROPBOX_RCLONE_REMOTE'))
    p.add_argument('--describe',action='store_true');a=p.parse_args()
    plan=midpoint_plan(existing_ionic_nodes={4,12,24})
    if a.describe:
        print(json.dumps({'status':'R31P_MIDPOINT_DIRECT_READY','plan':plan,'interpolation_contract':interpolation_contract(),
                          'H_parallelism':'R31M_HOST_TUNED_2x12_SMT','OD_JVP_parallelism':'12x1_PHYSICAL','ionic_new':[40,56]},indent=2));return 0
    if not a.drive or not a.dropbox:p.error('raw Drive and Dropbox rclone remotes are required')
    work=a.work.resolve();runtime=a.runtime.resolve();cp4=(a.cp4_root or work/'r31n_cp4_source/extracted').resolve();out=work/'r31p_midpoint_direct';out.mkdir(parents=True,exist_ok=True)
    for q in (a.tuning_profile,a.regression,ROOT/'scripts/run_tuned_heavy.py',ROOT/'scripts/backup_pending.py',ROOT/'scripts/r31p_provider_fill.py',ROOT/'scripts/r31p_ionic_fill.py'):
        if not Path(q).is_file():raise FileNotFoundError(q)
    summary={'schema':'WU088_R31P_MIDPOINT_DIRECT_SUMMARY_V1','plan':plan,'H':[],'provider_summary':None,'ionic_summary':None,
             'H_convergence_evaluated':False,'full49_admission_evaluated':False,'interpolation_evaluated':False,
             'trajectory_runs':0,'trajectory_admitted':False,'production_admitted':False}
    for z in MIDPOINTS:
        for n in H_ORDERS:
            state=close_h_basis(work=work,runtime=runtime,z=z,n=n,profile=a.tuning_profile.resolve(),regression=a.regression.resolve(),drive=a.drive,dropbox=a.dropbox,out=out)
            summary['H'].append(state);atomic_json(out/'R31P_MIDPOINT_DIRECT_SUMMARY.partial.json',summary)
    provider_out=out/'providers';cmd=[sys.executable,str(ROOT/'scripts/r31p_provider_fill.py'),'--cp4-root',str(cp4),'--out-root',str(provider_out),'--workers','12','--drive',a.drive,'--dropbox',a.dropbox]
    run_cmd(cmd);summary['provider_summary']=str(provider_out/'R31P_PROVIDER_FILL_SUMMARY.json')
    ionic_out=out/'ionic';cmd=[sys.executable,str(ROOT/'scripts/r31p_ionic_fill.py'),'--cp4-root',str(cp4),'--out-root',str(ionic_out),'--threads','2','--drive',a.drive,'--dropbox',a.dropbox]
    run_cmd(cmd);summary['ionic_summary']=str(ionic_out/'R31P_IONIC_FILL_SUMMARY.json')
    prov=json.loads(Path(summary['provider_summary']).read_text());ion=json.loads(Path(summary['ionic_summary']).read_text())
    h_durable=all(x.get('backup')=='DUAL_RAW_READBACK_VERIFIED' for x in summary['H']) and len(summary['H'])==10
    summary['all_direct_nodes_durable']=bool(h_durable and prov.get('all_nodes_dual_backed_up') is True and ion.get('all_nodes_durable') is True)
    summary['status']='R31P_MIDPOINT_DIRECT_COMPLETE_DURABLE' if summary['all_direct_nodes_durable'] else 'R31P_MIDPOINT_DIRECT_INCOMPLETE_DURABILITY'
    atomic_json(out/'R31P_MIDPOINT_DIRECT_SUMMARY.json',summary);print(json.dumps(summary,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
