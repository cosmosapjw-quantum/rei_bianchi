"""Independently testable PR150-literal Case-A RR/DR cooling reference.

Uses only the frozen owner igm_rates(H, He) from V7, not the actual Rust
Driver::fixed_step. Time X=ln(a/a0); gas thermal energy w [erg/H], total
H/He stocks normalized to total hydrogen nuclei (never neutral H I).

Four channels: HII RR, HeII RR, HeIII RR, HeII DR. The last two helium
channels have different binding energies, and HeII RR/DR have separate cooling.
Prescribed FLRW H(a) from V7, independent continuous Radau comparator.
Positive frozen-coefficient pair flows are symmetrically composed with an
implicit T midpoint. This is NOT a source-on, collision or EoR solver.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import exp, expm1, fsum, isfinite, log2
from pathlib import Path
import sys
from typing import Sequence

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

V7_REFERENCE = Path(__file__).resolve().parents[1] / "v7" / "reference"
if str(V7_REFERENCE) not in sys.path:
    sys.path.insert(0, str(V7_REFERENCE))
import radau_casea_reference as native  # noqa: E402: exact owner Grackle literals

CHANNELS = ("RR_HII", "RR_HeII", "RR_HeIII", "DR_HeII")
ION_INDEX = (1, 3, 4, 3)
PRODUCT_INDEX = (0, 2, 3, 2)
CHI_ERG = np.array((native.THRESHOLD_EV[0], native.THRESHOLD_EV[1],
                    native.THRESHOLD_EV[2], native.THRESHOLD_EV[1])) * native.EV_ERG
Y_HE = native.HE_H
KB = native.KB_ERG_K
T_DOMAIN = native.T_DOMAIN


def pair_exact(ion: float, electron: float, exposure: float) -> float:
    """Integrate I' = E' = -k*I*E at constant k over dimensionless exposure."""
    if not all(isfinite(v) and v >= 0 for v in (ion, electron, exposure)):
        raise ValueError("nonnegative finite pair stocks/exposure required")
    if ion == 0.0 or electron == 0.0 or exposure == 0.0:
        return 0.0
    smaller, larger = min(ion, electron), max(ion, electron)
    diff = larger - smaller
    if diff == 0:
        return smaller**2 * exposure / (1.0 + smaller * exposure)
    u = -expm1(-diff * exposure)
    return min(smaller, max(0.0, smaller * larger * u / (diff + smaller * u)))


def stock_vector(fractions: Sequence[float]) -> np.ndarray:
    h, he2, he3 = map(float, fractions)
    if not all(isfinite(x) for x in (h, he2, he3)) or not (0 <= h <= 1 and 0 <= he2 and 0 <= he3 and he2 + he3 <= 1):
        raise ValueError("H/He fractions outside nuclear simplex")
    return np.array((1-h, h, Y_HE*(1-he2-he3), Y_HE*he2, Y_HE*he3), dtype=float)


def nuclei_and_electrons(stocks: np.ndarray) -> tuple[float, float, float]:
    return float(stocks[0]+stocks[1]), float(stocks[2]+stocks[3]+stocks[4]), float(stocks[1]+stocks[3]+2*stocks[4])


def binding_energy(stocks: np.ndarray) -> float:
    return (native.THRESHOLD_EV[0] * stocks[1] +
            native.THRESHOLD_EV[1] * (stocks[3] + stocks[4]) +
            native.THRESHOLD_EV[2] * stocks[4]) * native.EV_ERG


def temperature_from_stocks(w: float, stocks: np.ndarray) -> float:
    _, _, ne = nuclei_and_electrons(stocks)
    total_h, total_he, _ = nuclei_and_electrons(stocks)
    return w / (1.5 * KB * (total_h + total_he + ne))


def rates_at(t: float) -> tuple[np.ndarray, np.ndarray]:
    rates = native.native_casea_rates(t)
    return rates[:4], rates[4:]


def symmetric_reactions(stocks0: np.ndarray, alpha: np.ndarray, cool: np.ndarray,
                        strength: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Time symmetric exact-pair composition at a fixed physical midpoint T.

    strength = DeltaX * n_H(Xmid)/H(Xmid) [s cm^-3]. For helium,
    each reaction's ion stock is per *total H* and ne is per total H,
    so no unphysical extra helium factor enters a channel pair rate.
    """
    gas = np.array(stocks0, dtype=float, copy=True)
    events = np.zeros(4)
    cooling = np.zeros(4)
    binding = np.zeros(4)
    for j in (0,1,2,3,3,2,1,0):
        if alpha[j] <= 0.0:
            if cool[j] > 0:
                raise ValueError("positive RR cooling with zero rate")
            continue
        _, _, ne = nuclei_and_electrons(gas)
        a = pair_exact(float(gas[ION_INDEX[j]]), ne, 0.5 * strength * float(alpha[j]))
        gas[ION_INDEX[j]] -= a
        gas[PRODUCT_INDEX[j]] += a
        events[j] += a
        cooling[j] += a * float(cool[j] / alpha[j])
        binding[j] += a * float(CHI_ERG[j])
    if np.min(gas) < -1e-12:
        raise ArithmeticError("positive reaction map violated")
    return gas, events, cooling, binding


