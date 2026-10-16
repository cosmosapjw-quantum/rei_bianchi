"""Conservative reversible chemistry + photo coupling, frozen-rate research bridge.

Scientific status: source-native PR154 photon photo-ionization (unchanged) coupled
with *manufactured frozen* RR/CI rate coefficients and specified radiative RR
kinetic losses. It does not call the authoritative Grackle owner and is NOT
production recombination/Case-A transfer or cosmological thermal history.

Units: per-H abundances/number; proper n_H [cm^-3], dt [s]; photon q and
thermal, binding, escaped energy [eV/H]. Metric (-,+,+,+), source-free
Killing photon geometry from PR154. Densities are held fixed per reaction step.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from math import exp, isfinite, fsum
from typing import Sequence
import source_aware as src

CHI_EV = src.CHI_EV
KB_EV_K = 8.617333262145e-5

class InsufficientThermalEnergy(ValueError):
    """Reject entire transaction if CI/RR thermal debit is not payable."""

@dataclass(frozen=True)
class FrozenCoefficients:
    """External owner must replace manufactured coefficients before production.

    alpha_rr, beta_ci have units cm^3 s^-1 for HI, HeI, HeII edge channels.
    RR channel i runs ion(HII,HeII,HeIII)->neutral(HI,HeI,HeII).
    rr_electron_kinetic_ev is assumed removed from thermal pool per event and
    added to *bolometric* escaped radiation, not a fabricated ionizing photon.
    """
    alpha_rr_cm3_s: tuple[float,float,float]
    beta_ci_cm3_s: tuple[float,float,float]
    rr_electron_kinetic_ev: tuple[float,float,float]
    authority: str="MANUFACTURED_CONSTANT_RATE_VALIDATION_ONLY"
    def __post_init__(self):
        if not all(len(row)==3 for row in (self.alpha_rr_cm3_s,
                                             self.beta_ci_cm3_s,
                                             self.rr_electron_kinetic_ev)):
            raise ValueError("rate vectors must each contain three species")
        for row in (self.alpha_rr_cm3_s,self.beta_ci_cm3_s,
                    self.rr_electron_kinetic_ev):
            if not all(isfinite(x) and x>=0.0 for x in row):
                raise ValueError("nonnegative finite rate/energy required")
        if self.authority!="MANUFACTURED_CONSTANT_RATE_VALIDATION_ONLY":
            raise ValueError("do not impersonate physical source authority")

@dataclass(frozen=True)
class ThermalReservoir:
    """Thermal and escaped radiation energy, absolute per-H accounting."""
    thermal_ev_per_h:float
    escape_ev_per_h:float=0.
    def __post_init__(self):
        if not all(isfinite(x) and x>=0. for x in
                   (self.thermal_ev_per_h,self.escape_ev_per_h)):
            raise ValueError("nonnegative reservoirs required")

@dataclass(frozen=True)
class ChemistryLedger:
    photo_events:tuple[float,float,float]
    rr_events:tuple[float,float,float]
    ci_events:tuple[float,float,float]
    photoheat_ev_per_h:float
    ci_thermal_debit_ev_per_h:float
    rr_thermal_debit_ev_per_h:float
    radiative_recombination_escape_ev_per_h:float
    binding_delta_ev_per_h:float
    thermal_delta_ev_per_h:float
    escaped_delta_ev_per_h:float
    geometric_work_ev_per_h:float
    photon_number_residual:float
    total_energy_residual_ev_per_h:float
    h_nuclei_residual:float
    he_nuclei_residual:float
    electron_charge_residual:float
    thermal_provider_authority:str="MANUFACTURED_CONSTANT_RATE_VALIDATION_ONLY"
    recoil_owner:str="NOT_ISSUED_BARYON_EULER"
    source_ownership:str="NO_PHOTON_BIRTH; NO_RECOMB_PHOTON_IN_UV; BOL_ESCAPE_ONLY"


def electrons(g:src.Gas)->float:
    return g.h_ii+g.he_ii+2*g.he_iii


def particles_per_h(g:src.Gas)->float:
    return g.h_total+g.he_total+electrons(g)


def temperature_k(g:src.Gas,thermal_ev_per_h:float)->float:
    if not isfinite(thermal_ev_per_h) or thermal_ev_per_h<0.:
        raise ValueError("invalid thermal energy")
    return 2.*thermal_ev_per_h/(3.*KB_EV_K*particles_per_h(g))


def binding_energy(g:src.Gas)->float:
    return (CHI_EV[0]*g.h_ii + CHI_EV[1]*(g.he_ii+g.he_iii)
            +CHI_EV[2]*g.he_iii)


def _ion(g:src.Gas,i:int)->float:
    return (g.h_ii,g.he_ii,g.he_iii)[i]


def _neutral(g:src.Gas,i:int)->float:
    return (g.h_i,g.he_i,g.he_ii)[i]


def _new_ion(g:src.Gas,i:int,amount:float,ionization:bool)->src.Gas:
    """Update stoichiometric gas stocks, amount>=0, no silent clipping."""
    if not isfinite(amount) or amount<0.:
        raise ValueError("invalid reaction event")
    if ionization:
        if i==0:return replace(g,h_i=g.h_i-amount,h_ii=g.h_ii+amount)
        if i==1:return replace(g,he_i=g.he_i-amount,he_ii=g.he_ii+amount)
        if i==2:return replace(g,he_ii=g.he_ii-amount,he_iii=g.he_iii+amount)
    else:
        if i==0:return replace(g,h_i=g.h_i+amount,h_ii=g.h_ii-amount)
        if i==1:return replace(g,he_i=g.he_i+amount,he_ii=g.he_ii-amount)
        if i==2:return replace(g,he_ii=g.he_ii+amount,he_iii=g.he_iii-amount)
    raise ValueError("invalid chemical transition")


def exact_collisional_ionization(n_neutral:float,e:float,k_s:float,dt_s:float)->tuple[float,float]:
    """n'=-k*n*e, e'=+k*n*e; exact logistic with n+e conserved.

    Returns remaining neutral n, event count. Assumes other channels frozen.
    """
    if not all(isfinite(v) and v>=0. for v in (n_neutral,e,k_s,dt_s)):
        raise ValueError("invalid collisional ionization pair")
    if n_neutral==0 or e==0 or k_s==0 or dt_s==0:
        return n_neutral,0.
    kdt=k_s*dt_s
    if not isfinite(kdt):raise ValueError("unrepresentable ionization exposure")
    K=n_neutral+e
    z=exp(-kdt*K)
    remaining=n_neutral*K*z/(e+n_neutral*z)
    amount=n_neutral-remaining
    if amount<0 or amount>n_neutral or remaining<0:
        raise ArithmeticError("collisional positive-domain violation")
    return remaining,amount


def evolve_coupled_photo_thermal(state:src.State,thermo:ThermalReservoir,
                                 dt_s:float,nh_cm3:float,rates:FrozenCoefficients,
                                 *,reaction_substeps:int=1,
                                 a_end:float|None=None,b_end:float|None=None,
                                 ) ->tuple[src.State,ThermalReservoir,ChemistryLedger]:
    """One atomic source-free splitting transaction, rejecting invalid budgets.

    Frozen source-defined rates (external owner later); photon spectral nodes
    and exact Verner cross sections from unmodified PR154 source module.
    Geometry is an endpoint Killing drift, not a time-dependent accuracy claim.
    Sources, CMB, CE, DR and freefree are deliberately not modelled here.
    """
    if not all(isfinite(v) and v>=0. for v in (dt_s,nh_cm3)):
        raise ValueError("invalid nonnegative dt and density")
    if not isinstance(reaction_substeps,int) or reaction_substeps<1:
        raise ValueError("positive integer reaction substeps required")
    if not isinstance(rates,FrozenCoefficients):raise TypeError("explicit rates required")
    photo_initial=state.nphot
    h_before=state.gas.h_total
    he_before=state.gas.he_total
    e_before=electrons(state.gas)
    total_before=state.u_phot_ev+thermo.thermal_ev_per_h+binding_energy(state.gas)+thermo.escape_ev_per_h
    # Collisionless endpoint geometry accounted for exactly once.
    geom,glm=src.evolve(state,0.,nh_cm3,a_end=a_end,b_end=b_end)
    state=geom
    gas=state.gas
    u=thermo.thermal_ev_per_h
    esc=thermo.escape_ev_per_h
    rr=[0.,0.,0.]
    ci=[0.,0.,0.]
    ph=[0.,0.,0.]
    photoheat=0.
    ci_debit=0.
    rr_debit=0.
    esc_added=0.
    # No physical source birth in this thermal coupling: avoid double owner.
    step=dt_s/reaction_substeps

    def one_reaction(kind:str,i:int,h:float):
        nonlocal gas,u,esc,rr,ci,ci_debit,rr_debit,esc_added
        if kind=="rr":
            initial=_ion(gas,i)
            ng,_,d=src.exact_pair(initial,electrons(gas),
                                    nh_cm3*rates.alpha_rr_cm3_s[i],h)
            if d==0.:return
            energy=rates.rr_electron_kinetic_ev[i]*d
            if energy>u:
                raise InsufficientThermalEnergy("RR free-electron energy exceeds thermal reservoir")
            gas=_new_ion(gas,i,d,False)
            rr[i]+=d
            u-=energy
            emitted=(CHI_EV[i]*d)+energy
            esc+=emitted
            rr_debit+=energy
            esc_added+=emitted
        elif kind=="ci":
            init=_neutral(gas,i)
            _,d=exact_collisional_ionization(init,electrons(gas),
                                              nh_cm3*rates.beta_ci_cm3_s[i],h)
            if d==0.:return
            energy=CHI_EV[i]*d
            if energy>u:
                raise InsufficientThermalEnergy("collisional ionization exceeds thermal reservoir")
            gas=_new_ion(gas,i,d,True)
            ci[i]+=d
            u-=energy
            ci_debit+=energy
        else:raise ValueError("unknown reaction")

    schedule=[("rr",0),("rr",1),("rr",2),
              ("ci",0),("ci",1),("ci",2)]
    for _ in range(reaction_substeps):
        for kind,i in schedule:
            one_reaction(kind,i,step*0.5)
        # The source owner returns a new state and ledger, never mutates inputs.
        state=replace(state,gas=gas)
        state,ledger=src.evolve(state,step,nh_cm3,reaction_substeps=1)
        gas=state.gas
        u+=ledger.photoheat_ev
        photoheat+=ledger.photoheat_ev
        for i in range(3):ph[i]+=ledger.photo_events[i]
        for kind,i in reversed(schedule):
            one_reaction(kind,i,step*0.5)
        state=replace(state,gas=gas)
    result_thermo=ThermalReservoir(u,esc)
    charge_expected=e_before + fsum(ph)+fsum(ci)-fsum(rr)
    state_after_e=electrons(state.gas)
    total_after=state.u_phot_ev+u+binding_energy(state.gas)+esc
    ledger_out=ChemistryLedger(
        tuple(ph),tuple(rr),tuple(ci),photoheat,ci_debit,rr_debit,
        esc_added,binding_energy(state.gas)-binding_energy(geom.gas),
        u-thermo.thermal_ev_per_h,esc-thermo.escape_ev_per_h,
        glm.geometric_work_ev,
        photo_initial-state.nphot-fsum(ph),
        total_before-total_after-glm.geometric_work_ev,
        h_before-state.gas.h_total,he_before-state.gas.he_total,
        state_after_e-charge_expected
    )
    return state,result_thermo,ledger_out
