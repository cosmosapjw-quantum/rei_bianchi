#!/usr/bin/env python3
"""Render, but never execute, a bwrap mount-plan fragment for a verified bundle."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Iterable


def _load_verifier():
    path = Path(__file__).with_name("verify_bundle.py")
    spec = importlib.util.spec_from_file_location("rei_sealed_authority_verifier", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load verifier: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_VERIFIER = _load_verifier()
AuthorityVerificationError = _VERIFIER.AuthorityVerificationError
verify_bundle = _VERIFIER.verify_bundle
_verify_bundle_against_contract = _VERIFIER._verify_bundle_against_contract


def render_plan(
    bundle_root: Path,
    expected_manifest_sha256: str,
) -> dict[str, object]:
    receipt, entries = _verify_bundle_against_contract(
        bundle_root,
        Path(__file__).with_name("CONTRACT.json"),
        expected_manifest_sha256,
        production_contract=True,
    )
    return _render_verified_entries(bundle_root, receipt, entries)


def _render_verified_entries(
    bundle_root: Path,
    receipt: dict[str, object],
    entries: list[dict[str, object]],
) -> dict[str, object]:
    bundle_root = bundle_root.absolute()
    directories = {"/"}
    for entry in entries:
        parent = PurePosixPath(entry["path"]).parent
        while str(parent) != "/":
            directories.add(str(parent))
            parent = parent.parent
    args: list[str] = [
        "--unshare-all",
        "--die-with-parent",
        "--new-session",
        "--clearenv",
        "--tmpfs",
        "/",
    ]
    for directory in sorted(directories - {"/"}, key=lambda item: (item.count("/"), item)):
        args.extend(("--dir", directory))
    for entry in entries:
        logical = entry["path"]
        if entry["type"] == "file":
            source = bundle_root / "rootfs" / logical.lstrip("/")
            args.extend(("--ro-bind", str(source), logical))
        else:
            args.extend(("--symlink", entry["target"], logical))
    return {
        "schema": "rei-bwrap-native-authority-mount-plan/v1",
        "classification": "NON_EXECUTABLE_TEMPLATE_BYTE_IDENTITY_ONLY",
        "executable": False,
        "source_path_stability": "NOT_KERNEL_ENFORCED_DO_NOT_EXECUTE",
        "bundle_receipt": receipt,
        "bwrap_argv_fragment": args,
        "required_external_plan_fields": [
            "pinned bwrap executable SHA-256 and dependency closure",
            "pinned child executable, ELF interpreter, and dynamic-library closure",
            "read-only repository and input-authority mounts",
            "an outside-worktree writable build-output mount",
            "minimal /proc and /dev policy justified by observed accesses",
            "kernel policy receipt required by the production entrypoint",
            "kernel-enforced source-tree immutability from final verification "
            "through child exit",
        ],
        "runtime_boundary": "NOT_RUN",
        "build": "NOT_RUN",
        "native_tests": "NOT_RUN",
        "adapter": "STOP_INVALID",
        "canonical_pilot": "NOT_RUN",
        "first_interval": "NO_PASS_FIRST_CANONICAL_INTERVAL",
        "scientific_pass": "NOT_CLAIMED",
        "scientific_publication": "NOT_RUN"
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-root", required=True, type=Path)
    parser.add_argument("--expected-manifest-sha256", required=True)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        plan = render_plan(args.bundle_root, args.expected_manifest_sha256)
    except (AuthorityVerificationError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 65
    print(json.dumps(plan, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
