#!/usr/bin/env python3
"""HE34-SCR: new mechanical state on a pinned saved background; no HE32 solver import."""
from pathlib import Path
import argparse, csv, hashlib, json, math, os, platform, sys, time
import numpy as np
import scipy
from scipy.integrate import solve_ivp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))
from certified_relaxation import solve_reduced

SOURCE_NPZ = Path("/tmp/he32_resume_20261022/restored/research/he32_sandbox_primordial_20261021/results/cases/s07_m03_r03.npz")
SOURCE_SHA = "c97ffa6a793c092b6b559b32581a7996a82b85a8e725b0e5893be9ae1e7bf30a"
CHIS = [10.0, 100.0, 1000.0, 10000.0]
TOL = 1e-6
NUMERICAL_QUADRATURE_BUDGET = 1e-9

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w") as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write("\n"); f.flush(); os.fsync(f.fileno())
    tmp.replace(path)

def background():
    target = HERE / "data/SAVED_BACKGROUND.csv"
    receipt = HERE / "evidence/BACKGROUND_INPUT.json"
    if not target.exists():
        if sha(SOURCE_NPZ) != SOURCE_SHA:
            raise ValueError("Saved HE32 case identity mismatch")
        with np.load(SOURCE_NPZ, allow_pickle=False) as d:
            names = list(d["observable_names"])
            o = d["observables"]
            N = o[:, names.index("eta")]
            S = o[:, names.index("signed_Sigma")] / math.sqrt(6)
            H = o[:, names.index("H_per_s")]
            z = o[:, names.index("z")]
        if len(N) != 201 or not np.all(np.diff(N) > 0) or not np.all(H > 0):
            raise ValueError("Saved input shape/expansion contract")
        target.parent.mkdir(parents=True, exist_ok=True)
        np.savetxt(target, np.column_stack([N,S,H,z]), delimiter=",",
                   header="N,S_s_over_H,H_per_s,mean_redshift", comments="", fmt="%.17g")
        save_json(receipt, {
            "source_case":"s07_m03_r03", "source_npz_sha256":SOURCE_SHA,
            "source_archive_sha256":"27cb0eb0a779815dfaa226849f706df2fed6f0ae6b792383cbc9a0f90635806a",
            "source_pin":"16a424b7290f484c57e97c8ed74f81e6d2043782",
            "csv_sha256":sha(target), "nodes":201,
            "mapping":"N=observable eta=ln(a/a0); S=signed_Sigma/sqrt(6); H and mean redshift copied",
            "interpolation":"piecewise-linear signed S is the exact input of this new control",
            "selection":"declared before execution: Sigma_F0=0.6, initial nonbaryonic P_m=P_r=0",
            "old_background_integrations":0,
            "scope":"one selected NPZ hash rechecked; full1392-payload recovery evidence reused"
        })
    meta = json.loads(receipt.read_text())
    if sha(target) != meta["csv_sha256"]:
        raise ValueError("Extracted input identity mismatch")
    a = np.loadtxt(target, delimiter=",", skiprows=1)
    return a[:,0], a[:,1], meta

def full_moments(N, S, chi, rtol=3e-11, atol=3e-13):
    """Independent linear eigenpressure reference W=a^5 P/p0, two variables."""
    state = np.array([1.,1.])
    history = [state.copy()]
    nfev = njev = nlu = 0
    for a,b,sa,sb in zip(N[:-1],N[1:],S[:-1],S[1:]):
        h=float(b-a); slope=float(sb-sa)/h
        def fun(t,w):
            s=float(sa)+slope*t
            flux=(chi/3.)*(w[1]-w[0])
            return [2*s*w[0]+flux, -4*s*w[1]-2*flux]
        def jac(t,w):
            s=float(sa)+slope*t
            return [[2*s-chi/3., chi/3.],
                    [2*chi/3., -4*s-2*chi/3.]]
        sol=solve_ivp(fun,(0.,h),state,method="Radau",rtol=rtol,atol=atol,jac=jac)
        if not sol.success:
            raise RuntimeError(sol.message)
        state=sol.y[:,-1]
        if not np.all(state>0) or not np.all(np.isfinite(state)):
            raise RuntimeError("Reference eigenpressure cone failure")
        history.append(state.copy())
        nfev+=sol.nfev; njev+=sol.njev; nlu+=sol.nlu
    W=np.asarray(history)
    pressure=(2*W[:,0]+W[:,1])/3
    ratio=(W[:,1]-W[:,0])/(3*pressure)
    return {"r":ratio, "u":np.log(pressure), "W":W,
            "nfev":nfev,"njev":njev,"nlu":nlu,
            "rtol":rtol,"atol":atol,"interval_solves":len(N)-1}

