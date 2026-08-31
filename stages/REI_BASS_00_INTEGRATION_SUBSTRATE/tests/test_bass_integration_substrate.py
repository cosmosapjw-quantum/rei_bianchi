from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))

import rei_bianchi.bass_integration_substrate as bass_module  # noqa: E402
from rei_bianchi.bass_integration_substrate import (  # noqa: E402
    BassIntegrationError,
    BlobPin,
    CertificateReference,
    GitAuthorityPin,
    GitCustodyReceipt,
    PublicationItem,
    ReferenceEdge,
    build_reference_only_graph,
    publish_event_transaction,
    publish_reference_graph,
    publish_validated_bytes,
    require_exact_bass_rec_pins,
    validate_local_git_authority,
    validate_reference_graph_bytes,
)


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode(
        "ascii"
    )


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={"LANG": "C", "LC_ALL": "C", "PATH": os.defpath},
    )
    return completed.stdout.strip()


def make_repository(parent: Path, project: str) -> tuple[Path, GitAuthorityPin]:
    repo = parent / project.lower()
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "Fixture")
    git(repo, "config", "user.email", "fixture@example.invalid")
    url = f"https://example.invalid/{project.lower()}.git"
    git(repo, "remote", "add", "origin", url)
    source = repo / "authority.txt"
    source.write_text(f"{project} exact authority\n", encoding="utf-8")
    git(repo, "add", "authority.txt")
    git(repo, "commit", "-q", "-m", "authority")
    commit = git(repo, "rev-parse", "HEAD")
    tree = git(repo, "rev-parse", "HEAD^{tree}")
    blob = git(repo, "rev-parse", "HEAD:authority.txt")
    pin = GitAuthorityPin(project, url, commit, tree, (BlobPin("authority.txt", blob),))
    return repo, pin


def fake_receipt(project: str) -> GitCustodyReceipt:
    discriminator = "1" if project == "BASS" else "2"
    pin = GitAuthorityPin(
        project,
        f"https://example.invalid/{project.lower()}.git",
        discriminator * 40,
        ("3" if project == "BASS" else "4") * 40,
        (BlobPin("authority.txt", ("5" if project == "BASS" else "6") * 40),),
    )
    identity = {
        "authority": pin.to_mapping(),
        "common_config_sha256": "7" * 64,
        "worktree_config_sha256": None,
    }
    return GitCustodyReceipt(pin, "7" * 64, None, hashlib.sha256(canonical_json(identity)).hexdigest())


def make_admitted_pair(root: Path):
    bass_repo, bass_pin = make_repository(root, "BASS")
    rec_repo, rec_pin = make_repository(root, "REC")
    return (
        validate_local_git_authority(bass_repo, bass_pin),
        validate_local_git_authority(rec_repo, rec_pin),
    )


def make_graph():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        bass, rec = make_admitted_pair(root)
        refs = (
            CertificateReference(
                "state", "BASS", "state-reference", "application/json", "a" * 64, 12
            ),
            CertificateReference(
                "recombination", "REC", "rate-reference", "application/json", "b" * 64, 9
            ),
        )
        return build_reference_only_graph(
            bass,
            rec,
            refs,
            (ReferenceEdge("state", "recombination", "depends-on"),),
        )


class ExactAuthorityRequirementTests(unittest.TestCase):
    def test_missing_exact_authorities_are_a_typed_blocker(self) -> None:
        with self.assertRaises(BassIntegrationError) as caught:
            require_exact_bass_rec_pins(None, None)
        self.assertEqual(caught.exception.code, "BASS_REC_EXACT_AUTHORITY_MISSING")

    def test_authority_project_order_is_closed(self) -> None:
        bass = fake_receipt("BASS").authority
        rec = fake_receipt("REC").authority
        with self.assertRaises(BassIntegrationError) as caught:
            require_exact_bass_rec_pins(rec, bass)
        self.assertEqual(caught.exception.code, "BASS_REC_EXACT_AUTHORITY_MISMATCH")


class GitCustodyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_exact_local_commit_tree_and_blob_are_accepted(self) -> None:
        repo, pin = make_repository(self.root, "BASS")
        receipt = validate_local_git_authority(repo, pin)
        self.assertEqual(receipt.authority, pin)
        self.assertRegex(receipt.common_config_sha256, r"^[0-9a-f]{64}$")
        self.assertIsNone(receipt.worktree_config_sha256)
        alternates = repo / ".git" / "objects" / "info" / "alternates"
        alternates.write_text("/unsealed/object/store\n", encoding="utf-8")
        with self.assertRaises(BassIntegrationError) as caught:
            validate_local_git_authority(repo, pin)
        self.assertEqual(
            caught.exception.code,
            "BASS_CUSTODY_EXTERNAL_OR_SHALLOW_OBJECTS_FORBIDDEN",
        )

    def test_common_scope_promisor_config_is_rejected_before_object_use(self) -> None:
        repo, pin = make_repository(self.root, "BASS")
        git(repo, "config", "remote.origin.promisor", "true")
        with self.assertRaises(BassIntegrationError) as caught:
            validate_local_git_authority(repo, pin)
        self.assertEqual(caught.exception.code, "BASS_CUSTODY_LAZY_OBJECT_CONFIG_FORBIDDEN")
        self.assertIn("common", caught.exception.detail)

    def test_worktree_scope_promisor_config_is_rejected(self) -> None:
        repo, pin = make_repository(self.root, "BASS")
        git(repo, "config", "extensions.worktreeConfig", "true")
        worktree = self.root / "linked"
        git(repo, "worktree", "add", "-q", "-b", "fixture-worktree", str(worktree))
        git(worktree, "config", "--worktree", "remote.origin.promisor", "true")
        with self.assertRaises(BassIntegrationError) as caught:
            validate_local_git_authority(worktree, pin)
        self.assertEqual(caught.exception.code, "BASS_CUSTODY_LAZY_OBJECT_CONFIG_FORBIDDEN")
        self.assertIn("worktree", caught.exception.detail)

    def test_partial_clone_filter_is_rejected_even_without_promisor_boolean(self) -> None:
        repo, pin = make_repository(self.root, "BASS")
        git(repo, "config", "remote.origin.partialclonefilter", "blob:none")
        with self.assertRaises(BassIntegrationError) as caught:
            validate_local_git_authority(repo, pin)
        self.assertEqual(caught.exception.code, "BASS_CUSTODY_LAZY_OBJECT_CONFIG_FORBIDDEN")

    def test_alternates_inserted_between_exact_reads_are_rejected_as_a_race(self) -> None:
        # Production defect: the initial absence check can pass, then a later
        # path-based Git read can consume a newly inserted alternate store.
        repo, pin = make_repository(self.root, "BASS")
        alternates = repo / ".git" / "objects" / "info" / "alternates"
        real_run_git = bass_module._run_git
        injected = False

        def inject_after_commit_read(repo_path, *args, **kwargs):
            nonlocal injected
            output = real_run_git(repo_path, *args, **kwargs)
            if args[:2] == ("rev-parse", "--verify") and not injected:
                alternates.write_text("/unsealed/object/store\n", encoding="utf-8")
                injected = True
            return output

        with mock.patch(
            "rei_bianchi.bass_integration_substrate._run_git",
            side_effect=inject_after_commit_read,
        ):
            with self.assertRaises(BassIntegrationError) as caught:
                validate_local_git_authority(repo, pin)
        self.assertTrue(injected)
        self.assertEqual(caught.exception.code, "BASS_CUSTODY_VALIDATION_RACE")

    def test_promisor_pack_marker_is_rejected_without_promisor_config(self) -> None:
        # Production defect: a *.promisor marker makes a pack promisor-backed
        # even when every inspected config key is locally complete.
        repo, pin = make_repository(self.root, "BASS")
        marker = repo / ".git" / "objects" / "pack" / "synthetic.promisor"
        marker.write_bytes(b"")
        with self.assertRaises(BassIntegrationError) as caught:
            validate_local_git_authority(repo, pin)
        self.assertEqual(caught.exception.code, "BASS_CUSTODY_PROMISOR_PACK_FORBIDDEN")

    def test_promisor_marker_inserted_between_exact_reads_is_rejected_as_a_race(self) -> None:
        # Production defect: a pack can become promisor-backed after the only
        # preflight check and remain eligible for a later exact-object read.
        repo, pin = make_repository(self.root, "BASS")
        marker = repo / ".git" / "objects" / "pack" / "raced.promisor"
        real_run_git = bass_module._run_git
        injected = False

        def inject_after_tree_read(repo_path, *args, **kwargs):
            nonlocal injected
            output = real_run_git(repo_path, *args, **kwargs)
            if args[:2] == ("show", "-s") and not injected:
                marker.write_bytes(b"")
                injected = True
            return output

        with mock.patch(
            "rei_bianchi.bass_integration_substrate._run_git",
            side_effect=inject_after_tree_read,
        ):
            with self.assertRaises(BassIntegrationError) as caught:
                validate_local_git_authority(repo, pin)
        self.assertTrue(injected)
        self.assertEqual(caught.exception.code, "BASS_CUSTODY_VALIDATION_RACE")

    def test_worktree_origin_url_override_cannot_shadow_the_pinned_common_origin(self) -> None:
        # Production defect: Git's worktree-scoped origin URL can override the
        # pinned common URL while the validator compares only common config.
        repo, pin = make_repository(self.root, "BASS")
        git(repo, "config", "extensions.worktreeConfig", "true")
        worktree = self.root / "linked-origin-override"
        git(repo, "worktree", "add", "-q", "-b", "fixture-origin-override", str(worktree))
        git(worktree, "config", "--worktree", "remote.origin.url", "https://attacker.invalid/bass.git")
        with self.assertRaises(BassIntegrationError) as caught:
            validate_local_git_authority(worktree, pin)
        self.assertEqual(caught.exception.code, "BASS_GIT_AUTHORITY_REMOTE_MISMATCH")
        self.assertIn("worktree", caught.exception.detail)

    def test_config_include_is_rejected_instead_of_hiding_lazy_settings(self) -> None:
        repo, pin = make_repository(self.root, "BASS")
        included = self.root / "included.config"
        included.write_text("[remote \"origin\"]\n\tpromisor = true\n", encoding="utf-8")
        git(repo, "config", "include.path", str(included))
        with self.assertRaises(BassIntegrationError) as caught:
            validate_local_git_authority(repo, pin)
        self.assertEqual(caught.exception.code, "BASS_CUSTODY_CONFIG_INCLUDE_FORBIDDEN")
        git(repo, "config", "--unset-all", "include.path")
        config_path = Path(git(repo, "rev-parse", "--absolute-git-dir")) / "config"
        with config_path.open("a", encoding="utf-8") as handle:
            handle.write(f"\n[includeIf \"gitdir:/unmatched/**\"]\n\tpath = {included}\n")
        with self.assertRaises(BassIntegrationError) as conditional_caught:
            validate_local_git_authority(repo, pin)
        self.assertEqual(
            conditional_caught.exception.code,
            "BASS_CUSTODY_CONFIG_INCLUDE_FORBIDDEN",
        )

    def test_wrong_tree_pin_is_rejected(self) -> None:
        repo, pin = make_repository(self.root, "BASS")
        wrong = GitAuthorityPin(pin.project, pin.repository_url, pin.commit_oid, "0" * 40, pin.blobs)
        with self.assertRaises(BassIntegrationError) as caught:
            validate_local_git_authority(repo, wrong)
        self.assertEqual(caught.exception.code, "BASS_GIT_AUTHORITY_TREE_MISMATCH")

    def test_wrong_blob_pin_is_rejected(self) -> None:
        repo, pin = make_repository(self.root, "BASS")
        wrong = GitAuthorityPin(
            pin.project,
            pin.repository_url,
            pin.commit_oid,
            pin.tree_oid,
            (BlobPin("authority.txt", "0" * 40),),
        )
        with self.assertRaises(BassIntegrationError) as caught:
            validate_local_git_authority(repo, wrong)
        self.assertEqual(caught.exception.code, "BASS_GIT_AUTHORITY_BLOB_MISMATCH")


