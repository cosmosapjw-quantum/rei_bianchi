"""Deterministic source-free spectral H/He chemistry reference results.

Source comparison: independent SciPy Radau integration of direct ODE with
Verner fits; not a cosmological reionization or temperature prediction.
"""
import json
from pathlib import Path
from math import fsum
import numpy as np
from dynamic_chemistry import Gas,evolve
from lrs_threshold_oracle import Ray,GAUSS8
from verner_angular import load_primary_fits
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'tests'))
from test_dynamic_chemistry import independent_ivp

INITIAL=Gas(.37,.03,.085,.012,.003)
LEVELS=((110.,.12),(72.,.08),(43.,.06))
END=.65
RATE=2.

def init_rays(s):
    return tuple(Ray(energy,mu,.5*w*amplitude,s)
                 for energy,amplitude in LEVELS for mu,w in GAUSS8)

def moments(rays,result):
    uv=fsum(N*r.geometry(END)[0] for N,r in zip(result.photon_final,rays))
    par=fsum(N*r.geometry(END)[0]*r.geometry(END)[1]**2
             for N,r in zip(result.photon_final,rays))
    return (3*par-uv)/(2*uv)

rows=[]
for s in [-.04,0.,.04]:
    ray_set=init_rays(s)
    yref=independent_ivp(ray_set,INITIAL,END,RATE)
    refs=[float(x) for x in yref]
    for step in [.08,.04,.02,.01,.005]:
        r=evolve(ray_set,INITIAL,END,rate_per_mb=RATE,step_max=step)
        state=[*r.photon_final,*r.final.as_tuple(),r.binding_ev,r.heat_ev,r.expansion_work_ev]
        error=max(abs(a-b) for a,b in zip(state,refs))
        rows.append({
          'signed_s_over_H':s,'Sigma':3**.5*abs(s),'max_step_X':step,
          'n_ray':len(ray_set),'substeps':r.substeps,'threshold_events':r.threshold_events,
          'electron_initial':INITIAL.electrons,'electron_final':r.final.electrons,
          'HII_final':r.final.HII,'HeII_final':r.final.HeII,'HeIII_final':r.final.HeIII,
          'absorption_by_species':r.absorbed,'photon_surviving':sum(r.photon_final),
          'heat_eV_per_nstar':r.heat_ev,'binding_eV_per_nstar':r.binding_ev,
          'redshift_shear_work_eV_per_nstar':r.expansion_work_ev,
          'pi_over_u':moments(ray_set,r),
          'max_abs_difference_to_Radau':error,
          'electron_photon_residual':r.photon_electron_residual,
          'H_residual':r.hydrogen_residual,
          'He_residual':r.helium_residual,
          'energy_residual_eV':r.energy_residual_ev,
        })
        print(f's/H={s:+.2f} dX={step:.3f} substeps={r.substeps} '
              f'error={error:.9e} ne={r.final.electrons:.9f} '
              f'pi/U={moments(ray_set,r):+.9f} '
              f'conserv_Ne={r.photon_electron_residual:.3e} '
              f'conserv_E={r.energy_residual_ev:.3e}')

payload={
 'claim_status':'NUMERICALLY_CHECKED_CONDITIONAL_REFERENCE_IN_SANDBOX',
 'environment':'ChatGPT container CPython scipy Radau; user Ubuntu/NCP integration NOT_RUN',
 'base_repo_commit':'bbbd18b5c16eff70bc32ba4296360dceb9060ec4',
 'source_reference':'Verner et al 1996, ApJ 465 487; donor in PR152',
 'initial_gas':dict(zip(('HI','HII','HeI','HeII','HeIII'),INITIAL.as_tuple())),
 'units':'stocks normalized to n_star, energies eV per n_star, X=ln(a/a0)',
 'rate_per_mb':RATE,
 'x_end':END,
 'assumptions':['fixed prescribed H/H0=1','constant signed s/H','source-free','only HI/HeI/HeII photoionization','no recombination or thermal feedback'],
 'reference':'independent SciPy Radau continuous ODE solved on photon-threshold event intervals, rtol=2e-11 atol=2e-13',
 'rows':rows
}
p=Path(__file__).resolve().parent/'evidence'/'dynamic_chemistry_radau_convergence.json'
p.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
print('WROTE',p)
