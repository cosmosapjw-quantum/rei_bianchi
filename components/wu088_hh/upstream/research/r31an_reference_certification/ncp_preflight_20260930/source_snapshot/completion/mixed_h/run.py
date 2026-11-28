"""Immutable pair checkpoints and all94 contraction; compiled heavy loops."""
import os
for k in('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,time,json,argparse,resource
sys.dont_write_bytecode=True
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np
from native import Native,grid,HERE,ROOT,LD,CD,sha
STATE=None
def save(path,**arrays):
 if path.exists():raise FileExistsError(path)
 tmp=path.with_suffix('.tmp')
 with tmp.open('wb')as f:np.savez_compressed(f,**arrays);f.flush();os.fsync(f.fileno())
 os.replace(tmp,path)
def init(n,g,z):
 global STATE
 d,t,W,gs,gw=grid(n,g);STATE=(Native(),d,t,W,gs,gw,z)
def pair(task):
 ia,ib,out=task;out=Path(out);native,d,t,W,gs,gw,z=STATE;a=float(d['exponents'][ia]);b=float(d['exponents'][ib]);v=float(d['v']);st=time.perf_counter();cpu=time.process_time()
 H0=[];H0sa=[]
 for active in(0,1):
  vals,ab=native.h0(a,b,t,W,z,v,active);H0.append(vals);H0sa.append(ab)
 foreign,fs=native.foreign(a,b,t,gs,gw,W[0],z,v)
 norm0=np.sqrt(2)*float(d['pref'])*(2*a/np.pi)**.75*(2*b/np.pi)**.75;norm=norm0*np.array([[1,2*np.sqrt(a),2*np.sqrt(a)],[1,2*np.sqrt(b),2*np.sqrt(b)]])
 foreign*=norm[None];fs*=abs(norm[None]);wall=time.perf_counter()-st;cpus=time.process_time()-cpu
 save(out,H0=np.array(H0),H0_sumabs=np.array(H0sa),foreign=foreign,foreign_sumabs=fs,ia=ia,ib=ib,wall_seconds=wall,cpu_seconds=cpus,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
 return {'ia':ia,'ib':ib,'wall_seconds':wall,'cpu_seconds':cpus,'path':str(out.relative_to(ROOT)),'sha256':sha(out)}
def assemble(folder,z):
 d,t,W,gs,gw=grid(int(folder.name.split('_')[0][1:]),int(folder.name.split('_')[1][1:]));h0=np.empty((2,7,3,12,12),CD);hsa=np.empty((2,7,3,12,12),LD);fore=np.empty((2,2,3,12,12),CD);fsa=np.empty((2,2,3,12,12),LD)
 for ia in range(12):
  for ib in range(12):
   with np.load(folder/f'pair_{ia:02}_{ib:02}.npz')as f:h0[...,ia,ib]=f['H0'];hsa[...,ia,ib]=f['H0_sumabs'];fore[...,ia,ib]=f['foreign'];fsa[...,ia,ib]=f['foreign_sumabs']
 reg=[(0,j)for j in range(24)]+[(1,j)for j in range(1,24)];v=LD(d['v']);ks=[v/2,-v/2];tau=LD(z)/v
 components=np.empty((9,47,2),CD);internal=np.empty((9,47,2),LD);orbital=np.empty((9,47,2),LD)
 C0=d['s_C'][:,0].astype(LD)
 for ch,(active,j)in enumerate(reg):
  ang=j//8;coeff=(d['s_C']if ang==0 else d['p_C'])[:,j%8].astype(LD);ab=coeff[:,None]*C0[None,:]
  for c in(0,1):
   act=active^c;par=1 if c==0 or ang==0 else-1;cz=(1 if c==0 else-1)*LD(z)/2
   ph=np.exp(CD(1j)*(2*ks[c]*cz+(LD(d['phase_E'][ch])-LD(d['phase_E'][47+c]))*tau))
   for comp in range(7):
    term=h0[act,comp,ang]*ab;ps=par*(-1 if c and comp in(2,3)else 1)
    components[comp,ch,c]=ph*ps*np.sum(term,dtype=CD);internal[comp,ch,c]=np.sum(hsa[act,comp,ang]*abs(ab),dtype=LD);orbital[comp,ch,c]=np.sum(abs(term),dtype=LD)
   abf=ab if act==0 else ab.T
   for side in(0,1):
    term=fore[side,act,ang]*abf;components[7+side,ch,c]=ph*par*np.sum(term,dtype=CD);internal[7+side,ch,c]=np.sum(fsa[side,act,ang]*abs(abf),dtype=LD);orbital[7+side,ch,c]=np.sum(abs(term),dtype=LD)
 H=components[1]-components[4]-components[5]+components[6]-components[7]-components[8];O=components[0];Dc=np.empty((47,2),CD);Dr=np.empty((2,47),CD)
 for ch,(active,j)in enumerate(reg):
  for c in(0,1):
   kc=ks[c];ka=ks[active];kb=ks[1-active];G1=components[2,ch,c];G2=components[3,ch,c]
   Dc[ch,c]=kc*(G1+G2)+CD(1j)*(kc*(2*kc-ka-kb)-LD(d['phase_E'][47+c]))*O[ch,c]
   Dr[c,ch]=-ka*G1.conj()-kb*G2.conj()-CD(1j)*LD(d['phase_E'][ch])*O[ch,c].conj()
 result=folder/'ASSEMBLED.npz'
 if not result.exists():save(result,H=H,H_row=H.conj().T,O=O,O_row=O.conj().T,D_col=Dc,D_row=Dr,components=components,grid_sumabs=internal,orbital_sumabs=orbital,z=z)
 return {'path':str(result.relative_to(ROOT)),'sha256':sha(result),'max_H':float(abs(H).max()),'max_component_grid_sumabs':float(internal.max()),'H_grid_sumabs_max':float(internal[[1,4,5,6,7,8]].sum(axis=0).max()),'max_orbital_condition':float(np.max(orbital/np.maximum(abs(components),LD('1e-4900'))))}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--n',type=int,required=True);ap.add_argument('--g',type=int,default=80);ap.add_argument('--z',type=float,required=True);ap.add_argument('--workers',type=int,default=4);args=ap.parse_args()
 if args.workers>4:raise ValueError('CPU quota')
 if json.loads((HERE/'PILOT.json').read_text())['status']!='PASS':raise RuntimeError('pilot required')
 folder=HERE/f'B{args.n}_g{args.g}_z{args.z:g}';folder.mkdir(exist_ok=True);init(args.n,args.g,args.z);native,d,t,W,gs,gw,z=STATE
 identity={'n':args.n,'g':args.g,'z':z,'model_sha256':sha(ROOT/'inputs/extracted/WU088_HH_R10_FULL_MIXED_BLOCK_OHD_PARTIAL_20260922_v1/inputs/FROZEN_INPUTS.npz'),'native':native.identity,'driver':sha(__file__),'adapter':sha(HERE/'native.py'),'grid_sha256':{k:__import__('hashlib').sha256(v.tobytes()).hexdigest()for k,v in{'t':t,'W':W,'gs':gs,'gw':gw}.items()},'representations':'canonical inversion + independently checked ETF conjugacy'}
 idpath=folder/'IDENTITY.json'
 if idpath.exists():
  if json.loads(idpath.read_text())!=identity:raise RuntimeError('checkpoint identity mismatch')
 else:idpath.write_text(json.dumps(identity,indent=2))
 tasks=[(ia,ib,str(folder/f'pair_{ia:02}_{ib:02}.npz'))for ia in range(12)for ib in range(12)if not(folder/f'pair_{ia:02}_{ib:02}.npz').exists()];st=time.perf_counter();print(json.dumps({'start':str(folder),'tasks':len(tasks),'workers':args.workers}),flush=True)
 with ProcessPoolExecutor(max_workers=args.workers,initializer=init,initargs=(args.n,args.g,args.z))as pool:
  futures=[pool.submit(pair,task)for task in tasks]
  for idx,f in enumerate(as_completed(futures),1):
   row=f.result();row['completed_this_run']=idx;row['elapsed_wall_seconds']=time.perf_counter()-st
   with(folder/'events.jsonl').open('a')as out:out.write(json.dumps(row)+'\n')
   print(json.dumps(row),flush=True)
 result=assemble(folder,args.z);result['wall_seconds']=time.perf_counter()-st;(folder/'RESULTS.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
if __name__=='__main__':main()
