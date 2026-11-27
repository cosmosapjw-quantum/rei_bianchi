"""Small exact theorem-check helpers, not a new scientific execution route.

No arrays, norms, historical values, or native code are loaded.  The frozen
scalar arithmetic implementation is immutable and only supplies a test oracle.
"""
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import importlib.util
import sys

OLD = Path(__file__).resolve().parents[2] / 'gap_closure_20261001_g0_g6_v1'
ENGINE = OLD / 'exact_gram/engine.py'
ENGINE_SHA256 = 'e10f206d63be1a99a441780108619574605014a9b01b3b327e21fecb18c5b9cc'
if hashlib.sha256(ENGINE.read_bytes()).hexdigest() != ENGINE_SHA256:
    raise RuntimeError('immutable scalar oracle identity mismatch')
spec = importlib.util.spec_from_file_location('_t3_frozen_scalar_oracle', ENGINE)
oracle = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = oracle
spec.loader.exec_module(oracle)

SIGN = 1 << 63
MAX_BITS = 0x7fefffffffffffff
MAX_FINITE = oracle.binary64_value(MAX_BITS)
TAU_BITS = 0x3ddb7cdfd9d7bdbb
TAU = oracle.binary64_value(TAU_BITS)
value = oracle.binary64_value


class Refusal(ValueError):
    pass


def canonical(bits):
    value(bits)  # Reject malformed or nonfinite bit patterns.
    return 0 if bits == SIGN else bits


def neighbor(bits, direction):
    bits = canonical(bits)
    if direction not in (-1, 1):
        raise Refusal('neighbor direction must be -1 or 1')
    if bits == 0:
        return 1 if direction == 1 else SIGN | 1
    answer = bits + (direction if bits < SIGN else -direction)
    try:
        return canonical(answer)
    except oracle.ContractError as exc:
        raise Refusal('finite adjacent threshold required') from exc


def midpoint(bits, direction):
    return (value(bits) + value(neighbor(bits, direction))) / 2


def rn_relation(x, bits, relation):
    """Exact preimage of one comparison with RN(x), protected finite domain."""
    if type(x) is not Q or abs(x) > MAX_FINITE:
        raise Refusal('exact Fraction in protected finite range required')
    bits = canonical(bits)
    even = not (bits & 1)
    if relation == '>=':
        cut = midpoint(bits, -1)
        return x > cut or (x == cut and even)
    if relation == '>':
        cut = midpoint(bits, 1)
        return x > cut or (x == cut and not even)
    if relation == '<=':
        cut = midpoint(bits, 1)
        return x < cut or (x == cut and even)
    if relation == '<':
        cut = midpoint(bits, -1)
        return x < cut or (x == cut and not even)
    raise Refusal('unknown relation')


def point_predicates(a_bits, b_bits, comparison):
    a_bits, b_bits = canonical(a_bits), canonical(b_bits)
    a, b = value(a_bits), value(b_bits)
    if a < 0 or b < 0 or b + TAU > MAX_FINITE:
        raise Refusal('finite nonnegative operands and protected b+tau required')
    weak = rn_relation(b + TAU, a_bits, '>=')
    if comparison == 'PRIMARY':
        strict = rn_relation(b - a, TAU_BITS, '>')
    elif comparison == 'SECONDARY':
        strict = False if a == MAX_FINITE else rn_relation(b - TAU, a_bits, '>')
    else:
        raise Refusal('explicit PRIMARY or SECONDARY required')
    return weak, strict


def representative_box(lower, upper):
    """Finite nonnegative binary64 lattice intersected with exact closed bounds."""
    if type(lower) is not Q or type(upper) is not Q or lower > upper:
        raise Refusal('ordered exact rational bounds required')
    lower, upper = max(Q(0), lower), min(MAX_FINITE, upper)
    if lower > upper:
        raise Refusal('no finite nonnegative scalar in enclosure')
    lo, hi = 0, MAX_BITS
    while lo < hi:
        mid = (lo + hi) // 2
        if value(mid) >= lower:
            hi = mid
        else:
            lo = mid + 1
    first = lo
    lo, hi = 0, MAX_BITS
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if value(mid) <= upper:
            lo = mid
        else:
            hi = mid - 1
    last = lo
    if value(first) < lower or value(last) > upper or first > last:
        raise Refusal('interval contains no binary64 scalar')
    return first, last


def interval_sufficient(local_bounds, other_bounds, comparison):
    """Universal worst-corner test under separately proved operand enclosures."""
    if len(local_bounds) != 2 or len(other_bounds) != 2:
        raise Refusal('exactly two metric enclosures required')
    a = [representative_box(*bounds) for bounds in local_bounds]
    b = [representative_box(*bounds) for bounds in other_bounds]
    if any(value(pair[1]) + TAU > MAX_FINITE for pair in b):
        raise Refusal('whole operand box must satisfy finite protected domain')
    predicates = [point_predicates(x[1], y[0], comparison) for x, y in zip(a, b)]
    return {'weak': [p[0] for p in predicates], 'strict': [p[1] for p in predicates],
            'supported_for_every_scalar_in_box': all(p[0] for p in predicates) and any(p[1] for p in predicates),
            'historical_trace_admitted': False, 'norm_correct_rounding_assumed': False}