def require_numerics(a):
    estimate=float(a.quadrature_error_estimate)+float(a.omitted_layer_tail_bound)
    if not a.approximation_valid or not a.quadrature_converged or not math.isfinite(estimate) or estimate>NUMERICAL_QUADRATURE_BUDGET:
        raise RuntimeError("Numerical quadrature/convergence budget failed")
    return estimate

def discrepancy(a,b):
    return {"ratio_abs":float(np.max(np.abs(a["r"]-b["r"]))),
            "log_pressure_abs":float(np.max(np.abs(a["u"]-b["u"])))}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=HERE/"results")
    parser.add_argument("--rerun-reason",default=None,
                        help="Required explicit reason to replace dependency-matched completed evidence")
    args=parser.parse_args()
    out=args.out;out.mkdir(parents=True,exist_ok=True)
    N,S,bg=background()
    code={str(p.relative_to(HERE)):sha(p) for p in [HERE/"run_control.py",HERE/"src/certified_relaxation.py"]}
    identity_obj={"code":code,"input":bg["csv_sha256"],"chi":CHIS,"tolerance":TOL,
                  "numpy":np.__version__,"scipy":scipy.__version__,
                  "reference":"Radau full eigenpressures segmented at exact source knots"}
    identity=hashlib.sha256(json.dumps(identity_obj,sort_keys=True).encode()).hexdigest()
    receipt=out/"MECHANICAL_RECEIPT.json"
    if receipt.exists() and args.rerun_reason is None:
        old=json.loads(receipt.read_text())
        if old["identity"]==identity and all(sha(out/p)==h for p,h in old["payload_sha256"].items()):
            print(json.dumps({"status":"REUSED_COMPLETE_MECHANICAL_CONTROL","identity":identity}),flush=True)
            return
        raise RuntimeError("Existing control identity changed: preserve evidence and provide --rerun-reason")
    started=time.perf_counter()
    references={};approximations={};runs=[];payloads=[]
    for chi in CHIS:
        print("new mechanical control chi="+str(chi),flush=True)
        a=solve_reduced(N,S,chi,tol_ratio=TOL,tol_logp=TOL)
        numerical_estimate=require_numerics(a)
        b=full_moments(N,S,chi)
        references[chi]=b;approximations[chi]=a
        dr=np.abs(a.r-b["r"]);du=np.abs(a.u-b["u"])
        record={"chi":chi,"certificate_valid":bool(a.certificate_valid),
                "quadrature_converged":bool(a.quadrature_converged),
                "numerical_quadrature_budget":NUMERICAL_QUADRATURE_BUDGET,
                "numerical_estimate_plus_tail":numerical_estimate,
                "accepted_by_continuum_bound":bool(a.certified),
                "certificate_failures":list(a.certificate_failures),
                "max_ratio_error_at_saved_nodes":float(np.max(dr)),
                "max_logp_error_at_saved_nodes":float(np.max(du)),
                "max_ratio_continuum_bound":float(a.max_ratio_error_bound),
                "final_logp_continuum_bound":float(a.final_logp_error_bound),
                "quadrature_error_estimate":float(a.quadrature_error_estimate),
                "omitted_layer_tail_bound":float(a.omitted_layer_tail_bound),
                "reference_nfev":b["nfev"],"reference_rtol":b["rtol"],"reference_atol":b["atol"],
                "final_ratio":float(a.r[-1]),"final_expansion_factored_logpressure":float(a.u[-1]),
                "final_p_over_p0":float(math.exp(-5*(N[-1]-N[0])+a.u[-1]))}
        # A finite reference comparison corroborates the analytic bound, with an explicit numerical margin.
        record["sampled_error_inside_bound_plus_5e-10"]=bool(
            np.all(dr<=np.asarray(a.ratio_error_bound)+5e-10) and
            np.all(du<=np.asarray(a.logp_error_bound)+5e-10))
        if not record["sampled_error_inside_bound_plus_5e-10"]:
            raise AssertionError(record)
        if a.certified and (np.max(dr)>TOL or np.max(du)>TOL):
            raise AssertionError("Accepted reduction misses fixed requested tolerance")
        name="mechanics_chi_"+format(chi,"g")+".csv"
        np.savetxt(out/name,np.column_stack([N,S,b["r"],a.r,b["u"],a.u,a.ratio_error_bound,a.logp_error_bound]),
                   delimiter=",",header="N,S,reference_r,reduced_r,reference_u,reduced_u,ratio_bound,logp_bound",comments="",fmt="%.17g")
        payloads.append(name);runs.append(record)
    print("independent tolerance refinement chi=1000",flush=True)
    tight=full_moments(N,S,1000.,rtol=3e-12,atol=3e-14)
    refinement=discrepancy(references[1000.],tight)
    if max(refinement.values())>1e-9:
        raise AssertionError("Reference refinement inadequate for 1e-6 target")
    coarse=full_moments(N,S,1000.,rtol=1e-7,atol=1e-9)
    baseline_error=discrepancy(coarse,tight)
    if max(baseline_error.values())>TOL:
        raise AssertionError("Cost comparison baseline does not meet fixed tolerance")
    if not approximations[1000.].certified:
        raise AssertionError("Preselected cost comparison chi1000 not certified; record and reconsider benchmark scope")
    reduced_times=[];radau_times=[]
    for trial in range(5):
        print("matched-cost trial "+str(trial+1),flush=True)
        order=("reduced","Radau") if trial%2==0 else ("Radau","reduced")
        for lane in order:
            start=time.perf_counter()
            if lane=="reduced":
                timed=solve_reduced(N,S,1000.,tol_ratio=TOL,tol_logp=TOL)
                require_numerics(timed)
                reduced_times.append(time.perf_counter()-start)
            else:
                full_moments(N,S,1000.,rtol=1e-7,atol=1e-9)
                radau_times.append(time.perf_counter()-start)
    bench={"chi":1000.,"requested_ratio_abs":TOL,"requested_logp_abs":TOL,
           "same_inputs":True,"same_output_nodes":201,
           "reduced_includes":"candidate, pressure quadrature, tail estimate, continuum error certificate",
           "reference_method":"full two-eigenpressure Radau at each source interval",
           "reference_rtol":1e-7,"reference_atol":1e-9,
           "baseline_actual_error_vs_tighter_oracle":baseline_error,
           "trial_order":[["reduced","Radau"] if j%2==0 else ["Radau","reduced"] for j in range(5)],
           "reduced_seconds":reduced_times,"Radau_seconds":radau_times,
           "median_speed_ratio_Radau_over_reduced":float(np.median(radau_times)/np.median(reduced_times)),
           "scope":"same workload and requested accuracy; reference is one available implicit baseline, not an optimality claim"}
    # Discriminating mutations use the already obtained reference; no reference trajectory is replayed.
    wrong_norm=solve_reduced(N,S*math.sqrt(6),1000.,tol_ratio=TOL,tol_logp=TOL)
    mutation_error=discrepancy({"r":wrong_norm.r,"u":wrong_norm.u},tight)
    bare_root0=-4*S[0]/(1000+2*S[0]+math.hypot(1000+2*S[0],math.sqrt(32)*S[0]))
    mutations={"normalization_sqrt6_omitted":mutation_error,
               "normalization_mutation_detected":bool(max(mutation_error.values())>TOL),
               "initial_layer_omitted_initial_ratio_error":float(abs(bare_root0)),
               "initial_layer_mutation_detected":bool(abs(bare_root0)>TOL)}
    if not mutations["normalization_mutation_detected"] or not mutations["initial_layer_mutation_detected"]:
        raise AssertionError("Discriminating mutation did not detect intended defect")
    info={"schema":"he34_scr.mechanical_controls.v1","identity":identity,
          "equations":"Wperp'=2S Wperp+chi(Wparallel-Wperp)/3; Wparallel'=-4S Wparallel-2chi(Wparallel-Wperp)/3",
          "input":bg,"parameters":identity_obj,
          "environment":{"python":sys.version,"numpy":np.__version__,"scipy":scipy.__version__,"platform":platform.platform(),"cpu_count_reported":os.cpu_count()},
          "target":{"ratio_abs":TOL,"logp_abs":TOL},
          "runs":runs,"reference_refinement":refinement,"matched_accuracy_benchmark":bench,"adversarial_mutations":mutations,
          "counts":{"old_HE32_IVPs_repeated":0,"old_HE32_renders_repeated":0,
                    "new_full_eigenpressure_reference_histories":4,"reference_refinements":1,
                    "coarse_baseline_accuracy_histories":1,"timed_baseline_histories":5,
                    "reference_interval_solves_total":2200,
                    "new_physical_cosmological_IVPs":0,"NCP_jobs":0},
          "total_wall_seconds":time.perf_counter()-started,
          "qualification":"The error bound is a continuum result for the declared interpolant. Ordinary binary64 and quadrature estimates are independently checked; no outward-rounded machine certificate or calibrated all-gas transport is claimed."}
    save_json(out/"MECHANICAL_CONTROLS.json",info);payloads.append("MECHANICAL_CONTROLS.json")
    save_json(receipt,{"identity":identity,"status":"completed","command":"python3 "+str(HERE/"run_control.py"),
                      "rerun_reason":args.rerun_reason,"payload_sha256":{p:sha(out/p) for p in payloads}})
    print(json.dumps({"status":"completed","runs":runs,"benchmark":bench,"refinement":refinement,"counts":info["counts"]},indent=2),flush=True)

if __name__=="__main__":
    try:
        main()
    except Exception as error:
        save_json(HERE/"evidence"/("CONTROL_FAILURE_"+time.strftime("%Y%m%dT%H%M%SZ",time.gmtime())+".json"),
                  {"error":repr(error),"command":sys.argv,"driver_sha256":sha(__file__)})
        raise

