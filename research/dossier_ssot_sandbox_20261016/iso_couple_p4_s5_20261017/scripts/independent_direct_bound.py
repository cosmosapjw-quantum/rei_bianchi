#!/usr/bin/env python3
"""SciPy ODE check of the conditional (gas-history-frozen) photon-only remainder.
No claim about the coupled gas feedback or observations.
"""
import json, math
from scipy.integrate import solve_ivp
SPEED=299792458.0
EVJ=1.602176634e-19
# Original PR150 Verner 1996 HI HeI HeII formulas and D H-equality conditional gate.
PARAMS=[(13.60,.4298,5.475e4,32.88,2.963,0.,0.,0.),(24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136),(54.42,1.720,1.369e4,32.88,2.963,0.,0.,0.)]
CHI_D=13.602134599702

def sigma(absorber,energy):
    if absorber==3:
        if energy<CHI_D:return 0.
        absorber=0
    eth,e0,sigma0,ya,p,yw,y0,y1=PARAMS[absorber]
    if energy<eth:return 0.
    x=energy/e0-y0
    y=math.hypot(x,y1)
    return sigma0*((x-1.)**2+yw**2)*y**(p/2-5.5)*(1+(y/ya)**.5)**(-p)*1e-22

def evaluate(h,s,energy,mu,tmax):
    hj=[h-s,h-s,h+2*s]
    def energy_ev(t):
        x=energy*math.sqrt((1-mu*mu)*math.exp(-2*hj[0]*t)+mu*mu*math.exp(-2*hj[2]*t))
        return x
    growth=math.exp(max(0.,-min(hj))*tmax)
    upper=energy*growth
    n_m3=[0.02,0.005,0.001,0.001]
    def rhs(t,y):
        en=energy_ev(t)
        kval=[n*SPEED*sigma(i,en) for i,n in enumerate(n_m3)]
        return [-y[0]*sum(kval)]+[y[0]*k for k in kval]+[y[0]*en*EVJ*sum(kval)]
    sol=solve_ivp(rhs,(0.,tmax),[1.,0.,0.,0.,0.,0.],rtol=1e-10,atol=1e-13,method='DOP853')
    assert sol.success,sol.message
    sur,*other=sol.y[:,-1]
    counts=other[:4]; energy_photo=other[4]
    residual=abs(sur+sum(counts)-1.)
    assert residual<5e-11
    assert all(-1e-13<=u<=1+1e-13 for u in counts)
    assert 0<=energy_photo<=(upper*EVJ)*(1+1e-9)
    assert all(energy_ev(t/100*tmax)<=upper*(1+1e-14) for t in range(101))
    return dict(h=h,s=s,initial_energy_ev=energy,mu=mu,tmax_s=tmax,upper_growth=growth,surviving=sur,
      channel_events=counts,absorption_energy_J=energy_photo,photon_identity_residual=residual,
      energy_upper_J=upper*EVJ,energy_margin_J=upper*EVJ-energy_photo,independent_method='SciPy DOP853 source-native Verner fit recreated independently')

cases=[(1e-15,0,13.7,0.3,2e14),(1e-15,0,60.,0.6,3e14),(1e-15,2e-15,36.,0.9,8e14),(1.2e-16,0.06*1.2e-16,80.,0.8,8e13)]
rows=[evaluate(*p) for p in cases]
print(json.dumps(dict(status='PASS_SCOPED_FIXED_OPACITY_DIRECT_TRANSPORT',cases=rows,max_photon_identity_residual=max(x['photon_identity_residual'] for x in rows)),ensure_ascii=False,indent=2))
