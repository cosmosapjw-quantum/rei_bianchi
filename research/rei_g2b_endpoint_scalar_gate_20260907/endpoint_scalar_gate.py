"""Read-only exact-rational G2b saved-endpoint calculation; no production import.

Binary64 stored values and parsed source constants are lifted exactly BEFORE
arithmetic. Products, elemental sums, normalization, faces and widths use Fraction.
This does not simulate binary64 source reductions or certify the box producer.
"""
from __future__ import annotations

import ast
import csv
from fractions import Fraction as Q
from itertools import product
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PARENT = "4c52886dc101af3ffdb9ee4edee0716bd149b25d"
LANE = "LOCAL_NEUTRAL_HAZARD_PRIMARY"
COUNT_FIELDS = ("N_HI", "N_HII", "N_HeI", "N_HeII", "N_HeIII")


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def binary_q(value):
    return Q(*float(value).as_integer_ratio())


def record(value):
    value = Q(value)
    return {"numerator": str(value.numerator), "denominator": str(value.denominator),
            "display_float_not_certificate": float(value)}


def weighted_share(totals, values):
    return sum((h * x for h, x in zip(totals, values, strict=True)), Q(0)) / sum(totals)


def contributions(h, he, qh, qe, charged):
    xh, xe2, xe3 = charged
    sh = weighted_share(h, (1 - x for x in xh))
    se = weighted_share(he, (1 - x - y for x, y in zip(xe2, xe3, strict=True)))
    return qh * sh, qe * se


def classify(denominator):
    return ("ENDPOINT_DENOMINATOR_POSITIVE" if denominator > 0
            else "ENDPOINT_CARTESIAN_REPRESENTATION_INSUFFICIENT")


def bound_file(path):
    relative = str(path.relative_to(ROOT))
    blob = git("rev-parse", f"{PARENT}:{relative}")
    if git("hash-object", str(path)) != blob:
        raise ValueError(f"immutable input byte mismatch: {relative}")
    return {"path": relative, "commit": PARENT, "blob": blob, "bytes": path.stat().st_size}


def assignment_literal(path, name):
    text = path.read_text()
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name
                                              for t in node.targets):
            return ast.get_source_segment(text, node.value)
    raise ValueError(f"missing constant {name}")


def source_mask(path):
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "owner_support"
                                              for t in node.targets):
            return ast.literal_eval(node.value.args[0])
    raise ValueError("owner mask missing")


