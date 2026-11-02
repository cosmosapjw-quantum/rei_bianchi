#!/usr/bin/env python3
"""Bind exact original F05 7-dependency runtime to a NEW, distinct V2 contract.

Original runtime_contract.build() and old accepted RUN_METADATA.json are used
unchanged. A V1 historical SHA mismatch never becomes a fake V1 acceptance.
All changes confined to research-only V2 workflow, no production source edits.
"""
from __future__ import annotations
import hashlib, importlib.util, json, sys, tarfile
from pathlib import Path

HISTORICAL_SHA="10ab5823e109f32d693c82d246b3369045ddecf5217fa30fc4013ab6d55c3810"
ORIGINAL_TAR="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
DEPENDENCIES={
    "numpy":"2.3.5","scipy":"1.17.0","pandas":"2.2.3",
    "python-dateutil":"2.9.0.post0","pytz":"2026.3.post1",
    "tzdata":"2026.3","six":"1.17.0"
}

def fail(cond,msg):
    if not cond: raise RuntimeError("REI_F05_V2_FULL_RUNTIME_"+msg)
def hashfile(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
    return h.hexdigest()

def bind(repo, stage, parent_source_worker_git_blob):
    repo=Path(repo).resolve();stage=Path(stage).resolve()
    script=stage/"analysis/runtime_contract.py"
    spec=importlib.util.spec_from_file_location("rei_f05_original_runtime_module",script)
    fail(spec is not None and spec.loader is not None,"ORIGINAL_RUNTIME_LOADER")
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    original_file=stage/"local_results/first_interval_r2_blocked_minimum_step.tar.gz"
    fail(hashfile(original_file)==ORIGINAL_TAR,"ORIGINAL_ARCHIVE_SHA")
    with tarfile.open(original_file,"r:gz") as z:
        historical=json.load(z.extractfile("RUN_METADATA.json"))["runtime_contract"]
    fail(historical["sha256"]==HISTORICAL_SHA,"HISTORICAL_RUNTIME_SHA")
    fresh=mod.build(repo,stage,require_clean=True)
    fail(fresh["dependencies"]==DEPENDENCIES,"COMPLETE_SEVEN_PIN_DEPENDENCIES")
    fail(fresh["jax_installed"] is False,"JAX_PRODUCTION_EXCLUSION")
    fail(set(fresh)==set(historical),"RUNTIME_SCHEMA")
    mismatch={k:{"historical":historical[k],"current":fresh[k]}
              for k in historical if historical[k]!=fresh[k]}
    # No broad relaxation: all original fixed source, binary, CPU, Python,
    # packages, BLAS thread, NumPy build config MUST match. Only Git HEAD
    # and the opaque runtime fingerprint are permitted to differ between
    # old 2026 V1 host and current versioned V2 source research.
    fail(set(mismatch)=={"git_head","numeric_fingerprint","sha256"},"UNEXPECTED_LEGACY_RUNTIME_CHANGE")
    for k in ("numpy","numpy_configuration_sha256","pandas","scipy"):
        fail(historical["numeric_fingerprint"][k]==fresh["numeric_fingerprint"][k],
             "NUMERIC_FINGERPRINT_"+k)
    n_changed=[k for k in fresh["numeric_fingerprint"]
              if fresh["numeric_fingerprint"][k]!=historical["numeric_fingerprint"][k]]
    fail(n_changed==["numpy_runtime_sha256"],"NUMPY_RUNTIME_MISMATCH_CLASSIFICATION")
    oldref=historical["numeric_fingerprint"]["numpy_runtime_sha256"]
    newer=fresh["numeric_fingerprint"]["numpy_runtime_sha256"]
    fail(oldref!=newer,"EXPECTED_MEANINGFUL_RUNTIME_DIFFERENCE_MISSING")
    result={
        "schema":"REI_F05_SEVEN_PIN_VERSIONED_V2_FULL_RUNTIME_CONTRACT_V2",
        "original_v1_sha256":HISTORICAL_SHA,
        "new_full_runtime_contract_sha256":fresh["sha256"],
        "new_full_runtime_contract":fresh,
        "all_seven_original_dependencies_byte_version_matched":True,
        "original_worker_file_hashes_identical":True,
        "original_historical_numeric_build_sha256_matched":True,
        "original_runtime_changed_fields":["git_head","numeric_fingerprint.numpy_runtime_sha256"],
        "old_numpy_runtime_sha256":oldref,
        "new_numpy_runtime_sha256":newer,
        "old_source_original_git_head":historical["git_head"],
        "new_source_owner_git_head":fresh["git_head"],
        "source_upstream_worker_git_blob_sha1":parent_source_worker_git_blob,
        "numa_cpu_simd_runtime_equivalence":"UNVERIFIED_OPAQUE_RUNTIME_FINGERPRINT_DIFF",
        "new_versioned_v2_runtime_is_NOT_original_v1_runtime":True,
        "not_autonomous_production_admission":True,
    }
    return result
