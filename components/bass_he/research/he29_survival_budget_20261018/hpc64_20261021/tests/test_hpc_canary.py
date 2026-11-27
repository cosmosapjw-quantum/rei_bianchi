"""New worker-boundary checks; manufactured I/O only, no native or solver run."""
import gzip
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

LANE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LANE / "src"))
import hpc_canary as h

execution_path = LANE.parents[1] / "he28_strip_refinement_20261018/src/execution.py"
spec = importlib.util.spec_from_file_location("he29_canary_test_execution", execution_path)
execution = importlib.util.module_from_spec(spec)
spec.loader.exec_module(execution)


def fixture(directory):
    base = Path(directory)
    packed = base / "packed"
    root = packed / h.HE29_REL
    data_root = base / "DATA"
    (root / "provenance").mkdir(parents=True)
    (root / "src").mkdir()
    (root / "src/reference_runner.py").write_text("fixture source only\n")
    (data_root / "inputs").mkdir(parents=True)
    server = "research/he25_proper_birth_20261016/src/owner_server.rs"
    (packed / server).parent.mkdir(parents=True)
    (packed / server).write_bytes(b"fixture pinned owner source")
    parents = {server: h.digest(packed / server)}
    inputs = {}
    for index in range(22):
        name = f"inputs/fixture_{index:02d}.json"
        (data_root / name).write_text(json.dumps({"fixture": index}))
        inputs[name] = h.digest(data_root / name)
    (root / "provenance/PARENT_SHA256.json").write_text(json.dumps(parents))
    (root / "provenance/INPUT_SHA256.json").write_text(json.dumps(inputs))
    binary = base / "fixture_binary"
    binary.write_bytes(b"not executable; no process may run")
    receipt = base / "OWNER_BUILD.json"
    receipt.write_text(json.dumps({"owner_source": "fixture owner",
        "binary_sha256": h.digest(binary), "server_source_sha256": parents[server]}))
    rr = SimpleNamespace(ROOT=root, REPO=packed, OWNER="fixture owner",
        THREADS={"OMP_NUM_THREADS": "1"}, digest=execution.digest,
        verify_manifest=execution.verify_manifest, manifest=execution.manifest,
        sys=SimpleNamespace(version="fixture python"), np=SimpleNamespace(__version__="fixture numpy"),
        scipy=SimpleNamespace(__version__="fixture scipy"),
        platform=SimpleNamespace(platform=lambda: "fixture platform"))
    args = SimpleNamespace(packed_root=str(packed), baseline_campaign=str(base / "baseline"),
        binary=str(binary), owner_receipt=str(receipt), data_root=str(data_root),
        library=str(base / "library.so"), bridge_receipt=str(base / "BRIDGE_BUILD.json"),
        out=str(base / "output"), table_cache=str(base / "cache"), table_workers=2,
        sync_every=256, source_revision="b" * 40)
    return rr, args


def prepared_fixture():
    return {"current": {"binary_sha256": "fixture_binary"},
        "prior": {"table_sha256": h.TABLE_SHA256,
                  "results": {"Radau": {"fixture": "Radau"}, "DOP853": {"fixture": "DOP853"}}},
        "build": {"fixture": "bridge"}, "reused": {"fixture": "four prior pairs"},
        "packed_publication": {"head": h.PACKED_REVISION},
        "adapter_publication": {"head": "b" * 40},
        "data_provenance": {"data_files_sha_verified": 22}, "new_adapter_sources": {}}


