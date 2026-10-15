#!/usr/bin/env python3
"""Validated 16-cell BASS_HE P01 conditional optical-depth readout.

No physical-model transfer: this accepts ONLY the exact byte-pinned, published
BASS_HE warm-P01 summary, never private 2904-ray arrays or current AX08 runtime.
Positive Poisson probabilities are computed using Decimal (no 1-exp cancellation).
"""
from __future__ import annotations
import csv
from decimal import Decimal, localcontext
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
INPUT=HERE/"input"
CSV_PATH=INPUT/"warm_P01_cumulative_tau.csv"
STATUS_PATH=INPUT/"RESULT_STATUS.json"
SOURCE_HEAD="b0af50b052862320896085fac70250f51c077944"
SOURCE_COMMIT="a5c958c414dea41216b445c05f58df837f05cacb"
CSV_SHA="46b4b3ef86e9a69d8fe5d6ac585bc9c145e2fde99f61a8acf3675b4491b86a40"
STATUS_SHA="c2bc5cda5f4c1db55fd1166d4aa86cf88d4b17dc3e574be1e5277fa49a493374"
DT=Decimal("6250000000")
FINAL_T=DT*16

def sha(path:Path)->str:
    h=sha256()
    with path.open("rb") as file:
        for part in iter(lambda:file.read(1<<20),b""):
            h.update(part)
    return h.hexdigest()

def require(condition:bool,name:str)->None:
    if not condition:raise ValueError(name)

def fmt(a:Decimal)->str:
    return format(a,".39E")

def positive_poisson_tail(t:Decimal)->Decimal:
    """exp(-t) sum_{k>=3} t^k/k!, >=0 without cancellation, t<=2e-7."""
    if t<0 or t>Decimal("0.0000002"):
        raise ValueError("POISSON_TAU_OUT_OF_SUPPORTED_RANGE")
    with localcontext() as context:
        context.prec=90
        term=t*t*t/Decimal(6)
        result=Decimal(0)
        for k in range(3,21):
            result+=term
            term=term*t/Decimal(k+1)
        # Omitted terms begin at k=21, bounded by term/(1-t/22).
        require(term/(1-t/Decimal(22))<Decimal("1e-100"),
                "UNRESOLVED_POSITIVE_POISSON_TAIL")
        return +((-t).exp()*result)

def probabilities(t:Decimal)->dict:
    with localcontext() as context:
        context.prec=90
        p0=(-t).exp()
        p1=t*p0
        p2=t*t*p0/2
        ge3=positive_poisson_tail(t)
        require(abs(p0+p1+p2+ge3-1)<Decimal("1e-85"),
                "POISSON_NORMALIZATION_FAILURE")
        return dict(p0=p0,p1=p1,p2=p2,ge3=ge3)

