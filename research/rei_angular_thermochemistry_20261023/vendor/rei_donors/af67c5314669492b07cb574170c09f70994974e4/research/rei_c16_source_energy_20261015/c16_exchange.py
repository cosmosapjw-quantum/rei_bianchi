#!/usr/bin/env python3
"""C16.0: actual C15 MD14 HHe open-source energy/stress work and momentum audit.

No physics source is silently invented. This auditor executes C15's exact
Einstein/gamma+nu/UV photo gas solver and measures all already-owned external
stellar emission and escaped Case-A photon energy transfers, plus an
INDEPENDENT geometric shear/adiabatic work integral using actual DOP853
dense-output trajectory.

Physical interpretation: these are open local energy/momentum fluxes Q^mu;
stellar/escape reservoirs are not part of the original Friedmann T_ab and
cannot be declared automatically physical gravitating stellar populations.
This is a constructive C16 conservation interface, not full ∇T_total=0.
"""
from __future__ import annotations
import math
from pathlib import Path
import sys
import time
from functools import lru_cache
import numpy as np
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"research/rei_c15_two_way_shear_20261015"))
from c15_coupled import (Coupled,Config,NativeStellarSource,Scenario,
                        stable_dx,START,STOP,KAPPA,THOMSON_RATE,EV_CM3_TO_PA,
                        SourceState,PhotonCloud,c10)
from short_interval import initial_gas
from dynamic import KB_EV_K

@lru_cache(maxsize=3)
def gauss_rule(order):
    if order not in (4,8,16):
        raise ValueError("source-domain Gauss order")
    a,b=leggauss(order)
    a.setflags(write=False);b.setflags(write=False)
    return a,b

def formula_energies(row, fHe):
    """Species exact original C11 thresholds, reconstructed from saved state."""
    xh=row["x_HII"];xh2=row["x_HeII"];xh3=row["x_HeIII"]
    xe=row["x_e_perH"]; T=row["Tgas_K"]
    temperature=1.5*KB_EV_K*T*(1+fHe+xe)
    binding=(c10.c9.BIND[0]*xh+
             fHe*c10.c9.BIND[1]*(xh2+xh3)+
             fHe*c10.c9.BIND[2]*xh3)
    return temperature,binding

def perH_source_balance(history,fHe):
    base=None;residuals=[];readbacks=[]
    for row in history:
        th,bind=formula_energies(row,fHe)
        uv=row["photon_U_eV_perH"]
        star=-row["source_E_eV_perH"]
        escaped=row["escape_E_eV_perH"]
        work=row["geometry_work_eV_perH"]
        energy=uv+th+bind+star+escaped+work
        if base is None:base=energy
        residuals.append(energy-base)
        readbacks.append({
            "a":row["a"],"photon_eV_perH":uv,
            "gas_thermal_eV_perH":th,"gas_binding_eV_perH":bind,
            "stellar_emission_source_eV_perH":-star,
            "CaseA_escaped_external_eV_perH":escaped,
            "measured_expansion_work_eV_perH":work,
            "cumulative_open_exchange_source_eV_perH":(-star)-escaped,
            "open_energy_balance_residual_eV_perH":energy-base})
    return readbacks, max(abs(z) for z in residuals)