def manufactured_runner(args, events, *, close_failure=False, incomplete=False):
    instances = []
    class Owner:
        def __init__(self, binary, evidence_path, expected_binary_sha256, sync_every):
            self.path, self.calls = Path(evidence_path), 2
            self.closed, self.failed = False, False
            self.sync_every = sync_every
            instances.append(self)
        def __enter__(self):
            events.append("owner_enter")
            return self
        def __exit__(self, kind, value, tb):
            events.append("owner_close")
            self.closed = True
            self.failed = kind is not None or close_failure
            if close_failure:
                raise OSError("manufactured close failure")
            with gzip.open(self.path, "wt") as stream:
                stream.write('{"fixture":"manufactured stream only"}\n')
        def flush_evidence(self, reason):
            trace = self.path.parent / "SEGMENT_ENDPOINTS.jsonl"
            lines = len(trace.read_text().splitlines()) if trace.exists() else 0
            events.append(("flush", reason, lines))
            return self.evidence_telemetry()
        def evidence_telemetry(self):
            return {"records_written": 3, "records_durable": 3, "verified_records": 3,
                "point_records_written": 2, "point_records_durable": 2, "verified_point_records": 2,
                "complete_gzip_readback": self.closed and not incomplete,
                "published": self.closed and not self.failed, "owner_failed": self.failed,
                "trace_error": "manufactured close failure" if close_failure else None,
                "fixture": "manufactured adapter wiring; not native evidence"}
    class Model:
        def __init__(self, owner, grid, **options):
            if options.get("expected_table_sha256") != h.TABLE_SHA256:
                raise AssertionError("production table gate omitted")
            if options.get("cache_dir") != args.table_cache or options.get("max_workers") != args.table_workers:
                raise AssertionError("table budget/cache not forwarded")
            self.source_table_sha256 = h.TABLE_SHA256
            self.source_table_diagnostics = {"fixture": True}
            self.source_table_cache = {"status": "HIT_VERIFIED", "fixture": True}
            self.source_table_execution = {"fixture": True}
            events.append("model")
    def solve(model, bridge, checkpoint):
        events.append("solve")
        checkpoint({"fixture": "first segment", "complete": True})
        checkpoint({"fixture": "second segment", "complete": True})
        return {"fixture": "manufactured solver return"}
    def save(path, value):
        events.append(("save", Path(path).name))
        h.atomic_json(path, value)
    def admit(result, baseline):
        events.append(("admit", baseline["fixture"]))
        return {"fixture": "unchanged admission binding invoked"}
    runner = SimpleNamespace(atomic_json=save, PackedBridge=lambda *args: "fixture bridge",
        GridSpec=lambda **kwargs: kwargs, solve_packed=solve,
        check_result=lambda result: events.append("check_result"), admit_pair=admit)
    return runner, (Model, Owner), instances


