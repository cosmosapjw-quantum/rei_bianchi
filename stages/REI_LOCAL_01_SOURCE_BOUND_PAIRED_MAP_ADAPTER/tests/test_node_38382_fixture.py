from __future__ import annotations

from dataclasses import replace
import errno
import hashlib
import inspect
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from stages.REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER.analysis.node_38382_fixture import (
    CANONICAL_ENDPOINT_STATE_SHA256,
    FULL_NODE_COUNT,
    NODE_38382_FIXTURE_MISSING,
    FieldSourceAuthority,
    FixtureRole,
    FullFieldReplayResult,
    Node38382Authority,
    Node38382FixtureError,
    TARGET_NODE,
    load_node_38382_fixture,
    load_node_38382_fixture_for_test,
)


class _DynamicParent:
    pass


class _PoisonTrialModule:
    def __init__(self):
        self.touched = False

    @property
    def UncertaintySecondOrderTrial(self):
        self.touched = True
        raise AssertionError("unpinned sys.modules parent consumed")


class _FieldModule:
    def __init__(self):
        self.calls = []

    def make_trial_class(self, repo):
        self.calls.append(Path(repo).resolve())
        return _DynamicParent


class _Predecessor:
    def __init__(
        self,
        *,
        node_count=FULL_NODE_COUNT,
        digest=CANONICAL_ENDPOINT_STATE_SHA256,
        hard_gates_pass=True,
    ):
        self.node_count = node_count
        self.digest = digest
        self.hard_gates_pass = hard_gates_pass
        self.replays = []
        self.predicates = []

    def replay(self, **kwargs):
        self.replays.append(kwargs)
        streams = kwargs["artifact_streams"]
        assert set(streams) == set(FixtureRole)
        assert all(not stream.closed for stream in streams.values())
        return FullFieldReplayResult(
            node_count=self.node_count,
            endpoint_state_sha256=self.digest,
            hard_gates_pass=self.hard_gates_pass,
            opaque={"full": True},
        )

    def predicate_node(self, replay_result, *, node_index):
        self.predicates.append((replay_result, node_index))
        return {"contained": True, "node_index": node_index}


