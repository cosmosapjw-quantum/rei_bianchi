"""Independent 80-digit ratio-of-survivors reference for R20.

Does not import the production analytic extent helper; only uses the verified
source grid for rate lookup. Separate algorithm, NOT a distinct-author review.
"""
from __future__ import annotations
import os
from pathlib import Path
import json, random, math, sys
import mpmath as mp
from research.wu_hd_source_bound_r18_20261029.src.native_rates import load_native_grid, TEMPERATURES_K
from src.grid_exposure import Segment, evolve_source_grid

ROOT=Path(__file__).resolve().parents[1]
PDF=Path(os.environ.get('WU_R20_SOURCE_PDF', str(ROOT/'parent/ORIGINAL_SOURCES/GL2022_CSIC_supplement.pdf')))


def reference(grid,n0,segments):
    mp.mp.dps=80
    conv=lambda x: mp.mpf(str(x))
    v=mp.mpf(1);E=mp.mpf(0)
    for seg in segments:
        k=grid.lookup(seg.temperature_K).nominal_m3_s
        km=mp.mpf(k.numerator)/k.denominator
        dt=conv(seg.duration_s);theta=conv(seg.theta_s)
        z=theta*dt
        I=dt/v if theta==0 else -mp.expm1(-z)/(theta*v)
        E+=km*I
        v*=mp.exp(z)
    a,b,c,d=map(conv,n0)
    if a==0 or b==0 or E==0:
        xi=mp.mpf(0);ra=a;rb=b
    elif a==b:
        ra=a/(1+a*E);rb=ra;xi=a-ra
    else:
        m,M=min(a,b),max(a,b)
        delta=M-m
        ratio=(m/M)*mp.exp(-delta*E)
        small=delta*ratio/(1-ratio)
        large=delta/(1-ratio)
        ra,rb=(small,large) if a<=b else (large,small)
        xi=m-small
    return (tuple(float(x/v) for x in (ra,rb,c+xi,d+xi)),float(E),float(v))


def run(ncases=160,seed=20261029):
    rng=random.Random(seed)
    grid=load_native_grid(PDF)
    max_abs=0.;max_rel=0.;max_exposure_rel=0.;max_volume_rel=0.
    failures=[]
    for i in range(ncases):
        base=10**rng.uniform(2,8)
        if i%5==0:a=b=base
        elif i%5==1:a=base;b=base*(1+10**rng.uniform(-12,-6))
        elif i%5==2:a=base;b=base*10**rng.uniform(.01,1)
        else:a=base*10**rng.uniform(-.3,.3);b=base*10**rng.uniform(-.3,.3)
        n0=(a,b,base*.1,base*.03)
        segments=[]
        for j in range(rng.randint(1,6)):
            dt=10**rng.uniform(6,11)
            z=rng.uniform(-.15,.15)
            segments.append(Segment(rng.choice(TEMPERATURES_K),dt,z/dt))
        calc=evolve_source_grid(grid,n0,segments)
        target,E,v=reference(grid,n0,segments)
        for x,y in zip(calc.final_state_m_minus3,target):
            err=abs(x-y);rel=err/max(abs(y),1.)
            max_abs=max(max_abs,err);max_rel=max(max_rel,rel)
            if err>2e-4 and rel>2e-10:
                failures.append({'case':i,'computed':x,'reference':y,'abs':err,'rel':rel})
        max_exposure_rel=max(max_exposure_rel,abs(calc.exposure_m3-E)/max(abs(E),1e-30))
        max_volume_rel=max(max_volume_rel,abs(calc.volume_ratio-v)/max(abs(v),1e-30))
    result={'schema':'wu.r20.independent_mpmath80.v1','cases':ncases,'seed':seed,
            'reference':'80-digit independent survivor-ratio formula, exact source Fraction rate',
            'max_absolute_density_m_minus3':max_abs,'max_relative_density_floor_1':max_rel,
            'max_relative_exposure':max_exposure_rel,'max_relative_volume':max_volume_rel,
            'acceptance':'per-component abs <= 2e-4 OR rel <= 2e-10',
            'failures':failures[:5],'passed':len(failures)==0,
            'distinct_author_review':False,'source_true_uncertainty':None}
    return result

if __name__=='__main__':
    result=run();print(json.dumps(result,indent=2));
    (ROOT/'results/INDEPENDENT_MPMATH80.json').write_text(json.dumps(result,indent=2)+'\n')
    if not result['passed']:sys.exit(1)
