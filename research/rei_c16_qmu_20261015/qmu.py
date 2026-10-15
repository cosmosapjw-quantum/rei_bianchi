#!/usr/bin/env python3
"""C16 eventwise Q0, Qz and positive Case-A photon moment realizability.

Reads actual C11/C13/C15 H/He physics; original source remains immutable.
Radiation energy and c*p_z are eV per H, source proper photon density is cm^-3.
An escaped Case-A *energy scalar* cannot determine its directional pressure,
number or spectral/angular photons. The source is held NOT_ADMITTED unless
these independent moments are provided.
"""
from __future__ import annotations
from dataclasses import dataclass
import math,sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"research/rei_c13_live_source_20261015"))
sys.path.insert(0,str(ROOT/"research/rei_c15_sigma_pi_feedback_20261015"))
import short_interval as c13
import coupled as c15

EV_CM3_TO_PA=1.602176634e-13


@dataclass(frozen=True)
class Moment:
    """Energy U, longitudinal c*p, Pi=Pparallel-Pperp (all eV per H)."""
    U:float
    cPz:float
    Pi:float

    @classmethod
    def from_sky(cls,photons):
        photons.check()
        w=photons.NperH*photons.E
        return cls(float(w.sum()),float(w@photons.mu),
                   float(w@(.5*(3*photons.mu**2-1))))

    def positive_cone(self,tol=5e-14):
        if not all(math.isfinite(x) for x in (self.U,self.cPz,self.Pi)):
            return False
        if self.U<0:return False
        if self.U==0:return self.cPz==0 and self.Pi==0
        return (-self.U/2-tol*self.U<=self.Pi<=self.U*(1+tol)
                and 3*self.cPz**2<=self.U*(self.U+2*self.Pi)+tol*self.U**2)


def positive_three_atom(moment:Moment,energy_eV=30.):
    """Sharp constructive Hausdorff [mu=-1,1] moment realization.

    m=<mu>=cPz/U; v=<mu²>=(U+2Pi)/(3U);  m²<=v<=1.
    lambda=(v-m²)/(1-m²). Mass at +/-1 is lambda*(1+/-m)/2,
    remainder 1-lambda sits at mu=m. E chosen for counterexample ONLY.
    This is NOT a licensed Case-A physical photon emission spectrum.
    """
    if (not moment.positive_cone(tol=1e-13) or
        not math.isfinite(energy_eV) or energy_eV<=0):
        raise ValueError("NONREALIZABLE_QMU_OR_PHOTON_ENERGY")
    if moment.U==0:return c13.PhotonCloud.empty()
    U=moment.U;m=moment.cPz/U;v=(U+2*moment.Pi)/(3*U)
    if abs(m)>=1-1e-14:
        if abs(v-1)>2e-13:raise ValueError("NO_ONE_POLE_LIMIT")
        return c13.PhotonCloud(np.array([energy_eV]),
              np.array([1. if m>=0 else -1.]),np.array([U/energy_eV]))
    lam=(v-m*m)/(1-m*m)
    if not -1e-13<=lam<=1+1e-13:
        raise ValueError("NEGATIVE_CONSTRUCTED_QUADRATURE")
    lam=min(1.,max(0.,lam))
    E=np.full(3,energy_eV)
    mus=np.array([-1.,1.,m])
    weights=U*np.array([lam*(1-m)/2,lam*(1+m)/2,1-lam])/energy_eV
    sky=c13.PhotonCloud(E,mus,weights)
    check=Moment.from_sky(sky)
    if max(abs(check.U-U),abs(check.cPz-moment.cPz),
           abs(check.Pi-moment.Pi))>1e-11*U:
        raise ArithmeticError("POSITIVE_RECONSTRUCTION_NOT_MOMENT_EXACT")
    return sky


