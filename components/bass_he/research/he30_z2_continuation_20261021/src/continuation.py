#!/usr/bin/env python3
"""Completed D3 result catalogue consumed by shared_runner.

The historical filename is retained for the runner API. This module never
integrates an ODE. write_case materializes only a verified, existing result.
"""
from __future__ import annotations
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import numpy as np
from analyze_saved import ARCHIVE_SHA, KERNEL, ROOT, atomic_bytes, sha

@lru_cache(maxsize=1)
def catalogue():
    root=ROOT / "results"
    data=json.loads((root / "CATALOG.json").read_text())
    if data["source_archive_sha256"] != ARCHIVE_SHA or data["source_kernel_commit"] != KERNEL:
        raise ValueError("source authority differs from the pinned D3 contract")
    if sha(root / "histories.npz") != data["histories_sha256"]:
        raise ValueError("compact history bytes changed; recover the original artifact")
    rows=data["cases"]
    with np.load(root / "histories.npz", allow_pickle=False) as a:
        if len(rows)!=237 or list(a["case_id"])!=[r["case_id"] for r in rows]:
            raise ValueError("case catalogue and data indices do not match")
        if a["Sigma_F"].shape!=(237,153) or abs(a["z_mean"][-1]-2)>1e-12:
            raise ValueError("incomplete saved history")
    return data,{r["case_id"]:r for r in rows}

def case_grid():
    return [dict(row) for row in catalogue()[0]["cases"]]

def case_identity(config):
    # Bind original scientific result, archive, and consumer schema; no rounded keys.
    payload={"schema":"HE30_D3_CONSUMPTION_V1","archive_sha256":ARCHIVE_SHA,
             "case_id":config["case_id"],"raw_sha256":config["source_raw_sha256"]}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def receipt(config):
    data,known=catalogue()
    if known.get(config["case_id"])!=config:
        raise ValueError("case is not an exact member of the completed source catalogue")
    return {"status":"REUSED_COMPLETED_D3","case_id":config["case_id"],
            "identity":case_identity(config),"source_raw_sha256":config["source_raw_sha256"],
            "source_archive_sha256":ARCHIVE_SHA,"histories_sha256":data["histories_sha256"],
            "epochs":153,"z_initial":20,"z_final":2,"science_runs_this_consumer":0,
            "artifact_role":"analysis observables; full raw states remain in the original D3 archive"}

def completed_result(config,path):
    path=Path(path)
    return path.is_file() and json.loads(path.read_text())==receipt(config)

def write_case(config,results_dir):
    expected=receipt(config)
    path=Path(results_dir)/(config["case_id"]+".json")
    if path.exists():
        if not completed_result(config,path):
            raise ValueError("different prior output preserved; choose a fresh consumer output directory")
        return expected
    # This is a small deterministic derived receipt, never a replacement raw result.
    from shared_runner import atomic_json
    atomic_json(path,expected,replace=False)
    return expected

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--materialize",type=Path,default=ROOT/"results/cases")
    a=p.parse_args()
    cases=case_grid()
    for config in cases: write_case(config,a.materialize)
    print(json.dumps({"validated_existing_cases":len(cases),"materialized_receipts":len(cases),
                      "science_runs":0,"pending_science":0},indent=2))

if __name__=="__main__":main()
