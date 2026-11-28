"""Uniform full-A block certificate and outward causal forcing convolution.

The nominal K block, whole-domain forcing, and source-backed caps are explicit
input premises. Metadata validation cannot establish an external scientific
premise. Raw lower arrays enclose the chosen ideal comparison, not true errors.
No predecessor scientific module, ODE solver, or native-source runner is used.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from fractions import Fraction
from math import factorial
import hashlib
import json
import re

BITS = 128
DEGREE = 96
MAX_SCALAR_BITS = 8192
R10_SHA256 = "1713df54bc3653003614f3deba93212735a345e8d7220f053ab9af2d84677fb1"


class DomainError(ValueError):
    pass


def Q(value):
    if isinstance(value, bool) or not isinstance(value, (int, str, Fraction)):
        raise DomainError("Exact int, Fraction, or rational text required")
    if isinstance(value, str) and len(value) > 6000:
        raise DomainError("Rational text exceeds the finite scalar domain")
    try:
        out = Fraction(value)
    except (ValueError, ZeroDivisionError, TypeError) as exc:
        raise DomainError("Invalid exact scalar") from exc
    if max(abs(out.numerator).bit_length(), out.denominator.bit_length()) > MAX_SCALAR_BITS:
        raise DomainError("Input exceeds 8192-bit numerator/denominator limit")
    return out


def _int(v, lo, hi, name):
    if isinstance(v, bool) or not isinstance(v, int) or not lo <= v <= hi:
        raise DomainError(f"{name} must be integer in [{lo},{hi}]")
    return v


def _seq(v):
    return isinstance(v, Sequence) and not isinstance(v, (str, bytes))


def _vec(v, name, length=None, nonnegative=False):
    if not _seq(v):
        raise DomainError(name + " must be a finite sequence")
    ans = tuple(Q(x) for x in v)
    if length is not None and len(ans) != length:
        raise DomainError(name + " dimension mismatch")
    if nonnegative and any(x < 0 for x in ans):
        raise DomainError(name + " must be nonnegative")
    return ans


def _nonneg(v, name):
    x = Q(v)
    if x < 0:
        raise DomainError(name + " must be nonnegative")
    return x


def _positive(v, name):
    x = Q(v)
    if x <= 0:
        raise DomainError(name + " must be positive")
    return x


def _ceil(n, d):
    return -(-n // d)


def _floor_scaled(v, scale):
    return v.numerator * scale // v.denominator


def _ceil_scaled(v, scale):
    return _ceil(v.numerator * scale, v.denominator)


def down(v):
    return Fraction(_floor_scaled(v, 1 << BITS), 1 << BITS)


def up(v):
    return Fraction(_ceil_scaled(v, 1 << BITS), 1 << BITS)


def _binding(v, n=None):
    if not isinstance(v, Mapping):
        raise DomainError("A source/family/state/clock binding is required")
    out = deepcopy(dict(v))
    for key in ("family_id", "clock", "source_sha256", "norm"):
        if not isinstance(out.get(key), str) or not out[key].strip():
            raise DomainError("Nonempty binding " + key + " is required")
    if not re.fullmatch(r"[0-9a-f]{64}", out["source_sha256"]):
        raise DomainError("Malformed source SHA256")
    if out["norm"] != "l1_on_kerP":
        raise DomainError("Only zero-mass l1 normalization is accepted")
    ids = out.get("state_ids")
    if (not _seq(ids) or not 1 <= len(ids) <= 13 or
            any(not isinstance(x, str) or not x for x in ids) or
            len(set(ids)) != len(ids) or (n is not None and len(ids) != n)):
        raise DomainError("Unique ordered state IDs must match dimension1..13")
    out["state_ids"] = list(ids)
    return out


def _generator(K, n):
    if not _seq(K) or len(K) != n:
        raise DomainError("Generator dimension mismatch")
    mat = tuple(_vec(row, "generator row", n) for row in K)
    if any(mat[i][j] < 0 for i in range(n) for j in range(n) if i != j):
        raise DomainError("Generator off-diagonals must be nonnegative")
    if any(sum(mat[i][j] for i in range(n)) != 0 for j in range(n)):
        raise DomainError("Generator columns must sum exactly to zero")
    return mat


def matrix_identity(K):
    """Canonical exact-rational matrix identity, independent of input spelling."""
    val = [[str(Q(x)) for x in row] for row in K]
    return hashlib.sha256(json.dumps(val, separators=(",", ":")).encode()).hexdigest()


def _tail(z, scale):
    a = Fraction(z, scale)
    if not 0 <= a <= 16:
        raise DomainError("Positive-series rounded argument exceeds[0,16]")
    if not a:
        return 0
    rem = a ** (DEGREE + 1) / factorial(DEGREE + 1) / (1 - a / (DEGREE + 2))
    return _ceil_scaled(rem, scale)


def _positive_series(x):
    """Directed exp and positive Bernstein series at 0<=x<=16."""
    scale = 1 << BITS
    xl, xu = _floor_scaled(x, scale), _ceil_scaled(x, scale)
    if xl < 0 or xu > 16 * scale:
        raise DomainError("Scalar scaled exponential argument exceeds[0,16]")
    tl = tu = sl = su = scale
    a_l = a_u = b_l = b_u = scale // 2
    for k in range(1, DEGREE + 1):
        tl = tl * xl // (scale * k)
        tu = _ceil(tu * xu, scale * k)
        sl += tl
        su += tu
        a_l += tl // (k + 2)
        a_u += _ceil(tu, k + 2)
        b_l += tl // ((k + 1) * (k + 2))
        b_u += _ceil(tu, (k + 1) * (k + 2))
    tail = _tail(xu, scale)
    pair = lambda lo, hi: (Fraction(lo, scale), Fraction(hi, scale))
    return {"exp": pair(sl, su + tail), "A": pair(a_l, a_u + tail),
            "B": pair(b_l, b_u + tail), "tail": Fraction(tail, scale),
            "argument_interval": pair(xl, xu)}


def _exp_fraction(x):
    r = _positive_series(abs(x))
    if x >= 0:
        return r["exp"]
    lo, hi = r["exp"]
    return down(1 / hi), up(1 / lo)


def exp_interval(x):
    return _exp_fraction(Q(x))


def bernstein_weights(d, delta):
    """exp(d*delta), W0, W1, phi; all integral weights are nonnegative."""
    d, dt = Q(d), _positive(delta, "delta")
    x = d * dt
    r = _positive_series(abs(x))
    a, b = r["A"], r["B"]
    if x >= 0:
        e = r["exp"]
        w0 = (down(dt * a[0]), up(dt * a[1]))
        w1 = (down(dt * b[0]), up(dt * b[1]))
    else:
        e = (down(1 / r["exp"][1]), up(1 / r["exp"][0]))
        w0 = (down(dt * e[0] * b[0]), up(dt * e[1] * b[1]))
        w1 = (down(dt * e[0] * a[0]), up(dt * e[1] * a[1]))
    phi = (w0[0] + w1[0], w0[1] + w1[1])
    return {"exp": e, "W0": w0, "W1": w1, "phi": phi,
            "d_delta": x, "positive_series_tail": r["tail"],
            "method": "dyadic128 positive Taylor96 Bernstein moments"}


def _nominal(v, K, tau, rho, bind):
    if not isinstance(v, Mapping):
        raise DomainError("Explicit nominal K certificate is required")
    cert = deepcopy(dict(v))
    for name in ("certificate_id", "source_pointer", "source_sha256"):
        if not isinstance(cert.get(name), str) or not cert[name]:
            raise DomainError("Missing nominal certificate " + name)
    if not cert["source_pointer"].startswith("/") or not re.fullmatch(r"[0-9a-f]{64}", cert["source_sha256"]):
        raise DomainError("Malformed nominal source locator")
    if (cert.get("fixed_homogeneous_K") is not True or
            cert.get("uniform_all_starts") is not True or
            cert.get("scientific_status") != "CERTIFIED_K_BLOCK"):
        raise DomainError("Fixed homogeneous all-starts K certificate required")
    if cert.get("K_sha256") != matrix_identity(K):
        raise DomainError("Nominal K matrix identity mismatch")
    if Q(cert.get("tau")) != tau or Q(cert.get("rho_K")) != rho:
        raise DomainError("Nominal certificate tau/rho mismatch")
    if _binding(cert.get("binding"), len(K)) != bind:
        raise DomainError("Nominal certificate family/state/clock binding mismatch")
    return cert


def generator_certificate(K, pi, destruction, w_box, tau, rho_K, *, binding, nominal_certificate):
    p = _vec(pi, "pi", nonnegative=True)
    if not 1 <= len(p) <= 13 or sum(p) != 1:
        raise DomainError("pi must be an exact probability vector of dimension1..13")
    n = len(p)
    mat = _generator(K, n)
    ds = _vec(destruction, "destruction", n, True)
    box = _vec(w_box, "w_box", 2, True)
    if box[0] > box[1]:
        raise DomainError("Reversed w box")
    tau, rho = _positive(tau, "tau"), _nonneg(rho_K, "rho_K")
    if rho > 1:
        raise DomainError("rho_K must be in[0,1]")
    bind = _binding(binding, n)
    nominal = _nominal(nominal_certificate, mat, tau, rho, bind)
    H = tuple(tuple(p[i] * ds[j] - (ds[j] if i == j else 0)
                    for j in range(n)) for i in range(n))
    _generator(H, n)
    bH = max(ds[j] * (1 - p[j]) for j in range(n))
    normH = max(sum(abs(H[i][j]) for i in range(n)) for j in range(n))
    if normH != 2 * bH:
        raise DomainError("Exact generator-norm identity failed")
    eps = tau * box[1] * bH
    # eps is an exact derived product; the 8192-bit bound applies to inputs,
    # not to valid intermediate numerators or denominators.
    expm = _exp_fraction(-eps)
    additive = min(Fraction(1), rho + 2 * eps)
    minor = (max(Fraction(0), down(1 - expm[1] * (1 - rho))),
             min(Fraction(1), up(1 - expm[0] * (1 - rho))))
    q = min(Fraction(1), up(additive), minor[1])
    return {"schema": "WU_R11_UNIFORM_FULL_A_BLOCK_V1", "dimension": n,
            "H": H, "b_H": bH, "H_l1_norm": normH,
            "tau": tau, "rho_K": rho, "w_box": box, "epsilon": eps,
            "exp_minus_epsilon_interval": expm,
            "q_additive": additive, "q_minorization_interval": minor, "q": q,
            "strict_implemented_contraction": q < 1, "binding": bind,
            "nominal_certificate": nominal,
            "family": "fixed K,pi,destruction; every measurable w in certified whole w_box",
            "uniform_all_starts": True, "nominal_K_rho_directly_transferred": False,
            "n1_zero_residual_subspace": n == 1, "physical_consumer_admitted": False}


def _forcing(v, cells, name):
    if _seq(v):
        return _vec(v, name, cells, True)
    return (_nonneg(v, name),) * cells


def _cap(v, key, cells, delta, binding):
    if v is None:
        return None, None
    if not isinstance(v, Mapping):
        raise DomainError("Cap must be a source-backed mapping")
    suffix = "endpoints_upper" if key == "point" else "whole_cells_upper"
    if v.get("source_kind") != "saved_R10_" + suffix or v.get("source_sha256") != R10_SHA256:
        raise DomainError("Only pinned R10 cap source is accepted")
    pointer = v.get("source_pointer", "")
    if not isinstance(pointer, str) or not re.fullmatch(r"/hd_cases/[0-3]/capped/" + suffix, pointer):
        raise DomainError("Cap pointer must identify exact R10 case and bound kind")
    if _int(v.get("cells"), 1, 192, "cap cells") != cells or Q(v.get("delta")) != delta:
        raise DomainError("Cap exact cell/clock grid mismatch")
    if _binding(v.get("binding")) != binding:
        raise DomainError("Cap source/family/state/clock binding mismatch")
    count = cells + 1 if key == "point" else cells
    vals = v.get("upper")
    if not _seq(vals) or len(vals) != count:
        raise DomainError("Cap array length mismatch")
    rows = tuple(_vec(row, "cap row", 2, True) for row in vals)
    return rows, pointer.rsplit("/", 1)[0]


def convolution_sweep(q, c, d, g_r, g_e, delta, initial, cells, block_steps, *,
                      binding, whole_caps=None, point_caps=None, bits=BITS, degree=DEGREE):
    """Enclose a supplied all-starts q block kernel on an aligned exact grid.

