"""Finite R13 raw comparison for exact piecewise-affine forcing.

This module accepts a declared full-A/all-starts certificate and declared
whole fine/coarse-domain forcing bounds. It validates their binding; it does
not infer a physical certificate from samples. All fixtures are conditional.
The residual convolution keeps its original t0 history. Endpoint lowers refer
to the chosen-rational-q ideal comparison. No predecessor runner or cap API
is imported. The scalar coupling c is not the speed of light.
"""
from bisect import bisect_right
from copy import deepcopy
from fractions import Fraction
import hashlib
import json

from positive_arithmetic import BITS, DEGREE, DomainError, _ceil, _tail, down, up

MAX_INPUT_BITS = 256
MAX_DERIVED_BITS = 16384
MAX_SOURCE_CELLS = 64
MAX_OBSERVATION_CELLS = 64
MAX_BASE_CELLS = 2048
MAX_REFINED_CELLS = 4096
MAX_BLOCKS = 8
MAX_OVERLAP_TERMS = 200000


def _bits(value):
    return max(abs(value.numerator).bit_length(), value.denominator.bit_length())


def exact(value, name="scalar"):
    if isinstance(value, bool) or not isinstance(value, (int, str, Fraction)):
        raise DomainError(name + ": exact int, Fraction or rational text required")
    if isinstance(value, str) and len(value) > 2048:
        raise DomainError(name + ": rational text too long")
    try:
        value = Fraction(value)
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise DomainError(name + ": invalid rational") from exc
    if _bits(value) > MAX_INPUT_BITS:
        raise DomainError(name + ": input scalar exceeds 256 bits")
    return value


def derived(value):
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise DomainError("Derived scalar must be exact")
    value = Fraction(value)
    if _bits(value) > MAX_DERIVED_BITS:
        raise DomainError("Derived scalar exceeds 16384 bits")
    return value


def add(a, b):
    return derived(a + b)


def sub(a, b):
    return derived(a - b)


def mul(a, b):
    return derived(a * b)


def div(a, b):
    if b == 0:
        raise DomainError("Exact division by zero")
    return derived(a / b)


def _nonnegative(value, name):
    x = exact(value, name)
    if x < 0:
        raise DomainError(name + ": nonnegative value required")
    return x


def _knots(values, name, maximum):
    if not isinstance(values, list) or not 2 <= len(values) <= maximum + 1:
        raise DomainError(name + ": cell count outside finite domain")
    out = [exact(x, name) for x in values]
    if any(a >= b for a, b in zip(out, out[1:])):
        raise DomainError(name + ": knots must be strictly increasing")
    return out


def _pairs(values, count, name):
    if not isinstance(values, list) or len(values) != count:
        raise DomainError(name + ": one endpoint pair per source cell required")
    result = []
    for row in values:
        if not isinstance(row, list) or len(row) != 2:
            raise DomainError(name + ": endpoint pair length must be two")
        result.append([_nonnegative(x, name) for x in row])
    return result


def _text(value, name):
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise DomainError(name + ": nonempty finite identity text required")
    return value


