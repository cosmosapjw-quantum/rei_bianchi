#!/usr/bin/env python3
"""Verify archive bytes/importability/help; do not execute the solver or preflight."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import time
import zipfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    start = time.monotonic()
    data = args.archive.read_bytes()
    with tempfile.TemporaryDirectory(prefix="phys68_capsule_restore_") as temporary:
        base = Path(temporary)
        with zipfile.ZipFile(args.archive) as archive:
            for name in archive.namelist():
                parsed = PurePosixPath(name)
                if parsed.is_absolute() or ".." in parsed.parts:
                    raise ValueError("unsafe capsule path")
            if archive.testzip() is not None:
                raise ValueError("archive CRC mismatch")
            archive.extractall(base)
        roots = list(base.iterdir())
        if len(roots) != 1 or not roots[0].is_dir():
            raise ValueError("single capsule root required")
        root = roots[0]
        manifest = json.loads((root/"MANIFEST.json").read_text())
        checked = []
        for entry in manifest["payloads"]:
            payload = (root/entry["path"]).read_bytes()
            if len(payload) != entry["bytes"] or hashlib.sha256(payload).hexdigest() != entry["sha256"]:
                raise ValueError("payload hash mismatch: "+entry["path"])
            checked.append(entry["path"])
        actual = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}
        if actual != set(checked)|{"MANIFEST.json"}:
            raise ValueError("unexpected or missing payload")
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment["PYTHONPATH"] = str(root/"src")
        checks = []
        commands = [
            [sys.executable, "scripts/phys68_ncp.py", "--help"],
            [sys.executable, "scripts/phys68_profiles.py", "--help"],
            [sys.executable, "-c", "import importlib,json,pathlib,runpy; "
             "m=json.loads(pathlib.Path('MANIFEST.json').read_text()); "
             "names=[p[4:-3].replace('/','.') for p in m['recursive_import_closure'] "
             "if p.startswith('src/') and not p.endswith('__init__.py')]; "
             "[importlib.import_module(n) for n in names]; "
             "w=runpy.run_path('scripts/phys68_ncp.py',run_name='capsule_import_only'); "
             "r=w['read_request']('research/hh_phys68_20261019/ncp_delivery/REQUEST_L64.json'); "
             "b=w['binding_for'](r,w['FROZEN_SOURCE']); "
             "print(json.dumps({'imported_modules':names,'request_max_ell':r.max_ell,"
             "'source_sha256':b['source_sha256'],'engine':b['engine'],"
             "'fingerprint':w['digest'](b),'scientific_executions':0},sort_keys=True))"],
        ]
        for command in commands:
            result = subprocess.run(command, cwd=root, env=environment,
                                    capture_output=True, text=True, timeout=30)
            checks.append({"command": command, "exit_code": result.returncode,
                           "stdout": result.stdout, "stderr": result.stderr})
            if result.returncode != 0:
                raise RuntimeError(json.dumps(checks[-1]))
        receipt = {
            "schema": "WU088_HH_PHYS68_L64_CAPSULE_CLEAN_RESTORE_V1",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "elapsed_seconds": time.monotonic()-start,
            "archive": str(args.archive.resolve()), "archive_bytes": len(data),
            "archive_sha256": hashlib.sha256(data).hexdigest(),
            "status": "PASS_HASH_IMPORT_HELP_REQUEST_BINDING",
            "payloads_checked": len(checked), "checks": checks,
            "temporary_restore_removed_after_check": True,
            "scientific_executions": 0, "radial_integrations": 0,
            "Coulomb_probes": 0, "angular_probes": 0,
            "tests_rerun": 0, "preflight_rerun": 0, "NCP_submissions": 0,
            "reuse": "Existing 21-test receipt and one mathematical preflight remain unchanged.",
            "HH_R10": "OFF",
        }
        args.receipt.write_text(json.dumps(receipt,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
        print(json.dumps({k:v for k,v in receipt.items() if k != "checks"},sort_keys=True,indent=2))


if __name__ == "__main__":
    main()
