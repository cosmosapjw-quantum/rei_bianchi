"""Matched-density, comparable-error wall-time measurement; local only."""
from bootstrap_v6 import setup
setup()
import json
from pathlib import Path
from time import perf_counter
from statistics import median
from recomb_dominated_v5 import INITIAL,N_STAR,H0,END,T0,rays
from recomb_thermal import evolve_thermal as original
from recomb_thermal_midpoint_v6 import evolve_thermal as midpoint
from rate_table import CaseARates


def run():
    provider=CaseARates()
    ref=14744.794774003176
    rr=rays(0.,0.)
    records=[]
    for name,method,h in (('V5_frozen_initial_temperature',original,1e-5),
                          ('V6_implicit_temperature_midpoint',midpoint,.0025),
                          ('V6_implicit_temperature_midpoint',midpoint,.00125)):
        elapsed=[]
        for _ in range(5):
            t=perf_counter()
            r=method(rr,INITIAL,END,temperature_initial_K=T0,max_step=h,
                     atomic_rates=provider,n_star_cm3=N_STAR,h0_s=H0)
            elapsed.append(perf_counter()-t)
        records.append({'method':name,'max_step':h,'nsteps':r.steps,
                        'abs_T_err_K':abs(r.final_temperature_K-ref),
                        'wall_s_median':median(elapsed),'wall_s_samples':elapsed,
                        'energy_residual_ev':r.energy_residual_ev})
    return {'environment':'ChatGPT sandbox CPython; no NCP execution or native Rust timing',
            'reference_T_K':ref,'n_star_cm3':N_STAR,'H0_s':H0,
            'records':records,'speedup_v5_1e5_vs_v6_0p0025':
            records[0]['wall_s_median']/records[1]['wall_s_median'],
            'speedup_v5_1e5_vs_v6_0p00125':
            records[0]['wall_s_median']/records[2]['wall_s_median']}
if __name__=='__main__':
    data=run()
    Path(__file__).with_name('cost_v6_results.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data,indent=2))
