#!/usr/bin/env python3
"""Different-implementation original source first-step referee; no rust imports."""
from __future__ import annotations
import csv, hashlib, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
P=ROOT/"source_inputs"/"ORIGINAL_REI_F08_S0_FIRSTSTEP_256_RAYS.csv"
Q=ROOT/"results"/"RUST_ORIGINAL_F08_FIRSTSTEP_HI_256.csv"
J=ROOT/"results"/"SCIENCE_RESULT.json"
C=29979245800.0; DT=625000000.0; E0=13.7
CHI=13.598434599702; EVALS=("S0_BI","S0_FLRW")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sig(e):
    if e<13.60:return 0.
    if not(e<=50000 and math.isfinite(e)):raise ValueError("atomic source domain")
    x=e/.4298
    y=abs(x)
    return 5.475e4*((x-1)**2)*y**(2.963/2-5.5)*(1+math.sqrt(y/32.88))**(-2.963)*1e-18
def rhs(nhi, e):
    optical=C*DT*nhi*sig(e)
    return optical/(1+optical)
def read(p):return list(csv.DictReader(p.open()))
def near(x,y):
    return math.isclose(x,y,rel_tol=3e-12,abs_tol=1e-24)
def run():
    source=read(P);out=read(Q);summary=json.loads(J.read_text())
    lock=json.loads((ROOT/"source_inputs"/"SOURCE_LOCK.json").read_text())
    assert sha(P)==lock["input_256_ray_csv_sha256"]
    assert sha(ROOT/"src"/"original_atomic_provider.rs")==lock["original_rust_atomic_sha256"]
    assert len(source)==len(out)==256 and summary["canonical_delta"]==0
    assert summary["original_full_26event_replayed"] is False
    errs={name:0.0 for name in (
        "exact_energy_ev","hat_lower_weight","source_birth_photon_per_H",
        "hat_forbidden_photon_per_H","sigma_exact_cm2","sigma_hat_cm2",
        "absorbed_characteristic_per_H","absorbed_hat_per_H",
        "delta_absorption_hat_minus_characteristic_per_H",
        "photoelectron_excess_characteristic_ev_per_H",
        "photoelectron_excess_hat_ev_per_H",
        "delta_excess_hat_minus_characteristic_ev_per_H","hat_energy_variance_ev2")}
    sums={key:{} for key in EVALS}
    for branch in EVALS:
        idxs=[i for i,v in enumerate(source) if v["branch"]==branch]
        assert len(idxs)==128 and idxs==list(range(0,128)) if branch=="S0_BI" else idxs==list(range(128,256))
        w=[]
        for i in idxs:
            a=source[i]; q=[float(a[f"q{k}"]) for k in "xyz"];h=[float(a["h"+k]) for k in "xyz"]
            g=math.sqrt(math.fsum((q[k]**2)*math.exp(-2*h[k]*DT) for k in range(3)))
            w.append(math.exp(-math.fsum(h)*DT)/(g*g*g))
        ws=math.fsum(w)
        accum={name:[] for name in ["nsource","leak","ac","ah","qc","qh"]}
        for j,i in enumerate(idxs):
            a=source[i]; o=out[i]
            assert o["branch"]==a["branch"] and int(o["direction_id"])==int(a["direction_id"])
            q=[float(a["q"+k]) for k in "xyz"];h=[float(a["h"+k]) for k in "xyz"]
            n=float(a["nHI_cm3"]); lo=float(a["e_lower_ev"]);hi=float(a["e_upper_ev"])
            e=E0*math.sqrt(math.fsum(q[k]**2*math.exp(-2*h[k]*DT) for k in range(3)))
            wl=(hi-e)/(hi-lo);wu=1-wl; n0=.05/128; ns=5e-15*DT*w[j]/ws
            ac=n0*rhs(n,e)+ns*rhs(n,hi)
            ah=n0*(wl*rhs(n,lo)+wu*rhs(n,hi))+ns*rhs(n,hi)
            qc=n0*rhs(n,e)*(e-CHI)+ns*rhs(n,hi)*(E0-CHI)
            qh=n0*(wl*rhs(n,lo)*(lo-CHI)+wu*rhs(n,hi)*(hi-CHI))+ns*rhs(n,hi)*(E0-CHI)
            predicted={
                "exact_energy_ev":e,"hat_lower_weight":wl,
                "source_birth_photon_per_H":ns,"hat_forbidden_photon_per_H":n0*wl,
                "sigma_exact_cm2":sig(e),"sigma_hat_cm2":wl*sig(lo)+wu*sig(hi),
                "absorbed_characteristic_per_H":ac,"absorbed_hat_per_H":ah,
                "delta_absorption_hat_minus_characteristic_per_H":ah-ac,
                "photoelectron_excess_characteristic_ev_per_H":qc,
                "photoelectron_excess_hat_ev_per_H":qh,
                "delta_excess_hat_minus_characteristic_ev_per_H":qh-qc,
                "hat_energy_variance_ev2":(e-lo)*(hi-e)}
            for key,val in predicted.items():
                native=float(o[key])
                if key=="hat_lower_weight":  # cancellation of 13.7-E: 1 ulp / 0.025 eV
                    passed=math.isclose(native,val,rel_tol=5e-11,abs_tol=4e-13)
                elif key=="hat_forbidden_photon_per_H":
                    passed=math.isclose(native,val,rel_tol=5e-11,abs_tol=3e-16)
                elif key=="hat_energy_variance_ev2":
                    passed=math.isclose(native,val,rel_tol=5e-9,abs_tol=2e-14)
                elif key.startswith("delta_"):
                    passed=math.isclose(native,val,rel_tol=5e-9,abs_tol=2e-18)
                else:
                    passed=near(native,val)
                if not passed:raise AssertionError(f"RUST_ORACLE_MISMATCH {branch} {i} {key} {native} {val}")
                errs[key]=max(errs[key],abs(native-val))
            for key,val in {"nsource":ns,"leak":n0*wl,"ac":ac,"ah":ah,"qc":qc,"qh":qh}.items():accum[key].append(val)
        sums[branch]={k:math.fsum(v) for k,v in accum.items()}
        owner=next(x for x in summary["branch_results"] if x["branch"]==branch)
        for k,field in {"nsource":"source_birth_in_step_per_H","leak":"first_step_hat_forbidden_weight_before_absorption_per_H",
                        "ac":"absorbed_characteristic_per_H","ah":"absorbed_hat_per_H",
                        "qc":"photoelectron_excess_characteristic_ev_per_H","qh":"photoelectron_excess_hat_ev_per_H"}.items():
            if not near(sums[branch][k],float(owner[field])):
                raise AssertionError("RUST_ORACLE_GLOBAL_MISMATCH "+branch+" "+k)
        assert 0<sums[branch]["leak"]<.05
    doc={"schema":"REI_OWNER_F08_FIRSTSTEP_BLIND_SAME_AUTHOR_INDEPENDENT_ORACLE_V1",
         "original_source_rows":256,"original_atomic_provider_sha256":lock["original_rust_atomic_sha256"],
         "physics_csv_sha256":sha(Q),"physics_json_sha256":sha(J),
         "individual_rust_oracle_checks":len(source)*len(errs),
         "max_absolute_differences":errs,"independently_recomputed_sums":sums,
         "science_status":"NUMERICALLY_CHECKED_SOURCE_CONDITIONAL_RUST_FROZEN_MATTER",
         "limitations":["not full HHe 26 event solver","no native continuum radiation transfer",
                        "no physical 16k-step feedback bound","not independent-author referee"],
         "canonical_DAG":"28/88","production":"HOLD"}
    f=ROOT/"results"/"INDEPENDENT_ORACLE.json"
    f.write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"verified_rows":len(source),"independent_scalar_checks":len(source)*len(errs),
                      "max_abs_err":max(errs.values()),"sums":sums,"audit_sha":sha(f)},indent=2))
if __name__=="__main__":run()
