#!/usr/bin/env python3
"""R31N source-bound fill for missing OD192 anchors and JVP192 z=48.

Uses exact recovered CP4 scientific sources. Pair evaluation is parallelized only
across independent primitive pairs; per-pair scientific arithmetic is unchanged.
"""
from __future__ import annotations
from pathlib import Path
import argparse, hashlib, importlib, json, multiprocessing, os, sys, time, zipfile
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from wu088_hh.r31n import audit_cp4_root, interpolate_pair_costs, jvp_assemble, od_contract, od_finalize, order_pairs_by_cost
from wu088_hh.backup import dual_backup, digest

CP4_SHA='c10c932a6cdad817982e00920a893733b367827b116d058791bf5aacad517cd9'
EXPECTED={
'completion/mixed_derivative/jvp.cpp':'2ea30233fb959ec916427d672d4b7180347f4689a036ae393da6073078892cbd',
'completion/mixed_derivative/native.py':'247c9eca3c8cfa35a437f48b4ba72aac98d24dff1bc336b008058141b591a22d',
'completion/mixed_derivative/run.py':'d092d3e81a952d90488f25922c57ea3148b9f036d15a884f7efe51ade09de935',
'completion/mixed_derivative/CONTRACT.json':'f5a10ef22dd5aefade7e9d9dc079066c0b3e0781a9c997411997cb67ba0acb66',
'completion/mixed_h/od_run.py':'63c0925ff938340feceb5768aba40da348b3afe323214a9792012e9d0bbc664d',
'completion/mixed_h/h0_backend.py':'128e13bd475ce6aeb57e3c601239318e00f6bfbfee6f99a85ba081aa97b1a9e5',
'completion/mixed_h/h0_fused.cpp':'d019713f8a9c6e864d60cc796104a0cdef629e491e6ab8de757995aa4f3672f2',
'completion/mixed_h/native.py':'44f784c895730d07e5a40ccc5369534f6a8e81798689a27c98a0bf5fd0a2d778',
'completion/ionic/ionic.py':'8b801a51cf857fc5fb4b88cfd69c43ba39338e68dc8fb9b7d7abcfb2c8e6df54',
'cont2c/convergence/frozen_grid_n192.npz':'e1959e1bbb66b5e27410daa3d3bdb0815885919f11af3a014d86a47f15b96301',
'inputs/extracted/WU088_HH_R10_FULL_MIXED_BLOCK_OHD_PARTIAL_20260922_v1/inputs/FROZEN_INPUTS.npz':'8482d2854ab620c58bb1d7a7a45cf88eb71fd75081242263a9ef48927f0a282c',
}
OD_Z=(16,32,48,64); JVP_Z=(48,)
STATE=None

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atomic_json(path,obj):
    path=Path(path);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n');os.replace(tmp,path)
def atomic_npz(path,**arrays):
    path=Path(path);tmp=path.with_suffix('.tmp')
    with tmp.open('wb') as f: np.savez_compressed(f,**arrays);f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)

def physical_cpus(n):
    allowed=sorted(os.sched_getaffinity(0));by={}
    for cpu in allowed:
        b=Path(f'/sys/devices/system/cpu/cpu{cpu}/topology')
        key=(int((b/'physical_package_id').read_text()),int((b/'core_id').read_text()))
        by.setdefault(key,cpu)
    cpus=sorted(by.values())
    if len(cpus)<n: raise RuntimeError(f'need {n} physical CPUs, found {len(cpus)}')
    return cpus[:n]

def _worker_slot(groups,counter,lock,barrier):
    with lock: idx=counter.value;counter.value+=1
    if idx>=len(groups): raise RuntimeError('worker slot overflow')
    os.sched_setaffinity(0,set(groups[idx]));barrier.wait()

def init_od(cp4,z,groups,counter,lock,barrier):
    global STATE
    _worker_slot(groups,counter,lock,barrier)
    base=Path(cp4)/'completion/mixed_h';sys.path.insert(0,str(base));sys.path.insert(0,str(Path(cp4)/'foreign_analytic'));sys.path.insert(0,str(Path(cp4)/'exact_weights'));sys.path.insert(0,str(Path(cp4)/'exact_weights/deps'))
    native=importlib.import_module('native');h0=importlib.import_module('h0_backend')
    d,t,W,_,_=native.grid(192);STATE=('od',h0.H0Fused(),d,t,W,float(z))

