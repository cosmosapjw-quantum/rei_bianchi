#!/usr/bin/env python3
"""Behavior contract for the 03A4 runtime-toolchain path binding."""

from __future__ import annotations

import copy
import hashlib
import importlib
import os
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "handoff" / "rei_runtime_prelease_import_firewall_green_20260903"
if str(PACKAGE) not in sys.path:
    sys.path.insert(0, str(PACKAGE))

common = importlib.import_module("common_v3_impl")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RuntimeToolchainPathBindingBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.actual: dict[str, Path] = {}
        self.declared: dict[str, Path] = {}
        for role, executable in (
            ("cc", True),
            ("ld", True),
            ("mpfr", False),
            ("gmp", False),
        ):
            actual = self.root / f"{role}.real"
            actual.write_bytes(f"locked-{role}-bytes\n".encode("ascii"))
            actual.chmod(0o755 if executable else 0o644)
            declared = self.root / f"{role}.declared"
            declared.symlink_to(actual.name)
            self.actual[role] = actual
            self.declared[role] = declared

        self.contract = {
            "runtime_toolchain_path_binding": {
                "authority": "POSTLEASE_PRODUCTION_PATHS",
                "paths": {
                    role: str(self.declared[role])
                    for role in ("cc", "ld", "mpfr", "gmp")
                },
            },
            "successor_section0": {
                "semantic_toolchain_lock": {
                    f"{role}_sha256": sha256(self.actual[role])
                    for role in ("cc", "ld", "mpfr", "gmp")
                }
            },
        }

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def validator(self):
        function = getattr(common, "validate_runtime_toolchain_witness_paths", None)
        self.assertTrue(
            callable(function),
            "RUNTIME_TOOLCHAIN_PATH_VALIDATOR_NOT_IMPLEMENTED",
        )
        return function

    def invoke(self, contract=None, paths=None):
        selected = self.actual if paths is None else paths
        return self.validator()(
            self.contract if contract is None else contract,
            cc=selected["cc"],
            ld=selected["ld"],
            mpfr=selected["mpfr"],
            gmp=selected["gmp"],
        )

    def test_fixed_declared_symlinks_accept_only_their_resolved_regular_files(self) -> None:
        snapshot = self.invoke()
        self.assertEqual(snapshot["schema"], "rei-runtime-toolchain-path-snapshot/v1")
        self.assertEqual(set(snapshot["paths"]), {"cc", "ld", "mpfr", "gmp"})
        for role in snapshot["paths"]:
            row = snapshot["paths"][role]
            self.assertEqual(row["declared_path"], str(self.declared[role]))
            self.assertEqual(row["resolved_path"], str(self.actual[role].resolve()))
            self.assertEqual(row["sha256"], sha256(self.actual[role]))
            self.assertEqual(row["size_bytes"], self.actual[role].stat().st_size)
            self.assertEqual(row["executable"], role in {"cc", "ld"})
        self.assertRegex(snapshot["sha256"], r"^[0-9a-f]{64}$")

    def test_same_hash_alternate_file_is_rejected(self) -> None:
        alternate = self.root / "cc.alternate"
        alternate.write_bytes(self.actual["cc"].read_bytes())
        alternate.chmod(0o755)
        paths = dict(self.actual)
        paths["cc"] = alternate
        with self.assertRaisesRegex(
            common.FirewallError,
            "RUNTIME_TOOLCHAIN_WITNESS_PATH_MISMATCH:cc",
        ):
            self.invoke(paths=paths)

    def test_runtime_path_hash_mismatch_is_rejected(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["successor_section0"]["semantic_toolchain_lock"][
            "ld_sha256"
        ] = "0" * 64
        with self.assertRaisesRegex(
            common.FirewallError,
            "RUNTIME_TOOLCHAIN_WITNESS_HASH_MISMATCH:ld",
        ):
            self.invoke(contract=contract)

    def test_missing_declared_runtime_path_is_rejected(self) -> None:
        self.declared["mpfr"].unlink()
        with self.assertRaisesRegex(
            common.FirewallError,
            "RUNTIME_TOOLCHAIN_PATH_UNAVAILABLE:mpfr",
        ):
            self.invoke()

    def test_nonexecutable_compiler_driver_is_rejected(self) -> None:
        self.actual["cc"].chmod(0o644)
        with self.assertRaisesRegex(
            common.FirewallError,
            "RUNTIME_TOOLCHAIN_PATH_NOT_EXECUTABLE:cc",
        ):
            self.invoke()

    def test_snapshot_hash_is_deterministic_and_covers_paths(self) -> None:
        first = self.invoke()
        second = self.invoke()
        self.assertEqual(first, second)

        changed = copy.deepcopy(self.contract)
        new_declared = self.root / "cc.second-declared"
        new_declared.symlink_to(self.actual["cc"].name)
        changed["runtime_toolchain_path_binding"]["paths"]["cc"] = str(
            new_declared
        )
        third = self.invoke(contract=changed)
        self.assertNotEqual(first["sha256"], third["sha256"])
        self.assertEqual(
            first["paths"]["cc"]["resolved_path"],
            third["paths"]["cc"]["resolved_path"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