class _MutateRestorePredecessor(_Predecessor):
    def __init__(self, source_path: Path, expected: bytes):
        super().__init__()
        self.source_path = source_path
        self.expected = expected
        self.snapshot_bytes = None
        self.write_errno = None

    def replay(self, **kwargs):
        streams = kwargs["artifact_streams"]
        receipts = kwargs["artifact_receipts"]
        role = FixtureRole.FULL_FIELD_CONTEXT
        self.source_path.write_bytes(b"attacker-mutated-inode")
        try:
            stream = streams[role]
            stream.seek(0)
            self.snapshot_bytes = stream.read()
            try:
                os.pwrite(stream.fileno(), b"x", 0)
            except OSError as exc:
                self.write_errno = exc.errno
            receipt = receipts[role]
            self.asserted_receipt = (
                receipt.sha256,
                receipt.device,
                receipt.inode,
                receipt.seals,
            )
        finally:
            self.source_path.write_bytes(self.expected)
        return super().replay(**kwargs)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_oid(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_field_authority(repo: Path) -> FieldSourceAuthority:
    matches = tuple(
        repo.glob(
            "stages/*AFFINE_SET_PARAMETERIZED_TAYLOR_MODEL_CONTINUOUS_BRANCH_ENCLOSURE_LOCK/analysis/field_trial.py"
        )
    )
    if len(matches) != 1:
        raise AssertionError(matches)
    path = matches[0]
    data = path.read_bytes()
    return FieldSourceAuthority(
        relative_path=path.relative_to(repo).as_posix(),
        sha256=hashlib.sha256(data).hexdigest(),
        git_blob_oid=git_blob_oid(data),
    )


class FixtureTree:
    def __init__(self, root: Path):
        self.root = root
        self.paths = {}
        for role in FixtureRole:
            path = root / f"{role.value}.bin"
            path.write_bytes((role.value + "\n").encode("ascii"))
            self.paths[role] = path
        self.authority = Node38382Authority(
            authority_id="immutable:test-fixture",
            endpoint_state_sha256=CANONICAL_ENDPOINT_STATE_SHA256,
            artifact_sha256={role: sha(path) for role, path in self.paths.items()},
            field_source=FieldSourceAuthority(
                relative_path=(
                    "stages/TEST_AFFINE_SET_PARAMETERIZED_TAYLOR_MODEL_"
                    "CONTINUOUS_BRANCH_ENCLOSURE_LOCK/analysis/field_trial.py"
                ),
                sha256="0" * 64,
                git_blob_oid="0" * 40,
            ),
        )
        self.write_manifest()

    def write_manifest(self, **updates):
        manifest = {
            "schema": "rei-node-38382-fixture/v1",
            "node_count": FULL_NODE_COUNT,
            "target_node": TARGET_NODE,
            "endpoint_state_sha256": CANONICAL_ENDPOINT_STATE_SHA256,
            "artifacts": {
                role.value: {
                    "path": path.name,
                    "sha256": sha(path),
                }
                for role, path in self.paths.items()
            },
        }
        manifest.update(updates)
        (self.root / "MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")


class Node38382FixtureTests(unittest.TestCase):
    def test_absent_actual_fixture_fails_closed(self):
        with TemporaryDirectory() as tmp:
            missing = Path(tmp) / "not-materialized"
            with self.assertRaises(Node38382FixtureError) as caught:
                load_node_38382_fixture(
                    repo_root=Path.cwd(),
                    fixture_root=missing,
                    authority=None,
                )
        self.assertEqual(caught.exception.code, NODE_38382_FIXTURE_MISSING)

    def test_manifest_path_escape_is_rejected(self):
        with TemporaryDirectory() as tmp:
            tree = FixtureTree(Path(tmp))
            manifest = json.loads((tree.root / "MANIFEST.json").read_text())
            manifest["artifacts"][FixtureRole.ENDPOINT.value]["path"] = "../escape"
            (tree.root / "MANIFEST.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(Node38382FixtureError, "NODE_38382_FIXTURE_PATH_INVALID"):
                load_node_38382_fixture_for_test(
                    repo_root=Path.cwd(), fixture_root=tree.root, authority=tree.authority, field_module=_FieldModule()
                )

    def test_manifest_schema_is_closed(self):
        with TemporaryDirectory() as tmp:
            tree = FixtureTree(Path(tmp))
            tree.write_manifest(schema="rei-node-38382-fixture/v2")
            with self.assertRaisesRegex(Node38382FixtureError, "NODE_38382_FIXTURE_SCHEMA_INVALID"):
                load_node_38382_fixture_for_test(
                    repo_root=Path.cwd(), fixture_root=tree.root, authority=tree.authority, field_module=_FieldModule()
                )

    def test_all_full_field_owner_and_reduction_artifacts_are_required(self):
        with TemporaryDirectory() as tmp:
            tree = FixtureTree(Path(tmp))
            manifest = json.loads((tree.root / "MANIFEST.json").read_text())
            del manifest["artifacts"][FixtureRole.REDUCTION_SIDECAR.value]
            (tree.root / "MANIFEST.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(Node38382FixtureError, "NODE_38382_FIXTURE_ROLE_SET_INVALID"):
                load_node_38382_fixture_for_test(
                    repo_root=Path.cwd(), fixture_root=tree.root, authority=tree.authority, field_module=_FieldModule()
                )

    def test_artifact_byte_digest_mismatch_is_rejected(self):
        with TemporaryDirectory() as tmp:
            tree = FixtureTree(Path(tmp))
            tree.paths[FixtureRole.FULL_FIELD_CONTEXT].write_bytes(b"mutated")
            with self.assertRaisesRegex(Node38382FixtureError, "NODE_38382_FIXTURE_DIGEST_MISMATCH"):
                load_node_38382_fixture_for_test(
                    repo_root=Path.cwd(), fixture_root=tree.root, authority=tree.authority, field_module=_FieldModule()
                )
        with TemporaryDirectory() as tmp:
            tree = FixtureTree(Path(tmp))
            fixture = load_node_38382_fixture_for_test(
                repo_root=Path.cwd(),
                fixture_root=tree.root,
                authority=tree.authority,
                field_module=_FieldModule(),
            )
            tree.paths[FixtureRole.FULL_FIELD_CONTEXT].write_bytes(b"post-load mutation")
            with self.assertRaisesRegex(
                Node38382FixtureError, "NODE_38382_FIXTURE_DIGEST_MISMATCH"
            ):
                fixture.replay_and_predicate_for_test(_Predecessor())

    def test_manifest_must_match_external_immutable_authority(self):
        with TemporaryDirectory() as tmp:
            tree = FixtureTree(Path(tmp))
            manifest = json.loads((tree.root / "MANIFEST.json").read_text())
            manifest["artifacts"][FixtureRole.ENDPOINT.value]["sha256"] = "0" * 64
            (tree.root / "MANIFEST.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(Node38382FixtureError, "NODE_38382_FIXTURE_AUTHORITY_MISMATCH"):
                load_node_38382_fixture_for_test(
                    repo_root=Path.cwd(), fixture_root=tree.root, authority=tree.authority, field_module=_FieldModule()
                )

    def test_metadata_requires_full_46080_node_replay_and_target_38382(self):
        with TemporaryDirectory() as tmp:
            tree = FixtureTree(Path(tmp))
            tree.write_manifest(node_count=TARGET_NODE + 1, target_node=TARGET_NODE - 1)
            with self.assertRaisesRegex(Node38382FixtureError, "NODE_38382_FIXTURE_DOMAIN_INVALID"):
                load_node_38382_fixture_for_test(
                    repo_root=Path.cwd(), fixture_root=tree.root, authority=tree.authority, field_module=_FieldModule()
                )

    def test_dynamic_parent_factory_called_once_and_only_target_is_predicated(self):
        with TemporaryDirectory() as tmp:
            tree = FixtureTree(Path(tmp))
            field = _FieldModule()
            fixture = load_node_38382_fixture_for_test(
                repo_root=Path.cwd(), fixture_root=tree.root, authority=tree.authority, field_module=field
            )
            self.assertEqual(len(field.calls), 1)
            self.assertTrue(issubclass(fixture.trial_class, _DynamicParent))
            predecessor = _Predecessor()
            result = fixture.replay_and_predicate_for_test(predecessor)
            self.assertEqual(len(predecessor.replays), 1)
            self.assertEqual(predecessor.replays[0]["node_count"], FULL_NODE_COUNT)
            self.assertEqual([node for _, node in predecessor.predicates], [TARGET_NODE])
            self.assertEqual(result.target_node, TARGET_NODE)
            self.assertEqual(result.replayed_node_count, FULL_NODE_COUNT)

    def test_one_node_slice_or_wrong_endpoint_identity_is_rejected(self):
        with TemporaryDirectory() as tmp:
            tree = FixtureTree(Path(tmp))
            fixture = load_node_38382_fixture_for_test(
                repo_root=Path.cwd(), fixture_root=tree.root, authority=tree.authority, field_module=_FieldModule()
            )
            for predecessor, message in (
                (_Predecessor(node_count=1), "NODE_38382_PREDECESSOR_REPLAY_INCOMPLETE"),
                (_Predecessor(digest="1" * 64), "NODE_38382_ENDPOINT_AUTHORITY_MISMATCH"),
                (_Predecessor(hard_gates_pass=1), "NODE_38382_PREDECESSOR_HARD_GATE_FAILED"),
            ):
                with self.subTest(message=message):
                    with self.assertRaisesRegex(Node38382FixtureError, message):
                        fixture.replay_and_predicate_for_test(predecessor)

    def test_mutate_and_restore_cannot_change_pinned_replay_bytes(self):
        with TemporaryDirectory() as tmp:
            tree = FixtureTree(Path(tmp))
            role = FixtureRole.FULL_FIELD_CONTEXT
            expected = tree.paths[role].read_bytes()
            source_identity = (
                tree.paths[role].stat().st_dev,
                tree.paths[role].stat().st_ino,
            )
            fixture = load_node_38382_fixture_for_test(
                repo_root=Path.cwd(),
                fixture_root=tree.root,
                authority=tree.authority,
                field_module=_FieldModule(),
            )
            predecessor = _MutateRestorePredecessor(tree.paths[role], expected)
            fixture.replay_and_predicate_for_test(predecessor)
            self.assertEqual(predecessor.snapshot_bytes, expected)
            self.assertEqual(predecessor.write_errno, errno.EPERM)
            self.assertEqual(tree.paths[role].read_bytes(), expected)
            self.assertNotEqual(predecessor.asserted_receipt[1:3], source_identity)
            self.assertEqual(predecessor.asserted_receipt[0], hashlib.sha256(expected).hexdigest())

    def test_production_loader_has_no_unpinned_field_injection(self):
        self.assertNotIn("field_module", inspect.signature(load_node_38382_fixture).parameters)
        with TemporaryDirectory() as tmp:
            tree = FixtureTree(Path(tmp))
            with self.assertRaises(TypeError):
                load_node_38382_fixture(
                    repo_root=Path.cwd(),
                    fixture_root=tree.root,
                    authority=tree.authority,
                    field_module=_FieldModule(),
                )

    def test_production_field_source_requires_exact_sha_and_git_blob(self):
        repo = Path.cwd().resolve()
        with TemporaryDirectory() as tmp:
            tree = FixtureTree(Path(tmp))
            exact = canonical_field_authority(repo)
            for wrong in (
                replace(exact, sha256="1" * 64),
                replace(exact, git_blob_oid="1" * 40),
            ):
                authority = replace(tree.authority, field_source=wrong)
                with self.subTest(wrong=wrong):
                    with self.assertRaisesRegex(
                        Node38382FixtureError, "NODE_38382_FIELD_AUTHORITY_MISMATCH"
                    ):
                        load_node_38382_fixture(
                            repo_root=repo,
                            fixture_root=tree.root,
                            authority=authority,
                        )
            with self.assertRaisesRegex(
                Node38382FixtureError, "NODE_38382_FIELD_PARENT_AUTHORITY_MISSING"
            ):
                load_node_38382_fixture(
                    repo_root=repo,
                    fixture_root=tree.root,
                    authority=replace(tree.authority, field_source=exact),
                )

    def test_self_attested_predecessor_cannot_enter_production_success(self):
        with TemporaryDirectory() as tmp:
            tree = FixtureTree(Path(tmp))
            fixture = load_node_38382_fixture_for_test(
                repo_root=Path.cwd(),
                fixture_root=tree.root,
                authority=tree.authority,
                field_module=_FieldModule(),
            )
            liar = _Predecessor(
                node_count=FULL_NODE_COUNT,
                digest=CANONICAL_ENDPOINT_STATE_SHA256,
                hard_gates_pass=True,
            )
            with self.assertRaisesRegex(
                Node38382FixtureError, "NODE_38382_VERIFIED_REPLAY_ABI_MISSING"
            ):
                fixture.replay_and_predicate(liar)
            self.assertEqual(liar.replays, [])
            self.assertEqual(liar.predicates, [])

    def test_production_never_consumes_unpinned_parent_cache_or_glob(self):
        repo = Path.cwd().resolve()
        with TemporaryDirectory() as tmp:
            tree = FixtureTree(Path(tmp))
            authority = replace(
                tree.authority, field_source=canonical_field_authority(repo)
            )
            poison_name = "affine_tm_parent_uncertainty_trial"
            previous = sys.modules.get(poison_name)
            poison = _PoisonTrialModule()
            sys.modules[poison_name] = poison
            try:
                with patch.object(
                    Path,
                    "glob",
                    side_effect=AssertionError("unpinned next(glob) consumed"),
                ):
                    with self.assertRaisesRegex(
                        Node38382FixtureError,
                        "NODE_38382_FIELD_PARENT_AUTHORITY_MISSING",
                    ):
                        load_node_38382_fixture(
                            repo_root=repo,
                            fixture_root=tree.root,
                            authority=authority,
                        )
                self.assertFalse(poison.touched)
            finally:
                if previous is None:
                    sys.modules.pop(poison_name, None)
                else:
                    sys.modules[poison_name] = previous


if __name__ == "__main__":
    unittest.main()
