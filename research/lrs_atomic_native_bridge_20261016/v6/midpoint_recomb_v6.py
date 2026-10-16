"""Implicitly time-centred Grackle Case-A mass-action subflow.

Standalone additive operator for the source-verified V5 reference, not native REI
production. Pair_Exact for frozen coefficients is used with a *self-consistent*
midpoint gas temperature; no negative stocks or energy correction by residual.

The rate table remains authoritative only on its validated 10--24 kK interior.
The scalar implicit solve rejects steps whose midpoint is outside that domain.

Midpoint closure is: A=PairExact(I0,ne0, h * alpha(Tmid) * rhoX),
E_cool=A Lambda(Tmid)/alpha(Tmid)/EV_ERG,
Tmid=[U0-E_cool/2]/[1.5*kB*(npart0-A/2)].

The last expression includes the removed *one electron per recombination* in
npart_mid. The same A decrements ion and electron; parent H/He inventory is
mutated only after the solve succeeds. Energy lost is assigned once to escaped
Case-A radiation. This closure is symmetric to order two for smooth rates.
"""
from __future__ import annotations

from bootstrap_v6 import setup
setup()
from dataclasses import dataclass
from math import isfinite, fsum
from typing import Callable, MutableSequence, Sequence

from scipy.optimize import brentq
from dynamic_chemistry import pair_exact, TARGET, PRODUCT
from recomb_thermal import particle_count, gas_temperature, K_B_EV_PER_K, EV_J

CHANNEL_COEFF = ((0, 4), (1, 5), (2, 6))
EV_ERG = EV_J*1.e7

@dataclass(frozen=True)
class MidpointEvent:
    count: float
    cooling_ev: float
    midpoint_temperature_K: float
    iterations: int


def midpoint_casea_event(
    gas: MutableSequence[float], thermal_ev: float, species: int,
    duration_X: float, volume_density_per_hubble: float,
    rate_provider: Callable[[float], Sequence[float]],
    binding_ev: float,
) -> tuple[float, float, MidpointEvent]:
    """Returns (new thermal, escaped-energy increment, event); mutates gas.

    volume_density_per_hubble = nstar_cm3*exp(-3Xmid)/(H/H0)/H0_s.
    No toy fallback: this method applies only when a real Case-A provider is set.
    """
    if species not in (0, 1, 2):
        raise ValueError("species channel index outside HII/HeII/HeIII")
    if not (isfinite(thermal_ev) and thermal_ev>=0 and
            isfinite(duration_X) and duration_X>=0 and
            isfinite(volume_density_per_hubble) and volume_density_per_hubble>=0 and
            isfinite(binding_ev) and binding_ev>0):
        raise ValueError("nonphysical input to midpoint reaction")
    ion=gas[PRODUCT[species]]
    ne=gas[1]+gas[3]+2.0*gas[4]
    T0=gas_temperature(thermal_ev,gas)
    if duration_X==0 or ion==0 or ne==0 or volume_density_per_hubble==0:
        return thermal_ev,0.,MidpointEvent(0.,0.,T0,0)
    if not hasattr(rate_provider,'minT') or not hasattr(rate_provider,'maxT'):
        raise TypeError('midpoint provider must have a documented finite temperature domain')
    low=float(rate_provider.minT)
    high=float(rate_provider.maxT)
    if not (0<low<=T0<=high):
        raise ValueError("initial T outside validated atomic provider domain")
    n0=particle_count(gas)
    if n0<=0:
        raise ValueError("zero gas particle census")
    calls=0
    def outcome(t:float):
        nonlocal calls
        coeff=tuple(float(q) for q in rate_provider(t))
        if len(coeff)!=8 or any(not isfinite(v) or v<0 for v in coeff):
            raise ValueError("bad native Case-A coefficients")
        if species==1:
            alpha=coeff[1]+coeff[3]
            cooling=coeff[5]+coeff[7]
        else:
            j,c=CHANNEL_COEFF[species]
            alpha=coeff[j]
            cooling=coeff[c]
        if alpha<=0:
            if cooling:
                raise ValueError("positive cooling with zero alpha")
            return 0.,0.,T0
        A=pair_exact(ion,ne,duration_X*volume_density_per_hubble*alpha)
        Q=A*(cooling/alpha)/EV_ERG
        midU=thermal_ev-0.5*Q
        midn=n0-0.5*A
        if midU<0 or midn<=0:
            raise ValueError("midpoint thermal reservoir or gas particle bound violated")
        calls+=1
        Tpred=midU/(1.5*K_B_EV_PER_K*midn)
        return A,Q,Tpred
    def residual(T):
        return T-outcome(T)[2]
    f_lo=residual(low)
    f_hi=residual(high)
    if f_lo*f_hi>0:
        raise ValueError("implicit midpoint temperature leaves validated provider range")
    if f_lo==0:
        midpoint=low
    elif f_hi==0:
        midpoint=high
    else:
        midpoint=brentq(residual,low,high,xtol=1e-10,
                        rtol=9e-15,maxiter=75)
    A,Q,Tpred=outcome(midpoint)
    if abs(midpoint-Tpred)>2e-7:
        raise ArithmeticError('implicit reaction midpoint residual too large')
    if Q>thermal_ev:
        raise ValueError('recombination cooling larger than thermal reservoir')
    newT=(thermal_ev-Q)/(1.5*K_B_EV_PER_K*(n0-A))
    if not (low <= newT <= high):
        raise ValueError('final gas temperature leaves validated donor domain')
    # Mutation only after ALL domain, conservation and solver checks have passed.
    gas[PRODUCT[species]]-=A
    gas[TARGET[species]]+=A
    return thermal_ev-Q,binding_ev*A+Q,MidpointEvent(A,Q,midpoint,calls)
