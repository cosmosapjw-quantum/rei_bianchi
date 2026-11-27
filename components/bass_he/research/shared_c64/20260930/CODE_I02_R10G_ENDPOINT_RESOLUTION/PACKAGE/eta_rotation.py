"""Research-only exact reparameterization of the existing Coulomb Eq.(47) ODE.

Atomic-unit/legacy velocity conventions are inherited explicitly; no author
FORTRAN is imported. This is NOT a new physical trajectory or production policy.
The independent DOP853 auditor uses the full matrix, not the Magnus parity loop.
"""
from __future__ import annotations
from functools import lru_cache
import math
import numpy as np


@lru_cache(maxsize=8)
def operators(l: int):
    m=np.arange(-l,l+1);lp=np.zeros((2*l+1,2*l+1),complex)
    for k,mk in enumerate(m[:-1]):
        lp[k+1,k]=math.sqrt(l*(l+1)-mk*(mk+1))
    lx=(lp+lp.conj().T)/2;lz=np.diag(m.astype(float)).astype(complex)
    w,V=np.linalg.eigh(lx)
    if np.max(abs(w-m))>5e-13:raise ArithmeticError('ANGULAR_BASIS_FAILURE')
    collapse=(abs(m)[None,:]==np.arange(l+1)[:,None]).astype(float)
    for x in (lx,lz,V,collapse):x.flags.writeable=False
    return lx,lz,V,collapse


def velocity(E):
    return np.sqrt(2*np.asarray(E,float)/(27.07*1.836153))


def _inputs(N,l,energies,rhos,R_cut,steps,mass_u,Z1,Z2):
    if type(N) is not int or type(l) is not int or not 1<=l<N:
        raise ValueError('integer 1<=l<N required')
    if type(steps) is not int or steps<4:raise ValueError('integer steps>=4 required')
    scalars=np.asarray([R_cut,mass_u,Z1,Z2],float)
    if not np.all(np.isfinite(scalars)) or np.any(scalars<=0):
        raise ValueError('positive finite cutoff/mass/charges required')
    E,r=np.broadcast_arrays(np.asarray(energies,float),np.asarray(rhos,float))
    E=E.ravel();r=r.ravel()
    if not len(r) or not np.all(np.isfinite(E)) or not np.all(np.isfinite(r)) or np.any(E<=0) or np.any(r<0):
        raise ValueError('finite positive energy and nonnegative rho required')
    v=velocity(E);a=Z1*Z2/(1836.153*mass_u*v*v);b=np.hypot(a,r)
    eps=6*Z1*Z2*(Z1+Z2)**2/(N**3*l*(l+1)*(2*l-1)*(2*l+1)*(2*l+3))
    return E,r,v,a,b,eps


def _probabilities(U,l):
    _,_,V,C=operators(l)
    signed=abs(V.conj().T@U@V)**2
    return (C@signed@C.T)/C.sum(1)[None,None,:]


def eta_rotation_batch(N:int,l:int,energies,rhos,*,R_cut:float,steps:int=256,
                       mass_u:float=.80,Z1:float=1.,Z2:float=2.) -> dict:
    """Return paired-broadcast propagators/probabilities with finite head-on limit.

    R=a+sqrt(a^2+rho^2) cosh(eta), dt/deta=R/v.
    i dA/deta = [(epsilon/v) R^3 Lx^2 - (rho/R) Lz] A.
    Integrates directly in the rotating frame. No endpoint gauge multiplication,
    clipping, renormalization, interpolation, or persisted admission cache.
    """
    E,r,v,a,b,eps=_inputs(N,l,energies,rhos,R_cut,steps,mass_u,Z1,Z2)
    dim=2*l+1;U=np.broadcast_to(np.eye(dim,dtype=complex),(len(r),dim,dim)).copy()
    active=a+b<float(R_cut);ix=np.flatnonzero(active)
    lx,lz,_,_=operators(l)
    if len(ix):
        aa,bb,rr,vv=a[ix],b[ix],r[ix],v[ix]
        bound=np.arccosh((float(R_cut)-aa)/bb)
        h=2./steps;offset=h/(2*math.sqrt(3))
        for parity in (0,1):
            ids=np.arange(parity,dim,2)
            if not len(ids):continue
            X=(lx@lx)[np.ix_(ids,ids)];Z=lz[np.ix_(ids,ids)]
            W=np.broadcast_to(np.eye(len(ids),dtype=complex),(len(ix),len(ids),len(ids))).copy()
            def H(y):
                radius=aa+bb*np.cosh(bound*y)
                return ((bound*eps*radius**3/vv)[:,None,None]*X
                        -(bound*rr/radius)[:,None,None]*Z)
            for k in range(steps):
                mid=-1+(k+.5)*h;H1=H(mid-offset);H2=H(mid+offset)
                K=.5*h*(H1+H2)+1j*math.sqrt(3)*h*h/12*(H1@H2-H2@H1)
                eig,V=np.linalg.eigh(K)
                W=((V*np.exp(-1j*eig)[:,None,:])@V.conj().swapaxes(-1,-2))@W
            U[ix[:,None,None],ids[None,:,None],ids[None,None,:]]=W
    P=_probabilities(U,l)
    return {'U_z':U,'P_abs':P,'entered':active,'steps':steps,
            'method':'ECCENTRIC_ANOMALY_PARITY_MAGNUS4_RESEARCH',
            'unitarity_defect':float(np.max(abs(U.conj().swapaxes(-1,-2)@U-np.eye(dim)))),
            'stochasticity_defect':float(np.max(abs(P.sum(1)-1)))}


def eta_dop853(N,l,energy,rho,*,R_cut,mass_u=.8,Z1=1.,Z2=2.):
    """Full-matrix independent integrator for the derived anomaly ODE, one point.

    Independent integrator != independent physical theory or independent review.
    """
    from scipy.integrate import solve_ivp
    E,r,v,a,b,eps=_inputs(N,l,[energy],[rho],R_cut,4,mass_u,Z1,Z2)
    if a[0]+b[0]>=R_cut:return {'P_abs':np.eye(l+1),'nfev':0,'success':True}
    limit=math.acosh((R_cut-a[0])/b[0]);dim=2*l+1;lx,lz,_,_=operators(l)
    def rhs(eta,flat):
        radius=a[0]+b[0]*math.cosh(eta)
        H=eps*radius**3/v[0]*(lx@lx)-r[0]/radius*lz
        return (-1j*H@flat.reshape(dim,dim)).ravel()
    sol=solve_ivp(rhs,(-limit,limit),np.eye(dim,dtype=complex).ravel(),method='DOP853',rtol=1e-12,atol=1e-14)
    if not sol.success:raise ArithmeticError('ANOMALY_DOP853_FAILURE: '+sol.message)
    U=sol.y[:,-1].reshape(dim,dim)
    return {'P_abs':_probabilities(U[None],l)[0],'nfev':sol.nfev,'success':True,
            'unitarity_defect':float(np.max(abs(U.conj().T@U-np.eye(dim))))}
