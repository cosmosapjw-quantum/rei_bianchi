#!/usr/bin/env python3
"""Read-only reconstruction of original four sealed RUN13 endpoints.
Original source/input bytes are copied unchanged into an isolated selected root.
Only original endpoint readers, SpectralModel construction and observables are
called. No integration, native process, tests, or source repair is performed.
"""
from pathlib import Path, PurePosixPath
import argparse
import datetime
from decimal import Decimal, localcontext
import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback


def ident(path):
    data=path.read_bytes()
    return {"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),
            "git_blob_sha1":hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()}


def write_new(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("xb") as f:
        f.write(data);f.flush();os.fsync(f.fileno())


def dump(path, value):
    write_new(path,(json.dumps(value,indent=2,allow_nan=False)+"\n").encode())


def ledger_contrast(a,b):
    names=("P", "HI", "HeI", "HeII", "DI", "B")
    terms=[b[k]-a[k] for k in names[:-1]]+[-(b["B"]-a["B"])]
    lhs=math.fsum(terms)
    rhs=math.fsum((b["R"],-a["R"]))
    with localcontext() as context:
        context.prec=100
        D=lambda x: Decimal.from_float(x)
        ra=sum((D(a[k]) for k in names[:-1]),Decimal(0))-D(a["B"])
        rb=sum((D(b[k]) for k in names[:-1]),Decimal(0))-D(b["B"])
        dleft=sum((D(b[k])-D(a[k]) for k in names[:-1]),Decimal(0))-(D(b["B"])-D(a["B"]))
        dright=rb-ra
        exact_defect=dleft-dright
    return {"fsum_delta_P_plus_delta_A_minus_delta_B":lhs,
            "fsum_delta_signed_residual":rhs,"fsum_identity_roundoff":lhs-rhs,
            "decimal100_identity_defect_from_exact_float_primaries":str(exact_defect),
            "scope":"Algebraic signed-ledger consistency on the saved finite state; no spectral or ODE error bound"}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-root",type=Path,required=True)
    ap.add_argument("--out-root",type=Path,required=True)
    ap.add_argument("--native-binary",type=Path,required=True,help="Identity record only; no native process is launched")
    args=ap.parse_args()
    src=args.source_root.resolve();out=args.out_root.resolve()
    if out.exists():
        raise ValueError("output must be a new directory")
    if src==out or src in out.parents:
        raise ValueError("output must be outside immutable source root")
    out.mkdir(parents=True)
    copy=out/"source_copy"
    report={"schema":"rei.run13.post_loss_saved_endpoint_reconstruction.v1","status":"IN_PROGRESS",
            "started_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "source_root":str(src),"copy_root":str(copy),"invocation":[sys.executable,*sys.argv],
            "script_identity":ident(Path(__file__)),"source_head":"3dcb5f7aed8d33ff64f7952e9465f4239a216c89",
            "fresh_IVP_runs":0,"fresh_native_processes":0,"fresh_test_suite_runs":0,
            "scope":"Original sealed endpoints reconstructed with unchanged original physical owner code; no IVP reruns"}
    started=time.perf_counter()
    try:
        if any(os.environ.get(k)!="1" for k in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS")):
            raise ValueError("single-thread numerical controls must be present before Python startup")
        if not sys.dont_write_bytecode:
            raise ValueError("Python -B required to protect original source inventory")
        manifest_path=src/"SHA256SUMS.txt"
        sealed={}
        for line in manifest_path.read_text().splitlines():
            digest,name=line[:64],line[66:]
            if name in sealed or len(digest)!=64:
                raise ValueError("invalid sealed source manifest")
            sealed[name]=digest
        report["original_manifest_identity"]=ident(manifest_path)
        report["native_binary_identity"]=ident(args.native_binary)
        if report["native_binary_identity"]["sha256"]!="3454e9e401560df188c7410de29d0712c4afe235e9899021e5314766ab778c8b":
            raise ValueError("associated original native binary differs")
        report["native_binary_used_for_reconstruction"]=False
        names=[
            "scripts/spectral_joint11.py","scripts/retarded_integrator.py",
            "scripts/gas_integrator_parent.py","scripts/run13_endpoint_guard.py",
            "inputs/source_table.py","inputs/bass164/PRODUCER_RECEIPT.json",
            "inputs/bass164/PROPOSED_REI_BACKGROUND.csv","provenance/RUN11_SHA256SUMS.txt",
            "inputs/spectral11/m1.json","inputs/spectral11/m2.json",
            "inputs/spectral11/m1_events.json","inputs/spectral11/m2_events.json"]
        for m in (1,2):
            for tol in ("3e-11","6e-12"):
                folder=f"evidence/joint11_sided_m{m}_{tol}"
                names.extend((folder+"/endpoint.npz",folder+"/result.json"))
                if m==2:
                    rec=json.loads((src/(folder+"/checkpoint.json")).read_bytes())
                    state_name=rec["state_file"]
                    if Path(state_name).name!=state_name:
                        raise ValueError("unsafe stored state filename")
                    names.extend((folder+"/checkpoint.json",folder+"/"+state_name))
        names=sorted(set(names))
        copies=[]
        for name in names:
            if PurePosixPath(name).is_absolute() or ".." in PurePosixPath(name).parts:
                raise ValueError("copy path escape")
            original=src/name
            if original.is_symlink():
                raise ValueError("symlink source")
            original_identity=ident(original)
            if original_identity["sha256"]!=sealed[name]:
                raise ValueError("selected source/input not sealed: "+name)
            write_new(copy/name,original.read_bytes())
            if ident(copy/name)!=original_identity:
                raise ValueError("source copy changed bytes")
            copies.append({"path":name,**original_identity,"original_manifest_matches":True,"copy_bytes_match":True})
        dump(out/"EXACT_SELECTED_SOURCE_COPY_MANIFEST.json",{"files":copies,"file_count":len(copies),"source_manifest_identity":report["original_manifest_identity"]})
        sys.path.insert(0,str(copy/"scripts"))
        import numpy as np
        import scipy
        import retarded_integrator as retarded
        import spectral_joint11 as spectral
        from run13_endpoint_guard import load_complete,load_sealed_parent
        if retarded.ROOT!=copy or spectral.R!=copy:
            raise ValueError("original modules did not resolve their isolated copy root")
        report["runtime"]={"python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__,
                           "platform":platform.platform(),"threads":{k:os.environ[k] for k in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS")}}
        report["path_binding"]={"retarded_ROOT":str(retarded.ROOT),"spectral_R":str(spectral.R),
             "physical_source_files_modified":False,"binding_method":"Original __file__-relative paths resolve in unchanged source copy; no producer absolute path rewritten"}
        cases={}
        ledgers={}
        for m in (1,2):
            for tol in (3e-11,6e-12):
                label=f"m{m}_{tol:.0e}"
                if m==1:
                    rec,y=load_sealed_parent(copy,m,tol,copy/"provenance/RUN11_SHA256SUMS.txt")
                    evidence_form="SEALED_RUN11_PARENT_MANIFEST"
                else:
                    rec,y=load_complete(copy,m,tol)
                    evidence_form="COMPLETE_GENERATION_STATE_AND_ENDPOINT_PROTOCOL"
                packet=json.loads((copy/f"inputs/spectral11/m{m}.json").read_bytes())
                model=spectral.SpectralModel(spectral.coalesce_reflections(packet))
                reconstructed=model.observables(y)
                if model.calls!=0 or model.server is not None:
                    raise ValueError("unexpected RHS activity during endpoint reconstruction")
                old=rec["observable"]
                if len(old)!=21 or set(old)!=set(reconstructed):
                    raise ValueError("original observable inventory differs")
                comparisons=[{"quantity":k,"archived":old[k],"reconstructed":reconstructed[k],
                              "exact_float_equal":old[k]==reconstructed[k],"absolute_delta":reconstructed[k]-old[k]}
                             for k in old]
                if not all(row["exact_float_equal"] for row in comparisons):
                    raise ValueError("original observable reconstruction mismatch: "+label)
                normal_pop=model.B*np.exp(-y[27:model.p])
                scale=model.nh*model.a0**3
                primaries={"P":math.fsum(float(v) for v in normal_pop)*scale,
                           **{s:float(y[model.p+i]*scale) for i,s in enumerate(("HI","HeI","HeII","DI"))},
                           "B":math.fsum(float(v) for v in model.B)*scale}
                primaries["R"]=math.fsum([primaries[k] for k in ("P","HI","HeI","HeII","DI")]+[-primaries["B"]])
                ledgers[label]=primaries
                energy=model.rays(1.,model.m)[0]
                pop=normal_pop*model.nh*model.a0**3
                first=model.coh[:,7]==0
                sub=first&(energy<13.6)
                cases[label]={"status":"COMPLETE_SAVED_ENDPOINT_RECONSTRUCTED","m":m,"requested_rtol":tol,
                              "evidence_form":evidence_form,"dimension":model.dim,
                              "event_intervals":rec["next_segment"],"archived_physical_cohorts":rec["physical_cohorts"],
                              "matched_observables":21,"comparisons":comparisons,"observables":reconstructed,
                              "signed_ledger_fsum_primaries_com3":primaries,
                              "sub_H_fit_first_cell_survivor_com3_numpy":float(pop[sub].sum()),
                              "sub_H_fit_first_cell_survivor_com3_fsum":math.fsum(float(v) for v in pop[sub]),
                              "sub_H_fit_energy_edge_eV":13.6,"model_rhs_calls":model.calls,
                              "fresh_IVP_runs":0,"native_processes":0}
        report["cases"]=cases
        report["signed_ledger_contrasts"]={
          "m2_tight_minus_standard":ledger_contrast(ledgers["m2_3e-11"],ledgers["m2_6e-12"]),
          "tight_m2_minus_m1":ledger_contrast(ledgers["m1_6e-12"],ledgers["m2_6e-12"]),
          "standard_m2_minus_m1":ledger_contrast(ledgers["m1_3e-11"],ledgers["m2_3e-11"])}
        a=cases["m1_3e-11"]["sub_H_fit_first_cell_survivor_com3_numpy"]
        b=cases["m2_3e-11"]["sub_H_fit_first_cell_survivor_com3_numpy"]
        report["sub_H_fit_m2_relative_difference"]=(b-a)/b
        report["spectral_continuum_bound"]="NOT_ESTABLISHED"
        for row in copies:
            if ident(src/row["path"])["sha256"]!=row["sha256"] or ident(copy/row["path"])["sha256"]!=row["sha256"]:
                raise ValueError("original or copied owner/input bytes changed during reader execution")
        actual_inventory={p.relative_to(src).as_posix() for p in src.rglob("*") if p.is_file()}
        if actual_inventory!=set(sealed)|{"SHA256SUMS.txt"}:
            raise ValueError("original333 inventory changed")
        report.update(status="IMPLEMENTATION_VERIFIED",completed_cases_reconstructed=4,
                      original_observables_exactly_matched=84,selected_source_input_copies=len(copies),
                      original_selected_source_and_input_bytes_unchanged=True,original333_inventory_unchanged=True,
                      source_semantics="Original native-provider/geometry/initial-packet/observable definitions retained")
    except Exception as exc:
        report.update(status="FAILED_OR_BLOCKED",error_type=type(exc).__name__,error=str(exc),traceback=traceback.format_exc())
    finally:
        report.update(completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),wall_s=time.perf_counter()-started)
        dump(out/"POST_LOSS_SAVED_ENDPOINT_84_RECEIPT.json",report)
    print(json.dumps({"status":report["status"],"matched_original_observables":report.get("original_observables_exactly_matched",0),
                      "sub_H_fit_m2_relative_difference":report.get("sub_H_fit_m2_relative_difference"),
                      "receipt":str(out/"POST_LOSS_SAVED_ENDPOINT_84_RECEIPT.json"),"error":report.get("error")},indent=2))
    return 0 if report["status"]=="IMPLEMENTATION_VERIFIED" else 1


if __name__=="__main__":
    raise SystemExit(main())
