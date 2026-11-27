"""Independent Python FFI/admission checks, with manufactured data only.

The fake native callable exercises real ctypes callback objects and buffers.
It does not load a shared library, launch a solver, or read any HE29 table.
"""
from contextlib import ExitStack
import ctypes as ct
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import vigilode_reference as vr
import run_vigilode as runner


class ManufacturedCallbacks:
    n = 2

    def __init__(self):
        self.counts = {"rhs": 0, "jvp": 0, "partial_u": 0}
        self.calls = []

    def rhs(self, u, z):
        self.counts["rhs"] += 1
        self.calls.append(("rhs", u, z.copy()))
        return np.array([z[0] + 2*u, 3*z[1] - u])

    def jvp(self, u, z, v):
        self.counts["jvp"] += 1
        self.calls.append(("jvp", u, z.copy(), v.copy()))
        return np.array([v[0], 3*v[1]])

    def partial_u(self, u, z):
        self.counts["partial_u"] += 1
        self.calls.append(("partial_u", u, z.copy()))
        return np.array([2., -1.])


class FakeNative:
    """An in-process Python callable, not a compiled/native solver."""
    def __init__(self, *, stats=None, telemetry=None, raw=None, rc=0,
                 output=None, hook=None):
        self.stat_overrides = stats or {}
        self.telemetry_overrides = telemetry or {}
        self.raw = raw
        self.rc = rc
        self.output = np.array([0.75, -0.25]) if output is None else np.asarray(output)
        self.hook = hook
        self.calls = 0

    def __call__(self, n, z, rhs, jvp, partial, context, initial_step,
                 max_step, max_attempts, out, stats_ptr, buffer, capacity):
        self.calls += 1
        self.received = (n, initial_step, max_step, max_attempts)
        if self.hook:
            self.hook(n, z, rhs, jvp, partial, out)
        np.ctypeslib.as_array(out, shape=(n,))[:] = self.output
        stats = ct.cast(stats_ptr, ct.POINTER(vr.He29Stats)).contents
        for key, value in {"abi_version": vr.ABI_VERSION, "status": 0,
                           "dimension": n, "final_u": 1., "output_samples": 2,
                           **self.stat_overrides}.items():
            setattr(stats, key, value)
        telemetry = {"success": True, "vigilode_source": vr.VIGILODE_SOURCE,
                     "dense_output_used": False, "rtol": 1e-10,
                     "atol_scaled": 1e-12, **self.telemetry_overrides}
        raw = self.raw if self.raw is not None else json.dumps(telemetry).encode()
        if len(raw)+1 > capacity:
            raise AssertionError("test fixture exceeds buffer")
        stats.json_required_bytes = len(raw)+1
        ct.memmove(buffer, raw+b"\0", len(raw)+1)
        return self.rc


def bridge_with(fake):
    bridge = vr.VigilODEBridge.__new__(vr.VigilODEBridge)
    bridge._solve = fake
    return bridge


class BuildReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="he29-build-contract-")
        self.addCleanup(self.temp.cleanup)
        self.lane = Path(self.temp.name)
        self.library = self.lane / "fake.so"
        self.library.write_bytes(b"manufactured bytes: not a shared library")
        self.receipt = self.lane / "BUILD.json"
        paths = ("rust_bridge/Cargo.toml", "rust_bridge/Cargo.lock",
                 "rust_bridge/src/lib.rs", "rust_bridge/include/he29_vigilode_bridge.h")
        sources = {}
        for relative in paths:
            target = self.lane / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("manufactured source " + relative)
            sources[relative] = vr.digest(target)
        self.data = {"schema": "he29.vigilode.build.v1", "status": "COMPILED",
                     "abi_version": 1, "vigilode_source": vr.VIGILODE_SOURCE,
                     "baseline_code_revision": vr.BASELINE_CODE,
                     "library_sha256": vr.digest(self.library), "bridge_sources": sources}
        self.write_receipt()

    def write_receipt(self):
        self.receipt.write_text(json.dumps(self.data))

    def verify(self):
        return vr.verify_build(self.library, self.receipt, lane=self.lane)

    def test_valid_receipt_binds_library_and_all_four_source_files(self):
        actual = self.verify()
        self.assertEqual(actual["receipt_sha256"], vr.digest(self.receipt))
        self.assertEqual(actual["bridge_sources"], self.data["bridge_sources"])

    def test_wrong_fixed_contract_fields_reject(self):
        for key in ("schema", "status", "abi_version", "vigilode_source", "baseline_code_revision"):
            with self.subTest(key=key):
                original = self.data[key]
                self.data[key] = "different"
                self.write_receipt()
                with self.assertRaisesRegex(ValueError, "BUILD_CONTRACT"):
                    self.verify()
                self.data[key] = original

    def test_library_bytes_changed_after_receipt_reject(self):
        self.library.write_bytes(b"changed binary")
        with self.assertRaisesRegex(ValueError, "LIBRARY_HASH"):
            self.verify()

    def test_source_bytes_changed_after_receipt_reject(self):
        (self.lane / "rust_bridge/src/lib.rs").write_text("changed source")
        with self.assertRaisesRegex(ValueError, "BRIDGE_SOURCE_MISMATCH"):
            self.verify()

    def test_source_path_set_is_exact(self):
        valid = dict(self.data["bridge_sources"])
        for sources in ({}, [], {k: v for k, v in valid.items() if not k.endswith("Cargo.lock")},
                        {**valid, "unapproved.rs": "0"*64}):
            with self.subTest(sources=sources):
                self.data["bridge_sources"] = sources
                self.write_receipt()
                with self.assertRaisesRegex(ValueError, "SOURCE_RECEIPT"):
                    self.verify()

    def test_identity_failure_prevents_cdll_load(self):
        with patch.object(vr, "verify_build", side_effect=ValueError("identity mismatch")), \
             patch.object(vr.ct, "CDLL") as loader:
            with self.assertRaisesRegex(ValueError, "identity mismatch"):
                vr.VigilODEBridge(self.library, self.receipt)
        loader.assert_not_called()

    def test_runtime_abi_failure_prevents_solve_binding(self):
        library = SimpleNamespace(he29_vigilode_abi_version=MagicMock(return_value=2))
        with patch.object(vr, "verify_build", return_value={"verified": True}), \
             patch.object(vr.ct, "CDLL", return_value=library):
            with self.assertRaisesRegex(ValueError, "ABI_VERSION"):
                vr.VigilODEBridge(self.library, self.receipt)
        self.assertFalse(hasattr(library, "he29_vigilode_segment"))


