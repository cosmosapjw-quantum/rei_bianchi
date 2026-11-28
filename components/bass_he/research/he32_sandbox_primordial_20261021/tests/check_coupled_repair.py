"""Reuse saved independent derivative references after the chemistry FD repair.

No repeated 52-column finite differences, no I/O-suite repetition and no IVP.
The unchanged RHS must match each original point exactly before reuse is admitted.
"""
from __future__ import annotations
import os
for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[name] = "1"
import argparse
import json
from pathlib import Path
import sys
import numpy as np

UNIT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(UNIT/"src"))
import coupled_pilot as science


def forbid(*args,**kwargs):
    raise AssertionError("No IVP is allowed in the saved-reference repair check")


science.solve_ivp=forbid


def fingerprints():
    paths=("src/coupled_pilot.py","src/compact_transport.py","src/primordial_network.py",
           "src/atomic_photo_rr.py","data/ISOTOPE_SCENARIO.json","data/ATOMIC_PHOTO_RR.json")
    return {path:science.file_sha(UNIT/path) for path in paths}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    old_path=args.reference/"INDEPENDENT_COUPLED_REVIEW.json"
    data_path=args.reference/"INDEPENDENT_COUPLED_DERIVATIVE_POINTS.npz"
    previous=json.loads(old_path.read_text())
    if science.file_sha(data_path)!=previous["derivative_data_sha256"]:
        raise ValueError("Saved reference bytes changed")
    record=dict(schema="he32.independent_coupled_repair.v1",science_ivp_runs=0,benchmark_runs=0,
                reference_json_sha256=science.file_sha(old_path),reference_data_sha256=science.file_sha(data_path),
                source_hashes_before=fingerprints(),threshold_scaled_jacobian=previous["thresholds"]["scaled_jacobian_error"],
                reference_reuse="3 saved points; unchanged RHS equality required; no finite-difference reference recomputation",
                io_tests="Not repeated; all 11 source-identity/atomic-I/O checks passed in the referenced v1 report",
                points=[])
    saved={}
    with np.load(data_path,allow_pickle=False) as archive:
        for old in previous["point_checks"]:
            index=old["point"]
            model=science.CoupledPilot(old["parameters"])
            y=archive[f"point{index}_state"]
            reference=archive[f"point{index}_five_point_reference"]
            rhs=science.CoupledPilot.rhs(model,old["eta"],y)
            unchanged=bool(np.array_equal(rhs,archive[f"point{index}_rhs"]))
            if not unchanged:
                raise ValueError("RHS changed at saved point; old reference reuse not admitted")
            jac=model.jacobian(old["eta"],y)
            delta=np.abs(jac-reference)
            scaled=delta/(1+np.maximum(np.abs(jac),np.abs(reference)))
            row=dict(point=index,eta=old["eta"],RHS_binary64_equal=unchanged,
                     maximum_absolute_difference=float(delta.max()),maximum_scaled_difference=float(scaled.max()),
                     pass_=bool(scaled.max()<=record["threshold_scaled_jacobian"]))
            record["points"].append(row)
            saved[f"point{index}_jacobian"]=jac
        # The fixed-source baryon census bounds every epoch because a increases.
        chemistry=model.chemistry
        nb_max=chemistry.nH0_m3*chemistry.baryons_per_H*1e-6/chemistry.aref**3
        record["proper_baryon_max_cm3"]=nb_max
        record["proper_baryon_bound_lt_0p01"]=bool(nb_max<.01)
    record["source_hashes_after"]=fingerprints()
    record["source_unchanged_during_check"]=(record["source_hashes_before"]==record["source_hashes_after"])
    np.savez_compressed(args.out/"REPAIRED_JACOBIANS.npz",**saved)
    record["repaired_jacobians_sha256"]=science.file_sha(args.out/"REPAIRED_JACOBIANS.npz")
    record["decision"]=("PASS_SCOPED_COUPLED_REPAIR" if all(p["pass_"] for p in record["points"])
                        and record["source_unchanged_during_check"] and record["proper_baryon_bound_lt_0p01"]
                        else "FINDING_REQUIRES_REPAIR")
    (args.out/"INDEPENDENT_COUPLED_REPAIR.json").write_text(json.dumps(science.plain(record),indent=2)+"\n")
    print(json.dumps({"decision":record["decision"],"science_ivp_runs":0,
                      "max_scaled_jacobian":max(r["maximum_scaled_difference"] for r in record["points"]),
                      "proper_baryon_max_cm3":nb_max,"source_unchanged":record["source_unchanged_during_check"]}))
    return 0 if record["decision"]=="PASS_SCOPED_COUPLED_REPAIR" else 2


if __name__=="__main__":
    raise SystemExit(main())
