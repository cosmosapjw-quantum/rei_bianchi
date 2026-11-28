"""Exact fixed-geometry stock/tr/depth DG pair-flux JVP on source-owned native snapshots."""
from pathlib import Path
import numpy as np,json,hashlib,ctypes as ct,subprocess,tarfile,time,os
D=Path(__file__).resolve().parent;P=D.parent;SH=Path.home()/'r118c4n_rei_shadow'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2,allow_nan=False)+'\n')
def build():
 arc=P/'r118c4f_external_stress/NATIVE_SHADOW_SOURCE.tar.gz';meta=json.loads((arc.parent/'SHADOW_ARCHIVE.json').read_text());assert sha(arc.read_bytes())==meta['archive_sha256']
 with tarfile.open(arc) as t:raw=t.extractfile('bridge/dg_rhs.cpp').read()
 s=raw.decode();a='double* outN,double* outV,double* diag)';assert s.count(a)==1
 q=s.replace('int dg_rhs(','int dg_jvp(').replace(a,'double* outN,double* outV,double* diag,const double* dA,const double* dB,double dtr)')
 old='long double F=(long double)C*((long double)di-dj-std::expm1(dg)*((long double)dj*(1+ri)+(long double)rj*di+(long double)di*dj));'
 assert q.count(old)==1
 q=q.replace(old,'''long double ddi=ri*(dA[i*nc+a]+dB[i*nc+a]*(q-cc[a])/hh[a]),ddj=rj*(dA[j*nc+b]+dB[j*nc+b]*(qp-cc[b])/hh[b]);
     long double ddg=-(long double)dg*dtr/tr;
     long double v1=x*x*x,v2=xp*xp*xp*std::exp(-dg);
     long double dC=(v2<v1 || (v2==v1 && ddg>0))?-(long double)C*ddg:0;
     long double Q=(long double)dj*(1+ri)+(long double)rj*di+(long double)di*dj;
     long double dQ=ddj*(1+ri+di)+ddi*(rj+dj);
     long double F=dC*((long double)di-dj-std::expm1(dg)*Q)+(long double)C*(ddi-ddj-std::exp(dg)*ddg*Q-std::expm1(dg)*dQ);''')
 (D/'original_dg_rhs.cpp').write_bytes(raw);(D/'dg_jvp.cpp').write_text(q)
 p=D/'dg_pair.so';cmd=['g++','-O3','-std=c++17','-fopenmp','-fPIC','-shared',str(D/'original_dg_rhs.cpp'),str(D/'dg_jvp.cpp'),'-o',str(p)]
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=120);(D/'dg_build.log').write_text(r.stdout+r.stderr);assert r.returncode==0
 write('DG_BUILD.json',dict(command=cmd,exit=r.returncode,source_sha=sha(raw),jvp_sha=sha(q.encode()),binary_sha=sha(p.read_bytes()),compiler=subprocess.check_output(['g++','--version'],text=True).splitlines()[0]))
def read(tag,i):
 path=D/f'{tag}_dg_{i}.txt';a={}
 for l in path.read_text().splitlines():
  k,v=l.split(' ',1);a[k]=np.fromstring(v,sep=' ')
 return a,sha(path.read_bytes())
