#!/usr/bin/env python3
"""R31P direct midpoint OD192/JVP192 fill from recovered CP4 sources.

No interpolation is evaluated here.  Scientific pair kernels and aggregate
contractions are exactly the recovered R31N/CP4 paths; only pair scheduling is
parallelized.
"""
from __future__ import annotations
from pathlib import Path
import argparse,json,os,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import r31n_provider_fill as base
from wu088_hh.r31p import MIDPOINTS


def load_jvp_costs(cp4:Path,z:int):
    anchors=(0,16,32,64)
    lo=max(a for a in anchors if a<=z); hi=min(a for a in anchors if a>=z)
    def one(node):
        folder=cp4/f'completion/mixed_derivative/B192_z{node}'
        out={}
        for ia in range(12):
            for ib in range(12):
                with base.np.load(folder/f'pair_{ia:02}_{ib:02}.npz',allow_pickle=False) as f:
                    out[ia,ib]=float(f['seconds'])
        return out
    if lo==hi:return one(lo)
    return base.interpolate_pair_costs(one(lo),one(hi),(z-lo)/(hi-lo))


def custom_identity(kind,z):
    return {'schema':'WU088_R31P_MIDPOINT_NODE_IDENTITY_V1','cp4_sha256':base.CP4_SHA,
            'kind':kind,'n':192,'z':float(z),'source_hashes':base.EXPECTED,
            'parallelism':'PAIR_LEVEL_ONLY_12x1_PHYSICAL','interpolation_evaluated':False}


def close_node(folder:Path,cp4:Path,z:int,kind:str,workers:int,groups,drive,dropbox,prefix):
    folder.mkdir(parents=True,exist_ok=True);base.ensure_identity(folder,custom_identity(kind,z))
    if kind=='OD192':
        costs=base.od_order_costs(cp4); initializer=base.init_od; assemble=base.assemble_od
    else:
        costs=load_jvp_costs(cp4,z); initializer=base.init_jvp; assemble=base.assemble_jvp
    order=base.order_pairs_by_cost(costs)
    tasks=[(i,j,str(folder/f'pair_{i:02}_{j:02}.npz')) for i,j in order if not (folder/f'pair_{i:02}_{j:02}.npz').exists()]
    if tasks:
        eff=min(workers,len(tasks)); _,wall=base.run_pool(tasks,eff,initializer,(str(cp4),z,groups[:eff]),folder/'events.jsonl')
    else: wall=0.0
    res=assemble(folder,cp4,z);res['compute_wall_seconds']=wall;res['r31p_kind']=kind
    seal=folder/f'R31P_{kind}_z{z}_NODE_SEAL.zip';ss,nb=base.deterministic_seal(folder,seal);res.update(seal_sha256=ss,seal_bytes=nb)
    if drive and dropbox:
        receipt=base.maybe_backup(seal,folder/'DUAL_BACKUP_RECEIPT.json',drive,dropbox,prefix+f'/{kind}_z{z}')
        res['backup']=receipt['status']
    return res


def main():
    p=argparse.ArgumentParser();p.add_argument('--cp4-root',type=Path,required=True);p.add_argument('--out-root',type=Path,required=True)
    p.add_argument('--workers',type=int,default=12);p.add_argument('--drive',default=os.environ.get('GDRIVE_RCLONE_REMOTE'))
    p.add_argument('--dropbox',default=os.environ.get('DROPBOX_RCLONE_REMOTE'))
    p.add_argument('--backup-prefix',default='BASS_DERIVATION_DOSSIERS_20260912/WU088_HH_R31P_MIDPOINT_DIRECT')
    p.add_argument('--describe',action='store_true');a=p.parse_args()
    if not 1<=a.workers<=12:p.error('workers must be 1..12 physical cores')
    cp4=a.cp4_root.resolve();audit=base.audit_cp4_root(cp4,base.EXPECTED)
    plan={'midpoints':list(MIDPOINTS),'OD192':list(MIDPOINTS),'JVP192':list(MIDPOINTS),'workers':a.workers,
          'parallelism':'PAIR_LEVEL_ONLY_12x1_PHYSICAL','interpolation_evaluated':False}
    if a.describe:
        print(json.dumps({'status':'R31P_PROVIDER_FILL_READY','cp4_audit':audit,'plan':plan},indent=2));return 0
    a.out_root.mkdir(parents=True,exist_ok=True);cpus=base.physical_cpus(a.workers);groups=[[c] for c in cpus]
    summary={'schema':'WU088_R31P_PROVIDER_FILL_SUMMARY_V1','cp4_sha256':base.CP4_SHA,'plan':plan,'nodes':[],
             'interpolation_evaluated':False,'trajectory_admitted':False,'production_admitted':False}
    for z in MIDPOINTS:
        summary['nodes'].append(close_node(a.out_root/f'OD192_z{z}',cp4,z,'OD192',a.workers,groups,a.drive,a.dropbox,a.backup_prefix))
        summary['nodes'].append(close_node(a.out_root/f'JVP192_z{z}',cp4,z,'JVP192',a.workers,groups,a.drive,a.dropbox,a.backup_prefix))
    summary['all_nodes_dual_backed_up']=all(n.get('backup')=='DUAL_RAW_READBACK_VERIFIED' for n in summary['nodes']) if a.drive and a.dropbox else False
    summary['status']='R31P_PROVIDER_FILL_COMPLETE_DURABLE' if summary['all_nodes_dual_backed_up'] else 'R31P_PROVIDER_FILL_COMPLETE_LOCAL_ONLY'
    base.atomic_json(a.out_root/'R31P_PROVIDER_FILL_SUMMARY.json',summary);print(json.dumps(summary,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
