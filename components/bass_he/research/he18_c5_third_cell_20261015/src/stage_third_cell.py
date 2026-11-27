#!/usr/bin/env python3
"""Create an isolated warm-P01 third-cell runtime from verified HE18 C3 evidence.

The real C3 source and its private inputs are read-only. No rei_bianchi code runs.
All private P01 data remain outside the public Git checkout.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent / "he18_c3_two_cell_20261015"
PREV_END_SHA = "f6942afc38865e4d149b34ea51535ffb657825ec13e8f5f518da8667cd79c8f7"
PREV_RESULT_SHA = "e75fa7b2b0e1b1c85393c3d4ae0b2ca16b9276d60c24a55a7ab507a2abb68b09"
SOURCE_SHA = "8c434debdcb66ee499d61f7822980c73c75469bd426839a1597687042b8c78f3"
INPUT_SHA = {
    "P01_STATE.npz": "3cbf35cf7910c37083de4c5b9db443c71b272f3877a48f74fb9f852fd70fe2be",
    "emissivity.out": "88743ec9041a47fd12f47bf50a75a06903089e1afd992b5460a4af471249469b",
}
STEP = 6250000000

def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def assert_digest(p: Path, expected: str) -> None:
    if digest(p) != expected:
        raise ValueError(f"SOURCE_BYTE_IDENTITY:{p.name}")

def subst_once(text: str, old: str, new: str, filename: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"PATCH_BASELINE_CHANGED:{filename}:{old!r}:{count}")
    return text.replace(old, new, 1)

def stage(prev: Path, dest: Path) -> dict:
    if dest.exists() or dest.with_name(dest.name + ".partial").exists():
        raise ValueError("REFUSE_OVERWRITE_EXISTING_RUNTIME")
    assert_digest(prev / "results/SECOND_ENDPOINT_MEMORY.json", PREV_END_SHA)
    assert_digest(prev / "results/TWO_CELL_VALIDATION.json", PREV_RESULT_SHA)
    assert_digest(prev / "_c1_private/src/warm_source_reference.py", SOURCE_SHA)
    for name, h in INPUT_SHA.items():
        assert_digest(prev / "inputs" / name, h)
    previous = json.loads((prev / "results/TWO_CELL_VALIDATION.json").read_text())
    outgoing = json.loads((prev / "results/SECOND_ENDPOINT_MEMORY.json").read_text())
    assert previous["status"] == "SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES"
    assert outgoing["source_interval_s"] == [str(STEP), str(2*STEP)]
    photon = outgoing["outgoing_photon_error_end_raw_exact"]
    gas = outgoing["scaled_gas_error_end_exact"]
    if len(photon) != 2904 or len(gas) != 4:
        raise ValueError("INCOMPLETE_C3_ENDPOINT_MEMORY")

    tmp = dest.with_name(dest.name + ".partial")
    try:
        for name in ("src", "checks", "results", "evidence", "inputs", "_c1_private/src", "_c1_private/inputs"):
            (tmp / name).mkdir(parents=True, exist_ok=True)
        for f in ("P01_STATE.npz", "emissivity.out", "P01_INTERVAL.json",
                  "HH_P01_COMPARISON.json"):
            shutil.copy2(prev / "inputs" / f, tmp / "inputs" / f)
        for f in ("P01_STATE.npz", "emissivity.out"):
            shutil.copy2(prev / "inputs" / f, tmp / "_c1_private/inputs" / f)
        for f in ("warm_source_reference.py",):
            shutil.copy2(prev / "_c1_private/src" / f, tmp / "_c1_private/src" / f)
        for f in ("interval_jet.py", "run_evaluations.py", "assemble_certificate.py", "warm_interval.py"):
            shutil.copy2(BASE / "src" / f, tmp / "src" / f)
        adapted = dict(
            gas_error_end_scaled=gas,
            photon_error_end_raw_exact=photon,
            source_interval_s=[str(STEP), str(2*STEP)],
            provenance_sha256=PREV_END_SHA,
        )
        carry_bytes = (json.dumps(adapted, indent=2) + "\n").encode()
        (tmp / "inputs/ENDPOINT_MEMORY_R7.json").write_bytes(carry_bytes)
        # This module is the unchanged C1 saved-state source used by the previous stage.
        source_file = tmp / "_c1_private/src/warm_source_reference.py"
        spec = importlib.util.spec_from_file_location("verified_c1_warm_reference", source_file)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        source = mod.Source()
        t0, t1 = source.times[2:4]
        if float(t0) != 2*STEP or float(t1) != 3*STEP:
            raise ValueError("NOT_THIRD_SAVED_CELL")
        left = np.asarray(source.y[:, 2], dtype=np.float64)
        right = np.asarray(source.y[:, 3], dtype=np.float64)
        if left.size != 2908 or right.size != 2908:
            raise ValueError("WRONG_WARM_STATE_DIMENSION")
        m0 = source.rhs(t0, source.y[:, 2])[0].astype(np.float64)
        m1 = source.rhs(t1, source.y[:, 3])[0].astype(np.float64)
        np.savez_compressed(tmp / "inputs/FIXED_REFERENCE.npz",
                            left=left, right=right, slope_left=m0,
                            slope_right=m1, h=float(t1-t0))
        src = tmp / "src/warm_interval.py"
        s = src.read_text()
        for old, new in (
            ("return self.global_volume(z+1)", "return self.global_volume(z+2)"),
            ("xq=lo(x)+1", "xq=lo(x)+2"),
            ("if xq<1 or hi(x)+1>2:", "if xq<2 or hi(x)+2>3:"),
            ("'SECOND_CELL_SHEAR_DOMAIN'", "'THIRD_CELL_SHEAR_DOMAIN'"),
            ("bound(0,2*self.h*self.si)", "bound(0,3*self.h*self.si)"),
        ):
            s = subst_once(s, old, new, src.name)
        src.write_text(s)
        runner = tmp / "src/run_evaluations.py"
        runner.write_text(subst_once(runner.read_text(), "'HE18_C3'", "'HE18_C5'", runner.name))
        assembly = tmp / "src/assemble_certificate.py"
        a = assembly.read_text()
        for old, new in (
            ("archived_state['states'][:s.n,1]", "archived_state['states'][:s.n,2]"),
            ("archived_state['states'][:s.n,2]", "archived_state['states'][:s.n,3]"),
        ):
            # The two changes are applied simultaneously below to prevent cascading replacement.
            pass
        if a.count("archived_state['states'][:s.n,1]") != 1 or a.count("archived_state['states'][:s.n,2]") != 1:
            raise ValueError("ASSEMBLER_INDEX_BASELINE_CHANGED")
        a = a.replace("archived_state['states'][:s.n,1]", "__THIRD_LEFT__")
        a = a.replace("archived_state['states'][:s.n,2]", "archived_state['states'][:s.n,3]")
        a = a.replace("__THIRD_LEFT__", "archived_state['states'][:s.n,2]")
        for old, new in (
            ("'SECOND_CELL_DYADIC_ENDPOINT_SOURCE_MISMATCH'", "'THIRD_CELL_DYADIC_ENDPOINT_SOURCE_MISMATCH'"),
            ("rows[1]['ne_cm3']", "rows[2]['ne_cm3']"),
            ("rows[2]['ne_cm3']", "rows[3]['ne_cm3']"),
            ("'HE18_C3'", "'HE18_C5'"),
            ("[str(h),str(2*h)]", "[str(2*h),str(3*h)]"),
            ("'second-cell FIXED_REFERENCE.npz exact dyadic coefficients'",
             "'third-cell FIXED_REFERENCE.npz exact dyadic coefficients'"),
        ):
            if old.startswith("rows["):
                # do these two simultaneously after all other edits
                continue
            a = subst_once(a, old, new, assembly.name)
        if a.count("rows[1]['ne_cm3']") != 1 or a.count("rows[2]['ne_cm3']") != 1:
            raise ValueError("PL_BASELINE_CHANGED")
        a = a.replace("rows[1]['ne_cm3']", "__THIRD_LEFT__")
        a = a.replace("rows[2]['ne_cm3']", "rows[3]['ne_cm3']")
        a = a.replace("__THIRD_LEFT__", "rows[2]['ne_cm3']")
        assembly.write_text(a)
        shutil.copy2(ROOT / "checks/verify_third.py", tmp / "checks/verify_third.py")
        shutil.copy2(ROOT / "checks/propagate_third.py", tmp / "checks/propagate_third.py")
        shutil.copy2(prev / "results/TWO_CELL_VALIDATION.json",
                     tmp / "inputs/PREV_TWO_CELL_VALIDATION.json")
        info = {
            "stage": "HE18_C5_THIRD_CELL",
            "source_commit": outgoing["source_commit"],
            "input_previous_end_sha256": PREV_END_SHA,
            "input_previous_two_cell_result_sha256": PREV_RESULT_SHA,
            "input_source_sha256": SOURCE_SHA,
            "input_private_sha256": INPUT_SHA,
            "new_frozen_reference_sha256": digest(tmp / "inputs/FIXED_REFERENCE.npz"),
            "adapted_carry_sha256": digest(tmp / "inputs/ENDPOINT_MEMORY_R7.json"),
            "cell_s": [str(2*STEP), str(3*STEP)],
            "source_rhs_endpoint_calls": 2,
            "full_ODE_calls": 0,
            "prior_certificates_reused": True,
            "other_repository_modified": False,
        }
        (tmp / "inputs/STAGED_SOURCE_IDENTITY.json").write_text(json.dumps(info, indent=2)+"\n")
        tmp.rename(dest)
        return info
    except BaseException:
        if tmp.exists():
            shutil.rmtree(tmp)
        raise

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--previous-runtime", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args=p.parse_args()
    print(json.dumps(stage(args.previous_runtime,args.output),indent=2))
