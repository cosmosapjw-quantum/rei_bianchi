#!/usr/bin/env python3
"""Bounded integration controls for the scheduler; ZERO scientific kernel calls.

Every subprocess imports a synthetic worker from a separate locked fixture.
The real off_path_worker and its interval kernels are never imported here.
The specified output directory is fresh and all first failures are preserved.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback
from unittest.mock import patch


STUB = r'''import hashlib,json,os,time
from pathlib import Path
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text())
def save(p,x):
 with Path(p).open("x") as s: json.dump(x,s,sort_keys=True)
class Context:
 def __init__(self,package):
  self.package=Path(package);self.source=sha(self.package/"SOURCE_LOCK.json")
 def run(self,node,subdivisions,precision,output_dir,purpose):
  output_dir=Path(output_dir);output_dir.mkdir()
  save(output_dir/"SYNTHETIC_CALL.json",dict(node=node,purpose=purpose,scientific_kernel_calls=0))
  if str(node)==os.environ.get("E13C7_SYNTHETIC_DELAY_NODE"):
   time.sleep(5)
  if str(node)==os.environ.get("E13C7_SYNTHETIC_FAIL_NODE"):
   raise RuntimeError("intentional synthetic worker failure")
  start=time.perf_counter()
  work=dict(node=node,N=subdivisions,precision=precision,source_lock_sha256=self.source,synthetic=True)
  semantic=hashlib.sha256(json.dumps(work,sort_keys=True).encode()).hexdigest()
  summary=dict(node=node,N=subdivisions,precision=precision,semantic_sha256=semantic,
   elapsed_seconds=time.perf_counter()-start,peak_RSS_KiB=1,new_coefficient_evaluations=0,
   new_local_enclosures=0,scientific_kernel_calls=0)
  save(output_dir/"RESULT.json",dict(work=work,summary=summary))
  save(output_dir/"ADMISSION.json",dict(synthetic_protocol_only=True,science="NOT_EVALUATED"))
  save(output_dir/"COMPLETE.json",dict(files={n:sha(output_dir/n) for n in ["RESULT.json","ADMISSION.json"]}))
  return summary
def validate_completed(ctx,node,N,P,path):
 path=Path(path);complete=read(path/"COMPLETE.json")
 assert complete["files"]=={n:sha(path/n) for n in ["RESULT.json","ADMISSION.json"]},"synthetic file SHA mismatch"
 result=read(path/"RESULT.json");work=result["work"]
 assert work==dict(node=node,N=N,precision=P,source_lock_sha256=ctx.source,synthetic=True),"synthetic identity mismatch"
 semantic=hashlib.sha256(json.dumps(work,sort_keys=True).encode()).hexdigest()
 assert result["summary"]["semantic_sha256"]==semantic
 return result["summary"]
'''


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, obj):
    with Path(path).open("x") as stream:
        json.dump(obj, stream, sort_keys=True, indent=2)
        stream.write("\n")


def read(path):
    return json.loads(Path(path).read_text())


def pin(path):
    return {"bytes": path.stat().st_size, "sha256": sha(path)}


def fixture(root, runner, seconds=180):
    root.mkdir()
    (root / "code").mkdir()
    (root / "inputs").mkdir()
    shutil.copyfile(runner, root / "code/parallel_batch.py")
    (root / "code/off_path_worker.py").write_text(STUB)
    save(root / "inputs/WORK_PLAN.json", {
        "schema": "bass-he-e13c7-work-plan-v1", "status": "SEALED_FOR_HEAVY_NCP",
        "mode": "OFF", "primary_N": 512, "precision": 60,
        "local_primary_nodes": [1, 2, 3, 4], "ncp_nodes": [9, 10],
        "prior_admitted_nodes": [20], "zero_nodes": [30],
        "limits": {"automatic_retries": 0, "seconds_per_path": seconds,
                   "memory_bytes_per_process": 128 * 1024 ** 2,
                   "max_local_workers": 2, "max_ncp_ranks": 64,
                   "memory_reserve_fraction": 0.2, "batch_wall_seconds": 30},
        "input_records": {str(n): {"estimated_cost_seconds": c} for n, c in
                          [(1, 9), (2, 8), (3, 7), (4, 6), (9, 9), (10, 9)]}})
    save(root / "SOURCE_LOCK.json", {"schema": "bass-he-e13c7-source-lock-v1",
         "files": {"code/off_path_worker.py": pin(root / "code/off_path_worker.py")}})
    files = ["SOURCE_LOCK.json", "inputs/WORK_PLAN.json", "code/off_path_worker.py", "code/parallel_batch.py"]
    save(root / "EXECUTION_LOCK.json", {"schema": "bass-he-e13c7-execution-lock-v1",
         "files": {name: pin(root / name) for name in files}})
    return sha(root / "EXECUTION_LOCK.json")


def command(package, output, lock_sha, extra=()):
    return [sys.executable, str(package / "code/parallel_batch.py"), "launch",
            "--package", str(package), "--output-dir", str(output),
            "--execution-lock-sha256", lock_sha, "--transport", "local", "--scope", "local",
            "--ranks", "auto"] + list(extra)


def invoke(command, record, env=None):
    started = time.perf_counter()
    run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, timeout=45, env=env, check=False)
    evidence = {"argv": command, "exit_code": run.returncode, "stdout": run.stdout,
                "stderr": run.stderr, "elapsed_seconds": time.perf_counter() - started,
                "scientific_kernel_calls": 0}
    save(record, evidence)
    return run


def counts(output):
    return len(list((output / "ranks").glob("rank_*/PATH_*_RESERVED.json")))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    runner, output = Path(args.runner).resolve(strict=True), Path(args.output_dir).resolve()
    output.mkdir(parents=True)
    results = []
    started = time.perf_counter()
    spec = importlib.util.spec_from_file_location("protocol_under_test", runner)
    protocol = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(protocol)

    def check(test_id, predicate, details=None):
        if not predicate:
            results.append({"test_id": test_id, "status": "FAIL", "details": details})
            raise AssertionError(test_id + ": " + str(details))
        results.append({"test_id": test_id, "status": "PASS", "details": details})

    try:
        package = output / "fixture"
        lock_sha = fixture(package, runner)
        plan = read(package / "inputs/WORK_PLAN.json")
        schedule = protocol.lpt_shards(plan, [1, 2, 3, 4], 2)
        check("P01_LPT_HAND_CALCULATED", schedule["shards"] == [[1, 4], [2, 3]] and
              schedule["predicted_rank_costs"] == ["15", "15"], schedule)
        atomic = output / "create_only.txt"
        protocol.save_bytes_new(atomic, b"first\n")
        collision = False
        try:
            protocol.save_bytes_new(atomic, b"replacement\n")
        except FileExistsError:
            collision = True
        check("P02_ATOMIC_CREATE_ONLY", collision and atomic.read_bytes() == b"first\n" and
              not list(output.glob(".pending_*")))

        fresh = output / "fresh"
        run = invoke(command(package, fresh, lock_sha, ["--ranks", "2"]), output / "P03_command.json")
        check("P03_FRESH_LOCAL_PROTOCOL", run.returncode == 0, run.stderr)
        complete = read(fresh / "BATCH_COMPLETE.json")
        check("P04_DETERMINISTIC_ASCENDING_COLLECTION", [r["node"] for r in complete["ordered_paths"]] ==
              [1, 2, 3, 4] and complete["new_validated_path_calls"] == 4 and
              complete["new_coefficient_evaluations"] == 0)
        host = read(fresh / "HOST_PREFLIGHT.json")
        check("P05_ACTUAL_AFFINITY_MEMORY_CAP", host["selected_ranks"] == 2 and
              len(set(host["rank_cpu_ids"])) == 2 and host["memory_rank_cap"] >= 2 and
              host["cpu_quota_rank_cap"] >= 2 and host["reserved_memory_bytes"] * 5 >=
              host["effective_memory_total_bytes"],
              {k: host[k] for k in ["selected_ranks", "rank_cpu_ids", "cpu_quota_rank_cap", "memory_rank_cap"]})
        check("P06_LOCAL_NOT_MPI_CLAIM", read(fresh / "LAUNCH_PROCESS_RECEIPT.json")["MPI_execution_status"] ==
              "NOT_RUN" and host["open_mpi"]["status"] == "NOT_RUN_LOCAL_TRANSPORT")

        fingerprints = {str(p.relative_to(fresh)): sha(p) for p in fresh.rglob("*") if p.is_file()}
        run = invoke(command(package, fresh, lock_sha), output / "P07_command.json")
        after = {str(p.relative_to(fresh)): sha(p) for p in fresh.rglob("*") if p.is_file()}
        check("P07_OUTPUT_COLLISION_PRESERVES_BYTES", run.returncode != 0 and after == fingerprints)

        resumed = output / "resumed"
        run = invoke(command(package, resumed, lock_sha, ["--resume-from", str(fresh)]),
                     output / "P08_command.json")
        check("P08_COMPLETE_RESUME_ZERO_REEXECUTION", run.returncode == 0 and counts(resumed) == 0 and
              read(resumed / "BATCH_COMPLETE.json")["reused_completed_paths"] == 4, run.stderr)
        check("P09_RESUME_SELF_CONTAINED_SEMANTIC_IDENTITY",
              read(resumed / "BATCH_COMPLETE.json")["collection_semantic_sha256"] ==
              complete["collection_semantic_sha256"] and
              all((resumed / row["relative_directory"] / "COMPLETE.json").is_file()
                  for row in complete["ordered_paths"]))

        wrong = output / "wrong_lock"
        run = invoke(command(package, wrong, "0" * 64), output / "P10_command.json")
        check("P10_EXTERNAL_LOCK_REJECTION_BEFORE_SCIENCE", run.returncode != 0 and counts(wrong) == 0 and
              not (wrong / "BATCH_COMPLETE.json").exists())

        cap = output / "excess_ranks"
        run = invoke(command(package, cap, lock_sha, ["--ranks", "999"]), output / "P11_command.json")
        check("P11_OVERSUBSCRIPTION_REJECTED", run.returncode != 0 and counts(cap) == 0)

        scope = output / "ncp_local_forbidden"
        run = invoke(command(package, scope, lock_sha, ["--scope", "ncp"]), output / "P12_command.json")
        check("P12_NCP_HAS_NO_LOCAL_FALLBACK", run.returncode != 0 and counts(scope) == 0)

        outside = output / "outside_local_scope"
        run = invoke(command(package, outside, lock_sha, ["--nodes", "9"]), output / "P13_command.json")
        check("P13_LOCAL_SCOPE_NOT_EXPANDED", run.returncode != 0 and counts(outside) == 0)

        absent = output / "absent_mpi"
        env = os.environ.copy()
        env["PATH"] = ""
        run = invoke(command(package, absent, lock_sha, ["--scope", "ncp", "--transport", "mpi"]),
                     output / "P14_command.json", env)
        check("P14_MISSING_MPI_EXPLICIT_FAILURE", run.returncode != 0 and counts(absent) == 0 and
              "mpiexec is unavailable; no fallback" in run.stderr)

        fail = output / "worker_failure"
        env = os.environ.copy()
        env["E13C7_SYNTHETIC_FAIL_NODE"] = "1"
        run = invoke(command(package, fail, lock_sha), output / "P15_command.json", env)
        check("P15_FIRST_WORKER_FAILURE_PRESERVED", run.returncode != 0 and
              (fail / "FAILURE.json").is_file() and not (fail / "BATCH_COMPLETE.json").exists() and
              any((fail / "ranks").glob("rank_*/FAILURE.json")))
        prior_complete = {int(p.parent.name.split("_")[1]) for p in (fail / "paths").glob("node_*/COMPLETE.json")}
        prior_attempted = {read(p)["node"] for p in (fail / "ranks").glob("rank_*/PATH_*_RESERVED.json")}
        prior_partial = {int(p.name.split("_")[1]) for p in (fail / "paths").iterdir()} - prior_complete
        restart = sorted((prior_attempted - prior_complete) | prior_partial)
        denied = output / "implicit_retry_denied"
        run = invoke(command(package, denied, lock_sha, ["--resume-from", str(fail)]),
                     output / "P16_command.json")
        check("P16_NO_AUTOMATIC_FAILED_PATH_RETRY", run.returncode != 0 and counts(denied) == 0 and
              "--retry-incomplete-nodes" in run.stderr)
        fixed = output / "explicit_resume"
        run = invoke(command(package, fixed, lock_sha, ["--resume-from", str(fail),
                     "--retry-incomplete-nodes", ",".join(map(str, restart))]),
                     output / "P17_command.json")
        check("P17_EXPLICIT_IDENTITY_BOUND_RESTART", run.returncode == 0 and
              read(fixed / "BATCH_COMPLETE.json")["reused_completed_paths"] == len(prior_complete) and
              counts(fixed) == 4 - len(prior_complete), run.stderr)

        identity = output / "resume_N_mismatch"
        run = invoke(command(package, identity, lock_sha, ["--resume-from", str(fresh), "--subdivisions", "1024"]),
                     output / "P18_command.json")
        check("P18_CHANGED_N_RESUME_REJECTED", run.returncode != 0 and counts(identity) == 0)

        bad_evidence = output / "tampered_prior"
        shutil.copytree(fresh, bad_evidence)
        result = bad_evidence / "paths/node_000001/RESULT.json"
        result.write_bytes(result.read_bytes() + b" ")
        tamper_run = output / "invalid_completed_evidence"
        run = invoke(command(package, tamper_run, lock_sha, ["--resume-from", str(bad_evidence)]),
                     output / "P19_command.json")
        check("P19_TAMPERED_COMPLETION_NOT_TREATED_AS_MISSING", run.returncode != 0 and counts(tamper_run) == 0)

        changed_package = output / "changed_package"
        changed_sha = fixture(changed_package, runner)
        worker = changed_package / "code/off_path_worker.py"
        worker.write_bytes(worker.read_bytes() + b"\n# changed bytes\n")
        changed_run = output / "locked_code_tamper"
        run = invoke(command(changed_package, changed_run, changed_sha), output / "P20_command.json")
        check("P20_CODE_TAMPER_BEFORE_KERNEL_IMPORT", run.returncode != 0 and counts(changed_run) == 0)

        missing_package = output / "unlocked_runtime_package"
        missing_sha = fixture(missing_package, runner)
        (missing_package / "code/unlocked.py").write_text("# unpinned runtime\n")
        missing_run = output / "unlocked_runtime_run"
        run = invoke(command(missing_package, missing_run, missing_sha), output / "P21_command.json")
        check("P21_RUNTIME_IMPORT_CLOSURE_REQUIRED", run.returncode != 0 and counts(missing_run) == 0)

        malformed_manifest = output / "malformed_manifest"
        shutil.copytree(fresh, malformed_manifest)
        manifest = read(malformed_manifest / "EXECUTION_MANIFEST.json")
        manifest["schedule"]["shards"] = [[1, 1], [2, 3]]
        (malformed_manifest / "EXECUTION_MANIFEST.json").write_text(json.dumps(manifest))
        error = None
        try:
            protocol.verify_manifest(malformed_manifest, sha(malformed_manifest / "EXECUTION_MANIFEST.json"))
        except ValueError as exc:
            error = str(exc)
        check("P22_DUPLICATE_MISSING_SHARDS_REJECTED", error and "coverage/uniqueness" in error)

        timeout_package = output / "timeout_package"
        timeout_sha = fixture(timeout_package, runner, seconds=1)
        timeout_run = output / "timeout_run"
        env = os.environ.copy()
        env["E13C7_SYNTHETIC_DELAY_NODE"] = "1"
        run = invoke(command(timeout_package, timeout_run, timeout_sha, ["--nodes", "1", "--ranks", "1"]),
                     output / "P23_command.json", env)
        check("P23_TIMEOUT_PRESERVES_PARTIAL_NO_RETRY", run.returncode != 0 and counts(timeout_run) == 1 and
              not (timeout_run / "BATCH_COMPLETE.json").exists() and
              read(timeout_run / "ranks/rank_0000/FAILURE.json")["type"] == "TimeoutError")

        check("P24_REAL_SCIENTIFIC_KERNELS_NOT_IMPORTED", "off_path_worker" not in sys.modules and
              "directed_interval" not in sys.modules and "path_enclosure" not in sys.modules)

        def ncp_root_missing_limits(path):
            name = str(path)
            if name == "/proc/self/cgroup":
                return "0::/"
            if name == "/proc/self/mountinfo":
                return "1 0 0:1 / /sys/fs/cgroup rw - cgroup2 cgroup rw"
            if name.endswith("cpuset.cpus.effective"):
                return "0-63"
            return None
        with patch.object(protocol, "read_text_optional", side_effect=ncp_root_missing_limits):
            observed = protocol.cgroup_observation()
            check("P25_OBSERVED_NCP_ROOT_MISSING_FILES_SUPPORTED", observed["cpu_quota_file_observation"] ==
                  "UNOBSERVED" and observed["memory_limit_file_observation"] == "UNOBSERVED" and
                  observed["levels"][0]["values"]["cpuset.cpus.effective"] == "0-63", observed)
            with patch.object(protocol.os, "sched_getaffinity", return_value=set(range(64))):
                synthetic_host = protocol.host_preflight(protocol.plan_limits(plan), "ncp", "2", 2, "local")
            check("P26_UNOBSERVED_QUOTA_NOT_UNLIMITED_OR_ATTESTED", synthetic_host["selected_ranks"] == 2 and
                  synthetic_host["cpu_quota_observation"] == "UNOBSERVED" and
                  synthetic_host["effective_cpu_quota"] is None and
                  synthetic_host["cpu_allocation_attestation"] == "NOT_ASSERTED",
                  {"synthetic_preflight_only": True, "actual_MPI_run": False,
                   "quota": synthetic_host["effective_cpu_quota"],
                   "quota_status": synthetic_host["cpu_quota_observation"]})

        v1 = output / "cgroup_v1_fixture"
        for controller in ("cpu", "memory"):
            (v1 / controller / "group").mkdir(parents=True)
        (v1 / "cpu/group/cpu.cfs_quota_us").write_text("150000\n")
        (v1 / "cpu/group/cpu.cfs_period_us").write_text("100000\n")
        (v1 / "memory/group/memory.limit_in_bytes").write_text(str(4 * 1024 ** 3))
        (v1 / "memory/group/memory.usage_in_bytes").write_text(str(1024 ** 3))
        original_read = protocol.read_text_optional
        def v1_files(path):
            if str(path) == "/proc/self/cgroup":
                return "2:cpu,cpuacct:/group\n3:memory:/group"
            if str(path) == "/proc/self/mountinfo":
                return ("1 0 0:1 / " + str(v1 / "cpu") + " rw - cgroup cgroup rw,cpu,cpuacct\n" +
                        "2 0 0:2 / " + str(v1 / "memory") + " rw - cgroup cgroup rw,memory")
            return original_read(path)
        with patch.object(protocol, "read_text_optional", side_effect=v1_files):
            observed = protocol.cgroup_observation()
            synthetic_host = protocol.host_preflight(protocol.plan_limits(plan), "local", "1", 2, "local")
            check("P27_V1_FINITE_QUOTA_MEMORY_RESOLVED", synthetic_host["effective_cpu_quota"] == "3/2" and
                  synthetic_host["cpu_quota_rank_cap"] == 1 and
                  synthetic_host["effective_memory_total_bytes"] == 4 * 1024 ** 3,
                  {"synthetic_preflight_only": True, "quota": synthetic_host["effective_cpu_quota"],
                   "memory_total_bytes": synthetic_host["effective_memory_total_bytes"]})
            error = None
            try:
                protocol.host_preflight(protocol.plan_limits(plan), "local", "2", 2, "local")
            except ValueError as exc:
                error = str(exc)
            check("P28_CONTRADICTORY_VISIBLE_QUOTA_BLOCKS_OVERALLOCATION", error and
                  "exceed effective CPU/memory/task/plan capacity: 1" in error)

        root_choice = protocol.root_launch_choice(True, "mpi", 0)
        launch_argv = protocol.mpi_command("/usr/bin/mpiexec", "/tmp/observed-hostfile", 64,
                                          ["python3", "rank-worker"], True)
        check("P29_EXPLICIT_ROOT_FLAG_DOCUMENTED_ARGV_ONLY", root_choice["effective_uid"] == 0 and
              root_choice["allow_openmpi_root_explicitly_requested"] is True and
              launch_argv.count("--allow-run-as-root") == 1,
              {"constructed_argv_only_MPI_NOT_RUN": launch_argv})
        error = None
        try:
            protocol.root_launch_choice(True, "mpi", 1000)
        except ValueError as exc:
            error = str(exc)
        check("P30_ROOT_OVERRIDE_REJECTED_FOR_NONROOT", error and "uid of 0" in error)
        error = None
        try:
            protocol.root_launch_choice(True, "local", 0)
        except ValueError as exc:
            error = str(exc)
        check("P31_ROOT_OVERRIDE_REJECTED_FOR_LOCAL", error and "invalid for local transport" in error)
        normal = protocol.mpi_command("/usr/bin/mpiexec", "/tmp/observed-hostfile", 64,
                                      ["python3", "rank-worker"], False)
        check("P32_NO_UNREQUESTED_ROOT_FLAG_ALL_RANKS_COMPUTE", "--allow-run-as-root" not in normal and
              normal[normal.index("-n") + 1] == "64" and "--nooversubscribe" in normal,
              {"constructed_argv_only_MPI_NOT_RUN": normal})
    except BaseException as exc:
        save(output / "FIRST_FAILURE.json", {"type": type(exc).__name__, "message": str(exc),
             "traceback": traceback.format_exc(), "preserved": True})
    report = {"schema": "bass-he-e13c7-parallel-protocol-tests-v1", "utc": datetime.now(timezone.utc).isoformat(),
              "runner_sha256": sha(runner), "test_file_sha256": sha(Path(__file__)),
              "results": results, "passed": sum(r["status"] == "PASS" for r in results),
              "failed": sum(r["status"] != "PASS" for r in results),
              "completed_all_controls": len(results) == 32 and all(r["status"] == "PASS" for r in results),
              "scientific_kernel_calls": 0, "MPI_execution": "NOT_RUN",
              "elapsed_seconds": time.perf_counter() - started,
              "evidence_directory": str(output), "independent_scientific_review": "NOT_PERFORMED_BY_AUTHOR"}
    save(output / "TEST_RESULTS.json", report)
    print(json.dumps({k: report[k] for k in ["passed", "failed", "completed_all_controls", "elapsed_seconds"]}))
    return 0 if report["completed_all_controls"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
