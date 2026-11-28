"""New I/O policy checks with an actual manufactured stdio process, no physics."""
from __future__ import annotations

import gzip
import importlib.util
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest import mock

import numpy as np

LANE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("he29_batched_native", LANE / "src/batched_native.py")
batched = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(batched)


def make_fake(directory, mode="valid"):
    path = Path(directory) / (mode + ".py")
    source = """#!/usr/bin/env python3
import os,sys
Y_HE = 0.2454 / (4.0 * (1.0 - 0.2454))
mode = MODE
source = SOURCE
if mode == 'bad_start': source = 'wrong_source'
print('HE25_OWNER_V1\\t'+source+'\\t'+format(1e-7,'.17e')+'\\t'+format(1e-7*Y_HE,'.17e'),flush=True)
for i,line in enumerate(sys.stdin,1):
    if mode == 'eof' and i == 4:
        print('manufactured EOF',file=sys.stderr,flush=True)
        os._exit(7)
    if mode == 'error' and i == 4:
        print('manufactured diagnostic',file=sys.stderr,flush=True)
        print('ERROR\\tmanufactured rejection',flush=True)
        continue
    a = float(line.split('\\t')[0])
    values = [1e-7/a**3,(1e-7*Y_HE)/a**3,1e-14,-0.0,-1e-16,3e-17,8.239220060997987]
    values += [i*1e-20 for i in range(1,16)]
    print('POINT\\t'+'\\t'.join(format(x,'.17e') for x in values),flush=True)
""".replace("MODE", repr(mode)).replace("SOURCE", repr(batched.SOURCE_COMMIT))
    path.write_text(source)
    path.chmod(0o755)
    return path


def point(owner, index=0):
    return owner.point((1 / 21, .1, .2)[index % 3],
                       [.1, .01, .001, 3.], [1e-15, 0., 3e-16],
                       [1e-26, 0., 3e-27])


def records(path):
    with gzip.open(path, "rt") as stream:
        return [json.loads(line) for line in stream]


def semantic_events(events):
    return [{k: v for k, v in row.items() if k != "monotonic_ns"} for row in events]


class BatchedNativeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="he29_trace_policy_")
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_original_point_bits_and_all_request_response_records(self):
        binary = make_fake(self.root)
        baseline_path = self.root / "original.gz"
        with batched.OriginalNativeOwner(binary, baseline_path) as original:
            baseline = [point(original, i) for i in range(7)]
        original_records = records(baseline_path)
        for batch in (1, 3, 256):
            with self.subTest(batch=batch):
                path = self.root / (f"batch{batch}.gz")
                with batched.BatchedNativeOwner(binary, path, sync_every=batch) as owner:
                    candidate = [point(owner, i) for i in range(7)]
                for expected, observed in zip(baseline, candidate):
                    self.assertEqual(expected.keys(), observed.keys())
                    for name in expected:
                        self.assertEqual(np.asarray(expected[name], dtype=np.float64).tobytes(),
                                         np.asarray(observed[name], dtype=np.float64).tobytes(), name)
                self.assertEqual(semantic_events(original_records), semantic_events(records(path)))
                t = owner.evidence_telemetry()
                self.assertEqual((t["records_written"], t["records_durable"], t["verified_records"]), (8, 8, 8))
                self.assertEqual(t["point_records_written"], 7)
                self.assertTrue(t["complete_gzip_readback"] and t["published"])
                self.assertFalse(owner.failed)

    def test_batch_boundary_and_explicit_segment_barrier(self):
        with batched.BatchedNativeOwner(make_fake(self.root), self.root / "barrier.gz", sync_every=3) as owner:
            self.assertEqual(owner.evidence_telemetry()["fsync_successes"], 1)
            point(owner); point(owner)
            t = owner.evidence_telemetry()
            self.assertEqual((t["point_records_written"], t["point_records_durable"]), (2, 0))
            point(owner)
            self.assertEqual(owner.evidence_telemetry()["point_records_durable"], 3)
            point(owner)
            t = owner.flush_evidence("segment_checkpoint")
            self.assertEqual((t["point_records_written"], t["point_records_durable"]), (4, 4))
            self.assertEqual(t["fsync_successes"], 3)
            self.assertEqual(t["hardkill_unsynchronized_successful_point_bound"], 2)

    def test_error_and_eof_flush_prior_points_and_keep_partial(self):
        for mode in ("error", "eof"):
            with self.subTest(mode=mode):
                path = self.root / (mode + ".gz")
                owner = batched.BatchedNativeOwner(make_fake(self.root, mode), path, sync_every=256)
                with self.assertRaisesRegex(RuntimeError, "HE25_OWNER_(ERROR|EOF)"):
                    with owner:
                        for _ in range(4):
                            point(owner)
                self.assertFalse(path.exists())
                observed = records(Path(str(path) + ".partial"))
                self.assertEqual(observed[0]["kind"], "handshake")
                self.assertEqual(sum(r["kind"] == "point" for r in observed), 4 if mode == "error" else 3)
                failures = [r for r in observed if r["kind"] == "failure"]
                self.assertEqual(len(failures), 1)
                self.assertTrue(failures[0]["request"])
                self.assertIn("manufactured", failures[0]["stderr"])
                self.assertTrue(owner.evidence_telemetry()["complete_gzip_readback"])
                self.assertEqual(owner.evidence_telemetry()["records_durable"], len(observed))
                self.assertTrue(owner.failed)

    def test_unchanged_handshake_and_input_validation(self):
        path = self.root / "bad.gz"
        with self.assertRaisesRegex(ValueError, "HE25_OWNER_HANDSHAKE_OR_SOURCE"):
            with batched.BatchedNativeOwner(make_fake(self.root, "bad_start"), path):
                self.fail("bad source accepted")
        self.assertEqual([r["kind"] for r in records(Path(str(path) + ".partial"))],
                         ["handshake", "failure"])
        with batched.BatchedNativeOwner(make_fake(self.root), self.root / "inputs.gz") as owner:
            with self.assertRaisesRegex(ValueError, "HE25_POINT_NEGATIVE_PHOTO"):
                owner.point(.1, [.1]*4, [-1., 0., 0.], [0.]*3)
            self.assertEqual(owner.calls, 0)

    def test_occupied_final_partial_or_symlink_prevents_process_start(self):
        binary = make_fake(self.root)
        for kind in ("final", "partial", "symlink"):
            with self.subTest(kind=kind):
                path = self.root / (kind + ".gz")
                target = Path(str(path) + ".partial") if kind == "partial" else path
                if kind == "symlink":
                    target.symlink_to(self.root / "absent")
                else:
                    target.write_bytes(b"existing-evidence")
                with mock.patch.object(batched._native.subprocess, "Popen", side_effect=AssertionError("started")):
                    with self.assertRaises(FileExistsError):
                        with batched.BatchedNativeOwner(binary, path):
                            pass
                if kind != "symlink":
                    self.assertEqual(target.read_bytes(), b"existing-evidence")

    def test_point_or_checkpoint_fsync_failure_is_sticky_and_not_published(self):
        binary = make_fake(self.root)
        real_fsync = os.fsync
        for phase in ("point", "checkpoint"):
            with self.subTest(phase=phase):
                path = self.root / (phase + ".gz")
                owner = batched.BatchedNativeOwner(binary, path, sync_every=1 if phase == "point" else 256)
                seen = 0
                def fail_once(fd):
                    nonlocal seen
                    seen += 1
                    if seen == 1:
                        raise OSError("manufactured fsync failure")
                    return real_fsync(fd)
                with self.assertRaisesRegex(OSError, "manufactured fsync failure"):
                    with owner:
                        with mock.patch.object(os, "fsync", side_effect=fail_once):
                            point(owner)
                            owner.flush_evidence("before_result")
                self.assertTrue(owner.failed)
                self.assertFalse(path.exists())
                self.assertTrue(Path(str(path) + ".partial").exists())
                self.assertIsNotNone(owner.evidence_telemetry()["trace_error"])
                with self.assertRaises(OSError):
                    owner.flush_evidence("must_not_admit")

    def test_startup_sync_failure_closes_actual_fake_process(self):
        owner = batched.BatchedNativeOwner(make_fake(self.root), self.root / "startup.gz")
        processes = []
        real_popen = batched._native.subprocess.Popen
        real_fsync = os.fsync
        calls = 0
        def capture(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            processes.append(process)
            return process
        def fail_once(fd):
            nonlocal calls
            calls += 1
            if calls == 1:
                raise OSError("startup sync failure")
            return real_fsync(fd)
        with mock.patch.object(batched._native.subprocess, "Popen", side_effect=capture), \
             mock.patch.object(os, "fsync", side_effect=fail_once):
            with self.assertRaisesRegex(OSError, "startup sync failure"):
                with owner:
                    self.fail("startup admitted")
        self.assertEqual(len(processes), 1)
        self.assertIsNotNone(processes[0].poll())
        self.assertIsNone(owner._process)
        self.assertFalse((self.root / "startup.gz").exists())

    def test_complete_gzip_corruption_blocks_create_only_publication(self):
        path = self.root / "corrupt.gz"
        owner = batched.BatchedNativeOwner(make_fake(self.root), path)
        readback = owner._read_complete_trace
        def corrupt_then_read():
            data = owner._partial.read_bytes()
            owner._partial.write_bytes(data[:-4])
            return readback()
        with mock.patch.object(owner, "_read_complete_trace", side_effect=corrupt_then_read):
            with self.assertRaises(EOFError):
                with owner:
                    point(owner)
        self.assertFalse(path.exists())
        self.assertTrue(owner._partial.exists())
        self.assertFalse(owner.evidence_telemetry()["complete_gzip_readback"])

    def test_publication_race_preserves_existing_final_and_new_partial(self):
        path = self.root / "race.gz"
        owner = batched.BatchedNativeOwner(make_fake(self.root), path)
        real_link = os.link
        def competing_link(src, dst):
            Path(dst).write_bytes(b"other-owner-output")
            return real_link(src, dst)
        with mock.patch.object(os, "link", side_effect=competing_link):
            with self.assertRaises(FileExistsError):
                with owner:
                    point(owner)
        self.assertEqual(path.read_bytes(), b"other-owner-output")
        self.assertEqual(len(records(owner._partial)), 2)
        self.assertFalse(owner.evidence_telemetry()["published"])

    def test_directory_sync_failure_propagates_even_after_file_link(self):
        path = self.root / "directory.gz"
        real_fsync = os.fsync
        def fail_directory(fd):
            if stat.S_ISDIR(os.fstat(fd).st_mode):
                raise OSError("directory sync failure")
            return real_fsync(fd)
        owner = batched.BatchedNativeOwner(make_fake(self.root), path)
        with mock.patch.object(os, "fsync", side_effect=fail_directory):
            with self.assertRaisesRegex(OSError, "directory sync failure"):
                with owner:
                    point(owner)
        self.assertTrue(owner.failed)
        self.assertTrue(path.exists())  # Created file is retained; no science RESULT is admitted.
        self.assertIsNotNone(owner.evidence_telemetry()["trace_error"])

    def test_invalid_batch_sizes_fail_before_process_or_evidence_creation(self):
        binary = make_fake(self.root)
        for value in (0, -1, True, 2.5, "256"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "POSITIVE_INTEGER"):
                batched.BatchedNativeOwner(binary, self.root / "invalid.gz", sync_every=value)
        self.assertFalse((self.root / "invalid.gz").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