def work_od(task):
    _,h,d,t,W,z=STATE;ia,ib,path=task;path=Path(path)
    if path.exists():
        with np.load(path,allow_pickle=False) as f:
            if int(f['ia'])!=ia or int(f['ib'])!=ib: raise RuntimeError('OD checkpoint coordinate mismatch')
        return {'ia':ia,'ib':ib,'path':str(path),'sha256':sha(path),'reused':True,'wall_seconds':0.0}
    st=time.perf_counter();a=float(d['exponents'][ia]);b=float(d['exponents'][ib]);rows=[];absolute=[]
    for active in (0,1):
        values,sa=h.h0(a,b,t,W,z,float(d['v']),active);rows.append(values[[0,2,3]]);absolute.append(sa[[0,2,3]])
    wall=time.perf_counter()-st;atomic_npz(path,OG=np.array(rows),sumabs_upper_diagnostic=np.array(absolute),ia=ia,ib=ib,wall_seconds=wall)
    return {'ia':ia,'ib':ib,'path':str(path),'sha256':sha(path),'reused':False,'wall_seconds':wall}

def init_jvp(cp4,z,groups,counter,lock,barrier):
    global STATE
    _worker_slot(groups,counter,lock,barrier)
    # CP4's trusted native builder deliberately refuses dynamic-loader injection.
    # Sanitize only inside this worker before importing/building the recovered source.
    for var in ('LD_PRELOAD','LD_LIBRARY_PATH'):
        os.environ.pop(var,None)
    base=Path(cp4)/'completion/mixed_derivative';sys.path.insert(0,str(base));sys.path.insert(0,str(Path(cp4)/'production/engineering'));sys.path.insert(0,str(Path(cp4)/'foreign_analytic'))
    native=importlib.import_module('native')
    with np.load(Path(cp4)/'cont2c/convergence/frozen_grid_n192.npz',allow_pickle=False) as f:d={k:f[k] for k in f.files}
    STATE=('jvp',native.Native(),d,float(z))

def work_jvp(task):
    _,native,d,z=STATE;ia,ib,path=task;path=Path(path)
    if path.exists(): return {'ia':ia,'ib':ib,'path':str(path),'sha256':sha(path),'reused':True,'wall_seconds':0.0}
    st=time.perf_counter();out,sa=native.pair(d['exponents'][ia],d['exponents'][ib],d['t'],d['W'],np.longdouble(z),np.longdouble(d['v']),d['pref']);wall=time.perf_counter()-st
    atomic_npz(path,out=out,sumabs=sa,seconds=wall)
    return {'ia':ia,'ib':ib,'path':str(path),'sha256':sha(path),'reused':False,'wall_seconds':wall}

def run_pool(tasks,workers,initializer,initargs,events):
    ctx=multiprocessing.get_context('spawn');counter=ctx.Value('i',0);lock=ctx.Lock();barrier=ctx.Barrier(workers);rows=[];start=time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers,mp_context=ctx,initializer=initializer,initargs=(*initargs,counter,lock,barrier)) as pool:
        futures={pool.submit(work_od if initializer is init_od else work_jvp,t):t for t in tasks}
        for fut in as_completed(futures):
            row=fut.result();row['elapsed_wall_seconds']=time.perf_counter()-start;rows.append(row)
            with Path(events).open('a') as f:f.write(json.dumps(row,sort_keys=True)+'\n')
            print(json.dumps(row),flush=True)
    return rows,time.perf_counter()-start

def load_d(cp4):
    with np.load(Path(cp4)/'cont2c/convergence/frozen_grid_n192.npz',allow_pickle=False) as f:return {k:f[k] for k in f.files}

def od_order_costs(cp4):
    folder=Path(cp4)/'completion/mixed_h/od/B192_z0';cost={}
    for ia in range(12):
        for ib in range(12):
            with np.load(folder/f'pair_{ia:02}_{ib:02}.npz',allow_pickle=False) as f:cost[ia,ib]=float(f['wall_seconds'])
    return cost

def jvp_order_costs(cp4):
    vals=[]
    for z in (32,64):
        folder=Path(cp4)/f'completion/mixed_derivative/B192_z{z}';cost={}
        for ia in range(12):
            for ib in range(12):
                with np.load(folder/f'pair_{ia:02}_{ib:02}.npz',allow_pickle=False) as f:cost[ia,ib]=float(f['seconds'])
        vals.append(cost)
    return interpolate_pair_costs(vals[0],vals[1],0.5)

