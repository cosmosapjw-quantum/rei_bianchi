#!/usr/bin/env python3
"""C13 short-interval dynamic source science, refinements and real benchmarks."""
from __future__ import annotations
import csv,hashlib,json,math,os,sys,time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from statistics import median
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from short_interval import (Scenario,NativeStellarSource,PhotonCloud,run,START,STOP,
        independent_scalar_killing)
from supplier_snapshot import run_real_source_bound

ALL_Q=(-.01,-.005,0.,.005,.01)
COALESCE_BUDGET=(1e-12,1e-11)
KEYS=("x_HII","x_HeII","x_HeIII","Tgas_K","photon_N_perH",
      "photon_U_eV_perH","thomson_tau","Pi_ion_Pa")


def load(name):
    return NativeStellarSource.load(Scenario(ROOT),HERE/f"NATIVE_SOURCE_{name}.csv")

def compressed_case(job):
    q,grid,n,thin=job
    src=load(grid)
    return run(q,src,nstep=n,coalescence_budget=COALESCE_BUDGET if thin else None)

def case_compact(x):
    return {"q":x["q"],"a_range":x["a_range"],"nstep":x["nstep"],
            "source_grid":x["source_grid"],
            "end":{k:x["end"][k] for k in KEYS+(
                "Sigma","shear_orientation","Pi_CMB_source_Pa",
                "source_N_perH","source_E_eV_perH","escape_E_eV_perH",
                "recomb_e_perH","geometry_work_eV_perH",
                "packet_count","packet_live_bytes")},
            "source_quadrature_relative_error":x["source_midpoint_relative_error"],
            "max_number_absolute_ledger_residual":x["max_number_abs_residual"],
            "max_energy_eV_perH_ledger_residual":x["max_energy_eV_perH_residual"],
            "maximum_packets":x["maximum_packets"],
            "coalescence_admitted_count":x["coalescence_admitted_count"],
            "coalescence_holds":x["coalescence_holds"],
            "max_coalescence_event_abs_perH":x["coalescence_max_event_abs_perH"],
            "max_coalescence_heat_abs_eV_perH":x["coalescence_max_heat_abs_eV_perH"]}


def step_convergence():
    src=load("8X8")
    cases=[run(0.,src,nstep=n) for n in (8,16,32,64,128)]
    data={}
    for key in ("x_HII","x_HeII","Tgas_K","photon_N_perH","thomson_tau"):
        gaps=[abs(cases[i+1]["end"][key]-cases[i]["end"][key]) for i in range(4)]
        orders=[math.log(gaps[i]/gaps[i+1],2) if gaps[i+1]>0 and gaps[i]>0 else None
                for i in range(3)]
        data[key]={"adjacent_grid_delta":gaps,"self_convergence_orders":orders}
    return {"grid":[8,16,32,64,128],"metrics":data,
            "source_midpoint_errors":[c["source_midpoint_relative_error"] for c in cases],
            "finest":case_compact(cases[-1])},cases[-1]


def native_spectral_angular_convergence():
    out=[]
    for q in (0.,.01):
        cases={name:run(q,load(name),nstep=64)
               for name in ("4X8","8X8","16X8","32X8","8X16")}
        ref=cases["32X8"]["end"]
        out.append({"q":q,"nstep":64,"cases":{name:case_compact(r) for name,r in cases.items()},
                    "absolute_vs_32X8":{name:{k:abs(r["end"][k]-ref[k]) for k in KEYS}
                                         for name,r in cases.items()}})
    return out


def paired_positive_compression():
    pairs=[]
    for q in (0.,-.01,.01):
        src=load("8X8")
        base=run(q,src,nstep=128)
        slim=run(q,src,nstep=128,coalescence_budget=COALESCE_BUDGET)
        absdiff={k:abs(base["end"][k]-slim["end"][k]) for k in KEYS}
        pairs.append({"q":q,"dense":case_compact(base),"coalesced":case_compact(slim),
                      "absolute_endpoint_delta":absdiff,
                      "all_stored_states_positive_and_ledgered":True})
    return pairs


