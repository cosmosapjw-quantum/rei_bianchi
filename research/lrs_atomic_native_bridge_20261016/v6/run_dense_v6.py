"""Strong-density H-only Case-A order diagnostic with independent Radau RHS."""
from __future__ import annotations

from bootstrap_v6 import setup
setup()
import json, math
from pathlib import Path
from scipy.integrate import solve_ivp
from recomb_dominated_v5 import (N_STAR,H0,END,INITIAL,STEPS,T0,rays,
                                 K_B_EV_PER_K,EV_J)
from recomb_thermal import evolve_thermal as old_evolve
from recomb_thermal_midpoint_v6 import evolve_thermal as midpoint_evolve
from rate_table import CaseARates


def run():
  provider=CaseARates()
  u0=1.5*K_B_EV_PER_K*T0*(INITIAL.hydrogen+INITIAL.electrons)
  def rhs(x,y):
    h2,u=y
    t=u/(1.5*K_B_EV_PER_K*(INITIAL.hydrogen+h2))
    vals=provider(float(t))
    rr=N_STAR/H0*math.exp(-3*x)*h2*h2*vals[0]
    return (-rr,-2*u-rr*vals[4]/vals[0]/(EV_J*1e7))
  res=solve_ivp(rhs,(0,END),(INITIAL.HII,u0),method='Radau',
                rtol=1e-12,atol=2e-15,max_step=.0001)
  if not res.success:raise RuntimeError(res.message)
  h2,uth=res.y[:,-1]
  tref=uth/(1.5*K_B_EV_PER_K*(INITIAL.hydrogen+h2))
  out={'input':{'n_star_cm3':N_STAR,'h0_s':H0,'x_end':END,'T0_K':T0},
       'radau':{'T_K':tref,'HII':h2,'nfev':res.nfev},'rows':[]}
  for step in STEPS + (STEPS[-1]/2,STEPS[-1]/4):
    legacy=old_evolve(rays(0.,0.),INITIAL,END,temperature_initial_K=T0,
                      max_step=step,atomic_rates=provider,n_star_cm3=N_STAR,h0_s=H0)
    tested=midpoint_evolve(rays(0.,0.),INITIAL,END,temperature_initial_K=T0,
                          max_step=step,atomic_rates=provider,n_star_cm3=N_STAR,h0_s=H0)
    out['rows'].append({
     'step':step,'legacy_temperature_error_K':abs(legacy.final_temperature_K-tref),
     'v6_temperature_error_K':abs(tested.final_temperature_K-tref),
     'legacy_HII_error':abs(legacy.final.HII-h2),
     'v6_HII_error':abs(tested.final.HII-h2),
     'legacy_T_K':legacy.final_temperature_K,
     'v6_T_K':tested.final_temperature_K,'v6_HII':tested.final.HII,
     'v6_energy_residual_ev':tested.energy_residual_ev,
     'v6_nuclear_residual_H':tested.hydrogen_residual,
     'v6_nuclear_residual_He':tested.helium_residual,
     'v6_electron_residual':tested.electron_reaction_residual,
     'v6_photo_residual':tested.photon_reaction_residual,
     'steps':tested.steps})
  for key in ('legacy_temperature_error_K','v6_temperature_error_K','legacy_HII_error','v6_HII_error'):
    err=[r[key] for r in out['rows']]
    out[key+'_orders']=[math.log(a/b,2) if a>0 and b>0 else None
                             for a,b in zip(err[:-1],err[1:])]
  return out

if __name__=='__main__':
  result=run()
  print(json.dumps(result,indent=2))
  Path(__file__).with_name('dense_v6_results.json').write_text(json.dumps(result,indent=2)+'\n')