class TestHPCCanary(unittest.TestCase):
    def test_external_data_root_keeps_pinned_sources_and_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            rr, args = fixture(directory)
            # An archive-supplied source/manifest cannot replace the Git source.
            (Path(args.data_root) / "src").mkdir()
            (Path(args.data_root) / "src/reference_runner.py").write_text("untrusted data source")
            current, evidence = h.check_sources_external(rr, args.binary, args.owner_receipt, args.data_root)
            self.assertEqual(evidence["data_files_sha_verified"], 22)
            self.assertFalse((rr.ROOT / "inputs").exists())
            self.assertEqual(current["source_files"],
                             {"src/reference_runner.py": h.digest(rr.ROOT / "src/reference_runner.py")})
            self.assertEqual(evidence["manifest_root"], str(rr.ROOT))
            self.assertFalse(evidence["archive_used_as_execution_source"])

    def test_changed_data_binary_or_parent_source_is_rejected(self):
        for kind in ("DATA", "binary", "parent"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                rr, args = fixture(directory)
                target = {"DATA": Path(args.data_root) / "inputs/fixture_00.json",
                          "binary": Path(args.binary),
                          "parent": rr.REPO / "research/he25_proper_birth_20261016/src/owner_server.rs"}[kind]
                target.write_bytes(b"changed actual bytes")
                with self.assertRaises(ValueError):
                    h.check_sources_external(rr, args.binary, args.owner_receipt, args.data_root)

    def test_input_scope_cannot_expand_or_shrink(self):
        with tempfile.TemporaryDirectory() as directory:
            rr, args = fixture(directory)
            path = rr.ROOT / "provenance/INPUT_SHA256.json"
            data = json.loads(path.read_text())
            data.pop(next(iter(data)))
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "INPUT_MANIFEST_SCOPE"):
                h.check_sources_external(rr, args.binary, args.owner_receipt, args.data_root)

    def test_preflight_separates_pins_and_reuses_existing_gates_without_native(self):
        with tempfile.TemporaryDirectory() as directory:
            rr, args = fixture(directory)
            prior = prepared_fixture()["prior"]
            runner = SimpleNamespace(THREADS=rr.THREADS, manifest=execution.manifest,
                baseline_contract=mock.Mock(return_value=(prior, {"runtime_matched_pairs": 4})),
                verify_build=mock.Mock(return_value={"bass_publication_head": h.PACKED_REVISION}),
                publication_contract=mock.Mock(return_value={"head": h.PACKED_REVISION}),
                PackedBridge=mock.Mock(side_effect=AssertionError("native bridge loaded")))
            def checkout(root, revision):
                return {"root": str(root), "head": revision, "clean": True}
            with mock.patch.object(h, "checked_checkout", side_effect=checkout), \
                 mock.patch.object(h, "load_a5", return_value=runner), \
                 mock.patch.dict(sys.modules, {"reference_runner": rr}), \
                 mock.patch.dict(os.environ, {"OMP_NUM_THREADS": "1", "RAYON_NUM_THREADS": "1"}):
                result = h.preflight(args)
            self.assertEqual(result["adapter_publication"]["head"], args.source_revision)
            self.assertEqual(result["packed_publication"]["head"], h.PACKED_REVISION)
            runner.baseline_contract.assert_called_once_with(args.baseline_campaign, result["current"])
            runner.publication_contract.assert_called_once_with(h.PACKED_REVISION,
                                                                result["build"], result["current"])
            runner.PackedBridge.assert_not_called()
            self.assertEqual((result["native_solver_calls"], result["source_tables_built"]), (0, 0))

    def test_preflight_rejects_wrong_saved_table_before_bridge(self):
        with tempfile.TemporaryDirectory() as directory:
            rr, args = fixture(directory)
            runner = SimpleNamespace(THREADS=rr.THREADS,
                baseline_contract=lambda *_: ({"table_sha256": "wrong table"}, {}),
                verify_build=mock.Mock(side_effect=AssertionError("bridge gate reached")))
            with mock.patch.object(h, "checked_checkout", return_value={}), \
                 mock.patch.object(h, "load_a5", return_value=runner), \
                 mock.patch.dict(sys.modules, {"reference_runner": rr}), \
                 mock.patch.dict(os.environ, {"OMP_NUM_THREADS": "1", "RAYON_NUM_THREADS": "1"}):
                with self.assertRaisesRegex(ValueError, "SAVED_TABLE_IDENTITY"):
                    h.preflight(args)
            runner.verify_build.assert_not_called()

    def test_new_revision_and_dirty_checkout_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def query(_, *args):
                return {("rev-parse", "--show-toplevel"): str(root),
                        ("rev-parse", "HEAD"): "a" * 40,
                        ("status", "--porcelain=v1", "--untracked-files=all"): " M changed.py"}[args]
            with mock.patch.object(h, "query", side_effect=query):
                with self.assertRaisesRegex(ValueError, "GIT_REVISION"):
                    h.checked_checkout(root, "b" * 40)
                with self.assertRaisesRegex(ValueError, "CHECKOUT_NOT_CLEAN"):
                    h.checked_checkout(root, "a" * 40)

    def test_worker_barriers_close_readback_and_both_baseline_admissions(self):
        with tempfile.TemporaryDirectory() as directory:
            _, args = fixture(directory)
            events = []
            runner, adapters, owners = manufactured_runner(args, events)
            with mock.patch.object(h, "preflight", return_value=prepared_fixture()), \
                 mock.patch.object(h, "load_a5", return_value=runner), \
                 mock.patch.object(h, "load_adapters", return_value=adapters), \
                 mock.patch.dict(os.environ, {h.WORKER_FLAG: "1"}):
                h.run_case(args)
            self.assertEqual([event for event in events if isinstance(event, tuple) and event[0] == "flush"],
                [("flush", "segment_checkpoint", 0), ("flush", "segment_checkpoint", 1),
                 ("flush", "before_raw_result", 2)])
            self.assertLess(events.index(("flush", "before_raw_result", 2)),
                            events.index(("save", "PACKED_RAW.json")))
            self.assertLess(events.index("owner_close"), events.index(("save", "RESULT.json")))
            self.assertIn(("admit", "Radau"), events)
            self.assertIn(("admit", "DOP853"), events)
            final = json.loads((Path(args.out) / "RESULT.json").read_text())
            self.assertTrue(final["native_evidence"]["complete_gzip_readback"])
            self.assertEqual(final["new_baseline_pairs"], 0)
            self.assertEqual(len(owners), 1)

    def test_incomplete_readback_preserves_raw_and_blocks_result(self):
        with tempfile.TemporaryDirectory() as directory:
            _, args = fixture(directory)
            runner, adapters, _ = manufactured_runner(args, [], incomplete=True)
            with mock.patch.object(h, "preflight", return_value=prepared_fixture()), \
                 mock.patch.object(h, "load_a5", return_value=runner), \
                 mock.patch.object(h, "load_adapters", return_value=adapters), \
                 mock.patch.dict(os.environ, {h.WORKER_FLAG: "1"}):
                with self.assertRaisesRegex(ValueError, "EVIDENCE_NOT_COMPLETE"):
                    h.run_case(args)
            self.assertTrue((Path(args.out) / "PACKED_RAW.json").is_file())
            self.assertTrue((Path(args.out) / "FAILURE.json").is_file())
            self.assertFalse((Path(args.out) / "RESULT.json").exists())

    def test_close_failure_preserves_raw_and_blocks_result(self):
        with tempfile.TemporaryDirectory() as directory:
            _, args = fixture(directory)
            runner, adapters, _ = manufactured_runner(args, [], close_failure=True)
            with mock.patch.object(h, "preflight", return_value=prepared_fixture()), \
                 mock.patch.object(h, "load_a5", return_value=runner), \
                 mock.patch.object(h, "load_adapters", return_value=adapters), \
                 mock.patch.dict(os.environ, {h.WORKER_FLAG: "1"}):
                with self.assertRaisesRegex(OSError, "manufactured close failure"):
                    h.run_case(args)
            self.assertTrue((Path(args.out) / "PACKED_RAW.json").is_file())
            self.assertFalse((Path(args.out) / "RESULT.json").exists())
            failure = json.loads((Path(args.out) / "FAILURE.json").read_text())
            self.assertEqual(failure["native_evidence"]["trace_error"], "manufactured close failure")

    def test_budget_paths_existing_output_and_watchdog_are_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            _, args = fixture(directory)
            for key, value in (("table_workers", 49), ("sync_every", 257),
                               ("out", str(Path(args.data_root) / "bad_output")),
                               ("table_cache", str(Path(args.out) / "bad_cache"))):
                with self.subTest(key=key), mock.patch.object(args, key, value):
                    with self.assertRaises(ValueError):
                        h.validate_options(args)
            with mock.patch.dict(os.environ, {h.WORKER_FLAG: "0"}):
                with self.assertRaisesRegex(ValueError, "PARENT_WATCHDOG"):
                    h.run_case(args)
            Path(args.out).mkdir()
            (Path(args.out) / "preserved").write_bytes(b"existing evidence")
            with mock.patch.object(h, "preflight", side_effect=AssertionError("must not start")), \
                 mock.patch.dict(os.environ, {h.WORKER_FLAG: "1"}):
                with self.assertRaises(FileExistsError):
                    h.run_case(args)
            self.assertEqual((Path(args.out) / "preserved").read_bytes(), b"existing evidence")


if __name__ == "__main__":
    unittest.main()
