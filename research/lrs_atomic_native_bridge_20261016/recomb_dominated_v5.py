"""Expose dense Case-A split-order limitation against an independent ODE."""
from __future__ import annotations
import json
from math import exp
import numpy as np
from scipy.integrate import solve_ivp
from study_v5 import T0,rays
from dynamic_chemistry import Gas
from recomb_thermal import EV_J,K_B_EV_PER_K,evolve_thermal
from rate_table import CaseARates

N_STAR=.1
H0=1e-16
END=.01
INITIAL=Gas(.37,.03,0.,0.,0.)
STEPS=(.0025,.00125,.000625,.0003125)


def run():
    provider=CaseARates()
    u0=1.5*K_B_EV_PER_K*T0*(INITIAL.hydrogen+INITIAL.electrons)
    def rhs(x,y):
        h2,u=y
        t=u/(1.5*K_B_EV_PER_K*(INITIAL.hydrogen+h2))
        rates=provider(t)
        rr=N_STAR/H0*exp(-3*x)*h2*h2*rates[0]
        return (-rr,-2*u-rr*rates[4]/rates[0]/(EV_J*1e7))
    reference=solve_ivp(rhs,(0,END),(INITIAL.HII,u0),method='Radau',
                        rtol=2e-11,atol=2e-14,max_step=.0005)
    if not reference.success:
        raise RuntimeError(reference.message)
    h2,u=reference.y[:,-1]
    rt=u/(1.5*K_B_EV_PER_K*(INITIAL.hydrogen+h2))
    rows=[]
    for step in STEPS:
        v=evolve_thermal(rays(0.,0.),INITIAL,END,temperature_initial_K=T0,
                         max_step=step,atomic_rates=provider,
                         n_star_cm3=N_STAR,h0_s=H0)
        rows.append({'step':step,'T_K':v.final_temperature_K,
                     'T_error_K':abs(v.final_temperature_K-rt),
                     'ne_error':abs(v.final.electrons-h2),
                     'energy_residual_ev':v.energy_residual_ev,
                     'recomb_events':v.recomb_events[0]})
    return {'n_star_cm3':N_STAR,'H0_s':H0,'X_end':END,
            'radau_T_K':rt,'radau_ne':h2,'radau_nfev':reference.nfev,
            'refinement':rows,
            'claim':'first-order observed in dense recombination; second-order general claim HOLD'}


if __name__=='__main__':
    print(json.dumps(run(),indent=2))
