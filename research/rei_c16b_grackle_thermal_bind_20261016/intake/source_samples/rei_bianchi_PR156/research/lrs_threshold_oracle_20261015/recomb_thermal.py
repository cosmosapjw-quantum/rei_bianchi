"""Conditional H/He photoionization + Case-B-like recombination + gas heat oracle.

Separate from REI production. Prescribed non-tilted LRS Bianchi I, constant
signed shear s/H, Verner-1996 ionization fits, initial photon rays only.
No source, scattering, continuum recombination photon retransport, secondary
ionization, Compton, line transport, gravitational backreaction, or H/He cooling
rates from a certified atomic provider.

X=ln(a/a0) dimensionless, photon and species comoving stocks in n_star units,
energy in eV per initial comoving n_star reference volume, physical T in K.
Input K_photo=c n_star 1e-22 m^2 / H0, multiplied by cross section in Mb.
Input K_rec,j=alpha_B,j(T_ref) n_star / H0, positive dimensionless toy values.
Recombination thermal-electron energy removed per event is (3/2) k_B T,
which is a *conditional closure*, not the actual recombination-cooling curve.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import exp, expm1, fsum, isfinite, ceil
from typing import Callable, Sequence

from dynamic_chemistry import Gas, pair_exact, threshold_events, CHANNELS, TARGET, PRODUCT
from lrs_threshold_oracle import Ray
from verner_angular import VernerFit, load_primary_fits

K_B_J_PER_K = 1.380649e-23
EV_J = 1.602176634e-19
K_B_EV_PER_K = K_B_J_PER_K / EV_J


@dataclass(frozen=True)
class PhotoRecombRates:
    photo_per_mb: float = 2.0
    recomb_at_tref: tuple[float, float, float] = (0.32, 0.15, 0.12)
    temperature_ref_K: float = 10_000.0
    temperature_power: tuple[float, float, float] = (0.7, 0.7, 0.7)

    def __post_init__(self):
        vals = (self.photo_per_mb, *self.recomb_at_tref, self.temperature_ref_K,
                *self.temperature_power)
        if not all(isfinite(v) for v in vals):
            raise ValueError("all coefficients must be finite")
        if self.photo_per_mb < 0 or any(c < 0 for c in self.recomb_at_tref):
            raise ValueError("photo/recombination coefficients must be nonnegative")
        if self.temperature_ref_K <= 0:
            raise ValueError("reference temperature must be positive")


def particle_count(gas: Sequence[float]) -> float:
    return fsum(gas[:2]) + fsum(gas[2:5]) + gas[1] + gas[3] + 2.0 * gas[4]


def chemical_energy(gas: Sequence[float], thresholds: Sequence[float]) -> float:
    hi, he1, he2 = thresholds
    return hi*gas[1] + he1*(gas[3]+gas[4]) + he2*gas[4]


def gas_temperature(thermal_ev: float, gas: Sequence[float]) -> float:
    if thermal_ev < 0 or not isfinite(thermal_ev):
        raise ValueError("thermal energy must be finite and nonnegative")
    npart = particle_count(gas)
    if npart <= 0:
        raise ValueError("gas must contain material particles")
    return thermal_ev/(1.5*K_B_EV_PER_K*npart)


@dataclass(frozen=True)
class ThermalResult:
    x_end: float
    initial: Gas
    final: Gas
    photons_initial: tuple[float, ...]
    photons_final: tuple[float, ...]
    initial_photon_energy_ev: float
    final_photon_energy_ev: float
    initial_thermal_ev: float
    final_thermal_ev: float
    initial_temperature_K: float
    final_temperature_K: float
    initial_chemical_ev: float
    final_chemical_ev: float
    photo_events: tuple[float, float, float]
    recomb_events: tuple[float, float, float]
    escaped_recomb_energy_ev: float
    photo_redshift_work_ev: float
    gas_adiabatic_work_ev: float
    steps: int
    source_threshold_events: int
    history: tuple[dict, ...]

    @property
    def photon_reaction_residual(self) -> float:
        return fsum(self.photons_initial)-fsum(self.photons_final)-fsum(self.photo_events)

    @property
    def electron_reaction_residual(self) -> float:
        return (self.final.electrons-self.initial.electrons
                -fsum(self.photo_events)+fsum(self.recomb_events))

    @property
    def hydrogen_residual(self) -> float:
        return self.final.hydrogen-self.initial.hydrogen

    @property
    def helium_residual(self) -> float:
        return self.final.helium-self.initial.helium

    @property
    def energy_residual_ev(self) -> float:
        return fsum((self.initial_photon_energy_ev,self.initial_thermal_ev,
                     self.initial_chemical_ev)) - fsum((
                self.final_photon_energy_ev,self.final_thermal_ev,
                self.final_chemical_ev,self.escaped_recomb_energy_ev,
                self.photo_redshift_work_ev,self.gas_adiabatic_work_ev))


def evolve_thermal(
    rays: Sequence[Ray], initial: Gas, x_end: float,
    *, temperature_initial_K: float = 8_000.0,
    rates: PhotoRecombRates | None = None,
    max_step: float = 0.025,
    hubble_ratio: Callable[[float], float] | None = None,
    fits: dict[str, VernerFit] | None = None,
    max_steps: int = 80_000,
    history: bool = False,
) -> ThermalResult:
    if not rays or not (isfinite(x_end) and x_end >= 0):
        raise ValueError("require rays and nonnegative finite endpoint")
    if not (isfinite(temperature_initial_K) and temperature_initial_K > 0):
        raise ValueError("require positive finite gas temperature")
    if not (isfinite(max_step) and max_step > 0 and max_steps >= 1):
        raise ValueError("invalid timestep budget")
    if any(ray.s_over_h != rays[0].s_over_h for ray in rays):
        raise ValueError("all rays must share one constant-shear background")
    rates = rates or PhotoRecombRates()
    fits = fits or load_primary_fits()
    hubble_ratio = hubble_ratio or (lambda x: 1.0)
    if any(ray.energy0_ev > min(fits[name].emax_ev for name in CHANNELS) for ray in rays):
        raise ValueError("photon outside Verner-1996 fit domain")
    if initial.hydrogen + initial.helium <= 0:
        raise ValueError("gas cannot be empty")
    thresholds = tuple(fits[name].threshold_ev for name in CHANNELS)
    gas = list(initial.as_tuple())
    thermal = particle_count(gas)*1.5*K_B_EV_PER_K*temperature_initial_K
    thermal0 = thermal
    bound0 = chemical_energy(gas, thresholds)
    photons = [ray.photons0 for ray in rays]
    original_photons = tuple(photons)
    photon0 = fsum(ray.energy0_ev*n for ray,n in zip(rays,photons))
    work_photon = work_gas = energy_escaped = 0.0
    photo_events = [0.0]*3
    recomb_events = [0.0]*3
    steps = 0

    # Preserve equivalent transport characteristics exactly. Otherwise
    # sequential nonlinear chemistry introduces artificial FLRW anisotropy.
    groups: dict[tuple[float, ...], list[int]] = {}
    for i,ray in enumerate(rays):
        key = ((ray.energy0_ev,) if rays[0].s_over_h == 0.0
               else (ray.energy0_ev,abs(ray.mu0)))
        groups.setdefault(key,[]).append(i)
    groups = tuple(tuple(group) for group in groups.values())
    saved=[]

    def snapshot(x: float):
        u = fsum(n*ray.geometry(x)[0] for n,ray in zip(photons,rays))
        p = fsum(n*ray.geometry(x)[0]*ray.geometry(x)[1]**2
                 for n,ray in zip(photons,rays))
        saved.append({"X":x,"Tgas_K":gas_temperature(thermal,gas),
                      "stocks":dict(zip(("HI","HII","HeI","HeII","HeIII"),gas)),
                      "ne":gas[1]+gas[3]+2*gas[4],
                      "photons":fsum(photons),"photon_energy_ev":u,
                      "pi_over_u":(3*p-u)/(2*u) if u else None,
                      "thermal_ev":thermal,"chemical_ev":chemical_energy(gas,thresholds)})

    if history:
        snapshot(0.0)

    edges = threshold_events(rays,fits,x_end)

    for lower,upper in zip(edges[:-1],edges[1:]):
        nsteps = max(1,ceil((upper-lower)/max_step))
        if steps+nsteps > max_steps:
            raise ValueError("timestep budget exceeded")
        for it in range(nsteps):
            a=lower+(upper-lower)*it/nsteps
            b=lower+(upper-lower)*(it+1)/nsteps
            m=(a+b)/2.0
            dt=b-a
            h = hubble_ratio(m)
            if not (isfinite(h) and h>0):
                raise ValueError("H/H0 must remain finite positive")
            ea = [ray.geometry(a)[0] for ray in rays]
            em = [ray.geometry(m)[0] for ray in rays]
            eb = [ray.geometry(b)[0] for ray in rays]
            work_photon += fsum(n*(e0-e1) for n,e0,e1 in zip(photons,ea,em))
            # Exact source-free ideal monatomic comoving thermal drift.
            old_thermal=thermal
            thermal *= exp(-dt)
            work_gas += old_thermal-thermal

            scale = exp(-3.0*m)/h
            photo_reactions = [
                (ids,j,scale*rates.photo_per_mb*fits[name].sigma_mb(em[ids[0]]))
                for ids in groups
                for j,name in enumerate(CHANNELS)
                if em[ids[0]] >= thresholds[j]
            ]

            def photo_stage(duration: float):
                nonlocal thermal
                for block in (photo_reactions,reversed(photo_reactions)):
                    for ids,j,k in block:
                        stock=fsum(photons[i] for i in ids)
                        consumed=pair_exact(stock,gas[TARGET[j]],duration*k/2.0)
                        if consumed == 0.0:
                            continue
                        survived=1.0-consumed/stock
                        for i in ids:
                            photons[i] *= survived
                        gas[TARGET[j]] -= consumed
                        gas[PRODUCT[j]] += consumed
                        thermal += (em[ids[0]]-thresholds[j])*consumed
                        photo_events[j] += consumed

            def recombination_stage(duration: float):
                nonlocal thermal,energy_escaped
                for ordering in (range(3),range(2,-1,-1)):
                    for j in ordering:
                        electron=gas[1]+gas[3]+2.0*gas[4]
                        ion=gas[PRODUCT[j]]
                        if ion==0.0 or electron==0.0 or duration==0.0:
                            continue
                        T=gas_temperature(thermal,gas)
                        k=(scale*rates.recomb_at_tref[j]
                           *(T/rates.temperature_ref_K)**(-rates.temperature_power[j]))
                        consumed=pair_exact(ion,electron,duration*k/2.0)
                        if consumed == 0.0:
                            continue
                        n_before=particle_count(gas)
                        removed_kinetic=thermal*(consumed/n_before)
                        gas[PRODUCT[j]] -= consumed
                        gas[TARGET[j]] += consumed
                        thermal -= removed_kinetic
                        energy_escaped += thresholds[j]*consumed+removed_kinetic
                        recomb_events[j] += consumed

            # Symmetric/photo-recomb Strang. Each substage is independently
            # symmetrized in the ordering of elementary exact pair maps.
            photo_stage(dt/2.0)
            recombination_stage(dt)
            photo_stage(dt/2.0)

            work_photon += fsum(n*(e0-e1) for n,e0,e1 in zip(photons,em,eb))
            old_thermal=thermal
            thermal *= exp(-dt)
            work_gas += old_thermal-thermal
            steps += 1
            if history:
                snapshot(b)

    photone=fsum(n*ray.geometry(x_end)[0] for n,ray in zip(photons,rays))
    final=Gas(*gas)
    return ThermalResult(
        x_end,initial,final,original_photons,tuple(photons),photon0,
        photone,thermal0,thermal,temperature_initial_K,
        gas_temperature(thermal,gas),bound0,chemical_energy(gas,thresholds),
        tuple(photo_events),tuple(recomb_events),energy_escaped,work_photon,
        work_gas,steps,max(0,len(edges)-2),tuple(saved))
