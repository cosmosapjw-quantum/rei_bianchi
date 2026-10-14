"""Exact rational algebra for the frozen PHYS33 kernel representation.

This module contains definitions only: no physical constants, source-file reads,
kernel evaluations, main entry point, or evaluated polynomial instances.
All non-integer arithmetic is fractions.Fraction arithmetic. Float, Decimal,
and string inputs are deliberately rejected; the owner supplies exact source
interpretations as Fraction objects (or exact integers).

Representation convention, for each returned derivative order n:

  k^(n)(E) = C * rational_multiplier * z**exponent_z
             * (1+z)**exponent_one_plus_z * polynomial(z),
  z = sqrt(E/B),
  C = PREF * sigma0 * area * ya**(P/2 - 11/2).

C and the noninteger powers are deliberately outside this exact algebra.
With the frozen positive PREF, sigma0, area, ya, and B, all the factored
quantities except polynomial(z) are positive. Jx and Jw stay in the polynomial.
Coefficients are always in ascending power order.
"""

from fractions import Fraction


def _fraction(value, name):
    """Admit only explicitly exact rational inputs."""
    if isinstance(value, Fraction):
        return value
    if type(value) is int:
        return Fraction(value)
    raise TypeError(name + " must be a Fraction or an exact int")


def _normalize(coefficients):
    """Copy, validate, and trim a nonempty ascending coefficient sequence."""
    result = [_fraction(value, "polynomial coefficient")
              for value in coefficients]
    if not result:
        raise ValueError("the zero polynomial must be represented by [0]")
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    if len(result) > 17:
        raise ValueError("polynomial degree exceeds the PHYS33 cap of 16")
    return result


def polynomial_add(left, right):
    """Return the exact sum of two ascending coefficient sequences."""
    left = _normalize(left)
    right = _normalize(right)
    result = [Fraction(0) for _ in range(max(len(left), len(right)))]
    for index, value in enumerate(left):
        result[index] += value
    for index, value in enumerate(right):
        result[index] += value
    return _normalize(result)


def polynomial_scale(coefficients, multiplier):
    """Return an exactly scaled polynomial."""
    coefficients = _normalize(coefficients)
    multiplier = _fraction(multiplier, "multiplier")
    return _normalize([multiplier * value for value in coefficients])


def polynomial_multiply(left, right):
    """Return the exact convolution, enforcing the degree cap."""
    left = _normalize(left)
    right = _normalize(right)
    if (len(left) == 1 and left[0] == 0
            or len(right) == 1 and right[0] == 0):
        return [Fraction(0)]
    if len(left) + len(right) - 2 > 16:
        raise ValueError("polynomial product degree exceeds the cap of 16")
    result = [Fraction(0) for _ in range(len(left) + len(right) - 1)]
    for i, left_value in enumerate(left):
        for j, right_value in enumerate(right):
            result[i + j] += left_value * right_value
    return _normalize(result)


def polynomial_derivative(coefficients):
    """Differentiate with respect to the dimensionless variable z."""
    coefficients = _normalize(coefficients)
    if len(coefficients) == 1:
        return [Fraction(0)]
    return _normalize([index * coefficients[index]
                       for index in range(1, len(coefficients))])


def polynomial_value(coefficients, argument):
    """Exact Horner evaluation; no instances are evaluated on import."""
    coefficients = _normalize(coefficients)
    argument = _fraction(argument, "argument")
    result = Fraction(0)
    for value in reversed(coefficients):
        result = result * argument + value
    return result


def derivative_numerator(coefficients, exponent_z, exponent_one_plus_z):
    """Return T[a,b]Q = [a+(a+b)z]Q + z(1+z)Q'.

    d/dE [z^a (1+z)^b Q] equals
      (2B)^(-1) z^(a-2) (1+z)^(b-1) T[a,b]Q.
    The caller owns the outside factor and exponent update.
    """
    coefficients = _normalize(coefficients)
    a = _fraction(exponent_z, "exponent_z")
    b = _fraction(exponent_one_plus_z, "exponent_one_plus_z")
    result = [Fraction(0) for _ in range(len(coefficients) + 1)]
    for index, value in enumerate(coefficients):
        result[index] += (a + index) * value
        result[index + 1] += (a + b + index) * value
    return _normalize(result)


