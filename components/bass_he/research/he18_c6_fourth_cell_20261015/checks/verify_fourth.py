#!/usr/bin/env python3
"""Source-scoped exact-rational fourth warm saved-cell verification.

This audits the assembled result and every carried photon component, without
replacing mpmath.iv or declaring a formal independently proved enclosure.
"""
from pathlib import Path
from fractions import Fraction as Q
from decimal import Decimal,localcontext,ROUND_CEILING,ROUND_FLOOR
import hashlib,json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
STEP=Q(6250000000)
def probability_lower(x):
    from math import factorial
    return sum(((-1)**(k+1)*x**k/Q(factorial(k)) for k in range(1,5)),Q(0))
def probability_upper(x):
    from math import factorial
    return sum(((-1)**(k+1)*x**k/Q(factorial(k)) for k in range(1,6)),Q(0))
def directed(x,lower):
    x=Q(x)
    with localcontext() as c:
        c.prec=45;c.rounding=ROUND_FLOOR if lower else ROUND_CEILING
        return str(Decimal(x.numerator)/Decimal(x.denominator))
def verify():
    info=json.loads((ROOT/"inputs/STAGED_SOURCE_IDENTITY.json").read_text())
    previous=json.loads((ROOT/"inputs/PREV_THREE_CELL_VALIDATION.json").read_text())
    cert=json.loads((ROOT/"results/CERTIFICATE.json").read_text())
    detail=json.loads((ROOT/"results/RESIDUAL_COUPLING.json").read_text())
    photon=json.loads((ROOT/"inputs/ENDPOINT_MEMORY_R7.json").read_text())
    out=json.loads((ROOT/"results/FOURTH_ENDPOINT_MEMORY.json").read_text())
    assert info["stage"]=="HE18_C6_FOURTH_CELL"
    assert info["cell_s"]==["18750000000","25000000000"]
    assert previous["schema"]=="he18.c5.third_cell_exact_review.v1"
    assert cert["cell_s"]==info["cell_s"] and cert["stage"]=="HE18_C6"
    assert cert["first_initial_match"] and cert["next_physical_cell_incoming_included"]
    prev_raw=ROOT/"inputs/PREV_THREE_CELL_VALIDATION.json"
    assert hashlib.sha256(prev_raw.read_bytes()).hexdigest()==info["prev_certificate_sha256"]
    with np.load(ROOT/"inputs/FIXED_REFERENCE.npz",allow_pickle=False) as fixed,\
         np.load(ROOT/"inputs/P01_STATE.npz",allow_pickle=False) as source:
        assert len(fixed["left"])==len(fixed["right"])==2908
        assert all(Q.from_float(float(a))==Q.from_float(float(b))
                   for a,b in zip(fixed["left"],source["states"][:2908,3]))
        assert all(Q.from_float(float(a))==Q.from_float(float(b))
                   for a,b in zip(fixed["right"],source["states"][:2908,4]))
    import sys
    sys.path.insert(0,str(ROOT/"src"))
    from warm_interval import WarmSource
    warm=WarmSource()
    hh=json.loads((ROOT/"inputs/HH_P01_COMPARISON.json").read_text())
    g0=list(map(Q,hh["gas_initial_exact"]))
    radii=list(map(Q,hh["gas_radii"]))
    err=[Q(t["rational"]) for t in cert["gas_error_components"]]
    usage=max((max(abs(x-g0[k]) for x in warm.controls[k])+err[k])/radii[k] for k in range(4))
    assert usage<1
    assert all(min(ctrl)>=0 for ctrl in warm.controls[4:])
    incoming_gas=list(map(Q,photon["gas_error_end_scaled"]))
    incoming_photon=list(map(Q,photon["photon_error_end_raw_exact"]))
    assert photon["source_interval_s"]==["12500000000","18750000000"]
    assert len(incoming_gas)==4 and len(incoming_photon)==2904
    assert all(x>=0 for x in incoming_gas+incoming_photon)
    assert [Q(x) for x in cert["incoming_gas_scaled"]]==incoming_gas
    assert len(detail["photon"])==len(detail["C_scaled"])==len(detail["B_scaled"])==2904
    assert cert["transparent_count"]>=0
    whole=json.loads((ROOT/"results/whole_jets.json").read_text())
    assert len(whole["nodes"])==2904
    assert sum(all(Q(c[0])==0 and Q(c[1])==0 for c in node["sigma"])
               for node in whole["nodes"])==cert["transparent_count"]
    scales=[Q(1),Q(1),Q(1),Q(32)]
    coupled=[STEP*sum((Q(detail["B_scaled"][j][i])*incoming_photon[j]
                       for j in range(2904)),Q(0)) for i in range(4)]
    assert coupled==list(map(Q,cert["incoming_photon_to_gas_scaled"]))
    scaled_err=[err[i]/scales[i] for i in range(4)]
    P=[[Q(x) for x in row] for row in cert["scaled_P"]]
    assert len(P)==4 and all(len(row)==4 for row in P)
    assert all(x>=0 for row in P for x in row)
    assert max(sum(row,Q(0)) for row in P)==Q(cert["gain"]["rational"])<1
    rhs=[incoming_gas[i]+coupled[i]
         +Q(cert["gas_integral_scaled"][i]["rational"])
         +Q(cert["photon_forcing_scaled"][i]["rational"]) for i in range(4)]
    for i in range(4):
        assert sum(((Q(i==j)-P[i][j])*scaled_err[j] for j in range(4)),Q(0))==rhs[i]
    outs=list(map(Q,out["outgoing_photon_error_end_raw_exact"]))
    assert len(outs)==2904 and out["incoming_components"]==2904
    assert out["source_interval_s"]==info["cell_s"]
    assert out["input_prev_C5_sha256"]==info["prev_photon_error_sha256"]
    assert out["outgoing_nonzero_count"]==sum(x>0 for x in outs)
    current=list(map(Q,out["scaled_gas_error_end_exact"]))
    assert current==scaled_err
    for j in range(2904):
        add=STEP*sum((Q(detail["C_scaled"][j][k])*current[k]
                      for k in range(4)),Q(0))
        r=Q(detail["photon"][j]["integral"])
        assert add>=0 and r>=0 and outs[j]==incoming_photon[j]+add+r
    assert sum(outs,Q(0))==(Q(out["incoming_sum"])
              +Q(out["added_coupling_sum"])+Q(out["added_residual_sum"]))
    third_tau=list(map(Q,previous["three_cell_tau_exact"]))
    fourth_tau=list(map(Q,cert["true_depth_interval"]))
    total=[third_tau[i]+fourth_tau[i] for i in range(2)]
    assert 0<total[0]<total[1]<1
    P4=[probability_lower(total[0]),probability_upper(total[1])]
    assert 0<P4[0]<P4[1]<1
    return {
      "schema":"he18.c6.fourth_cell_exact_review.v1",
      "status":"SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES",
      "checks":{x:True for x in (
        "three_cell_predecessor_hash","fourth_global_time_and_dyadic",
        "original_gas_global_box","all_2904_photon_intervals_and_zeros",
        "inherited_four_gas_componentwise","positive_resolvent_exact",
        "full_2904_photon_carry_exact","strict_photon_positivity",
        "fourth_column_bound","four_cell_tau_positive",
        "four_cell_probability_taylor_bounds")},
      "fourth_tau_exact":list(map(str,fourth_tau)),
      "four_cell_tau_exact":list(map(str,total)),
      "four_cell_probability_exact":list(map(str,P4)),
      "four_cell_tau_outward":[directed(total[0],True),directed(total[1],False)],
      "four_cell_probability_outward":[directed(P4[0],True),directed(P4[1],False)],
      "global_gas_box_fraction_upper":str(usage),
      "photon_nodes":2904,"transparent_nodes":cert["transparent_count"],
      "source_ODE_calls":0,"native_roundoff":None,"full_16_cell_admitted":False,
      "interval_library_independent_verification":False,
    }
if __name__=="__main__":
    target=ROOT/"results/FOUR_CELL_VALIDATION.json"
    if target.exists():raise SystemExit("REFUSE_OVERWRITE")
    result=verify()
    target.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in
      ("checks","four_cell_tau_exact","four_cell_probability_exact",
       "fourth_tau_exact","global_gas_box_fraction_upper")},indent=2))
