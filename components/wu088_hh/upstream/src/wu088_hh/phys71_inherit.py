"""Read the completed PHYS68/69 Volterra profiles without replaying them.

This stdlib-only boundary checks the exact archived bytes, request/engine
identity, panel coverage and the serialized predecessor enclosures.  It
imports no Arb/FLINT or integration code.  A newer Python runtime may read
these exact integers; the producer runtime remains provenance, never a
claim that the current process produced the saved enclosures.

The result supplies the two external rows (20,j), (21,j), j=0..36 on the
same 76 panels of [27,65].  Their common (20,21) pair is present once, hence
73 pairs.  The caller constructs any NEW Taylor coefficients under its own
recorded runtime.  No inherited integral or Coulomb evaluation occurs here.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import platform
import re
from typing import Any
from zipfile import ZipFile


SOURCE_SHA256 = "f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
LOW_ARCHIVE_SHA256 = "b930a1dff10f656c853d81f7ddc8048e9eb7b188431958cd8c4ca702ca87d1e3"
BAND_ARCHIVE_SHA256 = "538e16bb74ff5305584fbe2d42491dda55fdffdde536f9276e038bc48da561f0"
LOW_CERTIFICATE_SHA256 = "ddaae206009a276def281af5526851ceb717baf2e0de5f8472552a9db340de9a"
BAND_CERTIFICATE_SHA256 = "e123f084bea390a25162826f306c115d683b7c9fd3157b15967c88814787d0c8"
LOW_REQUEST_SHA256 = "16a2452e3341057e38a178b10dc48003992774196a5320c3f192176696b9b3e7"
BAND_REQUEST_SHA256 = "fd3ccce49a0e6ec89d96e089aa0942374457d1064684ae6c8a877fa292f8dacd"
LOW_RUN = "research/hh_phys68_20261019/profiles/run_l28_t65_completed"
BAND_RUN = "research/hh_phys69_20261019/band/run_j29_36_t65"
LOW_ARCHIVE = "research/hh_phys68_20261019/profiles/PROFILE_PANEL_PAYLOADS_20261019.zip"
BAND_ARCHIVE = "archives/PHYS69_BAND_PAYLOADS_20261019.zip"
B, OUTER, HALF_WIDTH, PANEL_COUNT = Fraction(27), Fraction(65), Fraction(1, 4), 76


class InheritedDataError(ValueError):
    """A saved profile cannot be used under the pinned inherited contract."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise InheritedDataError(reason)


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _json(data: bytes) -> dict:
    def unique(pairs):
        out = {}
        for key, value in pairs:
            _require(key not in out, f"duplicate JSON key: {key}")
            out[key] = value
        return out

    def invalid(value):
        raise InheritedDataError(f"nonfinite JSON token: {value}")

    result = json.loads(data, object_pairs_hook=unique, parse_constant=invalid)
    _require(type(result) is dict, "JSON root must be an object")
    return result


def _pinned_bytes(path: Path, expected: str) -> bytes:
    data = path.read_bytes()
    _require(sha256(data).hexdigest() == expected, f"pinned SHA256 mismatch: {path}")
    return data


def _integer(value: Any) -> int:
    if type(value) is int:
        return value
    if type(value) is str and re.fullmatch(r"[+-]?[0-9]+", value):
        return int(value)
    raise InheritedDataError("exact integer/string required; bool and float refused")


def dyadic(value: dict) -> Fraction:
    """Read a finite exact dyadic; display text is intentionally not parsed."""
    _require(type(value) is dict, "dyadic record must be an object")
    mantissa = _integer(value["mantissa"])
    exponent = value["exponent2"]
    _require(type(exponent) is int, "exponent2 must be an exact JSON integer")
    _require(abs(exponent) <= 100_000, "dyadic exponent outside saved-data limit")
    return Fraction(mantissa) * Fraction(2) ** exponent


def real_interval(value: dict) -> tuple[Fraction, Fraction]:
    midpoint, radius = dyadic(value["midpoint"]), dyadic(value["radius"])
    _require(radius >= 0, "negative serialized radius")
    return midpoint-radius, midpoint+radius


def _box(value: dict) -> dict[str, tuple[Fraction, Fraction]]:
    _require(type(value) is dict and {"real", "imag"} <= value.keys(),
             "complex rectangle requires real and imag")
    return {c: real_interval(value[c]) for c in ("real", "imag")}


def box_contains(outer: dict, inner: dict) -> bool:
    out, inside = _box(outer), _box(inner)
    return all(out[c][0] <= inside[c][0] and out[c][1] >= inside[c][1]
               for c in ("real", "imag"))