def flux_reconstruction(history,nh0):
    """Quantify unmatched external energy flux referenced to initial emission 0.

    For any external comoving source S_E per H, physical energy input per
    volume is nH(a)*dS_E/dt. To treat stellar+escaped terms in Einstein H
    one would need source-specific stellar EOS and the angular/energy history
    of escaped Case-A photons, including their distinct gravitational source.
    """
    src=[]
    for old,new in zip(history,history[1:]):
        dt=new["elapsed_s"]-old["elapsed_s"]
        if dt<=0:raise ValueError("NONPOSITIVE_C15_RECEIVER_TIME")
        a_mid=math.sqrt(old["a"]*new["a"])
        nh=nh0/a_mid**3
        delta_emission=new["source_E_eV_perH"]-old["source_E_eV_perH"]
        delta_escape=new["escape_E_eV_perH"]-old["escape_E_eV_perH"]
        delta_external=delta_emission-delta_escape
        external_power=nh*EV_CM3_TO_PA*delta_external/dt
        if not math.isfinite(external_power):
            raise ValueError("NONFINITE_EXTERNAL_OPEN_EINSTEIN_SOURCE")
        src.append({
            "a_mid":a_mid,"dt_s":dt,"delta_MD14_emitted_eV_perH":delta_emission,
            "delta_CaseA_escape_eV_perH":delta_escape,
            "open_net_external_energy_in_eV_perH":delta_external,
            "external_power_J_m3_s":external_power,
            "open_external_Q_over_H_rho_rad":external_power/max(
                new["H_per_s"]*new["source_CBMRho_J_m3"],1e-300),
            "unmodeled_baryon_momentum_transfer":"REFLECTION_SYMMETRIC_ZERO_DIPOLE_ONLY_IF_VERIFIED",
        })
    return src

