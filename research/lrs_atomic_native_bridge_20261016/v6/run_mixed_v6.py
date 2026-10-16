"""Scoped five-case, Grackle case-A mixed H/He tests vs independent V5 Radau."""

from __future__ import annotations
from bootstrap_v6 import setup
setup()
import json, math
from pathlib import Path
import numpy as np
from study_v5 import (rays,GAS,T0,END,N_STAR,H0,independent_rhs)
from dynamic_chemistry import Gas
from recomb_thermal import evolve_thermal as legacy
from recomb_thermal_midpoint_v6 import evolve_thermal as proposed
from rate_table import CaseARates
STEPS=(.005,.0025,.00125,.000625)

def run():
    p=CaseARates()
    cases={
        'H_only':(rays(0.,0.),Gas(.37,.03,0.,0.,0.)),
        'He_only':(rays(0.,0.),Gas(0.,0.,.085,.012,.003)),
        'mixed_FLRW':(rays(0.),GAS),
        'mixed_LRS_minus':(rays(-.04),GAS),
        'mixed_LRS_plus':(rays(+.04),GAS),
    }
    results={}
    for name,(rr,gas) in cases.items():
        y_ref,T_ref,ne_ref,nfev=independent_rhs(rr,gas,p)
        seq=[]
        for h in STEPS:
            opts=dict(temperature_initial_K=T0,max_step=h,atomic_rates=p,
                      n_star_cm3=N_STAR,h0_s=H0)
            old=legacy(rr,gas,END,**opts)
            new=proposed(rr,gas,END,**opts)
            v=np.array([*new.photons_final,*new.final.as_tuple(),new.final_thermal_ev])
            seq.append({'max_step':h,'radau_T_K':T_ref,
                        'old_T_abs_err':abs(old.final_temperature_K-T_ref),
                        'new_T_abs_err':abs(new.final_temperature_K-T_ref),
                        'old_ne_abs_err':abs(old.final.electrons-ne_ref),
                        'new_ne_abs_err':abs(new.final.electrons-ne_ref),
                        'max_state_abs_error':float(np.max(abs(y_ref-v))),
                        'new_energy_residual_ev':new.energy_residual_ev,
                        'new_photon_residual':new.photon_reaction_residual,
                        'new_electron_residual':new.electron_reaction_residual,
                        'minimum_gas':min(new.final.as_tuple()),
                        'minimum_photon':min(new.photons_final),
                        'photo_events':new.photo_events,'recomb_events':new.recomb_events,
                        'T_K':new.final_temperature_K,'ne':new.final.electrons})
        orders=[math.log(a['new_T_abs_err']/b['new_T_abs_err'],2)
                for a,b in zip(seq[:-1],seq[1:]) if a['new_T_abs_err']>0 and b['new_T_abs_err']>0]
        results[name]={'reference_T_K':T_ref,'reference_ne':ne_ref,'radau_nfev':nfev,
                       'rows':seq,'new_T_order':orders}
    return {'domain':'case-A 10--24kK; no native source or photon retransport',
            'Grackle_provider_hash':p.sha256,'nstar_cm3':N_STAR,'H0_s':H0,
            'duration_ln_a':END,'results':results}

if __name__=='__main__':
    ans=run()
    Path(__file__).with_name('mixed_v6_results.json').write_text(json.dumps(ans,indent=2)+'\n')
    for k,v in ans['results'].items():
        print(k,'Tref',v['reference_T_K'],'errors-old/new',[(round(r['old_T_abs_err'],9),round(r['new_T_abs_err'],9)) for r in v['rows']], 'orders',v['new_T_order'],flush=True)
