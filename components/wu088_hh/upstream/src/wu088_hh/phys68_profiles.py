"""Validated finite-block first-Born profiles and one full-sum second Born entry.

The original m=0 angular integral is evaluated algebraically.  Every Coulomb
and algebraic coefficient is an Arb enclosure; analytic Cauchy bounds control
the parts omitted by Taylor truncation.  No interpolation of point values is
used.  A profile q_ab = F_a F_b D1_ab obeys q'=-F_a F_b V_ab, q(T)=0.
For one target (l,p), D2_lp(B)=sum_j integral(q_lj q_pj / F_j**2).
The sum contains every j in 0..L and is complex bilinear, without conjugation.

All radii are dimensionless atomic coordinates.  Born entries have units
a0^-1.  Process-global FLINT precision/cap precludes threaded use.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform
import time
from typing import Callable

import flint
from flint import acb, acb_series, arb, ctx

from .phys65_exterior_bounds import SOURCE_SHA
from .phys66_radial_budget import certificate as radial_certificate, to_jsonable
from .phys67_coulomb_certificate import (
    B, K, complex_ball_record, dyadic_ball, restore_ball, restore_complex_ball,
)
from .phys68_angular import (
    angular_complex_disk_bound, angular_taylor_coefficients,
)
from .phys68_taylor import (
    TaylorDisk, TaylorEnclosureFailure, coulomb_taylor, dyadic_fraction,
    exact_fraction, inflate_complex, rational_ball,
)


class ProfileEnclosureFailure(TaylorEnclosureFailure):
    pass


def _integer(value, name, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name}: exact integer {low}..{high} required")
    return value


def pair_key(a: int, b: int) -> tuple[int, int]:
    return (min(a, b), max(a, b))


def pair_name(pair: tuple[int, int]) -> str:
    return f"{pair[0]},{pair[1]}"


@dataclass(frozen=True)
class ProfileRequest:
    max_ell: int = 28
    ell: int = 21
    ellprime: int = 20
    outer: str = "65"
    half_width: str = "1/4"
    zero_free_radius: str = "1/2"
    majorant_radius: str = "2"
    degree: int = 80
    precision_bits: int = 384
    coefficient_bits: int = 1024
    d1_absolute_goal: str = "1e-45"
    d2_absolute_goal: str = "1e-62"

    def validate(self):
        _integer(self.max_ell, "max_ell", 0, 64)
        _integer(self.ell, "ell", 0, self.max_ell)
        _integer(self.ellprime, "ellprime", 0, self.max_ell)
        _integer(self.degree, "degree", 2, 256)
        _integer(self.precision_bits, "precision_bits", 128, 4096)
        _integer(self.coefficient_bits, "coefficient_bits", self.precision_bits, 4096)
        outer, h, rho, big = (exact_fraction(getattr(self, k), k) for k in
                             ("outer", "half_width", "zero_free_radius", "majorant_radius"))
        if not B < outer <= 100:
            raise ValueError("27 < outer <= 100 required")
        if not 0 < h < rho < big < B - Fraction(7, 10):
            raise ValueError("0 < half_width < zero_free_radius < majorant_radius < B-R0 required")
        if ((outer-B)/(2*h)).denominator != 1:
            raise ValueError("uniform panels must partition [27,outer] exactly")
        for key in ("d1_absolute_goal", "d2_absolute_goal"):
            if exact_fraction(getattr(self, key), key) <= 0:
                raise ValueError("absolute goals must be positive")
        return self

    @property
    def pairs(self):
        return tuple(sorted({pair_key(a, j) for a in (self.ell, self.ellprime)
                             for j in range(self.max_ell+1)}))

    @property
    def panel_count(self):
        return int((exact_fraction(self.outer)-B)/(2*exact_fraction(self.half_width)))


def polynomial_integral(coefficients, start: Fraction, stop: Fraction) -> acb:
    """Enclose the exact polynomial integral, including coefficient roundoff."""
    result = acb(0)
    for n, coefficient in enumerate(coefficients):
        weight = (stop**(n+1)-start**(n+1))/(n+1)
        if weight:
            result += coefficient * rational_ball(weight)
    return result


def cauchy_tail(majorant: arb, radius: Fraction, extent: Fraction, degree: int) -> arb:
    if not 0 <= extent < radius:
        raise ValueError("Cauchy extent must be within the analytic disk")
    ratio = rational_ball(extent/radius)
    result = majorant * ratio**(degree+1)/(1-ratio)
    if not result.is_finite() or not result >= 0:
        raise ProfileEnclosureFailure("nonfinite Cauchy bound")
    return result.upper()


def local_coulomb_majorant(disk: TaylorDisk, radius: Fraction) -> arb:
    """ODE bound on a smaller disk, avoiding reuse of an unnecessarily large M."""
    if disk.ell is None or not 0 < radius <= disk.radius:
        raise ValueError("a Coulomb Taylor disk and a nested positive radius required")
    gap = disk.center-radius
    matrix = max(Fraction(1), K*K + 2/gap + disk.ell*(disk.ell+1)/gap**2)
    initial = max(x.abs_upper() for x in disk.coefficients[:2])
    return (initial * rational_ball(radius*matrix).exp()).upper()


def norm_radius_l1(value: acb) -> Fraction:
    """Rigorous complex absolute error about the stored rectangular midpoint."""
    if not value.is_finite():
        raise ProfileEnclosureFailure("nonfinite result")
    return dyadic_fraction(value.real.rad()) + dyadic_fraction(value.imag.rad())


def _rational_record(value: Fraction) -> dict:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


@dataclass
class ProfilePanel:
    center: Fraction
    half_width: Fraction
    coulomb: dict[int, TaylorDisk]
    q_coefficients: dict[tuple[int, int], tuple[acb, ...]]
    k_majorants: dict[tuple[int, int], arb]
    majorant_radius: Fraction
    q_left: dict[tuple[int, int], acb]
    second_born_increment: acb
    record: dict

    def evaluate_first_born(self, a: int, b: int, offset) -> acb:
        """Enclose a profile at any exact real point of this panel.

        K is not set to zero outside [B,T] inside complex disks; q^T is its
        analytic primitive with terminal value zero at T.  A real evaluation
        outside this panel is refused rather than extrapolated.
        """
        xx = exact_fraction(offset, "offset")
        if abs(xx) > self.half_width:
            raise ValueError("offset outside the certified panel")
        pair = pair_key(a, b)
        if pair not in self.q_coefficients:
            raise KeyError("pair not included in this target's full intermediate sum")
        disk = self.coulomb[a]
        with ctx.workprec(disk.precision_bits):
            q = acb(0)
            xball = rational_ball(xx)
            for coefficient in reversed(self.q_coefficients[pair]):
                q = q*xball + coefficient
            # q polynomial has degree N+1.  Its primitive remainder is
            # bounded by |x| times the degree-N K remainder on |z-c|<=|x|.
            n = len(self.q_coefficients[pair])-2
            qerror = rational_ball(abs(xx))*cauchy_tail(
                self.k_majorants[pair], self.majorant_radius, abs(xx), n)
            q = inflate_complex(q, qerror)
            denominator = self.coulomb[a].evaluate(xx)*self.coulomb[b].evaluate(xx)
            if denominator.contains(0):
                raise ProfileEnclosureFailure("point denominator unresolved")
            return q/denominator


def build_panel(request: ProfileRequest, center, q_right: dict) -> ProfilePanel:
    """One validated backward Volterra step and all-j second-Born integral."""
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
                     for j in range(request.max_ell+1)}
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
            for j in range(request.max_ell+1):
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
                "schema": "PHYS68_VALIDATED_VOLterra_PANEL_V1", "center": str(c),
                "left": str(c-h), "right": str(c+h), "half_width": str(h),
                "request": asdict(request), "source_sha256": SOURCE_SHA,
                "Coulomb_zero_free_lower": {str(j): dyadic_ball(lower[j]) for j in lower},
                "minimum_zero_free_lower": dyadic_ball(min(lower.values())),
                "pairs": pairs_record, "full_intermediate_sum": list(range(request.max_ell+1)),
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


ENGINE_FILES = (
    "phys65_exterior_bounds.py", "phys66_radial_budget.py", "phys67_first_born.py",
    "phys67_coulomb_certificate.py", "phys68_taylor.py", "phys68_angular.py",
    "phys68_profiles.py",
)


def engine_identity() -> dict:
    root = Path(__file__).parent
    files = {name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in ENGINE_FILES}
    return {"files_sha256": files, "python": platform.python_version(),
            "python_flint": flint.__version__, "flint": flint.__FLINT_VERSION__}


def _canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _write_json(path: Path, value):
    temporary = path.with_suffix(path.suffix+".tmp")
    temporary.write_text(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False)+"\n")
    temporary.replace(path)


def _dyadic_record_fraction(value: dict) -> Fraction:
    m, e = int(value["mantissa"]), int(value["exponent2"])
    return Fraction(m << e) if e >= 0 else Fraction(m, 1 << (-e))


def _serialized_box_contains(outer: dict, inner: dict) -> bool:
    """Exact rational comparison, unaffected by Arb's outward radius decoding."""
    for component in ("real", "imag"):
        om = _dyadic_record_fraction(outer[component]["midpoint"])
        orad = _dyadic_record_fraction(outer[component]["radius"])
        im = _dyadic_record_fraction(inner[component]["midpoint"])
        irad = _dyadic_record_fraction(inner[component]["radius"])
        if orad < 0 or irad < 0 or om-orad > im-irad or om+orad < im+irad:
            return False
    return True


