"""Finite R14 conditional quadratic-forcing comparison; no physical inference.

Original source, state, clock, full-A/all-starts, and whole-domain forcing
premises are explicitly bound. Exact quadratic positivity is checked before
vertex preprocessing. Positive Simpson/Bernstein overlap coefficients are
built once per rational base cell. Critical root boxes certify a supremum
gap but never become propagation clocks. History starts at the original t0.
No predecessor module, numerical ODE, generic cap adapter, or float is used.
"""
from bisect import bisect_right
from copy import deepcopy
from fractions import Fraction
from math import factorial
import hashlib
import json

BITS = 128
DEGREE = 96
ROOT_BISECTIONS = 96
MAX_INPUT_BITS = 256
MAX_DERIVED_BITS = 16384
MAX_SOURCE_CELLS = 16
MAX_OBSERVATION_CELLS = 32
MAX_EFFECTIVE_CELLS = 48
MAX_BASE_CELLS = 512
MAX_BLOCKS = 8
MAX_OVERLAP_TERMS = 250000
MAX_ROOT_BISECTIONS = 98304
FORCING_SCHEMA = "WU_R14_WHOLE_FORCING_V1"


class DomainError(ValueError):
    pass


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
        raise DomainError(name + ": input scalar exceeds256bits")
    return value


def derived(value):
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise DomainError("Derived scalar must be exact")
    value = Fraction(value)
    if _bits(value) > MAX_DERIVED_BITS:
        raise DomainError("Derived scalar exceeds16384bits")
    return value


def add(a, b):
    return derived(a + b)


def sub(a, b):
    return derived(a - b)


def mul(a, b):
    return derived(a * b)


def div(a, b):
    if not b:
        raise DomainError("Exact division by zero")
    return derived(Fraction(a) / b)


