#!/usr/bin/env python3
"""Analyze only the two preregistered C2g finite-basis reference layouts.

No eigensolve is reachable here. Large frames stay in a three-entry LRU cache;
JSON contains small matrices and diagnostic scalars, never sampled wavefunctions.
"""
from __future__ import annotations

import argparse
from collections import OrderedDict
from dataclasses import asdict
import json
from pathlib import Path
import time
import traceback

import numpy as np

from common_embedding import build_common_grid, snapshot_from_archives, write_source_binding
from multistate_provider import load_sector
from physical_contract import approved_inputs, load_json, source_identity
from projector import TargetSpec, ValidationTolerances, parallel_transport, validate_snapshot
from runtime_support import ContractError, atomic_create, file_identity


SCOPE = {
    "finite_basis_electronic_reference_only": True,
    "continuum_certificate": False, "full_H_certificate": False,
    "PDE_residual_certified": False, "atomic_correlation_established": False,
    "outside_box_tail_bound": False, "full_C2_closed": False,
    "scientific_PROMOTE": "HOLD", "full_certificate_fail_closed": True,
    "Eq55_next_node_authorized": False, "Eq55": "NOT_RUN",
    "production_default_change": "NOT_AUTHORIZED", "NCP64_actual_scaling": False,
}


def validate_layout_arguments(preregistration, layouts):
    expected = [row["id"] for row in preregistration["campaign"]["layouts"]]
    if len(expected) != 2 or len(set(expected)) != 2:
        raise ContractError("analysis requires exactly two distinct registered layouts")
    if set(layouts) != set(expected):
        raise ContractError("exactly the two registered layouts are required; missing or extra layout")
    if len({str(Path(p).resolve()) for p in layouts.values()}) != 2:
        raise ContractError("the two layouts must reference different results")
    return expected


def normalized_observables(frame, weights, r, outer_layer=(16., 20.)):
    """Symmetric Gram normalization; invariants of the supplied selected span.

    Does not silently claim acceptance when Gram is far from identity: the
    uncorrected defect and normalization correction are returned to the caller.
    """
    frame, weights, r = np.asarray(frame), np.asarray(weights), np.asarray(r)
    if (frame.ndim != 2 or weights.shape != (len(frame),) or r.shape != weights.shape
            or not np.isfinite(frame).all() or not np.isfinite(weights).all()
            or not np.isfinite(r).all() or np.any(weights <= 0)):
        raise ContractError("invalid finite positive-metric observable inputs")
    gram = frame.conj().T @ (weights[:, None] * frame)
    herm = (gram + gram.conj().T) * .5
    eig, vec = np.linalg.eigh(herm)
    if eig[0] <= np.finfo(float).eps * len(eig) * eig[-1]:
        raise ContractError("selected frame is numerically rank deficient")
    whitening = (vec * (1. / np.sqrt(eig))[None, :]) @ vec.conj().T
    r2_raw = frame.conj().T @ ((weights * r*r)[:, None] * frame)
    layer = (r >= outer_layer[0]) & (r <= outer_layer[1])
    tail_raw = frame.conj().T @ ((weights * layer)[:, None] * frame)
    r2 = whitening.conj().T @ r2_raw @ whitening
    tail = whitening.conj().T @ tail_raw @ whitening
    identity = np.eye(frame.shape[1])
    values = {
        "trace_r2": float(np.trace(r2).real),
        "outer_layer_probability_max": float(np.linalg.eigvalsh((tail + tail.conj().T)*.5)[-1]),
        "selected_Gram_max_entry_error": float(np.max(np.abs(gram-identity))),
        "selected_Gram_operator_norm_error": float(np.linalg.norm(gram-identity, 2)),
        "symmetric_normalization_correction_operator_norm": float(np.linalg.norm(whitening-identity, 2)),
        "normalization": "explicit symmetric positive Gram inverse square root",
        "outer_layer_scope": "basis-invariant within-box concentration, not exterior-tail probability bound",
    }
    return values, whitening


