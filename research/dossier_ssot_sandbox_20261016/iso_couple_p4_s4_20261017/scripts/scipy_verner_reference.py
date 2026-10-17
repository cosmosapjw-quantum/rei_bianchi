#!/usr/bin/env python3
"""Independent SciPy integration of source-selected Verner HI and D-H-equality.

This independently recreates the *same specified model*, not an independent
atomic-physics measurement or continuum EoR accuracy guarantee.
"""
import json, math
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from scipy.constants import c

T_END=5e12
H=1.2e-16
E0=13.605
CHI_D=13.598434599702 + 0.0037
ETH_H=13.60
# Verner et al. 1996, the exact H I fit parameters used in owner_src/atomic_provider.rs
PARAM=(0.4298,5.475e4,32.88,2.963,0.0,0.0,0.0)
def sigma_verner_hi_m2(energy_ev:float)->float:
    if energy_ev<ETH_H: return 0.0
    e0,sigma0,ya,p,yw,y0,y1=PARAM
    x=energy_ev/e0-y0
    y=math.hypot(x,y1)
    sigma_cm2 = sigma0 * ((x-1.)**2+yw**2) * y**(p/2.-5.5) * (1.+math.sqrt(y/ya))**(-p) * 1e-18
    return sigma_cm2*1e-4

def rates(t:float):
    en=E0*math.exp(-H*t)
    h_rate=0.03 * sigma_verner_hi_m2(en) * c
    d_rate=0.03 * sigma_verner_hi_m2(en) * c if en>=CHI_D else 0.
    return h_rate,d_rate

td=math.log(E0/CHI_D)/H
th=math.log(E0/ETH_H)/H
res=[]
for k in [0,1]:
    val,abserr=quad(lambda t:rates(t)[k],0,T_END,points=[td,th],epsabs=1e-16,epsrel=1e-13,limit=200)
    res.append(dict(channel=['HI','DI'][k],tau=val,quad_abserr=abserr))
rtotal=sum(x['tau'] for x in res)
rows=list(__import__('csv').DictReader(open(Path(__file__).resolve().parents[1]/'evidence/verner_threshold_error.csv')))
root_row=next(x for x in rows if int(x['N'])==128 and x['mode']=='edge_root')
rel_diff=abs(float(root_row['tau'])-rtotal)/rtotal
summary={'model':'Verner1996_HI + HI_H_EQUALITY_DI_with_independently_enforced_DI_edge',
         'source': 'exact_owner_parameter_values_reimplemented_in_python',
         'integrator':'SciPy quad split at analytic H and D photon-energy threshold crossing times',
         'E_birth_eV':E0,'H_per_s':H,'duration_s':T_END,'chi_D_ev':CHI_D,
         'H_verner_edge_ev':ETH_H,'H_cross_s':th,'D_cross_s':td,
         'tau_channels':res,'tau_total_scipy':rtotal,'survivor_scipy':math.exp(-rtotal),
         'rust_split_n128_tau':float(root_row['tau']),'rust_vs_scipy_relative':rel_diff,
         'claim_scope':'one prescribed FLRW-like ray; constant proper absorber density; no chemistry or EoR'}
p=Path(__file__).resolve().parents[1]/'evidence/SCIPY_VERNER_REFERENCE.json'
p.write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
assert rel_diff<2e-9,rel_diff