def canonical_forcing_sha256(source, gr, ge, binding):
    """Hash canonical exact forcing data plus its source/state/clock identity.

    This authenticates the declared bound function, not its physical validity.
    The separate source_sha256 names the supplied external source artifact.
    """
    payload = {"schema": "WU_R13_WHOLE_FORCING_V1",
               "source_id": binding["source_id"], "clock_id": binding["clock_id"],
               "clock_unit": binding["clock_unit"], "state_order": binding["state_order"],
               "source_knots": [str(x) for x in source],
               "g_r": [[str(x) for x in pair] for pair in gr],
               "g_e": [[str(x) for x in pair] for pair in ge]}
    data = (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _binding(case, q, tau, t0, end, states, source, gr, ge):
    binding, cert = case.get("binding"), case.get("certificate")
    if not isinstance(binding, dict) or not isinstance(cert, dict):
        raise DomainError("Explicit binding and full-A certificate required")
    for key in ("source_id", "clock_id", "clock_unit", "full_A_family_id", "source_locator"):
        value = _text(binding.get(key), "binding." + key)
        if cert.get(key) != value:
            raise DomainError("Certificate binding mismatch: " + key)
    for key in ("source_sha256", "whole_forcing_source_sha256"):
        value = binding.get(key)
        if (not isinstance(value, str) or len(value) != 64
                or any(ch not in "0123456789abcdef" for ch in value)):
            raise DomainError("Source SHA-256 identity required: " + key)
        if cert.get(key) != value:
            raise DomainError("Certificate source SHA-256 mismatch: " + key)
    status = binding.get("scientific_status")
    if status not in ("ARITHMETIC_CONTROL_PREMISE", "CERTIFIED_FULL_A_BLOCK") or cert.get("scientific_status") != status:
        raise DomainError("Explicit scientific_status binding required")
    order = binding.get("state_order")
    if (not isinstance(order, list) or len(order) != states
            or any(not isinstance(x, str) or not x or len(x) > 128 for x in order)
            or len(set(order)) != states or cert.get("state_order") != order):
        raise DomainError("Certificate state order mismatch")
    if (binding.get("whole_forcing_hash_format") != "WU_R13_WHOLE_FORCING_V1"
            or cert.get("whole_forcing_hash_format") != "WU_R13_WHOLE_FORCING_V1"):
        raise DomainError("Canonical whole forcing hash format required")
    if canonical_forcing_sha256(source, gr, ge, binding) != binding["whole_forcing_source_sha256"]:
        raise DomainError("Canonical whole forcing SHA-256 mismatch")
    if cert.get("generator") != "A=K+wH;H=pi*d^T-diag(d)":
        raise DomainError("Full-A generator declaration required")
    flags = ("fixed_K_pi_d", "full_w_box", "all_start_times", "zero_mass_residual",
             "short_remainder_nonexpansive", "forcing_whole_fine_coarse_domain")
    for flag in flags:
        if cert.get(flag) is not True:
            raise DomainError("Required certificate premise: " + flag)
    for key, target in (("q", q), ("tau", tau), ("t0", t0), ("T", end)):
        if exact(cert.get(key), "certificate." + key) != target:
            raise DomainError("Certificate scalar mismatch: " + key)
    wbox = cert.get("w_box")
    if not isinstance(wbox, list) or len(wbox) != 2:
        raise DomainError("Explicit whole w box required")
    wl, wh = [_nonnegative(x, "w_box") for x in wbox]
    if wl > wh:
        raise DomainError("Invalid whole w box")
    return binding, cert


def validate(case):
    if not isinstance(case, dict):
        raise DomainError("Input case must be a dictionary")
    if any(key in case for key in ("caps", "cap", "point_caps", "whole_caps")):
        raise DomainError("No generic cap adapter is in the R13 API")
    states = case.get("states")
    if isinstance(states, bool) or not isinstance(states, int) or not 1 <= states <= 13:
        raise DomainError("states must be an integer in [1,13]")
    q = exact(case.get("q"), "q")
    tau = exact(case.get("tau"), "tau")
    c = _nonnegative(case.get("c"), "c")
    d = exact(case.get("d"), "d")
    if not 0 <= q <= 1:
        raise DomainError("q must be in [0,1]")
    if tau <= 0:
        raise DomainError("tau must be positive")
    initial = case.get("initial")
    if not isinstance(initial, list) or len(initial) != 2:
        raise DomainError("initial must contain R0 and E0")
    r0, e0 = [_nonnegative(x, "initial") for x in initial]
    source = _knots(case.get("source_knots"), "source_knots", MAX_SOURCE_CELLS)
    obs = _knots(case.get("observation_knots"), "observation_knots", MAX_OBSERVATION_CELLS)
    if source[0] != obs[0] or source[-1] != obs[-1]:
        raise DomainError("Source and observation horizon mismatch")
    horizon = sub(source[-1], source[0])
    blocks = int(div(horizon, tau) // 1)
    if blocks > MAX_BLOCKS:
        raise DomainError("Horizon exceeds eight full kernel blocks")
    if abs(mul(d, horizon)) > 16:
        raise DomainError("abs(d)*horizon exceeds16")
    gr = _pairs(case.get("g_r"), len(source) - 1, "g_r")
    ge = _pairs(case.get("g_e"), len(source) - 1, "g_e")
    if states == 1 and (r0 != 0 or any(value != 0 for pair in gr for value in pair)):
        raise DomainError("Singleton zero-mass residual requires R0=0 and all g_r endpoints=0")
    binding, cert = _binding(case, q, tau, source[0], source[-1], states, source, gr, ge)
    return {"q": q, "tau": tau, "c": c, "d": d, "r0": r0, "e0": e0,
            "source": source, "obs": obs, "gr": gr, "ge": ge,
            "t0": source[0], "T": source[-1], "states": states,
            "blocks": blocks, "binding": binding, "certificate": cert}


def bernstein2_weights(d, duration):
    """Directed dyadic128 Taylor96 positive quadratic Bernstein moments.

    For x>=0, the k-th exp Taylor term is multiplied by respectively
    1/(k+3), 2/((k+2)(k+3)), 2/((k+1)(k+2)(k+3)). The copied exponential
    tail bounds each omitted moment tail because each multiplier is <=1.
    For z<0, W_i(z)=exp(z)*W_(2-i)(-z). No signed cancellation occurs.
    """
    d, duration = derived(d), derived(duration)
    if duration <= 0:
        raise DomainError("Weight duration must be positive")
    z = mul(d, duration)
    if abs(z) > 16:
        raise DomainError("Weight argument exceeds16")
    scale = 1 << BITS
    x = abs(z)
    xl = x.numerator * scale // x.denominator
    xu = _ceil(x.numerator * scale, x.denominator)
    tl = tu = sl = su = scale
    ml = [scale // 3] * 3
    mu = [_ceil(scale, 3)] * 3
    for k in range(1, DEGREE + 1):
        tl = tl * xl // (scale * k)
        tu = _ceil(tu * xu, scale * k)
        sl += tl
        su += tu
        numerators = (1, 2, 2)
        denominators = (k + 3, (k + 2) * (k + 3), (k + 1) * (k + 2) * (k + 3))
        for i in range(3):
            ml[i] += tl * numerators[i] // denominators[i]
            mu[i] += _ceil(tu * numerators[i], denominators[i])
    tail = _tail(xu, scale)
    positive_exp = (Fraction(sl, scale), Fraction(su + tail, scale))
    moments = [(Fraction(ml[i], scale), Fraction(mu[i] + tail, scale)) for i in range(3)]
    if z >= 0:
        exponent = positive_exp
        weights = [(down(mul(duration, lo)), up(mul(duration, hi))) for lo, hi in moments]
    else:
        exponent = (down(div(Fraction(1), positive_exp[1])), up(div(Fraction(1), positive_exp[0])))
        weights = [(down(mul(mul(duration, exponent[0]), lo)),
                    up(mul(mul(duration, exponent[1]), hi))) for lo, hi in reversed(moments)]
    phi = (add(add(weights[0][0], weights[1][0]), weights[2][0]),
           add(add(weights[0][1], weights[1][1]), weights[2][1]))
    return {"exp": exponent, "W0": weights[0], "W1": weights[1], "W2": weights[2],
            "phi": phi, "d_delta": z, "positive_series_tail": Fraction(tail, scale),
            "argument_interval": (Fraction(xl, scale), Fraction(xu, scale)),
            "method": "dyadic128 positive Taylor96 quadratic Bernstein moments"}


def _affine(pair, a, b, time):
    return add(pair[0], mul(sub(pair[1], pair[0]), div(sub(time, a), sub(b, a))))


def _poly(coefficients, u):
    return add(coefficients[0], mul(u, add(coefficients[1], mul(u, coefficients[2]))))


def run_case(case):
    p = validate(case)
    q, tau, c, d = p["q"], p["tau"], p["c"], p["d"]
    source, obs, t0, end = p["source"], p["obs"], p["t0"], p["T"]
    gr, ge, blocks = p["gr"], p["ge"], p["blocks"]
    powers = [Fraction(1)]
    for _ in range(blocks):
        powers.append(mul(powers[-1], q))

    def kernel(time):
        k = int(div(sub(time, t0), tau) // 1)
        return powers[k]

    events = set(source + obs)
    for knot in source:
        for k in range(blocks + 2):
            time = add(knot, mul(k, tau))
            if t0 <= time <= end:
                events.add(time)
    for k in range(blocks + 2):
        time = add(t0, mul(k, tau))
        if t0 <= time <= end:
            events.add(time)
    base = sorted(events)
    nbase = len(base) - 1
    if nbase > MAX_BASE_CELLS:
        raise DomainError("Base event grid exceeds2048cells")
    # Before any overlap evaluation: endpoints+midpoints <=2*N+1 and
    # at most N additional vertices. F cache is shared by all later reads.
    evaluation_bound = 3 * nbase + 1
    terms_per_evaluation = (len(source) - 1) * (blocks + 1)
    overlap_bound = evaluation_bound * terms_per_evaluation
    if overlap_bound > MAX_OVERLAP_TERMS:
        raise DomainError("Overlap work bound exceeds200000")
    fcache = {}
    actual_terms = 0

    def forcing(time):
        nonlocal actual_terms
        if time in fcache:
            return fcache[time]
        total = Fraction(0)
        for j, (a, b) in enumerate(zip(source, source[1:])):
            for k in range(blocks + 1):
                actual_terms += 1
                left = max(a, sub(time, mul(k + 1, tau)))
                right = min(b, sub(time, mul(k, tau)))
                if right > left and powers[k]:
                    area = div(mul(sub(right, left), add(_affine(gr[j], a, b, left),
                                                        _affine(gr[j], a, b, right))), 2)
                    total = add(total, mul(powers[k], area))
        if total < 0:
            raise DomainError("Internal positive overlap invariant failed")
        fcache[time] = total
        return total

    polynomials, vertices = [], []
    for left, right in zip(base, base[1:]):
        duration = sub(right, left)
        mid = add(left, div(duration, 2))
        initial_piece = mul(kernel(left), p["r0"])
        p0 = add(initial_piece, forcing(left))
        pm = add(initial_piece, forcing(mid))
        p1 = add(initial_piece, forcing(right))  # actual R right may jump down
        aa = mul(2, sub(add(p0, p1), mul(2, pm)))
        bb = sub(sub(mul(4, pm), mul(3, p0)), p1)
        coeff = [p0, div(bb, duration), div(aa, mul(duration, duration))]
        polynomials.append(coeff)
        if coeff[2]:
            vertex_offset = div(-coeff[1], mul(2, coeff[2]))
            if 0 < vertex_offset < duration:
                vertices.append(add(left, vertex_offset))
    refined = sorted(set(base + vertices))
    if len(refined) - 1 > MAX_REFINED_CELLS:
        raise DomainError("Vertex refined grid exceeds4096cells")
    fvals = [forcing(t) for t in refined]
    kvals = [kernel(t) for t in refined]
    rvals = [add(mul(h, p["r0"]), f) for h, f in zip(kvals, fvals)]
    if len(fcache) > evaluation_bound or actual_terms > overlap_bound:
        raise DomainError("Internal work-accounting invariant failed")

    cells, weight_rows, whole = [], [], []
    endpoints_lower = [[rvals[0], down(p["e0"])]]
    endpoints_upper = [[rvals[0], up(p["e0"])]]
    weight_cache = {}
    for i, (left, right) in enumerate(zip(refined, refined[1:])):
        duration = sub(right, left)
        base_index = bisect_right(base, left) - 1
        base_coeff = polynomials[base_index]
        offset = sub(left, base[base_index])
        local = [_poly(base_coeff, offset),
                 add(base_coeff[1], mul(mul(2, base_coeff[2]), offset)), base_coeff[2]]
        b0 = local[0]
        b1 = add(b0, div(mul(duration, local[1]), 2))
        b2 = _poly(local, duration)
        bernstein = [b0, b1, b2]
        if any(x < 0 for x in bernstein):
            raise DomainError("Vertex-split Bernstein positivity invariant failed")
        rmax = max(b0, b2, rvals[i + 1])
        source_index = bisect_right(source, left) - 1
        a, b = source[source_index:source_index + 2]
        e0 = _affine(ge[source_index], a, b, left)
        e1 = _affine(ge[source_index], a, b, right)
        elevated = [e0, div(add(e0, e1), 2), e1]
        qi = [add(mul(c, x), y) for x, y in zip(bernstein, elevated)]
        if duration not in weight_cache:
            weight_cache[duration] = bernstein2_weights(d, duration)
        weights = weight_cache[duration]
        exp_lo, exp_hi = weights["exp"]
        prev_lo, prev_hi = endpoints_lower[-1][1], endpoints_upper[-1][1]
        next_lo, next_hi = mul(exp_lo, prev_lo), mul(exp_hi, prev_hi)
        for j in range(3):
            lo, hi = weights["W" + str(j)]
            next_lo, next_hi = add(next_lo, mul(lo, qi[j])), add(next_hi, mul(hi, qi[j]))
        next_lo, next_hi = down(next_lo), up(next_hi)
        qmax = add(mul(c, rmax), max(e0, e1))
        majorant_hi = up(add(mul(exp_hi, prev_hi), mul(weights["phi"][1], qmax)))
        ewhole = max(prev_hi, next_hi, majorant_hi)
        cells.append({"left": left, "right": right, "coefficients_local": local,
                      "bernstein": bernstein, "whole_R": rmax,
                      "ge_endpoints": [e0, e1], "forcing_bernstein": qi})
        weight_rows.append({"left": left, "right": right, **weights})
        whole.append([rmax, ewhole])
        endpoints_lower.append([rvals[i + 1], next_lo])
        endpoints_upper.append([rvals[i + 1], next_hi])
    lookup = {t: i for i, t in enumerate(refined)}
    observation_lo = [endpoints_lower[lookup[t]] for t in obs]
    observation_hi = [endpoints_upper[lookup[t]] for t in obs]
    observation_whole = []
    for left, right in zip(obs, obs[1:]):
        subset = whole[lookup[left]:lookup[right]]
        observation_whole.append([max(x[0] for x in subset), max(x[1] for x in subset)])
    return {
        "parameters": {"q": q, "tau": tau, "c": c, "d": d, "initial": [p["r0"], p["e0"]],
                       "t0": t0, "T": end, "states": p["states"], "full_blocks": blocks,
                       "binding": deepcopy(p["binding"]), "certificate": deepcopy(p["certificate"])},
        "source": {"knots": source, "g_r": gr, "g_e": ge},
        "requested_times": obs, "base_times": base, "refined_times": refined,
        "vertex_times": sorted(set(vertices)),
        "exact": {"F_at_refined": fvals, "R_at_refined": rvals, "kernel_at_refined": kvals,
                  "R_quadratic_cells": cells},
        "raw": {"endpoints_lower": observation_lo, "endpoints_upper": observation_hi,
                "whole_cells_upper": observation_whole, "refined_endpoints_lower": endpoints_lower,
                "refined_endpoints_upper": endpoints_upper, "refined_whole_cells_upper": whole,
                "lower_meaning": "chosen-rational-q ideal comparison lower; not physical error lower",
                "whole_meaning": "closed-cell certificate, including right-endpoint left limits",
                "coarse_l1_multiplier": 4},
        "weights": weight_rows,
        "work": {"base_cells": nbase, "refined_cells": len(refined) - 1,
                 "F_evaluations_upper": evaluation_bound, "F_evaluations_actual": len(fcache),
                 "overlap_terms_upper": overlap_bound, "overlap_terms_actual": actual_terms,
                 "guard_applied_before_overlap": True, "limit": MAX_OVERLAP_TERMS,
                 "formula": "(3*base_cells+1)*source_cells*(full_blocks+1)"},
        "certificate_status": "DECLARED_PREMISES_BOUND_TO_EXACT_INPUT;PHYSICAL_VERIFICATION_NOT_INFERRED",
        "input_scientific_status": p["binding"]["scientific_status"],
        "source_provenance": {key: p["binding"][key] for key in
                              ("source_locator", "source_sha256", "whole_forcing_source_sha256")},
        "R_history": "GLOBAL_FROM_ORIGINAL_T0", "cap_application": "NONE",
        "arithmetic": {"rational_bits": MAX_DERIVED_BITS, "dyadic_bits": BITS, "Taylor_degree": DEGREE},
    }


def serializable(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {key: serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serializable(item) for item in value]
    return value
