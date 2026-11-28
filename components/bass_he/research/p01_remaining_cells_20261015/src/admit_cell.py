#!/usr/bin/env python3
"""Exact rational photon propagation and scientific admission per saved P01 cell.

Bounded, independently checkable source-scoped verifier, not a formal theorem
about mpmath.iv or a physical EoR abundance-history computation.
"""
from __future__ import annotations
from pathlib import Path
import argparse, hashlib, json, sys
from decimal import Decimal,localcontext,ROUND_CEILING,ROUND_FLOOR
from fractions import Fraction as Q
from math import factorial

import numpy as np
if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(250000)

from stage_cell import STEP,WORDS,DASH,sha

def directed(v,lower):
    v=Q(v)
    with localcontext() as context:
        context.prec=45
        context.rounding=ROUND_FLOOR if lower else ROUND_CEILING
        return str(Decimal(v.numerator)/Decimal(v.denominator))

def collision_lower(tau):
    return sum(((-1)**(k+1)*tau**k/Q(factorial(k)) for k in range(1,5)),Q(0))
def collision_upper(tau):
    return sum(((-1)**(k+1)*tau**k/Q(factorial(k)) for k in range(1,6)),Q(0))

def propagate_and_verify(root:Path,n:int)->dict:
    if not 8<=n<=16:raise ValueError("CELL_OUTSIDE_8_TO_16")
    root=root.resolve();p=n-1
    dest=root/"results"/f"{WORDS[n].upper()}_CELL_VALIDATION.json"
    out_file=root/"results"/f"{DASH[n]}_ENDPOINT_MEMORY.json"
    if dest.exists() or out_file.exists():
        raise ValueError("REFUSE_OVERWRITE_CERTIFIED_ERROR")
    meta=json.loads((root/"inputs/CONTINUATION_BINDING.json").read_text())
    if meta["cell"]!=n or meta["cell_s"]!=[str((n-1)*STEP),str(n*STEP)]:
        raise ValueError("INCORRECT_BINDING_OR_CLOCK")
    previous_file=root/"inputs/PREV_CELL_VALIDATION.json"
    old=json.loads(previous_file.read_text())
    if sha(previous_file)!=meta["prev_cert_sha256"]:raise ValueError("PREV_CERT_MUTATED")
    if old["status"]!="SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES":
        raise ValueError("PREV_NOT_ADMITTED")
    if old["schema"]!=f"he18.c{p+2}.{DASH[p].lower()}_cell_exact_review.v1":
        raise ValueError("PREV_SCHEMA_MISMATCH")
    source_c=json.loads((root/"results/CERTIFICATE.json").read_text())
    tensor=json.loads((root/"results/RESIDUAL_COUPLING.json").read_text())
    incoming_path=root/"inputs/ENDPOINT_MEMORY_R7.json"
    if sha(incoming_path)!=meta["incoming_adapter_sha256"]:
        raise ValueError("INPUT_ERROR_ADAPTER_MUTATED")
    incoming=json.loads(incoming_path.read_text())
    if incoming["source_interval_s"]!=[str((n-2)*STEP),str((n-1)*STEP)]:
        raise ValueError("INCOMING_SOURCE_CLOCK")
    if source_c["cell_s"]!=meta["cell_s"] or source_c["stage"]!=f"HE18_C{n+2}":
        raise ValueError("ASSEMBLY_NOT_THIS_CELL")
    if not source_c["first_initial_match"] or not source_c["next_physical_cell_incoming_included"]:
        raise ValueError("REFERENCE_OR_INCLUSION_FAILED")
    assert n<=16
    with np.load(root/"inputs/FIXED_REFERENCE.npz",allow_pickle=False) as fixed,\
         np.load(root/"inputs/P01_STATE.npz",allow_pickle=False) as original:
        assert fixed["left"].shape==(2908,) and fixed["right"].shape==(2908,)
        assert np.array_equal(fixed["left"],original["states"][:2908,n-1])
        assert np.array_equal(fixed["right"],original["states"][:2908,n])
        assert original["states"].shape[1]==17
    ep=list(map(Q,incoming["photon_error_end_raw_exact"]))
    eg=list(map(Q,incoming["gas_error_end_scaled"]))
    if len(ep)!=2904 or len(eg)!=4:raise ValueError("INCOMING_2904_OR_4_LENGTH")
    if any(x<0 for x in ep+eg):raise ValueError("NEGATIVE_INCOMING_RADIUS")
    if not all(len(tensor[key])==2904 for key in ("photon","B_scaled","C_scaled")):
        raise ValueError("WRONG_RAY_COUPLING_LENGTH")
    error=[Q(x["rational"]) for x in source_c["gas_error_components"]]
    scales=[Q(1),Q(1),Q(1),Q(32)]
    gas_scaled=[error[j]/scales[j] for j in range(4)]
    if [Q(x) for x in source_c["incoming_gas_scaled"]]!=eg:
        raise ValueError("INCOMING_GAS_CHANGED")
    coupling=[Q(STEP)*sum((Q(tensor["B_scaled"][j][i])*ep[j] for j in range(2904)),Q(0)) for i in range(4)]
    if coupling!=list(map(Q,source_c["incoming_photon_to_gas_scaled"])):
        raise ValueError("LOST_PHOTON_TO_GAS_MOMENTS")
    P=[[Q(x) for x in row] for row in source_c["scaled_P"]]
    if len(P)!=4 or any(len(r)!=4 for r in P) or any(x<0 for row in P for x in row):
        raise ValueError("COMPARISON_IS_NOT_POSITIVE")
    gain=max(sum(row,Q(0)) for row in P)
    if not Q(0)<=gain==Q(source_c["gain"]["rational"])<Q(1):
        raise ValueError("COMPARISON_GAIN_NOT_CONTRACTIVE")
    rhs=[
        eg[i]+coupling[i]+Q(source_c["gas_integral_scaled"][i]["rational"])
        +Q(source_c["photon_forcing_scaled"][i]["rational"])
        for i in range(4)]
    if any(sum(((Q(int(i==j))-P[i][j])*gas_scaled[j] for j in range(4)),Q(0))!=rhs[i] for i in range(4)):
        raise ValueError("RESOLVENT_EXACT_FRACTION_IDENTITY")
    sys.path.insert(0,str(root/"src"))
    from warm_interval import WarmSource
    warm=WarmSource()
    hh=json.loads((root/"inputs/HH_P01_COMPARISON.json").read_text())
    g0=list(map(Q,hh["gas_initial_exact"]))
    gasr=list(map(Q,hh["gas_radii"]))
    usage=max((max(abs(x-g0[i]) for x in warm.controls[i])+error[i])/gasr[i] for i in range(4))
    if usage>=1:raise ValueError("ORIGINAL_GAS_TUBE_ESCAPED")
    if not all(min(ctrl)>=0 for ctrl in warm.controls[4:]):
        raise ValueError("NEGATIVE_REFERENCE_PHOTON")
    whole=json.loads((root/"results/whole_jets.json").read_text())
    if len(whole["nodes"])!=2904:raise ValueError("WHOLE_NO_2904_PHOTONS")
    transparent=sum(all(Q(z[0])==Q(z[1])==0 for z in node["sigma"]) for node in whole["nodes"])
    if transparent!=source_c["transparent_count"]:
        raise ValueError("TRANSPARENT_SOURCE_NODE_NOT_MATCHED")
    outgoing=[]
    totalold=Q(0);totaladd=Q(0);totalres=Q(0)
    for j in range(2904):
        add=Q(STEP)*sum((Q(tensor["C_scaled"][j][k])*gas_scaled[k] for k in range(4)),Q(0))
        res=Q(tensor["photon"][j]["integral"])
        if ep[j]<0 or add<0 or res<0:raise ValueError("NEGATIVE_PHOTON_ERROR")
        outgoing.append(ep[j]+add+res)
        totalold+=ep[j];totaladd+=add;totalres+=res
    if any(x<0 for x in outgoing):
        raise ValueError("OUTGOING_PHOTON_NEGATIVE")
    old_tau=list(map(Q,old[f"{WORDS[p]}_cell_tau_exact"]))
    slab=list(map(Q,source_c["true_depth_interval"]))
    all_tau=[old_tau[i]+slab[i] for i in range(2)]
    if not 0<slab[0]<slab[1]<1 or not 0<all_tau[0]<all_tau[1]<1:
        raise ValueError("INVALID_TAU_OR_TIME_ORDER")
    prob=[collision_lower(all_tau[0]),collision_upper(all_tau[1])]
    if not 0<prob[0]<prob[1]<1:
        raise ValueError("COLLISION_PROBABILITY_NOT_POSITIVE")
    out=dict(schema=f"he18.c{n+2}.{DASH[n].lower()}_cell_outgoing_photon_errors.v1",
        source_commit=meta["source_commit"],source_interval_s=meta["cell_s"],
        input_prev_error_sha256=meta["prev_error_sha256"],
        incoming_adapter_sha256=meta["incoming_adapter_sha256"],
        incoming_components=2904,
        outgoing_photon_error_end_raw_exact=list(map(str,outgoing)),
        scaled_gas_error_end_exact=list(map(str,gas_scaled)),
        incoming_sum=str(totalold),added_coupling_sum=str(totaladd),
        added_residual_sum=str(totalres),
        outgoing_nonzero_count=sum(x>0 for x in outgoing),
        provider_roundoff_budget=None,source_ODE_invoked=False)
    report=dict(
        schema=f"he18.c{n+2}.{DASH[n].lower()}_cell_exact_review.v1",
        status="SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES",
        checks={k:True for k in (
            "predecessor_validated_and_sha", "saved_original_frozen_endpoints",
            "global_initial_epoch_clock_and_gas_domain",
            "full_2904_original_photon_node_grid",
            "nonnegative_photons_and_transparent_count",
            "four_gas_plus_2904_incoming_componentwise",
            "positive_full_four_by_four_resolvent",
            "all_2904_photon_radii_output_correct",
            "true_thomson_depth_positive_and_ordered",
            "cumulative_depth_and_collision_probability",
            "preserved_exact_original_source_identity")},
        slab_tau_exact=list(map(str,slab)),
        **{f"{WORDS[n]}_cell_tau_exact":list(map(str,all_tau)),
           f"{WORDS[n]}_cell_probability_exact":list(map(str,prob)),
           f"{WORDS[n]}_cell_tau_outward":[directed(all_tau[0],True),directed(all_tau[1],False)],
           f"{WORDS[n]}_cell_probability_outward":[directed(prob[0],True),directed(prob[1],False)]},
        global_gas_box_fraction_upper=str(usage),
        photon_nodes=2904,transparent_nodes=transparent,
        source_ODE_calls=0,native_roundoff=None,full_16_cell_admitted=False,
        interval_library_independent_verification=False,
    )
    out_file.write_text(json.dumps(out,indent=2)+"\n")
    dest.write_text(json.dumps(report,indent=2)+"\n")
    return dict(cell=n,time_s=meta["cell_s"],
        checks=len(report["checks"]),admitted=True,
        slab_tau_outward=[directed(slab[0],True),directed(slab[1],False)],
        cumulative_tau_outward=[directed(all_tau[0],True),directed(all_tau[1],False)],
        collision_probability_outward=[directed(prob[0],True),directed(prob[1],False)],
        column_radius=source_c["column_radius_m2_inv"]["upper_display"],
        gain_display=format(float(gain),".13g"),gas_tube_usage_display=format(float(usage),".13g"),
        transparent=transparent,photon_components=len(outgoing),
        outgoing_sha256=sha(out_file),validation_sha256=sha(dest))

if __name__=="__main__":
    pa=argparse.ArgumentParser()
    pa.add_argument("--runtime",type=Path,required=True)
    pa.add_argument("--cell",type=int,required=True)
    args=pa.parse_args()
    print(json.dumps(propagate_and_verify(args.runtime,args.cell),indent=2))
