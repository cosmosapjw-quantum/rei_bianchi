#!/usr/bin/env python3
"""Carry exactly all 2904 photon endpoint error radii from cell 6 to cell 7."""
from fractions import Fraction as Q
from pathlib import Path
import hashlib, json
ROOT=Path(__file__).resolve().parents[1]
STEP=Q(6250000000)
def compute():
    cert=json.loads((ROOT/"results/CERTIFICATE.json").read_text())
    detail=json.loads((ROOT/"results/RESIDUAL_COUPLING.json").read_text())
    info=json.loads((ROOT/"inputs/STAGED_SOURCE_IDENTITY.json").read_text())
    raw=(ROOT/"inputs/ENDPOINT_MEMORY_R7.json").read_bytes()
    if hashlib.sha256(raw).hexdigest()!=info["adapted_incoming_sha256"]:
        raise ValueError("INCOMING_2904_BYTE_IDENTITY")
    packet=json.loads(raw)
    ep=list(map(Q,packet["photon_error_end_raw_exact"]))
    eg=list(map(Q,packet["gas_error_end_scaled"]))
    if len(ep)!=2904 or len(eg)!=4 or len(detail["C_scaled"])!=2904 or len(detail["photon"])!=2904:
        raise ValueError("INCOMPLETE_INCOMING_ERROR")
    scales=[Q(1),Q(1),Q(1),Q(32)]
    current=[Q(x["rational"])/scales[k] for k,x in enumerate(cert["gas_error_components"])]
    carry=[];incoming=Q(0);added=Q(0);residue=Q(0)
    for j in range(2904):
        coupling=STEP*sum((Q(detail["C_scaled"][j][k])*current[k] for k in range(4)),Q(0))
        res=Q(detail["photon"][j]["integral"])
        if ep[j]<0 or coupling<0 or res<0:
            raise ValueError("NEGATIVE_PHOTON_RADIUS")
        carry.append(ep[j]+coupling+res)
        incoming+=ep[j];added+=coupling;residue+=res
    return dict(schema="he18.c9.seventh_cell_outgoing_photon_errors.v1",
        source_commit=info["source_commit"],source_interval_s=info["cell_s"],
        input_prev_C8_sha256=info["prev_photon_error_sha256"],
        incoming_adapter_sha256=info["adapted_incoming_sha256"],
        incoming_components=2904,
        outgoing_photon_error_end_raw_exact=list(map(str,carry)),
        scaled_gas_error_end_exact=list(map(str,current)),
        incoming_sum=str(incoming),added_coupling_sum=str(added),
        added_residual_sum=str(residue),
        outgoing_nonzero_count=sum(x>0 for x in carry),
        required_next_cell_majorants=None,
        provider_roundoff_budget=None,source_ODE_invoked=False)
if __name__=="__main__":
    dest=ROOT/"results/SEVENTH_ENDPOINT_MEMORY.json"
    if dest.exists():raise SystemExit("REFUSE_OVERWRITE")
    out=compute()
    dest.write_text(json.dumps(out,indent=2)+"\n")
    print("PHOTON_CARRY",out["incoming_components"],out["outgoing_nonzero_count"])
