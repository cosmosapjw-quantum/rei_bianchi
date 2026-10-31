"""Read-only independent numerical consistency check for 2026-10-31 CCC6 result."""
import sys, pathlib, json, math
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import run as m
from scipy.integrate import cumulative_trapezoid
arr,chem,th,pl,coul,data,owner,meta=m.input_load()
energy=m.energy_nodes(data,2100)
sigma=m.sigma_samples(data,owner,energy)
checks=[]
for epoch in [0,20,60,80,128,160,192]:
 j=max(epoch-1,0)
 nH=float(coul.n_b_m3.iloc[epoch]*1e-6*th.nHref_over_nb.iloc[j])
 XH=float(chem.xHII_start.iloc[0]) if epoch==0 else float(chem.xHII_end.iloc[j])
 XHe=float(chem.xHeI_end.iloc[j]); yHe=float(chem.helium_per_H_ref.iloc[j])
 nHI=nH*(1-XH);nHeI=nH*yHe*XHe
 ne=float(coul.n_e_m3.iloc[epoch]*1e-6)
 P,nu,h=m.first_probs(energy,sigma,ne,nHI,nHeI)
 # Independent integral of full selected hazard, using explicit energy-cell area.
 total=cumulative_trapezoid(np.sum(h,axis=0),energy,initial=0)
 direct=-np.expm1(-total)
 deviation=float(np.max(abs(P[:6].sum(axis=0)-direct)))
 closure=float(np.max(abs(P.sum(axis=0)-1)))
 # Diagnostic selected stochastic first collision obeys 0<=P<=1 for all energy nodes.
 assert deviation<2e-13,(epoch,deviation)
 assert closure<2e-13,(epoch,closure)
 assert min(P.ravel())>=-1e-14
 checks.append(dict(epoch=epoch,z=float(coul.z.iloc[epoch]),ne_full_cm3=ne,p_first_55eV=float(np.interp(55,energy,P[:6].sum(axis=0))),max_direct_integral_discrepancy=deviation,max_probability_closure=closure))
result={"scope":"ONE same-author independent quadrature check; full CCC6 subset and frozen BASS193", "checked_epochs":len(checks),"pointwise_energy_nodes":len(energy),"checks":checks,"max_discrepancy":max(z['max_direct_integral_discrepancy'] for z in checks),"max_closure":max(z['max_probability_closure'] for z in checks),"new_ivps":0,"independent_author":"NOT_RUN"}
(ROOT/'evidence'/'ADVERSARIAL_NUMERICAL_CHECK.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
