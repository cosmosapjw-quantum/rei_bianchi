"""Analysis and falsifiable numerical certificate for real native REI donor short runs.

Actual PR127 local-GL4 proper-time corrected Rust binary, two distinct
physical initial states, MD14/BB50K no synthetic source. Results are scoped
to 40 accepted steps (tiny elapsed redshift), not full EoR.
"""
from __future__ import annotations
import csv,hashlib,json,math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
CASES=("QZERO_BASELINE","QZERO_HYREC",
       "QMINUS_BASELINE","QMINUS_HYREC",
       "QPLUS_BASELINE","QPLUS_HYREC")
PHYSICAL=("a","zbar","xHII","xHeII","xHeIII","xe_per_H",
    "Tgas_K","H_s_inv","photon_number_per_H","photon_energy_eV_per_H",
    "source_n_per_H","absorbed_n_per_H","number_ledger_per_H",
    "energy_ledger_eV_per_H","last_error",
    "attempts","rejects","rhs_evaluations",
    "photo_free_dxHII_dt_per_s","photo_free_dT_dt_K_per_s")


def load_run(directory:Path):
    manifest=json.loads((directory/"RUN_RESULTS.json").read_text())
    if manifest["source_parent_commit"]!="edddcd6ea9a135fcf18c7be8357b5e11fea87407":
        raise ValueError("wrong native PR127 source")
    values={}
    for case,record in zip(CASES,manifest["serial_runs"]):
        f=directory/(case+".csv")
        sha=hashlib.sha256(f.read_bytes()).hexdigest()
        if sha!=record["sha256"] or case!=record["case"]:
            raise ValueError("native physical source output SHA changed")
        values[case]=list(csv.DictReader(f.open()))
        if len(values[case])!=41:
            raise ValueError("not 40 actually accepted native steps")
    if not all(manifest["identical_parallel_bytes"]):
        raise ValueError("physical output not reproducible in two-worker mode")
    return manifest,values


def compare_panels(a64,a4096):
    obs={}
    worst_time_rel=0.
    for case in CASES:
        rows64=a64[case];rows4096=a4096[case]
        for k,(v64,v4096) in enumerate(zip(rows64,rows4096)):
            for key in PHYSICAL:
                if v64[key]!=v4096[key]:
                    raise ValueError(f"source physics mismatch in {case}/{k}/{key}")
            t0=float(v64["time_s"]); t1=float(v4096["time_s"])
            rel=abs(t0-t1)/max(abs(t1),1)
            worst_time_rel=max(worst_time_rel,rel)
    if worst_time_rel>2e-13:
        raise ArithmeticError("cheap background panel clock deviates from original 4096 beyond planned tolerance")
    return {
      "source_physical_fields":list(PHYSICAL),
      "physical_rows_compared":6*41,
      "bitwise_equal_parsed_physical_fields":True,
      "worst_local_absolute_clock_relative":worst_time_rel,
      "method_4096":"original native point_at_scale Simpson4096, PR127 local GL4 chemistry-time increment",
      "method_64":"same physical driver but legacy point_at_scale Simpson64, PR127 local GL4 chemistry-time increment",
      "status":"PASS_SCOPED_40STEP_PANEL_REDUCTION",
    }


