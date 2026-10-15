#!/usr/bin/env python3
"""Finite-window P01 Thomson last-scatter probability mass, not CMB visibility.

For a homogeneous non-tilted electron gas, isotropic total Thomson hazard and
given source-scoped cumulative optical depth, the exact per-cell last-event
probability conditional on this finite window is positive:
 w_i=exp(-tau_final)*(exp(tau_i)-exp(tau_{i-1})).
No cosmological observer-tail/source equivalence is assumed.
"""
from __future__ import annotations
from decimal import Decimal,localcontext
import json
from pathlib import Path
from certified16 import source_rows,fmt

HERE=Path(__file__).resolve().parent

def build(rows):
    with localcontext() as ctx:
        ctx.prec=90
        total_l=Decimal(rows[-1]["source_tau_lower"])
        total_u=Decimal(rows[-1]["source_tau_upper"])
        mids=[(Decimal(r["source_tau_lower"])+Decimal(r["source_tau_upper"]))/2
              for r in rows]
        center=(total_l+total_u)/2
        previous_lower=Decimal(0)
        previous_upper=Decimal(0)
        previous_mid=Decimal(0)
        output=[]
        weights=[]
        lows=[]
        ups=[]
        for idx,row in enumerate(rows):
            lower=Decimal(row["source_tau_lower"])
            upper=Decimal(row["source_tau_upper"])
            middle=mids[idx]
            # Monotone in tau_i and -tau_{i-1}, monotone decreasing in tau_f.
            # Calculate all positive differences at 90 decimal digits.
            weight_lower=(-total_u+previous_upper).exp()*((lower-previous_upper).exp()-1)
            weight_upper=(-total_l+previous_lower).exp()*((upper-previous_lower).exp()-1)
            weight_mid=(-center+previous_mid).exp()*((middle-previous_mid).exp()-1)
            if not (Decimal(0)<weight_lower<=weight_mid<=weight_upper):
                raise RuntimeError("LAST_SCATTER_WEIGHT_OUT_OF_BRACKET")
            output.append({"cell":idx+1,
               "proper_end_s":row["proper_s"],
               "source_window_last_scatter_lower":fmt(weight_lower),
               "source_window_last_scatter_mid":fmt(weight_mid),
               "source_window_last_scatter_upper":fmt(weight_upper),
               "mean_probability_per_s":fmt(weight_mid/Decimal("6250000000"))})
            weights.append(weight_mid)
            lows.append(weight_lower)
            ups.append(weight_upper)
            previous_lower,previous_upper,previous_mid=lower,upper,middle
        normalization_mid=1-(-center).exp()
        conservative_lower=1-(-total_l).exp()
        conservative_upper=1-(-total_u).exp()
        summed=sum(weights)
        if abs(summed-normalization_mid)>Decimal("1e-85"):
            raise RuntimeError("P01_LAST_COLLISION_TELESCOPING_ERROR")
        if not(sum(lows)<=conservative_lower<=summed<=conservative_upper<=sum(ups)):
            raise RuntimeError("P01_LAST_COLLISION_ENCLOSURE_FAILURE")
        return {
            "schema":"rei.bass_he16.last_scatter_finite_window.v1",
            "status":"PASSED_16_SCOPED_POSITIVE_EVENT_WEIGHTS",
            "physics_scope":"finite conditional warm P01 past-to-final window, not observer CMB visibility",
            "model":"total Thomson scalar optical-depth Poisson event count; normal comoving homogeneous electron gas",
            "exact_formula":"wi=exp(-tau_final)*(exp(tau_i)-exp(tau_{i-1}))",
            "telescoping":"sum_i wi=1-exp(-tau_final)",
            "total_probability_lower":fmt(conservative_lower),
            "total_probability_mid":fmt(normalization_mid),
            "total_probability_upper":fmt(conservative_upper),
            "sum_mid":fmt(summed),
            "result":output,
            "scientific_admission":"NOT_ISSUED"
        }

if __name__=="__main__":
    rows,_=source_rows()
    result=build(rows)
    out=HERE/"results"/"warm_P01_finite_visibility.json"
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:result[k] for k in ("status","total_probability_lower",
                   "total_probability_mid","total_probability_upper","sum_mid")},indent=2))
