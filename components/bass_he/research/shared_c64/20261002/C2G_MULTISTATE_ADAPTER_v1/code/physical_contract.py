"""Closed C2g finite-basis physical pilot contract, separate from C2f fixtures."""
from __future__ import annotations

import json
import math
from pathlib import Path
import re

from runtime_support import (ContractError, GIB, _finite, _integer, _keys,
                             code_identity, file_identity)

SCHEMA = "bass-he.c2g.physical-reference.v1"
NODE = "C2G_MULTISTATE_EIGENSOLVER_ADAPTER_AND_REFERENCE_PREREGISTRATION"
SCOPE = "finite_basis_electronic_reference_pilot"
REVIEW_SCHEMA = "bass-he.c2g.physical-launch-review.v1"
TASK_KEYS = ("task_id", "R", "ZA", "ZB", "m", "lmax", "rmax", "elements", "boundaries",
             "degree", "quadrature", "tol", "maxiter", "center", "nroots", "level")
SOLVER_KEYS = tuple(k for k in TASK_KEYS if k not in ("task_id", "level"))


def load_json(path):
    def reject_constant(token):
        raise ContractError(f"nonfinite JSON token: {token}")
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ContractError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(Path(path).read_text(), parse_constant=reject_constant,
                      object_pairs_hook=unique_keys)


def _safe_name(value, where):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", value):
        raise ContractError(f"{where}: safe nonempty ASCII identifier required")


def _sha(value, where):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ContractError(f"{where}: lowercase SHA256 required")


def validate_manifest(value):
    _keys(value, ("schema", "node", "physical_launch_enabled", "evidence_scope",
                  "preregistration", "tasks", "limits"), "manifest")
    if value["schema"] != SCHEMA or value["node"] != NODE or value["evidence_scope"] != SCOPE:
        raise ContractError("wrong C2g physical-reference schema, node, or evidence scope")
    if value["physical_launch_enabled"] is not True:
        raise ContractError("literal physical_launch_enabled=true required after review")
    registered = value["preregistration"]
    _keys(registered, ("path", "sha256"), "preregistration")
    path = registered["path"]
    if (not isinstance(path, str) or not path or Path(path).is_absolute()
            or ".." in Path(path).parts or "\\" in path):
        raise ContractError("preregistration path must stay relative and below manifest directory")
    _sha(registered["sha256"], "preregistration.sha256")
    tasks = value["tasks"]
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= 12:
        raise ContractError("tasks: 1..12 explicitly listed tasks required")
    ids = set()
    configurations = set()
    roots = 0
    for index, task in enumerate(tasks):
        label = f"tasks[{index}]"
        _keys(task, TASK_KEYS, label)
        _safe_name(task["task_id"], label + ".task_id")
        _safe_name(task["level"], label + ".level")
        if task["task_id"] in ids:
            raise ContractError("duplicate task_id")
        ids.add(task["task_id"])
        _finite(task["R"], 0, 64, label + ".R", positive=True)
        for key in ("ZA", "ZB"):
            _finite(task[key], 0, 3, label + "." + key, positive=True)
        _integer(task["m"], 0, 1, label + ".m")
        _integer(task["lmax"], max(1, task["m"]), 28, label + ".lmax")
        _finite(task["rmax"], 0, 20, label + ".rmax", positive=True)
        _integer(task["elements"], 4, 40, label + ".elements")
        _integer(task["degree"], 2, 4, label + ".degree")
        _integer(task["quadrature"], 2 * task["degree"] + 2, 20, label + ".quadrature")
        _finite(task["tol"], 1e-14, 1e-9, label + ".tol")
        _integer(task["maxiter"], 1, 2000, label + ".maxiter")
        _integer(task["nroots"], 2, 6, label + ".nroots")
        if task["center"] != "O":
            raise ContractError("C2g pilot requires the common charge-center O coordinate origin")
        farthest_nucleus = task["R"] * max(task["ZA"], task["ZB"]) / (task["ZA"] + task["ZB"])
        if task["rmax"] <= farthest_nucleus:
            raise ContractError("box must strictly contain both nuclei")
        boundaries = task["boundaries"]
        if not isinstance(boundaries, list) or not 3 <= len(boundaries) <= 43:
            raise ContractError("explicit boundaries require 2..42 actual radial elements")
        for boundary in boundaries:
            _finite(boundary, 0, task["rmax"], label + ".boundaries[]")
        if boundaries[0] != 0 or boundaries[-1] != task["rmax"] or any(
                right <= left for left, right in zip(boundaries, boundaries[1:])):
            raise ContractError("boundaries must strictly increase from 0 to rmax")
        nuclear_radii = (task["R"] * task["ZA"] / (task["ZA"] + task["ZB"]),
                         task["R"] * task["ZB"] / (task["ZA"] + task["ZB"]))
        if any(radius not in boundaries for radius in nuclear_radii):
            raise ContractError("exact nuclear radii must be explicitly present in boundaries")
        config = tuple(tuple(task[k]) if k == "boundaries" else task[k] for k in SOLVER_KEYS)
        if config in configurations:
            raise ContractError("duplicate physical solve configuration")
        configurations.add(config)
        roots += task["nroots"]
    limits = value["limits"]
    _keys(limits, ("wall_seconds", "memory_gib", "max_ranks", "max_threads_per_rank",
                   "max_tasks", "max_eigenstates"), "limits")
    _finite(limits["wall_seconds"], 0, 300, "limits.wall_seconds", positive=True)
    _finite(limits["memory_gib"], 0, 4, "limits.memory_gib", positive=True)
    _integer(limits["max_ranks"], 1, 2, "limits.max_ranks")
    _integer(limits["max_threads_per_rank"], 1, 4, "limits.max_threads_per_rank")
    _integer(limits["max_tasks"], 1, 12, "limits.max_tasks")
    _integer(limits["max_eigenstates"], 2, 54, "limits.max_eigenstates")
    if len(tasks) > limits["max_tasks"] or roots > limits["max_eigenstates"]:
        raise ContractError("listed tasks/eigenstates exceed the explicit run budget")
    return value


