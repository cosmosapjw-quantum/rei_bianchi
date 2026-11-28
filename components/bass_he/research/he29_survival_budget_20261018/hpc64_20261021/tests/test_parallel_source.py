"""New cache/parallel boundary tests; no native/physical solver campaign."""
import copy
from dataclasses import asdict
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS", "RAYON_NUM_THREADS"):
    os.environ[variable] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import numpy as np
import parallel_source as p


class ToyModel:
    spec = p.GridSpec(m=4, angles=4, q=0., strips=1)
    source_count = .25
    source_table_nodes = 2
    K = 2
    t_end = 2.
    _cut_bounds = np.array([0., 1., 2.])


def toy():
    model = ToyModel()
    tables = {i: (ts, np.arange(6 * i, 6 * (i + 1), dtype=float).reshape(3, 2))
              for i, ts in p.table_layout(model).items()}
    contract = {"schema": p.CACHE_SCHEMA, "model": {"fixture": "TOY_ONLY"},
                "runtime": {"fixture": "test"}, "sources": {"fixture": "frozen"}}
    return model, tables, contract


class TestParallelSource(unittest.TestCase):
    def test_completion_order_preserves_row_order(self):
        model, wanted, _ = toy()
        got = {i: (ts, np.empty_like(values)) for i, (ts, values) in wanted.items()}
        seen = {i: np.zeros(3, dtype=bool) for i in got}
        tasks = [(i, row, values[row:row + 1], {"row": row}, 42)
                 for i, (_, values) in wanted.items() for row in range(3)]
        for result in reversed(tasks):
            p.install_chunk(got, seen, result)
        self.assertTrue(all(x.all() for x in seen.values()))
        self.assertEqual(p.table_digest(model, got), p.table_digest(model, wanted))
        for i in got:
            self.assertEqual(got[i][1].tobytes(), wanted[i][1].tobytes())

    def test_bad_or_duplicate_chunk_is_rejected(self):
        _, tables, _ = toy()
        seen = {i: np.zeros(3, dtype=bool) for i in tables}
        valid = (0, 0, np.ones((1, 2)), {}, 1)
        p.install_chunk(tables, seen, valid)
        with self.assertRaisesRegex(ValueError, "DUPLICATE"):
            p.install_chunk(tables, seen, valid)
        for result in [(4, 0, np.ones((1, 2)), {}, 1),
                       (0, 2, np.ones((2, 2)), {}, 1),
                       (1, 0, np.full((1, 2), float("nan")), {}, 1),
                       (1, 0, -np.ones((1, 2)), {}, 1),
                       (1, 0, np.ones((1, 2), dtype=np.float32), {}, 1)]:
            with self.subTest(result=result[:2]), self.assertRaises(ValueError):
                p.install_chunk(tables, seen, result)

    def test_original_digest_wire_fixture(self):
        model, tables, _ = toy()
        # Fixed original digest encoding fixture: spec, bounds, count/nodes,
        # ascending interval i8, times f8, C-order values f8, tabulated byte1.
        self.assertEqual(p.table_digest(model, tables),
            "805f384b6eaf83e13fb3315c99d7a2525bf5a03bc8a6b4ae7e00338a1a558e3c")

    def test_cache_roundtrip_is_readonly_and_keeps_last_report(self):
        model, tables, contract = toy()
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            report = {"fixture": "last canonical row", "max_relative_moment_error": 0.}
            manifest = p.publish_cache(folder, contract, model, tables, report, {"native_calls": 0})
            got, restored = p.load_cache(folder, contract, model,
                                         expected_table_sha256=manifest["table_sha256"])
            self.assertEqual(restored["last_source_moments"], report)
            for index in tables:
                self.assertEqual(got[index][1].tobytes(), tables[index][1].tobytes())
                self.assertIsInstance(got[index][1], np.memmap)
                with self.assertRaises(ValueError):
                    got[index][1][0, 0] = 7.
            with self.assertRaises(FileExistsError):
                p.publish_cache(folder, contract, model, tables, report, {})

    def test_tampered_or_symlink_payload_is_rejected(self):
        for mode in ("byte", "symlink"):
            model, tables, contract = toy()
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                folder = Path(directory)
                p.publish_cache(folder, contract, model, tables, {}, {})
                path = folder / "interval_000000_values.npy"
                if mode == "byte":
                    data = path.read_bytes()
                    path.write_bytes(data[:-1] + bytes([data[-1] ^ 1]))
                else:
                    path.rename(folder / "original.npy")
                    path.symlink_to(folder / "original.npy")
                with self.assertRaisesRegex(ValueError, "CACHE_FILE"):
                    p.load_cache(folder, contract, model)

    def test_contract_and_saved_digest_are_required(self):
        model, tables, contract = toy()
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            p.publish_cache(folder, contract, model, tables, {}, {})
            changed = copy.deepcopy(contract)
            changed["runtime"]["fixture"] = "different"
            self.assertNotEqual(p.cache_key(changed), p.cache_key(contract))
            with self.assertRaisesRegex(ValueError, "CACHE_IDENTITY"):
                p.load_cache(folder, changed, model)
            with self.assertRaisesRegex(ValueError, "CACHE_DIGEST"):
                p.load_cache(folder, contract, model, expected_table_sha256="0" * 64)

    def test_incomplete_cache_is_preserved(self):
        model, _, contract = toy()
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / "old-prefix").write_bytes(b"preserve")
            with self.assertRaisesRegex(ValueError, "INCOMPLETE"):
                p.load_cache(folder, contract, model)
            self.assertEqual((folder / "old-prefix").read_bytes(), b"preserve")

    def test_model_cache_hit_does_not_recompute(self):
        report = {"fixture": "synthetic constructor wiring; no physical evidence"}
        def manufactured(model, **_):
            tables = {i: (ts, np.zeros((len(ts), model.K)))
                      for i, ts in p.table_layout(model).items()}
            return tables, report, {"fixture": True, "native_calls": 0}
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.object(p, "construct_tables", side_effect=manufactured) as build:
                first = p.HPC64RefinedSourceModel(None, p.GridSpec(), cache_dir=directory,
                                                 source_table_nodes=256)
                second = p.HPC64RefinedSourceModel(None, p.GridSpec(), cache_dir=directory,
                                                  source_table_nodes=256)
                self.assertEqual(build.call_count, 1)
            self.assertEqual(second.source_table_cache["status"], "HIT_VERIFIED")
            self.assertEqual(first.source_table_sha256, second.source_table_sha256)
            self.assertEqual(second.last_source_moments, report)
            self.assertEqual(second.source_diagnostics, report)
            self.assertTrue(second.tabulated)

    def test_failed_build_keeps_failure_and_cannot_become_cache_hit(self):
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.object(p, "construct_tables", side_effect=RuntimeError("test failed task")):
                with self.assertRaisesRegex(RuntimeError, "test failed task"):
                    p.HPC64RefinedSourceModel(None, p.GridSpec(), cache_dir=directory,
                                             source_table_nodes=256)
            failures = list(Path(directory).glob("*/FAILURE.json"))
            self.assertEqual(len(failures), 1)
            self.assertIn("test failed task", json.loads(failures[0].read_text())["error"])
            with self.assertRaisesRegex(ValueError, "INCOMPLETE"):
                p.HPC64RefinedSourceModel(None, p.GridSpec(), cache_dir=directory,
                                         source_table_nodes=256)

    def test_resource_and_thread_contract_reject_bad_inputs(self):
        model, _, _ = toy()
        for options in ({"max_workers": 0, "chunk_rows": 1, "max_wall_s": 1.},
                        {"max_workers": 65, "chunk_rows": 1, "max_wall_s": 1.},
                        {"max_workers": 1, "chunk_rows": 0, "max_wall_s": 1.},
                        {"max_workers": 1, "chunk_rows": 1, "max_wall_s": float("inf")}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                p.construct_tables(model, **options)
        with mock.patch.dict(os.environ, {"OMP_NUM_THREADS": "2"}):
            with self.assertRaisesRegex(ValueError, "SINGLE_THREAD_ENV"):
                p.require_single_threads()

    def test_initializer_failure_becomes_task_error_without_respawn(self):
        saved_model, saved_error = p._WORKER_MODEL, p._WORKER_ERROR
        try:
            with mock.patch.object(p, "RefinedSourceModel", side_effect=ValueError("bad worker")):
                p.initialize_worker({"spec": asdict(p.GridSpec()), "source_count": .1,
                                     "nodes": 512}, {})
            with self.assertRaisesRegex(RuntimeError, "INITIALIZATION.*bad worker"):
                p.compute_chunk((0, 0, [.5]))
        finally:
            p._WORKER_MODEL, p._WORKER_ERROR = saved_model, saved_error


if __name__ == "__main__":
    unittest.main()
