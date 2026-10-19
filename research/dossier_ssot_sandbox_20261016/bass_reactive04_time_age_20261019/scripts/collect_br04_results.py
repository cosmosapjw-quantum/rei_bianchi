#!/usr/bin/env python3
"""Assemble the BR04 science summary from recorded results, without running physics."""
from pathlib import Path
import csv
from decimal import Decimal
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def main():
    inputs = ["evidence/native_audit/crossed/TIME_AGE_ANALYSIS.json",
              "evidence/age_study/AGE_CERTIFICATES.csv",
              "evidence/age_study/AGE_SOURCE_MIXTURE_BOUNDS.csv",
              "evidence/theory/DECIMAL_ACTUAL_NODE_VERIFICATION.json",
              "evidence/theory/DECIMAL_SOURCE_VERIFICATION.json",
              "evidence/theory/DECIMAL_EDGE_VERIFICATION.json"]
    native = json.loads((ROOT / inputs[0]).read_text())
    scalar = list(csv.DictReader((ROOT / inputs[1]).open()))
    source = list(csv.DictReader((ROOT / inputs[2]).open()))
    new = [c for c in native["cases"] if c["reuse"] == "NEW_BR04_NATIVE_HISTORY"]
    assert len(new) == 2
    maxima = {key: str(max(Decimal(c["verification"]["maxima"][key]) for c in new))
              for key in ("number_relative", "energy_relative", "species_relative")}
    r4 = native["fixed_r_time_slices"]["4"]
    results = {
        "schema": "rei.br04.science_results.v1",
        "unit": "BASS-REACTIVE-04_TIME_AGE",
        "scientific_status": "COMPLETE_VERIFIED_SCOPED_DIAGNOSTIC_CONTROL",
        "longspan_status": "NOT_ADMITTED_JOINT_TIME_AGE_CONVERGENCE_INCOMPLETE",
        "new_physics": False,
        "native": {"new_cases": [{k: c[k] for k in ("name", "N_t", "r", "wall_s", "final", "verification")} for c in new],
                   "new_macrosteps": sum(c["N_t"] for c in new),
                   "wall_s": sum(c["wall_s"] for c in new),
                   "reused_histories": len(native["cases"])-len(new),
                   "complete_rectangles": native["complete_rectangles"],
                   "max_independent_ledger_residuals": maxima,
                   "ledger_normalization": {"number":"cumulative emitted photon count", "species":"cumulative emitted photon count", "energy":"max magnitude of actual, expected, and initial total gas+radiation energy"},
                   "r4_time_slice": r4,
                   "mixed_differences": {key: value["final"] for key, value in native["rectangles"].items()},
                   "decision": "Two time-by-birth interactions measured. Mean age and q2 are sensitive to birth refinement; universal second order and native distribution convergence are not demonstrated."},
        "frozen_scalar": {"comparison_cases": len(scalar)//2, "measure_rows": len(scalar),
                          "tau93_single_step_survivors": [r for r in scalar if float(r["tau"])==93 and r["measure"]=="survivor" and r["nsteps"]=="1"],
                          "thick_scope": "AP tested through tau1e12; five parent fitted-rule calls at tau1e300 return NoForwardProgress and are classified as representation limits."},
        "frozen_source": {"labels":384,"unique_opacities":48,"comparison_cases":2304,"measure_rows":4608,
                          "survivor_rows":[r for r in source if r["measure"]=="survivor"],
                          "distance_scope":"Mixture CDF/W1 upper bounds from retained label certificates plus label-weight TV; not exact unlabelled mixture distances."},
        "independent": {},
        "input_sha256": {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs},
        "scope_limits": ["Frozen density/opacity reference does not bound evolving gas response without additional stability estimates.",
                         "Native output contains age moments and energy-weighted q2, not full age-energy-angle joint distributions.",
                         "Formal finite-difference orders are observational ratios, not an established asymptotic error model.",
                         "Source, spectral, angular, threshold and two-way Einstein obligations remain open."]
    }
    for path, key in zip(inputs[3:], ("scalar", "source", "edges")):
        data=json.loads((ROOT/path).read_text())
        results["independent"][key]={k:v for k,v in data.items() if k not in ("comparisons","input_hashes","created_utc","python")}
    (ROOT/"evidence/SCIENCE_RESULTS.json").write_text(json.dumps(results,indent=2)+"\n")
    print(json.dumps({"status":results["scientific_status"],"new_steps":results["native"]["new_macrosteps"],"new_native_wall_s":results["native"]["wall_s"]}))


if __name__ == "__main__":
    main()
