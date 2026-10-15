"""Positive finite photon-node/H-He photoionization research adapter.

Research-only source-aware two-way H/He state and photon reaction solution,
not rei_bianchi production native solver or physical reionization prediction.

Convention: ds^2 = -c^2dt^2 + a^2[e^(-2b)(dx^2+dy^2)+e^(4b)dz^2],
physical photon E(q,mu0,a,b)=q sqrt[(1-mu0^2) e^(2b)+mu0^2 e^(-4b)]/a.
Photon q has eV units with a_ref=1; all N/gas states per H nucleus;
proper hydrogen number density in cm^-3, proper time in s.

Verner data: three source-locked rows of Verner et al. (1996) original
photo.dat; parent donor SHA256 a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389;
rei_bianchi PR152 Git source commit bbbd18b5c16eff70bc32ba4296360dceb9060ec4.
Only 3 species/rows, no inference of real UV emissivity, sources or neutral history.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from math import exp, expm1, isfinite, sqrt, fsum
from typing import Sequence

C_CM_S = 2.99792458e10
MB_CM2 = 1.e-18
SPECIES = ("HI", "HeI", "HeII")
# Fit threshold (E_th) and physical ionization/binding energy (chi) differ.
CHI_EV = (13.598434599702, 24.587389011, 54.41776)
# (E_th, E_max, E0, sigma0 Mb, ya, P, yw, y0, y1) from original Verner photo.dat
VERNER_ROWS = (
 (13.60, 5.e4, 4.298e-1, 5.475e4, 3.288e1, 2.963, 0., 0., 0.),
 (24.59, 5.e4, 1.361e1, 9.492e2, 1.469, 3.188, 2.039, 4.434e-1, 2.136),
 (54.42, 5.e4, 1.720, 1.369e4, 3.288e1, 2.963, 0., 0., 0.),
)


def verner_mb(i: int, energy_ev: float) -> float:
    if i not in range(3) or not isfinite(energy_ev) or energy_ev < 0:
        raise ValueError("invalid absorber or energy")
    threshold, emax, e0, sigma0, ya, power, yw, y0, y1 = VERNER_ROWS[i]
    if energy_ev < threshold:
        return 0.0
    if energy_ev > emax:
        raise ValueError("original Verner 1996 fit E_max exceeded")
    x = energy_ev/e0-y0
    y = sqrt(x*x+y1*y1)
    result=sigma0*((x-1.)**2+yw*yw)*y**(power*0.5-5.5)*(1.+sqrt(y/ya))**(-power)
    if not isfinite(result) or result < 0:
        raise ArithmeticError("unphysical Verner fit")
    return result


def positive_finite(*nums: float) -> bool:
    return all(isfinite(x) and x >= 0. for x in nums)


@dataclass(frozen=True)
class Node:
    q_ev: float
    mu0: float
    n_per_h: float
    def __post_init__(self) -> None:
        if not (positive_finite(self.q_ev,self.n_per_h) and self.q_ev>0 and
                isfinite(self.mu0) and -1 <= self.mu0 <= 1):
            raise ValueError("invalid photon node")


@dataclass(frozen=True)
class Gas:
    h_i: float
    h_ii: float
    he_i: float
    he_ii: float
    he_iii: float
    def __post_init__(self) -> None:
        if not positive_finite(self.h_i,self.h_ii,self.he_i,self.he_ii,self.he_iii):
            raise ValueError("negative/nonfinite gas stock")
        if not (0 < self.h_i+self.h_ii <= 1.+5e-15 and
                0 <= self.he_i+self.he_ii+self.he_iii <= 1):
            raise ValueError("invalid H/He per-H normalization")
    @property
    def h_total(self) -> float:
        return self.h_i+self.h_ii
    @property
    def he_total(self) -> float:
        return self.he_i+self.he_ii+self.he_iii
    def absorber(self, i: int) -> float:
        return (self.h_i,self.he_i,self.he_ii)[i]
    def photoionize(self, i: int, consumed: float) -> Gas:
        if consumed < 0 or consumed > self.absorber(i):
            raise ValueError("invalid gas depletion")
        if i==0:
            return replace(self,h_i=self.h_i-consumed,h_ii=self.h_ii+consumed)
        if i==1:
            return replace(self,he_i=self.he_i-consumed,he_ii=self.he_ii+consumed)
        if i==2:
            return replace(self,he_ii=self.he_ii-consumed,he_iii=self.he_iii+consumed)
        raise ValueError("invalid absorber")


@dataclass(frozen=True)
class State:
    photons: tuple[Node,...]
    gas: Gas
    a: float=1.0
    b: float=0.0
    def __post_init__(self) -> None:
        if not (isfinite(self.a) and self.a>0 and isfinite(self.b) and abs(self.b)<50):
            raise ValueError("invalid background")
        if not all(isinstance(p,Node) for p in self.photons):
            raise ValueError("invalid photon node type")
    @property
    def nphot(self) -> float:
        return fsum(p.n_per_h for p in self.photons)
    @property
    def u_phot_ev(self) -> float:
        return fsum(p.n_per_h * physical_energy(p,self.a,self.b) for p in self.photons)


def energy_ratio(b: float, mu0: float) -> float:
    if not(isfinite(b) and abs(b)<50 and isfinite(mu0) and -1<=mu0<=1):
        raise ValueError("invalid geometry")
    return sqrt((1.-mu0*mu0)*exp(2.*b)+mu0*mu0*exp(-4.*b))


def physical_energy(p: Node, a: float, b: float) -> float:
    return p.q_ev*energy_ratio(b,p.mu0)/a


def mu_now(p:Node,b:float)->float:
    return p.mu0*exp(-2.*b)/energy_ratio(b,p.mu0)


def exact_pair(n:float,stock:float,k:float,dt:float)->tuple[float,float,float]:
    """Exact N'=-k N X, X'=-k N X, conserving N-X and positivity."""
    if not positive_finite(n,stock,k,dt):
        raise ValueError("invalid frozen pair")
    if n==0 or stock==0 or k==0 or dt==0:
        return n,stock,0.0
    minority=min(n,stock)
    difference=abs(n-stock)
    delta=k*difference*dt
    # phi=(1-exp(-delta))/delta, analytic non-singular at delta=0
    if delta < 1.e-5:
        phi=1.-delta*0.5+delta*delta/6.-delta**3/24.+delta**4/120.
    else:
        phi=-expm1(-delta)/delta
    small=minority*exp(-delta)/(1.+minority*k*dt*phi)
    events=minority-small
    if n<=stock:
        # Force both members to retain the original difference to roundoff.
        return small,difference+small,events
    return difference+small,small,events


@dataclass(frozen=True)
class Ledgers:
    photo_events: tuple[float,float,float]
    emitted_number: float
    emitted_energy_ev: float
    absorbed_energy_ev: float
    binding_energy_ev: float
    photoheat_ev: float
    geometric_work_ev: float
    absorbed_pz_ev_over_c: float
    number_residual: float
    energy_residual_ev: float
    hydrogen_residual: float
    helium_residual: float
    collision_owner: str="PHOTON_GAS_ABSORPTION_ONLY; NO_RECOMBINATION_OR_THOMSON"
    recoil_owner: str="OPEN_NO_BARYON_EULER_UPDATE"


def evolve(state:State,proper_dt_s:float,n_h_cm3:float,*,
           a_end:float|None=None,b_end:float|None=None,
           source:Sequence[Node]=(),reaction_substeps:int=1)->tuple[State,Ledgers]:
    """Split exact Killing drift+source and pairwise gas/photoionization.

    Second-order symmetric composition of all 3*J pair subflows for constant
    terminal geometry, frozen proper n_H and source injection before chemistry.
    Time-dependent geometry/nonuniform emission are explicitly not second order.
    """
    if not positive_finite(proper_dt_s,n_h_cm3):
        raise ValueError("negative/nonfinite proper time or density")
    if not isinstance(reaction_substeps,int) or reaction_substeps < 1:
        raise ValueError("reaction_substeps must be positive integer")
    a=state.a if a_end is None else a_end
    b=state.b if b_end is None else b_end
    if not(isfinite(a) and a>0 and isfinite(b) and abs(b)<50):
        raise ValueError("invalid endpoint geometry")
    if not all(isinstance(p,Node) for p in source):
        raise ValueError("invalid source photon")
    n_start=state.nphot
    energy_start=state.u_phot_ev
    work=fsum(p.n_per_h*(physical_energy(p,state.a,state.b)-physical_energy(p,a,b))
             for p in state.photons)
    injected=tuple(source)
    source_n=fsum(p.n_per_h for p in injected)
    source_u=fsum(p.n_per_h*physical_energy(p,a,b) for p in injected)
    photons=list(state.photons)+list(injected)
    for p in photons:
        for i in range(3):
            _=verner_mb(i,physical_energy(p,a,b)) # eager whole-node Emax validation
    rates=[tuple(C_CM_S*n_h_cm3*MB_CM2*verner_mb(i,physical_energy(p,a,b))
                 for i in range(3)) for p in photons]
    gas=state.gas
    events=[0.,0.,0.]
    binding=heat=absorbed_energy=pz=0.
    pair_idx=[(j,i) for j in range(len(photons)) for i in range(3) if rates[j][i]>0]
    half_dt=proper_dt_s/(2.*reaction_substeps)
    for _ in range(reaction_substeps):
        for order in (pair_idx,reversed(pair_idx)):
            for j,i in order:
                p=photons[j]
                newn,newgasstock,dn=exact_pair(p.n_per_h,gas.absorber(i),rates[j][i],half_dt)
                if dn==0.0:
                    continue
                # Assign partner stock directly: no cancellation of a tiny species.
                if i==0:
                    gas=replace(gas,h_i=newgasstock,h_ii=gas.h_ii+dn)
                elif i==1:
                    gas=replace(gas,he_i=newgasstock,he_ii=gas.he_ii+dn)
                else:
                    gas=replace(gas,he_ii=newgasstock,he_iii=gas.he_iii+dn)
                photons[j]=replace(p,n_per_h=newn)
                ee=physical_energy(p,a,b)
                events[i]+=dn
                absorbed_energy+=dn*ee
                binding+=dn*CHI_EV[i]
                heat+=dn*(ee-CHI_EV[i])
                pz+=dn*ee*mu_now(p,b)
    result=State(tuple(photons),gas,a,b)
    hres=state.gas.h_total-result.gas.h_total
    heres=state.gas.he_total-result.gas.he_total
    nres=(n_start+source_n)-(result.nphot+sum(events))
    eres=(energy_start+source_u)-(result.u_phot_ev+work+binding+heat)
    return result,Ledgers(tuple(events),source_n,source_u,absorbed_energy,binding,heat,work,pz,
                          nres,eres,hres,heres)
