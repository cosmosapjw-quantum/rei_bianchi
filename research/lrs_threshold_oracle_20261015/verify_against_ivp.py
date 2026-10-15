"""Independent direct cross-section ODE and angular convergence verification.

SciPy/Numpy are verification dependencies, not dependencies of the oracle.
"""
from __future__ import annotations
import json
from pathlib import Path
from math import exp, sqrt
import numpy as np
from scipy.integrate import solve_ivp
from lrs_threshold_oracle import Ray, Species, propagate, angular_moments

species=(Species("HI",13.5984,2.),
         Species("HeI",24.5874,.7),
         Species("HeII",54.4178,.3))
ray=Ray(100.,.61,1.,.07)
end=.8
ours=propagate(ray,species,end)
edges=sorted({0.,end,*ours.threshold_events.values()})
# state: N, three A_i, three thermal Q_i, expansion+shear work
y=np.zeros(8,dtype=float)
y[0]=1.
for a,b in zip(edges[:-1],edges[1:]):
    midpoint=ray.geometry((a+b)/2)[0]
    active=[midpoint>sp.threshold_ev for sp in species]
    def rhs(x,y):
        energy,mu,_=ray.geometry(x)
        # Deliberately evaluate n(X)*sigma(E(X)) directly,
        # independently of the factorization implemented by the oracle.
        k=[(sp.opacity_at_threshold*exp(-3*x)*
            (sp.threshold_ev/energy)**3) if enabled else 0.
           for sp,enabled in zip(species,active)]
        absorption=np.array(k)*y[0]
        dy=np.empty_like(y)
        dy[0]=-float(np.sum(absorption))
        dy[1:4]=absorption
        dy[4:7]=absorption*np.maximum(energy-np.array([sp.threshold_ev for sp in species]),0.)
        dy[7]=y[0]*energy*(1.+ray.s_over_h*(3*mu*mu-1.))
        return dy
    sol=solve_ivp(rhs,(a,b),y,method="DOP853",rtol=2e-13,atol=2e-14,max_step=.05)
    if not sol.success:
        raise RuntimeError(sol.message)
    y=sol.y[:,-1]

ours_observables=np.array([ours.photons_end,
                          *(ours.absorbed_counts[sp.name] for sp in species),
                          *(ours.heat_ev[sp.name] for sp in species),
                          ours.redshift_work_ev])
direct_abs_error=np.abs(y-ours_observables)
relative_scale=np.maximum(1.,abs(y))
max_rel=float(np.max(direct_abs_error/relative_scale))
if max_rel>1e-9:
    raise AssertionError(f"independent ODE discrepancy {max_rel}")

angular=[]
for xend in (.61,.8):
    for signed in (-.03,.03):
        rows=[]
        for n in (8,16,32,64,128):
            mus, weights=np.polynomial.legendre.leggauss(n)
            rays=[propagate(Ray(100.,float(mu),float(w)/2.,signed),
                            species,xend) for mu,w in zip(mus,weights)]
            moments=angular_moments(rays)
            rows.append({
                "n_mu":n,
                "pi_over_u":moments.pi_ev/moments.energy_ev,
                "heii_absorbed":sum(r.absorbed_counts["HeII"] for r in rays),
                "photons_end":sum(r.photons_end for r in rays)
            })
        ref=rows[-1]
        for r in rows:
            r["pi_rel_error_vs_128"]=abs(r["pi_over_u"]-ref["pi_over_u"])/max(abs(ref["pi_over_u"]),1e-14)
            r["heii_rel_error_vs_128"]=abs(r["heii_absorbed"]-ref["heii_absorbed"])/max(abs(ref["heii_absorbed"]),1e-14)
        angular.append({"x_end":xend,"s_over_h":signed,"resolutions":rows})

payload={
    "claim":"independent conditional reference verification; no production admission",
    "direct_cross_section_ivp":{
        "initial_ray":{"E0_ev":100.,"mu0":.61,"s_over_h":.07},
        "x_end":end,
        "x_thresholds":ours.threshold_events,
        "observables_order":["survivors","absorbed_HI","absorbed_HeI","absorbed_HeII",
                             "heat_HI_ev","heat_HeI_ev","heat_HeII_ev","redshift_shear_work_ev"],
        "reference_direct_ode":y.tolist(),
        "factorized_oracle":ours_observables.tolist(),
        "max_abs_error":float(direct_abs_error.max()),
        "max_scaled_error":max_rel,
        "ode_method":"DOP853 rtol=2e-13 atol=2e-14, event split"
    },
    "angular_convergence":angular
}
folder=Path(__file__).resolve().parent/"evidence"
folder.mkdir(exist_ok=True)
(folder/"independent_ivp_angular_convergence.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
print("IVP max absolute",payload["direct_cross_section_ivp"]["max_abs_error"])
print("IVP max scaled",max_rel)
for entry in angular:
    n8=entry["resolutions"][0]
    n64=entry["resolutions"][-2]
    print("threshold x/s",entry["x_end"],entry["s_over_h"],
          "n8 Pi_rel",n8["pi_rel_error_vs_128"],
          "n8 HeII_rel",n8["heii_rel_error_vs_128"],
          "n64 Pi_rel",n64["pi_rel_error_vs_128"],
          "n64 HeII_rel",n64["heii_rel_error_vs_128"])
