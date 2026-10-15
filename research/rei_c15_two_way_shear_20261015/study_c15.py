#!/usr/bin/env python3
"""Execute actual C15 two-way Einstein–Boltzmann + native MD14/HHe source study.

Supports marked short z≈4 range with manufactured warm CaseA chemistry IC only.
Actually checks time/angular/spectral/compression performance, never source
continuum certification. New metric is fed back into C13 source packets and
chemistry proper time; vacuum gamma/nu and UV stress feed Einstein.
"""
from __future__ import annotations
import concurrent.futures as cf
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from c15_coupled import (Config,Coupled,NativeStellarSource,Scenario,
    ROOT,THOMSON_RATE,START,STOP,KAPPA)

HERE=Path(__file__).resolve().parent
RES=HERE/"results"
STEPSET=(8,16,32,64,128)

def source_load(name="8X8"):
    return NativeStellarSource.load(Scenario(ROOT),
               ROOT/f"research/rei_c13_live_source_20261015/NATIVE_SOURCE_{name}.csv")
def solve(q=0.,kg=.2,kn=.2,nstep=64,compressed=True,source="8X8",
          uv_feedback=True,L=8,thomson=True):
    c=Coupled(Config(legacy_q_for_locked_source=q,kappa_gamma=kg,kappa_nu=kn,
        nstep=nstep,compression=compressed,L=L,uv_stress_in_shear=uv_feedback,
        thomson=thomson),source_load(source))
    return c.run()
def subset(z):
    return {
      "Sigma_ref":z["Sigma_ref_user"],"epsilon_sigma":z["orientation_initial"],
      "kappa_gamma":z["numerical"]["kappa_gamma"],"kappa_nu":z["numerical"]["kappa_nu"],
      "L":z["numerical"]["L"],"nstep":z["numerical"]["nstep"],
      "thomson":z["numerical"]["energy_gamma_nu_Thomson"],
      "compression":z["numerical"]["coalescence"],
      "uv_pi_sourced_in_Einstein":z["numerical"]["uv_pi_in_shear"],
      "elapsed_proper_s":z["endpoint"]["elapsed_s"],
      "Sigma_end":z["endpoint"]["Sigma"],
      "b_end":z["endpoint"]["b"],
      "Tgas_K":z["endpoint"]["Tgas_K"],
      "xHII":z["endpoint"]["x_HII"],
      "xHeII":z["endpoint"]["x_HeII"],
      "xHeIII":z["endpoint"]["x_HeIII"],
      "nuE2":z["endpoint"]["radiation_nu_E2"],
      "gammaE2":z["endpoint"]["radiation_gamma_E2"],
      "Pi_CMB_neutrinos_Pa":z["endpoint"]["Pi_gamma_and_nu_Pa"],
      "Pi_UV_Pa":z["endpoint"]["Pi_ion_Pa"],
      "tau_integrated":z["endpoint"]["tau_Thomson_DOP853"],
      "photon_NperH":z["endpoint"]["photon_N_perH"],
      "photon_U_eV_perH":z["endpoint"]["photon_U_eV_perH"],
      "photo_source_NperH":z["endpoint"]["source_N_perH"],
      "max_N_ledger_perH":z["numerical"]["max_photo_number_ledger_error_perH"],
      "max_E_ledger_eVperH":z["numerical"]["max_photo_energy_ledger_error_eV_perH"],
      "max_packet_count":max(r["packet_count"] for r in z["history"]),
      "wall_s":z["numerical"]["coupled_wall_s"],
      "RHS_evaluations":z["numerical"]["geometry_rhs_calls"],
      "clock_Picard_iters_per_macro_max":max(z["numerical"]["proper_clock_iterations"]),
    }