def photon_species_event(g0,g1,p0,p1,mu,dt,receipt):
    """Independently reconstruct original C10 implicit-midpoint absorptions."""
    if not (math.isfinite(dt) and dt>0 and len(mu)==len(p0.E)):
        raise ValueError("MISMATCHED_EVENT_DIRECTION_CLOCK")
    neutral=(g0.neutral+g1.neutral)*.5
    dtc=c13.C_CGS*dt
    tau=dtc*(p0.sigma@neutral)
    factor=np.ones_like(tau)
    np.divide(-np.expm1(-tau),tau,out=factor,where=tau>0)
    A=(p0.count*factor)[:,None]*(dtc*p0.sigma*neutral[None,:])
    species=A.sum(axis=0)
    if np.max(abs(species-np.array(receipt["species_events_cm3"])))>3e-12*g0.nH:
        raise ArithmeticError("ORIGINAL_C10_EVENT_SPECIES_MISMATCH")
    E=(A*p0.E[:,None]).sum(axis=0)
    pz=(A*(p0.E*mu)[:,None]).sum(axis=0)
    pi=(A*(p0.E*.5*(3*mu**2-1))[:,None]).sum(axis=0)
    loss=p0.count-p1.count
    if (abs(float(loss@p0.E)-sum(E))>4e-12*g0.nH
        or abs(float((loss*p0.E)@mu)-sum(pz))>4e-12*g0.nH):
        raise ArithmeticError("C10_EVENT_PHOTON_4_MOMENT_DISCREPANCY")
    binding=float(species@c13.c10.c9.BIND)
    gas_delta=g1.thermal_eV_cm3-g0.thermal_eV_cm3
    if abs(sum(E)-binding-gas_delta)>4e-12*g0.nH:
        raise ArithmeticError("PHOTO_HEATING_BINDING_TRANSFER_NOT_CLOSED")
    return {"species_counts_cm3":species.tolist(),"species_energy_eV_cm3":E.tolist(),
            "species_cPz_eV_cm3":pz.tolist(),"species_Pi_eV_cm3":pi.tolist(),
            "Q0_to_gas_eV_cm3":float(sum(E)),
            "required_material_cPz_eV_cm3":float(sum(pz)),
            "thermal_heating_eV_cm3":float(gas_delta),
            "chemical_binding_eV_cm3":binding}


def native_C11_Qmu(gas,cloud,dt,provider=None):
    """Actual original C11 accepted Case-A chemistry, true 3 absorber channels.

    Returned 'material recoil' is required impulse, not a baryon velocity.
    Escaped Case-A radiation remains ENERGY-ONLY, no invented N/mu/Pi.
    """
    if provider is None:provider=c13.CaseARates()
    cloud.check();gas.check()
    p0=cloud.to_native_chemistry(gas.nH)
    original=c13.c11.ReservoirState(gas,p0)
    expected,source_receipt=c13.c11.strang_step(original,dt,provider)
    g1,p1,r1=c13.c10.midpoint_step(gas,p0,dt/2)
    g2,recomb=c13.c11.rec_step(g1,dt,provider)
    g3,p3,r3=c13.c10.midpoint_step(g2,p1,dt/2)
    if not np.array_equal(p3.count,expected.photons.count):
        raise ArithmeticError("C11_SPLIT_REPLAY_NOT_IDENTICAL")
    for value in ("nHI","nHeI","nHeII","thermal_eV_cm3"):
        if abs(getattr(g3,value)-getattr(expected.gas,value))>2e-14*gas.nH:
            raise ArithmeticError("C11_GAS_SPLIT_DIFFERENCE_"+value)
    parts=(photon_species_event(gas,g1,p0,p1,cloud.mu,dt/2,r1),
           photon_species_event(g2,g3,p1,p3,cloud.mu,dt/2,r3))
    absorbed=sum(v["Q0_to_gas_eV_cm3"] for v in parts)
    impulse=sum(v["required_material_cPz_eV_cm3"] for v in parts)
    escaped=float(recomb["escape_eV_cm3"])
    newgas=(g3.thermal_eV_cm3+g3.binding_eV_cm3)
    oldgas=(gas.thermal_eV_cm3+gas.binding_eV_cm3)
    balance=absorbed-escaped-(newgas-oldgas)
    if abs(balance)>6e-12*gas.nH:
        raise ArithmeticError("C11_CASEA_RADIATION_MATERIAL_ESCROW")
    Nres=(expected.photons.n+g3.ne+expected.recomb_electrons_cm3-
          (p0.n+gas.ne))/gas.nH
    if abs(Nres)>1e-11:raise ArithmeticError("C11_PHOTON_ELECTRON_NUMBER")
    return {"schema":"rei.c16.actual_C11_Q0_photo_Qz_recoil_required.v1",
            "proper_dt_s":dt,
            "first_photo":parts[0],"last_photo":parts[1],
            "photo_absorbed_energy_eV_perH":absorbed/gas.nH,
            "required_baryon_recoil_cPz_eV_perH":impulse/gas.nH,
            "true_CaseA_scalar_escape_eV_perH":escaped/gas.nH,
            "CaseA_recomb_event_counts_perH":
                (np.array(recomb["recomb_events_cm3"])/gas.nH).tolist(),
            "gas_energy_increase_eV_perH":(newgas-oldgas)/gas.nH,
            "energy_exchange_residual_eV_perH":balance/gas.nH,
            "electron_photon_ledger_residual_perH":Nres,
            "CaseA_escape_Qz_and_Pi":"NOT_DETERMINED_BY_ORIGINAL_OWNER",
            "baryon_velocity_recoil":"NOT_EVOLVED_BY_C11_CASEA"}


