#!/usr/bin/env python3
"""One tiny fixture check of packaging exclusions, layout, hashes, and modes."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise ValueError("check receipt must be new")
    packager = Path(__file__).resolve().with_name("package_recovery.py")
    raw = packager.read_bytes()
    compile(raw, str(packager), "exec")
    keep = {
        "bin/gas_rhs_server": ("fixture executable bytes; never executed\n", 0o755),
        "README.md": ("ordinary fixture file with an input execute bit\n", 0o755),
        "postloss_native/src/lib.rs": ("fixture source\n", 0o644),
        "postloss_native/evidence/receipt.json": ("{}\n", 0o644),
        "recovery/postloss_runtime_delivery/toolchain/OFFICIAL_COMPONENTS_RECEIPT.json": ("{}\n", 0o644),
        "recovery/postloss_runtime_delivery/toolchain/downloads/rust.tar.xz.sha256": ("fixture checksum text\n", 0o644),
        "recovery/postloss_runtime_delivery/postloss_gas_build/logs/gas.stdout.log": ("fixture retained build log\n", 0o644),
    }
    drop = [
        "recovery/toolchain/downloads/rust.tar.xz", "recovery/toolchain/prefix/bin/rustc",
        "recovery/postloss_native_build/crate/src/lib.rs", "recovery/postloss_gas_build/logs/duplicate.log",
        "recovery/postloss_endpoint_reconstruction/source_copy/old.py", "postloss_native/target/debug/large",
        "cargo_home/registry/cache", "postloss_native/__pycache__/module.pyc", ".git/objects/object",
        "SALVAGE_PUBLICATION_01.json", "source_recovery/runtime/SALVAGE_PUBLICATION_02.json",
        "recovery/POSTLOSS_NATIVE_SOURCE_AND_EVIDENCE.zip", "extra.pyc", "extra.pyo", "extra.xz",
    ]
    with tempfile.TemporaryDirectory(prefix="package-policy-fixture-", dir=packager.parent) as temporary:
        directory = Path(temporary)
        root = directory / "input"
        root.mkdir()
        for rel, (text, mode) in keep.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
            path.chmod(mode)
        for rel in drop:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("excluded fixture data\n")
        archive = directory / "fixture.zip"
        command = [sys.executable, "-B", str(packager), "--root", str(root), "--output", str(archive),
                   "--git-head", "PACKAGING_FIXTURE_ONLY_NOT_A_PUBLICATION"]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        if result.returncode:
            raise RuntimeError("packaging fixture failed: " + result.stderr)
        with zipfile.ZipFile(archive) as zipped:
            expected = {"run15/" + path for path in keep} | {"MANIFEST.json"}
            if set(zipped.namelist()) != expected:
                raise ValueError("retained or excluded fixture path mismatch")
            manifest = json.loads(zipped.read("MANIFEST.json"))
            entries = {row["path"]: row for row in manifest["files"]}
            for rel, (text, _) in keep.items():
                name = "run15/" + rel
                if zipped.read(name) != text.encode():
                    raise ValueError("fixture bytes changed: " + rel)
                expected_mode = 0o755 if rel.startswith("bin/") else 0o644
                if ((zipped.getinfo(name).external_attr >> 16) & 0o777) != expected_mode:
                    raise ValueError("ZIP executable/ordinary mode mismatch: " + rel)
                if entries[name]["mode"] != format(expected_mode, "04o"):
                    raise ValueError("manifest mode metadata mismatch: " + rel)
        package_receipt = json.loads(archive.with_suffix(".receipt.json").read_text())
        check = {
            "status": "PACKAGING_FIXTURE_PASS", "packager_sha256": hashlib.sha256(raw).hexdigest(),
            "packager_syntax_compile": "PASS", "fixture_archive_only": True, "final_archive_created": False,
            "fixture_command": command, "retained_fixture_files": sorted(keep), "excluded_fixture_files": drop,
            "retained_file_count": len(keep), "excluded_file_count": len(drop),
            "retained_curated_toolchain_evidence": True, "retained_native_source_and_evidence": True,
            "preserved_layout": "run15/<relative-path>", "binary_mode": "0755", "ordinary_mode": "0644",
            "fixture_packager_receipt": package_receipt,
            "new_native_processes": 0, "new_native_ivps": 0, "native_test_suites": 0,
        }
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(check, stream, indent=2)
        stream.write("\n")
    print(json.dumps(check, indent=2))


if __name__ == "__main__":
    main()
