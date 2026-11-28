"""Longer radial endpoints with complete coefficient-state continuation.

Reuses unchanged PR63/64 angular source, Coulomb normalization and ordered
matrix recurrence. Only endpoint extension and explicit join are new.
Computed coefficients remain noncertifying finite angular/radial numerics.
"""
from __future__ import annotations
import math
from pathlib import Path
from time import perf_counter
import numpy as np
from scipy.integrate import solve_ivp
from .phys63_scaled_riccati import AngularScreen,central_impedance,B,K,SCREEN_SCALE
from .phys64_born_hierarchy import ordered_sources
from .phys66_radial_budget import certificate

class JoinedPath:
    def __init__(self,segments): self.segments=segments
    def sol(self,r):
        if np.ndim(r):return np.column_stack([self.sol(float(t)) for t in r])
        for low,high,s in self.segments:
            if low-1e-12<=r<=high+1e-12:return s.sol(float(r))
        raise ValueError('outside integrated radial interval')

def solve_endpoint(source:str|Path,ells:tuple=(20,21),m:int=0,outer:float=65.,
                   join:float=39.,orders:int=3,nodes:int=128,
                   rtol:float=2e-11,max_step:float=.25)->dict:
    if any(isinstance(x,bool) or not math.isfinite(x) for x in (outer,join,rtol,max_step)):
        raise ValueError('finite real numerical integration parameters required')
    if not B<join<outer<=80:raise ValueError('require 27<join<outer<=80')
    if type(orders) is not int or not 1<=orders<=5:raise ValueError('orders1..5')
    if not 1e-13<=rtol<=1e-7 or not .02<=max_step<=.5:raise ValueError('solver precision contract')
    angular=AngularScreen(tuple(ells),m,nodes);ells=angular.ells;n=len(ells)
    bounds=certificate(source,max(ells),str(outer),orders)
    lam=np.array([l*(l+1) for l in ells],float)
    begin=perf_counter()
    state=np.zeros(2*n+orders*n*n,complex)
    state[:n]=[central_impedance(l,float(outer)) for l in ells]
    def rhs(r,y):
        z=y[:n];co=y[2*n:].reshape(orders,n,n)
        dc=-(z[None,:,None]+z[None,None,:])*co-ordered_sources(co,angular.scaled(r))
        return np.r_[-(K*K+2/r-lam/r**2)-z*z,z,dc.ravel()]
    paths=[];calls=0;terminal=None
    for hi,lo in ((float(outer),float(join)),(float(join),B)):
        sol=solve_ivp(rhs,(hi,lo),state,method='DOP853',dense_output=True,
                      rtol=rtol,atol=rtol*1e-3,max_step=max_step)
        if not sol.success or not np.isfinite(sol.y).all():raise ArithmeticError('endpoint integration: '+sol.message)
        state=sol.y[:,-1].copy();calls+=sol.nfev;paths.append((lo,hi,sol))
        if terminal is None:terminal=state.copy()
    co=state[2*n:].reshape(orders,n,n).copy()
    return {'coefficients':co,'contributions':np.array([SCREEN_SCALE**(j+1)*c for j,c in enumerate(co)]),
            'central_z':state[:n].copy(),'solution':JoinedPath(paths),'join_state':terminal,
            'ells':ells,'m':m,'outer':float(outer),'join':float(join),'nodes':nodes,
            'orders':orders,'rtol':rtol,'max_step':max_step,'seconds':perf_counter()-begin,
            'nfev':calls,'source_sha256':bounds['source_sha256'],
            'analytic_radial_components':bounds,
            'status':'FINITE_ANGULAR_RADIAL_ORDER_COEFFICIENTS_NONCERTIFYING',
            'full_nonlinear_remainder_certified':False,
            'spatial_and_roundoff_error_certified':False,
            'omitted_angular_modes_certified':False,
            'computed_coefficient_integration_error_bound':None}
