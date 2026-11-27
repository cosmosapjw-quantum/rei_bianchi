"""Finite-angular, finite-radial original screened DtN via scaled Riccati.

Real E=49/200 Hartree. Increasing-r derivative Z=U' U^-1.
The physical screen is set to zero beyond `outer` for THIS numeric solve.
Delta=Z-Z_C is integrated directly as Delta=(3e-23*strength)*Y.
No all-angular truncation or floating-point interval certificate is claimed.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from time import perf_counter
import math
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import gammaln, lpmv
from .phys63_lap_contract import source_guard

B=27.0
K=0.7
SCREEN_SCALE=3e-23

@lru_cache(maxsize=512)
def central_impedance(ell:int, radius:float, dps:int=55)->complex:
    """Independent high precision H=G+iF, exact DLMF 33.4 recurrence."""
    import mpmath as mp
    with mp.workdps(dps):
        k=mp.mpf(7)/10; eta=-1/k; rho=k*mp.mpf(str(radius))
        H=lambda l:mp.coulombg(l,eta,rho)+1j*mp.coulombf(l,eta,rho)
        h=H(ell)
        hp=((ell+1)/rho+eta/(ell+1))*h-mp.sqrt(1+(eta/(ell+1))**2)*H(ell+1)
        return complex(k*hp/h)

class AngularScreen:
    """Direct original angular 2S, scaled by 3e-23, without multipole closure."""
    def __init__(self,ells:tuple[int,...],m:int,nodes:int=128):
        if (not ells or len(set(ells))!=len(ells) or type(m) is not int
            or any(type(l) is not int or not abs(m)<=l<=64 for l in ells)):
            raise ValueError('distinct integer ell in |m|..64 required')
        if type(nodes) is not int or not 64<=nodes<=512:
            raise ValueError('angular quadrature nodes 64..512')
        self.ells=ells;self.m=m
        self.mu,self.weights=np.polynomial.legendre.leggauss(nodes)
        ma=abs(m)
        self.basis=np.array([np.sqrt((2*l+1)/2*np.exp(gammaln(l-ma+1)-gammaln(l+ma+1)))*lpmv(ma,l,self.mu) for l in ells])
    def scaled(self,r:float)->np.ndarray:
        sep=.7
        s=np.sqrt(r*r+sep*sep-2*r*sep*self.mu)
        v=2*(1+1/s)*np.exp(-2*s)/SCREEN_SCALE
        A=self.basis*np.sqrt(self.weights*v)
        return A@A.T

def solve_response(source:str|Path,ells:tuple[int,...]=(20,21),m:int=0,
                   outer:float=39.0,nodes:int=128,rtol:float=2e-11,
                   strength:float=1.0,nonlinear:bool=True)->dict:
    """Finite original Galerkin response, full nonlinear Riccati equation.

    strength=1 is physical. Other strengths are verification controls only.
    The nonlinear delta² term is implemented, but is beneath f64 resolution
    relative to the physical response and cannot be claimed measured.
    """
    digest=source_guard(source)
    if not math.isfinite(outer) or not B<outer<=55:
        raise ValueError('finite outer radius in (27,55]')
    if not math.isfinite(rtol) or not 1e-13<=rtol<=1e-7:
        raise ValueError('rtol in [1e-13,1e-7]')
    if not math.isfinite(strength) or not 0<=strength<=1e22:
        raise ValueError('nonnegative bounded verification strength')
    angular=AngularScreen(ells,m,nodes);n=len(ells)
    ll=np.array([l*(l+1) for l in ells],dtype=float)
    scale=SCREEN_SCALE*strength
    zT=np.array([central_impedance(l,float(outer)) for l in ells])
    # log profiles included for a distinct numerical Born quadrature path.
    start=np.concatenate([zT,np.zeros(n,dtype=complex),np.zeros(n*n,dtype=complex)])
    def rhs(r,y):
        z=y[:n];Y=y[2*n:].reshape(n,n)
        dz=-(K*K+2/r-ll/r**2)-z*z
        dY=-z[:,None]*Y-Y*z[None,:]
        if strength>0:
            dY=dY-angular.scaled(r)
            if nonlinear:dY=dY-scale*(Y@Y)
        return np.concatenate([dz,z,dY.ravel()])
    begin=perf_counter()
    sol=solve_ivp(rhs,(outer,B),start,method='DOP853',rtol=rtol,atol=rtol*1e-3,dense_output=True,max_step=.35)
    elapsed=perf_counter()-begin
    if not sol.success or not np.isfinite(sol.y).all():
        raise ArithmeticError('Riccati integration failed: '+sol.message)
    last=sol.y[:,-1];Y=last[2*n:].reshape(n,n)
    return {'delta':scale*Y,'scaled_delta':Y,'central_z':last[:n],
            'solution':sol,'ells':ells,'m':m,'outer':outer,'nodes':nodes,
            'nfev':sol.nfev,'seconds':elapsed,'strength':strength,
            'nonlinear_equation':nonlinear,'source_sha256':digest,
            'status':'FINITE_ANGULAR_RADIAL_NONCERTIFYING',
            'physical_nonlinear_remainder_resolved':False if strength==1 else None}

def born_from_central_path(result:dict,radial_nodes:int=80)->np.ndarray:
    """Separate radial quadrature of first Born on same finite interval.

    Central profiles come from Riccati w'=z, not an independent special
    function oracle; the driver also compares a stored prior mpmath oracle.
    """
    if type(radial_nodes) is not int or not 12<=radial_nodes<=256:
        raise ValueError('radial nodes 12..256')
    ells=result['ells'];n=len(ells);T=result['outer'];sol=result['solution']
    angular=AngularScreen(ells,result['m'],result['nodes'])
    x,w=np.polynomial.legendre.leggauss(radial_nodes)
    r=B+(T-B)*(x+1)/2; w=w*(T-B)/2
    logB=sol.sol(B)[n:2*n]
    D=np.zeros((n,n),dtype=complex)
    for ri,wi in zip(r,w):
        p=np.exp(sol.sol(ri)[n:2*n]-logB)
        D+=wi*(p[:,None]*angular.scaled(ri)*p[None,:])
    return SCREEN_SCALE*result['strength']*D

def direct_fundamental_control(source:str|Path,ells=(0,1),m=0,outer=33.,
                               strength=1e20,nodes=128,rtol=2e-11)->dict:
    """Independent original second-order U,U' equation at amplified screen.

    This control is deliberately NONPHYSICAL. It makes nonlinear response
    resolvable and tests matrix/sign implementation without tiny subtraction.
    """
    source_guard(source);angular=AngularScreen(ells,m,nodes);n=len(ells)
    if not B<outer<=40 or not 1e16<=strength<=1e21:
        raise ValueError('bounded amplified verification only')
    ll=np.array([l*(l+1) for l in ells],dtype=float)
    zT=np.array([central_impedance(l,float(outer)) for l in ells])
    start=np.concatenate([np.eye(n,dtype=complex).ravel(),np.diag(zT).ravel()])
    def rhs(r,y):
        U=y[:n*n].reshape(n,n);Up=y[n*n:].reshape(n,n)
        Q=np.diag(K*K+2/r-ll/r**2)+strength*SCREEN_SCALE*angular.scaled(r)
        return np.concatenate([Up.ravel(),(-Q@U).ravel()])
    sol=solve_ivp(rhs,(outer,B),start,method='DOP853',rtol=rtol,atol=rtol*1e-3,max_step=.1)
    if not sol.success:raise ArithmeticError(sol.message)
    U=sol.y[:n*n,-1].reshape(n,n);Up=sol.y[n*n:,-1].reshape(n,n)
    Z=np.linalg.solve(U.T,Up.T).T
    invU=np.linalg.inv(U)
    flux=(Z-Z.conj().T)/(2j)
    transported=invU.conj().T@np.diag(zT.imag)@invU
    return {'Z':Z,'flux_error':float(np.linalg.norm(flux-transported)),
            'nfev':sol.nfev,'status':'MANUFACTURED_AMPLIFIED_SCREEN_CONTROL'}
