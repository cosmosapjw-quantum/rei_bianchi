"""Independent band integrals and restricted execution/resume contracts.

These manufactured models exercise new assembly only.  They do not rerun any
completed original-physics PHYS68 integration or NCP execution.
"""
from contextlib import nullcontext
from dataclasses import asdict, replace
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from flint import acb, arb, ctx
import pytest

import wu088_hh.phys68_profiles as old
import wu088_hh.phys69_band_profiles as p
from wu088_hh.phys68_taylor import TaylorDisk, rational_ball


def small_request(**kwargs):
    base = p.BandRequest(min_ell=29, max_ell=30, outer="28", degree=32,
                         precision_bits=256, coefficient_bits=512,
                         d2_numerical_absolute_goal="1e-6")
    return replace(base, **kwargs)


@pytest.fixture
def constant_model(monkeypatch):
    seen = {"Coulomb_modes": [], "pairs": []}
    def h(ell, center, degree, radius, bits):
        seen["Coulomb_modes"].append(ell)
        return TaylorDisk(F(center), F(radius), (acb(1),)+(acb(0),)*degree,
                          arb(1), bits, ell, "manufactured F=1")
    def v(a, b, center, degree, *args):
        seen["pairs"].append((a, b))
        return (acb(rational_ball(F((a+1)*(b+1), 2048))),)+(acb(0),)*degree
    monkeypatch.setattr(p, "coulomb_taylor", h)
    monkeypatch.setattr(p, "angular_taylor_coefficients", v)
    monkeypatch.setattr(p, "angular_complex_disk_bound", lambda *args: arb(1))
    monkeypatch.setattr(p, "local_coulomb_majorant", lambda *args: arb(1))
    monkeypatch.setattr(p, "source_guard", lambda *args: p.SOURCE_SHA)
    monkeypatch.setattr(p, "engine_identity", lambda: {"manufactured_engine": "v1"})
    monkeypatch.setattr(old, "run_profiles", lambda *args, **kwargs: pytest.fail("old integration executed"))
    monkeypatch.setattr(old, "build_panel", lambda *args, **kwargs: pytest.fail("old full-mode panel executed"))
    return (lambda a, b: F((a+1)*(b+1), 2048)), seen


def test_default_scope_is_disjoint_and_complete():
    request = p.BandRequest().validate()
    assert request.intermediate_modes == tuple(range(29, 37))
    assert request.coulomb_modes == (20, 21, *range(29, 37))
    assert len(request.pairs) == 16 and request.panel_count == 76
    assert all(p.pair_key(a, j) in request.pairs for a in (20, 21) for j in range(29, 37))
    assert request.d2_numerical_absolute_goal == "1e-63"


@pytest.mark.parametrize("changes", [
    {"min_ell": 28}, {"min_ell": True}, {"min_ell": 37},
    {"max_ell": 65}, {"ell": 37}, {"outer": 65.0}, {"outer": True},
    {"d2_numerical_absolute_goal": 1e-63}, {"d2_numerical_absolute_goal": True},
    {"half_width": "3/10"}, {"zero_free_radius": "1/4"},
    {"coefficient_bits": 128}, {"d2_numerical_absolute_goal": "0"},
])
def test_invalid_or_completed_intermediate_band_refused(changes):
    with pytest.raises((TypeError, ValueError)):
        replace(p.BandRequest(), **changes).validate()


def test_manufactured_band_exact_integral_and_selected_modes(constant_model):
    value, seen = constant_model
    request = small_request()
    q = {pair: acb(0) for pair in request.pairs}
    with ctx.workprec(256):
        total = acb(0)
        for c in (F(111, 4), F(109, 4)):
            panel = p.build_band_panel(request, c, q)
            for pair in request.pairs:
                for offset in (F(-1, 4), F(0), F(1, 4)):
                    exact = value(*pair)*(28-c-offset)
                    assert panel.evaluate_first_born(*pair, offset).contains(rational_ball(exact))
            assert [t["j"] for t in panel.record["second_Born_terms"]] == [29, 30]
            total += panel.second_born_increment
            q = panel.q_left
        exact = sum((value(21, j)*value(20, j) for j in (29, 30)), F(0))/3
        assert total.contains(rational_ball(exact))
        assert not total.contains(rational_ball(2*exact))
        assert p.norm_radius_l1(total) < F(1, 10**6)
    assert set(seen["Coulomb_modes"]) == {20, 21, 29, 30}
    assert set(seen["pairs"]) == set(request.pairs)
    assert len(seen["Coulomb_modes"]) == 8


