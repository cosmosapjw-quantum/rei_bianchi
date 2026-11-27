"""Exact rational reference for CONDITIONAL interval implications.

No physical RHS, nonlinear solver, native callback or certificate issuer lives
here. Caller-supplied interval bounds and domain statements remain assumptions.
Finite rational operations are exact; binary64 inputs must be converted explicitly
to their exact ratios by the caller rather than silently rounded decimal values.
"""
from dataclasses import dataclass
from fractions import Fraction as Q


def rational(x):
    if isinstance(x, float):
        raise TypeError("convert binary64 explicitly with Fraction.from_float")
    return Q(x)


@dataclass(frozen=True)
class Interval:
    lo: Q
    hi: Q

    def __init__(self, lo, hi=None):
        lo = rational(lo)
        hi = lo if hi is None else rational(hi)
        if lo > hi:
            raise ValueError("reversed interval")
        object.__setattr__(self, "lo", lo)
        object.__setattr__(self, "hi", hi)

    def __add__(self, other):
        other = iv(other)
        return Interval(self.lo + other.lo, self.hi + other.hi)

    __radd__ = __add__

    def __neg__(self):
        return Interval(-self.hi, -self.lo)

    def __sub__(self, other):
        return self + (-iv(other))

    def __rsub__(self, other):
        return iv(other) - self

    def __mul__(self, other):
        other = iv(other)
        p = (self.lo * other.lo, self.lo * other.hi,
             self.hi * other.lo, self.hi * other.hi)
        return Interval(min(p), max(p))

    __rmul__ = __mul__

    def reciprocal(self):
        if self.lo <= 0 <= self.hi:
            raise ValueError("division interval contains zero")
        return Interval(1 / self.hi, 1 / self.lo)

    def __truediv__(self, other):
        return self * iv(other).reciprocal()

    def __rtruediv__(self, other):
        return iv(other) / self

    def square(self):
        if self.lo <= 0 <= self.hi:
            return Interval(0, max(self.lo**2, self.hi**2))
        return Interval(min(self.lo**2, self.hi**2),
                        max(self.lo**2, self.hi**2))

    @property
    def mag(self):
        return max(abs(self.lo), abs(self.hi))

    @property
    def mid(self):
        return (self.lo + self.hi) / 2

    @property
    def width(self):
        return self.hi - self.lo

    def contains(self, value):
        value = iv(value)
        return self.lo <= value.lo and value.hi <= self.hi

    def json(self):
        return {"lo": str(self.lo), "hi": str(self.hi)}


def iv(x):
    return x if isinstance(x, Interval) else Interval(x)


def vector(v, n=None):
    v = tuple(iv(x) for x in v)
    if not v or (n is not None and len(v) != n):
        raise ValueError("vector dimension")
    return v


def matrix(a, rows=None, cols=None):
    a = tuple(tuple(iv(x) for x in row) for row in a)
    if not a or not a[0] or any(len(row) != len(a[0]) for row in a):
        raise ValueError("matrix shape")
    if (rows is not None and len(a) != rows) or (
            cols is not None and len(a[0]) != cols):
        raise ValueError("matrix dimension")
    return a


def dot(a, b):
    if len(a) != len(b):
        raise ValueError("dot dimension")
    return sum((iv(x) * iv(y) for x, y in zip(a, b)), Interval(0))


def matvec(a, v):
    a = matrix(a)
    v = vector(v, len(a[0]))
    return tuple(dot(row, v) for row in a)


def matmul(a, b):
    a, b = matrix(a), matrix(b)
    if len(a[0]) != len(b):
        raise ValueError("product dimension")
    return tuple(tuple(dot(row, col) for col in zip(*b)) for row in a)


def exact_matrix(c, n):
    c = matrix(c, n, n)
    if any(x.lo != x.hi for row in c for x in row):
        raise ValueError("preconditioner must be fixed, not interval-valued")
    return c


def defect_matrix(a, c):
    a = matrix(a)
    n = len(a)
    a = matrix(a, n, n)
    c = exact_matrix(c, n)
    ca = matmul(c, a)
    return tuple(tuple((Interval(int(i == j)) - ca[i][j]).mag
                       for j in range(n)) for i in range(n))


def positive_scales(scales, n):
    scales = tuple(rational(x) for x in scales)
    if len(scales) != n or any(x <= 0 for x in scales):
        raise ValueError("positive scales required")
    return scales


def norm_bound(b, scales):
    s = positive_scales(scales, len(b))
    return max(sum(bij * sj for bij, sj in zip(row, s)) / si
               for row, si in zip(b, s))


def solve_exact(a, rhs):
    """Small exact Gaussian solve, used only for the comparison matrix I-B."""
    n = len(rhs)
    if len(a) != n or any(len(row) != n for row in a):
        raise ValueError("solve dimension")
    work = [[rational(x) for x in row] + [rational(y)]
            for row, y in zip(a, rhs)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if work[i][j]), None)
        if pivot is None:
            raise ValueError("singular comparison matrix")
        work[j], work[pivot] = work[pivot], work[j]
        p = work[j][j]
        work[j] = [x / p for x in work[j]]
        for i in range(n):
            if i != j:
                p = work[i][j]
                work[i] = [x - p * y for x, y in zip(work[i], work[j])]
    return tuple(row[-1] for row in work)


