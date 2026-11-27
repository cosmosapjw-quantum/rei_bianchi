"""Certified continuum reduction of the prescribed-rate HE33 mechanics.

The exact input is a piecewise-linear signed S(N), constant chi > 0, and
N=ln(a/a0) starting at zero.  The returned variables are r=q/p and
u=ln((p/p0)*exp(5*N)); Q=j=0 is required by this model.  No background or
transport-frequency uncertainty is included.

``certified`` means that the analytic *continuum approximation* envelopes
meet both requested tolerances.  It is not an outward-rounded machine proof.
Ordinary binary64 arithmetic, quadrature error estimates, and the analytic
omitted-layer tail are reported separately.  Invalid input raises ValueError;
unavailable or excessive certificates return an explicit nonaccepted result.

Dependencies: NumPy and SciPy.  Importing this module performs no computation
and writes no files.  See THEORY.md in the independent derivation evidence.
"""

from dataclasses import dataclass
import math
from typing import Tuple

import numpy as np
from scipy.integrate import quad


__all__ = ["solve_reduced", "ReducedSolution", "ReducedEvaluation", "IntervalDiagnostics"]

_SQRT32 = math.sqrt(32.0)
_TINY = np.finfo(float).tiny
_MIN_SUBNORMAL = float(np.nextafter(0.0, 1.0))


def _scalar(value, name):
    a = np.asarray(value)
    if a.ndim != 0 or a.dtype.kind not in "fiu":
        raise ValueError(f"{name} must be a real scalar")
    result = float(a)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _vector(value, name):
    a = np.asarray(value)
    if a.ndim != 1 or a.dtype.kind not in "fiu":
        raise ValueError(f"{name} must be a one-dimensional real array")
    a = np.array(a, dtype=float, copy=True)
    if not np.all(np.isfinite(a)):
        raise ValueError(f"{name} must contain only finite values")
    return a


def _readonly(a):
    a = np.asarray(a, dtype=float)
    a.flags.writeable = False
    return a


def _root(s, chi):
    """Rational stable root; scaling avoids unnecessary squared overflow."""
    scale = max(abs(s), chi)
    x, y = chi / scale, s / scale
    ds = math.hypot(x + 2.0 * y, _SQRT32 * y)
    b = -4.0 * y / (x + 2.0 * y + ds)
    d = scale * ds
    if not math.isfinite(d):
        raise ArithmeticError("stable-root rate is outside the finite binary64 range")
    return b, d


def _source(sa, sb, fraction):
    if fraction == 0.0:
        return sa
    if fraction == 1.0:
        return sb
    return (1.0 - fraction) * sa + fraction * sb


def _relaxation_integrals(kappa, h):
    """Return exp(-kh), m0, h-m0, m1=(h-m0)/k without cancellation."""
    z = kappa * h
    decay = math.exp(-z)
    if z < 1.0e-3:
        # m1/h^2 = 1/2-z/6+z^2/24-... .  This branch also handles
        # underflow of kappa*h to zero without changing m0's limit h.
        phi2 = 0.5 + z * (-1.0 / 6.0 + z * (1.0 / 24.0 + z * (
            -1.0 / 120.0 + z * (1.0 / 720.0 + z * (-1.0 / 5040.0)))))
        hm0 = h * (z * phi2)
        m0 = h * (1.0 - z * phi2)
        m1 = (h * h) * phi2
    else:
        m0 = -math.expm1(-z) / kappa
        hm0 = h - m0
        m1 = hm0 / kappa
    return decay, m0, hm0, m1


def _max_t_exp(rate, h, multiple=1.0):
    # Keeping a rate multiplier separate avoids overflowing 2*D when its
    # reciprocal, which is the required result, remains representable.
    z = rate * h
    return h * math.exp(-multiple * z) if z <= 1.0 / multiple else ((1.0 / rate) / multiple) / math.e


def _propagate_bounds(kappa, h, sm, residual, eleft, lleft):
    if residual == 0.0 and eleft == 0.0:
        return 0.0, lleft
    decay, m0, _, m1 = _relaxation_integrals(kappa, h)
    eend = decay * eleft + residual * m0
    # In particular, avoid 0*inf when h^2 is outside binary64 but the
    # corresponding residual term vanishes exactly.
    integrated = (eleft * m0 if eleft else 0.0) + (residual * m1 if residual else 0.0)
    return eend, lleft + 4.0 * sm * integrated


