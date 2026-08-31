from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STAGE = ROOT / "stages" / "REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER"
BRIDGE = STAGE / "analysis" / "rust_source_bound_thermal.py"


def _load_bridge():
    spec = importlib.util.spec_from_file_location("rei_runtime_closure_bridge", BRIDGE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load bridge at {BRIDGE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _run(*args: str, cwd: Path) -> None:
    subprocess.run(
        args,
        cwd=cwd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


class RuntimeInputClosureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="rei-runtime-closure-")
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        _run("git", "init", "--quiet", cwd=self.repo)
        _run("git", "config", "user.name", "REI Test", cwd=self.repo)
        _run("git", "config", "user.email", "rei-test@example.invalid", cwd=self.repo)
        self.stage = self.repo / "stage"
        self.stage.mkdir()
        self.authority = self.repo / "authority.bin"
        self.authority.write_bytes(b"pinned-authority\n")
        self.lock_path = self.stage / "INPUT_LOCK.json"
        self.bridge = _load_bridge()
        self._write_lock()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write_lock(
        self,
        *,
        declared_imports: tuple[str, ...] = ("hashlib",),
        forbidden_imports: tuple[str, ...] = ("jax", "jaxlib"),
    ) -> None:
        lock = {
            "runtime_closure": {
                "schema": "rei-runtime-input-closure/v2",
                "enforcement_scope": "INVOCATION_SCOPED_NOT_GLOBAL_INTERCEPTION",
                "declared_paths": [
                    {
                        "path": "authority.bin",
                        "sha256": hashlib.sha256(self.authority.read_bytes()).hexdigest(),
                        "role": "TEST_AUTHORITY",
                    }
                ],
                "declared_import_roots": list(declared_imports),
                "forbidden_import_roots": list(forbidden_imports),
                "path_policy": {
                    "resolve_symlinks": True,
                    "reject_undeclared": True,
                    "require_regular_file": True,
                    "verify_sha256": True,
                },
                "git_config_policy": {
                    "inspect_repo_local": True,
                    "inspect_common": True,
                    "inspect_worktree_when_enabled": True,
                    "reject_extensions_partial_clone": True,
                    "reject_promisor_remotes": True,
                    "system_and_global_out_of_scope": True,
                },
            }
        }
        self.lock_path.write_text(json.dumps(lock, sort_keys=True), encoding="utf-8")

    def _validate(
        self,
        *,
        repo: Path | None = None,
        invocation=None,
    ):
        effective_repo = repo or self.repo
        effective_stage = effective_repo / "stage"
        effective_lock = effective_stage / "INPUT_LOCK.json"
        return self.bridge.validate_runtime_closure(
            repo=effective_repo,
            stage_dir=effective_stage,
            input_lock_path=effective_lock,
            invocation=invocation or (lambda _capability: (effective_repo / "authority.bin").read_bytes()),
        )

    def test_01_declared_identity_and_import_pass(self) -> None:
        result = self._validate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["enforcement_scope"], "INVOCATION_SCOPED_NOT_GLOBAL_INTERCEPTION")
        self.assertEqual(result["observed_path_count"], 1)

    def test_02_actual_undeclared_open_is_rejected_immediately(self) -> None:
        extra = self.repo / "undeclared.bin"
        extra.write_bytes(b"not locked")
        with self.assertRaisesRegex(RuntimeError, "UNDECLARED_PATH"):
            self._validate(invocation=lambda _capability: extra.read_bytes())

    def test_03_declared_path_hash_drift_is_rejected(self) -> None:
        self.authority.write_bytes(b"mutated")
        with self.assertRaisesRegex(RuntimeError, "HASH_MISMATCH"):
            self._validate()

    def test_04_actual_undeclared_import_root_is_rejected(self) -> None:
        module_name = "rei_runtime_undeclared_probe"
        (self.repo / f"{module_name}.py").write_text("VALUE = 1\n", encoding="utf-8")

        def import_probe(_capability):
            sys.path.insert(0, str(self.repo))
            sys.modules.pop(module_name, None)
            try:
                __import__(module_name)
            finally:
                sys.modules.pop(module_name, None)
                sys.path.remove(str(self.repo))

        with self.assertRaisesRegex(RuntimeError, "UNDECLARED_IMPORT"):
            self._validate(invocation=import_probe)

    def test_04b_cached_undeclared_import_is_also_rejected(self) -> None:
        self.assertIn("os", sys.modules)
        with self.assertRaisesRegex(RuntimeError, "UNDECLARED_IMPORT"):
            self._validate(invocation=lambda _capability: __import__("os"))

    def test_05_actual_jax_import_is_rejected_even_if_declared(self) -> None:
        self._write_lock(declared_imports=("hashlib", "jax"))
        package = self.repo / "jax"
        package.mkdir()
        (package / "__init__.py").write_text("VALUE = 1\n", encoding="utf-8")

        def import_jax(_capability):
            sys.path.insert(0, str(self.repo))
            sys.modules.pop("jax", None)
            try:
                __import__("jax")
            finally:
                sys.modules.pop("jax", None)
                sys.path.remove(str(self.repo))

        with self.assertRaisesRegex(RuntimeError, "FORBIDDEN_IMPORT"):
            self._validate(invocation=import_jax)

    def test_06_fabricated_self_report_cannot_produce_pass(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "SELF_REPORTED_OBSERVATION_FORBIDDEN"):
            self.bridge.validate_runtime_closure(
                repo=self.repo,
                stage_dir=self.stage,
                input_lock_path=self.lock_path,
                observed_paths=(self.authority,),
                observed_imports=("hashlib",),
            )

    def test_07_missing_invocation_cannot_produce_pass(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "RUNTIME_OBSERVATION_CAPABILITY_REQUIRED"):
            self.bridge.validate_runtime_closure(
                repo=self.repo,
                stage_dir=self.stage,
                input_lock_path=self.lock_path,
            )

    def test_07b_callback_cannot_suppress_an_audit_violation_into_pass(self) -> None:
        extra = self.repo / "suppressed.bin"
        extra.write_bytes(b"not locked")

        def suppress_probe(_capability):
            try:
                extra.read_bytes()
            except RuntimeError:
                pass

        with self.assertRaisesRegex(RuntimeError, "UNDECLARED_PATH"):
            self._validate(invocation=suppress_probe)

    def test_07c_observer_capability_is_factory_only_and_expires(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError, "RUNTIME_OBSERVATION_CAPABILITY_FACTORY_REQUIRED"
        ):
            self.bridge.RuntimeClosureCapability(None)

        captured = []
        self._validate(invocation=lambda capability: captured.append(capability))
        with self.assertRaisesRegex(
            RuntimeError, "RUNTIME_OBSERVATION_CAPABILITY_INACTIVE"
        ):
            captured[0]._observe_path(self.authority)

    def test_07d_unobserved_thread_context_is_rejected(self) -> None:
        def threaded_probe(_capability):
            worker = threading.Thread(target=lambda: None)
            worker.start()
            worker.join()

        with self.assertRaisesRegex(RuntimeError, "UNOBSERVED_EXECUTION_CONTEXT"):
            self._validate(invocation=threaded_probe)

    def test_08_local_partial_clone_config_is_rejected(self) -> None:
        _run("git", "config", "extensions.partialClone", "origin", cwd=self.repo)
        with self.assertRaisesRegex(RuntimeError, "GIT_PARTIAL_CLONE"):
            self._validate()

    def test_09_common_promisor_config_is_rejected_from_linked_worktree(self) -> None:
        _run("git", "add", "authority.bin", "stage/INPUT_LOCK.json", cwd=self.repo)
        _run("git", "commit", "--quiet", "-m", "fixture", cwd=self.repo)
        linked = Path(self.tmp.name) / "linked"
        _run("git", "worktree", "add", "--quiet", "--detach", str(linked), cwd=self.repo)
        _run("git", "config", "remote.origin.promisor", "true", cwd=self.repo)
        with self.assertRaisesRegex(RuntimeError, "GIT_PROMISOR"):
            self._validate(repo=linked)

    def test_10_worktree_promisor_config_is_rejected(self) -> None:
        _run("git", "add", "authority.bin", "stage/INPUT_LOCK.json", cwd=self.repo)
        _run("git", "commit", "--quiet", "-m", "fixture", cwd=self.repo)
        linked = Path(self.tmp.name) / "linked"
        _run("git", "worktree", "add", "--quiet", "--detach", str(linked), cwd=self.repo)
        _run("git", "config", "extensions.worktreeConfig", "true", cwd=self.repo)
        _run("git", "config", "--worktree", "remote.origin.promisor", "true", cwd=linked)
        with self.assertRaisesRegex(RuntimeError, "GIT_PROMISOR"):
            self._validate(repo=linked)


if __name__ == "__main__":
    unittest.main()
