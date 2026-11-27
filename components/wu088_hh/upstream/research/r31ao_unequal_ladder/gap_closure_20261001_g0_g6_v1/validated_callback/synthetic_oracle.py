"""Exact synthetic polynomial oracle, never a numerical ball backend."""
from dataclasses import dataclass
from fractions import Fraction as Q
from math import factorial, comb


def rising(x, n):
    out=Q(1)
    for j in range(n): out*=x+j
    return out


def radial_even(k, derivative, sigma, s):
    """Terminating 1F1 evaluated as a polynomial using exact rationals."""
    if k not in (0,2,4,6,8) or derivative not in (0,1,2):
        raise ValueError('synthetic even degrees 0..8 and derivatives 0..2 only')
    if not isinstance(sigma,Q) or not isinstance(s,Q) or sigma<=0:
        raise ValueError('positive exact rational sigma and exact rational s required')
    h=k//2
    pref=(2*sigma)**h*rising(Q(3,2),h)
    return pref*sum((rising(-h,n)/rising(Q(3,2),n)
                     *(-1/(2*sigma))**n*s**(n-derivative)
                     /factorial(n-derivative)
                     for n in range(derivative,h+1)),Q(0))


def gaussian_cartesian_moment(k,sigma,s):
    """Independent expansion of E[(X²+Y²+Z²)^(k/2)].

    X has mean sqrt(s); Y,Z have mean zero; independent variance sigma.
    All surviving sqrt(s) powers are even, so s is used algebraically.
    """
    h=k//2
    def centered(n):
        return Q(factorial(2*n),2**n*factorial(n))*sigma**n
    def displaced(n):
        return sum((comb(2*n,2*j)*centered(j)*s**(n-j)
                    for j in range(n+1)),Q(0))
    return sum((Q(factorial(h),factorial(i)*factorial(j)*factorial(h-i-j))
                *displaced(i)*centered(j)*centered(h-i-j)
                for i in range(h+1) for j in range(h-i+1)),Q(0))


@dataclass(frozen=True)
class Box:
    re_lo: Q
    re_hi: Q
    im_lo: Q
    im_hi: Q
    def __post_init__(self):
        if not all(isinstance(x,Q) for x in (self.re_lo,self.re_hi,self.im_lo,self.im_hi)):
            raise ValueError('exact rationals only')
        if self.re_lo>self.re_hi or self.im_lo>self.im_hi:
            raise ValueError('inverted interval')


def domain_ok(box,margin):
    if not isinstance(margin,Q) or margin<=0:
        raise ValueError('strict positive exact margin required')
    return box.re_lo>margin
