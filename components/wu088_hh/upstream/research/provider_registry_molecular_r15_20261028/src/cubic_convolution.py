"""R15 exact supplied-B3 comparison, authored conditional arithmetic only.

Original-t0 full-A memory, source/state/clock premises and actual endpoints
remain explicit. Positive Simpson B4 overlaps and finite derivative-variation
subdivision never restart memory or invent physical source certification.
No predecessor/reference import and no import-time scientific calculation.
"""
from bisect import bisect_right
from copy import deepcopy
from fractions import Fraction
from math import comb
import hashlib
import json
import re
import sys

BITS = 128
DEGREE = 96
SUBDIVISION_DEPTH = 96
MAX_INPUT_BITS = 256
MAX_DERIVED_BITS = 16384
MAX_SOURCE_CELLS = 16
MAX_OBSERVATION_CELLS = 32
MAX_BASE_CELLS = 512
MAX_BLOCKS = 8
MAX_OVERLAP_TERMS = 100000
MAX_SPLITS = 147456
MAX_NODES = 295424
FORCING_SCHEMA = "WU_R15_WHOLE_FORCING_V1"
RUNTIME_INT_MAX_STR_DIGITS = 6000
MAX_OUTPUT_RATIONAL_TEXT = 10000
IDENTITY_KEYS = ("source_id", "clock_id", "clock_unit", "full_A_family_id",
                 "source_locator", "source_sha256", "whole_forcing_source_sha256",
                 "scientific_status", "state_order", "whole_forcing_hash_format")
PREMISE_FLAGS = ("fixed_K_pi_d", "full_w_box", "all_start_times", "zero_mass_residual",
                 "short_remainder_nonexpansive", "forcing_whole_fine_coarse_domain")
INPUT_KEYS = ("states", "q", "tau", "c", "d", "initial", "source_knots",
              "observation_knots", "g_r", "g_e", "binding", "certificate")


class DomainError(ValueError):
    pass


def configure_r15_runtime():
    """Use a finite digit limit, sufficient for bounded derived components."""
    setter = getattr(sys, "set_int_max_str_digits", None)
    getter = getattr(sys, "get_int_max_str_digits", None)
    if setter is None or getter is None:
        raise DomainError("R15 requires finite integer-string conversion policy")
    setter(RUNTIME_INT_MAX_STR_DIGITS)
    if getter() != RUNTIME_INT_MAX_STR_DIGITS:
        raise DomainError("R15 integer-string limit must equal6000")
    return RUNTIME_INT_MAX_STR_DIGITS


def _bits(value):
    return max(abs(value.numerator).bit_length(), value.denominator.bit_length())