class ReferenceGraphTests(unittest.TestCase):
    def test_public_self_attested_receipts_cannot_build_a_claim_graph(self) -> None:
        refs = (
            CertificateReference("state", "BASS", "state", "application/json", "a" * 64, 1),
            CertificateReference("rates", "REC", "rates", "application/json", "b" * 64, 1),
        )
        with self.assertRaises(BassIntegrationError) as caught:
            build_reference_only_graph(
                fake_receipt("BASS"),
                fake_receipt("REC"),
                refs,
                (ReferenceEdge("state", "rates", "depends-on"),),
            )
        self.assertEqual(caught.exception.code, "BASS_AUTHORITY_NOT_ADMITTED")

    def test_wire_validation_is_explicitly_non_claim_bearing(self) -> None:
        validation = validate_reference_graph_bytes(make_graph().to_bytes())
        self.assertFalse(getattr(validation, "claim_bearing", True))
        self.assertEqual(
            getattr(validation, "status", None),
            "WIRE_STRUCTURAL_ONLY_NOT_AUTHORITY_ADMISSION",
        )

    def test_claim_admission_requires_external_authorities_and_payload_digest(self) -> None:
        admission_function = getattr(bass_module, "admit_reference_graph_bytes", None)
        self.assertIsNotNone(admission_function)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bass_repo, bass_pin = make_repository(root, "BASS")
            rec_repo, rec_pin = make_repository(root, "REC")
            bass_authority = validate_local_git_authority(bass_repo, bass_pin)
            rec_authority = validate_local_git_authority(rec_repo, rec_pin)
            graph = build_reference_only_graph(
                bass_authority,
                rec_authority,
                (
                    CertificateReference(
                        "state", "BASS", "state", "application/json", "a" * 64, 1
                    ),
                    CertificateReference(
                        "rates", "REC", "rates", "application/json", "b" * 64, 1
                    ),
                ),
                (ReferenceEdge("state", "rates", "depends-on"),),
            )
            payload = graph.to_bytes()
            admission = admission_function(
                payload,
                bass_authority,
                rec_authority,
                hashlib.sha256(payload).hexdigest(),
            )
            self.assertTrue(admission.claim_bearing)
            with self.assertRaises(TypeError):
                type(admission)(graph, hashlib.sha256(payload).hexdigest())
            with self.assertRaises(BassIntegrationError) as caught:
                admission_function(payload, bass_authority, rec_authority, "0" * 64)
            self.assertEqual(caught.exception.code, "BASS_REFERENCE_GRAPH_EXTERNAL_DIGEST_MISMATCH")

    def test_graph_is_deterministic_canonical_and_reference_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            bass, rec = make_admitted_pair(Path(temporary))
            refs = (
                CertificateReference("state", "BASS", "state", "application/json", "a" * 64, 1),
                CertificateReference("rates", "REC", "rates", "application/json", "b" * 64, 1),
            )
            edges = (ReferenceEdge("state", "rates", "depends-on"),)
            graph = build_reference_only_graph(bass, rec, refs, edges)
            replay = build_reference_only_graph(bass, rec, tuple(reversed(refs)), edges)
        parsed = validate_reference_graph_bytes(graph.to_bytes())
        self.assertEqual(parsed["raw_certificate_payloads"], "NOT_ADMITTED")
        self.assertEqual(graph.to_bytes(), replay.to_bytes())

    def test_raw_certificate_payload_key_is_rejected(self) -> None:
        value = make_graph().to_mapping()
        value["certificate_payload"] = "forbidden"
        with self.assertRaises(BassIntegrationError) as caught:
            validate_reference_graph_bytes(canonical_json(value))
        self.assertEqual(caught.exception.code, "BASS_RAW_CERTIFICATE_PAYLOAD_FORBIDDEN")

    def test_graph_digest_mutation_is_rejected(self) -> None:
        value = make_graph().to_mapping()
        value["references"][0]["role"] = "mutated"
        with self.assertRaises(BassIntegrationError) as caught:
            validate_reference_graph_bytes(canonical_json(value))
        self.assertEqual(caught.exception.code, "BASS_REFERENCE_GRAPH_DIGEST_MISMATCH")
        forged = make_graph().to_mapping()
        forged["authorities"][0]["receipt_sha256"] = "0" * 64
        unsigned = dict(forged)
        del unsigned["graph_sha256"]
        forged["graph_sha256"] = hashlib.sha256(canonical_json(unsigned)).hexdigest()
        with self.assertRaises(BassIntegrationError) as forged_caught:
            validate_reference_graph_bytes(canonical_json(forged))
        self.assertEqual(forged_caught.exception.code, "BASS_CUSTODY_RECEIPT_DIGEST_MISMATCH")

    def test_cycle_and_unknown_nodes_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            bass, rec = make_admitted_pair(Path(temporary))
            refs = (
                CertificateReference("a", "BASS", "a", "application/json", "a" * 64, 1),
                CertificateReference("b", "REC", "b", "application/json", "b" * 64, 1),
            )
            with self.subTest("cycle"):
                with self.assertRaises(BassIntegrationError) as caught:
                    build_reference_only_graph(
                        bass,
                        rec,
                        refs,
                        (ReferenceEdge("a", "b", "next"), ReferenceEdge("b", "a", "next")),
                    )
                self.assertEqual(caught.exception.code, "BASS_REFERENCE_GRAPH_INVALID")
            with self.subTest("unknown"):
                with self.assertRaises(BassIntegrationError) as caught:
                    build_reference_only_graph(
                        bass,
                        rec,
                        refs,
                        (ReferenceEdge("a", "missing", "next"),),
                    )
                self.assertEqual(caught.exception.code, "BASS_REFERENCE_GRAPH_INVALID")


class DescriptorPublicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_validated_unnamed_inode_is_published_read_only(self) -> None:
        payload = b"descriptor-bound\n"
        destination = self.root / "receipt.json"
        receipt = publish_validated_bytes(destination, payload, hashlib.sha256(payload).hexdigest())
        self.assertEqual(destination.read_bytes(), payload)
        self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o444)
        self.assertEqual((destination.stat().st_dev, destination.stat().st_ino), (receipt.device, receipt.inode))

    def test_digest_mutation_never_creates_destination(self) -> None:
        destination = self.root / "bad"
        with self.assertRaises(BassIntegrationError) as caught:
            publish_validated_bytes(destination, b"payload", "0" * 64)
        self.assertEqual(caught.exception.code, "BASS_DESCRIPTOR_PUBLICATION_DIGEST_MISMATCH")
        self.assertFalse(destination.exists())

    def test_validator_failure_never_creates_destination(self) -> None:
        destination = self.root / "bad"

        def reject(_: bytes) -> None:
            raise BassIntegrationError("TEST_VALIDATOR_REJECTED", "intentional")

        payload = b"payload"
        with self.assertRaises(BassIntegrationError):
            publish_validated_bytes(
                destination,
                payload,
                hashlib.sha256(payload).hexdigest(),
                validator=reject,
            )
        self.assertFalse(destination.exists())

    def test_existing_destination_is_never_overwritten(self) -> None:
        destination = self.root / "existing"
        destination.write_bytes(b"authority")
        payload = b"new"
        with self.assertRaises(BassIntegrationError) as caught:
            publish_validated_bytes(destination, payload, hashlib.sha256(payload).hexdigest())
        self.assertEqual(caught.exception.code, "BASS_DESCRIPTOR_PUBLICATION_DESTINATION_EXISTS")
        self.assertEqual(destination.read_bytes(), b"authority")

    def test_destination_race_cannot_swap_the_validated_unnamed_inode(self) -> None:
        destination = self.root / "raced"

        def race(_: int) -> None:
            destination.write_bytes(b"attacker")

        payload = b"valid"
        with self.assertRaises(BassIntegrationError) as caught:
            publish_validated_bytes(
                destination,
                payload,
                hashlib.sha256(payload).hexdigest(),
                _after_descriptor_validation=race,
            )
        self.assertEqual(caught.exception.code, "BASS_DESCRIPTOR_PUBLICATION_DESTINATION_EXISTS")
        self.assertEqual(destination.read_bytes(), b"attacker")

    def test_parent_namespace_rename_cannot_forge_the_receipt_destination(self) -> None:
        # Production defect: the inode is linked through the original dirfd,
        # while the lexical receipt path can be replaced with an attacker inode.
        original_parent = self.root / "event"
        original_parent.mkdir()
        moved_parent = self.root / "event-moved"
        destination = original_parent / "receipt"
        payload = b"owned"

        def replace_parent_namespace(_: int) -> None:
            original_parent.rename(moved_parent)
            original_parent.mkdir()
            destination.write_bytes(b"attacker")

        with self.assertRaises(BassIntegrationError) as caught:
            publish_validated_bytes(
                destination,
                payload,
                hashlib.sha256(payload).hexdigest(),
                _after_descriptor_validation=replace_parent_namespace,
            )
        self.assertEqual(caught.exception.code, "BASS_DESCRIPTOR_PUBLICATION_NAMESPACE_CHANGED")
        self.assertEqual(destination.read_bytes(), b"attacker")
        self.assertFalse((moved_parent / "receipt").exists())

    def test_descriptor_is_read_only_before_publication(self) -> None:
        mutation_failures: list[int] = []

        def try_mutation(fd: int) -> None:
            try:
                os.pwrite(fd, b"X", 0)
            except OSError as exc:
                mutation_failures.append(exc.errno)

        payload = b"immutable"
        destination = self.root / "immutable"
        publish_validated_bytes(
            destination,
            payload,
            hashlib.sha256(payload).hexdigest(),
            _after_descriptor_validation=try_mutation,
        )
        self.assertTrue(mutation_failures)
        self.assertEqual(destination.read_bytes(), payload)

    def test_descriptor_mode_mutation_after_validation_is_rejected(self) -> None:
        # Production defect: the test callback can chmod the validated inode
        # after the only mode transition, yielding a writable published file.
        payload = b"mode-closed"
        destination = self.root / "mode-mutated"

        def make_writable(fd: int) -> None:
            os.fchmod(fd, 0o666)

        with self.assertRaises(BassIntegrationError) as caught:
            publish_validated_bytes(
                destination,
                payload,
                hashlib.sha256(payload).hexdigest(),
                _after_descriptor_validation=make_writable,
            )
        self.assertEqual(caught.exception.code, "BASS_DESCRIPTOR_PUBLICATION_INTEGRITY_FAILED")
        self.assertFalse(destination.exists())

    def test_event_failure_rolls_back_only_the_transaction_inode(self) -> None:
        first = self.root / "first"
        second = self.root / "second"
        second.write_bytes(b"preexisting")
        first_payload = b"one"
        second_payload = b"two"
        items = (
            PublicationItem(str(first), first_payload, hashlib.sha256(first_payload).hexdigest()),
            PublicationItem(str(second), second_payload, hashlib.sha256(second_payload).hexdigest()),
        )
        with self.assertRaises(BassIntegrationError):
            publish_event_transaction(items)
        self.assertFalse(first.exists())
        self.assertEqual(second.read_bytes(), b"preexisting")

        fsync_destination = self.root / "fsync-failure"
        fsync_payload = b"durable"
        real_fsync = os.fsync
        failed_directory_sync = False

        def fail_first_directory_sync(fd: int) -> None:
            nonlocal failed_directory_sync
            if stat.S_ISDIR(os.fstat(fd).st_mode) and not failed_directory_sync:
                failed_directory_sync = True
                raise OSError("injected directory fsync failure")
            real_fsync(fd)

        with mock.patch("rei_bianchi.bass_integration_substrate.os.fsync", side_effect=fail_first_directory_sync):
            with self.assertRaises(BassIntegrationError) as caught:
                publish_validated_bytes(
                    fsync_destination,
                    fsync_payload,
                    hashlib.sha256(fsync_payload).hexdigest(),
                )
        self.assertEqual(caught.exception.code, "BASS_DESCRIPTOR_PUBLICATION_FAILED")
        self.assertFalse(fsync_destination.exists())

    def test_event_rollback_keeps_the_original_parent_namespace_after_rename(self) -> None:
        original_parent = self.root / "event"
        original_parent.mkdir()
        moved_parent = self.root / "event-moved"
        first = original_parent / "first"
        second = original_parent / "second"
        first_payload = b"owned-first"
        second_payload = b"owned-second"
        real_publish = publish_validated_bytes
        publish_count = 0

        def publish_then_rename(*args, **kwargs):
            nonlocal publish_count
            result = real_publish(*args, **kwargs)
            publish_count += 1
            if publish_count == 1:
                original_parent.rename(moved_parent)
                original_parent.mkdir()
                (original_parent / "first").write_bytes(b"unrelated-first")
                (original_parent / "second").write_bytes(b"collision")
            return result

        items = (
            PublicationItem(str(first), first_payload, hashlib.sha256(first_payload).hexdigest()),
            PublicationItem(str(second), second_payload, hashlib.sha256(second_payload).hexdigest()),
        )
        with mock.patch(
            "rei_bianchi.bass_integration_substrate.publish_validated_bytes",
            side_effect=publish_then_rename,
        ):
            with self.assertRaises(BassIntegrationError) as caught:
                publish_event_transaction(items)
        self.assertEqual(caught.exception.code, "BASS_DESCRIPTOR_PUBLICATION_NAMESPACE_CHANGED")
        self.assertFalse((moved_parent / "first").exists())
        self.assertEqual((original_parent / "first").read_bytes(), b"unrelated-first")

    def test_event_rejects_split_parent_namespaces_before_second_publication(self) -> None:
        # Production defect: reopening each lexical parent independently lets
        # one transaction succeed across two different directory inodes.
        original_parent = self.root / "event-split"
        original_parent.mkdir()
        moved_parent = self.root / "event-split-moved"
        first = original_parent / "first"
        second = original_parent / "second"
        first_payload = b"owned-first"
        second_payload = b"owned-second"
        real_publish = publish_validated_bytes
        publish_count = 0

        def publish_then_replace_parent(*args, **kwargs):
            nonlocal publish_count
            result = real_publish(*args, **kwargs)
            publish_count += 1
            if publish_count == 1:
                original_parent.rename(moved_parent)
                original_parent.mkdir()
            return result

        items = (
            PublicationItem(str(first), first_payload, hashlib.sha256(first_payload).hexdigest()),
            PublicationItem(str(second), second_payload, hashlib.sha256(second_payload).hexdigest()),
        )
        with mock.patch(
            "rei_bianchi.bass_integration_substrate.publish_validated_bytes",
            side_effect=publish_then_replace_parent,
        ):
            with self.assertRaises(BassIntegrationError) as caught:
                publish_event_transaction(items)
        self.assertEqual(caught.exception.code, "BASS_DESCRIPTOR_PUBLICATION_NAMESPACE_CHANGED")
        self.assertFalse((moved_parent / "first").exists())
        self.assertFalse(second.exists())

    def test_event_rollback_quarantines_a_stat_unlink_race_without_deleting_unrelated_inode(self) -> None:
        event_parent = self.root / "event"
        event_parent.mkdir()
        first = event_parent / "first"
        second = event_parent / "second"
        second.write_bytes(b"collision")
        unrelated = self.root / "unrelated"
        unrelated.write_bytes(b"unrelated")
        first_payload = b"owned-first"
        second_payload = b"owned-second"
        items = (
            PublicationItem(str(first), first_payload, hashlib.sha256(first_payload).hexdigest()),
            PublicationItem(str(second), second_payload, hashlib.sha256(second_payload).hexdigest()),
        )
        real_rename = os.rename
        injected = False

        def swap_before_quarantine(src, dst, *args, **kwargs):
            nonlocal injected
            src_dir_fd = kwargs.get("src_dir_fd")
            dst_dir_fd = kwargs.get("dst_dir_fd")
            if src == "first" and src_dir_fd is not None and dst_dir_fd is not None and not injected:
                injected = True
                real_rename(
                    "first",
                    "owned-stolen",
                    src_dir_fd=src_dir_fd,
                    dst_dir_fd=src_dir_fd,
                )
                os.link(unrelated, "first", dst_dir_fd=src_dir_fd)
            return real_rename(src, dst, *args, **kwargs)

        with mock.patch(
            "rei_bianchi.bass_integration_substrate.os.rename",
            side_effect=swap_before_quarantine,
        ):
            with self.assertRaises(BassIntegrationError) as caught:
                publish_event_transaction(items)
        self.assertEqual(caught.exception.code, "BASS_EVENT_TRANSACTION_ROLLBACK_RACE")
        self.assertTrue(injected)
        self.assertEqual(first.read_bytes(), b"unrelated")
        self.assertEqual(first.stat().st_ino, unrelated.stat().st_ino)

    def test_reference_graph_publication_replays_closed_envelope(self) -> None:
        graph = make_graph()
        destination = self.root / "graph.json"
        receipt = publish_reference_graph(destination, graph)
        self.assertEqual(receipt.sha256, hashlib.sha256(graph.to_bytes()).hexdigest())
        parsed = validate_reference_graph_bytes(destination.read_bytes())
        self.assertEqual(parsed["graph_sha256"], graph.graph_sha256)


if __name__ == "__main__":
    unittest.main()
