"""Read-only exact assembly of saved L28 plus the new j29..36 Born band.

This standard-library module evaluates no special functions or integrals.
It validates saved payload chains and sums exact midpoint/error records.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

from . import phys69_angular_tail as tail

EXPECTED_BAND_SHA = "e123f084bea390a25162826f306c115d683b7c9fd3157b15967c88814787d0c8"
EXPECTED_REQUEST = {
    "min_ell": 29, "max_ell": 36, "ell": 21, "ellprime": 20,
    "outer": "65", "half_width": "1/4", "zero_free_radius": "1/2",
    "majorant_radius": "2", "degree": 96, "precision_bits": 512,
    "coefficient_bits": 1536, "d2_numerical_absolute_goal": "1e-63",
}
MODES = list(range(29, 37))
COULOMB_MODES = [20, 21]+MODES
PAIRS = [[a, j] for a in (20, 21) for j in MODES]
ENGINE_FILES = {
    "phys65_exterior_bounds.py", "phys66_radial_budget.py", "phys67_first_born.py",
    "phys67_coulomb_certificate.py", "phys68_taylor.py", "phys68_angular.py",
    "phys68_profiles.py",
}
FIXED_GOAL = F("1e-62")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def _same(actual, expected, label):
    if canonical(actual) != canonical(expected):
        raise ValueError(f"{label} mismatch")


def _ball(value):
    if not isinstance(value, dict) or not {"midpoint", "radius"} <= set(value):
        raise ValueError("serialized real ball required")
    mid, rad = tail._dyadic(value["midpoint"]), tail._dyadic(value["radius"])
    if rad < 0:
        raise ValueError("negative ball radius")
    return mid, rad


def _box(value):
    if not isinstance(value, dict) or set(value) != {"real", "imag"}:
        raise ValueError("serialized complex box required")
    return tuple(_ball(value[k]) for k in ("real", "imag"))


def _contains(outer, inner):
    return all(om-orad <= im-irad and im+irad <= om+orad
               for (om, orad), (im, irad) in zip(outer, inner))


def _zero_record():
    real = {"display": "0", "midpoint": {"mantissa": "0", "exponent2": 0},
            "radius": {"mantissa": "0", "exponent2": 0}}
    return {"real": real, "imag": real}


def _source_engine_guard(repo, engine):
    prior = engine["phys68_reused_engine"]
    if set(prior["files_sha256"]) != ENGINE_FILES:
        raise ValueError("reused numerical engine coverage mismatch")
    pins = {f"src/wu088_hh/{name}": sha for name, sha in prior["files_sha256"].items()}
    pins.update({
        "src/wu088_hh/phys69_band_profiles.py": engine["band_source_sha256"],
        "scripts/phys69_band_profiles.py": engine["band_cli_sha256"],
        "scripts/phys68_ncp.py": engine["process_wrapper_sha256"],
    })
    for name, sha in pins.items():
        tail._hash_guard(repo/name, sha)
    return pins


def validate_saved_band(repo, directory, expected_sha=EXPECTED_BAND_SHA):
    """Check complete mode coverage, every payload, exact carry and aggregation."""
    repo, directory = Path(repo), Path(directory)
    raw = tail._hash_guard(directory/"CERTIFICATE.json", expected_sha)
    cert = json.loads(raw)
    _same(cert.get("schema"), "PHYS69_FINITE_T_BAND_CERTIFICATE_V1", "band schema")
    _same(cert.get("request"), EXPECTED_REQUEST, "fixed band request")
    _same(cert.get("scientific_execution"), "COMPLETE", "band execution")
    _same(cert.get("status"), "CERTIFIED_BAND_NUMERICAL_GOAL_MET", "band status")
    for key, value in {
        "source_sha256": tail.SOURCE_SHA, "full_intermediate_sum": MODES,
        "Coulomb_modes": COULOMB_MODES, "pairs": PAIRS, "m": 0,
        "panel_count_required": 76, "HH_R10": "OFF",
        "radial_cutoff_error_included": False, "excluded_angular_error_included": False,
        "numerical_absolute_goal_met": True,
        "completed_PHYS68_intermediate_0_to_28_integrations": 0,
    }.items():
        _same(cert.get(key), value, key)
    request = json.loads((directory/"REQUEST.json").read_text())
    _same(request.get("schema"), "PHYS69_BAND_REQUEST_V1", "request schema")
    binding = {"request": EXPECTED_REQUEST, "source_sha256": tail.SOURCE_SHA,
               "engine": cert["engine"], "HH_R10": "OFF"}
    _same(request.get("binding"), binding, "request binding")
    fingerprint = digest(binding)
    _same(request.get("fingerprint"), fingerprint, "request fingerprint")
    _same(cert.get("fingerprint"), fingerprint, "certificate fingerprint")
    source_pins = _source_engine_guard(repo, cert["engine"])
    if len(cert["panels"]) != 76:
        raise ValueError("complete 76-panel manifest required")
    state = {f"{a},{j}": _zero_record() for a, j in PAIRS}
    total = [[F(0), F(0)], [F(0), F(0)]]
    file_pins = {"CERTIFICATE.json": expected_sha,
                 "REQUEST.json": hashlib.sha256((directory/"REQUEST.json").read_bytes()).hexdigest()}
    minimum_gate = None
    for index, entry in enumerate(cert["panels"]):
        filename = f"panel_{index:04d}.json"
        _same(entry.get("index"), index, "manifest panel order")
        _same(entry.get("file"), filename, "manifest panel path")
        raw_panel = (directory/filename).read_bytes()
        file_pins[filename] = hashlib.sha256(raw_panel).hexdigest()
        saved = json.loads(raw_panel)
        payload = saved["payload"]
        payload_sha = digest(payload)
        for got in (saved.get("payload_sha256"), entry.get("payload_sha256")):
            _same(got, payload_sha, "panel payload SHA256")
        _same(saved.get("index"), index, "panel index")
        _same(saved.get("fingerprint"), fingerprint, "panel fingerprint")
        _same(saved.get("right_state_sha256"), digest(state), "backward state hash")
        center = F(65)-F(2*index+1, 4)
        for key, expected in {
            "schema": "PHYS69_VALIDATED_BAND_VOLterra_PANEL_V1",
            "request": EXPECTED_REQUEST, "source_sha256": tail.SOURCE_SHA,
            "center": str(center), "left": str(center-F(1, 4)),
            "right": str(center+F(1, 4)), "half_width": "1/4",
            "full_intermediate_sum": MODES, "Coulomb_modes": COULOMB_MODES,
            "HH_R10": "OFF",
        }.items():
            _same(payload.get(key), expected, f"panel {key}")
        _same([row["pair"] for row in payload["pairs"]], PAIRS, "panel pair coverage")
        _same([row["j"] for row in payload["second_Born_terms"]], MODES, "D2 mode coverage")
        gates = payload["Coulomb_zero_free_lower"]
        if set(gates) != {str(j) for j in COULOMB_MODES}:
            raise ValueError("zero-free gate coverage mismatch")
        for gate in gates.values():
            mid, rad = _ball(gate)
            if mid-rad <= 0:
                raise ValueError("nonpositive saved zero-free gate")
            minimum_gate = mid-rad if minimum_gate is None else min(minimum_gate, mid-rad)
        for row in payload["pairs"]:
            key = ",".join(map(str, row["pair"]))
            if not _contains(_box(row["q_right"]), _box(state[key])):
                raise ValueError("consumed boundary excludes predecessor")
            _box(row["q_left"])
            state[key] = row["q_left"]
        increment = _box(payload["second_Born_increment"])
        for component in range(2):
            total[component][0] += increment[component][0]
            total[component][1] += increment[component][1]
    _same(cert["D1_q_B_cutoff"], state, "final q boundary")
    final_box = _box(cert["D2_B_cutoff"])
    if not _contains(final_box, total):
        raise ValueError("final D2 box excludes exact saved increment sum")
    error = tail.read_rational(cert["D2_numerical_absolute_error_l1"])
    if error != sum(r for _, r in final_box) or not 0 <= error <= F("1e-63"):
        raise ValueError("band numerical radius mismatch or goal failure")
    return cert, {
        "status": "PASS_SAVED_PAYLOAD_CHAIN_EXACT_ARITHMETIC",
        "panels_verified": 76, "payload_hashes_verified": 76,
        "boundary_carries_verified": 76*16, "old_radial_integrations": 0,
        "new_radial_integrations": 0, "special_function_evaluations": 0,
        "minimum_zero_free_lower": tail.rational_record(minimum_gate),
        "source_pins": source_pins, "saved_files_sha256": file_pins,
        "runtime_recorded_at_production": cert["engine"]["phys68_reused_engine"],
    }


def assemble_exact(old_mid, band_mid, old_error, band_error, display_digits=24):
    """Equation (6), plus an explicitly charged finite-decimal display error."""
    tail._integer(display_digits, "display_digits", 1, 100)
    if len(old_mid) != 2 or len(band_mid) != 2:
        raise ValueError("two exact complex midpoint components required")
    old_mid = tuple(tail._exact(v) for v in old_mid)
    band_mid = tuple(tail._exact(v) for v in band_mid)
    old_error, band_error = tail._exact(old_error), tail._exact(band_error)
    if min(old_error, band_error) < 0:
        raise ValueError("nonnegative numerical radii required")
    midpoint = tuple(a+b for a, b in zip(old_mid, band_mid))
    components = {"old_L28_numerical": old_error, "new_j29_to_36_numerical": band_error,
                  "one_full_L36_radial_beta2_Gamma64": tail.RADIAL_BETA2_L64_T65_UPPER,
                  "excluded_j_above_36_all_radial": tail.excluded_second_born_bound(36),
                  "exact_midpoint_addition": F(0)}
    error = sum(components.values())
    with localcontext() as ctx:
        ctx.prec = display_digits
        ctx.rounding = ROUND_HALF_EVEN
        shown = tuple(str(Decimal(v.numerator)/Decimal(v.denominator)) for v in midpoint)
    display_error = sum(abs(v-F(s)) for v, s in zip(midpoint, shown))
    return {
        "midpoint_exact": {k: tail.rational_record(v) for k, v in zip(("real", "imag"), midpoint)},
        "error_components": {k: tail.rational_record(v) for k, v in components.items()},
        "absolute_error_about_exact_midpoint": tail.rational_record(error),
        "absolute_error_upper_decimal": tail.upward_decimal(error),
        "display_midpoint": dict(zip(("real", "imag"), shown)),
        "display_rounding_error_l1": tail.rational_record(display_error),
        "absolute_error_about_display_midpoint": tail.rational_record(error+display_error),
        "display_absolute_error_upper_decimal": tail.upward_decimal(error+display_error),
        "fixed_absolute_goal": "1e-62", "fixed_goal_met": error <= FIXED_GOAL,
        "display_fixed_goal_met": error+display_error <= FIXED_GOAL,
        "real_part_strictly_positive": midpoint[0] > error,
        "imag_part_strictly_positive": midpoint[1] > error,
    }


def verify_inherited_engine(old_certificate, old_request, band_engine):
    """Bind unchanged kernels to the fingerprint inside the SHA-pinned old result."""
    _same(old_request.get("schema"), "PHYS68_PROFILE_REQUEST_V1", "old request schema")
    binding = old_request["binding"]
    fingerprint = digest(binding)
    _same(old_request.get("fingerprint"), fingerprint, "old request fingerprint")
    _same(old_certificate.get("fingerprint"), fingerprint, "old certificate engine binding")
    _same(binding["request"], old_certificate["request"], "old physical request")
    _same(binding["source_sha256"], tail.SOURCE_SHA, "old frozen source")
    _same(band_engine["phys68_reused_engine"], binding["engine"], "unchanged PHYS68 engine")
    return binding["engine"]


def assemble_saved(repo, band_directory, expected_sha=EXPECTED_BAND_SHA):
    old, pins = tail.inherit(repo)
    band, verification = validate_saved_band(repo, band_directory, expected_sha)
    old_path = next(name for name in pins if name.endswith("CERTIFICATE.json"))
    old_request_path = Path(old_path).with_name("REQUEST.json")
    old_request_bytes = (Path(repo)/old_request_path).read_bytes()
    verify_inherited_engine(old, json.loads(old_request_bytes), band["engine"])
    pins = {**pins, str(old_request_path): hashlib.sha256(old_request_bytes).hexdigest()}
    result = assemble_exact(
        tail.saved_complex_midpoint(old["D2_B_cutoff"]),
        tail.saved_complex_midpoint(band["D2_B_cutoff"]),
        tail.read_rational(old["D2_numerical_absolute_error_l1"]),
        tail.read_rational(band["D2_numerical_absolute_error_l1"]))
    return {
        "schema": "PHYS69_ACTUAL_ALL_ANGULAR_D2_CERTIFICATE_V1",
        "status": "CERTIFIED_ALL_ANGULAR_D2_GOAL_MET" if result["display_fixed_goal_met"]
                  else "VALID_ALL_ANGULAR_ENCLOSURE_GOAL_NOT_MET",
        "scope": "actual outgoing DtN lambda^2 coefficient; m0; external(21,20); every j and every r>=27",
        "physics": {"B": "27", "k": "7/10", "E_Hartree": "49/200", "eta_C": "-10/7",
                    "shift": "7/10", "Z": "+u'(B)u(B)^-1", "D2": "Z''(0)/2"},
        "units": "a0^-1", "finite_computed_intermediate_range": [0, 36],
        "finite_radial_cutoff": "65", "newly_integrated_intermediate_range": [29, 36],
        "inherited_pins": pins, "new_band_certificate_sha256": expected_sha,
        "saved_band_verification": verification, "result": result,
        "new_integrations_in_this_assembly": 0, "old_executions_repeated": 0,
        "full_nonlinear_lambda1_error": None, "original_source_driven_xi_certified": False,
        "PHYS63_qualitative_existence": "ESTABLISHED_REUSED", "HH_R10": "OFF",
    }
