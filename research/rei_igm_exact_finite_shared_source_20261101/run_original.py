#!/usr/bin/env python3
"""Original 26-event frozen-owner 46080-node SOURCE-ONLY exact finite quotient study."""
from __future__ import annotations
import argparse,csv,gzip,hashlib,importlib.util,io,json,sys
from pathlib import Path
import numpy as np
from finite_source import source_response, EV_ERG

SRC="research/rei_igm_tick160_global_photon_20261101/photon_global_feedback.py"
ARCHIVE_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
STATE_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
ORIGINAL_KERNEL_BLOB="ca2676c84b3c93766c59aa3ef81740565226dad9"
INDICES=(0,2,3)

def parent_source(repo):
    path=repo/SRC
    spec=importlib.util.spec_from_file_location("original_verified_three_moment_owner",path)
    if spec is None or spec.loader is None:raise ImportError(path)
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    if m.SOURCE_SHA!=ARCHIVE_SHA or m.STATE_SHA!=STATE_SHA or m.KERNEL_BLOB!=ORIGINAL_KERNEL_BLOB:
        raise ValueError("PR332 frozen source identity changed")
    return m

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return h.hexdigest()

def floatv(x):
    return float(0.5*(np.asarray(x.lo)+np.asarray(x.hi))) if hasattr(x,"lo") else float(x)

