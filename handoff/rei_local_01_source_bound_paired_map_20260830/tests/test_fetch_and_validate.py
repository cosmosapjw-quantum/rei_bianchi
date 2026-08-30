#!/usr/bin/env python3
"""Behavioral tests for the immutable-payload locator.

These tests deliberately build real Git repositories and object graphs.  They
do not mock Git, hashes, filesystem modes, refs, worktrees, or validator
execution.  The production pins are replaced only through ``ObjectPins`` so
the same validation path is exercised with small, hand-auditable fixtures.
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass, replace
import errno
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest import mock


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
LOCATOR_PATH = PACKAGE_ROOT / "FETCH_AND_VALIDATE.py"
MODULE_NAME = "rei_local_01_fetch_and_validate_under_test"

if not LOCATOR_PATH.is_file():
    raise ImportError(f"required locator module is missing: {LOCATOR_PATH}")

SPEC = importlib.util.spec_from_file_location(MODULE_NAME, LOCATOR_PATH)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import machinery guard
    raise ImportError(f"cannot load locator module: {LOCATOR_PATH}")
locator = importlib.util.module_from_spec(SPEC)
sys.modules[MODULE_NAME] = locator
SPEC.loader.exec_module(locator)


PAYLOAD_ROOT = "research/continuation_20260830"
HELPER_PATH = f"{PAYLOAD_ROOT}/paired_budget.py"
VALIDATOR_PATH = f"{PAYLOAD_ROOT}/verify_payload.py"
MANIFEST_PATH = f"{PAYLOAD_ROOT}/MANIFEST.sha256"
PUBLICATION_PATH = f"{PAYLOAD_ROOT}/REMOTE_PUBLICATION.json"
REC_LOCK_PATH = "external/rec_bianchi.lock.json"
BLOCKED_ARCHIVE_PATH = (
    "stages/fixture/local_results/"
    "first_interval_r2_blocked_minimum_step.tar.gz"
)

DELIVERY_PATHS = (
    f"{PAYLOAD_ROOT}/README.md",
    f"{PAYLOAD_ROOT}/CONTRACT.json",
    f"{PAYLOAD_ROOT}/CODEX_HANDOFF.md",
    HELPER_PATH,
    VALIDATOR_PATH,
    f"{PAYLOAD_ROOT}/check_mutations.py",
    f"{PAYLOAD_ROOT}/tests/test_paired_budget.py",
    f"{PAYLOAD_ROOT}/tests/test_payload.py",
    f"{PAYLOAD_ROOT}/evidence/TESTS.log",
    f"{PAYLOAD_ROOT}/evidence/mutations/MUTATIONS.json",
    f"{PAYLOAD_ROOT}/evidence/mutations/drop_remainders.log",
    f"{PAYLOAD_ROOT}/evidence/mutations/reverse_difference.log",
    f"{PAYLOAD_ROOT}/evidence/mutations/relax_strict_limit.log",
)

EXPECTED_RESULT = {
    "transport_status": "PASS_IMMUTABLE_PAYLOAD_ONLY",
    "scientific_validation": "NOT_RUN",
    "canonical_adapter": "NOT_RUN",
    "pilot_46080x3": "NOT_RUN",
    "first_interval": "NO_PASS",
    "pr14_disposition": "RECORDED_BLOCKED_MINIMUM_STEP",
    "remote_ref_status": "MATCH",
}


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run Git with stable text handling and useful assertion diagnostics."""

    process = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "LC_ALL": "C", "LANG": "C"},
        check=False,
    )
    if check and process.returncode:
        raise AssertionError(
            f"git {' '.join(args)} failed in {repo}\n"
            f"stdout:\n{process.stdout}\nstderr:\n{process.stderr}"
        )
    return process


def git_bytes(repo: Path, *args: str) -> bytes:
    process = subprocess.run(
        ["git", "--no-replace-objects", *args],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "LC_ALL": "C", "LANG": "C"},
        check=False,
    )
    if process.returncode:
        raise AssertionError(
            f"git {' '.join(args)} failed in {repo}\n"
            f"stderr:\n{process.stderr.decode(errors='replace')}"
        )
    return process.stdout


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class Graph:
    payload_commit: str
    payload_tree: str
    payload_subtree: str
    manifest_blob: str
    manifest_sha256: str
    validator_blob: str
    validator_sha256: str
    terminal_commit: str
    terminal_tree: str
    publication_blob: str
    publication_sha256: str
    branch: str