class WorkAuditor(Coupled):
    """Actual C15 RHS and full source, with independent dense Gauss work check."""

    def __init__(self,cfg,source,order=8):
        super().__init__(cfg,source)
        self.work_order=order
        self.raw_receipts=[]
        self.admitted_receipts=[]
        self.actual_momentum_receipts=[]
        initial_weighted_E=float(np.dot(source.weights,source.energy))
        initial_odd_E=float(np.dot(source.weights*source.energy,source.mu))
        initial_odd_N=float(np.dot(source.weights,source.mu))
        if (not np.all(source.weights>=0) or
            abs(initial_odd_E)>2e-13*initial_weighted_E or
            abs(initial_odd_N)>2e-13):
            raise ValueError("C16_REFLECTION_SYMMETRY_REQUIRES_ZERO_INITIAL_PHOTON_DIPOLE")
    def drift_segment(self,micro,y,a_end):
        # First execute exact C15 source and photon chemistry operator, no
        # duplicate source/material model. Second solve is an independent
        # integration of the same GR RHS only for dense-trajectory quadrature.
        before_b=float(y[1]);a0=micro.a
        after,y1,dt=super().drift_segment(micro,y,a_end)
        x0=math.log(a0);x1=math.log(a_end)
        sol=solve_ivp(lambda x,state:self.rhs(x,state,micro,before_b),
                      (x0,x1),y,method="DOP853",rtol=2e-12,atol=2e-14,
                      dense_output=True,t_eval=[x1])
        if not sol.success or not np.isfinite(sol.y).all():
            raise RuntimeError("DENSE_SOURCE_CLOCK_INDEPENDENT_REPLAY_FAILED")
        # Replayed *binary64* state should match C15 original endpoint.
        if np.max(abs(sol.y[:,-1]-y1))>2e-13:
            raise RuntimeError("SOURCE_OWNER_GRAVITY_REPLAY_NOT_IDENTICAL")
        nodes,weights=gauss_rule(self.work_order)
        dx=stable_dx(a0,a_end)
        positions=x0+(nodes+1)*.5*(x1-x0)
        states=sol.sol(positions)
        oldcloud=micro.photons
        uthermal_before=micro.gas.thermal_eV_cm3/micro.gas.nH
        integrals=np.empty_like(nodes)
        photon_work_integrand=np.empty_like(nodes)
        for i,xx in enumerate(positions):
            q=self.quantities(float(xx),states[:,i],micro,before_b)
            delta_x=float(xx)-x0
            b=float(states[1,i])
            sky=oldcloud.drift(delta_x,b-before_b)
            part_energy=sky.E*sky.NperH
            U_ph=float(np.sum(part_energy))
            P2=float(np.dot(part_energy,(3*sky.mu**2-1)/2))
            alpha=q["s"]/q["h"]
            photon_work_integrand[i]=U_ph+2*alpha*P2
            thermal_work_integrand=2*uthermal_before*math.exp(-2*delta_x)
            integrals[i]=photon_work_integrand[i]+thermal_work_integrand
        W_adaptive=.5*dx*float(np.dot(weights,integrals))
        W_phot=.5*dx*float(np.dot(weights,photon_work_integrand))
        W_th=uthermal_before*(-math.expm1(-2*dx))
        # Different numerical/analytic paths: original exact photon Killing
        # endpoints, independent quadrature of local energy and signed Pi.
        direct_phot=oldcloud.energy-after.photons.energy
        direct_th=uthermal_before-after.gas.thermal_eV_cm3/after.gas.nH
        direct_work=direct_phot+direct_th
        residual_phot=W_phot-direct_phot
        residual_total=W_adaptive-direct_work
        ratio=abs(residual_total)/max(abs(direct_work),1e-18)
        if (not math.isfinite(residual_total) or
              abs(residual_phot)>4e-11 or abs(residual_total)>4e-11 or
              abs(W_th-direct_th)>4e-11):
            raise RuntimeError(f"GRAVITATIONAL_P_TENSOR_WORK_MISMATCH {residual_total}, {residual_phot}, {ratio}")
        self.raw_receipts.append({
            "a0":a0,"a1":a_end,"xspan":dx,"proper_dt_s":dt,
            "start_C15_original_b":before_b,"end_C15_b":float(y1[1]),
            "independent_Gauss_order":self.work_order,
            "photon_exact_Killing_work_eV_perH":direct_phot,
            "photon_covariant_integrated_work_eV_perH":W_phot,
            "gas_thermal_exact_adiabatic_work_eV_perH":direct_th,
            "gas_thermal_integrated_work_eV_perH":W_th,
            "combined_Killing_plus_thermal_work_eV_perH":direct_work,
            "independent_covariant_pressure_shear_integral_eV_perH":W_adaptive,
            "shear_pressure_work_error_eV_perH":residual_phot,
            "combined_physical_pressure_work_error_eV_perH":residual_total})
        return after,y1,dt
    def step(self,micro,y,a_end):
        start=len(self.raw_receipts)
        old_work=micro.geometry_work_eV_perH
        out,yy,info=super().step(micro,y,a_end)
        got=self.raw_receipts[start:]
        if len(got)<2:
            raise RuntimeError("PICARD_ACCEPTED_HALFSTEP_RECEIPT_MISSING")
        # C15 Picard re-evaluates second drift on a trial source; only LAST
        # attempt is actually retained. Discard rejected receipt branches.
        accepted=(got[0],got[-1])
        measured=sum(z["combined_Killing_plus_thermal_work_eV_perH"]
                     for z in accepted)
        actual=out.geometry_work_eV_perH-old_work
        if abs(measured-actual)>3e-12:
            raise RuntimeError("C15_WORK_RECEIPTS_NOT_MATCH_ACCEPTED_SOURCE")
        self.admitted_receipts.extend(accepted)
        self.raw_receipts=self.raw_receipts[:start]
        # The user-locked non-tilted, reflection symmetric LRS source has no
        # spatial photon momentum transfer Q_z. An arbitrary tilted or dipolar
        # emissivity needs a separate Einstein momentum/baryon recoil owner.
        pUV=float(np.dot(out.photons.NperH*out.photons.E,out.photons.mu))
        pN=float(np.dot(out.photons.NperH,out.photons.mu))
        uv_energy=out.photons.energy
        norm=max(uv_energy,1e-60)
        if abs(pUV)/norm>2e-12 or abs(pN)/max(out.photons.number,1e-60)>2e-12:
            raise RuntimeError("C16_NON_TILTED_MOMENTUM_TRANSFER_CANNOT_IGNORE_REAL_DIPOLE")
        n=self.n
        odd_pstf=max(abs(float(yy[3+j*n+1])) for j in range(4))
        if odd_pstf>2e-12:
            raise RuntimeError("C16_ANTISYMMETRIC_BASS_PSTF_COLLISION_INVALID")
        self.actual_momentum_receipts.append({
            "a":out.a,"uv_rad_energy_flux_P1_eV_perH":pUV,
            "number_P1_perH":pN,
            "max_E_or_N_PSTF_dipole":odd_pstf,
            "ratio_uv_flux_to_energy":abs(pUV)/norm})
        return out,yy,info
    def run(self):
        science=super().run()
        fHe=initial_gas(self.model,START).nHe/initial_gas(self.model,START).nH
        rows,err=perH_source_balance(science["history"],fHe)
        flux=flux_reconstruction(science["history"],self.model.nh)
        work=sum(r["combined_Killing_plus_thermal_work_eV_perH"]
                 for r in self.admitted_receipts)
        if len(self.admitted_receipts)!=2*self.cfg.nstep:
            raise RuntimeError("C16_INCOMPLETE_PHYSICAL_HALFSTEP_WORK_EVIDENCE")
        if abs(work-science["endpoint"]["geometry_work_eV_perH"])>4e-12:
            raise RuntimeError("C16_TOTAL_PHYSICAL_PRESSURE_WORK_NOT_ANCHORED")
        if err>2e-11:
            raise RuntimeError("EXTERNAL_MD14_C11_ACTUAL_LEDGER_FAILED")
        result=dict(science)
        result["C16_scoped_open_Q_energy_audit"]={
            "schema":"rei.C16.stellar_HHe_UV_physical_Q_open_energy_and_shear_work.v1",
            "source_model":"real native MD14 photons, actual C11 CaseA HHe, BASS photon neutrino Einstein backreaction",
            "claim_boundary":"physical photon+gas+stellar-emission-debit+escaped CaseA account balanced per H. Total covariant Einstein stress-energy NOT CLOSED without external reservoir EOS/history.",
            "max_open_source_energy_ledger_abs_eV_perH":err,
            "max_independent_GL_pressure_shear_work_error_eV_perH":max(
                abs(r["combined_physical_pressure_work_error_eV_perH"])
                for r in self.admitted_receipts),
            "max_independent_GL_photon_pressure_shear_work_error_eV_perH":max(
                abs(r["shear_pressure_work_error_eV_perH"])
                for r in self.admitted_receipts),
            "number_accepted_source_halfsteps":len(self.admitted_receipts),
            "actual_stellar_energy_emitted_eV_perH":science["endpoint"]["source_E_eV_perH"],
            "actual_CaseA_escaped_energy_eV_perH":science["endpoint"]["escape_E_eV_perH"],
            "signed_external_net_eV_perH":science["endpoint"]["source_E_eV_perH"]-science["endpoint"]["escape_E_eV_perH"],
            "observed_ionizing_UV_energy_end_eV_perH":science["endpoint"]["photon_U_eV_perH"],
            "actual_cumulative_pressure_work_eV_perH":work,
            "initial_source_energy_zero":True,
            "external_Q_is_gravitationally_owned_by_stellar_plus_escaped_radiation":"NOT_IMPLEMENTED",
            "actual_ionizing_photon_nonzero_gravity_loop":"YES",
            "angular_axis_reflection_source_momentum_dipole": {
              "assumption":"strict non-tilted reflection-symmetric radiation and emission",
              "max_ratio_uv_energy_flux_to_energy":max(r["ratio_uv_flux_to_energy"] for r in self.actual_momentum_receipts),
              "max_abs_uv_P1_eV_perH":max(abs(r["uv_rad_energy_flux_P1_eV_perH"]) for r in self.actual_momentum_receipts),
              "max_BASS_PSTF_gamma_nu_dipole":max(r["max_E_or_N_PSTF_dipole"] for r in self.actual_momentum_receipts),
              "baryon_momentum_recoil_for_any_tilt_or_dipolar_source":"NOT_IMPLEMENTED"
            },
            "independent_momentum_checks":self.actual_momentum_receipts,
            "independent_perH_energy_tables":rows,
            "explicit_source_exchange_flux":flux,
            "independent_accepted_half_step_work_table":self.admitted_receipts,
            "scientific_admission":"NOT_ISSUED"}
        return result
