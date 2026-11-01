#!/usr/bin/env python3
"""Source-authentic F05 original tick160->161 NONAUTHORITATIVE physical state preview.

Runs the original unchanged 26-event MPRK22(1)+Alexander SDIRK2 native full,
half1 and half2 maps. Reuses the successful PR350 M-matrix residual enclosure
ONLY as a separately labelled candidate error estimator, not as owner admission.
Outputs real 46080-cell H/He/T/electron previews; never writes .state/REIADP1,
modifies original worker, marks official acceptance, or continues at tick162.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,importlib.util,io,json,sys
from pathlib import Path
import numpy as np

FROZEN_SOURCE_TAR="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
FROZEN_STATE="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
FROZEN_KERNEL="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
ORIGINAL_FAIL=2.1245050576368385e-4
ORIGINAL_GATE=2e-4
WIDTH_GATE=2e-3
N=46080
CHANNELS=("x_HII","x_HeII","x_HeIII","log_T")

def load(name,path):
    sp=importlib.util.spec_from_file_location(name,str(path))
    if sp is None or sp.loader is None:raise FileNotFoundError(path)
    module=importlib.util.module_from_spec(sp)
    sys.modules[name]=module
    sp.loader.exec_module(module)
    return module

def digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()

def interval_cols(name,q):
    lo=np.asarray(q.lo,dtype=np.float64)
    hi=np.asarray(q.hi,dtype=np.float64)
    if lo.shape!=(N,) or hi.shape!=(N,) or np.any(lo>hi):
        raise ArithmeticError("PREVIEW_INTERVAL_INVALID_"+name)
    if not np.isfinite(lo).all() or not np.isfinite(hi).all():
        raise ArithmeticError("PREVIEW_INTERVAL_NONFINITE_"+name)
    return {name+"_lower":lo,name+"_upper":hi}

def write_csv(path,fields):
    assert all(np.asarray(x).shape==(N,) for x in fields.values())
    with Path(path).open("wb") as stream:
        with gzip.GzipFile(fileobj=stream,filename="",mode="wb",
                           compresslevel=6,mtime=0) as gz:
            with io.TextIOWrapper(gz,encoding="utf-8",newline="") as txt:
                writer=csv.writer(txt)
                writer.writerow(["node",*fields])
                for i in range(N):
                    writer.writerow([i,*[format(float(x[i]),".17g") for x in fields.values()]])
    return digest(path)

def run(repo,lane,out):
    repo=Path(repo).resolve()
    out=Path(out).resolve()
    out.mkdir(parents=True,exist_ok=False)
    old=load("rei_f05_owner_preview_p350",repo/"research/rei_f05_mmatrix_residual_20261101/residual_certificate.py")
    orig=old.load_original()
    if lane not in orig.LANES:raise ValueError("UNEXPECTED_ORIGINAL_LANE")
    captured={}
    previous_map=orig.original_map
    previous_increment=orig.krawczyk_increment
    def traced_original_map(m,model,base,label,pop,logt,t0,t1,nh,nhe):
        step,delta,receipt=previous_map(m,model,base,label,pop,logt,t0,t1,nh,nhe)
        if label=="full":
            captured.update(parent_pop=pop,parent_logt=logt,nh=nh,nhe=nhe,module=m,
                            start_clock=float(t0),end_clock=float(t1))
        if label in ("half1","half2"):
            captured[label+"_delta"]=delta
        if label=="half2":
            captured["final_step"]=step
        return step,delta,receipt
    orig.original_map=traced_original_map
    def certified(m,parent,flux,den,dt,nh,nhe):
        return old.structural_residual_increment(m,parent,flux,den,dt,nh,nhe,orig)
    orig.krawczyk_increment=certified
    try:
        # EXACT original stage, source archive and kernel; unchanged native maps.
        r=orig.run(repo,lane,out)
    finally:
        orig.original_map=previous_map
        orig.krawczyk_increment=previous_increment
    required=(r["status"]=="SCOPED_SOURCE_REAL_F05_INCREMENT_GATE_CANDIDATE_PASS"
              and r["original_nodes"]==N
              and r["frozen_original_archive_sha256"]==FROZEN_SOURCE_TAR
              and r["original_state_array_sha256"]==FROZEN_STATE
              and r["original_26event_kernel_sha256"]==FROZEN_KERNEL
              and r["original_local_error_gate"]==ORIGINAL_GATE
              and r["original_public_width_gate"]==WIDTH_GATE
              and r["historical_crossbox_logT_check"]>ORIGINAL_GATE
              and r["original_native_table_event_pass"]
              and r["original_public_width_pass"]
              and r["original_set_ledgers"]["passed"]
              and r["original_set_ledgers"]["evaluated_ledgers"]==14
              and r["all_original_4_channel_local_defects_below_gate"]
              and set(r["steps"])=={"full","half1","half2"})
    if not required or not all(r["increment_defect_coordinates"][c]["nodes_below_unchanged_2eMinus4"]==N
                               for c in CHANNELS):
        raise ArithmeticError("ORIGINAL_NATIVE_OR_ALTERNATIVE_GATE_NOT_SATISFIED")
    s=captured["final_step"]
    m=captured["module"]
    P=captured["parent_pop"]
    Z=captured["parent_logt"]
    nh=np.asarray(captured["nh"])
    nhe=np.asarray(captured["nhe"])
    if s.classification!="PASS" or not s.certified:
        raise ArithmeticError("SECOND_HALF_NATIVE_MAP_NOT_CERTIFIED")
    if not all(r["steps"][label]["original_table_event_count"]==0
               for label in ("full","half1","half2")):
        raise ArithmeticError("ACTUAL_ORIGINAL_TABLE_EVENT")
    p=s.population
    z=s.log_temperature
    if any(np.asarray(v).shape!=(N,) for v in (z.lo,z.hi,nh,nhe)):
        raise ValueError("ORIGINAL_PREVIEW_STATE_SHAPE")
    if np.any(p.lo<=0) or np.any(p.lo>p.hi) or np.any(z.lo>z.hi):
        raise ArithmeticError("PREVIEW_STATE_PHYSICAL_CONE")
    ne0=m._I(P.lo[:,1],P.hi[:,1])+m._I(P.lo[:,3],P.hi[:,3])+2*m._I(P.lo[:,4],P.hi[:,4])
    ne1=m._I(p.lo[:,1],p.hi[:,1])+m._I(p.lo[:,3],p.hi[:,3])+2*m._I(p.lo[:,4],p.hi[:,4])
    x_old=m._I(P.lo[:,1],P.hi[:,1])/m._I(nh)
    xh=m._I(p.lo[:,1],p.hi[:,1])/m._I(nh)
    xhe1=m._I(p.lo[:,3],p.hi[:,3])/m._I(nhe)
    xhe2=m._I(p.lo[:,4],p.hi[:,4])/m._I(nhe)
    temp0=m.iv.exp(Z)
    temp1=m.iv.exp(z)
    ep0=m._I(nh+nhe)+ne0
    ep1=m._I(nh+nhe)+ne1
    heat=1.5*m.KB*ep1*temp1
    d1=captured["half1_delta"]
    d2=captured["half2_delta"]
    delta={name:d1[name]+d2[name] for name in CHANNELS}
    dne=(delta["x_HII"]*m._I(nh)
         +delta["x_HeII"]*m._I(nhe)
         +2*delta["x_HeIII"]*m._I(nhe))
    cols={}
    for key,q in (
      ("source_H_nuclei_N",m._I(nh)),
      ("source_He_nuclei_N",m._I(nhe)),
      ("tick160_xHII",x_old),
      ("tick161_preview_xHII",xh),
      ("tick161_preview_xHeII",xhe1),
      ("tick161_preview_xHeIII",xhe2),
      ("tick160_Tgas_K",temp0),
      ("tick161_preview_Tgas_K",temp1),
      ("tick160_electron_count_N",ne0),
      ("tick161_preview_electron_count_N",ne1),
      ("tick161_preview_U_erg",heat),
      ("tick160_to_161_delta_logT",delta["log_T"]),
      ("tick160_to_161_delta_electron_N",dne)):
        cols.update(interval_cols(key,q))
    path=out/"ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz"
    csv_sha=write_csv(path,cols)
    # Internal preview arrays cannot be mistaken for the original REIADP1
    # accepted-state format by the source-owner loader.
    preview=out/"PREVIEW_NONAUTHORITATIVE_TICK161.npz"
    with preview.open("wb") as f:
        np.savez_compressed(f,population_lower=p.lo,population_upper=p.hi,
             log_temperature_lower=z.lo,log_temperature_upper=z.hi,
             parent_log_temperature_lower=Z.lo,parent_log_temperature_upper=Z.hi)
    with preview.open("rb") as f:
        if f.read(8)==b"REIADP1\x00":
            raise ArithmeticError("UNAPPROVED_REIADP1_STATE_FORMAT_FORBIDDEN")
    pop_sums={"h_source_nuclei":float(np.sum(nh)),
          "he_source_nuclei":float(np.sum(nhe)),
          "electron_count_N_lower":float(np.sum(ne1.lo)),
          "electron_count_N_upper":float(np.sum(ne1.hi)),
          "gas_energy_erg_lower":float(np.sum(heat.lo)),
          "gas_energy_erg_upper":float(np.sum(heat.hi)),
          "Tgas_min_K":float(np.min(temp1.lo)),
          "Tgas_max_K":float(np.max(temp1.hi)),
          "xHII_min":float(np.min(xh.lo)),
          "xHII_max":float(np.max(xh.hi)),
          "xHeII_min":float(np.min(xhe1.lo)),
          "xHeII_max":float(np.max(xhe1.hi)),
          "xHeIII_min":float(np.min(xhe2.lo)),
          "xHeIII_max":float(np.max(xhe2.hi)),
          "delta_logT_max_abs_upper":float(np.max(orig.interval_upper(delta["log_T"]))),
          "delta_electron_N_total_lower":float(np.sum(dne.lo)),
          "delta_electron_N_total_upper":float(np.sum(dne.hi))}
    if not all(np.isfinite(x) for x in pop_sums.values()):
        raise ArithmeticError("NONFINITE_PHYSICAL_SOURCE_OBSERVABLE")
    report={
      "schema":"ORIGINAL_REI_F05_TICK161_REAL_SOURCE_NONAUTHORITATIVE_PREVIEW_V1",
      "source_git_parent_pr":350,
      "immutable_parent_head":"38e32c7b23683930e788696bb65e923819678aac",
      "original_source_tar_sha256":FROZEN_SOURCE_TAR,
      "original_accepted_state_array_sha256":FROZEN_STATE,
      "original_kernel_sha256":FROZEN_KERNEL,
      "original_tick":"160/131072",
      "target_preview_tick":"161/131072",
      "actual_original_spatial_cells":N,
      "source_shape_lane":lane,
      "same_physical_input_across_shape_lanes":True,
      "native_maps":"ORIGINAL_FULL_HALF1_HALF2",
      "native_original_map_status":{k:r["steps"][k]["status"] for k in ("full","half1","half2")},
      "candidate_local_error":"M_MATRIX_RESIDUAL_INCREMENTS",
      "candidate_local_defect_upper":{k:r["increment_defect_coordinates"][k]["max_correlated_increment_defect_upper"] for k in CHANNELS},
      "original_historical_independent_logT_fail":r["historical_crossbox_logT_check"],
      "original_native_public_width_max":r["original_output_max_public_width"],
      "source_original_14_ledger_pass":r["original_set_ledgers"]["passed"],
      "source_original_table_event_pass":r["original_native_table_event_pass"],
      "frozen_gate_2eMinus4_candidate":True,
      "original_worker_acceptance_method":"INDEPENDENT_FULL_VS_TWOHALF_ENDPOINT_BOX",
      "original_worker_acceptance":"UNCHANGED_HISTORICAL_FAILURE",
      "official_state_161":"NOT_ACCEPTED_OR_WRITTEN",
      "published_npz_is_unapproved_not_REIADP1":True,
      "csv_physical_columns":len(cols)+1,
      "csv_physical_rows":N,
      "physical_csv_file":path.name,
      "physical_csv_sha256":csv_sha,
      "preview_state_file":preview.name,
      "preview_state_sha256":digest(preview),
      "observables":pop_sums,
      "central_DAG":"28/88_REPORTED",
      "working_DAG":"33/88_REPORTED",
      "physical_fast_DAG":"4/7_REPORTED",
      "canonical_delta":0,
      "production":"HOLD",
      "authorization":"NONAUTHORITATIVE_SCIENCE_ONLY",
      "claim_kind":"SOURCE_CONDITIONAL_NATIVE_DISCRETE_PHYSICS_NOT_CONTINUUM_IVP_PROOF",
      "original_owner_modified":False
    }
    (out/"PREVIEW_RESULT.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:report[k] for k in ("source_shape_lane",
      "physical_csv_sha256","preview_state_sha256","candidate_local_defect_upper",
      "official_state_161","central_DAG","canonical_delta")},sort_keys=True),flush=True)
    print("ORIGINAL_NATIVE_PREVIEW_OBSERVABLES",json.dumps(pop_sums,sort_keys=True),flush=True)
    return report

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--repo",type=Path,required=True)
    parser.add_argument("--lane",required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    run(args.repo,args.lane,args.out)