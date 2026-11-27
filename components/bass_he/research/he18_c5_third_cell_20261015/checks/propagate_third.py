#!/usr/bin/env python3
"""Third warm P01 saved-cell exact componentwise photon radius propagation."""
from fractions import Fraction as Q
from pathlib import Path
import hashlib, json
ROOT=Path(__file__).resolve().parents[1]
def compute():
    cert=json.loads((ROOT/"results/CERTIFICATE.json").read_text())
    couplings=json.loads((ROOT/"results/RESIDUAL_COUPLING.json").read_text())
    orig=(ROOT/"inputs/ENDPOINT_MEMORY_R7.json").read_bytes()
    staged=json.loads((ROOT/"inputs/STAGED_SOURCE_IDENTITY.json").read_text())
    if hashlib.sha256(orig).hexdigest()!=staged["adapted_carry_sha256"]:
        raise ValueError("INCOMING_2904_BYTE_IDENTITY")
    incoming=json.loads(orig)
    ep=list(map(Q,incoming["photon_error_end_raw_exact"]))
    gas=list(map(Q,incoming["gas_error_end_scaled"]))
    if len(ep)!=2904 or len(gas)!=4 or len(couplings["C_scaled"])!=2904 or len(couplings["photon"])!=2904:
        raise ValueError("MISSING_CARRY_COMPONENT")
    step=Q(6250000000);scale=[Q(1),Q(1),Q(1),Q(32)]
    eg=[Q(x["rational"])/scale[k] for k,x in enumerate(cert["gas_error_components"])]
    out=[]; inc=Q(0); coupling_total=Q(0);res_total=Q(0)
    for j in range(2904):
        coupling=step*sum((Q(couplings["C_scaled"][j][k])*eg[k] for k in range(4)),Q(0))
        res=Q(couplings["photon"][j]["integral"])
        if ep[j]<0 or coupling<0 or res<0:raise ValueError("NEGATIVE_PHOTON_RADIUS")
        out.append(ep[j]+coupling+res)
        inc+=ep[j];coupling_total+=coupling;res_total+=res
    return dict(
        schema="he18.c5.third_cell_outgoing_photon_errors.v1",
        source_commit=staged["source_commit"],
        source_interval_s=["12500000000","18750000000"],
        incoming_second_cell_sha256=staged["input_previous_end_sha256"],
        incoming_adapted_sha256=staged["adapted_carry_sha256"],
        incoming_photon_components=2904,
        incoming_nonzero_count=sum(v>0 for v in ep),
        outgoing_photon_error_end_raw_exact=[str(v) for v in out],
        scaled_gas_error_end_exact=list(map(str,eg)),
        incoming_sum=str(inc),
        added_coupling_sum=str(coupling_total),
        added_residual_sum=str(res_total),
        nonzero_count=sum(v>0 for v in out),
        next_cell_source_jacobian=None,
        roundoff_budget=None,
        physical_input_evolution_error=None,
        new_native_solver_calls=0,
    )
if __name__=="__main__":
    target=ROOT/"results/THIRD_ENDPOINT_MEMORY.json"
    if target.exists():raise SystemExit("REFUSE_OVERWRITE")
    result=compute()
    target.write_text(json.dumps(result,indent=2)+"\n")
    print("Third cell incoming and outgoing photon components:",
          result["incoming_photon_components"],len(result["outgoing_photon_error_end_raw_exact"]))
    print("Outgoing nonzero",result["nonzero_count"])