def _log1pmx(x):
    if abs(x) >= 1.0e-3:
        return math.log1p(x) - x
    # log(1+x)-x, retaining its O(x^2) value near zero.
    return x * x * (-0.5 + x * (1.0 / 3.0 + x * (-0.25 + x * (
        0.2 + x * (-1.0 / 6.0 + x * (1.0 / 7.0 + x * (-0.125)))))))


def _constant_pressure(sa, chi, h, rleft, ba, d0, c):
    z = d0 * h
    em1 = math.expm1(-z)
    w = c * em1
    logden = math.log1p(w)
    base = sa * (-4.0 * ba) * h
    if z < 1.0e-3:
        # base+logden can cancel to O(h^2) when rleft=0.  Use
        # -4*S*rleft*h+c*(z+expm1(-z))+(log1p(w)-w) instead.
        phi2 = 0.5 + z * (-1.0 / 6.0 + z * (1.0 / 24.0 + z * (
            -1.0 / 120.0 + z * (1.0 / 720.0 + z * (-1.0 / 5040.0)))))
        increment = math.fsum((sa * (-4.0 * rleft) * h,
                               c * z * z * phi2, _log1pmx(w)))
    else:
        increment = math.fsum((base, logden))
    return increment, base, logden


@dataclass(frozen=True)
class IntervalDiagnostics:
    index: int
    left: float
    right: float
    Sa: float
    Sb: float
    r_left: float
    r_right: float
    b_left: float
    D0: float
    delta0: float
    c: float
    denominator_min: float
    finite_interval_denominator_min: float
    cone_lower: float
    cone_upper: float
    cone_method: str
    kappa: float
    residual_bound: float
    certificate_valid: bool
    bound_available: bool
    approximation_valid: bool
    failures: Tuple[str, ...]
    root_pressure_increment: float
    layer_pressure_increment: float
    quadrature_error_estimate: float
    omitted_layer_tail_bound: float
    quadrature_evaluations: int
    layer_x_cap: float
    quadrature_converged: bool
    quadrature_messages: Tuple[str, ...]
    pressure_method: str


@dataclass(frozen=True)
class ReducedEvaluation:
    """Dense values; array shapes equal the input evaluation-point shape."""
    N: np.ndarray
    r: np.ndarray
    u: np.ndarray
    ratio_error_bound: np.ndarray
    logp_error_bound: np.ndarray
    quadrature_error_estimate: np.ndarray
    omitted_layer_tail_bound: np.ndarray


@dataclass(frozen=True)
class ReducedSolution:
    N: np.ndarray
    S: np.ndarray
    chi: float
    r: np.ndarray
    u: np.ndarray
    ratio_error_bound: np.ndarray
    logp_error_bound: np.ndarray
    quadrature_error_estimate_at_nodes: np.ndarray
    omitted_layer_tail_bound_at_nodes: np.ndarray
    tol_ratio: float
    tol_logp: float
    certificate_valid: bool
    certified: bool
    certificate_failures: Tuple[str, ...]
    approximation_valid: bool
    quadrature_converged: bool
    intervals: Tuple[IntervalDiagnostics, ...]
    _quad_abs_per_interval: float

    @property
    def interval_count(self):
        return len(self.N) - 1

    @property
    def max_ratio_error_bound(self):
        return float(np.max(self.ratio_error_bound))

    @property
    def final_logp_error_bound(self):
        return float(self.logp_error_bound[-1])

    @property
    def quadrature_error_estimate(self):
        return float(self.quadrature_error_estimate_at_nodes[-1])

    @property
    def omitted_layer_tail_bound(self):
        return float(self.omitted_layer_tail_bound_at_nodes[-1])

    @property
    def status(self):
        if not self.approximation_valid:
            return "approximation_unavailable"
        if not self.certificate_valid:
            return "certificate_unavailable"
        return "accepted_continuum_bound" if self.certified else "bound_not_met"

    def evaluate(self, N_eval):
        """Evaluate the same candidate and continuum envelope, without extrapolation.

        Dense pressure values require fresh scalar quadrature on partial
        nonconstant intervals.  Its estimate and analytic omitted tail are
        returned separately, cumulatively from N=0.  Stored knots are reused.
        """
        points = np.asarray(N_eval)
        if points.dtype.kind not in "fiu":
            raise ValueError("evaluation points must be real")
        points = np.array(points, dtype=float, copy=True)
        if (not np.all(np.isfinite(points)) or np.any(points < self.N[0])
                or np.any(points > self.N[-1])):
            raise ValueError("evaluation points must be finite and inside the knot interval")
        outputs = [np.empty(points.size, dtype=float) for _ in range(6)]
        for k, point in enumerate(points.flat):
            j = int(np.searchsorted(self.N, point, side="right") - 1)
            if point == self.N[j]:
                values = (self.r[j], self.u[j], self.ratio_error_bound[j],
                          self.logp_error_bound[j], self.quadrature_error_estimate_at_nodes[j],
                          self.omitted_layer_tail_bound_at_nodes[j])
            elif j >= len(self.intervals) or not self.intervals[j].approximation_valid:
                values = (math.nan, math.nan, math.inf, math.inf, math.inf, math.inf)
            else:
                rec = self.intervals[j]
                tau = float(point - rec.left)
                rr = _candidate(rec, self.chi, tau)
                ui, _, _, qe, tail, _, _, _, _ = _pressure_increment(
                    rec, self.chi, tau, self._quad_abs_per_interval)
                if rec.bound_available:
                    ee, ll = _propagate_bounds(rec.kappa, tau, max(abs(rec.Sa), abs(rec.Sb)),
                        rec.residual_bound, self.ratio_error_bound[j], self.logp_error_bound[j])
                else:
                    ee = ll = math.inf
                values = (rr, self.u[j] + ui, ee, ll,
                          self.quadrature_error_estimate_at_nodes[j] + qe,
                          self.omitted_layer_tail_bound_at_nodes[j] + tail)
            for output, value in zip(outputs, values):
                output[k] = value
        return ReducedEvaluation(_readonly(points), *(
            _readonly(a.reshape(points.shape)) for a in outputs))


