"""Finite local models prescribed by EXECUTION_CONTRACT.md; no runtime network."""
from pathlib import Path
import json
from functools import lru_cache
import numpy as np
from scipy.special import iv, kv

BASE = Path(__file__).resolve().parents[1]
COEFF = json.loads((BASE/'inputs/atomic_coefficients.json').read_text())
DECAY = json.loads((BASE/'inputs/EVALUATED_DECAY_INPUTS.json').read_text())
ROW = COEFF['rr']['1:1']
KB = 1.380649e-23
EV = 1.602176634e-19
CHI = COEFF['photo_VF1996']['1:0']['Eth_eV']*EV
LAMBDA = 1/DECAY['neutron_mean_lifetime_s']
A = ROW['A_cm3_s']*1e-6
B = ROW['B']
S0, S1 = np.sqrt(ROW['T0_K']), np.sqrt(ROW['T1_K'])
C_PRIMITIVE = (2+B)*S0+(2-B)*S1
ELL2 = (C_PRIMITIVE+np.sqrt(C_PRIMITIVE*C_PRIMITIVE-12*S0*S1))/6
ELL1 = S0*S1/(3*ELL2)
B1 = (S0-ELL1)*(S1-ELL1)/(-3*ELL1*(ELL2-ELL1))
B2 = -2/3-B1


def rate(T):
    r = np.sqrt(T)
    alpha = A/((r/S0)*(1+r/S0)**(1-B)*(1+r/S1)**(1+B))
    D = -.5-(1-B)*r/(2*(r+S0))-(1+B)*r/(2*(r+S1))
    Dw = -(1-B)*r*S0/(4*(r+S0)**2)-(1+B)*r*S1/(4*(r+S1)**2)
    return alpha, D, Dw


@lru_cache(maxsize=3)
def alpha_initial(Ti):
    return rate(Ti)[0]


def thermal_rhs(s, y, Ti):
    x, w = y[:2]
    T = Ti*np.exp(w)
    alpha, D, _ = rate(T)
    k = alpha/alpha_initial(Ti)
    return np.array([-k*x*x, -(2/3)*k*x*x*D/(1+x)])


def thermal_jac(s, y, Ti):
    x, w = y
    alpha, D, Dw = rate(Ti*np.exp(w))
    k = alpha/alpha_initial(Ti)
    return np.array([[-2*k*x, -k*x*x*D],
                     [-(2/3)*k*D*x*(2+x)/(1+x)**2,
                      -(2/3)*k*x*x*(D*D+Dw)/(1+x)]])


def energies(x, w, Ti):
    T = Ti*np.exp(w)
    return 1.5*KB*(1+x)*T, CHI*x


def reference_thermal_rhs(s, y, Ti, Escale):
    x, w, _ = y
    T = Ti*np.exp(w)
    alpha, D, _ = rate(T)
    energy_rate = x*x*(alpha/alpha_initial(Ti))*(CHI+KB*T*(1.5+D))/Escale
    return np.r_[thermal_rhs(s, y, Ti), energy_rate]


def primitive(w, Ti):
    ri = np.sqrt(Ti)
    dr = ri*np.expm1(w/2)
    return -6*(w/2+B1*np.log1p(dr/(ri+ELL1))+B2*np.log1p(dr/(ri+ELL2)))


def reconstruct_x(w, Ti, xi=.9):
    return xi+(1+xi)*np.expm1(primitive(w, Ti))


def reduced_rhs(s, y, Ti):
    w = y[0]
    return thermal_rhs(s, [reconstruct_x(w, Ti), w], Ti)[1:]


def beta_rhs(v, y, rho):
    n, p, h = y
    rr = rho*p*p
    return np.array([-n, n-rr, rr])


def beta_jac(v, y, rho):
    p = y[1]
    return np.array([[-1., 0, 0], [1., -2*rho*p, 0], [0, 2*rho*p, 0]])


def decay_step(y, d):
    n, p, h = y
    delta = n*(-np.expm1(-d))
    return np.array([n*np.exp(-d), p+delta, h])


def rr_step(y, d, rho):
    n, p, h = y
    q = rho*p*d
    delta = p*q/(1+q)
    return np.array([n, p/(1+q), h+delta])


def strang(rho, N, end=4., initial=(.1,.2,.7)):
    out = np.empty((3, N+1))
    out[:, 0] = initial
    d = end/N
    for j in range(N):
        out[:, j+1] = decay_step(rr_step(decay_step(out[:, j], d/2), d, rho), d/2)
    return out


def bessel_reference(v, rho, initial=(.1,.2,.7)):
    v = np.asarray(v)
    ni, pi, hi = initial
    n = ni*np.exp(-v)
    if rho == 0:
        p = pi+ni*(-np.expm1(-v))
    elif ni == 0:
        p = pi/(1+rho*pi*v)
    else:
        z0 = 2*np.sqrt(rho*ni)
        z = z0*np.exp(-v/2)
        c = z0*kv(1,z0)-2*rho*pi*kv(0,z0)
        d = z0*iv(1,z0)+2*rho*pi*iv(0,z0)
        u = c*iv(0,z)+d*kv(0,z)
        uv = z*(-c*iv(1,z)+d*kv(1,z))/2
        p = uv/(rho*u)
    p = np.where(v == 0, pi, p)
    h = hi+(ni-n)+(pi-p)
    return np.array([n,p,h])


def embed(y):
    result = np.zeros((21,)+np.shape(y)[1:])
    result[0], result[2], result[1] = y
    return result


def embedded_rhs(v, Y, rho):
    # Independent reaction-scatter assembly in original state order n, HI, HII.
    result = np.zeros(21)
    decay = Y[0]
    rr = rho*Y[2]**2
    result[0] -= decay
    result[2] += decay-rr
    result[1] += rr
    return result
