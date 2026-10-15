"""Run source-pinned REI photon/neutrino Thomson + BASS massive J^i pilot.

Actual ODE: independent massless gamma/nu multipoles and massive l=0,2
velocity weighted i=0..2; high moments l4/i3/4 supplied exactly from
canonical BASS FD 96-radial Killing characteristics. Coupled Einstein H,s.
All H/He n_e for photon Thomson drawn one-way from unchanged original
REI 312238-row HHe donor. No native H/He chemistry/RT recomputation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import time
import sys

import numpy as np
from massive_radial import MassiveRadialGrid,MassiveRadialSpecies
from species_hierarchy import SpeciesHierarchy
from run_hierarchy import source_lock,actual_electrons,sha,public_sigma_from_q
from lrs_boltzmann import SourceLock

HERE=Path(__file__).resolve().parent
BASS_HEAD="9e50f936f3289cb0c7c8127772cf9fb8d172d7a8"
MASSIVE_SHA="1857567475b1c8586298f868e5420aae7a72e8e1ba69cce6a5b21bfca4fdd790"
BASS_HEAD="9e50f936f3289cb0c7c8127772cf9fb8d172d7a8"


def compare_momentum_batch():
    grid=MassiveRadialGrid(30,96,32)
    xs=np.linspace(0,math.log(21/5),1024)
    bs=.02*np.sin(xs*2)
    scalar=np.array([
        [m.j0,m.j2,m.j4] for m in
        (grid.moments(float(x),float(b),.5,2) for x,b in zip(xs,bs))
    ])
    vector=grid.batch(xs,bs,.5,2,chunk=64)
    max_abs=float(np.max(abs(scalar-vector)))
    max_relative=float(np.max(abs(scalar-vector)/
        np.maximum(np.maximum(abs(scalar),abs(vector)),1e-14)))
    if max_abs>8e-15:
        raise ArithmeticError("massive batched source differs from scalar")
    # Matched-workload scalar reference: compute all three moments in
    # ONE scalar call, rather than artificially repeating it three times.
    def scalar_once():
        return np.array([
            [moment.j0,moment.j2,moment.j4]
            for moment in (
                grid.moments(float(x),float(b),.5,2)
                for x,b in zip(xs,bs)
            )
        ])
    clocks={}
    for tag,fn,trials in [
        ("scalar",scalar_once,4),
        ("vector",lambda:grid.batch(xs,bs,.5,2,chunk=64),5)
    ]:
        ts=[]
        for _ in range(trials):
            t=time.perf_counter()
            fn()
            ts.append(time.perf_counter()-t)
        clocks[tag]={"median_s":statistics.median(ts),"trials_s":ts}
    return {
        "samples":len(xs),"radial_nodes":96,"angular_nodes":32,
        "max_abs_difference":max_abs,
        "max_scaled_relative_difference":max_relative,
        "scalar":clocks["scalar"],"chunked":clocks["vector"],
        "speedup":clocks["scalar"]["median_s"]/clocks["vector"]["median_s"],
        "scope":"only original Fermi-Dirac radial J0/J2/J4 evaluation, not full REI solver",
    }


def run(*,root:Path,bass160:Path,output:Path):
    original=bass160/"research/rei_axbi_sigma_matter_20261015/sigma_matter.py"
    assert sha(original)==MASSIVE_SHA
    source=source_lock()
    donor,metadata=actual_electrons(root)
    source_sha=metadata["history_sha256"]
    configs=[
       # tag, Sigma, orientation, f_m, A_m, m/Tref, real HHe Thomson
       ("gamma_nu_no_matter",0.,0,0.,0.,30.,True),
       ("massive_positive",0.,0,.1,.5,30.,True),
       ("massive_negative",0.,0,.1,-.5,30.,True),
       ("massive_no_thomson",0.,0,.1,.5,30.,False),
       ("massive_cold",0.,0,.1,.5,300.,True),
       ("massive_signed_plus",public_sigma_from_q(.01)[0],1,.1,.5,30.,True),
       ("massive_signed_minus",public_sigma_from_q(-.01)[0],-1,.1,.5,30.,True),
    ]
    all_rows=[]
    summary=[]
    for tag,sigma,sign,fm,Am,m,scatter in configs:
        obj=MassiveRadialSpecies(source,2.7255,ellmax=8,
            Sigma_ref=sigma,orientation=sign,kappa_gamma=.2,kappa_nu=.2,
            ne_source=donor if scatter else None,
            mass_fraction=fm,massive_A=Am,mass_over_T_ref=m,imax=2)
        sol,states,wall=obj.integrate(n=161,rtol=3e-11,atol=2e-13)
        max_mass_err=0.
        max_J0_energy_rel=0.
        max_photon_number=0.
        for i,x in enumerate(sol.t):
            st=states[i]
            k=obj.main_size;n=obj.imax+1
            expected=st["exact_radial_towers"]
            err=max(float(np.max(abs(sol.y[k:k+n,i]-expected.j0[:n]))),
                    float(np.max(abs(sol.y[k+n:k+2*n,i]-expected.j2[:n]))))
            max_mass_err=max(max_mass_err,err)
            max_photon_number=max(max_photon_number,
                 abs(st["N_gamma"][0]-1),abs(st["N_nu"][0]-1))
            max_J0_energy_rel=max(max_J0_energy_rel,
                abs(sol.y[k,i]-expected.j0[0])/max(expected.j0[0],1e-200))
            all_rows.append({
                "case":tag,"a":st["a"],"zbar":1/st["a"]-1,
                "eta":float(x),"Sigma":st["Sigma"],
                "orientation":int(np.sign(st["s"])),"shear_s_per_s":st["s"],
                "H_per_s":st["H"],"b":float(sol.y[1,i]),
                "proper_elapsed_s":float(sol.y[0,i]/source.href),
                "mass_fraction_initial":fm,"Am":Am,"m_over_Tref":m,
                "Pi_r_gamma_Jm3":st["Pi_gamma_J_m3"],
                "Pi_r_massless_nu_Jm3":st["Pi_nu_J_m3"],
                "Pi_massive_Jm3":st["Pi_matter_J_m3"],
                "massive_energy_norm":st["massive_energy_norm"],
                "J0_0_integrated":sol.y[k,i],
                "J0_0_exact":expected.j0[0],
                "J2_0_integrated":sol.y[k+n,i],
                "J2_0_exact":expected.j2[0],
                "gamma_J2":float(st["E_gamma"][2]),
                "massless_nu_J2":float(st["E_nu"][2]),
                "gamma_N0":float(st["N_gamma"][0]),
                "massless_nu_N0":float(st["N_nu"][0]),
            })
        if max_mass_err>5e-9 or max_photon_number>5e-11:
            raise ArithmeticError(f"numerical massive or photon invariants fail {tag}")
        last=states[-1]
        summary.append({
           "case":tag,"Sigma_ref":sigma,"orientation_ref":sign,
           "mass_fraction":fm,"A_m":Am,"m_over_Tref":m,
           "gamma_thomson":scatter,"nfev":int(sol.nfev),
           "wall_s":wall,"Sigma_end":last["Sigma"],
           "b_end":float(sol.y[1,-1]),
           "massive_Pi_end_Jm3":last["Pi_matter_J_m3"],
           "gamma_Pi_end_Jm3":last["Pi_gamma_J_m3"],
           "nu_Pi_end_Jm3":last["Pi_nu_J_m3"],
           "gamma_J2_end":float(last["E_gamma"][2]),
           "nu_J2_end":float(last["E_nu"][2]),
           "max_absolute_massive_i_tower_difference":max_mass_err,
           "max_relative_massive_J0_integral_error":max_J0_energy_rel,
           "max_gamma_nu_number_error":max_photon_number,
        })
    # Explicit original PR137 zero-mass fraction numerical identity.
    baseline=SpeciesHierarchy(source,2.7255,8,Sigma_ref=0.,orientation=0,
        kappa_gamma=.2,kappa_nu=.2,ne_source=donor)
    bs,vals,bwall=baseline.integrate(161,rtol=3e-11,atol=2e-13)
    assert abs(vals[-1]["Sigma"]-summary[0]["Sigma_end"])<8e-11
    assert abs(bs.y[1,-1]-summary[0]["b_end"])<8e-11
    sdict={r["case"]:r for r in summary}
    assert sdict["massive_positive"]["Sigma_end"]>sdict["massive_negative"]["Sigma_end"]
    assert sdict["massive_positive"]["gamma_J2_end"]<sdict["massive_no_thomson"]["gamma_J2_end"]
    assert sdict["massive_cold"]["massive_Pi_end_Jm3"]<sdict["massive_positive"]["massive_Pi_end_Jm3"]

    output.mkdir(parents=True,exist_ok=True)
    with (output/"COUPLED_MASSIVE_HISTORY.csv").open("w") as f:
        w=csv.DictWriter(f,fieldnames=list(all_rows[0]),lineterminator="\n")
        w.writeheader();w.writerows(all_rows)
    result={
      "schema":"rei.BASS_PR160.PR137.massive_i2_gamma_nu.v1",
      "date":"2026-10-15",
      "status":"SCOPED_HOMOGENEOUS_EXACT_VLASOV_RADIAL_MOMENT_ODE_AND_GAMMA_NU_THOMSON_PASS",
      "parent_REI_PR137_sha":"5d41df647c4fd624d8a1b574f67fdd0b82ff5102",
      "source_BASS_PR160_sha":BASS_HEAD,
      "source_BASS160_sigma_matter_byte_sha256":MASSIVE_SHA,
      "source_original_REI_HHe_ne_sha256":source_sha,
      "source_ne_interpolation":metadata,
      "massive_kinetic_fraction_of_original_Omega_m":"restricted nonbaryonic fraction, split off from cold dust; no extra mass budget",
      "massive_distributions":"Fermi-Dirac 96 positive radial quadrature and positive 1+Am P2 source, m/T exploratory nonbaryonic particle",
      "time_towers":"actual l=0,2 i=0..2 ODE using original BASS Eq12 scalar LRS reduction, exact higher l=4 and i>2 source boundary from Killing characteristics",
      "collisions":"original PR137 gamma-only E2=0 unpolarized Thomson from real frozen native HHe n_e(a); massless nu no direct collisions; massive collisionless",
      "n_cases":len(configs),"saved_history_rows":len(all_rows),
      "original_PR137_fm0_endpoint_Sigma_diff":summary[0]["Sigma_end"]-vals[-1]["Sigma"],
      "original_PR137_fm0_endpoint_b_diff":summary[0]["b_end"]-bs.y[1,-1],
      "case_results":summary,
      "benchmark_massive_moment":compare_momentum_batch(),
      "important_unadmitted":["not autonomous finite velocity hierarchy: exact upper-moment oracle","no source H/He recomputation under changed Einstein metric","no full polarized E/B Thomson or ionizing radiation moment source","not a measured massive species model or BBN neutrino solution","not native full REI production solver","no fit or observations"]
    }
    (output/"RESULTS.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":result["status"],"cases":len(configs),"rows":len(all_rows),
      "no_mass_ref_Sigma":summary[0]["Sigma_end"],
      "massive_plus_Sigma":sdict["massive_positive"]["Sigma_end"],
      "massive_minus_Sigma":sdict["massive_negative"]["Sigma_end"],
      "massive_positive_Pi_Jm3":sdict["massive_positive"]["massive_Pi_end_Jm3"],
      "scalar_vector_speedup":result["benchmark_massive_moment"]["speedup"],
      "max_integrated_J_error":max(r["max_absolute_massive_i_tower_difference"] for r in summary),
    },indent=2))
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--repo-owner",required=True,type=Path)
    parser.add_argument("--bass160-root",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    arg=parser.parse_args()
    run(root=arg.repo_owner,bass160=arg.bass160_root,output=arg.output)