@dataclass(frozen=True)
class Domain:
    family_id: str
    source_revision: str
    common_seed_id: str
    terminal_time_id: str
    theta: tuple
    coverage: str = "UNIFORM_PARAMETER_RECTANGLE"
    smoothness_assumption: str = "C2_ON_OPEN_DOMAIN"
    admissibility_assumption: bool = True

    def require(self):
        if not all((self.family_id, self.source_revision, self.common_seed_id,
                    self.terminal_time_id)):
            raise ValueError("missing family/source/seed/time identity")
        if self.coverage != "UNIFORM_PARAMETER_RECTANGLE":
            raise ValueError("point-only data cannot bound a finite rectangle")
        if self.smoothness_assumption != "C2_ON_OPEN_DOMAIN":
            raise ValueError("C2 domain assumption missing")
        if not self.admissibility_assumption:
            raise ValueError("physical admissibility assumption missing")
        if len(self.theta) != 2 or any(not isinstance(t, Interval) or t.width <= 0
                                       for t in self.theta):
            raise ValueError("nondegenerate ordered parameter rectangle required")

    @property
    def area(self):
        self.require()
        return self.theta[0].width * self.theta[1].width

    def require_same_family(self, other):
        self.require()
        other.require()
        if self != other:
            raise ValueError("paired bounds need the same family/seed/time/rectangle")


@dataclass(frozen=True)
class RootArithmetic:
    domain: Domain
    a: tuple
    c: tuple
    center: tuple
    radius: tuple
    b: tuple
    q: Q
    image_radius: tuple
    native_authority: bool = False


def uniform_root_arithmetic(gc, a, c, center, radius, domain):
    """Sufficient algebra ONLY, conditional on uniform truthful source bounds."""
    domain.require()
    gc = vector(gc)
    n = len(gc)
    a, c = matrix(a, n, n), exact_matrix(c, n)
    center = tuple(rational(x) for x in center)
    if len(center) != n:
        raise ValueError("center dimension")
    radius = positive_scales(radius, n)
    b = defect_matrix(a, c)
    q = norm_bound(b, radius)
    if q >= 1:
        raise ValueError("uniform contraction condition failed")
    beta = tuple(x.mag for x in matvec(c, gc))
    image = tuple(bi + sum(x * r for x, r in zip(row, radius))
                  for bi, row in zip(beta, b))
    if any(im >= r for im, r in zip(image, radius)):
        raise ValueError("strict root image inclusion failed")
    return RootArithmetic(domain, a, c, center, radius, b, q, image)


@dataclass(frozen=True)
class LinearArithmetic:
    enclosure: tuple
    beta: tuple
    radius: tuple
    q: Q
    b: tuple
    native_authority: bool = False


def linear_enclosure(a, c, rhs, scales, center=None):
    rhs = vector(rhs)
    n = len(rhs)
    a, c = matrix(a, n, n), exact_matrix(c, n)
    scales = positive_scales(scales, n)
    center = tuple(Q(0) for _ in range(n)) if center is None else tuple(
        rational(x) for x in center)
    if len(center) != n:
        raise ValueError("linear center dimension")
    b = defect_matrix(a, c)
    q = norm_bound(b, scales)
    if q >= 1:
        raise ValueError("linear contraction condition failed")
    ac = matvec(a, center)
    residual = tuple(f - v for f, v in zip(rhs, ac))
    beta = tuple(x.mag for x in matvec(c, residual))
    comparison = tuple(tuple(Q(int(i == j)) - b[i][j] for j in range(n))
                       for i in range(n))
    radius = solve_exact(comparison, beta)
    if any(r < 0 for r in radius):
        raise ArithmeticError("nonnegative comparison solution expected")
    enclosure = tuple(Interval(z - r, z + r) for z, r in zip(center, radius))
    return LinearArithmetic(enclosure, beta, radius, q, b)


def mixed_forcing(gab, gya, gyb, gyy, u, v):
    """-(G_ab + G_ya V + G_yb U + G_yy[U,V]); old-state jets are in G."""
    gab = vector(gab)
    n = len(gab)
    gya, gyb = matrix(gya, n, n), matrix(gyb, n, n)
    u, v = vector(u, n), vector(v, n)
    if len(gyy) != n:
        raise ValueError("Hessian output dimension")
    gyy = tuple(matrix(h, n, n) for h in gyy)
    av, bu = matvec(gya, v), matvec(gyb, u)
    return tuple(-(gab[k] + av[k] + bu[k] + dot(u, matvec(gyy[k], v)))
                 for k in range(n))


