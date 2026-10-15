"""Executed radial, angular, velocity-index and radiation-l/time convergence.

These are independent numerical variants of one selected kinetic model, not
a physical posterior, full native REI AX11 estimate, or rigorous a-priori
bound on the missing E/B and reactive collision terms.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from run_hierarchy import source_lock,public_sigma_from_q
from massive_radial import MassiveRadialSpecies


def check(out:Path):
    s=source_lock()
    src=[
      ("initial_quadrupoles",0.,0,.5,30.),
      ("signed_plus",public_sigma_from_q(.01)[0],1,.5,30.),
      ("massive_cold",0.,0,.5,300.)
    ]
    variants=[
      ("low",64,16,4,0,1e-9,4e-12),
      ("source",96,32,8,2,3e-11,2e-13),
      ("tight",128,64,12,4,2e-12,1e-14)
    ]
    cases=[]
    for label,S,eps,A,mass in src:
        values=[]
        for level,nr,nmu,L,imax,rtol,atol in variants:
            model=MassiveRadialSpecies(s,2.7255,L,
               Sigma_ref=S,orientation=eps,kappa_gamma=.2,kappa_nu=.2,
               mass_fraction=.1,massive_A=A,mass_over_T_ref=mass,
               imax=imax,nr=nr,nmu=nmu,ne_source=None)
            sol,diag,wall=model.integrate(121,rtol,atol)
            l=diag[-1]
            N=imax+1;off=model.main_size
            exact=l["exact_radial_towers"]
            J0err=max(abs(sol.y[off+i,-1]-exact.j0[i])
                      for i in range(N))
            J2err=max(abs(sol.y[off+N+i,-1]-exact.j2[i])
                      for i in range(N))
            values.append({
                "label":level,"n_radial":nr,"n_mu":nmu,
                "gamma_nu_L":L,"velocity_i_max":imax,
                "rtol":rtol,"atol":atol,
                "end_Sigma":l["Sigma"],"end_b":float(sol.y[1,-1]),
                "massive_pi_end_Jm3":l["Pi_matter_J_m3"],
                "J0_abs_err":J0err,"J2_abs_err":J2err,
                "nfev":sol.nfev,"wall_s":wall,
            })
        baseline=values[1];tight=values[2]
        errs={
            "source_minus_tight_Sigma_abs":
                abs(baseline["end_Sigma"]-tight["end_Sigma"]),
            "source_minus_tight_b_abs":
                abs(baseline["end_b"]-tight["end_b"]),
            "source_minus_tight_Pim_relative":
                abs(baseline["massive_pi_end_Jm3"]-
                    tight["massive_pi_end_Jm3"])/max(abs(tight["massive_pi_end_Jm3"]),1e-100)
        }
        if errs["source_minus_tight_Sigma_abs"]>5e-9:
            raise AssertionError(f"unexpected massive time/angle grid failure {label}")
        cases.append({"label":label,"trials":values,"comparison":errs})
    results={
        "schema":"rei.pr137_bass160.massive_velocity_hierarchy_convergence.v1",
        "scope":"ODE local-time/angular/radial/velocity-index convergence of modeled homogeneous Bianchi I; exact high-moment oracle remains",
        "cases":cases,
        "source_parent":"rei_bianchi PR137, 5d41df647c4fd624d8a1b574f67fdd0b82ff5102",
        "BASS_original_sha":"1857567475b1c8586298f868e5420aae7a72e8e1ba69cce6a5b21bfca4fdd790",
        "status":"PASS_SCOPED_COMBINED_GRID_AND_TIME_REFINEMENT"}
    out.write_text(json.dumps(results,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
        "status":results["status"],
        "cases":[{"case":c["label"],"diff":c["comparison"]}
                 for c in results["cases"]]
    },indent=2))
    return results


if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--output",type=Path,required=True)
    arg=cli.parse_args()
    check(arg.output)
