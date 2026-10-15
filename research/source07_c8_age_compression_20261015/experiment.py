#!/usr/bin/env python3
"""Positive sparse age compression for frozen receiver: diagnosed scope only."""
import json,math,sys,time
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from numpy.polynomial.legendre import leggauss
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'research/source07_c1_baseline_20261014'))
from q_emission_baseline import Scenario,Spectrum
model=Scenario(root);spec=Spectrum();dt=1e10;C=29979245800.
fit=[(13.60,.4298,5.475e4,32.88,2.963,0.,0.,0.),(24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136),(54.42,1.720,1.369e4,32.88,2.963,0.,0.,0.)]
bind=(13.598434599702,24.587389011,54.41776)
nh=model.nh*5**3*(1-.0002); nhe=model.nh*5**3*.2454/(4*(1-.2454))
gas_base=(nh,nhe,0.0)
mu,muw=leggauss(12);e_nodes,e_weights=leggauss(16)

def sigma(E,p):
 chi,e0,s0,ya,po,yw,y0,y1=p
 if E<chi:return 0.
 x=E/e0-y0;y=math.hypot(x,y1)
 return s0*((x-1.)**2+yw*yw)*y**(po/2-5.5)*(1+math.sqrt(y/ya))**(-po)*1e-18

def vector(a,q,gas):
 rp,rz=model.ratios(.2,q); # ratios supplied from fixed physical anchor z=20; calculate relative age from geometrical background instead
 rpa,rza=model.ratios(a,q)
 rp/=rpa; rz/=rza
 # Positive integrals over initial energy with threshold cuts, 12 angle directions
 out=np.zeros(5)
 for m,wm in zip(mu,muw):
  scale=math.sqrt(rp*rp*(1-m*m)+rz*rz*m*m)
  cuts=sorted(set([13.6,100.]+[th/scale for th in (13.6,24.59,54.42) if 13.6<th/scale<100.]))
  for lo,hi in zip(cuts,cuts[1:]):
   for e,w in zip((lo+hi)/2+(hi-lo)/2*e_nodes,(hi-lo)/2*e_weights):
    flux=wm/2*w*spec.phi(e)
    E=e*scale
    lam=np.array([C*n*sigma(E,p) for n,p in zip(gas,fit)])
    rate=lam.sum(); absorb=lam*(-math.expm1(-rate*dt)/rate) if rate>0 else np.zeros(3)
    out+=flux*np.array([1.,E,absorb[0],absorb[1],sum(absorb[j]*(E-bind[j]) for j in range(3))])
 return out

results=[]
ages=np.geomspace(model.ar,.2,36)
for q in (-.01,0.,.01):
 t0=time.perf_counter()
 A=np.array([vector(a,q,gas_base) for a in ages]).T
 weights=np.ones(len(ages))/len(ages)
 target=A@weights
 scales=np.maximum(np.max(abs(A),axis=1),1e-30)
 norm=A/scales[:,None]; rhs=target/scales
 objective=np.linspace(0,1,len(ages))
 lp=linprog(objective,A_eq=norm,b_eq=rhs,bounds=(0,None),method='highs',options={'primal_feasibility_tolerance':1e-10,'dual_feasibility_tolerance':1e-10})
 assert lp.success,lp.message
 pos=lp.x>1e-9
 compressed= A@lp.x
 check=np.max(abs(compressed-target)/np.maximum(abs(target),1e-30))
 assert check<1e-9,check
 assert abs(sum(lp.x)-sum(weights))<1e-10
 # Independent gas density sensitivity is not constrained: this is out-of-sample.
 newgas=(nh*.6,nhe*1.3,0.)
 B=np.array([vector(a,q,newgas) for a in ages]).T
 err=np.abs(B@lp.x-B@weights)/np.maximum(np.abs(B@weights),1e-30)
 row={'q':q,'age_count':len(ages),'retained_count':int(pos.sum()),'nodes':[(float(ages[i]),float(lp.x[i])) for i in np.where(pos)[0]],'reconstructed_relative_error':float(check),'holdout_gas_relative_errors':err.tolist(),'wall_seconds':time.perf_counter()-t0,'positive':bool(np.all(lp.x>=0))}
 results.append(row)
 print('q',q,'retained',row['retained_count'],'same-state relative',row['reconstructed_relative_error'],'gas-holdout',err.tolist(),flush=True)
Path(__file__).with_name('results.json').write_text(json.dumps(results,indent=2)+'\n')
