#!/usr/bin/env python3
"""Real REI C11 photo/Case-A electron opacity drives Thomson hierarchy and Einstein shear.

1) BASS source-locked Einstein-Vlasov anisotropic background a=aref->.2;
2) actually execute existing REI C11 fixed receiver 1e12s H/He photon+CaseA gas;
3) at a=.2, evolve energy & number PSTF LRS brightness with time-dependent
   real C11 electron density, Thomson collision, radiation/matter stress and
   Einstein expansion/shear for that 1e12s. This is a physically scoped
   OPERATOR-SPLIT short-window hybrid, not a full cosmological coupled HHe
   source/atomic/radiative Boltzmann history and not polarised.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path
import sys
import time
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator
from lrs_boltzmann import (HierarchyBackground,SourceLock,ElectronHistory,
                           GAMMA_PER_NE,GAMMA_PER_NE,C_SI)
from run_hierarchy import source_lock,public_sigma_from_q,HERE
sys.path.insert(0,str(HERE.parent/"source07_c11_casea_20261015"))
import casea

EV_J=1.602176634e-19
EV_CM3_TO_J_M3=EV_J*1e6
DURATION=1e12

def real_C11(nsteps=32,nmu=8,ne=8):
    """Native original PR130 C11 Case-A+photo source and positive packet execution."""
    if nsteps not in (16,32,64,128):
        raise ValueError("bounded native C11 grids")
    response=casea.one_run(q=0.,spectrum="bb50k",nsteps=nsteps,
         interval_s=DURATION,compress=False,nmu=nmu,ne=ne)
    p=casea.C9.Scenario(casea.ROOT)
    gas=casea.c10.Gas.initial(p)
    history=response["history"]
    data={
       "source":"original C11 CaseA provider PR130 source q=0 BB50K packet maps",
       "source_A_REI_scenario":"actual fixed a=.2 receiver; not dynamically recomputed from new backreaction",
       "gas_proper_nH_cm3":float(gas.nH),
       "gas_proper_nHe_cm3":float(gas.nHe),
       "gas_source_clock_fixed":True,
       "ionizing_photon_kinetic_pi_not_in_new_Einstein_source":True,
       "nsteps":nsteps,
       "accepted":response["accepted"],"rejected":response["rejected"],
       "full_source_grackle_CaseA_sha256":response["table_sha256"],
       "max_energy_eV_H":response["max_energy_residual_eV_per_H"],
       "max_photon_electron_per_H":response["max_electron_photon_residual_per_H"],
       "initial":history[0],"final":history[-1],
       "sampled_HHe_time_series":history
    }
    # This original source owns the internal CaseA RR/DR escaped-energy ledger.
    e0=sum(history[0][name] for name in
           ("photon_U_eV_per_H","thermal_eV_per_H","binding_eV_per_H","radiative_escape_eV_per_H"))
    max_e=max(abs(sum(h[name] for name in
           ("photon_U_eV_per_H","thermal_eV_per_H","binding_eV_per_H","radiative_escape_eV_per_H"))-e0)
           for h in history)
    if max_e>1e-9 or response["max_energy_residual_eV_per_H"]>1e-9:
        raise RuntimeError("C11_SOURCE_ENERGY_LEDGER_NOT_CONSERVING")
    if response["max_electron_photon_residual_per_H"]>1e-9:
        raise RuntimeError("C11_SOURCE_PHOTON_ELECTRON_NOT_CONSERVING")
    return data

class Receiver:
    def __init__(self,base:HierarchyBackground,c11:dict,collision:bool):
        self.bg=base
        self.cos=base.cos
        self.collision=collision
        self.c11=c11
        times=np.array([z["time_s"] for z in c11["sampled_HHe_time_series"]])
        xe=np.array([z["xe_per_H"] for z in c11["sampled_HHe_time_series"]])
        if times[0]!=0 or times[-1]!=DURATION or np.any(np.diff(times)<=0):
            raise ValueError("C11 RECEIVER CLOCK")
        self.ne_of_t=PchipInterpolator(times,xe*c11["gas_proper_nH_cm3"],extrapolate=False)
    def physical(self,t,y):
        # receiver y = [absolute background log(a/a_ref),b,v,u,J_energy,N_number].
        x,b,v,u=y[:4]
        if x<self.cos.xmax-1e-11 or x>self.cos.xmax+.01:
            raise ValueError("RECEIVER_X_OUTSIDE_SHORT_WINDOW")
        a=self.cos.aref*math.exp(x)
        j=y[4:4+self.bg.L+1];jn=y[4+self.bg.L+1:]
        if j[0]<=0 or jn[0]<=0:raise ValueError("NEGATIVE_CMB_RADIATION")
        s=self.cos.href*v
        dust=self.cos.omega_m/a**3
        rad=self.cos.omega_r/a**4*((1-self.bg.eta)+self.bg.eta*j[0])
        h=math.sqrt(self.cos.h0**2*(dust+self.cos.omega_lambda+rad+u)+s*s)
        piRnorm=self.bg.eta*self.cos.omega_r/a**4*j[2]/3
        piMnorm=-2*self.bg.nu*dust*s/h
        ne=float(self.ne_of_t(t))
        if not math.isfinite(ne) or ne<0:raise ValueError("INVALID_C11_NE")
        gamma=ne*GAMMA_PER_NE if self.collision else 0.0
        return x,a,b,v,u,j,jn,s,h,piRnorm,piMnorm,gamma,ne
    def rhs(self,t,y):
        x,a,b,v,u,j,jn,s,h,piRnorm,piMnorm,gamma,ne=self.physical(t,y)
        # Source exact energy: Thomson monopole conservative, ∂t J0 =-2sJ2.
        dE=s*(self.bg.A@j)-gamma*self.bg.damp*j
        dN=s*(self.bg.A_number@jn)-gamma*self.bg.damp*jn
        dv=-3*h*v+3*self.cos.h0**2/self.cos.href*(piRnorm+piMnorm)
        du=-5*h*u-6*s*piMnorm
        return np.r_[h,s,dv,du,dE,dN]
    def solve(self,y0,n=129,rtol=2e-12,atol=2e-14):
        if len(y0)!=4+2*(self.bg.L+1):raise ValueError("WRONG_REI_HISTORY_STATE")
        q=np.array(y0,dtype=float).copy()
        q[0]=self.cos.xmax
        t0=time.perf_counter()
        sol=solve_ivp(self.rhs,(0,DURATION),q,method="DOP853",
          rtol=rtol,atol=atol,
          t_eval=np.linspace(0,DURATION,n))
        wall=time.perf_counter()-t0
        if not sol.success:raise RuntimeError("RECEIVER_HHE_THOMSON_COUPLED_SOLVER_FAIL")
        records=[]
        for k,t in enumerate(sol.t):
            x,a,b,v,u,j,jn,s,h,piR,piM,gamma,ne=self.physical(t,sol.y[:,k])
            deriv=self.rhs(t,sol.y[:,k])
            # Number/energy moment properties are analytic identities of the
            # true angular operator and collision matrix, including real C11 ne.
            workE=deriv[4]+2*s*j[2]
            workN=deriv[4+self.bg.L+1]
            if abs(workE)>3e-22 or abs(workN)>3e-22:
                raise RuntimeError("THOMSON_BOLTZMANN_LEDGER")
            records.append({
              "t_s":float(t),"a":a,"b":b,
              "Sigma":math.sqrt(3)*abs(s)/h,
              "H_per_s":h,
              "radiation_energy_J_m3":(self.cos.rhocrit_j_m3*self.cos.omega_r/a**4)*
                 ((1-self.bg.eta)+self.bg.eta*j[0]),
              "pi_radiation_J_m3":piR*self.cos.rhocrit_j_m3,
              "pi_matter_J_m3":piM*self.cos.rhocrit_j_m3,
              "ne_cm3":ne,"gamma_T_per_s":gamma,
              "radiation_J0":float(j[0]),"radiation_J2":float(j[2]),
              "number_N0":float(jn[0]),"number_N2":float(jn[2]),
              "thermal_u_rhocrit":float(u)
            })
        return sol,records,wall

def main():
    s=source_lock()
    sigma,eps=public_sigma_from_q(0.0)
    source=HierarchyBackground(s,8,1.,+.2,sigma,eps)
    pre,wall=source.integrate(n=351)
    chemistry=real_C11(nsteps=32,nmu=8,ne=8)
    receiver0=Receiver(source,chemistry,collision=False)
    receiver1=Receiver(source,chemistry,collision=True)
    old=pre.y[:,-1]
    y0=np.r_[source.cos.xmax,old[1:]]
    s0,z0,w0=receiver0.solve(y0)
    s1,z1,w1=receiver1.solve(y0)
    # Same physical initial history, only Thomson opacity is switched.
    if abs(s0.y[1,0]-s1.y[1,0])>1e-14:
        raise RuntimeError("THOMSON_CONTROL_INITIAL_MISMATCH")
    if max(abs(x["number_N0"]-1) for x in z1)>5e-12:
        raise RuntimeError("PHOTON_NUMBER_CONSERVATION_FAIL")
    if abs(z0[-1]["radiation_J2"]-z1[-1]["radiation_J2"])<1e-12:
        raise RuntimeError("THOMSON_STRESS_RESPONSE_NOT_PRESENT")
    if any(x["Sigma"]<0 for x in z0+z1):
        raise RuntimeError("NEGATIVE_NORM_SIGMA")
    # Source gas thermal energy must not be silently double-counted against the
    # cosmological dust rest-mass energy used by Einstein H.
    rho_gas_thermal=chemistry["final"]["thermal_eV_per_H"]*chemistry["gas_proper_nH_cm3"]*EV_CM3_TO_J_M3
    dust=source.cos.omega_m/.2**3*source.cos.rhocrit_j_m3
    ratio=rho_gas_thermal/dust
    if ratio>1e-7:
        raise RuntimeError("IGNORED_GAS_THERMAL_BACKREACTION_TOO_BIG")
    out={
      "schema":"rei.crossrepo.actual_casea_HHe_thomson_Einstein_receiver.v1",
      "status":"ACTUAL_REI_C11_GAS_REACTION_TO_BASS_THOMSON_AND_EINSTEIN_PI_COUPLED",
      "physical_scope":"BASS source-free Einstein-Vlasov prehistory z20->4; genuine REI C11 fixed a=.2 source photon photo+CaseA gas1e12s; external HHe ne(t) drives Thomson; H/s and photon multipoles solved together over short receiver; radiation Pi backreacts",
      "omission":"Does not re-redshift original C9 ionizing source cohorts under the changed Einstein shear; C11 gas densities fixed over 1e12s, no exp dilution/cosmological redshift in C11 HHe packets; no full polarization, no kinetic matter pi or physical cosmic observer tail",
      "BASS_initial_stress":{"Sigma_ref":sigma,"axis":eps,"kappa":+.2,"eta":1,
          "original_BASS_vendor_sha256":__import__("run_hierarchy").sha(HERE/"suppliers/bass/rei_axbi_initial_stress_20261015/einstein_vlasov.py")},
      "C11_photo_CaseA":{"source_sha256":chemistry["full_source_grackle_CaseA_sha256"],
         "gas_proper_nH_cm3":chemistry["gas_proper_nH_cm3"],
         "nsteps":chemistry["nsteps"],"accepted":chemistry["accepted"],
         "max_energy_residual_eV_per_H":chemistry["max_energy_eV_H"],
         "max_photon_electron_residual_per_H":chemistry["max_photon_electron_per_H"],
         "initial":chemistry["initial"],"final":chemistry["final"]},
      "short_receiver":{
         "time_s":DURATION,"num_samples":len(z1),
         "initial":z1[0],
         "collisionless_endpoint":z0[-1],
         "real_C11_Thomson_endpoint":z1[-1],
         "delta_J2_Thomson":z1[-1]["radiation_J2"]-z0[-1]["radiation_J2"],
         "delta_Sigma_Thomson":z1[-1]["Sigma"]-z0[-1]["Sigma"],
         "integrated_scattering_opacity":float(np.trapezoid([x["gamma_T_per_s"] for x in z1],[x["t_s"] for x in z1])),
         "collisionless_elapsed_wall_s":w0,"Thomson_elapsed_wall_s":w1,
         "gas_thermal_over_cosmological_dust_energy":ratio,
         "traceback_original_initial_state_kept":True
      },
      "scientific_admission":"NOT_ISSUED"
    }
    (HERE/"results/C11_thomson_receiver_integration.json").write_text(json.dumps(out,indent=2)+"\n")
    (HERE/"results/C11_real_HHe_receiver.json").write_text(json.dumps(chemistry,indent=2)+"\n")
    print(json.dumps({"status":out["status"],
     "C11_initial":{k:chemistry["initial"][k] for k in ("x_HII","x_HeII","Tgas_K")},
     "C11_final":{k:chemistry["final"][k] for k in ("x_HII","x_HeII","Tgas_K")},
     "energy_ledger":chemistry["max_energy_eV_H"],
     "tau_window":out["short_receiver"]["integrated_scattering_opacity"],
     "delta_J2":out["short_receiver"]["delta_J2_Thomson"],
     "delta_Sigma":out["short_receiver"]["delta_Sigma_Thomson"],
     "ignored_thermal_ratio":ratio},indent=2))
if __name__=="__main__":main()