@dataclass
class Result:
    x_end: float
    steps: int
    overdensity: float
    stocks: np.ndarray
    w: float
    events: np.ndarray
    cooling: np.ndarray
    binding_escape: np.ndarray
    work: float
    initial_w: float
    initial_binding: float
    max_Tmid_residual: float
    min_temperature: float
    max_temperature: float
    max_step_exposure: float

    @property
    def temperature(self) -> float:
        return temperature_from_stocks(self.w, self.stocks)

    @property
    def electron_per_h(self) -> float:
        return nuclei_and_electrons(self.stocks)[2]

    @property
    def energy_residual(self) -> float:
        return self.initial_w + self.initial_binding - (
            self.w + binding_energy(self.stocks) + self.work +
            fsum(self.binding_escape) + fsum(self.cooling))

    @property
    def per_channel_escape(self) -> np.ndarray:
        return self.binding_escape + self.cooling


def evolve(steps: int, *, x_end: float = native.X_END,
           initial_fractions: Sequence[float] = native.INITIAL_FRACTIONS,
           T0: float = native.T0_K, density_factor: float = 1.0) -> Result:
    if not isinstance(steps, int) or steps < 1 or steps > 50000:
        raise ValueError("invalid step count")
    if not (isfinite(x_end) and x_end >= 0 and isfinite(density_factor) and density_factor >= 0):
        raise ValueError("invalid integration interval/density")
    if not (T_DOMAIN[0] <= T0 <= T_DOMAIN[1]):
        raise ValueError("outside validated owner rate branch")
    gas = stock_vector(initial_fractions)
    _, _, ne0 = nuclei_and_electrons(gas)
    initial_w = 1.5 * KB * T0 * (1+Y_HE+ne0)
    initial_binding = binding_energy(gas)
    w = initial_w
    events = np.zeros(4)
    coolings = np.zeros(4)
    escapes_binding = np.zeros(4)
    work = 0.0
    max_residual = 0.0
    t_min = T0
    t_max = T0
    exposure_max = 0.0
    dx=x_end/steps
    for i in range(steps):
        xmid = (i+0.5)*dx
        a = native.A0 * exp(xmid)
        nh = density_factor * native.density(a)[0]
        strength = dx * nh / native.hubble(a)
        # Exact adiabatic half-flow: w'=-2w.
        w_ad = w * exp(-dx)
        work += w-w_ad
        before_ne = nuclei_and_electrons(gas)[2]
        before_gas = gas.copy()

        def probe(temp:float):
            al, cool = rates_at(temp)
            candidate, ev, q, b = symmetric_reactions(before_gas, al, cool, strength)
            after_ne = nuclei_and_electrons(candidate)[2]
            after_w = w_ad - fsum(q)
            mid_w = w_ad - 0.5*fsum(q)
            mid_n = 1+Y_HE+0.5*(before_ne+after_ne)
            if after_w < 0 or mid_w <= 0 or mid_n <= 0:
                raise ValueError("thermal reservoir exhausted in RR step")
            Tmid = mid_w/(1.5*KB*mid_n)
            return candidate, ev, q, b, Tmid, after_w, al

        def residual(t:float):
            return t-probe(t)[4]
        flo=residual(T_DOMAIN[0]); fhi=residual(T_DOMAIN[1])
        if flo*fhi>0:
            raise ValueError("RR midpoint T outside certified Grackle branch")
        tm=brentq(residual, *T_DOMAIN, xtol=2e-10, rtol=8.9e-15, maxiter=75)
        gas_new, ev, q, b, t_actual, w_after, al=probe(tm)
        max_residual=max(max_residual,abs(tm-t_actual))
        exposure_max=max(exposure_max,float(max(strength*before_ne*v for v in al)))
        if abs(tm-t_actual)>3e-7:
            raise ArithmeticError("inexact implicit midpoint")
        w_adiabatic_end=w_after*exp(-dx)
        work += w_after-w_adiabatic_end
        gas=gas_new
        w=w_adiabatic_end
        events+=ev
        coolings+=q
        escapes_binding+=b
        tt=temperature_from_stocks(w,gas)
        if not T_DOMAIN[0] <= tt <= T_DOMAIN[1]:
            raise ValueError("final temperature leaves validated atomic branch")
        t_min=min(t_min,tt,tm)
        t_max=max(t_max,tt,tm)
    return Result(x_end,steps,density_factor,gas,w,events,coolings,escapes_binding,
                  work,initial_w,initial_binding,max_residual,t_min,t_max,exposure_max)