def common_frame_comparison(left, right, weights):
    """Raw diagnostic geometry even if a separately registered gate fails.

    A residual SVD avoids cancellation from sqrt(1-sigma**2) at backend parity.
    No polar alignment is performed or authorized by this function.
    """
    zeros = np.zeros(len(weights))
    _, cl = normalized_observables(left, weights, zeros)
    _, cr = normalized_observables(right, weights, zeros)
    u, v = left @ cl, right @ cr
    overlap = u.conj().T @ (weights[:, None]*v)
    sigma = np.linalg.svd(overlap, compute_uv=False)
    residual = np.sqrt(weights)[:, None]*(v-u@overlap)
    sines = np.linalg.svd(residual, compute_uv=False)
    return {"principal_overlap_singular_values": sigma.tolist(),
            "principal_overlap_sigma_min": float(sigma[-1]),
            "projector_operator_distance": float(sines[0]),
            "projector_frobenius_distance": float(np.sqrt(2)*np.linalg.norm(sines))}, overlap


class Gates:
    def __init__(self):
        self.rows = []

    def add(self, name, value, threshold, *, comparison="le", category="implementation"):
        if not np.isfinite(value) or not np.isfinite(threshold):
            raise ContractError("nonfinite measured value or registered gate")
        ok = value <= threshold if comparison == "le" else value > threshold
        row = {"name": name, "value": float(value), "threshold": float(threshold),
               "comparison": "<=" if comparison == "le" else ">", "pass": bool(ok), "category": category}
        self.rows.append(row)
        return bool(ok)

    def result(self):
        failed = [row for row in self.rows if not row["pass"]]
        return {"all": self.rows, "first_failed_gate": failed[0] if failed else None,
                "failed_count": len(failed),
                "implementation_pass": all(x["pass"] for x in self.rows if x["category"] == "implementation"),
                "candidate_transport_pass": all(x["pass"] for x in self.rows if x["category"] == "candidate_transport"),
                "finite_basis_exploration_pass": all(x["pass"] for x in self.rows if x["category"] == "finite_basis_exploration")}


def _complex_matrix(a):
    return {"real": a.real.tolist(), "imag": a.imag.tolist()}


def _verify_file(identity):
    if file_identity(identity["path"]) != identity:
        raise ContractError("recorded file identity changed: " + identity["path"])


