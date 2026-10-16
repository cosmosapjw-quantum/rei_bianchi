"""C8: independent Radau vs positive exact-pair midpoint RR/DR and four cooling ledgers."""
from __future__ import annotations
import csv
import json
import math
from pathlib import Path
from time import perf_counter
import sys

import numpy as np
from scipy.integrate import quad, solve_ivp

from rrdr_sourcefree_v8 import (
    CHANNELS, KB, Y_HE, compare, evolve, native, nuclei_and_electrons,
    radau_reference, rhs_independent, stock_vector, temperature_from_stocks,
)

ROOT=Path(__file__).resolve().parent
EVIDENCE=ROOT/'evidence'
EVIDENCE.mkdir(exist_ok=True)
CASES=[
    ('actual_native_z20_short',1.0,1e-5,15000.0),
    ('fixed_overdensity_100',100.,.002,15000.),
    ('fixed_overdensity_1000',1000.,.002,15000.),
    ('fixed_overdensity_10000',10000.,.0003,15000.),
    ('helium_DR_sensitive_22000K',1000.,.002,22000.),
]
COUNTS=[8,16,32,64,128]


def t_from_sol(result):
    end=result.y[:,-1]
    return temperature_from_stocks(float(end[3]),stock_vector(end[:3]))


def independent_channel_quadrature(temperature=22000., d=1000., span=.002):
    ref=radau_reference(x_end=span,T0=temperature,density_factor=d)
    # Reintegrate a second time with dense-output interpolation and integrate
    # the corresponding event/cooling integrands with independent quadrature.
    old=np.zeros(17)
    old[:3]=native.INITIAL_FRACTIONS
    ne=old[0]+Y_HE*(old[1]+2*old[2])
    old[3]=1.5*KB*temperature*(1+Y_HE+ne)
    r=solve_ivp(lambda x,y:rhs_independent(x,y,d),[0,span],old,
                method='Radau',rtol=2e-12,atol=[8e-15]*3+[1e-28]*14,
                max_step=span/64,dense_output=True)
    if not r.success:
        raise RuntimeError(r.message)
    q=[];events=[]
    for j in range(4):
        eq=quad(lambda x:rhs_independent(x,r.sol(x),d)[8+j],0,span,
                epsabs=1e-28,epsrel=5e-11,limit=150)[0]
        ea=quad(lambda x:rhs_independent(x,r.sol(x),d)[4+j],0,span,
                epsabs=1e-13,epsrel=5e-11,limit=150)[0]
        q.append(eq);events.append(ea)
    difq=[abs(v-ref.y[8+j,-1]) for j,v in enumerate(q)]
    difev=[abs(v-ref.y[4+j,-1]) for j,v in enumerate(events)]
    return dict(method='independent_quad_on_Radau_dense_solution',
                quadrature_cooling=dict(zip(CHANNELS,q)),
                quadrature_events=dict(zip(CHANNELS,events)),
                max_cooling_difference_erg_per_H=max(difq),
                max_event_difference_per_H=max(difev),
                differences_by_channel_cooling=dict(zip(CHANNELS,difq)),
                differences_by_channel_events=dict(zip(CHANNELS,difev)))


def run():
    outputs=[];flat=[]
    for name,density,span,temp in CASES:
        params={'x_end':span,'density_factor':density,'T0':temp}
        ref=radau_reference(**params)
        tight=radau_reference(**params,rtol=2e-13)
        ref_t=t_from_sol(ref);tight_t=t_from_sol(tight)
        rows=[]
        for n in COUNTS:
            started=perf_counter();res=evolve(n,**params);time_spent=perf_counter()-started
            metrics=compare(res,ref)
            h=span/n
            row={'N':n,'h':h,'Tgas_K':res.temperature,
                 'electron_per_H':res.electron_per_h,
                 'RR_DR_event_total_per_H':float(sum(res.events)),
                 'escaped_binding_by_channel_erg_per_H':dict(zip(CHANNELS,res.binding_escape.tolist())),
                 'cooling_by_channel_erg_per_H':dict(zip(CHANNELS,res.cooling.tolist())),
                 'events_by_channel_per_H':dict(zip(CHANNELS,res.events.tolist())),
                 'work_gas_erg_per_H':res.work,
                 'thermal_energy_erg_per_H':res.w,
                 'elapsed_wall_s_sandbox':time_spent,
                 **metrics}
            flat.append({'case':name,'N':n,'h':h,'T_error_K':metrics['T_error_K'],
                         'ne_abs_error':metrics['ne_abs_error'],
                         'max_cooling_energy_error_erg_per_H':metrics['max_cooling_energy_error_erg_per_H'],
                         'energy_residual_erg_per_H':metrics['energy_residual_erg_per_H'],
                         'max_rr_exposure':metrics['max_rr_exposure']})
            rows.append(row)
        errs=[row['T_error_K'] for row in rows]
        orders=[math.log2(a/b) if a>1e-10 and b>1e-10 else None
                for a,b in zip(errs[:-1],errs[1:])]
        entry={'case':name,'density_factor':density,'Xend':span,'T0_K':temp,
               'comparison':'continuous_independent_Radau_rhs',
               'radau_Tgas_K':ref_t,
               'radau_tolerance_refinement_T_K':abs(tight_t-ref_t),
               'radau_endpoint_chemistry_diff':float(max(abs(tight.y[:3,-1]-ref.y[:3,-1]))),
               'radau_nfev':ref.nfev,
               'temperature_orders_log2':orders,
               'endpoint_Radau_event_by_channel':dict(zip(CHANNELS,ref.y[4:8,-1].tolist())),
               'endpoint_Radau_cooling_erg_per_H_by_channel':dict(zip(CHANNELS,ref.y[8:12,-1].tolist())),
               'rows':rows}
        outputs.append(entry)
        print(name,'D',density,'span',span,'ref_T',ref_t,'errors_K',errs,
              'orders',orders,flush=True)
    cross=independent_channel_quadrature()
    print('Channel quadrature independent crosscheck',cross,flush=True)
    data={'schema':'rei.lrs.v8.C8_evidence.1',
          'src':'PR163 a6fe0e8b1932ddf60496c5a9dbb68c19d6f0851f; PR150 native owner 6ea2b1b4b3875c9163cafc45efe720afded43fc4',
          'claim':'original native Grackle coefficient backed Python RR/DR reference, NOT actual Rust execution',
          'channel_names':CHANNELS,
          'zero_regime':'D=1,X=1e-5 temperature endpoint differences are roundoff-scale: do NOT infer order',
          'overdense_regime':'Prescribed density multiplier at fixed H(a), not a self-consistent cosmological overdensity',
          'cases':outputs,'independent_quadrature':cross}
    (EVIDENCE/'C8_REFINEMENT.json').write_text(json.dumps(data,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    with (EVIDENCE/'C8_REFINEMENT.csv').open('w',newline='') as f:
        out=csv.DictWriter(f,fieldnames=list(flat[0]));out.writeheader();out.writerows(flat)
    return data

if __name__=='__main__':run()