def _verify_boundary_carry(payload: dict, state: dict, pairs: tuple) -> dict:
    rows = {tuple(row["pair"]): row for row in payload["pairs"]}
    if set(rows) != set(pairs) or len(payload["pairs"]) != len(pairs):
        raise ValueError("panel pair coverage mismatch")
    for pair in pairs:
        if not _serialized_box_contains(rows[pair]["q_right"], state[pair_name(pair)]):
            raise ValueError("panel input does not enclose predecessor boundary")
    # Hash the immutable saved predecessor, not its potentially wider decoded
    # Arb object. The actual consumed q_right is separately required to contain it.
    return {pair_name(pair): rows[pair]["q_left"] for pair in pairs}


def load_profile_panel(source: str | Path, output: str | Path, index: int) -> ProfilePanel:
    """Restore a certified profile without repeating its Volterra/D2 integration.

    The saved q-center enclosures are retained.  Only their exact coefficient
    generators are reconstructed.  This compact representation avoids storing
    hundreds of thousands of redundant coefficients; it is tied to identical
    engine bytes/runtime and the original input hash.  No old science campaign
    or integration step is invoked by this loader.
    """
    out = Path(output)
    saved_request = json.loads((out/"REQUEST.json").read_text())
    binding = saved_request["binding"]
    request = ProfileRequest(**binding["request"]).validate()
    _integer(index, "index", 0, request.panel_count-1)
    radial_certificate(source, request.max_ell, request.outer, 2)
    if binding != {"request": asdict(request), "source_sha256": SOURCE_SHA, "engine": engine_identity()}:
        raise ValueError("profile request/source/engine/runtime fingerprint mismatch")
    fingerprint = hashlib.sha256(_canonical(binding)).hexdigest()
    if saved_request.get("fingerprint") != fingerprint:
        raise ValueError("profile request fingerprint mismatch")
    saved = json.loads((out/f"panel_{index:04d}.json").read_text())
    payload = saved["payload"]
    digest = hashlib.sha256(_canonical(payload)).hexdigest()
    if saved.get("fingerprint") != fingerprint or saved.get("index") != index or saved.get("payload_sha256") != digest:
        raise ValueError("profile payload identity mismatch")
    manifest = json.loads((out/"CERTIFICATE.json").read_text())
    entries = {r["index"]: r for r in manifest["panels"]}
    if manifest.get("fingerprint") != fingerprint or index not in entries or entries[index]["payload_sha256"] != digest:
        raise ValueError("profile is not in the recorded checkpoint/certificate manifest")
    h = exact_fraction(request.half_width)
    big = exact_fraction(request.majorant_radius)
    center = exact_fraction(request.outer)-(2*index+1)*h
    if payload.get("center") != str(center) or payload.get("full_intermediate_sum") != list(range(request.max_ell+1)):
        raise ValueError("profile panel domain/intermediate sum mismatch")
    rows = {tuple(row["pair"]): row for row in payload["pairs"]}
    if set(rows) != set(request.pairs) or len(payload["pairs"]) != len(request.pairs):
        raise ValueError("profile pair coverage mismatch")
    cap = ctx.cap
    with ctx.workprec(request.precision_bits):
        ctx.cap = request.degree+1
        try:
            disks = {j: coulomb_taylor(j, center, request.degree, big, request.precision_bits)
                     for j in range(request.max_ell+1)}
            hs = {j: acb_series(list(d.coefficients), prec=request.degree+1) for j, d in disks.items()}
            qc, kbig, qleft = {}, {}, {}
            for pair in request.pairs:
                a,b = pair
                vv = angular_taylor_coefficients(a,b,center,request.degree,
                                                request.precision_bits,request.coefficient_bits)
                kk = hs[a]*hs[b]*acb_series(list(vv), prec=request.degree+1)
                qc[pair] = (restore_complex_ball(rows[pair]["q_center"]),) + tuple(
                    -kk[n]/(n+1) for n in range(request.degree+1))
                kbig[pair] = restore_ball(rows[pair]["K_big_disk_majorant"])
                qleft[pair] = restore_complex_ball(rows[pair]["q_left"])
            return ProfilePanel(center,h,disks,qc,kbig,big,qleft,
                                restore_complex_ball(payload["second_Born_increment"]),payload)
        finally:
            ctx.cap = cap


