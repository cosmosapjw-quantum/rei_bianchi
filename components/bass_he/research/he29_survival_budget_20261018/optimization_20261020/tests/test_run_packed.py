"""Five new entrypoint checks using manufactured files and simulated workers.

Original source verification, four-pair analysis and admission functions run
on deliberately manufactured receipts.  No native library, owner, physical
solver, original test suite or actual worker subprocess is invoked here.
"""
from contextlib import ExitStack
from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

LANE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LANE / "src"))
import run_packed as runner
import reference_runner as original
from reference_contract import OWNER, JOBS, THREADS

REVISION = "0123456789abcdef0123456789abcdef01234567"


class PackedRunnerEntrypointChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="he29-packed-entry-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "manufactured-repository"
        self.he29 = self.repo / "research/he29"
        self.server = self.repo / "research/he25_proper_birth_20261016/src/owner_server.rs"
        self.server.parent.mkdir(parents=True)
        self.server.write_text("manufactured source identity; never compiled\n")
        self.input = self.he29 / "inputs/DATA.json"
        self.input.parent.mkdir(parents=True)
        self.input.write_text('{"manufactured_data":true}\n')
        self.source = self.he29 / "src/fixture.py"
        self.source.parent.mkdir(parents=True)
        self.source.write_text("# identity-only fixture, never imported\n")
        provenance = self.he29 / "provenance"
        provenance.mkdir()
        self.write(provenance / "PARENT_SHA256.json",
            {str(self.server.relative_to(self.repo)): runner.digest(self.server)})
        self.write(provenance / "INPUT_SHA256.json",
            {str(self.input.relative_to(self.he29)): runner.digest(self.input)})
        self.binary = self.root / "manufactured-owner.bin"
        self.binary.write_bytes(b"not executable: manufactured owner identity")
        self.owner_receipt = self.root / "OWNER.json"
        self.write(self.owner_receipt, dict(owner_source=OWNER,
            binary_sha256=runner.digest(self.binary), server_source_sha256=runner.digest(self.server)))
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(patch.object(original, "ROOT", self.he29))
        stack.enter_context(patch.object(original, "REPO", self.repo))
        stack.enter_context(patch.object(runner, "REPO", self.repo))
        stack.enter_context(patch.object(runner, "HE29", self.he29))
        stack.enter_context(patch.dict(os.environ, {**THREADS, "RAYON_NUM_THREADS": "1"}))
        self.current = runner.check_sources(self.binary, self.owner_receipt)
        self.campaign = self.root / "manufactured-baseline"
        for r, nodes in JOBS:
            case = self.campaign / f"m8_r{r}_table{nodes}"
            case.mkdir(parents=True)
            identity = {**deepcopy(self.current), "m": 8, "r": r, "q": 0.,
                        "angles": 4, "table_nodes": nodes}
            a = dict(temperature_K=8., gas_final=[1e-5, 2e-5, 1e-13, .001],
                number_defect=0., energy_defect_ev=0., species_defect=[0., 0., 0.],
                gas_positive=True, min_photon=0.)
            b = {**deepcopy(a), "temperature_K": 8. + 1e-12}
            table = f"manufactured-table-{r}-{nodes}"
            result = dict(status="REFERENCE_COMPLETED_SCOPED", table_sha256=table,
                point_qualification={"points": 6}, results={"Radau": a, "DOP853": b})
            for name, data in (("IDENTITY.json", identity), ("RESULT.json", result),
                               ("TABLE.json", {"source_table_sha256": table})):
                self.write(case / name, data)
        self.build = dict(schema="he29.optimized.build.v1", status="COMPILED",
                          abi_version=2, bass_publication_head=REVISION,
                          scope="manufactured build receipt; no shared library loaded")
        self.verify = stack.enter_context(patch.object(runner, "verify_build", return_value=self.build))
        self.git_status = ""
        stack.enter_context(patch.object(runner, "query", side_effect=self.query))
        self.args = SimpleNamespace(out=str(self.root / "case-output"),
            baseline_campaign=str(self.campaign), binary=str(self.binary),
            owner_receipt=str(self.owner_receipt), library=str(self.root / "unused-library.so"),
            bridge_receipt=str(self.root / "unused-build.json"), source_revision=REVISION)

    @staticmethod
    def write(path, data):
        Path(path).write_text(json.dumps(data, allow_nan=False))

    def query(self, argv, *, strip=True):
        if argv[-2:] == ["rev-parse", "HEAD"]:
            return REVISION
        if argv[-2:] == ["rev-parse", "HEAD^{tree}"]:
            return "fedcba9876543210fedcba9876543210fedcba98"
        if argv[-4:] == ["status", "--porcelain=v1", "--untracked-files=all", "-z"]:
            self.assertFalse(strip)
            return self.git_status
        raise AssertionError("Unexpected manufactured Git query: " + repr(argv))

    def test_four_pair_gate_and_runtime_equality_for_every_pair(self):
        current, prior, reused, build, publication = runner.preflight(self.args)
        self.assertEqual(current, self.current)
        self.assertEqual(reused["runtime_matched_pairs"], 4)
        self.assertEqual(len(reused["all_pair_receipts"]), 4)
        self.assertEqual(reused["baseline_analysis"]["new_solver_calls"], 0)
        self.assertEqual(publication["head"], REVISION)
        self.assertFalse(reused["baseline_analysis"]["references"][0]["error_radius_certified"])
        path = self.campaign / "m8_r8_table512/IDENTITY.json"
        saved = path.read_bytes()
        for field in ("python", "numpy", "scipy"):
            with self.subTest(runtime=field):
                identity = json.loads(saved)
                identity["runtime"][field] = "changed manufactured runtime"
                self.write(path, identity)
                self.verify.reset_mock()
                with self.assertRaisesRegex(ValueError, "BASELINE_RUNTIME"):
                    runner.preflight(self.args)
                self.verify.assert_not_called()
        path.write_bytes(saved)
        missing = self.campaign / "m8_r4_table1024/RESULT.json"
        missing.unlink()
        self.verify.reset_mock()
        with self.assertRaisesRegex(ValueError, "FOUR_COMPLETED_BASELINE_PAIRS"):
            runner.preflight(self.args)
        self.verify.assert_not_called()

    def test_original_source_input_and_binary_gates_reach_new_preflight(self):
        self.assertIs(runner.check_sources, original.check_sources)
        self.assertIs(runner.run_process, original.run_process)
        self.assertIs(runner.check_result, original.check_result)
        self.assertIs(runner.admit_pair, original.admit_pair)
        for path in (self.source, self.server, self.input, self.binary):
            with self.subTest(changed_path=path.name):
                saved = path.read_bytes()
                path.write_bytes(saved + b"manufactured drift")
                self.verify.reset_mock()
                try:
                    with self.assertRaisesRegex(ValueError,
                            "SOURCE_IDENTITY|BASELINE_IDENTITY|NATIVE_BUILD_IDENTITY"):
                        runner.preflight(self.args)
                    self.verify.assert_not_called()
                finally:
                    path.write_bytes(saved)

    def simulated_case(self, *, table="manufactured-table-4-512", result=None):
        stack = ExitStack()
        self.addCleanup(stack.close)
        owner = SimpleNamespace(calls=0)
        context = MagicMock()
        context.__enter__.return_value = owner
        owner_factory = stack.enter_context(patch.object(runner, "NativeOwner", return_value=context))
        bridge = stack.enter_context(patch.object(runner, "PackedBridge", return_value=object()))
        model = SimpleNamespace(source_table_sha256=table,
            source_table_diagnostics={"manufactured": True})
        constructor = stack.enter_context(patch.object(runner, "OptimizedRefinedSourceModel", return_value=model))
        if result is None:
            result = json.loads((self.campaign / "m8_r4_table512/RESULT.json").read_text())["results"]["Radau"]
        def solve(model, bridge, checkpoint):
            checkpoint({"segment": 0, "complete": True, "manufactured": True})
            return deepcopy(result)
        solver = stack.enter_context(patch.object(runner, "solve_packed", side_effect=solve))
        compare = stack.enter_context(patch.object(runner, "admit_pair", wraps=original.admit_pair))
        return stack, owner_factory, constructor, solver, compare

    def test_rebuilt_table_mismatch_stops_before_packed_solver(self):
        stack, owner, constructor, solve, compare = self.simulated_case(table="wrong-manufactured-table")
        with self.assertRaisesRegex(ValueError, "REBUILT_TABLE_MISMATCH"):
            runner.run_case(self.args)
        solve.assert_not_called()
        compare.assert_not_called()
        self.assertEqual(constructor.call_args.kwargs, dict(tabulate=True,
            source_table_nodes=512, max_table_bytes=2*1024**3, max_table_wall_s=600.))
        spec = constructor.call_args.args[1]
        self.assertEqual((spec.m, spec.angles, spec.q, spec.strips), (8, 4, 0., 4))
        out = Path(self.args.out)
        self.assertTrue((out / "TABLE.json").is_file())
        self.assertTrue((out / "FAILURE.json").is_file())
        self.assertFalse((out / "RESULT.json").exists())

    def test_both_original_admissions_and_raw_retention_on_rejection(self):
        prior = json.loads((self.campaign / "m8_r4_table512/RESULT.json").read_text())["results"]["Radau"]
        for admitted in (True, False):
            with self.subTest(admitted=admitted):
                self.args.out = str(self.root / ("admitted-output" if admitted else "rejected-output"))
                result = deepcopy(prior)
                if not admitted:
                    result["temperature_K"] += 2e-9
                stack, owner, constructor, solve, compare = self.simulated_case(result=result)
                try:
                    if admitted:
                        runner.run_case(self.args)
                        self.assertEqual(compare.call_count, 2)
                    else:
                        with self.assertRaisesRegex(ValueError, "REFERENCE_UNSTABLE"):
                            runner.run_case(self.args)
                    solve.assert_called_once()
                    out = Path(self.args.out)
                    self.assertEqual(json.loads((out / "PACKED_RAW.json").read_text())["result"], result)
                    self.assertTrue((out / "SEGMENT_ENDPOINTS.jsonl").is_file())
                    if admitted:
                        receipt = json.loads((out / "RESULT.json").read_text())
                        self.assertEqual(set(receipt["comparison_to_saved_baseline"]), {"Radau", "DOP853"})
                        self.assertEqual(receipt["case"], runner.CASE)
                        self.assertEqual(receipt["baseline_pairs_reused"], 4)
                        self.assertEqual(receipt["new_baseline_pairs"], 0)
                        self.assertEqual(receipt["native_calls"], 0)
                        self.assertEqual(receipt["packed_threads"], 1)
                    else:
                        self.assertTrue((out / "FAILURE.json").is_file())
                        self.assertFalse((out / "RESULT.json").exists())
                finally:
                    stack.close()

    def test_publication_binding_and_simulated_process_group_timeout_receipt(self):
        self.build["bass_publication_head"] = "f"*40
        with self.assertRaisesRegex(ValueError, "BUILD_PUBLICATION_MISMATCH"):
            runner.preflight(self.args)
        self.build["bass_publication_head"] = REVISION
        data_path = str(self.input.relative_to(self.repo))
        self.git_status = "?? " + data_path + "\0"
        publication = runner.preflight(self.args)[4]
        self.assertEqual(publication["verified_untracked_input_data"],
                         {data_path: runner.digest(self.input)})
        for status, error in (("?? extra.py\0", "UNVERIFIED_UNTRACKED_FILE"),
                              (" M tracked.py\0", "TRACKED_SOURCE_DIRTY")):
            with self.subTest(status=status):
                self.git_status = status
                with self.assertRaisesRegex(ValueError, error):
                    runner.preflight(self.args)
        self.git_status = "?? " + data_path + "\0"
        calls = []
        def simulated_process(argv, destination, timeout):
            calls.append((argv, Path(destination), timeout))
            self.assertEqual(os.environ[runner.WORKER_FLAG], "1")
            self.assertEqual(os.environ["RAYON_NUM_THREADS"], "1")
            receipt = dict(returncode=-15, timed_out=True, wall_s=900.,
                stdout_sha256="manufactured-stdout", stderr_sha256="manufactured-stderr")
            runner.atomic_json(Path(destination) / "COMMAND.json", dict(argv=argv, timeout_s=timeout))
            runner.atomic_json(Path(destination) / "RECEIPT.json", receipt)
            return receipt
        argv = [str(LANE / "src/run_packed.py"), "canary", "--out", self.args.out,
                "--wall-s", "900", "--source-revision", REVISION]
        for name in ("baseline_campaign", "binary", "owner_receipt", "library", "bridge_receipt"):
            argv += ["--" + name.replace("_", "-"), getattr(self.args, name)]
        with patch.object(sys, "argv", argv), patch.object(runner, "run_process", side_effect=simulated_process), \
                patch.object(runner, "NativeOwner") as native, patch.object(runner, "PackedBridge") as bridge:
            with self.assertRaises(SystemExit) as caught:
                runner.main()
            self.assertEqual(caught.exception.code, 1)
            native.assert_not_called()
            bridge.assert_not_called()
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][2], 900.)
        self.assertEqual(calls[0][0][2], "_worker")
        self.assertIn(REVISION, calls[0][0])
        summary = json.loads((Path(self.args.out) / "SUMMARY.json").read_text())
        self.assertEqual(summary["new_canary_cases"], 0)
        self.assertEqual(summary["requested_canary_cases"], 1)
        self.assertTrue(summary["timed_out"])
        self.assertTrue((Path(self.args.out) / "FAILURE.json").is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
