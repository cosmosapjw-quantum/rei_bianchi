"""Independent coupled-Jacobian, shear-budget and immutable-I/O point checks.

This script forbids solve_ivp and never generates a physical trajectory.  Its
three stored states are off-trajectory derivative points, not pilot results.
"""
from __future__ import annotations
import os
for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile

import numpy as np

UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT / "src"))
import coupled_pilot as science


def forbidden_ivp(*args, **kwargs):
    raise AssertionError("IVP execution is forbidden in this independent point review")


science.solve_ivp = forbidden_ivp


def hashes():
    paths = ("src/coupled_pilot.py", "src/compact_transport.py", "src/primordial_network.py",
             "src/atomic_photo_rr.py", "data/ATOMIC_PHOTO_RR.json", "data/ISOTOPE_SCENARIO.json")
    return {name: science.file_sha(UNIT / name) for name in paths}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    record = dict(schema="he32.independent_coupled_point_review.v1", status="running",
                  science_ivp_runs=0, benchmark_runs=0, source_hashes_before=hashes(),
                  thresholds=dict(scaled_jacobian_error=2e-7, scaled_directional_error=2e-7,
                                  shear_budget_derivative_scaled=2e-12),
                  independent_stencil="five-point central difference, h=1e-4*max(1,abs(y_j))",
                  point_checks=[])

    def save():
        (args.out / "INDEPENDENT_COUPLED_REVIEW.json").write_text(json.dumps(science.plain(record), indent=2)+"\n")

    save()
    point_data = {}
    specifications = [dict(Sigma_F=0., P_m=0., P_r=0., eta=0., b=0.),
                      dict(Sigma_F=.003, P_m=.0003, P_r=-.001, eta=.8, b=.04),
                      dict(Sigma_F=.6, P_m=0., P_r=0., eta=1.6, b=.12)]
    for index, spec in enumerate(specifications):
        config = {key: spec[key] for key in ("Sigma_F", "P_m", "P_r")}
        model = science.CoupledPilot(config)
        x = spec["eta"]
        y = model.initial_state()
        y[0], y[1], y[2] = .7*x, spec["b"], y[2]*math.exp(-x)
        towers = y[3:model.nt].reshape(4, model.transport.n)
        towers[0, 0], towers[2, 0] = 1.05, 1.03
        for k in range(4):
            towers[k, 1] += .002*(k+1)
            towers[k, 2] = .0003*(k-1.5)
        # Interior values exercise all electronic derivative columns, including
        # high Li charges that stay exactly zero in the selected pilot IC.
        y[model.chem] = [.6, .4, .3, .4, .3, .2, .3, .25, .25]
        j = model.jacobian(x, y)
        reference = np.empty_like(j)
        for col in range(model.size):
            h = 1e-4 * max(1., abs(float(y[col])))
            pp, p, m, mm = [y.copy() for _ in range(4)]
            pp[col] += 2*h
            p[col] += h
            m[col] -= h
            mm[col] -= 2*h
            reference[:, col] = ((model.rhs(x, mm)-model.rhs(x, pp))
                                  + 8*(model.rhs(x, p)-model.rhs(x, m)))/(12*h)
        delta = np.abs(j-reference)
        scaled = delta/(1+np.maximum(np.abs(j), np.abs(reference)))
        geom_cols = [1, 2, 3, 3+2*model.transport.n]
        analytic_cols = [k for k in range(model.size) if k not in geom_cols]
        vector = np.sin(np.arange(model.size)+.3)
        step = 2e-5
        finite_jvp = (model.rhs(x, y+step*vector)-model.rhs(x, y-step*vector))/(2*step)
        jvp = j@vector
        jvp_error = float(np.max(np.abs(jvp-finite_jvp)/(1+np.maximum(np.abs(jvp),np.abs(finite_jvp)))))
        rhs = model.rhs(x, y)
        budget_expected = math.exp(3*x)*(3*y[2]+rhs[2])
        budget_actual = float(np.sum(rhs[model.budget]))
        budget_error = abs(budget_actual-budget_expected)/(1+max(abs(budget_actual),abs(budget_expected)))
        groups = (slice(0,2),slice(2,5),slice(5,9))
        conservation = [float(np.sum(rhs[model.chem][group])) for group in groups]
        row = dict(point=index, parameters=config, eta=x, state_dimension=model.size,
                   maximum_absolute_jacobian_difference=float(np.max(delta)),
                   maximum_scaled_jacobian_difference=float(np.max(scaled)),
                   geometry_columns_max_scaled=float(np.max(scaled[:,geom_cols])),
                   analytic_columns_max_scaled=float(np.max(scaled[:,analytic_cols])),
                   directional_max_scaled=jvp_error,
                   shear_budget_derivative_scaled_error=budget_error,
                   chemical_group_rhs_sums=conservation,
                   photon_number_monopole_derivative=float(rhs[3+model.transport.n]),
                   neutrino_number_monopole_derivative=float(rhs[3+3*model.transport.n]))
        row["pass"] = bool(np.max(scaled)<=record["thresholds"]["scaled_jacobian_error"]
                           and jvp_error<=record["thresholds"]["scaled_directional_error"]
                           and budget_error<=record["thresholds"]["shear_budget_derivative_scaled"]
                           and row["photon_number_monopole_derivative"]==0.
                           and row["neutrino_number_monopole_derivative"]==0.)
        record["point_checks"].append(row)
        point_data.update({f"point{index}_state":y,f"point{index}_jacobian":j,
                           f"point{index}_five_point_reference":reference,
                           f"point{index}_rhs":rhs})
        save()

    # Metadata tests use explicitly labelled transient I/O fixtures, never the
    # campaign's results/cases directory and never a claimed science solution.
    base = dict(Sigma_F=0, P_m=0, P_r=0)
    same = dict(Sigma_F=0., P_m=0., P_r=0., samples=201., ellmax=16., case_id="alias", role="io_test")
    identities_equal = science.case_identity(base)==science.case_identity(same)
    changed_identity = science.case_identity(base)!=science.case_identity(dict(base,rtol=1e-10))
    io = dict(integer_float_alias_same_identity=identities_equal,
              tolerance_change_changes_identity=changed_identity)
    with tempfile.TemporaryDirectory(prefix="he32_independent_io_fixture_") as directory:
        temporary = Path(directory)
        path = temporary/"labelled_io_fixture.npz"
        metadata = dict(schema=science.SCHEMA, status="independent_io_fixture_not_a_trajectory",
                        case_id="labelled_io_fixture", identity=science.case_identity(base),
                        config=science.normalize(base), checks={}, npz=path.name,
                        purpose="metadata recovery test only; no solve_ivp call")
        payload = np.arange(12,dtype=float).reshape(3,4)
        science.atomic_npz(path, {"fixture_array":payload,
                                 "metadata_json":np.asarray(science.canonical(metadata).decode())})
        original_sha = science.file_sha(path)
        with np.load(path,allow_pickle=False) as archive:
            io["npz_roundtrip_exact"] = bool(np.array_equal(payload,archive["fixture_array"]))
        try:
            science.atomic_npz(path, {"must_not_replace":payload})
        except FileExistsError:
            io["existing_npz_not_overwritten"] = science.file_sha(path)==original_sha
        else:
            io["existing_npz_not_overwritten"] = False
        recovered = science.recover_receipt(path)
        io["metadata_only_recovery_hash_exact"] = recovered["npz_sha256"]==original_sha
        io["nontrajectory_fixture_not_reusable"] = not science.completed_result(base,path.with_suffix(".json"))
        for label, checks in (("empty",{}),("truthy_integer",{name:1 for name in science.CHECK_NAMES}),
                              ("missing",{name:True for name in science.CHECK_NAMES if name!="finite"})):
            malformed = dict(recovered, status="completed", checks=checks)
            malformed_path = temporary/(label+".json")
            malformed_path.write_text(json.dumps(malformed))
            io[label+"_gates_rejected"] = not science.completed_result(base,malformed_path)
        wrong_hash = dict(recovered, status="completed", checks={name:True for name in science.CHECK_NAMES},
                          npz_sha256="0"*64)
        wrong_path = temporary/"wrong_hash.json"
        wrong_path.write_text(json.dumps(wrong_hash))
        io["checksum_mismatch_rejected"] = not science.completed_result(base,wrong_path)
        io["original_npz_bytes_preserved"] = science.file_sha(path)==original_sha
    record["io_and_identity_checks"] = io
    record["source_hashes_after"] = hashes()
    record["science_sources_unchanged"] = record["source_hashes_before"]==record["source_hashes_after"]
    np.savez_compressed(args.out/"INDEPENDENT_COUPLED_DERIVATIVE_POINTS.npz",**point_data)
    record["derivative_data_sha256"] = science.file_sha(args.out/"INDEPENDENT_COUPLED_DERIVATIVE_POINTS.npz")
    record["status"] = ("PASS_SCOPED_COUPLED_POINT_REVIEW" if all(r["pass"] for r in record["point_checks"])
                        and all(io.values()) and record["science_sources_unchanged"] else "FINDING_REQUIRES_REPAIR")
    save()
    print(json.dumps(dict(status=record["status"],science_ivp_runs=0,
                         max_scaled_jacobian=max(r["maximum_scaled_jacobian_difference"] for r in record["point_checks"]),
                         source_unchanged=record["science_sources_unchanged"])))
    return 0 if record["status"]=="PASS_SCOPED_COUPLED_POINT_REVIEW" else 2


if __name__ == "__main__":
    raise SystemExit(main())
