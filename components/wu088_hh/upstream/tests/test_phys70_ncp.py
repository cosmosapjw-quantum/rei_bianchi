"""New wrapper-only tests; all child outputs are NONPHYSICAL TEST FIXTURES.

These tests run no Coulomb initializer, old integral, native solver or old suite.
The immutable original NPZ is used only for its SHA guard.  Temporary fake
programs exercise process control and receipt handling and are never delivered
as scientific results or as a performance measurement.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import phys70_ncp as runner


def request(lmax: int = 28) -> dict:
    return {"schema": "PHYS70_OPTIMIZED_REQUEST_V1", "engine": "block_simd", "HH_R10": "OFF",
            "physics_request": {"schema": "PHYS69_VIGILODE_REQUEST_V1", "lmax": lmax,
                "angular_nodes": 96 if lmax == 28 else 128, "rtol": 3e-11, "atol": 3e-13,
                "initial_step": 0.01, "max_step": 0.5, "max_attempts": 20000,
                "upstream_commit": runner.UPSTREAM, "frozen_source_sha256": runner.SOURCE_SHA,
                "HH_R10": "OFF"}}


def fixture_result(req: dict, request_sha: str = "a" * 64, seed_sha: str = "b" * 64) -> dict:
    """Synthetic structural fixture: its endpoint is not a WU calculation."""
    n = 2 * (4 * (req["physics_request"]["lmax"] + 1) + 1)
    end = [0.0] * n
    end[-2:] = [1.25, -0.5]
    return {"schema": "PHYS70_OPTIMIZED_RESULT_V1", "complete": True,
            "request": copy.deepcopy(req), "B": 27, "T": 65, "k": 0.7,
            "eta_C": "-10/7", "m": 0, "target": [21, 20],
            "clock": "tau=65-r;0..38", "q_scale": "2^80", "d2_scale": "2^160",
            "status": runner.SUCCESS_STATUS, "request_sha256": request_sha,
            "seed_sha256": seed_sha, "source_sha256": runner.SOURCE_SHA,
            "engine": req["engine"], "upstream_commit": runner.UPSTREAM, "HH_R10": "OFF",
            "endpoint": {"d2": {"real": math.ldexp(1.25, -160), "imag": math.ldexp(-0.5, -160)}},
            "observed_times_tau": [0.0, 38.0], "observed_states_scaled": [[0.0] * n, end],
            "accepted_steps": 1, "rejected_steps": 0, "attempts": 1, "state_reuses": 0,
            "counters": {"fixture_only": "NONPHYSICAL_TEST_FIXTURE"},
            "integration_elapsed_seconds": 0.0, "test_fixture": True}


class ContractTests(unittest.TestCase):
    def test_inherits_fixed_physics_and_supports_only_three_engines(self):
        for engine in sorted(runner.ENGINES):
            req = request()
            req["engine"] = engine
            runner.validate_request(req)
        for change in [("HH_R10", "ON"), ("engine", "unknown")]:
            req = request()
            req[change[0]] = change[1]
            with self.assertRaises(ValueError):
                runner.validate_request(req)
        for key, value in [("frozen_source_sha256", "0" * 64), ("upstream_commit", "0" * 40),
                           ("HH_R10", "ON"), ("lmax", True), ("angular_nodes", 2),
                           ("rtol", float("inf")), ("max_step", 0.5001), ("initial_step", 0.6)]:
            req = request()
            req["physics_request"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                runner.validate_request(req)

    def test_rejects_duplicate_and_nonfinite_json(self):
        for data in (b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}', b'[]'):
            with self.subTest(data=data), self.assertRaises(ValueError):
                runner.decode(data)

    def test_result_identity_shape_counters_and_normalization(self):
        req = request()
        result = fixture_result(req)
        runner.validate_result(result, req, "a" * 64, "b" * 64)
        mutations = [
            lambda r: r.update(engine="legacy_gmres"),
            lambda r: r.update(request_sha256="c" * 64),
            lambda r: r.update(seed_sha256="c" * 64),
            lambda r: r.update(source_sha256="c" * 64),
            lambda r: r.update(complete=False, status="PARTIAL_INTEGRATION"),
            lambda r: r.update(observed_times_tau=[0, 37]),
            lambda r: r["observed_states_scaled"][1].pop(),
            lambda r: r["observed_states_scaled"][1].__setitem__(0, float("nan")),
            lambda r: r["endpoint"]["d2"].update(real=1.0),
            lambda r: r.update(accepted_steps=True),
            lambda r: r.update(attempts=2),
            lambda r: r.update(state_reuses=-1),
            lambda r: r.update(counters=[]),
            lambda r: r.update(integration_elapsed_seconds=-1),
        ]
        for i, mutate in enumerate(mutations):
            changed = copy.deepcopy(result)
            mutate(changed)
            with self.subTest(case=i), self.assertRaises(ValueError):
                runner.validate_result(changed, req, "a" * 64, "b" * 64)

    def test_delivery_requests_preserve_required_tolerances(self):
        folder = ROOT / "research/hh_phys70_20261020/ncp_delivery"
        large = runner.read(folder / "REQUEST_L64.json")
        perf = runner.read(folder / "REQUEST_L28_PERF.json")
        runner.validate_request(large)
        runner.validate_request(perf)
        self.assertEqual(large["physics_request"], runner.read(
            ROOT / "research/hh_phys69_20261019/vigilode/REQUEST_L64.json"))
        self.assertEqual((perf["physics_request"]["rtol"], perf["physics_request"]["atol"],
                          perf["physics_request"]["max_step"]), (3e-11, 3e-13, 0.5))
        self.assertEqual((large["engine"], perf["engine"]), ("block_simd", "block_simd"))

    def test_result_requires_the_full_matching_request(self):
        req = request()
        wrong_engine = copy.deepcopy(req)
        wrong_engine["engine"] = "legacy_gmres"
        wrong_tolerance = copy.deepcopy(req)
        wrong_tolerance["physics_request"]["rtol"] *= 10
        for other in (None, req["physics_request"], wrong_engine, wrong_tolerance):
            result = fixture_result(req)
            result["request"] = other
            with self.subTest(request=other), self.assertRaisesRegex(ValueError, "request"):
                runner.validate_result(result, req, "a" * 64, "b" * 64)

    def test_result_requires_original_geometry_and_channel_tags(self):
        req = request()
        for key, value in [("B", 28), ("T", 64), ("k", 0.8), ("m", 1),
                           ("m", False), ("target", [20, 21]), ("target", [21, 20, 0])]:
            result = fixture_result(req)
            result[key] = value
            with self.subTest(key=key, value=value), self.assertRaisesRegex(ValueError, key):
                runner.validate_result(result, req, "a" * 64, "b" * 64)

    def test_result_keeps_coulomb_and_scaled_d2_distinct_from_driven_xi(self):
        req = request()
        for key, value in [("eta_C", "Fy"), ("eta_C", "Fy-phi"), ("eta_C", -10 / 7),
                           ("q_scale", "2^160"), ("q_scale", "eta=Fy"),
                           ("d2_scale", "2^80"), ("d2_scale", "xi=Fy-phi"),
                           ("clock", "r=27..65")]:
            result = fixture_result(req)
            result[key] = value
            with self.subTest(key=key, value=value), self.assertRaisesRegex(ValueError, key):
                runner.validate_result(result, req, "a" * 64, "b" * 64)

    def test_fingerprint_covers_both_crates_and_excludes_build_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            names = ["scripts/phys70_ncp.py", "scripts/phys69_vigilode.py",
                     "scripts/phys68_rust_reference.py", "src/wu088_hh/phys67_coulomb_certificate.py"]
            for crate in ("phys70_optimized", "phys69_vigilode"):
                names += [f"native/{crate}/Cargo.toml", f"native/{crate}/Cargo.lock",
                          f"native/{crate}/src/lib.rs", f"native/{crate}/src/nested/core.rs"]
            names += ["native/phys70_optimized/build.rs", "native/phys70_optimized/target/generated.rs"]
            for name in names:
                f = root / name
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text("NONPHYSICAL TEST SOURCE " + name)
            with mock.patch.multiple(runner, ROOT=root, CRATE=root / "native/phys70_optimized",
                                     SCRIPT_DIR=root / "scripts", __file__=str(root / "scripts/phys70_ncp.py")):
                first = runner.engine_identity()
                self.assertIn("native/phys70_optimized/build.rs", first)
                self.assertNotIn("native/phys70_optimized/target/generated.rs", first)
                path = root / "native/phys69_vigilode/src/nested/core.rs"
                path.write_text("CHANGED NONPHYSICAL TEST SOURCE")
                second = runner.engine_identity()
                self.assertNotEqual(first, second)


@unittest.skipUnless(os.name == "posix", "process limits use the NCP POSIX contract")
class WrapperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.req = self.base / "input.json"
        self.req.write_bytes(b' \n' + json.dumps(request(), separators=(",", ":")).encode() + b' \n')
        self.seed = self.base / "fixture_seed.txt"
        self.seed.write_text("# NONPHYSICAL TEST FIXTURE\n" +
                             "".join(f"{ell} 1 0 0 1\n" for ell in range(29)))
        self.marker = self.base / "fixture_invocations.txt"
        self.binary = self.make_binary("success")
        self.patch = mock.patch.object(runner, "engine_identity", return_value={"test_fixture": "f" * 64})
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def make_binary(self, mode):
        path = self.base / ("fixture_binary_" + mode)
        program = f'''#!{sys.executable}
# NONPHYSICAL TEST FIXTURE: this program is not a numerical solver.
import hashlib,json,math,pathlib,sys,time
MODE={mode!r}
marker=pathlib.Path({str(self.marker)!r})
with marker.open("a") as f: f.write("fixture invocation\\n")
assert sys.argv[1]=="run"
if MODE=="timeout":
 print("NONPHYSICAL timeout fixture",flush=True)
 time.sleep(30)
if MODE=="error":
 print("NONPHYSICAL failure fixture",file=sys.stderr)
 sys.exit(2)
request_path,seed_path,source_path=map(pathlib.Path,sys.argv[2:5])
req=json.loads(request_path.read_text())
n=2*(4*(req["physics_request"]["lmax"]+1)+1)
end=[0.0]*n
end[-2:]=[1.25,-0.5]
digest=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
result={{"schema":"PHYS70_OPTIMIZED_RESULT_V1","complete":MODE!="partial",
 "request":req,"B":27,"T":65,"k":0.7,"eta_C":"-10/7","m":0,"target":[21,20],
 "clock":"tau=65-r;0..38","q_scale":"2^80","d2_scale":"2^160",
 "status":"PARTIAL_INTEGRATION" if MODE=="partial" else {runner.SUCCESS_STATUS!r},
 "request_sha256":digest(request_path),"seed_sha256":digest(seed_path),"source_sha256":digest(source_path),
 "engine":req["engine"],"upstream_commit":req["physics_request"]["upstream_commit"],"HH_R10":"OFF",
 "endpoint":{{"d2":{{"real":math.ldexp(1.25,-160),"imag":math.ldexp(-0.5,-160)}}}},
 "observed_times_tau":[0,38],"observed_states_scaled":[[0.0]*n,end],
 "accepted_steps":1,"rejected_steps":0,"attempts":1,"state_reuses":0,
 "counters":{{"fixture_only":"NONPHYSICAL_TEST_FIXTURE"}},
 "integration_elapsed_seconds":0.0,"test_fixture":True}}
print(json.dumps(result))
if MODE=="nonzero": sys.exit(7)
'''
        path.write_text(program)
        path.chmod(0o755)
        return path

    def args(self, out="run", extra=(), binary=None):
        return runner.parser().parse_args([
            "--request", str(self.req), "--out", str(self.base / out),
            "--source", str(runner.DEFAULT_SOURCE), "--seed", str(self.seed),
            "--binary", str(binary or self.binary), "--timeout", "3", "--memory-gib", "1",
            *extra])

    def snapshot(self, directory):
        return {str(p.relative_to(directory)): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in directory.rglob("*") if p.is_file()}

    def test_exact_request_bytes_and_immutable_completed_resume(self):
        out = self.base / "run"
        result = runner.run(self.args(extra=["--run"]))
        self.assertEqual(result["status"], "COMPLETED_NATIVE_APPLICATION")
        self.assertEqual((out / "REQUEST.json").read_bytes(), self.req.read_bytes())
        self.assertEqual(runner.read(out / "RESULT.json")["request_sha256"], runner.sha(self.req))
        before = self.snapshot(out)
        marker = self.marker.read_bytes()
        with mock.patch.object(runner, "execute", side_effect=AssertionError("resume launched process")), \
             mock.patch.object(runner, "create_bytes", side_effect=AssertionError("resume wrote a file")):
            resumed = runner.run(self.args(extra=["--resume", "--run"]))
        self.assertEqual((resumed["new_integrations"], resumed["files_written"]), (0, 0))
        self.assertEqual(before, self.snapshot(out))
        self.assertEqual(marker, self.marker.read_bytes())

    def test_existing_directory_requires_resume(self):
        runner.run(self.args(extra=["--run"]))
        before = self.snapshot(self.base / "run")
        with self.assertRaises(FileExistsError):
            runner.run(self.args(extra=["--run"]))
        self.assertEqual(before, self.snapshot(self.base / "run"))

    def test_resume_rejects_changed_request_bytes_binary_seed_and_engine(self):
        runner.run(self.args(extra=["--run"]))
        original = self.req.read_bytes()
        self.req.write_bytes(original + b"\n")
        with self.assertRaises(ValueError):
            runner.run(self.args(extra=["--resume"]))
        self.req.write_bytes(original)
        old_binary = self.binary.read_bytes()
        self.binary.write_bytes(old_binary + b"\n# changed binary fixture\n")
        with self.assertRaises(ValueError):
            runner.run(self.args(extra=["--resume"]))
        self.binary.write_bytes(old_binary)
        seed_bytes = self.seed.read_bytes()
        self.seed.write_bytes(seed_bytes + b"# changed seed bytes\n")
        with self.assertRaises(ValueError):
            runner.run(self.args(extra=["--resume"]))
        self.seed.write_bytes(seed_bytes)
        with mock.patch.object(runner, "engine_identity", return_value={"test_fixture": "e" * 64}), \
             self.assertRaises(ValueError):
            runner.run(self.args(extra=["--resume"]))
        self.assertEqual(self.marker.read_text().count("fixture invocation"), 1)

    def test_resume_detects_result_tampering(self):
        runner.run(self.args(extra=["--run"]))
        path = self.base / "run/RESULT.json"
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "checksums"):
            runner.run(self.args(extra=["--resume"]))

    def test_resume_requires_successful_process_receipt_even_with_updated_checksums(self):
        runner.run(self.args(extra=["--run"]))
        out = self.base / "run"
        integration = runner.read(out / "INTEGRATE_NATIVE.EXECUTION.json")
        integration["exit_code"] = 9
        (out / "INTEGRATE_NATIVE.EXECUTION.json").write_text(json.dumps(integration))
        receipt = runner.read(out / "EXECUTION.json")
        receipt["commands"] = [integration]
        (out / "EXECUTION.json").write_text(json.dumps(receipt))
        (out / "CHECKSUMS.json").write_text(json.dumps({
            "schema": "PHYS70_EXECUTION_CHECKSUMS_V1", "files": runner.payload_hashes(out)}))
        with self.assertRaisesRegex(ValueError, "invocation receipt"):
            runner.run(self.args(extra=["--resume"]))

    def test_partial_output_and_failure_are_retained_and_not_resumed(self):
        binary = self.make_binary("partial")
        with self.assertRaisesRegex(ValueError, "partial"):
            runner.run(self.args(binary=binary, extra=["--run"]))
        out = self.base / "run"
        self.assertFalse(runner.read(out / "RESULT.json")["complete"])
        self.assertEqual(runner.read(out / "EXECUTION.json")["status"],
                         "FAILED_OR_PARTIAL_WITH_PRESERVED_EVIDENCE")
        before = self.snapshot(out)
        with self.assertRaisesRegex(ValueError, "only completed"):
            runner.run(self.args(binary=binary, extra=["--resume", "--run"]))
        self.assertEqual(before, self.snapshot(out))

    def test_nonzero_exit_never_admits_complete_looking_output(self):
        with self.assertRaises(RuntimeError):
            runner.run(self.args(binary=self.make_binary("nonzero"), extra=["--run"]))
        out = self.base / "run"
        self.assertTrue(runner.read(out / "RESULT.json")["complete"])
        self.assertEqual(runner.read(out / "INTEGRATE_NATIVE.EXECUTION.json")["exit_code"], 7)
        self.assertEqual(runner.read(out / "EXECUTION.json")["status"],
                         "FAILED_OR_PARTIAL_WITH_PRESERVED_EVIDENCE")

    def test_non_json_failure_preserves_stderr_without_fabricated_result(self):
        with self.assertRaises(RuntimeError):
            runner.run(self.args(binary=self.make_binary("error"), extra=["--run"]))
        out = self.base / "run"
        self.assertFalse((out / "RESULT.json").exists())
        self.assertIn("NONPHYSICAL failure fixture", (out / "INTEGRATE_NATIVE.stderr.txt").read_text())

    def test_wall_limit_terminates_child_and_preserves_receipt(self):
        with self.assertRaises(RuntimeError):
            runner.run(self.args(binary=self.make_binary("timeout"), extra=["--run", "--timeout", "1"]))
        execution = runner.read(self.base / "run/INTEGRATE_NATIVE.EXECUTION.json")
        self.assertTrue(execution["timed_out"])
        self.assertNotEqual(execution["exit_code"], 0)
        self.assertLess(execution["elapsed_seconds"], 5)

    def test_memory_limit_is_applied_in_real_child(self):
        out = self.base / "limits"
        out.mkdir()
        command = [sys.executable, "-c", "import resource,json;print(json.dumps(list(resource.getrlimit(resource.RLIMIT_AS))))"]
        receipt = runner.execute(command, out, "LIMIT_FIXTURE", os.environ.copy(), 3, 1.0)
        self.assertEqual(receipt["exit_code"], 0)
        self.assertEqual(json.loads((out / "LIMIT_FIXTURE.stdout.txt").read_text()), [1024**3, 1024**3])

    def test_preflight_make_seed_launches_no_process_or_initializer(self):
        args = self.args(extra=["--make-seed"])
        args.seed = None
        with mock.patch.object(runner, "execute", side_effect=AssertionError("preflight executed child")):
            result = runner.run(args)
        out = self.base / "run"
        self.assertEqual(result["status"], "PREFLIGHT_ONLY")
        self.assertFalse((out / "SEED_INPUT.txt").exists())
        self.assertFalse(self.marker.exists())
        self.assertEqual(runner.read(out / "EXECUTION.json")["preflight"]["special_function_calls"], 0)

    def test_existing_seed_takes_priority_over_make_seed(self):
        runner.run(self.args(extra=["--make-seed", "--run"]))
        receipt = runner.read(self.base / "run/EXECUTION.json")
        self.assertEqual(len(receipt["commands"]), 1)
        self.assertEqual((self.base / "run/SEED_INPUT.txt").read_bytes(), self.seed.read_bytes())

    def test_wrong_source_and_bad_limits_fail_before_output_creation(self):
        wrong = self.base / "wrong.npz"
        wrong.write_bytes(b"NONPHYSICAL wrong-source fixture")
        for extra in (["--source", str(wrong)], ["--memory-gib", "0.5"], ["--timeout", "0"]):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                runner.run(self.args(extra=extra))
            self.assertFalse((self.base / "run").exists())

    def test_locked_build_command_and_external_binary_path(self):
        target = self.base / "target"
        cargo = self.base / "fixture_cargo"
        rustc = self.base / "fixture_rustc"
        rustc.write_text(f'#!{sys.executable}\nprint("NONPHYSICAL Rust version fixture")\n')
        rustc.chmod(0o755)
        cargo.write_text(f'''#!{sys.executable}
# NONPHYSICAL build fixture; no Rust compilation occurs.
import pathlib,shutil,sys
if sys.argv[1]=="build":
 assert "--locked" in sys.argv and "--release" in sys.argv and "--offline" in sys.argv
 assert sys.argv[sys.argv.index("--jobs")+1]=="1"
 target=pathlib.Path(sys.argv[sys.argv.index("--target-dir")+1])/"release"
 target.mkdir(parents=True)
 shutil.copy2({str(self.binary)!r},target/{runner.BINARY_NAME!r})
else: print("NONPHYSICAL Cargo version fixture")
''')
        cargo.chmod(0o755)
        args = self.args(extra=["--run", "--offline", "--target-dir", str(target),
                                "--cargo", str(cargo), "--rustc", str(rustc)])
        args.binary = None
        self.assertEqual(runner.run(args)["status"], "COMPLETED_NATIVE_APPLICATION")
        receipt = runner.read(self.base / "run/EXECUTION.json")
        self.assertEqual(len(receipt["commands"]), 4)
        self.assertEqual(receipt["identity"]["binary_sha256"], runner.sha(self.binary))
        self.assertEqual(receipt["commands"][-1]["command"][1], "run")


if __name__ == "__main__":
    unittest.main()
