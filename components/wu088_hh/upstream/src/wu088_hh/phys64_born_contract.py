"""Exact conditional Catalan bounds and a proved physical low-channel case.

Atomic numerical coordinates r/a0, k*a0=7/10; V=epsilon*W in reduced
Schrodinger equation. A kernel bound is an ASSUMPTION unless constructed
by low_mode_certificate. This module never certifies a numerical ODE run.
"""
from fractions import Fraction as F
from math import comb

EPSILON = F(3, 10**23)
B = F(27)
K2 = F(49, 100)


def catalan(n: int) -> int:
    if type(n) is not int or n < 0:
        raise ValueError('nonnegative integer index required')
    return comb(2*n, n)//(n+1)


def majorant(kernel_upper: F, potential_upper: F, epsilon: F, order: int) -> dict:
    """If ||T||<=K and ||W||<=w, bound the tail after `order` terms.

    Delta=sum epsilon**n Y_n; A=K*w; ||Y_n||<=Cat(n-1)*K**(n-1)*A**n.
    The returned arithmetic is exact; it does not validate supplied K,w.
    """
    if not all(isinstance(x, F) for x in (kernel_upper, potential_upper, epsilon)):
        raise TypeError('exact Fraction inputs required')
    if kernel_upper < 0 or potential_upper < 0 or type(order) is not int or order < 1:
        raise ValueError('nonnegative bounds and positive order required')
    a = kernel_upper*potential_upper
    q = 4*abs(epsilon)*kernel_upper*a
    if q >= 1:
        raise ValueError('Catalan convergence condition q<1 not established')
    coefficients = [catalan(n-1)*kernel_upper**(n-1)*a**n for n in range(1,order+1)]
    return {'q':q, 'tail_upper':abs(epsilon)*a*q**order/(1-q),
            'coefficient_bounds':coefficients,
            'scope':'CONDITIONAL_ON_KERNEL_AND_MULTIPLIER_UPPER_BOUNDS',
            'validates_ode_roundoff_or_spatial_truncation':False}


def low_mode_certificate(outer: F=F(39), order: int=2) -> dict:
    """Proved continuum certificate ONLY for ell subset {0,1}, r in [27,T].

    q_l(r)=k²+2/r-l(l+1)/r² is positive decreasing for these modes.
    E_l=|H'|²+q_l|H|² <=2q_l. The current Im(H*H')=k gives
    |H(t)/H(r)|²<=4(k²+2/B)/k². This bounds the exact Volterra kernel.
    Real original V is Galerkin projected and cut to zero outside T.
    """
    if not isinstance(outer,F) or not B < outer <= 55:
        raise ValueError('exact rational outer radius in (27,55] required')
    source_exp_lower=sum((F(263,5)**j)/F(_factorial(j)) for j in range(161))
    screen_upper=2*(1+F(10,263))/source_exp_lower
    if not screen_upper < EPSILON:
        raise ArithmeticError('original screen envelope not certified')
    ratio_upper=4*(K2+2/B)/K2
    kernel_upper=(outer-B)*ratio_upper
    out=majorant(kernel_upper,F(1),EPSILON,order)
    out.update({'scope':'PROVED_CONTINUUM_ONLY_ELL_SUBSET_0_1_SCREEN_CUT_AT_T',
                'outer':outer,'epsilon':EPSILON,'screen_upper':screen_upper,
                'transport_ratio_squared_upper':ratio_upper,'kernel_upper':kernel_upper,
                'high_angular_or_P20_Q21_certificate':False})
    return out


def _factorial(n: int) -> int:
    ans=1
    for j in range(2,n+1): ans*=j
    return ans
