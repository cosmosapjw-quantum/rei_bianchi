"""Opt-in real-R bound-state anchors from fixed-index self-adjoint pencils.

Research candidate, not an interval or continuum certificate. Coordinates are
R/a0 and E/Eh. The original continued-fraction and continuation APIs are untouched.
Fixed tau is essential: changing the basis with the root variable invalidates
finite-dimensional monotonicity. The returned (k,q) are spectral ordinals, not CF
matching positions. Requires the optional SciPy research dependency.
"""
from __future__ import annotations
from functools import lru_cache
from numbers import Integral
import math
import numpy as np
from scipy.linalg import cholesky, eigh, solve_triangular
from scipy.optimize import brentq
from scipy.special import eval_genlaguerre, gammaln, roots_genlaguerre


class BranchUnresolved(RuntimeError):
    """No admissible bound-state anchor within the explicit numerical budget."""


def _int(x, name, lo=0):
    if isinstance(x, (bool, np.bool_)) or not isinstance(x, Integral) or x < lo:
        raise ValueError(f'{name} must be an integer >= {lo}')
    return int(x)


def _positive(x, name):
    if isinstance(x, (bool, np.bool_)) or not np.isscalar(x) or np.iscomplexobj(x):
        raise ValueError(f'{name} must be real, finite and positive')
    x=float(x)
    if not math.isfinite(x) or x<=0:
        raise ValueError(f'{name} must be real, finite and positive')
    return x


def _state(state):
    if len(state)!=3: raise ValueError('state must be (N,l,abs(m))')
    N,l,m=(_int(x,n) for x,n in zip(state,('N','l','m')))
    if not 0<=m<=l<N: raise ValueError('require 0 <= m <= l < N')
    return N,l,m


def _sym(x): return (x+x.T)*.5


@lru_cache(maxsize=32)
def _basis(m, size):
    # Degree bound: H acting on a degree size-1 polynomial raises it by at most 2.
    # The additional weight (x+4tau)^m is polynomial for integer m.
    x,w=roots_genlaguerre(size+m+5, m)
    j=np.arange(size)
    norms=np.exp(.5*(gammaln(j+1)-gammaln(j+2*m+1)))
    V=np.column_stack([eval_genlaguerre(i,2*m,x) for i in j])*norms
    D=np.column_stack([np.zeros_like(x) if i==0 else -eval_genlaguerre(i-1,2*m+1,x) for i in j])*norms
    DD=np.column_stack([np.zeros_like(x) if i<2 else eval_genlaguerre(i-2,2*m+2,x) for i in j])*norms
    for a in (x,w,V,D,DD): a.setflags(write=False)
    return x,w,V,D,DD


@lru_cache(maxsize=128)
def _pencils(R,m,tau,size,Z1,Z2):
    a=(Z1+Z2)*R; b=(Z2-Z1)*R
    x,w,V,D,DD=_basis(m,size)
    Q=x*(x+4*tau); W=w*(x+4*tau)**m
    HV=-Q[:,None]*DD+(Q-(m+1)*(2*x+4*tau))[:,None]*D
    HV+=((m+1-a/(2*tau))*x+2*tau*(m+1)-m*(m+1)-a)[:,None]*V
    G=V.T@(W[:,None]*V)
    K=V.T@(W[:,None]*HV)
    C=V.T@((W*Q/4)[:,None]*V)  # derivative with respect to w=(p/tau)^2
    asym=float(np.max(abs(K-K.T))/max(1.,float(np.max(abs(K)))))
    if not math.isfinite(asym) or asym>1e-10:
        raise BranchUnresolved(f'radial assembly lost symmetry: {asym}')
    L=cholesky(_sym(G),lower=True)
    def whiten(H):
        T=solve_triangular(L,_sym(H),lower=True)
        return _sym(solve_triangular(L,T.T,lower=True).T)
    radial_constant=whiten(K-C)
    radial_slope=whiten(C)
    # One extra mode is necessary to compute P eta^2 P rather than (P eta P)^2.
    ls=np.arange(m,m+size+1,dtype=float)
    c=np.sqrt(((ls[:-1]+1)**2-m*m)/((2*ls[:-1]+1)*(2*ls[:-1]+3)))
    X=np.diag(c,1)+np.diag(c,-1)
    angular_constant=np.diag(ls[:-1]*(ls[:-1]+1))+b*X[:-1,:-1]
    angular_slope=tau*tau*(np.eye(size)-(X@X)[:-1,:-1])
    for arr in (radial_constant,radial_slope,angular_constant,angular_slope):
        if not np.all(np.isfinite(arr)): raise BranchUnresolved('non-finite pencil')
        arr.setflags(write=False)
    return dict(radial_constant=radial_constant,radial_slope=radial_slope,
                angular_constant=angular_constant,angular_slope=angular_slope,
                radial_symmetry_defect=asym,tau=tau,size=size,R=R,m=m,Z1=Z1,Z2=Z2)


