"""Exact, project-input-free implementation lemmas. No scientific payload loader."""
from fractions import Fraction as Q
from math import factorial, isqrt


def rising(a, n):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative integer order required")
    result = Q(1)
    for j in range(n):
        result *= Q(a) + j
    return result


def radial_shift(k, r):
    """Return shifted a,b and exact multiplier apart from (2sigma)^(k/2-r)."""
    if type(k) is not int or not 0 <= k <= 8 or type(r) is not int or not 0 <= r <= 2:
        raise ValueError("supported radial k=0..8, r=0..2")
    a, b = -Q(k, 2), Q(3, 2)
    return a + r, b + r, (-1)**r * rising(a, r) / rising(b, r)


def even_radial_coefficients(k):
    """c[j] multiplies sigma**(k/2-j) * s**j; exact noncentral radial polynomial."""
    if type(k) is not int or not 0 <= k <= 8 or k % 2:
        raise ValueError("even degree k=0,2,4,6,8 required")
    n = k // 2
    return tuple(2**(n-j) * rising(Q(3, 2), n) * rising(-n, j) * (-1)**j
                 / rising(Q(3, 2), j) / factorial(j) for j in range(n + 1))


def hermite_envelope_terms(i, mu):
    """Return (sqrt(pi)*A_ir, nu_ir), leaving sqrt(pi) symbolic."""
    mu = Q(mu)
    if type(i) is not int or not 0 <= i <= 8 or mu <= 0:
        raise ValueError("i=0..8 and exact positive mu required")
    return tuple((Q(factorial(i+1), 2**(i+1)*factorial(r)*factorial(i+1-2*r))
                  * mu**(i+1-2*r), Q(2*i+3, 2)-r)
                 for r in range((i+1)//2+1))


def sqrt_upper_rational(x, bits=64):
    """Outward dyadic upper bound using integer arithmetic alone."""
    x = Q(x)
    if x < 0 or type(bits) is not int or not 0 <= bits <= 100000:
        raise ValueError("nonnegative radicand and bounded integer precision required")
    scale = 1 << bits
    n = isqrt((x.numerator * scale * scale) // x.denominator)
    if Q(n*n, scale*scale) < x:
        n += 1
    return Q(n, scale)


def rectangle_disk_radius(rx, ry, bits=64):
    rx, ry = Q(rx), Q(ry)
    if rx < 0 or ry < 0:
        raise ValueError("nonnegative rectangle radii required")
    return sqrt_upper_rational(rx*rx + ry*ry, bits)


def complement_bound(C, S_t, W_u, J_t, S_u):
    args = tuple(map(Q, (C, S_t, W_u, J_t, S_u)))
    if any(x < 0 for x in args):
        raise ValueError("nonnegative independent upper bounds required")
    C, S_t, W_u, J_t, S_u = args
    return C * (S_t * W_u + J_t * S_u)


def exact_tau(z, stored_v):
    z, stored_v = Q(z), Q(stored_v)
    if not stored_v:
        raise ValueError("nonzero stored velocity required")
    return z / stored_v


def supported_by_lower_gaps(lower_gaps, tolerance):
    """Mathematical sufficient Pareto condition; not the frozen machine comparator."""
    gaps, tol = tuple(map(Q, lower_gaps)), Q(tolerance)
    if len(gaps) != 2 or tol < 0:
        raise ValueError("two exact lower gaps and nonnegative tolerance required")
    return all(g >= -tol for g in gaps) and any(g > tol for g in gaps)


class Poly:
    """Small exact multivariate polynomial ring, used only for algebra checks."""
    def __init__(self, terms, nvars):
        self.nvars = nvars
        self.terms = {tuple(k): Q(v) for k, v in terms.items() if v}

    @classmethod
    def constant(cls, c, nvars):
        return cls({(0,)*nvars: Q(c)}, nvars)

    @classmethod
    def variable(cls, idx, nvars):
        e = [0]*nvars
        e[idx] = 1
        return cls({tuple(e): Q(1)}, nvars)

    def _coerce(self, other):
        if isinstance(other, Poly):
            if self.nvars != other.nvars:
                raise ValueError("different polynomial rings")
            return other
        return self.constant(other, self.nvars)

    def __add__(self, other):
        other = self._coerce(other)
        terms = self.terms.copy()
        for e, c in other.terms.items():
            terms[e] = terms.get(e, Q(0)) + c
        return Poly(terms, self.nvars)

    __radd__ = __add__

    def __neg__(self):
        return Poly({e: -c for e, c in self.terms.items()}, self.nvars)

    def __sub__(self, other):
        return self + (-self._coerce(other))

    def __rsub__(self, other):
        return self._coerce(other) - self

    def __mul__(self, other):
        other = self._coerce(other)
        result = {}
        for e, c in self.terms.items():
            for f, d in other.terms.items():
                g = tuple(x+y for x, y in zip(e, f))
                result[g] = result.get(g, Q(0)) + c*d
        return Poly(result, self.nvars)

    __rmul__ = __mul__

    def __pow__(self, n):
        if type(n) is not int or n < 0:
            raise ValueError("nonnegative integer exponent required")
        result = self.constant(1, self.nvars)
        for _ in range(n):
            result *= self
        return result

    def diff(self, idx):
        result = {}
        for e, c in self.terms.items():
            if e[idx]:
                f = list(e)
                f[idx] -= 1
                result[tuple(f)] = c*e[idx]
        return Poly(result, self.nvars)

    def __eq__(self, other):
        other = self._coerce(other)
        return self.terms == other.terms
