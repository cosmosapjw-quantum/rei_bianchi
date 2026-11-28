#!/usr/bin/env python3
"""Exact Fraction Bernstein panel-refinement benchmark on saved photon jets.

No source evaluation, no changed nominal runtime, and no admissibility change.
The 16-panel production certificate is unchanged; 8 and 32 are diagnostics.
"""
from pathlib import Path
import argparse,hashlib,json,sys,time
from fractions import Fraction as Q
def run(runtime):
    src=runtime/"src";sys.path.insert(0,str(src))
    from assemble_certificate import residual_bounds
    a=runtime/"results/mid_jets.json"
    b=runtime/"results/whole_jets.json"
    mid=json.loads(a.read_text())["photon"]
    whole=json.loads(b.read_text())["photon"]
    if len(mid)!=2904 or len(whole)!=2904:
        raise ValueError("INCOMPLETE_PHOTON_NODE_GRID")
    out={"schema":"he18.c8.exact_panel_refinement.v1",
         "runtime_source":str(runtime),
         "mid_sha256":hashlib.sha256(a.read_bytes()).hexdigest(),
         "whole_sha256":hashlib.sha256(b.read_bytes()).hexdigest(),
         "nested_panels":[8,16,32],
         "summary":[],"nonincreasing_checks":{}}
    previous=None
    for n in (8,16,32):
        start=time.perf_counter()
        vals=[residual_bounds(x,y,n) for x,y in zip(mid,whole)]
        secs=time.perf_counter()-start
        stats=dict(panels_per_photon=n,photon_count=2904,
            wall_seconds=secs,
            photon_bound_sums_exact={
              k:str(sum((v[k] for v in vals),Q(0)))
              for k in ("sup","integral","weighted_integral")})
        if previous is not None:
            for k in ("sup","integral","weighted_integral"):
                inc=sum(vals[i][k]>previous[i][k] for i in range(2904))
                stats[f"{k}_increased_vs_prev"]=inc
                if inc: raise ValueError(f"REFINEMENT_NOT_MONOTONE_{k}:{inc}")
        out["summary"].append(stats)
        previous=vals
    out["nonincreasing_checks"]={
        k:all(row.get(f"{k}_increased_vs_prev",0)==0 for row in out["summary"])
        for k in ("sup","integral","weighted_integral")}
    out["all_pass"]=all(out["nonincreasing_checks"].values())
    return out
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--runtime",type=Path,required=True)
    a=parser.parse_args()
    result=run(a.runtime)
    dest=a.runtime/"evidence/PANEL_REFINEMENT.json"
    if dest.exists():raise SystemExit("REFUSE_EXISTING_REFINEMENT_RESULT")
    dest.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({**result,"summary":[{k:v for k,v in rec.items()
            if k!="photon_bound_sums_exact"} for rec in result["summary"]]},indent=2))
