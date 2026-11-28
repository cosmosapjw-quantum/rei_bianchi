#!/usr/bin/env python3
"""INDEPENDENT, NONCERTIFYING all-panel float64 full-coupling diagnostics."""
from __future__ import annotations
import argparse
import json
import math
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))

from wu088_hh.phys33_residual import dyadic, load_frozen
from wu088_hh.phys33_general_strip_preview import preview_general_strip

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--frozen",type=Path,default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
    ap.add_argument("--nr",type=int,default=96)
    ap.add_argument("--ns",type=int,default=128)
    ap.add_argument("--out",type=Path,required=True)
    o=ap.parse_args()
    rr,u,source_sha=load_frozen(o.frozen,True)
    panels=[]
    for j in range(6):
        lo,hi=dyadic(rr[j,0]),dyadic(rr[j,-1])
        p=preview_general_strip(o.frozen,(lo+hi)/2,(hi-lo)/2,o.nr,o.ns)
        assert p["input_sha256"]==source_sha and p["panel"]==j
        panels.append(p)
    total=math.sqrt(sum(p["sampled_volume_L2"]**2 for p in panels))
    report={
       "schema":"WU088_HH_PHYS41_NONCERTIFYING_GLOBAL_GAUSS_V1",
       "status":"FLOAT64_DIAGNOSTIC_NOT_AN_INTERVAL_OR_CERTIFICATE",
       "scientific_scope":"original 6-panel complete s-angular screened residual, broken bulk only",
       "input_sha256":source_sha,"nr":o.nr,"ns":o.ns,
       "sampled_broken_bulk_L2":total,"panels":panels,
       "does_not_certify":["radial quadrature error","origin, exterior","interface sheets",
                            "continuous outgoing inverse","scattering physical rate"]
    }
    o.out.parent.mkdir(parents=True,exist_ok=True)
    o.out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"sampled_broken_bulk_L2":total,"nr":o.nr,"ns":o.ns,
                      "panel_norms":[z["sampled_volume_L2"] for z in panels]}))
if __name__=="__main__":
    main()
