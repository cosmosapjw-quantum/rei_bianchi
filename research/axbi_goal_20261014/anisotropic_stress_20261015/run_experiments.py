#!/usr/bin/env python3
"""R5+C5-C8 source-scoped coupled radiation/matter anisotropic-stress experiments."""
import argparse
import csv
import json
import math
from pathlib import Path
import statistics
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from coupled_pi import (
    PhysicalScenario,Solver,sigma_init_from_legacy_signed_ratio,
    HREF,H0,RHO_CRIT,OM,OR,OL,K,AREF,XEND,GAMMA_M
)
HERE=Path(__file__).resolve().parent

def label(sigma,orientation,f,nu):
    return f"Sigma_init={sigma:.9f}__axis={orientation:+d}__f={f:.2f}__nu={nu:.3f}"

def scenario_runs(rtol=5e-11,atol=3e-13):
    # Legacy original q is only used to reproduce initial conditions. Report
    # scientific results with Sigma and an axis orientation.
    inputs=[(0.0,0),(.005,1),(.005,-1),(.01,1),(.01,-1)]
    scenarios=[]
    for legacy_magnitude,orientation in inputs:
        sigma,orient=sigma_init_from_legacy_signed_ratio(legacy_magnitude*orientation)
        for f,nu in [(0.,0.),(1.,0.),(1.,.02)]:
            model=PhysicalScenario(sigma,orient,f,nu)
            solver=Solver(model)
            sol,infos,wall=solver.solve(rtol=rtol,atol=atol,n=501)
            scenarios.append((model,sol,infos,wall,solver.moments.evals))
    return scenarios

def baseline_sources(owner):
    import hashlib
    cases={
       "Sigma_init_0":"runs/flrw/32d11e733155/ZERO_composed_001",
       "Sigma_init_small_axis_plus":"runs/paired/32d11e733155/SHEAR_HALF_PLUS_composed_002",
       "Sigma_init_small_axis_minus":"runs/paired/32d11e733155/SHEAR_HALF_MINUS_composed_001",
       "Sigma_init_large_axis_plus":"runs/paired/32d11e733155/SHEAR_MINUS_composed_001" # this file is negative orientation!
    }
    cases["Sigma_init_large_axis_minus"]=cases.pop("Sigma_init_large_axis_plus")
    def digest(path):
        h=hashlib.sha256()
        with path.open("rb") as f:
            for b in iter(lambda:f.read(1<<20),b""):h.update(b)
        return h.hexdigest()
    outs={}
    for key,rel in cases.items():
        folder=owner/"research/axbi_goal_20261014"/rel
        r=json.loads((folder/"COMPOSITION_RECEIPT.json").read_text())
        p=folder/"history.csv"
        assert r["status"]=="COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION"
        assert digest(p)==r["output_sha256"]["history.csv"]
        # Actual signed reference legacy field is not used as a new observable.
        last=p.read_bytes().splitlines()[-1].decode().split(",")
        hist=float(last[3]);h=float(last[7]);s=float(last[8]);b=float(last[6])
        Sigma=math.sqrt(3)*abs(s)/h
        outs[key]={"file_sha256":digest(p),"actual_last_b":b,
          "actual_last_Sigma":Sigma,"actual_last_orientation":int(np.sign(s)),
          "actual_last_elapsed_s":hist,"actual_rows":312238,
          "H_per_s":h,"s_per_s":s}
    return outs

