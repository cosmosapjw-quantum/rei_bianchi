#!/usr/bin/env python3
"""Hash the complete load-bearing runtime and process environment."""
from __future__ import annotations

import hashlib
import contextlib
import importlib.metadata
import importlib.util
import io
import json
import os
import platform
from pathlib import Path
import subprocess
import sys
from typing import Any

CONTRACT_FILES = (
    "INPUT_LOCK.json",
    "requirements-runtime.txt",
    "analysis/adaptive_policy.py",
    "analysis/attempt_worker.py",
    "analysis/jax_import_guard.py",
    "analysis/run_adaptive_history.py",
    "analysis/runtime_contract.py",
    "analysis/state_io.py",
)
PINNED_DEPENDENCIES = {
    "numpy": "2.3.5",
    "scipy": "1.17.0",
    "pandas": "2.2.3",
    "python-dateutil": "2.9.0.post0",
    "pytz": "2026.3.post1",
    "tzdata": "2026.3",
    "six": "1.17.0",
}
NUMERIC_FINGERPRINT_DEPENDENCIES = ("numpy", "scipy", "pandas")
THREAD_LIMITS = (
    "BLIS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
DYNAMIC_STAGE_PATTERNS = {
    "continuous_interval_rhs": "stages/*R2_R1A_R1_VALIDATED_CONTINUOUS*",
    "implicit_certificates": "stages/*EVALUATION_SITE_SPARSE_GENERATOR_VALIDATED_MPRK22_SDIRK2*",
    "uncertainty_trial": "stages/*R2_R1A_FOUR_CORNER*",
}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_head(repo: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    head = result.stdout.strip()
    if result.returncode or len(head) != 40:
        raise RuntimeError("runtime contract requires a readable git HEAD")
    return head


def _require_tracked_clean(repo: Path) -> None:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=no"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode or result.stdout.strip():
        raise RuntimeError("runtime contract requires a clean tracked worktree")


def _dynamic_selections(repo: Path) -> dict[str, str]:
    selected = {}
    for name, pattern in DYNAMIC_STAGE_PATTERNS.items():
        matches = sorted(path for path in repo.glob(pattern) if path.is_dir())
        if len(matches) != 1:
            raise RuntimeError(
                f"dynamic stage selection {name} expected one match, observed {len(matches)}"
            )
        selected[name] = matches[0].relative_to(repo).as_posix()
    return selected


def loaded_numeric_fingerprint() -> dict[str, Any]:
    import numpy
    import pandas
    import scipy

    configuration = io.StringIO()
    with contextlib.redirect_stdout(configuration):
        numpy.show_config()
    runtime = io.StringIO()
    with contextlib.redirect_stdout(runtime):
        numpy.show_runtime()
    return {
        "numpy": numpy.__version__,
        "numpy_configuration_sha256": hashlib.sha256(
            configuration.getvalue().encode("utf-8")
        ).hexdigest(),
        "numpy_runtime_sha256": hashlib.sha256(
            runtime.getvalue().encode("utf-8")
        ).hexdigest(),
        "pandas": pandas.__version__,
        "scipy": scipy.__version__,
    }


def _numeric_probe() -> dict[str, Any]:
    environment = os.environ.copy()
    environment.pop("PYTHONHOME", None)
    environment.pop("PYTHONPATH", None)
    for name in THREAD_LIMITS:
        environment[name] = "1"
    environment["PYTHONHASHSEED"] = "0"
    environment["PYTHONNOUSERSITE"] = "1"
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--numeric-probe"],
        text=True,
        capture_output=True,
        env=environment,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(f"numeric runtime probe failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def build(
    repo: Path,
    stage: Path,
    *,
    numeric_fingerprint: dict[str, Any] | None = None,
    require_clean: bool = True,
) -> dict[str, Any]:
    repo = Path(repo).resolve()
    stage = Path(stage).resolve()
    if require_clean:
        _require_tracked_clean(repo)
    file_hashes = {}
    for relative in CONTRACT_FILES:
        path = stage / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        file_hashes[relative] = sha256_file(path)
    dependencies = {}
    for name, expected in PINNED_DEPENDENCIES.items():
        try:
            dependencies[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            dependencies[name] = None
        if dependencies[name] != expected:
            raise RuntimeError(
                f"dependency {name} version mismatch: "
                f"expected {expected}, observed {dependencies[name]}"
            )
    if importlib.util.find_spec("jax") is not None:
        raise RuntimeError("JAX must be absent from the production runtime")
    numeric = numeric_fingerprint or _numeric_probe()
    if any(
        numeric.get(name) != dependencies[name]
        for name in NUMERIC_FINGERPRINT_DEPENDENCIES
    ):
        raise RuntimeError("numeric import versions differ from distribution metadata")
    value = {
        "contract_schema": 1,
        "dependencies": dependencies,
        "dynamic_stage_selections": _dynamic_selections(repo),
        "files": file_hashes,
        "git_head": _git_head(repo),
        "jax_installed": False,
        "machine": platform.machine(),
        "numeric_fingerprint": numeric,
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "system": platform.system(),
        "thread_limits": {name: "1" for name in THREAD_LIMITS},
    }
    value["sha256"] = hashlib.sha256(canonical_json_bytes(value)).hexdigest()
    return value


def verify(
    expected_sha256: str,
    repo: Path,
    stage: Path,
    *,
    numeric_fingerprint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    value = build(repo, stage, numeric_fingerprint=numeric_fingerprint)
    if value["sha256"] != expected_sha256:
        raise ValueError(
            "runtime contract mismatch: "
            f"expected {expected_sha256}, observed {value['sha256']}"
        )
    return value


if __name__ == "__main__" and "--numeric-probe" in sys.argv:
    print(json.dumps(loaded_numeric_fingerprint(), sort_keys=True))
elif __name__ == "__main__":
    here = Path(__file__).resolve().parent
    stage = here.parent
    repo = stage.parents[1]
    print(json.dumps(build(repo, stage), indent=2, sort_keys=True))
