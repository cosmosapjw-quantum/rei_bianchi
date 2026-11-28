"""Bounded GitHub Actions execution and exact tracked-source checkpoint transport.
No network, credentials, repository writes, old scientific replay, or implicit retry.
"""
from __future__ import annotations
import ast
import base64
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
LEAF = ROOT / "research/provider_registry_molecular_r9_20261028"
SCOPE = [
    "AGENTS.md", ".github/workflows/wu-r9-checkpoint.yml",
    "research/provider_registry_molecular_r4_20261027",
    "research/provider_registry_molecular_r5_20261027",
    "research/provider_registry_molecular_r6_20261027",
    "research/provider_registry_molecular_r7_20261027",
    "research/provider_registry_molecular_r8_20261027",
    "research/provider_registry_molecular_r9_20261028",
]
def sha256(b):
    return hashlib.sha256(b).hexdigest()
def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)
def json_bytes(value):
    return (json.dumps(value, ensure_ascii=True, indent=2) + "\n").encode()
def utc():
    return datetime.now(timezone.utc).isoformat()
def child_limits(seconds):
    resource.setrlimit(resource.RLIMIT_CPU, (seconds, seconds + 1))
def transmit(path, raw):
    label = str(path)
    encoded = base64.b64encode(raw).decode("ascii")
    pieces = [encoded[i:i+4096] for i in range(0, len(encoded), 4096)]
    print("R9_FILE_META " + json.dumps({"path":label, "bytes":len(raw), "sha256":sha256(raw), "chunks":len(pieces)}), flush=True)
    for i, chunk in enumerate(pieces):
        print("R9_FILE_CHUNK " + json.dumps({"path":label, "i":i, "b64":chunk}), flush=True)

