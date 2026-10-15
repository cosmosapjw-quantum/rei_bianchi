#!/usr/bin/env python3
"""C14 reproducible source-native C13 HHe electron + PR137 Thomson study."""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
import time

import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import dynamic_thomson as s
from dynamic_thomson import (PhysicalThomson,OneWayThomson,ElectronSource,
                            Scenario,NativeStellarSource,ROOT,run_c13)

QS=(-.01,-.005,0.,.005,.01)
KAPPA=.2


def scientific_summary(x):
    out={k:x[k] for k in (
        "q","L","kappa_gamma","kappa_nu","scattering",
        "Omega_photon_and_neutrino","tau_C13_trapezoid",
        "tau_thomson_DOP853","tau_independent_quad",
        "tau_relative_disagreement_C13_vs_quad",
        "tau_relative_disagreement_solver_vs_quad",
        "max_unpolarized_energy_mono_RHS_residual",
        "max_photon_and_neutrino_number_mono_RHS_residual",
        "gamma_number_N0_max_drift","nu_number_N0_max_drift"
    )}
    return {**out,"initial":x["history"][0],"final":x["history"][-1],
            "original_C13_final":{k:x["c13_final"][k] for k in
              ("x_HII","x_HeII","x_HeIII","Tgas_K","photon_N_perH",
               "source_N_perH","Pi_ion_Pa","thomson_tau","Sigma")}}


def one_q(q:float):
    m=Scenario(ROOT)
    src=NativeStellarSource.load(m,
        ROOT/"research/rei_c13_live_source_20261015/NATIVE_SOURCE_8X8.csv")
    c13=run_c13(q,src,nstep=128,coalescence_budget=(1e-12,1e-11))
    electrons=ElectronSource.from_real_c13(c13,m)
    configs=((KAPPA,KAPPA,True),(KAPPA,KAPPA,False),(0.,0.,True))
    rows={}
    for ka,kn,on in configs:
        label=("seeded_on" if on else "seeded_off") if ka else "isotropic_on"
        response=OneWayThomson(electrons,
              PhysicalThomson(ka,kn,L=8,scattering=on)).run(steps=97)
        rows[label]=response
    on=rows["seeded_on"]["history"][-1]
    off=rows["seeded_off"]["history"][-1]
    delta={"gamma_J2_collided_minus_free":on["gamma_energy_J2"]-off["gamma_energy_J2"],
           "neutrino_J2_collided_minus_free":on["nu_energy_J2"]-off["nu_energy_J2"],
           "physical_Pi_gamma_collided_minus_free_Pa":
              on["Pi_gamma_physical_Pa"]-off["Pi_gamma_physical_Pa"],
           "Einstein_shear_source_gamma_s2":
              on["shear_rhs_source_gamma_s2"],
           "Einstein_shear_source_nu_s2":
              on["shear_rhs_source_nu_s2"],
           "C13_ionizing_photon_shear_source_s2":
              s.KAPPA*c13["end"]["Pi_ion_Pa"],
           "gamma_to_neutrino_energy_density_ratio":
              rows["seeded_on"]["Omega_photon_and_neutrino"]["Omega_gamma"]/
              rows["seeded_on"]["Omega_photon_and_neutrino"]["Omega_nu"],
           "same_C13_electron_history_all_controls":True}
    if abs(delta["neutrino_J2_collided_minus_free"])>1e-12:
        raise RuntimeError("THOMSON_ON_NEUTRINO_CHANNEL")
    return {"q":q,"controls":{k:scientific_summary(v) for k,v in rows.items()},
            "delta_collision":delta,
            "representative_history":rows["seeded_on"]["history"],
            "real_C13_final":c13["end"],
            "C13_source_ledger":[c13["max_number_abs_residual"],
                                 c13["max_energy_eV_perH_residual"]]}


