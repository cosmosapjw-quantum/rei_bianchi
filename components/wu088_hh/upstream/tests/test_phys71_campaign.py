"""Functional tests using manufactured panels, never physical D3 integrations."""
from copy import deepcopy
from dataclasses import asdict
from fractions import Fraction as F
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

from flint import acb, arb, ctx
from wu088_hh import phys71_campaign as campaign
from wu088_hh.phys67_coulomb_certificate import complex_ball_record, dyadic_ball
from wu088_hh.phys71_d3 import D3Request, rational_record
from wu088_hh.phys71_inherit import InheritedPanel, InheritedProfiles, dyadic

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("phys71_ncp_tested", REPO/"scripts/phys71_ncp.py")
ncp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ncp)


def manufactured_prepared():
    panels = tuple(InheritedPanel(i, F(65)-F(2*i+1,4), F(65)-F(i+1,2),
                                  F(65)-F(i,2), {}, {}, {}) for i in range(76))
    inherited = InheritedProfiles(panels, {"families": [
        {"family": label, "panels": [{"payload_sha256": campaign.digest([label, i])}
                                       for i in range(76)]} for label in ("LOW_TEST", "BAND_TEST")]})
    request = D3Request()
    binding = {"schema": "MANUFACTURED_TEST_ONLY", "request": asdict(request), "HH_R10": "OFF"}
    return campaign.PreparedCampaign(inherited, request, binding, campaign.digest(binding))


def manufactured_builder(calls):
    def build(panel, carry, request):
        index = 75-panel.index
        calls.append((index, ctx.prec))
        # Detect accidental 53-bit summation: 1 + 2^-300 - 1 must retain 2^-300.
        increment = (acb(1) if index == 0 else acb(1)/(1 << 300)
                     if index == 1 else acb(-1) if index == 2 else acb(0))
        right = {p: carry[p]+acb(1)/(1 << 200) for p in campaign.DIRECTED_PAIRS}
        rows = [{"external": a, "j": j,
                 "P_left": complex_ball_record(carry[(a,j)]),
                 "P_right": complex_ball_record(right[(a,j)]),
                 "P_center": complex_ball_record((carry[(a,j)]+right[(a,j)])/2),
                 "S_majorant": dyadic_ball(arb(1)), "S_panel_remainder": dyadic_ball(arb(0)),
                 "U_disk_majorant": dyadic_ball(arb(1))} for a,j in campaign.DIRECTED_PAIRS]
        payload = {"schema": "PHYS71_D3_PANEL_V1", "inherited_index": panel.index,
                   "forward_index": index, "left": str(panel.left), "center": str(panel.center),
                   "right": str(panel.right), "all_modes": list(range(37)),
                   "D3_increment": complex_ball_record(increment),
                   "D3_increment_error_l1": rational_record(F(0)),
                   "integrand_disk_majorant": dyadic_ball(arb(1)),
                   "integrand_panel_remainder": dyadic_ball(arb(0)),
                   "source_response_carries": rows, "new_D1_or_D2_integrations": 0,
                   "HH_R10": "OFF"}
        return right, increment, payload
    return build


def snapshot(directory):
    import hashlib
    return {str(p.relative_to(directory)): (p.stat().st_size, p.stat().st_mtime_ns,
            hashlib.sha256(p.read_bytes()).hexdigest()) for p in directory.rglob("*") if p.is_file()}


class CampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.out = cls.root/"complete_manufactured"
        cls.prepared = manufactured_prepared()
        cls.calls = []
        with patch.object(campaign, "build_d3_panel", manufactured_builder(cls.calls)):
            cls.result = campaign.run_campaign(cls.prepared, cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_complete_sum_uses_384_bits_and_restores_precision(self):
        self.assertEqual(self.calls, [(i,384) for i in range(76)])
        self.assertEqual(self.result["computed"], 76)
        self.assertTrue(self.result["record"]["absolute_goal_met"])
        midpoint = dyadic(self.result["record"]["D3_B_cutoff"]["real"]["midpoint"])
        self.assertEqual(midpoint, F(1, 1 << 300))
        old_precision = ctx.prec
        with patch.object(campaign, "build_d3_panel", side_effect=AssertionError("unexpected callback")):
            campaign.run_campaign(self.prepared, self.out, resume=True)
        self.assertEqual(ctx.prec, old_precision)

    def test_completed_resume_is_strictly_readonly_and_zero_callbacks(self):
        before = snapshot(self.root)
        with patch.object(campaign, "build_d3_panel", side_effect=AssertionError("unexpected callback")), \
             patch.object(campaign, "_campaign_lock", side_effect=AssertionError("unexpected lock")):
            result = campaign.run_campaign(self.prepared, self.out, resume=True)
        self.assertEqual(result["computed"], 0)
        self.assertEqual(result["reused"], 76)
        self.assertTrue(result["read_only"])
        self.assertEqual(before, snapshot(self.root))

    def test_partial_pilot_and_resume_preserve_first_panel_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)/"pilot"
            calls = []
            with patch.object(campaign, "build_d3_panel", manufactured_builder(calls)):
                first = campaign.run_campaign(self.prepared, out, max_new_panels=1)
                before = snapshot(out)
                second = campaign.run_campaign(self.prepared, out, resume=True, max_new_panels=2)
            self.assertEqual(first["record"]["status"], "PARTIAL_CHECKPOINT")
            self.assertEqual(first["record"]["panels_complete"], 1)
            self.assertEqual(second["computed"], 2)
            self.assertEqual(second["reused"], 1)
            self.assertEqual(calls, [(0,384),(1,384),(2,384)])
            after = snapshot(out)
            self.assertTrue(all(after[k] == v for k,v in before.items()))
            p = campaign.read(out/"panel_0000.json")["payload"]
            self.assertEqual((p["inherited_index"],p["left"],p["right"]), (75,"27","55/2"))

    def test_existing_run_requires_explicit_resume(self):
        with self.assertRaises(FileExistsError), patch.object(campaign, "build_d3_panel",
                                                           side_effect=AssertionError("callback")):
            campaign.run_campaign(self.prepared, self.out)

    def test_mismatched_binding_refuses_saved_data(self):
        binding = {**self.prepared.binding, "different_engine": True}
        other = campaign.PreparedCampaign(self.prepared.inherited, self.prepared.request,
                                           binding, campaign.digest(binding))
        with self.assertRaisesRegex(ValueError,"fingerprint mismatch"):
            campaign.inspect_saved(other,self.out)

    def test_saved_payload_hash_and_carry_are_both_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"modified"
            with patch.object(campaign,"build_d3_panel",manufactured_builder([])):
                campaign.run_campaign(self.prepared,out,max_new_panels=1)
            path=out/"panel_0000.json"
            saved=campaign.read(path)
            saved["payload"]["source_response_carries"][0]["P_left"]=complex_ball_record(acb(2))
            path.write_text(json.dumps(saved))
            with self.assertRaisesRegex(ValueError,"payload SHA256"):
                campaign.inspect_saved(self.prepared,out)
            saved["payload_sha256"]=campaign.digest(saved["payload"])
            path.write_text(json.dumps(saved))
            with self.assertRaisesRegex(ValueError,"does not enclose predecessor"):
                campaign.inspect_saved(self.prepared,out)

    def test_invalid_new_panel_limit_and_zero_limit_never_create_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"absent"
            for value in (True,1.5,-1,77):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    campaign.run_campaign(self.prepared,out,max_new_panels=value)
            result=campaign.run_campaign(self.prepared,out,max_new_panels=0)
            self.assertTrue(result["read_only"])
            self.assertFalse(out.exists())

    def test_create_only_json_does_not_overwrite_existing_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"one.json"
            campaign.create_json(path,{"first":1})
            before=path.read_bytes()
            with self.assertRaises(FileExistsError):
                campaign.create_json(path,{"second":2})
            self.assertEqual(path.read_bytes(),before)
            self.assertEqual([p.name for p in path.parent.iterdir()],["one.json"])

    def test_default_cli_preflight_is_no_write_no_child(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"uncreated"
            with patch.object(ncp,"prepare_campaign",return_value=self.prepared), \
                 patch.object(ncp,"run_child",side_effect=AssertionError("unexpected child")), \
                 contextlib.redirect_stdout(io.StringIO()) as stream:
                code=ncp.main(["--out",str(out)])
            self.assertEqual(code,0)
            self.assertEqual(json.loads(stream.getvalue())["Coulomb_evaluations"],0)
            self.assertFalse(out.exists())

    def test_completed_cli_resume_does_not_spawn_or_write_logs(self):
        before=snapshot(self.root)
        with patch.object(ncp,"prepare_campaign",return_value=self.prepared), \
             patch.object(ncp,"run_child",side_effect=AssertionError("unexpected child")), \
             contextlib.redirect_stdout(io.StringIO()):
            code=ncp.main(["--run","--resume","--out",str(self.out)])
        self.assertEqual(code,0)
        self.assertEqual(before,snapshot(self.root))


class ResourceWorkerTests(unittest.TestCase):
    def test_limits_and_thread_cap_are_applied_to_a_real_small_child(self):
        with tempfile.TemporaryDirectory() as tmp:
            logs=Path(tmp)/"limits"
            script=("import json,os,resource;print(json.dumps({'as':resource.getrlimit(resource.RLIMIT_AS),"
                    "'cpu':resource.getrlimit(resource.RLIMIT_CPU),'nice':os.getpriority(os.PRIO_PROCESS,0),"
                    "'threads':os.environ['OPENBLAS_NUM_THREADS']}))")
            r=ncp.run_child([sys.executable,"-c",script],logs,timeout=5,memory_gib=1,cpu_seconds=3,nice=10)
            self.assertEqual(r["exit_code"],0)
            observed=json.loads((logs/"STDOUT.jsonl").read_text())
            self.assertEqual(observed["as"],[r["address_space_bytes_limit"]]*2)
            self.assertEqual(observed["cpu"],[r["cpu_seconds_limit"]]*2)
            self.assertGreaterEqual(observed["nice"],10)
            self.assertEqual(observed["threads"],"1")

    def test_timeout_kills_owned_process_group_and_preserves_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            logs=Path(tmp)/"timeout"
            r=ncp.run_child([sys.executable,"-c","import time;time.sleep(10)"],logs,
                            timeout=1,memory_gib=1,cpu_seconds=3,nice=10)
            self.assertTrue(r["timed_out"])
            self.assertLess(r["exit_code"],0)
            self.assertTrue((logs/"CHILD_RECEIPT.json").is_file())
            self.assertLess(r["elapsed_seconds"],5)

    def test_invalid_resource_limits_fail_before_writing_logs(self):
        with tempfile.TemporaryDirectory() as tmp:
            logs=Path(tmp)/"invalid"
            for kwargs in ({"timeout":True},{"memory_gib":0},{"cpu_seconds":1.5},{"nice":-1}):
                with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):
                    ncp.run_child([sys.executable,"-c","pass"],logs,**kwargs)
            self.assertFalse(logs.exists())


