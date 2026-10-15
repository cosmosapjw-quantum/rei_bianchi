"""Compare equal-budget unpartitioned vs threshold-aligned angular quadrature.

All calls evaluate the *full Verner fits*, not the earlier E^-3 cancellation.
"""
from __future__ import annotations
import json
from math import fsum
from pathlib import Path
from time import perf_counter
from numpy.polynomial.legendre import leggauss

from lrs_threshold_oracle import Ray
from verner_angular import Absorber, angular_verner, exact_angular_cutpoints, load_primary_fits, propagate_verner

f=load_primary_fits()
species=tuple(Absorber(f[name],strength) for name,strength in
              (("HI",2.),("HeI",.7),("HeII",.3)))


def fixed_angular(s:float,xend:float,nodes:int,split:bool)->dict:
    cuts=(exact_angular_cutpoints(100.,s,xend,(sp.fit.threshold_ev for sp in species))
          if split else (-1.,1.))
    mu,w=leggauss(nodes)
    values=[]
    begin=perf_counter()
    for l,r in zip(cuts[:-1],cuts[1:]):
        mid=(l+r)/2
        half=(r-l)/2
        for t,weight in zip(mu,w):
            direction=float(mid+half*t)
            rad=propagate_verner(Ray(100.,direction,1.,s),species,xend)
            ww=.5*float(half*weight)
            values.append((ww*rad.photons_end,
                           ww*rad.photons_end*rad.energy_end_ev,
                           ww*rad.photons_end*rad.energy_end_ev*rad.mu_end**2,
                           ww*rad.absorbed_counts["HeII"],
                           ww*rad.heat_ev["HeII"],
                           ww*rad.redshift_work_ev))
    rows=[fsum(v[i] for v in values) for i in range(6)]
    return {"split":split,"n_per_panel":nodes,
            "n_rays":len(values),"n_panels":len(cuts)-1,
            "survivors":rows[0],"pi_over_u":(3*rows[2]-rows[1])/(2*rows[1]),
            "heii_count":rows[3],"heii_heat_ev":rows[4],
            "redshift_shear_work_ev":rows[5],
            "wall_s":perf_counter()-begin,"cuts":cuts}


evidence=[]
for s in (-.03,.03):
    for xend in (.61,.8):
        ref=fixed_angular(s,xend,64,True)
        trials=[fixed_angular(s,xend,n,False) for n in (8,16,24,32,64,128)]
        trials += [fixed_angular(s,xend,n,True) for n in (4,8,16,32)]
        for row in trials:
            row["heii_abs_relative_error"]=abs(row["heii_count"]-ref["heii_count"])/abs(ref["heii_count"])
            row["pi_absolute_error"]=abs(row["pi_over_u"]-ref["pi_over_u"])
        entry={"s_over_h":s,"xend":xend,"reference":ref,"trials":trials}
        evidence.append(entry)
        line=[r for r in trials if r["n_rays"]==24]
        print(f"s/H={s:+.2f} X={xend}: cuts={ref['cuts']}")
        for row in line:
            print("  24 rays split:",row["split"],"HeII_relerr:",f'{row["heii_abs_relative_error"]:.5e}',
                  "Pi_abs_err:",f'{row["pi_absolute_error"]:.5e}',"wall_s",round(row["wall_s"],4),flush=True)

folder=Path(__file__).resolve().parent/"evidence"
(folder/"verner_angular_convergence.json").write_text(json.dumps({
    "label":"Numerically checked: conditional Verner cross-section angular study",
    "donor_primary_url":"https://www.pa.uky.edu/~verner/dima/photo//photo.dat",
    "comparison_reference":"piecewise fixed 64-point Gauss-Legendre on each critical interval",
    "comparisons":evidence},indent=2)+"\n")