def dense_and_parallel():
    t0=time.perf_counter()
    serial=[one_q(q) for q in QS]
    serial_s=time.perf_counter()-t0
    t0=time.perf_counter()
    with ProcessPoolExecutor(max_workers=3) as pool:
        parallel=list(pool.map(one_q,QS))
    parallel_s=time.perf_counter()-t0
    if serial!=parallel:
        # All stored science floats and distributions are deterministic, no
        # run timing values are stored per q.
        raise AssertionError("SERIAL_PARALLEL_SCIENCE_NOT_IDENTICAL")
    return {"scenarios":serial,"benchmark":{
          "q_cases":list(QS),"workers":3,"whole_process_serial_s":serial_s,
          "whole_process_three_workers_s":parallel_s,
          "speedup":serial_s/parallel_s,
          "science_bitwise_identical":True}}


def donor_refinement():
    m=Scenario(ROOT)
    src=NativeStellarSource.load(m,
         ROOT/"research/rei_c13_live_source_20261015/NATIVE_SOURCE_8X8.csv")
    rows=[]
    for n in (32,64,128,256):
        donor=run_c13(0.,src,nstep=n,coalescence_budget=(1e-12,1e-11))
        elec=ElectronSource.from_real_c13(donor,m)
        hierarchy=OneWayThomson(elec,PhysicalThomson(.2,.2,L=8)).run(steps=65)
        rows.append({"C13_steps":n,
                     "tau":hierarchy["tau_independent_quad"],
                     "solver":hierarchy["tau_thomson_DOP853"],
                     "gamma_J2":hierarchy["history"][-1]["gamma_energy_J2"],
                     "ion_xHII":donor["end"]["x_HII"]})
    gaps=[abs(rows[i+1]["tau"]-rows[i]["tau"]) for i in range(3)]
    order=math.log(gaps[0]/gaps[1],2) if gaps[1]>0 else None
    return {"cases":rows,"tau_difference_doubling":gaps,
            "first_observed_refinement_order":order,
            "scope":"donor a-grid coupled uncertainty, not full global tau error proof"}


def hierarchy_resolution(q=.01):
    m=Scenario(ROOT)
    src=NativeStellarSource.load(m,
          ROOT/"research/rei_c13_live_source_20261015/NATIVE_SOURCE_8X8.csv")
    electron=ElectronSource.from_real_c13(
          run_c13(q,src,nstep=128,coalescence_budget=(1e-12,1e-11)),m)
    out=[]
    for l in (4,8,12,16):
        rhs=OneWayThomson(electron,PhysicalThomson(.2,.2,L=l)).run()
        out.append({"L":l,"gamma_J2":rhs["history"][-1]["gamma_energy_J2"],
                    "gamma_J0":rhs["history"][-1]["gamma_energy_J0"],
                    "nu_J2":rhs["history"][-1]["nu_energy_J2"],
                    "tau":rhs["tau_thomson_DOP853"]})
    return {"q":q,"cases":out,
            "observed_L_difference":
            [abs(out[i+1]["gamma_J2"]-out[i]["gamma_J2"]) for i in range(3)]}


def matrix_benchmark():
    for _ in range(3):
        s.legendre_matrix(8,power=4)
        s._cached_source_angular_operators(8)
    uncached=[];cached=[]
    for _ in range(7):
        t=time.perf_counter()
        A=s.legendre_matrix(8,power=4)
        N=s.legendre_matrix(8,power=3)
        C=s.thomson_coeffs(8)
        uncached.append(time.perf_counter()-t)
        t=time.perf_counter()
        CA,CN,CC=s._cached_source_angular_operators(8)
        cached.append(time.perf_counter()-t)
        np.testing.assert_array_equal(CA,A)
        np.testing.assert_array_equal(CN,N)
        np.testing.assert_array_equal(CC,C)
    return {"L":8,"repetitions":7,
            "uncached_median_s":statistics.median(uncached),
            "cached_median_s":statistics.median(cached),
            "microkernel_speedup":statistics.median(uncached)/statistics.median(cached),
            "shared_read_only_arrays":True,
            "not_full_native_solver_speedup":True}


