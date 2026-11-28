"""Order-resolved original screened Riccati response in atomic coordinates.

Finite angular Galerkin + finite radial [27,T] ONLY; original screen is
zero outside T. Each coefficient is integrated on its own scale, so D2
is not obtained by subtracting two approximately equal D1-sized numbers.
Numerical coefficients are not rigorous all-angular error certificates.
"""
from __future__ import annotations
from pathlib import Path
from time import perf_counter
import math
import numpy as np
from scipy.integrate import solve_ivp
from .phys63_lap_contract import source_guard
from .phys63_scaled_riccati import B, K, SCREEN_SCALE, AngularScreen, central_impedance


def ordered_sources(coefficients: np.ndarray, potential: np.ndarray) -> np.ndarray:
    """Order n source is sum_{j=1}^{n-1} Y_j Y_{n-j}; never commute matrices."""
    c=np.asarray(coefficients,dtype=complex)
    w=np.asarray(potential,dtype=complex)
    if c.ndim!=3 or c.shape[0]<1 or c.shape[1]!=c.shape[2] or w.shape!=c.shape[1:]:
        raise ValueError('coefficient stack and square potential required')
    out=np.zeros_like(c);out[0]=w
    for n in range(1,len(c)):
        for j in range(n):out[n]+=c[j]@c[n-1-j]
    return out


def solve_orders(source: str|Path, ells: tuple[int,...]=(20,21), m: int=0,
                 outer: float=39., orders: int=3, nodes: int=128,
                 rtol: float=2e-11, max_step: float=.25) -> dict:
    """Solve exact triangular Born hierarchy with terminal Y_n(T)=0.

    The arbitrary coupling is lambda in Delta=sum lambda**n Y_n.
    Physical contributions use lambda=SCREEN_SCALE, not a fitted strength.
    The independently estimated orders do not make their sum exact.
    """
    digest=source_guard(source)
    if type(orders) is not int or not 1<=orders<=5:
        raise ValueError('orders must be integer 1..5')
    if not math.isfinite(outer) or not B<outer<=55:
        raise ValueError('outer must be in (27,55]')
    if not math.isfinite(rtol) or not 1e-13<=rtol<=1e-7:
        raise ValueError('rtol must be in [1e-13,1e-7]')
    if not math.isfinite(max_step) or not .02<=max_step<=.5:
        raise ValueError('max_step must be in [.02,.5]')
    angular=AngularScreen(tuple(ells),m,nodes);ells=angular.ells;n=len(ells)
    ll=np.array([l*(l+1) for l in ells],float)
    start=np.zeros(2*n+orders*n*n,complex)
    begin=perf_counter()
    start[:n]=[central_impedance(l,float(outer)) for l in ells]
    def rhs(r,state):
        z=state[:n];c=state[2*n:].reshape(orders,n,n)
        s=ordered_sources(c,angular.scaled(r))
        dc=-(z[None,:,None]+z[None,None,:])*c-s
        dz=-(K*K+2/r-ll/r**2)-z*z
        return np.concatenate((dz,z,dc.ravel()))
    sol=solve_ivp(rhs,(float(outer),B),start,method='DOP853',rtol=rtol,
                  atol=rtol*1e-3,dense_output=True,max_step=max_step)
    if not sol.success or not np.isfinite(sol.y).all():
        raise ArithmeticError('Born hierarchy failed: '+sol.message)
    c=sol.y[2*n:,-1].reshape(orders,n,n).copy()
    return {'coefficients':c,'contributions':np.array([SCREEN_SCALE**(j+1)*a for j,a in enumerate(c)]),
            'central_z':sol.y[:n,-1].copy(),'solution':sol,'ells':ells,'m':m,
            'outer':float(outer),'nodes':nodes,'orders':orders,'rtol':rtol,
            'max_step':max_step,'seconds':perf_counter()-begin,'nfev':sol.nfev,
            'source_sha256':digest,'status':'FINITE_ANGULAR_RADIAL_NUMERICAL_TAYLOR_COEFFICIENTS',
            'full_nonlinear_remainder_certified':False,
            'spatial_and_roundoff_error_certified':False}


def coefficient_quadrature(result: dict, order: int=2, radial_nodes: int=80) -> np.ndarray:
    """Independent quadrature of a coefficient source using dense ODE profiles.

    This checks time stepping versus quadrature, not independence of the
    Coulomb profile/source implementation. Complex transpose, no conjugate.
    """
    if type(order) is not int or not 1<=order<=result['orders']:
        raise ValueError('coefficient order not available')
    if type(radial_nodes) is not int or not 16<=radial_nodes<=256:
        raise ValueError('quadrature nodes must be in 16..256')
    ells=result['ells'];n=len(ells);T=result['outer'];sol=result['solution']
    angular=AngularScreen(ells,result['m'],result['nodes'])
    x,w=np.polynomial.legendre.leggauss(radial_nodes)
    radii=B+(T-B)*(x+1)/2;weights=w*(T-B)/2
    logB=sol.sol(B)[n:2*n];value=np.zeros((n,n),complex)
    for r,weight in zip(radii,weights):
        state=sol.sol(r);p=np.exp(state[n:2*n]-logB)
        c=state[2*n:].reshape(result['orders'],n,n)
        term=ordered_sources(c,angular.scaled(r))[order-1]
        value+=weight*p[:,None]*term*p[None,:]
    return value


def series_delta(result: dict, strength: float=1., upto: int|None=None) -> np.ndarray:
    """Reconstruct for a specified potential multiplier; nonunit is a control."""
    if not math.isfinite(strength) or not 0<=strength<=1e22:
        raise ValueError('strength must be finite in [0,1e22]')
    upto=result['orders'] if upto is None else upto
    if type(upto) is not int or not 1<=upto<=result['orders']:
        raise ValueError('requested series order unavailable')
    return sum(((SCREEN_SCALE*strength)**(j+1)*result['coefficients'][j]
                for j in range(upto)),np.zeros_like(result['coefficients'][0]))


def summary(result: dict) -> dict:
    """JSON-safe result; all coefficient matrices remain in NPZ output."""
    d={k:result[k] for k in ('ells','m','outer','nodes','orders','rtol','max_step',
                           'seconds','nfev','source_sha256','status',
                           'full_nonlinear_remainder_certified','spatial_and_roundoff_error_certified')}
    target=(result['ells'].index(21),result['ells'].index(20)) if 20 in result['ells'] and 21 in result['ells'] else (0,0)
    d['reported_indices']=list(target)
    d['terms']=[{'order':j+1,'coefficient_entry':[float(c[target].real),float(c[target].imag)],
                 'physical_entry':[float(result['contributions'][j][target].real),float(result['contributions'][j][target].imag)],
                 'coefficient_frobenius':float(np.linalg.norm(c)),
                 'transpose_symmetry_defect':float(np.linalg.norm(c-c.T)/max(np.linalg.norm(c),1e-300))}
                for j,c in enumerate(result['coefficients'])]
    return d
