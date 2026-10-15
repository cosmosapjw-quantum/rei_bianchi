#!/usr/bin/env python3
"""Actual source-matched gamma/neutrino Boltzmann hierarchy with Einstein backreaction.

Full radiation energy-density split from source-locked Tcmb0 and rounded Omega_r;
Thomson collision on gamma only; gamma + massless-nu Pi source the shear.
Not full polarized source-coupled HHe/REI cosmological UV radiative transfer.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from run_hierarchy import source_lock,actual_electrons,public_sigma_from_q,HERE,sha
from species_hierarchy import SpeciesHierarchy

def run():
    c=source_lock()
    donor,donor_meta=actual_electrons(Path.home()/"Dropbox/bianchi/rei_bianchi")
    setups=[
      (0.,0.,0.,False,0.),
      (0.,.2,.2,False,0.),
      (0.,.2,.2,True,0.),
      (0.,.2,0.,True,0.),
      (0.,0.,.2,True,0.),
      (+.005,.2,.2,True,0.),
      (-.005,.2,.2,True,0.),
      (+.005,.2,.2,True,.02),
    ]
    lines=[]
    figs=[]
    for i,(q,kg,kn,do_thom,nu) in enumerate(setups):
        sig,eps=public_sigma_from_q(q)
        m=SpeciesHierarchy(c,2.7255,ellmax=8,Sigma_ref=sig,
                           orientation=eps,kappa_gamma=kg,kappa_nu=kn,
                           ne_source=donor if do_thom else None,matter_nu_viscosity=nu)
        s,info,wall=m.integrate(n=501)
        last=info[-1]
        energy_rad=last["rad_energy_norm"]*c.rhocrit_j_m3
        if abs(last["Pi_radiation_J_m3"]-last["Pi_gamma_J_m3"]-last["Pi_nu_J_m3"])>1e-25:
            raise RuntimeError("SOURCE_RADIATION_PI_SUM_NOT_CONSERVING")
        # Prove true independent gamma/nu photon number and separate Thomson support.
        if any(abs(x["N_gamma"][0]-1)>2e-12 or abs(x["N_nu"][0]-1)>2e-12 for x in info):
            raise RuntimeError("PHOTON_AND_NEUTRINO_NUMBER_MONOPOLE_NOT_PRESERVED")
        if not do_thom and kg==kn and nu==0:
            from run_hierarchy import KineticStressBackground,Initial
            bass=KineticStressBackground(Initial(q,kg))
            ref=bass.at_a(c.aend)
            mismatch=abs(s.y[1,-1]-ref["b"])
            if mismatch>1e-10:raise RuntimeError("BASS_MASSLESS_RADIATION_LIMIT_WRONG")
        else:mismatch=None
        rec={
            "case":i,"Sigma_ref":sig,"epsilon_sigma_ref":eps,
            "kappa_gamma":kg,"kappa_massless_nu":kn,
            "has_original_AX08_ne_Thomson":do_thom,
            "viscous_matter_nu":nu,
            "Omega_gamma":m.omega_gamma,"Omega_nu_massless":m.omega_nu,
            "Omega_gamma_over_rounded_Omega_r":m.f_gamma,
            "Omega_massless_nu_over_rounded_Omega_r":m.f_nu,
            "endpoint_Sigma":last["Sigma"],
            "endpoint_gamma_J0":float(last["E_gamma"][0]),
            "endpoint_gamma_J2":float(last["E_gamma"][2]),
            "endpoint_neutrino_J0":float(last["E_nu"][0]),
            "endpoint_neutrino_J2":float(last["E_nu"][2]),
            "endpoint_gamma_N0":float(last["N_gamma"][0]),
            "endpoint_neutrino_N0":float(last["N_nu"][0]),
            "endpoint_Pi_gamma_Jm3":last["Pi_gamma_J_m3"],
            "endpoint_Pi_neutrino_Jm3":last["Pi_nu_J_m3"],
            "endpoint_Pi_matter_Jm3":last["Pi_matter_J_m3"],
            "endpoint_Pi_total_radiation_Jm3":last["Pi_radiation_J_m3"],
            "source_BASS_no_thomson_b_difference":mismatch,
            "nfev":s.nfev,"ODE_wall_s":wall,
        }
        lines.append(rec)
        figs.append((rec,s,info))
    # Strict collision-only discriminant at Sigma_ref=0, two positive quadrupoles:
    clean=lines[1];scattered=lines[2]
    if not(scattered["endpoint_gamma_J2"]<clean["endpoint_gamma_J2"] and
           scattered["endpoint_neutrino_J2"]>=clean["endpoint_neutrino_J2"]):
        raise RuntimeError("THOMSON_SOURCE_SPECIES_FIREWALL_BROKEN")
    out={
        "schema":"rei.BASS_PR159.REI_Thomson.positive_gamma_nu.v1",
        "status":"GAMMA_ONLY_THOMSON_AND_NEUTRINO_COLLISIONLESS_EINSTEIN_PI_BACKREACTION_VERIFIED",
        "BASS_provider_HEAD":"fa8c60fba73ce5dd40ce47833749ae70dd0c64d7",
        "source_rounded_Omega_r":c.omega_r,
        "Tcmb0_K":2.7255,
        "gamma_fraction":lines[0]["Omega_gamma_over_rounded_Omega_r"],
        "massless_nu_fraction":lines[0]["Omega_massless_nu_over_rounded_Omega_r"],
        "real_HHe_donor_source":donor_meta,
        "case_results":lines,
        "physics":{
           "valid":"Einstein source sees Pi_gamma+Pi_nu+Pi_matter; gamma only is Thomson damped; all number N0 conserved; symmetric LRS source",
           "not_implemented":"full polarized E/B hierarchy, source-resolved photoionizing pressure stress, dynamical HHe microphysical energy/chemistry feedback into Sigma over z20->4, independent massive neutrinos",
           "optical_source":"actual frozen ZERO history uses smooth donor positive C2 interpolation; measurable error separate"
        },
        "scientific_admission":"NOT_ISSUED"
    }
    (HERE/"results/gamma_neutrino_separate.json").write_text(json.dumps(out,indent=2)+"\n")
    fig,(ax,bx)=plt.subplots(2,1,figsize=(10,8),constrained_layout=True)
    for rec,s,info in figs:
        if rec["Sigma_ref"]>0:continue
        if rec["kappa_gamma"]!=.2:continue
        z=1/(c.aref*np.exp(s.t))-1
        label=f"Thomson={int(rec['has_original_AX08_ne_Thomson'])}, kappa_nu={rec['kappa_massless_nu']:.1f}"
        ax.plot(z,[p["Sigma"] for p in info],label=label)
        bx.plot(z,[p["Pi_gamma_J_m3"]+p["Pi_nu_J_m3"] for p in info],label=label)
    for panel in (ax,bx):
        panel.invert_xaxis();panel.grid(alpha=.3);panel.legend(fontsize=8);panel.set_xlabel("Mean redshift")
    ax.set_ylabel("Sigma = sqrt(sigma_ab sigma^ab/2)/H")
    bx.set_ylabel("Pi_gamma + Pi_massless_nu [J/m^3]")
    fig.suptitle("Physical photon/neutrino radiation partition, BASS multipole-driven Einstein backreaction")
    fig.savefig(HERE/"results/gamma_nu_partition_backreaction.png",dpi=180)
    plt.close(fig)
    print(json.dumps({
        "status":out["status"],"f_gamma":out["gamma_fraction"],
        "gamma_J2_no_thomson":clean["endpoint_gamma_J2"],
        "gamma_J2_with_thomson":scattered["endpoint_gamma_J2"],
        "neutrino_J2_with_thomson":scattered["endpoint_neutrino_J2"],
        "Sigma_no_thomson":clean["endpoint_Sigma"],
        "Sigma_with_thomson":scattered["endpoint_Sigma"]},indent=2))
if __name__=="__main__":run()