def source_rows(path:Path=CSV_PATH,status_path:Path=STATUS_PATH,check_sha:bool=True)->tuple[list[dict],dict]:
    status=json.loads(status_path.read_text())
    require(status.get("original_source_commit")==SOURCE_COMMIT,
            "BASS_HE_SOURCE_COMMIT_CHANGED")
    require(status.get("total_source_saved_cells")==16
            and status.get("completed_saved_cells")==16,
            "NOT_COMPLETE_16_SAVED_CELLS")
    require(status.get("scientific_status")=="SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES",
            "BASS_HE_SCIENCE_SCOPE_CHANGED")
    require(status.get("not_physical_EoR_ion_abundance_history") is True
            and status.get("native_binary64_rounding_or_formal_backend_proof") is False,
            "BASS_HE_CLAIM_CEILING_CHANGED")
    if check_sha:
        require(sha(status_path)==STATUS_SHA,
                "BYTE_IDENTITY_FAILURE_UPSTREAM_STATUS")
        require(sha(path)==CSV_SHA and status.get("public_csv_sha256")==CSV_SHA,
                "BYTE_IDENTITY_FAILURE_UPSTREAM_CSV")
    with path.open(newline="") as f:
        rows=list(csv.DictReader(f))
    require(len(rows)==16,"BAD_CELL_COUNT")
    output=[]
    last_t=0
    last_lo=Decimal(0)
    last_hi=Decimal(0)
    for i,row in enumerate(rows,start=1):
        t=int(row["source_end_proper_s"])
        lo=Decimal(row["cumulative_tau_lower"])
        hi=Decimal(row["cumulative_tau_upper"])
        require(int(row["cell"])==i and t==i*int(DT) and t>last_t,
                "NONCONTIGUOUS_PROPER_CLOCK")
        require(row["admitted"]=="True" and Decimal(0)<lo<=hi,
                "NONPOSITIVE_OR_UNADMITTED_CELL")
        require(lo>last_hi and hi>last_lo,
                "CUMULATIVE_OR_INDIVIDUAL_TAU_NOT_STRICTLY_POSITIVE")
        deltas=(lo-last_hi,hi-last_lo)
        require(deltas[0]>0 and deltas[1]>=deltas[0],
                "NONPOSITIVE_CELL_INCREMENT")
        p_lo=probabilities(lo)
        p_hi=probabilities(hi)
        require(p_hi["ge3"]>=p_lo["ge3"],"NONMONOTONE_SCATTERING_TAIL")
        # p1,p2 monotone for these very small optical depths (tau<1).
        require(lo<Decimal(1),"POISSON_MONOTONICITY_ASSUMPTION_BROKEN")
        output.append({
            "cell":i,"proper_s":t,
            "source_tau_lower":fmt(lo),"source_tau_upper":fmt(hi),
            "slab_tau_lower":fmt(deltas[0]),"slab_tau_upper":fmt(deltas[1]),
            "prob_zero_lower":fmt(p_hi["p0"]),"prob_zero_upper":fmt(p_lo["p0"]),
            "prob_once_lower":fmt(p_lo["p1"]),"prob_once_upper":fmt(p_hi["p1"]),
            "prob_twice_lower":fmt(p_lo["p2"]),"prob_twice_upper":fmt(p_hi["p2"]),
            "prob_three_plus_lower":fmt(p_lo["ge3"]),
            "prob_three_plus_upper":fmt(p_hi["ge3"]),
            "simple_tail_bound_upper":fmt(hi**3/6)
        })
        last_lo,last_hi,last_t=lo,hi,t
    require(last_t==int(FINAL_T)
            and last_lo==Decimal(status["final_tau_outward"][0])
            and last_hi==Decimal(status["final_tau_outward"][1]),
            "UPSTREAM_FINAL_INTERVAL_DOES_NOT_MATCH_CSV")
    return output,status

def build_report(rows:list[dict],status:dict)->dict:
    final=rows[-1]
    return {
        "schema":"rei.bass_he16.source_scoped_poisson.v1",
        "scientific_status":"SOURCE_SCOPED_CONDITIONAL_POISSON_POSTPROCESS_ONLY",
        "source_commit":SOURCE_HEAD,"physics_original_commit":SOURCE_COMMIT,
        "input_sha256":{CSV_PATH.name:sha(CSV_PATH),STATUS_PATH.name:sha(STATUS_PATH)},
        "unit":"tau and collision probabilities dimensionless; elapsed proper time s",
        "photon_count_model":"independent scattering-count Poisson process at cumulative optical depth",
        "correct_scope":"fixed archived warm P01 source, non-tilted Bianchi I, 16 saved cells; tau not observer-line-of-sight",
        "not_transferable_to":"AX08 cold MD14, physical global EoR abundance, radiative Boltzmann operator norm, thermal feedback",
        "method":"Decimal90 positive sum k>=3; p_0,p_1,p_2,tail; inward probability monotonic maps of rigorous conditional tau endpoints",
        "tail_derivative":"d/dtau P(N>=3)=exp(-tau)*tau^2/2 >=0",
        "tail_bound":"0 <= P(N>=3) <= tau^3/6 for tau>=0",
        "num_saved_cells":len(rows),
        "final":final,
        "cells":rows,
    }

if __name__=="__main__":
    rows,status=source_rows()
    report=build_report(rows,status)
    out=HERE/"results"/"certified_poisson.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:report["final"][k] for k in
       ("source_tau_lower","source_tau_upper","prob_once_lower","prob_once_upper",
        "prob_twice_lower","prob_twice_upper","prob_three_plus_lower","prob_three_plus_upper")},
        indent=2))