def load_layout(layout, path, manifest, inputs, current_source):
    launch_identity = file_identity(path)
    launch = load_json(path)
    if launch.get("schema") != "bass-he.c2g.physical-launch-result.v1" or launch.get("status") != "PASS":
        raise ContractError("physical launch did not complete with PASS")
    for field in ("execution", "backend", "ranks", "binding"):
        if launch.get(field) != layout[field]:
            raise ContractError("launch differs from registered layout: " + field)
    if launch.get("threads_per_rank") != layout["threads"]:
        raise ContractError("launch thread count differs from registered layout")
    if (launch.get("layout_id") != layout["id"] or launch.get("inputs") != inputs
            or launch.get("post_identity_error") is not None):
        raise ContractError("launch registered identity or final source check mismatch")
    _verify_file(launch["context"])
    context = load_json(launch["context"]["path"])
    if context["inputs"] != inputs or context["source"] != current_source:
        raise ContractError("actual launch context does not bind these reviewed source bytes")
    if context["native_identity"] is not None:
        for item in context["native_identity"].values():
            if isinstance(item, dict) and set(item) == {"path", "bytes", "sha256"}:
                _verify_file(item)
    process = launch["process"]
    if process["returncode"] != 0 or process.get("termination") is not None:
        raise ContractError("launcher reports failed or terminated process")
    _verify_file(launch["worker_result"])
    worker = load_json(launch["worker_result"]["path"])
    if (worker.get("schema") != "bass-he.c2g.physical-worker-result.v1"
            or worker.get("status") != "PASS" or worker.get("post_identity_errors")):
        raise ContractError("worker did not preserve successful final identities")
    if worker["execution"] != layout["execution"] or worker["backend"] != layout["backend"]:
        raise ContractError("worker layout identity differs")
    expected_inputs = {k: v["sha256"] for k, v in inputs.items()}
    expected_source = {k: v["sha256"] for k, v in current_source.items()}
    workers = worker["workers"]
    if sorted(w["rank"] for w in workers) != list(range(layout["ranks"])):
        raise ContractError("worker ranks incomplete or duplicated")
    identity = workers[0]["identity"]
    if (identity["context_sha256"] != launch["context"]["sha256"]
            or identity["native"] != context["native_identity"]):
        raise ContractError("worker launch context/native byte binding mismatch")
    for item in workers:
        if (item["identity"] != identity or item.get("preflight_error") is not None
                or item["identity"]["inputs"] != expected_inputs
                or item["identity"]["source"] != expected_source):
            raise ContractError("input/source identity or cross-rank identity mismatch")
    results = worker["results"]
    if len(results) != len(manifest["tasks"]) or len(results) != 12:
        raise ContractError("not all twelve preregistered tasks completed")
    archives = {}
    for index, (task, row) in enumerate(zip(manifest["tasks"], results)):
        if (row["task_index"] != index or row["task_id"] != task["task_id"] or row["task"] != task
                or row["rank"] != index % layout["ranks"] or row["status"] != "PASS"
                or row["input_identity"] != identity or row["backend"] != layout["backend"]):
            raise ContractError("task ownership, exact configuration, or identity mismatch")
        _verify_file(row["receipt"])
        receipt = load_json(row["receipt"]["path"])
        if receipt != {k: v for k, v in row.items() if k != "receipt"}:
            raise ContractError("task receipt content differs from gathered summary")
        ar = row["result"]["archive"]
        archive = load_sector(ar["source_path"], expected_sha256=ar["source_sha256"])
        if (archive.source_bytes != ar["source_bytes"] or archive.source_id != task["task_id"]
                or list(archive.state_ids) != ar["state_ids"]
                or len(archive.result.states) != task["nroots"]):
            raise ContractError("archive root count or source identity mismatch")
        first = archive.result.states[0]
        for field in ("R", "ZA", "ZB", "m", "degree"):
            if getattr(first, field) != task[field]:
                raise ContractError("archive physical parameters differ from manifest")
        if (not np.array_equal(first.boundaries, task["boundaries"])
                or int(first.ls[-1]) != task["lmax"] or first.metadata["origin_center"] != task["center"]
                or first.metadata["radial_quadrature"] != task["quadrature"]
                or archive.result.metadata["backend"] != layout["backend"]):
            raise ContractError("archive basis or assembly backend differs from manifest")
        for name, digest in archive.result.metadata["source_files_sha256"].items():
            if expected_source["code/"+name] != digest:
                raise ContractError("archive observed solver source differs from execution binding")
        if layout["backend"] == "native":
            if archive.result.metadata["native_library"]["library_sha256"] != context["native_identity"]["library"]["sha256"]:
                raise ContractError("archive native library differs from pinned execution binary")
        elif archive.result.metadata["native_library"] is not None:
            raise ContractError("numpy archive unexpectedly declares a native library")
        if (list(row["result"]["energies"]) != [s.energy for s in archive.result.states]
                or list(row["result"]["algebraic_residuals"]) != [s.residual for s in archive.result.states]
                or not np.array_equal(row["result"]["projected_operator"], archive.result.projected_operator)
                or not np.array_equal(row["result"]["mass_gram"], archive.result.mass_gram)):
            raise ContractError("small-matrix or scalar receipt differs from actual archived bytes")
        archives[(task["level"], task["R"], task["m"])] = archive
    if sum(len(a.result.states) for a in archives.values()) != 54:
        raise ContractError("registered independent root count is incomplete")
    return archives, {"launch_identity": launch_identity, "worker_identity": launch["worker_result"],
        "wall_seconds": process["wall_seconds"], "sampled_owned_rss_peak_bytes": process["sampled_owned_rss_peak_bytes"],
        "worker_wall_seconds": worker["wall_seconds"],
        "sum_task_wall_seconds": sum(row["wall_seconds"] for row in results),
        "stage_seconds_sum": {key: sum(a.result.metadata["stage_seconds"][key] for a in archives.values())
                              for key in ("tabulation", "assembly", "eigensolve", "postprocess")},
        "execution": layout, "independent_roots": 54, "sector_solves": 12}


class SnapshotCache:
    def __init__(self, archives, grid, bindings, atol):
        self.archives, self.grid, self.bindings, self.atol = archives, grid, bindings, atol
        self.cache = OrderedDict()

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        while len(self.cache) >= 3:
            self.cache.popitem(last=False)
        layout, level, R = key
        pair = tuple(self.archives[layout][(level, R, m)] for m in (0, 1))
        item = snapshot_from_archives(pair, self.grid, source_binding_path=self.bindings[key],
                                      gram_identity_atol=self.atol)
        self.cache[key] = item
        return item


