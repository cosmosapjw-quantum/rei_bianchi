#!/usr/bin/env python3
"""Independent source-scoped provenance/continuity check for cells 7->16."""
import argparse,hashlib,json,sys
from pathlib import Path
from fractions import Fraction as Q

if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(250000)
from stage_cell import WORDS,DASH,STEP,SOURCE_SHA,PRIVATE_DATA_SHA,sha

def verify(first,root,until=16):
    if not 8<=until<=16:raise ValueError("INVALID_END")
    previous=first
    results=[]
    for n in range(8,until+1):
        path=root/f"HE18_MULTICELL_{n:02d}_20261015"
        if n==8 and not path.exists():
            path=Path("/tmp/HE18_MULTICELL_08_20261015")
        if not path.is_dir():raise FileNotFoundError(f"MISSING_CELL_{n}")
        meta=json.loads((path/"inputs/CONTINUATION_BINDING.json").read_text())
        if meta["cell"]!=n or meta["source_sha256"]!=SOURCE_SHA:
            raise ValueError("SOURCE_IDENTITY_OR_CELL_CHANGED")
        cert_p=previous/"results"/f"{WORDS[n-1].upper()}_CELL_VALIDATION.json"
        error_p=previous/"results"/f"{DASH[n-1]}_ENDPOINT_MEMORY.json"
        if sha(cert_p)!=meta["prev_cert_sha256"] or sha(error_p)!=meta["prev_error_sha256"]:
            raise ValueError(f"PREDECESSOR_NOT_BYTE_IDENTICAL:{n}")
        for name,digest in PRIVATE_DATA_SHA.items():
            if sha(path/"inputs"/name)!=digest:raise ValueError(f"ORIGINAL_INPUT_MUTATED:{n}:{name}")
        if meta["cell_s"]!=[str((n-1)*STEP),str(n*STEP)]:
            raise ValueError("ORIGINAL_TIME_CLOCK_LOST")
        src_result=path/"results"/f"{WORDS[n].upper()}_CELL_VALIDATION.json"
        state=path/"results"/f"{DASH[n]}_ENDPOINT_MEMORY.json"
        a=json.loads(src_result.read_text());b=json.loads(state.read_text())
        if not all(a["checks"].values()) or len(a["checks"])!=11 or a["photon_nodes"]!=2904:
            raise ValueError(f"ADMISSION_GUARD_FAILED:{n}")
        if b["source_interval_s"]!=meta["cell_s"] or len(b["outgoing_photon_error_end_raw_exact"])!=2904:
            raise ValueError(f"ORPHANED_PHOTON_RADIATIVE_CARRY:{n}")
        prev=json.loads(cert_p.read_text())
        prev_tau=list(map(Q,prev[f"{WORDS[n-1]}_cell_tau_exact"]))
        this_tau=list(map(Q,a["slab_tau_exact"]))
        cum=list(map(Q,a[f"{WORDS[n]}_cell_tau_exact"]))
        if any(prev_tau[i]+this_tau[i]!=cum[i] for i in range(2)):
            raise ValueError(f"CUMULATIVE_TAU_NOT_EXACT_TELESCOPING:{n}")
        if not 0<cum[0]<cum[1]<1:
            raise ValueError("NONPOSITIVE_OR_WRONG_CLOCK_DEPTH")
        res=dict(cell=n,cert_sha256=sha(src_result),error_sha256=sha(state),
                 cumulative_tau_mid=float((cum[0]+cum[1])/2),
                 gas_box_use=float(Q(a["global_gas_box_fraction_upper"])),
                 emitted_photon_components=2904,
                 transparent=a["transparent_nodes"])
        results.append(res)
        previous=path
    return dict(schema="he18.p01.chain_verify.v1",first_cell=8,last_cell=until,
        physical_previous_completed=7,verified_source_cells=len(results)+7,
        source_sha256=SOURCE_SHA,all_chain_checks_pass=True,physical_scoped=True,
        final=results[-1],cell_receipts=results,
        source_ODE_replayed=False,native_roundoff_independent_review=False)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--previous-seven",type=Path,required=True)
    p.add_argument("--campaign",type=Path,required=True)
    p.add_argument("--until",type=int,default=16)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    out=verify(a.previous_seven,a.campaign,a.until)
    if a.output.exists():raise SystemExit("REFUSE_OVERWRITE")
    a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({"all_chain_checks_pass":out["all_chain_checks_pass"],
        "verified_source_cells":out["verified_source_cells"],
        "last":out["final"],"cell_count":len(out["cell_receipts"])},indent=2))
