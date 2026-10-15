#!/usr/bin/env python3
"""Real C15-native Case-A energy birth, exact angular envelope, opt-in isotropy,
independent Killing benchmark, matched time/angle convergence and signed Sigma.
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
import csv,json,math,statistics,sys,time,hashlib
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import recomb_angular as a


def physical_case(item):
    sig,ori,n,gauss=item
    p=a.c15.Parameters(sig,ori,.2,.2,.1,.5)
    return a.actual_C15_case(p,nsteps=n,nmu=gauss)


def concise(source):
    z=source["final"]
    keys=("escape_U_eV_perH","U_rec_eV_perH","Pi_rec_eV_perH",
          "cPz_rec_eV_perH","U_rec_Killing_work_eV_perH",
          "Pi_rec_lower","Pi_rec_upper","Pi_rec_Pa")
    return {"Sigma_initial":source["parameters"]["Sigma_initial"],
            "orientation":source["parameters"]["orientation"],
            "nsteps":source["nsteps"],"nmu":source["nmu"],
            "emission_clock":source["emission_clock"],
            "final":{k:z.get(k) for k in keys},
            "linearized_isotropic_abs_dSigma":
                source["linearized_abs_delta_Sigma_from_conditional_isotropic_CaseA"],
            "sharp_positive_angular_source_abs_dSigma_envelope":
                source["sharp_linearized_abs_delta_Sigma_envelope_any_positive_angles"],
            "linearized_sign_sensitive_ds_interval":
                source["linearized_shear_source_response_interval_per_s"],
            "original_C15_energy_ledger_replaced_residual":
                source["max_hhe_energy_ledger_replacement_abs_eV_H"]}


def signed_models():
    return [physical_case((sig,ori,64,32))
            for sig,ori in ((0,0),(.002,1),(.002,-1))]


def temporal_refinement():
    cases=[]
    for sig,ori in ((0,0),(.002,1),(.002,-1)):
        data=[physical_case((sig,ori,n,32)) for n in (8,16,32,64,128)]
        for name in ("U_rec_eV_perH","Pi_rec_eV_perH","escape_U_eV_perH"):
            pass
        details={}
        for field in ("U_rec_eV_perH","Pi_rec_eV_perH","escape_U_eV_perH"):
            vals=[z["final"][field] for z in data]
            gap=[abs(vals[i+1]-vals[i]) for i in range(len(vals)-1)]
            orders=[math.log(gap[i]/gap[i+1],2) if gap[i+1]>0 and gap[i]>0 else None
                    for i in range(len(gap)-1)]
            details[field]={"source_samples":vals,"abs_step_gaps":gap,
                            "observed_orders":orders}
        cases.append({"Sigma_initial":sig,"orientation":ori,
                      "nsteps":[8,16,32,64,128],"result":details})
    return cases


def angular_refinement_and_independent_quad():
    p=a.c15.Parameters(.002,1,.2,.2,.1,.5)
    values=[physical_case((.002,1,64,nmu)) for nmu in (8,16,24,32,64)]
    reference=values[-1]["final"]
    data=[]
    for r in values:
        row=r["final"]
        data.append({"gauss_n":r["nmu"],"final_Pi_eV_perH":row["Pi_rec_eV_perH"],
                     "final_U_eV_perH":row["U_rec_eV_perH"],
                     "abs_vs_64_Pi":abs(row["Pi_rec_eV_perH"]-reference["Pi_rec_eV_perH"]),
                     "abs_vs_64_U":abs(row["U_rec_eV_perH"]-reference["U_rec_eV_perH"])})
    calc=[a.isotropic_kernel(db,32) for db in (-.1,-.01,-1e-4,0,1e-4,.01,.1)]
    truth=[a.isotropic_independent_quad(db) for db in (-.1,-.01,-1e-4,0,1e-4,.01,.1)]
    err=max(abs(x-y) for v,w in zip(calc,truth) for x,y in zip(v,w))
    return {"angular":data,"independent_adaptive_quad_max_abs":err,
            "midpoint_gauss_64":"reference only, not global error certification"}


def birthtime_discretization_comparison():
    p=a.c15.Parameters(.002,1,.2,.2,.1,.5)
    data=[]
    for n in (16,32,64,128):
        midpoint=a.actual_C15_case(p,nsteps=n,emission_clock="midpoint",nmu=32)
        endpoint=a.actual_C15_case(p,nsteps=n,emission_clock="endpoint",nmu=32)
        data.append({"nsteps":n,
                    "midpoint_U_eVperH":midpoint["final"]["U_rec_eV_perH"],
                    "endpoint_U_eVperH":endpoint["final"]["U_rec_eV_perH"],
                    "midpoint_Pi_eVperH":midpoint["final"]["Pi_rec_eV_perH"],
                    "endpoint_Pi_eVperH":endpoint["final"]["Pi_rec_eV_perH"],
                    "Pi_midpoint_minus_endpoint":
                       midpoint["final"]["Pi_rec_eV_perH"]-endpoint["final"]["Pi_rec_eV_perH"]})
    return data


def scalar_benchmark():
    # Genuine ejection ages and actual b from C15. Replication tests
    # microkernel scalability, not new astrophysical source populations.
    obj=physical_case((.002,1,128,64))
    originals=[a.Birth(**item) for item in obj["source_escapes"]]
    seeds=originals*16
    obs_a=obj["final"]["a"];obs_b=obj["final"]["b"]
    mu,w=a.gauss(64)
    ref=a.radiation_from_births(seeds,obs_a,obs_b,64)
    def scalar():
        U=P=F=0.
        for item in seeds:
            dx=obs_b-item.b;z=item.energy_eV_perH*item.a/obs_a
            for m,ww in zip(mu,w):
                rr,pp,ff=a.scalar_ang_kernel(float(m),dx)
                U+=z*ww*rr;P+=z*ww*pp;F+=z*ww*ff
        return U,P,F
    s=scalar()
    assert abs(s[0]-ref["U_rec_eV_H"])<4e-13
    assert abs(s[1]-ref["Pi_rec_eV_H"])<4e-13
    assert abs(s[2]-ref["cPz_rec_eV_H"])<4e-13
    times={"vector":[],"scalar":[]}
    for _ in range(5):
        t=time.perf_counter()
        z=a.radiation_from_births(seeds,obs_a,obs_b,64)
        times["vector"].append(time.perf_counter()-t)
        t=time.perf_counter()
        old=scalar()
        times["scalar"].append(time.perf_counter()-t)
    return {"actual_b_and_Ubirth_samples":len(originals),
            "replication_for_scaling_only":16,
            "benchmark_source_events":len(seeds),
            "Gauss_angles":64,
            "positive_radiative_event_angle_products":len(seeds)*64,
            "median_vector_s":statistics.median(times["vector"]),
            "median_scalar_s":statistics.median(times["scalar"]),
            "wall_time_samples_s":times,
            "speedup_bolometric_angular_microkernel":
               statistics.median(times["scalar"])/statistics.median(times["vector"]),
            "independent_scalar_max_abs_disagreement":max(
               abs(s[0]-ref["U_rec_eV_H"]),abs(s[1]-ref["Pi_rec_eV_H"]),
               abs(s[2]-ref["cPz_rec_eV_H"])),
            "spectrum_free_moment_age_storage_bytes_per_event":24,
            "hypothetical_full_angular_energy_packet_bytes_per_event":64*24,
            "no_whole_native_AX08_speedup_claim":True}


def parallel_compare():
    jobs=[(sig,ori,64,32) for sig,ori in ((0,0),(.002,1),(.002,-1))]
    start=time.perf_counter()
    single=[concise(physical_case(j)) for j in jobs]
    single_wall=time.perf_counter()-start
    start=time.perf_counter()
    with ProcessPoolExecutor(max_workers=3) as pool:
        multi=[concise(r) for r in pool.map(physical_case,jobs)]
    multi_wall=time.perf_counter()-start
    if multi!=single:
        raise ValueError("C17_PARALLEL_SCIENCE_DIFFERENT")
    return {"jobs":jobs,"workers":3,"serial_wall_s":single_wall,
            "parallel_wall_s":multi_wall,"speedup":single_wall/multi_wall,
            "all_scientific_floats_identical":True,
            "host_worker_overhead_warning":True}


def save_plots(signed):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    path=HERE/"ESCAPING_CASEA_STRESS_HISTORY.csv"
    keys=("a","b","H","Sigma","escape_U_eV_perH",
          "U_rec_eV_perH","Pi_rec_eV_perH","cPz_rec_eV_perH",
          "Pi_rec_lower","Pi_rec_upper","U_rec_Killing_work_eV_perH")
    with path.open("w",newline="") as f:
        wr=csv.writer(f,lineterminator="\n")
        wr.writerow(("Sigma_initial","orientation_initial")+keys)
        for row in signed:
            sig=row["parameters"]["Sigma_initial"]
            ori=row["parameters"]["orientation"]
            for r in row["history"]:
                wr.writerow((sig,ori)+tuple(r.get(k,float("nan")) for k in keys))
    fig,axes=plt.subplots(2,1,figsize=(8.8,7.2),sharex=True)
    for row in signed:
        ori=row["parameters"]["orientation"]
        h=row["history"]
        x=np.array([z["a"] for z in h])
        label=f"initial Sigma={row['parameters']['Sigma_initial']}, orientation={ori:+d}"
        axes[0].plot(x,[z["Pi_rec_eV_perH"] for z in h],label=label)
        axes[1].plot(x,[z["escape_U_eV_perH"] for z in h],ls=":",label="emitted escrow, "+label)
        axes[1].plot(x,[z["U_rec_eV_perH"] for z in h],label="propagated, "+label)
    axes[0].set_ylabel("Case A conditional physical Pi [eV/H]")
    axes[1].set_ylabel("Positive recombination radiation U [eV/H]")
    axes[-1].set_xlabel("Mean scale factor, narrow near-z4 window")
    axes[0].set_title("C17 transparent isotropic Case-A source; not a physical full EoR prediction")
    for ax in axes:ax.grid(alpha=.25);ax.legend(fontsize=7,ncol=2)
    fig.tight_layout()
    fig.savefig(HERE/"ESCAPING_CASEA_STRESS_HISTORY.png",dpi=150)
    plt.close(fig)
    return {"machine_readable_csv":path.name,
            "plot":"ESCAPING_CASEA_STRESS_HISTORY.png",
            "rows":sum(len(x["history"]) for x in signed)}


def main():
    start=time.perf_counter()
    signed=signed_models()
    source_gate={"schema":"rei.c17.actual_C15_Escaped_CaseA_sharp_positive_angular.v1",
                 "model":"original C15 Sigma-stress-coupled Einstein + original CaseA scalar owner, transparent radiation added conditional",
                 "actual_source_git_parent":"f85394d50078fc384ce6aff55e669da866dfca35",
                 "scientific_admission":"exact angular positive bound; opt-in isotropic collisionless Bolometric model, Einstein linearized fixed background; NOT full Qmu or full z20-4",
                 "signed_cases":[concise(x) for x in signed],
                 "sampled_history":signed,
                 "actual_time_refinement":temporal_refinement(),
                 "original_gauss_angular_refinement":angular_refinement_and_independent_quad(),
                 "source_birthtime_location_error":birthtime_discretization_comparison(),
                 "spectrum_free_angular_microkernel":scalar_benchmark(),
                 "parallel_three_sources":parallel_compare(),
                 "plots":save_plots(signed)}
    source_gate["whole_study_s"]=time.perf_counter()-start
    (HERE/"C17_STUDY_RESULTS.json").write_text(
         json.dumps(source_gate,indent=2)+"\n")
    for x in signed:
        print("C17_SIGN",x["parameters"]["Sigma_initial"],
              x["parameters"]["orientation"],
              "Erec",x["final"]["U_rec_eV_perH"],
              "Pi_iso",x["final"]["Pi_rec_eV_perH"],
              "deltaSig_iso",x["linearized_abs_delta_Sigma_from_conditional_isotropic_CaseA"],
              "deltaSig_sharp",x["sharp_linearized_abs_delta_Sigma_envelope_any_positive_angles"],flush=True)
    print("MICRO_SPEED",source_gate["spectrum_free_angular_microkernel"]["speedup_bolometric_angular_microkernel"],
          "PARALLEL",source_gate["parallel_three_sources"]["speedup"],flush=True)
    print("TOTAL_WALL",source_gate["whole_study_s"],flush=True)

if __name__=="__main__":
    main()
