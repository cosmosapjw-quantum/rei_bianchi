#!/usr/bin/env python3
"""SOURCE07 C8, conservative source-age-resolved quadrature benchmark.
Finite impulses and frozen gas only; never substitutes an evolving ionization solver.
"""
import sys,math,json,time
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from numpy.polynomial.legendre import leggauss
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'research/source07_c1_baseline_20261014'))
from q_emission_baseline import Scenario,Spectrum
model=Scenario(root); spectrum=Spectrum()
fit=[(13.60,.4298,5.475e4,32.88,2.963,0.,0.,0.),(24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136),(54.42,1.720,1.369e4,32.88,2.963,0.,0.,0.)]
bind=[13.598434599702,24.587389011,54.41776]
dt=1e10; C=29979245800.; nHI=model.nh*5**3*(1-.0002); nHeI=model.nh*5**3*.2454/(4*(1-.2454)); gas=[nHI,nHeI,0.]

def sigma(E,par):
    chi,e0,s0,ya,p,yw,y0,y1=par
    if E<chi:return 0.
    x=E/e0-y0;y=math.hypot(x,y1)
    return s0*((x-1.)**2+yw*yw)*y**(p/2-5.5)*(1.+math.sqrt(y/ya))**(-p)*1e-18

def reaction(E):
    L=[C*n*sigma(E,p) for n,p in zip(gas,fit)]; total=sum(L)
    if total==0:return [0.]*4
    a=-math.expm1(-total*dt)/total
    absorbed=[a*x for x in L]
    return absorbed+[sum(n*(E-bind[k]) for k,n in enumerate(absorbed))]

def split(scale):
    cuts=[13.6,100.]
    for th in (13.6,24.59,54.42):
        t=th/scale
        if cuts[0]<t<cuts[-1]:cuts.append(t)
    return list(zip(sorted(set(cuts))[:-1],sorted(set(cuts))[1:]))

def moment(scale,method,n=4):
    out=np.zeros(4)
    if method=='gauss':nodes,weights=leggauss(n)
    for lo,hi in split(scale):
        if method=='gauss':
            E=0.5*(hi-lo)*nodes+0.5*(hi+lo)
            for e,w in zip(E,weights):out+=0.5*(hi-lo)*w*spectrum.phi(e)*np.asarray(reaction(e*scale))
        else:
            for j in range(4):out[j]+=quad(lambda e:spectrum.phi(e)*reaction(e*scale)[j],lo,hi,epsabs=4e-14,epsrel=8e-12,limit=180)[0]
    return out

def calc(q,method,n):
    mu,w=leggauss(32);rp,rz=model.ratios(0.2,q); vol=(model.ar/.2)**3;res=np.zeros(4)
    fresh=moment(1,method,n)
    for m,weight in zip(mu,w):
        scale=math.sqrt(rp*rp*(1-m*m)+rz*rz*m*m)
        jac=vol/(scale**3)
        res+=weight/2*(moment(scale,method,n)+jac*fresh)
    return res*model.rate(model.ar)*dt

rows=[]
for q in [-.01,0.,.01]:
    t=time.perf_counter();truth=calc(q,'quad',0);ref_sec=time.perf_counter()-t
    for n in (2,4,8,16):
        t=time.perf_counter();result=calc(q,'gauss',n);sec=time.perf_counter()-t
        rel=[float((result[j]-truth[j])/truth[j]) if truth[j] else None for j in range(4)]
        rows.append(dict(q=q,gauss_order=n,relative_errors=rel,seconds=sec,reference_seconds=ref_sec,truth=[float(x) for x in truth]))
        print('q',q,'n',n,'relative HI HeI HeII heat',rel,'seconds',round(sec,4),flush=True)
Path(__file__).with_name('results.json').write_text(json.dumps(rows,indent=2)+'\n')