def analyze(manifest_path, review_path, layouts, output):
    started = time.monotonic()
    manifest, inputs, _ = approved_inputs(manifest_path, review_path)
    prereg = load_json(inputs["preregistration"]["path"])
    layout_ids = validate_layout_arguments(prereg, layouts)
    source = source_identity(Path(__file__).parent)
    archives, timing = {}, {}
    for layout in prereg["campaign"]["layouts"]:
        name = layout["id"]
        archives[name], timing[name] = load_layout(layout, layouts[name], manifest, inputs, source)
    levels = [x["name"] for x in prereg["basis"]["levels"]]
    radii = prereg["physical_model"]["R_set"]
    if levels != ["coarse", "medium", "fine"] or len(radii) != 2:
        raise ContractError("this analyzer requires the registered three levels and two R coordinates")
    states = tuple(s for a in archives[layout_ids[0]].values() for s in a.result.states)
    embedding = prereg["common_embedding"]
    implementation = prereg["gates"]["implementation"]
    exploration = prereg["gates"]["finite_basis_exploration"]
    candidate = prereg["gates"]["candidate_transport"]
    tol_doc = prereg["gates"]["C2f_validation_parameters"]
    tolerances = ValidationTolerances(**{k: tol_doc[k] for k in ("gram_atol", "degeneracy_atol", "residual_max", "external_gap_min")})
    target = TargetSpec.large_R_rank5()
    bindings = {}
    binding_dir = Path(output).parent / (Path(output).stem + "_source_bindings")
    binding_dir.mkdir(exist_ok=False)
    for layout in layout_ids:
        for level in levels:
            for R in radii:
                key = layout, level, R
                path = binding_dir / f"{layout}_{level}_R{R}.json"
                write_source_binding(tuple(archives[layout][(level, R, m)] for m in (0, 1)), path,
                                     source_id=f"C2g:{layout}:{level}:R{R}")
                bindings[key] = path
    gates, grids, diagnostics, cross_R, basis_pairs = Gates(), {}, {}, {}, {}
    overlap_tables = {}
    for grid_name, spec in (("registered", embedding), ("refined", embedding["refinement_check"])):
        grid = build_common_grid(states, radial_order=spec["radial_GL_order"], eta_order=spec["eta_GL_order"],
            phi_count=spec["phi_points"], extra_radial_knots=embedding["extra_radial_knots"], max_points=2_000_000)
        grids[grid_name] = {"shape": grid.shape, "point_count": grid.point_count, "embedding_id": grid.embedding_id,
            "metric_id": grid.metric_id, "hilbert_space_id": grid.hilbert_space_id,
            "allocation_estimate": grid.allocation_estimate(12)}
        cache = SnapshotCache(archives, grid, bindings, implementation["finite_mass_isometry_max_entry_error"])
        r = np.repeat(grid.r, grid.shape[1]*grid.shape[2])
        diagnostics[grid_name], cross_R[grid_name], overlap_tables[grid_name] = {}, {}, {}
        for layout in layout_ids:
            diagnostics[grid_name][layout], cross_R[grid_name][layout], overlap_tables[grid_name][layout] = {}, {}, {}
            for level in levels:
                for R in radii:
                    key = layout, level, R
                    embedded = cache.get(key)
                    snap = embedded.snapshot
                    label = f"{grid_name}/{layout}/{level}/R{R}"
                    gram = snap.vectors.conj().T @ (grid.weights[:, None]*snap.vectors)
                    gram_defect = gram-np.eye(len(snap.states))
                    h = embedded.selected_galerkin_operator
                    obs, _ = normalized_observables(snap.selected_frame, grid.weights, r, tuple(exploration["outer_layer"]))
                    energies = [snap.states[j].energy for j in snap.selected_indices]
                    partner = max(abs(s.energy-snap.states[j].energy)
                        for s in snap.states if s.m == 1 for j in range(len(snap.states))
                        if snap.states[j].state_id in s.known_degenerate_partners)
                    conjugacy = max(float(np.max(np.abs(snap.vectors[:, i].conj()-snap.vectors[:, j])))
                        for i, s in enumerate(snap.states) if s.m == 1 for j in range(len(snap.states))
                        if snap.states[j].state_id in s.known_degenerate_partners)
                    gap = min(abs(s.energy-g.energy) for s in snap.states if s.role.value == "selected"
                              for g in snap.states if g.role.value == "guard")
                    values = {**obs, "selected_energies": energies, "all_column_count": len(snap.states),
                        "all_column_Gram_max_entry_error": float(np.max(np.abs(gram_defect))),
                        "all_column_Gram_operator_norm_error": float(np.linalg.norm(gram_defect, 2)),
                        "relative_algebraic_residual_max": max(s.residual_norm for s in snap.states),
                        "finite_mass_isometry_max_entry_error": max(x["max_abs_error"] for x in embedded.provenance["mass_isometry_checks"]),
                        "partner_energy_abs_error": partner, "partner_conjugacy_max_entry_error": conjugacy,
                        "projected_H_hermitian_max_entry_error": float(np.max(np.abs(h-h.conj().T))),
                        "projected_H_hermitian_operator_norm_error": float(np.linalg.norm(h-h.conj().T, 2)),
                        "observed_supplied_guard_spacing": gap, "source_provenance": embedded.provenance}
                    for name in ("all_column_Gram_max_entry_error", "all_column_Gram_operator_norm_error",
                                 "relative_algebraic_residual_max", "finite_mass_isometry_max_entry_error",
                                 "partner_energy_abs_error", "projected_H_hermitian_max_entry_error",
                                 "projected_H_hermitian_operator_norm_error"):
                        gates.add(label+"/"+name, values[name], implementation[name])
                    gates.add(label+"/partner_conjugacy_exact_reconstruction", conjugacy, 0.)
                    gates.add(label+"/observed_supplied_guard_spacing", gap, candidate["observed_supplied_guard_spacing_min"],
                              comparison="gt", category="candidate_transport")
                    if level == "fine":
                        gates.add(label+"/outer_layer", obs["outer_layer_probability_max"], exploration["fine_selected_outer_layer_probability_max"], category="finite_basis_exploration")
                    try:
                        values["C2f_validation"] = {"status": "PASS", "diagnostics": asdict(validate_snapshot(snap, target, tolerances, backend="reference"))}
                    except Exception as exc:
                        values["C2f_validation"] = {"status": "FAIL", "error": type(exc).__name__+": "+str(exc)}
                    gates.add(label+"/C2f_validation_rejection_count", int(values["C2f_validation"]["status"] != "PASS"), 0.)
                    diagnostics[grid_name][layout][f"{level}/R{R}"] = values
            for level in levels:
                left = cache.get((layout, level, radii[0])).snapshot
                right = cache.get((layout, level, radii[1])).snapshot
                pair, overlap = common_frame_comparison(left.selected_frame, right.selected_frame, grid.weights)
                overlap_tables[grid_name][layout][level] = overlap
                pair["normalized_selected_overlap"] = _complex_matrix(overlap)
                gates.add(f"{grid_name}/{layout}/{level}/cross_R_sigma", pair["principal_overlap_sigma_min"], candidate["principal_overlap_sigma_min"], comparison="gt", category="candidate_transport")
                try:
                    moved = parallel_transport(left, right, target, tolerances, sigma_min=candidate["principal_overlap_sigma_min"], backend="reference")
                    pair["C2f_transport"] = {"status": "PASS", "actual_operator_projection_supplied": moved.actual_operator_projection_supplied,
                        "reduced_operator_semantics": moved.reduced_operator_semantics,
                        "transformed_ritz_operator": _complex_matrix(moved.transformed_ritz_operator),
                        "aligned_columns_are_individual_eigenstates": False}
                    del moved
                except Exception as exc:
                    pair["C2f_transport"] = {"status": "BLOCKED", "error": type(exc).__name__+": "+str(exc)}
                gates.add(f"{grid_name}/{layout}/{level}/C2f_transport_rejection_count",
                          int(pair["C2f_transport"]["status"] != "PASS"), 0., category="candidate_transport")
                cross_R[grid_name][layout][level] = pair
        if grid_name == "registered":
            for layout in layout_ids:
                basis_pairs[layout] = {}
                for lower, upper in zip(levels, levels[1:]):
                    for R in radii:
                        a = cache.get((layout, lower, R)).snapshot
                        b = cache.get((layout, upper, R)).snapshot
                        metrics, _ = common_frame_comparison(a.selected_frame, b.selected_frame, grid.weights)
                        da, db = (diagnostics[grid_name][layout][f"{lev}/R{R}"] for lev in (lower, upper))
                        metrics["energy_max_abs_delta"] = float(np.max(np.abs(np.array(da["selected_energies"])-db["selected_energies"])))
                        metrics["trace_r2_relative_delta"] = abs(da["trace_r2"]-db["trace_r2"])/max(abs(db["trace_r2"]), np.finfo(float).tiny)
                        basis_pairs[layout][f"{lower}_to_{upper}/R{R}"] = metrics
                        if upper == "fine":
                            for short, registered in (("energy_max_abs_delta", "medium_to_fine_energy_max_abs_delta"),
                                ("projector_operator_distance", "medium_to_fine_selected_projector_operator_distance_max"),
                                ("trace_r2_relative_delta", "medium_to_fine_trace_r2_relative_delta_max")):
                                gates.add(f"{layout}/R{R}/{registered}", metrics[short], exploration[registered], category="finite_basis_exploration")
            parity = {}
            for level in levels:
                for R in radii:
                    a, b = (cache.get((name, level, R)).snapshot for name in layout_ids)
                    metrics, _ = common_frame_comparison(a.selected_frame, b.selected_frame, grid.weights)
                    metrics["all_returned_energy_max_abs_error"] = max(abs(x.energy-y.energy) for x, y in zip(a.states, b.states))
                    label = f"{level}/R{R}"
                    parity[label] = metrics
                    gates.add("backend/"+label+"/energy", metrics["all_returned_energy_max_abs_error"], implementation["backend_energy_max_abs_error"])
                    gates.add("backend/"+label+"/projector", metrics["projector_operator_distance"], implementation["backend_projector_operator_distance_max"])
            del a, b
        cache.cache.clear()
        # Delete references outside the LRU before moving to a differently sampled grid.
        del cache, embedded, snap, left, right, r
    quadrature = {}
    for layout in layout_ids:
        quadrature[layout] = {}
        for level in levels:
            delta = float(np.max(np.abs(overlap_tables["registered"][layout][level]-overlap_tables["refined"][layout][level])))
            quadrature[layout][level] = {"cross_R_5x5_overlap_max_abs_delta": delta}
            gates.add(f"quadrature/{layout}/{level}/overlap", delta, implementation["quadrature_overlap_max_abs_delta"])
            for R in radii:
                coarse = diagnostics["registered"][layout][f"{level}/R{R}"]
                fine = diagnostics["refined"][layout][f"{level}/R{R}"]
                d = abs(coarse["trace_r2"]-fine["trace_r2"])
                quadrature[layout][level][f"R{R}"] = {"trace_r2_abs_delta": d,
                    "outer_layer_probability_abs_delta": abs(coarse["outer_layer_probability_max"]-fine["outer_layer_probability_max"])}
                gates.add(f"quadrature/{layout}/{level}/R{R}/trace_r2", d, implementation["quadrature_trace_r2_max_abs_delta"])
    for identity in inputs.values():
        _verify_file(identity)
    if source_identity(Path(__file__).parent) != source:
        raise ContractError("analysis source files changed during execution")
    gate_result = gates.result()
    result = {"schema": "bass-he.c2g.reference-analysis.v1", "status": "ANALYSIS_COMPLETE",
        "scope": SCOPE, "inputs": inputs, "source_identity": source,
        "registered_thresholds_unchanged": prereg["gates"], "grid": grids,
        "snapshot_diagnostics": diagnostics, "cross_R": cross_R, "basis_refinement": basis_pairs,
        "backend_parity": parity, "quadrature_refinement": quadrature, "gates": gate_result,
        "timing": {"layouts": timing, "numpy_serial_wall_over_native_mpi_wall": timing[layout_ids[0]]["wall_seconds"]/timing[layout_ids[1]]["wall_seconds"],
            "scope": "single whole-workload observation confounds backend and parallelism; not a pure backend speedup or robust scaling estimate",
            "repetitions": 1, "NCP64_actual_measurement": False},
        "postprocess_wall_seconds": time.monotonic()-started,
        "eigensolves_started_by_analysis": 0,
        "in_memory_embedding_cache_capacity": 3,
        "interpretation": "failed finite-basis screens retain raw values and do not erase separately reported implementation validation; guard collisions block C2f transport"}
    atomic_create(output, result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--review", required=True)
    parser.add_argument("--layout", action="append", required=True, help="registered_id=/absolute/launch_result.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    output = Path(args.output).absolute()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError("analysis output is create-only")
    try:
        layouts = {}
        for token in args.layout:
            name, path = token.split("=", 1)
            if name in layouts:
                raise ContractError("duplicate layout argument")
            layouts[name] = path
        result = analyze(args.manifest, args.review, layouts, output)
        print(json.dumps({"status": result["status"], "gates": {k: v for k, v in result["gates"].items() if k != "all"}, "output": str(output)}, allow_nan=False))
        return 0
    except Exception as exc:
        atomic_create(output, {"schema": "bass-he.c2g.reference-analysis.v1", "status": "FAIL",
            "scope": SCOPE, "error": {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}})
        print(json.dumps({"status": "FAIL", "error": str(exc), "output": str(output)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