def factorial_rhs():
    file=ROOT/"NATIVE_FACTORIAL_RHS.csv"
    rows=list(csv.DictReader(file.open()))
    if len(rows)!=12:
        raise ValueError("missing 3 signed-q by 4 actual native source states")
    out={}
    for q in ("0.00000000000000000e0","-1.00000000000000002e-2","1.00000000000000002e-2"):
        picked={r["combination"]:r for r in rows if r["q_ref"]==q}
        if set(picked)!={"baseline","x_only","T_only","full_donor"}:
            raise ValueError("incomplete factorial native RHS")
        for p in picked.values():
            if abs(float(p["energy_local_residual_erg_cm3_s"]))>1e-45:
                raise ValueError("native thermochemical event ledger nonzero")
        out[q]={}
        for key in ("dxHII_dt_s_inv","dTgas_dt_K_s_inv","rr_HI_cm3_s",
                    "ci_HI_cm3_s","CMB_heat_erg_cm3_s"):
            b=float(picked["baseline"][key])
            x=float(picked["x_only"][key])
            t=float(picked["T_only"][key])
            f=float(picked["full_donor"][key])
            dx=x-b
            dt=t-b
            cross=f-x-t+b
            delta=f-b
            if abs((dx+dt+cross)-delta)>5e-14*max(abs(f),abs(b),1e-100):
                raise ValueError("factorial response decomposition failed")
            out[q][key]=dict(baseline=b,donor=f,full_difference=delta,
                x_only_contribution=dx,T_only_contribution=dt,interaction=cross)
    # Fresh q+/q- gases share physical input, H even in q; source scalar
    # recombination rate at zero ionizing stocks is exactly even.
    xp=out["1.00000000000000002e-2"]["dxHII_dt_s_inv"]
    xm=out["-1.00000000000000002e-2"]["dxHII_dt_s_inv"]
    if xp!=xm:
        raise ValueError("signed q initial collision scalar not even in the frozen model")
    return {"schema":"rei.rec.initial_rhs_factorial.v1",
            "source":"native actual HHe Grackle case A, no ionizing photon stock, nH proper cm-3",
            "controlled_variables":"x_HII and initial gas temperature; original physical number fractions in respective time",
            "factorial":out,
            "q_plus_minus_hydrogen_rate_identical":True,
            "not_full_native_photo_RHS_at_later_times":True}


def run():
    meta64,short=load_run(ROOT/"science_40step_p64")
    meta4096,reference=load_run(ROOT/"science_40step_p4096")
    if meta64["panels"]!=64 or meta4096["panels"]!=4096:
        raise ValueError("wrong source panel pair")
    match=compare_panels(short,reference)
    rhs=factorial_rhs()
    q0reference=reference["QZERO_BASELINE"]
    last=q0reference[-1]
    time_s=float(last["time_s"])
    zstart=float(q0reference[0]["zbar"])
    zend=float(last["zbar"])
    output={
       "schema":"rei.rec.native_donor_short_validation.v1",
       "source_rei_scenario_sha256":meta64["original_REI_scenario_sha256"],
       "source_hyrec_full_stdout_sha256":meta64["original_2012_HyRec_stdout_sha256"],
       "source_native_parent_PR127":meta64["source_parent_commit"],
       "source_paired_IC_identity":meta64["donor_blob_id"],
       "accepted_steps_per_case":40,
       "cases":list(CASES),
       "elapsed_proper_seconds":time_s,
       "start_zbar":zstart,
       "end_zbar":zend,
       "redshift_advance":zstart-zend,
       "physical_horizon_warning":"Only ~6.5 years of proper cosmic time near zbar20: not a zbar20->4 evolution.",
       "physics_grid_parity":match,
       "factorial_RHS_evidence":rhs,
       "background_64_panel_measured_serial_sum_s":meta64["serial_wall_sum_s"],
       "background_4096_panel_measured_serial_sum_s":meta4096["serial_wall_sum_s"],
       "short_run_speedup_64_over_4096":meta4096["serial_wall_sum_s"]/meta64["serial_wall_sum_s"],
       "native_parallel_4096_speedup":meta4096["parallel_speedup"],
       "native_parallel_64_speedup":meta64["parallel_speedup"],
       "source_scope":"native short REI correct local GL4 clock and photon/injection/chemistry, fixed optional original donor; no native full EoR IC adoption.",
       "status":"PASS_SCOPED_SHORT_NATIVE_IC_AND_MATCHED_PANEL_REDUCTION",
    }
    (ROOT/"NATIVE_SHORT_SENSITIVITY_ANALYSIS.json").write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:output[k] for k in
        ("status","elapsed_proper_seconds","redshift_advance",
         "short_run_speedup_64_over_4096",
         "native_parallel_4096_speedup","native_parallel_64_speedup")},
        indent=2))
    print("X_RHS_DECOMPOSITION_Q0",json.dumps(
        rhs["factorial"]["0.00000000000000000e0"]["dxHII_dt_s_inv"],indent=2))
    return output


if __name__=="__main__":
    run()
