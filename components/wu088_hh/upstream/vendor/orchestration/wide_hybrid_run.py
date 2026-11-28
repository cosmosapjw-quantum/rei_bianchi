"""R31 checkpointed complete wide-H producer using the R30-admitted hybrid12 candidate.

This computes H source artifacts only. It does not admit a full matrix or run propagation.
Completed pair checkpoints are source-bound and reused exactly on resume.
"""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
import sys,json,time,argparse,resource,hashlib,struct,math,fcntl,ctypes
sys.dont_write_bytecode=True
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
MIXED=ROOT/'completion/mixed_h'
sys.path.insert(0,str(MIXED))
from native import grid,sha,LD,CD,DP,LP
from wide_reference import WideReference
from run import save,assemble
STATE=None

def provider_gate():
    r=json.loads((HERE/'RESULT.json').read_text()); q=json.loads((HERE/'INDEPENDENT_REVIEW.json').read_text())
    if not r['status'].startswith('PASS_SCOPED_H_LEVEL_ACCURACY_AND_COST') or q['status']!='PASS_SCOPED_H_LEVEL_ACCURACY_AND_COST':
        raise RuntimeError('R30 provider gate not closed')
    return {'R30_result_sha256':sha(HERE/'RESULT.json'),'R30_review_sha256':sha(HERE/'INDEPENDENT_REVIEW.json'),'R30_contract_sha256':sha(HERE/'CONTRACT.json'),'R30_binary_sha256':sha(HERE/'hybrid12_wide_h.so')}

class Hybrid12:
    def __init__(self):
        self.ref=WideReference()
        self.lib=ctypes.CDLL(str(HERE/'hybrid12_wide_h.so'))
        self.fn=self.lib.mh_wide_foreign
        self.fn.argtypes=[ctypes.c_size_t,ctypes.c_size_t,DP,DP,DP,DP,DP,LP,LP]; self.fn.restype=ctypes.c_int
        self.identity={'reference':self.ref.identity,'candidate_binary_sha256':sha(HERE/'hybrid12_wide_h.so'),'candidate_source_sha256':sha(HERE/'hybrid12_wide_h_v2.cpp'),'continuation_sha256':sha(HERE/'continuation.hpp'),**provider_gate()}
    def h0(self,*args,**kwargs): return self.ref.h0(*args,**kwargs)
    def foreign(self,a,b,t,gs,gw,W,z,q):
        arrays=[np.ascontiguousarray(x,dtype=np.float64) for x in (t,gs,gw,W,np.array([a,b,z,q],dtype=np.float64))]
        if arrays[3].shape!=(9,len(t),len(t)) or gs.shape!=gw.shape: raise ValueError('shape')
        if not all(np.isfinite(x).all() for x in arrays) or np.any(t<=0) or np.any(gs<0): raise ValueError('domain')
        out=np.empty((2,2,3),CD); sa=np.empty((2,2,3),LD)
        rc=self.fn(len(t),len(gs),*[x.ctypes.data_as(DP) for x in arrays],out.ctypes.data_as(LP),sa.ctypes.data_as(LP))
        if rc: raise RuntimeError('hybrid12 native status '+str(rc))
        if not np.isfinite(out).all() or not np.isfinite(sa).all(): raise FloatingPointError('nonfinite')
        return out,sa

def folder_for(n,g,z,scale='unit'):
    z=float(z)
    if not math.isfinite(z) or abs(z)>64 or scale not in ('unit','R'): raise ValueError('wide geometry/scale')
    return MIXED/'wide_hybrid12'/f'B{n}_g{g}_s{scale}_z{struct.pack(">d",z).hex()}'

def configuration(n,g,z,scale):
    d,t,W,gs,gw=grid(n,g); length=math.hypot(2,z) if scale=='R' else 1.
    return d,t,W,gs/length,gw/length,length

def init(n,g,z,scale):
    global STATE
    STATE=(Hybrid12(),*configuration(n,g,z,scale),z)