def identity(cp4,kind,z):
    return {'schema':'WU088_R31N_NODE_IDENTITY_V1','cp4_sha256':CP4_SHA,'kind':kind,'n':192,'z':float(z),'source_hashes':EXPECTED,'parallelism':'PAIR_LEVEL_ONLY_12x1_PHYSICAL'}
def ensure_identity(folder,obj):
    p=Path(folder)/'IDENTITY.json'
    if p.exists():
        if json.loads(p.read_text())!=obj: raise RuntimeError('R31N node identity mismatch')
    else: atomic_json(p,obj)

def assemble_od(folder,cp4,z):
    d=load_d(cp4);raw=np.empty((2,3,3,12,12),np.clongdouble);sa=np.empty(raw.shape,np.longdouble)
    for ia in range(12):
        for ib in range(12):
            with np.load(Path(folder)/f'pair_{ia:02}_{ib:02}.npz',allow_pickle=False) as f:raw[...,ia,ib]=f['OG'];sa[...,ia,ib]=f['sumabs_upper_diagnostic']
    comp,summed=od_contract(raw,sa,d,z);out=od_finalize(comp,d,z);p=Path(folder)/'ASSEMBLED_OD.npz'
    if not p.exists(): atomic_npz(p,**out,components_OG=comp,sumabs_upper_diagnostic=summed,n=192,z=float(z))
    result={'status':'COMPUTED_R31N_FINE_OD_SOURCE_BOUND','path':str(p),'sha256':sha(p),'n':192,'z':float(z),'Hamiltonian_included':False,'independent_dotO_included':False}
    atomic_json(Path(folder)/'RESULTS.json',result);return result

def assemble_jvp(folder,cp4,z):
    d=load_d(cp4);raw=np.empty((2,2,3,12,12),np.clongdouble);sa=np.empty(raw.shape,np.longdouble)
    for ia in range(12):
        for ib in range(12):
            with np.load(Path(folder)/f'pair_{ia:02}_{ib:02}.npz',allow_pickle=False) as f:raw[...,ia,ib]=f['out'];sa[...,ia,ib]=f['sumabs']
    O,dot=jvp_assemble(raw,d,z);p=Path(folder)/'ASSEMBLED.npz'
    if not p.exists(): atomic_npz(p,O=O,dotO=dot,raw=raw,sumabs=sa,z=np.longdouble(z))
    result={'status':'COMPUTED_R31N_INDEPENDENT_DERIVATIVE_SOURCE_BOUND','path':str(p),'sha256':sha(p),'n':192,'z':float(z)}
    atomic_json(Path(folder)/'RESULTS.json',result);return result

def deterministic_seal(folder,out):
    folder=Path(folder);out=Path(out);tmp=out.with_suffix('.tmp.zip');members=sorted(p for p in folder.rglob('*') if p.is_file() and p.resolve()!=out.resolve() and p.name!='DUAL_BACKUP_RECEIPT.json')
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as zf:
        for p in members:
            zi=zipfile.ZipInfo(str(p.relative_to(folder)));zi.date_time=(2026,9,27,0,0,0);zi.external_attr=(0o100644<<16);zi.compress_type=zipfile.ZIP_DEFLATED
            zf.writestr(zi,p.read_bytes())
    os.replace(tmp,out);return sha(out),out.stat().st_size

def target(remote,prefix,name): return remote.rstrip('/')+('' if remote.endswith(':') else '/')+prefix.strip('/')+'/'+name