def main():
 build();lib=ct.CDLL(str(D/'dg_pair.so'));ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS');types=[ct.c_int,ct.c_int]+[ptr]*7+[ct.c_double]*4+[ct.c_int,ptr,ptr,ct.c_int,ptr,ptr,ptr,ptr,ptr]
 for n in ['dg_rhs','dg_jvp']:
  fn=getattr(lib,n);fn.restype=ct.c_int;fn.argtypes=types+([ptr,ptr,ct.c_double] if n=='dg_jvp' else [])
 def eval(a,A=None,B=None,tr=None,dA=None,dB=None,dtr=None):
  m=a['meta'];nr,nc=map(int,m[:2]);o=np.zeros(nr*nc);v=o.copy();diag=np.zeros(6)
  args=[nr,nc,*[a[k] for k in ['e','d','n','w','w0']],a['A'] if A is None else A,a['B'] if B is None else B,*m[2:5],m[5] if tr is None else tr,len(a['zh']),a['zh'],a['wh'],len(a['zl']),a['zl'],a['wl'],o,v,diag]
  if dA is None:rc=lib.dg_rhs(*args)
  else:rc=lib.dg_jvp(*args,dA,dB,dtr)
  assert rc==0,(rc,diag);return np.stack([o,v]),diag
 rows=[];arrays={}
 for i in [0,22]:
  a,sha0=read('base',i);p,sp=read('H+0.003',i);m,sm=read('H-0.003',i);h=.003;ma=a['meta'];nr,nc=map(int,ma[:2]);depth=ma[6];dA=(p['A']-m['A'])/(2*h);dB=(p['B']-m['B'])/(2*h);dtr=(p['meta'][5]-m['meta'][5])/(2*h);dd=(p['meta'][6]-m['meta'][6])/(2*h)
  R,diag=eval(a);expected=np.stack([a['rhsN'],a['rhsV']]);gap=np.linalg.norm(R-expected)/max(np.linalg.norm(expected),1e-300);assert gap<1e-12
  dR,dg=eval(a,dA=dA,dB=dB,dtr=dtr);dI=depth*dR+dd*R
  c=(a['e'][:-1]+a['e'][1:])/2;dc=np.tile(c,nr);d=np.repeat(a['d'],nc);cap=ma[7];kt=8.617333262145e-5*2.7255/ma[8]
  def moments(z):
   n=cap*z[0].sum();u=(z[1]+dc*z[0])*d*cap*kt;P=np.einsum('i,ij,ik->jk',u.reshape(nr,nc).sum(1),a['n'].reshape(nr,3),a['n'].reshape(nr,3));return n,float(u.sum()),P
  num,en,pr=moments(dI);nr0=float(abs(num)/max(np.linalg.norm(dI[0],1)*cap,1e-300));er0=float(abs(en)/max(np.linalg.norm((dI[1]+dc*dI[0])*d,1)*cap*kt,1e-300))
  tests=[]
  for eps in [.01,.003,.001]:
   pp,dp=eval(a,A=a['A']+eps*dA,B=a['B']+eps*dB,tr=ma[5]+eps*dtr);mm,dm=eval(a,A=a['A']-eps*dA,B=a['B']-eps*dB,tr=ma[5]-eps*dtr)
   fd=((depth+eps*dd)*pp-(depth-eps*dd)*mm)/(2*eps)
   fn,fe,fp=moments(fd)
   tests.append(dict(eps=eps,jvp_relative=float(np.linalg.norm(fd-dI)/max(np.linalg.norm(dI),1e-300)),pressure_relative=float(np.linalg.norm(fp-pr)/max(np.linalg.norm(pr),1e-300)),number=float(fn),energy=float(fe)))
  # Actual total path secant differs from fixed geometry/theta derivative; quantify the omitted terms.
  full=(p['meta'][6]*np.stack([p['rhsN'],p['rhsV']])-m['meta'][6]*np.stack([m['rhsN'],m['rhsV']]))/(2*h)
  rows.append(dict(collision=i,native_rhs_relative=float(gap),native_diag=diag.tolist(),derivative_diag=dg.tolist(),dA_norm=float(np.linalg.norm(dA)),dB_norm=float(np.linalg.norm(dB)),dtr=float(dtr),ddepth=float(dd),derivative_norm=float(np.linalg.norm(dI)),number_relative=nr0,energy_relative=er0,pressure_derivative=pr.tolist(),pressure_trace=float(np.trace(pr)),physical_number_derivative=float(num),physical_energy_derivative=en,tests=tests,full_native_secant_relative_gap=float(np.linalg.norm(full-dI)/max(np.linalg.norm(full),1e-300)),geometry_direction_norm=float(np.linalg.norm((p['d']-m['d'])/(2*h))),theta_direction=float((p['meta'][4]-m['meta'][4])/(2*h)),source_sha=[sha0,sp,sm]))
  arrays[f'base_rhs_{i}']=R;arrays[f'd_rhs_{i}']=dR;arrays[f'd_increment_{i}']=dI;arrays[f'full_secant_{i}']=full;print(rows[-1],flush=True)
 np.savez_compressed(D/'DG_JVP.npz',**arrays);write('DG_JVP.json',dict(rows=rows,scope='Actual source-owned native DG collision calls, exact local fixed geometry and theta stock/tr/depth JVP. Native signed path secant includes geometry/theta; not full stock/cooling/geometry chain derivative. Conservation measured on local correction only.'))
if __name__=='__main__':main()
