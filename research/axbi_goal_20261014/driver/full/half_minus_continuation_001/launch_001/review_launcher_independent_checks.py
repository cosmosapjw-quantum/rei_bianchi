#!/usr/bin/env python3
"""Read-only AX08-SHEAR_HALF_MINUS separate-mechanism launcher review.

No native/independent model reviewer is available here. Independently parses
canonical source/contract without importing the launcher; checks high-impact
mutable/lifecycle and frozen-input operations against the existing DAG.
"""
import ast
import hashlib
import json
from pathlib import Path
import sys

OWN=Path(__file__).resolve().parent
ROOT=Path(__import__("os").environ.get("AX08_CANONICAL_ROOT",str(Path(__file__).resolve().parents[6])))
PATH=OWN/"launcher.py"
CONTRACT=OWN/"LAUNCH_CONTRACT.json"
def filehash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):
    return json.loads(path.read_text())
def require(cond,code):
    if not cond:
        raise AssertionError(code)
def main():
    c=load(CONTRACT)
    source=PATH.read_text()
    tree=ast.parse(source)
    definitions={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    mandatory={"preflight","launch","classify_half_plus","classify_minus","process_record","is_owner","is_science","safe_json"}
    require(mandatory.issubset(definitions),"MISSING_LIFECYCLE_METHOD")
    funcs={k:ast.get_source_segment(source,v) for k,v in definitions.items()}
    # Factual source AST controls; not an automated proof of arbitrary Python execution.
    pre=funcs["preflight"]; launch=funcs["launch"]; main_func=funcs["main"]
    require("subprocess.Popen(" not in pre and "subprocess.Popen(" not in main_func, "PREFLIGHT_SIDE_EFFECT")
    require(launch.count("subprocess.Popen(")==1,"MUST_HAVE_EXACTLY_ONE_SCIENCE_POPEN")
    require(launch.index('safe_json(OWN/"RESERVATION.json"')<launch.index("subprocess.Popen("),
            "RESERVATION_NOT_BEFORE_POPEN")
    require(launch.index("preflight()")<launch.index('safe_json(OWN/"RESERVATION.json"'),
            "BINDING_NOT_CHECKED_BEFORE_RESERVATION")
    require('start_new_session=True' in launch and 'os.killpg(proc.pid' in launch,
            "OWNED_PROCESS_GROUP_MISSING")
    require('--release' in main_func and 'if args.release is None' in main_func,
            "RELEASE_CANNOT_BE_OPTIONAL")
    for flag in ("remote_checked","pending_checked","exclusive_owner","independent_launcher_review",
                 "launcher_sha256","contract_sha256","half_plus_terminal_sha256","minus_terminal_sha256",
                 "science_count_after_reservation","observed_unix_s"):
        require(flag in launch,"MISSING_LAUNCH_RELEASE_BINDING:"+flag)
    for metric in ("RSS_CAP","SCIENCE_OUTPUT_CAP","LAUNCHER_OUTPUT_CAP","COMBINED_OUTPUT_CAP",
                   "WALL_CAP"):
        require(metric in launch,"MISSING_RUNTIME_RESOURCE_CAP:"+metric)
    proc=funcs["is_science"]
    require("argv[0]" in proc and "argv[1:]" not in proc,"PROCESS_CLASSIFIER_ARGV_FALSE_POSITIVE")
    owner=funcs["is_owner"]
    require('relative_to(AX/"driver/full")' in owner,"UNSCOPED_SCHEDULER_OWNER")
    checks={"ast_source_controls":"PASS"}
    entries={
        "authority":(c["existing_authority"]["path"],c["existing_authority"]["sha256"]),
        "existing_independent_binding_review":(
            c["existing_authority"]["independent_binding_review"],
            c["existing_authority"]["independent_review_sha256"]),
        "private_binding":(c["binding"]["path"],c["binding"]["sha256"]),
        "private_authority":(
            "research/axbi_goal_20261014/driver/full/half_minus_continuation_001/EXECUTION_AUTHORITY.binding",
            c["binding"]["private_authority_binding_sha256"]),
        "binary":(c["binding"]["binary"],c["binding"]["binary_sha256"]),
    }
    for name,(path,digest) in entries.items():
        require(filehash(ROOT/path)==digest,"FROZEN_IDENTITY_FAILED:"+name)
        checks[name]={"sha256":digest,"status":"PASS"}
    require(c["case"]=="SHEAR_HALF_MINUS","CASE_CHANGED")
    require(c["execution"]["outer_argv"][-1]==c["binding"]["sha256"],"ARGV_BINDING_CHANGED")
    require(c["execution"]["caps"]["new_observed_starts_max"]==1,"MORE_THAN_ONE_START")
    require(c["execution"]["caps"]["automatic_retries"]==0,"UNAUTHORIZED_RETRY")
    require(c["execution"]["caps"]["combined_segment_MiB"]==4096,"RESOURCE_BUDGET_DRIFT")
    require(c["execution"]["effective_trajectory_caps"]["accepted"]==500000,"STEP_CAP_DRIFT")
    require(c["execution"]["effective_trajectory_caps"]["rhs"]==20000000,"RHS_CAP_DRIFT")
    outputs=[c["execution"]["output"],c["execution"]["raw_output"]]
    require(not any((ROOT/p).exists() for p in outputs),"EXISTING_SCIENCE_OUTPUT")
    require(not any((OWN/p).exists() for p in ("RESERVATION.json","PROCESS_ACK.json",
                                                "TERMINAL_RECEIPT.json")),"RESERVATION_ALREADY_SPENT")
    old=load(ROOT/"research/axbi_goal_20261014/driver/full/epoch_recovery_001/plus/recovery_001/INCIDENT_CLASSIFICATION.json")
    require(old["status"]=="RUNTIME_CLASSIFIER_FALSE_POSITIVE_SOLVER_ABORTED",
            "PLUS_HISTORIC_RUNTIME_MISCLASSIFIED")
    prev=load(ROOT/"research/axbi_goal_20261014/driver/full/half_plus_continuation_001/launch_001/TERMINAL_RECEIPT.json")
    require(prev["exit_code"]==0 and prev["stop_reason"] is None, "HALF_PLUS_NOT_TERMINAL")
    case=ROOT/"research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_HALF_PLUS_composed_002/COMPOSITION_RECEIPT.json"
    comp=load(case)
    require(comp["status"]=="COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION" and comp["row_counts"]["history.csv"]["composed_rows"]==312238,
            "HALF_PLUS_HISTORY_NOT_COMPOSED")
    terminal=load(ROOT/"research/axbi_goal_20261014/driver/full/minus_continuation_001/launch_001/TERMINAL_RECEIPT.json")
    require(terminal.get("exit_code")==0 and terminal.get("stop_reason") is None,"PRIOR_MINUS_TERMINAL_NOT_NATURAL")
    comp=load(ROOT/"research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_MINUS_composed_001/COMPOSITION_RECEIPT.json")
    require(comp["status"]=="COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION" and comp["row_counts"]["history.csv"]["composed_rows"]==312238,
            "PRIOR_MINUS_COMPLETE_COMPOSITION_MISSING")
    report={
       "schema":"rei.axbi.shear_minus_launcher_mechanical_review.v1",
       "status":"PASS_SCOPED_INDEPENDENT_IMPLEMENTATION_CONTROL",
       "review_independence":"separate read-only AST/contract/source-hash checker, same assistant model; fresh independent model NOT_RUN",
       "source_sha256":filehash(PATH),"contract_sha256":filehash(CONTRACT),
       "reviewed_case":"SHEAR_HALF_MINUS","checks":checks,
       "prerequisite_half_plus_completed_rows":312238,"prerequisite_minus_completed_rows":312238,
       "preexisting_independent_scientific_binding_review":c["existing_authority"]["independent_review_sha256"],
       "new_solver_starts":0,"scientific_admission":"NOT_ISSUED",
       "limits":"Not a substitute for physical finite-precision solver/convergence validation; controller must reobserve remote and local slots before one science start."
    }
    print(json.dumps(report,indent=2))
if __name__=="__main__":
    main()
