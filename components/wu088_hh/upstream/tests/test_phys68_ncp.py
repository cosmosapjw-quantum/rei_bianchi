"""Request/output refusal, actual zero-panel engine binding and process controls."""
from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("phys68_ncp", ROOT/"scripts/phys68_ncp.py")
ncp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ncp)


def binding():
    request = ncp.read_request()
    return request, ncp.binding_for(request, ncp.FROZEN_SOURCE)


def test_only_unexecuted_optional_l64_request_is_selected():
    request = ncp.read_request()
    assert request.max_ell == 64 and request.panel_count == 152
    assert len(request.pairs) == 129
    assert all(tuple(sorted((ell,j))) in request.pairs for ell in (20,21) for j in range(65))
    assert request.precision_bits == 768 and request.coefficient_bits == 2048
    assert request.half_width == "1/8" and request.zero_free_radius == "1/4"


@pytest.mark.parametrize("mutation", [
    {"max_ell": 28}, {"ell": 20}, {"outer": "55"}, {"half_width": "1/4"},
    {"degree": 80}, {"precision_bits": 384}, {"d2_absolute_goal": "1e-50"},
])
def test_unsupported_or_relaxed_request_is_refused(tmp_path, mutation):
    payload = dict(ncp.FIXED_REQUEST)
    payload.update(mutation)
    path = tmp_path/"request.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        ncp.read_request(path)


def test_request_missing_fields_is_not_filled_with_l28_defaults(tmp_path):
    path = tmp_path/"request.json"
    path.write_text('{"max_ell":64}')
    with pytest.raises(ValueError, match="complete fixed"):
        ncp.read_request(path)


def test_changed_source_fails_before_output_is_created(tmp_path):
    bad = tmp_path/"changed.npz"
    bad.write_bytes(b"not original source")
    with pytest.raises(ValueError, match="SHA256"):
        ncp.binding_for(ncp.read_request(), bad)
    assert sorted(x.name for x in tmp_path.iterdir()) == ["changed.npz"]


def test_output_name_is_full_binding_fingerprint_and_read_only(tmp_path):
    request, bound = binding()
    plan = ncp.inspect_destination(tmp_path, bound)
    assert Path(plan["output"]).name == "phys68_l64_"+ncp.digest(bound)
    assert plan["profile_request_sha256"] == ncp.digest(asdict(request))
    assert not plan["resume"] and not Path(plan["output"]).exists()


def test_nonempty_unbound_output_is_refused_before_child(tmp_path):
    _, bound = binding()
    output = Path(ncp.inspect_destination(tmp_path, bound)["output"])
    output.mkdir()
    (output/"unrelated.txt").write_text("preserve")
    with pytest.raises(ValueError, match="no bound REQUEST"):
        ncp.inspect_destination(tmp_path, bound)
    assert (output/"unrelated.txt").read_text() == "preserve"


def test_real_zero_panel_request_selects_resume_without_radial_work(tmp_path):
    from wu088_hh.phys68_profiles import run_profiles
    request, bound = binding()
    first = ncp.inspect_destination(tmp_path, bound)
    # Calls the real existing engine with max_new_panels=0. This creates only
    # request/checkpoint metadata and executes no Coulomb or radial panel.
    result = run_profiles(ncp.FROZEN_SOURCE, first["output"], request, max_new_panels=0)
    assert result["panels_computed_this_call"] == 0
    assert result["status"] == "PARTIAL_CHECKPOINT_NO_FINAL_CERTIFICATE"
    plan = ncp.inspect_destination(tmp_path, bound)
    assert plan["resume"]
    command = ncp.solver_command(plan, tmp_path/"fixed.json", ncp.FROZEN_SOURCE)
    assert command[-1] == "--resume"
    assert str(ROOT/"scripts/phys68_profiles.py") in command
    assert not list(Path(plan["output"]).glob("panel_*.json"))