def calculate_series(runs):
    recs=[]
    for model,sol,info,wall,nfev in runs:
        x=sol.t
        # Direct exact constraint residual: from solver evaluation.
        e=[abs(z["H_per_s"]**2-z["hamiltonian_rhs_per_s2"])/z["H_per_s"]**2 for z in info]
        # Energy continuity enforced *by construction* within the model.
        # Test the exact coupled differential identity via scalar-form alternative.
        max_energy=0.
        max_constraint=float(np.max(e))
        max_ray=0.
        evaluator=Solver(model)
        for i,xi in enumerate(sol.t):
            y=sol.y[:,i]
            dy,stuff=evaluator.eval(xi,y) # physical residual, no duplicate GL rule allocation
            a=stuff["a"]
            h=stuff["H_per_s"];s=stuff["signed_s_per_s"];v=s/h
            piR=stuff["pi_r_over_rhocrit"]
            piM=stuff["pi_m_over_rhocrit"]
            u=float(y[2])
            # Predicted matter energy derivative d(rho_m)/dx
            dust=OM/a**3
            dm= -3*dust+dy[2]
            dm_exact=-3*(dust+GAMMA_M*u)-6*v*piM
            # Radiation exact M0 derivative using M0'=-2*M2:
            omrad=OR/a**4
            dr=-4*stuff["rad_energy_over_rhocrit"]-6*v*piR
            # Independent matter equation:
            max_energy=max(max_energy,abs(dm-dm_exact)/max(1,dust))
            # dH/dt predicted by constraint differentiation vs Raychaudhuri.
            ds_dx=HREF*dy[1]
            dH2_dx=H0**2*(dm+dr)+2*s*ds_dx
            ray_dx=-3*H0**2*(dust+GAMMA_M*u+4*stuff["rad_energy_over_rhocrit"]/3)-6*s*s
            max_ray=max(max_ray,abs(dH2_dx-ray_dx)/max(h*h,1e-60))
        f=info[-1];init=info[0]
        if max_ray>2e-11 or max_constraint>1e-12 or max_energy>1e-12:
            raise RuntimeError(f"MODEL_EINSTEIN_ENERGY_CONSTRAINT_FAIL:{max_ray},{max_constraint},{max_energy}")
        rec={
          "source_label":label(model.Sigma_ref,model.orientation,model.free_radiation_fraction,model.matter_viscosity_strength),
          "Sigma_ref":model.Sigma_ref,
          "orientation":model.orientation,
          "fraction_free_radiation":model.free_radiation_fraction,
          "nu_shear_viscosity":model.matter_viscosity_strength,
          "endpoint_a":f["a"],
          "endpoint_b":float(sol.y[0,-1]),
          "endpoint_signed_s_per_s":f["signed_s_per_s"],
          "endpoint_Sigma":f["Sigma"],
          "endpoint_Sigma_WE":f["Sigma_WE"],
          "endpoint_proper_t_s":float(sol.y[3,-1])/HREF,
          "endpoint_pi_rad_J_m3":f["pi_r_J_m3"],
          "endpoint_pi_matter_J_m3":f["pi_m_J_m3"],
          "endpoint_thermal_u_over_rhocrit":float(sol.y[2,-1]),
          "max_viscous_temperature_production_proxy":float(np.max([z["viscous_heating_source_per_x"] for z in info])),
          "max_abs_Sigma":float(max(z["Sigma"] for z in info)),
          "max_abs_pi_rad_J_m3":float(max(abs(z["pi_r_J_m3"]) for z in info)),
          "max_abs_pi_matter_J_m3":float(max(abs(z["pi_m_J_m3"]) for z in info)),
          "constraint_relative_max":max_constraint,
          "raychaudhuri_vs_energy_relative_max":max_ray,
          "matter_energy_ledger_relative_max":max_energy,
          "numerical_rhs_calls":int(sol.nfev),
          "wall_s":wall,
          "moments_evaluations":nfev,
          "physical_scope":"collisionless initially isotropic radiation, effective thermal energy with gamma=5/3, phenomenological shear viscosity, no source/HHe coupling",
        }
        recs.append(rec)
    return recs

def plot_runs(runs):
    base=HERE/"results"
    fig,axs=plt.subplots(2,2,figsize=(11,9),constrained_layout=True)
    for model,sol,info,_,_ in runs:
        if model.Sigma_ref==0:continue
        if model.orientation!=1:continue
        if model.Sigma_ref<.01:continue
        a=AREF*np.exp(sol.t);z=1/a-1
        desc=("stress free" if model.free_radiation_fraction==0 else
               "radiation pi" if model.matter_viscosity_strength==0 else
               "radiation + viscous matter pi")
        sig=np.array([w["Sigma"] for w in info])
        pm=np.array([w["pi_m_J_m3"] for w in info])
        pr=np.array([w["pi_r_J_m3"] for w in info])
        axs[0,0].plot(z,sig,label=desc)
        axs[0,1].plot(z,sol.y[0,:],label=desc)
        axs[1,0].plot(z,pr,label=desc)
        axs[1,1].plot(z,pm,label=desc)
    for ax,tag in zip(axs.flat,
         ("Sigma = sqrt(sigma_ab sigma^ab/2)/H",
          "Anisotropic metric b",
          "Radiation pi scalar [J/m3]",
          "Matter pi scalar [J/m3]")):
        ax.invert_xaxis();ax.set_ylabel(tag);ax.set_xlabel("Mean redshift")
        ax.grid(alpha=.25);ax.legend(fontsize=8)
    fig.suptitle("Coupled Einstein LRS Bianchi I, Sigma_ref≈0.01732, stress-free vs radiation vs matter viscosity")
    fig.savefig(base/"coupled_sigma_pi_radiation_matter.png",dpi=175)
    plt.close(fig)

    fig,ax=plt.subplots(figsize=(9,5.5),constrained_layout=True)
    for model,sol,info,_,_ in runs:
        if model.Sigma_ref==0 or model.matter_viscosity_strength:continue
        if model.free_radiation_fraction!=1:continue
        if model.Sigma_ref<.01:continue
        z=1/(AREF*np.exp(sol.t))-1
        ax.plot(z,sol.y[0],label="axis orientation "+("+" if model.orientation>0 else "-"))
    ax.invert_xaxis();ax.grid(alpha=.3);ax.legend()
    ax.set_xlabel("Mean redshift");ax.set_ylabel("signed b, not equal and opposite under radiation stress")
    ax.set_title("Radiation quadrupolar anisotropic stress breaks exact sign-reflection background")
    fig.savefig(base/"radiation_stress_breaks_signed_b_parity.png",dpi=175)
    plt.close(fig)

