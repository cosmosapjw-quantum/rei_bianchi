"""Convergence matrix for manufactured birth/opacity timings and neutral feedback."""
from __future__ import annotations
import json,csv,platform,sys,hashlib
from pathlib import Path
import numpy as np
import scipy
sys.path.insert(0,str(Path(__file__).resolve().parent/"src"))
from birth_opacity_clock import *

HERE=Path(__file__).resolve().parent
out=HERE/'evidence';out.mkdir(exist_ok=True)
ns=(8,16,32,64,128,256)
problems={
 'both_change':Experiment(),
 'birth_gradient_only':Experiment(opacity_slope=0.),
 'opacity_gradient_only':Experiment(source_slope=0.),
 'constant_source_rate':Experiment(opacity_slope=0.,source_slope=0.),
 'bounded_stiff_probe':Experiment(opacity0=38.,t_end=.4,source0=.45),
}
rows=[]; summary={}
for name,p in problems.items():
 ref=radau(p)
 exact_linear=independent_exact_photon(p)
 for mode in MODES:
  prior=None; errs=[]
  for n in ns:
   r=evolve(p,n,mode)
   e=abs(r.photons-ref[0])
   lin=linear_frozen_midpoint(p,n,mode)
   ell=ledgers(r,p)
   row={'case':name,'mode':mode,'N':n,'h':p.t_end/n,
        'N_end':r.photons,'HI_end':r.neutral,'HII_end':r.ionized,
        'births':r.births,'absorptions':r.absorptions,
        'photon_error_vs_Radau':e,
        'ion_error_vs_Radau':abs(r.ionized-(p.neutral0-ref[1])),
        'birth_error_vs_Radau':abs(r.births-ref[2]),
        'linear_N_error_vs_exact':abs(lin[0]-exact_linear[0]),
        'max_exposure_proxy':r.max_exposure,
        'max_ledger_abs':max(abs(ell[k]) for k in ['photons','neutral_atoms','ion_reactions','energy_ev']),
        'photon_error_order':None if prior is None else slope(prior,e)}
   prior=e;errs.append(e);rows.append(row)
  last=rows[-1]
  summary[f'{name}|{mode}']={'last_order':last['photon_error_order'],
      'finest_abs_error':errs[-1], 'first_abs_error':errs[0],
      'last_exposure':last['max_exposure_proxy']}
with (out/'convergence.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
report={'schema':'rei.v9.clock.isolation.1',
        'scientific_status':'CONDITIONAL_SMOOTH_MANUFACTURED_ONLY',
        'native_status':'NOT_RUN',
        'parent':'PR168 c02fb3492b99b79c8b2e3bae1a6183510ff1df9b',
        'setting':{'X':'ln(a/a0)','N':'photons per total H','M':'HI per total H','energy_ev':80,'chi_ev':13.6},
        'environment':{'python':sys.version.split()[0], 'numpy':np.__version__,'scipy':scipy.__version__},
        'cases':{k:p.__dict__ for k,p in problems.items()},
        'summary':summary,'rows':rows,
        'limitation':'Fixed-energy toy source, no physical source-age, no Grackle, no transport redshift; do not assign full PR150 BE causality from this only.'}
(out/'convergence.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print(json.dumps({'rows':len(rows),'significant':{k:v for k,v in summary.items() if k.startswith('both_change')}},indent=2))