def build_kernel_representations(P, ya, B, Jx, Jw, chi, max_order=4):
    """Build exact factored representations for k through k^(max_order).

    Parameters are rational and source-free. B must be the exact product
    E0*ya, computed by the caller from the original source-real constants.
    No stored rounded prefactor is consumed or reconstructed here.

    Return dict[int, dict] with keys polynomial, exponent_z,
    exponent_one_plus_z, and rational_multiplier. The latter is positive
    and is exactly 1 / [4*(2*B)^n]. Polynomial degree is at most 8+n,
    hence at most 12 for the allowed derivative orders 0 through 4.
    """
    P = _fraction(P, "P")
    ya = _fraction(ya, "ya")
    B = _fraction(B, "B")
    Jx = _fraction(Jx, "Jx")
    Jw = _fraction(Jw, "Jw")
    chi = _fraction(chi, "chi")
    if ya <= 0 or B <= 0:
        raise ValueError("ya and B must be strictly positive")
    if type(max_order) is not int or not 0 <= max_order <= 4:
        raise ValueError("max_order must be an integer from 0 through 4")

    # phi/C_phi = z^(P-11) (1+z)^(-P) Q_phi(z).
    # C_phi = sigma0*area*ya^(P/2-11/2); Jw remains inside Q_phi.
    a = P - 11
    b_phi = -P
    square_factor = polynomial_multiply([-1, 0, ya], [-1, 0, ya])
    q_phi = polynomial_multiply(square_factor, [Jx - Jw * chi, 0, Jw * B])

    # D=z/2*d_z. D^2+3D has common outside factor 1/4 and
    # exponent (1+z)^(b_phi-2). The 3D term therefore contributes
    # exactly 6*(1+z)*T[a,b_phi]Q_phi to the common polynomial.
    q_D = derivative_numerator(q_phi, a, b_phi)
    q_DD = derivative_numerator(q_D, a, b_phi - 1)
    q_3D = polynomial_scale(polynomial_multiply([1, 1], q_D), 6)
    q = polynomial_add(q_DD, q_3D)
    b = b_phi - 2
    multiplier = Fraction(1, 4)

    representations = {}
    for order in range(max_order + 1):
        representations[order] = {
            "polynomial": list(q),
            "exponent_z": a,
            "exponent_one_plus_z": b,
            "rational_multiplier": multiplier,
        }
        if order < max_order:
            q = derivative_numerator(q, a, b)
            a -= 2
            b -= 1
            multiplier /= 2 * B
    return representations


def _binomial(n, k):
    """Exact integer binomial coefficient for the bounded algebra below."""
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    result = 1
    for j in range(1, k + 1):
        result = result * (n - k + j) // j
    return result


def affine_power_coefficients(coefficients, left, right):
    """Return the power coefficients of Q(left+(right-left)*t).

    Both endpoints are exact rationals. A degenerate interval is allowed
    and gives a constant polynomial, retaining the original degree slots.
    """
    coefficients = _normalize(coefficients)
    left = _fraction(left, "left")
    right = _fraction(right, "right")
    if right < left:
        raise ValueError("right must be greater than or equal to left")
    width = right - left
    d = len(coefficients) - 1
    left_powers = [Fraction(1)]
    width_powers = [Fraction(1)]
    for _ in range(d):
        left_powers.append(left_powers[-1] * left)
        width_powers.append(width_powers[-1] * width)
    shifted = []
    for k in range(d + 1):
        coefficient = Fraction(0)
        for j in range(k, d + 1):
            coefficient += coefficients[j] * _binomial(j, k) * left_powers[j - k]
        shifted.append(width_powers[k] * coefficient)
    return shifted


def bernstein_coefficients(coefficients, left, right, degree=None):
    """Return exact Bernstein coefficients on a closed rational interval.

    If degree is omitted, use the polynomial's actual degree. An explicit
    degree may elevate it, but cannot lower it or exceed 16. For the zero
    polynomial the degree convention is 0. If Q(left+h*t)=sum a_k*t^k,

      beta_i = sum_{k=0}^{min(i,d)} a_k * C(i,k)/C(n,k),

    so Q(left+h*t)=sum beta_i*C(n,i)*t^i*(1-t)^(n-i).
    This is an exact identity, not point sampling or a fitted approximation.
    """
    coefficients = _normalize(coefficients)
    d = len(coefficients) - 1
    if degree is None:
        degree = d
    if type(degree) is not int or degree < d or degree > 16:
        raise ValueError("Bernstein degree must be an integer in [degree(Q),16]")
    shifted = affine_power_coefficients(coefficients, left, right)
    result = []
    for i in range(degree + 1):
        coefficient = Fraction(0)
        for k in range(min(i, d) + 1):
            coefficient += shifted[k] * Fraction(_binomial(i, k), _binomial(degree, k))
        result.append(coefficient)
    return result


def bernstein_bounds(coefficients, left, right, degree=None):
    """Return a rigorous exact (lower, upper) polynomial range enclosure."""
    converted = bernstein_coefficients(coefficients, left, right, degree)
    return min(converted), max(converted)
