"""Independent high-precision ODE-flow check, not a different-author review.

Uses mpmath integral solution and scipy.solve_ivp, with source identity verified
separately by R18. No imported R19 flow implementation except via comparison.
"""
from __future__ import annotations
import json, math, os, random, sys, time
from pathlib import Path
import mpmath as mp
import numpy as np
from scipy.integrate import solve_ivp
from research.wu_hd_source_bound_r18_20261029.src.native_rates import load_native_grid
from research.wu_hd_nominal_exchange_r19_20261029.src.nominal_exchange import flow_nominal, flow_constant_expansion, source_rhs
ROOT=Path(__file__).resolve().parents[3]
PDF=Path(os.environ.get('WU_R19_SOURCE_PDF',ROOT/'ORIGINAL_SOURCES/GL2022_CSIC_supplement.pdf'))


def run():
    grid=load_native_grid(PDF)
    mp.mp.dps=80
    k=mp.mpf(23)/mp.mpf(200000000000000000)
    rng=random.Random(20261029)
    max_relative=0.0;max_absolute=0.0; cases=0
    start=time.perf_counter()
    for _ in range(160):
        # log-uniform positive reactants, varied asymmetry, all dimensionless
        # exposures up to ~1e3; nonzero product pools do not change rate.
        a=10**rng.uniform(2,9)
        b=a*(10**rng.uniform(-2,2))
        if rng.randrange(5)==0:b=a
        exposure=10**rng.uniform(-8,3)
        t=exposure/(float(k)*max(a,b))
        theta= rng.choice([0.0,1e-12,-1e-12,3e-11,-3e-11])
        if abs(theta*t)>3: theta=0.0
        result=flow_constant_expansion(grid,(a,b,0.1*a,0.2*b),t,theta)
        av,bv,tt,th=map(mp.mpf,map(str,(a,b,t,theta)))
        if theta==0:
            eff=tt;v=mp.mpf(1)
        else:
            v=mp.exp(th*tt);eff=mp.expm1(th*tt)*mp.exp(-th*tt)/th
        m=min(av,bv);M=max(av,bv);delta=M-m
        if delta==0:
            u=m/(1+k*m*eff)
            xi=m-u
        else:
            q=mp.exp(-k*delta*eff)
            xi=m*M*(1-q)/(M-m*q)
        reference=[(av-xi)/v,(bv-xi)/v,(mp.mpf('0.1')*av+xi)/v,(mp.mpf('0.2')*bv+xi)/v]
        for x,y in zip(result.state_m3,reference):
            err=abs(mp.mpf(str(x))-y)
            max_absolute=max(max_absolute,float(err))
            if y>mp.mpf('1e-100'):
                max_relative=max(max_relative,float(err/y))
        cases+=1
    # Independent direct numerical IVP for representative expanding and
    # contracting histories. Not a substitute for exact source uncertainty.
    ivp=[]
    for theta in (0,1e-11,-1e-11):
        y0=np.array([1e6,2e6,2e5,3e5]);tend=1e10
        sol=solve_ivp(lambda t,y: source_rhs(grid,y,expansion_theta_s=theta),
                      (0,tend),y0,method='DOP853',rtol=1e-12,atol=1e-7)
        assert sol.success
        analytic=np.array(flow_constant_expansion(grid,y0,tend,theta).state_m3)
        discrepancy=float(np.max(np.abs(sol.y[:,-1]-analytic)))
        assert discrepancy<=5e-5,(theta,discrepancy)
        ivp.append({'theta_s_inverse':theta,'max_abs_number_density_m_minus3':discrepancy,'nfev':sol.nfev})
    out={'schema':'wu.r19.independent_algorithmic_reference.v1',
         'mpmath_dps':80,'random_seed':20261029,'high_precision_cases':cases,
         'max_relative_error_nonzero':max_relative,'max_absolute_error_m_minus3':max_absolute,
         'relative_threshold':3e-9,'absolute_threshold_m_minus3':2e-5,
         'scipy_ode_cases':ivp,'elapsed_wall_seconds':time.perf_counter()-start,
         'independent_author':False,'source_uncertainty':None,
         'verdict':'PASS' if max_relative<3e-9 and max_absolute<2e-5 else 'FAIL'}
    assert out['verdict']=='PASS',out
    return out

if __name__=='__main__':
    data=run();print(json.dumps(data,indent=2))
