"""Manufactured persistence tests; no private checkpoint or native runtime."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

HERE = Path(__file__).resolve().parent
HPC = HERE.parent
Q1B = HPC.parent
for directory in (HPC, Q1B / "c11/restart", Q1B / "c11/controller",
                  Q1B / "c10", Q1B / "checkpoint", Q1B / "c11/integration/production"):
    sys.path.insert(0, str(directory))

from adaptive_checkpoint import make_adaptive_snapshot, validate_adaptive_snapshot
from atomic_checkpoint import load_generation, publish_generation
from entry_checkpoint import COUNTERS
from production_journal import AttemptJournal, sha as journal_sha
from segmented_checkpoint import SegmentedCheckpointError, SegmentedStore, sha


class SegmentedTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.legacy = self.root / "legacy"
        self.directory = self.root / "segments"
        self.shape = (1, 2)
        self.controls = dict(schema="rei.q1b.c11.adaptive_controls.v1", method_order=1,
            physical_state_floor=False, scientific_normalization_changed=False,
            local_defect_target=1e-7, safety=.8, min_shrink=.2, max_growth=2.,
            min_step_s=.01, max_step_s=100., initial_step_s=2.,
            max_attempts=20, max_accepted_macros=20,
            observable_scales={"xHII": 1.}, distribution_scales={})
        states = [self.state(float(i)) for i in range(3)]
        self.cursor = self.make_cursor(1, 2.)
        arrays, metadata = make_adaptive_snapshot(states=states, controls=self.controls,
            cursor=self.cursor, end_time_s=100., hard_events=[], scales=np.ones(15),
            dependency_closure={})
        metadata["production_output_records"] = [dict(epoch_index=0, time_s=0., label="seed")]
        metadata["production_kernel_history"] = {str(i): {"gamma": [float(i)]} for i in range(3)}
        metadata["production_transition"] = {"preserved": True}
        identity = dict(source="1" * 64, grid="2" * 64, binary="3" * 64,
                        control=metadata["restart_binding_sha256"], physics_contract="4" * 64,
                        physical_validator=sha(Q1B / "c11/restart/adaptive_checkpoint.py"))
        path = publish_generation(self.legacy, 1, arrays, metadata, identity, validate_adaptive_snapshot)
        self.loaded = load_generation(self.legacy, 1, identity, validate_adaptive_snapshot)
        self.legacy_ref = dict(generation=1, manifest_sha256=sha(path / "manifest.json"))
        self.binding = dict(schema="manufactured.hpc.runtime.v1", max_attempts=20,
                            execution="single_coordinator")
        self.store = SegmentedStore(self.directory)
        self.reference = self.store.initialize(self.legacy, self.legacy_ref, self.loaded,
                                               shape=self.shape, runtime_binding=self.binding)

    @staticmethod
    def make_cursor(generation, clock, *, rejections=0):
        return dict(schema="rei.q1b.c11.adaptive_cursor.v1", next_step_s=2.,
                    attempts=generation + rejections, accepted_macros=generation,
                    rejected_macros=rejections, accepted_boundaries=2 * generation,
                    accepted_clock_s=clock)

    def state(self, clock):
        return dict(t_s=clock, gas=np.array([.1, .1, .1, 1.]),
                    N=np.array([[.2, .3]]), U_eV=np.array([[.4, .6]]),
                    R=np.ones(self.shape), support=np.array([[[1., 3.], [1., 3.]]]),
                    counters=dict.fromkeys(COUNTERS, 0.), nH_ref=1., nHe_ref=.1,
                    diagnostics={"gamma": [clock], "native_rows": {"integer": 1}})

    def append(self, *, store=None, generation=2, rejections=0, begin_hash="a" * 64):
        store = store or self.store
        cursor = self.make_cursor(generation, float(2 * generation), rejections=rejections)
        trial = dict(accepted=True, error_ratio=.5)
        records = [dict(epoch_index=generation - 1, time_s=float(2 * generation), label="new")]
        transaction = dict(attempt=cursor["attempts"], begin_sha256=begin_hash,
                           trial=trial, output_records=records)
        pair = [self.state(float(2 * generation - 1)), self.state(float(2 * generation))]
        return store.commit(pair, cursor, trial, transaction, records)

    def test_round_trip_preserves_states_metadata_and_original_binding(self):
        reference = self.append()
        reopened = SegmentedStore(self.directory).load(reference)
        self.assertEqual(reopened["cursor"], self.make_cursor(2, 4.))
        self.assertEqual(reopened["metadata"]["segmented_prefix_count"], 5)
        self.assertEqual(reopened["metadata"]["restart_binding"], self.loaded["metadata"]["restart_binding"])
        self.assertEqual(reopened["metadata"]["hpc_runtime_binding"], self.binding)
        self.assertEqual(reopened["metadata"]["production_transition"], {"preserved": True})
        for key in ("gas", "N", "U_eV", "R", "support"):
            self.assertEqual(reopened["state"][key].tobytes(), self.state(4.)[key].tobytes())
        self.assertEqual(reopened["initial_state"]["t_s"], 0.)
        self.assertEqual(reopened["state"]["diagnostics"], self.state(4.)["diagnostics"])
        self.assertFalse(reopened["metadata"]["scientific_admission"])

    def test_two_new_rows_per_generation_and_one_demand_export(self):
        first = self.append()
        second = self.append(generation=3)
        for number in (2, 3):
            with np.load(self.directory / f"gen-{number:08d}/arrays.npz", allow_pickle=False) as arrays:
                self.assertEqual(arrays["packed"].shape, (2, 15))
        manifest = json.loads((self.directory / "gen-00000003/manifest.json").read_text())
        self.assertEqual(manifest["previous_checkpoint"], first)
        states = list(self.store.iter_states())
        self.assertEqual([s["t_s"] for s in states], list(map(float, range(7))))
        exported = self.store.export_legacy_snapshot()
        self.assertEqual(exported["arrays"]["prefix_clock"].tolist(), list(map(float, range(7))))
        self.assertEqual(exported["arrays"]["prefix_state"].shape, (7, 15))
        self.assertEqual(exported["metadata"]["adaptive_cursor"], self.make_cursor(3, 6.))
        self.assertEqual(exported["metadata"]["production_output_records"][-1]["epoch_index"], 2)
        self.assertEqual(exported["metadata"]["exported_segmented_checkpoint"], second)
        self.assertTrue(validate_adaptive_snapshot(exported["arrays"], exported["metadata"])["ledgers_checked"])

    def test_resume_does_not_read_old_large_payloads(self):
        self.append()
        reference = self.append(generation=3)
        import segmented_checkpoint as module
        real_sha = module.sha
        visited = []
        def recording_sha(path):
            visited.append(Path(path))
            return real_sha(path)
        with patch.object(module, "sha", side_effect=recording_sha):
            result = SegmentedStore(self.directory).load(reference)
        self.assertEqual(result["cursor"]["accepted_macros"], 3)
        self.assertNotIn(self.directory / "gen-00000002/arrays.npz", visited)
        self.assertNotIn(self.legacy / "gen-00000001/arrays.npz", visited)
        self.assertIn(self.directory / "gen-00000003/arrays.npz", visited)

    def test_gap_and_missing_member_fail_closed(self):
        self.append()
        self.append(generation=3)
        shutil.rmtree(self.directory / "gen-00000002")
        with self.assertRaisesRegex(SegmentedCheckpointError, "SEQUENCE_GAP"):
            SegmentedStore(self.directory).load_latest()

    def test_tampered_final_payload_fails_closed(self):
        reference = self.append()
        path = self.directory / "gen-00000002/arrays.npz"
        original = path.read_bytes()
        path.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
        with self.assertRaisesRegex(SegmentedCheckpointError, "CORRUPT_MEMBER"):
            SegmentedStore(self.directory).load(reference)

    def test_old_payload_checked_when_explicitly_read(self):
        self.append()
        reference = self.append(generation=3)
        path = self.directory / "gen-00000002/arrays.npz"
        original = path.read_bytes()
        path.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
        # Fast restart advertises selective scope, not a historical byte audit.
        self.assertEqual(SegmentedStore(self.directory).load(reference)["cursor"]["accepted_macros"], 3)
        with self.assertRaisesRegex(SegmentedCheckpointError, "CORRUPT_MEMBER"):
            SegmentedStore(self.directory).verify_history()

    def test_orphan_temporary_preserved_and_blocks_use(self):
        orphan = self.directory / ".tmp-gen-00000002-interrupted"
        orphan.mkdir()
        (orphan / "arrays.npz").write_bytes(b"partial")
        with self.assertRaisesRegex(SegmentedCheckpointError, "ORPHAN_TEMP"):
            self.store.load_latest()
        self.assertTrue(orphan.exists())

    def test_failed_publication_has_no_accepted_generation(self):
        with patch("segmented_checkpoint._rename_no_replace", side_effect=OSError("injected fsync/rename failure")):
            with self.assertRaisesRegex(OSError, "injected"):
                self.append()
        self.assertFalse((self.directory / "gen-00000002").exists())
        self.assertTrue(list(self.directory.glob(".tmp-gen-00000002-*")))
        with self.assertRaisesRegex(SegmentedCheckpointError, "ORPHAN_TEMP"):
            SegmentedStore(self.directory).load_latest()

    def test_lost_journal_commit_reconciles_saved_acceptance_without_replay(self):
        journal = AttemptJournal(self.root / "journal", self.cursor, self.reference)
        number = journal.begin({"manufactured": True})
        digest = journal_sha(journal._path(number, "begin"))
        reference = self.append(begin_hash=digest)
        resumed_store = SegmentedStore(self.directory)
        resumed_journal = AttemptJournal(self.root / "journal", self.cursor, self.reference)
        def reconcile(begin):
            return resumed_store.reconcile(begin, journal_sha(resumed_journal._path(begin["attempt"], "begin")))
        resumed = resumed_journal.resume(reconcile)
        self.assertEqual(resumed["checkpoint"], reference)
        self.assertEqual(resumed["cursor"]["attempts"], 2)
        row = json.loads(resumed_journal._path(number, "commit").read_text())
        self.assertTrue(row["reconciled_from_atomic_checkpoint"])

    def test_unpublished_trial_is_not_replayed(self):
        begin = dict(attempt=2, cursor=self.cursor, checkpoint=self.reference)
        self.assertIsNone(self.store.reconcile(begin, "a" * 64))
        self.assertEqual(self.store.load_latest()["checkpoint"], self.reference)

    def test_rejected_attempts_do_not_add_boundaries(self):
        self.append(rejections=3)
        result = self.store.load_latest()
        self.assertEqual(result["cursor"]["attempts"], 5)
        self.assertEqual(result["cursor"]["accepted_boundaries"], 4)
        self.assertEqual(len(list(self.store.iter_states())), 5)

    def test_mismatched_transaction_or_bad_ledger_cannot_publish(self):
        cursor = self.make_cursor(2, 4.)
        trial = dict(accepted=True)
        transaction = dict(attempt=2, begin_sha256="a" * 64, trial=trial, output_records=[])
        pair = [self.state(3.), self.state(4.)]
        pair[-1]["U_eV"][0, 0] += .1
        with self.assertRaisesRegex(ValueError, "ledger exceeds"):
            self.store.commit(pair, cursor, trial, transaction, [])
        self.assertFalse((self.directory / "gen-00000002").exists())
        transaction["attempt"] = 5
        with self.assertRaisesRegex(SegmentedCheckpointError, "TRANSACTION"):
            self.store.commit([self.state(3.), self.state(4.)], cursor, trial, transaction, [])

    def test_initialization_is_idempotent_but_runtime_binding_drift_is_not(self):
        self.assertEqual(self.store.initialize(self.legacy, self.legacy_ref, self.loaded,
                         shape=self.shape, runtime_binding=self.binding), self.reference)
        changed = dict(self.binding, max_attempts=99)
        with self.assertRaisesRegex(SegmentedCheckpointError, "REINITIALIZATION_DRIFT"):
            self.store.initialize(self.legacy, self.legacy_ref, self.loaded,
                                  shape=self.shape, runtime_binding=changed)

    def test_legacy_relocation_and_manifest_identity(self):
        reference = self.append()
        moved = self.root / "moved-legacy"
        shutil.move(str(self.legacy), moved)
        relocated = SegmentedStore(self.directory, legacy_directory=moved)
        self.assertEqual(relocated.load(reference)["state"]["t_s"], 4.)
        self.assertEqual(len(list(relocated.iter_states(reference))), 5)
        path = moved / "gen-00000001/manifest.json"
        path.write_text(path.read_text() + " ")
        with self.assertRaisesRegex(SegmentedCheckpointError, "LEGACY_SEED_MANIFEST_HASH"):
            list(relocated.iter_states(reference))


if __name__ == "__main__":
    unittest.main()
