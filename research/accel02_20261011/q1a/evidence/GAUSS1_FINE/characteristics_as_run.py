"""Fixed-covector radiation primitives; no gas solution or source invention."""
from __future__ import annotations
import numpy as np


def geometry_nodes(q_eV, mu0, geometry):
    q, m = np.asarray(q_eV), np.asarray(mu0)
    a, b = geometry['a_rel'], geometry['b']-geometry.get('b_i', 0.)
    if (q.shape != m.shape or not np.isfinite(q).all() or not np.isfinite(m).all()
            or np.any(q<=0) or np.any(abs(m)>1) or not np.isfinite([a,b]).all() or a<=0):
        raise ValueError('CHARACTERISTIC_DOMAIN')
    ratio=np.sqrt((1-m*m)*np.exp(2*b)+m*m*np.exp(-4*b))/a
    return q*ratio, m*np.exp(-2*b)/(a*ratio), ratio


def make_grid(n_energy, n_mu, qmax, qmin=10.):
    if int(n_energy)!=n_energy or int(n_mu)!=n_mu or n_energy<2 or n_mu<1 or not qmax>qmin>0:
        raise ValueError('GRID_DOMAIN')
    edges=np.linspace(np.log(qmin),np.log(qmax),n_energy+1)
    q=np.exp((edges[1:]+edges[:-1])/2)
    mu,wmu=np.polynomial.legendre.leggauss(n_mu)
    return np.repeat(q,n_mu),np.tile(mu,n_energy),np.repeat(np.diff(edges),n_mu)*np.tile(wmu/2,n_energy)


def source_reference(q_eV, mu0, weights, geometry, emissivity, band=(10.,50000.)):
    energy,_,ratio=geometry_nodes(q_eV,mu0,geometry)
    w=np.asarray(weights)
    if w.shape!=energy.shape or not np.isfinite(w).all() or np.any(w<=0):
        raise ValueError('SOURCE_WEIGHT_DOMAIN')
    source=np.zeros_like(energy)
    selected=(energy>=band[0])&(energy<=band[1])
    source[selected]=emissivity.photon_emission_log(energy[selected],geometry['z'])*w[selected]/ratio[selected]**3
    return source


def exponential_step(number, source, kappa_species, dt):
    """Frozen-stage exact continuous-source absorption, kappa in s^-1.

    N and S have the same reference-volume convention. Returned absorption has
    shape(n,3), is species resolved, and closes N1+abs=N0+Sdt. The residence
    integral is stable even where source and sink nearly balance. Values are
    validated; invalid abundances, opacities and steps are not clipped.
    """
    n,s,k=np.asarray(number,dtype=float),np.asarray(source,dtype=float),np.asarray(kappa_species,dtype=float)
    if (n.ndim!=1 or s.shape!=n.shape or k.shape!=(len(n),3) or
        not np.isfinite(n).all() or not np.isfinite(s).all() or not np.isfinite(k).all()
        or np.any(n<0) or np.any(s<0) or np.any(k<0) or not np.isfinite(dt) or dt<0):
        raise ValueError('EXPONENTIAL_STAGE_DOMAIN')
    x=k.sum(axis=1)*dt
    if not np.isfinite(x).all(): raise ValueError('EXPONENTIAL_STAGE_OVERFLOW')
    p1=np.empty_like(x); p2=np.empty_like(x)
    small=x<1e-3; xx=x[small]
    p1[small]=1+xx*(-.5+xx*(1/6+xx*(-1/24+xx*(1/120-xx/720))))
    p2[small]=.5+xx*(-1/6+xx*(1/24+xx*(-1/120+xx*(1/720-xx/5040))))
    xx=x[~small]
    p1[~small]=-np.expm1(-xx)/xx
    p2[~small]=(1-p1[~small])/xx
    out=np.exp(-x)*n+s*dt*p1
    residence=dt*(n*p1+s*dt*p2)
    absorbed=k*residence[:,None]
    if not np.isfinite(out).all() or not np.isfinite(absorbed).all():
        raise ValueError('EXPONENTIAL_STAGE_RESULT_OVERFLOW')
    return dict(number=out,absorbed_by_species=absorbed,source_added=s*dt,integrated_number=residence)
