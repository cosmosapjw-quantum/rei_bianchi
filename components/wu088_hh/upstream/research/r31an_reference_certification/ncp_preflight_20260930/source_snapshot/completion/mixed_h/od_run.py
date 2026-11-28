"""Separate fine-order O/D only; deliberately exports no Hamiltonian."""
import os
for k in('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,time,argparse
sys.dont_write_bytecode=True
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np
from native import HERE,ROOT,grid,LD,CD,sha
from h0_backend import H0Fused
from run import save
WORK=None
def init(n,z):
 global WORK
 d,t,W,_,_=grid(n);WORK=(H0Fused(),d,t,W,z)
def calc(task):
 ia,ib,path=task;h,d,t,W,z=WORK;a=float(d['exponents'][ia]);b=float(d['exponents'][ib]);rows=[];absolute=[];st=time.perf_counter()
 for active in(0,1):
  values,sa=h.h0(a,b,t,W,z,float(d['v']),active);rows.append(values[[0,2,3]]);absolute.append(sa[[0,2,3]])
 save(__import__('pathlib').Path(path),OG=np.array(rows),sumabs_upper_diagnostic=np.array(absolute),ia=ia,ib=ib,wall_seconds=time.perf_counter()-st)
 return {'ia':ia,'ib':ib,'wall_seconds':time.perf_counter()-st,'sha256':sha(path)}
def assemble(folder,n,z):
 d,*_=grid(n);raw=np.empty((2,3,3,12,12),CD);sa=np.empty(raw.shape,LD)
 for ia in range(12):
  for ib in range(12):
   with np.load(folder/f'pair_{ia:02}_{ib:02}.npz')as f:raw[...,ia,ib]=f['OG'];sa[...,ia,ib]=f['sumabs_upper_diagnostic']
 v=LD(d['v']);ks=[v/2,-v/2];tau=LD(z)/v;reg=[(0,j)for j in range(24)]+[(1,j)for j in range(1,24)];out=np.empty((3,47,2),CD);summed=np.empty((3,47,2),LD);C0=d['s_C'][:,0].astype(LD)
 for ch,(active,j)in enumerate(reg):
  ang=j//8;C=(d['s_C']if ang==0 else d['p_C'])[:,j%8].astype(LD);coeff=C[:,None]*C0[None,:]
  for c in(0,1):
   act=active^c;par=1 if c==0 or ang==0 else-1;cz=(1 if c==0 else-1)*LD(z)/2;phase=np.exp(CD(1j)*(2*ks[c]*cz+(LD(d['phase_E'][ch])-LD(d['phase_E'][47+c]))*tau))
   for field in(0,1,2):
    parity=par*(-1 if c and field else 1);out[field,ch,c]=phase*parity*np.sum(raw[act,field,ang]*coeff,dtype=CD);summed[field,ch,c]=np.sum(sa[act,field,ang]*abs(coeff),dtype=LD)
 O=out[0];Dc=np.empty((47,2),CD);Dr=np.empty((2,47),CD)
 for ch,(active,j)in enumerate(reg):
  for c in(0,1):
   kc=ks[c];ka=ks[active];kb=ks[1-active];G1=out[1,ch,c];G2=out[2,ch,c];Dc[ch,c]=kc*(G1+G2)+CD(1j)*(kc*(2*kc-ka-kb)-LD(d['phase_E'][47+c]))*O[ch,c];Dr[c,ch]=-ka*G1.conj()-kb*G2.conj()-CD(1j)*LD(d['phase_E'][ch])*O[ch,c].conj()
 path=folder/'ASSEMBLED_OD.npz'
 if not path.exists():save(path,O=O,O_row=O.conj().T,D_col=Dc,D_row=Dr,components_OG=out,sumabs_upper_diagnostic=summed,n=n,z=z)
 return {'status':'COMPUTED_FINE_OD_NOT_INDEPENDENT_DOT_O','path':str(path.relative_to(ROOT)),'sha256':sha(path),'n':n,'z':z,'fields':['O','O_row','D_col','D_row'],'Hamiltonian_included':False,'independent_dotO_included':False}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--n',type=int,default=192);ap.add_argument('--z',type=float,required=True);ap.add_argument('--workers',type=int,default=1);args=ap.parse_args()
 if not 1<=args.workers<=8:raise ValueError('CPU allocation')
 folder=HERE/'od'/f'B{args.n}_z{args.z:g}';folder.mkdir(parents=True,exist_ok=True);h=H0Fused();d,t,W,_,_=grid(args.n);ident={'source_identity':h.identity,'driver_sha256':sha(__file__),'model_sha256':sha(ROOT/'inputs/extracted/WU088_HH_R10_FULL_MIXED_BLOCK_OHD_PARTIAL_20260922_v1/inputs/FROZEN_INPUTS.npz'),'n':args.n,'z':args.z,'t_sha256':__import__('hashlib').sha256(t.tobytes()).hexdigest(),'W_sha256':__import__('hashlib').sha256(W.tobytes()).hexdigest(),'scope':'O/D only; paired independent dotO must use same declared quadrature'};ip=folder/'IDENTITY.json'
 if ip.exists()and json.loads(ip.read_text())!=ident:raise RuntimeError('OD source identity')
 if not ip.exists():ip.write_text(json.dumps(ident,indent=2))
 tasks=[(ia,ib,str(folder/f'pair_{ia:02}_{ib:02}.npz'))for ia in range(12)for ib in range(12)if not(folder/f'pair_{ia:02}_{ib:02}.npz').exists()];st=time.perf_counter()
 with ProcessPoolExecutor(max_workers=args.workers,initializer=init,initargs=(args.n,args.z))as pool:
  for future in as_completed([pool.submit(calc,t)for t in tasks]):
   row=future.result();row['elapsed_wall_seconds']=time.perf_counter()-st
   with(folder/'events.jsonl').open('a')as f:f.write(json.dumps(row)+'\n')
   print(json.dumps(row),flush=True)
 result=assemble(folder,args.n,args.z);result['wall_seconds']=time.perf_counter()-st;(folder/'RESULTS.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
if __name__=='__main__':main()
