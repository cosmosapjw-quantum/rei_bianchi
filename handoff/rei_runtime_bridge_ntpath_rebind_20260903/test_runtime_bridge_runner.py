from __future__ import annotations

import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock


PACKAGE = Path(__file__).resolve().parent
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = PACKAGE / "runtime_bridge_runner.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location(
        "rei_runtime_ntpath_rebind_runner_test", RUNNER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FakeBridge:
    GIT = Path("/usr/bin/git")

    def __init__(self, outputs: dict[tuple[str, ...], str]) -> None:
        self.outputs = outputs

    def _run(self, command, cwd=None):
        del cwd
        arguments = tuple(command[3:])
        if arguments not in self.outputs:
            raise AssertionError(arguments)
        return self.outputs[arguments]


class RuntimeBridgeNtpathRebindTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = _load_runner()

    def _standalone_bridge(self, repo: Path) -> FakeBridge:
        dot_git = repo / ".git"
        (dot_git / "objects/info").mkdir(parents=True)
        return FakeBridge(
            {
                ("rev-parse", "--absolute-git-dir"): f"{dot_git}\n",
                ("rev-parse", "--git-common-dir"): f"{dot_git}\n",
                ("rev-parse", "--is-shallow-repository"): "false\n",
                ("worktree", "list", "--porcelain"): (
                    f"worktree {repo}\nHEAD {'1' * 40}\ndetached\n"
                ),
            }
        )

    def test_01_package_index_is_closed_and_blob_exact(self) -> None:
        self.runner.verify_manifest()

    def test_02_package_index_rejects_an_unindexed_extra_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rei-rebind-package-") as temporary:
            target = Path(temporary) / "package"
            shutil.copytree(PACKAGE, target)
            (target / "unexpected.txt").write_text("unexpected\n", encoding="utf-8")
            with self.assertRaisesRegex(
                self.runner.HandoffError, "PACKAGE_SCOPE_MISMATCH"
            ):
                self.runner.verify_manifest(
                    root=target, manifest=target / "PACKAGE_INDEX.json"
                )

    def test_03_contract_exactly_rebinds_pr37_lock_and_new_attempt(self) -> None:
        contract = self.runner.load_contract()
        self.assertEqual(
            contract["immutable_predecessor"]["commit"],
            "5b6957237bbe8edfdfe3c980910cba690d23775c",
        )
        self.assertEqual(
            contract["immutable_predecessor"]["tree"],
            "805e92779ba6e7d956d5ac936f0934f5879fd3a1",
        )
        self.assertEqual(
            contract["runtime_bridge"]["input_lock"]["sha256"],
            "20db870e76ff8a82f2b6f6d38d90eb915b73d5564d6dfbee60a524862ab2e989",
        )
        self.assertEqual(contract["attempt_budget"]["prior_runtime_attempts"], 2)
        self.assertEqual(contract["attempt_budget"]["remaining_native_attempts"], 1)
        self.assertNotEqual(
            contract["attempt_budget"]["create_only_claim_path"],
            contract["attempt_budget"]["superseded_consumed_claim_path"],
        )
        self.assertEqual(
            contract["claim_ceiling"]["first_interval"],
            "NO_PASS_FIRST_CANONICAL_INTERVAL",
        )

    def test_04_actual_pr37_checkout_matches_patched_lock_and_bridge(self) -> None:
        observed = self.runner.verify_patched_runtime_inputs(REPOSITORY_ROOT)
        self.assertEqual(observed["declared_import_root_count"], 23)
        self.assertEqual(observed["declared_path_count"], 17)
        self.assertEqual(observed["forbidden_import_roots"], ["jax", "jaxlib"])
        self.assertEqual(
            observed["input_lock_sha256"],
            "20db870e76ff8a82f2b6f6d38d90eb915b73d5564d6dfbee60a524862ab2e989",
        )
        self.assertEqual(
            observed["production_bridge_sha256"],
            "91fe316f1e8b81d64e9929d7a4814b77808fdf486e2ca67cd2f615e8617fce85",
        )

    def test_05_input_binding_rejects_hash_drift_before_native_dispatch(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rei-rebind-input-") as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            lock_path = repo / "lock.json"
            bridge_path = repo / "bridge.py"
            bridge_path.write_text("VALUE = 1\n", encoding="utf-8")
            lock = {
                "schema": "rei-local-01-input-lock/v2",
                "runtime_closure": {
                    "declared_import_roots": ["ntpath", "pathlib"],
                    "declared_paths": [{} for _ in range(17)],
                    "forbidden_import_roots": ["jax", "jaxlib"],
                },
            }
            lock_path.write_text(json.dumps(lock, sort_keys=True), encoding="utf-8")
            contract = copy.deepcopy(self.runner.load_contract())
            contract["runtime_bridge"] = {
                "path": "bridge.py",
                "sha256": _sha256(bridge_path),
                "input_lock": {
                    "path": "lock.json",
                    "sha256": _sha256(lock_path),
                    "schema": "rei-local-01-input-lock/v2",
                    "required_declared_import_root": "ntpath",
                    "required_declared_path_count": 17,
                    "required_forbidden_import_roots": ["jax", "jaxlib"],
                },
            }
            self.runner.verify_patched_runtime_inputs(repo, contract)
            lock_path.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(
                self.runner.HandoffError, "PATCHED_INPUT_LOCK_IDENTITY_MISMATCH"
            ):
                self.runner.verify_patched_runtime_inputs(repo, contract)

    def test_06_section0_receipt_still_requires_exact_regular_bytes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rei-rebind-section0-") as temporary:
            path = Path(temporary) / "section0.json"
            path.write_text(
                json.dumps({"status": "PASS_IMMUTABLE_SECTION_0"}),
                encoding="utf-8",
            )
            digest = _sha256(path)
            observed = self.runner.load_section_0_receipt(
                path, digest, "PASS_IMMUTABLE_SECTION_0"
            )
            self.assertEqual(observed["status"], "PASS_IMMUTABLE_SECTION_0")
            with self.assertRaisesRegex(self.runner.HandoffError, "IDENTITY_MISMATCH"):
                self.runner.load_section_0_receipt(
                    path, "0" * 64, "PASS_IMMUTABLE_SECTION_0"
                )
            link = Path(temporary) / "section0-link.json"
            link.symlink_to(path)
            with self.assertRaisesRegex(self.runner.HandoffError, "IDENTITY_MISMATCH"):
                self.runner.load_section_0_receipt(
                    link, digest, "PASS_IMMUTABLE_SECTION_0"
                )

    def test_07_fresh_single_root_repository_context_is_required(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rei-rebind-clone-") as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            bridge = self._standalone_bridge(repo)
            self.assertEqual(
                self.runner.verify_standalone_repository_context(bridge, repo),
                (repo.resolve(),),
            )
            (repo / ".git/objects/info/alternates").write_text(
                "/untrusted/object-store\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(
                self.runner.HandoffError, "ALTERNATES_FORBIDDEN"
            ):
                self.runner.verify_standalone_repository_context(bridge, repo)

    def test_08_new_attempt_claim_is_create_only_and_material_delta_bound(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rei-rebind-claim-") as temporary:
            claim = Path(temporary) / "attempt.json"
            created = self.runner.claim_runner_attempt(claim)
            record = json.loads(created.read_text(encoding="utf-8"))
            self.assertEqual(record["status"], "NATIVE_ATTEMPT_CLAIMED")
            self.assertEqual(
                record["immutable_predecessor_commit"],
                "5b6957237bbe8edfdfe3c980910cba690d23775c",
            )
            self.assertEqual(
                record["patched_input_lock_sha256"],
                "20db870e76ff8a82f2b6f6d38d90eb915b73d5564d6dfbee60a524862ab2e989",
            )
            with self.assertRaisesRegex(
                self.runner.HandoffError, "RUNTIME_ATTEMPT_ALREADY_CLAIMED"
            ):
                self.runner.claim_runner_attempt(claim)

    def test_09_main_dispatches_at_most_once_for_the_new_claim(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rei-rebind-main-") as temporary:
            root = Path(temporary)
            output = root / "output"
            output.mkdir()
            claim = root / "attempt.json"
            arguments = [
                "--repo",
                str(root / "repo"),
                "--section0-receipt",
                str(root / "section0.json"),
                "--rustc",
                "/usr/bin/python3",
                "--evidence-root",
                str(root / "evidence"),
            ]
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                io.StringIO()
            ) as captured, mock.patch.object(
                self.runner._base,
                "run",
                return_value=({"status": "TEST_PASS"}, output),
            ) as dispatch:
                first = self.runner.main(arguments, attempt_claim_path=claim)
                second = self.runner.main(arguments, attempt_claim_path=claim)
            self.assertEqual(first, 0)
            self.assertEqual(second, 65)
            self.assertEqual(dispatch.call_count, 1)
            self.assertIn("RUNTIME_ATTEMPT_ALREADY_CLAIMED", captured.getvalue())

    def test_10_unexpected_runtime_failure_remains_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rei-rebind-fail-") as temporary:
            root = Path(temporary)
            with contextlib.redirect_stderr(io.StringIO()) as captured:
                status = self.runner.main(
                    [
                        "--repo",
                        str(root / "missing-repo"),
                        "--section0-receipt",
                        str(root / "missing-receipt.json"),
                        "--rustc",
                        "/usr/bin/python3",
                        "--evidence-root",
                        str(root / "evidence"),
                    ],
                    attempt_claim_path=root / "attempt.json",
                )
            self.assertEqual(status, 65)
            self.assertIn("STOP_INVALID", captured.getvalue())


if __name__ == "__main__":
    unittest.main()
