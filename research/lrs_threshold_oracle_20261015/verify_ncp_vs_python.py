"""Independent Python vs NCP Rust retained-row readback (full Verner He II)."""
import csv
import json
from math import fsum
from pathlib import Path
from numpy.polynomial.legendre import leggauss

from lrs_threshold_oracle import Ray
from verner_angular import load_primary_fits, Absorber, propagate_verner, exact_angular_cutpoints

here=Path(__file__).resolve().parent
csvpath=here/"evidence"/"ncp_heii_sweep_20261015"/"ncp_full_sweep.csv"
rows=list(csv.DictReader(csvpath.open()))
assert len(rows)==6171
cross=[r for r in rows if int(r["has_cuts"])>0 and float(r["heii_abs_ref"])>1e-8]
assert len(cross)==533
choices=[rows[0],cross[0],
         max(cross,key=lambda r: float(r["plain24_abs_error"])),
         cross[-1],rows[-1]]
unique={r["idx"]:r for r in choices}
fit=load_primary_fits()["HeII"]
absorber=Absorber(fit,0.3)
points,weights=leggauss(64)

def independent_python_ref(e0,s,xend):
    cuts=exact_angular_cutpoints(e0,s,xend,[fit.threshold_ev])
    result=[]
    for a,b in zip(cuts[:-1],cuts[1:]):
        center=(a+b)/2.
        half=(b-a)/2.
        for u,w in zip(points,weights):
            r=propagate_verner(Ray(e0,float(center+half*u),1.,s),
                               [absorber],xend)
            result.append(.5*half*float(w)*r.absorbed_counts["HeII"])
    return fsum(result)

checks=[]
for row in unique.values():
    e0,s,end=(float(row[key]) for key in ("E0_ev","s_over_H","Xend"))
    true=independent_python_ref(e0,s,end)
    rust=float(row["heii_abs_ref"])
    absdiff=abs(true-rust)
    checks.append({"idx":int(row["idx"]),
                   "parameters":[e0,s,end],
                   "rust_reference":rust,
                   "python_reference":true,
                   "absolute_difference":absdiff,
                   "relative_difference":absdiff/max(true,1e-15),
                   "has_cuts":bool(int(row["has_cuts"]))})
    print("idx",row["idx"],"cut",row["has_cuts"],
          "Python",true,"Rust",rust,"absdiff",absdiff,flush=True)
    assert absdiff<3e-12, f"independent NCP/Python mismatch at {row['idx']}"
output=here/"evidence"/"ncp_heii_sweep_20261015"/"python_independent_crosscheck.json"
output.write_text(json.dumps({"status":"PASSED","rows":checks},sort_keys=True,indent=2)+"\n")
print("NCP independent Python comparison: PASSED",len(checks),"sampled cases")