def _ceil(n, d):
    return -(-n // d)


def down(value):
    value = derived(value)
    return derived(Fraction(value.numerator * (1 << BITS) // value.denominator, 1 << BITS))


def up(value):
    value = derived(value)
    return derived(Fraction(_ceil(value.numerator * (1 << BITS), value.denominator), 1 << BITS))


def _nonnegative(value, name):
    value = exact(value, name)
    if value < 0:
        raise DomainError(name + ": nonnegative value required")
    return value


def _knots(values, name, maximum):
    if not isinstance(values, list) or not 2 <= len(values) <= maximum + 1:
        raise DomainError(name + ": cell count outside finite domain")
    result = [exact(x, name) for x in values]
    if any(a >= b for a, b in zip(result, result[1:])):
        raise DomainError(name + ": knots must be strictly increasing")
    return result


def _power2(b):
    return [b[0], mul(2, sub(b[1], b[0])), add(sub(b[0], mul(2, b[1])), b[2])]


def _horner(coefficients, x):
    value = Fraction(0)
    for coefficient in reversed(coefficients):
        value = add(mul(value, x), coefficient)
    return value


def _source_vertex(triplet):
    c, b, a = _power2(triplet)
    if a:
        vertex = div(-b, mul(2, a))
        if 0 < vertex < 1:
            return vertex
    return None


def _triplets(values, count, name):
    if not isinstance(values, list) or len(values) != count:
        raise DomainError(name + ": one Bernstein triplet per source cell required")
    result = []
    for row in values:
        if not isinstance(row, list) or len(row) != 3:
            raise DomainError(name + ": Bernstein triplet length must be three")
        triplet = [exact(x, name) for x in row]
        power = _power2(triplet)
        if triplet[0] < 0 or triplet[2] < 0:
            raise DomainError(name + ": quadratic source is negative at an endpoint")
        vertex = _source_vertex(triplet)
        if power[2] > 0 and vertex is not None and _horner(power, vertex) < 0:
            raise DomainError(name + ": quadratic source is negative at interior minimum")
        result.append(triplet)
    return result


def _text(value, name):
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise DomainError(name + ": nonempty finite identity text required")
    return value


def canonical_forcing_sha256(source, gr, ge, binding):
    payload = {"schema": FORCING_SCHEMA, "source_id": binding["source_id"],
               "clock_id": binding["clock_id"], "clock_unit": binding["clock_unit"],
               "state_order": binding["state_order"], "source_knots": [str(x) for x in source],
               "g_r": [[str(x) for x in row] for row in gr],
               "g_e": [[str(x) for x in row] for row in ge]}
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
    if binding.get("whole_forcing_hash_format") != FORCING_SCHEMA or cert.get("whole_forcing_hash_format") != FORCING_SCHEMA:
        raise DomainError("Canonical R14 whole forcing hash format required")
    if canonical_forcing_sha256(source, gr, ge, binding) != binding["whole_forcing_source_sha256"]:
        raise DomainError("Canonical whole forcing SHA-256 mismatch")
    if cert.get("generator") != "A=K+wH;H=pi*d^T-diag(d)":
        raise DomainError("Full-A generator declaration required")
    for flag in ("fixed_K_pi_d", "full_w_box", "all_start_times", "zero_mass_residual",
                 "short_remainder_nonexpansive", "forcing_whole_fine_coarse_domain"):
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
        raise DomainError("No generic cap adapter is in the R14 API")
    states = case.get("states")
    if isinstance(states, bool) or not isinstance(states, int) or not 1 <= states <= 13:
        raise DomainError("states must be an integer in [1,13]")
    q, tau = exact(case.get("q"), "q"), exact(case.get("tau"), "tau")
    c, d = _nonnegative(case.get("c"), "c"), exact(case.get("d"), "d")
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
    gr = _triplets(case.get("g_r"), len(source) - 1, "g_r")
    ge = _triplets(case.get("g_e"), len(source) - 1, "g_e")
    if states == 1 and (r0 or any(x for row in gr for x in row)):
        raise DomainError("Singleton zero-mass residual requires R0=0 and all g_r coefficients=0")
    binding, cert = _binding(case, q, tau, source[0], source[-1], states, source, gr, ge)
    return {"q": q, "tau": tau, "c": c, "d": d, "r0": r0, "e0": e0,
            "source": source, "obs": obs, "gr": gr, "ge": ge,
            "t0": source[0], "T": source[-1], "states": states,
            "blocks": blocks, "binding": binding, "certificate": cert}


def _split(coefficients, x):
    work = list(coefficients)
    left, right = [work[0]], [work[-1]]
    while len(work) > 1:
        work = [add(mul(sub(1, x), a), mul(x, b)) for a, b in zip(work, work[1:])]
        left.append(work[0])
        right.append(work[-1])
    return left, list(reversed(right))


def _restrict(coefficients, a, b):
    if not 0 <= a <= b <= 1:
        raise DomainError("Internal Bernstein restriction outside[0,1]")
    if a == 1:
        return [coefficients[-1]] * len(coefficients)
    right = list(coefficients) if not a else _split(coefficients, a)[1]
    return _split(right, div(sub(b, a), sub(1, a)))[0]


def _preprocess(p):
    knots = [p["t0"]]
    gr, ge, owners, vertices = [], [], [], []
    for j, (left, right) in enumerate(zip(p["source"], p["source"][1:])):
        cuts = {Fraction(0), Fraction(1)}
        for triplet in (p["gr"][j], p["ge"][j]):
            vertex = _source_vertex(triplet)
            if vertex is not None:
                cuts.add(vertex)
                vertices.append(add(left, mul(sub(right, left), vertex)))
        cuts = sorted(cuts)
        for a, b in zip(cuts, cuts[1:]):
            rr, ee = _restrict(p["gr"][j], a, b), _restrict(p["ge"][j], a, b)
            if any(x < 0 for x in rr + ee):
                raise DomainError("Internal source-vertex positivity invariant failed")
            gr.append(rr)
            ge.append(ee)
            owners.append(j)
            knots.append(add(left, mul(sub(right, left), b)))
    if len(gr) > MAX_EFFECTIVE_CELLS:
        raise DomainError("Effective source cell count exceeds48")
    return {"knots": knots, "g_r": gr, "g_e": ge, "original_cell_indices": owners,
            "source_vertex_times": sorted(set(vertices))}


def precharge_work(nbase, neffective, blocks):
    for value in (nbase, neffective, blocks):
        if isinstance(value, bool) or not isinstance(value, int):
            raise DomainError("Work counts must be exact integers")
    if not 1 <= nbase <= MAX_BASE_CELLS:
        raise DomainError("Base event grid exceeds512cells or is empty")
    if not 1 <= neffective <= MAX_EFFECTIVE_CELLS:
        raise DomainError("Effective source cell count exceeds48 or is empty")
    if not 0 <= blocks <= MAX_BLOCKS:
        raise DomainError("Work full-block count outside[0,8]")
    overlap = nbase * neffective * (blocks + 1)
    roots = 2 * ROOT_BISECTIONS * nbase
    if overlap > MAX_OVERLAP_TERMS:
        raise DomainError("Overlap work bound exceeds250000")
    if roots > MAX_ROOT_BISECTIONS:
        raise DomainError("Root bisection bound exceeds98304")
    return overlap, roots


def _power3(b):
    return [b[0], mul(3, sub(b[1], b[0])),
            mul(3, add(sub(b[0], mul(2, b[1])), b[2])),
            add(sub(add(-b[0], mul(3, b[1])), mul(3, b[2])), b[3])]


def _critical(power):
    c, b, a = power[1], mul(2, power[2]), mul(3, power[3])
    degree = 2 if a else 1 if b else 0 if c else -1
    exact_roots, boxes = {}, []
    steps = 0

    def record(x, multiplicity=1):
        if 0 <= x <= 1:
            exact_roots[x] = {"x": x, "multiplicity": multiplicity,
                              "location": "LEFT_ENDPOINT" if x == 0 else "RIGHT_ENDPOINT" if x == 1 else "INTERIOR"}

    if degree == 1:
        record(div(-c, b))
    elif degree == 2:
        vertex = div(-b, mul(2, a))
        cuts = [Fraction(0)] + ([vertex] if 0 < vertex < 1 else []) + [Fraction(1)]
        for x in cuts:
            if not _horner([c, b, a], x):
                record(x, 2 if add(mul(2, mul(a, x)), b) == 0 else 1)
        for left, right in zip(cuts, cuts[1:]):
            fl, fr = _horner([c, b, a], left), _horner([c, b, a], right)
            if not fl or not fr or (fl > 0) == (fr > 0):
                continue
            lo, hi, iterations = left, right, 0
            for _ in range(ROOT_BISECTIONS):
                mid = div(add(lo, hi), 2)
                fm = _horner([c, b, a], mid)
                steps += 1
                iterations += 1
                if not fm:
                    record(mid)
                    lo = hi = mid
                    break
                if (fl > 0) == (fm > 0):
                    lo, fl = mid, fm
                else:
                    hi, fr = mid, fm
            if lo != hi:
                boxes.append({"lo": lo, "hi": hi, "iterations": iterations,
                              "derivative_at_lo": fl, "derivative_at_hi": fr,
                              "branch": [left, right]})
    interior_count = sum(0 < x < 1 for x in exact_roots) + len(boxes)
    if interior_count > 2 or steps > 2 * ROOT_BISECTIONS:
        raise DomainError("Internal critical root accounting invariant failed")
    return {"derivative_power": [c, b, a], "degree": degree,
            "constant_polynomial": degree == -1,
            "exact_roots": [exact_roots[x] for x in sorted(exact_roots)],
            "root_boxes": boxes, "bisections_actual": steps}


def _supremum(bernstein, power, critical, actual_right):
    candidates = [{"x": Fraction(0), "value": bernstein[0], "kind": "ACTUAL_LEFT_ENDPOINT"},
                  {"x": Fraction(1), "value": bernstein[-1], "kind": "RIGHT_LEFT_LIMIT"},
                  {"x": Fraction(1), "value": actual_right, "kind": "ACTUAL_RIGHT_ENDPOINT"}]
    for root in critical["exact_roots"]:
        if root["location"] == "INTERIOR":
            candidates.append({"x": root["x"], "value": _horner(power, root["x"]), "kind": "EXACT_INTERIOR_CRITICAL"})
    lower = upper = max(row["value"] for row in candidates)
    boxes = []
    for box in critical["root_boxes"]:
        lo, hi = box["lo"], box["hi"]
        coeff = _restrict(bernstein, lo, hi)
        mid = div(add(lo, hi), 2)
        value, hull = _horner(power, mid), max(coeff)
        lower, upper = max(lower, value), max(upper, hull)
        boxes.append({"lo": lo, "hi": hi, "bernstein": coeff, "midpoint": mid,
                      "midpoint_value": value, "hull_upper": hull})
    mb = mul(3, max(abs(sub(b, a)) for a, b in zip(bernstein, bernstein[1:])))
    bound = div(mb, 1 << ROOT_BISECTIONS)
    gap = sub(upper, lower)
    if gap < 0 or gap > bound:
        raise DomainError("Internal root-box supremum gap invariant failed")
    return {"exact_lower": lower, "exact_upper": upper, "exact_gap": gap,
            "M_B": mb, "Cmax": max(bernstein), "proved_gap_bound": bound,
            "dyadic_lower": down(lower), "dyadic_upper": up(upper),
            "exact_candidates": candidates, "box_bounds": boxes}


def _tail(xu, scale):
    x = derived(Fraction(xu, scale))
    if not 0 <= x <= 16:
        raise DomainError("Positive-series rounded argument exceeds[0,16]")
    if not x:
        return 0
    power = Fraction(1)
    for _ in range(DEGREE + 1):
        power = mul(power, x)
    tail = div(div(power, factorial(DEGREE + 1)), sub(1, div(x, DEGREE + 2)))
    return _ceil(tail.numerator * scale, tail.denominator)


def bernstein3_weights(d, duration):
    """Positive dyadic128/Taylor96 cubic beta moments, signed d by reversal."""
    d, duration = derived(d), derived(duration)
    if duration <= 0:
        raise DomainError("Weight duration must be positive")
    z = mul(d, duration)
    if abs(z) > 16:
        raise DomainError("Weight argument exceeds16")
    scale, x = 1 << BITS, abs(z)
    xl = x.numerator * scale // x.denominator
    xu = _ceil(x.numerator * scale, x.denominator)
    tl = tu = sl = su = scale
    ml, mu = [scale // 4] * 4, [scale // 4] * 4
    for k in range(1, DEGREE + 1):
        tl = tl * xl // (scale * k)
        tu = _ceil(tu * xu, scale * k)
        sl, su = sl + tl, su + tu
        numerators = (1, 3, 6, 6)
        denominators = (k + 4, (k + 3) * (k + 4),
                        (k + 2) * (k + 3) * (k + 4),
                        (k + 1) * (k + 2) * (k + 3) * (k + 4))
        for i in range(4):
            ml[i] += tl * numerators[i] // denominators[i]
            mu[i] += _ceil(tu * numerators[i], denominators[i])
    tail = _tail(xu, scale)
    positive_exp = (derived(Fraction(sl, scale)), derived(Fraction(su + tail, scale)))
    moments = [(derived(Fraction(ml[i], scale)), derived(Fraction(mu[i] + tail, scale))) for i in range(4)]
    if z >= 0:
        exponent = positive_exp
        weights = [(down(mul(duration, lo)), up(mul(duration, hi))) for lo, hi in moments]
    else:
        exponent = (down(div(1, positive_exp[1])), up(div(1, positive_exp[0])))
        weights = [(down(mul(mul(duration, exponent[0]), lo)),
                    up(mul(mul(duration, exponent[1]), hi))) for lo, hi in reversed(moments)]
    phi = (Fraction(0), Fraction(0))
    for lo, hi in weights:
        phi = (add(phi[0], lo), add(phi[1], hi))
    return {"exp": exponent, "W0": weights[0], "W1": weights[1], "W2": weights[2], "W3": weights[3],
            "phi": phi, "d_delta": z, "positive_series_tail": derived(Fraction(tail, scale)),
            "argument_interval": (derived(Fraction(xl, scale)), derived(Fraction(xu, scale))),
            "method": "dyadic128 positive Taylor96 cubic Bernstein moments"}


def run_case(case):
    p = validate(case)
    q, tau, c, d = p["q"], p["tau"], p["c"], p["d"]
    effective = _preprocess(p)
    source, gr, ge = effective["knots"], effective["g_r"], effective["g_e"]
    obs, t0, end, blocks = p["obs"], p["t0"], p["T"], p["blocks"]
    events = set(obs)
    for knot in source:
        for k in range(blocks + 1):
            time = add(knot, mul(k, tau))
            if t0 <= time <= end:
                events.add(time)
    base = sorted(events)
    nbase = len(base) - 1
    overlap_bound, root_bound = precharge_work(nbase, len(gr), blocks)
    # No overlap coefficient or derivative root is evaluated before this charge.
    powers = [Fraction(1)]
    for _ in range(blocks):
        powers.append(mul(powers[-1], q))

    def kernel(time):
        return powers[int(div(sub(time, t0), tau) // 1)]

    cells, actual_terms, nonempty = [], 0, 0
    root_steps = 0
    for left, right in zip(base, base[1:]):
        duration = sub(right, left)
        mid = div(add(left, right), 2)
        fb = [Fraction(0)] * 4
        for j, (a, b) in enumerate(zip(source, source[1:])):
            for k in range(blocks + 1):
                actual_terms += 1
                shift_lo, shift_hi = mul(k + 1, tau), mul(k, tau)
                lm, um = max(a, sub(mid, shift_lo)), min(b, sub(mid, shift_hi))
                if um <= lm:
                    continue
                nonempty += 1
                if not powers[k]:
                    continue
                l0, l1 = (a, a) if a >= sub(mid, shift_lo) else (sub(left, shift_lo), sub(right, shift_lo))
                u0, u1 = (b, b) if b <= sub(mid, shift_hi) else (sub(left, shift_hi), sub(right, shift_hi))
                d0, d1 = sub(u0, l0), sub(u1, l1)
                if min(d0, d1) < 0:
                    raise DomainError("Internal overlap length endpoint is negative")
                m0, m1 = div(add(l0, u0), 2), div(add(l1, u1), 2)
                restrictions = []
                for v0, v1 in ((l0, l1), (m0, m1), (u0, u1)):
                    restrictions.append(_restrict(gr[j], div(sub(v0, a), sub(b, a)), div(sub(v1, a), sub(b, a))))
                s = [add(add(restrictions[0][i], mul(4, restrictions[1][i])), restrictions[2][i]) for i in range(3)]
                coeff = [div(mul(d0, s[0]), 6),
                         div(add(mul(mul(2, d0), s[1]), mul(d1, s[0])), 18),
                         div(add(mul(d0, s[2]), mul(mul(2, d1), s[1])), 18),
                         div(mul(d1, s[2]), 6)]
                if any(x < 0 for x in coeff):
                    raise DomainError("Internal Simpson positivity invariant failed")
                fb = [add(x, mul(powers[k], y)) for x, y in zip(fb, coeff)]
        initial_piece = mul(kernel(left), p["r0"])
        bernstein = [add(initial_piece, x) for x in fb]
        actual_right = add(mul(kernel(right), p["r0"]), fb[-1])
        power = _power3(bernstein)
        critical = _critical(power)
        root_steps += critical["bisections_actual"]
        supremum = _supremum(bernstein, power, critical, actual_right)
        source_index = bisect_right(source, left) - 1
        a, b = source[source_index:source_index + 2]
        ee = _restrict(ge[source_index], div(sub(left, a), sub(b, a)), div(sub(right, a), sub(b, a)))
        elevated = [ee[0], div(add(ee[0], mul(2, ee[1])), 3),
                    div(add(mul(2, ee[1]), ee[2]), 3), ee[2]]
        qi = [add(mul(c, x), y) for x, y in zip(bernstein, elevated)]
        cells.append({"left": left, "right": right, "bernstein": bernstein,
                      "coefficients_normalized": power, "initial_piece": initial_piece,
                      "F_bernstein": fb, "right_left_limit": bernstein[-1],
                      "actual_right_endpoint": actual_right, "ge_bernstein": ee,
                      "forcing_bernstein": qi, "critical": critical, "supremum": supremum})
    if actual_terms != overlap_bound or root_steps > root_bound:
        raise DomainError("Internal full-work accounting invariant failed")
    if any(a["F_bernstein"][-1] != b["F_bernstein"][0] for a, b in zip(cells, cells[1:])):
        raise DomainError("Internal global convolution continuity invariant failed")
    fvals = [cells[0]["F_bernstein"][0]] + [cell["F_bernstein"][-1] for cell in cells]
    kvals = [kernel(t) for t in base]
    rvals = [add(mul(k, p["r0"]), f) for k, f in zip(kvals, fvals)]
    endpoint_lo, endpoint_hi = [[rvals[0], down(p["e0"])]], [[rvals[0], up(p["e0"])]]
    whole_lo, whole_hi, weight_rows, cache = [], [], [], {}
    for i, cell in enumerate(cells):
        duration = sub(cell["right"], cell["left"])
        if duration not in cache:
            cache[duration] = bernstein3_weights(d, duration)
        weights = cache[duration]
        elo, ehi = weights["exp"]
        prev_lo, prev_hi = endpoint_lo[-1][1], endpoint_hi[-1][1]
        next_lo, next_hi = mul(elo, prev_lo), mul(ehi, prev_hi)
        for j in range(4):
            lo, hi = weights["W" + str(j)]
            next_lo = add(next_lo, mul(lo, cell["forcing_bernstein"][j]))
            next_hi = add(next_hi, mul(hi, cell["forcing_bernstein"][j]))
        next_lo, next_hi = down(next_lo), up(next_hi)
        qmax = add(mul(c, cell["supremum"]["exact_upper"]), max(cell["ge_bernstein"]))
        majorant_hi = up(add(mul(ehi, prev_hi), mul(weights["phi"][1], qmax)))
        whole_lo.append([cell["supremum"]["dyadic_lower"], max(prev_lo, next_lo)])
        whole_hi.append([cell["supremum"]["dyadic_upper"], max(prev_hi, next_hi, majorant_hi)])
        cell["whole_E_majorant"] = {"forcing_upper": qmax, "left_E_upper": prev_hi,
                                    "right_majorant_upper": majorant_hi,
                                    "supremum_upper": whole_hi[-1][1]}
        endpoint_lo.append([rvals[i + 1], next_lo])
        endpoint_hi.append([rvals[i + 1], next_hi])
        weight_rows.append({"left": cell["left"], "right": cell["right"], **weights})
    lookup = {t: i for i, t in enumerate(base)}
    observation_lo = [endpoint_lo[lookup[t]] for t in obs]
    observation_hi = [endpoint_hi[lookup[t]] for t in obs]
    observation_whole_lo, observation_whole_hi, observation_suprema = [], [], []
    for left, right in zip(obs, obs[1:]):
        start, stop = lookup[left], lookup[right]
        observation_whole_lo.append([max(row[j] for row in whole_lo[start:stop]) for j in range(2)])
        observation_whole_hi.append([max(row[j] for row in whole_hi[start:stop]) for j in range(2)])
        sl = max(cell["supremum"]["exact_lower"] for cell in cells[start:stop])
        su = max(cell["supremum"]["exact_upper"] for cell in cells[start:stop])
        bound = max(cell["supremum"]["proved_gap_bound"] for cell in cells[start:stop])
        if sub(su, sl) > bound:
            raise DomainError("Internal observation supremum gap invariant failed")
        observation_suprema.append({"left": left, "right": right, "exact_lower": sl,
                                    "exact_upper": su, "exact_gap": sub(su, sl), "proved_gap_bound": bound})
    return {"parameters": {"q": q, "tau": tau, "c": c, "d": d, "initial": [p["r0"], p["e0"]],
                           "t0": t0, "T": end, "states": p["states"], "full_blocks": blocks,
                           "binding": deepcopy(p["binding"]), "certificate": deepcopy(p["certificate"])},
            "source": {"knots": p["source"], "g_r": p["gr"], "g_e": p["ge"]},
            "effective_source": effective, "requested_times": obs, "base_times": base, "refined_times": base,
            "exact": {"F_at_refined": fvals, "R_at_refined": rvals, "kernel_at_refined": kvals,
                      "R_cubic_cells": cells, "observation_R_suprema": observation_suprema},
            "raw": {"endpoints_lower": observation_lo, "endpoints_upper": observation_hi,
                    "whole_cells_lower": observation_whole_lo, "whole_cells_upper": observation_whole_hi,
                    "refined_endpoints_lower": endpoint_lo, "refined_endpoints_upper": endpoint_hi,
                    "refined_whole_cells_lower": whole_lo, "refined_whole_cells_upper": whole_hi,
                    "lower_meaning": "chosen-rational-q ideal comparison lower; not physical error lower",
                    "whole_meaning": "closed-cell supremum enclosure, including right-endpoint left limits",
                    "coarse_l1_multiplier": 4},
            "weights": weight_rows,
            "work": {"original_source_cells": len(p["gr"]), "effective_source_cells": len(gr),
                     "base_cells": nbase, "refined_cells": nbase, "full_blocks": blocks,
                     "overlap_terms_upper": overlap_bound, "overlap_terms_actual": actual_terms,
                     "nonempty_overlap_terms": nonempty, "root_bisections_upper": root_bound,
                     "root_bisections_actual": root_steps, "coefficient_cell_builds": nbase,
                     "guard_applied_before_overlap": True, "guard_applied_before_root_isolation": True,
                     "overlap_limit": MAX_OVERLAP_TERMS, "root_limit": MAX_ROOT_BISECTIONS,
                     "formula": "base_cells*effective_source_cells*(full_blocks+1);2*96*base_cells"},
            "certificate_status": "DECLARED_PREMISES_BOUND_TO_EXACT_INPUT;PHYSICAL_VERIFICATION_NOT_INFERRED",
            "input_scientific_status": p["binding"]["scientific_status"],
            "source_provenance": {key: p["binding"][key] for key in
                                  ("source_locator", "source_sha256", "whole_forcing_source_sha256")},
            "R_history": "GLOBAL_FROM_ORIGINAL_T0", "cap_application": "NONE",
            "arithmetic": {"rational_bits": MAX_DERIVED_BITS, "dyadic_bits": BITS,
                           "Taylor_degree": DEGREE, "root_bisections": ROOT_BISECTIONS,
                           "root_boxes_are_propagation_clocks": False}}


def serializable(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {key: serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serializable(item) for item in value]
    return value
