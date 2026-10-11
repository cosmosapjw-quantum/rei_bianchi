"""Finite source/redshift and positive fixed-bath absorption; no gas solve."""
from functools import lru_cache
import math
from pathlib import Path
import sys
import numpy as np
from scipy.optimize import brentq
from scipy.special import logsumexp

Q1B=Path(__file__).resolve().parent.parent/'q1b'
sys.path.insert(0,str(Q1B))
from reconstruction import reconstruct, opacity_moments

@lru_cache(maxsize=4)
def gauss(order):return np.polynomial.legendre.leggauss(order)

def source_integrals(source, logR, ta, tb, panels, order):
    """SN,SQ integration plus independent injected energy and radiation work.

    source(t) is (angle,2): SN,SQ. Energy unit here is eV, not erg.
    """
    x,w=gauss(order);rows=[]
    rb=math.exp(logR(tb))
    for left,right in zip(panels[:-1],panels[1:]):
        if not ta<=left<right<=tb:raise ValueError('ENTRY_TIME_PANEL_DOMAIN')
        terms=[]
        for u,v in zip(x,w):
            t=left+(u+1)*(right-left)/2
            s=np.asarray(source(float(t)),float);lr=logR(float(t));r=math.exp(lr)
            if s.ndim!=2 or s.shape[1]!=2 or np.any(s<0) or not np.isfinite(s).all():
                raise ValueError('ENTRY_SOURCE_DOMAIN')
            delta_r=rb*math.expm1(lr-logR(tb))
            terms.append(np.stack([s[:,0],s[:,1],r*s[:,1],delta_r*s[:,1]],axis=1)*v*(right-left)/2)
        rows.append(np.sum(terms,axis=0))
    return np.sum(rows,axis=0)

def incident(N,U,logra,logrb,integrals):
    N,U=np.asarray(N,float),np.asarray(U,float)
    ra,rb=math.exp(logra),math.exp(logrb)
    outN=N+integrals[:,0];outQ=U/ra+integrals[:,1]
    delta_r=rb*math.expm1(logra-logrb)
    return outN,rb*outQ,delta_r*U/ra+integrals[:,3]

def fit_positive(N,U,R,a,b,order):
    """Match authoritative N/U without changing target or using a photon seed."""
    cell=reconstruct(N,U,R,a,b)
    if cell.status in ('EMPTY','ZERO_WIDTH_EMPTY'):
        return np.array([]),np.array([]),{'empty':True}
    if cell.status!='INTERIOR':raise ValueError('ENTRY_STRICT_CONE_REQUIRED')
    # Invoke the existing coordinate admission path, without a native call.
    guard=opacity_moments(cell,lambda q:np.ones_like(q),orders=(64,128),rtol=1e-7)
    x,w=gauss(order);v=(x+1)/2;w=w/2
    logq=cell.quantile_log(v)
    dq=a*np.expm1(logq);xi=dq/(b-a);q=a+dq
    target=(cell.mean_q-a)/(b-a)
    if not xi.min()<target<xi.max():raise ValueError('ENTRY_MEAN_OUTSIDE_NODE_CONVEX_HULL')
    def weights(eta):
        lw=np.log(w)+eta*xi
        return np.exp(lw-logsumexp(lw))
    def f(eta):return float(weights(eta)@xi)-target
    lo,hi=-1.,1.
    for expansions in range(41):
        if f(lo)<=0<=f(hi):break
        if expansions==40:raise ValueError('ENTRY_TILT_BRACKET_CAP')
        lo*=2;hi*=2
    eta,info=brentq(f,lo,hi,xtol=2e-13,rtol=1e-14,maxiter=160,full_output=True)
    p=N*weights(eta)
    nr=abs(math.fsum(p)-N)/N
    qr=abs(math.fsum(q*p)-U/R)/(U/R)
    mr=abs(float((p/N)@xi)-target)
    if nr>1e-12 or qr>1e-12 or mr>1e-7 or np.any(p<=0) or not np.isfinite(p).all():
        raise ArithmeticError('ENTRY_POSITIVE_MOMENT_FIT_FAILED')
    return q,p,{'eta':eta,'iterations':info.iterations,'expansions':expansions,
        'N_residual':nr,'Q_residual':qr,'cell_mean_residual':mr,
        'coordinate_indicator':guard['float_q_coordinate_indicator'],
        'target_N':N,'target_U':U,'target_mean':cell.mean_q,'target_cell_fraction':target,
        'N_U_to_mean_rounding':(cell.mean_q*R*N-U)/U}

def attenuate(p,kappa,h):
    """Same positive nodes define survival and species-resolved absorption."""
    p=np.asarray(p,float);kappa=np.asarray(kappa,float)
    if kappa.shape!=(len(p),3) or np.any(kappa<0) or not np.isfinite(kappa).all() or h<0:
        raise ValueError('ENTRY_ABSORPTION_DOMAIN')
    total=kappa.sum(axis=1);tau=h*total
    if not np.isfinite(tau).all():raise ArithmeticError('ENTRY_UNRESOLVED_OPACITY_PRODUCT')
    survive=p/(1+tau);fraction=tau/(1+tau)
    shares=np.divide(kappa,total[:,None],out=np.zeros_like(kappa),where=total[:,None]!=0)
    absorbed=p[:,None]*fraction[:,None]*shares
    if np.any(survive<0) or np.any(absorbed<0):raise ArithmeticError('ENTRY_NEGATIVE_WEIGHT')
    residual=abs(survive+absorbed.sum(axis=1)-p)
    if np.any(residual>1e-12*p):raise ArithmeticError('ENTRY_POINTWISE_NUMBER_PAIRING')
    return survive,absorbed