def test_existing_request_fingerprint_mismatch_refused(tmp_path):
    _, bound = binding()
    output = Path(ncp.inspect_destination(tmp_path, bound)["output"])
    output.mkdir()
    (output/"REQUEST.json").write_text(json.dumps({"schema":"PHYS68_PROFILE_REQUEST_V1",
                                                 "fingerprint":"0"*64,"binding":bound}))
    with pytest.raises(ValueError, match="fingerprint mismatch"):
        ncp.inspect_destination(tmp_path, bound)


def test_same_request_under_changed_runtime_does_not_start_duplicate(tmp_path):
    _, bound = binding()
    old = json.loads(json.dumps(bound))
    old["engine"]["python"] = "different-prior-version"
    folder = tmp_path/("phys68_l64_"+ncp.digest(old))
    folder.mkdir()
    (folder/"REQUEST.json").write_text(json.dumps({"schema":"PHYS68_PROFILE_REQUEST_V1",
                                                 "fingerprint":ncp.digest(old),"binding":old}))
    with pytest.raises(ValueError, match="another engine/runtime"):
        ncp.inspect_destination(tmp_path, bound)


def test_plain_child_runs_with_single_thread_environment(tmp_path):
    expression = "import os,json; print(json.dumps({'omp':os.environ['OMP_NUM_THREADS'],'blas':os.environ['OPENBLAS_NUM_THREADS']}))"
    observed = []
    result = ncp.run_child([sys.executable, "-c", expression], tmp_path/"child", wall_seconds=10,
                           on_start=observed.append)
    assert result["returncode"] == 0 and not result["timed_out"]
    assert observed == [result["child_pid"]]
    assert json.loads((tmp_path/"child/STDOUT.jsonl").read_text()) == {"omp":"1","blas":"1"}
    assert result["ncp_resource_limits_applied"] is False


def test_owned_child_wall_timeout_is_recorded_and_reaped(tmp_path):
    result = ncp.run_child([sys.executable, "-c", "import time; time.sleep(10)"],
                           tmp_path/"timeout", wall_seconds=1)
    assert result["timed_out"] and result["returncode"] != 0
    assert result["elapsed_seconds"] < 7


def test_invalid_resource_contract_is_refused_before_any_process(tmp_path):
    with pytest.raises(ValueError, match="wall_seconds"):
        ncp.run_child([sys.executable,"-c","raise SystemExit(99)"], tmp_path/"none", wall_seconds=0)
    assert not (tmp_path/"none").exists()


def test_campaign_lock_refuses_concurrent_wrapper_and_releases(tmp_path):
    with ncp.campaign_lock(tmp_path, "a"*64):
        with pytest.raises(ValueError, match="already owns"):
            with ncp.campaign_lock(tmp_path, "a"*64):
                pytest.fail("concurrent lock admitted")
    with ncp.campaign_lock(tmp_path, "a"*64):
        pass


def test_old_success_is_not_attributed_to_child_without_a_new_invocation(tmp_path):
    path = tmp_path/"INVOCATIONS.jsonl"
    old = {"fingerprint":"a"*64,"status":"CERTIFIED_GOALS_MET"}
    path.write_text(json.dumps(old)+"\n")
    assert ncp.new_child_invocation(path, 1, "a"*64) is None
    current = {"fingerprint":"a"*64,"status":"FAILED_NO_COMPLETION_CLAIM"}
    with path.open("a") as stream:
        stream.write(json.dumps(current)+"\n")
    assert ncp.new_child_invocation(path, 1, "a"*64) == current


def test_cli_refusal_reports_no_launch_and_does_not_enter_preflight(tmp_path):
    result = __import__("subprocess").run([sys.executable, str(ROOT/"scripts/phys68_ncp.py"),
                                          "--run", "--wall-seconds", "0", "--out-root", str(tmp_path/"none")],
                                         capture_output=True, text=True, timeout=15)
    record = json.loads(result.stdout)
    assert result.returncode == 1
    assert record["status"] == "FAILED_BEFORE_LAUNCH"
    assert record["solver_started"] is False
    assert "preflight" not in record
    assert not (tmp_path/"none").exists()
