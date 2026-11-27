#!/usr/bin/env python3
"""Stage next immutable warm P01 source slab from the previous certified slab.

No ODE integration: two pinned source RHS endpoint evaluations supply a saved
Hermite reference. All four gas and 2904 photon error components are retained.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, shutil, sys
from pathlib import Path
from fractions import Fraction as Q

import numpy as np
if hasattr(sys,"set_int_max_str_digits"):
    sys.set_int_max_str_digits(250000)
STEP=6250000000
SOURCE_SHA="8c434debdcb66ee499d61f7822980c73c75469bd426839a1597687042b8c78f3"
PRIVATE_DATA_SHA={
    "P01_STATE.npz":"3cbf35cf7910c37083de4c5b9db443c71b272f3877a48f74fb9f852fd70fe2be",
    "emissivity.out":"88743ec9041a47fd12f47bf50a75a06903089e1afd992b5460a4af471249469b",
}
WORDS={7:"seven",8:"eight",9:"nine",10:"ten",11:"eleven",12:"twelve",
       13:"thirteen",14:"fourteen",15:"fifteen",16:"sixteen"}
DASH={7:"SEVENTH",8:"EIGHTH",9:"NINTH",10:"TENTH",11:"ELEVENTH",
      12:"TWELFTH",13:"THIRTEENTH",14:"FOURTEENTH",15:"FIFTEENTH",
      16:"SIXTEENTH"}

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def once(s,old,new,field):
    count=s.count(old)
    if count!=1:
        raise ValueError(f"INHERITED_CODE_ANCHOR:{field}:{old!r}:{count}")
    return s.replace(old,new,1)

def simultaneous(s,pairs,field):
    markers=[]
    for i,(old,new) in enumerate(pairs):
        marker=f"__HE18_SHIFT_{field}_{i}__"
        s=once(s,old,marker,field)
        markers.append((marker,new))
    for marker,new in markers:
        s=once(s,marker,new,field)
    return s

def new_warm_interval(s,n):
    p=n-1
    for old,new in (
        (f"return self.global_volume(z+{p-1})",
         f"return self.global_volume(z+{n-1})"),
        (f"xq=lo(x)+{p-1}",f"xq=lo(x)+{n-1}"),
        (f"if xq<{p-1} or hi(x)+{p-1}>{p}:",
         f"if xq<{n-1} or hi(x)+{n-1}>{n}:"),
        (f"'{DASH[p]}_CELL_SHEAR_DOMAIN'",
         f"'{DASH[n]}_CELL_SHEAR_DOMAIN'"),
        (f"bound(0,{p}*self.h*self.si)",
         f"bound(0,{n}*self.h*self.si)"),
    ):
        s=once(s,old,new,"warm_interval")
    return s

def new_assembler(s,n):
    p=n-1
    pairs=[
        (f"archived_state['states'][:s.n,{p-1}]",
         f"archived_state['states'][:s.n,{n-1}]"),
        (f"archived_state['states'][:s.n,{p}]",
         f"archived_state['states'][:s.n,{n}]"),
        (f"rows[{p-1}]['ne_cm3']",f"rows[{n-1}]['ne_cm3']"),
        (f"rows[{p}]['ne_cm3']",f"rows[{n}]['ne_cm3']"),
    ]
    s=simultaneous(s,pairs,"assembler")
    for old,new in (
        (f"'{DASH[p]}_CELL_DYADIC_ENDPOINT_SOURCE_MISMATCH'",
         f"'{DASH[n]}_CELL_DYADIC_ENDPOINT_SOURCE_MISMATCH'"),
        (f"'HE18_C{p+2}'",f"'HE18_C{n+2}'"),
        (f"[str({p-1}*h),str({p}*h)]",
         f"[str({n-1}*h),str({n}*h)]"),
        (f"'{WORDS[p]}th-cell FIXED_REFERENCE.npz exact dyadic coefficients'",
         f"'{WORDS[n]}th-cell FIXED_REFERENCE.npz exact dyadic coefficients'"),
    ):
        # Many inherited labels are irregular English (seven->seventh).
        if "th-cell" in old:
            old=f"'{DASH[p].lower()}-cell FIXED_REFERENCE.npz exact dyadic coefficients'"
            new=f"'{DASH[n].lower()}-cell FIXED_REFERENCE.npz exact dyadic coefficients'"
        s=once(s,old,new,"assemble_certificate")
    return s

def stage(previous:Path,dest:Path,n:int):
    if not 8<=n<=16:raise ValueError("CELL_OUTSIDE_8_TO_16")
    previous=previous.resolve();dest=dest.resolve()
    if dest.exists() or dest.with_name(dest.name+".partial").exists():
        raise ValueError("REFUSE_OVERWRITE_EXISTING_RUNTIME")
    p=n-1
    pc=previous/"results"/f"{WORDS[p].upper()}_CELL_VALIDATION.json"
    pm=previous/"results"/f"{DASH[p]}_ENDPOINT_MEMORY.json"
    if not pc.is_file() or not pm.is_file():
        raise ValueError(f"PREDECESSOR_NOT_DURABLE:{p}")
    prev_c=json.loads(pc.read_text())
    prev_m=json.loads(pm.read_text())
    if prev_c.get("status")!="SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES":
        raise ValueError("PREDECESSOR_NOT_CERTIFIED")
    if prev_c.get("schema")!=f"he18.c{p+2}.{DASH[p].lower()}_cell_exact_review.v1":
        raise ValueError("PREDECESSOR_SCHEMA")
    if prev_m.get("source_interval_s")!=[str((p-1)*STEP),str(p*STEP)]:
        raise ValueError("PREDECESSOR_CLOCK_MISMATCH")
    gas=prev_m.get("scaled_gas_error_end_exact")
    photons=prev_m.get("outgoing_photon_error_end_raw_exact")
    if len(gas or [])!=4 or len(photons or [])!=2904:
        raise ValueError("INCOMPLETE_INCOMING_4_PLUS_2904")
    if any(Q(x)<0 for x in gas+photons):
        raise ValueError("NEGATIVE_PREVIOUS_ERROR")
    source_file=previous/"_c1_private/src/warm_source_reference.py"
    if sha(source_file)!=SOURCE_SHA:raise ValueError("SOURCE_SHA_CHANGED")
    for name,h in PRIVATE_DATA_SHA.items():
        if sha(previous/"inputs"/name)!=h:raise ValueError("ORIGINAL_PRIVATE_INPUT_CHANGED:"+name)
    work=dest.with_name(dest.name+".partial")
    try:
        for sub in ("src","checks","inputs","results","evidence","_c1_private/src","_c1_private/inputs"):
            (work/sub).mkdir(parents=True,exist_ok=True)
        for name in ("P01_STATE.npz","emissivity.out","P01_INTERVAL.json","HH_P01_COMPARISON.json"):
            shutil.copy2(previous/"inputs"/name,work/"inputs"/name)
        for name in PRIVATE_DATA_SHA:
            shutil.copy2(previous/"inputs"/name,work/"_c1_private/inputs"/name)
        shutil.copy2(source_file,work/"_c1_private/src/warm_source_reference.py")
        for name in ("interval_jet.py","run_evaluations.py","warm_interval.py","assemble_certificate.py"):
            shutil.copy2(previous/"src"/name,work/"src"/name)
        shutil.copy2(Path(__file__).parent/"run_parallel.py",work/"src/run_parallel.py")
        runner=work/"src/run_parallel.py"
        runner.write_text(runner.read_text().replace(
            "he18.c9.two_process_evaluation.v1",
            f"he18.c{n+2}.two_process_evaluation.v1",1))

        shutil.copy2(Path(__file__).parent/"admit_cell.py",work/"checks/admit_cell.py")
        carry={
            "gas_error_end_scaled":gas,"photon_error_end_raw_exact":photons,
            "source_interval_s":prev_m["source_interval_s"],
            "exact_previous_sha256":sha(pm),
        }
        (work/"inputs/ENDPOINT_MEMORY_R7.json").write_text(json.dumps(carry,indent=2)+"\n")
        shutil.copy2(pc,work/"inputs/PREV_CELL_VALIDATION.json")
        # Original source is held immutable and queried at *saved* endpoints only.
        spec=importlib.util.spec_from_file_location(f"pinned_P01_{n}",work/"_c1_private/src/warm_source_reference.py")
        mod=importlib.util.module_from_spec(spec);assert spec.loader
        spec.loader.exec_module(mod)
        src=mod.Source()
        t0,t1=src.times[n-1:n+1]
        if float(t0)!=(n-1)*STEP or float(t1)!=n*STEP:
            raise ValueError("NOT_A_SAVED_P01_SLAB")
        y0=np.asarray(src.y[:,n-1],dtype=np.float64)
        y1=np.asarray(src.y[:,n],dtype=np.float64)
        if y0.size!=2908 or y1.size!=2908:
            raise ValueError("WRONG_SOURCE_STATE_DIMENSION")
        m0=np.asarray(src.rhs(t0,src.y[:,n-1])[0],dtype=np.float64)
        m1=np.asarray(src.rhs(t1,src.y[:,n])[0],dtype=np.float64)
        np.savez_compressed(work/"inputs/FIXED_REFERENCE.npz",left=y0,right=y1,
                            slope_left=m0,slope_right=m1,h=float(t1-t0))
        w=work/"src/warm_interval.py";w.write_text(new_warm_interval(w.read_text(),n))
        w=work/"src/assemble_certificate.py";w.write_text(new_assembler(w.read_text(),n))
        w=work/"src/run_evaluations.py"
        w.write_text(once(w.read_text(),f"'HE18_C{p+2}'",f"'HE18_C{n+2}'","run_evaluations"))
        # Only the SHA-pinned private research source may relax Python's
        # integer decimal representation cap; exact Fraction math is unchanged.
        x=work/"src/assemble_certificate.py";s=x.read_text()
        if "set_int_max_str_digits(50000)" in s:
            s=once(s,"set_int_max_str_digits(50000)","set_int_max_str_digits(250000)","trusted_serializer")
        elif s.count("set_int_max_str_digits(250000)")!=1:
            raise ValueError("TRUSTED_SERIALIZATION_CONTRACT_MISSING")
        x.write_text(s)
        meta={
           "schema":"he18.p01_continuation.stage.v1",
           "cell":n,"stage":f"HE18_C{n+2}_{DASH[n]}_CELL",
           "source_commit":prev_m["source_commit"],"source_sha256":SOURCE_SHA,
           "cell_s":[str((n-1)*STEP),str(n*STEP)],
           "prev_cert_sha256":sha(pc),"prev_error_sha256":sha(pm),
           "incoming_adapter_sha256":sha(work/"inputs/ENDPOINT_MEMORY_R7.json"),
           "original_inputs":PRIVATE_DATA_SHA,
           "frozen_hermite_sha256":sha(work/"inputs/FIXED_REFERENCE.npz"),
           "actual_endpoint_RHS_calls":2,"full_source_ODE_runs":0,"all_2904_carried":True,
           "selected_fraction_backend":"memoized exact 16-panel Bernstein",
        }
        (work/"inputs/CONTINUATION_BINDING.json").write_text(json.dumps(meta,indent=2)+"\n")
        work.rename(dest)
        return meta
    except BaseException:
        if work.exists():shutil.rmtree(work)
        raise

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--previous",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    a.add_argument("--cell",type=int,required=True)
    z=a.parse_args()
    print(json.dumps(stage(z.previous,z.output,z.cell),indent=2))
