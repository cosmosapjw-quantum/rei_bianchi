"""Bounded forward PHYS71 campaign, reusing immutable PHYS68/69 profiles.

Saved panels are append-only. A completed resume validates and returns before
creating a lock, directory, receipt, or numerical callback. Every restoration
and final ball sum uses the request precision rather than Arb's default.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, dataclass
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import uuid

from flint import acb, ctx

from .phys67_coulomb_certificate import complex_ball_record, restore_complex_ball
from .phys68_taylor import inflate_complex, rational_ball
from .phys71_d3 import D3Request, build_d3_panel, engine_identity, rational_record
from .phys71_angular_d3 import excluded_third_born_bound
from .phys71_inherit import (PANEL_COUNT, SOURCE_SHA256, InheritedProfiles,
                             box_contains, canonical, dyadic, load_inherited_profiles,
                             real_interval, _json, _pinned_bytes)


# PR115's printed upward endpoint. The shorter 1.484322e-79 is inward.
# Its producer snapshot and rejected aggregate are retained; no panels rerun.
RADIAL_BETA3_UPPER = F("1.48432231489e-79")
PROOF_PINS = {
    "research/hh_phys65_20261018/r5/PROOF.md":
        "00a1f86a8f8d132d53f2e8ea274a26948fd80420ac1c2e943d7036910ef41959",
    "research/hh_phys66_20261018/r5/PROOF.md":
        "c0f67c47c36f445494af3df52a9e09e27a853962b8f500ebe1572603febb68ca",
}
DIRECTED_PAIRS = tuple((a, j) for a in (20, 21) for j in range(37))


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def _check(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    path = Path(path)
    _check(not path.is_symlink() and path.is_file(), "evidence must be an ordinary file")
    return _json(path.read_bytes())


def create_json(path, value):
    """Commit complete JSON with an atomic, create-only hard link."""
    path = Path(path)
    temporary = path.parent/("."+path.name+"."+uuid.uuid4().hex+".tmp")
    data = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+"\n").encode()
    try:
        with temporary.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)  # Fails rather than replacing an existing result.
    finally:
        temporary.unlink(missing_ok=True)


def campaign_engine_identity(repo):
    result = engine_identity()
    result["campaign_files_sha256"] = {
        name: hashlib.sha256((repo/name).read_bytes()).hexdigest()
        for name in ("src/wu088_hh/phys71_campaign.py", "scripts/phys71_ncp.py")}
    return result


@dataclass(frozen=True)
class PreparedCampaign:
    inherited: InheritedProfiles
    request: D3Request
    binding: dict
    fingerprint: str


def prepare_campaign(repo_root, *, low_archive=None, band_archive=None, request=None):
    """Read-only hash validation; no Coulomb, Taylor, or integral callback."""
    repo = Path(repo_root)
    req = (request or D3Request()).validate()
    inherited = load_inherited_profiles(repo, low_archive=low_archive, band_archive=band_archive)
    for path, expected in PROOF_PINS.items():
        _pinned_bytes(repo/path, expected)
    binding = {
        "schema": "PHYS71_D3_BINDING_V1", "request": asdict(req),
        "source_sha256": SOURCE_SHA256,
        "inherited": [{k: family[k] for k in ("family", "archive_sha256",
                          "certificate_sha256", "request_sha256", "fingerprint")}
                       for family in inherited.provenance["families"]],
        "inherited_proof_sha256": dict(PROOF_PINS),
        "engine": campaign_engine_identity(repo),
        "coefficient": "D3=Z'''(0)/6", "angular_contraction": "bilinear_no_conjugation",
        "radial_beta3_upward_bound": rational_record(RADIAL_BETA3_UPPER),
        "HH_R10": "OFF",
    }
    return PreparedCampaign(inherited, req, binding, digest(binding))


def _zero_state():
    real = {"display": "0", "midpoint": {"mantissa": "0", "exponent2": 0},
            "radius": {"mantissa": "0", "exponent2": 0}}
    value = {"real": real, "imag": real}
    return {f"{a},{j}": value for a, j in DIRECTED_PAIRS}


def _radius(record):
    # Both components are validated, including negative radii and bools.
    for component in ("real", "imag"):
        real_interval(record[component])
    return sum((dyadic(record[c]["radius"]) for c in ("real", "imag")), F(0))


def _rational(record):
    _check(type(record) is dict and set(record) == {"numerator", "denominator"},
           "exact rational record required")
    _check(all(type(record[k]) is str for k in record), "exact rational strings required")
    return F(int(record["numerator"]), int(record["denominator"]))


def validate_new_panel(payload, inherited, state, forward_index):
    """Verify serialized finite enclosures and the forward carry contract."""
    _check(payload.get("schema") == "PHYS71_D3_PANEL_V1", "D3 panel schema mismatch")
    _check(type(payload.get("forward_index")) is int and payload["forward_index"] == forward_index,
           "forward index mismatch")
    _check(type(payload.get("inherited_index")) is int and payload["inherited_index"] == inherited.index,
           "inherited index mismatch")
    for key in ("left", "center", "right"):
        _check(type(payload.get(key)) is str and F(payload[key]) == getattr(inherited, key),
               "new panel geometry mismatch")
    _check(payload.get("all_modes") == list(range(37)) and
           all(type(j) is int for j in payload["all_modes"]), "new panel angular coverage mismatch")
    _check(payload.get("HH_R10") == "OFF" and
           type(payload.get("new_D1_or_D2_integrations")) is int and
           payload["new_D1_or_D2_integrations"] == 0, "old integrations or HH_R10 scope changed")
    radius = _radius(payload["D3_increment"])
    _check(_rational(payload["D3_increment_error_l1"]) == radius, "panel numerical radius mismatch")
    rows = payload["source_response_carries"]
    _check(type(rows) is list and len(rows) == len(DIRECTED_PAIRS), "74 directed carries required")
    pairs = []
    for row in rows:
        _check(type(row.get("external")) is int and type(row.get("j")) is int,
               "directed pair must use exact integers")
        pairs.append((row["external"], row["j"]))
    _check(tuple(pairs) == DIRECTED_PAIRS, "directed carry coverage/order mismatch")
    next_state = {}
    for (a, j), row in zip(pairs, rows):
        key = f"{a},{j}"
        _check(box_contains(row["P_left"], state[key]), "P_left does not enclose predecessor carry")
        _radius(row["P_right"])
        _radius(row["P_center"])
        for field in ("S_majorant", "S_panel_remainder", "U_disk_majorant"):
            _check(real_interval(row[field])[0] >= 0, "negative primitive majorant/remainder")
        next_state[key] = row["P_right"]
    for field in ("integrand_disk_majorant", "integrand_panel_remainder"):
        _check(real_interval(payload[field])[0] >= 0, "negative integration majorant/remainder")
    return next_state


def _panel_evidence(prepared, forward_index):
    inherited_index = PANEL_COUNT-1-forward_index
    return {family["family"]: family["panels"][inherited_index]["payload_sha256"]
            for family in prepared.inherited.provenance["families"]}


def _verify_certificate(cert, prepared, panels):
    body = dict(cert)
    checksum = body.pop("certificate_payload_sha256", None)
    _check(checksum == digest(body), "certificate payload SHA256 mismatch")
    _check(cert.get("schema") == "PHYS71_ALL_ANGULAR_D3_CERTIFICATE_V1" and
           cert.get("fingerprint") == prepared.fingerprint and
           cert.get("request") == asdict(prepared.request), "certificate request mismatch")
    _check(cert.get("scientific_execution") == "COMPLETE" and cert.get("HH_R10") == "OFF",
           "incomplete certificate or HH_R10 mismatch")
    _check(cert.get("source_sha256") == SOURCE_SHA256 and cert.get("coefficient") == "D3=Z'''(0)/6",
           "certificate physical identity mismatch")
    for field, expected in (("panel_count_required", PANEL_COUNT),
                            ("precision_bits", prepared.request.precision_bits),
                            ("new_D1_or_D2_integrations", 0),
                            ("inherited_profile_payloads_reused", 152),
                            ("radial_cutoff_bound_reused_from_max_L", 64)):
        _check(type(cert.get(field)) is int and cert[field] == expected,
               "certificate duplicated count/precision/scope mismatch: "+field)
    _check(cert.get("PHYS63_qualitative_existence") == "ESTABLISHED_REUSED",
           "certificate changed established PHYS63 scope")
    _check(cert.get("panels") == [p["receipt"] for p in panels] and len(panels) == PANEL_COUNT,
           "certificate/panel membership mismatch")
    expected = {c: [F(0), F(0)] for c in ("real", "imag")}
    for item in panels:
        for c in expected:
            lo, hi = real_interval(item["payload"]["D3_increment"][c])
            expected[c][0] += lo
            expected[c][1] += hi
    total = cert["D3_B_cutoff"]
    for c in expected:
        lo, hi = real_interval(total[c])
        _check(lo <= expected[c][0] and hi >= expected[c][1], "certificate does not enclose saved increment sum")
    numerical = _radius(total)
    angular = excluded_third_born_bound(36)
    total_error = numerical+RADIAL_BETA3_UPPER+angular
    for c in ("real", "imag"):
        lo, hi = real_interval(total[c])
        full_lo, full_hi = real_interval(cert["D3_full_radial_all_angular_box"][c])
        _check(full_lo <= lo-RADIAL_BETA3_UPPER-angular and
               full_hi >= hi+RADIAL_BETA3_UPPER+angular,
               "full-radial all-angular rectangle omits an error term")
    _check(_rational(cert["numerical_error_l1"]) == numerical and
           _rational(cert["radial_cutoff_error_upper"]) == RADIAL_BETA3_UPPER and
           _rational(cert["excluded_angular_error_upper"]) == angular and
           _rational(cert["total_error_about_cutoff_midpoint"]) == total_error,
           "certificate error budget mismatch")
    goal_met = total_error <= F(prepared.request.absolute_goal)
    _check(cert.get("absolute_goal_met") is goal_met and
           cert.get("status") == ("CERTIFIED_GOAL_MET" if goal_met else "CERTIFIED_GOAL_NOT_MET"),
           "certificate goal decision mismatch")
    _check(cert.get("full_nonlinear_remainder_certified") is False and
           cert.get("original_driven_xi_certified") is False,
           "certificate has unsupported promoted scope")


def inspect_saved(prepared, output):
    """Read every saved forward panel; never create or update anything."""
    out = Path(output)
    _check(not out.is_symlink() and (not out.exists() or out.is_dir()), "output must be an ordinary directory")
    state, panels = _zero_state(), []
    if not out.exists():
        return {"panels": panels, "state": state, "certificate": None, "exists": False}
    request_path = out/"REQUEST.json"
    if not request_path.exists():
        _check(not any(out.iterdir()), "nonempty output has no bound request")
        return {"panels": panels, "state": state, "certificate": None, "exists": False}
    request = read(request_path)
    _check(request == {"schema": "PHYS71_CAMPAIGN_REQUEST_V1", "binding": prepared.binding,
                       "fingerprint": prepared.fingerprint, "HH_R10": "OFF"},
           "existing request/source/engine/runtime fingerprint mismatch")
    paths = sorted(out.glob("panel_*.json"))
    _check(len(paths) <= PANEL_COUNT and
           [p.name for p in paths] == [f"panel_{i:04d}.json" for i in range(len(paths))],
           "saved panel gap or unexpected index")
    for index, path in enumerate(paths):
        saved = read(path)
        payload = saved["payload"]
        _check(saved.get("fingerprint") == prepared.fingerprint and
               type(saved.get("index")) is int and saved["index"] == index,
               "saved panel identity mismatch")
        _check(saved.get("payload_sha256") == digest(payload), "saved panel payload SHA256 mismatch")
        _check(saved.get("left_state_sha256") == digest(state), "saved left predecessor SHA256 mismatch")
        _check(saved.get("inherited_payload_sha256") == _panel_evidence(prepared, index),
               "saved inherited input hash mismatch")
        state = validate_new_panel(payload, prepared.inherited.panels[75-index], state, index)
        panels.append({"payload": payload, "receipt": {"index": index, "file": path.name,
                       "payload_sha256": saved["payload_sha256"],
                       "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}})
    cert = read(out/"CERTIFICATE.json") if (out/"CERTIFICATE.json").exists() else None
    if cert is not None:
        _verify_certificate(cert, prepared, panels)
    return {"panels": panels, "state": state, "certificate": cert, "exists": True}


@contextmanager
def _campaign_lock(output):
    import fcntl
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    lock = out.parent/("."+out.name+".phys71.lock")
    _check(not lock.is_symlink(), "campaign lock must not be a symlink")
    with lock.open("a+") as stream:
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("another process owns this PHYS71 campaign") from exc
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def _certificate(prepared, panels):
    req = prepared.request
    with ctx.workprec(req.precision_bits):
        total = acb(0)
        for panel in panels:
            total += restore_complex_ball(panel["payload"]["D3_increment"])
        center_record = complex_ball_record(total)
        numerical = _radius(center_record)
        angular = excluded_third_born_bound(req.max_ell)
        total_error = numerical+RADIAL_BETA3_UPPER+angular
        full_box = complex_ball_record(inflate_complex(total,
                           rational_ball(RADIAL_BETA3_UPPER+angular).upper()))
    goal_met = total_error <= F(req.absolute_goal)
    cert = {"schema": "PHYS71_ALL_ANGULAR_D3_CERTIFICATE_V1",
            "fingerprint": prepared.fingerprint, "request": asdict(req),
            "source_sha256": SOURCE_SHA256, "coefficient": "D3=Z'''(0)/6",
            "D3_B_cutoff": center_record, "D3_full_radial_all_angular_box": full_box,
            "numerical_error_l1": rational_record(numerical),
            "radial_cutoff_error_upper": rational_record(RADIAL_BETA3_UPPER),
            "radial_cutoff_bound_reused_from_max_L": 64,
            "excluded_angular_error_upper": rational_record(angular),
            "total_error_about_cutoff_midpoint": rational_record(total_error),
            "absolute_goal_met": goal_met,
            "status": "CERTIFIED_GOAL_MET" if goal_met else "CERTIFIED_GOAL_NOT_MET",
            "scientific_execution": "COMPLETE", "panels": [p["receipt"] for p in panels],
            "panel_count_required": PANEL_COUNT, "precision_bits": req.precision_bits,
            "new_D1_or_D2_integrations": 0, "inherited_profile_payloads_reused": 152,
            "full_nonlinear_remainder_certified": False, "original_driven_xi_certified": False,
            "PHYS63_qualitative_existence": "ESTABLISHED_REUSED", "HH_R10": "OFF"}
    cert["certificate_payload_sha256"] = digest(cert)
    _verify_certificate(cert, prepared, panels)
    return cert


def run_campaign(prepared, output, *, resume=False, max_new_panels=None, progress=None):
    """Append at most the requested new D3 panels, or return a verified result."""
    if max_new_panels is not None:
        _check(type(max_new_panels) is int and 0 <= max_new_panels <= PANEL_COUNT,
               "max_new_panels must be an exact integer in 0..76")
    saved = inspect_saved(prepared, output)
    if saved["exists"] and not resume:
        raise FileExistsError("existing bound campaign: use --resume")
    if saved["certificate"] is not None:
        return {"record": saved["certificate"], "computed": 0, "reused": PANEL_COUNT,
                "read_only": True, "new_callbacks": 0}
    if max_new_panels == 0:
        return {"record": {"status": "PREFLIGHT_ONLY", "panels_present": len(saved["panels"]),
                            "fingerprint": prepared.fingerprint, "HH_R10": "OFF"},
                "computed": 0, "reused": len(saved["panels"]), "read_only": True, "new_callbacks": 0}
    out = Path(output)
    with _campaign_lock(out):
        saved = inspect_saved(prepared, out)  # A concurrent owner may have advanced it.
        if saved["exists"] and not resume:
            raise FileExistsError("existing bound campaign: use --resume")
        if saved["certificate"] is not None:
            return {"record": saved["certificate"], "computed": 0, "reused": PANEL_COUNT,
                    "read_only": True, "new_callbacks": 0}
        out.mkdir(parents=True, exist_ok=True)
        if not saved["exists"]:
            create_json(out/"REQUEST.json", {"schema": "PHYS71_CAMPAIGN_REQUEST_V1",
                "binding": prepared.binding, "fingerprint": prepared.fingerprint, "HH_R10": "OFF"})
        initial = len(saved["panels"])
        panels, state = saved["panels"], saved["state"]
        computed = 0
        with ctx.workprec(prepared.request.precision_bits):
            carry = {(a,j): restore_complex_ball(state[f"{a},{j}"]) for a,j in DIRECTED_PAIRS}
            for index in range(initial, PANEL_COUNT):
                if max_new_panels is not None and computed >= max_new_panels:
                    break
                inherited = prepared.inherited.panels[75-index]
                right, increment, payload = build_d3_panel(inherited, carry, prepared.request)
                _check(set(right) == set(DIRECTED_PAIRS) and increment.is_finite() and
                       all(v.is_finite() for v in right.values()), "nonfinite/incomplete new D3 output")
                next_state = validate_new_panel(payload, inherited, state, index)
                _check(box_contains(payload["D3_increment"], complex_ball_record(increment)),
                       "serialized increment does not enclose builder result")
                _check(all(box_contains(next_state[f"{a},{j}"], complex_ball_record(right[(a,j)]))
                           for a,j in DIRECTED_PAIRS), "serialized right carry does not enclose builder result")
                wrapper = {"index": index, "fingerprint": prepared.fingerprint,
                           "left_state_sha256": digest(state), "payload_sha256": digest(payload),
                           "inherited_payload_sha256": _panel_evidence(prepared, index), "payload": payload}
                path = out/f"panel_{index:04d}.json"
                create_json(path, wrapper)
                panels.append({"payload": payload, "receipt": {"index": index, "file": path.name,
                               "payload_sha256": wrapper["payload_sha256"],
                               "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}})
                state = next_state
                carry = {(a,j): restore_complex_ball(state[f"{a},{j}"]) for a,j in DIRECTED_PAIRS}
                computed += 1
                if progress:
                    progress({"completed": len(panels), "required": PANEL_COUNT,
                              "computed": computed, "reused": initial, "inherited_index": inherited.index})
        if len(panels) == PANEL_COUNT:
            record = _certificate(prepared, panels)
            create_json(out/"CERTIFICATE.json", record)
        else:
            record = {"schema": "PHYS71_D3_CHECKPOINT_V1", "status": "PARTIAL_CHECKPOINT",
                      "fingerprint": prepared.fingerprint, "panels": [p["receipt"] for p in panels],
                      "panels_complete": len(panels), "panels_required": PANEL_COUNT,
                      "computed_this_call": computed, "reused_this_call": initial,
                      "absolute_goal_met": None, "HH_R10": "OFF"}
            create_json(out/f"CHECKPOINT_{len(panels):04d}.json", record)
        return {"record": record, "computed": computed, "reused": initial,
                "read_only": False, "new_callbacks": computed}