def test_complex_band_is_bilinear_with_no_extra_factor(monkeypatch, constant_model):
    request = small_request()
    monkeypatch.setattr(p, "angular_taylor_coefficients",
                        lambda a, b, c, n, *args: (acb(0, 1),)+(acb(0),)*n)
    q = {pair: acb(0) for pair in request.pairs}
    with ctx.workprec(256):
        total = acb(0)
        for c in (F(111, 4), F(109, 4)):
            panel = p.build_band_panel(request, c, q)
            total += panel.second_born_increment
            q = panel.q_left
        assert total.contains(rational_ball(F(-2, 3)))
        assert not total.contains(rational_ball(F(2, 3)))
        assert not total.contains(rational_ball(F(-4, 3)))


def test_missing_band_pair_refused(constant_model):
    request = small_request()
    q = {pair: acb(0) for pair in request.pairs}
    q.pop(next(iter(q)))
    with pytest.raises(ValueError, match="every requested"):
        p.build_band_panel(request, F(111, 4), q)


def test_zero_free_failure_is_explicit_and_context_is_restored(monkeypatch, constant_model):
    def bad(ell, c, n, r, bits):
        return TaylorDisk(F(c), F(r), (acb(0), acb(1))+(acb(0),)*(n-1), arb(10), bits, ell)
    monkeypatch.setattr(p, "coulomb_taylor", bad)
    request = small_request()
    before = (ctx.prec, ctx.cap)
    with pytest.raises(p.ProfileEnclosureFailure, match="UNRESOLVED_ZERO_FREE_BOUND"):
        p.build_band_panel(request, F(111, 4), {pair: acb(0) for pair in request.pairs})
    assert (ctx.prec, ctx.cap) == before


def test_preflight_has_no_radial_integral(monkeypatch, constant_model):
    monkeypatch.setattr(p, "build_band_panel", lambda *a: pytest.fail("preflight integrated a panel"))
    result = p.preflight("manufactured", small_request())
    assert result["status"] == "PREFLIGHT_ONLY_PASS"
    assert result["radial_panels"] == 0 and result["intermediate_sum"] == [29, 30]


def test_resume_only_computes_missing_new_band_panels(tmp_path, monkeypatch, constant_model):
    value, _ = constant_model
    request = small_request()
    first = p.run_band_profiles("manufactured", tmp_path, request, max_new_panels=1)
    original = (tmp_path/"panel_0000.json").read_bytes()
    assert first["status"] == "PARTIAL_CHECKPOINT_NO_FINAL_CERTIFICATE"
    assert first["panels_computed_this_call"] == 1 and "D2_B_cutoff" not in first
    second = p.run_band_profiles("manufactured", tmp_path, request, resume=True)
    assert second["panels_reused_this_call"] == 1 and second["panels_computed_this_call"] == 1
    assert (tmp_path/"panel_0000.json").read_bytes() == original
    assert second["status"] == "CERTIFIED_BAND_NUMERICAL_GOAL_MET"
    exact = sum((value(21, j)*value(20, j) for j in (29, 30)), F(0))/3
    with ctx.workprec(256):
        assert p.restore_complex_ball(second["D2_B_cutoff"]).contains(rational_ball(exact))
    error = second["D2_numerical_absolute_error_l1"]
    assert F(int(error["numerator"]), int(error["denominator"])) < F(1, 10**6)
    assert not second["radial_cutoff_error_included"]
    assert not second["excluded_angular_error_included"]
    assert not second["original_driven_xi_certified"]
    assert second["completed_PHYS68_intermediate_0_to_28_integrations"] == 0
    assert second["m"] == 0 and second["HH_R10"] == "OFF"
    monkeypatch.setattr(p, "build_band_panel", lambda *a: pytest.fail("completed panel repeated"))
    third = p.run_band_profiles("manufactured", tmp_path, request, resume=True)
    assert third["panels_reused_this_call"] == 2 and third["panels_computed_this_call"] == 0


def test_existing_directory_and_engine_changes_are_refused(tmp_path, monkeypatch, constant_model):
    request = small_request()
    p.run_band_profiles("manufactured", tmp_path, request, max_new_panels=0)
    with pytest.raises(FileExistsError):
        p.run_band_profiles("manufactured", tmp_path, request)
    with pytest.raises(ValueError, match="fingerprint"):
        p.run_band_profiles("manufactured", tmp_path, replace(request, degree=33), resume=True)
    monkeypatch.setattr(p, "engine_identity", lambda: {"manufactured_engine": "v2"})
    with pytest.raises(ValueError, match="fingerprint"):
        p.run_band_profiles("manufactured", tmp_path, request, resume=True)


