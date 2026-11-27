"""R10 exact full-generator coefficient and outward triangular comparison flow.

Every numerical input is exact.  A lower endpoint encloses the *ideal comparison
solution*, never the physical error.  Metadata identity checks do not certify the
truth of a caller's physical source, invariant box, or previously proved caps.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from fractions import Fraction
from math import factorial
import re

R9_SHA256 = "494fad7b2195dfbf16857901127cdaa676d83cb1beafbf2c081122f99ba2d8d7"
BITS = 128
DEGREE = 96
MAX_SCALAR_BITS = 8192


class DomainError(ValueError):
    pass


def Q(value):
    """Parse a bounded exact scalar; binary floats and booleans are refused."""
    if isinstance(value, bool) or not isinstance(value, (int, str, Fraction)):
        raise DomainError("An exact int, Fraction, or rational string is required")
    if isinstance(value, str) and len(value) > 6000:
        raise DomainError("Rational text exceeds the finite scalar domain")
    try:
        out = Fraction(value)
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise DomainError("Invalid exact rational") from exc
    if max(abs(out.numerator).bit_length(), out.denominator.bit_length()) > MAX_SCALAR_BITS:
        raise DomainError("Scalar exceeds 8192-bit numerator/denominator domain")
    return out


def _int(value, lo, hi, name):
    if isinstance(value, bool) or not isinstance(value, int) or not lo <= value <= hi:
        raise DomainError(f"{name} must be an integer in [{lo},{hi}]")
    return value


def _vec(values, name, length=None, nonnegative=False):
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise DomainError(name + " must be a finite sequence")
    ans = tuple(Q(x) for x in values)
    if length is not None and len(ans) != length:
        raise DomainError(name + " dimension mismatch")
    if nonnegative and any(x < 0 for x in ans):
        raise DomainError(name + " must be nonnegative")
    return ans


def _nonnegative(value, name):
    q = Q(value)
    if q < 0:
        raise DomainError(name + " must be nonnegative")
    return q


def _positive(value, name):
    q = Q(value)
    if q <= 0:
        raise DomainError(name + " must be positive")
    return q


def _ceil(n, d):
    return -(-n // d)


def _scaled(q, scale, upward):
    n = q.numerator * scale
    return _ceil(n, q.denominator) if upward else n // q.denominator


def down(q, bits=BITS):
    _int(bits, BITS, BITS, "bits")
    q = Q(q)
    return Fraction(_scaled(q, 1 << bits, False), 1 << bits)


def up(q, bits=BITS):
    _int(bits, BITS, BITS, "bits")
    q = Q(q)
    return Fraction(_scaled(q, 1 << bits, True), 1 << bits)


def _binding(value, n):
    if not isinstance(value, Mapping):
        raise DomainError("Source/family/clock binding is required")
    out = deepcopy(dict(value))
    for key in ("family_id", "clock", "source_sha256", "norm"):
        if not isinstance(out.get(key), str) or not out[key].strip():
            raise DomainError("Nonempty binding " + key + " is required")
    if not re.fullmatch(r"[0-9a-f]{64}", out["source_sha256"]):
        raise DomainError("Binding source SHA256 is malformed")
    if out["norm"] != "l1_on_kerP":
        raise DomainError("Only l1 on the zero-sum residual space is supported")
    ids = out.get("state_ids")
    if (not isinstance(ids, (list, tuple)) or len(ids) != n or
            any(not isinstance(x, str) or not x for x in ids) or len(set(ids)) != n):
        raise DomainError("Unique ordered state IDs must match the generator")
    return out


def _generator(values, n):
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)) or len(values) != n:
        raise DomainError("Generator row dimension mismatch")
    A = tuple(_vec(row, "generator row", n) for row in values)
    if any(A[i][j] < 0 for i in range(n) for j in range(n) if i != j):
        raise DomainError("Generator must have nonnegative off-diagonal entries")
    if any(sum(A[i][j] for i in range(n)) != 0 for j in range(n)):
        raise DomainError("Generator columns must sum exactly to zero")
    return A


def _contraction(A):
    n = len(A)
    if n == 1:
        return Fraction(0), ()
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            val = A[i][j] + A[j][i] + sum(
                (min(A[k][i], A[k][j]) for k in range(n) if k not in (i, j)), Fraction(0))
            pairs.append({"i": i, "j": j, "overlap": val})
    return min(p["overlap"] for p in pairs), tuple(pairs)


def generator_certificate(K, pi, destruction, w_box, *, binding):
    """Exact min coefficient of K+w*(pi*d^T-diag(d)), w in [mw,Mw]."""
    p = _vec(pi, "pi", nonnegative=True)
    if not 1 <= len(p) <= 13 or sum(p) != 1:
        raise DomainError("pi must be an exact simplex point of dimension1..13")
    n = len(p)
    k = _generator(K, n)
    ds = _vec(destruction, "destruction", n, nonnegative=True)
    box = _vec(w_box, "w box", 2, nonnegative=True)
    if box[0] > box[1]:
        raise DomainError("w box is reversed or empty")
    bind = _binding(binding, n)
    H = tuple(tuple(p[i] * ds[j] - (ds[j] if i == j else 0)
                    for j in range(n)) for i in range(n))
    _generator(H, n)
    def at(w):
        return tuple(tuple(k[i][j] + w * H[i][j] for j in range(n)) for i in range(n))
    lower, upper = at(box[0]), at(box[1])
    lamK, pairsK = _contraction(k)
    lamH, pairsH = _contraction(H)
    lam, pairs = _contraction(lower)
    endpoint, upperpairs = _contraction(upper)
    separate = lamK + box[0] * lamH
    if not 0 <= separate <= lam <= endpoint:
        raise DomainError("Exact full-generator monotonicity check failed")
    return {
        "schema": "WU_R10_FULL_GENERATOR_COEFFICIENT_V1", "dimension": n,
        "lambda": lam, "lambda_K": lamK, "lambda_H": lamH,
        "separate_sum_lower": separate, "lambda_at_w_upper": endpoint,
        "w_box": box, "H": H, "A_w_lower": lower, "A_w_upper": upper,
        "pairs_K": pairsK, "pairs_H": pairsH, "pairs_w_lower": pairs,
        "pairs_w_upper": upperpairs, "binding": bind,
        "uniform_minimum_reason": "Each pair-overlap is nondecreasing in w; exact minimum at w lower",
        "generator_scope": "fixed_exact_K_pi_d_with_w_in_declared_interval",
        "n1_zero_residual_subspace": n == 1,
        "nominal_K_block_rho_transferred": False,
        "physical_consumer_admitted": False,
    }


def _tail_int(norm_int, scale, degree):
    """Ceiling of scalar geometric Taylor remainder on the dyadic grid."""
    alpha = Fraction(norm_int, scale)
    if alpha < 0 or alpha > 16:
        raise DomainError("Rounded positive-series infinity norm exceeds16")
    if alpha == 0:
        return 0
    tail = alpha ** (degree + 1) / factorial(degree + 1) / (1 - alpha / (degree + 2))
    return _scaled(tail, scale, True)


def _scalar_positive(z, scale, degree):
    zl, zu = _scaled(z, scale, False), _scaled(z, scale, True)
    if zl < 0 or zu > 16 * scale:
        raise DomainError("Scalar exponential argument exceeds[0,16]")
    tl = tu = sl = su = scale
    for k in range(1, degree + 1):
        tl = tl * zl // (scale * k)
        tu = _ceil(tu * zu, scale * k)
        sl += tl
        su += tu
    tail = _tail_int(zu, scale, degree)
    return sl, su + tail, tail


def _matrix_positive(C, scale, degree):
    lo = [[_scaled(x, scale, False) for x in row] for row in C]
    hi = [[_scaled(x, scale, True) for x in row] for row in C]
    if any(x < 0 for row in lo for x in row):
        raise DomainError("Shifted comparison matrix must be nonnegative")
    norm = max(sum(row) for row in hi)
    if norm > 16 * scale:
        raise DomainError("Rounded positive-series infinity norm exceeds16")
    tl = [[scale * int(i == j) for j in range(3)] for i in range(3)]
    tu = [row[:] for row in tl]
    sl = [row[:] for row in tl]
    su = [row[:] for row in tl]
    for k in range(1, degree + 1):
        tl = [[sum(lo[i][m] * tl[m][j] for m in range(3)) // (scale * k)
               for j in range(3)] for i in range(3)]
        tu = [[_ceil(sum(hi[i][m] * tu[m][j] for m in range(3)), scale * k)
               for j in range(3)] for i in range(3)]
        for i in range(3):
            for j in range(3):
                sl[i][j] += tl[i][j]
                su[i][j] += tu[i][j]
    tail = _tail_int(norm, scale, degree)
    for i in range(3):
        for j in range(3):
            su[i][j] += tail
    return sl, su, {
        "C_lower": tuple(tuple(Fraction(x, scale) for x in row) for row in lo),
        "C_upper": tuple(tuple(Fraction(x, scale) for x in row) for row in hi),
        "norm_upper": Fraction(norm, scale), "tail_upper_per_entry": Fraction(tail, scale),
    }


def flow_interval(lam, c, d, g_r, g_e, delta, *, whole=False, bits=BITS, degree=DEGREE):
    """Outward matrix exp(delta*M); homogeneous augmentation avoids inverses."""
    _int(bits, BITS, BITS, "bits")
    _int(degree, DEGREE, DEGREE, "degree")
    if not isinstance(whole, bool):
        raise DomainError("whole must be boolean")
    lam = _nonnegative(lam, "lambda")
    c = _nonnegative(c, "c")
    d = Q(d)
    gr, ge = _nonnegative(g_r, "g_r"), _nonnegative(g_e, "g_e")
    delta = _positive(delta, "delta")
    if whole:
        M = ((Fraction(0), Fraction(0), gr), (c, max(d, Fraction(0)), ge),
             (Fraction(0), Fraction(0), Fraction(0)))
        shift = Fraction(0)
    else:
        M = ((-lam, Fraction(0), gr), (c, d, ge),
             (Fraction(0), Fraction(0), Fraction(0)))
        shift = max(lam, -d, Fraction(0))
    C = tuple(tuple(delta * (M[i][j] + (shift if i == j else 0))
                    for j in range(3)) for i in range(3))
    scale = 1 << bits
    sl, su, matrix_meta = _matrix_positive(C, scale, degree)
    scalar_lo, scalar_hi, scalar_tail = _scalar_positive(delta * shift, scale, degree)
    reciprocal_lo = scale * scale // scalar_hi
    reciprocal_hi = _ceil(scale * scale, scalar_lo)
    lower = [[Fraction(sl[i][j] * reciprocal_lo // scale, scale) for j in range(3)] for i in range(3)]
    upper = [[Fraction(_ceil(su[i][j] * reciprocal_hi, scale), scale) for j in range(3)] for i in range(3)]
    # These structural equalities are exact for this fixed triangular affine M.
    for i, j in ((0, 1), (2, 0), (2, 1)):
        lower[i][j] = upper[i][j] = Fraction(0)
    lower[2][2] = upper[2][2] = Fraction(1)
    if gr == 0:
        lower[0][2] = upper[0][2] = Fraction(0)
    if c == 0:
        lower[1][0] = upper[1][0] = Fraction(0)
    if ge == 0 and c * gr == 0:
        lower[1][2] = upper[1][2] = Fraction(0)
    for i in (0, 1):
        if M[i][i] == 0:
            lower[i][i] = upper[i][i] = Fraction(1)
    return {
        "schema": "WU_R10_TRIANGULAR_FLOW_INTERVAL_V1", "M": M, "delta": delta,
        "lower": tuple(map(tuple, lower)), "upper": tuple(map(tuple, upper)),
        "shift": shift, "positive_series": matrix_meta,
        "negative_scalar_exp_interval": (Fraction(reciprocal_lo, scale), Fraction(reciprocal_hi, scale)),
        "scalar_positive_tail_upper": Fraction(scalar_tail, scale),
        "bits": bits, "degree": degree, "whole_cell_monotone_majorant": whole,
        "inverse_of_M_used": False,
    }


def _apply(A, state, upward, scale):
    vector = tuple(state) + (Fraction(1),)
    return tuple(Fraction(_scaled(sum((A[i][j] * vector[j] for j in range(3)), Fraction(0)),
                                         scale, upward), scale) for i in range(2))


def _caps(value, kind, delta, cells, bind):
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise DomainError("Caps require a source-bound mapping")
    if value.get("source_sha256") != R9_SHA256:
        raise DomainError("Cap source SHA256 is not frozen R9 primary")
    suffix = "whole_cells" if kind == "whole" else "endpoints"
    if value.get("source_kind") != "saved_R9_" + suffix:
        raise DomainError("Only saved certified R9 upper bounds are accepted as caps")
    pointer = value.get("source_pointer")
    if not isinstance(pointer, str) or not re.fullmatch(r"/hd_cases/[0-3]/capped/" + suffix, pointer):
        raise DomainError("Cap source pointer must identify the frozen same-kind R9 field")
    if Q(value.get("delta")) != delta or value.get("cells") != cells or isinstance(value.get("cells"), bool):
        raise DomainError("Cap grid differs")
    if value.get("binding") != bind:
        raise DomainError("Cap family/state/clock binding differs")
    rows = value.get("upper")
    count = cells if kind == "whole" else cells + 1
    if not isinstance(rows, (list, tuple)) or len(rows) != count:
        raise DomainError("Cap array geometry differs")
    return tuple(_vec(row, "cap upper", 2, nonnegative=True) for row in rows)


def sweep(K, pi, destruction, w_box, c, d, g_r, g_e, delta, initial, cells, *,
          binding, whole_caps=None, point_caps=None, bits=BITS, degree=DEGREE):
    """Propagate a triangular comparison and optional certified same-case caps."""
    _int(bits, BITS, BITS, "bits")
    _int(degree, DEGREE, DEGREE, "degree")
    cells = _int(cells, 1, 192, "cells")
    dt = _positive(delta, "delta")
    initial = _vec(initial, "initial", 2, nonnegative=True)
    cert = generator_certificate(K, pi, destruction, w_box, binding=binding)
    c, d = _nonnegative(c, "c"), Q(d)
    gr, ge = _nonnegative(g_r, "g_r"), _nonnegative(g_e, "g_e")
    if cert["dimension"] == 1 and (initial[0] != 0 or gr != 0 or c != 0):
        raise DomainError("Dimension1 residual requires R0=g_r=c=0 in this finite API")
    bind = cert["binding"]
    wc, pc = _caps(whole_caps, "whole", dt, cells, bind), _caps(point_caps, "point", dt, cells, bind)
    if (wc is None) != (pc is None):
        raise DomainError("Capped mode requires both same-cell and same-clock cap arrays")
    capped = wc is not None
    if capped and any(pc[0][i] < initial[i] or wc[0][i] < initial[i] for i in range(2)):
        raise DomainError("Initial caps must contain the declared initial radius")
    if capped:
        left = whole_caps["source_pointer"].split("/")[2]
        right = point_caps["source_pointer"].split("/")[2]
        if left != right:
            raise DomainError("Whole/point caps must come from the same saved R9 case")
    flow = flow_interval(cert["lambda"], c, d, gr, ge, dt, bits=bits, degree=degree)
    whole_flow = flow_interval(cert["lambda"], c, d, gr, ge, dt, whole=True, bits=bits, degree=degree)
    scale = 1 << bits
    endpoint_upper = [initial]
    endpoint_lower = [initial] if not capped else None
    whole_upper = []
    for n in range(cells):
        point = _apply(flow["upper"], endpoint_upper[-1], True, scale)
        whole = _apply(whole_flow["upper"], endpoint_upper[-1], True, scale)
        if capped:
            whole = tuple(min(whole[i], wc[n][i]) for i in range(2))
            point = tuple(min(point[i], whole[i], pc[n + 1][i]) for i in range(2))
        else:
            # Preserve coverage of the reported outward endpoint as well as all
            # ideal continuous times; the added max is a rounding enclosure.
            whole = tuple(max(whole[i], point[i]) for i in range(2))
            endpoint_lower.append(_apply(flow["lower"], endpoint_lower[-1], False, scale))
        endpoint_upper.append(point)
        whole_upper.append(whole)
    return {
        "schema": "WU_R10_TRIANGULAR_SWEEP_V1", "mode": "capped" if capped else "raw",
        "generator": cert, "coefficients": {"lam": cert["lambda"], "c": c, "d": d, "g_r": gr, "g_e": ge},
        "delta": dt, "cells": cells, "initial": initial, "binding": bind,
        "endpoints_lower": endpoint_lower, "endpoints_upper": endpoint_upper,
        "whole_cells_upper": whole_upper, "flow_interval": flow, "whole_flow_interval": whole_flow,
        "lower_endpoint_meaning": "ideal uncapped comparison solution only" if not capped else None,
        "cap_source_sha256": R9_SHA256 if capped else None,
        "rounding": {"bits": bits, "degree": degree, "per_term_and_state_directed": True,
                     "raw_whole_includes_reported_outward_endpoint": True},
        "certificate_validity": "conditional on supplied source/box/coefficient/cap premises; metadata checks do not prove them",
        "physical_consumer_admitted": False, "new_ODE_calls": 0,
    }


def export(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Mapping):
        return {str(k): export(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [export(v) for v in value]
    return value
