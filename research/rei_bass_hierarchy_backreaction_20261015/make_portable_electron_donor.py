#!/usr/bin/env python3
"""Build a small, portable SOURCE-QUALIFIED donor from real AX08 ZERO H/He ne(a).

This is 8193 *derived* smooth interpolation knots, not the original 312238-row
historical dataset, and NOT an AX11 or standalone chemical reionization output.
A portable replay can reconstruct the same conditional opacity input without
mounting the user's ~159MB private source history.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from lrs_boltzmann import SmoothElectronHistory

HERE=Path(__file__).resolve().parent
REL=Path("research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO_composed_001")
def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for b in iter(lambda:stream.read(1<<20),b""):
            h.update(b)
    return h.hexdigest()
def build(owner):
    folder=owner/REL
    meta=json.loads((folder/"COMPOSITION_RECEIPT.json").read_text())
    assert meta["status"]=="COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION"
    assert meta["row_counts"]["history.csv"]["composed_rows"]==312238
    history=folder/"history.csv"
    assert digest(history)==meta["output_sha256"]["history.csv"]
    actual=np.loadtxt(history,delimiter=",",skiprows=1,usecols=(4,13),dtype=float)
    assert actual.shape==(312238,2)
    interpolation=SmoothElectronHistory(actual[:,0],actual[:,1],nodes=8193)
    aa=np.exp(interpolation.x)
    nn=interpolation.density(aa)
    assert np.all(np.diff(aa)>0) and np.all(nn>0)
    target=HERE/"results/portable_electron_source_8193.csv"
    np.savetxt(target,np.column_stack((aa,nn)),delimiter=",",
        header="a_mean,ne_proper_cm3",comments="",fmt="%.17g")
    reloaded=np.loadtxt(target,delimiter=",",skiprows=1,dtype=float)
    assert reloaded.shape==(8193,2)
    again=SmoothElectronHistory(reloaded[:,0],reloaded[:,1],nodes=8193)
    maxdiff=float(np.max(np.abs(again.density(aa)/nn-1)))
    if maxdiff>4e-11:raise RuntimeError("PORTABLE_KNOT_ROUNDTRIP_FAILED")
    result={
      "schema":"rei.bass_source_locked_portable_electron_donor.v1",
      "source_type":"DERIVED_INTERPOLATION_KNOTS_NOT_ORIGINAL_REI_HISTORY",
      "original_OWNER_history_sha256":digest(history),
      "original_source_history_rows":312238,
      "source_original_filename":"ZERO_composed_001/history.csv",
      "saved_knots":8193,
      "current_time_epoch":"source historical zbar=20 to4; no new independent chemistry",
      "interpolation_rule":"original full ln(a),ln(ne) --> sample 8193 uniform ln(a) with np.interp, natural CubicSpline; ne always strictly positive",
      "reference_C2_observed_max_rel_against_312238_source":
           interpolation.max_relative_source_error,
      "portable_roundtrip_max_rel":maxdiff,
      "saved_file_sha256":digest(target),
      "filename":target.name,
      "original_historical_RAW_HISTORY_NOT_UPLOADED":True,
      "scientific_admission":"NOT_ISSUED"
    }
    (HERE/"results/portable_electron_source_manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--owner-root",required=True,type=Path)
    x=p.parse_args()
    print(json.dumps(build(x.owner_root),indent=2))