def load_manifest(path):
    return validate_manifest(load_json(path))


def validate_review(review, manifest_identity, preregistration_identity):
    _keys(review, ("schema", "status", "approved_manifest_sha256",
                   "approved_preregistration_sha256", "reviewer", "evidence_scope"), "review")
    if review["schema"] != REVIEW_SCHEMA or review["status"] != "PASS" or review["evidence_scope"] != SCOPE:
        raise ContractError("an explicit PASS review in this physical pilot scope is required")
    if not isinstance(review["reviewer"], str) or not review["reviewer"].strip():
        raise ContractError("named reviewer required")
    if review["approved_manifest_sha256"] != manifest_identity["sha256"]:
        raise ContractError("review does not approve the exact manifest bytes")
    if review["approved_preregistration_sha256"] != preregistration_identity["sha256"]:
        raise ContractError("review does not approve the exact preregistration bytes")
    return review


def approved_inputs(manifest_path, review_path):
    """Measure original bytes twice, then bind the independently reviewed hashes."""
    manifest_identity = file_identity(manifest_path)
    manifest = load_manifest(manifest_path)
    root = Path(manifest_identity["path"]).parent
    preregistration_path = (root / manifest["preregistration"]["path"]).resolve(strict=True)
    if not preregistration_path.is_relative_to(root):
        raise ContractError("preregistration symlink escapes manifest directory")
    preregistration_identity = file_identity(preregistration_path)
    if preregistration_identity["sha256"] != manifest["preregistration"]["sha256"]:
        raise ContractError("preregistration SHA256 mismatch")
    # JSON must be parseable and finite even though the independent review owns
    # the scientific schema and acceptance decisions.
    load_json(preregistration_path)
    review_identity = file_identity(review_path)
    review = validate_review(load_json(review_path), manifest_identity, preregistration_identity)
    for identity in (manifest_identity, preregistration_identity, review_identity):
        if file_identity(identity["path"]) != identity:
            raise ContractError("input bytes changed during contract verification")
    return manifest, {"manifest": manifest_identity, "preregistration": preregistration_identity,
                      "review": review_identity}, review


def source_identity(code_dir):
    """All local Python plus native source/build scripts, not generated artifacts."""
    directory = Path(code_dir).resolve()
    result = {"code/" + k: v for k, v in code_identity(directory).items()}
    for pattern in ("*.f90", "*.py"):
        for path in sorted((directory.parent / "native").glob(pattern)):
            result["native/" + path.name] = file_identity(path)
    return result


