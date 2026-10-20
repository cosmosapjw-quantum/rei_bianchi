#!/usr/bin/env python3
"""One create-only offline source/backup build and META-only cache compatibility check."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


def ident(path):
    raw = path.read_bytes()
    return {"path": str(path), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def put(path, value):
    with path.open("x") as output:
        json.dump(value, output, indent=2)
        output.write("\n")


def copy_exact(source, target):
    rows = []
    for p in sorted(source.rglob("*")):
        if not p.is_file():
            continue
        assert not p.is_symlink()
        q = target / p.relative_to(source)
        q.parent.mkdir(parents=True, exist_ok=True)
        with q.open("xb") as out:
            out.write(p.read_bytes())
        shutil.copystat(p, q)
        a, b = ident(p), ident(q)
        assert a["sha256"] == b["sha256"]
        rows.append({"source": a, "copy": b})
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run19-root", required=True, type=Path)
    ap.add_argument("--prefix", required=True, type=Path)
    ap.add_argument("--vendor", required=True, type=Path)
    ap.add_argument("--cache", required=True, type=Path)
    ap.add_argument("--reference-binary", type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--timeout", type=float, default=15.0)
    args = ap.parse_args()
    root, output = args.run19_root.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    cargo_home, target = output / "cargo_home", output / "target"
    cargo_home.mkdir()
    target.mkdir()
    restored = output / "source/research/atomic_nuclear_ssot_20261017"
    copies = []
    for name in ("native", "rate_cubic"):
        copies += copy_exact(root / name, restored / "run19" / name)
    copies += copy_exact(root.parent / "run13/recovered/code/rei_bass_coupled",
                         restored / "run13/recovered/code/rei_bass_coupled")
    put(output / "SOURCE_COPY_MANIFEST.json", {"schema": "REI_RUN19_CLEAN_SOURCE_COPY_V1", "files": copies,
        "all_bytes_equal": True, "scope": "fresh local source copy; no remote Git fetch performed"})
    env = os.environ.copy()
    for name in ("RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER", "CARGO_ENCODED_RUSTFLAGS"):
        env.pop(name, None)
    selected = {"CARGO_HOME": str(cargo_home), "CARGO_TARGET_DIR": str(target),
        "CARGO_NET_OFFLINE": "true", "CARGO_INCREMENTAL": "0", "CARGO_BUILD_JOBS": "2",
        "RUSTC": str(args.prefix / "bin/rustc"), "RUSTDOC": str(args.prefix / "bin/rustdoc"),
        "RUSTFLAGS": "", "LD_LIBRARY_PATH": str(args.prefix / "lib")}
    env.update(selected)
    env["PATH"] = str(args.prefix / "bin") + os.pathsep + env.get("PATH", "")
    native = restored / "run19/native"
    argv = [str(args.prefix / "bin/cargo"), "--config", 'source.crates-io.replace-with="rei-vendored"',
        "--config", 'source.rei-vendored.directory=' + json.dumps(str(args.vendor.resolve())),
        "build", "--release", "--offline", "--locked", "--jobs", "2", "--target-dir", str(target),
        "--example", "gas_rhs_server"]
    put(output / "BUILD_REQUEST.json", {"argv": argv, "cwd": str(native), "environment_overrides": selected,
        "initial_cargo_home_file_count": 0, "initial_target_file_count": 0, "timeout_seconds": args.timeout})
    start = time.monotonic()
    try:
        run = subprocess.run(argv, cwd=native, env=env, capture_output=True, timeout=args.timeout)
        code, stdout, stderr, timed_out = run.returncode, run.stdout, run.stderr, False
    except subprocess.TimeoutExpired as error:
        code, stdout, stderr, timed_out = None, error.stdout or b"", error.stderr or b"", True
    wall = time.monotonic() - start
    (output / "build.stdout.txt").write_bytes(stdout)
    (output / "build.stderr.txt").write_bytes(stderr)
    put(output / "BUILD_RESULT.json", {"exit_code": code, "wall_seconds": wall, "timed_out": timed_out,
        "logs": [ident(output / "build.stdout.txt"), ident(output / "build.stderr.txt")]})
    receipt = {"schema": "REI_RUN19_CLEAN_OFFLINE_SOURCE_BACKUP_RESTORE_V1",
        "source_copy_manifest": ident(output / "SOURCE_COPY_MANIFEST.json"), "vendor": str(args.vendor.resolve()),
        "build_request": ident(output / "BUILD_REQUEST.json"), "build_result": ident(output / "BUILD_RESULT.json"),
        "status": "BLOCKED" if code != 0 else "BUILD_COMPLETE", "native_rhs_calls": 0, "ivp_runs": 0,
        "full_test_suites_run": 0, "git_only_restore": False,
        "scope": "new local source copy plus preserved vendor sources, empty Cargo home/target, existing exact Rust toolchain; no new remote checkout"}
    if code == 0:
        binary = target / "release/examples/gas_rhs_server"
        cache_before = ident(args.cache)
        meta_argv = [str(binary), "--rates", "cubic", "--table-cache", str(args.cache)]
        meta_start = time.monotonic()
        meta = subprocess.run(meta_argv, input=b"META\n", capture_output=True, env=env, timeout=1)
        (output / "meta.stdout.txt").write_bytes(meta.stdout)
        (output / "meta.stderr.txt").write_bytes(meta.stderr)
        assert meta.returncode == 0, meta.stderr
        result = json.loads(meta.stdout)
        assert result["cubic_source_id"] == "53f101a30c0d6fdae246eb6ca545660e8bab5aaf22e34787c6ba15fd1ec8fcc4"
        assert result["table_cache_action"] == "LOADED_EXACT_SOURCE"
        assert result["table_cache_sha256"] == cache_before["sha256"]
        assert ident(args.cache) == cache_before
        assert result["step_evaluator"] == "IGM_GRACKLE_DIRECT_F64_V1"
        receipt.update({"status": "IMPLEMENTATION_VERIFIED", "restored_binary": ident(binary),
            "meta_command": meta_argv, "meta_wall_seconds": time.monotonic() - meta_start,
            "meta_exit_code": meta.returncode, "metadata": result, "cache_before_after_exact": cache_before,
            "compiler": subprocess.check_output([str(args.prefix / "bin/rustc"), "--version"], env=env, text=True).strip()})
        if args.reference_binary:
            reference = ident(args.reference_binary)
            receipt.update({"reference_binary": reference,
                "binary_bytes_equal_reference": ident(binary)["sha256"] == reference["sha256"]})
    put(output / "CLEAN_OFFLINE_RESTORE_RECEIPT.json", receipt)
    print(json.dumps({"status": receipt["status"], "build_seconds": wall, "receipt": ident(output / "CLEAN_OFFLINE_RESTORE_RECEIPT.json"),
        "native_rhs_calls": 0, "ivps": 0}, indent=2))
    if code != 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