def pair(task):
    ia,ib,path=task; h,d,t,W,gs,gw,length,z=STATE; a=float(d['exponents'][ia]); b=float(d['exponents'][ib]); q=float(d['v'])
    start=time.perf_counter();cpu=time.process_time();H0=[];H0sa=[]
    for active in (0,1):
        val,sa=h.h0(a,b,t,W,z,q,active);H0.append(val);H0sa.append(sa)
    foreign,fa=h.foreign(a,b,t,gs,gw,W[0],z,q)
    norm0=np.sqrt(2)*float(d['pref'])*(2*a/np.pi)**.75*(2*b/np.pi)**.75
    norm=norm0*np.array([[1,2*np.sqrt(a),2*np.sqrt(a)],[1,2*np.sqrt(b),2*np.sqrt(b)]])
    foreign*=norm[None];fa*=abs(norm[None])
    timing={'wall_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    save(Path(path),H0=np.array(H0),H0_sumabs=np.array(H0sa),foreign=foreign,foreign_sumabs=fa,ia=ia,ib=ib,**timing)
    return {'ia':ia,'ib':ib,'path':str(Path(path).relative_to(ROOT)),'sha256':sha(path),**timing}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--n',type=int,choices=(160,192),required=True);ap.add_argument('--g',type=int,default=80);ap.add_argument('--z',type=float,required=True);ap.add_argument('--gamma-scale',choices=('unit','R'),default='unit');ap.add_argument('--workers',type=int,default=8);ap.add_argument('--describe',action='store_true');a=ap.parse_args()
    if not 1<=a.workers<=8 or not 1<=a.g<=192: raise ValueError('worker/gamma limit')
    provider_gate();folder=folder_for(a.n,a.g,a.z,a.gamma_scale)
    if a.describe:
        print(json.dumps({'status':'READY_NOT_STARTED','folder':str(folder.relative_to(ROOT)),'n':a.n,'g':a.g,'z':a.z,'z_hex':float(a.z).hex(),'gamma_scale':a.gamma_scale,'workers':a.workers,'provider_gate':provider_gate()},indent=2));return
    folder.mkdir(parents=True,exist_ok=True)
    with (folder/'RUN.lock').open('a') as lock:
        fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
        h=Hybrid12();d,t,W,gs,gw,length=configuration(a.n,a.g,a.z,a.gamma_scale); ah=lambda x:hashlib.sha256(x.tobytes()).hexdigest()
        identity={'producer':'wide_hybrid12_R30_v1','n':a.n,'g':a.g,'z':float(a.z),'z_hex':float(a.z).hex(),'gamma_scale':a.gamma_scale,'gamma_scale_length':length,'model_sha256':sha(ROOT/'inputs/extracted/WU088_HH_R10_FULL_MIXED_BLOCK_OHD_PARTIAL_20260922_v1/inputs/FROZEN_INPUTS.npz'),'native':h.identity,'driver':sha(__file__),'assembler':sha(MIXED/'run.py'),'grid_source':sha(MIXED/'native.py'),'weights_source':sha(ROOT/'exact_weights/exact_laplace_weights.py'),'grid_sha256':{k:ah(v) for k,v in dict(t=t,W=W,gs=gs,gw=gw).items()},'sumabs_semantics':'triangle/L1 upper diagnostic, no outward rounding','claim_ceiling':'H source computation only; requires B160/B192 convergence and later O/D/JVP/ionic full-matrix admission.'}
        ip=folder/'IDENTITY.json'
        if ip.exists() and json.loads(ip.read_text())!=identity: raise RuntimeError('checkpoint source/grid/geometry changed')
        if not ip.exists(): ip.write_text(json.dumps(identity,indent=2)+'\n')
        events=folder/'events.jsonl';old={}
        if events.exists():
            for line in events.read_text().splitlines():
                row=json.loads(line)
                if 'ia' in row: old[(row['ia'],row['ib'])]=row['sha256']
        tasks=[]
        for ia in range(12):
            for ib in range(12):
                p=folder/f'pair_{ia:02}_{ib:02}.npz'
                if p.exists():
                    if old.get((ia,ib))!=sha(p): raise RuntimeError('uncommitted or changed pair checkpoint: '+str(p))
                else: tasks.append((ia,ib,str(p)))
        start=time.perf_counter();print(json.dumps({'start':str(folder.relative_to(ROOT)),'pending_pairs':len(tasks),'workers':a.workers}),flush=True)
        with ProcessPoolExecutor(max_workers=a.workers,initializer=init,initargs=(a.n,a.g,a.z,a.gamma_scale)) as pool:
            for k,f in enumerate(as_completed([pool.submit(pair,x) for x in tasks]),1):
                row=f.result();row.update(completed_this_run=k,elapsed_wall_seconds=time.perf_counter()-start)
                with events.open('a') as log:log.write(json.dumps(row)+'\n');log.flush();os.fsync(log.fileno())
                print(json.dumps(row),flush=True)
        result=assemble(folder,a.z);result.update(status='COMPUTED_WIDE_HYBRID12_H_NOT_ADMITTED',producer='wide_hybrid12_R30_v1',n=a.n,g=a.g,z=float(a.z),z_hex=float(a.z).hex(),gamma_scale=a.gamma_scale,wall_seconds_this_invocation=time.perf_counter()-start,identity_sha256=sha(ip),quadrature_admitted=False,trajectory_admitted=False)
        rp=folder/'RESULTS.json'
        if rp.exists():
            saved=json.loads(rp.read_text())
            if saved['sha256']!=result['sha256'] or saved['identity_sha256']!=result['identity_sha256']: raise RuntimeError('completed result changed')
        else: rp.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result),flush=True)
if __name__=='__main__':main()