def _pairs(modes: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted({tuple(sorted((a, j))) for a in (20, 21) for j in modes}))


def validate_panel(saved: dict, *, index: int, request: dict, fingerprint: str,
                   expected_payload_sha256: str, previous_state: dict | None,
                   band: bool) -> tuple[dict, dict]:
    """Check one already bound panel and return payload and next exact state.

    ``previous_state`` is the preceding panel's *serialized* q_left, not a
    re-encoded Arb value.  q_right may be wider because Arb magnitude decoding
    rounds outward; its rectangle must enclose that exact predecessor.
    """
    modes = tuple(range(29, 37)) if band else tuple(range(29))
    coulomb = tuple(sorted({20, 21, *modes}))
    pairs = _pairs(modes)
    _require(type(index) is int and 0 <= index < PANEL_COUNT, "invalid panel index")
    _require(type(saved.get("index")) is int and saved["index"] == index,
             "saved panel index mismatch")
    payload = saved["payload"]
    digest = sha256(canonical(payload)).hexdigest()
    _require(saved.get("payload_sha256") == expected_payload_sha256 == digest,
             "panel payload SHA256 mismatch")
    _require(saved.get("fingerprint") == fingerprint, "panel fingerprint mismatch")
    expected_schema = ("PHYS69_VALIDATED_BAND_VOLterra_PANEL_V1" if band
                       else "PHYS68_VALIDATED_VOLterra_PANEL_V1")
    _require(payload.get("schema") == expected_schema, "panel schema mismatch")
    _require(payload.get("request") == request, "panel request mismatch")
    _require(payload.get("source_sha256") == SOURCE_SHA256, "panel source mismatch")
    _require(payload.get("HH_R10") == "OFF", "HH_R10 must remain OFF")
    _require(payload.get("full_intermediate_sum") == list(modes), "intermediate coverage mismatch")
    if band:
        _require(payload.get("Coulomb_modes") == list(coulomb), "Coulomb mode coverage mismatch")
    center = OUTER-(2*index+1)*HALF_WIDTH
    for name, expected in (("center", center), ("left", center-HALF_WIDTH),
                           ("right", center+HALF_WIDTH), ("half_width", HALF_WIDTH)):
        _require(type(payload.get(name)) is str and Fraction(payload[name]) == expected,
                 f"panel {name} mismatch")
    _require(payload.get("analytic_domain_includes_uncut_K_beyond_terminal_T") is True,
             "analytic continuation premise missing")
    _require(payload.get("q_profile_reconstruction_requires_same_kernel_fingerprint") is True,
             "kernel reconstruction premise missing")
    rows = payload["pairs"]
    _require(type(rows) is list and len(rows) == len(pairs), "pair count mismatch")
    seen = []
    for row in rows:
        pair = row.get("pair")
        _require(type(pair) is list and len(pair) == 2 and
                 all(type(j) is int for j in pair), "pair requires two exact integers")
        seen.append(tuple(pair))
    _require(tuple(seen) == pairs, "pair order/coverage mismatch or duplicate pair")
    if previous_state is None:
        _require(index == 0, "only the terminal panel may lack a predecessor")
        previous_state = {f"{a},{b}": row["q_right"]
                          for (a, b), row in zip(pairs, rows)}
        _require(all(v == (0, 0) for value in previous_state.values()
                     for v in _box(value).values()), "terminal q(T) must be exactly zero")
    _require(set(previous_state) == {f"{a},{b}" for a, b in pairs}, "predecessor pair mismatch")
    _require(saved.get("right_state_sha256") == sha256(canonical(previous_state)).hexdigest(),
             "predecessor serialization SHA256 mismatch")
    degree = request["degree"]
    for (a, b), row in zip(pairs, rows):
        _require(box_contains(row["q_right"], previous_state[f"{a},{b}"]),
                 "q_right does not enclose the serialized predecessor")
        _box(row["q_center"])
        _box(row["q_left"])
        _box(row["D1_center"])
        _require(type(row.get("q_coefficient_count")) is int and
                 row["q_coefficient_count"] == degree+2, "q coefficient count mismatch")
        majorant = real_interval(row["K_big_disk_majorant"])
        remainder = real_interval(row["K_panel_remainder_upper"])
        _require(majorant[0] > 0, "K majorant must be positive")
        ratio = HALF_WIDTH/Fraction(request["majorant_radius"])
        _require(remainder[0] >= majorant[1]*ratio**(degree+1)/(1-ratio),
                 "stored K remainder does not enclose its Cauchy bound")
        _require(real_interval(row["q_small_disk_majorant"])[0] > 0,
                 "q disk majorant must be positive")
    zero_free = payload["Coulomb_zero_free_lower"]
    _require(set(zero_free) == {str(j) for j in coulomb}, "zero-free mode coverage mismatch")
    _require(all(real_interval(v)[0] > 0 for v in zero_free.values()),
             "nonpositive saved zero-free gate")
    next_state = {f"{a},{b}": row["q_left"] for (a, b), row in zip(pairs, rows)}
    return payload, next_state


