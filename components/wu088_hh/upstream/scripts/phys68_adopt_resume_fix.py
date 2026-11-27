#!/usr/bin/env python3
"""Adopt the two genuine PHYS68 panels after the bounded serialization-only fix.

This one-purpose migration is not a generic force-resume option.  It requires
the exact recorded old profile implementation, unchanged original definitions
apart from run_profiles, identical remaining engine/runtime/input/request, and
unchanged complete panel payload hashes.  No integral is computed.  The old
directory remains intact and a new directory receives provenance-bound copies.
"""
from __future__ import annotations
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from flint import acb,ctx
from wu088_hh.phys68_profiles import (
    ProfileRequest, SOURCE_SHA, _canonical, _write_json, _verify_boundary_carry,
    complex_ball_record, engine_identity, exact_fraction, pair_name, radial_certificate,
)

OLD_SHA="50878a9198cd8b5cd25b72472f14c7400803ba15257fcc13961d1cbe9c6edb62"
ADDED={"_dyadic_record_fraction","_serialized_box_contains","_verify_boundary_carry"}


def top_level_ast(path):
    result={}
    for i,node in enumerate(ast.parse(path.read_text()).body):
        key=getattr(node,"name",f"statement_{i}")
        # Statements after inserted definitions include only original named
        # functions here; imports/constants preceding them retain their indices.
        result[key]=ast.dump(node,include_attributes=False)
    return result


def adopt(source,oldout,newout,oldcode):
    source,oldout,newout,oldcode=map(Path,(source,oldout,newout,oldcode))
    if hashlib.sha256(oldcode.read_bytes()).hexdigest()!=OLD_SHA:
        raise ValueError("not the exact previously executed source")
    current=ROOT/"src/wu088_hh/phys68_profiles.py"
    old_ast,new_ast=top_level_ast(oldcode),top_level_ast(current)
    # Inserted helpers shift the anonymous ENGINE_FILES statement, so compare
    # all old named definitions and the full anonymous statement sequences.
    old_named={k:v for k,v in old_ast.items() if not k.startswith("statement_")}
    new_named={k:v for k,v in new_ast.items() if not k.startswith("statement_")}
    if set(new_named)-set(old_named)!=ADDED or set(old_named)-set(new_named):
        raise ValueError("unexpected definition changes")
    changed=[k for k in old_named if old_named[k]!=new_named[k]]
    if changed != ["run_profiles"]:
        raise ValueError(f"numerical/profile definitions changed: {changed}")
    old_statements=[v for k,v in old_ast.items() if k.startswith("statement_")]
    new_statements=[v for k,v in new_ast.items() if k.startswith("statement_")]
    if old_statements!=new_statements:
        raise ValueError("imports/constants changed")
    saved=json.loads((oldout/"REQUEST.json").read_text())
    old_binding=saved["binding"]
    if saved["fingerprint"]!=hashlib.sha256(_canonical(old_binding)).hexdigest():
        raise ValueError("old request hash mismatch")
    req=ProfileRequest(**old_binding["request"]).validate()
    if req!=ProfileRequest():
        raise ValueError("migration restricted to the recorded default L28/T65 request")
    radial_certificate(source,req.max_ell,req.outer,2)
    new_engine=engine_identity()
    old_engine=old_binding["engine"]
    if old_binding["source_sha256"]!=SOURCE_SHA:
        raise ValueError("old source mismatch")
    if old_engine["files_sha256"].get("phys68_profiles.py")!=OLD_SHA:
        raise ValueError("old engine does not match preserved source")
    expected=json.loads(json.dumps(old_engine))
    expected["files_sha256"]["phys68_profiles.py"]=new_engine["files_sha256"]["phys68_profiles.py"]
    if expected!=new_engine:
        raise ValueError("another kernel/runtime changed")
    oldcert=json.loads((oldout/"CERTIFICATE.json").read_text())
    if (oldcert.get("fingerprint")!=saved["fingerprint"] or
        oldcert["scientific_execution"]!="PARTIAL_CHECKPOINT" or len(oldcert["panels"])!=2):
        raise ValueError("only the genuine two-panel checkpoint may be adopted")
    if newout.exists():
        raise FileExistsError("new output must not exist; old output is never overwritten")
    binding={"request":old_binding["request"],"source_sha256":SOURCE_SHA,"engine":new_engine}
    fingerprint=hashlib.sha256(_canonical(binding)).hexdigest()
    files=[]; checked=[]
    with ctx.workprec(req.precision_bits):
        state={pair_name(p):complex_ball_record(acb(0)) for p in req.pairs}
        for i,manifest in enumerate(oldcert["panels"]):
            path=oldout/f"panel_{i:04d}.json"
            data=json.loads(path.read_text());payload=data["payload"]
            digest=hashlib.sha256(_canonical(payload)).hexdigest()
            expected_center=str(exact_fraction(req.outer)-(2*i+1)*exact_fraction(req.half_width))
            if (data["fingerprint"]!=saved["fingerprint"] or data["index"]!=i or
                data["payload_sha256"]!=digest or manifest["payload_sha256"]!=digest or
                payload["center"]!=expected_center or
                payload["full_intermediate_sum"]!=list(range(req.max_ell+1)) or
                data["right_state_sha256"]!=hashlib.sha256(_canonical(state)).hexdigest()):
                raise ValueError("old panel identity/chain mismatch")
            state=_verify_boundary_carry(payload,state,req.pairs)
            data["fingerprint"]=fingerprint
            data["adopted_from"]={"fingerprint":saved["fingerprint"],"file_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                                  "payload_sha256":digest,"numerical_reexecution":False}
            files.append((path.name,data));checked.append({"index":i,"file":path.name,"payload_sha256":digest})
    newout.mkdir(parents=True)
    _write_json(newout/"REQUEST.json",{"schema":"PHYS68_PROFILE_REQUEST_V1","fingerprint":fingerprint,"binding":binding,"HH_R10":"OFF"})
    for name,data in files:_write_json(newout/name,data)
    receipt={"schema":"PHYS68_BOUNDED_CHECKPOINT_ADOPTION_V1","recorded_utc":datetime.now(timezone.utc).isoformat(),
             "old_source_sha256":OLD_SHA,"new_source_sha256":new_engine["files_sha256"]["phys68_profiles.py"],
             "old_fingerprint":saved["fingerprint"],"new_fingerprint":fingerprint,
             "unchanged_original_definitions":[k for k in old_named if k!="run_profiles"],
             "changed_original_definitions":changed,"added_definitions":sorted(ADDED),
             "anonymous_import_constant_statements_unchanged":True,
             "other_kernel_runtime_source_request_unchanged":True,"panels_adopted":checked,
             "old_output":str(oldout),"old_files_modified":False,"solver_integrations":0,
             "why":"Arb radius restoration may widen by one magnitude ulp; bind saved predecessor bytes and require exact containing input boxes",
             "HH_R10":"OFF"}
    _write_json(newout/"ADOPTION_RECEIPT.json",receipt)
    return receipt


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,required=True);p.add_argument("--old-out",type=Path,required=True)
    p.add_argument("--new-out",type=Path,required=True);p.add_argument("--old-code",type=Path,required=True)
    a=p.parse_args();print(json.dumps(adopt(a.source,a.old_out,a.new_out,a.old_code),sort_keys=True))


if __name__=="__main__":main()
