"""Independent analytic mixed overlap derivative, immutable pair checkpoints."""
import os,sys,time,json,argparse
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from native import Native,HERE,ROOT,LD,CD,sha
import numpy as np
REG=[(0,j)for j in range(24)]+[(1,j)for j in range(1,24)]
def grid(n):
 p=ROOT/f'cont2c/convergence/frozen_grid_n{n}.npz'
 if not p.exists():raise ValueError('Use the exact frozen grid file for this version: '+str(p))
 with np.load(p,allow_pickle=False)as f:d={k:f[k]for k in f.files}
 return d,p
def save(path,**arrays):
 if path.exists():raise FileExistsError(path)
 tmp=path.with_suffix('.tmp')
 with tmp.open('wb')as f:np.savez_compressed(f,**arrays);f.flush();os.fsync(f.fileno())
 os.replace(tmp,path)
def assemble(raw,d,z):
 # raw[electron, O_or_zJVP, angle, canonical_a, canonical_b]. Remote
 # active primitive changes exponent order; no matrix averaging is performed.
 v=LD(d['v']);tau=LD(z)/v;O=np.empty((47,2),CD);dot=np.empty((47,2),CD)
 for ch,(active,j)in enumerate(REG):
  angle=j//8;coeff=(d['s_C']if angle==0 else d['p_C'])[:,j%8].astype(LD);ground=d['s_C'][:,0].astype(LD);ab=coeff[:,None]*ground[None,:]
  for cusp in (0,1):
   canonical_active=active^cusp;tab=raw[canonical_active,:,angle]
   if canonical_active:tab=tab.transpose(0,2,1)
   pair=np.sum(tab*ab[None],axis=(1,2),dtype=CD)
   parity=-1 if cusp and angle else 1
   deltaE=LD(d['phase_E'][ch])-LD(d['phase_E'][47+cusp]);phase=np.exp(CD(1j)*(v*LD(z)/2+deltaE*tau))
   O[ch,cusp]=parity*phase*pair[0]
   dot[ch,cusp]=parity*phase*(v*pair[1]+CD(1j)*(v*v/2+deltaE)*pair[0])
 return O,dot
def evaluate(z,n=192):
 z=LD(z);d,gpath=grid(n);native=Native();folder=HERE/f'B{n}_z{z:g}';folder.mkdir(exist_ok=True)
 identity={'z':str(z),'n':n,'grid':sha(gpath),'native':native.identity,'driver':sha(__file__),'contract':sha(HERE/'CONTRACT.json')}
 ip=folder/'IDENTITY.json'
 if ip.exists():
  if json.loads(ip.read_text())!=identity:raise RuntimeError('checkpoint source mismatch')
 else:ip.write_text(json.dumps(identity,indent=2)+'\n')
 raw=np.empty((2,2,3,12,12),CD);sumabs=np.empty(raw.shape,LD);start=time.perf_counter();cpu=time.process_time();rows=[]
 for ia,a in enumerate(d['exponents']):
  for ib,b in enumerate(d['exponents']):
   path=folder/f'pair_{ia:02}_{ib:02}.npz'
   if path.exists():
    with np.load(path,allow_pickle=False)as f:out=f['out'];sa=f['sumabs'];seconds=float(f['seconds'])
   else:
    tick=time.perf_counter();out,sa=native.pair(a,b,d['t'],d['W'],z,LD(d['v']),d['pref']);seconds=time.perf_counter()-tick
    save(path,out=out,sumabs=sa,seconds=seconds)
   raw[...,ia,ib]=out;sumabs[...,ia,ib]=sa;rows.append(seconds)
  print(json.dumps({'z':str(z),'row':ia,'elapsed':time.perf_counter()-start}),flush=True)
 O,dot=assemble(raw,d,z);path=folder/'ASSEMBLED.npz'
 if not path.exists():save(path,O=O,dotO=dot,raw=raw,sumabs=sumabs,z=z)
 result={'status':'COMPUTED_INDEPENDENT_DERIVATIVE','path':str(path.relative_to(ROOT)),'sha256':sha(path),'wall_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu,'primitive_seconds':sum(rows),'identity':identity}
 (folder/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
 return O,dot,result
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--z',type=str,nargs='+',required=True);ap.add_argument('--n',type=int,default=192);args=ap.parse_args()
 if json.loads((HERE/'PILOT.json').read_text())['status']!='PASS':raise RuntimeError('pilot not passed')
 for z in args.z:print(json.dumps(evaluate(z,args.n)[2]),flush=True)
if __name__=='__main__':main()
