"""Source compression control only: frozen E/gas absorption, not EoR/native evolution."""
from pathlib import Path
import sys,json,numpy as np
P=Path(__file__).resolve().parents[1];sys.path[:0]=[str(P/'src'),str(P.parent/'he25_proper_birth_20261016/src')]
from sourcecut import SourceCutModel
from physics import sigma_cm2,shape,Y_HE,BIND_EV,C_CM_S,A_BIRTH

def features(E,age,nh):
 sig=sigma_cm2(E);lam=C_CM_S*nh*sig*np.array([1-1e-5,Y_HE*(1-1e-5),Y_HE*1e-5]);total=lam.sum(1)
 surv=np.exp(-total*age);loss=-np.expm1(-total*age)
 events=loss[:,None]*np.divide(lam,total[:,None],out=np.zeros_like(lam),where=total[:,None]>0)
 return np.c_[surv,E*surv,events,events*(E[:,None]-BIND_EV)]

def reference(age,nh,order):
 z,w=np.polynomial.legendre.leggauss(order);E=[];W=[]
 for lo,hi in zip([13.6,24.59,54.42],[24.59,54.42,100.]):
  E.extend((lo+hi)/2+(hi-lo)/2*z);W.extend((hi-lo)/2*w)
 E=np.array(E);W=np.array(W)*shape(E);return W@features(E,age,nh)/W.sum()
rows=[]
for m in [4,8,16]:
 model=SourceCutModel(None,m=m,angles=4,q=0.)
 for f in [.1,.37,.9]:
  t=f*model.t_end;x=model.x(t);nh=1.89819845071402689e-7/(A_BIRTH*np.exp(x))**3
  raw,r=model.source_moments(t);E=model.geometry(t)[0]
  for age in [1e10,1e11]:
   ref=reference(age,nh,128);check=reference(age,nh,256);assert max(abs(ref-check))<2e-13
   actual=raw@features(E,age,nh)/raw.sum()
   rows.append({'m':m,'time_fraction':f,'frozen_age_s':age,'reference':ref.tolist(),'admitted':actual.tolist(),'abs_defect':abs(actual-ref).tolist()})
out={'scope':'SOURCE_ONLY_FROZEN_FUTURE_KERNEL, no work/no dynamical gas/no EoR claim','features':['survival','surviving_energy_eV','HI_event','HeI_event','HeII_event','HI_heat_eV','HeI_heat_eV','HeII_heat_eV'],'cases':rows,'interpretation':'Exact eight birth moments do not imply exact future attenuation; fixed-K cubature remains a finite spectral approximation.'}
p=Path('/root/HE27_NCP_SOURCECUT_20261016/FUTURE_KERNEL_CONTROL.json')
with p.open('x') as file:json.dump(out,file,indent=2)
print(json.dumps({m:np.max([r['abs_defect'] for r in rows if r['m']==m],axis=0).tolist() for m in [4,8,16]},indent=2))
