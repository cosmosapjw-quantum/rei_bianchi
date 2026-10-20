#!/usr/bin/env python3
"""One source-ZIP restoration gate; writes only this final_restore directory."""
from __future__ import annotations

import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import zipfile


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    here = Path(__file__).resolve().parent
    base = here.parent.parent
    parent_rel = Path("repo/research/dossier_ssot_sandbox_20261016/bass_reactive06_vigilode_reference_20261019/parent/crate")
    crate_roots = [Path("brperf01/integration"), Path("brperf01/native_rates"), Path("brperf01/rates"), parent_rel]
    payloads: dict[str, bytes] = {}
    for root in crate_roots:
        for name in ("Cargo.toml", "Cargo.lock", "README.md"):
            source = base / root / name
            if source.is_file():
                payloads[str(root / name)] = source.read_bytes()
        for directory in ("src", "owner_src", "tests", "examples"):
            for source in sorted((base / root / directory).rglob("*")):
                if source.is_file():
                    payloads[str(source.relative_to(base))] = source.read_bytes()
    selected_contracts = [
        "brperf01/integration/ANALYZE.py",
        "brperf01/integration/RUN_STAGE.py",
        "brperf01/integration/VERIFY_RESTORE.py",
        "brperf01/integration/evidence/GOLDEN_CSV_SHA256.json",
        "brperf01/integration/evidence/FINAL_SOURCE_IDENTITY.json",
        "brperf01/native_rates/evidence/ORIGINAL_SOURCE_IDENTITY.json",
        "brperf01/native_rates/evidence/ADAPTER_AUDIT.json",
        "brperf01/rates/SOURCE_CONTRACT.json",
    ]
    for name in selected_contracts:
        payloads[name] = (base / name).read_bytes()
    for name in payloads:
        assert not any(part in {"target", "fresh_target", "fresh_restore", "final_restore", "runtime"} for part in Path(name).parts)
    expectation = json.loads(payloads["brperf01/integration/evidence/FINAL_SOURCE_IDENTITY.json"])
    for name, expected in expectation["source_payloads"].items():
        assert name in payloads and sha(payloads[name]) == expected, name
    manifest = {
        "schema": "BRPERF01_FINAL_RESTORE_SOURCE_V1",
        "scope": "Four crate source trees and selected contracts; no targets, execution outputs, runtime, registry, or archive self-inclusion.",
        "crate_roots": [str(path) for path in crate_roots],
        "payloads": {name: {"sha256": sha(data), "bytes": len(data)} for name, data in sorted(payloads.items())},
    }
    manifest_bytes = (json.dumps(manifest, indent=2) + "\n").encode()
    (here / "SOURCE_MANIFEST.json").write_bytes(manifest_bytes)
    archive = here / "BRPERF01_NATIVE_INTEGRATION_SOURCE_RESTORE.zip"
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as stream:
        for name, data in sorted({**payloads, "SOURCE_MANIFEST.json": manifest_bytes}.items()):
            info = zipfile.ZipInfo(name, (2026, 10, 20, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            stream.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    archive_identity = {"file": archive.name, "sha256": sha(archive.read_bytes()), "bytes": archive.stat().st_size, "entries": len(payloads) + 1, "payload_files": len(payloads), "manifest_sha256": sha(manifest_bytes)}
    (here / "ARCHIVE_IDENTITY.json").write_text(json.dumps(archive_identity, indent=2) + "\n")

    restored = here / "restore_tree"
    restored.mkdir(exist_ok=False)
    with zipfile.ZipFile(archive) as stream:
        assert len(stream.namelist()) == len(set(stream.namelist())) == len(payloads) + 1
        for name in stream.namelist():
            path = Path(name)
            assert not path.is_absolute() and ".." not in path.parts
        stream.extractall(restored)
    restored_manifest = json.loads((restored / "SOURCE_MANIFEST.json").read_text())
    assert sha((restored / "SOURCE_MANIFEST.json").read_bytes()) == archive_identity["manifest_sha256"]
    for name, expected in restored_manifest["payloads"].items():
        path = restored / name
        assert sha(path.read_bytes()) == expected["sha256"] and path.stat().st_size == expected["bytes"], name

    target = here / "empty_target"
    target.mkdir(exist_ok=False)
    assert not list(target.iterdir())
    cargo_home = here / "cargo_home"
    cargo_home.mkdir(exist_ok=False)
    config_source = base / "brperf01/runtime/cargo_home/config.toml"
    (cargo_home / "config.toml").write_bytes(config_source.read_bytes())
    prefix = base / "brperf01/runtime/rust-1.94.1"
    env = dict(os.environ)
    env["PATH"] = str(prefix / "bin") + os.pathsep + env.get("PATH", "")
    env["LD_LIBRARY_PATH"] = str(prefix / "lib") + os.pathsep + env.get("LD_LIBRARY_PATH", "")
    env["CARGO_HOME"] = str(cargo_home)
    env["CARGO_TARGET_DIR"] = str(target)
    versions = {}
    for tool, args in (("rustc", ["-vV"]), ("cargo", ["--version"]), ("rustfmt", ["--version"]), ("cargo-clippy", ["--version"])):
        versions[tool] = subprocess.check_output([str(prefix / "bin" / tool), *args], env=env, text=True).strip()
    runtime = {"compiler_prefix_reused": str(prefix), "registry_reused": str(base / "brperf01/runtime/vendor/registry"), "cargo_home_new": str(cargo_home), "cargo_config_sha256": sha(config_source.read_bytes()), "target_new_and_empty_before_first_build": True, "target": str(target), "versions": versions, "compiler_archive_and_registry_receipts": {name: sha((base / name).read_bytes()) for name in ["brperf01/runtime_evidence/RUNTIME_IDENTITY.json", "brperf01/runtime_evidence/REGISTRY_VERIFICATION.json", "brperf01/runtime_evidence/REGISTRY_LOCK_MATCH.json"]}}
    (here / "RUNTIME_REUSE.json").write_text(json.dumps(runtime, indent=2) + "\n")
    commands = []

    def run(argv: list[str], label: str) -> None:
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with (here / f"{label}.log").open("w") as stream:
            result = subprocess.run(argv, env=env, cwd=restored, stdout=stream, stderr=subprocess.STDOUT)
        commands.append({"name": label, "argv": argv, "started_utc": started, "returncode": result.returncode, "log": f"{label}.log"})
        (here / "COMMANDS.json").write_text(json.dumps(commands, indent=2) + "\n")
        assert result.returncode == 0, f"{label} failed; see retained log"

    integration = restored / "brperf01/integration"
    science_out = here / "science_output"
    run(["python3", str(integration / "RUN_STAGE.py"), str(science_out), "--stage", "science"], "FRESH_INTEGRATION_STAGE")
    run(["python3", str(integration / "VERIFY_RESTORE.py"), str(science_out)], "FRESH_CSV_BYTE_PARITY")
    run(["cargo", "test", "--offline", "--locked", "--manifest-path", str(restored / "brperf01/native_rates/Cargo.toml")], "FRESH_NATIVE_ADAPTER_TESTS")
    parity = json.loads((here / "FRESH_CSV_BYTE_PARITY.log").read_text())
    assert parity["status"] == "PASS" and parity["checked_payloads"] == 16
    native_log = (here / "FRESH_NATIVE_ADAPTER_TESTS.log").read_text()
    assert "test result: ok. 9 passed; 0 failed" in native_log
    science = {str(nodes): json.loads((science_out / f"science_{nodes}/INDEPENDENT_ANALYSIS.json").read_text()) for nodes in (4097, 8193)}
    for result in science.values():
        assert result["status"] == "PASS" and result["completed_histories"] == 45 and result["accepted_macrosteps"] == 5040
    original_checks = {}
    restored_checks = {}
    for name, expected in manifest["payloads"].items():
        original_checks[name] = sha((base / name).read_bytes()) == expected["sha256"]
        restored_checks[name] = sha((restored / name).read_bytes()) == expected["sha256"]
    assert all(original_checks.values()) and all(restored_checks.values())
    assert sha(archive.read_bytes()) == archive_identity["sha256"]
    result = {"recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "status": "PASS", "scope": "FRESH_SOURCE_ZIP_NATIVE_TABLE_TRAJECTORY_RESTORE", "archive": archive_identity, "verified_extracted_payloads": len(payloads), "original_source_unchanged": all(original_checks.values()), "restored_source_unchanged_after_build": all(restored_checks.values()), "source_verification": original_checks, "runtime": runtime, "commands": commands, "scoped_rustfmt_strict_clippy_offline_build": "PASS via restored RUN_STAGE.py", "native_adapter_tests": {"passed": 9, "failed": 0, "profile": "debug"}, "deterministic_csv_byte_parity": {"passed": 16, "failed": 0}, "science": science, "fresh_binary_sha256": sha((target / "release/rei_brperf01_integration").read_bytes()), "original_final_binary_sha256": expectation["release_binary_sha256"], "binary_identity_policy": "Fresh path/compiler outputs may change binary bytes; scientific CSV identity is the gate.", "benchmarks_rerun": False, "not_claimed": ["fresh compiler installation", "fresh vendor redownload", "new timing validation", "BASS photon driver integration", "global publication/provider backup ACK"]}
    (here / "VERIFICATION.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "archive": archive_identity, "CSV_byte_parity": "16/16", "native_tests": "9/9", "histories_each_resolution": "45/45", "macrosteps_each_resolution": 5040, "original_sources_unchanged": True, "benchmarks_rerun": False}))


if __name__ == "__main__":
    main()