def pencils(*, R, m, tau, size=40, Z1=1., Z2=2.) -> dict:
    """Precompute Hermitian A+wB pencils with fixed basis. Arrays are read-only."""
    R=_positive(R,'R');tau=_positive(tau,'tau')
    Z1=_positive(Z1,'Z1');Z2=_positive(Z2,'Z2')
    m=_int(m,'m');size=_int(size,'size',8)
    if size>128 or m>12: raise ValueError('bounded backend: size<=128, m<=12')
    return dict(_pencils(R,m,tau,size,Z1,Z2))


def _eig(pencil, sector, ordinal, w, vectors=False):
    H=pencil[sector+'_constant']+w*pencil[sector+'_slope']
    ans=eigh(H,eigvals_only=not vectors,subset_by_index=(ordinal,ordinal),driver='evr')
    if not vectors: return float(ans[0])
    ev,V=ans;z=V[:,0];ev=float(ev[0]);r=float(np.linalg.norm(H@z-ev*z))
    relative=r/max(1.,np.linalg.norm(H,ord=np.inf),abs(ev))
    return ev,relative,float(z@pencil[sector+'_slope']@z)


def match_value(pencil: dict, k: int, q: int, w: float) -> float:
    """mu_k(w)+lambda_q(w), strictly increasing in exact finite arithmetic."""
    k=_int(k,'k');q=_int(q,'q');w=_positive(w,'w')
    if max(k,q)>=pencil['size']: raise ValueError('ordinal outside basis')
    return _eig(pencil,'radial',k,w)+_eig(pencil,'angular',q,w)


def solve_indexed(state, R, *, Z1=1., Z2=2., size=40, tau=None, maxiter=100) -> dict:
    """Solve one fixed-basis scalar equation. Basis error is not checked here."""
    N,l,m=_state(state);R=_positive(R,'R');Z1=_positive(Z1,'Z1');Z2=_positive(Z2,'Z2')
    maxiter=_int(maxiter,'maxiter',1)
    tau=(Z1+Z2)*R/(2*N) if tau is None else _positive(tau,'tau')
    pp=pencils(R=R,m=m,tau=tau,size=size,Z1=Z1,Z2=Z2)
    k=N-l-1;q=l-m
    if max(k,q)>=size-2: raise ValueError('basis too small for requested ordinals')
    calls=0
    def fun(w):
        nonlocal calls
        calls+=1
        return match_value(pp,k,q,w)
    lo=.0625;hi=16.;flo=fun(lo);fhi=fun(hi)
    for _ in range(12):
        if flo<0<fhi: break
        if flo>=0:lo*=.25;flo=fun(lo)
        if fhi<=0:hi*=4;fhi=fun(hi)
    else: raise BranchUnresolved('no positive scalar bracket within 12 expansions')
    try:
        w,root=brentq(fun,lo,hi,xtol=2e-13,rtol=1e-14,maxiter=maxiter,full_output=True)
    except (RuntimeError,ValueError) as exc:
        raise BranchUnresolved(f'bounded scalar solve failed: {exc}') from exc
    mu,rr,dr=_eig(pp,'radial',k,w,True)
    lam,ar,da=_eig(pp,'angular',q,w,True)
    f=mu+lam;slope=dr+da
    if not root.converged or not math.isfinite(f) or abs(f)>2e-9 or max(rr,ar)>1e-10 or slope<=0:
        raise BranchUnresolved(f'spectral gate failed: F={f}, residuals={rr,ar}, slope={slope}')
    p=tau*math.sqrt(w)
    return dict(state=[N,l,m],indices=dict(radial=k,angular=q),R=R,Z1=Z1,Z2=Z2,
                p=p,separation_lambda=lam,energy_hartree=-2*p*p/R**2,
                w=w,tau=tau,size=int(size),matching_residual=f,positive_slope=slope,
                eigensystem_relative_residual=max(rr,ar),scalar_evaluations=calls,
                scalar_iterations=int(root.iterations),bracket=[lo,hi],bracket_values=[flo,fhi],
                radial_symmetry_defect=pp['radial_symmetry_defect'],
                energy_root_correction_estimate=abs(2*tau*tau/R**2*f/slope),
                label_authority='FIXED_RADIAL_ANGULAR_STURM_ORDINALS',
                rigorous_interval_certificate=False)