def _candidate(rec, chi, tau):
    if tau == 0.0:
        return rec.r_left
    h = rec.right - rec.left
    s = _source(rec.Sa, rec.Sb, tau / h)
    b, _ = _root(s, chi)
    z = rec.D0 * tau
    em1 = math.expm1(-z)
    denominator = 1.0 + rec.c * em1
    if denominator <= 0.0:
        raise ArithmeticError("initial-layer denominator is nonpositive")
    if z < 0.5:
        change = rec.delta0 * (1.0 - rec.c) * em1 / denominator
        return math.fsum((rec.r_left, b - rec.b_left, change))
    return b + rec.delta0 * math.exp(-z) / denominator


def _quad_with_report(fun, lower, upper, epsabs):
    result = quad(fun, lower, upper, epsabs=epsabs, epsrel=2.0e-13,
                  limit=100, full_output=1)
    value, estimate, info = result[:3]
    messages = tuple(str(x) for x in result[3:])
    converged = not messages and math.isfinite(value) and math.isfinite(estimate)
    return value, estimate, int(info["neval"]), converged, messages


def _pressure_increment(rec, chi, tau, epsabs):
    """Return total, base, layer, estimate, tail, neval, cap, ok, messages."""
    if tau == 0.0:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, True, ()
    if rec.Sa == rec.Sb:
        total, base, layer = _constant_pressure(rec.Sa, chi, tau, rec.r_left,
                                                rec.b_left, rec.D0, rec.c)
        return total, base, layer, 0.0, 0.0, 0, 0.0, True, ()
    h = rec.right - rec.left

    def base_fun(t):
        s = _source(rec.Sa, rec.Sb, t / h)
        b, _ = _root(s, chi)
        # Algebraically 16*S^2/(D+chi+2*S), without squaring S.
        return s * (-4.0 * b)

    base, eb, nb, okb, mb = _quad_with_report(base_fun, 0.0, tau, epsabs / 2.0)
    if rec.delta0 == 0.0:
        return base, base, 0.0, eb, 0.0, nb, 0.0, okb, mb
    end_x = rec.D0 * tau
    den_end = 1.0 + rec.c * math.expm1(-end_x)
    den_min = min(1.0, den_end)
    if den_min <= 0.0:
        raise ArithmeticError("initial-layer denominator is nonpositive")
    # A finite-interval denominator also bounds the omitted finite tail when
    # the stronger asymptotic denominator check has made proof unavailable.
    amplitude = abs(rec.delta0) / den_min
    sm = max(abs(rec.Sa), abs(_source(rec.Sa, rec.Sb, tau / h)))
    log_prefactor = (math.log(4.0) + math.log(sm) + math.log(amplitude)
                     - math.log(rec.D0)) if sm > 0.0 and amplitude > 0.0 else -math.inf
    cap_needed = max(48.0, log_prefactor - math.log(max(epsabs / 4.0, _TINY)))
    cap = min(end_x, cap_needed)

    def layer_fun(x):
        s = _source(rec.Sa, rec.Sb, (x / rec.D0) / h)
        denominator = 1.0 + rec.c * math.expm1(-x)
        delta = rec.delta0 * math.exp(-x) / denominator
        return (s / rec.D0) * (-4.0 * delta)

    layer, el, nl, okl, ml = _quad_with_report(layer_fun, 0.0, cap, epsabs / 2.0)
    tail = 0.0
    if cap < end_x and log_prefactor != -math.inf:
        tail = max(math.exp(log_prefactor - cap), _MIN_SUBNORMAL)
    return math.fsum((base, layer)), base, layer, eb + el, tail, nb + nl, cap, okb and okl, mb + ml


