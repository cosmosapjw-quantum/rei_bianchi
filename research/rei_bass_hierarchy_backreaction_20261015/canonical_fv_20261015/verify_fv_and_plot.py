"""Independent multi-grid, source and Einstein checks plus actual plotted histories."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
from canonical_fv import CanonicalFVSpecies,CanonicalMomentumFV
from massive_radial import MassiveRadialSpecies
from run_hierarchy import source_lock,public_sigma_from_q,actual_electrons


def verify(source_owner:Path,out:Path):
    src=source_lock()
    donor,donor_info=actual_electrons(source_owner)
    cases=[
        ("warm_relativistic",0.,0,3.,.5),
        ("intermediate",0.,0,30.,.5),
        ("signed_plus",public_sigma_from_q(.01)[0],1,30.,-.5),
    ]
    levels=[
        ("coarse",12,8,2,8,1e-9,3e-12),
        ("nominal",24,12,3,8,3e-11,3e-13),
        ("fine",48,24,3,12,2e-12,2e-14),
    ]
    results=[]
    for name,S,orient,mass,A in cases:
        rows=[]
        for label,nr,nmu,ng,L,rtol,atol in levels:
            m=CanonicalFVSpecies(src,2.7255,L,
                Sigma_ref=S,orientation=orient,kappa_gamma=.2,
                kappa_nu=.2,ne_source=donor,
                mass_fraction=.1,massive_A=A,mass_over_Tref=mass,
                radial_cells=nr,angular_cells=nmu,
                subcell_gauss_order=ng)
            solution,diag,_=m.integrate(n=101,rtol=rtol,atol=atol)
            tail=diag[-1]
            rows.append({
                "label":label,
                "radial_cells":nr,"angular_cells":nmu,
                "Gauss_subcell_order":ng,"photon_L":L,
                "positive_phase_packets":m.momentum.packet_count,
                "nfev":solution.nfev,"Sigma":tail["Sigma"],
                "b":float(solution.y[1,-1]),
                "Pi_matter_J_m3":tail["Pi_matter_J_m3"],
                "H_per_s":tail["H"],
                "gamma_N0_error":float(abs(tail["N_gamma"][0]-1)),
                "nu_N0_error":float(abs(tail["N_nu"][0]-1)),
            })
        ref=MassiveRadialSpecies(src,2.7255,8,
            Sigma_ref=S,orientation=orient,kappa_gamma=.2,
            kappa_nu=.2,ne_source=donor,mass_fraction=.1,
            massive_A=A,mass_over_T_ref=mass,imax=2)
        ref_solution,ref_states,_=ref.integrate(n=101,rtol=2e-12,atol=2e-14)
        d=ref_states[-1]
        comparison={
            "source_minus_fine_Sigma_abs":abs(rows[1]["Sigma"]-rows[2]["Sigma"]),
            "source_minus_BASS_PR140_Sigma_abs":abs(rows[1]["Sigma"]-d["Sigma"]),
            "source_minus_fine_Pim_rel":abs(rows[1]["Pi_matter_J_m3"]-rows[2]["Pi_matter_J_m3"])/max(abs(rows[2]["Pi_matter_J_m3"]),1e-100),
            "fine_minus_BASS_PR140_Sigma_abs":abs(rows[2]["Sigma"]-d["Sigma"]),
        }
        if (comparison["source_minus_fine_Sigma_abs"]>1e-9
            or comparison["source_minus_BASS_PR140_Sigma_abs"]>1e-8):
            raise ArithmeticError("nonconverged canonical FV Einstein source")
        results.append({
            "case":name,
            "initial":{"Sigma_ref":S,"orientation":orient,
                       "m_over_Tref":mass,"A_massive":A},
            "trials":rows,
            "BASS_PR140_independent":{"Sigma":d["Sigma"],
                 "Pi_matter_Jm3":d["Pi_matter_J_m3"]},
            "errors":comparison
        })
    receipt={
        "schema":"rei.bass.positive_canonical_FV_convergence.v1",
        "reference_original_REI_source":"frozen HHe ne(a) from source PR140/PR137",
        "donor_history_SHA256":donor_info["history_sha256"],
        "original_BASS160_massive_source_sha256":"1857567475b1c8586298f868e5420aae7a72e8e1ba69cce6a5b21bfca4fdd790",
        "cases":results,
        "status":"PASS_SCOPED_CANONICAL_CELL_QUADRATURE_CONVERGENCE",
        "limits":"Finite resolution and original electron-source interpolation separate; no two-way HHe or polarized Thomson.",
    }
    (out/"CONVERGENCE.json").write_text(
        json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    return receipt


def plots(out:Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    data=list(csv.DictReader((out/"CANONICAL_FV_HISTORY.csv").open()))
    if len(data)!=8*121:raise ValueError("no complete actual source histories")
    cases=["gamma_nu_only","massive_plus","massive_minus",
           "massive_relativistic","massive_cold"]
    for column,label,filename in [
        ("Sigma","Normalized shear Sigma = sqrt(3)|s|/H",
          "CANONICAL_FV_SIGMA_HISTORY.png"),
        ("Pi_massive_J_m3","Positive canonical FV massive tensor pi_s [Pa]",
          "CANONICAL_FV_MASSIVE_PI.png"),
        ("massive_rho_norm","Normalized positive massive energy density",
          "CANONICAL_FV_MASSIVE_ENERGY.png"),
    ]:
        fig,ax=plt.subplots(figsize=(8,4.7))
        for case in cases:
            sub=[x for x in data if x["case"]==case]
            if len(sub)!=121:raise ValueError(f"incomplete case {case}")
            ax.plot([float(x["zbar"]) for x in sub],
                    [float(x[column]) for x in sub],label=case,lw=1.3)
        ax.set_xlim(20,4)
        ax.set_xlabel("Mean redshift zbar")
        ax.set_ylabel(label)
        ax.grid(alpha=.2)
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(out/filename,dpi=150)
        plt.close(fig)
    return 3


if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--original-owner",required=True,type=Path)
    cli.add_argument("--output",required=True,type=Path)
    args=cli.parse_args()
    rec=verify(args.original_owner,args.output)
    num=plots(args.output)
    print(json.dumps({"status":rec["status"],
       "source_to_fine_Sigma_errors":[x["errors"]["source_minus_fine_Sigma_abs"] for x in rec["cases"]],
       "source_to_BASS_PR140_Sigma_errors":[x["errors"]["source_minus_BASS_PR140_Sigma_abs"] for x in rec["cases"]],
       "figures":num},indent=2))