def run_profiles(source: str | Path, output: str | Path, request: ProfileRequest | None = None,
                 resume: bool = False, max_new_panels: int | None = None,
                 progress: Callable[[dict], None] | None = None) -> dict:
    """Run or safely resume one exact request; successful panels are never recomputed.

    Resume binds original input, request, engine source bytes, runtime, every
    saved payload hash, and the backward state chain.  Partial results never
    masquerade as a final Born certificate.  Existing output requires --resume.
    """
    request = (request or ProfileRequest()).validate()
    if max_new_panels is not None:
        _integer(max_new_panels, "max_new_panels", 0, request.panel_count)
    radial = radial_certificate(source, request.max_ell, request.outer, 2)
    identity = engine_identity()
    binding = {"request": asdict(request), "source_sha256": SOURCE_SHA, "engine": identity}
    fingerprint = hashlib.sha256(_canonical(binding)).hexdigest()
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    request_file = out/"REQUEST.json"
    if request_file.exists():
        if not resume:
            raise FileExistsError("existing request: use resume to verify/reuse it")
        previous = json.loads(request_file.read_text())
        if previous.get("fingerprint") != fingerprint or previous.get("binding") != binding:
            raise ValueError("request/source/engine/runtime fingerprint mismatch")
    else:
        if any(out.iterdir()):
            raise ValueError("output directory is not empty and has no bound request")
        _write_json(request_file, {"schema": "PHYS68_PROFILE_REQUEST_V1", "fingerprint": fingerprint,
                                  "binding": binding, "HH_R10": "OFF"})
    started = time.monotonic()
    q = {pair: acb(0) for pair in request.pairs}
    total = acb(0)
    reused = computed = 0
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
                digest = saved.get("payload_sha256")
                payload = saved.get("payload")
                if digest != hashlib.sha256(_canonical(payload)).hexdigest():
                    raise ValueError(f"panel payload hash mismatch: {index}")
                if (saved.get("fingerprint") != fingerprint or saved.get("index") != index or
                        saved.get("right_state_sha256") != right_sha or payload.get("center") != str(center)):
                    raise ValueError(f"panel chain/request mismatch: {index}")
                if payload.get("full_intermediate_sum") != list(range(request.max_ell+1)):
                    raise ValueError("saved panel omits intermediate modes")
                q = {tuple(row["pair"]): restore_complex_ball(row["q_left"]) for row in payload["pairs"]}
                if set(q) != set(request.pairs):
                    raise ValueError("saved panel omits first-Born pairs")
                inc = restore_complex_ball(payload["second_Born_increment"])
                reused += 1
            else:
                if max_new_panels is not None and computed >= max_new_panels:
                    break
                panel = build_panel(request, center, q)
                payload, q, inc = panel.record, panel.q_left, panel.second_born_increment
                digest = hashlib.sha256(_canonical(payload)).hexdigest()
                saved = {"fingerprint": fingerprint, "index": index,
                         "right_state_sha256": right_sha, "payload_sha256": digest, "payload": payload}
                _write_json(path, saved)
                computed += 1
            if not inc.is_finite() or any(not x.is_finite() for x in q.values()):
                raise ProfileEnclosureFailure("nonfinite resumed or computed state")
            state = _verify_boundary_carry(payload, state, request.pairs)
            total += inc
            receipts.append({"index": index, "file": path.name, "payload_sha256": digest})
            if progress:
                progress({"panel": index+1, "of": request.panel_count, "center": str(center),
                          "reused": reused, "computed": computed})
        complete = len(receipts) == request.panel_count
        final = {
            "schema": "PHYS68_FINITE_BLOCK_PROFILE_CERTIFICATE_V1", "fingerprint": fingerprint,
            "request": asdict(request), "source_sha256": SOURCE_SHA,
            "scientific_execution": "COMPLETE" if complete else "PARTIAL_CHECKPOINT",
            "panels": receipts, "panel_count_required": request.panel_count,
            "panels_computed_this_call": computed, "panels_reused_this_call": reused,
            "pairs": [list(p) for p in request.pairs],
            "full_intermediate_sum": list(range(request.max_ell+1)),
            "finite_block_only": True, "m": 0,
            "D1_profile_scope": "the two external rows needed by the specified D2 entry; not a separately executed full D1 matrix",
            "numerical_components": {
                "angular": "exact m0 Laurent reduction with Arb coefficient/evaluation roundoff",
                "Coulomb": "Arb H/H(B), analytic ODE Taylor disks, complex zero-free gates",
                "profiles": "validated Volterra primitives; upstream carry uncertainty retained",
                "integration": "polynomial integrals plus Cauchy remainders on every panel and every j",
                "roundoff": "all arithmetic enclosed by Arb; reported total includes accumulated coefficient and operation radii",
            },
            "analytic_radial_cutoff": to_jsonable(radial),
            "excluded_angular_bound": None, "original_driven_xi_certified": False,
            "PHYS63_qualitative_existence": "ESTABLISHED_REUSED",
            "NCP_submission": "NOT_SUBMITTED_BY_THIS_FUNCTION",
            "publication": "NOT_PERFORMED_BY_THIS_FUNCTION", "backup": "NOT_PERFORMED_BY_THIS_FUNCTION",
            "elapsed_seconds": time.monotonic()-started, "HH_R10": "OFF",
        }
        if complete:
            beta1 = radial["terms"][0]["radial_cutoff_bound"]
            beta2 = radial["terms"][1]["radial_cutoff_bound"]
            d1_errors = {pair_name(p): norm_radius_l1(q[p])+beta1 for p in request.pairs}
            numerror = norm_radius_l1(total)
            bound = numerror+beta2
            max_d1 = max(d1_errors.values())
            d1_met = max_d1 <= exact_fraction(request.d1_absolute_goal)
            d2_met = bound <= exact_fraction(request.d2_absolute_goal)
            final.update({
                "D1_B_cutoff": {pair_name(p): complex_ball_record(q[p]) for p in request.pairs},
                "D1_B_full_radial_absolute_error_l1": {p: _rational_record(e) for p, e in d1_errors.items()},
                "D1_B_max_full_radial_absolute_error_l1": _rational_record(max_d1),
                "D2_B_cutoff": complex_ball_record(total),
                "D2_B_full_radial_box": complex_ball_record(inflate_complex(total, rational_ball(beta2).upper())),
                "D2_numerical_absolute_error_l1": _rational_record(numerror),
                "D2_radial_cutoff_error": _rational_record(beta2),
                "D2_full_radial_absolute_error_about_cutoff_midpoint": _rational_record(bound),
                "absolute_goal_met": {"D1_B_all_requested_pairs": d1_met, "D2_target": d2_met},
                "status": "CERTIFIED_GOALS_MET" if d1_met and d2_met else "VALID_ENCLOSURE_GOAL_NOT_MET",
            })
        else:
            final["status"] = "PARTIAL_CHECKPOINT_NO_FINAL_CERTIFICATE"
        _write_json(out/"CERTIFICATE.json", final)
        return final