def exact(value, name="scalar"):
    if isinstance(value, bool) or not isinstance(value, (int, str, Fraction)):
        raise DomainError(name + ": exact integer or ASCII rational required")
    if isinstance(value, str):
        if len(value) > 2048:
            raise DomainError(name + ": rational text exceeds2048characters")
        if re.fullmatch(r"[+-]?[0-9]+(?:/[+-]?[0-9]+)?", value) is None:
            raise DomainError(name + ": ASCII integer/p/q required; whitespace/decimal/exponent forbidden")
        try:
            pieces = value.split("/", 1)
            numerator = int(pieces[0])
            denominator = int(pieces[1]) if len(pieces) == 2 else 1
        except ValueError as exc:
            raise DomainError(name + ": invalid rational text") from exc
        if max(abs(numerator).bit_length(), abs(denominator).bit_length()) > MAX_INPUT_BITS:
            raise DomainError(name + ": input numerator/denominator exceeds256bits")
        if not denominator:
            raise DomainError(name + ": zero denominator")
        value = Fraction(numerator, denominator)
    else:
        value = Fraction(value)
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
    scale = 1 << BITS
    return derived(Fraction(value.numerator * scale // value.denominator, scale))


def up(value):
    value = derived(value)
    scale = 1 << BITS
    return derived(Fraction(_ceil(value.numerator * scale, value.denominator), scale))


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
        raise DomainError(name + ": knots must strictly increase")
    return result


def _quadruplets(values, count, name):
    if not isinstance(values, list) or len(values) != count:
        raise DomainError(name + ": one B3 row per original source cell required")
    result = []
    for row in values:
        if not isinstance(row, list) or len(row) != 4:
            raise DomainError(name + ": B3 row must contain four coefficients")
        result.append([_nonnegative(x, name) for x in row])
    return result


def _text(value, name):
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise DomainError(name + ": finite nonempty identity text required")
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
    if set(binding) != set(IDENTITY_KEYS):
        raise DomainError("Binding field set does not match R15 input schema")
    certificate_keys = set(IDENTITY_KEYS + PREMISE_FLAGS + ("generator", "q", "tau", "t0", "T", "w_box"))
    if set(cert) != certificate_keys:
        raise DomainError("Certificate field set does not match R15 input schema")
    for key in IDENTITY_KEYS[:5]:
        value = _text(binding.get(key), "binding." + key)
        if cert.get(key) != value:
            raise DomainError("Certificate binding mismatch: " + key)
    for key in ("source_sha256", "whole_forcing_source_sha256"):
        value = binding.get(key)
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
            raise DomainError("Source SHA256 identity required: " + key)
        if cert.get(key) != value:
            raise DomainError("Certificate source SHA256 mismatch: " + key)
    status = binding.get("scientific_status")
    if status not in ("ARITHMETIC_CONTROL_PREMISE", "CERTIFIED_FULL_A_BLOCK") or cert.get("scientific_status") != status:
        raise DomainError("Explicit scientific_status binding required")
    order = binding.get("state_order")
    if (not isinstance(order, list) or len(order) != states
            or any(not isinstance(x, str) or not x or len(x) > 128 for x in order)
            or len(set(order)) != states or cert.get("state_order") != order):
        raise DomainError("Certificate state order mismatch")
    if binding.get("whole_forcing_hash_format") != FORCING_SCHEMA or cert.get("whole_forcing_hash_format") != FORCING_SCHEMA:
        raise DomainError("Canonical R15 forcing hash format required")
    if canonical_forcing_sha256(source, gr, ge, binding) != binding["whole_forcing_source_sha256"]:
        raise DomainError("Canonical whole forcing SHA256 mismatch")
    if cert.get("generator") != "A=K+wH;H=pi*d^T-diag(d)":
        raise DomainError("Full-A generator declaration required")
    for flag in PREMISE_FLAGS:
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
        raise DomainError("Whole w box must be ordered")
    return binding, cert


def validate(case):
    if not isinstance(case, dict):
        raise DomainError("Input case must be an object")
    if any(key in case for key in ("caps", "cap", "point_caps", "whole_caps")):
        raise DomainError("No generic cap adapter in R15")
    if set(case) != set(INPUT_KEYS):
        raise DomainError("Input field set does not match R15 schema")
    states = case.get("states")
    if isinstance(states, bool) or not isinstance(states, int) or not 1 <= states <= 13:
        raise DomainError("states must be an integer in[1,13]")
    q, tau = exact(case.get("q"), "q"), exact(case.get("tau"), "tau")
    c, d = _nonnegative(case.get("c"), "c"), exact(case.get("d"), "d")
    if not 0 <= q <= 1:
        raise DomainError("q must lie in[0,1]")
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
    gr = _quadruplets(case.get("g_r"), len(source) - 1, "g_r")
    ge = _quadruplets(case.get("g_e"), len(source) - 1, "g_e")
    if states == 1 and (r0 or any(x for row in gr for x in row)):
        raise DomainError("Singleton zero-mass residual requires R0=0 and all g_r=0")
    binding, cert = _binding(case, q, tau, source[0], source[-1], states, source, gr, ge)
    return {"q": q, "tau": tau, "c": c, "d": d, "r0": r0, "e0": e0,
            "source": source, "obs": obs, "gr": gr, "ge": ge, "t0": source[0],
            "T": source[-1], "states": states, "blocks": blocks,
            "binding": binding, "certificate": cert}


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
        raise DomainError("Bernstein restriction outside[0,1]")
    if a == 1:
        return [coefficients[-1]] * len(coefficients)
    right = list(coefficients) if not a else _split(coefficients, a)[1]
    return _split(right, div(sub(b, a), sub(1, a)))[0]


def _evaluate(coefficients, x):
    work = list(coefficients)
    while len(work) > 1:
        work = [add(mul(sub(1, x), a), mul(x, b)) for a, b in zip(work, work[1:])]
    return work[0]


def _power4(bernstein):
    coefficients = []
    for k in range(5):
        value = Fraction(0)
        for j in range(k + 1):
            value = add(value, mul((-1) ** (k - j) * comb(k, j), bernstein[j]))
        coefficients.append(mul(comb(4, k), value))
    return coefficients


def precharge_work(nbase, nsource, blocks):
    if any(isinstance(v, bool) or not isinstance(v, int) for v in (nbase, nsource, blocks)):
        raise DomainError("Work counts must be exact integers")
    if not 1 <= nbase <= MAX_BASE_CELLS:
        raise DomainError("Base grid count outside[1,512]")
    if not 1 <= nsource <= MAX_SOURCE_CELLS:
        raise DomainError("Original source count outside[1,16]")
    if not 0 <= blocks <= MAX_BLOCKS:
        raise DomainError("Work full-block count outside[0,8]")
    overlap = nbase * nsource * (blocks + 1)
    splits, nodes = 3 * SUBDIVISION_DEPTH * nbase, (6 * SUBDIVISION_DEPTH + 1) * nbase
    if overlap > MAX_OVERLAP_TERMS or overlap > 73728 or splits > MAX_SPLITS or nodes > MAX_NODES:
        raise DomainError("Precharged finite work exceeds the R15 contract")
    return overlap, splits, nodes


def _variation(coefficients):
    signs = [1 if x > 0 else -1 for x in coefficients if x]
    return sum(a != b for a, b in zip(signs, signs[1:]))


def _quartic_supremum(bernstein, actual_right=None, depth_limit=SUBDIVISION_DEPTH):
    """Positive B4 complete partition; optional finite D is diagnostics only."""
    if not isinstance(bernstein, (list, tuple)) or len(bernstein) != 5:
        raise DomainError("Quartic supremum needs five exact B4 coefficients")
    bernstein = [derived(x) for x in bernstein]
    if min(bernstein) < 0:
        raise DomainError("R15 extrema component requires nonnegative B4 coefficients")
    if isinstance(depth_limit, bool) or not isinstance(depth_limit, int) or not 0 <= depth_limit <= SUBDIVISION_DEPTH:
        raise DomainError("Diagnostic depth must lie in[0,96]")
    actual_right = bernstein[-1] if actual_right is None else derived(actual_right)
    if actual_right < 0:
        raise DomainError("Actual right endpoint must be nonnegative")
    split_cap, node_cap = 3 * depth_limit, 6 * depth_limit + 1
    derivative = [mul(4, sub(b, a)) for a, b in zip(bernstein, bernstein[1:])]
    mb = max(abs(x) for x in derivative)
    stack = [(bernstein, Fraction(0), Fraction(1), 0)]
    leaves, splits, visits, max_depth = [], 0, 0, 0
    while stack:
        coeff, left, right, depth = stack.pop()
        visits += 1
        if visits > node_cap:
            raise DomainError("Derivative-variation visit cap exceeded")
        max_depth = max(max_depth, depth)
        diff = [mul(4, sub(b, a)) for a, b in zip(coeff, coeff[1:])]
        variation = _variation(diff)
        leaf = {"left": left, "right": right, "depth": depth, "variation": variation,
                "endpoint_values": [coeff[0], coeff[-1]]}
        if not any(diff):
            leaf.update(kind="CONSTANT", lower=coeff[0], upper=coeff[0])
        elif not variation:
            kind = "NONDECREASING" if all(x >= 0 for x in diff) else "NONINCREASING"
            value = max(coeff[0], coeff[-1])
            leaf.update(kind=kind, lower=value, upper=value)
        elif depth == depth_limit:
            midpoint = div(add(left, right), 2)
            value = _evaluate(coeff, Fraction(1, 2))
            leaf.update(kind="DEPTH_LIMIT", midpoint=midpoint, midpoint_value=value,
                        bernstein=coeff, lower=max(coeff[0], coeff[-1], value), upper=max(coeff))
        else:
            splits += 1
            if splits > split_cap:
                raise DomainError("Derivative-variation split cap exceeded")
            middle = div(add(left, right), 2)
            lc, rc = _split(coeff, Fraction(1, 2))
            stack.append((rc, middle, right, depth + 1))
            stack.append((lc, left, middle, depth + 1))
            continue
        leaves.append(leaf)
    unresolved = [leaf for leaf in leaves if leaf["kind"] == "DEPTH_LIMIT"]
    if visits != 2 * splits + 1 or len(leaves) != splits + 1 or len(unresolved) > 3:
        raise DomainError("Complete subdivision accounting invariant failed")
    if leaves[0]["left"] != 0 or leaves[-1]["right"] != 1 or any(a["right"] != b["left"] for a, b in zip(leaves, leaves[1:])):
        raise DomainError("Subdivision does not partition the complete normalized cell")
    lower = max([actual_right] + [leaf["lower"] for leaf in leaves])
    upper = max([actual_right] + [leaf["upper"] for leaf in leaves])
    gap, bound, cmax = sub(upper, lower), div(mb, 1 << depth_limit), max(bernstein)
    if gap < 0 or gap > bound or mb > mul(4, cmax):
        raise DomainError("Quartic supremum gap invariant failed")
    supremum = {"exact_lower": lower, "exact_upper": upper, "exact_gap": gap,
                "M_B": mb, "Cmax": cmax, "proved_gap_bound": bound,
                "dyadic_lower": down(lower), "dyadic_upper": up(upper)}
    subdivision = {"method": "BERNSTEIN_DERIVATIVE_VARIATION_V1", "depth_limit": depth_limit,
                   "derivative_bernstein": derivative, "splits_actual": splits,
                   "nodes_visited": visits, "max_depth": max_depth, "terminal_leaves": len(leaves),
                   "depth_limit_leaves": len(unresolved),
                   "max_unresolved_width": max([sub(leaf["right"], leaf["left"]) for leaf in unresolved] or [Fraction(0)]),
                   "leaves": leaves}
    return {"supremum": supremum, "subdivision": subdivision}


def _overlap_bernstein4(original, a, b, l0, l1, u0, u1):
    d0, d1 = sub(u0, l0), sub(u1, l1)
    if min(d0, d1) < 0:
        raise DomainError("Negative overlap length at a base-cell endpoint")
    m0, m1 = div(add(l0, u0), 2), div(add(l1, u1), 2)
    restrictions = [_restrict(original, div(sub(v0, a), sub(b, a)), div(sub(v1, a), sub(b, a)))
                    for v0, v1 in ((l0, l1), (m0, m1), (u0, u1))]
    ss = [add(add(restrictions[0][i], mul(4, restrictions[1][i])), restrictions[2][i]) for i in range(4)]
    result = []
    for k in range(5):
        value = Fraction(0)
        if k < 4:
            value = add(value, mul(mul(4 - k, d0), ss[k]))
        if k:
            value = add(value, mul(mul(k, d1), ss[k - 1]))
        result.append(div(value, 24))
    if min(result) < 0:
        raise DomainError("Positive Simpson B4 overlap invariant failed")
    return result


def _beta(n):
    return [Fraction(1, n + 5), Fraction(4, (n + 4) * (n + 5)),
            Fraction(12, (n + 3) * (n + 4) * (n + 5)),
            Fraction(24, (n + 2) * (n + 3) * (n + 4) * (n + 5)),
            Fraction(24, (n + 1) * (n + 2) * (n + 3) * (n + 4) * (n + 5))]


def _tail(x, last_term):
    """Exponential tail after n=96, dominated by ratio x/98."""
    if not 0 <= x <= 16:
        raise DomainError("Positive Taylor argument outside[0,16]")
    first_omitted = mul(last_term, div(x, DEGREE + 1))
    return div(first_omitted, sub(1, div(x, DEGREE + 2)))


def bernstein4_weights(d, duration):
    d, duration = derived(d), derived(duration)
    if duration <= 0:
        raise DomainError("Moment duration must be positive")
    z = mul(d, duration)
    if abs(z) > 16:
        raise DomainError("Moment argument exceeds16")
    if not z:
        exponent = (Fraction(1), Fraction(1))
        weights = [(div(duration, 5), div(duration, 5)) for _ in range(5)]
        phi = (duration, duration)
    else:
        x, term, exponential = abs(z), Fraction(1), Fraction(1)
        moments = [Fraction(1, 5)] * 5
        for n in range(1, DEGREE + 1):
            term = mul(term, div(x, n))
            exponential = add(exponential, term)
            moments = [add(value, mul(term, beta)) for value, beta in zip(moments, _beta(n))]
        tail = _tail(x, term)
        positive_exp = (down(exponential), up(add(exponential, tail)))
        positive_moments = [(value, add(value, mul(tail, beta))) for value, beta in zip(moments, _beta(DEGREE + 1))]
        if z > 0:
            exponent = positive_exp
            weights = [(down(mul(duration, lo)), up(mul(duration, hi))) for lo, hi in positive_moments]
        else:
            exponent = (down(div(1, positive_exp[1])), up(div(1, positive_exp[0])))
            weights = [(down(mul(mul(duration, exponent[0]), lo)),
                        up(mul(mul(duration, exponent[1]), hi))) for lo, hi in reversed(positive_moments)]
        phi = (Fraction(0), Fraction(0))
        for lo, hi in weights:
            phi = (add(phi[0], lo), add(phi[1], hi))
    return {"z": z, "exp": exponent, "phi": phi, **{"W" + str(i): pair for i, pair in enumerate(weights)}}


def run_case(case):
    configure_r15_runtime()
    p = validate(case)
    q, tau, c, d = p["q"], p["tau"], p["c"], p["d"]
    source, gr, ge = p["source"], p["gr"], p["ge"]
    obs, t0, end, blocks = p["obs"], p["t0"], p["T"], p["blocks"]
    events = set(obs)
    for knot in source:
        for k in range(blocks + 1):
            time = add(knot, mul(k, tau))
            if t0 <= time <= end:
                events.add(time)
    base = sorted(events)
    overlap_bound, split_bound, node_bound = precharge_work(len(base) - 1, len(gr), blocks)
    # All finite work is charged before the first overlap or subdivision.
    powers = [Fraction(1)]
    for _ in range(blocks):
        powers.append(mul(powers[-1], q))

    def kernel(time):
        return powers[int(div(sub(time, t0), tau) // 1)]

    cells, actual_terms, nonempty, total_splits, total_nodes = [], 0, 0, 0, 0
    for left, right in zip(base, base[1:]):
        mid = div(add(left, right), 2)
        fb = [Fraction(0)] * 5
        for j, (a, b) in enumerate(zip(source, source[1:])):
            for k in range(blocks + 1):
                actual_terms += 1
                if actual_terms > overlap_bound:
                    raise DomainError("Actual overlap count exceeds precharge")
                shift_lo, shift_hi = mul(k + 1, tau), mul(k, tau)
                lm, um = max(a, sub(mid, shift_lo)), min(b, sub(mid, shift_hi))
                if um <= lm:
                    continue
                nonempty += 1
                if not powers[k]:
                    continue
                l0, l1 = (a, a) if a >= sub(mid, shift_lo) else (sub(left, shift_lo), sub(right, shift_lo))
                u0, u1 = (b, b) if b <= sub(mid, shift_hi) else (sub(left, shift_hi), sub(right, shift_hi))
                coeff = _overlap_bernstein4(gr[j], a, b, l0, l1, u0, u1)
                fb = [add(x, mul(powers[k], y)) for x, y in zip(fb, coeff)]
        initial_piece = mul(kernel(left), p["r0"])
        bernstein = [add(initial_piece, x) for x in fb]
        actual_right = add(mul(kernel(right), p["r0"]), fb[-1])
        extrema = _quartic_supremum(bernstein, actual_right)
        total_splits += extrema["subdivision"]["splits_actual"]
        total_nodes += extrema["subdivision"]["nodes_visited"]
        if total_splits > split_bound or total_nodes > node_bound:
            raise DomainError("Actual subdivision work exceeds global precharge")
        source_index = bisect_right(source, left) - 1
        a, b = source[source_index:source_index + 2]
        ee = _restrict(ge[source_index], div(sub(left, a), sub(b, a)), div(sub(right, a), sub(b, a)))
        elevated = [ee[0], div(add(ee[0], mul(3, ee[1])), 4),
                    div(add(ee[1], ee[2]), 2), div(add(mul(3, ee[2]), ee[3]), 4), ee[3]]
        forcing = [add(mul(c, value), direct) for value, direct in zip(bernstein, elevated)]
        cells.append({"left": left, "right": right, "bernstein": bernstein,
                      "coefficients_normalized": _power4(bernstein), "initial_piece": initial_piece,
                      "F_bernstein": fb, "right_left_limit": bernstein[-1],
                      "actual_right_endpoint": actual_right, "ge_bernstein": ee,
                      "forcing_bernstein": forcing, **extrema})
    if actual_terms != overlap_bound:
        raise DomainError("Overlap accounting invariant failed")
    if any(a["F_bernstein"][-1] != b["F_bernstein"][0] for a, b in zip(cells, cells[1:])):
        raise DomainError("Original global convolution is not continuous")
    fvals = [cells[0]["F_bernstein"][0]] + [cell["F_bernstein"][-1] for cell in cells]
    kvals = [kernel(time) for time in base]
    rvals = [add(mul(k, p["r0"]), f) for k, f in zip(kvals, fvals)]
    endpoint_lo = [[rvals[0], down(p["e0"])]]
    endpoint_hi = [[rvals[0], up(p["e0"])]]
    whole_lo, whole_hi, weight_rows, cache = [], [], [], {}
    for index, cell in enumerate(cells):
        duration = sub(cell["right"], cell["left"])
        if duration not in cache:
            cache[duration] = bernstein4_weights(d, duration)
        weights = cache[duration]
        elo, ehi = weights["exp"]
        prev_lo, prev_hi = endpoint_lo[-1][1], endpoint_hi[-1][1]
        next_lo, next_hi = mul(elo, prev_lo), mul(ehi, prev_hi)
        for j in range(5):
            lo, hi = weights["W" + str(j)]
            next_lo = add(next_lo, mul(lo, cell["forcing_bernstein"][j]))
            next_hi = add(next_hi, mul(hi, cell["forcing_bernstein"][j]))
        next_lo, next_hi = down(next_lo), up(next_hi)
        qmax = add(mul(c, cell["supremum"]["exact_upper"]), max(cell["ge_bernstein"]))
        majorant_hi = up(add(mul(ehi, prev_hi), mul(weights["phi"][1], qmax)))
        whole_lo.append([cell["supremum"]["dyadic_lower"], max(prev_lo, next_lo)])
        whole_hi.append([cell["supremum"]["dyadic_upper"], max(prev_hi, next_hi, majorant_hi)])
        cell["whole_E_majorant"] = {"Qmax": qmax, "left_E_upper": prev_hi,
                                    "right_majorant_upper": majorant_hi,
                                    "supremum_upper": whole_hi[-1][1]}
        endpoint_lo.append([rvals[index + 1], next_lo])
        endpoint_hi.append([rvals[index + 1], next_hi])
        weight_rows.append({"left": cell["left"], "right": cell["right"], **weights})
    lookup = {time: index for index, time in enumerate(base)}
    observation_lo = [endpoint_lo[lookup[time]] for time in obs]
    observation_hi = [endpoint_hi[lookup[time]] for time in obs]
    observation_whole_lo, observation_whole_hi, observation_suprema = [], [], []
    for left, right in zip(obs, obs[1:]):
        start, stop = lookup[left], lookup[right]
        observation_whole_lo.append([max(row[j] for row in whole_lo[start:stop]) for j in range(2)])
        observation_whole_hi.append([max(row[j] for row in whole_hi[start:stop]) for j in range(2)])
        selected = [cell["supremum"] for cell in cells[start:stop]]
        aggregate = {key: max(row[key] for row in selected) for key in
                     ("exact_lower", "exact_upper", "M_B", "Cmax", "proved_gap_bound")}
        aggregate["exact_gap"] = sub(aggregate["exact_upper"], aggregate["exact_lower"])
        aggregate["dyadic_lower"] = down(aggregate["exact_lower"])
        aggregate["dyadic_upper"] = up(aggregate["exact_upper"])
        if aggregate["exact_gap"] > aggregate["proved_gap_bound"]:
            raise DomainError("Observation supremum gap invariant failed")
        observation_suprema.append(aggregate)
    return {"parameters": {"q": q, "tau": tau, "c": c, "d": d, "initial": [p["r0"], p["e0"]],
                           "t0": t0, "T": end, "states": p["states"], "full_blocks": blocks,
                           "binding": deepcopy(p["binding"]), "certificate": deepcopy(p["certificate"])},
            "source": {"knots": source, "g_r": gr, "g_e": ge},
            "requested_times": obs, "base_times": base, "refined_times": base,
            "exact": {"F_at_refined": fvals, "R_at_refined": rvals, "kernel_at_refined": kvals,
                      "R_quartic_cells": cells, "observation_R_suprema": observation_suprema},
            "raw": {"endpoints_lower": observation_lo, "endpoints_upper": observation_hi,
                    "whole_cells_lower": observation_whole_lo, "whole_cells_upper": observation_whole_hi,
                    "refined_endpoints_lower": endpoint_lo, "refined_endpoints_upper": endpoint_hi,
                    "refined_whole_cells_lower": whole_lo, "refined_whole_cells_upper": whole_hi},
            "weights": weight_rows,
            "work": {"original_source_cells": len(gr), "base_cells": len(cells), "refined_cells": len(cells),
                     "full_blocks": blocks, "overlap_terms_upper": overlap_bound,
                     "overlap_terms_actual": actual_terms, "nonempty_overlap_terms": nonempty,
                     "subdivision_splits_upper": split_bound, "subdivision_splits_actual": total_splits,
                     "subdivision_nodes_upper": node_bound, "subdivision_nodes_actual": total_nodes,
                     "coefficient_cell_builds": len(cells), "guard_applied_before_overlap": True,
                     "guard_applied_before_subdivision": True, "overlap_limit": MAX_OVERLAP_TERMS,
                     "split_limit": MAX_SPLITS, "node_limit": MAX_NODES,
                     "formula": "Nbase*Nsource*(B+1);3*96*Nbase;(6*96+1)*Nbase"},
            "certificate_status": "DECLARED_PREMISES_BOUND_TO_EXACT_INPUT;PHYSICAL_VERIFICATION_NOT_INFERRED",
            "input_scientific_status": p["binding"]["scientific_status"],
            "source_provenance": {"source_locator": p["binding"]["source_locator"],
                                  "source_sha256": p["binding"]["source_sha256"],
                                  "whole_forcing_source_sha256": p["binding"]["whole_forcing_source_sha256"],
                                  "source_classification": p["binding"]["scientific_status"]},
            "R_history": "GLOBAL_FROM_ORIGINAL_T0", "cap_application": "NONE",
            "arithmetic": {"rational_bits": MAX_DERIVED_BITS, "dyadic_bits": BITS,
                           "Taylor_degree": DEGREE, "subdivision_depth": SUBDIVISION_DEPTH,
                           "derivative_degree_max": 3, "runtime_int_max_str_digits": RUNTIME_INT_MAX_STR_DIGITS,
                           "output_rational_text_max_characters": MAX_OUTPUT_RATIONAL_TEXT,
                           "subdivision_points_are_propagation_clocks": False,
                           "lower_meaning": "ideal supplied-forcing comparison lower; not physical error lower",
                           "whole_meaning": "closed-cell supremum enclosure, including left limits and actual endpoints",
                           "coarse_l1_multiplier": 4}}


def _serializable(value):
    if isinstance(value, Fraction):
        text = str(derived(value))
        if len(text) > MAX_OUTPUT_RATIONAL_TEXT:
            raise DomainError("Serialized rational exceeds10000characters")
        return text
    if isinstance(value, dict):
        return {key: _serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serializable(item) for item in value]
    return value


def serializable(value):
    configure_r15_runtime()
    return _serializable(value)
