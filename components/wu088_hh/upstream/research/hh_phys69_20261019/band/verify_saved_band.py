#!/usr/bin/env python3
"""Verify saved PHYS69 evidence with hashlib/Fraction only; zero solver calls."""
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]


def digest(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def integer(value):
    if type(value) is int:
        return value
    if type(value) is str and re.fullmatch(r"[+-]?[0-9]+", value):
        return int(value)
    raise ValueError("exact integer or integer string required; float/bool refused")


def dyadic(value):
    mantissa, exponent = integer(value["mantissa"]), value["exponent2"]
    if type(exponent) is not int:
        raise ValueError("exact integer exponent2 required")
    return Fraction(mantissa)*Fraction(2)**exponent


def interval(component):
    midpoint, radius = dyadic(component["midpoint"]), dyadic(component["radius"])
    if radius < 0:
        raise ValueError("negative radius")
    return midpoint-radius, midpoint+radius


def box_contains(outer, inner):
    return all(interval(outer[c])[0] <= interval(inner[c])[0]
               and interval(outer[c])[1] >= interval(inner[c])[1] for c in ("real", "imag"))


def verify():
    out = BASE/"run_j29_36_t65"
    bound = json.loads((out/"REQUEST.json").read_text())
    binding, fingerprint = bound["binding"], bound["fingerprint"]
    assert bound["schema"] == "PHYS69_BAND_REQUEST_V1"
    assert digest(binding) == fingerprint
    assert binding == json.loads((BASE/"ENGINE_BINDING_BEFORE_EXECUTION.json").read_text())
    request = binding["request"]
    assert request == json.loads((BASE/"REQUEST_BAND_29_36.json").read_text())
    assert request["min_ell"] == 29 and request["max_ell"] == 36
    assert request["ell"] == 21 and request["ellprime"] == 20 and request["outer"] == "65"
    source = ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == binding["source_sha256"]
    engine = binding["engine"]
    files = {ROOT/"src/wu088_hh"/name: value for name, value in
             engine["phys68_reused_engine"]["files_sha256"].items()}
    files.update({ROOT/"src/wu088_hh/phys69_band_profiles.py": engine["band_source_sha256"],
                  ROOT/"scripts/phys69_band_profiles.py": engine["band_cli_sha256"],
                  ROOT/"scripts/phys68_ncp.py": engine["process_wrapper_sha256"]})
    for path, expected in files.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, path
    certificate_path = out/"CERTIFICATE.json"
    certificate = json.loads(certificate_path.read_text())
    assert certificate["schema"] == "PHYS69_FINITE_T_BAND_CERTIFICATE_V1"
    assert certificate["fingerprint"] == fingerprint and certificate["engine"] == engine
    assert certificate["request"] == request and certificate["source_sha256"] == binding["source_sha256"]
    assert certificate["status"] == "CERTIFIED_BAND_NUMERICAL_GOAL_MET"
    assert certificate["scientific_execution"] == "COMPLETE"
    assert certificate["full_intermediate_sum"] == list(range(29, 37))
    assert certificate["Coulomb_modes"] == [20, 21, *range(29, 37)]
    pairs = [(a, j) for a in (20, 21) for j in range(29, 37)]
    assert certificate["pairs"] == [list(p) for p in pairs]
    assert certificate["m"] == 0 and certificate["HH_R10"] == "OFF"
    assert not certificate["radial_cutoff_error_included"]
    assert not certificate["excluded_angular_error_included"]
    assert not certificate["original_driven_xi_certified"]
    assert len(certificate["panels"]) == 76 and len(list(out.glob("panel_*.json"))) == 76
    totals = {c: [Fraction(0), Fraction(0)] for c in ("real", "imag")}
    state = None
    payloads = []
    for index, manifest in enumerate(certificate["panels"]):
        assert manifest["index"] == index and manifest["file"] == f"panel_{index:04d}.json"
        path = out/manifest["file"]
        saved = json.loads(path.read_text())
        payload = saved["payload"]
        assert saved["fingerprint"] == fingerprint and saved["index"] == index
        assert saved["payload_sha256"] == manifest["payload_sha256"] == digest(payload)
        center = Fraction(65)-Fraction(2*index+1, 4)
        assert payload["center"] == str(center)
        assert payload["request"] == request
        assert payload["full_intermediate_sum"] == list(range(29, 37))
        assert payload["Coulomb_modes"] == [20, 21, *range(29, 37)]
        assert [t["j"] for t in payload["second_Born_terms"]] == list(range(29, 37))
        assert [row["pair"] for row in payload["pairs"]] == [list(p) for p in pairs]
        if state is None:
            state = {f"{row['pair'][0]},{row['pair'][1]}": row["q_right"] for row in payload["pairs"]}
            assert all(interval(value[c]) == (0, 0) for value in state.values() for c in ("real", "imag"))
        assert saved["right_state_sha256"] == digest(state)
        for row in payload["pairs"]:
            key = f"{row['pair'][0]},{row['pair'][1]}"
            assert box_contains(row["q_right"], state[key]), (index, key)
        state = {f"{row['pair'][0]},{row['pair'][1]}": row["q_left"] for row in payload["pairs"]}
        for value in payload["Coulomb_zero_free_lower"].values():
            assert interval(value)[0] > 0
        for component in totals:
            lo, hi = interval(payload["second_Born_increment"][component])
            totals[component][0] += lo
            totals[component][1] += hi
        payloads.append({"path": path.name, "payload_sha256": saved["payload_sha256"],
                         "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "size": path.stat().st_size})
    for component in totals:
        lo, hi = interval(certificate["D2_B_cutoff"][component])
        assert lo <= totals[component][0] and hi >= totals[component][1]
    exact_error = sum((dyadic(certificate["D2_B_cutoff"][c]["radius"]) for c in totals), Fraction(0))
    error_record = certificate["D2_numerical_absolute_error_l1"]
    assert exact_error == Fraction(integer(error_record["numerator"]), integer(error_record["denominator"]))
    assert exact_error <= Fraction(request["d2_numerical_absolute_goal"])
    gate = json.loads((BASE/"FIRST_TWO_GATE.json").read_text())
    for row in gate["panels"]:
        assert hashlib.sha256((out/row["path"]).read_bytes()).hexdigest() == row["file_sha256"]
    invocations = [json.loads(s) for s in (out/"INVOCATIONS.jsonl").read_text().splitlines() if s.strip()]
    assert len(invocations) == 2
    assert [(i["computed"], i["reused"], i["exit_code"]) for i in invocations] == [(2, 0, 0), (74, 2, 0)]
    assert all(i["fingerprint"] == fingerprint and i["HH_R10"] == "OFF" for i in invocations)
    return {"schema": "PHYS69_STORED_BAND_FRACTION_AUDIT_V1", "status": "PASS",
            "verified_utc": datetime.now(timezone.utc).isoformat(), "fingerprint": fingerprint,
            "certificate_sha256": hashlib.sha256(certificate_path.read_bytes()).hexdigest(),
            "producer_source_files_verified": len(files), "panel_payloads_verified": 76,
            "boundary_carry_pairs_verified": 76*16, "Coulomb_positive_gates_verified": 76*10,
            "first_two_panel_bytes_unchanged": True, "D2_box_encloses_exact_saved_increment_sum": True,
            "numerical_error_equals_exact_L1_radius": True, "invocations": invocations,
            "scientific_integrals_executed_by_this_audit": 0, "panels": payloads,
            "publication": "NOT_PERFORMED_BY_THIS_AUDIT", "backup": "NOT_PERFORMED_BY_THIS_AUDIT",
            "HH_R10": "OFF"}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
