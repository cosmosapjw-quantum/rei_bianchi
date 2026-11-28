#!/usr/bin/env python3
"""Verify REI199 D8 saved-sample signed shear brackets without solving IVPs."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import tarfile
from pathlib import Path

import numpy as np

ARCHIVE_SHA256 = "7b39d8c8ffa0b61762211295a25d14412de37f6e1a6d163ebf0b93a8337f2251"
ARCHIVE_BYTES = 36_855_980
OWNER_HEAD = "744438f4512c7df1646aad0136ddc435b27200b0"
CASES = {
    "d58d4df366eadd417f7fbbd20b5906f51265660fb6bff81dec830d4bf16965e8": -0.0003,
    "6a9c9e40b8da9297509128b11f9ae5714c554a3e7df978f3a9268facf1749825": -0.0001,
    "1c39be4e6a5b7a7862d97efda76ea24b5b88a07db2696ffe76fe4b6cbf9c2e91": 0.0,
    "d98e5a31e6765c37b80a1ffaf007ff83042482a1b0a6be3dbe67fbc86d56a272": 0.0001,
}
BASE = "repo_payload/research/rei_age_exposure_envelope_20261018/sigma_pi_pilot_20261021/z2_extension/results"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def crossing_brackets(x: np.ndarray, y: np.ndarray) -> list[int]:
    """Return left indices for strict adjacent sign changes in stored samples."""
    if x.ndim != 1 or y.ndim != 1 or x.shape != y.shape or len(x) < 2:
        raise ValueError("x and y must be equal-length one-dimensional arrays")
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)) or not np.all(np.diff(x) > 0):
        raise ValueError("samples must be finite and x strictly increasing")
    return [int(i) for i in np.flatnonzero(y[:-1] * y[1:] < 0)]


def _member(tar: tarfile.TarFile, name: str) -> bytes:
    f = tar.extractfile(name)
    if f is None:
        raise ValueError(f"missing archive member: {name}")
    return f.read()


def analyze(archive: Path) -> dict:
    raw_archive = archive.read_bytes()
    if len(raw_archive) != ARCHIVE_BYTES or sha(raw_archive) != ARCHIVE_SHA256:
        raise ValueError("owner archive size/SHA256 mismatch")
    with tarfile.open(fileobj=io.BytesIO(raw_archive), mode="r:gz") as tar:
        manifest = json.loads(_member(tar, "MANIFEST.json"))
        manifest_items = manifest.get("files", manifest.get("entries", []))
        records = {r.get("archive_path", r.get("path", r.get("relative_path"))): r for r in manifest_items if isinstance(r, dict)}
        if not records:
            raise ValueError("unrecognized owner archive manifest schema")
        selected = {}
        for case_id, p_m0 in CASES.items():
            root = f"{BASE}/cases/{case_id}"
            members = {}
            for filename in ("INPUT.json", "RESULT.json", "ATTEMPT.json", "raw.npz", "tail.npz"):
                name = f"{root}/{filename}"
                data = _member(tar, name)
                rec = records.get(name) or records.get("./" + name)
                if rec is None or rec.get("sha256") != sha(data) or rec.get("size", rec.get("size_bytes", len(data))) != len(data):
                    raise ValueError(f"top manifest mismatch: {name}")
                members[filename] = data
            inp = json.loads(members["INPUT.json"])
            result = json.loads(members["RESULT.json"])
            attempt = json.loads(members["ATTEMPT.json"])
            cfg = inp["config"]
            if inp["id"] != case_id or inp["phase"] != "b2":
                raise ValueError(f"case identity mismatch: {case_id}")
            if cfg["ellmax"] != 8 or cfg["radial_cells"] != 24 or cfg["angular_cells"] != 12:
                raise ValueError(f"unexpected finite grid: {case_id}")
            if not all(result["checks"].values()):
                raise ValueError(f"stored result checks failed: {case_id}")
            if not math.isclose(cfg.get("P_m_i", 0.0), p_m0, rel_tol=0, abs_tol=1e-18):
                raise ValueError(f"matter initial value mismatch: {case_id}")
            if not math.isclose(cfg.get("P_r_i", cfg.get("Pi_F_signed_i")), -0.001, rel_tol=0, abs_tol=1e-18):
                raise ValueError(f"radiation initial value mismatch: {case_id}")
            with np.load(io.BytesIO(members["raw.npz"])) as npz:
                arrays = {k: npz[k].copy() for k in npz.files}
            x = arrays["x"]
            s, h = arrays["s"], arrays["H"]
            sigma_signed = np.sqrt(6.0) * s / h
            if len(x) != 153 or not np.allclose(np.abs(sigma_signed), arrays["Sigma_F"], rtol=2e-12, atol=1e-15):
                raise ValueError(f"signed shear convention mismatch: {case_id}")
            pm = arrays["Pi_F_signed_matter"]
            pr = arrays["Pi_F_signed_gamma"] + arrays["Pi_F_signed_nu"]
            total = pm + pr
            if not np.allclose(total, arrays["Pi_F_signed"], rtol=2e-12, atol=1e-15):
                raise ValueError(f"signed tensor-sum mismatch: {case_id}")
            if not np.allclose(np.abs(total), arrays["Pi_F"], rtol=2e-12, atol=1e-15):
                raise ValueError(f"full-frame norm mismatch: {case_id}")
            brackets = crossing_brackets(x, sigma_signed)
            if len(brackets) != 1:
                raise ValueError(f"expected exactly one stored adjacent bracket: {case_id} got {brackets}")
            i = brackets[0]
            selected[case_id] = {
                "P_m_initial": p_m0,
                "P_r_initial": -0.001,
                "phase": inp["phase"],
                "solver_saved": cfg["solver"],
                "sample_count": int(len(x)),
                "attempt_supervisor_outcome": attempt.get("supervisor_outcome"),
                "result_completion_basis": result.get("completion_basis", "solver_success"),
                "hashes": {k: sha(v) for k, v in members.items()},
                "bracket": {
                    "sample_indices": [i, i + 1],
                    "x": [float(x[i]), float(x[i + 1])],
                    "a": [float(arrays["a"][i]), float(arrays["a"][i + 1])],
                    "z": [float(1 / arrays["a"][i] - 1), float(1 / arrays["a"][i + 1] - 1)],
                    "elapsed_proper_s": [float(arrays["elapsed_proper_s"][i]), float(arrays["elapsed_proper_s"][i + 1])],
                    "Sigma_F_signed": [float(sigma_signed[i]), float(sigma_signed[i + 1])],
                    "P_m_signed": [float(pm[i]), float(pm[i + 1])],
                    "P_r_signed": [float(pr[i]), float(pr[i + 1])],
                    "P_total_signed": [float(total[i]), float(total[i + 1])],
                    "Pi_F_full_norm": [float(abs(total[i])), float(abs(total[i + 1]))],
                },
            }
        return {
            "schema": "WU088_HH_PHYS76_REI199_D8_SAVED_SAMPLE_BRACKETS_v1",
            "scope": "four B-lane L8 cases; stored adjacent sample sign brackets only",
            "owner_archive": {"sha256": ARCHIVE_SHA256, "bytes": ARCHIVE_BYTES},
            "owner_branch_head_observed": OWNER_HEAD,
            "new_ivp_calls": 0,
            "continuum_root_certificate": False,
            "continuum_source_residual_certificate": False,
            "cases": selected,
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.archive)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"cases": len(result["cases"]), "new_ivp_calls": 0, "output": str(args.out)}))


if __name__ == "__main__":
    main()
