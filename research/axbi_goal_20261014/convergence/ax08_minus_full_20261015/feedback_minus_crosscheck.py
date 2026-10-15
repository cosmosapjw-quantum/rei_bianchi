#!/usr/bin/env python3
"""Independent saved AX08 full minus feedback, Python Kahan vs Rust O(1) reader.

Source is a source-locked observationally uncalibrated Bianchi-I stress
screening diagnostic. This does NOT correct the background or certify error.
"""
import argparse
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import time

HERE=Path(__file__).resolve().parent
PREVIOUS=HERE.parent/"ax08_half_plus_20261015/reconstruct_feedback.py"
BINARY=Path("/tmp/rei_ax08_minus_feedback_fast_20261015")
PATHS={
 "ZERO":"research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO_composed_001/feedback.csv",
 "SHEAR_MINUS":"research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_MINUS_composed_001/feedback.csv"
}
def check(root):
    spec=importlib.util.spec_from_file_location("ax08_source_scoped_feedback",PREVIOUS)
    ref=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ref)
    ref.ROOT=root
    scientific={}
    for case,rel in PATHS.items():
        p=root/rel
        parent=p.parent
        receipt=json.loads((parent/"COMPOSITION_RECEIPT.json").read_text())
        if receipt["status"]!="COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION":
            raise RuntimeError("SOURCE_NOT_COMPLETED")
        if ref.digest(p)!=receipt["output_sha256"]["feedback.csv"]:
            raise RuntimeError("FEEDBACK_BYTES_NOT_FROZEN")
        scientific[case]=ref.accumulate(p,case)
    start=time.perf_counter()
    proc=subprocess.run([str(BINARY),str(root),"--serial"],check=True,capture_output=True,text=True)
    serial_wall=time.perf_counter()-start
    fast=list(csv.DictReader(io.StringIO(proc.stdout)))
    if set(r["case"] for r in fast)!=set(PATHS):
        raise RuntimeError("RUST_CASE_SET_NOT_MATCHING")
    deltas={}
    for r in fast:
        case=r["case"]
        src=scientific[case]
        contract={
         "rows":src["n_rows"],
         "max_abs_delta_s_over_H":src["max_abs_delta_s_over_H"]["abs_delta_s_over_H"],
         "endpoint_delta_s_over_H":src["endpoint"]["total_delta_s_over_H"],
         "max_extra_energy_ratio":src["max_abs_extra_energy_ratio"]["abs_ratio"],
         "endpoint_effective_rad_delta_s_over_H":src["endpoint"]["effective_radiation_delta_s_over_H"],
         "endpoint_ionizing_delta_s_over_H":src["endpoint"]["ionizing_delta_s_over_H"],
         "end_a":src["endpoint"]["a"],
        }
        errors={}
        for k,expected in contract.items():
            actual=float(r[k])
            err=abs(actual-expected)
            tolerance=max(1e-25,1e-12*abs(expected))
            if err>tolerance:
                raise RuntimeError(f"RUST_PYTHON_NUMERICAL_MISMATCH:{case}:{k}:{err}>{tolerance}")
            errors[k]=err
        deltas[case]={"errors":errors,"reference":src}
    return {
      "schema":"rei.axbi.minus_full_omitted_shear_stress.v1",
      "status":"PYTHON_KAHAN_RUST_STREAMING_NUMERICAL_PARITY_PASS",
      "source_real_cases":["ZERO","SHEAR_MINUS"],
      "cgs_si":"pressure J/m³, dt proper s, dimensionless δs/H, explicit SI G and c",
      "comparison":"actual 312238 saved physical times, not q-signed full solution set",
      "python_science":scientific,
      "rust_python_residuals":{k:v["errors"] for k,v in deltas.items()},
      "rust_serial_wall_s":serial_wall,
      "uncertainty":"time-step and angular/energy quadrature not numerically certified",
      "feedback_applied_to_evolution":False,
      "scientific_admission":"NOT_ISSUED"
    }
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--owner-root",required=True,type=Path)
    args=ap.parse_args()
    out=check(args.owner_root)
    (HERE/"results_001"/"feedback_minus_crosscheck.json").write_text(json.dumps(out,indent=2)+"\n")
    for name,z in out["python_science"].items():
        print(name,"max_abs_delta_s_over_H",z["max_abs_delta_s_over_H"]["abs_delta_s_over_H"],
              "endpoint_delta_s_over_H",z["endpoint"]["total_delta_s_over_H"],
              "energy_ratio",z["max_abs_extra_energy_ratio"]["abs_ratio"],
              "below_1e-4",z["measured_below_perturbative_ceiling"])