def bound_state(state,R,*,Z1=1.,Z2=2.,sizes=(40,56,72),tau=None,
                energy_tol=2e-10,lambda_tol=2e-9,maxiter=100) -> dict:
    """Return the first nested-basis converged candidate; fail closed at ceiling."""
    N,l,m=_state(state);R=_positive(R,'R');Z1=_positive(Z1,'Z1');Z2=_positive(Z2,'Z2')
    energy_tol=_positive(energy_tol,'energy_tol');lambda_tol=_positive(lambda_tol,'lambda_tol')
    sizes=tuple(_int(s,'size',8) for s in sizes)
    if len(sizes)<2 or any(b<=a for a,b in zip(sizes,sizes[1:])):
        raise ValueError('at least two strictly increasing basis sizes required')
    tau=(Z1+Z2)*R/(2*N) if tau is None else _positive(tau,'tau')
    history=[]
    for size in sizes:
        r=solve_indexed(state,R,Z1=Z1,Z2=Z2,size=size,tau=tau,maxiter=maxiter)
        if history:
            old=history[-1];de=abs(r['energy_hartree']-old['energy_hartree'])
            dl=abs(r['separation_lambda']-old['separation_lambda'])
            if de<=energy_tol*max(1.,abs(r['energy_hartree'])) and dl<=lambda_tol*max(1.,abs(r['separation_lambda'])):
                return {**r,'basis_converged':True,'energy_basis_difference':de,
                        'lambda_basis_difference':dl,'basis_history':history+[r],
                        'classification':'NUMERICALLY_VALIDATED_REAL_ANCHOR_NOT_INTERVAL_CERTIFIED'}
        history.append(r)
    raise BranchUnresolved(f'basis convergence not reached at sizes={sizes}; energies={[x["energy_hartree"] for x in history]}')


def bound_pair(state_a,state_b,R,*,Z1=1.,Z2=2.,sizes=(40,56,72),**kwargs) -> dict:
    """Solve both named states at exactly R using a shared physical basis scale."""
    sa=_state(state_a);sb=_state(state_b)
    if sa==sb:raise ValueError('distinct advertised states required')
    if sa[2]!=sb[2]:raise ValueError('this radial-crossing adapter requires common m')
    R=_positive(R,'R');Z1=_positive(Z1,'Z1');Z2=_positive(Z2,'Z2')
    tau=(Z1+Z2)*R/(2*max(sa[0],sb[0]))
    a=bound_state(sa,R,Z1=Z1,Z2=Z2,sizes=sizes,tau=tau,**kwargs)
    b=bound_state(sb,R,Z1=Z1,Z2=Z2,sizes=sizes,tau=tau,**kwargs)
    z1=np.array([a['p'],a['separation_lambda']]);z2=np.array([b['p'],b['separation_lambda']])
    gap=float(np.linalg.norm((z2-z1)/np.maximum(1.,np.maximum(abs(z1),abs(z2)))))
    if gap<1e-8:raise BranchUnresolved('advertised pair collapsed in joint (p,lambda) space')
    return dict(a=a,b=b,distinct=True,joint_scaled_gap=gap,
                energy_gap=b['energy_hartree']-a['energy_hartree'],
                physical_channel_admitted=False)
