#!/usr/bin/env python3
"""Independent stdlib readback of actual original F08 S0 Bianchi Thomson sky.

This program reads the DATA bytes rather than importing observer_sky.py.
Its checks are consistency tests, not independent source-model dynamical runs.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math,statistics
from collections import defaultdict
from pathlib import Path

PAIRS=[(8,16),(16,32),(32,64)]
FRACTIONS=[.25,.5,.75,.95]
NUMROWS=10752
EXPECTED_SOURCE={
"S0_BI-electron_density.csv.gz":"663911291bea564d314e1d46df9750c03a39fd5d9404eca6a7485776d894f723",
"S0_FLRW-electron_density.csv.gz":"0b81cae87d6f90888d1d3def1995cd8d029625d1cc1dd11bffab94e8d30e7efa",
"science_scenario_v1.json":"c83d2d43adda663707f99af2b45576eb4478cd94d3440a21fd21eaed32b5f2c1"}

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def audit(out):
    out=Path(out).resolve()
    source=Path(__file__).resolve().parent/"source_inputs"
    for name,sha in EXPECTED_SOURCE.items():
        if digest(source/name)!=sha:raise ValueError("original source input has changed")
    j=json.loads((out/"RESULT.json").read_text())
    assert j["status"]=="SOURCE_AUTHENTIC_PRESCRIBED_BIANCHI_OBSERVER_CONDITIONAL_NUMERICALLY_CHECKED"
    assert j["ray_count"]==NUMROWS and j["canonical_delta"]==0
    assert j["source_original_F08_scientific_admission"]=="HOLD"
    assert j["source_original_F09"]=="BLOCKED_EXTERNAL_ATOMIC_PROVIDER_DOMAIN"
    assert j["observer_relative_redshift_not_absolute_cosmic_z"]
    csvpath=out/j["source_sky_csv"]
    assert digest(csvpath)==j["source_sky_csv_sha256"]
    H=j["original_prescribed_H_s_inv"]
    c=j["original_c_cm_s"];sig=j["original_thomson_sigma_cm2"]
    original_time=j["observer_cosmic_time_s"]
    counts=defaultdict(int);bygroup=defaultdict(list)
    max_decomp=max_redshift=max_visibility=max_parity=0.
    selected=[]
    with gzip.open(csvpath,"rt",newline="",encoding="utf8") as f:
        rd=csv.DictReader(f)
        columns=list(rd.fieldnames)
        assert len(columns)==j["physical_science_columns"]
        for i,row in enumerate(rd):
            t={k:(int(v) if k in ("angular_nmu","angular_nphi","mu_bin","phi_bin") else float(v))
               for k,v in row.items()}
            assert all(math.isfinite(float(v)) for v in t.values())
            key=(t["angular_nmu"],t["angular_nphi"],t["window_fraction"])
            counts[key]+=1
            bygroup[key].append(t)
            if i in set(round(k*(NUMROWS-1)/23) for k in range(24)):
                selected.append(row)
            assert abs(sum(t[k]**2 for k in ("nx","ny","nz"))-1)<5e-15
            assert 0<=t["emission_time_s"]<=original_time
            assert t["tau_BI"]>0 and t["tau_FLRW"]>0
            assert t["tau_BI_conditional_sample_lo"]<=t["tau_BI"]+1e-18
            assert t["tau_BI"]<=t["tau_BI_conditional_sample_hi"]+1e-18
            redshift_resid=abs(0.5*math.log(sum(t[k]**2*math.exp(2*H[h]*(original_time-t["emission_time_s"]))
                     for h,k in enumerate(("nx","ny","nz"))))-math.log1p(t["relative_redshift"]))
            max_redshift=max(max_redshift,redshift_resid)
            residual=abs(t["delta_tau_total"]-t["delta_tau_material_fixed_time"]-t["delta_tau_geometry_fixed_relative_z"])
            max_decomp=max(max_decomp,residual)
            want= c*sig*t["ne_BI_emitter_cm3"]*math.exp(-t["tau_BI"])/(
                (1+t["relative_redshift"])*t["effective_directional_H_s_inv"])
            max_visibility=max(max_visibility,abs(want-t["visibility_BI_per_relative_z"]))
            assert abs(math.exp(-t["tau_BI"])-t["transmission_BI"])<2e-15
            assert t["visibility_BI_per_relative_z"]>0
    assert i+1==NUMROWS
    assert len(selected)==24
    assert max_decomp<2e-19 and max_redshift<3e-14 and max_visibility<2e-14
    recompute=[]
    for m,p in PAIRS:
        for frac in FRACTIONS:
            group=bygroup[(m,p,frac)]
            assert len(group)==m*p
            geo=[r["delta_tau_geometry_fixed_relative_z"] for r in group]
            gm=statistics.fmean(geo)
            cent=[v-gm for v in geo]
            quad=[[statistics.fmean(cent[k]*((group[k][("nx","ny","nz")[a]]*
                group[k][("nx","ny","nz")[b]])-(1/3 if a==b else 0))
                for k in range(len(group))) for b in range(3)] for a in range(3)]
            orig=next(q for q in j["sky_windows"] if q["angular_nmu"]==m and
                      q["angular_nphi"]==p and q["fraction"]==frac)
            for a in range(3):
                for b in range(3):
                    if abs(quad[a][b]-orig["quadrupole_xyz"][a][b])>2e-19:
                        raise ValueError("independent quadrupole numeric mismatch")
            assert abs(sum(quad[i][i] for i in range(3)))<1e-17
            pairs={(r["mu_bin"],r["phi_bin"]):r for r in group}
            for row in group:
                opp=pairs[(m-1-row["mu_bin"],(row["phi_bin"]+p//2)%p)]
                max_parity=max(max_parity,abs(row["tau_BI"]-opp["tau_BI"]),
                                       abs(row["visibility_BI_per_relative_z"]-opp["visibility_BI_per_relative_z"]))
            recompute.append({"grid":[m,p],"fraction":frac,
                "Q_diag":[quad[k][k] for k in range(3)],
                "tau_BI_sky_mean":statistics.fmean(r["tau_BI"] for r in group),
                "tau_FLRW":group[0]["tau_FLRW"],
                "geometry_rms":math.sqrt(statistics.fmean(x*x for x in cent)),
                "material_delta":group[0]["delta_tau_material_fixed_time"],
                "max_parity_abs":max_parity})
    assert max_parity<1e-17
    with (out/"INDEPENDENT_SKY_WITNESS_24.csv").open("w",encoding="utf8",newline="") as file:
        wr=csv.DictWriter(file,fieldnames=columns);wr.writeheader();wr.writerows(selected)
    result={"schema":"REI_F08_S0_THOMSON_OBSERVER_INDEPENDENT_AUDIT_V1",
        "original_F08_input_hashes_verified":True,"original_F09_domain_block_preserved":True,
        "source_data_csv_sha256":j["source_sky_csv_sha256"],
        "actual_original_F08_s0_source_runs":2,"source_original_accepted_steps":16000,
        "physical_numerical_sky_ray_rows":NUMROWS,"source_data_columns":len(columns),
        "exact_redshift_max_log_residual":max_redshift,
        "exact_material_geometry_max_abs_residual":max_decomp,
        "visibility_formula_max_abs_residual":max_visibility,
        "opposite_direction_parity_max_abs":max_parity,
        "independent_quadrupole_check":"PASS_WITHIN_2e-19",
        "source_history_model_error_bound":"NOT_CLAIMED",
        "assumed_source_time_interpolation":"PIECEWISE_LINEAR",
        "source_scientific_admission":"HOLD",
        "central_DAG":"28/88_REPORTED","canonical_delta":0,
        "source_units":"proper_cm^-3_times_cm2_times_cm_per_s_times_proper_s",
        "sky_grid_summary":recompute}
    (out/"INDEPENDENT_AUDIT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("SOURCE_F08_OBSERVER_INDEPENDENT_AUDIT",
          json.dumps({"rows":NUMROWS,"columns":len(columns),"redshift_residual":max_redshift,
          "material_geometry_residual":max_decomp,"max_visibility_residual":max_visibility,
          "max_parity":max_parity,"quad_groups":len(recompute),"source_csv":result["source_data_csv_sha256"],
          "canonical_delta":0},sort_keys=True),flush=True)
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("output",type=Path)
    args=p.parse_args()
    audit(args.output)

if __name__=="__main__":
    main()
