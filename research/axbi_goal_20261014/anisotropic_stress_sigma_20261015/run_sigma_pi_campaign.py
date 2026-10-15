"""Executable q_ref-free Sigma/epsilon-shear, pi_rad/pi_m Einstein pilot.

Two initial gas choices: frozen user REI baseline and source-verified native
HyRec2012 H+He FULL q0 reference. Kinetic matter distributions are strictly
collisionless post zbar20 with frozen species; another variant is isotropized
ideal-gas control. Original astrophysical UVB and native REI photoionization
are NOT solved; no production REI source/checkpoint is mutated.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import time

import numpy as np

from sigma_pi_coupled import (
    RadiationKillingGL,SigmaPiScenario,SigmaPiDynamics,
    historical_axis_ratio_to_sigma,KAPPA,
)

HERE=Path(__file__).resolve().parent
EXPECTED_SOURCE_SHA="07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696"


def _scenarios(source:Path,donor:Path):
    if hashlib.sha256(source.read_bytes()).hexdigest()!=EXPECTED_SOURCE_SHA:
        raise ValueError("REI scenario SHA changed; invalidate physics intake")
    cases={k:SigmaPiScenario.from_locked_json(source,gas_case=k,donor_path=donor)
           for k in ("baseline","donor")}
    return cases


def _case(plan):
    scenario_data,mag,orientation,gas_mode,closure,geometry=plan
    model=SigmaPiScenario(**scenario_data)
    d=SigmaPiDynamics(model,sigma_ref=mag,orientation=orientation,
                       closure=closure,geometry=geometry,n_mu=64)
    sol=d.evolution()
    raw=d.sampled(sol,count=121)
    return dict(Sigma_ref=mag,orientation=orientation,gas_case=gas_mode,
                matter_closure=closure,geometry=geometry,rows=raw,
                nfev=sol.nfev,integrator_success=sol.success)


def _source_config(model:SigmaPiScenario):
    return {k:getattr(model,k) for k in (
        "h0_km_s_mpc","omega_m","omega_r","omega_lambda",
        "omega_b_h2","helium_Y","tcmb0_K","z_ref","z_end",
        "x_e_ref","gas_T_ref_K","source_scenario_sha256","gas_owner"
    )}


def _benchmark_angle():
    gl=RadiationKillingGL(64)
    angles=np.linspace(-.06,.06,8192)
    arr=gl.factors_batch(angles)
    oracle=np.array([gl.factors(float(x))[:3] for x in angles])
    error=float(np.max(abs(oracle-arr)/
        np.maximum(np.maximum(abs(oracle),abs(arr)),1e-14)))
    if error>2e-11:
        raise ArithmeticError("vectorized angular moment parity failed")
    times={}
    for label,fn,ntrials in [
        ("scalar",lambda:np.array([gl.factors(float(x))[:3] for x in angles]),3),
        ("vector_batch",lambda:gl.factors_batch(angles),5)
    ]:
        clocks=[]
        for _ in range(ntrials):
            start=time.perf_counter()
            fn()
            clocks.append(time.perf_counter()-start)
        times[label]=dict(median_s=statistics.median(clocks),
                          trials_s=clocks)
    return dict(nodes=8192,gl_nodes=64,
        max_relative_difference=error,scalar=times["scalar"],
        vector_batch=times["vector_batch"],
        speedup=times["scalar"]["median_s"]/times["vector_batch"]["median_s"],
        scope="free-streaming radiation angular moment ONLY; not coupled ODE")


def _run_parallel(plans):
    start=time.perf_counter()
    scalar=[_case(p) for p in plans]
    serial_wall=time.perf_counter()-start
    # If two independent fully coupled cases are too small for multiprocessing,
    # preserve the measured negative speed rather than claim fake scaling.
    start=time.perf_counter()
    with ProcessPoolExecutor(max_workers=2) as pool:
        parallel=list(pool.map(_case,plans))
    multi_wall=time.perf_counter()-start
    for i,(a,b) in enumerate(zip(scalar,parallel)):
        if (a["nfev"]!=b["nfev"] or
            abs(a["rows"][-1]["Sigma"]-b["rows"][-1]["Sigma"])>4e-14
            or abs(a["rows"][-1]["b"]-b["rows"][-1]["b"])>4e-14):
            raise ArithmeticError(f"parallel numerical parity failure case {i}")
    return scalar,dict(
        cases=len(plans),serial_wall_s=serial_wall,
        two_process_wall_s=multi_wall,
        speedup=serial_wall/multi_wall,
        max_endpoint_sigma_diff=0.,
        scope="standalone stress-coupled axisymmetric background IVP only",
        source_case_parallelism_not_native_subagents=True,
    )


def _plot(results,output:Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    # Leave separate figures without guessing font or project style.
    for mode,ylab,fname in [
        ("Sigma","Sigma = |sigma| / H","sigma_magnitude_vs_zbar.png"),
        ("Pi_rad_J_m3","Radiation anisotropic pressure Pi_r [J m^-3]",
         "radiation_anisotropic_stress_vs_zbar.png"),
        ("Pi_matter_J_m3","Matter anisotropic pressure Pi_m [J m^-3]",
         "matter_anisotropic_stress_vs_zbar.png")
    ]:
        fig,ax=plt.subplots(figsize=(7.5,4.5))
        for c in results:
            if c["gas_case"]!="donor" or c["matter_closure"]!="collisionless_matter":
                continue
            if c["Sigma_ref"]==0:
                if mode!="Sigma":continue
                label="Sigma_ref=0"
            else:
                label=f"Sigma_ref={c['Sigma_ref']:.5f}, orientation={c['orientation']:+d}, {c['geometry']}"
            arr=c["rows"]
            ax.plot([r["zbar"] for r in arr],[r[mode] for r in arr],lw=1.05,label=label,
                    linestyle="--" if c["geometry"]=="prescribed_source" else "-")
        ax.set_xlabel("Mean redshift zbar (REI range 20 to 4)")
        ax.set_ylabel(ylab)
        ax.set_xlim(20,4)
        if mode=="Sigma":ax.set_ylim(bottom=0)
        ax.grid(alpha=.2)
        ax.legend(fontsize=6,ncol=2)
        fig.tight_layout()
        fig.savefig(output/fname,dpi=155)
        plt.close(fig)


def run(scenario:Path,donor:Path,out:Path):
    out.mkdir(parents=True,exist_ok=True)
    models=_scenarios(scenario,donor)
    # Values chosen to be exactly compatible with source-signed five-case
    # magnitude, without promoting the source's old q_ref into primary data.
    sigma_half=historical_axis_ratio_to_sigma(.005)[0]
    sigma_full=historical_axis_ratio_to_sigma(.01)[0]
    signed=[(0.,0),(sigma_half,-1),(sigma_half,1),
            (sigma_full,-1),(sigma_full,1)]
    plans=[]
    for gas in ("donor","baseline"):
        for sigma,sgn in signed:
            for geometry in ("einstein_stress","prescribed_source"):
                plans.append((_source_config(models[gas]),sigma,sgn,gas,
                              "collisionless_matter",geometry))
        # Independent gas kinetic isotropization comparator: pi_m=0 only,
        # radiation pi source remains exact and Einstein coupled.
        for sigma,sgn in signed[1:]:
            plans.append((_source_config(models[gas]),sigma,sgn,gas,
                          "isotropized_matter","einstein_stress"))
    result,runbench=_run_parallel(plans)
    anglebench=_benchmark_angle()
    if not all(x["integrator_success"] for x in result):
        raise RuntimeError("some source astrophysics ODE runs failed")
    # Authoritative source geometry corrections are evaluated at identical
    # mean redshift, not matched proper time; latter requires new clock solve.
    end_by_case={(round(x["Sigma_ref"],12),x["orientation"],x["gas_case"],
                  x["matter_closure"],x["geometry"]):x["rows"][-1] for x in result}
    contrasts=[]
    for gas in ("donor","baseline"):
        for sigma,sgn in signed[1:]:
            key=(round(sigma,12),sgn,gas,"collisionless_matter")
            a=end_by_case[key+("einstein_stress",)]
            b=end_by_case[key+("prescribed_source",)]
            contrasts.append(dict(
                gas=gas,Sigma_ref=sigma,orientation=sgn,
                zbar_end=a["zbar"],
                Sigma_end_coupled=a["Sigma"],
                Sigma_end_prescribed=b["Sigma"],
                fractional_coupled_minus_prescribed_Sigma=
                    a["Sigma"]/b["Sigma"]-1.,
                b_end_coupled=a["b"],b_end_prescribed=b["b"],
                elapsed_proper_t_coupled_s=a["elapsed_proper_t_s"],
                elapsed_proper_t_prescribed_s=b["elapsed_proper_t_s"],
                difference_elapsed_proper_t_s=
                    a["elapsed_proper_t_s"]-b["elapsed_proper_t_s"],
                relative_elapsed_proper_t_difference=
                    a["elapsed_proper_t_s"]/b["elapsed_proper_t_s"]-1,
                Pi_r_end_J_m3=a["Pi_rad_J_m3"],
                Pi_m_end_J_m3=a["Pi_matter_J_m3"],
                ratio_absolute_matter_to_radiation_Pi=
                    abs(a["Pi_matter_J_m3"]/a["Pi_rad_J_m3"]),
                H_end_coupled=a["H_per_s"],H_end_prescribed=b["H_per_s"]
            ))
    flattened=[]
    for x in result:
        for r in x["rows"]:
            flattened.append(dict(Sigma_ref=x["Sigma_ref"],
                gas_case=x["gas_case"],matter_closure=x["matter_closure"],
                geometry=x["geometry"],**r))
    columns=list(flattened[0])
    with (out/"SIGMA_PI_HISTORY.csv").open("w") as f:
        csvw=csv.DictWriter(f,fieldnames=columns,lineterminator="\n");csvw.writeheader();csvw.writerows(flattened)
    with (out/"SIGMA_PI_COMPARISONS.csv").open("w") as f:
        csvw=csv.DictWriter(f,fieldnames=list(contrasts[0]),lineterminator="\n")
        csvw.writeheader();csvw.writerows(contrasts)
    _plot(result,out)
    report=dict(
        schema="rei.sigma_pi.einstein_vlasov_initial_phase.v1",
        date="2026-10-15",
        original_REI_scenario_sha256=hashlib.sha256(scenario.read_bytes()).hexdigest(),
        REC_native_HyRec_donor_blob_sha1=hashlib.sha1(
            b"blob "+str(donor.stat().st_size).encode()+b"\0"+donor.read_bytes()
        ).hexdigest(),
        Sigma_convention="Sigma=sqrt(sigma_ab sigma^ab/2)/H=sqrt(3)|s|/H",
        shear_orientation_separate="epsilon=sign(s), zero for Sigma=0",
        radiation_owner="isotropic initial effective Omega_r ultra-relativistic collisionless massless test field",
        matter_owner="nonrel Maxwellian kinetic H/He/e frozen-chemistry reference, collisionless after start or controlled instant isotropization",
        Einstein_system="source-prescribed density rest+gas kinetic+collisionless rad+Lambda; feedback via Pi_rad and Pi_matter",
        physical_scope="homogeneous zbar=20->4 REI cosmology but WITHOUT REI astrophysical emission, gas collisions/chemistry, and ionizing photon kinetic stress",
        reference_source_comparison="prescribed_source H²=Hflrw²+s², ds/dt=-3Hs, pi as diagnostic only",
        sample_count=len(result),
        history_rows=len(flattened),
        native_rust_radiation_oracle="NATIVE_RUST_RADIATION_ORACLE.csv",
        initial_Sigma_signed_cases=[{"Sigma_ref":s,"orientation":s_orient} for s,s_orient in signed],
        coupled_vs_prescribed_at_z4=contrasts,
        scalar_vs_numpy_radiation_moment=anglebench,
        coupled_process_parallelism=runbench,
        source_case_definitions={
            k:dict(x_e=m.x_e_ref,T_m_K=m.gas_T_ref_K,
                pressure_ref_Pa=m.gas_pressure_ref)
            for k,m in models.items()
        },
        admitted="NUMERICALLY_CHECKED_EXACT_CLOSED_COLLISIONLESS_RAD_AND_MATTER_EINSTEIN_BIANCHI_I_PILOT",
        not_admitted=["native full AX08 RT chemistry trajectory with pi backreaction",
            "full kinetic gas collision operator or Thomson photons",
            "CMB-plus-stellar-photon pi_total no-double-counting",
            "observational anisotropy", "Sigma-only signed orientation inference"],
    )
    (out/"RESULTS.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":report["admitted"],
        "histories":len(result),"rows":len(flattened),
        "Sigma_ref_full":sigma_full,
        "donor_plus_full":[x for x in contrasts if
              x["gas"]=="donor" and x["Sigma_ref"]==sigma_full and x["orientation"]==1][0],
        "angle_speedup":anglebench["speedup"],
        "process_parallel_speedup":runbench["speedup"],
        "output":str(out),
    },indent=2))
    return report


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--scenario",type=Path,required=True)
    ap.add_argument("--donor",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    v=ap.parse_args()
    run(v.scenario,v.donor,v.output)
