"""Source-pinned initial shear vs anisotropic-stress cancellation experiment.

Actual BASS160 finite-mass velocity-index J hierarchy + PR137 separate
gamma/nu Einstein-Thomson, borrowed UNMODIFIED from PR140. We solve the
physical shooting equation signed s/H at mean zbar4 = 0 while preserving
full initially positive angular distributions W=1+A P2 and signed Sigma_ref.

This is a controlled one-way frozen HHe electron-source cosmology, NOT a
fit to CMB observations nor completed reionization/Einstein feedback.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path
from scipy.integrate import simpson
from scipy.optimize import brentq
from scipy.constants import G,c
import numpy as np

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent
sys.path.insert(0,str(PARENT))
sys.path.insert(0,str(PARENT/"massive_radial_20261015"))
from massive_radial import MassiveRadialSpecies
from run_hierarchy import source_lock,public_sigma_from_q,actual_electrons

ROOT=HERE.parents[2]  # REI checkout root? 'research'/parent => inspect before use
EXPECTED_SHA={
    "massive_radial_20261015/massive_radial.py":"6143accbaf9e4845e549e31d2490418531f310efa99293fd373c6f81bf5defb5",
    "species_hierarchy.py":"ced7906b35c26d8d0374ee8ce7f67ceb957b51a63d44e5a2661997b7e46983c5",
    "lrs_boltzmann.py":"06ef834e4cd7adacf01f0ad6e3becc5aea9a493b5b99fd398be82610543984cc",
    "run_hierarchy.py":"5dcbbf6000b6d20b550b8269e92208a9ee30de64c8148ca7aad97de24229375f",
}

def source_identity():
    out={}
    for name,locked in EXPECTED_SHA.items():
        path=PARENT/name
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if digest !=locked:
            raise RuntimeError(f"PR140_FROZEN_SOURCE_CHANGED:{name}:{digest}")
        out[name]=digest
    return out

def new_model(q,*,kappa_gamma=.2,kappa_nu=.2,Am=.5,
              fm=.1,mass=30.,nrad=96,nmu=32,
              ne_source=None,gravity_owner="hierarchy",imax=2,L=8):
    """q is a SOURCE-COMPATIBILITY adapter; public Sigma/orientation preserved."""
    sigma,sign=public_sigma_from_q(q)
    return MassiveRadialSpecies(source_lock(),2.7255,ellmax=L,
        Sigma_ref=sigma,orientation=sign,kappa_gamma=kappa_gamma,
        kappa_nu=kappa_nu,ne_source=ne_source,mass_fraction=fm,
        massive_A=Am,mass_over_T_ref=mass,imax=imax,nr=nrad,nmu=nmu,
        gravity_owner=gravity_owner)

def solve(q,*,n=161,rtol=3e-11,atol=2e-13,**kw):
    m=new_model(q,**kw)
    ivp,states,wall=m.integrate(n=n,rtol=rtol,atol=atol)
    f=states[-1]
    H=f["H"];shear=f["s"]
    rho=m.source.rhocrit_j_m3
    init=m.fields(0.,m.initial_state())
    # Physical SI source: pi_s=(p_parallel-p_perp)/3 and
    # dot(s)+3 H s = 8πG/c² ∑pi_s.
    Pi=np.array([row["Pi_gamma_J_m3"]+row["Pi_nu_J_m3"]+row["Pi_matter_J_m3"]
                 for row in states])
    a=np.array([row["a"] for row in states])
    h=np.array([row["H"] for row in states])
    eq_source=(8*math.pi*G/c**2)*simpson(a**3*Pi/h,x=ivp.t)
    left=a[-1]**3*shear - a[0]**3*init["s"]
    green_residual=left-eq_source
    normal=max(abs(left),abs(eq_source),abs(a[0]**3*init["s"]),1e-24)
    start_pi={key:float(init[key]) for key in
             ["Pi_gamma_J_m3","Pi_nu_J_m3","Pi_matter_J_m3"]}
    ret={
      "q_ref_internal":float(q),
      "Sigma_ref_user":float(m.Sigma_ref),
      "orientation_ref":int(m.orientation),
      "kappa_gamma":float(m.k_gamma),"kappa_nu":float(m.k_nu),
      "A_massive":float(m.Amass),
      "mass_fraction_of_original_omega_m":float(m.fmass),
      "mass_over_T_ref":float(m.massive.mass),
      "nrad":m.massive.q.size,"nmu":m.massive.mu.size,
      "L":m.ellmax,"i_max":m.imax,
      "n_rows":len(ivp.t),"nfev":int(ivp.nfev),
      "wall_s":float(wall),
      "signed_s_over_H_end":float(shear/H),
      "Sigma_end":float(f["Sigma"]),
      "b_end":float(ivp.y[1,-1]),
      "H_end_per_s":float(H),
      "proper_elapsed_s_end":float(ivp.y[0,-1]/m.source.href),
      "initial_pi_s_Jm3":start_pi,
      "final_pi_s_Jm3":{key:float(f[key]) for key in start_pi},
      "initial_signed_s_per_s":float(init["s"]),
      "final_signed_s_per_s":float(shear),
      "initial_mass_kinetic_norm":float(init["massive_energy_norm"]),
      "initial_matter_pressure_norm":float(init["massive_mean_pressure_norm"]),
      "initial_photon_energy_norm":float(init["rad_energy_norm"]),
      "max_gamma_number_error":float(max(abs(u["N_gamma"][0]-1) for u in states)),
      "max_nu_number_error":float(max(abs(u["N_nu"][0]-1) for u in states)),
      "Green_function_einstein_source_integral":float(eq_source),
      "Green_function_left_endpoint_difference":float(left),
      "Green_function_relative_defect":float(abs(green_residual)/normal),
      "ln_photon_directional_energy_transverse_minus_longitudinal":
          float(-3*ivp.y[1,-1]),
    }
    return ret

def residual(q, **kwargs):
    return solve(q,n=41,rtol=6e-11,atol=2e-13,**kwargs)["signed_s_over_H_end"]

def cancel(kw, *, bracket=(-0.003,.003),tol=7e-12,
           n=241,rtol=1e-11,atol=1e-13):
    """Solve signed late shear, NOT nonnegative Sigma, for root."""
    left=residual(bracket[0],**kw)
    right=residual(bracket[1],**kw)
    if not left<0<right:
        raise RuntimeError("SOURCE_SIGNED_SHEAR_BRACKET_NOT_DETECTED")
    t0=time.perf_counter()
    root=brentq(lambda q:residual(q,**kw),*bracket,
                xtol=tol,rtol=1e-10,maxiter=24)
    final=solve(root,n=n,rtol=rtol,atol=atol,**kw)
    final["bracket_before"]=[float(left),float(right)]
    final["solve_seconds_total"]=time.perf_counter()-t0
    final["root_type"]="signed s/H at mean zbar4 = 0; instantaneous shear only"
    final["source_kinetic_truncation"]="upper i,ell from source-exact Killing oracle"
    final["full_HHe_chemistry_evolving_with_new_metric"]="NOT_RUN"
    return final

SCENARIOS=[
 ("radiation_only",dict(kappa_gamma=.2,kappa_nu=.2,Am=0.,fm=0.,mass=30.)),
 ("rad_plus_massive_positive",dict(kappa_gamma=.2,kappa_nu=.2,Am=.5,fm=.1,mass=30.)),
 ("rad_plus_massive_negative",dict(kappa_gamma=.2,kappa_nu=.2,Am=-.5,fm=.1,mass=30.)),
 ("massive_only_positive",dict(kappa_gamma=0.,kappa_nu=0.,Am=.5,fm=.1,mass=30.)),
 ("massive_only_negative",dict(kappa_gamma=0.,kappa_nu=0.,Am=-.5,fm=.1,mass=30.)),
 ("cold_massive_plus_rad",dict(kappa_gamma=.2,kappa_nu=.2,Am=.5,fm=.1,mass=300.)),
 ("photon_seed_only",dict(kappa_gamma=.2,kappa_nu=0.,Am=0.,fm=0.,mass=30.)),
 ("neutrino_seed_only",dict(kappa_gamma=0.,kappa_nu=.2,Am=0.,fm=0.,mass=30.))
]

def run(*,out:Path,with_ne:bool=False,
        q_grid=(-.0015,-.0010,-.0005,0.,.0005)):
    source_identity()
    s=source_lock()
    donor=None
    electron_metadata=None
    if with_ne:
        donor,electron_metadata=actual_electrons(Path.home()/"Dropbox/bianchi/rei_bianchi")
    # Direct baseline physical null test at q=0 with no source anisotropic stress.
    control=solve(0.,n=101,kappa_gamma=0,kappa_nu=0,Am=0,fm=0,mass=30,nrad=64,nmu=24,ne_source=donor)
    if abs(control["signed_s_over_H_end"])>2e-12:
        raise AssertionError("NONZERO_SHEAR_GENERATED_WITH_ZERO_Pi_AND_SHEAR")
    # First diagnostic all q_ref zero with nonzero initial stresses.
    stress_seeds=[]
    for tag,kw in SCENARIOS:
        result=solve(0.,n=101,nrad=64,nmu=24,ne_source=donor,**kw)
        stress_seeds.append({"tag":tag,**result})
    # Solve signed q_ref cancellation for each separate physical kinetic supplier.
    roots=[]
    for tag,kw in SCENARIOS:
        fast=dict(kw,nrad=64,nmu=24,ne_source=donor)
        result=cancel(fast,n=241)
        if abs(result["signed_s_over_H_end"])>1e-8:
            raise RuntimeError("Q_CANCEL_ROOT_NOT_NUMERICALLY_CERTIFIED_SCOPED")
        roots.append({"tag":tag,**result})
    # True input resolution/time convergence on the positive massive + radiation case.
    target=next(z for z in roots if z["tag"]=="rad_plus_massive_positive")
    q=target["q_ref_internal"]
    cfg=next(v for t,v in SCENARIOS if t=="rad_plus_massive_positive")
    nominal=solve(q,n=241,nrad=96,nmu=32,ne_source=donor,**cfg)
    strict=solve(q,n=401,nrad=128,nmu=64,L=12,imax=4,
                 rtol=4e-12,atol=3e-14,ne_source=donor,**cfg)
    return {
      "schema":"rei.axbi.initial_sigma_pi_shear_cancellation.source_assisted_v1",
      "status":"NUMERICALLY_CHECKED_SOURCE_SCOPED_EINSTEIN_VLASOV",
      "source_sha256":source_identity(),
      "base_PR140_HEAD":"b1cba753083ad83049c23ff538834564b49b7b6e",
      "original_BASS_massive_source_commit":"9e50f936f3289cb0c7c8127772cf9fb8d172d7a8",
      "physical_equation":"dot(s)+3Hs=(8piG/c2)Pi_s, Pi_s=(p_parallel-p_perp)/3; Sigma=sqrt3*abs(s)/H, sign(s) independent",
      "scenario_count":len(SCENARIOS),"source_rei_model_HHe_electron":electron_metadata,
      "control_zero_stress_and_zero_shear":control,
      "q_zero_nonzero_initial_pi_runs":stress_seeds,
      "signed_initial_shear_cancellation_roots":roots,
      "cancellation_target_convergence":{
        "target_q":q,
        "root_low_grid":target,
        "nominal_96r32a_L8_i2":nominal,
        "strict_128r64a_L12_i4":strict,
        "signed_s_over_H_strict_minus_low_grid":strict["signed_s_over_H_end"]-target["signed_s_over_H_end"],
        "b_strict_minus_low_grid":strict["b_end"]-target["b_end"],
        "pi_massive_strict_minus_low_grid":strict["final_pi_s_Jm3"]["Pi_matter_J_m3"]-target["final_pi_s_Jm3"]["Pi_matter_J_m3"],
      },
      "critical_exclusions":["not a universal no-go or observed anisotropy",
            "not coupled recomputed HHe photo-chemistry under this new metric",
            "not full E/B polarized Thomson or ionizing stress",
            "not a rigorous AX11 numerical error certificate",
            "not an autonomous massive full l,i hierarchy",
            "not a production native rei_bianchi binary or full EoR history"]
    }

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--with-real-ne",action="store_true")
    a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    t=time.perf_counter()
    j=run(out=a.output,with_ne=a.with_real_ne)
    j["total_elapsed_s"]=time.perf_counter()-t
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(j,indent=2)+"\n")
    for item in j["signed_initial_shear_cancellation_roots"]:
        print("CANCEL",item["tag"],"q",item["q_ref_internal"],
              "initial Sigma",item["Sigma_ref_user"],
              "signed_end_s/H",item["signed_s_over_H_end"],
              "nonzero_metric_b",item["b_end"],
              "integrated_green_error",item["Green_function_relative_defect"],flush=True)
    print("HIGH_RES",j["cancellation_target_convergence"]["strict_128r64a_L12_i4"]["signed_s_over_H_end"],
          "elapsed",j["total_elapsed_s"])
