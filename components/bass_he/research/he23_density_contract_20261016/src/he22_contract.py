"""HE22 source-age H/He native microphysics *interface*, independently testable.

Input: original HE21 photons at an actual chemical midpoint; physical E in eV,
nonnegative counts per original H, original Verner cross sections.
Native owner: `rei_microphysics::igm_thermal::igm_point_rhs`, with h=0 because
geometry/adiabatic work belongs to the outer transport. The standalone
FakeOwner test double below is never a substitute for physical owner output.

Energy reservoirs: photon + thermal(eV/H) + ion binding(eV/H) + work +
Case-A escaped energy - CMB supplied energy. Each event owner is unique.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
import math
import numpy as np

from he21_photo import (
    BIND_EV, C_CM_S, EV_ERG, Y_HE, admissible, binding, neutral,
    sigma_cm2,
)

@dataclass(frozen=True)
class NativePoint:
    fraction_dt: np.ndarray   # s^-1, order HII HeII HeIII
    w_dt_ev_per_h_s: float
    temperature_K: float
    photo_events_cm3_s: np.ndarray
    thermal_micro_erg_cm3_s: float
    binding_micro_erg_cm3_s: float
    escape_erg_cm3_s: float
    cmb_to_gas_erg_cm3_s: float
    photo_input_erg_cm3_s: float
    ci_events_cm3_s: np.ndarray | None = None
    rr_events_cm3_s: np.ndarray | None = None
    dr_events_cm3_s: float = 0.


@dataclass(frozen=True)
class PhotoMap:
    new_counts: np.ndarray
    events_per_H: np.ndarray  # HI HeI HeII, from photons at midpoint
    heat_per_H: np.ndarray    # species photoelectrons eV/H
    gamma_s: np.ndarray      # original ion rate per absorber s^-1
    heat_erg_per_absorber_s: np.ndarray
    photon_number_residual: float
    photon_energy_residual_eV_per_H: float
    source_energy_eV_per_H: float


def photomap(gas: np.ndarray, counts: np.ndarray, energy_eV: np.ndarray,
             nH_cm3: float, dt_s: float) -> PhotoMap:
    """Positive competing-absorption exponential, *instantaneous* source birth.

    No within-step source rate: HE21 already deposits a cohort at the midpoint.
    Unlike CR72's continuous-source phi1, incoming counts already include births.
    """
    gas = np.asarray(gas, dtype=float)
    n = np.asarray(counts, dtype=float)
    energy = np.asarray(energy_eV, dtype=float)
    if not(admissible(gas) and math.isfinite(nH_cm3) and nH_cm3 > 0
           and math.isfinite(dt_s) and dt_s > 0 and n.ndim == 1
           and energy.shape == n.shape and np.isfinite(n).all()
           and (n >= 0).all() and np.isfinite(energy).all()
           and (energy > 0).all()):
        raise ValueError('HE22_PHOTON_INPUT_DOMAIN')
    frac = neutral(gas)  # absorbers per original H nucleus
    if (frac < 0).any():
        raise ValueError('HE22_NEGATIVE_NEUTRAL')
    sigma = sigma_cm2(energy)
    lam = C_CM_S*nH_cm3*sigma*frac[np.newaxis,:]   # physical s^-1
    total = lam.sum(axis=1)
    lost = n*(-np.expm1(-total*dt_s))
    shares = np.divide(lam,total[:,None],out=np.zeros_like(lam),where=total[:,None]>0)
    events = lost[:,None]*shares
    per_species = events.sum(axis=0)
    heat_species = np.sum(events*(energy[:,None]-BIND_EV[None,:]),axis=0)
    if (heat_species < -1e-20).any():
        raise ArithmeticError('HE22_PHOTOHEAT_NEGATIVE')
    gamma=np.zeros(3)
    power=np.zeros(3)
    np.divide(per_species,dt_s*frac,out=gamma,where=frac>0)
    np.divide(heat_species*EV_ERG,dt_s*frac,out=power,where=frac>0)
    if np.any((frac==0)&(per_species>0)):
        raise ArithmeticError('HE22_UNOWNED_PHOTOEVENT')
    after = n-lost
    if (after < -1e-22).any():
        raise ArithmeticError('HE22_NEGATIVE_SURVIVOR')
    # Photoelectric bookkeeping with *physical* binding energies, not fits.
    incoming_energy=float(np.dot(n,energy))
    surviving_energy=float(np.dot(after,energy))
    absorbed=float(np.dot(per_species,BIND_EV)+heat_species.sum())
    return PhotoMap(after,per_species,heat_species,gamma,power,
          float(n.sum()-after.sum()-per_species.sum()),
          incoming_energy-surviving_energy-absorbed,incoming_energy)


def evaluate(gas_new: np.ndarray, gas_old: np.ndarray, counts: np.ndarray,
             energy: np.ndarray, nH_cm3: float, dt_s: float,
             native: Callable) -> tuple[np.ndarray,PhotoMap,NativePoint]:
    photo = photomap(gas_new,counts,energy,nH_cm3,dt_s)
    point = native(gas_new, photo.gamma_s,photo.heat_erg_per_absorber_s)
    if not isinstance(point,NativePoint):
        raise TypeError('HE22_REQUIRE_NATIVE_POINT')
    nd = nH_cm3*photo.events_per_H/dt_s
    photon_input = nH_cm3*photo.source_energy_eV_per_H*0.0
    photon_input += nH_cm3*(float(np.dot(photo.events_per_H,BIND_EV))+
                    float(photo.heat_per_H.sum()))*EV_ERG/dt_s
    if not np.allclose(point.photo_events_cm3_s,nd,rtol=2e-10,atol=1e-29):
        raise AssertionError('HE22_NATIVE_EVENT_OWNER_MISMATCH')
    if not np.isclose(point.photo_input_erg_cm3_s,photon_input,rtol=2e-10,atol=1e-29):
        raise AssertionError('HE22_NATIVE_PHOTO_ENERGY_MISMATCH')
    native_energy=(point.thermal_micro_erg_cm3_s+
       point.binding_micro_erg_cm3_s+point.escape_erg_cm3_s-
       point.cmb_to_gas_erg_cm3_s-point.photo_input_erg_cm3_s)
    if abs(native_energy)>2e-9*max(abs(photon_input),1e-29):
        raise AssertionError('HE22_NATIVE_MICRO_ENERGY_MISMATCH')
    if not(np.isfinite(point.fraction_dt).all() and math.isfinite(point.w_dt_ev_per_h_s)):
        raise ArithmeticError('HE22_NONFINITE_MICRO_RHS')
    residual=gas_new-gas_old-dt_s*np.r_[point.fraction_dt,point.w_dt_ev_per_h_s]
    return residual,photo,point


@dataclass(frozen=True)
class StepResult:
    gas: np.ndarray
    photons: np.ndarray
    events_per_H: np.ndarray
    photoheat_per_H: np.ndarray
    escaped_ev_per_H: float
    cmb_to_gas_ev_per_H: float
    photons_number_residual: float
    photons_energy_residual: float
    total_energy_residual_ev_per_H: float
    scaled_implicit_residual: float
    iterations: int
    rhs_calls: int
    ci_per_H: np.ndarray | None = None
    rr_per_H: np.ndarray | None = None
    dr_per_H: float = 0.


def solve_midpoint(gas0, photons0, energy_eV, nh, dt, native,
                   tolerance=3e-12, maxiter=15) -> StepResult:
    """Bounded damped 4x4 Newton using one original native chemical RHS owner.

    For initial photo-only lower-level unit tests, a stand-in NativePoint can
    be injected; only actual Rust-owner execution admits native chemical science.
    """
    gas0=np.asarray(gas0,dtype=float)
    if not admissible(gas0): raise ValueError('HE22_INVALID_INITIAL_GAS')
    g=gas0.copy();calls=0
    scale=np.array([1.,1.,1.,max(gas0[3],1e-5)])
    def probe(v):
        nonlocal calls
        calls+=1
        return evaluate(v,gas0,photons0,energy_eV,nh,dt,native)
    def ledger(v,p,point):
        escaped=point.escape_erg_cm3_s*dt/(nh*EV_ERG)
        cmb=point.cmb_to_gas_erg_cm3_s*dt/(nh*EV_ERG)
        du=float(v[3]-gas0[3]);db=float(binding(v)-binding(gas0))
        e_after=float(np.dot(p.new_counts,energy_eV))
        total=(e_after-p.source_energy_eV_per_H+du+db+escaped-cmb)
        physical_scale=max(abs(p.source_energy_eV_per_H),abs(du)+abs(db)+abs(escaped)+abs(cmb),1e-15)
        limit=max(3e-11*physical_scale,2e-12*abs(v[3]))
        return total,limit,escaped,cmb
    for k in range(maxiter+1):
        residual,p,point=probe(g)
        err=float(np.max(np.abs(residual)/scale))
        total_energy,energy_limit,escaped,cmb=ledger(g,p,point)
        # Both existing gates must hold; no tolerance is changed or relaxed.
        if err < tolerance and abs(total_energy)<=energy_limit: break
        if k==maxiter: raise RuntimeError('HE22_NEWTON_ITERATION_CAP')
        jac=np.empty((4,4))
        for j in range(4):
            h=(1e-6*max(abs(g[j]),1e-4)) if j<3 else (2e-6*max(g[j],1e-4))
            trial=g.copy();trial[j]+=h
            if not admissible(trial):
                h=-h;trial[j]=g[j]+h
            if not admissible(trial): raise RuntimeError('HE22_NO_ADMISSIBLE_DIFFERENCE')
            rr,_,_=probe(trial)
            jac[:,j]=(rr-residual)/h
        try: direction=np.linalg.solve(jac,-residual)
        except np.linalg.LinAlgError as e: raise RuntimeError('HE22_SINGULAR_JACOBIAN') from e
        accepted=False
        for back in range(24):
            trial=g+direction*2.0**(-back)
            if not admissible(trial):continue
            try: r,_,_=probe(trial)
            except (ValueError, ArithmeticError):continue
            trial_err=float(np.max(np.abs(r)/scale))
            if trial_err<err:
                g=trial;accepted=True;break
        if not accepted:raise RuntimeError('HE22_LINESEARCH_FAILED')
    # Note: a stiff native Jacobian may need better JVP/SNES; never broaden tolerances silently.
    total_energy,energy_limit,escaped,cmb=ledger(g,p,point)
    if abs(total_energy)>energy_limit:
        raise AssertionError('HE22_TOTAL_ENERGY_LEDGER_FAIL')
    return StepResult(g,p.new_counts,p.events_per_H,p.heat_per_H,escaped,cmb,
       p.photon_number_residual,p.photon_energy_residual_eV_per_H,total_energy,
       err,k,calls,
       None if point.ci_events_cm3_s is None else point.ci_events_cm3_s*dt/nh,
       None if point.rr_events_cm3_s is None else point.rr_events_cm3_s*dt/nh,
       point.dr_events_cm3_s*dt/nh)


class PhotoOnlyTestDouble:
    """A constructed conservation oracle. This is NOT Grackle/owner Rust."""
    def __init__(self, nh:float): self.nh=nh
    def __call__(self, gas, gamma, power):
        a=neutral(gas); photo=a*gamma; heat=a*power/EV_ERG
        changes=np.array([photo[0],(photo[1]-photo[2])/Y_HE,photo[2]/Y_HE])
        binding_rate=float(np.dot(photo,BIND_EV))
        return NativePoint(changes,float(heat.sum()),0.,self.nh*photo,
           self.nh*EV_ERG*float(heat.sum()),self.nh*EV_ERG*binding_rate,
           0.,0.,self.nh*EV_ERG*(float(heat.sum())+binding_rate))


class ConstructedCaseAEscapeTestDouble:
    """Manufactured H/He recombination+escape rate oracle. NEVER native physics.

    Nonzero bounded RR rates, no collisional/Compton cooling; derived energy
    projection explicitly tests that Case-A escape is not photon source twice.
    """
    def __init__(self,nh,rr_s=1e-11): self.nh=nh;self.rr_s=rr_s
    def __call__(self,gas,gamma,power):
        alpha=neutral(gas)
        photo=alpha*gamma
        heat=alpha*power/EV_ERG
        rec=np.array([gas[0],Y_HE*gas[1],Y_HE*gas[2]])*self.rr_s
        fr=np.array([photo[0]-rec[0],
           (photo[1]-photo[2]-rec[1]+rec[2])/Y_HE,
           (photo[2]-rec[2])/Y_HE])
        binding_rate=float(np.dot(photo-rec,BIND_EV))
        escape_eV_s=float(np.dot(rec,BIND_EV))
        thermal_rate=float(np.sum(heat))
        nh=self.nh
        return NativePoint(fr,thermal_rate,0.,nh*photo,
           nh*EV_ERG*thermal_rate,nh*EV_ERG*binding_rate,
           nh*EV_ERG*escape_eV_s,0.,
           nh*EV_ERG*(float(np.dot(photo,BIND_EV))+thermal_rate))
