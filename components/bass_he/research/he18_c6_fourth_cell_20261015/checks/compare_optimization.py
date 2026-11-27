#!/usr/bin/env python3
"""Check sparse interval evaluator against the original for identical C6 inputs.

Checks *all* photon residual Taylor coefficients and every radiation-source
component, not just final tau. Overlap is a regression diagnostic, not a formal
proof of mpmath.iv's rounding implementation.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from fractions import Fraction as Q
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def compatible(a,b):
    aa,ab=Q(a[0]),Q(a[1]);ba,bb=Q(b[0]),Q(b[1])
    if aa>ab or ba>bb:raise AssertionError("REVERSED_INTERVAL")
    return max(aa,ba)<=min(ab,bb)
def evaluate(base,opt):
    inputs=["P01_STATE.npz","emissivity.out","FIXED_REFERENCE.npz",
            "ENDPOINT_MEMORY_R7.json","STAGED_SOURCE_IDENTITY.json"]
    for name in inputs:
        assert sha(base/"inputs"/name)==sha(opt/"inputs"/name),name
    stats=dict(component_intervals_checked=0,component_disjoint=0,
        exact_node_records_equal=True,photons=2904,transparent=0)
    for name in ("mid_jets.json","whole_jets.json"):
        a=json.loads((base/"results"/name).read_text())
        b=json.loads((opt/"results"/name).read_text())
        assert a["nodes"]==b["nodes"], "CHANGED_EMISSIVITY_OR_OPACITY_NODE"
        assert a["env"]==b["env"],"CHANGED_GEOMETRY"
        assert len(a["gas"])==len(b["gas"])==4
        assert len(a["photon"])==len(b["photon"])==2904
        for key in ("gas","photon","gamma","qphoto"):
            assert len(a[key])==len(b[key])
            for x,y in zip(a[key],b[key]):
                assert len(x)==len(y)
                for j,k in zip(x,y):
                    stats["component_intervals_checked"]+=1
                    if not compatible(j,k):stats["component_disjoint"]+=1
        if name=="whole_jets.json":
            stats["transparent"]=sum(all(all(Q(t)==0 for t in coeff)
                for coeff in nd["sigma"]) for nd in b["nodes"])
    assert stats["component_disjoint"]==0,stats
    for cert in ("CERTIFICATE.json",):
        a=json.loads((base/"results"/cert).read_text())
        b=json.loads((opt/"results"/cert).read_text())
        assert Q(a["gain"]["rational"])<1 and Q(b["gain"]["rational"])<1
        assert compatible(a["true_depth_interval"],b["true_depth_interval"])
        stats["baseline_gain"]=float(Q(a["gain"]["rational"]))
        stats["optimized_gain"]=float(Q(b["gain"]["rational"]))
        stats["baseline_col_radius_m2"]=float(Q(a["column_radius_m2_inv"]["rational"]))
        stats["optimized_col_radius_m2"]=float(Q(b["column_radius_m2_inv"]["rational"]))
    def wall(log,label):
        m=re.search(rf"{label}=(\d+(?:\.\d+)?)",log)
        if not m:raise AssertionError(f"NO_WALL_TIMER:{label}")
        return float(m.group(1))
    for tag in ("MID","WHOLE","ASSEMBLE"):
        a=(base/"evidence"/({"MID":"mid","WHOLE":"whole","ASSEMBLE":"assemble"}[tag]+".stderr")).read_text()
        b=(opt/"evidence"/({"MID":"mid","WHOLE":"whole","ASSEMBLE":"assemble"}[tag]+".stderr")).read_text()
        label=("BASELINE_"+tag+"_WALL" if tag=="ASSEMBLE" else tag+"_WALL_SECONDS")
        lo=wall(a,label)
        label=("OPT_"+tag+"_WALL_SECONDS" if tag!="ASSEMBLE" else "OPT_ASSEMBLE_WALL_SECONDS")
        hi=wall(b,label)
        stats[tag.lower()+"_baseline_s"]=lo;stats[tag.lower()+"_optimized_s"]=hi
        stats[tag.lower()+"_speedup"]=lo/hi
    stats["scientific_claim"]="SOURCE_SCOPED_EVALUATOR_EQUIVALENCE_DIAGNOSTIC"
    stats["no_formal_interval_backend_review"]=True
    return stats
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--baseline",type=Path,required=True)
    p.add_argument("--optimized",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=evaluate(a.baseline,a.optimized)
    if a.output.exists():raise SystemExit("REFUSE_OVERWRITE")
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
