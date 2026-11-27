# Derived from immutable B1 optical.py; changes: namespace, scaled exact origin,
# tested l<=64, and explicit normalization metadata. Historical source preserved.
"""Reference scattering for a declared finite-range optical radial operator.

This is not a physical He++/H source table. Width columns are nonnegative
unassigned loss reservoirs. The free outer boundary is part of the supplied
model, never an automatic truncation of a Coulomb/polarization tail.

Dimensionless energy unit: E0=hbar**2/(2*mu*L**2). Widths are Gamma/E0,
where H_opt=H_real-i*Gamma/2 and Gamma=hbar*A for a specified decay model.
"""
from __future__ import annotations
import hashlib
import json
import math
import numbers
import warnings
from typing import Any, Sequence

import numpy as np
from scipy.integrate import IntegrationWarning, quad, solve_ivp
from scipy.special import hyp0f1, spherical_jn, spherical_yn

class ContractError(ValueError):
    """Malformed or unsupported mathematical model/operation."""
class NumericalFailure(RuntimeError):
    """Execution or floating-point consistency failed; no result is approved."""


def _number(x: Any, name: str, *, positive: bool=False) -> float:
    if isinstance(x,(bool,np.bool_)) or not isinstance(x,numbers.Real):
        raise ContractError(f'{name}: finite real numeric input required')
    y=float(x)
    if not math.isfinite(y) or (positive and y<=0):
        raise ContractError(f'{name}: finite'+(' positive' if positive else '')+' value required')
    return y


def _checked(z: Any, name: str) -> None:
    if not np.all(np.isfinite(z)):
        raise NumericalFailure(f'{name}: nonfinite arithmetic')


def _regular(q2: complex, ell: int, x: float, anchor: float) -> tuple[complex,complex]:
    """Regular solution divided by anchor**(ell+1), never forming that power.

    Only the first constant-potential cell is covered. This is a normalization
    identity, not a modification of the operator or a small-radius truncation.
    """
    b=ell+1.5
    ratio=x/anchor
    z=-q2*x*x/4
    f=hyp0f1(b,z); fp=hyp0f1(b+1,z)
    power=ratio**(ell+1)
    u=power*f
    du=(ell+1)/anchor*ratio**ell*f-q2*x*power*fp/(2*b)
    _checked((u,du),'scaled origin solution')
    return complex(u),complex(du)


def _array(x: Any, name: str, ndim: int) -> np.ndarray:
    try:
        # Do not silently discard imaginary parts or coerce strings/bools.
        a=np.asarray(x)
        if a.dtype.kind not in 'iuf' or a.ndim!=ndim:raise ValueError(name)
        a=np.asarray(x,dtype=np.float64)
    except (ValueError,TypeError,OverflowError) as e:
        raise ContractError(f'{name}: finite {ndim}D real array required') from e
    if not np.all(np.isfinite(a)):raise ContractError(f'{name}: nonfinite input')
    return a


