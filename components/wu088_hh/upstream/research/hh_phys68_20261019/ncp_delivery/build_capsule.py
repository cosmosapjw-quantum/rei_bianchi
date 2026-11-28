#!/usr/bin/env python3
"""Package the already implemented L64 runner without running its mathematics."""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[3]
AREA = Path("research/hh_phys68_20261019/ncp_delivery")
NAME = "WU088_HH_PHYS68_L64_D2_RUNNER_20261019"
FROZEN = Path("research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
FROZEN_SHA = "f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
WRAPPER_SHA = "a75f578889f76d2d8f896aaecd8513a52f952706706ee08619285fdd0bb0d8d1"


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False)+"\n").encode()


def source_closure():
    queue = [Path("scripts/phys68_ncp.py"), Path("scripts/phys68_profiles.py"),
             Path("src/wu088_hh/__init__.py")]
    seen = set()
    while queue:
        path = queue.pop()
        if path in seen:
            continue
        if not (ROOT/path).is_file():
            raise FileNotFoundError(path)
        seen.add(path)
        for node in ast.walk(ast.parse((ROOT/path).read_text())):
            modules = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    package = list(path.with_suffix("").parts[1:-1])
                    package = package[:len(package)-node.level+1]
                    modules = [".".join(package+([node.module] if node.module else []))]
                elif node.module:
                    modules = [node.module]
            for module in modules:
                if module == "wu088_hh" or module.startswith("wu088_hh."):
                    target = Path("src").joinpath(*module.split(".")).with_suffix(".py")
                    if not (ROOT/target).is_file():
                        target = Path("src").joinpath(*module.split("."))/"__init__.py"
                    if target not in seen:
                        queue.append(target)
    return sorted(seen)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    closure = source_closure()
    paths = set(closure)
    paths.update([
        FROZEN,
        Path("tests/test_phys68_ncp.py"),
        Path("research/hh_phys65_20261018/r5/PROOF.md"),
        Path("research/hh_phys66_20261018/r5/PROOF.md"),
        Path("research/hh_phys68_20261019/theory/PROOF.md"),
        Path("research/hh_phys68_20261019/taylor/PROOF.md"),
        Path("research/hh_phys68_20261019/angular/PROOF.md"),
    ])
    for name in ("README_KO.md", "REQUEST_L64.json", "requirements.txt",
                 "TEST_EXECUTION.json", "TEST_STDOUT.txt", "TEST_STDERR.txt",
                 "PREFLIGHT_EXECUTION.json", "PREFLIGHT_STDOUT.json",
                 "PREFLIGHT_STDERR.txt", "PREFLIGHT_EXECUTED_WRAPPER.py.txt",
                 "INITIAL_TEST_SOURCE.py.txt", "build_capsule.py"):
        paths.add(AREA/name)
    paths.update(p.relative_to(ROOT) for p in (ROOT/AREA/"preflight_only").rglob("*") if p.is_file())
    payloads = {str(path): (ROOT/path).read_bytes() for path in sorted(paths)}
    if hashlib.sha256(payloads[str(FROZEN)]).hexdigest() != FROZEN_SHA:
        raise ValueError("original NPZ differs")
    if hashlib.sha256(payloads["scripts/phys68_ncp.py"]).hexdigest() != WRAPPER_SHA:
        raise ValueError("wrapper differs from the final 21-test receipt")
    manifest = {
        "schema": "WU088_HH_PHYS68_L64_CAPSULE_MANIFEST_V1",
        "source_repository": "https://github.com/cosmosapjw-quantum/WU088_HH",
        "inherited_base_commit": "1a149efeba61a9ffd7ea882bdd86f7ea36c0b78c",
        "publication": "PREPARED_BEFORE_PHYS68_PUBLICATION_SEE_OUTER_DELIVERY",
        "scientific_state": "L64_PREPARED_NOT_SUBMITTED",
        "source_sha256": FROZEN_SHA,
        "HH_R10": "OFF",
        "recursive_import_closure": [str(p) for p in closure],
        "runtime_packages": "research/hh_phys68_20261019/ncp_delivery/requirements.txt",
        "README": "research/hh_phys68_20261019/ncp_delivery/README_KO.md",
        "fixed_request": "research/hh_phys68_20261019/ncp_delivery/REQUEST_L64.json",
        "payloads": [{"path": path, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
                     for path, data in payloads.items()],
        "manifest_excludes_itself": True,
        "packaging_scientific_executions": 0,
    }
    payloads["MANIFEST.json"] = canonical(manifest)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.exists():
        raise FileExistsError("create-only capsule output already exists")
    with zipfile.ZipFile(args.out, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path, data in sorted(payloads.items()):
            item = zipfile.ZipInfo(NAME+"/"+path, (2026, 10, 19, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o100644 << 16
            archive.writestr(item, data, compresslevel=9)
    data = args.out.read_bytes()
    receipt = {
        "schema": "WU088_HH_PHYS68_L64_CAPSULE_BUILD_V1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "archive": str(args.out.resolve()), "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "archive_root": NAME, "payload_count_excluding_manifest": len(payloads)-1,
        "recursive_import_closure_count": len(closure),
        "source_sha256": FROZEN_SHA,
        "scientific_executions": 0,
        "tests_rerun": 0,
        "preflight_rerun": 0,
        "NCP_submissions": 0,
        "clean_restore_verification": "PENDING_SEPARATE_RECEIPT",
    }
    (ROOT/AREA/"CAPSULE_MANIFEST.json").write_bytes(canonical(manifest))
    (ROOT/AREA/"CAPSULE_BUILD_RECEIPT.json").write_bytes(canonical(receipt))
    print(canonical(receipt).decode(), end="")


if __name__ == "__main__":
    main()
