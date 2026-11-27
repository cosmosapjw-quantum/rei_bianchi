"""Exact G7 coefficients and conditional third-order bound.

Scope: real symmetric trace-free dimensionless integrated shear S, a fixed
principal/commuting Bianchi-I map exp(-S), and isotropic INITIAL directions.
This is not a general noncommuting-history or observer-weighted-sky adapter.
"""
from fractions import Fraction
from itertools import product

MAX_BITS = 4096

def rational(value):
    """Accept exact rationals only; no silent binary64 or boolean coercion."""
    if type(value) not in (int, Fraction):
        raise TypeError('exact int/Fraction required')
    value = Fraction(value)
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > MAX_BITS:
        raise ValueError('rational resource limit exceeded')
    return value

def checked_matrix(matrix):
    if type(matrix) not in (tuple, list) or len(matrix) != 3:
        raise ValueError('3x3 matrix required')
    if any(type(row) not in (tuple, list) or len(row) != 3 for row in matrix):
        raise ValueError('3x3 matrix required')
    S = tuple(tuple(rational(x) for x in row) for row in matrix)
    if any(S[i][j] != S[j][i] for i in range(3) for j in range(3)):
        raise ValueError('symmetric S required')
    if sum(S[i][i] for i in range(3)) != 0:
        raise ValueError('trace-free S required')
    return S

def _square(S):
    return tuple(tuple(sum(S[i][k]*S[k][j] for k in range(3)) for j in range(3)) for i in range(3))

def moments(matrix):
    S = checked_matrix(matrix)
    tr2 = sum(S[i][j]*S[j][i] for i in range(3) for j in range(3))
    upper = max(sum(abs(x) for x in row) for row in S)
    return {'trace_s2':tr2, 'mean_delta_second':tr2/5,
            'mean_delta2_second':2*tr2/15, 'spectral_norm_upper':upper}

def response(matrix, A, B):
    """Second-order <F(Delta)/F(0)-1>; A and B are matching derivatives."""
    A, B = rational(A), rational(B)
    m = moments(matrix)
    return A*m['mean_delta_second'] + B*m['mean_delta2_second']/2

def remainder_bound(matrix, A, B, M3):
    """Conditional bound, NOT an automatically certified observable error.

The caller must separately prove F/F(0) is C^3 for |Delta|<=sbar and that
|d^3(F/F(0))/dDelta^3|<=M3 there. Passing M3 does not certify that premise.
The returned bound is (4|A|/3+|B|+M3/6)*sbar^3, where sbar>=||S||_2.
"""
    A, B, M3 = rational(A), rational(B), rational(M3)
    if M3 < 0:
        raise ValueError('nonnegative proved M3 upper bound required')
    sbar = moments(matrix)['spectral_norm_upper']
    return (4*abs(A)/3 + abs(B) + M3/6)*sbar**3

def angular_moments_14(matrix):
    """Independent degree-4 exact sphere cubature; no norm diagonalization.

Six axes have weight 1/15 each, eight cube corners have weight 3/40 each.
Corner direction products are formed as v_i*v_j/3, avoiding sqrt(3).
Only q, r, q^2 polynomials are integrated, not the nonpolynomial exact map.
"""
    S = checked_matrix(matrix)
    S2 = _square(S)
    qmean = rmean = q2mean = Fraction(0)
    for i in range(3):
        w = Fraction(2,15)
        qmean += w*S[i][i]
        rmean += w*S2[i][i]
        q2mean += w*S[i][i]**2
    for v in product((-1,1),repeat=3):
        w = Fraction(3,40)
        q = sum(v[i]*v[j]*S[i][j] for i in range(3) for j in range(3))/3
        r = sum(v[i]*v[j]*S2[i][j] for i in range(3) for j in range(3))/3
        qmean += w*q
        rmean += w*r
        q2mean += w*q*q
    return {'mean_q':qmean, 'mean_r':rmean, 'mean_q2':q2mean}