def solve_reduced(N_knots, S_knots, chi, r0=0.0, tol_ratio=1.0e-6, tol_logp=1.0e-6):
    """Solve the algebraic-root plus frozen nonlinear-layer approximation.

    Parameters are finite real values.  N_knots starts at exactly zero and
    increases strictly; there must be at least two matching N and S values.
    chi and both tolerances are strictly positive; r0 belongs to [-1/2, 1].
    The arrays in the result are read-only.  u[0]=0 exactly.

    ``certificate_valid`` requires positive kappa, positive asymptotic layer
    denominator, a rigorous cone enclosure, and finite analytic envelopes on
    every interval.  ``certified`` additionally requires max(E)<=tol_ratio and
    L_final<=tol_logp.  Bound failure preserves the candidate; unrecoverable
    numerical range/pole failures preserve the completed prefix and mark the
    remaining values unavailable.  No clipping or tolerance relaxation occurs.
    """
    N, S = _vector(N_knots, "N_knots"), _vector(S_knots, "S_knots")
    chi, r0 = _scalar(chi, "chi"), _scalar(r0, "r0")
    tol_ratio, tol_logp = _scalar(tol_ratio, "tol_ratio"), _scalar(tol_logp, "tol_logp")
    if len(N) < 2 or len(S) != len(N):
        raise ValueError("N_knots and S_knots must have matching lengths of at least two")
    if N[0] != 0.0:
        raise ValueError("N_knots must start at zero, where a=a0 and p=p0")
    with np.errstate(over="ignore", invalid="ignore"):
        widths = np.diff(N)
    if not np.all(np.isfinite(widths)) or np.any(widths <= 0.0):
        raise ValueError("N_knots must increase strictly with finite interval widths")
    if chi <= 0.0 or tol_ratio <= 0.0 or tol_logp <= 0.0:
        raise ValueError("chi, tol_ratio, and tol_logp must be strictly positive")
    if not -0.5 <= r0 <= 1.0:
        raise ValueError("r0 must lie in the invariant pressure cone [-1/2, 1]")
    count = len(N) - 1
    epsabs = max(_TINY, min(1.0e-13, tol_logp / (64.0 * count)))
    r, u = np.full(len(N), math.nan), np.full(len(N), math.nan)
    eb, lb, qe, tails = (np.full(len(N), math.inf) for _ in range(4))
    r[0], u[0] = r0, 0.0
    eb[0] = lb[0] = qe[0] = tails[0] = 0.0
    records, failures = [], []
    proof_available, approximation_valid, quadrature_ok = True, True, True

    for j, width in enumerate(widths):
        h, sa, sb, rleft = float(width), float(S[j]), float(S[j + 1]), float(r[j])
        sm = max(abs(sa), abs(sb))
        kappa = chi - 6.0 * sm
        local_failures = []
        if kappa <= 0.0 or not math.isfinite(kappa):
            local_failures.append("kappa_nonpositive_or_nonfinite")
        try:
            ba, d0 = _root(sa, chi)
            bb, _ = _root(sb, chi)
            delta0 = rleft - ba
            # Avoid forming the potentially overflowing product 4*Sa.
            c = (sa / d0) * (4.0 * delta0)
            dmin = min(1.0, 1.0 - c)
            den_end = 1.0 + c * math.expm1(-d0 * h)
            finite_dmin = min(1.0, den_end)
            if dmin <= 0.0 or not math.isfinite(dmin):
                local_failures.append("denominator_nonpositive_or_nonfinite")
            if finite_dmin <= 0.0 or not math.isfinite(finite_dmin):
                raise ArithmeticError("initial-layer denominator is nonpositive on the interval")
            delta_end = delta0 * math.exp(-d0 * h) / den_end
            rend = bb + delta_end
            if sa == sb:
                cone_lo, cone_hi = min(rleft, ba), max(rleft, ba)
                cone_method = "constant_frozen_flow"
            elif (sb >= sa and delta0 >= 0.0) or (sb <= sa and delta0 <= 0.0):
                cone_lo, cone_hi = min(rleft, rend), max(rleft, rend)
                cone_method = "aligned_monotone_root_and_layer"
            else:
                cone_lo = min(ba, bb) + min(delta0, delta_end)
                cone_hi = max(ba, bb) + max(delta0, delta_end)
                cone_method = "sum_of_analytic_endpoint_ranges"
            if not (-0.5 <= cone_lo <= cone_hi <= 1.0):
                local_failures.append("candidate_cone_not_proved")
            residual = math.inf
            if not local_failures:
                if sa == sb:
                    residual = 0.0
                else:
                    ls = abs(sb - sa) / h
                    d_lower = chi - 2.0 * sm
                    b_bound = 2.0 * (sm / chi) / (1.0 - 2.0 * (sm / chi))
                    amplitude = abs(delta0) / dmin
                    rb = min(2.25, 2.0 + 2.0 * b_bound + 4.0 * b_bound**2) * (ls / d_lower)
                    ld = ((2.0 + 36.0 * (sm / chi)) / (1.0 - 2.0 * (sm / chi))) * ls
                    residual = rb + ld * amplitude * _max_t_exp(d0, h) + (
                        4.0 * ls * amplitude**2 * _max_t_exp(d0, h, 2.0))
                if not math.isfinite(residual):
                    local_failures.append("residual_bound_nonfinite")
            bound_available = proof_available and not local_failures
            rec = IntervalDiagnostics(j, float(N[j]), float(N[j + 1]), sa, sb,
                rleft, rend, ba, d0, delta0, c, dmin, finite_dmin,
                cone_lo, cone_hi, cone_method, kappa, residual,
                not local_failures, bound_available, True, tuple(local_failures),
                0.0, 0.0, 0.0, 0.0, 0, 0.0, True, (),
                "constant_source_closed_form" if sa == sb else "root_quad_and_rescaled_layer_quad")
            # The near-left form also improves an extremely short endpoint.
            rend = _candidate(rec, chi, h)
            increment, base, layer, err, tail, neval, cap, qok, messages = _pressure_increment(
                rec, chi, h, epsabs)
            if not math.isfinite(rend) or not math.isfinite(increment):
                raise ArithmeticError("candidate or pressure increment is nonfinite")
            if bound_available:
                eb[j + 1], lb[j + 1] = _propagate_bounds(kappa, h, sm, residual, eb[j], lb[j])
                if not math.isfinite(eb[j + 1]) or not math.isfinite(lb[j + 1]):
                    local_failures.append("propagated_bound_nonfinite")
                    bound_available = False
                    eb[j + 1] = lb[j + 1] = math.inf
            r[j + 1], u[j + 1] = rend, u[j] + increment
            if not math.isfinite(u[j + 1]):
                raise ArithmeticError("accumulated log pressure is nonfinite")
            qe[j + 1], tails[j + 1] = qe[j] + err, tails[j] + tail
            rec = IntervalDiagnostics(j, float(N[j]), float(N[j + 1]), sa, sb,
                rleft, rend, ba, d0, delta0, c, dmin, finite_dmin,
                cone_lo, cone_hi, cone_method, kappa, residual,
                not local_failures, bound_available, True, tuple(local_failures),
                base, layer, err, tail, neval, cap, qok, messages, rec.pressure_method)
            records.append(rec)
            quadrature_ok = quadrature_ok and qok
            if local_failures:
                proof_available = False
                failures.extend(f"interval {j}: {why}" for why in local_failures)
        except (ArithmeticError, ValueError, OverflowError) as exc:
            # Preserve useful completed nodes.  Do not silently switch model,
            # clip a denominator, relax a tolerance, or hide a failure.
            approximation_valid = proof_available = False
            failures.extend(f"interval {j}: {why}" for why in local_failures)
            failures.append(f"interval {j}: approximation_unavailable: {exc}")
            break

    certificate_valid = proof_available and approximation_valid and len(records) == count
    max_e, final_l = float(np.max(eb)), float(lb[-1])
    if certificate_valid and max_e > tol_ratio:
        failures.append("ratio_tolerance_not_met")
    if certificate_valid and final_l > tol_logp:
        failures.append("logp_tolerance_not_met")
    certified = certificate_valid and max_e <= tol_ratio and final_l <= tol_logp
    return ReducedSolution(*(_readonly(a) for a in (N, S)), chi,
        *(_readonly(a) for a in (r, u, eb, lb, qe, tails)),
        tol_ratio, tol_logp, certificate_valid, certified, tuple(failures),
        approximation_valid, quadrature_ok, tuple(records), epsabs)