@dataclass(frozen=True)
class InheritedPanel:
    index: int
    center: Fraction
    left: Fraction
    right: Fraction
    pairs: dict[tuple[int, int], dict]
    low_payload: dict
    band_payload: dict
    coulomb_modes: tuple[int, ...] = tuple(range(37))


@dataclass(frozen=True)
class InheritedProfiles:
    panels: tuple[InheritedPanel, ...]
    provenance: dict


def _load_family(repo: Path, archive: Path, *, band: bool) -> tuple[list[dict], dict]:
    run = BAND_RUN if band else LOW_RUN
    archive_sha = BAND_ARCHIVE_SHA256 if band else LOW_ARCHIVE_SHA256
    request_sha = BAND_REQUEST_SHA256 if band else LOW_REQUEST_SHA256
    cert_sha = BAND_CERTIFICATE_SHA256 if band else LOW_CERTIFICATE_SHA256
    request_bytes = _pinned_bytes(repo/run/"REQUEST.json", request_sha)
    cert_bytes = _pinned_bytes(repo/run/"CERTIFICATE.json", cert_sha)
    bound, cert = _json(request_bytes), _json(cert_bytes)
    binding, fingerprint = bound["binding"], bound["fingerprint"]
    _require(sha256(canonical(binding)).hexdigest() == fingerprint, "bound request fingerprint mismatch")
    _require(bound.get("schema") == ("PHYS69_BAND_REQUEST_V1" if band else "PHYS68_PROFILE_REQUEST_V1"),
             "bound request schema mismatch")
    _require(bound.get("HH_R10") == cert.get("HH_R10") == "OFF", "HH_R10 must remain OFF")
    _require(binding.get("source_sha256") == cert.get("source_sha256") == SOURCE_SHA256,
             "bound original source mismatch")
    request, engine = binding["request"], binding["engine"]
    _require(cert.get("request") == request and cert.get("fingerprint") == fingerprint,
             "certificate binding mismatch")
    _require(cert.get("scientific_execution") == "COMPLETE", "inherited campaign is not complete")
    _require(cert.get("status") == ("CERTIFIED_BAND_NUMERICAL_GOAL_MET" if band else "CERTIFIED_GOALS_MET"),
             "inherited certificate did not pass its own goal")
    _require(cert.get("m") == 0 and cert.get("panel_count_required") == PANEL_COUNT,
             "certificate domain mismatch")
    reused = engine["phys68_reused_engine"] if band else engine
    engine_files = {f"src/wu088_hh/{name}": value
                    for name, value in reused["files_sha256"].items()}
    if band:
        _require(cert.get("engine") == engine, "band certificate engine mismatch")
        engine_files.update({"src/wu088_hh/phys69_band_profiles.py": engine["band_source_sha256"],
                             "scripts/phys69_band_profiles.py": engine["band_cli_sha256"],
                             "scripts/phys68_ncp.py": engine["process_wrapper_sha256"]})
    for name, expected in engine_files.items():
        _pinned_bytes(repo/name, expected)
    data = _pinned_bytes(archive, archive_sha)
    prefix = "run_j29_36_t65" if band else "run_l28_t65_completed"
    expected_members = {f"{prefix}/panel_{i:04d}.json" for i in range(PANEL_COUNT)}
    if band:
        expected_members |= {f"{prefix}/CERTIFICATE.json", f"{prefix}/REQUEST.json"}
    else:
        expected_members |= {"PANEL_MANIFEST.json", "run_l28_t65/panel_0000.json",
                             "run_l28_t65/panel_0001.json"}
    panels, receipts, state = [], [], None
    with ZipFile(BytesIO(data)) as z:
        names = z.namelist()
        _require(len(names) == len(set(names)) and set(names) == expected_members,
                 "archive membership mismatch or duplicate ZIP member")
        _require(all(not PurePosixPath(n).is_absolute() and ".." not in PurePosixPath(n).parts
                     for n in names), "unsafe ZIP member path")
        manifest_checks = 0
        if band:
            _require(z.read(f"{prefix}/REQUEST.json") == request_bytes and
                     z.read(f"{prefix}/CERTIFICATE.json") == cert_bytes,
                     "archived request/certificate byte mismatch")
        else:
            manifest = _json(z.read("PANEL_MANIFEST.json"))
            _require(manifest.get("schema") == "PHYS68_ALL_PANEL_BYTES_MANIFEST_V1" and
                     manifest.get("HH_R10") == "OFF", "low archive manifest mismatch")
            entries = manifest["entries"]
            _require(len(entries) == 78 and {e["path"] for e in entries} == expected_members-{"PANEL_MANIFEST.json"},
                     "low manifest membership mismatch")
            for item in entries:
                raw = z.read(item["path"])
                _require(type(item["bytes"]) is int and len(raw) == item["bytes"] and
                         sha256(raw).hexdigest() == item["sha256"], "low manifest payload byte mismatch")
                manifest_checks += 1
        manifests = cert["panels"]
        _require(type(manifests) is list and len(manifests) == PANEL_COUNT, "certificate panel count mismatch")
        for index, item in enumerate(manifests):
            filename = f"panel_{index:04d}.json"
            _require(type(item.get("index")) is int and item["index"] == index and
                     item.get("file") == filename, "certificate panel index/name mismatch")
            raw = z.read(f"{prefix}/{filename}")
            saved = _json(raw)
            payload, state = validate_panel(saved, index=index, request=request,
                                            fingerprint=fingerprint,
                                            expected_payload_sha256=item["payload_sha256"],
                                            previous_state=state, band=band)
            panels.append(payload)
            receipts.append({"index": index, "member": f"{prefix}/{filename}",
                             "bytes": len(raw), "file_sha256": sha256(raw).hexdigest(),
                             "payload_sha256": saved["payload_sha256"]})
    return panels, {"family": "PHYS69_BAND" if band else "PHYS68_LOW",
                    "archive_sha256": archive_sha, "archive_bytes": len(data),
                    "certificate_sha256": cert_sha, "request_sha256": request_sha,
                    "fingerprint": fingerprint, "producer_engine": engine,
                    "producer_runtime": {k: reused[k] for k in ("python", "python_flint", "flint")},
                    "engine_files_sha256": engine_files,
                    "selected_panels_verified": PANEL_COUNT,
                    "archive_members": len(expected_members),
                    "low_manifest_file_hashes_verified": manifest_checks,
                    "panels": receipts}