def main():
    started = utc()
    request = json.loads((LEAF / "RUN_REQUEST.json").read_text())
    if request.get("schema") != "WU_R9_RUN_REQUEST_V1":
        raise ValueError("Unknown request schema")
    stage = request["stage"]
    if stage not in [f"S{i:02d}" for i in range(1,11)] + ["FINAL"]:
        raise ValueError("Invalid stage")
    action = request["action"]
    expected = {"S06":"primary", "S07":"reference"}.get(stage, "archive")
    if action != expected:
        raise ValueError("Scientific stage/action mismatch")
    if os.environ.get("GITHUB_RUN_ATTEMPT") != "1":
        raise ValueError("No automatic rerun or budget reset")
    commit = git("rev-parse","HEAD").decode().strip()
    tree = git("rev-parse","HEAD^{tree}").decode().strip()
    if os.environ.get("GITHUB_SHA") != commit:
        raise ValueError("Actual checkout differs from event SHA")
    runtime = {}
    process = None
    exit_code = 0
    if stage == "S05":
        freeze_paths = ["CONTRACT.json", "theory/PROOF_KO.md", "theory/THEORY_CODE_MAP.json", "src/causal_resolvent.py", "verification/PRIMARY_INPUT.json", "verification/REFERENCE_INPUT.json", "verification/run_primary.py", "verification/run_reference.py", "verification/wolfram_new_checks.wl"]
        frozen, findings = [], []
        for relative in freeze_paths:
            path = LEAF / relative
            raw = path.read_bytes()
            row = {"path":str(path.relative_to(ROOT)),"bytes":len(raw),"sha256":sha256(raw)}
            if path.suffix == ".py":
                try:
                    ast.parse(raw,filename=relative)
                    row["AST_status"] = "PASS"
                except SyntaxError as exc:
                    row["AST_status"] = "FAIL"
                    findings.append({"path":relative,"kind":"SyntaxError","message":str(exc)})
            frozen.append(row)
        freeze = {"schema":"WU_R9_PREEXECUTION_FREEZE_V1","source_commit":commit,
                  "source_tree":tree,"created_utc":utc(),"files":frozen,"findings":findings,
                  "status":"PASS" if not findings else "FAIL","scientific_imports":0,
                  "scientific_executions":0,"old_science_replay":0}
        runtime["raw/PREEXECUTION_FREEZE.json"] = json_bytes(freeze)
        if findings:
            exit_code = 1
    if action in ("primary", "reference"):
        frozen = json.loads((LEAF / "raw/PREEXECUTION_FREEZE.json").read_text())
        if frozen["status"] != "PASS":
            raise ValueError("Scientific execution requires the actual S05 preflight PASS")
        for item in frozen["files"]:
            if sha256((ROOT/item["path"]).read_bytes()) != item["sha256"]:
                raise ValueError("Frozen scientific dependency changed: "+item["path"])
        runner = LEAF / "verification" / ("run_" + action + ".py")
        output = LEAF / "raw" / (action.upper() + "_RESULTS.json")
        cpu_limit, wall_limit = 60, 90
        if output.exists():
            raise ValueError("Result already exists; refuse repeated scientific execution")
        output.parent.mkdir(exist_ok=True)
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        wall0 = time.monotonic()
        try:
            cp = subprocess.run([sys.executable, str(runner)], cwd=ROOT, capture_output=True,
                                timeout=wall_limit, preexec_fn=lambda: child_limits(cpu_limit))
            exit_code = cp.returncode
            stdout, stderr = cp.stdout, cp.stderr
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            exit_code = 124
            stdout, stderr = exc.stdout or b"", exc.stderr or b""
            timed_out = True
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        process = {"schema":"WU_R9_ACTUAL_PROCESS_V1","stage":stage,"action":action,
                   "source_commit":commit,"command":[sys.executable,str(runner.relative_to(ROOT))],
                   "started_utc":started,"finished_utc":utc(),"executions":1,"returncode":exit_code,
                   "timeout":timed_out,"OS_user_CPU_s":after.ru_utime-before.ru_utime,
                   "OS_system_CPU_s":after.ru_stime-before.ru_stime,
                   "OS_CPU_s":(after.ru_utime-before.ru_utime)+(after.ru_stime-before.ru_stime),
                   "wall_s":time.monotonic()-wall0,"CPU_limit_s":cpu_limit,
                   "includes_imports_and_serialization":True,"old_science_replay":0}
        runtime["raw/"+action.upper()+"_PROCESS.json"] = json_bytes(process)
        runtime["raw/"+action.upper()+"_STDOUT.txt"] = stdout
        runtime["raw/"+action.upper()+"_STDERR.txt"] = stderr
        if output.exists():
            raw = output.read_bytes()
            if len(raw) > 8*1024*1024:
                raise ValueError("Result output exceeds fixed transport bound")
            runtime["raw/"+output.name] = raw
        else:
            exit_code = exit_code or 1
    rows = []
    payload = []
    listing = git("ls-tree","-rz","HEAD","--",*SCOPE)
    for entry in listing.split(b"\0"):
        if not entry:
            continue
        meta, path_b = entry.split(b"\t",1)
        mode, kind, blob = meta.decode().split()
        path = path_b.decode()
        if kind != "blob" or mode not in ("100644","100755"):
            raise ValueError("Unsupported scoped tracked object")
        raw = (ROOT/path).read_bytes()
        actual_blob = hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        if actual_blob != blob:
            raise ValueError("Tracked source differs from commit: "+path)
        rows.append({"path":path,"mode":mode,"git_blob":blob,"bytes":len(raw),"sha256":sha256(raw)})
        payload.append((path,raw,mode))
    manifest = {"schema":"WU_R9_SCOPED_SOURCE_CHECKPOINT_V1","stage":stage,"action":action,
                "request_id":request["request_id"],"created_utc":utc(),"repository":"cosmosapjw-quantum/WU088_HH",
                "source_commit":commit,"source_tree":tree,"scope":SCOPE,
                "entire_repository_or_git_history":False,"tracked_source_files":len(rows),"source":rows,
                "runtime_outputs":[{"path":"RUNTIME/"+p,"bytes":len(b),"sha256":sha256(b),
                                    "part_of_source_commit":False} for p,b in runtime.items()],
                "manifest_self_hash_excluded":True}
    out = ROOT/"out"
    out.mkdir(exist_ok=True)
    name = "WU_MOLECULAR_R9_"+stage+"_SOURCE_20261028_"+commit[:12]+".zip"
    archive = out/name
    with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for path, raw, mode in payload:
            info = zipfile.ZipInfo(path, (2026,10,28,0,0,0))
            info.external_attr = int(mode,8) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info,raw)
        z.writestr("CHECKPOINT_MANIFEST.json",json_bytes(manifest))
        for path,raw in runtime.items():
            z.writestr("RUNTIME/"+path,raw)
    zip_raw = archive.read_bytes()
    transport = {"schema":"WU_R9_TRANSPORT_V1","stage":stage,"action":action,"source_commit":commit,
                 "source_tree":tree,"archive_name":name,"archive_bytes":len(zip_raw),
                 "archive_sha256":sha256(zip_raw),"source_files":len(rows),
                 "runtime_files":len(runtime),"process":process,"created_utc":utc()}
    print("R9_TRANSPORT "+json.dumps(transport,ensure_ascii=True),flush=True)
    transmit("CHECKPOINT_MANIFEST.json",json_bytes(manifest))
    for path, raw in runtime.items():
        transmit(path,raw)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError("ZIP CRC verification failed")
    print("R9_ARCHIVE_LOCAL_CRC_PASS",flush=True)
    return exit_code

if __name__ == "__main__":
    raise SystemExit(main())
