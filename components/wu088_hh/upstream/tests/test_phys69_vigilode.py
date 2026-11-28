"""Changed-client validation only; no old HH campaign or physical solver run."""
import copy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("phys69_vigilode", ROOT / "scripts/phys69_vigilode.py")
client = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(client)
REQUEST_PATH = ROOT / "research/hh_phys69_20261019/vigilode/REQUEST_L28.json"


def request():
    return json.loads(REQUEST_PATH.read_text())


def result_fixture():
    req = request()
    result = {"schema": "PHYS69_VIGILODE_RESULT_V1", "status": "COMPLETED_BINARY64_REFERENCE_NOT_CERTIFICATE",
              "request": req, "complete": True, "upstream_commit": client.UPSTREAM,
              "source_sha256": client.SOURCE_SHA, "seed_sha256": client.SEED_L28_SHA,
              "B": 27, "T": 65, "target": [21,20], "m": 0, "q_scale": "2^80", "d2_scale": "2^160",
              "HH_R10": "OFF", "observed_times_tau": [0.0,38.0],
              "observed_states_scaled": [[0.0]*234, [0.0]*234],
              "counters": {"jacobian_builds": 0, "direct_factorizations": 0, "jvp_vectors": 10},
              "attempts": 4, "accepted_steps": 3, "rejected_steps": 1,
              "endpoint": {"d2": {"real": 7.017743632815533e-48, "imag": 3.2001632223052117e-48}}}
    return result


@pytest.mark.parametrize("key,value", [
    ("lmax",True), ("lmax",65), ("angular_nodes",40), ("atol",float("nan")),
    ("rtol",True), ("initial_step",0), ("max_attempts",0), ("upstream_commit","main"), ("HH_R10","ON")])
def test_invalid_requests_fail_closed(key,value):
    req = request(); req[key] = value
    with pytest.raises(ValueError): client.validate_request(req)


def test_pinned_requests_and_saved_seed_are_accepted():
    client.validate_request(request())
    client.validate_request(json.loads((REQUEST_PATH.parent / "REQUEST_L64.json").read_text()))
    client.validate_seed(client.DEFAULT_SEED,28)
    assert client.sha(client.DEFAULT_SEED) == client.SEED_L28_SHA


def test_additional_request_key_is_rejected():
    req = request(); req["eta"] = -10/7
    with pytest.raises(ValueError): client.validate_request(req)


@pytest.mark.parametrize("mutation", ["short_states", "short_dimension", "nonfinite", "wrong_seed", "wrong_L", "false_matrix_free", "partial", "bad_ledger"])
def test_bad_native_result_cannot_pass_by_zip_truncation(mutation):
    result = result_fixture()
    if mutation == "short_states": result["observed_states_scaled"].pop()
    elif mutation == "short_dimension": result["observed_states_scaled"][1].pop()
    elif mutation == "nonfinite": result["observed_states_scaled"][1][2] = float("nan")
    elif mutation == "wrong_seed": result["seed_sha256"] = "0"*64
    elif mutation == "wrong_L": result["request"]["lmax"] = 64
    elif mutation == "false_matrix_free": result["counters"]["jacobian_builds"] = 1
    elif mutation == "partial": result["complete"] = False
    elif mutation == "bad_ledger": result["attempts"] = 3
    with pytest.raises(ValueError): client.validate_result(result,request(),client.SOURCE_SHA,client.SEED_L28_SHA)


def test_complete_result_shape_passes():
    client.validate_result(result_fixture(),request(),client.SOURCE_SHA,client.SEED_L28_SHA)


def test_exact_integer_square_root_brackets():
    for value in [Fraction(0),Fraction(4),Fraction(2),Fraction(17,31),Fraction(1,10**140)]:
        low,high = client.sqrt_bounds(value)
        assert low*low <= value <= high*high
        assert high-low <= Fraction(1,2**512)
    assert client.sqrt_bounds(Fraction(4)) == (Fraction(2),Fraction(2))


def test_saved_arb_reference_compares_without_an_integrator():
    result = result_fixture()
    comparison = client.compare_certificate(result,client.DEFAULT_CERT)
    assert comparison["goal_met"]
    assert Fraction(int(comparison["relative_error_upper"]["numerator"]),int(comparison["relative_error_upper"]["denominator"])) < Fraction(1,10**14)
    assert not comparison["algorithm_uniform_error_bound"]
    result["endpoint"]["d2"]["real"] *= 1.001
    assert not client.compare_certificate(result,client.DEFAULT_CERT)["goal_met"]


def test_l64_does_not_reuse_l28_arb_certificate():
    result = result_fixture(); result["request"]["lmax"] = 64
    with pytest.raises(ValueError): client.compare_certificate(result,client.DEFAULT_CERT)


def test_wrong_reference_bytes_are_rejected(tmp_path):
    file = tmp_path / "CERTIFICATE.json"; file.write_text("{}")
    with pytest.raises(ValueError): client.compare_certificate(result_fixture(),file)


def test_missing_channel_seed_is_rejected(tmp_path):
    file = tmp_path / "seed.txt"; file.write_text("0 1 0 0 1\n")
    with pytest.raises(ValueError): client.validate_seed(file,28)
