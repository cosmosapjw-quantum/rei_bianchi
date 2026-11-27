"""Validated second-Born contribution from a new, disjoint intermediate band.

Only j=min_ell..max_ell is integrated.  The completed PHYS68 j=0..28
campaign is never called.  Coulomb modes include the two external modes,
but they enter the intermediate sum only if explicitly in the new band.
The result is a finite-T band contribution, without radial or angular tails.
All radii are dimensionless atomic coordinates and Born entries are a0^-1.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import time
from typing import Callable

from flint import acb, acb_series, arb, ctx

from .phys65_exterior_bounds import SOURCE_SHA, source_guard
from .phys67_coulomb_certificate import (
    B, complex_ball_record, dyadic_ball,
    restore_complex_ball as _restore_legacy_complex_ball,
)
from .phys68_angular import angular_complex_disk_bound, angular_taylor_coefficients
from .phys68_taylor import coulomb_taylor, exact_fraction, inflate_complex, rational_ball
from .phys68_profiles import (
    ProfileRequest, ProfilePanel, ProfileEnclosureFailure,
    _integer, _canonical, _write_json, _rational_record, _verify_boundary_carry,
    pair_key, pair_name, polynomial_integral, cauchy_tail,
    local_coulomb_majorant, norm_radius_l1, engine_identity as phys68_engine_identity,
)


def validate_complex_ball_record(data: dict) -> None:
    """Reject implicit float/bool truncation before the unchanged Arb decoder."""
    for component in ("real", "imag"):
        for part in ("midpoint", "radius"):
            value = data[component][part]
            mantissa, exponent = value["mantissa"], value["exponent2"]
            if not (type(mantissa) is int or
                    (type(mantissa) is str and re.fullmatch(r"[+-]?[0-9]+", mantissa))):
                raise ValueError("dyadic mantissa requires an exact integer or integer string")
            if type(exponent) is not int:
                raise ValueError("dyadic exponent2 requires an exact integer")
            if part == "radius" and int(mantissa) < 0:
                raise ValueError("dyadic radius must be nonnegative")


def restore_complex_ball(data: dict) -> acb:
    validate_complex_ball_record(data)
    return _restore_legacy_complex_ball(data)


@dataclass(frozen=True)
class BandRequest:
    min_ell: int = 29
    max_ell: int = 36
    ell: int = 21
    ellprime: int = 20
    outer: str = "65"
    half_width: str = "1/4"
    zero_free_radius: str = "1/2"
    majorant_radius: str = "2"
    degree: int = 96
    precision_bits: int = 512
    coefficient_bits: int = 1536
    d2_numerical_absolute_goal: str = "1e-63"

    def validate(self):
        _integer(self.min_ell, "min_ell", 29, 64)
        _integer(self.max_ell, "max_ell", self.min_ell, 64)
        # Reuse the unchanged analytic domain and finite-mode validation.
        # This is validation only: it calls no PHYS68 integration routine.
        ProfileRequest(
            max_ell=self.max_ell, ell=self.ell, ellprime=self.ellprime,
            outer=self.outer, half_width=self.half_width,
            zero_free_radius=self.zero_free_radius, majorant_radius=self.majorant_radius,
            degree=self.degree, precision_bits=self.precision_bits,
            coefficient_bits=self.coefficient_bits,
            d2_absolute_goal=self.d2_numerical_absolute_goal,
        ).validate()
        return self

    @property
    def intermediate_modes(self):
        return tuple(range(self.min_ell, self.max_ell+1))

    @property
    def coulomb_modes(self):
        return tuple(sorted({self.ell, self.ellprime, *self.intermediate_modes}))

    @property
    def pairs(self):
        return tuple(sorted({pair_key(a, j) for a in (self.ell, self.ellprime)
                             for j in self.intermediate_modes}))

    @property
    def panel_count(self):
        return int((exact_fraction(self.outer)-B)/(2*exact_fraction(self.half_width)))


def engine_identity() -> dict:
    """Bind both reused numerical kernels and this restricted band assembly."""
    old = phys68_engine_identity()
    root = Path(__file__).resolve().parents[2]
    return {
        "phys68_reused_engine": old,
        "band_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "band_cli_sha256": hashlib.sha256((root/"scripts/phys69_band_profiles.py").read_bytes()).hexdigest(),
        "process_wrapper_sha256": hashlib.sha256((root/"scripts/phys68_ncp.py").read_bytes()).hexdigest(),
    }


def request_binding(source: str | Path, request: BandRequest) -> dict:
    request.validate()
    return {"request": asdict(request), "source_sha256": source_guard(source),
            "engine": engine_identity(), "HH_R10": "OFF"}


def preflight(source: str | Path, request: BandRequest | None = None) -> dict:
    """New-band compatibility at the innermost panel; zero radial integrals."""
    request = (request or BandRequest()).validate()
    binding = request_binding(source, request)
    c = B+exact_fraction(request.half_width)
    rho, big = exact_fraction(request.zero_free_radius), exact_fraction(request.majorant_radius)
    begin = time.monotonic()
    gates = []
    with ctx.workprec(request.precision_bits):
        for j in sorted({request.ell, request.ellprime, request.max_ell}):
            disk = coulomb_taylor(j, c, request.degree, big, request.precision_bits)
            lower = disk.zero_free_lower(rho)
            if not lower > 0:
                raise ProfileEnclosureFailure(f"UNRESOLVED_ZERO_FREE_BOUND: ell={j}; center={c}")
            gates.append({"ell": j, "lower": dyadic_ball(lower)})
        angular = []
        for a in sorted({request.ell, request.ellprime}):
            coeffs = angular_taylor_coefficients(a, request.max_ell, c, request.degree,
                                                request.precision_bits, request.coefficient_bits)
            if len(coeffs) != request.degree+1 or not all(v.is_finite() for v in coeffs):
                raise ProfileEnclosureFailure("nonfinite or incomplete angular coefficients")
            angular.append({"pair": [a, request.max_ell], "coefficient_count": len(coeffs),
                            "coefficient_0": complex_ball_record(coeffs[0])})
    return {"schema": "PHYS69_BAND_PREFLIGHT_V1", "status": "PREFLIGHT_ONLY_PASS",
            "binding": binding, "fingerprint": hashlib.sha256(_canonical(binding)).hexdigest(),
            "center": str(c), "zero_free_gates": gates, "angular": angular,
            "radial_panels": 0, "intermediate_sum": list(request.intermediate_modes),
            "elapsed_seconds": time.monotonic()-begin, "HH_R10": "OFF"}


def run_band_profiles(source: str | Path, output: str | Path,
                      request: BandRequest | None = None, resume: bool = False,
                      max_new_panels: int | None = None,
                      progress: Callable[[dict], None] | None = None) -> dict:
    """Compute only a disjoint j>=29 band and reuse every valid saved panel.

    The exact predecessor serialization is hashed, while the actual consumed
    Arb q_right is separately checked to enclose it.  This retains PHYS68's
    corrected handling of outward Arb magnitude decoding on resume.
    """
    request = (request or BandRequest()).validate()
    if max_new_panels is not None:
        _integer(max_new_panels, "max_new_panels", 0, request.panel_count)
    binding = request_binding(source, request)
    fingerprint = hashlib.sha256(_canonical(binding)).hexdigest()
    out = Path(output)
    if out.is_symlink():
        raise ValueError("output must be an ordinary directory")
    out.mkdir(parents=True, exist_ok=True)
    request_file = out/"REQUEST.json"
    if request_file.exists():
        if not resume:
            raise FileExistsError("existing request: use --resume to verify/reuse it")
        previous = json.loads(request_file.read_text())
        if (previous.get("schema") != "PHYS69_BAND_REQUEST_V1" or
                previous.get("fingerprint") != fingerprint or previous.get("binding") != binding):
            raise ValueError("request/source/engine/runtime fingerprint mismatch")
    else:
        if any(out.iterdir()):
            raise ValueError("output directory is not empty and has no bound request")
        _write_json(request_file, {"schema": "PHYS69_BAND_REQUEST_V1", "fingerprint": fingerprint,
                                  "binding": binding, "HH_R10": "OFF"})
    begin = time.monotonic()
    q = {pair: acb(0) for pair in request.pairs}
    total = acb(0)
    computed = reused = 0
    receipts = []
    h, outer = exact_fraction(request.half_width), exact_fraction(request.outer)
    with ctx.workprec(request.precision_bits):
        state = {pair_name(pair): complex_ball_record(q[pair]) for pair in request.pairs}
        for index in range(request.panel_count):
            center = outer-(2*index+1)*h
            path = out/f"panel_{index:04d}.json"
            right_sha = hashlib.sha256(_canonical(state)).hexdigest()
            if path.exists():
                if not resume:
                    raise FileExistsError(f"panel already exists: {path.name}")
                saved = json.loads(path.read_text())
                digest, payload = saved.get("payload_sha256"), saved.get("payload")
                if digest != hashlib.sha256(_canonical(payload)).hexdigest():
                    raise ValueError(f"panel payload hash mismatch: {index}")
                if (saved.get("fingerprint") != fingerprint or saved.get("index") != index or
                        saved.get("right_state_sha256") != right_sha or payload.get("center") != str(center)):
                    raise ValueError(f"panel chain/request mismatch: {index}")
                if (payload.get("full_intermediate_sum") != list(request.intermediate_modes) or
                        payload.get("Coulomb_modes") != list(request.coulomb_modes)):
                    raise ValueError("saved panel intermediate/Coulomb mode coverage mismatch")
                for row in payload["pairs"]:
                    validate_complex_ball_record(row["q_right"])
                q = {tuple(row["pair"]): restore_complex_ball(row["q_left"]) for row in payload["pairs"]}
                if set(q) != set(request.pairs):
                    raise ValueError("saved panel pair coverage mismatch")
                inc = restore_complex_ball(payload["second_Born_increment"])
                reused += 1
            else:
                if max_new_panels is not None and computed >= max_new_panels:
                    break
                panel = build_band_panel(request, center, q)
                payload, q, inc = panel.record, panel.q_left, panel.second_born_increment
                digest = hashlib.sha256(_canonical(payload)).hexdigest()
                _write_json(path, {"fingerprint": fingerprint, "index": index,
                                  "right_state_sha256": right_sha,
                                  "payload_sha256": digest, "payload": payload})
                computed += 1
            if not inc.is_finite() or any(not value.is_finite() for value in q.values()):
                raise ProfileEnclosureFailure("nonfinite resumed or computed state")
            state = _verify_boundary_carry(payload, state, request.pairs)
            total += inc
            receipts.append({"index": index, "file": path.name, "payload_sha256": digest})
            if progress:
                progress({"panel": index+1, "of": request.panel_count, "center": str(center),
                          "reused": reused, "computed": computed})
        complete = len(receipts) == request.panel_count
        final = {
            "schema": "PHYS69_FINITE_T_BAND_CERTIFICATE_V1", "fingerprint": fingerprint,
            "request": asdict(request), "source_sha256": SOURCE_SHA, "engine": binding["engine"],
            "scientific_execution": "COMPLETE" if complete else "PARTIAL_CHECKPOINT",
            "panels": receipts, "panel_count_required": request.panel_count,
            "panels_computed_this_call": computed, "panels_reused_this_call": reused,
            "pairs": [list(p) for p in request.pairs],
            "full_intermediate_sum": list(request.intermediate_modes),
            "Coulomb_modes": list(request.coulomb_modes), "m": 0,
            "scope": "FINITE_T_SECOND_BORN_INTERMEDIATE_BAND_ONLY",
            "radial_cutoff_error_included": False, "excluded_angular_error_included": False,
            "original_driven_xi_certified": False,
            "completed_PHYS68_intermediate_0_to_28_integrations": 0,
            "PHYS63_qualitative_existence": "ESTABLISHED_REUSED",
            "NCP_submission": "NOT_SUBMITTED_BY_THIS_FUNCTION",
            "publication": "NOT_PERFORMED_BY_THIS_FUNCTION",
            "backup": "NOT_PERFORMED_BY_THIS_FUNCTION",
            "elapsed_seconds": time.monotonic()-begin, "HH_R10": "OFF",
        }
        if complete:
            error = norm_radius_l1(total)
            met = error <= exact_fraction(request.d2_numerical_absolute_goal)
            final.update({"D2_B_cutoff": complex_ball_record(total),
                          "D2_numerical_absolute_error_l1": _rational_record(error),
                          "numerical_absolute_goal_met": met,
                          "D1_q_B_cutoff": {pair_name(p): complex_ball_record(q[p]) for p in request.pairs},
                          "status": "CERTIFIED_BAND_NUMERICAL_GOAL_MET" if met else "VALID_BAND_ENCLOSURE_GOAL_NOT_MET"})
        else:
            final["status"] = "PARTIAL_CHECKPOINT_NO_FINAL_CERTIFICATE"
        _write_json(out/"CERTIFICATE.json", final)
        return final


def build_band_panel(request: BandRequest, center, q_right: dict) -> ProfilePanel:
    """One validated backward step for the explicitly selected new band."""
    request.validate()
    c = exact_fraction(center, "center")
    h = exact_fraction(request.half_width)
    rho = exact_fraction(request.zero_free_radius)
    big = exact_fraction(request.majorant_radius)
    if not B+h <= c <= exact_fraction(request.outer)-h:
        raise ValueError("panel center outside request")
    if set(q_right) != set(request.pairs):
        raise ValueError("every requested first-Born pair needs a right boundary enclosure")
    if any(not isinstance(x, acb) or not x.is_finite() for x in q_right.values()):
        raise ProfileEnclosureFailure("invalid q right boundary")
    started = time.monotonic()
    cap = ctx.cap
    with ctx.workprec(request.precision_bits):
        ctx.cap = request.degree+1
        try:
            disks = {j: coulomb_taylor(j, c, request.degree, big, request.precision_bits)
                     for j in request.coulomb_modes}
            lower = {j: d.zero_free_lower(rho) for j, d in disks.items()}
            failed = [j for j, value in lower.items() if not value > 0]
            if failed:
                raise ProfileEnclosureFailure(f"UNRESOLVED_ZERO_FREE_BOUND: ell={failed}; reduce h and rho")
            hs = {j: acb_series(list(d.coefficients), prec=request.degree+1)
                  for j, d in disks.items()}
            small_h = {j: local_coulomb_majorant(d, rho) for j, d in disks.items()}
            vbig = angular_complex_disk_bound(c, big, request.precision_bits)
            vsmall = angular_complex_disk_bound(c, rho, request.precision_bits)
            qleft, qc, qsmall, kbig, qseries = {}, {}, {}, {}, {}
            pairs_record = []
            max_d1_point_radius = Fraction(0)
            for pair in request.pairs:
                a, b = pair
                vv = angular_taylor_coefficients(a, b, c, request.degree,
                                                request.precision_bits, request.coefficient_bits)
                kk = hs[a]*hs[b]*acb_series(list(vv), prec=request.degree+1)
                kcoef = tuple(kk[n] for n in range(request.degree+1))
                majorant = (disks[a].majorant*disks[b].majorant*vbig).upper()
                remainder = cauchy_tail(majorant, big, h, request.degree)
                center_value = inflate_complex(q_right[pair] + polynomial_integral(kcoef, Fraction(0), h),
                                               (rational_ball(h)*remainder).upper())
                left = inflate_complex(q_right[pair] + polynomial_integral(kcoef, -h, h),
                                       (rational_ball(2*h)*remainder).upper())
                coeffs = (center_value,) + tuple(-kcoef[n]/(n+1) for n in range(request.degree+1))
                small_k = (small_h[a]*small_h[b]*vsmall).upper()
                mq = (q_right[pair].abs_upper() + rational_ball(rho+h)*small_k).upper()
                qleft[pair], qc[pair], qsmall[pair], kbig[pair] = left, coeffs, mq, majorant
                qseries[pair] = acb_series(list(coeffs), prec=request.degree+1)
                atcenter = center_value/(disks[a].coefficients[0]*disks[b].coefficients[0])
                max_d1_point_radius = max(max_d1_point_radius, norm_radius_l1(atcenter))
                pairs_record.append({
                    "pair": list(pair), "q_right": complex_ball_record(q_right[pair]),
                    "q_center": complex_ball_record(center_value), "q_left": complex_ball_record(left),
                    "D1_center": complex_ball_record(atcenter),
                    "K_big_disk_majorant": dyadic_ball(majorant),
                    "K_panel_remainder_upper": dyadic_ball(remainder),
                    "q_small_disk_majorant": dyadic_ball(mq),
                    "profile_coefficients": "q0=q_center; q[n+1]=-K[n]/(n+1); K=F_a F_b V_ab, generated by exact request-bound kernels",
                    "q_coefficient_count": len(coeffs),
                })
            increment = acb(0)
            numerical_tail_sum = arb(0)
            term_records = []
            for j in request.intermediate_modes:
                p1, p2 = pair_key(request.ell, j), pair_key(request.ellprime, j)
                integrand = qseries[p1]*qseries[p2]/(hs[j]*hs[j])
                coeffs = tuple(integrand[n] for n in range(request.degree+1))
                majorant = (qsmall[p1]*qsmall[p2]/(lower[j]*lower[j])).upper()
                error = (rational_ball(2*h)*cauchy_tail(majorant, rho, h, request.degree)).upper()
                polynomial_value = polynomial_integral(coeffs, -h, h)
                value = inflate_complex(polynomial_value, error)
                increment += value
                numerical_tail_sum += error
                term_records.append({"j": j, "integral": complex_ball_record(value),
                                     "integrand_majorant": dyadic_ball(majorant),
                                     "integration_tail_upper": dyadic_ball(error)})
            if not increment.is_finite():
                raise ProfileEnclosureFailure("second-Born panel integral is nonfinite")
            record = {
                "schema": "PHYS69_VALIDATED_BAND_VOLterra_PANEL_V1", "center": str(c),
                "left": str(c-h), "right": str(c+h), "half_width": str(h),
                "request": asdict(request), "source_sha256": SOURCE_SHA,
                "Coulomb_zero_free_lower": {str(j): dyadic_ball(lower[j]) for j in lower},
                "minimum_zero_free_lower": dyadic_ball(min(lower.values())),
                "pairs": pairs_record, "full_intermediate_sum": list(request.intermediate_modes),
                "Coulomb_modes": list(request.coulomb_modes),
                "second_Born_terms": term_records,
                "second_Born_increment": complex_ball_record(increment),
                "integration_Cauchy_tail_sum_upper": dyadic_ball(numerical_tail_sum.upper()),
                "max_D1_center_numerical_radius_l1": _rational_record(max_d1_point_radius),
                "analytic_domain_includes_uncut_K_beyond_terminal_T": True,
                "q_profile_reconstruction_requires_same_kernel_fingerprint": True,
                "elapsed_seconds": time.monotonic()-started, "HH_R10": "OFF",
            }
            return ProfilePanel(c, h, disks, qc, kbig, big, qleft, increment, record)
        finally:
            ctx.cap = cap