def save_plot_and_csv(scenarios):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out=HERE/"C14_HHE_THOMSON_HISTORY.csv"
    with out.open("w",newline="") as f:
        wr=csv.writer(f,lineterminator="\n")
        cols=("a","zbar","tau","electron_ne_cm3","gamma_energy_J2",
              "nu_energy_J2","gamma_number_N0","nu_number_N0",
              "Pi_gamma_physical_Pa","Pi_nu_physical_Pa")
        wr.writerow(("q",)+cols)
        for r in scenarios:
            for h in r["representative_history"]:
                wr.writerow((r["q"],)+tuple(h[key] for key in cols))
    fig,axes=plt.subplots(2,1,figsize=(9,7.2),sharex=True)
    for r in scenarios:
        if r["q"] not in (0.,-.01,.01):continue
        data=r["representative_history"]
        z=[x["zbar"] for x in data]
        axes[0].plot(z,[x["gamma_energy_J2"] for x in data],
                     label=f"photon, q={r['q']:+.2f}")
        axes[0].plot(z,[x["nu_energy_J2"] for x in data],
                     ls=":",label=f"neutrino, q={r['q']:+.2f}")
        axes[1].plot(z,[x["tau"] for x in data],label=f"q={r['q']:+.2f}")
    axes[0].set_ylabel("J2 (kappa=0.2 illustrative seed)")
    axes[1].set_ylabel("Thomson optical depth")
    axes[1].set_xlabel("Mean redshift (short a=0.1999 to 0.2 interval)")
    for ax in axes:
        ax.grid(alpha=.25)
        ax.legend(fontsize=8,ncol=2)
    axes[0].set_title("C14 actual C13 H/He electron history -> source-locked PR137 LRS Thomson")
    axes[0].set_xlim(1/.1999-1,4.)
    fig.tight_layout()
    fig.savefig(HERE/"C14_HHE_THOMSON_HISTORY.png",dpi=140)
    plt.close(fig)
    return {"csv":out.name,"plot":"C14_HHE_THOMSON_HISTORY.png",
            "rows":sum(len(z["representative_history"]) for z in scenarios)}


def main():
    start=time.perf_counter()
    allcases=dense_and_parallel()
    results={"schema":"rei.c14.actual_C13_electrons_BASS_PR137_Thomson_gamma_nu.v1",
        "source":s.validate_source_sha(),
        "C13_native_MD14_source":"MD14_Z002_FESC_BB50K_13P6_100_V1",
        "science_scope":"a=.1999 to .2 real HHe source/expansion/CaseA prescribed q, one-way unpolarized Thomson photon/nu hierarchy, no Einstein feedback or polarization",
        "signed_q_cases":allcases["scenarios"],
        "parallel":allcases["benchmark"],
        "rate_donor_refinement":donor_refinement(),
        "multipole_resolution":hierarchy_resolution(),
        "matrix_operator_caching":matrix_benchmark(),
        "plots":save_plot_and_csv(allcases["scenarios"])}
    results["total_wall_s"]=time.perf_counter()-start
    target=HERE/"C14_STUDY_RESULTS.json"
    target.write_text(json.dumps(results,indent=2)+"\n")
    print("PARALLEL",results["parallel"])
    print("CACHED",results["matrix_operator_caching"])
    for q in results["signed_q_cases"]:
        res=q["controls"]["seeded_on"]
        print("q",q["q"],"tau",res["tau_thomson_DOP853"],
              "delta J2",q["delta_collision"]["gamma_J2_collided_minus_free"],
              "nu delta",q["delta_collision"]["neutrino_J2_collided_minus_free"],
              "Pi source",res["final"]["Pi_gamma_physical_Pa"],
              "C13 xHII",res["original_C13_final"]["x_HII"])
    print("TOTAL_WALL",results["total_wall_s"])

if __name__=="__main__":main()
