"""Conditional odd-acceptance/marked-count moments for 4He(gamma,d)d.

Only exact dimensionless/frozen-generation kinematics. No nuclear rate, detector
calibration, gamma flux, stopping or production is inferred. All input numeric
parameters are exact Fraction, int or decimal string, never float.
"""
from __future__ import annotations
from fractions import Fraction as F
from dataclasses import dataclass

def rat(x):
    if isinstance(x, (float, bool)) or not isinstance(x, (int,str,F)):
        raise TypeError('Exact rational representation required; floats/bools forbidden')
    return F(x)


def reweight_outer(a, u, r):
    """PR111 universal even-moment bound, applied without source reintegration."""
    a,u,r=map(rat,(a,u,r))
    if not 0 <= a <= u <= 1 or r < 1:
        raise ValueError('0<=a<=u<=1 and r>=1 required')
    return a/(a+r*(1-a)), r*u/(1-u+r*u)


def odd_leakage_envelope(a, u, r, delta2, *, exchange_even_response=False):
    """Global deterministic interval, no statistical interpretation.

    Baseline distribution even in mu in [-1,1], q(mu)>0 with
    sup q / inf q <= r. Let m=E_q[mu], b=E_q[mu**2],
    v=delta2*(b-m**2) in MeV**2. Bound m**2 and v with exact rationals.
    The signed m is unknown; only m**2<=m2_upper is certified.
    """
    if not isinstance(exchange_even_response, bool):
        raise TypeError('exchange_even_response must be an explicit bool')
    d2=rat(delta2)
    if d2 < 0: raise ValueError('delta2>=0')
    lo,hi=reweight_outer(a,u,r)
    r=rat(r)
    eta=F(0) if exchange_even_response else (r-1)/(r+1)
    m2max=eta*eta*hi
    vmin=d2*(1-eta*eta)*lo
    vmax=d2*hi
    return {'eta':eta,'bq_lower':lo,'bq_upper':hi,
            'm2_upper':m2max,'mean_energy_offset_squared_max_MeV2':d2*m2max,
            'conditional_var_lower_MeV2':vmin,'conditional_var_upper_MeV2':vmax}


@dataclass(frozen=True)
class Mat2:
    xx:F
    xy:F
    yy:F


def marked_event_moments(k0,delta,mean_mu,b_mu,mean_count,var_count):
    """Conditional iid *selected* mark N-independent random sum.

    Ordered / arm-tagged pair mark Y=(k0+delta*mu,k0-delta*mu).
    The physical unordered pair must not be inferred from an odd response.
    N>=0 integer RV
    independent of marks, with mean_count>=0 and var_count>=0.
    Returns exact mean vector, covariance and common/contrast projections.
    NOTE delta is positive sqrt(delta2) when working in physical MeV.
    """
    k0,delta,m,b,lam,nu=map(rat,(k0,delta,mean_mu,b_mu,mean_count,var_count))
    if not (-1<=m<=1 and 0<=b<=1 and m*m<=b):
        raise ValueError('unrealizable first/second angular moment')
    if k0 < 0 or delta<0 or lam<0 or nu<0:
        raise ValueError('nonnegative k0, delta, count moments required')
    if delta > k0:
        raise ValueError('kinetic daughter energies must be nonnegative for |mu|<=1')
    frac = lam - (lam.numerator // lam.denominator)
    if nu < frac*(1-frac):
        raise ValueError('integer event count moment infeasible: var below Bernoulli floor')
    x=k0+delta*m; y=k0-delta*m
    v=delta*delta*(b-m*m)
    cov=Mat2(lam*v+nu*x*x, -lam*v+nu*x*y, lam*v+nu*y*y)
    return {'mean':(lam*x,lam*y),'mark_variance':v,'covariance':cov,
            'pair_total_mean':2*lam*k0,
            'pair_total_variance':4*nu*k0*k0,
            'pair_difference_mean':2*lam*delta*m,
            'pair_difference_variance':4*delta*delta*(lam*b+(nu-lam)*m*m),
            'sum_difference_covariance':4*nu*k0*delta*m}


def poisson_cross_covariance(k0, delta2, bq, mean_count):
    """Under *explicit* Poisson N, off-diagonal independent of odd m."""
    k0,d2,b,lam=map(rat,(k0,delta2,bq,mean_count))
    if k0<0 or d2<0 or d2>k0*k0 or not 0<=b<=1 or lam<0:
        raise ValueError('invalid physical Poisson conditional moment inputs')
    return lam*(k0*k0-d2*b)


def physics_gate():
    return dict(kappa=None, R_event=None, heat_rate=None, D_fast_pool=None,
                physical_activation=False,L4=False,production='HOLD',
                detector_q_measured=False,exchange_even_response_verified=False,
                event_count_law_measured=False)