def solve_partial_wave(energy: float, ell: int, edges: Sequence[float],
                       potential: Sequence[float], widths: Sequence[Sequence[float]],
                       *, rtol: float=2e-11, atol: float=2e-13,
                       max_nfev: int=100000) -> dict[str,Any]:
    """Solve one l for a *specified* piecewise constant finite-range operator.

    Positive reservoir flux, rather than 1-|S|², is the primary loss estimator.
    The first cell has an exact regular hypergeometric solution and quadrature;
    later cells use DOP853 and integrate the nonnegative dwelling density.
    Wavefunction and accumulated flux are rescaled together at shell boundaries.
    No phase shifts, temperatures, asymptotic tails or physical widths are fitted.
    """
    energy=_number(energy,'energy',positive=True)
    if isinstance(ell,(bool,np.bool_)) or not isinstance(ell,numbers.Integral) or not 0<=ell<=64:
        raise ContractError('ell: integer in supported reference range 0..64 required')
    ell=int(ell)
    rtol=_number(rtol,'rtol',positive=True);atol=_number(atol,'atol',positive=True)
    if not 1e-13<=rtol<=1e-4 or not 1e-16<=atol<=1e-5:
        raise ContractError('unsupported binary64 tolerance range')
    if isinstance(max_nfev,bool) or not isinstance(max_nfev,numbers.Integral) or max_nfev<1:
        raise ContractError('max_nfev: positive integer required')
    x=_array(edges,'edges',1);v=_array(potential,'potential',1);g=_array(widths,'widths',2)
    n=len(v)
    if not 1<=n<=512 or len(x)!=n+1 or x[0]!=0 or np.any(np.diff(x)<=0):
        raise ContractError('edges: start at zero and strictly increase; one interval per potential')
    if g.shape[0]!=n or not 1<=g.shape[1]<=32 or np.any(g<0):
        raise ContractError('widths: nonnegative (shell, reservoir) matrix required')
    total_g=np.array([math.fsum(row) for row in g],dtype=float)
    _checked(total_g,'total widths')
    model={'energy':energy,'edges':x.tolist(),'potential':v.tolist(),'widths':g.tolist(),
           'outer':'exactly_free','origin':'regular','width_convention':'H_real-i*Gamma/2'}
    digest=hashlib.sha256(json.dumps(model,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    q2=complex(energy-v[0],total_g[0]/2)
    u,p=_regular(q2,ell,float(x[1]),float(x[1]))
    scale=max(abs(u),abs(p))
    if not math.isfinite(scale) or scale<1e-140 or scale>1e140:
        raise NumericalFailure('initial normalization outside supported range')
    quad_error=0.;evaluations=0
    if total_g[0]>0:
        def density(r):
            a,_=_regular(q2,ell,r,float(x[1]))
            return abs(a/scale)**2
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error',IntegrationWarning)
                dwell,quad_error=quad(density,0,float(x[1]),epsabs=atol,epsrel=rtol,limit=200)
        except (IntegrationWarning,ValueError,OverflowError) as e:
            raise NumericalFailure('first-cell density quadrature failed') from e
        if not math.isfinite(dwell) or dwell<=0:raise NumericalFailure('nonpositive initial dwelling integral')
        J=g[0]*dwell
    else:
        J=np.zeros(g.shape[1],dtype=float)
    u/=scale;p/=scale
    scales=[scale]
    for j in range(1,n):
        q2=complex(energy-v[j],total_g[j]/2)
        left=float(x[j]);right=float(x[j+1])
        def rhs(r,y):
            nonlocal evaluations
            evaluations+=1
            if evaluations>max_nfev:raise NumericalFailure('NFEV_BUDGET_EXCEEDED')
            a=complex(y[0],y[1]);b=complex(y[2],y[3])
            dp=-(q2-ell*(ell+1)/(r*r))*a
            return (b.real,b.imag,dp.real,dp.imag,abs(a)**2)
        y0=(u.real,u.imag,p.real,p.imag,0.)
        # Resolve oscillatory structure; coefficients are constant on each shell.
        frequency=math.sqrt(abs(q2))+math.sqrt(ell*(ell+1))/left
        max_step=min((right-left)/8,.4/max(1.,frequency))
        try:
            with np.errstate(over='raise',invalid='raise',divide='raise'):
                sol=solve_ivp(rhs,(left,right),y0,method='DOP853',rtol=rtol,atol=atol,max_step=max_step)
        except (FloatingPointError,OverflowError,ValueError) as e:
            raise NumericalFailure(f'radial propagation failed in shell {j}') from e
        if not sol.success:raise NumericalFailure(f'ODE_FAILED: {sol.message}')
        y=sol.y[:,-1];_checked(y,'radial state')
        u=complex(y[0],y[1]);p=complex(y[2],y[3]);dwell=float(y[4])
        if dwell<=0:raise NumericalFailure('nonpositive propagated dwelling integral')
        scale=max(abs(u),abs(p))
        if not math.isfinite(scale) or not 1e-140<scale<1e140:
            raise NumericalFailure('wavefunction rescaling outside supported range')
        J=(J+g[j]*dwell)/(scale*scale)
        _checked(J,'scaled loss integrals')
        u/=scale;p/=scale;scales.append(scale)
    k=math.sqrt(energy);z=k*float(x[-1])
    jhat=z*spherical_jn(ell,z);nhat=z*spherical_yn(ell,z)
    dj=k*(spherical_jn(ell,z)+z*spherical_jn(ell,z,derivative=True))
    dn=k*(spherical_yn(ell,z)+z*spherical_yn(ell,z,derivative=True))
    _checked((jhat,nhat,dj,dn),'outer basis')
    alpha=(u*dn-p*nhat)/k;beta=(jhat*p-dj*u)/k
    den=alpha+1j*beta
    if abs(den)<1e-140 or not math.isfinite(abs(den)):raise NumericalFailure('incoming amplitude out of range')
    S=(alpha-1j*beta)/den
    # Pj = 2 J/(k |den|^2). Never square a possibly huge incoming amplitude.
    Pj=np.zeros_like(J)
    for index,integral in enumerate(J):
        if integral>0:
            logp=math.log(2.)+math.log(float(integral))-math.log(k)-2*math.log(float(abs(den)))
            try:Pj[index]=math.exp(logp)
            except OverflowError as exc:raise NumericalFailure('loss logarithm overflow') from exc
    _checked(Pj,'loss probabilities')
    if np.any((np.max(g,axis=0)>0)&(Pj==0)):
        raise NumericalFailure('positive loss underflowed; no zero-source substitution')
    P=math.fsum(Pj.tolist())
    subtraction=1-abs(S)**2
    mismatch=abs(P-subtraction)
    tolerance=max(200*(rtol+atol),1e-10)
    if P<0 or P>1+tolerance or mismatch>tolerance:
        raise NumericalFailure('OPTICAL_FLUX_CONSISTENCY_FAILED')
    sig=math.pi*(2*ell+1)*P/energy
    if not math.isfinite(sig) or (P>0 and sig==0):raise NumericalFailure('partial cross-section arithmetic out of range')
    return {'schema':'bass-he.optical-partial-wave.v1','data_kind':'DECLARED_OPTICAL_MODEL_PARTIAL_WAVE',
            'model_sha256':digest,'model':model,'ell':ell,'energy_over_E0':energy,'S':[S.real,S.imag],
            'loss_probability':P,'component_loss_probabilities':Pj.tolist(),
            'loss_formula':'positive_flux_integral','loss_by_subtraction':subtraction,
            'flux_identity_absolute_defect':mismatch,'flux_acceptance_atol':tolerance,
            'sigma_partial_over_L2':sig,'nfev':evaluations,
            'first_cell_quad_error_estimate':quad_error,'rescaling_factors':scales,
            'origin_normalization':'u divided by first_edge**(ell+1), power never formed',
            'incoming_normalization':'positive flux via log incoming modulus; square never formed',
            'supported_l_max':64,
            'rtol':rtol,'atol':atol,'arithmetic':'binary64/complex128',
            'outer_boundary':'exactly_free_beyond_last_edge_by_model_definition',
            'source_widths_are_decay_rates':False,'width_unit':'Gamma/E0; Gamma=hbar*A only for a supplied physical decay model',
            'loss_attribution':'UNASSIGNED_OPTICAL_RESERVOIRS',
            'physical_source_admitted':False,'RCT_cross_section':None,'photon_energy_moment':None,
            'physical_uncertainty':None,'rigorous_numerical_enclosure':False}


def partial_sum(results: Sequence[dict[str,Any]]) -> dict[str,Any]:
    """Assemble computed partial waves, never silently complete the l tail."""
    if not results or not all(isinstance(r,dict) and r.get('schema')=='bass-he.optical-partial-wave.v1' for r in results):
        raise ContractError('nonempty optical partial-wave results required')
    ls=[r['ell'] for r in results]
    if len(set(ls))!=len(ls):raise ContractError('duplicate partial waves')
    if len({r['model_sha256'] for r in results})!=1:raise ContractError('different operators/energies cannot be summed')
    return {'schema':'bass-he.optical-partial-sum.v1','ell_values':sorted(ls),
            'sigma_computed_over_L2':math.fsum(r['sigma_partial_over_L2'] for r in results),
            'full_cross_section':None,'l_tail_bound':None,'RCT_cross_section':None,
            'physical_source_admitted':False,'model_sha256':results[0]['model_sha256']}


def physical_scales(length_m: float,reduced_mass_kg: float,hbar_J_s: float) -> dict[str,float]:
    """Explicit scale only, not atomic-mass or isotope admission."""
    L=_number(length_m,'length_m',positive=True);mu=_number(reduced_mass_kg,'reduced_mass_kg',positive=True)
    hb=_number(hbar_J_s,'hbar_J_s',positive=True)
    try:E=hb*hb/(2*mu*L*L);area=L*L
    except (ZeroDivisionError,OverflowError) as e:raise NumericalFailure('scale arithmetic failed') from e
    if E<=0 or area<=0 or not math.isfinite(E+area):raise NumericalFailure('scale outside binary64 range')
    return {'energy_J':E,'area_m2':area,'time_s':hb/E}
