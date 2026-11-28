"""Independent formula/80-digit oracle for R21 caloric ledger (same-author algorithm)."""
from __future__ import annotations
from pathlib import Path
import json
import math
import random
import mpmath as mp

from research.wu_hd_source_bound_r18_20261029.src.native_rates import load_native_grid
from research.wu_hd_source_grid_r20_20261029.src.grid_exposure import Segment
from research.wu_hd_thermal_mechanical_ledger_r21_20261029.src.thermal_ledger import build_ledger

PDF=Path(__file__).resolve().parents[3]/'ORIGINAL_SOURCES/GL2022_CSIC_supplement.pdf'
mp.mp.dps=80
kb=mp.mpf('1.380649e-23')
rng=random.Random(4915)
grid=load_native_grid(PDF)
absE=relE=absBath=relBath=absXi=0.0
count=160
for idx in range(count):
    a=0 if idx%43==0 else 10**rng.uniform(3,8)
    b=a if idx%13==0 else 10**rng.uniform(2,8)
    n=(a,b,10**rng.uniform(1,6),10**rng.uniform(1,5))
    seq=[]
    for j in range(1+(idx%4)):
        t=10**rng.uniform(6,10)
        th=rng.uniform(-2e-11,2e-11)
        seq.append(Segment((105,255,505)[(idx+j)%3],t,th))
    flow, led=build_ledger(grid,n,seq)
    Ntot=sum(mp.mpf(str(x)) for x in n)
    v=mp.mpf(1); expo=mp.mpf(0); work=mp.mpf(0)
    for s in seq:
        z=mp.mpf(str(s.theta_s))*mp.mpf(str(s.duration_s))
        k=grid.lookup(s.temperature_K).nominal_m3_s
        kmp=mp.mpf(k.numerator)/mp.mpf(k.denominator)
        inv=mp.mpf(str(s.duration_s))/v * (-mp.expm1(-z)/z if z!=0 else 1)
        expo += kmp * inv
        v *= mp.exp(z)
        work += Ntot*kb*mp.mpf(s.temperature_K)*z
    tr=mp.mpf('1.5')*Ntot*kb*mp.mpf(seq[-1].temperature_K-seq[0].temperature_K)
    intercept=-(work+tr)
    aa,bb=mp.mpf(str(a)),mp.mpf(str(b))
    if aa==0 or bb==0: xi=mp.mpf(0)
    elif aa==bb: xi=aa*aa*expo/(1+aa*expo)
    else:
        small=min(aa,bb);large=max(aa,bb);delta=large-small
        R=-mp.expm1(-delta*expo)
        xi=small*large*R/(delta+small*R)
    AE=abs(mp.mpf(str(flow.exposure_m3))-expo)
    AX=abs(mp.mpf(str(flow.extent_reference_m_minus3))-xi)
    AB=abs(mp.mpf(str(led.bath_known_intercept_J_per_ref_m3))-intercept)
    absE=max(absE,float(AE));absXi=max(absXi,float(AX));absBath=max(absBath,float(AB))
    relE=max(relE,float(AE/max(abs(expo),mp.mpf('1e-50'))))
    relBath=max(relBath,float(AB/max(abs(intercept),mp.mpf('1e-34'))))
    assert AE <= mp.mpf('8e-14')*max(abs(expo),mp.mpf('1e-40')), (idx,'E',AE)
    assert AX <= mp.mpf('2e-12')*max(abs(xi),mp.mpf(1)), (idx,'XI',AX)
    assert AB <= mp.mpf('8e-14')*max(abs(intercept),mp.mpf('1e-34')), (idx,'BATH',AB)
output={"schema":"wu.r21.independent_mpmath80.v1","cases":count,"PASS":count,"precision_dps":80,"same_author_different_algorithm":True,"distinct_author":False,"max_abs_exposure_m3":absE,"max_abs_extent_ref_m3":absXi,"max_abs_bath_intercept_J_ref_m3":absBath,"max_rel_exposure":relE,"max_rel_bath_intercept":relBath,"source_pdf_sha256":grid.source_sha256}
target=Path(__file__).resolve().parents[1]/'results'/'INDEPENDENT_MPMATH80.json'
target.write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps(output,indent=2))
