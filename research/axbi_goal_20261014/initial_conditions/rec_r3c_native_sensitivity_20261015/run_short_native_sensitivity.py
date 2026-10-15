"""Run source-verified fresh REI native short signed q gas sensitivities.

The ORIGINAL REI scenario remains immutable. This script uses only the
selected donor's locked, disabled input under an isolated PR127-derived
experimental branch with the actual chemistry/time-owner fix. No checkpoint
resume or automatic promotion into full production.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import time

ROOT=Path(__file__).resolve().parents[4]
DIR=Path(__file__).resolve().parent
SCENARIO=ROOT/"research/axbi_goal_20261014/scenario/SCENARIO_LOCK.json"
DONOR=DIR/"REI_DONOR_CANDIDATE_OPTIN_ONLY.json"
RUST=ROOT/"rust/rei_microphysics"
EXPECTED_SCENARIO_SHA="07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696"
EXPECTED_DONOR_BLOB="1e3fdd5019f2a9a7d5ccd6a23e2f3a03faf74bd4"
EXPECTED_PARENT="edddcd6ea9a135fcf18c7be8357b5e11fea87407"
EXPECTED_HYREC_NATIVE="6fa5cb83a45ed3599d824ff821b6c8df41dd6d0e78a46cf9b33fde91b933e400"


def _sha(p:Path):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _check_identity():
    scenario=json.loads(SCENARIO.read_text())
    donor=json.loads(DONOR.read_text())
    if _sha(SCENARIO)!=EXPECTED_SCENARIO_SHA:
        raise ValueError("authoritative REI scenario changed")
    source_blob=subprocess.run(["git","hash-object",str(DONOR)],capture_output=True,
                  text=True,check=True).stdout.strip()
    if source_blob!=EXPECTED_DONOR_BLOB:
        raise ValueError("REC->REI donor byte identity mismatch")
    if (donor["activation"]!="DISABLED_REQUIRES_SEPARATE_REI_SENSITIVITY_CAMPAIGN"
        or donor["source_rei_scenario_sha256"]!=EXPECTED_SCENARIO_SHA
        or donor["source_rec_full_C_stdout_sha256"]!=EXPECTED_HYREC_NATIVE
        or donor["adopted_into_original_REI_scenario"]):
        raise ValueError("donor source/identity/adoption changed")
    head=subprocess.run(["git","-C",str(ROOT),"rev-parse","HEAD"],capture_output=True,
                  text=True,check=True).stdout.strip()
    if head!=EXPECTED_PARENT:
        raise ValueError("native code baseline no longer PR127; rederive approval")
    b=scenario["gas_initial"]
    assert b["x_HII"]==.0002 and b["x_HeII"]==b["x_HeIII"]==0
    assert donor["candidate_initial_gas"]["x_HeII"]==0.0
    assert donor["candidate_initial_gas"]["x_HeIII"]==0.0
    return scenario,donor


def _config(case:str,gas:dict,q:float,*,panels=4096,steps=12):
    cfg=[
       f"q_ref={q:.17g}",
       "same_h=false",
       "end_zbar=19.0",
       "escape_fraction=0.2",
       f"initial_temperature_k={gas['Tgas_K']:.17g}",
       f"initial_hii_fraction={gas['x_HII']:.17g}",
       "energy_subdivisions=16",
       "n_mu=8",
       f"background_panels={panels}",
       "local_target=1e-5",
       "initial_dln_a=1e-5",
       f"max_steps={max(1000,steps+1)}",
       f"max_attempts={max(10000,4*steps+1024)}",
       f"max_rhs={max(250000,40*steps)}",
       "max_wall_s=90",
       "spectra_every_accepted=60",
       "output_budget_mib=256",
    ]
    return "\n".join(cfg)+"\n"


def _run(binary:Path,case:str,cfgpath:Path,csvpath:Path,steps:int):
    started=time.perf_counter()
    run=subprocess.run([str(binary),"--config",str(cfgpath),"--output",
              str(csvpath),"--case",case,"--steps",str(steps)],
              cwd=RUST,capture_output=True,text=True,timeout=100,
              env={**os.environ,"OMP_NUM_THREADS":"1","OPENBLAS_NUM_THREADS":"1"})
    elapsed=time.perf_counter()-started
    if run.returncode:
        raise RuntimeError(f"{case} native process exit={run.returncode}: {run.stderr[-2000:]}")
    rows=list(csv.DictReader(csvpath.open()))
    if not (2<=len(rows)<=steps+1):
        raise RuntimeError(f"{case}: invalid actual native history length {len(rows)}")
    if len(rows)<steps+1 and abs(float(rows[-1]["zbar"])-19.0)>1e-10:
        raise RuntimeError(f"{case}: early termination without physical endpoint")
    for k,r in enumerate(rows):
        if int(r["accepted"])!=k:
            raise RuntimeError(f"{case} wrong accepted index at {k}")
        if k>0 and not (float(r["a"])>float(rows[k-1]["a"])):
            raise RuntimeError(f"{case} non-growing mean scale factor")
        if abs(float(r["energy_ledger_eV_per_H"]))>1e-8:
            raise RuntimeError(f"{case} energy ledger failed at {k}")
        if abs(float(r["number_ledger_per_H"]))>1e-8:
            raise RuntimeError(f"{case} photon-number ledger failed at {k}")
    return dict(case=case,sha256=_sha(csvpath),rows=len(rows),
                wall_s=elapsed,stderr=run.stderr.strip(),last=rows[-1],
                data=rows)


def _match_at_shared_scale(left:list,right:list):
    """Interpolate only WITHIN actually covered accepted-scale ranges.

    A common fixed-a diagnostic is separate from a common proper-time
    diagnostic. This interpolation is a time grid comparison, not solver
    truncation or continuum uncertainty certification.
    """
    def interpolate(rows,log_a,key):
        yy=[(math.log(float(r["a"])),float(r[key])) for r in rows]
        if not (yy[0][0]<=log_a<=yy[-1][0]):
            raise ValueError("shared log-a outside sampled history")
        for k in range(len(yy)-1):
            t0,v0=yy[k];t1,v1=yy[k+1]
            if t0<=log_a<=t1:
                f=(log_a-t0)/(t1-t0)
                return (1-f)*v0+f*v1
        return yy[-1][1]
    # Last shared endpoint has both states actually sampled, do not
    # extrapolate one case to another's later clock.
    last=min(float(left[-1]["a"]),float(right[-1]["a"]))
    loglast=math.log(last)
    keys=("xHII","Tgas_K","photon_number_per_H","photon_energy_eV_per_H",
          "time_s","xe_per_H")
    lv={k:interpolate(left,loglast,k) for k in keys}
    rv={k:interpolate(right,loglast,k) for k in keys}
    return {
       "a_shared":last,"zbar_shared":1/last-1,
       "baseline":lv,"donor":rv,
       "donor_minus_baseline":{k:rv[k]-lv[k] for k in keys},
       "mapping":"piecewise linear interpolation in ln(a), within common sampled support",
       "matched_proper_time":False
    }


def run(outdir:Path,steps:int=12,workers:int=2,panels:int=4096):
    if not (1<=steps<=8192 and workers in (1,2) and panels in (64,256,4096)):
        raise ValueError("bounded diagnostic only")
    scenario,donor=_check_identity()
    target=Path(os.environ.get("CARGO_TARGET_DIR",
                  "/home/cosmosapjw/rec_theory_runs/REI_HYREC_IC_NATIVE_20261015/target"))
    binary=target/"release/examples/axbi_rec_donor_short"
    if not binary.is_file():
        raise FileNotFoundError(f"native Rust source must be built first: {binary}")
    outdir=outdir.resolve()
    outdir.mkdir(parents=True,exist_ok=True)
    orig={
       "x_HII":float(scenario["gas_initial"]["x_HII"]),
       "Tgas_K":2.7255*21**2/(150*(.0224/.023)**.4)
    }
    donor_gas=donor["candidate_initial_gas"]
    cases=[
       ("QZERO_BASELINE",orig,0.0),
       ("QZERO_HYREC",donor_gas,0.0),
       ("QMINUS_BASELINE",orig,-.01),
       ("QMINUS_HYREC",donor_gas,-.01),
       ("QPLUS_BASELINE",orig,.01),
       ("QPLUS_HYREC",donor_gas,.01),
    ]
    jobs=[]
    for case,gas,q in cases:
        path=outdir/(case+".cfg")
        path.write_text(_config(case,gas,q,panels=panels,steps=steps))
        jobs.append((case,path,outdir/(case+".csv")))
    reference=[]
    for case,cfg,csvname in jobs:
        reference.append(_run(binary,case,cfg,csvname,steps))
    ordered_s=sum(r["wall_s"] for r in reference)
    results=[]
    # Independent same compiled source, same source config and isolated paths
    # with a maximum of two native processes, not native LLM subagents.
    for case,cfg,csvname in jobs:
        parname=outdir/(case+".parallel.csv")
        results.append((case,cfg,parname))
    began=time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        compared=list(executor.map(lambda args:_run(binary,*args,steps=steps),results))
    parallel_s=time.perf_counter()-began
    for orig_run,repeat in zip(reference,compared):
        if orig_run["sha256"]!=repeat["sha256"]:
            raise RuntimeError("serial/parallel native output SHA mismatch")
        # Duplicate full history is a validation receipt, not an output we
        # need to keep in VCS. Delete only OUR isolated comparison outputs.
        (outdir/(repeat["case"]+".parallel.csv")).unlink()
    pairs={}
    for key,i,j in [("ZERO",0,1),("MINUS",2,3),("PLUS",4,5)]:
        pairs[key]=_match_at_shared_scale(reference[i]["data"],reference[j]["data"])
    output={
      "schema":"rei.rec.initial_sensitivity.native_short.v1",
      "scope":"actual PR127 corrected local proper-time native REI MD14/BB50K operator, 12+ actual accepted steps per case; NOT entire zbar20-to-4 campaign",
      "source_parent_commit":EXPECTED_PARENT,
      "native_example_sha256":_sha(ROOT/"rust/rei_microphysics/examples/axbi_rec_donor_short.rs"),
      "native_driver_source_sha256":_sha(ROOT/"rust/rei_microphysics/src/axbi_driver.rs"),
      "original_REI_scenario_sha256":EXPECTED_SCENARIO_SHA,
      "original_2012_HyRec_stdout_sha256":EXPECTED_HYREC_NATIVE,
      "donor_blob_id":EXPECTED_DONOR_BLOB,
      "no_production_checkpoint_resumes":True,
      "source_photon_model":"original native MD14/BB50K, fresh astrophysical photon stock zero",
      "helium_conversion":"HyRec x_e->REI HII conditional on neutral helium at zbar20",
      "physical_domain_zbar":[4,20],
      "q_values":[0,-.01,.01],
      "steps":steps,"panels":panels,
      "serial_runs": [
       {k:v for k,v in r.items() if k!="data"}
       for r in reference
      ],
      "identical_parallel_bytes":[a["sha256"]==b["sha256"] for a,b in zip(reference,compared)],
      "serial_wall_sum_s":ordered_s,
      "parallel_workers":workers,
      "parallel_wall_s":parallel_s,
      "parallel_speedup":ordered_s/parallel_s,
      "common_mean_scale_comparisons":pairs,
      "total_a_endpoint_differences_are_not_auto_equality":"paired independent adaptive grids compared only within common physical support",
      "physics_admission":"LOCAL_NATIVE_SOURCE_IC_SENSITIVITY_ONLY",
    }
    (outdir/"RUN_RESULTS.json").write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "passed":True,"steps":steps,"serial_s":ordered_s,"parallel_s":parallel_s,
      "speedup":ordered_s/parallel_s,
      "pairs":{k:{"zbar":v["zbar_shared"],
                    "delta_xHII":v["donor_minus_baseline"]["xHII"],
                    "delta_Tgas_K":v["donor_minus_baseline"]["Tgas_K"],
                    "delta_photons_per_H":v["donor_minus_baseline"]["photon_number_per_H"]}
              for k,v in pairs.items()},
      "source_rows":len(reference[0]["data"]),
    },indent=2))
    return output


if __name__=="__main__":
    import argparse
    a=argparse.ArgumentParser()
    a.add_argument("--output-dir",type=Path,required=True)
    a.add_argument("--steps",type=int,default=12)
    a.add_argument("--workers",type=int,default=2)
    a.add_argument("--panels",type=int,default=4096)
    args=a.parse_args()
    run(args.output_dir,args.steps,args.workers,args.panels)