def run_model_pair_tests():
    raw=scenario_runs()
    results=calculate_series(raw)
    # Analytic sign-even and sign-odd properties can break when radiation
    # M2(b) has even b² terms; they are exact for truly stress-free backgrounds.
    def lookup(sig,orientation,f,nu):
        return next(r for r in results if r["Sigma_ref"]==sig and r["orientation"]==orientation
           and r["fraction_free_radiation"]==f and r["nu_shear_viscosity"]==nu)
    sigsmall=sigma_init_from_legacy_signed_ratio(.005)[0]
    siglarge=sigma_init_from_legacy_signed_ratio(.01)[0]
    epsb=[]
    for sig in (sigsmall,siglarge):
        stress0plus=lookup(sig,1,0.,0.);stress0minus=lookup(sig,-1,0.,0.)
        if abs(stress0plus["endpoint_b"]+stress0minus["endpoint_b"])>3e-13:
            raise RuntimeError("STRESS_FREE_B_SIGN_REFLECTION_FAILURE")
        coupledplus=lookup(sig,1,1.,0.);coupledminus=lookup(sig,-1,1.,0.)
        epsb.append({"Sigma_ref":sig,
          "stress_free_pair_b_sum":stress0plus["endpoint_b"]+stress0minus["endpoint_b"],
          "radiation_stress_pair_b_sum":coupledplus["endpoint_b"]+coupledminus["endpoint_b"],
          "radiation_stress_Sigma_end_difference":coupledplus["endpoint_Sigma"]-coupledminus["endpoint_Sigma"]})
    plot_runs(raw)
    out={
      "schema":"rei.axbi.Sigma_pi_coupled_pilot_v1",
      "status":"RADIATION_AND_MATTER_PI_COUPLED_ODE_ACTUALLY_EXECUTED",
      "source_owner_pr":"fa20d75e344a28c833a47cbca82315ccbbdf6882",
      "model":"Einstein exact LRS Bianchi I + noninteracting collisionless initially isotropic radiation + pressureless cold dust + viscously heated gamma5/3 thermal reservoir",
      "Sigma":"sqrt(sigma_ab sigma^ab/2)/H=sqrt3 abs(s)/H, separate orientation sign",
      "Sigma_WainwrightEllis":"Sigma/sqrt3, equals abs(s)/H in this LRS model",
      "radiation_free_fraction":{"0":"perfect isotropic radiation","1":"all effective Omega_r collisionless anisotropic; conditional envelope"},
      "matter_viscosity":"eta=nu rho_dust/H; pi_m=-2 eta sigma_tensor; energy dumped into gamma5/3 reservoir, no cosmological baryonic chemistry",
      "entropy_proxy":"-sigma_pi_m = 12 eta s² >=0 for nu>=0",
      "initial_source_cases":5,
      "scenarios":[{"initial_Sigma":x,"axis":e} for x,e in
                    ((0.,0),(sigsmall,1),(sigsmall,-1),(siglarge,1),(siglarge,-1))],
      "solutions":results,
      "sign_reflection":epsb,
      "literature_context":["https://arxiv.org/abs/1003.3491","https://arxiv.org/abs/1610.00020"],
      "science_legacy_AX08_HHe_reionization_run":False,
      "scientific_admission":"NOT_ISSUED"
    }
    (HERE/"results/experiment.json").write_text(json.dumps(out,indent=2)+"\n")
    return out

if __name__=="__main__":
    d=run_model_pair_tests()
    for x in d["solutions"]:
        if x["Sigma_ref"]>0 and x["orientation"]==1 and x["Sigma_ref"]>.01:
            print(f"f_free={x['fraction_free_radiation']},viscosity={x['nu_shear_viscosity']} Sigma_end={x['endpoint_Sigma']:.12g} Pi_r={x['endpoint_pi_rad_J_m3']:.6g} Pi_m={x['endpoint_pi_matter_J_m3']:.6g} visc_heat={x['endpoint_thermal_u_over_rhocrit']:.6g} physics_rhserr={x['raychaudhuri_vs_energy_relative_max']:.3e}")
    print("SIGN_REFLECTION",d["sign_reflection"])