class FfiContractTests(unittest.TestCase):
    def test_ctypes_callbacks_and_valid_endpoint_admission(self):
        cb = ManufacturedCallbacks()
        seen = {}
        def exercise(n, z, rhs, jvp, partial, out):
            seen["rhs_code"] = rhs(None, .25, z, n, out)
            seen["rhs"] = np.ctypeslib.as_array(out, shape=(n,)).copy()
            direction = np.array([2., -4.])
            seen["jvp_code"] = jvp(None, .25, z, direction.ctypes.data_as(vr.DOUBLE_PTR), n, out)
            seen["jvp"] = np.ctypeslib.as_array(out, shape=(n,)).copy()
            seen["partial_code"] = partial(None, .25, z, n, out)
            seen["partial"] = np.ctypeslib.as_array(out, shape=(n,)).copy()
        fake = FakeNative(hook=exercise)
        initial = np.array([.5, -.5])
        actual, evidence = bridge_with(fake).segment(cb, initial, max_attempts=17)
        np.testing.assert_array_equal(actual, [.75, -.25])
        np.testing.assert_array_equal(initial, [.5, -.5])
        np.testing.assert_array_equal(seen["rhs"], [1., -1.75])
        np.testing.assert_array_equal(seen["jvp"], [2., -12.])
        np.testing.assert_array_equal(seen["partial"], [2., -1.])
        self.assertEqual([seen[k] for k in ("rhs_code", "jvp_code", "partial_code")], [0, 0, 0])
        self.assertEqual(fake.received, (2, 1/32, 1., 17))
        self.assertEqual(evidence["callback_failures"], [])
        self.assertEqual(evidence["python_callbacks"], {"rhs": 1, "jvp": 1, "partial_u": 1})

    def test_each_completion_stat_is_required(self):
        for key, value in (("abi_version", 2), ("status", 1), ("dimension", 3),
                           ("final_u", .999), ("output_samples", 3)):
            with self.subTest(key=key):
                with self.assertRaises(vr.VigilODEFailure) as caught:
                    bridge_with(FakeNative(stats={key: value})).segment(ManufacturedCallbacks(), [.5, -.5])
                self.assertEqual(caught.exception.evidence["stats"][key], value)

    def test_each_telemetry_admission_field_is_required(self):
        for key, value in (("success", False), ("success", 1),
                           ("vigilode_source", "wrong"), ("dense_output_used", True),
                           ("dense_output_used", 0), ("rtol", 2e-10), ("atol_scaled", 2e-12)):
            with self.subTest(key=key, value=value):
                with self.assertRaises(vr.VigilODEFailure):
                    bridge_with(FakeNative(telemetry={key: value})).segment(ManufacturedCallbacks(), [.5, -.5])

    def test_returncode_and_nonfinite_output_reject(self):
        for fake in (FakeNative(rc=1), FakeNative(output=[np.nan, 0.]), FakeNative(output=[np.inf, 0.])):
            with self.subTest(rc=fake.rc, output=fake.output):
                with self.assertRaises(vr.VigilODEFailure) as caught:
                    bridge_with(fake).segment(ManufacturedCallbacks(), [.5, -.5])
                self.assertEqual(caught.exception.state, [.75, -.25] if fake.rc else None)

    def test_malformed_and_nonobject_telemetry_is_scoped_failure(self):
        for raw in (b"{truncated", b"[]", b"null", b"true", b"123", b'"text"'):
            with self.subTest(raw=raw):
                with self.assertRaises(vr.VigilODEFailure) as caught:
                    bridge_with(FakeNative(raw=raw)).segment(ManufacturedCallbacks(), [.5, -.5])
                self.assertIsInstance(caught.exception.evidence["telemetry"], dict)
                self.assertEqual(caught.exception.state, [.75, -.25])

    def test_first_python_exception_survives_fake_native_success(self):
        cb = ManufacturedCallbacks()
        cb.rhs = MagicMock(side_effect=RuntimeError("first callback error"))
        cb.partial_u = MagicMock(side_effect=SystemExit("second callback error"))
        codes = []
        def exercise(n, z, rhs, jvp, partial, out):
            codes.append(rhs(None, .25, z, n, out))
            codes.append(partial(None, .25, z, n, out))
        with self.assertRaises(vr.VigilODEFailure) as caught:
            bridge_with(FakeNative(hook=exercise)).segment(cb, [.5, -.5])
        failures = caught.exception.evidence["callback_failures"]
        self.assertEqual(codes, [1, 1])
        self.assertEqual(len(failures), 1)
        self.assertIn("first callback error", failures[0]["error"])
        self.assertIn("RuntimeError", failures[0]["traceback"])

    def test_wrong_arity_and_null_pointers_fail_without_calling_model(self):
        for mode in ("arity", "null_state", "null_output", "null_direction"):
            with self.subTest(mode=mode):
                cb = ManufacturedCallbacks()
                codes = []
                def exercise(n, z, rhs, jvp, partial, out):
                    null = vr.DOUBLE_PTR()
                    if mode == "null_direction":
                        codes.append(jvp(None, .25, z, null, n, out))
                    else:
                        codes.append(rhs(None, .25, null if mode == "null_state" else z,
                                         n+1 if mode == "arity" else n,
                                         null if mode == "null_output" else out))
                with self.assertRaises(vr.VigilODEFailure):
                    bridge_with(FakeNative(hook=exercise)).segment(cb, [.5, -.5])
                self.assertEqual(codes, [1])
                self.assertEqual(cb.calls, [])

    def test_nonfinite_callback_output_becomes_retained_failure(self):
        cb = ManufacturedCallbacks()
        cb.rhs = lambda u, z: np.array([np.nan, 0.])
        codes = []
        def exercise(n, z, rhs, jvp, partial, out):
            codes.append(rhs(None, .25, z, n, out))
        with self.assertRaises(vr.VigilODEFailure) as caught:
            bridge_with(FakeNative(hook=exercise)).segment(cb, [.5, -.5])
        self.assertEqual(codes, [1])
        self.assertIn("callback output", caught.exception.evidence["callback_failures"][0]["error"])

    def test_invalid_budget_fails_before_fake_native_call(self):
        for options in ({"initial_step": 0}, {"max_step": 1.1}, {"initial_step": .5, "max_step": .25},
                        {"initial_step": np.nan}, {"max_attempts": True}, {"max_attempts": 100001}):
            with self.subTest(options=options):
                fake = FakeNative()
                with self.assertRaisesRegex(ValueError, "STEP_BUDGET"):
                    bridge_with(fake).segment(ManufacturedCallbacks(), [.5, -.5], **options)
                self.assertEqual(fake.calls, 0)