def load_inherited_profiles(repo_root: str | Path, *,
                            low_archive: str | Path | None = None,
                            band_archive: str | Path | None = None) -> InheritedProfiles:
    """Return verified saved data; missing archives are an explicit access error.

    Archives may be supplied from a verified capsule.  No automatic search,
    extraction, restore, mutation, coefficient generation or solver call is
    performed.  Default paths are the source/evidence capsule layout.
    """
    repo = Path(repo_root)
    _pinned_bytes(repo/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz", SOURCE_SHA256)
    low, low_prov = _load_family(repo, Path(low_archive) if low_archive is not None else repo/LOW_ARCHIVE,
                                 band=False)
    band, band_prov = _load_family(repo, Path(band_archive) if band_archive is not None else repo/BAND_ARCHIVE,
                                   band=True)
    combined = []
    for index, (lp, bp) in enumerate(zip(low, band)):
        _require(all(lp[k] == bp[k] for k in ("center", "left", "right", "half_width")),
                 "low/band panel alignment mismatch")
        rows = {tuple(row["pair"]): row for row in [*lp["pairs"], *bp["pairs"]]}
        _require(tuple(sorted(rows)) == _pairs(tuple(range(37))) and len(rows) == 73,
                 "combined pair coverage mismatch")
        combined.append(InheritedPanel(index, Fraction(lp["center"]), Fraction(lp["left"]),
                                       Fraction(lp["right"]), rows, lp, bp))
    provenance = {"schema": "PHYS71_INHERITED_PROFILES_V1", "status": "VERIFIED_SAVED_DATA",
                  "source_sha256": SOURCE_SHA256, "B": "27", "T": "65", "m": 0,
                  "external_modes": [21, 20], "intermediate_modes": list(range(37)),
                  "panels": PANEL_COUNT, "pairs_per_panel": 73,
                  "inherited_payloads_verified": 2*PANEL_COUNT,
                  "boundary_pair_enclosures_verified": PANEL_COUNT*73,
                  "reader_python": platform.python_version(),
                  "reader_runtime_is_producer_runtime_claim": False,
                  "producer_runtime_equality_required": False,
                  "coefficient_regeneration_performed": False,
                  "Coulomb_evaluations": 0, "new_integrals": 0,
                  "old_payload_writes": 0, "families": [low_prov, band_prov], "HH_R10": "OFF"}
    return InheritedProfiles(tuple(combined), provenance)