def output(repo,out):
    repo=repo.resolve();out=out.resolve();out.mkdir(parents=True,exist_ok=True)
    src=parent_source(repo)
    source,mod,model,pop0,pop1,frozen,t=src.context(repo)
    if len(pop0)!=46080:raise ValueError("SOURCE_NODE_COUNT")
    forcing=model.forcing_bounds(t,t)
    c=src.coefficients(model,mod,floatv(forcing.z))
    j=np.asarray([floatv(x) for x in forcing.current],float)
    e=np.asarray([floatv(x) for x in forcing.external_subgrid],float)
    q=np.asarray(model.excess_eV,dtype=float)
    r=source_response(pop0[:,INDICES],pop1[:,INDICES],
      frozen["lo"][:,INDICES],frozen["hi"][:,INDICES],c,e,j,q)
    _,sc0,original0,_,_,_,_=src.do_case(mod,model,"same_clock_original_initial",pop0,pop0,pop0,t)
    _,sc1,original1,_,_,_,_=src.do_case(mod,model,"same_clock_original_accepted",pop1,frozen["lo"],frozen["hi"],t)
    # Source owner independent implementation: original _explicit_photo_fields and its heating
    # are checked by do_case; this new finite-source code matches its nodewise photo rates.
    for tag,our,orig in (("initial",r["initial_photo_events_per_s"],original0),
                         ("accepted",r["accepted_photo_events_per_s"],original1)):
        if not np.allclose(our,orig,rtol=8e-12,atol=1e-25):
            raise AssertionError("original 26-event nodewise photo-owner mismatch "+tag)
    hz0=float(np.sum(r["initial_photoheat_erg_per_s"]))
    hz1=float(np.sum(r["accepted_photoheat_erg_per_s"]))
    if not np.isclose(hz0,sc0["source_photoheat_erg_per_s"],rtol=8e-12,atol=0):
        raise AssertionError("original photoheat initial owner mismatch")
    if not np.isclose(hz1,sc1["source_photoheat_erg_per_s"],rtol=8e-12,atol=0):
        raise AssertionError("original photoheat accepted owner mismatch")
    changed=r["change_photo_events_per_s"]
    linear=r["linear_change_photo_events_per_s"]
    rem=r["exact_remainder_photo_events_per_s"]
    remB=r["allX_remainder_bound_photo_events_per_s"]
    # A mismatch here fails the entire source physics run, never quietly clipped.
    max_residual=float(np.max(np.abs(changed-linear-rem)))
    max_abs_change=float(np.max(np.abs(changed)))
    if max_residual>4e-11*max(1e-200,max_abs_change):
        raise AssertionError("finite source difference not exactly closed")
    if np.any(np.abs(rem)>remB+1e-12*np.maximum(1e-180,remB)):
        raise AssertionError("accepted source not contained by fixed-forcing all-X remainder")
    cols={}
    for s,name in enumerate(("HI","HeI","HeII")):
        for key,a in (("initial",r["initial_photo_events_per_s"]),("accepted",r["accepted_photo_events_per_s"]),
                      ("delta",changed),("linear",linear),("exact_rem",rem),("allX_outer_rem",remB)):
            cols[f"{name}_{key}_events_per_s"]=a[:,s]
    for key,a in (("initial",r["initial_photoheat_erg_per_s"]),("accepted",r["accepted_photoheat_erg_per_s"]),
                  ("delta",r["accepted_photoheat_erg_per_s"]-r["initial_photoheat_erg_per_s"]),
                  ("linear",r["linear_photoheat_erg_per_s"]),
                  ("exact_rem",r["exact_remainder_photoheat_erg_per_s"]),
                  ("allX_outer_rem",r["allX_remainder_photoheat_bound_erg_per_s"])):
        cols["photoheat_"+key+"_erg_per_s"]=a
    path=out/"SOURCE_EXACT_FINITE_REMAINDER_46080.csv.gz"
    with path.open("wb") as fh:
        with gzip.GzipFile(fileobj=fh,mode="wb",filename="",mtime=0,compresslevel=6) as gz:
            with io.TextIOWrapper(gz,encoding="utf-8",newline="") as text:
                wr=csv.writer(text);wr.writerow(["node",*cols])
                for i in range(len(pop0)):
                    wr.writerow([i,*[format(float(v[i]),".17g") for v in cols.values()]])
    percentiles={name:{str(p):float(np.percentile(arr,p)) for p in (0,5,50,95,100)}
                 for name,arr in cols.items()}
    report=dict(schema="REI_IGM_SOURCE_26EVENT_EXACT_FINITE_MOMENT_REMAINDER_V1",
        original_archive_sha256=ARCHIVE_SHA,state_array_sha256=STATE_SHA,original_kernel_git_blob=ORIGINAL_KERNEL_BLOB,
        input_pr=332,original_accept_tick=160,total_first_interval_ticks=131072,unique_source_nodes=len(pop0),
        new_source_model_node_rows=len(pop0),time_s=t,z=floatv(forcing.z),
        current_photons_per_s=j.tolist(),external_sink_point=e.tolist(),
        source_forcing_intervals=[{"current_lo":float(x.lo),"current_hi":float(x.hi),
                                 "external_lo":float(y.lo),"external_hi":float(y.hi)}
                for x,y in zip(forcing.current,forcing.external_subgrid)],
        source_fixed_forcing_only=True,source_frozen_same_clock_counterfactual=True,
        group_physics=r["group_rows"],original_snapshot_initial=sc0,original_snapshot_accepted=sc1,
        max_46k_source_quotient_residual_events_per_s=max_residual,
        group_photo_events_delta_per_s=np.sum(changed,axis=0).tolist(),
        group_photo_events_linear_per_s=np.sum(linear,axis=0).tolist(),
        group_photo_events_exact_remainder_per_s=np.sum(rem,axis=0).tolist(),
        original_photoheat_delta_erg_per_s=hz1-hz0,
        linear_photoheat_delta_erg_per_s=float(np.sum(r["linear_photoheat_erg_per_s"])),
        exact_nonlinear_photoheat_remainder_erg_per_s=float(np.sum(r["exact_remainder_photoheat_erg_per_s"])),
        source_marginal_allX_box_remainder_bound_erg_per_s=float(np.sum(r["allX_remainder_photoheat_bound_erg_per_s"])),
        nodewise_column_quantiles=percentiles,source_csv=path.name,source_csv_sha256=sha(path),
        method="exact same-clock rational nonlinear source identity; PR332 three shared neutral totals; not whole 26-event time-map Jacobian/remainder",
        validation="old original source per-node flux and original photoheat checked with independent PR332 do_case",
        first_canonical_interval="BLOCKED_MINIMUM_STEP",old_logT_failure=2.1245050576368385e-4,
        original_local_error_gate=2e-4,original_state_width_gate=2e-3,
        central_dag="28/88_REPORTED",working_dag="33/88_REPORTED",physical_fast="4/7_REPORTED",canonical_delta=0,
        native_subagent="NOT_RUN",independent_author="NOT_RUN",production="HOLD",merge=False)
    (out/"RESULT.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("ACTUAL_ORIGINAL_SOURCE_PHYSICS",json.dumps({
      "rows":len(pop0),"groups":len(r["group_rows"]),
      "per_species_delta":report["group_photo_events_delta_per_s"],
      "per_species_exact_second_order":report["group_photo_events_exact_remainder_per_s"],
      "photoheat_delta":hz1-hz0,"photoheat_remainder":report["exact_nonlinear_photoheat_remainder_erg_per_s"],
      "source_csv_sha":report["source_csv_sha256"],"first_interval":"BLOCKED","central_DAG":"28/88"},sort_keys=True),flush=True)
    return report

if __name__=="__main__":
    pa=argparse.ArgumentParser();pa.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[2])
    pa.add_argument("--out",type=Path,required=True);a=pa.parse_args();output(a.repo,a.out)