def C15_escrow_and_escape_bound(p:c15.Parameters,nsteps=32):
    """Replay C15 source geometry exactly and inspect stellar, chemistry escrows.

    Escape Pi range is a *positive photon realizability* outer bound, not a
    proof of actual Case A spectral emission or of full nonlinear GR error.
    """
    m=c15.EinsteinBoltzmann(p)
    state=m.initial()
    N0=state.gas_and_UV.number_ledger()
    U0=state.gas_and_UV.energy_ledger()
    dx=c13.stable_dx(state.a,c13.STOP)/nsteps
    history=[]
    nerr=Eerr=flux=Eesc=total_b=0.
    for i in range(nsteps):
        target=c13.STOP if i==nsteps-1 else m.a0*math.exp((i+1)*dx)
        before=state
        state,row=m.step(state,target,feedback=True,compress=True)
        v=state.gas_and_UV
        old=before.gas_and_UV
        born=v.source_E_eV_perH-old.source_E_eV_perH
        rec=v.escape_E_eV_perH-old.escape_E_eV_perH
        if born<-1e-12 or rec<-1e-12:
            raise ArithmeticError("NEGATIVE_OWNER_MD14_OR_CASEA_ENERGY")
        moment=Moment.from_sky(v.photons)
        if not moment.positive_cone():
            raise ArithmeticError("C15_PRODUCED_NONPOSITIVE_ANGULAR_STATE")
        pi_from_sigma=row["Pi_UV"]/(v.gas.nH*EV_CM3_TO_PA)
        if abs(moment.Pi-pi_from_sigma)>2e-11*max(moment.U,1e-20):
            raise ArithmeticError("PHOTON_PRESSURE_QUADRUPOLE_OWNER_MISMATCH")
        nerr=max(nerr,abs(v.number_ledger()-N0))
        Eerr=max(Eerr,abs(v.energy_ledger()-U0))
        flux=max(flux,abs(moment.cPz))
        Eesc=max(Eesc,v.escape_E_eV_perH)
        total_b+=abs(state.b-before.b)
        history.append({"a":state.a,"t_s":v.elapsed_s,
              "actual_Einstein_H_per_s":row["H"],
              "Sigma":row["Sigma"],"orientation":row["orientation"],
              "emitted_MD14_energy_this_step_eV_perH":born,
              "formal_emitter_energy_loss_eV_perH":-born,
              "emitted_CaseA_escape_energy_this_step_eV_perH":rec,
              "total_CaseA_escape_energy_eV_perH":v.escape_E_eV_perH,
              "UV_U_eV_perH":moment.U,
              "UV_cPz_eV_perH":moment.cPz,
              "UV_Pi_eV_perH":moment.Pi,
              "actual_UV_Pi_Pa":row["Pi_UV"],
              "positive_radiation_moment_cone":moment.positive_cone(),
              "scalar_CaseA_future_Pi_source":"UNKNOWN"})
    if Eerr>5e-11 or nerr>5e-12:
        raise ArithmeticError("C15_ASTRO_EMITTER_ENERGY_ESCROW_LEDGER")
    model=c13.Scenario(c13.ROOT)
    proper_nHmax=model.nh/m.a0**3
    # Fixed-background, source-free-propagation upper estimate: all escape
    # radiation remains, no future absorption, and maximum anisotropic gain
    # per Killing ray bounded by exp(2 sum |Delta b|).
    esc_max_pa=proper_nHmax*Eesc*EV_CM3_TO_PA*math.exp(2*total_b)
    dt=state.gas_and_UV.elapsed_s
    # Conditional certified-floor input: require positive smooth expanding
    # H(t) to remain above 99% of the minimum of the sampled solved H.
    # This is an explicitly stated *a posteriori* assumption, not a theorem.
    Hfloor=.99*min(z["actual_Einstein_H_per_s"] for z in history)
    if not Hfloor>0:raise ArithmeticError("NONEXPANDING_SOURCE_CLOCK")
    bound=math.sqrt(3)*c15.KAPPA*esc_max_pa*dt/Hfloor
    # A formal emission debit is not the evolving stellar mass-energy
    # solution. It supplies a necessary MINIMUM reservoir energy, not a
    # causal emitting-star model. Its missing gravitational subtraction has
    # a conditional frozen-field Hamiltonian budget.
    emitted_total=state.gas_and_UV.source_E_eV_perH
    emitter_density_budget=proper_nHmax*emitted_total*EV_CM3_TO_PA
    missing_H2_fraction_envelope=(c15.KAPPA*emitter_density_budget/Hfloor**2)
    return {"schema":"rei.c16.actual_C15_stellar_emitter_escrow_CaseA_positive_Pi_range.v1",
            "parameters":dict(p.__dict__),"nsteps":nsteps,
            "history":history,"end":history[-1],
            "max_real_photochemical_energy_ledger_eV_perH":Eerr,
            "max_real_photochemical_number_ledger_perH":nerr,
            "max_reflection_symmetric_UV_flux_abs_eV_perH":flux,
            "CaseA_escape_cumulative_energy_eV_perH":Eesc,
            "total_original_MD14_stellar_emission_energy_eV_perH":emitted_total,
            "formal_minimum_stellar_reservoir_energy_eV_perH":emitted_total,
            "source_energy_over_proton_rest_mass":emitted_total/938272081.3,
            "conditional_missing_emitter_H2_fraction_upper":missing_H2_fraction_envelope,
            "formal_unintegrated_stellar_emitter_reservoir":
                "external MD14 source emitter debit only, not Einstein matter state",
            "CaseA_missing_Pi_at_emission_eV_perH_interval":[-Eesc/2,Eesc],
            "escape_radiation_energy_density_envelope_Pa":esc_max_pa,
            "linearized_omitted_escape_stress_absolute_delta_Sigma_bound":bound,
            "assumed_H_floor_per_s_for_response":Hfloor,
            "bound_scope":"fixed computed expanding geometry, H>=0.99 min sampled H, positive free-streaming escape photons; NOT a nonlinear perturbed Einstein-system theorem",
            "physics_gate":"CASEA_SPECTRUM_ANGULAR_MOMENTS_NOT_ADMITTED"}
