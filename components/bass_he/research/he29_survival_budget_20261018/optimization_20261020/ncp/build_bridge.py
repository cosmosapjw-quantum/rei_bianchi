#!/usr/bin/env python3
"""Build only the ABI2 packed bridge from pinned clean Git and a frozen lockfile.

No physical solver, old source suite, transport case or automatic canary runs.
An existing exact clean VigilODE checkout may be reused without network.
Every subprocess is bounded as a process group and keeps stdout/stderr.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import traceback

LANE = Path(__file__).resolve().parents[1]
HE29 = LANE.parent
REPO = HE29.parents[1]
sys.path.insert(0, str(HE29.parent / "he28_strip_refinement_20261018/src"))
from execution import atomic_json, digest, manifest, run_process

VIGILODE_SOURCE = "a21d573980f66fe02891bd216153443b5352f921"
BASELINE_CODE = "1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f"
BRIDGE_PATHS = ["Cargo.toml", "Cargo.lock", "src/lib.rs", "src/packed.rs", "include/he29_optimized_bridge.h"]
RUSTFLAGS = "-C\x1ftarget-cpu=x86-64"


def query(argv):
    return subprocess.run(argv, check=True, capture_output=True, text=True, timeout=30).stdout.strip()


def checked(argv, output, label, wall):
    receipt = run_process(argv, output / "commands" / label, wall)
    if receipt["returncode"] != 0 or receipt["timed_out"]:
        raise RuntimeError("HE29_OPT_BUILD_COMMAND_FAILED: " + label)
    return receipt


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, help="fresh directory outside the BASS_HE checkout")
    ap.add_argument("--source-revision", required=True, help="exact 40-character published BASS_HE commit")
    ap.add_argument("--vigilode-checkout", help="existing clean checkout exactly at the pinned SHA")
    ap.add_argument("--cargo", default="cargo")
    ap.add_argument("--rustc", default="rustc")
    ap.add_argument("--offline", action="store_true", help="require an already populated Cargo cache")
    args = ap.parse_args()
    out = Path(args.out).resolve()
    if out.is_relative_to(REPO):
        raise ValueError("HE29_OPT_BUILD_OUT_MUST_BE_OUTSIDE_REPOSITORY")
    out.mkdir(parents=True, exist_ok=False)
    try:
        if len(args.source_revision) != 40 or any(c not in "0123456789abcdef" for c in args.source_revision):
            raise ValueError("HE29_OPT_SOURCE_REVISION_REQUIRES_FULL_SHA")
        cargo = shutil.which(args.cargo)
        rustc = shutil.which(args.rustc)
        if not cargo or not rustc:
            raise RuntimeError("HE29_OPT_RUST_TOOLCHAIN_MISSING")
        cargo, rustc = str(Path(cargo).resolve(strict=True)), str(Path(rustc).resolve(strict=True))
        rust_version = query([rustc, "--version", "--verbose"])
        cargo_version = query([cargo, "--version", "--verbose"])
        compiler_hashes = {"rustc": digest(rustc), "cargo": digest(cargo)}
        if (not rust_version.splitlines()[0].startswith("rustc 1.94.1 ")
                or not cargo_version.splitlines()[0].startswith("cargo 1.94.1 ")
                or "host: x86_64-unknown-linux-gnu" not in rust_version.splitlines()):
            raise RuntimeError("HE29_OPT_REQUIRES_RECORDED_RUST_CARGO_1_94_1_X86_64_LINUX")
        publication_head = query(["git", "-C", str(REPO), "rev-parse", "HEAD"])
        if publication_head != args.source_revision:
            raise ValueError("HE29_OPT_PUBLISHED_SOURCE_SHA")
        publication_tree = query(["git", "-C", str(REPO), "rev-parse", "HEAD^{tree}"])
        # This builder consumes an explicitly published, clean checkout.
        if query(["git", "-C", str(REPO), "status", "--porcelain"]):
            raise RuntimeError("HE29_OPT_REPOSITORY_DIRTY: use the published clean checkout")
        dependency = out / "vigilode"
        if args.vigilode_checkout:
            source = Path(args.vigilode_checkout).resolve(strict=True)
            if query(["git", "-C", str(source), "rev-parse", "HEAD"]) != VIGILODE_SOURCE:
                raise ValueError("HE29_OPT_CHECKOUT_SHA")
            if query(["git", "-C", str(source), "status", "--porcelain"]):
                raise ValueError("HE29_OPT_CHECKOUT_DIRTY")
            dependency.symlink_to(source, target_is_directory=True)
        else:
            checked(["git", "clone", "--filter=blob:none", "--no-checkout",
                     "https://github.com/cosmosapjw-quantum/vigilode.git", str(dependency)],
                    out, "clone", 300.)
            checked(["git", "-C", str(dependency), "sparse-checkout", "set", "--no-cone",
                     "/Cargo.toml", "/Cargo.lock", "/LICENSE", "/crates/", "/fixtures/"],
                    out, "sparse", 60.)
            checked(["git", "-C", str(dependency), "fetch", "origin", VIGILODE_SOURCE],
                    out, "fetch", 300.)
            checked(["git", "-C", str(dependency), "checkout", "--detach", VIGILODE_SOURCE],
                    out, "checkout", 300.)
        if query(["git", "-C", str(dependency), "rev-parse", "HEAD"]) != VIGILODE_SOURCE:
            raise ValueError("HE29_OPT_FINAL_CHECKOUT_SHA")
        if query(["git", "-C", str(dependency), "status", "--porcelain"]):
            raise ValueError("HE29_OPT_FINAL_CHECKOUT_DIRTY")
        dependency_tree = query(["git", "-C", str(dependency), "rev-parse", "HEAD^{tree}"])
        dependency_lock = digest(dependency / "Cargo.lock")
        source_snapshot = manifest([LANE / "rust_bridge" / p for p in BRIDGE_PATHS], LANE)
        target_bridge = out / "rust_bridge"
        for relative in BRIDGE_PATHS:
            source = LANE / "rust_bridge" / relative
            target = target_bridge / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        staged_snapshot = {"rust_bridge/" + p: digest(target_bridge / p) for p in BRIDGE_PATHS}
        if staged_snapshot != source_snapshot:
            raise ValueError("HE29_OPT_STAGE_COPY_IDENTITY")
        # The existing upstream profile is not modified. The small bridge has
        # its own Cargo root and locked versions; no full-workspace test target.
        os.environ["RUSTC"] = rustc
        os.environ["CARGO_BUILD_JOBS"] = "2"
        os.environ["CARGO_INCREMENTAL"] = "0"
        os.environ["RAYON_NUM_THREADS"] = "1"
        os.environ.pop("RUSTFLAGS", None)
        os.environ.pop("CARGO_BUILD_TARGET", None)
        for key in ("RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER"):
            os.environ[key] = ""
        # Explicitly override configured rustflags, including target features.
        os.environ["CARGO_ENCODED_RUSTFLAGS"] = RUSTFLAGS
        argv = [cargo, "build", "--release", "--locked", "--lib", "--manifest-path",
                str(target_bridge / "Cargo.toml"), "--target-dir", str(out / "target")]
        if args.offline:
            argv.append("--offline")
        build = checked(argv, out, "build", 1800.)
        if ({"rust_bridge/" + p: digest(target_bridge / p) for p in BRIDGE_PATHS} != source_snapshot
                or manifest([LANE / "rust_bridge" / p for p in BRIDGE_PATHS], LANE) != source_snapshot):
            raise ValueError("HE29_OPT_SOURCE_CHANGED_DURING_BUILD")
        if (query(["git", "-C", str(dependency), "rev-parse", "HEAD"]) != VIGILODE_SOURCE
                or query(["git", "-C", str(dependency), "status", "--porcelain"])
                or query(["git", "-C", str(dependency), "rev-parse", "HEAD^{tree}"]) != dependency_tree
                or digest(dependency / "Cargo.lock") != dependency_lock):
            raise ValueError("HE29_OPT_DEPENDENCY_CHANGED_DURING_BUILD")
        if (query(["git", "-C", str(REPO), "rev-parse", "HEAD"]) != publication_head
                or query(["git", "-C", str(REPO), "rev-parse", "HEAD^{tree}"]) != publication_tree
                or query(["git", "-C", str(REPO), "status", "--porcelain"])
                or query([rustc, "--version", "--verbose"]) != rust_version
                or query([cargo, "--version", "--verbose"]) != cargo_version
                or {"rustc": digest(rustc), "cargo": digest(cargo)} != compiler_hashes):
            raise ValueError("HE29_OPT_BUILD_OWNER_CHANGED")
        library = out / "target/release/libhe29_optimized_bridge.so"
        if not library.is_file():
            raise RuntimeError("HE29_OPT_LINUX_LIBRARY_NOT_FOUND")
        data = {"schema": "he29.optimized.build.v1", "status": "COMPILED", "abi_version": 2,
                "baseline_code_revision": BASELINE_CODE, "vigilode_source": VIGILODE_SOURCE,
                "bass_publication_head": publication_head, "bass_publication_tree": publication_tree,
                "source_revision_argument": args.source_revision, "library_path": str(library),
                "library_sha256": digest(library), "bridge_sources": source_snapshot,
                "source_identity_before_after_match": True,
                "vigilode_tree": dependency_tree,
                "upstream_cargo_lock_sha256": dependency_lock,
                "rustc_sha256": compiler_hashes["rustc"], "cargo_sha256": compiler_hashes["cargo"],
                "compiler_binary_identity_before_after_match": True,
                "compiler_wrappers": "EXPLICIT_EMPTY_OVERRIDE", "cargo_encoded_rustflags": RUSTFLAGS,
                "rustc_verbose": rust_version, "cargo_version": cargo_version,
                "build_receipt": build, "build_jobs": 2, "fast_math_enabled": False,
                "physical_runs": 0, "source_suites_replayed": 0, "canary_runs": 0}
        atomic_json(out / "BUILD_IDENTITY.json", data)
        print(json.dumps(data, indent=2))
    except BaseException as exc:
        atomic_json(out / "BUILD_FAILURE.json", {"status": "BUILD_FAILED", "error": repr(exc),
                    "traceback": traceback.format_exc(), "physical_runs": 0})
        raise


if __name__ == "__main__":
    main()