class ReviewRegressionTests(unittest.TestCase):
    """Boundary review checks; no inherited or new physical solver callbacks."""
    def certificate_fixture(self):
        prepared = manufactured_prepared()
        zero = complex_ball_record(acb(0))
        panels = [{"payload": {"D3_increment": zero}, "receipt": {"index": i}}
                  for i in range(76)]
        return prepared, panels, campaign._certificate(prepared, panels)

    @staticmethod
    def rehash(cert):
        cert.pop("certificate_payload_sha256", None)
        cert["certificate_payload_sha256"] = campaign.digest(cert)
        return cert

    def test_rehashed_false_full_box_is_rejected(self):
        prepared, panels, cert = self.certificate_fixture()
        cert["D3_full_radial_all_angular_box"] = complex_ball_record(acb(0))
        with self.assertRaisesRegex(ValueError, "omits an error term"):
            campaign._verify_certificate(self.rehash(cert), prepared, panels)

    def test_rehashed_duplicate_identity_counts_and_scope_are_rejected(self):
        prepared, panels, cert = self.certificate_fixture()
        changes = {"source_sha256": "0"*64, "coefficient": "D3=Z'''(0)",
                   "panel_count_required": 75, "precision_bits": 53,
                   "new_D1_or_D2_integrations": 1, "inherited_profile_payloads_reused": 149,
                   "radial_cutoff_bound_reused_from_max_L": 36,
                   "PHYS63_qualitative_existence": "OPEN"}
        for field, value in changes.items():
            changed = deepcopy(cert)
            changed[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                campaign._verify_certificate(self.rehash(changed), prepared, panels)

    def test_campaign_created_between_inspection_and_lock_requires_resume(self):
        prepared = manufactured_prepared()
        calls = []
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)/"race"
            @contextlib.contextmanager
            def create_before_lock(_output):
                out.mkdir()
                campaign.create_json(out/"REQUEST.json", {
                    "schema": "PHYS71_CAMPAIGN_REQUEST_V1", "binding": prepared.binding,
                    "fingerprint": prepared.fingerprint, "HH_R10": "OFF"})
                yield
            with patch.object(campaign, "_campaign_lock", create_before_lock), \
                 patch.object(campaign, "build_d3_panel", manufactured_builder(calls)), \
                 self.assertRaises(FileExistsError):
                campaign.run_campaign(prepared, out, max_new_panels=1)
            self.assertEqual(calls, [])

    def test_cold_cli_import_creates_no_project_bytecode(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp)/"cache"
            env = os.environ.copy()
            env.pop("PYTHONDONTWRITEBYTECODE", None)
            env["PYTHONPYCACHEPREFIX"] = str(cache)
            result = subprocess.run([sys.executable, str(REPO/"scripts/phys71_ncp.py"), "--help"],
                                    env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            project_bytecode = [str(p) for p in cache.rglob("*.pyc")
                                if "wu088_hh" in p.parts]
            self.assertEqual(project_bytecode, [])

    @unittest.skipUnless(Path("/proc").is_dir(), "Linux process-state readback required")
    def test_timeout_kills_term_ignoring_grandchild_and_sets_bytecode_guard(self):
        grandchild = ("import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);"
                      "print('ready',flush=True);time.sleep(30)")
        script = ("import subprocess,sys,time,json,os;"
                  f"p=subprocess.Popen([sys.executable,'-c',{grandchild!r}],stdout=subprocess.PIPE,text=True);"
                  "p.stdout.readline();print(json.dumps({'pid':p.pid,"
                  "'bytecode_guard':os.environ.get('PYTHONDONTWRITEBYTECODE')}),flush=True);time.sleep(30)")
        def running(pid):
            try:
                return Path(f"/proc/{pid}/stat").read_text().split(") ",1)[1].split()[0] != "Z"
            except FileNotFoundError:
                return False
        pid = None
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp)/"descendant"
            try:
                env = {key: value for key, value in os.environ.items()
                       if key != "PYTHONDONTWRITEBYTECODE"}
                with patch.dict(os.environ, env, clear=True):
                    receipt = ncp.run_child([sys.executable,"-c",script], logs,
                                           timeout=1,memory_gib=1,cpu_seconds=3,nice=10)
                observed = json.loads((logs/"STDOUT.jsonl").read_text())
                pid = observed["pid"]
                self.assertTrue(receipt["timed_out"])
                deadline = time.monotonic()+1
                while running(pid) and time.monotonic() < deadline:
                    time.sleep(0.02)
                with self.subTest(boundary="descendant_cleanup"):
                    self.assertFalse(running(pid), "TERM-ignoring owned descendant survived")
                with self.subTest(boundary="bytecode_environment"):
                    self.assertEqual(observed["bytecode_guard"], "1")
            finally:
                if pid is not None and running(pid):
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass

    def test_timeout_always_kills_group_after_direct_child_exits(self):
        child = Mock(pid=123456789)
        child.wait.side_effect = [subprocess.TimeoutExpired(["manufactured-child"],1),
                                  -signal.SIGTERM, -signal.SIGTERM]
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(ncp.subprocess, "Popen", return_value=child), \
             patch.object(ncp.platform, "platform", return_value="MANUFACTURED_TEST_ONLY"), \
             patch.object(ncp.os, "killpg") as kill_group:
            ncp.run_child(["manufactured-child"], Path(tmp)/"branch",
                          timeout=1,memory_gib=1,cpu_seconds=3,nice=10)
        self.assertEqual([tuple(c.args) for c in kill_group.call_args_list],
                         [(child.pid,signal.SIGTERM), (child.pid,signal.SIGKILL)])


if __name__=="__main__":
    unittest.main()
