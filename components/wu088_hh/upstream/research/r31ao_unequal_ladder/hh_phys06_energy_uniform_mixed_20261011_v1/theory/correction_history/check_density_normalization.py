"""Exact replay specification of the already performed scalar source check.

This file was saved after the original inline command; it has not itself been
invoked again. No scientific suite, native endpoint, root or IVP is called.
"""
from pathlib import Path
from fractions import Fraction as Q
import json

p = Path("/workspace/scratch/198b9c7581be/HH_NEXT_20261011_intake/ncp_source/ARCHIVED_COMMON_SEED_POINT_INPUT.json")
j = json.loads(p.read_text())
f = j["constants_from_identity_words"]["fHe"]
for tag, nh in [("archived_time_density", j["point_derived_n_H_cm3"])] + [
    ("proposed_endpoint_density_dt_" + str(z["dt_s"]), z["n_H_cm3"])
    for z in j["point_derived_endpoint_densities_not_evolved"]
]:
    nhe = nh * f
    delta = Q(f) - Q(nhe) / Q(nh)
    print(json.dumps({
        "case": tag,
        "nH_hex": nh.hex(),
        "stage_fHe_hex": f.hex(),
        "stored_model_nHe_hex": nhe.hex(),
        "delta_f_stage_minus_model_exact_ratio": str(delta),
        "delta_f_float_for_display": float(delta),
        "is_exactly_zero": delta == 0,
        "scope": "Source-construction scalar arithmetic, no endpoint or root execution"
    }))
