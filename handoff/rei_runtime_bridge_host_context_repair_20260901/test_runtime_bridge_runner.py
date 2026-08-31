from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock


RUNNER_PATH = Path(__file__).with_name("runtime_bridge_runner.py")


def _load_runner():
    spec = importlib.util.spec_from_file_location(
        "rei_runtime_host_context_runner_test", RUNNER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


class RuntimeBridgeRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = _load_runner()

    def _standalone_bridge(
        self,
        repo: Path,
        *,
        report: str | None = None,
        common_dir: Path | None = None,
        shallow: str = "false\n",
    ) -> FakeBridge:
        dot_git = repo / ".git"
        (dot_git / "objects/info").mkdir(parents=True)
        common = common_dir if common_dir is not None else dot_git
        return FakeBridge(
            {
                ("rev-parse", "--absolute-git-dir"): f"{dot_git}\n",
                ("rev-parse", "--git-common-dir"): f"{common}\n",
                ("rev-parse", "--is-shallow-repository"): shallow,
                ("worktree", "list", "--porcelain"): report
                if report is not None
                else f"worktree {repo}\nHEAD {'1' * 40}\ndetached\n",
            }
        )

    def test_manifest_is_closed_and_hashes_every_package_file(self) -> None:
        self.runner.verify_manifest()

    def test_section0_receipt_requires_exact_regular_bytes_and_status(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "section0.json"
            path.write_text(
                json.dumps({"status": "PASS_IMMUTABLE_SECTION_0"}), encoding="utf-8"
            )
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            observed = self.runner.load_section_0_receipt(
                path, digest, "PASS_IMMUTABLE_SECTION_0"
            )
            self.assertEqual(observed["status"], "PASS_IMMUTABLE_SECTION_0")
            with self.assertRaisesRegex(self.runner.HandoffError, "IDENTITY_MISMATCH"):
                self.runner.load_section_0_receipt(
                    path, "0" * 64, "PASS_IMMUTABLE_SECTION_0"
                )
            with self.assertRaisesRegex(self.runner.HandoffError, "STATUS_MISMATCH"):
                self.runner.load_section_0_receipt(path, digest, "OTHER")
            link = Path(temporary) / "section0-link.json"
            link.symlink_to(path)
            with self.assertRaisesRegex(self.runner.HandoffError, "IDENTITY_MISMATCH"):
                self.runner.load_section_0_receipt(
                    link, digest, "PASS_IMMUTABLE_SECTION_0"
                )

    def test_contract_compiles_attempt_budget_identity_and_claim_ceiling(self) -> None:
        contract = self.runner.load_contract()
        self.assertEqual(
            contract["immutable_predecessor"]["commit"],
            "723882d80d57ee8a919bc52ab74633b743447d0c",
        )
        self.assertEqual(
            contract["execution_context"]["repository_mode"],
            "FRESH_STANDALONE_CLONE",
        )
        self.assertEqual(contract["attempt_budget"]["remaining_native_attempts"], 1)
        self.assertEqual(
            contract["residual_blockers"]["production_prunable_parser"],
            "PRUNABLE_WORKTREE_ENUMERATION_UNHANDLED",
        )
        self.assertEqual(contract["rust_backend"]["rounding_policy"], "MPFR_RNDD_RNDU")
        self.assertEqual(contract["claim_ceiling"]["adapter"], "STOP_INVALID")

    def test_rustc_locator_is_absolute_executable_and_explicitly_bound(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            resolved = self.runner.configure_rustc_locator(Path("/usr/bin/python3"))
            self.assertEqual(os.environ["REI_RUSTC_1_94_1"], str(resolved))
            with self.assertRaisesRegex(self.runner.HandoffError, "NOT_ABSOLUTE"):
                self.runner.configure_rustc_locator(Path("relative/rustc"))
            with self.assertRaisesRegex(self.runner.HandoffError, "UNAVAILABLE"):
                self.runner.configure_rustc_locator(Path("/definitely/missing/rustc"))
            with tempfile.TemporaryDirectory() as temporary:
                nonexecutable = Path(temporary) / "rustc"
                nonexecutable.write_text("not executable", encoding="utf-8")
                nonexecutable.chmod(0o600)
                with self.assertRaisesRegex(self.runner.HandoffError, "UNAVAILABLE"):
                    self.runner.configure_rustc_locator(nonexecutable)

    def test_single_root_private_common_dir_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            bridge = self._standalone_bridge(repo)
            self.assertEqual(
                self.runner.verify_standalone_repository_context(bridge, repo),
                (repo.resolve(),),
            )

    def test_multiple_or_prunable_worktree_inventory_is_rejected_typed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            missing = Path(temporary) / "missing-linked-worktree"
            report = (
                f"worktree {repo}\nHEAD {'1' * 40}\ndetached\n\n"
                f"worktree {missing}\nHEAD {'2' * 40}\n"
                "prunable gitdir file points to non-existent location\n"
            )
            bridge = self._standalone_bridge(repo, report=report)
            with self.assertRaisesRegex(
                self.runner.HandoffError, "RUNTIME_STANDALONE_CLONE_REQUIRED"
            ):
                self.runner.verify_standalone_repository_context(bridge, repo)

    def test_common_dir_alternates_and_shallow_mutations_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)

            linked = root / "linked"
            linked.mkdir()
            foreign_common = root / "foreign.git"
            foreign_common.mkdir()
            linked_bridge = self._standalone_bridge(
                linked, common_dir=foreign_common
            )
            with self.assertRaisesRegex(
                self.runner.HandoffError, "RUNTIME_STANDALONE_CLONE_REQUIRED"
            ):
                self.runner.verify_standalone_repository_context(linked_bridge, linked)

            alternate = root / "alternate"
            alternate.mkdir()
            alternate_bridge = self._standalone_bridge(alternate)
            (alternate / ".git/objects/info/alternates").write_text(
                "/untrusted/object-store\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(
                self.runner.HandoffError, "ALTERNATES_FORBIDDEN"
            ):
                self.runner.verify_standalone_repository_context(
                    alternate_bridge, alternate
                )

            shallow = root / "shallow"
            shallow.mkdir()
            shallow_bridge = self._standalone_bridge(shallow, shallow="true\n")
            with self.assertRaisesRegex(
                self.runner.HandoffError, "SHALLOW_REPOSITORY_FORBIDDEN"
            ):
                self.runner.verify_standalone_repository_context(shallow_bridge, shallow)

    def test_worktree_inventory_race_is_typed_before_evidence_creation(self) -> None:
        class ChangedBridge:
            def _worktree_roots(self, repo):
                del repo
                raise FileNotFoundError("stale path")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(
                self.runner.HandoffError,
                "RUNTIME_WORKTREE_INVENTORY_CHANGED_AFTER_PREFLIGHT",
            ):
                self.runner.create_evidence_root(
                    root / "evidence", ChangedBridge(), root
                )
            self.assertFalse((root / "evidence").exists())

    def test_create_only_attempt_claim_prevents_second_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(
            io.StringIO()
        ), contextlib.redirect_stderr(io.StringIO()) as captured:
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
            with mock.patch.object(
                self.runner,
                "run",
                return_value=({"status": "TEST_PASS"}, output),
            ) as dispatch:
                first = self.runner.main(arguments, attempt_claim_path=claim)
                second = self.runner.main(arguments, attempt_claim_path=claim)
            self.assertEqual(first, 0)
            self.assertEqual(second, 65)
            self.assertEqual(dispatch.call_count, 1)
            self.assertTrue(claim.is_file())
            self.assertIn("RUNTIME_ATTEMPT_ALREADY_CLAIMED", captured.getvalue())

    def test_unexpected_runtime_error_is_still_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stderr(
            io.StringIO()
        ) as captured:
            status = self.runner.main(
                [
                    "--repo",
                    str(Path(temporary) / "missing-repo"),
                    "--section0-receipt",
                    str(Path(temporary) / "missing-receipt.json"),
                    "--rustc",
                    "/usr/bin/python3",
                    "--evidence-root",
                    str(Path(temporary) / "evidence"),
                ],
                attempt_claim_path=Path(temporary) / "attempt.json",
            )
        self.assertEqual(status, 65)
        self.assertIn("STOP_INVALID", captured.getvalue())


if __name__ == "__main__":
    unittest.main()
