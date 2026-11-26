"""Conditional energy-changing angular pair kernel on actual repaired local spectrum.
Separable Doppler-weighted Thomson approximation, not microscopic angle-frequency Compton.
"""
import numpy as np,json
from pathlib import Path
from scipy.constants import k,m_e,c
from edge_audit import project
D=Path(__file__).resolve().parent
def run_one(lab):
 row,r,nh,(x,delta,w,n,bb)=project(lab);assert row['projected_min_ratio']>0
 a=r['a'][-1];tc=2.7255/a;theta=r['T'][-1]/tc;dl=np.log(x[1]/x[0]);f0=1/np.expm1(x)
 d=x[1:]-x[:-1];dd=d/theta;b=-np.expm1(-dd);qq=np.exp(-dd);g=(x[:-1]*x[1:])**2*dd/(d*b)
 # Symmetric cross-angle conductance with normalized weighted marginals.
 mu=n@n.T;K=.75*(1+mu*mu)*(1-mu);M=(w[:,None]*w[None,:])*K
 for _ in range(64):
  s=np.sqrt(w/M.sum(axis=1));M=s[:,None]*M*s[None,:]
 assert np.max(abs(M.sum(axis=1)-w))<1e-13 and np.max(abs(M-M.T))<1e-15
 # Actual final accepted step time. Explicit local collision at this physical clock only.
 dt=np.log(r['a'][-1]/r['a'][-2])/(2.1842852410855023e-18*r['h'][-1]);clock=k*r['T'][-1]/(m_e*c*c)*r['ne'][-1]*1e6*c*6.6524587051e-29*dt
 capacity=w[:,None]*x**3*dl;full=f0+delta
 DF=np.zeros_like(delta);DR=np.zeros_like(delta);DS=np.zeros_like(delta)
 sum_energy=0.;scalar_energy=0.;sum_abs=0.;eqerr=0.
 avg=w@delta
 for j in range(len(d)):
  U,V=delta[:,j],delta[:,j+1]
  j0=-g[j]*f0[j]*(1+f0[j+1])*np.exp(-d[j])*np.expm1(d[j]*(1-1/theta))
  # lower direction i, upper direction j; stable difference from same reference
  ds=g[j]*((1+b[j]*f0[j])*V[None,:]+(-qq[j]+b[j]*f0[j+1])*U[:,None]+b[j]*U[:,None]*V[None,:])
  z=clock*M*ds;z0=clock*M*j0;zf=z0+z
  DS[:,j]+=z.sum(axis=1);DS[:,j+1]-=z.sum(axis=0)
  DF[:,j]+=zf.sum(axis=1);DF[:,j+1]-=zf.sum(axis=0)
  DR[:,j]+=z0.sum(axis=1);DR[:,j+1]-=z0.sum(axis=0)
  sum_energy-=d[j]*z.sum();sum_abs+=abs(z).sum()
  scalar=g[j]*((1+b[j]*f0[j])*avg[j+1]+(-qq[j]+b[j]*f0[j+1])*avg[j]+b[j]*avg[j]*avg[j+1])
  scalar_energy-=d[j]*clock*scalar
  e0=1/np.expm1(x[j]/theta);e1=1/np.expm1(x[j+1]/theta)
  eq=e1*(1+e0)-qq[j]*e0*(1+e1);eqerr=max(eqerr,abs(eq)/max(e1*(1+e0),1e-300))
 assert np.min(full+DF/capacity)>=0 and np.min(f0+DR/capacity)>=0
 assert abs(DS.sum())<1e-13*max(sum_abs,1e-300)
 energy=float(np.sum(DS*x));assert abs(energy-sum_energy)<1e-12*max(abs(sum_energy),1e-300)
 return dict(clock=float(clock),marginal_error=float(max(abs(M.sum(axis=1)-w))),number_relative=float(abs(DS.sum())/max(sum_abs,1e-300)),energy_relative=float(abs(energy-sum_energy)/max(abs(sum_energy),1e-300)),signed_Q_eV_H=float(bb*15/np.pi**4*sum_energy),scalar_Q_eV_H=float(bb*15/np.pi**4*scalar_energy),angular_difference_eV_H=float(bb*15/np.pi**4*(sum_energy-scalar_energy)),relative_angular_difference=float(abs(sum_energy-scalar_energy)/max(abs(scalar_energy),1e-300)),equilibrium_relative=eqerr,minimum_full_ratio=float(np.min((full+DF/capacity)/f0)))
def run():
 rows={k:run_one(k) for k in ['edge_elastic512','edge_elastic1024','edge_elastic1024_72ray']}
 o=dict(rows=rows,scope='actual terminal spectrum, one physical local explicit collision increment, symmetric Doppler-weighted separable angular kernel and Bose detailed balance, full-reference difference, not inserted into live gas; no exact microscopic anisotropic Compton')
 (D/'ANGULAR_ENERGY.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()