This arithmetic API assumes q is a valid full-propagator block certificate.
Use sweep() to construct q from an explicit fixed K certificate.
"""
    _int(bits, BITS, BITS, "bits")
    _int(degree, DEGREE, DEGREE, "degree")
    cells = _int(cells, 1, 192, "cells")
    m = _int(block_steps, 1, 192, "block_steps")
    q = _nonneg(q, "q")
    if q > 1:
        raise DomainError("q must be in[0,1]")
    c, d, dt = _nonneg(c, "c"), Q(d), _positive(delta, "delta")
    init = _vec(initial, "initial", 2, True)
    bind = _binding(binding)
    if len(bind["state_ids"]) == 1 and (init[0] != 0 or any(_forcing(g_r, cells, "g_r"))):
        raise DomainError("Singleton zero-mass residual and forcing must vanish")
    gr, ge = _forcing(g_r, cells, "g_r"), _forcing(g_e, cells, "g_e")
    pc, pidx = _cap(point_caps, "point", cells, dt, bind)
    wc, widx = _cap(whole_caps, "whole", cells, dt, bind)
    if pc is not None and wc is not None and pidx != widx:
        raise DomainError("Point and whole caps identify different cases")
    if pc is not None and any(pc[0][k] < init[k] for k in (0, 1)):
        raise DomainError("Initial point cap is below the declared initial bound")
    w = bernstein_weights(d, dt)
    e, w0, w1, phi = (w[k] for k in ("exp", "W0", "W1", "phi"))
    hl = [Fraction(1)]
    hu = [Fraction(1)]
    for n in range(1, cells + 1):
        if n % m == 0:
            hl.append(down(hl[-1] * q))
            hu.append(up(hu[-1] * q))
        else:
            hl.append(hl[-1])
            hu.append(hu[-1])
    fl = [Fraction(0)]
    fu = [Fraction(0)]
    for n in range(1, cells + 1):
        fl.append(down(dt * sum((hl[n-1-j] * gr[j] for j in range(n)), Fraction(0))))
        fu.append(up(dt * sum((hu[n-1-j] * gr[j] for j in range(n)), Fraction(0))))
    rl = [down(hl[n] * init[0] + fl[n]) for n in range(cells + 1)]
    ru = [up(hu[n] * init[0] + fu[n]) for n in range(cells + 1)]
    rl[0] = ru[0] = init[0]
    el, eu = [init[1]], [init[1]]
    raw_whole, affine = [], []
    for n in range(cells):
        vl = down(hl[n] * init[0] + fl[n+1])
        vu = up(hu[n] * init[0] + fu[n+1])
        rs = max(ru[n], vu, ru[n+1])
        el.append(down(e[0]*el[-1] + c*(w0[0]*rl[n]+w1[0]*vl) + phi[0]*ge[n]))
        eu.append(up(e[1]*eu[-1] + c*(w0[1]*ru[n]+w1[1]*vu) + phi[1]*ge[n]))
        constant_end = up(e[1]*eu[n] + phi[1]*(c*rs+ge[n]))
        raw_whole.append((rs, max(eu[n], eu[n+1], constant_end)))
        affine.append({"left_interval": (rl[n],ru[n]), "right_left_limit_interval": (vl,vu)})
    raw_low = list(zip(rl,el))
    raw_high = list(zip(ru,eu))
    capped = pc is not None or wc is not None
    if capped:
        outp = [init]
        outw = []
        for n in range(cells):
            rs = min(raw_whole[n][0], wc[n][0]) if wc is not None else raw_whole[n][0]
            left_e = min(outp[n][1], eu[n], pc[n][1] if pc is not None else outp[n][1])
            if wc is not None:
                left_e = min(left_e, wc[n][1])
            scalar_end = up(e[1]*left_e + phi[1]*(c*rs+ge[n]))
            es = min(raw_whole[n][1], max(left_e,scalar_end))
            if wc is not None:
                es = min(es,wc[n][1])
            re = min(ru[n+1],rs,pc[n+1][0] if pc is not None else ru[n+1])
            ee = min(eu[n+1],scalar_end,es,pc[n+1][1] if pc is not None else eu[n+1])
            outw.append((rs,es))
            outp.append((re,ee))
        # Each endpoint lies in its adjacent closed cells. This output-only
        # intersection does not reset or alter the global R forcing memory.
        for n in range(cells+1):
            neighbors = outw[max(0,n-1):min(cells,n+1)]
            outp[n] = tuple(min([outp[n][k]]+[row[k] for row in neighbors]) for k in (0,1))
        output_low = None
    else:
        outp, outw, output_low = raw_high, raw_whole, raw_low
    return {"schema": "WU_R11_BLOCK_CONVOLUTION_SWEEP_V1", "mode": "capped" if capped else "raw",
            "q": q, "block_steps": m, "tau": m*dt, "delta": dt, "cells": cells,
            "initial": init, "binding": bind, "coefficients": {"c":c,"d":d,"g_r":gr,"g_e":ge},
            "kernel_lower": hl, "kernel_upper": hu, "forcing_lower": fl, "forcing_upper": fu,
            "R_affine_cells": affine, "Bernstein_weights": w,
            "endpoints_lower": output_low, "endpoints_upper": outp, "whole_cells_upper": outw,
            "lower_endpoint_meaning": "chosen rational-q ideal comparison only; never physical-error lower",
            "h0": 1, "whole_cell_definition": "closed [n*delta,(n+1)*delta], including right left-limit",
            "fresh_forcing": "current source cell enters with age coefficient h0=1",
            "R_memory_reset": False, "cap_source_sha256": R10_SHA256 if capped else None,
            "rounding": {"bits":bits,"degree":degree,"method":"outward exact-rational/dyadic"},
            "physical_consumer_admitted": False, "new_ODE_calls": 0}


def sweep(K, pi, destruction, w_box, tau, rho_K, c, d, g_r, g_e, delta, initial, cells, *,
          binding, nominal_certificate, whole_caps=None, point_caps=None, bits=BITS, degree=DEGREE):
    tau, dt = _positive(tau,"tau"), _positive(delta,"delta")
    ratio = tau / dt
    if ratio.denominator != 1 or not 1 <= ratio.numerator <= 192:
        raise DomainError("tau/delta must be an exact integer in[1,192]")
    cert = generator_certificate(K, pi, destruction, w_box, tau, rho_K,
                                 binding=binding, nominal_certificate=nominal_certificate)
    out = convolution_sweep(cert["q"], c, d, g_r, g_e, dt, initial, cells, ratio.numerator,
                             binding=binding, whole_caps=whole_caps, point_caps=point_caps,
                             bits=bits, degree=degree)
    out["generator"] = cert
    return out


def export(v):
    if isinstance(v, Fraction):
        return str(v)
    if isinstance(v, Mapping):
        return {str(k):export(x) for k,x in v.items()}
    if isinstance(v,(tuple,list)):
        return [export(x) for x in v]
    return v
