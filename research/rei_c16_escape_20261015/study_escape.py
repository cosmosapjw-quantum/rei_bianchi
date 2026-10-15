#!/usr/bin/env python3
"""Executed C16 Case-A photon positive angular pressure shear response study.

Uses exact source C15 chemistry midpoint escaped photons, original PR144
positive moment emitter reconstruction, native C13 Killing transport,
and response sharp envelope. Whole astrophysical Einstein system NOT closed.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import statistics
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from numpy.polynomial.legendre import leggauss
from escape_transport import (
 run_escape_response,response_mode,angular_moments_fast,
 radiation_cloud,Moment,sharp_per_event,evolved_moments,endpoint_source_pressure,
 KAPPA,EV_CM3_TO_PA,START,STOP
)

HERE=Path(__file__).resolve().parent
OUT=HERE/"results"

def response_reference_cloud_drift(births,g,kind,order=16):
    """Physically separate original native C13 sky.drift evaluated node by node."""
    nodes,weights=leggauss(order)
    end=g.x[-1]
    ans=0.
    for born in births:
        lower=math.log(born.a)
        if lower>=end:continue
        cloud=radiation_cloud(born.energy_eV_perH,kind)
        local=0.
        for n,w in zip(nodes,weights):
            pos=lower+(n+1)/2*(end-lower)
            a,b,H=g.geometry([pos])
            sky=cloud.drift(float(pos-lower),float(b[0]-born.b))
            pi=Moment.from_sky(sky).Pi
            pressure=pi*g.hydrogen_density_cm3(float(a[0]))*EV_CM3_TO_PA
            local+=float(w)*math.exp(-3*(end-pos))*KAPPA*pressure/float(H[0])
        ans+=(end-lower)/2*local
    return ans

def conditionally_sharp_source(g,births,kind):
    """Proof witness at each sampled actual gamma/nu/HHe external radiation epoch."""
    data=[]
    for x in g.x:
        a,b,H=g.geometry([x])
        vals=[angular_moments_fast(z,a,b,kind) for z in births if math.log(z.a)<=x+1e-14]
        U=float(sum(float(v[0][0]) for v in vals))
        P=float(sum(float(v[1][0]) for v in vals))
        data.append({"a":float(a[0]),"zbar":float(1/a[0]-1),"x":float(x),
            "escaped_U_eV_perH":U,"escaped_P2_eV_perH":P,
            "escaped_Pi_J_m3":float(g.hydrogen_density_cm3(float(a[0]))*EV_CM3_TO_PA*P/3)})
    return data

def study():
    begin=time.perf_counter()
    realcases={
      "FLRW_initial_with_primordial_quadrupole":(0.,.2,32),
      "SIGMA_REF_0_NO_PRIMORDIAL_QUAD":(0.,0.,32),
      "positive_Sigma_ref_0p00866014":(.005,.2,32),
      "negative_Sigma_ref_0p00866014":(-.005,.2,32),
      "positive_Sigma_ref_0p01731964":(.01,.2,32),
    }
    source={}
    plots={}
    for key,(q,kappa,n) in realcases.items():
        clock=time.perf_counter()
        x,g,births=run_escape_response(q,n,kappa,16)
        mag=x["fixed_background_shear_magnitude_Sigma_first_order_bounds"]
        if mag is not None:
            assert mag[0]<=mag[1]
        else:
            assert x["fixed_background_Sigma_cusp_crosses_zero"]
        assert x["fixed_background_unsigned_Sigma_total_sharp_interval"][0]>=0
        if x["base_axis_orientation_end"]==0 and key!="SIGMA_REF_0_NO_PRIMORDIAL_QUAD":
            raise RuntimeError("NONTRIVIAL_SOURCE_GRAVITATIONAL_SHEAR_SIGN_MISSING")
        source[key]={p:v for p,v in x.items() if p!="events"}
        source[key]["full_native_birth_events_sha256"]=hashlib.sha256(
             json.dumps(x["events"],sort_keys=True).encode()).hexdigest()
        source[key]["compute_wall_s"]=time.perf_counter()-clock
        plots[key]={"geometry":g,"births":births,"initial_C16":x}
        print("ACTUAL_CASEA_ESCAPED_BOUND",key,json.dumps({
            "Sigma_base":x["Sigma_base_end"],
            "dSigma_fixed_signed":x["fixed_background_signed_Normalized_Sigma_response_bounds"],
            "dSigma_fixed_magnitude_sorted_or_null_at_cusp":mag,
            "actual_total_Sigma_fixed_H_range":
                x["fixed_background_unsigned_Sigma_total_sharp_interval"],
            "emitted_U":x["original_actual_CaseA_emitted_U_eV_perH"],
            "realizable_sharp":x["conditional_angular_realizations_reproduce_extrema"],
            "wall":source[key]["compute_wall_s"]}),flush=True)
    # True C15 source birth-step refinement and Green integrator refinement
    refined={}
    for n in (16,32,64,128):
        x,g,b=run_escape_response(.005,n,.2,16)
        refined[n]={"source_escaped_eV_perH":x["original_actual_CaseA_emitted_U_eV_perH"],
                    "positive_Sigma_base":x["Sigma_base_end"],
                    "sharp_negative_deltaS":x["source_sharp_lower_shear_signed_per_s"],
                    "sharp_positive_deltaS":x["source_sharp_upper_shear_signed_per_s"],
                    "sharp_deltaSigma_bounds":x["fixed_background_signed_Normalized_Sigma_response_bounds"],
                    "isotropic_deltaS":x["response_shear_signed_per_s"]["isotropic"]}
        print("CASEA_C16_REFINEMENT",n,refined[n],flush=True)
    # Independent shadow integral rule, numeric pressure-cone realization and
    # native C13 original sky.drift compare for one source-locked reference
    z=plots["positive_Sigma_ref_0p00866014"]
    births=z["births"];g=z["geometry"]
    methods=("transverse","PR144_zeroPi","isotropic","axial")
    rules={}
    for rule in (8,16,32):
        rules[rule]={m:response_mode(births,g,m,order=rule) for m in methods}
    differences={}
    # The physical response amplitude, not tiny cancellation-dominated
    # near-zero middle response, is the well-conditioned validation scale.
    # Original C13 and batched fast sums match to ~1e-17 of the sharp cone
    # amplitude even if weak isotropic delta_s has ~1e-10 relative rounding.
    meaningful_scale=max(abs(response_mode(births,g,"envelope_low",16)),
                         abs(response_mode(births,g,"envelope_high",16)))
    assert meaningful_scale>0
    timings={"batched_native_Killing":[],"original_C13_PhotonCloud_drift":[]}
    for m in methods:
        fast=rules[16][m]
        slow=response_reference_cloud_drift(births,g,m,order=16)
        match=abs(fast-slow)/meaningful_scale
        differences[m]={"fast":fast,"slow":slow,
            "absolute_mismatch_per_s":abs(fast-slow),
            "error_over_true_positive_source_cone_amplitude":match,
            "weak_response_relative_mismatch_diagnostic_only":
               abs(fast-slow)/max(abs(fast),abs(slow),1e-45)}
        if match>5e-13:
            raise RuntimeError("C16_INDEPENDENT_KILLING_POSITIVE_MOMENT_RESPONSE_MISMATCH:"+m)
    # Match 5 independent repeated scalar-kernel timings; no whole C15 speedup.
    for _ in range(5):
        for name,fun in (
          ("batched_native_Killing",lambda:response_mode(births,g,"isotropic",order=16)),
          ("original_C13_PhotonCloud_drift",lambda:response_reference_cloud_drift(births,g,"isotropic",order=16))):
            started=time.perf_counter()
            fun()
            timings[name].append(time.perf_counter()-started)
    med={k:statistics.median(v) for k,v in timings.items()}
    compare={"rule_tolerance":{
       "max_abs_8_vs_16":max(abs(rules[8][m]-rules[16][m]) for m in methods),
       "max_abs_16_vs_32":max(abs(rules[16][m]-rules[32][m]) for m in methods)},
       "independent_source_photon_drift_crosscheck":differences,
       "timing_median_seconds":med,
       "vectorized_angular_scoped_kernel_speedup":
          med["original_C13_PhotonCloud_drift"]/med["batched_native_Killing"],
       "timing_repetitions":5}
    # Sharp-bound trajectory for user: actual positive Sigma_ref, plot normalized.
    xs=g.x
    history=[]
    # Memoize the source-driven angular profiles only once per model/mode.
    # The previous reference pattern recomputed all epochs for each plotted
    # epoch, O(n_macro^3); cached profiles lower it to O(n_macro^2).
    angular_profiles={mode:conditionally_sharp_source(g,births,mode) for mode in methods}
    for i,x in enumerate(xs):
        current=[angular_profiles[mode][i] for mode in methods]
        # fixed-background signed shear response Green up to each accepted a
        dsmin=response_mode(births,g,"envelope_low",order=16,at_x=x)
        dsmax=response_mode(births,g,"envelope_high",order=16,at_x=x)
        a,b,H=g.geometry([x])
        history.append({"a":float(a[0]),"zbar":float(1/a[0]-1),
           "source_base_Sigma":float(math.sqrt(3)*abs(float(g.s[i]))/float(H[0])),
           "escaped_U_isotropic_perH":current[2]["escaped_U_eV_perH"],
           "CaseA_escape_P2_lower_eV_perH":current[0]["escaped_P2_eV_perH"],
           "CaseA_escape_P2_upper_eV_perH":current[3]["escaped_P2_eV_perH"],
           "CaseA_escape_P2_isotropic_eV_perH":current[2]["escaped_P2_eV_perH"],
           "sharp_dSigma_signed_low":math.sqrt(3)*dsmin/float(H[0]),
           "sharp_dSigma_signed_high":math.sqrt(3)*dsmax/float(H[0])})
    fig,(ax,bx)=plt.subplots(2,1,figsize=(9.7,8.4),constrained_layout=True)
    z=[r["zbar"] for r in history]
    ax.plot(z,[r["CaseA_escape_P2_lower_eV_perH"] for r in history],label="sharp transverse lower")
    ax.plot(z,[r["CaseA_escape_P2_upper_eV_perH"] for r in history],label="sharp axial upper")
    ax.plot(z,[r["CaseA_escape_P2_isotropic_eV_perH"] for r in history],label="conditioned isotropic at emission")
    bx.plot(z,[r["sharp_dSigma_signed_low"] for r in history],label="signed shear response lower")
    bx.plot(z,[r["sharp_dSigma_signed_high"] for r in history],label="signed shear response upper")
    ax.set_ylabel("Escaped Case-A P2 per H [eV]")
    bx.set_ylabel("Fixed-background signed delta Sigma")
    for a in (ax,bx):
        a.invert_xaxis();a.grid(alpha=.3);a.legend(fontsize=8);a.set_xlabel("Mean redshift")
    fig.suptitle("Actual native Case-A emitted energy, PR144 positive angular extremizers, fixed C16 Bianchi Killing transport")
    fig.savefig(OUT/"real_CaseA_escape_sharp_shear_envelope.png",dpi=170)
    plt.close(fig)
    # Important independent higher hierarchy counterexample, not actual C16 kinematics.
    high=0.2
    m0=evolved_moments(1.,0.,.1999,high,.2,"PR144_zeroPi")
    m1=evolved_moments(1.,0.,.1999,high,.2,"isotropic")
    if abs(m1.Pi-m0.Pi)<.01:
        raise RuntimeError("C16_CASEA_UNLICENSED_HIGHER_MOMENTS_COUNTEREXAMPLE_MISSING")
    counterexample={
        "initial_U_eVperH":1.,"initial_energy_dipole":0.,
        "initial_energy_quadrupole":0.,
        "manufactured_delta_b":high,
        "original_PR144_three_node_zeroPi_future_Pi":m0.Pi,
        "source_isotropic_positive_GL64_zeroPi_future_Pi":m1.Pi,
        "future_pressure_difference_from_unfixed_l4_plus":m1.Pi-m0.Pi,
        "not_actual_C16_background":True}
    result={
      "schema":"rei.c16B.true_CaseA_escape_positive_angle_Killing_transport.sharp_response.v1",
      "status":"ACTUAL_CASEA_ESCAPE_SOURCE_SHARP_ANGULAR_ENVELOPE_RECONSTRUCTION_AND_SCOPED_EINSTEIN_RESPONSE_VERIFIED",
      "parent_PR143":"af67c5314669492b07cb574170c09f70994974e4",
      "donor_original_PR144":"f85394d50078fc384ce6aff55e669da866dfca35",
      "cases":source,
      "native_source_step_refinement":refined,
      "independent_quadrature_and_speed":compare,
      "C16_real_shear_and_escape_response_history":history,
      "positive_higher_angular_moment_nonidentifiability_counterexample":counterexample,
      "physics_admission":{
          "exact":"sharp pressure bounds for each instantaneous positive source with fixed emission energy, times and background Killing transport; linear Green bound on signed shear source",
          "independent_cone_source":"PR144 exact original positive three-node constructor used to attain lower and upper stresses",
          "not_claimed":"actual CaseA emission direction and photon spectrum, total Einstein stellar/escape energy-momentum closure, nonlinear backreacted HHe evolution or global redshift history",
          "external_Md14_C11_energy_sink_calibration":"kept original C16 source ledger, emitted escaped CaseA energy alone does not determine its angular radiation stress",
          "scientific_admission":"NOT_ISSUED"},
      "total_experiment_wall_s":time.perf_counter()-begin}
    (OUT/"CASEA_ESCAPE_SHARP_STUDY.json").write_text(json.dumps(result,indent=2)+"\n")
    print("SCOPED_ESCAPED_SOURCE_STUDY_SUMMARY",json.dumps({
      "cases":len(source),
      "refinements":sorted(refined),
      "independent_gauss_delta_max":compare["rule_tolerance"]["max_abs_16_vs_32"],
      "source_photon_original_vs_fast_max_relative":max(v["error_over_true_positive_source_cone_amplitude"] for v in differences.values()),
      "scoped_real_run_vector_angular_speedup":compare["vectorized_angular_scoped_kernel_speedup"],
      "counterexample_nonidentification_Pi_difference":counterexample["future_pressure_difference_from_unfixed_l4_plus"],
      "time_seconds":result["total_experiment_wall_s"]},indent=2))
if __name__=="__main__":
    study()
