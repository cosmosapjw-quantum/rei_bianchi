#!/usr/bin/env python3
"""Independent BR05 local panel certificates and native retained-width audit.

The inputs are read-only monitor exports. No dynamics, source, Verner, or Killing
integration is rerun. Root's independent source/geometry audit owns those gates.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime,timezone
from decimal import Decimal,localcontext
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback
from verify_panel_math import Reference,cert,exact64,exn,sha,write_csv,D,Z,O

def read(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def check(monitor,outdir):
    started=time.monotonic()
    names=["MONITOR_RULES.csv","MONITOR_PANELS.csv","MONITOR_BIRTHS.csv",
           "MONITOR_STEPS.csv","MONITOR_FINAL_COHORTS.csv"]
    hashes={name:sha(monitor/name) for name in names}
    steps={int(v["step"]):v for v in read(monitor/names[3])}
    rules={(int(v["step"]),int(v["rule_id"])):v for v in read(monitor/names[0])}
    panels={(int(v["step"]),int(v["rule_id"]),int(v["panel_id"])):v for v in read(monitor/names[1])}
    nodes={}
    cohorts={}
    birth_count=0
    template_ids=set()
    with (monitor/names[2]).open(newline="") as f:
        for row in csv.DictReader(f):
            step,rule,node,panel=(int(row[k]) for k in ["step","rule_id","node_id","panel_id"])
            key=(step,rule)
            nk=(*key,node)
            pair=(row["target_age_x"],row["emission_weight"])
            if nk in nodes:
                assert nodes[nk]==pair,("rule/template node drift",nk)
            else:
                nodes[nk]=pair
            assert panel==node//2
            assert (*key,panel) in panels
            cohort=int(row["cohort_index"])
            assert cohort not in cohorts,("cohort ID reused",cohort)
            cohorts[cohort]=((*key,panel),row["actual_birth_time_s"])
            template_ids.add((step,int(row["template_id"])))
            left=float(panels[(*key,panel)]["left_x"])
            right=float(panels[(*key,panel)]["right_x"])
            clock=float(row["actual_clock_age_x"])
            assert left<=clock<=right,("actual clock outside panel",cohort)
            assert float(row["born_count_com3"])>=0 and float(row["accepted_count_com3"])>=0
            birth_count+=1
    panel_refs=[]
    parts={}
    maxima={}
    failures=[]
    checks=0
    with localcontext() as ctx:
        ctx.prec=90
        for index,(key,row) in enumerate(panels.items()):
            step,rule,panel=key
            rr=rules[(step,rule)]
            sr=steps[step]
            tau_f=float(rr["tau"])
            tau=exact64(rr["tau"])
            assert 0<=tau<=D("1e12"),"outside declared Decimal tail domain"
            lf,rf=float(row["left_x"]),float(row["right_x"])
            width_f=float(row["width_from_actual_weights"])
            dt_f=float(sr["dt_s"])
            t1_f=float(sr["t1_s"])
            refn=int(rr["refinement"])
            assert row["width_bits_match"]=="true"
            assert width_f==rf-lf
            pair=[(float(nodes[(step,rule,2*panel+i)][0]),
                   float(nodes[(step,rule,2*panel+i)][1])) for i in range(2)]
            assert width_f==pair[0][1]+pair[1][1]
            assert float(row["nominal_width_s"])==dt_f*width_f
            assert float(row["optical_width"])==tau_f*width_f
            assert float(row["represented_birth_left_s"])==t1_f-dt_f*rf
            assert float(row["represented_birth_right_s"])==t1_f-dt_f*lf
            assert float(row["represented_width_s"])==((t1_f-dt_f*lf)-(t1_f-dt_f*rf))
            # Reconstruct the actual binary64 inputs to Rust compare_nodes.
            local_fp=[(exact64((x-lf)/width_f),exact64(w/width_f)) for x,w in pair]
            local_tau=exact64(tau_f*width_f)
            calc=cert(local_tau,local_fp)
            exact_m=calc["exact_mass"]
            log_ratio=calc["logmass"]-exact_m.ln()
            mean_exact=(O/local_tau-exn(local_tau)/(O-exn(local_tau))) if local_tau else D(1)/2
            second_exact=(D(2)/(local_tau*local_tau)-(O+D(2)/local_tau)*exn(local_tau)/(O-exn(local_tau))) if local_tau else D(1)/3
            expected={"exact_mass":exact_m,"discrete_mass":calc["mass"],
              "relative_mass_defect":calc["mass"]/exact_m-1,"log_mass_ratio":log_ratio,
              "cdf_sup":calc["ks"],"w1_normalized":calc["w1"],
              "exact_mean":mean_exact,"discrete_mean":calc["mean"],
              "mean_defect":calc["mean"]-mean_exact,"exact_second":second_exact,
              "discrete_second":calc["second"],"second_defect":calc["second"]-second_exact}
            errs={}
            for field,value in expected.items():
                got=exact64(row["local_kernel_survivor_unit_"+field])
                err=abs(got-value)
                tolerance=D("3e-14")
                if field in ["w1_normalized","exact_mean","discrete_mean","exact_second","discrete_second","exact_mass"]:
                    tolerance=D("2e-10")*abs(value)+D("2e-30")
                passed=err<=tolerance
                checks+=1
                maxima[field]=max(maxima.get(field,Z),err)
                errs[field]=str(err)
                if not passed:
                    failures.append({"panel":list(key),"field":field,"actual":str(got),
                                     "reference":str(value),"error":str(err),"tolerance":str(tolerance)})
            # Separately use exact represented global node reals and true panel
            # endpoints. This is the mathematical composition measure, whose
            # mass is not silently replaced by a rounded local certificate.
            left,right=exact64(lf),exact64(rf)
            width=right-left
            true_local=[((exact64(x)-left)/width,exact64(w)/width) for x,w in pair]
            true_c=cert(tau*width,true_local)
            mp=exn(tau*left)*width*true_c["exact_mass"]
            nq=exn(tau*left)*width*true_c["mass"]
            exact_panel_float_ref=exn(tau*left)*exact64(width_f)*Reference(local_tau).phi
            panel_mass_error=abs(exact64(row["exact_survival_per_unit_born"])-exact_panel_float_ref)
            maxima["panel_exact_survival_mass"]=max(maxima.get("panel_exact_survival_mass",Z),panel_mass_error)
            assert panel_mass_error<=D("3e-14")*exact_panel_float_ref+exact64(float.fromhex("0x0.0000000000001p-1022"))
            assert (row["reference_underflow"]=="true")== (float(row["exact_survival_per_unit_born"])==0.0)
            parts.setdefault((step,rule),[]).append((mp,nq,width,true_c))
            nominal=exact64(dt_f)*width
            physical_excess=max(Z,nominal-exact64(dt_f)/refn)
            optical_excess=max(Z,tau*width-(1+tau*left)/refn)
            assert physical_excess<=D("3e-15")*max(O,nominal)
            assert optical_excess<=D("3e-15")*max(O,tau*width)
            panel_refs.append({"step":step,"rule_id":rule,"panel_id":panel,
              "local_tau_input":str(local_tau),"local_w1_reference":str(calc["w1"]),
              "local_cdfsup_reference":str(calc["ks"]),"true_panel_exact_mass":str(mp),
              "true_panel_discrete_mass":str(nq),
              "physical_width_bound_roundoff_excess_s":str(physical_excess),
              "optical_width_bound_roundoff_excess":str(optical_excess),
              "largest_local_field_absolute_error":str(max(D(e) for e in errs.values()))})
            if (index+1)%2000==0:
                print("PANELS_CHECKED",index+1,flush=True)
        composition=[]
        for key,vals in parts.items():
            rr=rules[key]
            mass=Reference(exact64(rr["tau"])).phi
            qmass=sum((v[1] for v in vals),Z)
            assert abs(sum((v[0] for v in vals),Z)-mass)<D("1e-64")
            normalized=[(m/mass,n/qmass,h,c) for m,n,h,c in vals]
            tv=sum((abs(p-q) for p,q,h,c in normalized),Z)/2
            width=sum((p*h for p,q,h,c in normalized),Z)
            fitted=sum((p*h*c["w1"] for p,q,h,c in normalized),Z)
            w1_bound=sum((min(p,q)*h*c["w1"] for p,q,h,c in normalized),Z)+tv
            ks_bound=max(p*c["ks"] for p,q,h,c in normalized)+tv
            observed_w1=exact64(rr["kernel_survivor_unit_w1_normalized"])
            observed_ks=exact64(rr["kernel_survivor_unit_cdf_sup"])
            tolerance=D("2e-10")*abs(fitted)+D("2e-30")
            assert abs(observed_w1-fitted)<=tv+tolerance,(key,observed_w1,fitted,tv)
            assert observed_w1<=w1_bound+tolerance
            assert observed_ks<=ks_bound+D("3e-14")
            assert fitted<=width+D("1e-64")
            composition.append({"step":key[0],"rule_id":key[1],
             "frozen_mass_weighted_width_x":str(width),"reference_matched_panel_w1_x":str(fitted),
             "represented_panel_mass_TV":str(tv),"minmass_W1_plus_TV_bound_x":str(w1_bound),
             "panel_CDFsup_plus_TV_bound":str(ks_bound),
             "observed_rule_w1_x":str(observed_w1),"observed_rule_cdfsup":str(observed_ks)})
        total=weighted=Z
        unmatched=0
        final_count=positive=zero=0
        represented_weighted=Z
        max_final_clock_defect=Z
        with (monitor/names[4]).open(newline="") as f:
            for row in csv.DictReader(f):
                idx=int(row["cohort_index"])
                n=exact64(row["retained_count_com3"])
                assert n>=0
                final_count+=1
                if idx not in cohorts:
                    unmatched+=1
                    continue
                key,tb=cohorts[idx]
                pr=panels[key]
                sr=steps[key[0]]
                dt=exact64(sr["dt_s"])
                t1=exact64(sr["t1_s"])
                tf=exact64(row["final_time_s"])
                age=exact64(row["age_s"])
                age_real=tf-exact64(tb)
                max_final_clock_defect=max(max_final_clock_defect,abs(age-age_real))
                lower=tf-t1+dt*exact64(pr["left_x"])
                upper=tf-t1+dt*exact64(pr["right_x"])
                assert lower<=age<=upper,("final clock outside recorded birth panel",idx)
                width=exact64(pr["nominal_width_s"])
                total+=n;weighted+=n*width
                represented_weighted+=n*exact64(pr["represented_width_s"])
                if n>0:positive+=1
                else:zero+=1
        assert unmatched==0,("initial cohorts lack birth-panel IDs",unmatched)
        assert final_count==len(cohorts),(final_count,len(cohorts))
        width_native=weighted/total if total else None
        represented_width_native=represented_weighted/total if total else None
    assert not failures,failures[:3]
    for name,digest in hashes.items():
        assert sha(monitor/name)==digest,("input changed",name)
    outdir.mkdir(parents=True,exist_ok=True)
    write_csv(outdir/"NATIVE_PANEL_DECIMAL90.csv",panel_refs)
    write_csv(outdir/"NATIVE_PANEL_COMPOSITION.csv",composition)
    receipt={"schema":"BR05_NATIVE_PANEL_DECIMAL90_VERIFICATION_V1","status":"PASS",
      "created_utc":datetime.now(timezone.utc).isoformat(),"python":sys.version,
      "script_sha256":sha(Path(__file__)),"helper_sha256":sha(Path(__file__).with_name("verify_panel_math.py")),
      "input_directory":str(monitor.resolve()),"input_sha256":hashes,
      "elapsed_s":time.monotonic()-started,"decimal_precision":90,
      "steps":len(steps),"unique_step_rules":len(rules),"panels":len(panels),
      "unique_rule_nodes":len(nodes),"birth_rows":birth_count,"templates":len(template_ids),
      "certificate_field_comparisons":checks,"max_certificate_absolute_errors":{k:str(v) for k,v in maxima.items()},
      "final_cohorts":final_count,"final_positive_cohorts":positive,"final_zero_cohorts":zero,
      "unmatched_initial_cohorts":unmatched,"final_count_com3":str(total),
      "final_native_mass_weighted_nominal_panel_width_s":str(width_native) if width_native is not None else None,
      "final_native_mass_weighted_represented_panel_width_s":str(represented_width_native) if represented_width_native is not None else None,
      "max_final_clock_roundoff_s":str(max_final_clock_defect),
      "admissible_scope":"Independent local frozen-kernel certificates, exact-represented panel composition/TV, support membership and final actual retained-width statistic.",
      "not_claimed":["Native gas absolute-error certificate","Source/Verner/Killing correctness (separate root audit)","Outer S10 adaptive-trial monitoring","New dynamics execution by this checker"],
      "failures":failures}
    (outdir/"NATIVE_PANEL_VERIFICATION.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({k:receipt[k] for k in ["status","steps","unique_step_rules","panels","birth_rows","certificate_field_comparisons","final_native_mass_weighted_nominal_panel_width_s"]}),flush=True)
    return receipt

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--monitor-dir",type=Path,required=True)
    ap.add_argument("--out-dir",type=Path,required=True)
    args=ap.parse_args()
    try:
        check(args.monitor_dir,args.out_dir)
    except Exception as exc:
        args.out_dir.mkdir(parents=True,exist_ok=True)
        path=args.out_dir/"UNEXPECTED_VERIFICATION_FAILURE.json"
        if path.exists():
            path=args.out_dir/("UNEXPECTED_VERIFICATION_FAILURE_"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")+".json")
        path.write_text(json.dumps({"status":"FAIL","created_utc":datetime.now(timezone.utc).isoformat(),
          "exception":repr(exc),"traceback":traceback.format_exc(),
          "scope":"Independent read-only monitor analysis; no solver result changed"},indent=2)+"\n")
        raise