def maybe_backup(seal,receipt,drive,dropbox,prefix):
    seal=Path(seal);receipt=Path(receipt);s,n=digest(seal)
    if receipt.exists():
        old=json.loads(receipt.read_text())
        if old.get('source_sha256')==s and old.get('source_bytes')==n and old.get('dual_raw_readback_verified') is True:return old
        raise RuntimeError('existing backup receipt does not match seal')
    dest={'google_drive':target(drive,prefix,seal.name),'dropbox':target(dropbox,prefix,seal.name)}
    r=dual_backup(seal,dest,receipt)
    if not r['dual_raw_readback_verified']:raise RuntimeError('node dual backup incomplete')
    return r

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cp4-root',type=Path,required=True);ap.add_argument('--out-root',type=Path,required=True);ap.add_argument('--workers',type=int,default=12);ap.add_argument('--drive',default=os.environ.get('GDRIVE_RCLONE_REMOTE'));ap.add_argument('--dropbox',default=os.environ.get('DROPBOX_RCLONE_REMOTE'));ap.add_argument('--backup-prefix',default='BASS_DERIVATION_DOSSIERS_20260912/WU088_HH_R31N_PROVIDER_FILL');ap.add_argument('--describe',action='store_true');a=ap.parse_args()
    if not 1<=a.workers<=12:ap.error('workers must be 1..12 physical cores')
    cp4=a.cp4_root.resolve();audit=audit_cp4_root(cp4,EXPECTED);plan={'od_z':list(OD_Z),'jvp_z':list(JVP_Z),'workers':a.workers,'parallelism':'PAIR_LEVEL_ONLY','remote_backup_at_node_close':bool(a.drive and a.dropbox)}
    if a.describe: print(json.dumps({'status':'R31N_PROVIDER_FILL_READY','cp4_audit':audit,'plan':plan},indent=2));return 0
    a.out_root.mkdir(parents=True,exist_ok=True);cpus=physical_cpus(a.workers);groups=[[c] for c in cpus];summary={'schema':'WU088_R31N_PROVIDER_FILL_SUMMARY_V1','cp4_sha256':CP4_SHA,'plan':plan,'nodes':[],'production_admitted':False,'trajectory_admitted':False}
    odcost=od_order_costs(cp4)
    for z in OD_Z:
        folder=a.out_root/f'OD192_z{z}';folder.mkdir(parents=True,exist_ok=True);ensure_identity(folder,identity(cp4,'OD192',z));order=order_pairs_by_cost(odcost);tasks=[(i,j,str(folder/f'pair_{i:02}_{j:02}.npz')) for i,j in order if not (folder/f'pair_{i:02}_{j:02}.npz').exists()]
        
        if tasks:
            eff=min(a.workers,len(tasks));rows,wall=run_pool(tasks,eff,init_od,(str(cp4),z,groups[:eff]),folder/'events.jsonl')
        else: rows,wall=[],0.0
        res=assemble_od(folder,cp4,z);res['compute_wall_seconds']=wall
        seal=folder/f'R31N_OD192_z{z}_NODE_SEAL.zip';ss,nb=deterministic_seal(folder,seal);res.update(seal_sha256=ss,seal_bytes=nb)
        if a.drive and a.dropbox:res['backup']=maybe_backup(seal,folder/'DUAL_BACKUP_RECEIPT.json',a.drive,a.dropbox,a.backup_prefix+f'/OD192_z{z}')['status']
        summary['nodes'].append(res)
    cost=jvp_order_costs(cp4)
    for z in JVP_Z:
        folder=a.out_root/f'JVP192_z{z}';folder.mkdir(parents=True,exist_ok=True);ensure_identity(folder,identity(cp4,'JVP192',z));order=order_pairs_by_cost(cost);tasks=[(i,j,str(folder/f'pair_{i:02}_{j:02}.npz')) for i,j in order if not (folder/f'pair_{i:02}_{j:02}.npz').exists()]
        
        if tasks:
            eff=min(a.workers,len(tasks));rows,wall=run_pool(tasks,eff,init_jvp,(str(cp4),z,groups[:eff]),folder/'events.jsonl')
        else: rows,wall=[],0.0
        res=assemble_jvp(folder,cp4,z);res['compute_wall_seconds']=wall
        seal=folder/f'R31N_JVP192_z{z}_NODE_SEAL.zip';ss,nb=deterministic_seal(folder,seal);res.update(seal_sha256=ss,seal_bytes=nb)
        if a.drive and a.dropbox:res['backup']=maybe_backup(seal,folder/'DUAL_BACKUP_RECEIPT.json',a.drive,a.dropbox,a.backup_prefix+f'/JVP192_z{z}')['status']
        summary['nodes'].append(res)
    summary['all_nodes_dual_backed_up']=all(n.get('backup')=='DUAL_RAW_READBACK_VERIFIED' for n in summary['nodes']) if (a.drive and a.dropbox) else False
    summary['status']='R31N_PROVIDER_FILL_COMPLETE_DURABLE' if summary['all_nodes_dual_backed_up'] else 'R31N_PROVIDER_FILL_COMPLETE_LOCAL_ONLY'
    atomic_json(a.out_root/'R31N_PROVIDER_FILL_SUMMARY.json',summary);print(json.dumps(summary,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
