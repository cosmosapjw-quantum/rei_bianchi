#!/usr/bin/env python3
"""R31R depth-first direct-node materialization at z=2 only.

This is a cost-minimizing discriminator after R31Q. It does not evaluate
interpolation locally. If z=2 later proves [0,4] unresolved, the global
piecewise-linear admission can be pursued depth-first without precomputing
all ten breadth-first bisection nodes.
"""
from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,os,sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts'),str(ROOT/'vendor/orchestration')]
from wu088_hh.r31r import FIRST_DISCRIMINATOR_NODE,H_ORDERS,first_discriminator_plan,h_folder_name


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def atomic_json(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n');os.replace(tmp,path)


def jvp_z0_costs(cp4):
    import numpy as np
    folder=Path(cp4)/'completion/mixed_derivative/B192_z0';cost={}
    for ia in range(12):
        for ib in range(12):
            with np.load(folder/f'pair_{ia:02}_{ib:02}.npz',allow_pickle=False) as f:cost[ia,ib]=float(f['seconds'])
    return cost


def close_h(*,runtime,z,n,profile,regression,drive,dropbox,out):
    import r31p_midpoint_direct as hp
    folder=runtime/'completion/mixed_h/wide_hybrid12'/h_folder_name(n,z)
    receipts=out/'delta_receipts'/f'z{int(z)}_B{n}'
    prefix=f'BASS_DERIVATION_DOSSIERS_20260912/WU088_HH_R31R_DEPTHFIRST/H_z{int(z)}/B{n}'
    attempts=0;compute_wall=0.0
    while True:
        attempts+=1
        if attempts>20:raise RuntimeError(f'H z={z} B{n} did not close within 20 bounded invocations')
        if folder.exists():hp.ack_pending(folder,receipts,drive,dropbox,prefix)
        if hp.h_complete(folder):break
        cmd=[sys.executable,str(ROOT/'scripts/run_tuned_heavy.py'),'--runtime',str(runtime),'--tuning-profile',str(profile),'--regression',str(regression),
             '--n',str(n),'--g','80','--z',repr(float(z)),'--gamma-scale','unit','--max-new-pairs','12','--max-wall-seconds','600','--execution-lane','local']
        _,wall=hp.run_cmd(cmd,allowed=(0,74));compute_wall+=wall
        if folder.exists():hp.ack_pending(folder,receipts,drive,dropbox,prefix)
    state=hp.verify_h_state(folder);state['bounded_invocations']=attempts;state['wrapper_compute_wall_seconds']=compute_wall
    seal=out/'h_seals'/f'R31R_H_z{int(z)}_B{n}_PAIR_STATE.zip'
    receipt=out/'h_seals'/f'R31R_H_z{int(z)}_B{n}_DUAL_BACKUP_RECEIPT.json'
    if receipt.exists():
        br,(ss,nb)=hp.reuse_or_restore_backed_seal(seal,receipt,folder)
    else:
        ss,nb=hp.deterministic_state_seal(folder,seal)
        br=hp.backup_seal(seal,receipt,drive,dropbox,prefix+'/final')
    state.update(seal=str(seal),seal_sha256=ss,seal_bytes=nb,backup=br['status'])
    return state


def provider_identity(pb,kind,z):
    return {'schema':'WU088_R31R_DEPTHFIRST_NODE_IDENTITY_V1','cp4_sha256':pb.CP4_SHA,'kind':kind,'n':192,'z':float(z),
            'source_hashes':pb.EXPECTED,'parallelism':'PAIR_LEVEL_ONLY_12x1_PHYSICAL','interpolation_evaluated':False}


def close_provider(pb,folder,cp4,z,kind,workers,groups,drive,dropbox,prefix):
    folder.mkdir(parents=True,exist_ok=True);pb.ensure_identity(folder,provider_identity(pb,kind,z))
    if kind=='OD192':costs=pb.od_order_costs(cp4);initializer=pb.init_od;assemble=pb.assemble_od
    else:costs=jvp_z0_costs(cp4);initializer=pb.init_jvp;assemble=pb.assemble_jvp
    order=pb.order_pairs_by_cost(costs)
    tasks=[(i,j,str(folder/f'pair_{i:02}_{j:02}.npz')) for i,j in order if not (folder/f'pair_{i:02}_{j:02}.npz').exists()]
    if tasks:
        eff=min(workers,len(tasks));_,wall=pb.run_pool(tasks,eff,initializer,(str(cp4),z,groups[:eff]),folder/'events.jsonl')
    else:wall=0.0
    res=assemble(folder,cp4,z);res['compute_wall_seconds']=wall;res['r31r_kind']=kind
    seal=folder/f'R31R_{kind}_z{int(z)}_NODE_SEAL.zip';ss,nb=pb.deterministic_seal(folder,seal);res.update(seal_sha256=ss,seal_bytes=nb)
    if drive and dropbox:
        res['backup']=pb.maybe_backup(seal,folder/'DUAL_BACKUP_RECEIPT.json',drive,dropbox,prefix+f'/{kind}_z{int(z)}')['status']
    return res


def reuse_ionic_z2(cp4):
    index=json.loads((cp4/'completion/ionic/curve/INDEX.json').read_text())
    matches=[x for x in index['nodes'] if float(x['z'])==2.0]
    if len(matches)!=1:raise RuntimeError('expected exactly one CP4 ionic z=2 node')
    node=matches[0]
    if node.get('status')!='ADMITTED_NATIVE_NODE':raise RuntimeError('CP4 ionic z=2 is not admitted')
    receipt=cp4/node['receipt'];block=cp4/node['block_npz']
    return {'z':2.0,'status':'REUSED_CP4_ADMITTED_IONIC_NODE','receipt':node['receipt'],'receipt_sha256':sha(receipt),
            'block_npz':node['block_npz'],'block_sha256':sha(block),'backup':'CP4_ARCHIVE_DURABLE_REUSE'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--runtime',type=Path,required=True);p.add_argument('--cp4-root',type=Path)
    p.add_argument('--tuning-profile',type=Path,default=ROOT/'evidence/host_5900x/HOST_TUNING_PROFILE.json')
    p.add_argument('--regression',type=Path,default=ROOT/'evidence/host_5900x/SCIENCE_RESOLUTION_NATIVE_REGRESSION.json')
    p.add_argument('--drive',default=os.environ.get('GDRIVE_RCLONE_REMOTE'));p.add_argument('--dropbox',default=os.environ.get('DROPBOX_RCLONE_REMOTE'))
    p.add_argument('--describe',action='store_true');a=p.parse_args()
    plan=first_discriminator_plan()
    if a.describe:
        print(json.dumps({'status':'R31R_Z2_DISCRIMINATOR_READY','plan':plan,'interpolation_evaluated':False},indent=2));return 0
    if not a.drive or not a.dropbox:p.error('raw Drive and Dropbox rclone remotes are required')
    work=a.work.resolve();runtime=a.runtime.resolve();cp4=(a.cp4_root or work/'r31n_cp4_source/extracted').resolve();out=work/'r31r_depthfirst_z2';out.mkdir(parents=True,exist_ok=True)
    import r31n_provider_fill as pb
    audit=pb.audit_cp4_root(cp4,pb.EXPECTED)
    summary={'schema':'WU088_R31R_Z2_DIRECT_SUMMARY_V1','plan':plan,'cp4_audit':audit,'H':[],'providers':[],'ionic':None,
             'H_convergence_evaluated':False,'full49_admission_evaluated':False,'interpolation_evaluated':False,'trajectory_runs':0,
             'trajectory_admitted':False,'production_admitted':False}
    z=FIRST_DISCRIMINATOR_NODE
    for n in H_ORDERS:
        summary['H'].append(close_h(runtime=runtime,z=z,n=n,profile=a.tuning_profile.resolve(),regression=a.regression.resolve(),drive=a.drive,dropbox=a.dropbox,out=out))
        atomic_json(out/'R31R_Z2_DIRECT_SUMMARY.partial.json',summary)
    cpus=pb.physical_cpus(12);groups=[[c] for c in cpus]
    for kind in ('OD192','JVP192'):
        summary['providers'].append(close_provider(pb,out/f'{kind}_z2',cp4,z,kind,12,groups,a.drive,a.dropbox,
            'BASS_DERIVATION_DOSSIERS_20260912/WU088_HH_R31R_DEPTHFIRST'))
    summary['ionic']=reuse_ionic_z2(cp4)
    h_ok=len(summary['H'])==2 and all(x.get('backup')=='DUAL_RAW_READBACK_VERIFIED' for x in summary['H'])
    p_ok=len(summary['providers'])==2 and all(x.get('backup')=='DUAL_RAW_READBACK_VERIFIED' for x in summary['providers'])
    summary['all_direct_sources_durable']=bool(h_ok and p_ok and summary['ionic']['backup']=='CP4_ARCHIVE_DURABLE_REUSE')
    summary['status']='R31R_Z2_DIRECT_COMPLETE_DURABLE' if summary['all_direct_sources_durable'] else 'R31R_Z2_DIRECT_INCOMPLETE_DURABILITY'
    atomic_json(out/'R31R_Z2_DIRECT_SUMMARY.json',summary);print(json.dumps(summary,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
