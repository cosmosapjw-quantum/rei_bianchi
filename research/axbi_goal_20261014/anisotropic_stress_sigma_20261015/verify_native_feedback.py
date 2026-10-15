"""Cross-check new Sigma-based Einstein ODE against an existing REAL REI record.

This compares the limiting perturbative radiation-stress feedback reconstructed
from native completed REI half-plus saved history against the independent
Einstein-coupled vs prescribed Sigma difference. The former was *not* fed into
this ODE. The two estimands differ at higher order and exclude different
gas/ionizing-radiation details. Scoped consistency, not native physics parity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

HERE=Path(__file__).resolve().parent
NATIVE=HERE.parent/"convergence/ax08_half_plus_20261015/feedback_reconstruction.json"
RESULT=HERE/"RESULTS.json"


def verify(results=RESULT, source=NATIVE):
    run=json.loads(Path(results).read_text())
    actual=json.loads(Path(source).read_text())
    if actual.get("schema")!="rei.axbi.reconstructed_feedback.v1":
        raise ValueError("unexpected saved REI native feedback identity")
    row=next(x for x in run["coupled_vs_prescribed_at_z4"]
             if x["gas"]=="baseline" and x["orientation"]==1 and
             x["Sigma_ref"]<.01)
    calculated=(row["Sigma_end_coupled"]-row["Sigma_end_prescribed"])/math.sqrt(3)
    control=actual["results"]["SHEAR_HALF_PLUS"]["endpoint"][
        "effective_radiation_delta_s_over_H"]
    ionizing=actual["results"]["SHEAR_HALF_PLUS"]["endpoint"][
        "ionizing_delta_s_over_H"]
    if calculated>=0 or control>=0:
        raise AssertionError("radiation stress must oppose positive shear")
    relative=abs(calculated-control)/max(abs(control),1e-120)
    # 0.3% is a scoped numerical consistency threshold for perturbed vs
    # nonlinear solutions, NOT a convergence or observational precision gate.
    status="PASS_PERTURBATIVE_CROSS_MODEL" if relative<.003 else "FAIL"
    return {
        "schema":"rei.sigma_pi.scoped_feedback_crosscheck.v1",
        "original_native_saved_feedback_sha256":hashlib.sha256(
            Path(source).read_bytes()).hexdigest(),
        "original_native_history_rows":actual["results"]["SHEAR_HALF_PLUS"]["n_rows"],
        "original_native_shear_magnitude_case":"half source equivalent Sigma_ref≈0.0086601458",
        "scope":"original REI actual-saved photon feedback perturbation vs new collisionless Einstein sourced background; no production recoupling",
        "original_source_perturbative_delta_s_over_H":control,
        "new_Einstein_delta_s_over_H":calculated,
        "signed_native_ionizing_delta_s_over_H":ionizing,
        "relative_difference":relative,
        "acceptance_threshold":.003,
        "status":status,
    }


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    outcome=verify()
    a.output.write_text(json.dumps(outcome,sort_keys=True,indent=2)+"\n")
    print(json.dumps(outcome,indent=2))
    if not outcome["status"].startswith("PASS"):
        raise SystemExit(1)
