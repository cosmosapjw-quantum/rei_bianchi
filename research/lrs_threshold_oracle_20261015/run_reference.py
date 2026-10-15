"""Write a deterministic, light-weight signed-shear Bianchi ray comparison."""
import json
from pathlib import Path
from lrs_threshold_oracle import GAUSS8, Ray, Species, propagate, angular_moments

species=(Species("HI",13.5984,2.),
         Species("HeI",24.5874,.7),
         Species("HeII",54.4178,.3))

rows=[]
for s in (-.03,0.,.03):
    results=[propagate(Ray(100.,mu,.5*weight,s),species,.8)
             for mu,weight in GAUSS8]
    moments=angular_moments(results)
    rows.append({
        "s_over_h":s,
        "Sigma":3**.5*abs(s),
        "N_surviving":sum(r.photons_end for r in results),
        "N_absorbed":{sp.name:sum(r.absorbed_counts[sp.name] for r in results)
                      for sp in species},
        "photoheat_ev":{sp.name:sum(r.heat_ev[sp.name] for r in results)
                         for sp in species},
        "redshift_shear_work_ev":sum(r.redshift_work_ev for r in results),
        "surviving_energy_ev":moments.energy_ev,
        "pi_over_u":moments.pi_ev/moments.energy_ev,
        "max_number_residual":max(abs(r.photon_number_residual) for r in results),
        "max_energy_residual_ev":max(abs(r.energy_residual_ev) for r in results),
        "total_substeps":sum(r.substeps for r in results),
    })

evidence=Path(__file__).resolve().parent/"evidence"
evidence.mkdir(exist_ok=True)
payload={
    "status":"NUMERICALLY_CHECKED_CONDITIONAL_TOY",
    "contract":"fixed neutral a^-3, thresholded E^-3 opacity, prescribed H/H0",
    "parent_commit":"0fcb2dddf5de6b583c2e00f150abff0b2afb6315",
    "grid":"8-point Gauss-Legendre initial mu, 8-node nested ray quadrature",
    "rows":rows,
}
(evidence/"results.json").write_text(json.dumps(payload,sort_keys=True,indent=2)+"\n")
print(json.dumps(rows,sort_keys=True,indent=2))