def native_identity(path):
    if path is None:
        return None
    library = file_identity(path)
    metadata = file_identity(Path(library["path"]).with_suffix(".build.json"))
    build = load_json(metadata["path"])
    expected_flags = ["-O3", "-std=f2008", "-fPIC", "-shared", "-fopenmp",
                      "-fno-fast-math", "-ffp-contract=off", "-fno-associative-math",
                      "-Wall", "-Wextra"]
    if (build.get("schema") != "bass-native-build-v1" or build.get("mode") != "strict"
            or build.get("abi") != 3 or build.get("flags") != expected_flags
            or build.get("native_cpu_isa") is not False):
        raise ContractError("native build is not the preregistered strict ABI3 binary64 flag configuration")
    if (build.get("library_sha256") != library["sha256"]
            or build.get("library_bytes") != library["bytes"]):
        raise ContractError("native build manifest does not bind the supplied library bytes")
    if build.get("source") != "element_assembly.f90":
        raise ContractError("native build must name the reviewed element assembly source")
    source = file_identity(Path(__file__).resolve().parents[1] / "native" / "element_assembly.f90")
    if build.get("source_sha256") != source["sha256"]:
        raise ContractError("native build source SHA256 differs from current checked source")
    if file_identity(metadata["path"]) != metadata or file_identity(library["path"]) != library:
        raise ContractError("native bytes changed during identity verification")
    return {"library": library, "build_metadata": metadata, "source": source,
            "strict_flags": expected_flags, "abi": 3}


def validate_registered_layout(preregistration_path, execution, backend, ranks, threads, binding):
    """Bind the allowed combination to the exact reviewed scientific preregistration."""
    preregistration = load_json(preregistration_path)
    try:
        layouts = preregistration["campaign"]["layouts"]
    except (KeyError, TypeError) as exc:
        raise ContractError("reviewed preregistration lacks campaign.layouts") from exc
    if not isinstance(layouts, list) or len(layouts) != 2:
        raise ContractError("exactly two preregistered campaign layouts required")
    actual = (execution, backend, ranks, threads, binding)
    allowed = []
    for layout in layouts:
        _keys(layout, ("id", "execution", "backend", "ranks", "threads", "binding"), "campaign layout")
        allowed.append(tuple(layout[key] for key in ("execution", "backend", "ranks", "threads", "binding")))
    if actual not in allowed:
        raise ContractError("requested layout absent from the exact reviewed preregistration")
    return next(layout["id"] for layout in layouts if tuple(
        layout[key] for key in ("execution", "backend", "ranks", "threads", "binding")) == actual)


def validate_request(manifest, execution, backend, native_library, ranks, threads, binding, host):
    validate_manifest(manifest)
    if execution not in ("serial", "mpi") or backend not in ("numpy", "native"):
        raise ContractError("explicit serial|mpi execution and numpy|native backend required; no fallback")
    if binding not in ("none", "core"):
        raise ContractError("binding must be none or core")
    if (execution, backend, ranks, threads, binding) not in (
            ("serial", "numpy", 1, 1, "none"),
            ("mpi", "native", 2, 1, "none")):
        raise ContractError("layout is not one of the two preregistered C2g pilot layouts")
    if execution == "serial" and ranks != 1:
        raise ContractError("serial execution requires exactly one rank")
    limits = manifest["limits"]
    _integer(ranks, 1, limits["max_ranks"], "requested ranks")
    _integer(threads, 1, limits["max_threads_per_rank"], "requested threads")
    if ranks * threads > host["effective_cpu_budget"]:
        raise ContractError("rank×thread request exceeds pre-MPI host CPU budget")
    if binding == "core" and len(host["physical_cores_in_affinity"]) < ranks * threads:
        raise ContractError("not enough measured physical cores for core binding")
    if limits["memory_gib"] * GIB > host["memory_available_bytes"]:
        raise ContractError("memory budget exceeds current measured available host memory")
    if backend == "native":
        if not native_library:
            raise ContractError("native backend requires an explicit library")
        native_identity(native_library)
    elif native_library is not None:
        raise ContractError("numpy backend must not receive a native library")
