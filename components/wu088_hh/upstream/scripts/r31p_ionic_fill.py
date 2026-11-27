#!/usr/bin/env python3
"""R31P midpoint ionic intake: reuse CP4 admitted nodes, compute z=40/56 only."""
from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import r31n_provider_fill as base
from wu088_hh.r31p import MIDPOINTS,CP4_REUSED_IONIC,ensure_cp4_ionic_executables
from wu088_hh.backup import dual_backup,digest


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def target(remote,prefix,name):return remote.rstrip('/')+('' if remote.endswith(':') else '/')+prefix.strip('/')+'/'+name

def seal_files(cp4:Path,paths:list[str],out:Path):
    tmp=out.with_suffix('.tmp.zip');out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as zf:
        for rel in sorted(set(paths)):
            p=cp4/rel
            if not p.is_file():raise FileNotFoundError(p)
            zi=zipfile.ZipInfo(rel);zi.date_time=(2026,9,27,0,0,0);zi.external_attr=(0o100644<<16);zi.compress_type=zipfile.ZIP_DEFLATED
            zf.writestr(zi,p.read_bytes())
    os.replace(tmp,out);return sha(out),out.stat().st_size

def backup(seal:Path,receipt:Path,drive,dropbox,prefix):
    s,n=digest(seal)
    if receipt.exists():
        old=json.loads(receipt.read_text())
        if old.get('source_sha256')==s and old.get('source_bytes')==n and old.get('dual_raw_readback_verified') is True:return old
        raise RuntimeError('ionic backup receipt mismatch')
    dest={'google_drive':target(drive,prefix,seal.name),'dropbox':target(dropbox,prefix,seal.name)}
    r=dual_backup(seal,dest,receipt)
    if not r['dual_raw_readback_verified']:raise RuntimeError('ionic dual backup incomplete')
    return r

def main():
    p=argparse.ArgumentParser();p.add_argument('--cp4-root',type=Path,required=True);p.add_argument('--out-root',type=Path,required=True)
    p.add_argument('--drive',default=os.environ.get('GDRIVE_RCLONE_REMOTE'));p.add_argument('--dropbox',default=os.environ.get('DROPBOX_RCLONE_REMOTE'))
    p.add_argument('--backup-prefix',default='BASS_DERIVATION_DOSSIERS_20260912/WU088_HH_R31P_MIDPOINT_DIRECT/IONIC')
    p.add_argument('--threads',type=int,choices=(1,2),default=2);p.add_argument('--describe',action='store_true');a=p.parse_args()
    cp4=a.cp4_root.resolve();audit=base.audit_cp4_root(cp4,base.EXPECTED);index=json.loads((cp4/'completion/ionic/curve/INDEX.json').read_text())
    byz={int(x['z']):x for x in index['nodes']}
    plan={'reuse':sorted(CP4_REUSED_IONIC),'compute':[z for z in MIDPOINTS if z not in CP4_REUSED_IONIC],'threads':a.threads,'interpolation_evaluated':False}
    if a.describe:print(json.dumps({'status':'R31P_IONIC_FILL_READY','cp4_audit':audit,'plan':plan},indent=2));return 0
    executable_modes=ensure_cp4_ionic_executables(cp4)
    a.out_root.mkdir(parents=True,exist_ok=True);rows=[]
    for z in MIDPOINTS:
        if z in CP4_REUSED_IONIC:
            node=byz[z]
            if node['status']!='ADMITTED_NATIVE_NODE':raise RuntimeError(f'CP4 ionic z={z} not admitted')
            block=cp4/node['block_npz'];receipt=cp4/node['receipt']
            rows.append({'z':z,'status':'REUSED_CP4_ADMITTED_IONIC_NODE','receipt':node['receipt'],'receipt_sha256':sha(receipt),
                         'block_npz':node['block_npz'],'block_sha256':sha(block),'backup':'CP4_ARCHIVE_DURABLE_REUSE'})
            continue
        cli=cp4/'completion/ionic/node_cli_v2.py';env=dict(os.environ);env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None)
        proc=subprocess.run([sys.executable,str(cli),'--z',repr(float(z)),'--threads',str(a.threads)],cwd=cp4,env=env,capture_output=True,text=True)
        if proc.returncode:raise RuntimeError(f'ionic z={z} failed: {proc.stderr[-4000:]}')
        line=[x for x in proc.stdout.splitlines() if x.strip()][-1];out=json.loads(line)
        if out['status'] not in ('ADMITTED_NATIVE_NODE','REUSED_ADMITTED_NODE'):raise RuntimeError(f'ionic z={z} not admitted: {out}')
        rel=out['receipt'];node=json.loads((cp4/rel).read_text());paths=[rel,node['block_npz'],*node['records'].values()]
        seal=a.out_root/f'R31P_IONIC_z{z}_NODE_SEAL.zip';ss,nb=seal_files(cp4,paths,seal)
        row={'z':z,'status':'ADMITTED_NATIVE_NODE','receipt':rel,'receipt_sha256':sha(cp4/rel),'block_npz':node['block_npz'],
             'block_sha256':sha(cp4/node['block_npz']),'seal_sha256':ss,'seal_bytes':nb}
        if a.drive and a.dropbox:
            br=backup(seal,a.out_root/f'IONIC_z{z}_DUAL_BACKUP_RECEIPT.json',a.drive,a.dropbox,a.backup_prefix+f'/z{z}');row['backup']=br['status']
        rows.append(row)
    durable=all(r.get('backup') in ('CP4_ARCHIVE_DURABLE_REUSE','DUAL_RAW_READBACK_VERIFIED') for r in rows)
    summary={'schema':'WU088_R31P_IONIC_FILL_SUMMARY_V1','cp4_sha256':base.CP4_SHA,'plan':plan,'executable_modes':executable_modes,'nodes':rows,
             'all_nodes_durable':durable,'interpolation_evaluated':False,'trajectory_admitted':False,'production_admitted':False,
             'status':'R31P_IONIC_FILL_COMPLETE_DURABLE' if durable else 'R31P_IONIC_FILL_COMPLETE_LOCAL_ONLY'}
    base.atomic_json(a.out_root/'R31P_IONIC_FILL_SUMMARY.json',summary);print(json.dumps(summary,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
