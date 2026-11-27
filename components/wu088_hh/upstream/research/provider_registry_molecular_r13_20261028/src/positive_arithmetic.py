"""R11 proven pure arithmetic, copied without predecessor imports or execution.

The function bodies below are byte-for-byte source copies from R11. The outer
R12 API separately enforces 1024-bit input scalars. This internal copied helper
retains the original 8192-bit conversion guard to accommodate derived exact
segment lengths; it is not an enlargement of the public R12 input domain.
"""
from fractions import Fraction
from math import factorial

BITS = 128
DEGREE = 96
MAX_SCALAR_BITS = 8192
R11_ARITHMETIC_SOURCE_SHA256 = "c3720dcc9b4e79e7d44eaa16c420a1a9b0d29d141be2fd994cc77c779cc9fa0f"
R11_ARITHMETIC_SOURCE_PATH = "research/provider_registry_molecular_r11_20261028/src/full_generator_blocks.py"
COPIED_FUNCTIONS = ('Q', '_positive', '_ceil', '_floor_scaled', '_ceil_scaled', 'down', 'up', '_tail', '_positive_series', '_exp_fraction', 'exp_interval', 'bernstein_weights')


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