def cpu_benchmark():
    src=load("8X8")
    trials={}
    for thin in (False,True):
        tag="positive_two_moment" if thin else "dense"
        args={"nstep":128,"coalescence_budget":COALESCE_BUDGET if thin else None}
        for _ in range(2):run(0.,src,**args)
        elapsed=[]
        for _ in range(7):
            t=time.perf_counter()
            x=run(0.,src,**args)
            elapsed.append(time.perf_counter()-t)
        trials[tag]={"wall_s":elapsed,"median_s":median(elapsed),
                     "final_packet_count":x["end"]["packet_count"],
                     "final_photon_cloud_bytes":x["end"]["packet_live_bytes"],
                     "source_and_rate_preparation_included":True}
    return {"problem":"q0 fixed native source 8X8 nstep128, same C11 CaseA and geometry",
            "BLAS_threads":1,"warm_repeats":7,
            "measured":trials,
            "median_total_speedup":trials["dense"]["median_s"]/trials["positive_two_moment"]["median_s"],
            "final_photon_memory_factor":trials["dense"]["final_photon_cloud_bytes"]/trials["positive_two_moment"]["final_photon_cloud_bytes"],
            "no_whole_native_AX08_runtime_claim":True}


def vector_killing_benchmark():
    rng=np.random.default_rng(11);N=8192
    E=rng.uniform(13.6,100.,N); mu=rng.uniform(-.999,.999,N)
    sky=PhotonCloud(E,mu,np.ones(N)/N)
    da=.0003;db=.000015
    for _ in range(2):
        out=sky.drift(da,db)
        sc=[independent_scalar_killing(float(e),float(m),da,db) for e,m in zip(E,mu)]
    vec=[];scal=[]
    for _ in range(5):
        t=time.perf_counter();out=sky.drift(da,db);vec.append(time.perf_counter()-t)
        t=time.perf_counter();sc=[independent_scalar_killing(float(e),float(m),da,db) for e,m in zip(E,mu)];scal.append(time.perf_counter()-t)
    S=np.asarray(sc)
    err=float(max(np.max(abs(out.E-S[:,0])/E),np.max(abs(out.mu-S[:,1]))))
    assert err<5e-15
    return {"packets":N,"vector_median_s":median(vec),"scalar_median_s":median(scal),
            "speedup":median(scal)/median(vec),"max_relative_error":err,
            "microkernel_only":True}


def parallel_cases():
    jobs=[(q,"8X8",64,True) for q in ALL_Q]
    t=time.perf_counter();serial=[case_compact(compressed_case(job)) for job in jobs]
    serial_sec=time.perf_counter()-t
    t=time.perf_counter()
    with ProcessPoolExecutor(max_workers=3) as pool:
        simultaneous=[case_compact(x) for x in pool.map(compressed_case,jobs)]
    parallel_sec=time.perf_counter()-t
    assert serial==simultaneous
    return {"q_cases":list(ALL_Q),"workers":3,"serial_wall_s":serial_sec,
            "parallel_wall_s":parallel_sec,"speedup":serial_sec/parallel_sec,
            "all_scientific_floats_identical":True,"source_mode":"real owner MD14 8X8"}


