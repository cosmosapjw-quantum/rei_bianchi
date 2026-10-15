#!/usr/bin/env python3
"""New independent LRS Bianchi-I matter/radiation anisotropic-stress solver.

Source-free initially isotropic collisionless radiation plus pressureless
matter, and optional shear-viscous internal-thermal energy. Does NOT attempt
the legacy H/He photoionizing photon transport, recombination or collisions.

Metric (-,+,+,+), orthonormal shear diag(-s,-s,2s), scalar shear sqrt(3)|s|,
Sigma=sqrt(3)|s|/H. Signed orientation remains epsilon=sgn(s).
All Pi and rho are SI energy J/m^3; equations use K=8*pi*G/c^2.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path
import time
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp

H0=67.4e3/3.0856775814913673e22
G_SI=6.67430e-11
C_SI=299792458.0
K=8*math.pi*G_SI/C_SI**2
RHO_CRIT=3*H0*H0/K
OM=0.315
OR=9.2e-5
OL=1-OM-OR
AREF=1/21
AEND=.2
GAMMA_M=5/3
HREF=H0*math.sqrt(OM/AREF**3+OR/AREF**4+OL)
XEND=math.log(AEND/AREF)
COEF_M0=np.array([
    8/5,-16/21,8/35,16/231,4528/32175,-2656/15015,
    -254248/3828825,25107568/183324141,10458544/195859125,
    -644335456/5547967425,-732698224/17375502375,
    4574816/46334673,1570056394912/45853950767625],float)
COEF_M2=np.array([
    -8/5,8/7,-16/35,-40/231,-4528/10725,1328/2145,
    1016992/3828825,-12553784/20369349,-10458544/39171825,
    322167728/504360675,1465396448/5791834125,
    -29736304/46334673,-1570056394912/6550564395375,
    13886441783391392/21890676096464175],float)
assert len(COEF_M0)==13 and len(COEF_M2)==14
# sigma/H is user-defined shear scalar / mean H: WE usual Sigma_norm=Sigma/sqrt(3).
def sigma_init_from_legacy_signed_ratio(legacy_signed_s_over_Fref):
    q=legacy_signed_s_over_Fref
    if not math.isfinite(q) or abs(q)>0.05:
        raise ValueError("unsupported frozen AX08 reference family")
    return math.sqrt(3)*abs(q)/math.hypot(1,q), int(np.sign(q))
def legacy_ratio_from_sigma(sigma_ref,orientation):
    if not(math.isfinite(sigma_ref) and 0<=sigma_ref<math.sqrt(3)):
        raise ValueError("physical initial scalar Sigma in [0,sqrt3)")
    if sigma_ref==0:
        if orientation!=0:raise ValueError("zero Sigma requires orientation zero")
        return 0.0
    if orientation not in (-1,1):raise ValueError("nonzero Sigma requires orientation ±1")
    return orientation*sigma_ref/math.sqrt(3-sigma_ref*sigma_ref)

def horner(x,coefs):
    out=0.
    for c in coefs[::-1]:
        out=out*x+c
    return out

class Moments:
    def __init__(self,method="taylor14",order=128):
        if method not in ("taylor14","gl128"):
            raise ValueError("unknown radiation moments")
        if order!=128:raise ValueError("GL128 only")
        self.method=method
        self.mu,self.w=leggauss(128)
        self.w=self.w*.5
        self.m2p=(3*self.mu*self.mu-1)/2
        self.evals=0
    def __call__(self,b):
        self.evals+=1
        if abs(b)>.025:
            raise ValueError("B_SHEAR_OUTSIDE_SOURCE_FREE_VALIDATED_DOMAIN")
        if self.method=="taylor14":
            return 1+b*b*horner(b,COEF_M0), b*horner(b,COEF_M2)
        mm2=self.mu*self.mu
        pert=(1-mm2)*np.expm1(-2*b)+mm2*np.expm1(4*b)
        dev=np.expm1(-2*np.log1p(pert))
        m0=1+float(np.dot(dev,self.w))
        m2=float(np.dot(dev,self.w*self.m2p))
        return m0,m2

@dataclass(frozen=True)
class PhysicalScenario:
    Sigma_ref:float
    orientation:int
    free_radiation_fraction:float=1.
    matter_viscosity_strength:float=0.
    def __post_init__(self):
        legacy_ratio_from_sigma(self.Sigma_ref,self.orientation)
        if not(0<=self.free_radiation_fraction<=1):
            raise ValueError("free radiation energy fraction f in [0,1]")
        if not(math.isfinite(self.matter_viscosity_strength) and 0<=self.matter_viscosity_strength<=.1):
            raise ValueError("nu must be in [0,.1] bounded causal-free NS pilot only")
    @property
    def signed_s_ref(self):
        # Href=sqrt(Fref^2+sref^2) and sref/Href=orientation*Sigma/sqrt(3).
        q=legacy_ratio_from_sigma(self.Sigma_ref,self.orientation)
        return HREF*q

class Solver:
    def __init__(self,scenario:PhysicalScenario,moment_method="taylor14"):
        self.scenario=scenario
        self.moments=Moments(moment_method)
    def eval(self,x,y):
        b,v,u,tau=np.asarray(y,dtype=float)
        if not np.isfinite([b,v,u,tau]).all() or x<0 or x>XEND+1e-12:
            raise ValueError("INVALID_STATE")
        if u< -1e-11:raise ValueError("NEGATIVE_VISCOSITY_HEAT")
        a=AREF*math.exp(x)
        s=HREF*v
        m0,m2=self.moments(b)
        omrad=OR/a**4
        ommatter=OM/a**3
        rad_total=omrad*(1+self.scenario.free_radiation_fraction*(m0-1))
        rad_free=omrad*self.scenario.free_radiation_fraction
        hr2=H0*H0*(ommatter+u+rad_total+OL)+s*s
        if not hr2>0:raise ValueError("NONEXPANDING_CONSTRAINT")
        h=math.sqrt(hr2)
        # Pi_rad is (p_parallel-p_perp)/3, NOT p_parallel-p_perp.
        # In normalized rhoCrit SI units: Pi_rad/rhocrit = f*Omega_r*a^-4*M2/3.
        pi_rad=rad_free*m2/3
        # eta = nu * rho_dust/H (SI dynamic viscosity J*s/m3).
        eta=self.scenario.matter_viscosity_strength*(RHO_CRIT*ommatter)/h
        pi_m=-2*eta*s/RHO_CRIT
        frac=s/h
        dy=[
            frac,
            -3*v+(3*H0*H0/(HREF*h))*(pi_rad+pi_m),
            -3*GAMMA_M*u-6*frac*pi_m,
            HREF/h
        ]
        stuff={
            "x":x,"a":a,"H_per_s":h,"signed_s_per_s":s,
            "Sigma":math.sqrt(3)*abs(frac),
            "Sigma_WE":abs(frac),
            "orientation":int(np.sign(s)),
            "radiation_m0":m0,"radiation_m2":m2,
            "rad_energy_over_rhocrit":rad_total,
            "rho_dust_over_rhocrit":ommatter,
            "rho_thermal_over_rhocrit":u,
            "pressure_th_over_rhocrit":(GAMMA_M-1)*u,
            "pi_r_over_rhocrit":pi_rad,
            "pi_m_over_rhocrit":pi_m,
            "pi_total_J_m3":(pi_rad+pi_m)*RHO_CRIT,
            "pi_r_J_m3":pi_rad*RHO_CRIT,
            "pi_m_J_m3":pi_m*RHO_CRIT,
            "eta_m_J_s_m3":eta,
            "shear_energy_per_H2":s*s/(h*h),
            "hamiltonian_rhs_per_s2":H0*H0*(ommatter+u+rad_total+OL)+s*s,
            "radiation_energy_ledger_d_rho_dx":-4*rad_total-6*frac*pi_rad,
            "viscous_heating_source_per_x":-6*frac*pi_m,
        }
        return dy,stuff
    def rhs(self,x,y):
        return self.eval(x,y)[0]
    def solve(self,rtol=5e-11,atol=3e-13,n=501,max_step=np.inf):
        if not(0<rtol<1e-7 and 0<atol<1e-8):
            raise ValueError("unphysical solver accuracy domain")
        q=legacy_ratio_from_sigma(self.scenario.Sigma_ref,self.scenario.orientation)
        y0=[0.,q,0.,0.]
        grid=np.linspace(0.,XEND,n)
        start=time.perf_counter()
        s=solve_ivp(self.rhs,(0.,XEND),y0,method="DOP853",
            rtol=rtol,atol=atol,max_step=max_step,t_eval=grid,dense_output=True)
        wall=time.perf_counter()-start
        if not s.success:
            raise RuntimeError(f"COUPLED_SOLVER_FAILURE:{s.message}")
        if not np.isfinite(s.y).all() or np.min(s.y[2])<-1e-12 or np.min(s.y[3])<0:
            raise RuntimeError("UNPHYSICAL_COSMOLOGICAL_STATE")
        infos=[self.eval(float(x),s.y[:,i])[1] for i,x in enumerate(s.t)]
        if any(not(0<=w["Sigma"]<math.sqrt(3)) for w in infos):
            raise RuntimeError("SHEAR_SIGMA_NORMALIZATION_OUTSIDE_DOMAIN")
        return s,infos,wall