def main():
    inherited = json.loads((ROOT / "research/rei_owner_first_cell_bound_20260907/RESULT_AND_INPUTS.json").read_text())
    paths = {key: ROOT / val for key, val in inherited["sources"].items()}
    box_path = paths["CROSS"] / "data/VALIDATED_PUBLIC_BOXES.npz"
    initial_path = paths["INITIAL"] / "data/initial_material_state_z6.npz"
    tensor_path = paths["ADAPT"] / "analysis/tensorized_inputs.py"
    owner_path = paths["ADAPT"] / "analysis/array_owner_kernel.py"
    atomic_path = paths["FORCING"] / "data/atomic_moments/verner_gray_and_limit_moments.csv"
    forcing_path = paths["FORCING"] / "data/bdf_replay/canonical_time_resolved_forcing_nodes.csv"
    external_path = paths["INITIAL"] / "data/owner_law_time_matrix.csv"
    metadata_path = paths["INITIAL"] / "data/initial_material_state_metadata.json"
    lane_path = paths["CROSS"] / f"data/LANE_{LANE}.json"
    input_files = [box_path, initial_path, tensor_path, owner_path, atomic_path,
                   forcing_path, external_path, metadata_path, lane_path,
                   paths["CROSS"] / "analysis/containment_audit.py",
                   paths["CROSS"] / "analysis/interval_discrete_map.py",
                   paths["CROSS"] / "data/STAGEWISE_ENDPOINT_CONTAINMENT.json"]
    bindings = [bound_file(p) for p in input_files]
    assert bindings[0]["blob"] == "8f67740b43c82be04f8efd521990b7b2b185afea"
    assert bindings[1]["blob"] == "e3a2a55f1187e958276193d7368541ca11197c31"
    with np.load(box_path, allow_pickle=False) as data:
        lower = data[f"{LANE}__lower"]
        upper = data[f"{LANE}__upper"]
    with np.load(initial_path, allow_pickle=False) as data:
        initial = [data[key] for key in COUNT_FIELDS]
    for array, shape in [(lower, (4, 46080)), (upper, (4, 46080)),
                         *[(a, (46080,)) for a in initial]]:
        if array.shape != shape or array.dtype != np.dtype("float64") or not np.isfinite(array).all():
            raise ValueError("unexpected array shape/dtype or nonfinite value")
    if not np.all(lower <= upper) or not all(np.all(a >= 0) for a in initial):
        raise ValueError("unordered box or negative initial population")
    print("INTAKE PASS: fixed blobs, allow_pickle=False, shapes, finite values and ordered box", flush=True)

    # No ordinary-float addition or subtraction before these lifts.
    populations = [tuple(map(binary_q, a)) for a in initial]
    h = tuple(x + y for x, y in zip(*populations[:2], strict=True))
    he = tuple(x + y + z for x, y, z in zip(*populations[2:], strict=True))
    assert min(h) > 0 and min(he) > 0
    H, He = sum(h), sum(he)
    lo = [tuple(map(binary_q, row)) for row in lower[:3]]
    up = [tuple(map(binary_q, row)) for row in upper[:3]]
    mid = [tuple((l + u) / 2 for l, u in zip(lrow, urow, strict=True))
           for lrow, urow in zip(lo, up, strict=True)]
    width = [tuple(u - l for l, u in zip(lrow, urow, strict=True))
             for lrow, urow in zip(lo, up, strict=True)]

    literals = {"NH0": assignment_literal(owner_path, "NH0_CM3"),
                "YHE": assignment_literal(owner_path, "YHE"),
                "MPC_CM": assignment_literal(tensor_path, "MPC_CM")}
    rows = list(csv.DictReader(atomic_path.open()))
    for species, key in [("HI", "sigma_HI_G2b"), ("HeI", "sigma_HeI_G2b")]:
        row = next(r for r in rows if r["species"] == species and r["group"] == "G2b")
        assert row["supported"] == "True"
        literals[key] = row["gray_sigma_cm2"]
    const = {name: binary_q(float(value)) for name, value in literals.items()}
    qh = const["NH0"] * const["MPC_CM"] * const["sigma_HI_G2b"]
    qe = const["NH0"] * const["YHE"] * const["MPC_CM"] * const["sigma_HeI_G2b"]
    assert 0 < qh < Q("0.124") and 0 < qe < Q("0.113")
    mask = source_mask(tensor_path)
    controls = []

    def check(identifier, condition, description):
        assert condition, f"{identifier}: {description}"
        controls.append({"id": identifier, "result": "PASS", "description": description})
        print(f"{identifier} PASS: {description}", flush=True)

    check("G01", sum(x / H for x in h) == sum(x / He for x in he) == 1,
          "actual elemental weights normalize to exactly one")
    # Independent vertex enumeration: direct scalar expansion, no face helper.
    hs, hes = (Q(1), Q(3)), (Q(2), Q(5))
    ls = ((Q(1, 5), Q(1, 4)), (Q(1, 3), Q(1, 4)), (Q(1, 7), Q(1, 8)))
    us = ((Q(3, 5), Q(1, 2)), (Q(1, 2), Q(1, 3)), (Q(1, 5), Q(1, 6)))
    vertices = []
    for flags in product((0, 1), repeat=6):
        x = [us[s][i] if flags[2*s+i] else ls[s][i] for s in range(3) for i in range(2)]
        vertices.append(Q(2) * ((1-x[0]) + 3*(1-x[1])) / 4
                        + Q(3) * (2*(1-x[2]-x[4]) + 5*(1-x[3]-x[5])) / 7)
    check("G02", min(vertices) == sum(contributions(hs, hes, Q(2), Q(3), us)),
          "upper face equals minimum of independently expanded 64 rational vertices")
    share = weighted_share(hs, (Q(3, 4), Q(1, 4)))
    double_weight_mutant = sum((hs[k]/4)**2 * (Q(3, 4), Q(1, 4))[k] for k in range(2))
    split = weighted_share((Q(1), Q(1), Q(2)), (Q(3, 4), Q(1, 4), Q(1, 4)))
    check("G03", share == split == Q(3, 8) and share != double_weight_mutant,
          "extensive counts weighted once; node splitting invariant; double-weight mutant rejected")
    check("G04", mask == [[1,1,0,0],[0,0,1,1],[0,1,1,1],[0,0,0,1]]
          and [row[2] for row in mask] == [0,1,1,0],
          "source G2b owner mask is exactly HI plus HeI")

    hface, heface = contributions(h, he, qh, qe, up)
    hlo, helo = contributions(h, he, qh, qe, lo)
    hm, hem = contributions(h, he, qh, qe, mid)
    dlo, dmid, dhi = hface + heface, hm + hem, hlo + helo
    penalty = (qh * weighted_share(h, width[0])
               + qe * weighted_share(he, (x+y for x,y in zip(width[1], width[2], strict=True)))) / 2
    max_widths = [max(w) for w in width]
    coarse = (Q("0.124")*max_widths[0] + Q("0.113")*(max_widths[1]+max_widths[2])) / 2
    check("G05", dlo == dmid - penalty and dhi == dmid + penalty
          and 0 <= penalty < coarse < Q("1e-6"),
          "actual lower-face/midpoint/upper-face exact identity and coarse width budget")
    check("G06", classify(Q(1, 10)) == "ENDPOINT_DENOMINATOR_POSITIVE"
          and all(classify(x) == "ENDPOINT_CARTESIAN_REPRESENTATION_INSUFFICIENT"
                  for x in (Q(0), Q(-1, 10))),
          "positive, zero and negative controls classified without a floor")

    # Literal checks reuse the parent shape-preserving first-cell theorem.
    # No PCHIP evaluator, bound helper or producer is imported or executed.
    forcing = [r for r in csv.DictReader(forcing_path.open())
               if r["interval_index"] == "0" and r["node_index"] in ("0", "1")]
    external = [r for r in csv.DictReader(external_path.open())
                if r["interval_index"] == "0" and r["node_index"] in ("0", "1")
                and r["group"] == "G2b" and r["component"] == "EFFECTIVE_HI_SUBGRID"]
    jmax = Q("1.4e48")  # exact conservative theorem bound, not rounded source operation
    assert len(forcing) == len(external) == 2
    assert all(0 < Q(r["absorption_G2b_s-1_cMpc-3"]) < jmax
               and 0 < binary_q(float(r["absorption_G2b_s-1_cMpc-3"])) < jmax
               and Q(r["kappa_G2b_cMpc-1"]) > 0 for r in forcing)
    assert all(Q(r["raw_component_kappa_cMpc_inv"]) == 0 for r in external)
    conditional = 2*jmax*max(qh, qe)/dlo if dlo > 0 else None
    neutral_h = [1-x for x in up[0]]
    neutral_he = [1-x-y for x,y in zip(up[1], up[2], strict=True)]
    metadata = json.loads(metadata_path.read_text())
    ordinary_h = float(np.sum(initial[0] + initial[1]))
    ordinary_he = float(np.sum(initial[2] + initial[3] + initial[4]))
    exact_values = {"H_total": H, "He_total": He, "q_H": qh, "q_He": qe,
                    "H_contribution_lo": hface, "He_contribution_lo": heface,
                    "D_lo": dlo, "D_mid": dmid, "D_hi": dhi,
                    "X_HI_mid": hm/qh, "X_HeI_mid": hem/qe,
                    "width_penalty": penalty, "coarse_width_penalty": coarse,
                    "minimum_node_HI_upper_face": min(neutral_h),
                    "minimum_node_HeI_upper_face": min(neutral_he), "J_max": jmax}
    if conditional is not None:
        exact_values["conditional_L_G2b_upper"] = conditional
    result = {"task": "REI_G2B_ENDPOINT_SCALAR_GATE", "status": classify(dlo),
              "input_commit": PARENT, "input_tree": git("rev-parse", f"{PARENT}^{{tree}}"),
              "tested_source": {"commit": git("rev-parse", "HEAD"), "tree": git("rev-parse", "HEAD^{tree}"),
                                "script_blob": git("hash-object", str(Path(__file__))),
                                "script_path": str(Path(__file__).relative_to(ROOT))},
              "arithmetic_model": "EXACT_RATIONAL_OF_STORED_BINARY64_ARRAYS_AND_PARSED_BINARY64_SOURCE_CONSTANTS; Jmax exact decimal conservative bound",
              "arithmetic_details": "Lift with as_integer_ratio before sums/products/subtractions; h/he and H/He are exact sums of the stored initial population entries; no rounded NumPy totals enter normalization. Source constant products are exact products of parsed operands, not emulated machine operations.",
              "lane": LANE, "node_count": len(h), "input_bindings": bindings,
              "source_literals": literals, "parsed_constant_values": {k:record(v) for k,v in const.items()},
              "owner_support": mask, "controls": controls,
              "exact": {k:record(v) for k,v in exact_values.items()},
              "actual_exact_maximum_widths": [record(x) for x in max_widths],
              "diagnostics": {"negative_HI_upper_face_nodes": sum(x<0 for x in neutral_h),
                              "negative_HeI_upper_face_nodes": sum(x<0 for x in neutral_he),
                              "nonpositive_HeI_upper_face_nodes": sum(x<=0 for x in neutral_he),
                              "midpoint_coarse_positivity_gate": dmid > Q("1e-6"),
                              "ordinary_source_H_sum": ordinary_h, "ordinary_source_He_sum": ordinary_he,
                              "metadata_H_total": metadata["global_H_nuclei_cMpc-3"],
                              "metadata_He_total": metadata["global_He_nuclei_cMpc-3"],
                              "ordinary_H_minus_metadata": ordinary_h-metadata["global_H_nuclei_cMpc-3"],
                              "ordinary_He_minus_metadata": ordinary_he-metadata["global_He_nuclei_cMpc-3"],
                              "normalization_diagnostics_are_not_a_tolerance_gate": True},
              "first_cell_inputs": [{k:r[k] for k in ["time_s","z_mid","absorption_G2b_s-1_cMpc-3","kappa_G2b_cMpc-1"]} for r in forcing],
              "historical_lane_report_not_rerun": json.loads(lane_path.read_text()),
              "bound_domain": "Saved Cartesian endpoint gives the affine denominator minimum; JVP constant is for the physically admissible nonnegative-share subset, with fixed elemental totals and fixed comparison time/forcing, conditional on inherited box inclusion and first-cell exact-real PCHIP hull.",
              "source_site": "second-half thermal_t1_final corrected population; no other site or continuous trajectory tube",
              "input_norm": "l1 of extensive HI/H and HeI/He global-element-normalized node shares",
              "output_norm": "l1 of resolved G2b HI and HeI node photon currents",
              "units": {"D": "cMpc^-1 with common (1+z)^2 removed", "L": "box photons/s per unit dimensionless input l1 share"},
              "runtime": {"python": sys.version, "executable": sys.executable,
                          "numpy": np.__version__, "numpy_path": np.__file__},
              "claim_ceiling": {"producer_revalidated": False, "binary64_owner_parity": False,
                                "complete_source_input_tube": "UNKNOWN", "OTS_atomic_derivatives": "OPEN",
                                "thermal_inverse": "OPEN", "exact_flow_rho": "OPEN", "production_PASS": False},
              "old_suite_replays": 0, "production_imports": False, "producer_runs": 0}
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    for key in ["H_contribution_lo", "He_contribution_lo", "D_lo", "D_mid", "width_penalty", "coarse_width_penalty"]:
        value = exact_values[key]
        print(f"{key} EXACT {value.numerator}/{value.denominator}\n{key} DISPLAY {float(value):.17g}", flush=True)
    if conditional is not None:
        print(f"conditional_L_G2b_upper EXACT {conditional}\nconditional_L_G2b_upper DISPLAY {float(conditional):.17g}", flush=True)
    print(f"RESULT {result['status']}; controls={len(controls)}/6; no old suite or producer replay", flush=True)


if __name__ == "__main__":
    main()
