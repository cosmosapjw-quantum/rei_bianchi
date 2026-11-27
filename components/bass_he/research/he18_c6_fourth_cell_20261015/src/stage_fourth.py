#!/usr/bin/env python3
"""Stage the fourth warm P01 cell without reusing third-cell error as a scalar.

Exactly two archived-source RHS endpoint evaluations freeze the Hermite reference.
All 4 gas and 2904 photon error radii come from a hash-pinned C5 predecessor.
This only stages a new private runtime; it never writes private inputs to Git.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, shutil
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
INDEX=3
STEP=6250000000
PREV_CERT_SHA="1efa13a863272f44c071e8d774765fbb23ccd19d6ac7d21b61519a3beb87d551"
PREV_OUT_SHA="2ae0683aa7228184bddb3bbc3795962f13d8ba49dacb8c636a5c679443a14f11"
SOURCE_SHA="8c434debdcb66ee499d61f7822980c73c75469bd426839a1597687042b8c78f3"
INPUT_PINS={
 "P01_STATE.npz":"3cbf35cf7910c37083de4c5b9db443c71b272f3877a48f74fb9f852fd70fe2be",
 "emissivity.out":"88743ec9041a47fd12f47bf50a75a06903089e1afd992b5460a4af471249469b"
}
def digest(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def must_sha(p:Path,expected:str):
    if digest(p)!=expected:raise ValueError(f"HASH_PIN_MISMATCH:{p.name}")
def sub(text,old,new,what):
    n=text.count(old)
    if n!=1:raise ValueError(f"PATCH_BASELINE_CHANGED:{what}:{old}:{n}")
    return text.replace(old,new,1)
def patch_assembler(text):
    # Simultaneous substitution prevents source-right colliding with new-left index.
    for old,mark in (("archived_state['states'][:s.n,2]","_CELL_LEFT_"),
                      ("archived_state['states'][:s.n,3]","_CELL_RIGHT_"),
                      ("rows[2]['ne_cm3']","_NE_LEFT_"),
                      ("rows[3]['ne_cm3']","_NE_RIGHT_")):
        text=sub(text,old,mark,"assemble_certificate.py")
    for mark,new in (("_CELL_LEFT_","archived_state['states'][:s.n,3]"),
                     ("_CELL_RIGHT_","archived_state['states'][:s.n,4]"),
                     ("_NE_LEFT_","rows[3]['ne_cm3']"),
                     ("_NE_RIGHT_","rows[4]['ne_cm3']")):
        text=sub(text,mark,new,"assemble_certificate.py")
    for old,new in (
      ("'THIRD_CELL_DYADIC_ENDPOINT_SOURCE_MISMATCH'","'FOURTH_CELL_DYADIC_ENDPOINT_SOURCE_MISMATCH'"),
      ("'HE18_C5'","'HE18_C6'"),
      ("[str(2*h),str(3*h)]","[str(3*h),str(4*h)]"),
      ("'third-cell FIXED_REFERENCE.npz exact dyadic coefficients'","'fourth-cell FIXED_REFERENCE.npz exact dyadic coefficients'")):
        text=sub(text,old,new,"assemble_certificate.py")
    return text
def patch_source(text):
    for old,new in (
      ("return self.global_volume(z+2)","return self.global_volume(z+3)"),
      ("xq=lo(x)+2","xq=lo(x)+3"),
      ("if xq<2 or hi(x)+2>3:","if xq<3 or hi(x)+3>4:"),
      ("'THIRD_CELL_SHEAR_DOMAIN'","'FOURTH_CELL_SHEAR_DOMAIN'"),
      ("bound(0,3*self.h*self.si)","bound(0,4*self.h*self.si)")):
        text=sub(text,old,new,"warm_interval.py")
    return text
def stage(prev:Path, dest:Path):
    prev=prev.resolve()
    if dest.exists() or dest.with_name(dest.name+".partial").exists():
        raise ValueError("REFUSE_OVERWRITE")
    must_sha(prev/"results/THREE_CELL_VALIDATION.json",PREV_CERT_SHA)
    must_sha(prev/"results/THIRD_ENDPOINT_MEMORY.json",PREV_OUT_SHA)
    must_sha(prev/"_c1_private/src/warm_source_reference.py",SOURCE_SHA)
    for name,pin in INPUT_PINS.items():must_sha(prev/"inputs"/name,pin)
    cert=json.loads((prev/"results/THREE_CELL_VALIDATION.json").read_text())
    incoming=json.loads((prev/"results/THIRD_ENDPOINT_MEMORY.json").read_text())
    if cert["status"]!="SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES":
        raise ValueError("PREDECESSOR_NOT_ADMITTED")
    if incoming["source_interval_s"]!=[str(2*STEP),str(3*STEP)]:
        raise ValueError("WRONG_PREVIOUS_TIME_WINDOW")
    ep=incoming["outgoing_photon_error_end_raw_exact"]
    eg=incoming["scaled_gas_error_end_exact"]
    if len(ep)!=2904 or len(eg)!=4:raise ValueError("INCOMPLETE_PREVIOUS_ERRORS")
    from fractions import Fraction as Q
    if any(Q(x)<0 for x in ep+eg):raise ValueError("NEGATIVE_INCOMING_ERROR")
    tmp=dest.with_name(dest.name+".partial")
    try:
        for rel in ("src","checks","results","evidence","inputs","_c1_private/src","_c1_private/inputs"):
            (tmp/rel).mkdir(parents=True,exist_ok=True)
        for name in ("P01_STATE.npz","emissivity.out","P01_INTERVAL.json","HH_P01_COMPARISON.json"):
            shutil.copy2(prev/"inputs"/name,tmp/"inputs"/name)
        for name in INPUT_PINS:
            shutil.copy2(prev/"inputs"/name,tmp/"_c1_private/inputs"/name)
        shutil.copy2(prev/"_c1_private/src/warm_source_reference.py",
                     tmp/"_c1_private/src/warm_source_reference.py")
        for name in ("warm_interval.py","interval_jet.py","run_evaluations.py","assemble_certificate.py"):
            shutil.copy2(prev/"src"/name,tmp/"src"/name)
        carry=dict(gas_error_end_scaled=eg,photon_error_end_raw_exact=ep,
                   source_interval_s=[str(2*STEP),str(3*STEP)],
                   exact_previous_sha256=PREV_OUT_SHA)
        (tmp/"inputs/ENDPOINT_MEMORY_R7.json").write_text(json.dumps(carry,indent=2)+"\n")
        shutil.copy2(prev/"results/THREE_CELL_VALIDATION.json",
                     tmp/"inputs/PREV_THREE_CELL_VALIDATION.json")
        source_p=tmp/"_c1_private/src/warm_source_reference.py"
        spec=importlib.util.spec_from_file_location("pinned_original_warm_P01",source_p)
        mod=importlib.util.module_from_spec(spec);assert spec.loader is not None
        spec.loader.exec_module(mod)
        src=mod.Source()
        t0,t1=src.times[INDEX:INDEX+2]
        if float(t0)!=3*STEP or float(t1)!=4*STEP:raise ValueError("WRONG_SAVED_CELL_INDEX")
        a=np.asarray(src.y[:,INDEX],dtype=np.float64)
        b=np.asarray(src.y[:,INDEX+1],dtype=np.float64)
        assert a.size==b.size==2908
        m0=src.rhs(t0,src.y[:,INDEX])[0].astype(np.float64)
        m1=src.rhs(t1,src.y[:,INDEX+1])[0].astype(np.float64)
        np.savez_compressed(tmp/"inputs/FIXED_REFERENCE.npz",
            left=a,right=b,slope_left=m0,slope_right=m1,h=float(t1-t0))
        w=tmp/"src/warm_interval.py";w.write_text(patch_source(w.read_text()))
        w=tmp/"src/run_evaluations.py"
        w.write_text(sub(w.read_text(),"'HE18_C5'","'HE18_C6'","run_evaluations.py"))
        w=tmp/"src/assemble_certificate.py";w.write_text(patch_assembler(w.read_text()))
        for name in ("propagate_fourth.py","verify_fourth.py"):
            shutil.copy2(ROOT/"checks"/name,tmp/"checks"/name)
        info=dict(stage="HE18_C6_FOURTH_CELL",physical_cell_index=4,
            source_commit=incoming["source_commit"],
            source_ref_sha256=SOURCE_SHA,
            prev_certificate_sha256=PREV_CERT_SHA,
            prev_photon_error_sha256=PREV_OUT_SHA,
            input_sha256=INPUT_PINS,
            frozen_reference_sha256=digest(tmp/"inputs/FIXED_REFERENCE.npz"),
            adapted_incoming_sha256=digest(tmp/"inputs/ENDPOINT_MEMORY_R7.json"),
            cell_s=[str(3*STEP),str(4*STEP)],
            source_rhs_endpoint_calls=2,source_ODE_runs=0,other_repo_mutated=False)
        (tmp/"inputs/STAGED_SOURCE_IDENTITY.json").write_text(json.dumps(info,indent=2)+"\n")
        tmp.rename(dest)
        return info
    except BaseException:
        if tmp.exists():shutil.rmtree(tmp)
        raise
if __name__=="__main__":
    pa=argparse.ArgumentParser()
    pa.add_argument("--previous-runtime",type=Path,required=True)
    pa.add_argument("--output",type=Path,required=True)
    a=pa.parse_args()
    print(json.dumps(stage(a.previous_runtime,a.output),indent=2))