class RepositoryFixture:
    """Four-commit source/helper/payload/terminal graph with a bare origin."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.remote = root / "origin.git"
        self.author = root / "author"
        self.counter = root / "validator-runs.txt"

        git(root, "init", "--bare", str(self.remote))
        git(root, "init", "--initial-branch=main", str(self.author))
        git(self.author, "config", "user.name", "Locator Test")
        git(self.author, "config", "user.email", "locator@example.invalid")
        git(self.author, "remote", "add", "origin", self.remote.as_uri())

        self._write("tracked.txt", b"tracked baseline\n")
        self._write("staged.txt", b"staged baseline\n")
        self._write(REC_LOCK_PATH, b'{"fixture":"locked"}\n')
        self._write(BLOCKED_ARCHIVE_PATH, b"\x1f\x8bfixture-blocked-archive\n")
        git(self.author, "add", "--all")
        self._commit("fixture source")
        self.source_commit = self._rev_parse("HEAD")
        self.source_tree = self._rev_parse("HEAD^{tree}")
        self.rec_lock_blob = self._rev_parse(f"HEAD:{REC_LOCK_PATH}")
        self.blocked_archive_blob = self._rev_parse(
            f"HEAD:{BLOCKED_ARCHIVE_PATH}"
        )
        self.blocked_archive_sha256 = sha256(
            git_bytes(self.author, "show", f"HEAD:{BLOCKED_ARCHIVE_PATH}")
        )
        git(self.author, "branch", "source", self.source_commit)

        self.helper_raw = b"def paired_budget(left, right):\n    return left + right\n"
        self._write(HELPER_PATH, self.helper_raw)
        git(self.author, "add", HELPER_PATH)
        self._commit("fixture helper")
        self.helper_commit = self._rev_parse("HEAD")
        self.helper_tree = self._rev_parse("HEAD^{tree}")
        self.helper_parent = self._rev_parse("HEAD^")
        self.helper_blob = self._rev_parse(f"HEAD:{HELPER_PATH}")

        self.canonical = self.create_variant(branch="continuation")
        git(
            self.author,
            "push",
            "origin",
            f"{self.source_commit}:refs/heads/source",
            f"{self.canonical.terminal_commit}:refs/heads/continuation",
        )

    def _write(self, relative: str, raw: bytes) -> None:
        target = self.author / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)

    def _commit(self, message: str) -> None:
        git(self.author, "commit", "--no-gpg-sign", "-m", message)

    def _rev_parse(self, expression: str) -> str:
        return git(self.author, "rev-parse", expression).stdout.strip()

    def _safe_validator(
        self,
        *,
        add_unexpected_file: bool = False,
        add_unexpected_directory: bool = False,
        chmod_metadata: bool = False,
        chmod_root: bool = False,
    ) -> bytes:
        actions = []
        if add_unexpected_file:
            actions.append(
                'Path(args.root, "unexpected-validator-output.bin").write_bytes(b"extra")'
            )
        if add_unexpected_directory:
            actions.append('Path(args.root, "unexpected-empty-directory").mkdir()')
        if chmod_metadata:
            actions.append(
                f'Path(args.root, {MANIFEST_PATH!r}).chmod(0o600)'
            )
        if chmod_root:
            actions.append('Path(args.root).chmod(0o777)')
        mutation = "\n".join(actions) if actions else "pass"
        return textwrap.dedent(
            f"""\
            #!/usr/bin/env python3
            import argparse
            import json
            from pathlib import Path

            parser = argparse.ArgumentParser()
            parser.add_argument("--root", required=True)
            parser.add_argument("--repo", required=True)
            args = parser.parse_args()
            if not Path(args.root).is_dir() or not Path(args.repo).is_dir():
                raise SystemExit(3)
            {mutation}
            counter = Path({str(self.counter)!r})
            count = int(counter.read_text()) if counter.exists() else 0
            counter.write_text(str(count + 1))
            print(json.dumps({{
                "status": "PASS_PAYLOAD_ONLY",
                "files": 13,
                "source_objects": "CHECKED",
                "claim": "NO_PASS_FIRST_CANONICAL_INTERVAL",
                "next": "REI-LOCAL-01_SOURCE_BOUND_PAIRED_MAP_ADAPTER"
            }}, sort_keys=True))
            """
        ).encode("utf-8")

    @staticmethod
    def _malicious_validator(marker: Path) -> bytes:
        return textwrap.dedent(
            f"""\
            #!/usr/bin/env python3
            from pathlib import Path
            Path({str(marker)!r}).write_text("EXECUTED")
            raise SystemExit(91)
            """
        ).encode("utf-8")

    def _payload_bytes(self, validator_raw: bytes) -> dict[str, bytes]:
        contract = {
            "schema": "fixture-continuation/v1",
            "delivery_paths": list(DELIVERY_PATHS),
            "source": {"commit": self.source_commit, "tree": self.source_tree},
            "partial_publication": {
                "commit": self.helper_commit,
                "tree": self.helper_tree,
            },
            "claims": {"current": "NO_PASS_FIRST_CANONICAL_INTERVAL"},
            "next_action": "REI-LOCAL-01_SOURCE_BOUND_PAIRED_MAP_ADAPTER",
        }
        payload: dict[str, bytes] = {
            f"{PAYLOAD_ROOT}/README.md": b"# Fixture payload\r\nraw-byte-nul:\x00\r\n",
            f"{PAYLOAD_ROOT}/CONTRACT.json": (
                json.dumps(contract, indent=2, sort_keys=True) + "\n"
            ).encode("utf-8"),
            f"{PAYLOAD_ROOT}/CODEX_HANDOFF.md": b"Fixture handoff only.\n",
            HELPER_PATH: self.helper_raw,
            VALIDATOR_PATH: validator_raw,
            f"{PAYLOAD_ROOT}/check_mutations.py": b"print('fixture')\n",
            f"{PAYLOAD_ROOT}/tests/test_paired_budget.py": b"# fixture test\n",
            f"{PAYLOAD_ROOT}/tests/test_payload.py": b"# fixture test\n",
            f"{PAYLOAD_ROOT}/evidence/TESTS.log": b"fixture evidence\n",
            f"{PAYLOAD_ROOT}/evidence/mutations/MUTATIONS.json": b"{}\n",
            f"{PAYLOAD_ROOT}/evidence/mutations/drop_remainders.log": b"detected\n",
            f"{PAYLOAD_ROOT}/evidence/mutations/reverse_difference.log": b"detected\n",
            f"{PAYLOAD_ROOT}/evidence/mutations/relax_strict_limit.log": b"detected\n",
        }
        if set(payload) != set(DELIVERY_PATHS):  # fixture authoring invariant
            raise AssertionError("fixture payload does not match DELIVERY_PATHS")
        return payload

    def create_variant(
        self,
        *,
        branch: str,
        malicious_marker: Path | None = None,
        symlink_path: str | None = None,
        executable_path: str | None = None,
        unsafe_manifest: bool = False,
        receipt_mismatch: bool = False,
        add_unexpected_file: bool = False,
        add_unexpected_directory: bool = False,
        chmod_metadata: bool = False,
        chmod_root: bool = False,
    ) -> Graph:
        """Create a payload/terminal pair rooted at the immutable helper commit."""

        git(self.author, "checkout", "--detach", self.helper_commit)
        validator_raw = (
            self._malicious_validator(malicious_marker)
            if malicious_marker is not None
            else self._safe_validator(
                add_unexpected_file=add_unexpected_file,
                add_unexpected_directory=add_unexpected_directory,
                chmod_metadata=chmod_metadata,
                chmod_root=chmod_root,
            )
        )
        payload = self._payload_bytes(validator_raw)
        for name, raw in payload.items():
            self._write(name, raw)

        if symlink_path is not None:
            target = self.author / symlink_path
            target.unlink()
            target.symlink_to("README.md")
        if executable_path is not None:
            (self.author / executable_path).chmod(0o755)

        manifest_lines: list[str] = []
        for name in DELIVERY_PATHS:
            target = self.author / name
            raw = (
                os.readlink(target).encode("utf-8")
                if target.is_symlink()
                else target.read_bytes()
            )
            manifest_lines.append(f"{sha256(raw)}  {name}\n")
        if unsafe_manifest:
            manifest_lines.append(f"{sha256(b'escape')}  ../escape\n")
        manifest_raw = "".join(manifest_lines).encode("ascii")
        self._write(MANIFEST_PATH, manifest_raw)

        git(self.author, "add", "--all")
        self._commit(f"fixture payload {branch}")
        payload_commit = self._rev_parse("HEAD")
        payload_tree = self._rev_parse("HEAD^{tree}")
        payload_subtree = self._rev_parse(f"HEAD:{PAYLOAD_ROOT}")
        manifest_blob = self._rev_parse(f"HEAD:{MANIFEST_PATH}")
        validator_blob = self._rev_parse(f"HEAD:{VALIDATOR_PATH}")

        bound_payload_commit = self.source_commit if receipt_mismatch else payload_commit
        publication = {
            "schema": "rei-research-followthrough-publication/v1",
            "repository": "fixture/repo",
            "pull_request": {
                "number": 18,
                "state_at_binding": "OPEN_DRAFT_UNMERGED",
                "base_branch": "source",
                "base_head": self.source_commit,
                "head_branch": branch,
            },
            "immutable_payload": {
                "commit": bound_payload_commit,
                "tree": payload_tree,
                "path": PAYLOAD_ROOT,
                "subtree_sha1": payload_subtree,
                "manifest_blob_sha1": manifest_blob,
                "manifest_entries": len(DELIVERY_PATHS),
                "validator": VALIDATOR_PATH,
            },
            "preserved_preimage": {
                "commit": self.helper_commit,
                "tree": self.helper_tree,
                "helper_blob": self.helper_blob,
                "disposition": "UNCHANGED_HELPER_AND_ANCESTRY_RETAINED",
            },
            "verification": {
                "canonical_source_map_adapter": "NOT_RUN",
                "all_node_pilot": "NOT_RUN",
                "complete_interval": "NOT_RUN",
            },
            "claims": {
                "PR14": "STOP_INVALID_RETAINED",
                "current": "NO_PASS_FIRST_CANONICAL_INTERVAL",
                "rec_splice": False,
                "performance": "NONE",
            },
            "source_rec_lock_blob": self.rec_lock_blob,
            "exact_next_action": "REI-LOCAL-01_SOURCE_BOUND_PAIRED_MAP_ADAPTER",
            "scope": "REMOTE_METADATA_OUTSIDE_IMMUTABLE_PAYLOAD_MANIFEST",
            "merge_or_ready_authorized": False,
        }
        publication_raw = (
            json.dumps(publication, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        self._write(PUBLICATION_PATH, publication_raw)
        git(self.author, "add", PUBLICATION_PATH)
        self._commit(f"fixture terminal {branch}")
        terminal_commit = self._rev_parse("HEAD")
        terminal_tree = self._rev_parse("HEAD^{tree}")
        publication_blob = self._rev_parse(f"HEAD:{PUBLICATION_PATH}")
        git(self.author, "branch", "--force", branch, terminal_commit)

        return Graph(
            payload_commit=payload_commit,
            payload_tree=payload_tree,
            payload_subtree=payload_subtree,
            manifest_blob=manifest_blob,
            manifest_sha256=sha256(manifest_raw),
            validator_blob=validator_blob,
            validator_sha256=sha256(validator_raw),
            terminal_commit=terminal_commit,
            terminal_tree=terminal_tree,
            publication_blob=publication_blob,
            publication_sha256=sha256(publication_raw),
            branch=branch,
        )

    def push_graph(self, graph: Graph) -> None:
        git(
            self.author,
            "push",
            "--force",
            "origin",
            f"{graph.terminal_commit}:refs/heads/{graph.branch}",
        )

    def pins(self, graph: Graph | None = None):
        graph = graph or self.canonical
        return locator.ObjectPins(
            repository="fixture/repo",
            source_branch="source",
            pull_request_number=18,
            source_commit=self.source_commit,
            source_tree=self.source_tree,
            helper_commit=self.helper_commit,
            helper_tree=self.helper_tree,
            helper_parent=self.helper_parent,
            helper_path=HELPER_PATH,
            helper_blob=self.helper_blob,
            payload_commit=graph.payload_commit,
            payload_tree=graph.payload_tree,
            payload_parent=self.helper_commit,
            payload_path=PAYLOAD_ROOT,
            payload_subtree=graph.payload_subtree,
            manifest_path=MANIFEST_PATH,
            manifest_blob=graph.manifest_blob,
            manifest_sha256=graph.manifest_sha256,
            manifest_entries=len(DELIVERY_PATHS),
            terminal_commit=graph.terminal_commit,
            terminal_tree=graph.terminal_tree,
            terminal_parent=graph.payload_commit,
            publication_path=PUBLICATION_PATH,
            publication_blob=graph.publication_blob,
            publication_sha256=graph.publication_sha256,
            validator_path=VALIDATOR_PATH,
            validator_blob=graph.validator_blob,
            validator_sha256=graph.validator_sha256,
            rec_lock_path=REC_LOCK_PATH,
            rec_lock_blob=self.rec_lock_blob,
            blocked_archive_path=BLOCKED_ARCHIVE_PATH,
            blocked_archive_blob=self.blocked_archive_blob,
            blocked_archive_sha256=self.blocked_archive_sha256,
            delivery_paths=DELIVERY_PATHS,
            remote_branch=graph.branch,
        )

    def clone(
        self,
        name: str,
        *,
        branch: str = "continuation",
        blobless: bool = False,
        shallow: bool = False,
    ) -> Path:
        clone = self.root / name
        if blobless:
            git(self.remote, "config", "uploadpack.allowFilter", "true")
        clone_arguments = [
            "clone",
            "--no-local",
            "--single-branch",
            "--branch",
            branch,
        ]
        if blobless:
            clone_arguments.extend(("--filter=blob:none", "--no-checkout"))
        if shallow:
            clone_arguments.append("--depth=1")
        clone_arguments.extend((self.remote.as_uri(), str(clone)))
        git(
            self.root,
            *clone_arguments,
        )
        git(clone, "config", "user.name", "Locator Test")
        git(clone, "config", "user.email", "locator@example.invalid")
        return clone

    def advance_remote_branch(self, branch: str = "continuation") -> str:
        git(self.author, "checkout", "--detach", self.canonical.terminal_commit)
        self._write("remote-drift.txt", b"observational branch drift\n")
        git(self.author, "add", "remote-drift.txt")
        self._commit("advance observational branch")
        drift = self._rev_parse("HEAD")
        git(
            self.author,
            "push",
            "--force",
            "origin",
            f"{drift}:refs/heads/{branch}",
        )
        return drift


class LocatorBehaviorTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="locator-tests-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.fixture = RepositoryFixture(self.root)

    def assert_error(self, code: str, callback) -> locator.LocatorError:
        with self.assertRaises(locator.LocatorError) as caught:
            callback()
        self.assertEqual(code, caught.exception.code)
        return caught.exception

    def run_locator(
        self,
        repo: Path,
        destination: Path,
        *,
        pins=None,
        receipt: Path | None = None,
    ) -> dict[str, str]:
        return locator.fetch_and_validate(
            repo=repo,
            destination=destination,
            receipt=receipt,
            pins=pins or self.fixture.pins(),
            remote="origin",
        )

    def test_success_materializes_raw_bytes_and_runs_validator_exactly_once(self) -> None:
        repo = self.fixture.clone("consumer")
        destination = self.root / "materialized"
        receipt = self.root / "locator-receipt.json"

        result = self.run_locator(repo, destination, receipt=receipt)

        self.assertEqual(EXPECTED_RESULT, result)
        self.assertEqual("1", self.fixture.counter.read_text(encoding="ascii"))
        for path in (*DELIVERY_PATHS, MANIFEST_PATH):
            self.assertEqual(
                git_bytes(
                    repo,
                    "show",
                    f"{self.fixture.canonical.payload_commit}:{path}",
                ),
                (destination / path).read_bytes(),
                path,
            )
            self.assertFalse((destination / path).is_symlink(), path)
        self.assertEqual(
            git_bytes(
                repo,
                "show",
                f"{self.fixture.canonical.terminal_commit}:{PUBLICATION_PATH}",
            ),
            (destination / PUBLICATION_PATH).read_bytes(),
        )
        written_receipt = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertEqual(EXPECTED_RESULT, written_receipt["result"])
        self.assertEqual(sha256(receipt.read_bytes()), result.receipt_sha256)
        verification = locator.verify_receipt_destination(
            destination,
            receipt,
            expected_receipt_sha256=result.receipt_sha256,
            pins=self.fixture.pins(),
        )
        self.assertEqual("PASS_DESTINATION_BINDING", verification["status"])
        self.assertEqual(
            self.fixture.canonical.terminal_commit,
            written_receipt["pins"]["terminal_commit"],
        )

    def test_branch_tip_drift_is_observational_when_pinned_objects_remain(self) -> None:
        repo = self.fixture.clone("consumer")
        drift = self.fixture.advance_remote_branch()
        self.assertNotEqual(drift, self.fixture.canonical.terminal_commit)

        result = self.run_locator(repo, self.root / "materialized")

        self.assertEqual({**EXPECTED_RESULT, "remote_ref_status": "DRIFT"}, result)
        self.assertEqual("1", self.fixture.counter.read_text(encoding="ascii"))

    def test_unavailable_remote_is_observational_when_graph_is_already_local(self) -> None:
        repo = self.fixture.clone("consumer")
        git(
            repo,
            "remote",
            "set-url",
            "origin",
            (self.root / "missing-origin.git").as_uri(),
        )

        result = self.run_locator(repo, self.root / "materialized")

        self.assertEqual({**EXPECTED_RESULT, "remote_ref_status": "NOT_CHECKED"}, result)
        self.assertEqual("1", self.fixture.counter.read_text(encoding="ascii"))

    def test_missing_objects_are_fetched_by_full_sha_without_moving_refs(self) -> None:
        repo = self.fixture.clone("source-only", branch="source")
        absent = git(
            repo,
            "cat-file",
            "-e",
            f"{self.fixture.canonical.terminal_commit}^{{commit}}",
            check=False,
        )
        self.assertNotEqual(0, absent.returncode, "fixture unexpectedly has terminal")
        before = locator.snapshot_repository(repo)

        result = self.run_locator(repo, self.root / "materialized")

        self.assertEqual(EXPECTED_RESULT, result)
        self.assertEqual(before, locator.snapshot_repository(repo))
        git(repo, "cat-file", "-e", f"{self.fixture.canonical.terminal_commit}^{{commit}}")

    def test_missing_graph_with_unavailable_remote_fails_without_repo_mutation(self) -> None:
        repo = self.fixture.clone("source-only", branch="source")
        git(
            repo,
            "remote",
            "set-url",
            "origin",
            (self.root / "missing-origin.git").as_uri(),
        )
        before = locator.snapshot_repository(repo)
        destination = self.root / "materialized"

        self.assert_error(
            "FETCH_UNAVAILABLE",
            lambda: self.run_locator(repo, destination),
        )

        self.assertEqual(before, locator.snapshot_repository(repo))
        self.assertFalse(destination.exists())

    def test_blobless_clone_refetches_unfiltered_reachable_closure(self) -> None:
        repo = self.fixture.clone("blobless", branch="source", blobless=True)
        missing_environment = {
            **os.environ,
            "LC_ALL": "C",
            "LANG": "C",
            "GIT_NO_LAZY_FETCH": "1",
        }
        before_blob = subprocess.run(
            ["git", "cat-file", "-e", self.fixture.canonical.validator_blob],
            cwd=repo,
            env=missing_environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(0, before_blob.returncode, "fixture blob is not missing")
        before = locator.snapshot_repository(repo)

        result = self.run_locator(repo, self.root / "materialized")

        self.assertEqual(EXPECTED_RESULT, result)
        self.assertEqual(before, locator.snapshot_repository(repo))
        after_blob = subprocess.run(
            ["git", "cat-file", "-e", self.fixture.canonical.validator_blob],
            cwd=repo,
            env=missing_environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(0, after_blob.returncode, after_blob.stderr.decode())

    def test_shallow_repository_is_rejected_before_fetch_or_validation(self) -> None:
        repo = self.fixture.clone("shallow", shallow=True)
        self.assertEqual(
            "true",
            git(repo, "rev-parse", "--is-shallow-repository").stdout.strip(),
        )
        destination = self.root / "materialized"

        self.assert_error(
            "REPOSITORY_POLICY",
            lambda: self.run_locator(repo, destination),
        )

        self.assertFalse(destination.exists())
        self.assertFalse(self.fixture.counter.exists())

    def test_ambient_git_repository_and_config_environment_is_ignored(self) -> None:
        repo = self.fixture.clone("requested-repo", branch="source")
        ambient = self.fixture.author
        hostile_environment = {
            "GIT_DIR": str(ambient / ".git"),
            "GIT_WORK_TREE": str(ambient),
            "GIT_COMMON_DIR": str(ambient / ".git"),
            "GIT_OBJECT_DIRECTORY": str(ambient / ".git" / "objects"),
            "GIT_INDEX_FILE": str(ambient / ".git" / "index"),
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "remote.origin.url",
            "GIT_CONFIG_VALUE_0": "file:///definitely-not-the-requested-origin",
        }
        before = locator.snapshot_repository(repo)

        with mock.patch.dict(os.environ, hostile_environment, clear=False):
            self.assertEqual(repo.resolve(), locator._repository_root(repo))
            result = self.run_locator(repo, self.root / "materialized")

        self.assertEqual(EXPECTED_RESULT, result)
        self.assertEqual(before, locator.snapshot_repository(repo))

    def test_short_or_wrong_type_pins_and_wrong_graph_are_rejected(self) -> None:
        repo = self.fixture.clone("consumer")
        pins = self.fixture.pins()
        cases = (
            (
                "short SHA",
                replace(pins, source_commit=pins.source_commit[:7]),
                "INVALID_PIN",
            ),
            (
                "tree supplied where commit is required",
                replace(pins, source_commit=pins.source_tree),
                "OBJECT_MISMATCH",
            ),
            (
                "wrong source tree",
                replace(pins, source_tree=pins.payload_tree),
                "OBJECT_MISMATCH",
            ),
            (
                "wrong helper parent",
                replace(pins, helper_parent=pins.helper_commit),
                "OBJECT_MISMATCH",
            ),
        )
        for label, bad_pins, code in cases:
            with self.subTest(label=label):
                destination = self.root / f"bad-{label.replace(' ', '-')}"
                self.assert_error(
                    code,
                    lambda p=bad_pins, d=destination: self.run_locator(
                        repo, d, pins=p
                    ),
                )
                self.assertFalse(destination.exists())
        self.assertFalse(self.fixture.counter.exists())

    def test_replace_ref_and_dirty_validator_cannot_redirect_execution(self) -> None:
        malicious_marker = self.root / "MALICIOUS_EXECUTED"
        attack = self.fixture.create_variant(
            branch="replace-attack", malicious_marker=malicious_marker
        )
        self.fixture.push_graph(attack)
        repo = self.fixture.clone("consumer")
        git(repo, "fetch", "--no-tags", "origin", "replace-attack")
        git(
            repo,
            "replace",
            self.fixture.canonical.payload_commit,
            attack.payload_commit,
        )
        (repo / VALIDATOR_PATH).write_bytes(
            RepositoryFixture._malicious_validator(malicious_marker)
        )
        before = locator.snapshot_repository(repo)

        result = self.run_locator(repo, self.root / "materialized")

        self.assertEqual(EXPECTED_RESULT, result)
        self.assertEqual(before, locator.snapshot_repository(repo))
        self.assertFalse(malicious_marker.exists())
        self.assertEqual("1", self.fixture.counter.read_text(encoding="ascii"))

    def test_validator_executes_authenticated_bytes_not_a_reopened_path(self) -> None:
        repo = self.fixture.clone("consumer")
        destination = self.root / "materialized"
        marker = self.root / "PATH_RACE_EXECUTED"
        malicious = textwrap.dedent(
            f"""\
            from pathlib import Path
            import json
            Path({str(marker)!r}).write_text("EXECUTED")
            print(json.dumps({locator.EXPECTED_VALIDATOR_RESULT!r}, sort_keys=True))
            """
        ).encode("utf-8")
        real_run = subprocess.run

        def replace_path_at_process_boundary(command, *args, **kwargs):
            if command and command[0] == sys.executable and "-I" in command:
                validator = Path(kwargs["cwd"]) / VALIDATOR_PATH
                authenticated = validator.read_bytes()
                validator.write_bytes(malicious)
                try:
                    return real_run(command, *args, **kwargs)
                finally:
                    validator.write_bytes(authenticated)
            return real_run(command, *args, **kwargs)

        with mock.patch.object(
            locator.subprocess, "run", side_effect=replace_path_at_process_boundary
        ):
            result = self.run_locator(repo, destination)

        self.assertEqual(EXPECTED_RESULT, result)
        self.assertFalse(marker.exists())
        self.assertEqual("1", self.fixture.counter.read_text(encoding="ascii"))
        self.assertEqual(
            self.fixture.canonical.validator_sha256,
            sha256((destination / VALIDATOR_PATH).read_bytes()),
        )

    def test_self_consistent_rehashed_manifest_attack_is_rejected_pre_execution(self) -> None:
        malicious_marker = self.root / "MALICIOUS_EXECUTED"
        attack = self.fixture.create_variant(
            branch="manifest-attack", malicious_marker=malicious_marker
        )
        self.fixture.push_graph(attack)
        repo = self.fixture.clone("consumer", branch="manifest-attack")
        original = self.fixture.canonical
        mixed_pins = replace(
            self.fixture.pins(attack),
            manifest_blob=original.manifest_blob,
            manifest_sha256=original.manifest_sha256,
            validator_blob=original.validator_blob,
            validator_sha256=original.validator_sha256,
        )

        self.assert_error(
            "OBJECT_MISMATCH",
            lambda: self.run_locator(
                repo, self.root / "materialized", pins=mixed_pins
            ),
        )

        self.assertFalse(malicious_marker.exists())
        self.assertFalse(self.fixture.counter.exists())

    def test_authenticated_validator_nonzero_exit_is_fail_closed(self) -> None:
        marker = self.root / "PINNED_VALIDATOR_EXECUTED"
        graph = self.fixture.create_variant(
            branch="validator-nonzero", malicious_marker=marker
        )
        self.fixture.push_graph(graph)
        repo = self.fixture.clone("consumer", branch=graph.branch)
        destination = self.root / "materialized"
        receipt = self.root / "receipt.json"

        self.assert_error(
            "VALIDATOR_FAILURE",
            lambda: self.run_locator(
                repo,
                destination,
                receipt=receipt,
                pins=self.fixture.pins(graph),
            ),
        )

        self.assertTrue(marker.is_file())
        self.assertFalse(destination.exists())
        self.assertFalse(receipt.exists())

    def test_manifest_path_modes_and_symlinks_must_be_safe_regular_blobs(self) -> None:
        variants = (
            {
                "branch": "symlink-attack",
                "symlink_path": f"{PAYLOAD_ROOT}/CODEX_HANDOFF.md",
            },
            {
                "branch": "mode-attack",
                "executable_path": f"{PAYLOAD_ROOT}/CODEX_HANDOFF.md",
            },
            {"branch": "path-attack", "unsafe_manifest": True},
        )
        for number, arguments in enumerate(variants):
            with self.subTest(branch=arguments["branch"]):
                graph = self.fixture.create_variant(**arguments)
                self.fixture.push_graph(graph)
                repo = self.fixture.clone(
                    f"consumer-{number}", branch=graph.branch
                )
                destination = self.root / f"materialized-{number}"
                self.assert_error(
                    "OBJECT_MISMATCH",
                    lambda r=repo, d=destination, g=graph: self.run_locator(
                        r, d, pins=self.fixture.pins(g)
                    ),
                )
                self.assertFalse(destination.exists())
        self.assertFalse(self.fixture.counter.exists())

    def test_publication_receipt_must_semantically_cross_bind_the_graph(self) -> None:
        mismatch = self.fixture.create_variant(
            branch="receipt-mismatch", receipt_mismatch=True
        )
        self.fixture.push_graph(mismatch)
        repo = self.fixture.clone("consumer", branch=mismatch.branch)

        self.assert_error(
            "PUBLICATION_MISMATCH",
            lambda: self.run_locator(
                repo, self.root / "materialized", pins=self.fixture.pins(mismatch)
            ),
        )

        self.assertFalse(self.fixture.counter.exists())

    def test_validator_cannot_add_unmanifested_materialized_files(self) -> None:
        graph = self.fixture.create_variant(
            branch="validator-extra-file", add_unexpected_file=True
        )
        self.fixture.push_graph(graph)
        repo = self.fixture.clone("consumer", branch=graph.branch)
        destination = self.root / "materialized"
        receipt = self.root / "receipt.json"

        error = self.assert_error(
            "VALIDATOR_AUTH_MISMATCH",
            lambda: self.run_locator(
                repo,
                destination,
                receipt=receipt,
                pins=self.fixture.pins(graph),
            ),
        )

        self.assertEqual("1", self.fixture.counter.read_text(encoding="ascii"))
        self.assertFalse(destination.exists())
        self.assertFalse(receipt.exists())
        retained = list(self.root.glob(".materialized.locator-*"))
        self.assertEqual(1, len(retained))
        self.assertEqual(str(retained[0]), error.undeleted_stage_pathname)
        self.assertEqual(0o700, retained[0].stat().st_mode & 0o777)
        self.assertTrue((retained[0] / VALIDATOR_PATH).is_file())

    def test_validator_cannot_add_empty_directories_or_chmod_metadata(self) -> None:
        variants = (
            {"branch": "validator-extra-directory", "add_unexpected_directory": True},
            {"branch": "validator-chmod-metadata", "chmod_metadata": True},
            {"branch": "validator-chmod-root", "chmod_root": True},
        )
        for number, arguments in enumerate(variants):
            with self.subTest(branch=arguments["branch"]):
                graph = self.fixture.create_variant(**arguments)
                self.fixture.push_graph(graph)
                repo = self.fixture.clone(f"consumer-closure-{number}", branch=graph.branch)
                destination = self.root / f"materialized-closure-{number}"
                self.assert_error(
                    "VALIDATOR_AUTH_MISMATCH",
                    lambda r=repo, d=destination, g=graph: self.run_locator(
                        r, d, pins=self.fixture.pins(g)
                    ),
                )
                self.assertFalse(destination.exists())
                retained = list(
                    self.root.glob(f".{destination.name}.locator-*")
                )
                self.assertEqual(1, len(retained))
                self.assertEqual(0o700, retained[0].stat().st_mode & 0o777)

    def test_stage_privacy_restore_failure_is_explicit(self) -> None:
        graph = self.fixture.create_variant(
            branch="validator-chmod-root-restore-failure", chmod_root=True
        )
        self.fixture.push_graph(graph)
        repo = self.fixture.clone("consumer-restore-failure", branch=graph.branch)
        destination = self.root / "materialized-restore-failure"

        with mock.patch.object(
            locator.os,
            "fchmod",
            side_effect=OSError(errno.EROFS, "injected fchmod failure"),
        ):
            error = self.assert_error(
                "STAGE_PRIVACY_FAILURE",
                lambda: self.run_locator(
                    repo,
                    destination,
                    pins=self.fixture.pins(graph),
                ),
            )

        self.assertIsNotNone(error.undeleted_stage_pathname)
        self.assertFalse(destination.exists())

    def test_stage_privacy_failure_dominates_and_reports_repository_drift(self) -> None:
        graph = self.fixture.create_variant(
            branch="validator-chmod-root-with-drift", chmod_root=True
        )
        self.fixture.push_graph(graph)
        repo = self.fixture.clone("consumer-privacy-drift", branch=graph.branch)
        destination = self.root / "materialized-privacy-drift"
        real_snapshot = locator.snapshot_repository
        calls = 0

        def drift_after_initial_snapshot(path: Path):
            nonlocal calls
            calls += 1
            snapshot = real_snapshot(path)
            return snapshot if calls == 1 else replace(
                snapshot, head_commit=b"external-drift\n"
            )

        with (
            mock.patch.object(
                locator.os,
                "fchmod",
                side_effect=OSError(errno.EROFS, "injected fchmod failure"),
            ),
            mock.patch.object(
                locator,
                "snapshot_repository",
                side_effect=drift_after_initial_snapshot,
            ),
        ):
            error = self.assert_error(
                "STAGE_PRIVACY_FAILURE",
                lambda: self.run_locator(
                    repo,
                    destination,
                    pins=self.fixture.pins(graph),
                ),
            )

        self.assertIn("repository also changed", str(error))
        self.assertIsNotNone(error.undeleted_stage_pathname)
        self.assertFalse(destination.exists())

    def test_dangling_destination_and_receipt_symlinks_are_rejected(self) -> None:
        repo = self.fixture.clone("consumer")
        destination = self.root / "materialized"
        destination.symlink_to(self.root / "missing-destination-target", target_is_directory=True)

        self.assert_error(
            "DESTINATION_EXISTS",
            lambda: self.run_locator(repo, destination),
        )
        self.assertTrue(destination.is_symlink())
        self.assertFalse(self.fixture.counter.exists())

        destination.unlink()
        receipt = self.root / "receipt.json"
        receipt.symlink_to(self.root / "missing-receipt-target")
        self.assert_error(
            "RECEIPT_EXISTS",
            lambda: self.run_locator(repo, destination, receipt=receipt),
        )
        self.assertTrue(receipt.is_symlink())
        self.assertFalse(self.fixture.counter.exists())

    def test_atomic_directory_publication_never_replaces_a_racing_owner(self) -> None:
        repo = self.fixture.clone("consumer")
        destination = self.root / "materialized"
        receipt = self.root / "receipt.json"
        published = locator._publish_directory_noreplace
        owner_inode: tuple[int, int] | None = None

        def race(stage: Path, target: Path) -> None:
            nonlocal owner_inode
            target.mkdir()
            owner = target.stat()
            owner_inode = (owner.st_dev, owner.st_ino)
            published(stage, target)

        with mock.patch.object(locator, "_publish_directory_noreplace", side_effect=race):
            self.assert_error(
                "DESTINATION_EXISTS",
                lambda: self.run_locator(repo, destination, receipt=receipt),
            )

        owner = destination.stat()
        self.assertEqual(owner_inode, (owner.st_dev, owner.st_ino))
        self.assertEqual([], list(destination.iterdir()))
        self.assertFalse(receipt.exists())

    def test_substituted_stage_source_never_receives_a_pass_receipt(self) -> None:
        repo = self.fixture.clone("consumer")
        destination = self.root / "materialized"
        displaced = self.root / "authenticated-stage"
        receipt = self.root / "receipt.json"
        published = locator._publish_directory_noreplace

        def substitute(stage: Path, target: Path) -> None:
            stage.rename(displaced)
            stage.mkdir(mode=0o700)
            (stage / "attacker.txt").write_text("not authenticated", encoding="utf-8")
            published(stage, target)

        with mock.patch.object(
            locator, "_publish_directory_noreplace", side_effect=substitute
        ):
            self.assert_error(
                "VALIDATOR_AUTH_MISMATCH",
                lambda: self.run_locator(repo, destination, receipt=receipt),
            )

        self.assertEqual(
            "not authenticated",
            (destination / "attacker.txt").read_text(encoding="utf-8"),
        )
        self.assertTrue((displaced / VALIDATOR_PATH).is_file())
        self.assertFalse(receipt.exists())

    def test_error_retention_never_reports_or_removes_replacement_name(self) -> None:
        repo = self.fixture.clone("consumer")
        destination = self.root / "materialized"
        displaced = self.root / "authenticated-stage"
        real_rehash = locator._rehash_stage
        calls = 0

        def substitute_before_error(stage, graph, pins, identity) -> None:
            nonlocal calls
            calls += 1
            if calls == 2:
                stage.rename(displaced)
                stage.mkdir(mode=0o700)
                (stage / "owner-data.txt").write_text("preserve me", encoding="utf-8")
                raise locator.LocatorError(
                    "VALIDATOR_AUTH_MISMATCH", "injected post-validator failure"
                )
            real_rehash(stage, graph, pins, identity)

        with mock.patch.object(locator, "_rehash_stage", side_effect=substitute_before_error):
            error = self.assert_error(
                "VALIDATOR_AUTH_MISMATCH",
                lambda: self.run_locator(repo, destination),
            )

        owner_files = list(self.root.glob(".materialized.locator-*/owner-data.txt"))
        self.assertEqual(1, len(owner_files))
        self.assertEqual("preserve me", owner_files[0].read_text(encoding="utf-8"))
        self.assertTrue((displaced / VALIDATOR_PATH).is_file())
        self.assertEqual(0o700, displaced.stat().st_mode & 0o777)
        self.assertIsNone(error.undeleted_stage_pathname)
        self.assertEqual(
            "SUBSTITUTED_DO_NOT_REMOVE_REPORTED_NAME", error.stage_path_status
        )
        self.assertEqual(displaced.stat().st_dev, error.retained_stage_identity["device"])
        self.assertEqual(displaced.stat().st_ino, error.retained_stage_identity["inode"])
        self.assertFalse(destination.exists())

    def test_receipt_publication_is_bound_to_an_anonymous_authenticated_inode(self) -> None:
        repo = self.fixture.clone("consumer")
        destination = self.root / "materialized"
        receipt = self.root / "receipt.json"
        displaced = self.root / "authenticated-receipt-temp"
        published = locator._publish_file_noreplace

        def substitute_if_path_backed(source, target: Path, authority) -> None:
            if isinstance(source, Path):
                source.rename(displaced)
                source.write_text('{"attacker":true}\n', encoding="utf-8")
            published(source, target, authority)

        with mock.patch.object(
            locator, "_publish_file_noreplace", side_effect=substitute_if_path_backed
        ):
            result = self.run_locator(repo, destination, receipt=receipt)

        written = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertEqual(EXPECTED_RESULT, result)
        self.assertEqual(EXPECTED_RESULT, written["result"])
        self.assertNotIn("attacker", written)

    def test_receipt_link_uses_capability_free_proc_fd_route(self) -> None:
        self.assertEqual(
            (
                -100,
                b"/proc/self/fd/17",
                23,
                b"receipt.json",
                0x400,
            ),
            locator._receipt_link_arguments(17, 23, "receipt.json"),
        )
        if hasattr(os, "O_NONBLOCK"):
            self.assertTrue(locator._regular_flags() & os.O_NONBLOCK)

    def test_receipt_link_is_the_last_fallible_publication_step(self) -> None:
        repo = self.fixture.clone("consumer")
        destination = self.root / "materialized"
        receipt = self.root / "receipt.json"
        real_open = locator.os.open

        def reject_post_link_target_reopen(path, flags, *args, **kwargs):
            if path == receipt.name and kwargs.get("dir_fd") is not None:
                raise OSError(errno.EIO, "injected post-link target-open failure")
            return real_open(path, flags, *args, **kwargs)

        with mock.patch.object(
            locator.os, "open", side_effect=reject_post_link_target_reopen
        ):
            result = self.run_locator(repo, destination, receipt=receipt)

        self.assertEqual(EXPECTED_RESULT, result)
        self.assertEqual(EXPECTED_RESULT, json.loads(receipt.read_bytes())["result"])

    def test_descriptor_close_failure_after_receipt_link_is_nonsemantic(self) -> None:
        repo = self.fixture.clone("consumer")
        destination = self.root / "materialized"
        receipt = self.root / "receipt.json"
        real_close = locator.os.close

        def fail_close_after_commit(descriptor: int) -> None:
            if receipt.exists():
                raise OSError(errno.EIO, "injected close failure after link")
            real_close(descriptor)

        with mock.patch.object(locator.os, "close", side_effect=fail_close_after_commit):
            result = self.run_locator(repo, destination, receipt=receipt)

        self.assertEqual(EXPECTED_RESULT, result)
        self.assertEqual(sha256(receipt.read_bytes()), result.receipt_sha256)

    def test_bound_destination_must_match_authenticated_expected_closure(self) -> None:
        repo = self.fixture.clone("consumer")
        destination = self.root / "materialized"
        receipt = self.root / "receipt.json"
        bind = locator._bind_destination

        def mutate_then_bind(path, identity, expected_closure):
            target = path / VALIDATOR_PATH
            target.write_bytes(b"X" * target.stat().st_size)
            return bind(path, identity, expected_closure)

        with mock.patch.object(locator, "_bind_destination", side_effect=mutate_then_bind):
            self.assert_error(
                "DESTINATION_BINDING_MISMATCH",
                lambda: self.run_locator(repo, destination, receipt=receipt),
            )

        self.assertFalse(receipt.exists())
        self.assertTrue(destination.is_dir())

    def test_destination_swap_before_receipt_commit_fails_without_receipt(self) -> None:
        repo = self.fixture.clone("consumer")
        destination = self.root / "materialized"
        displaced = self.root / "authenticated-materialized"
        receipt = self.root / "receipt.json"
        published = locator._publish_file_noreplace

        def swap_then_publish(source, target, authority) -> None:
            destination.rename(displaced)
            destination.mkdir()
            (destination / "ATTACK.txt").write_text("replacement", encoding="utf-8")
            published(source, target, authority)

        with mock.patch.object(
            locator, "_publish_file_noreplace", side_effect=swap_then_publish
        ):
            self.assert_error(
                "DESTINATION_BINDING_MISMATCH",
                lambda: self.run_locator(repo, destination, receipt=receipt),
            )

        self.assertFalse(receipt.exists())
        self.assertEqual("replacement", (destination / "ATTACK.txt").read_text())
        self.assertTrue((displaced / VALIDATOR_PATH).is_file())

    def test_receipt_binding_rejects_swap_at_final_link_boundary(self) -> None:
        repo = self.fixture.clone("consumer")
        destination = self.root / "materialized"
        displaced = self.root / "authenticated-materialized"
        receipt = self.root / "receipt.json"
        real_link = locator._link_receipt_fd

        def swap_at_link(source_descriptor, target_parent, target_name):
            destination.rename(displaced)
            destination.mkdir()
            (destination / "ATTACK.txt").write_text("replacement", encoding="utf-8")
            return real_link(source_descriptor, target_parent, target_name)

        with mock.patch.object(locator, "_link_receipt_fd", side_effect=swap_at_link):
            result = self.run_locator(repo, destination, receipt=receipt)

        self.assertEqual(EXPECTED_RESULT, result)
        self.assertTrue(receipt.is_file())
        self.assert_error(
            "DESTINATION_BINDING_MISMATCH",
            lambda: locator.verify_receipt_destination(
                destination,
                receipt,
                expected_receipt_sha256=result.receipt_sha256,
                pins=self.fixture.pins(),
            ),
        )
        binding = json.loads(receipt.read_bytes())["destination_binding"]
        displaced_stat = displaced.stat()
        self.assertEqual(displaced_stat.st_dev, binding["root"]["device"])
        self.assertEqual(displaced_stat.st_ino, binding["root"]["inode"])

    def test_consumer_rejects_post_success_content_and_receipt_mutation(self) -> None:
        repo = self.fixture.clone("consumer")
        destination = self.root / "materialized"
        receipt = self.root / "receipt.json"
        result = self.run_locator(repo, destination, receipt=receipt)
        receipt_raw = receipt.read_bytes()

        payload = destination / VALIDATOR_PATH
        original = payload.read_bytes()
        payload.write_bytes(b"Y" * len(original))
        self.assert_error(
            "DESTINATION_BINDING_MISMATCH",
            lambda: locator.verify_receipt_destination(
                destination,
                receipt,
                expected_receipt_sha256=result.receipt_sha256,
                pins=self.fixture.pins(),
            ),
        )

        payload.write_bytes(original)
        receipt.write_bytes(receipt_raw.replace(b'"files": 15', b'"files": 99'))
        self.assert_error(
            "DESTINATION_BINDING_MISMATCH",
            lambda: locator.verify_receipt_destination(
                destination,
                receipt,
                expected_receipt_sha256=result.receipt_sha256,
                pins=self.fixture.pins(),
            ),
        )

    def test_consumer_rejects_rehashed_forged_receipt_contract_fields(self) -> None:
        repo = self.fixture.clone("consumer")
        destination = self.root / "materialized"
        receipt = self.root / "receipt.json"
        self.run_locator(repo, destination, receipt=receipt)
        original = json.loads(receipt.read_bytes())

        def mutate_schema(document):
            document["schema"] = "attacker/v1"

        def mutate_pins(document):
            document["pins"]["terminal_commit"] = "0" * 40

        def mutate_result(document):
            document["result"]["first_interval"] = "PASS"

        def mutate_validator(document):
            document["validator_result"]["claim"] = "PASS"

        def mutate_atomicity(document):
            document["atomicity"] = "attacker"

        def mutate_binding(document):
            document["destination_binding"]["schema"] = "attacker/v1"

        for label, mutation in (
            ("schema", mutate_schema),
            ("pins", mutate_pins),
            ("result", mutate_result),
            ("validator", mutate_validator),
            ("atomicity", mutate_atomicity),
            ("binding", mutate_binding),
        ):
            with self.subTest(field=label):
                forged = json.loads(json.dumps(original))
                mutation(forged)
                raw = (json.dumps(forged, indent=2, sort_keys=True) + "\n").encode()
                receipt.write_bytes(raw)
                self.assert_error(
                    "DESTINATION_BINDING_MISMATCH",
                    lambda value=raw: locator.verify_receipt_destination(
                        destination,
                        receipt,
                        expected_receipt_sha256=sha256(value),
                        pins=self.fixture.pins(),
                    ),
                )

    def test_repository_drift_is_checked_before_pass_receipt_publication(self) -> None:
        repo = self.fixture.clone("consumer")
        destination = self.root / "materialized"
        receipt = self.root / "receipt.json"
        real_snapshot = locator.snapshot_repository
        calls = 0

        def drift_on_final_pre_receipt_snapshot(path: Path):
            nonlocal calls
            calls += 1
            snapshot = real_snapshot(path)
            if calls == 3:
                return replace(snapshot, head_commit=b"external-drift\n")
            return snapshot

        with mock.patch.object(
            locator,
            "snapshot_repository",
            side_effect=drift_on_final_pre_receipt_snapshot,
        ):
            self.assert_error(
                "REPOSITORY_MUTATED",
                lambda: self.run_locator(repo, destination, receipt=receipt),
            )

        self.assertTrue((destination / VALIDATOR_PATH).is_file())
        self.assertFalse(receipt.exists())

    def test_receipt_race_never_deletes_or_overwrites_replacement_owner_data(self) -> None:
        repo = self.fixture.clone("consumer")
        destination = self.root / "materialized"
        displaced = self.root / "authenticated-materialized"
        receipt = self.root / "receipt.json"
        published = locator._publish_file_noreplace

        def race(temporary, target: Path, authority) -> None:
            destination.rename(displaced)
            destination.mkdir()
            (destination / "owner-data.txt").write_text("preserve me", encoding="utf-8")
            target.write_text("owner receipt", encoding="utf-8")
            published(temporary, target, authority)

        with mock.patch.object(locator, "_publish_file_noreplace", side_effect=race):
            self.assert_error(
                "DESTINATION_BINDING_MISMATCH",
                lambda: self.run_locator(repo, destination, receipt=receipt),
            )

        self.assertEqual(
            "preserve me",
            (destination / "owner-data.txt").read_text(encoding="utf-8"),
        )
        self.assertEqual("owner receipt", receipt.read_text(encoding="utf-8"))
        self.assertTrue((displaced / VALIDATOR_PATH).is_file())

    def test_receipt_link_eexist_race_preserves_owner_and_destination(self) -> None:
        repo = self.fixture.clone("consumer")
        destination = self.root / "materialized"
        receipt = self.root / "receipt.json"
        real_link = locator._link_receipt_fd

        def create_owner_at_link(source_descriptor, target_parent, target_name):
            receipt.write_text("owner receipt", encoding="utf-8")
            return real_link(source_descriptor, target_parent, target_name)

        with mock.patch.object(locator, "_link_receipt_fd", side_effect=create_owner_at_link):
            self.assert_error(
                "RECEIPT_EXISTS",
                lambda: self.run_locator(repo, destination, receipt=receipt),
            )

        self.assertEqual("owner receipt", receipt.read_text(encoding="utf-8"))
        self.assertTrue((destination / VALIDATOR_PATH).is_file())

    def test_existing_destination_is_fail_closed_and_untouched(self) -> None:
        repo = self.fixture.clone("consumer")
        destination = self.root / "materialized"
        destination.mkdir()
        sentinel = destination / "owner-data.txt"
        sentinel.write_text("preserve me", encoding="utf-8")

        self.assert_error(
            "DESTINATION_EXISTS",
            lambda: self.run_locator(repo, destination),
        )

        self.assertEqual("preserve me", sentinel.read_text(encoding="utf-8"))
        self.assertEqual([sentinel], list(destination.iterdir()))
        self.assertFalse(self.fixture.counter.exists())

    def test_cli_main_emits_stable_json_error_and_exit_code(self) -> None:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = locator.main(
                [
                    "--repo",
                    str(self.root / "not-a-repository"),
                    "--destination",
                    str(self.root / "materialized"),
                ]
            )

        payload = json.loads(stderr.getvalue())
        self.assertEqual(locator.EXIT_CODES["REPOSITORY_POLICY"], code)
        self.assertEqual("FAIL", payload["status"])
        self.assertEqual("REPOSITORY_POLICY", payload["code"])

    def test_dirty_untracked_refs_index_head_and_worktrees_are_preserved(self) -> None:
        repo = self.fixture.clone("consumer")
        (repo / "tracked.txt").write_text("dirty working tree\n", encoding="utf-8")
        (repo / "staged.txt").write_text("staged mutation\n", encoding="utf-8")
        git(repo, "add", "staged.txt")
        (repo / "owner-untracked.txt").write_text("preserve\n", encoding="utf-8")
        git(repo, "branch", "owner-local-ref", self.fixture.source_commit)
        extra_worktree = self.root / "owner-extra-worktree"
        git(
            repo,
            "worktree",
            "add",
            "--detach",
            str(extra_worktree),
            self.fixture.source_commit,
        )
        before = locator.snapshot_repository(repo)
        before_status = git(repo, "status", "--porcelain=v2", "--branch").stdout

        result = self.run_locator(repo, self.root / "materialized")

        self.assertEqual(EXPECTED_RESULT, result)
        self.assertEqual(before, locator.snapshot_repository(repo))
        self.assertEqual(
            before_status,
            git(repo, "status", "--porcelain=v2", "--branch").stdout,
        )
        self.assertEqual(
            "preserve\n",
            (repo / "owner-untracked.txt").read_text(encoding="utf-8"),
        )
        self.assertTrue(extra_worktree.is_dir())


if __name__ == "__main__":
    unittest.main()
