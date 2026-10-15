#!/usr/bin/env python3
"""C16 proof-by-construction, actual C11 event and C15 physical source audit."""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
import csv,hashlib,json,math,statistics,sys,time
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import qmu as q

SIGN_CASES=((0.,0),(.002,1),(.002,-1))


def one_case(sig,ori,n=64):
    return q.C15_escrow_and_escape_bound(
        q.c15.Parameters(sig,ori,.2,.2,.1,.5),nsteps=n)


def scalar_event_receipt(pop,E,mu,sigma,neutral,dt):
    """Independent scalar finite photon competition with physical momentum."""
    rates=q.c13.C_CGS*dt
    acc=np.zeros((3,3),dtype=float)
    for i in range(len(E)):
        lamb=rates*neutral*sigma[i]
        tau=sum(lamb)
        factor=-math.expm1(-tau)/tau if tau>0 else 1.
        inc=pop[i]*factor*lamb
        acc[0]+=inc
        acc[1]+=inc*E[i]
        acc[2]+=inc*E[i]*mu[i]
    return acc


def microkernel_benchmark():
    cos=q.c13.Scenario(q.c13.ROOT)
    src=q.c13.NativeStellarSource.load(cos,
         ROOT/"research/rei_c13_live_source_20261015/NATIVE_SOURCE_8X8.csv")
    gas=q.c13.initial_gas(cos,.1999)
    sky=src.birth(.02)
    repeats=32
    E=np.tile(sky.E,repeats)
    mu=np.tile(sky.mu,repeats)
    weights=np.tile(sky.NperH,repeats)/repeats
    from short_interval import PhotonCloud
    big=PhotonCloud(E,mu,weights)
    dt=1e10
    initial=big.to_native_chemistry(gas.nH)
    after_gas,after,receipt=q.c13.c10.midpoint_step(gas,initial,dt)
    neutral=(gas.neutral+after_gas.neutral)/2
    truth=q.photon_species_event(gas,after_gas,initial,after,mu,dt,receipt)
    independent=scalar_event_receipt(initial.count,E,mu,initial.sigma,neutral,dt)
    expected=np.array((truth["species_counts_cm3"],
                      truth["species_energy_eV_cm3"],
                      truth["species_cPz_eV_cm3"]))
    np.testing.assert_allclose(expected,independent,rtol=4e-11,atol=5e-21)
    samples_fast=[];samples_slow=[]
    for _ in range(5):
        t=time.perf_counter()
        got=q.photon_species_event(gas,after_gas,initial,after,mu,dt,receipt)
        samples_fast.append(time.perf_counter()-t)
        t=time.perf_counter()
        old=scalar_event_receipt(initial.count,E,mu,initial.sigma,neutral,dt)
        samples_slow.append(time.perf_counter()-t)
    return {"model":"native unmodified C10 original HI/HeI/HeII",
            "num_source_positive_packets":len(E),"source_replication":repeats,
            "same_species_counts_energy_and_cPz_parity":True,
            "max_abs_scalar_vs_vector":float(np.max(abs(expected-independent))),
            "seven_plus_repetition":5,"median_scalar_s":statistics.median(samples_slow),
            "median_vector_s":statistics.median(samples_fast),
            "microkernel_speedup":statistics.median(samples_slow)/statistics.median(samples_fast),
            "source_packet_storage_bytes":big.live_bytes,
            "not_native_whole_solver_speedup":True}


def restore_moments_and_counterexample(escape_eV_H):
    U=escape_eV_H
    cases={}
    for name,pi in (("axial_poles",U),("transverse_ring",-U/2),
                    ("isotropic_pressure_moment",0.)):
        mom=q.Moment(U,0.,pi)
        sky=q.positive_three_atom(mom,energy_eV=30.)
        m=q.Moment.from_sky(sky)
        cases[name]={"number_per_H":sky.number,"energy_eV_per_H":m.U,
                     "cPz_eV_per_H":m.cPz,"Pi_eV_per_H":m.Pi,
                     "positive_packet_count":sky.packet_count,
                     "mu_values":sky.mu.tolist(),
                     "photon_number_and_energy_manufactured":True}
    return {"source":"actual C15 owner Case-A escape total energy, but no original physical escape N/E/angular spectrum",
            "same_energy_and_manufactured_monochromatic_number":True,
            "same_longitudinal_momentum":0.,
            "different_Pi_physical_pressure_difference":True,
            "sharp_realizability_hull":"-U/2<=Pi<=U, 3F^2<=U(U+2Pi)",
            "monochromatic_30ev_used_only_as_mathematical_witness_NOT_REAL_CASEA_SOURCE":True,
            "cases":cases}


def physical_original_C11_cases():
    cos=q.c13.Scenario(q.c13.ROOT)
    src=q.c13.NativeStellarSource.load(cos,
         ROOT/"research/rei_c13_live_source_20261015/NATIVE_SOURCE_8X8.csv")
    gas=q.c13.initial_gas(cos,.1999)
    symmetric=src.birth(.02)
    directed=q.c13.PhotonCloud(symmetric.E,symmetric.mu,
                              symmetric.NperH*(1+.8*symmetric.mu))
    return {"symmetric_original_MD14":q.native_C11_Qmu(gas,symmetric,1e10),
            "asymmetric_positive_sensitivity_only":q.native_C11_Qmu(gas,directed,1e10)}