def study():
    t0=time.perf_counter()
    variants=[
       ("ISOTROPIC_FLRW", dict(q=0,kg=0,kn=0,nstep=64)),
       ("SEED_POSITIVE_RAD",dict(q=0,kg=.2,kn=.2,nstep=64)),
       ("POS_SHEAR",dict(q=.005,kg=.2,kn=.2,nstep=64)),
       ("NEG_SHEAR",dict(q=-.005,kg=.2,kn=.2,nstep=64)),
       ("POS_SHEAR_LARGE",dict(q=.01,kg=.2,kn=.2,nstep=64)),
       ("NEG_SHEAR_LARGE",dict(q=-.01,kg=.2,kn=.2,nstep=64)),
       ("NO_UV_PI_CONTROL",dict(q=.005,kg=.2,kn=.2,nstep=64,uv_feedback=False)),
       ("THOMSON_OFF_CONTROL",dict(q=0,kg=.2,kn=.2,nstep=64,thomson=False)),
       ("GAMMA_ONLY_KAPPA",dict(q=0,kg=.2,kn=0,nstep=64)),
       ("NU_ONLY_KAPPA",dict(q=0,kg=0,kn=.2,nstep=64)),
    ]
    outputs={}
    for name,p in variants:
        z=solve(**p)
        outputs[name]=z
        print("ACTUAL_C15",name,json.dumps(subset(z)),flush=True)
    times={}
    for name in ("ISOTROPIC_FLRW","SEED_POSITIVE_RAD"):
        p=dict(kg=0,kn=0) if name=="ISOTROPIC_FLRW" else dict(kg=.2,kn=.2)
        times[name]=[]
        for n in STEPSET:
            z=solve(nstep=n,**p)
            times[name].append(subset(z))
            print("REFINEMENT",name,n,z["endpoint"]["x_HII"],z["endpoint"]["Tgas_K"],
                  z["endpoint"]["Sigma"],z["numerical"]["coupled_wall_s"],flush=True)
    angular={}
    for L in (4,8,12):
        z=solve(q=0,nstep=64,kg=.2,kn=.2,L=L)
        angular[L]=subset(z)
    frequency={}
    for res in ("4X8","8X8","16X8","32X8"):
        z=solve(q=0,nstep=64,kg=.2,kn=.2,source=res)
        frequency[res]=subset(z)
    # Seven fresh matched whole-code timings on source gamma/nu + HHe chemistry,
    # real original stellar spectral cells, 64 time steps.
    bench={"uncompressed":[],"coalesced":[]}
    for _ in range(5):
        for name,flag in (("uncompressed",False),("coalesced",True)):
            z=solve(q=0,nstep=64,compressed=flag)
            bench[name].append({"wall_s":z["numerical"]["coupled_wall_s"],
                "max_packet_count":subset(z)["max_packet_count"],"output":subset(z)})
    early=bench["uncompressed"][-1]["output"]
    last=bench["coalesced"][-1]["output"]
    for fld,tol in (("xHII",3e-11),("Tgas_K",2e-8),("Sigma_end",3e-12),
                    ("Pi_UV_Pa",4e-27),("tau_integrated",2e-11)):
        if abs(early[fld]-last[fld])>tol:
            raise RuntimeError("C15_COMPRESSION_MATCHED_PHYSICS_BUDGET_HOLD:"+fld)
    best={
       "median_uncompressed_s":statistics.median(x["wall_s"] for x in bench["uncompressed"]),
       "median_coalesced_s":statistics.median(x["wall_s"] for x in bench["coalesced"]),
       "max_packets_uncompressed":max(x["max_packet_count"] for x in bench["uncompressed"]),
       "max_packets_coalesced":max(x["max_packet_count"] for x in bench["coalesced"]),
       "actual_scoped_minimal_ion_difference":early["xHII"]-last["xHII"],
       "actual_scoped_temperature_difference_K":early["Tgas_K"]-last["Tgas_K"],
       "all_measurements":bench
    }
    best["measured_full_C15_speedup"]=best["median_uncompressed_s"]/best["median_coalesced_s"]
    # No coordinate/time rescaling of source C13 initial chemistry.
    result={
       "schema":"rei.c15.coupled_phenomenological_short_window_study.v1",
       "status":"C15_ACTUAL_BIDIRECTIONAL_EINSTEIN_PSTF_UV_CASEA_SHORT_WINDOW_RUNS",
       "source_git_parent_PR139":"1ca73d64d3aaf7ea3ed4b7265522bbfdfae7e228",
       "source_hash":source_load().source_sha256,
       "physics":"exact C13 native stellar photon age/spectral/angle emissions, HHe photon photochem CaseA, C14 gamma+nu boltzmann J_l/N_l with only gamma Thomson and new Einstein H,s feedback, Killing source UV ray re-evolved each coupled step",
       "physics_caveat":"MD14 stellar reservoir & recombination escaped photon cosmological energy-momentum not closed; gas IC manufactured warm near z4; UV-induced perturbation below numerical detection; no polarization/matter Pi",
       "initial_cases":{k:subset(v) for k,v in outputs.items()},
       "proper_time_refinement":times,
       "angular_refinement":angular,
       "source_frequency_refinement":frequency,
       "performance_matched":best,
       "total_wall_s":time.perf_counter()-t0,
       "scientific_admission":"NOT_ISSUED"
    }
    (RES/"STUDY_C15.json").write_text(json.dumps(result,indent=2)+"\n")
    # Scientific graphs from actually executed coalesced source history.
    a=outputs["SEED_POSITIVE_RAD"]["history"]
    q=[outputs["POS_SHEAR"]["history"],outputs["NEG_SHEAR"]["history"]]
    fig,axes=plt.subplots(3,1,figsize=(10,10),constrained_layout=True)
    for title,history in [("Sigma_init=0,kappa=.2",a),
                          ("epsilon_sigma=+1",q[0]),("epsilon_sigma=-1",q[1])]:
        t=np.array([r["elapsed_s"] for r in history])/1e13
        axes[0].plot(t,[r["Sigma"] for r in history],label=title)
        axes[1].plot(t,[r["x_HII"] for r in history],label=title)
        axes[2].plot(t,[r["Tgas_K"] for r in history],label=title)
    for ax,title in zip(axes,("Hubble-normalized shear Sigma","Hydrogen ionized fraction","Thermal gas temperature [K]")):
        ax.set_xlabel("Local elapsed proper time [10^13 s]")
        ax.set_ylabel(title);ax.grid(alpha=.3);ax.legend(fontsize=8)
    fig.suptitle("C15 near z4: dynamically Einstein-coupled radiation/UV, source-native CaseA HHe; preliminary")
    fig.savefig(RES/"C15_Sigma_HHe_two_way.png",dpi=165)
    plt.close(fig)
    for label,full in (("SEED_POSITIVE_RAD",a),("POS_SHEAR",q[0])):
        with (RES/f"C15_{label}_HISTORY.csv").open("w") as f:
            import csv
            fields=list(full[0])
            writer=csv.DictWriter(f,fields,lineterminator="\n")
            writer.writeheader()
            for row in full:writer.writerow(row)
    print("STUDY_SUMMARY",json.dumps({
       "number_scenarios":len(variants),"proper_time_refinement":2*len(STEPSET),
       "angular":len(angular),"source_frequency":len(frequency),
       "compression_med_speedup":best["measured_full_C15_speedup"],
       "compression_packet_ratio":best["max_packets_uncompressed"]/best["max_packets_coalesced"],
       "elapsed_s":result["total_wall_s"]},indent=2))
if __name__=="__main__":study()