def implicit_mixed_arithmetic(root, ga, gb, gab, gya, gyb, gyy,
                              centers=None):
    if not isinstance(root, RootArithmetic):
        raise TypeError("uniform root arithmetic prerequisite required")
    root.domain.require()
    centers = (None, None, None) if centers is None else centers
    if len(centers) != 3:
        raise ValueError("U,V,W centers required")
    u = linear_enclosure(root.a, root.c, [-iv(x) for x in ga], root.radius,
                         centers[0])
    v = linear_enclosure(root.a, root.c, [-iv(x) for x in gb], root.radius,
                         centers[1])
    forcing = mixed_forcing(gab, gya, gyb, gyy, u.enclosure, v.enclosure)
    w = linear_enclosure(root.a, root.c, forcing, root.radius, centers[2])
    return {"u": u, "v": v, "w": w, "forcing": forcing,
            "scope": "CONDITIONAL_ON_SUPPLIED_UNIFORM_DERIVATIVE_BOUNDS",
            "native_authority": False}


def finite_rectangle(w, domain, required_rectangle=None):
    domain.require()
    if required_rectangle is not None and tuple(required_rectangle) != domain.theta:
        raise ValueError("requested rectangle not covered")
    return tuple(iv(x) * domain.area for x in vector(w))


def observable_mixed(gradient, hessian, u, v, w):
    """Mixed derivative of a parameter-independent nonlinear observable."""
    w = vector(w)
    n = len(w)
    gradient, hessian = vector(gradient, n), matrix(hessian, n, n)
    return dot(gradient, w) + dot(vector(u, n), matvec(hessian, vector(v, n)))


def paired_linear_difference(a_two, c_two, delta_a, delta_f, w_full,
                             scales, two_domain, full_domain, center=None):
    """A_two ΔW = Δf - ΔA W_full using SAME-parameter joint delta bounds.

    Supplying narrow deltas without a source-derived enclosure is not valid.
    Ordinary independent interval subtraction is valid but can lose cancellation.
    """
    two_domain.require_same_family(full_domain)
    delta_f = vector(delta_f)
    n = len(delta_f)
    delta_a = matrix(delta_a, n, n)
    product = matvec(delta_a, vector(w_full, n))
    forcing = tuple(df - p for df, p in zip(delta_f, product))
    result = linear_enclosure(a_two, c_two, forcing, scales, center)
    return {"difference": result, "forcing": forcing,
            "rectangle_difference": finite_rectangle(result.enclosure, two_domain),
            "native_authority": False}


def energy_transform(fhe, chi):
    f = rational(fhe)
    chi = tuple(rational(c) for c in chi)
    if f <= 0 or len(chi) != 3 or any(c <= 0 for c in chi):
        raise ValueError("positive fHe and binding energies required")
    beta = (chi[0], f * chi[1], f * (chi[1] + chi[2]))
    s = tuple(tuple(Q(int(i == j)) for j in range(4)) for i in range(3)) + (
        beta + (Q(1),),)
    inverse = s[:3] + (tuple(-b for b in beta) + (Q(1),),)
    return s, inverse


def photo_energy_component(gas, n, energy, sigma, cnh, fhe, dt, chi):
    """One fixed-input affine-opacity group; all arithmetic exact.

    N>=0 is a primal requirement. Derivative directions may be signed. Constants,
    density, timestep and N are held fixed in the returned gas Hessian.
    """
    gas = tuple(rational(x) for x in gas)
    sigma = tuple(rational(x) for x in sigma)
    n, energy, cnh, fhe, dt = map(rational, (n, energy, cnh, fhe, dt))
    if len(gas) != 4 or len(sigma) != 3:
        raise ValueError("photo shape")
    x, y1, y2, thermal = gas
    if not (0 <= x <= 1 and 0 <= y1 and 0 <= y2 and y1 + y2 <= 1 and thermal > 0):
        raise ValueError("photo gas domain")
    if n < 0 or energy <= 0 or cnh <= 0 or fhe <= 0 or dt <= 0 or any(v < 0 for v in sigma):
        raise ValueError("photo primal data domain")
    chi = tuple(rational(v) for v in chi)
    s, _ = energy_transform(fhe, chi)
    rates = (cnh * sigma[0] * (1 - x),
             cnh * sigma[1] * fhe * (1 - y1 - y2),
             cnh * sigma[2] * fhe * y1)
    kappa = sum(rates)
    den = 1 + dt * kappa
    if den <= 0:
        raise ValueError("positive denominator required")
    alpha = (-cnh * sigma[0], cnh * fhe * (sigma[2] - sigma[1]),
             -cnh * fhe * sigma[1], Q(0))
    k = (rates[0], (rates[1] - rates[2]) / fhe, rates[2] / fhe,
         sum(r * (energy - ch) for r, ch in zip(rates, chi)))
    ledger = sum(si * ki for si, ki in zip(s[3], k))
    phi = energy * n * kappa / den
    gradient = tuple(energy * n * a / den**2 for a in alpha)
    hessian = tuple(tuple(-2 * dt * energy * n * a * b / den**3
                         for b in alpha) for a in alpha)
    return {"kappa": kappa, "denominator": den, "alpha": alpha,
            "K": k, "energy_ledger": ledger, "phi": phi,
            "gradient": gradient, "hessian": hessian,
            "negative_rank_one_weight": 2 * dt * energy * n / den**3,
            "photon": n / den, "native_authority": False}