def parallel_audit():
    jobs=[(sig,ori,32) for sig,ori in SIGN_CASES]
    t=time.perf_counter()
    serial=[one_case(*job) for job in jobs]
    serial_sec=time.perf_counter()-t
    t=time.perf_counter()
    with ProcessPoolExecutor(max_workers=3) as pool:
        parallel=list(pool.map(_worker,jobs))
    parallel_sec=time.perf_counter()-t
    if serial!=parallel:raise AssertionError("SOURCE_C16_SERIAL_PARALLEL_DATA_CHANGED")
    return {"cases":serial,
            "parallel":{"workers":3,"source_cases":SIGN_CASES,
                        "serial_time_s":serial_sec,
                        "parallel_time_s":parallel_sec,
                        "speedup":serial_sec/parallel_sec,
                        "all_scientific_fields_bitwise_identical":True}}


def _worker(job):
    return one_case(*job)


def refinement():
    p=q.c15.Parameters(0.,0,.2,.2,.1,.5)
    grid=(8,16,32,64,128)
    runs=[q.C15_escrow_and_escape_bound(p,nsteps=n) for n in grid]
    return {"grid":grid,"columns":{name:[r[name] for r in runs] for name in (
        "CaseA_escape_cumulative_energy_eV_perH",
        "total_original_MD14_stellar_emission_energy_eV_perH",
        "conditional_missing_emitter_H2_fraction_upper",
        "linearized_omitted_escape_stress_absolute_delta_Sigma_bound")},
        "validity":"finite sampled C15 physical histories and fixed-background linearized upper budget, not nonlinear global error bound"}


def write_csv(cases):
    target=HERE/"QMU_STELLAR_CASEA_SHORT_HISTORY.csv"
    cols=("a","t_s","Sigma","orientation",
          "emitted_MD14_energy_this_step_eV_perH",
          "formal_emitter_energy_loss_eV_perH",
          "emitted_CaseA_escape_energy_this_step_eV_perH",
          "total_CaseA_escape_energy_eV_perH",
          "UV_U_eV_perH","UV_cPz_eV_perH","UV_Pi_eV_perH")
    with target.open("w",newline="") as f:
        out=csv.writer(f,lineterminator="\n")
        out.writerow(("Sigma_initial","orientation_initial")+cols)
        for c in cases:
            p=c["parameters"]
            for row in c["history"]:
                out.writerow((p["Sigma_initial"],p["orientation"])+
                             tuple(row[name] for name in cols))
    return {"filename":target.name,"rows":sum(len(c["history"]) for c in cases)}


def main():
    start=time.perf_counter()
    out=parallel_audit()
    results={
        "schema":"rei.c16.positive_qmu_photo_real_emitter_escrow_casea_information_gap.v1",
        "scope":"actual C11 Case A multi-species photon absorption momentum receipt + actual C15 near-z4 physical Q0+formal source escrow, not complete Qmu in Einstein GR",
        "source_history_parallel":out["cases"],
        "parallel":out["parallel"],
        "original_C11_event":physical_original_C11_cases(),
        "source_scalar_escape_counterexample":
            restore_moments_and_counterexample(
                out["cases"][0]["CaseA_escape_cumulative_energy_eV_perH"]),
        "source_age_step_refinement":refinement(),
        "vectorized_species_momentum_microkernel":microkernel_benchmark(),
        "CSV":write_csv(out["cases"])}
    results["elapsed_total_s"]=time.perf_counter()-start
    (HERE/"C16_STUDY_RESULTS.json").write_text(json.dumps(
        results,indent=2,default=lambda x:float(x) if isinstance(x,np.generic)
        else x.tolist() if isinstance(x,np.ndarray) else str(x))+"\n")
    for a in results["source_history_parallel"]:
        print("C15_REAL",a["parameters"]["Sigma_initial"],a["parameters"]["orientation"],
              "Eesc",a["CaseA_escape_cumulative_energy_eV_perH"],
              "Emit",a["total_original_MD14_stellar_emission_energy_eV_perH"],
              "dSigma_esc_bound",a["linearized_omitted_escape_stress_absolute_delta_Sigma_bound"],
              "missing_H2",a["conditional_missing_emitter_H2_fraction_upper"],flush=True)
    print("ASYM_RECOIL",results["original_C11_event"]["asymmetric_positive_sensitivity_only"]["required_baryon_recoil_cPz_eV_perH"],flush=True)
    print("PERF",results["vectorized_species_momentum_microkernel"]["microkernel_speedup"],
          results["parallel"]["speedup"],flush=True)
    print("STUDY_ELAPSED",results["elapsed_total_s"],flush=True)

if __name__=="__main__":main()