@pytest.mark.parametrize("mutation", ["hash", "coverage", "carry"])
def test_saved_panel_corruption_is_refused(tmp_path, constant_model, mutation):
    request = small_request()
    p.run_band_profiles("manufactured", tmp_path, request)
    path = tmp_path/("panel_0001.json" if mutation == "carry" else "panel_0000.json")
    saved = json.loads(path.read_text())
    if mutation == "hash":
        saved["payload"]["center"] = "99"
        message = "payload hash"
    else:
        if mutation == "coverage":
            saved["payload"]["full_intermediate_sum"] = [30]
            message = "coverage"
        else:
            saved["payload"]["pairs"][0]["q_right"] = p.complex_ball_record(acb(0))
            message = "does not enclose"
        saved["payload_sha256"] = hashlib.sha256(p._canonical(saved["payload"])).hexdigest()
    path.write_text(json.dumps(saved))
    with pytest.raises(ValueError, match=message):
        p.run_band_profiles("manufactured", tmp_path, request, resume=True)


def test_valid_enclosure_does_not_imply_requested_accuracy(tmp_path, constant_model):
    request = small_request(degree=2, d2_numerical_absolute_goal="1e-63")
    result = p.run_band_profiles("manufactured", tmp_path, request)
    assert result["scientific_execution"] == "COMPLETE"
    assert result["status"] == "VALID_BAND_ENCLOSURE_GOAL_NOT_MET"
    assert not result["numerical_absolute_goal_met"]


@pytest.mark.parametrize("part,field,value", [
    ("midpoint", "mantissa", 1.9), ("midpoint", "mantissa", True),
    ("midpoint", "mantissa", "1.0"), ("midpoint", "exponent2", 1.0),
    ("radius", "exponent2", False), ("radius", "mantissa", "-1"),
])
def test_dyadic_json_cannot_truncate_float_or_bool(part, field, value):
    record = p.complex_ball_record(acb(0))
    record["real"][part][field] = value
    with pytest.raises(ValueError, match="dyadic"):
        p.restore_complex_ball(record)


@pytest.fixture
def cli_module(monkeypatch):
    path = Path(__file__).resolve().parents[1]/"scripts/phys69_band_profiles.py"
    monkeypatch.syspath_prepend(str(path.parent))
    spec = importlib.util.spec_from_file_location("phys69_band_cli_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cli_complete_request_and_output_binding(tmp_path, cli_module):
    path = tmp_path/"request.json"
    path.write_text(json.dumps(asdict(p.BandRequest())))
    assert cli_module.read_request(path) == p.BandRequest()
    bad = asdict(p.BandRequest()); bad.pop("min_ell")
    path.write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="complete"):
        cli_module.read_request(path)
    out = tmp_path/"out"; out.mkdir()
    (out/"unbound.txt").write_text("not an execution receipt")
    with pytest.raises(ValueError, match="no bound request"):
        cli_module.inspect_output(out, {}, True)


@pytest.mark.parametrize("returncode,timed_out,append_receipt,expected", [
    (0, False, True, 0), (0, False, False, 1), (0, True, True, 1), (2, False, True, 1),
])
def test_wrapper_requires_current_child_success_receipt(tmp_path, monkeypatch, cli_module,
                                                       returncode, timed_out, append_receipt, expected):
    binding = {"request": asdict(p.BandRequest()), "HH_R10": "OFF"}
    fingerprint = hashlib.sha256(p._canonical(binding)).hexdigest()
    monkeypatch.setattr(cli_module, "request_binding", lambda *a: binding)
    monkeypatch.setattr(cli_module, "campaign_lock", lambda *a: nullcontext())
    out = tmp_path/"campaign"
    def fake_child(command, logs, *args):
        logs.mkdir(parents=True)
        if append_receipt:
            out.mkdir(exist_ok=True)
            (out/"INVOCATIONS.jsonl").write_text(json.dumps({"fingerprint": fingerprint, "exit_code": 0})+"\n")
        return {"returncode": returncode, "timed_out": timed_out}
    monkeypatch.setattr(cli_module, "run_child", fake_child)
    assert cli_module.main(["--out", str(out), "--run"]) == expected
    receipt = next((tmp_path/"campaign_invocations").glob("*/WRAPPER_RECEIPT.json"))
    saved = json.loads(receipt.read_text())
    assert saved["child"]["returncode"] == returncode
    assert saved["HH_R10"] == "OFF" and not saved["NCP_submitted"]
