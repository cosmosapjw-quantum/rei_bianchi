"""Independent nonautonomous one-bin radiative source oracle.

Positive linear N' = j(t) - lambda(t) N, A' = lambda(t) N, Q=E*A.
This is NOT H/He chemistry: gas fractions and photon energy are fixed. All
methods share the same positive rates evaluated at the same midpoint; the
source is created in proper time, not log scale. A high-accuracy DOP853 IVP
is used only for independent end-time comparisons.
"""
from __future__ import annotations
import math
from scipy.integrate import solve_ivp
from birth_cohort import frozen_packet


def lam(t, strength=7.0):
    return strength*(1+0.42*math.sin(2*math.pi*t+0.18))

def emissivity(t):
    return 1.0*(1+0.6*math.cos(3*math.pi*t+0.33))

def reference(n0:float,strength:float=7.0):
    def rhs(t,y):
        rate=lam(t,strength)*y[0]
        return [emissivity(t)-rate,rate,emissivity(t)]
    sol=solve_ivp(rhs,(0,1),(n0,0,0),method='DOP853',rtol=2e-13,atol=2e-15)
    if not sol.success:raise ArithmeticError(sol.message)
    x=sol.y[:,-1]
    if abs(x[0]+x[1]-n0-x[2])>8e-13:raise ArithmeticError('reference number budget')
    return x

def trial(n0:float,n:int,method:str,strength:float=7.0):
    h=1/n;nphot=n0;A=S=0
    for k in range(n):
        mid=(k+.5)*h
        new=frozen_packet(old=nphot,source_rate=emissivity(mid),dt=h,
                          lambdas=(lam(mid,strength),),energy_ev=60.0,
                          binding_ev=(13.598434599702,),method=method)
        nphot=new.survivor;A+=new.absorbed;S+=new.injected_count
        if abs(new.number_residual)>8e-15:raise AssertionError('per-step conservation')
        if min(nphot,A,S)<-1e-15:raise AssertionError('positivity')
    if abs(nphot+A-n0-S)>2e-13:raise AssertionError('total photon count ledger')
    return (nphot,A,S)

def campaign():
    masses=(0.,0.08,0.25,0.7)
    ns=(4,8,16,32,64,128,256)
    experiments=[]
    for n0 in masses:
        ref=reference(n0)
        for method in ('legacy_be','be_old_uniform_birth','uniform_exact'):
            rows=[]
            for n in ns:
                calc=trial(n0,n,method)
                rows.append({'n':n,'N':calc[0],'absorbed':calc[1],
                             'source_count':calc[2], 'absolute_vs_DOP853':abs(calc[0]-ref[0])})
            rats=[]
            for i in range(1,len(rows)-1):
                dcoarse=abs(rows[i-1]['N']-rows[i]['N'])
                dfine=abs(rows[i]['N']-rows[i+1]['N'])
                rats.append(dcoarse/dfine if dfine else None)
            experiments.append({'n0':n0,'method':method,'DOP853_final_photons':float(ref[0]),
                                'rows':rows,'step_difference_ratios':rats})
    return experiments

if __name__=='__main__':
    import json
    from pathlib import Path
    out=Path(__file__).parent/'evidence'/'MANUFACTURED_STUDY.json'
    trials=campaign();out.write_text(json.dumps({'schema':'rei.bass.conditional_uniform_birth.v1',
        'scope':'manufactured one-bin nonautonomous linear positive photon source, not actual native chemistry',
        'runs':trials},indent=2)+'\n')
    for n0 in (0.,.08,.25,.7):
        q=[x for x in trials if x['n0']==n0]
        print('initial_old',n0,[(x['method'],x['step_difference_ratios'][-1],x['rows'][-1]['absolute_vs_DOP853']) for x in q])
