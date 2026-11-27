"""Independent synthetic diagnostics using Decimal, never enclosure authority.

Engine bounds are justified analytically and by exact directed arithmetic.
This oracle uses an AGM pi computation, erf series and composite Simpson sums.
The Simpson refinement difference is a diagnostic, not a certified error bound.
"""
from decimal import Decimal as D, localcontext
from fractions import Fraction
from functools import lru_cache
from math import factorial


def dec(q):
    q = Fraction(q)
    return D(q.numerator) / D(q.denominator)


@lru_cache(maxsize=4)
def pi(digits=90):
    with localcontext() as ctx:
        ctx.prec = digits + 20
        a, b, t, power = D(1), D(1)/D(2).sqrt(), D(1)/4, D(1)
        for _ in range(12):
            next_a = (a+b)/2
            b = (a*b).sqrt()
            t -= power*(a-next_a)**2
            a = next_a
            power *= 2
        result = (a+b)**2/(4*t)
        ctx.prec = digits
        return +result


def gamma_half(twice_shape, x):
    """Upper half-integer gamma via independent entire erf Taylor series."""
    x = dec(x)
    root = x.sqrt()
    term, series = D(1), D(1)
    for n in range(1, 1024):
        term *= -x/n
        addition = term/(2*n+1)
        series += addition
        if abs(addition) < D('1e-100'):
            break
    else:
        raise RuntimeError('Synthetic oracle series cap')
    result = pi().sqrt()-2*root*series
    for shape2 in range(1, twice_shape, 2):
        result = D(shape2)/2*result + root**shape2*(-x).exp()
    return result


def density_parameters(i, mu, a):
    mu, a = dec(mu), dec(a)
    lam = mu*mu/4
    coeffs = [D(factorial(i+1))*mu**(i+1-2*r)
              /(pi().sqrt()*D(2)**(i+1)*factorial(r)*factorial(i+1-2*r))
              for r in range((i+1)//2+1)]
    return lam, a, coeffs


def phi(t, i, lam, a, coeffs):
    if not t:
        return D(0)
    return (-lam/t).exp()*sum(c/(t**(i+1-r)*t.sqrt())
                             for r,c in enumerate(coeffs))/((a+t)*(a+t).sqrt())


def phi_inverse(x, i, lam, a, coeffs):
    # t=1/x, including dt=x^-2 dx. Powers are nonnegative integers.
    return (-lam*x).exp()*sum(c*x**(i+1-r) for r,c in enumerate(coeffs)) / ((1+a*x)*(1+a*x).sqrt())


def simpson(func, lo, hi, panels):
    if panels % 2:
        raise ValueError('Even panel count required')
    h = (hi-lo)/panels
    total = func(lo)+func(hi)
    for j in range(1,panels):
        total += (4 if j%2 else 2)*func(lo+j*h)
    return total*h/3


def mass_diagnostics(i, mu, a, l, T):
    with localcontext() as ctx:
        ctx.prec = 90
        lam, aa, coeffs = density_parameters(i,mu,a)
        f = lambda t: phi(t,i,lam,aa,coeffs)
        inv = lambda x: phi_inverse(x,i,lam,aa,coeffs)
        result = {}
        for name, func, lo, hi in [('lower',f,D(0),dec(l)),
                                  ('interior',f,dec(l),dec(T)),
                                  ('upper',inv,D(0),1/dec(T))]:
            coarse = simpson(func,lo,hi,256)
            fine = simpson(func,lo,hi,512)
            result[name] = {'value':fine,'refinement_delta':abs(fine-coarse),
                            'panels':[256,512],'precision_digits':90,
                            'rigorous_quadrature':False}
        return result