def save_history(ref):
    path=HERE/"LIVE_SOURCE_ABUNDANCE_HISTORY.csv"
    with path.open("w",newline="") as f:
        writer=csv.writer(f,lineterminator="\n")
        fields=["a","zbar","elapsed_s","x_HI","x_HII","x_HeI","x_HeII",
                "x_HeIII","Tgas_K","photon_N_perH","source_N_perH",
                "thomson_tau","Sigma","Pi_ion_Pa","Pi_CMB_source_Pa"]
        writer.writerow(fields)
        for h in ref["history"]:
            writer.writerow([h["a"],h["zbar"],h["elapsed_s"],
                1-h["x_HII"],h["x_HII"],1-h["x_HeII"]-h["x_HeIII"],
                h["x_HeII"],h["x_HeIII"],h["Tgas_K"],
                h["photon_N_perH"],h["source_N_perH"],h["thomson_tau"],
                h["Sigma"],h["Pi_ion_Pa"],h["Pi_CMB_source_Pa"]])
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    h=ref["history"]
    x=np.array([r["zbar"] for r in h])
    fig,axs=plt.subplots(3,1,figsize=(9,10),sharex=True)
    for name,values in (("HI",[1-r["x_HII"] for r in h]),
                        ("HII",[r["x_HII"] for r in h]),
                        ("HeI",[1-r["x_HeII"]-r["x_HeIII"] for r in h]),
                        ("HeII",[r["x_HeII"] for r in h]),
                        ("HeIII",[r["x_HeIII"] for r in h])):
        axs[0].plot(x,values,label=name)
    axs[0].set_ylabel("Ion fraction of its element");axs[0].legend(ncol=5,fontsize=8)
    axs[1].plot(x,[r["Tgas_K"] for r in h],label="Gas temperature [K]")
    axs[1].set_ylabel("Gas temperature [K]")
    axs[2].plot(x,[r["photon_N_perH"] for r in h],label="Remaining photons/H")
    axs[2].plot(x,[r["source_N_perH"] for r in h],label="Cumulative emitted photons/H")
    axs[2].set_ylabel("Photons per H");axs[2].set_xlabel("Mean redshift (short near-z4 interval)")
    axs[2].legend(fontsize=8)
    for ax in axs:ax.grid(alpha=.23)
    axs[0].set_title("C13 source-backed short interval: NOT the complete EoR history")
    axs[0].set_xlim(x[0],x[-1])
    fig.tight_layout()
    fig.savefig(HERE/"LIVE_SOURCE_ABUNDANCE_HISTORY.png",dpi=150)
    plt.close(fig)
    return {"csv":path.name,"plot":"LIVE_SOURCE_ABUNDANCE_HISTORY.png","rows":len(h)}


def main():
    t=time.perf_counter()
    convergence,ref=step_convergence()
    result={"schema":"rei.c13.md14_native_source_bass_c11_pi_dynamic.v1",
            "physical_scope":"zbar4.0025-to4, H/He receiver starts prescribed xHII=.4 xHeII=.5 xHeIII=.3 T=12000 K; source has real owner MD14 photons; no full cosmic initial history",
            "source_original_rust_sha256":hashlib.sha256((ROOT/"rust/rei_microphysics/src/axbi_sources.rs").read_bytes()).hexdigest(),
            "c11_rate_table_sha256":hashlib.sha256((ROOT/"research/source07_c11_casea_20261015/owner_grackle_rates_129.csv").read_bytes()).hexdigest(),
            "source_grid_sha256":{name:load(name).source_sha256 for name in ("4X8","8X8","16X8","32X8","8X16")},
            "independent_bass_cr_true_child_bound":run_real_source_bound(),
            "step_convergence":convergence,
            "source_resolution":native_spectral_angular_convergence(),
            "compression_comparator":paired_positive_compression(),
            "exact_killing_vector_benchmark":vector_killing_benchmark(),
            "whole_c13_source_chemistry_benchmark":cpu_benchmark(),
            "independent_signed_q_parallelism":parallel_cases(),
            "history_outputs":save_history(ref)}
    result["elapsed_total_s"]=time.perf_counter()-t
    (HERE/"C13_STUDY_RESULTS.json").write_text(json.dumps(result,indent=2)+"\n")
    for k in ("whole_c13_source_chemistry_benchmark","exact_killing_vector_benchmark",
              "independent_signed_q_parallelism"):
        print(k,json.dumps(result[k],indent=2)[:2200],flush=True)
    for k,v in convergence["metrics"].items():
        print("SELF_CONVERGENCE",k,v["self_convergence_orders"],flush=True)
    print("STUDY_C13_TOTAL_S",result["elapsed_total_s"],flush=True)
if __name__=="__main__":main()
