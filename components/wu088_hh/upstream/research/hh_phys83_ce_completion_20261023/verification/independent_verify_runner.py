#!/usr/bin/env python3
"""Independent admission/resume controls with explicitly synthetic file payloads.

Never call calculate(), main(--execute), or any scientific kernel.  Seven dummy
files satisfy the completion schema solely to test file/claim admission. Their
declared callback budget is synthetic and is never a physical execution count.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
from unittest.mock import patch

from independent_verify import Recorder,safe,sha,utc

UNIT=Path(__file__).resolve().parents[1]
RUNNER=UNIT/"source/run_study.py"
PINNED_RUNNER="dee42bcd164fbdfdceedc72200df53e2e687bf5978caddd1f5a40c63bc360f85"


def canon(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()


def write_json(path,value):
    with path.open("x",encoding="utf-8") as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False)
        stream.write("\n")


def rewrite_fixture(path,value):
    # Deliberate adverse mutation of this verifier's own fixture, never real data.
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def tree_hashes(root):
    return {str(p.relative_to(root)):sha(p) for p in root.rglob("*") if p.is_file()}


def make_identity(tag):
    payload={"schema":"MOCK_PHYS83_ADMISSION_ONLY_V1","case":tag,
             "MOCK_ONLY":True,"actual_physical_calculation":False}
    return {"scientific_identity":hashlib.sha256(canon(payload)).hexdigest(),"payload":payload}


def mock_summary(runner):
    return {"status":"COMPLETED_SCOPED","callback_counts":dict(runner.EXPECTED),
            "MOCK_ONLY":True,"declared_budget_for_schema_control_only":True,
            "actual_kernel_callbacks":0,"actual_physics_rows":0}


def write_dummy_results(output,runner):
    summary=mock_summary(runner)
    write_json(output/"ENVIRONMENT.json",{"MOCK_ONLY":True,"runtime":"synthetic"})
    for name in ("rate_grid.csv","steady_grid.csv","transient_grid.csv"):
        with (output/name).open("x",encoding="utf-8") as stream:
            stream.write("MOCK_ONLY,value\ntrue,0\n")
    write_json(output/"SCIENCE_SUMMARY.json",summary)
    with (output/"execution_events.jsonl").open("x",encoding="utf-8") as stream:
        stream.write(json.dumps({"MOCK_ONLY":True,"event":"NO_PHYSICAL_CALCULATION"})+"\n")
    return summary


def build_cases(rec,runner):
    cases=[]
    mock_counts={"successful_mock_callbacks":0,"deliberately_failed_mock_callbacks":0,
                 "forbidden_callbacks":0,"real_calculate_calls":0}

    def forbidden(*args,**kwargs):
        mock_counts["forbidden_callbacks"]+=1
        raise AssertionError("FORBIDDEN_CALLBACK_CALLED")

    def forbidden_calculate(*args,**kwargs):
        mock_counts["real_calculate_calls"]+=1
        raise AssertionError("REAL_SCIENTIFIC_CALCULATE_FORBIDDEN")
    runner.calculate=forbidden_calculate

    def fresh(tag):
        base=rec.path/"MOCK_ONLY_cases"/tag
        base.mkdir(parents=True,exist_ok=False)
        identity=make_identity(tag)
        return base,identity,base/"output",base/"registry"

    def seed(tag,status="COMPLETED"):
        base,identity,output,registry=fresh(tag)
        output.mkdir();registry.mkdir()
        write_json(output/"SCIENCE_IDENTITY.json",identity)
        summary=write_dummy_results(output,runner)
        files={p.name:{"bytes":p.stat().st_size,"SHA256":sha(p)} for p in output.iterdir() if p.is_file()}
        complete={"schema":"PHYS83_CE_COMPLETION_V1","status":"COMPLETED",
                  "scientific_identity":identity["scientific_identity"],"files":files,"execution":summary,
                  "MOCK_ONLY":True}
        write_json(output/"COMPLETE.json",complete)
        claim={"scientific_identity":identity["scientific_identity"],"status":status,"MOCK_ONLY":True}
        if status=="COMPLETED":claim["completion_SHA256"]=sha(output/"COMPLETE.json")
        claim_path=registry/(identity["scientific_identity"]+".json")
        write_json(claim_path,claim)
        return base,identity,output,registry,claim_path

    def rebind_fixture_certificate(output,claim_path):
        claim=json.loads(claim_path.read_text())
        claim["completion_SHA256"]=sha(output/"COMPLETE.json")
        rewrite_fixture(claim_path,claim)

    def refresh_payload_hash(output,filename):
        complete=json.loads((output/"COMPLETE.json").read_text())
        p=output/filename
        complete["files"][filename]={"bytes":p.stat().st_size,"SHA256":sha(p)}
        rewrite_fixture(output/"COMPLETE.json",complete)

    def add(name,callback):cases.append((name,"runner_mock",callback))

    def new_then_skip():
        base,identity,output,registry=fresh("new_then_skip")
        def callback(where):
            mock_counts["successful_mock_callbacks"]+=1
            return write_dummy_results(where,runner)
        created=runner.execute_new_or_skip(identity,output,registry,callback)
        rec.check("new_mock_identity_completed",created["status"]=="COMPLETED_NEW_IDENTITY")
        rec.check("exact_seven_mock_payloads",created["verified_payload_files"]==7)
        rec.check("one_mock_callback",mock_counts["successful_mock_callbacks"]==1)
        before=tree_hashes(base)
        skipped=runner.execute_new_or_skip(identity,output,registry,forbidden)
        rec.check("completed_identity_skip",skipped["status"]=="SKIP_COMPLETED_IDENTITY")
        rec.check("reported_resume_callbacks_zero",skipped["science_callbacks"]==0)
        rec.check("actual_resume_callbacks_zero",mock_counts["forbidden_callbacks"]==0)
        rec.check("resume_preserves_all_mock_bytes",tree_hashes(base)==before)
    add("runner_new_mock_then_completed_skip",new_then_skip)

    def payload_corruption():
        base,identity,output,registry,claim=seed("payload_corruption")
        with (output/"rate_grid.csv").open("ab") as stream:stream.write(b"corruption\n")
        before=tree_hashes(base)
        rec.reject("corruption_rejected_before_callback",lambda:runner.execute_new_or_skip(identity,output,registry,forbidden),(ValueError,))
        rec.check("corrupt_mock_evidence_unchanged",tree_hashes(base)==before)
    add("runner_payload_corruption_rejected",payload_corruption)

    def certificate_corruption():
        base,identity,output,registry,claim=seed("certificate_corruption")
        complete=json.loads((output/"COMPLETE.json").read_text())
        complete["altered_certificate"]=True
        rewrite_fixture(output/"COMPLETE.json",complete)
        before=tree_hashes(base)
        rec.reject("COMPLETE_hash_bound_to_claim",lambda:runner.execute_new_or_skip(identity,output,registry,forbidden),(ValueError,))
        rec.check("altered_certificate_preserved",tree_hashes(base)==before)
    add("runner_completion_certificate_corruption",certificate_corruption)

    def empty_and_identity_only():
        for kind in ("empty","identity_only"):
            base,identity,output,registry,claim=seed("manifest_"+kind)
            complete=json.loads((output/"COMPLETE.json").read_text())
            complete["files"]={} if kind=="empty" else {"SCIENCE_IDENTITY.json":complete["files"]["SCIENCE_IDENTITY.json"]}
            rewrite_fixture(output/"COMPLETE.json",complete)
            rebind_fixture_certificate(output,claim)
            before=tree_hashes(base)
            rec.reject("manifest_has_actual_required_payloads:"+kind,
                       lambda:runner.execute_new_or_skip(identity,output,registry,forbidden),(ValueError,))
            rec.check("invalid_manifest_not_repaired_silently",tree_hashes(base)==before)
    add("runner_empty_and_identity_only_manifests",empty_and_identity_only)

    def existing_output():
        base,identity,output,registry=fresh("existing_output")
        output.mkdir();(output/"preserved.txt").write_bytes(b"MOCK_ONLY immutable preexisting data\n")
        before=tree_hashes(output)
        rec.reject("existing_output_no_overwrite",lambda:runner.execute_new_or_skip(identity,output,registry,forbidden),(FileExistsError,))
        rec.check("existing_output_bytes_preserved",tree_hashes(output)==before)
        rec.check("no_identity_claim_created",not (registry/(identity["scientific_identity"]+".json")).exists())
    add("runner_existing_output_no_overwrite",existing_output)

    def incomplete_claims():
        for status in ("ADMITTED","FAILED_PRESERVED"):
            base,identity,output,registry=fresh("claim_"+status)
            registry.mkdir();output.mkdir()
            (output/"partial_mock.txt").write_bytes(b"MOCK_ONLY unfinished evidence\n")
            claim=registry/(identity["scientific_identity"]+".json")
            write_json(claim,{"scientific_identity":identity["scientific_identity"],"status":status,"MOCK_ONLY":True})
            before=tree_hashes(base)
            rec.reject("existing_claim_no_automatic_retry:"+status,
                       lambda:runner.execute_new_or_skip(identity,output,registry,forbidden),(RuntimeError,))
            rec.check("existing_claim_evidence_preserved",tree_hashes(base)==before)
    add("runner_failed_or_incomplete_claim_no_retry",incomplete_claims)

    def exclusive_claim():
        base,identity,output,registry=fresh("exclusive_claim")
        registry.mkdir()
        claim=registry/(identity["scientific_identity"]+".json")
        runner.write_new(claim,{"scientific_identity":identity["scientific_identity"],"status":"ADMITTED","MOCK_ONLY":True})
        before=sha(claim)
        rec.reject("O_EXCL_claim_collision",lambda:runner.write_new(claim,{"overwritten":True}),(FileExistsError,))
        rec.check("exclusive_claim_bytes_unchanged",sha(claim)==before)
        rec.reject("simulated_concurrent_duplicate_no_callback",
                   lambda:runner.execute_new_or_skip(identity,output,registry,forbidden),(RuntimeError,))
        rec.check("duplicate_did_not_create_output",not output.exists())
    add("runner_sequential_exclusive_claim_control",exclusive_claim)

    def callback_failure():
        base,identity,output,registry=fresh("callback_failure")
        def failing(where):
            mock_counts["deliberately_failed_mock_callbacks"]+=1
            (where/"partial_mock.txt").write_bytes(b"MOCK_ONLY partial result survives\n")
            raise RuntimeError("INJECTED_MOCK_CALLBACK_FAILURE")
        rec.reject("injected_mock_failure_propagates",lambda:runner.execute_new_or_skip(identity,output,registry,failing),(RuntimeError,))
        claim=registry/(identity["scientific_identity"]+".json")
        failure=json.loads((output/"FAILED.json").read_text())
        rec.check("failed_status_preserved",failure["status"]=="FAILED_PRESERVED"
                  and json.loads(claim.read_text())["status"]=="FAILED_PRESERVED")
        rec.check("failure_reason_preserved","INJECTED_MOCK_CALLBACK_FAILURE" in failure["error"])
        rec.check("partial_mock_payload_preserved",(output/"partial_mock.txt").read_bytes()==b"MOCK_ONLY partial result survives\n")
        rec.check("failure_not_marked_complete",not (output/"COMPLETE.json").exists())
        before=tree_hashes(base)
        rec.reject("failed_mock_callback_not_repeated",lambda:runner.execute_new_or_skip(identity,output,registry,forbidden),(RuntimeError,))
        rec.check("failure_resume_bytes_unchanged",tree_hashes(base)==before)
        rec.check("exactly_one_injected_mock_failure",mock_counts["deliberately_failed_mock_callbacks"]==1)
    add("runner_callback_failure_preservation",callback_failure)

    def metadata_recovery():
        base,identity,output,registry,claim=seed("metadata_recovery",status="ADMITTED")
        output_before=tree_hashes(output)
        response=runner.execute_new_or_skip(identity,output,registry,forbidden)
        rec.check("metadata_recovery_skips_science",response["status"]=="SKIP_COMPLETED_IDENTITY" and response["science_callbacks"]==0)
        updated=json.loads(claim.read_text())
        rec.check("metadata_recovery_binds_certificate",updated["status"]=="COMPLETED" and updated["completion_SHA256"]==sha(output/"COMPLETE.json"))
        rec.check("metadata_recovery_preserves_payload",tree_hashes(output)==output_before)
    add("runner_metadata_only_recovery",metadata_recovery)

    def runtime_exclusion():
        base,identity,output,registry=fresh("runtime_exclusion")
        fixture=base/"synthetic_input_unit"
        for path in tuple(runner.CORE)+tuple("source_data/"+name for name in runner.RAW):
            target=fixture/path;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(("MOCK_ONLY identity bytes: "+path+"\n").encode())
        baseline=runner.scientific_identity(fixture)
        with patch.object(runner.platform,"python_version",return_value="MOCK_RUNTIME_CHANGED"), \
             patch.object(runner.importlib.metadata,"version",return_value="MOCK_PACKAGE_CHANGED"):
            changed=runner.scientific_identity(fixture)
        rec.check("runtime_metadata_not_in_identity",changed==baseline)
        rec.check("runtime_replay_flag_false",baseline["payload"]["runtime_version_in_identity"] is False)
        rec.check("runtime_value_not_hashed","MOCK_RUNTIME_CHANGED" not in json.dumps(baseline))
    add("runner_runtime_metadata_excluded_from_identity",runtime_exclusion)

    def restored_bytes():
        base,identity,output,registry,claim=seed("portable_restore")
        restored=base/"restored_output"
        shutil.copytree(output,restored)
        rec.check("restored_bytes_exact",tree_hashes(output)==tree_hashes(restored))
        response=runner.execute_new_or_skip(identity,restored,registry,forbidden)
        rec.check("restored_output_resume_zero_callbacks",response["status"]=="SKIP_COMPLETED_IDENTITY" and response["science_callbacks"]==0)
        rec.check("restored_seven_files_verified",response["verified_payload_files"]==7)
    add("runner_restored_mock_bytes_resume",restored_bytes)

    def internal_binding_guards():
        for mutation in ("identity","summary","accounting","missing_certificate_hash"):
            base,identity,output,registry,claim=seed("binding_"+mutation)
            if mutation=="identity":
                data=json.loads((output/"SCIENCE_IDENTITY.json").read_text());data["payload"]["changed"]=True
                rewrite_fixture(output/"SCIENCE_IDENTITY.json",data)
                refresh_payload_hash(output,"SCIENCE_IDENTITY.json");rebind_fixture_certificate(output,claim)
            elif mutation=="summary":
                data=json.loads((output/"SCIENCE_SUMMARY.json").read_text());data["changed"]=True
                rewrite_fixture(output/"SCIENCE_SUMMARY.json",data)
                refresh_payload_hash(output,"SCIENCE_SUMMARY.json");rebind_fixture_certificate(output,claim)
            elif mutation=="accounting":
                complete=json.loads((output/"COMPLETE.json").read_text())
                complete["execution"]["callback_counts"]["paired_rate_calls"]-=1
                rewrite_fixture(output/"COMPLETE.json",complete);rebind_fixture_certificate(output,claim)
            else:
                data=json.loads(claim.read_text());del data["completion_SHA256"]
                rewrite_fixture(claim,data)
            before=tree_hashes(base)
            rec.reject("completion_internal_binding:"+mutation,
                       lambda:runner.execute_new_or_skip(identity,output,registry,forbidden),(ValueError,))
            rec.check("invalid_binding_evidence_preserved",tree_hashes(base)==before)
    add("runner_identity_summary_accounting_bindings",internal_binding_guards)

    def final_no_science():
        rec.check("production_calculate_never_called",mock_counts["real_calculate_calls"]==0)
        rec.check("all_reject_or_skip_paths_zero_callbacks",mock_counts["forbidden_callbacks"]==0)
        rec.check("scientific_modules_never_imported",all(name not in sys.modules for name in ("matched_ce","frozen_star","nuclear_ownership")))
        rec.counters.update(mock_counts)
        rec.counters["actual_scientific_grid_callbacks"]=0
        rec.counters["old_completed_identity_callbacks"]=0
    add("runner_no_production_science_calls",final_no_science)
    return cases,mock_counts


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--case",action="append",default=[])
    parser.add_argument("--lease-receipt",type=Path)
    args=parser.parse_args()
    output=args.output.resolve()
    if UNIT/"verification" not in output.parents:raise ValueError("VERIFICATION_ONLY_OUTPUT_REQUIRED")
    output.mkdir(parents=True,exist_ok=False)
    if sha(RUNNER)!=PINNED_RUNNER:raise ValueError("REVIEWED_RUNNER_IDENTITY_CHANGED")
    names=("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS","BLIS_NUM_THREADS")
    env={name:os.environ.get(name) for name in names}
    if any(value!="1" for value in env.values()):raise RuntimeError("SINGLE_THREAD_REQUIRED")
    start={"schema":"PHYS83_INDEPENDENT_RUNNER_MOCK_CONTROLS_V1","started_utc":utc(),"MOCK_ONLY":True,
           "runner_SHA256":sha(RUNNER),"verifier_SHA256":sha(Path(__file__)),"workers":1,"thread_environment":env,
           "lease_receipt":str(args.lease_receipt) if args.lease_receipt else None,
           "lease_receipt_status":"WRAPPER_WRITES_AFTER_CHILD_EXIT","science_callbacks":0}
    write_json(output/"START.json",start)
    spec=importlib.util.spec_from_file_location("_independent_mock_target_run_study",RUNNER)
    runner=importlib.util.module_from_spec(spec);sys.modules[spec.name]=runner;spec.loader.exec_module(runner)
    real_paths=tuple(runner.CORE)+tuple("source_data/"+name for name in runner.RAW)
    real_before={name:sha(UNIT/name) for name in real_paths}
    rec=Recorder(output)
    cases,counts=build_cases(rec,runner)
    if set(args.case)-{name for name,_,_ in cases}:raise ValueError("UNKNOWN_CASE")
    selected=[row for row in cases if not args.case or row[0] in args.case]
    success=True
    for name,group,callback in selected:
        if not rec.run(name,group,callback):success=False;break
    unchanged={name:sha(UNIT/name) for name in real_paths}==real_before
    if success:
        rec.current="all_controls_real_input_identity"
        try:rec.check("real_scientific_files_unmodified",unchanged)
        except AssertionError:success=False
    outcome={**start,"finished_utc":utc(),"status":"PASS_SCOPED" if success else "FAIL_PRESERVED",
             "checks":rec.checks,"cases":rec.results,"mock_callback_counts":counts,"counters":dict(rec.counters),
             "unfinished_cases":[row[0] for row in selected if row[0] not in {r["case"] for r in rec.results}],
             "real_input_SHA256":real_before,"real_inputs_unmodified":unchanged,
             "scope":"Only mock payloads/claims; synthetic declared callback budget is not physical execution",
             "scientific_grid_executed":False,"calculate_executed":False,
             "completed_science_identity_reruns":0,"production_admission":"NOT_ISSUED"}
    write_json(output/"RESULT.json",safe(outcome));rec.stream.close()
    print(json.dumps({"status":outcome["status"],"checks":rec.checks,"cases":len(rec.results),
                      "mock_callback_counts":counts,"real_inputs_unmodified":unchanged,"output":str(output)}),flush=True)
    return 0 if success else 1


if __name__=="__main__":raise SystemExit(main())