class SegmentModel:
    scale = np.array([2., .5, 4., 10.])
    t_end = 7.
    breakpoints = np.array([2., 5.])

    def __init__(self):
        self.intervals = []

    def initial_state(self):
        return np.array([4., 3., 8., 5.])

    def set_interval(self, left, right):
        self.intervals.append((left, right))

    def rhs(self, t, y):
        return np.zeros(4)

    def jac(self, t, y):
        return np.zeros((4, 4))

    def result(self, state, metadata):
        return {"state": state.tolist(), "metadata": metadata}


class SegmentationTests(unittest.TestCase):
    def test_original_boundaries_and_endpoint_state_carry_are_preserved(self):
        model, records = SegmentModel(), []
        calls = []
        step = np.array([.1, .2, .3, .4])
        def segment(cb, z, **options):
            calls.append((cb.left, cb.right, z.copy(), options))
            return z + step, {"synthetic_segment": len(calls)}
        actual = vr.solve_vigilode(model, SimpleNamespace(segment=segment), records.append, max_attempts=29)
        self.assertEqual(model.intervals, [(0., 2.), (2., 5.), (5., 7.)])
        self.assertEqual(len(records), 3)
        for index, row in enumerate(records):
            self.assertTrue(row["complete"])
            np.testing.assert_allclose(row["physical_state"], model.initial_state()+(index+1)*step*model.scale)
            np.testing.assert_allclose(calls[index][2], model.initial_state()/model.scale+index*step)
            self.assertEqual(calls[index][3], {"max_attempts": 29})
        np.testing.assert_allclose(actual["state"], records[-1]["physical_state"])
        self.assertEqual(actual["metadata"]["segment_count"], 3)
        self.assertFalse(actual["metadata"]["dense_output_used"])
        self.assertFalse(actual["metadata"]["new_global_error_bound"])

    def test_first_failed_segment_retains_last_complete_and_partial_states(self):
        model, records = SegmentModel(), []
        step = np.array([.1, .2, .3, .4])
        count = 0
        def segment(cb, z, **options):
            nonlocal count
            count += 1
            if count == 2:
                raise vr.VigilODEFailure("manufactured failure", {"attempts": 9}, [1., 2., 3., 4.])
            return z + step, {"synthetic_segment": count}
        with self.assertRaises(vr.VigilODEFailure):
            vr.solve_vigilode(model, SimpleNamespace(segment=segment), records.append)
        self.assertEqual(count, 2)
        self.assertEqual(model.intervals, [(0., 2.), (2., 5.)])
        self.assertEqual(len(records), 2)
        self.assertFalse(records[-1]["complete"])
        np.testing.assert_allclose(records[-1]["last_completed_physical_state"], model.initial_state()+step*model.scale)
        self.assertEqual(records[-1]["partial_observed_scaled_state"], [1., 2., 3., 4.])
        self.assertEqual(records[-1]["evidence"], {"attempts": 9})


class CanaryAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="he29-canary-contract-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.current = {"binary_sha256": "f"*64, "source_files": {"s": "1"},
                        "parent_sources": {"p": "2"}, "input_sources": {"i": "3"},
                        "numerical_thread_environment": {"thread": "1"},
                        "runtime": {"python": "test-python", "numpy": "test-numpy", "scipy": "test-scipy"}}
        self.case = self.root / "m8_r4_table512"
        self.case.mkdir()
        (self.case / "IDENTITY.json").write_text(json.dumps(self.current))
        self.prior = {"table_sha256": "manufactured-table", "results": {"Radau": {"saved": "Radau"}, "DOP853": {"saved": "DOP853"}}}
        (self.case / "RESULT.json").write_text(json.dumps(self.prior))
        self.args = SimpleNamespace(out=str(self.root / "new-case"), binary="unused-binary",
                                    owner_receipt="unused-owner-receipt", baseline_campaign=str(self.root),
                                    library="unused-library", bridge_receipt="unused-build")

    def test_four_pair_gate_checks_before_reading_baseline_case(self):
        for summary in ({"complete": False, "completed": 0}, {"complete": True, "completed": 3}):
            with self.subTest(summary=summary), patch.object(runner, "analyze", return_value=summary):
                with self.assertRaisesRegex(ValueError, "FOUR_COMPLETED_BASELINE_PAIRS"):
                    runner.baseline_contract(self.root / "does-not-exist", self.current)

    def test_admitted_baseline_reuse_preserves_exact_receipt_hashes(self):
        summary = {"complete": True, "completed": 4}
        with patch.object(runner, "analyze", return_value=summary):
            result, reuse = runner.baseline_contract(self.root, self.current)
        self.assertEqual(result, self.prior)
        self.assertEqual(reuse["baseline_analysis"], summary)
        self.assertEqual(reuse["case_receipt_sha256"], vr.digest(self.case / "RESULT.json"))
        self.assertEqual(reuse["case_identity_sha256"], vr.digest(self.case / "IDENTITY.json"))
        self.assertEqual(reuse["baseline_code_revision"], vr.BASELINE_CODE)

    def test_changed_source_binary_input_threads_or_runtime_reject(self):
        for key in ("binary_sha256", "source_files", "parent_sources", "input_sources", "numerical_thread_environment", "python", "numpy", "scipy"):
            with self.subTest(key=key), patch.object(runner, "analyze", return_value={"complete": True, "completed": 4}):
                identity = json.loads(json.dumps(self.current))
                if key in ("python", "numpy", "scipy"):
                    identity["runtime"][key] = "changed"
                else:
                    identity[key] = "changed"
                (self.case / "IDENTITY.json").write_text(json.dumps(identity))
                with self.assertRaisesRegex(ValueError, "BASELINE_(IDENTITY|RUNTIME)"):
                    runner.baseline_contract(self.root, self.current)

    def test_baseline_gate_failure_prevents_build_verification(self):
        with patch.object(runner, "check_sources", return_value=self.current), \
             patch.object(runner, "baseline_contract", side_effect=ValueError("baseline not ready")), \
             patch.object(runner, "verify_build") as verify:
            with self.assertRaisesRegex(ValueError, "baseline not ready"):
                runner.preflight(self.args)
        verify.assert_not_called()

    def mocked_case(self, *, table="manufactured-table", check_error=None):
        stack = ExitStack()
        self.addCleanup(stack.close)
        owner = SimpleNamespace(calls=0)
        owner_context = MagicMock()
        owner_context.__enter__.return_value = owner
        model = SimpleNamespace(source_table_sha256=table, source_table_diagnostics={"manufactured": True})
        stack.enter_context(patch.object(runner, "preflight", return_value=(self.current, self.prior, {"synthetic": True}, {"synthetic": True})))
        stack.enter_context(patch.dict(os.environ, {**runner.THREADS, "RAYON_NUM_THREADS": "1"}))
        stack.enter_context(patch.object(runner, "VigilODEBridge", return_value=object()))
        stack.enter_context(patch.object(runner, "NativeOwner", return_value=owner_context))
        stack.enter_context(patch.object(runner, "RefinedSourceModel", return_value=model))
        stack.enter_context(patch.object(runner, "manifest", return_value={"manufactured": "hash"}))
        solve = stack.enter_context(patch.object(runner, "solve_vigilode", return_value={"manufactured_endpoint": [1., 2., 3., 4.]}))
        check = stack.enter_context(patch.object(runner, "check_result", side_effect=check_error))
        compare = stack.enter_context(patch.object(runner, "admit_pair", return_value={"manufactured_pass": True}))
        return solve, check, compare

    def test_rebuilt_table_mismatch_prevents_solver_execution(self):
        solve, check, compare = self.mocked_case(table="different-table")
        with self.assertRaisesRegex(ValueError, "REBUILT_TABLE_MISMATCH"):
            runner.run_case(self.args)
        solve.assert_not_called()
        check.assert_not_called()
        compare.assert_not_called()
        out = Path(self.args.out)
        self.assertTrue((out / "TABLE.json").exists())
        self.assertEqual(json.loads((out / "FAILURE.json").read_text())["status"], "HOLD_FIRST_FAILURE")
        self.assertFalse((out / "RESULT.json").exists())

    def test_admission_failure_preserves_raw_endpoint_and_failure_receipt(self):
        solve, check, compare = self.mocked_case(check_error=ValueError("manufactured endpoint rejection"))
        with self.assertRaisesRegex(ValueError, "manufactured endpoint rejection"):
            runner.run_case(self.args)
        solve.assert_called_once()
        check.assert_called_once()
        compare.assert_not_called()
        out = Path(self.args.out)
        self.assertEqual(json.loads((out / "VIGILODE_RAW.json").read_text())["result"], solve.return_value)
        self.assertEqual(json.loads((out / "FAILURE.json").read_text())["status"], "HOLD_FIRST_FAILURE")
        self.assertFalse((out / "RESULT.json").exists())

    def test_canary_success_compares_both_saved_methods_and_creates_no_baseline_pair(self):
        solve, check, compare = self.mocked_case()
        runner.run_case(self.args)
        self.assertEqual(compare.call_count, 2)
        self.assertEqual([call.args[1] for call in compare.call_args_list],
                         [self.prior["results"]["Radau"], self.prior["results"]["DOP853"]])
        result = json.loads((Path(self.args.out) / "RESULT.json").read_text())
        self.assertEqual(result["status"], "CANARY_COMPLETED_SCOPED")
        self.assertEqual(result["case"], {"m": 8, "r": 4, "angles": 4, "q": 0., "table_nodes": 512})
        self.assertEqual(result["baseline_pairs_reused"], 4)
        for field in ("new_baseline_pairs", "transport_replays", "source_only_suites_replayed", "native_calls"):
            self.assertEqual(result[field], 0)
        for field in ("continuous_spectrum", "global_gas_temperature_bound", "upstream_grackle_whole_runtime_equivalence"):
            self.assertEqual(result[field], "HOLD")


if __name__ == "__main__":
    unittest.main()
