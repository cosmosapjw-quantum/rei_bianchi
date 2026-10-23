#!/usr/bin/env python3
"""C15 source-locked SHORT-INTERVAL coupled Bianchi-I shear + UV H/He chemistry.

Physics actually connected:
  C13 REAL native MD14 UV birth and photon Killing drift and Case-A HHe chemistry,
  C14 ORIGINAL BASS PSTF E/N massless gamma and neutrino multipoles + photon Thomson,
  Einstein H and signed shear evolving from Pi_gamma+Pi_nu+Pi_UV.
Unlike C13, evolving shear is fed back into the *next UV photon characteristic,
source proper clock, gas expansion and chemistry* on every macro step.

Sharp scope firewall: the C13 z~4 H/He gas initial conditions are manufactured;
the UV stellar energy supply/escaped recombination photons are externally sourced,
not a closed Einstein total T_ab reservoir. We do NOT claim covariant total
energy-momentum conservation with those external reservoirs, polarization E/B,
matter viscous/kinetic closure or whole-z20->4 reionization.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
import math,sys,hashlib,json
import numpy as np
from scipy.integrate import solve_ivp

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"research/rei_c13_live_source_20261015"))
sys.path.insert(0,str(ROOT/"research/rei_c14_thomson_receiver_20261015"))
from short_interval import (Scenario,NativeStellarSource,SourceState,PhotonCloud,
    initial_gas,emit_half,reaction_step,START,STOP,stable_dx,
    C_CGS,THOMSON_CGS,EV_CM3_TO_PA,c10,CaseARates,Background,Family)
from dynamic_thomson import (_cached_source_angular_operators,omega_gamma_fraction,
    validate_source_sha, KAPPA, A_RAD)
from coalesce import reduce_age_cohorts

NATURE="EXTERNAL_SOURCE_EXCHANGE_AND_C11_GAS_BBNLIKE_IC_NOT_FULL_GR_COMOVING_TENSOR"
TCMB=2.7255
L_SUPPORTED=(4,8,12)
THOMSON_RATE=C_CGS*THOMSON_CGS

@dataclass(frozen=True)
class Config:
    legacy_q_for_locked_source:float=0.
    kappa_gamma:float=.2
    kappa_nu:float=.2
    L:int=8
    gravity_feedback:bool=True
    uv_stress_in_shear:bool=True
    thomson:bool=True
    nstep:int=32
    compression:bool=True
    def __post_init__(self):
        if self.legacy_q_for_locked_source not in (0.,-.005,.005,-.01,.01):
            raise ValueError("HISTORICAL_SOURCE_BOUNDARY_ADAPTER_INVALID")
        if self.L not in L_SUPPORTED or self.nstep not in (8,16,32,64,128):
            raise ValueError("FINITE_EXECUTABLE_SOURCE_GRID_CONTRACT")
        if not all(math.isfinite(x) and -.5<=x<=.5
                   for x in (self.kappa_gamma,self.kappa_nu)):
            raise ValueError("POSITIVE_BASS_INITIAL_P2_DISTRIBUTION_REQUIRED")
        if not self.gravity_feedback:
            raise ValueError("C15_REQUIRE_ACTIVE_EINSTEIN_SHEAR_FEEDBACK")

def source_hash(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for part in iter(lambda:f.read(1<<20),b""):h.update(part)
    return h.hexdigest()

class Coupled:
    def __init__(self,cfg:Config,source:NativeStellarSource):
        self.cfg=cfg
        self.source=source
        self.model=Scenario(ROOT)
        self.bg0=Background(Family(cfg.legacy_q_for_locked_source))
        self.provider=CaseARates()
        self.n=cfg.L+1
        self.AE,self.AN,self.damp=_cached_source_angular_operators(cfg.L)
        mus,_=np.polynomial.legendre.leggauss(64)
        self.angular_positive_basis=(
            np.polynomial.legendre.legvander(mus,cfg.L)*
            np.arange(1,2*cfg.L+2,2)[None,:])
        self.frac=omega_gamma_fraction(self.model)
        self.H0=self.model.h0
        self.Href=self.bg0.href
        self.om=self.model.om
        self.ol=self.model.ol
        self.og=self.frac["Omega_gamma"]
        self.on=self.frac["Omega_nu"]
        self.rho_crit=self.H0*self.H0/KAPPA
        self.eval_count=0
        self.max_uv_hamiltonian_fraction=0.
        self.max_ultraviolet_pi=0.
    def init_state(self):
        q=self.cfg.legacy_q_for_locked_source
        g=initial_gas(self.model,START)
        payload=SourceState(START,g,PhotonCloud.empty())
        original=self.bg0.at_a(START)
        b=original["b"];s=original["shear_s_per_s"]
        y=np.zeros(4+4*self.n)  # last slot independently integrated Thomson optical depth
        y[:3]=[0.,b,s/self.Href]
        for i,k in enumerate((self.cfg.kappa_gamma,self.cfg.kappa_gamma,
                               self.cfg.kappa_nu,self.cfg.kappa_nu)):
            y[3+i*self.n]=1.
            y[3+i*self.n+2]=k/5
        return payload,y
    def quantities(self,x,y,micro:SourceState,reference_b:float):
        a=math.exp(x)
        b=float(y[1]);s=self.Href*float(y[2])
        n=self.n
        eg,ng,en,nn=(y[3+i*n:3+(i+1)*n] for i in range(4))
        if (not np.isfinite(y).all() or not (START*(1-1e-12)<=a<=STOP*(1+1e-12))
              or min(eg[0],ng[0],en[0],nn[0])<=0):
            raise ValueError("INVALID_C15_GRAVITY_RADIATION_STATE")
        dxa=math.log1p((a-micro.a)/micro.a)
        if dxa< -1e-11:raise ValueError("INCONSISTENT_C15_SEGMENT_OWNER_CLOCK")
        dx=max(0.,dxa)
        if micro.photons.packet_count:
            photons=micro.photons.drift(dx,b-reference_b)
            energy_perH=photons.NperH*photons.E
            uv_rho=micro.gas.nH*math.exp(-3*dx)*float(energy_perH.sum())*EV_CM3_TO_PA
            uv_pi=micro.gas.nH*math.exp(-3*dx)*float(
                energy_perH @ ((3*photons.mu*photons.mu-1)/2))*EV_CM3_TO_PA
        else:
            uv_rho=uv_pi=0.
        thermal=micro.gas.thermal_eV_cm3*math.exp(-5*dx)*EV_CM3_TO_PA
        binding=micro.gas.binding_eV_cm3*math.exp(-3*dx)*EV_CM3_TO_PA
        cbm_rho=self.rho_crit*(self.og*eg[0]+self.on*en[0])/a**4
        cbm_pi=self.rho_crit*(self.og*eg[2]+self.on*en[2])/a**4
        h2=self.H0**2*(self.om/a**3+self.ol+
                       (self.og*eg[0]+self.on*en[0])/a**4)+s*s
        # External UV/gas thermo/atomic excitation reservoirs perturb H;
        # stellar photon emission and escaped recombination have no dynamical
        # source energy closure here. This H is a scoped Einstein constraint
        # with explicit EXTERNAL_Q gap, not a conserved full cosmology.
        h2+=KAPPA*(uv_rho+thermal+binding)
        if not math.isfinite(h2) or h2<=0:raise ValueError("NEGATIVE_C15_H")
        h=math.sqrt(h2)
        Hnorm=h/self.Href
        ne=micro.gas.ne*math.exp(-3*dx)
        if ne<0:raise ValueError("NEGATIVE_ACTUAL_C13_ELECTRON_DENSITY")
        return dict(a=a,b=b,s=s,h=h,eg=eg,ng=ng,en=en,nn=nn,
          uv_rho=uv_rho,uv_pi=uv_pi,thermal=thermal,binding=binding,
          cbm_rho=cbm_rho,cbm_pi=cbm_pi,ne=ne,Gamma=ne*THOMSON_RATE,
          Sigma=math.sqrt(3)*abs(s)/h,
          epsilon_sigma=(1 if s>0 else -1 if s<0 else 0),
          uv_hamiltonian_fraction=KAPPA*uv_rho/h2)
    def rhs(self,x,y,micro,reference_b):
        self.eval_count+=1
        q=self.quantities(x,y,micro,reference_b)
        n=self.n;s=q["s"];h=q["h"];alpha=s/h
        pressure=q["cbm_pi"]+(q["uv_pi"] if self.cfg.uv_stress_in_shear else 0.)
        ds_axis_dx=-3*y[2]+KAPPA*pressure/(self.Href*h)
        t=self.Href/h
        d_b=alpha
        eg,ng,en,nn=(q[v] for v in ("eg","ng","en","nn"))
        rate=q["Gamma"]/h if self.cfg.thomson else 0.
        dEg=alpha*self.AE@eg-rate*self.damp*eg
        dNg=alpha*self.AN@ng-rate*self.damp*ng
        dEn=alpha*self.AE@en
        dNn=alpha*self.AN@nn
        return np.r_[t,d_b,ds_axis_dx,dEg,dNg,dEn,dNn,q["Gamma"]/h]
    def drift_segment(self,micro:SourceState,y,a_end):
        a0=micro.a
        if not a0<a_end<=STOP:raise ValueError("C15_SEGMENT_NOT_ORDERED")
        x0=math.log(a0);x1=math.log(a_end)
        # At x0 reconstruct start source sky b0 (only for current single drift).
        start_b=float(y[1])
        solution=solve_ivp(lambda x,yy:self.rhs(x,yy,micro,start_b),
           (x0,x1),y,method="DOP853",rtol=2e-12,atol=2e-14,
           t_eval=[x1])
        if not solution.success:
            raise RuntimeError("C15_COUPLED_EINSTEIN_ODE_FAILED:"+solution.message)
        yy=solution.y[:,-1]
        dt=(yy[0]-y[0])/self.Href
        db=yy[1]-y[1]
        if not(math.isfinite(dt) and dt>0):
            raise ValueError("C15_COUPLED_CLOCK_FAILURE")
        # Actual C13 photon Killing map and proper gas expansion + ledger owner.
        from short_interval import SourceState
        oldcloud=micro.photons
        nextcloud=oldcloud.drift(stable_dx(a0,a_end),db)
        f=(a0/a_end)**3
        g=micro.gas
        nextgas=c10.Gas(g.nH*f,g.nHe*f,g.nHI*f,g.nHeI*f,g.nHeII*f,
                        g.thermal_eV_cm3*f*(a0/a_end)**2)
        nextgas.check()
        delta_work=(oldcloud.energy-nextcloud.energy)+(
              g.thermal_eV_cm3/g.nH-nextgas.thermal_eV_cm3/nextgas.nH)
        if delta_work< -1e-9:raise RuntimeError("EXCESSIVE_NEGATIVE_COSMOLOGICAL_WORK")
        micro_after=SourceState(
           a_end,nextgas,nextcloud,micro.elapsed_s+dt,
           micro.source_N_perH,micro.source_E_eV_perH,
           micro.recomb_e_perH,micro.escape_E_eV_perH,
           micro.geometry_work_eV_perH+delta_work,
           micro.thomson_tau+
             .5*THOMSON_RATE*dt*(g.ne+nextgas.ne))
        return micro_after,yy,dt
    def step(self,micro,y,a_end):
        amid=math.sqrt(micro.a*a_end)
        first,ym,dt1=self.drift_segment(micro,y,amid)
        rate=self.model.rate(amid)
        dt_guess=2*dt1
        converged=False
        for i in range(6):
            born=emit_half(first,self.source,rate,dt_guess/2)
            reacted,_=reaction_step(born,dt_guess,self.provider)
            newborn=emit_half(reacted,self.source,rate,dt_guess/2)
            after,ye,dt2=self.drift_segment(newborn,ym,a_end)
            new_dt=dt1+dt2
            if abs(new_dt-dt_guess)<max(5e-8,3e-12*new_dt):
                converged=True
                break
            dt_guess=new_dt
        if not converged:raise RuntimeError("C15_MIDPOINT_PHOTOCHEM_CLOCK_NOT_CONVERGED")
        micro_out=after
        micro_out.thomson_tau=micro.thomson_tau+(
          .5*THOMSON_RATE*dt1*(micro.gas.ne+first.gas.ne)
          +.5*THOMSON_RATE*dt2*(newborn.gas.ne+micro_out.gas.ne))
        if abs((micro_out.elapsed_s-micro.elapsed_s)-new_dt)>max(.04,1e-11*new_dt):
            raise RuntimeError("C15_PROPER_CLOCK_OWNER_NOT_EQUAL")
        return micro_out,ye,{"dt_s":new_dt,"iters":i+1,
            "min_dt":min(dt1,dt2),"max_dt":max(dt1,dt2)}
    def run(self):
        micro,y=self.init_state()
        baseN=micro.number_ledger();baseE=micro.energy_ledger()
        out=[];last_steps=[]
        def row():
            q=self.quantities(math.log(micro.a),y,micro,float(y[1]))
            s=micro.summary()
            energy=q["cbm_rho"];p=q["cbm_pi"]
            s.update({
              "Sigma":q["Sigma"],"epsilon_sigma":q["epsilon_sigma"],
              "b":q["b"],"H_per_s":q["h"],"s_per_s":q["s"],
              "Pi_gamma_and_nu_Pa":p,"Pi_UV_feedback_Pa":s["Pi_ion_Pa"],
              "Pi_Einstein_shear_Pa":p+(s["Pi_ion_Pa"] if self.cfg.uv_stress_in_shear else 0),
              "radiation_energy_E0":float(q["eg"][0]),
              "radiation_gamma_E2":float(q["eg"][2]),
              "radiation_nu_E2":float(q["en"][2]),
              "number_gamma_N0":float(q["ng"][0]),
              "number_nu_N0":float(q["nn"][0]),
              "source_CBMRho_J_m3":energy,
              "source_UV_energy_J_m3":s["ion_rad_energy_Pa"],
              "tau_Thomson_DOP853":float(y[-1]),
              "UV_to_CMB_radiation_energy":s["ion_rad_energy_Pa"]/max(q["cbm_rho"],1e-99),
              "UV_to_CMB_pressure":abs(s["Pi_ion_Pa"])/max(abs(q["cbm_pi"]),1e-99)
            })
            return s
        out.append(row())
        dx=stable_dx(START,STOP)/self.cfg.nstep
        start=perf_counter()
        compressed=0;holds=0;maxstep_errN=0;maxstep_errE=0
        for i in range(self.cfg.nstep):
            nexta=STOP if i==self.cfg.nstep-1 else START*math.exp((i+1)*dx)
            micro,y,z=self.step(micro,y,nexta)
            if self.cfg.compression and micro.photons.packet_count>len(self.source.energy):
                # source-conditioned positive cohort reductions, exact C13 owner
                reduced,receipt=reduce_age_cohorts(micro.photons,len(self.source.energy),
                    micro.gas,z["dt_s"],event_budget=1e-12,heat_budget=1e-11)
                if receipt["admitted"]:
                    micro.photons=reduced;compressed+=1
                else:holds+=1
            micro.photons.check()
            eN=abs(micro.number_ledger()-baseN)
            eE=abs(micro.energy_ledger()-baseE)
            maxstep_errN=max(maxstep_errN,eN)
            maxstep_errE=max(maxstep_errE,eE)
            if eN>1e-11 or eE>1e-9:
                raise RuntimeError("C15_PHOTON_CHEMICAL_LEDGER_NOT_CONSERVATIVE")
            here=row()
            if abs(here["source_UV_energy_J_m3"]-self.quantities(
                 math.log(micro.a),y,micro,float(y[1]))["uv_rho"])>1e-20:
                raise RuntimeError("UV_HAMILTONIAN_RADIATION_SOURCE_NOT_IDENTICAL")
            # Structural energy and number hierarchy checks, including
            # the actual C13 source-dependent chemistry electron density.
            ydot=self.rhs(math.log(micro.a),y,micro,float(y[1]))
            alpha=here["s_per_s"]/here["H_per_s"]
            n=self.n
            for offset in (3,3+n,3+2*n,3+3*n):
                moments=y[offset:offset+n]
                # Legendre reconstruction samples the full angular sky, with
                # no clipping/projection that could hide an unphysical solution.
                if float(np.min(self.angular_positive_basis @ moments)) < -2e-11:
                    raise RuntimeError("BASS_ANGULAR_DISTRIBUTION_NEGATIVE")
                if moments[0]<=0 or abs(moments[2])>moments[0]*(1+1e-12):
                    raise RuntimeError("BASS_RADIATION_PRESSURE_POSITIVITY_CONE")
            for ellj,ellN in ((3,3+n),(3+2*n,3+3*n)):
                if abs(ydot[ellj]+2*alpha*y[ellj+2])>1e-12:
                    raise RuntimeError("EINSTEIN_BOLTZMANN_ENERGY_MONOPOLE_WORK_FAILURE")
                if abs(ydot[ellN])>1e-12:
                    raise RuntimeError("BOLTZMANN_PARTICLE_NUMBER_MONOPOLE_NOT_CONSERVING")
            out.append(here);last_steps.append(z)
        wall=perf_counter()-start
        if (max(abs(x["number_gamma_N0"]-1) for x in out)>2e-11 or
            max(abs(x["number_nu_N0"]-1) for x in out)>2e-11):
            raise RuntimeError("C15_PHOTON_NEUTRINO_NUMBER_CONSERVATION")
        return dict(
         schema="rei.c15.real_source_Einstein_Boltzmann_chemical_feedback.v1",
         scientific_status="IMPLEMENTED_SCOPED_SHORT_NEAR_Z4_NO_COMPLETE_EOR_ADMISSION",
         source_native_sha256=self.source.source_sha256,
         original_C14_PR139_sha256="1ca73d64d3aaf7ea3ed4b7265522bbfdfae7e228",
         model="non-tilted LRS Bianchi I, Einstein sourced by gamma,nu and UV quadrupole, native MD14 photons + C11 Grackle CaseA chemistry on changed proper clock; polarized/E,B not solved",
         start_source="C13 declared xHII=.4 HeII=.5 HeIII=.3 T=12000K at a=.1999, not physical z20 donor",
         radiation_partition=self.frac,
         Sigma_ref_user=math.sqrt(3)*abs(self.bg0.case.q_ref)/math.hypot(1,self.bg0.case.q_ref),
         orientation_initial=int(np.sign(self.bg0.case.q_ref)),
         numerical={"nstep":self.cfg.nstep,"L":self.cfg.L,
           "kappa_gamma":self.cfg.kappa_gamma,"kappa_nu":self.cfg.kappa_nu,
           "energy_gamma_nu_Thomson":self.cfg.thomson,
           "gravity_feedback":self.cfg.gravity_feedback,"uv_pi_in_shear":self.cfg.uv_stress_in_shear,
           "coalescence":self.cfg.compression,
           "coalescence_admits":compressed,"coalescence_holds":holds,
           "max_photo_number_ledger_error_perH":maxstep_errN,
           "max_photo_energy_ledger_error_eV_perH":maxstep_errE,
           "geometry_rhs_calls":self.eval_count,
          "tau_Thomson_source_trapezoid":micro.thomson_tau,
          "tau_Thomson_coupled_differential":float(y[-1]),
          "tau_relative_coupled_vs_trapezoid":abs(micro.thomson_tau-y[-1])/max(float(y[-1]),1e-40),
           "coupled_wall_s":wall,"proper_clock_iterations":[x["iters"] for x in last_steps]},
         physical_gap={
           "global_einstein_source_conservation":"NOT_CLOSED_EXTERNAL_MD14_STELLAR_EMISSION_AND_RECOMBINATION_ESCAPE_RESERVOIRS",
           "gas_photo_thermochemistry":"original C11 CaseA with photon consumption, does not include collisionally excited/cooling network",
           "matter_anisotropic_pi":"ZERO_PERFECT_FLUID, BASS massive and causal viscosity separate",
           "polarization":"E2_B_and_Thomson_spin_mixing_NOT_INCLUDED",
           "redshift_domain":"only a=.1999 to .2 manufactured 12kK gas",
           "scientific_admission":"NOT_ISSUED"},
         endpoint=out[-1], history=out,operator_ledger_records=last_steps)
