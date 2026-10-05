"""Production-free MPFI200 first-order implicit-stage checker, no Rust evaluator."""
import importlib.util,json,math,struct
from pathlib import Path
from sage.all import RealIntervalField,matrix,vector
R=RealIntervalField(200)
s=importlib.util.spec_from_file_location('frozen_actual_nonphoto','docs/atomic_reionization_handoff_20261004_v1/runtime_returns/evidence/F04_certificate/checker.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class AD:
 def __init__(self,value,index=None,g=None):
  self.v=R(value);self.g=vector(R,4) if g is None else g
  if index is not None and index<4:self.g[index]=R(1)
 def __add__(self,b):
  b=b if isinstance(b,AD) else AD(b);return AD(self.v+b.v,g=self.g+b.g)
 __radd__=__add__
 def __neg__(self):return AD(-self.v,g=-self.g)
 def __sub__(self,b):return self+-(b if isinstance(b,AD) else AD(b))
 def __rsub__(self,b):return AD(b)-self
 def __mul__(self,b):
  b=b if isinstance(b,AD) else AD(b);return AD(self.v*b.v,g=self.g*b.v+b.g*self.v)
 __rmul__=__mul__
 def __truediv__(self,b):
  b=b if isinstance(b,AD) else AD(b);assert not(b.v.lower()<=0<=b.v.upper());return self*AD(1/b.v,g=-b.g/(b.v*b.v))
 def __rtruediv__(self,b):return AD(b)/self
 def power(self,p):
  p=R(float(p));assert self.v.lower()>0;v=(p*self.v.log()).exp();return AD(v,g=p*v/self.v*self.g)
 def exp(self):
  v=self.v.exp();return AD(v,g=v*self.g)
 def log(self):
  assert self.v.lower()>0;return AD(self.v.log(),g=self.g/self.v)
manifest=json.loads(Path('runs/rei_fastest_v1/map_certificate/parent_manifest.json').read_text());constants=json.loads(Path('docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/ft03_map_constants.json').read_text())
class Model(m.Model):
 def __init__(self,nh,fhe,hmean,energies,sigma,dt):
  super().__init__(manifest,constants);self.nh=R(float(nh));self.nhe=R(float(float(nh)*float(fhe)));self.fhe=self.nhe/self.nh;self.photo_fhe=R(float(fhe));self.hmean=R(float(hmean));self.energy_nodes=[R(float(e)) for e in energies];self.sig=[[R(float(v)) for v in row] for row in sigma];self.dt=R(float(dt));self.sigma=[[R(0)]*3 for _ in range(3)]
 def coupled(self,gas,pi):
  yy=list(gas)+[R(1)]*3;f=super().rhs(yy)[:4];y=[AD(v,index=i) for i,v in enumerate(yy)];l=[1-y[0],self.photo_fhe*(1-y[1]-y[2]),self.photo_fhe*y[1]];out=[]
  for k in range(len(pi)):
   opacity=self.c*self.nh*sum((l[a]*self.sig[k][a] for a in range(3)),AD(0));pn=AD(pi[k])/(1+self.dt*opacity);out.append(pn)
   rates=[self.c*self.nh*l[a]*self.sig[k][a]*pn for a in range(3)]
   f[0]+=rates[0];f[1]+=(rates[1]-rates[2])/self.photo_fhe;f[2]+=rates[2]/self.photo_fhe
   for a in range(3):f[3]+=rates[a]*(self.energy_nodes[k]-self.chi[a])
  f[3]-=R(2)*self.hmean*y[3];return f,out

def certify(nh,fhe,hmean,energies,sigma,dt,parent_gas,parent_photons,centre,gas,C,photons):
 old=m.J;m.J=AD
 try:
  model=Model(nh,fhe,hmean,energies,sigma,dt);P=[R(float(a),float(b)) for a,b in parent_gas];Pi=[R(float(a),float(b)) for a,b in parent_photons];Y=[R(float(a),float(b)) for a,b in gas];y=vector(R,[R(float(v)) for v in centre]);c=matrix(R,[[R(float(v)) for v in row] for row in C])
  assert all(Y[i].lower()<=y[i].lower() and y[i].upper()<=Y[i].upper() for i in range(4)),'CENTRE_IN_Y'
  F0,_=model.coupled(y,Pi);F,pn=model.coupled(Y,Pi);I=matrix.identity(R,4);B=I-c*(I-R(float(dt))*matrix(R,[[f.g[j] for j in range(4)] for f in F]));K=y-c*(y-vector(R,P)-R(float(dt))*vector(R,[f.v for f in F0]))+B*(vector(R,Y)-y)
  assert all(Y[i].lower()<K[i].lower() and K[i].upper()<Y[i].upper() for i in range(4)),'UNIFORM_K4'
  q=max(sum(R(m.absmax(B[i,j])) for j in range(4)).upper() for i in range(4));assert q<1,'UNIFORM_Q'
  t=model.temperature([AD(v) for v in list(Y)+[R(1)]*3]).v;assert t.lower()>=35000 and t.upper()<=60000,'S0_T_BOX'
  for k,ph in enumerate(pn):
   a,b=photons[k];assert R(float(a)).lower()<=max(R(0).lower(),ph.v.lower()) and ph.v.upper()<=R(float(b)).upper(),'OUTGOING_PHOTON_BOX'
  return {'q':m.upper(q),'temperature':[float(t.lower()),float(t.upper())],'K':[m.enc(v) for v in K]}
 finally:m.J=old

if __name__=='__main__':
 p=Path('.cuh/fastest-track/REI-F08-STAGE');f=json.loads((p/'fixture.json').read_text());d=json.loads((p/'root_data.json').read_text());sigma=[[m.bits(f['sigma_bits'][3*a+k]) for a in range(3)] for k in range(3)]
 r=certify(f['stage']['n_h_cm3'],f['stage']['f_he'],f['stage']['h_mean_per_s'],f['energies_ev'],sigma,f['dt_s'],d['parent_gas'],d['parent_photons'],d['centre'],d['gas'],d['C'],d['photons']);print(json.dumps({'status':'PASS','scope':'First-order checker qualification against fixed independently checked conditional fixture','result':r,'production_evaluator_called':False}))
