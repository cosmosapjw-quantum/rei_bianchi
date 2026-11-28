#!/usr/bin/env python3
"""Third cell checks independent of the staged interval/Taylor assembler.

Uses exact Fraction algebra, source endpoint byte values and all 2904 carries.
"""
from pathlib import Path
from fractions import Fraction as Q
import json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
ST=Q(6250000000)
def pexp_below(x):
    from math import factorial
    return sum(((-1)**(k+1)*x**k/Q(factorial(k)) for k in range(1,5)),Q(0))
def pexp_above(x):
    from math import factorial
    return sum(((-1)**(k+1)*x**k/Q(factorial(k)) for k in range(1,6)),Q(0))
def verify():
    info=json.loads((ROOT/"inputs/STAGED_SOURCE_IDENTITY.json").read_text())
    old=json.loads((ROOT/"inputs/PREV_TWO_CELL_VALIDATION.json").read_text())
    cert=json.loads((ROOT/"results/CERTIFICATE.json").read_text())
    d=json.loads((ROOT/"results/RESIDUAL_COUPLING.json").read_text())
    c=json.loads((ROOT/"inputs/ENDPOINT_MEMORY_R7.json").read_text())
    out=json.loads((ROOT/"results/THIRD_ENDPOINT_MEMORY.json").read_text())
    assert info["cell_s"]==["12500000000","18750000000"]
    assert cert["cell_s"]==info["cell_s"] and cert["stage"]=="HE18_C5"
    assert old["schema"]=="he18.c3.exact_rational_two_cell_review.v1"
    import sys
    sys.path.insert(0,str(ROOT/"src"))
    from warm_interval import WarmSource
    s=WarmSource()
    hh=json.loads((ROOT/"inputs/HH_P01_COMPARISON.json").read_text())
    g0=list(map(Q,hh["gas_initial_exact"]))
    rad=list(map(Q,hh["gas_radii"]))
    sc=[Q(1),Q(1),Q(1),Q(32)]
    e=[Q(z["rational"]) for z in cert["gas_error_components"]]
    usage=[(max(abs(y-g0[k]) for y in s.controls[k])+e[k])/rad[k] for k in range(4)]
    if not max(usage)<1:raise AssertionError("GLOBAL_GAS_BOX_ESCAPED")
    if not all(min(ctrl)>=0 for ctrl in s.controls[4:]):
        raise AssertionError("REFERENCE_PHOTON_NEGATIVE")
    whole=json.loads((ROOT/"results/whole_jets.json").read_text())
    if len(whole["nodes"])!=2904:raise AssertionError("WHOLE_NODE_COUNT")
    if cert["transparent_count"]!=sum(all(Q(z[0])==0 and Q(z[1])==0 for z in p["sigma"]) for p in whole["nodes"]):
        raise AssertionError("TRANSPARENT_NODE_MISMATCH")
    assert cert["first_initial_match"] is True
    assert cert["next_physical_cell_incoming_included"] is True
    assert Q(cert["gain"]["rational"])<1
    assert Q(cert["temperature_error_K"]["rational"])>=0
    with np.load(ROOT/"inputs/FIXED_REFERENCE.npz",allow_pickle=False) as ref, np.load(ROOT/"inputs/P01_STATE.npz",allow_pickle=False) as orig:
        assert len(ref["left"])==len(ref["right"])==2908
        assert all(Q.from_float(float(v))==Q.from_float(float(w)) for v,w in zip(ref["left"],orig["states"][:2908,2]))
        assert all(Q.from_float(float(v))==Q.from_float(float(w)) for v,w in zip(ref["right"],orig["states"][:2908,3]))
    assert c["source_interval_s"]==[str(ST),str(2*ST)]
    ep=list(map(Q,c["photon_error_end_raw_exact"]));eg=list(map(Q,c["gas_error_end_scaled"]))
    assert len(ep)==2904 and len(eg)==4
    assert len(d["photon"])==len(d["B_scaled"])==len(d["C_scaled"])==2904
    assert all(x>=0 for x in ep+eg)
    assert [Q(x) for x in cert["incoming_gas_scaled"]]==eg
    carry=[ST*sum((Q(d["B_scaled"][j][k])*ep[j] for j in range(2904)),Q(0)) for k in range(4)]
    assert carry==list(map(Q,cert["incoming_photon_to_gas_scaled"]))
    incoming=out["outgoing_photon_error_end_raw_exact"]
    assert len(incoming)==2904 and out["nonzero_count"]==2904
    assert out["incoming_second_cell_sha256"]==info["input_previous_end_sha256"]
    raw=list(map(Q,incoming))
    gas_scale=[Q(1),Q(1),Q(1),Q(32)]
    propagated=[Q(x["rational"])/gas_scale[k] for k,x in enumerate(cert["gas_error_components"])]
    assert propagated==list(map(Q,out["scaled_gas_error_end_exact"]))
    assert out["source_interval_s"]==info["cell_s"]
    cadd=[ST*sum((Q(d["C_scaled"][j][k])*propagated[k] for k in range(4)),Q(0)) for j in range(2904)]
    residual=[Q(d["photon"][j]["integral"]) for j in range(2904)]
    assert all(raw[j]==ep[j]+cadd[j]+residual[j] for j in range(2904))
    assert sum(raw,Q(0))==Q(out["incoming_sum"])+Q(out["added_coupling_sum"])+Q(out["added_residual_sum"])
    pp=[[Q(a) for a in row] for row in cert["scaled_P"]]
    assert len(pp)==4 and all(len(r)==4 for r in pp)
    assert all(x>=0 for row in pp for x in row)
    assert max(sum(row,Q(0)) for row in pp)==Q(cert["gain"]["rational"])<1
    forcG=[Q(x["rational"]) for x in cert["gas_integral_scaled"]]
    forcP=[Q(x["rational"]) for x in cert["photon_forcing_scaled"]]
    lhs=[[Q(i==j)-pp[i][j] for j in range(4)] for i in range(4)]
    rhs=[eg[k]+carry[k]+forcG[k]+forcP[k] for k in range(4)]
    assert all(sum((lhs[i][j]*propagated[j] for j in range(4)),Q(0))==rhs[i] for i in range(4))
    tau2=list(map(Q,old["two_cell_tau_interval_exact"]))
    tau3=list(map(Q,cert["true_depth_interval"]))
    three=[tau2[i]+tau3[i] for i in range(2)]
    assert Q(0)<three[0]<three[1]<Q(1)
    probability=[pexp_below(three[0]),pexp_above(three[1])]
    assert Q(0)<probability[0]<probability[1]<Q(1)
    return dict(schema="he18.c5.third_cell_exact_review.v1",status="SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES",
        checks={k:True for k in (
            "previous_two_cells_exact","adjacent_global_clock","source_dyadic_endpoints_2908",
            "nonzero_incoming_gas4_and_photon2904","positive_gas_comparison_inverse",
            "all_2904_photon_error_components_carried","exact_resolvent_equation",
            "positive_radii_and_photon_states","strictly_positive_third_depth",
            "three_cell_tau_additive","three_cell_probability_monotone")},
        third_cell_tau_exact=list(map(str,tau3)),three_cell_tau_exact=list(map(str,three)),
        three_cell_probability_exact=list(map(str,probability)),
        global_gas_box_fraction_upper=str(max(usage)),
        photon_nodes=2904,transparent_nodes=cert["transparent_count"],
        source_rhs_ODE_calls=0,
        provider_roundoff_certification=None,physical_source_model_uncertainty=None,
        native_all_16_cells_certified=False)
if __name__=="__main__":
    result=verify();dest=ROOT/"results/THREE_CELL_VALIDATION.json"
    if dest.exists():raise SystemExit("REFUSE_OVERWRITE")
    dest.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in ("checks",)},indent=2))