def rhs_independent(x:float, y:np.ndarray, density_factor:float=1.0)->np.ndarray:
    """Direct continuous equations. Deliberately does not call pair/reaction map."""
    p,heii,heiii,w=y[:4]
    if min(p,heii,heiii,w)<-1e-15 or p>1+1e-12 or heii+heiii>1+1e-12:
        raise ValueError("invalid continuous HHe state")
    ne_per_h=p+Y_HE*(heii+2*heiii)
    temp=w/(1.5*KB*(1+Y_HE+ne_per_h))
    alpha,cool=rates_at(temp)
    a=native.A0*exp(x)
    nh=native.density(a)[0]*density_factor
    coefficient=nh*ne_per_h/native.hubble(a)
    ionperh=np.array((p,Y_HE*heii,Y_HE*heiii,Y_HE*heii))
    ev=coefficient*ionperh*alpha
    q=coefficient*ionperh*cool
    out=np.zeros(17,dtype=float)
    out[0]=-ev[0]
    out[1]=(-ev[1]+ev[2]-ev[3])/Y_HE
    out[2]=-ev[2]/Y_HE
    out[3]=-2*w-fsum(q)
    out[4:8]=ev
    out[8:12]=q
    out[12:16]=ev*CHI_ERG
    out[16]=2*w
    return out


def radau_reference(*, x_end:float=native.X_END,
                    initial_fractions:Sequence[float]=native.INITIAL_FRACTIONS,
                    T0:float=native.T0_K,density_factor:float=1.0,
                    rtol:float=2e-12):
    gas=stock_vector(initial_fractions)
    ne=nuclei_and_electrons(gas)[2]
    w=1.5*KB*T0*(1+Y_HE+ne)
    y0=np.zeros(17)
    y0[:3]=initial_fractions
    y0[3]=w
    atol=[8e-15]*3+[1e-28]*14
    ans=solve_ivp(lambda x,y:rhs_independent(x,y,density_factor),[0.,x_end],y0,
                  method='Radau',rtol=rtol,atol=atol,
                  max_step=x_end/64 if x_end else 1e-5)
    if not ans.success:
        raise RuntimeError(ans.message)
    return ans


def result_vector(res:Result)->np.ndarray:
    return np.array((res.stocks[1],res.stocks[3]/Y_HE,res.stocks[4]/Y_HE,
                     res.w,*res.events,*res.cooling,*res.binding_escape,res.work))


def compare(res:Result, reference)->dict:
    expect=reference.y[:,-1]
    err=np.abs(result_vector(res)-expect)
    ref_stock=stock_vector(expect[:3])
    reference_T=temperature_from_stocks(float(expect[3]),ref_stock)
    return {
        'T_error_K':abs(res.temperature-reference_T),
        'ne_abs_error':abs(res.electron_per_h-nuclei_and_electrons(ref_stock)[2]),
        'max_absolute_fraction_error':float(max(err[:3])),
        'max_cooling_energy_error_erg_per_H':float(max(err[8:12])),
        'cooling_error_by_channel_erg_per_H':dict(zip(CHANNELS,err[8:12].tolist())),
        'event_error_by_channel_per_H':dict(zip(CHANNELS,err[4:8].tolist())),
        'energy_residual_erg_per_H':res.energy_residual,
        'midpoint_max_residual_K':res.max_Tmid_residual,
        'max_rr_exposure':res.max_step_exposure,
    }
