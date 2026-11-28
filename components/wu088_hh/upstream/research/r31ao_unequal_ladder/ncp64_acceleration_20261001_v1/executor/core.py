"""Identity-bound opaque-byte tasks. Synthetic scope only; no scientific reducer."""
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile

import guard

SCHEMA = "WU088_NCP64_TASK_MANIFEST_V1"
MAX_MANIFEST = 8 << 20
MAX_FILE = 512 << 20
HERE = Path(__file__).resolve().parent
BASE_ENV = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C", "TZ": "UTC",
            "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"}


class ContractError(ValueError):
    pass


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("utf-8")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def no_duplicates(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ContractError("DUPLICATE_JSON_KEY")
        d[k] = v
    return d


def read_json(path, cap=MAX_MANIFEST):
    p = Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size > cap:
        raise ContractError("INVALID_OR_OVERSIZED_JSON_FILE")
    with p.open("rb") as f:
        raw = f.read(cap + 1)
    if len(raw) > cap:
        raise ContractError("JSON_FILE_GREW_OVER_LIMIT")
    try:
        return json.loads(raw, object_pairs_hook=no_duplicates,
                          parse_constant=lambda x: (_ for _ in ()).throw(ContractError("NONFINITE_JSON"))), raw
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise ContractError("INVALID_JSON:" + str(exc)) from exc


def absolute(path):
    if type(path) is not str or not path or "\0" in path:
        raise ContractError("INVALID_PATH")
    p = Path(path)
    if not p.is_absolute() or ".." in p.parts:
        raise ContractError("ABSOLUTE_NONTRAVERSING_PATH_REQUIRED")
    return p


def integer(value, lo, hi, field):
    if type(value) is not int or not lo <= value <= hi:
        raise ContractError("INVALID_" + field)


def identity_spec(d):
    if type(d) is not dict or set(d) != {"path", "sha256", "bytes"}:
        raise ContractError("EXACT_FILE_IDENTITY_REQUIRED")
    absolute(d["path"])
    integer(d["bytes"], 0, MAX_FILE, "FILE_SIZE")
    if type(d["sha256"]) is not str or not re.fullmatch("[0-9a-f]{64}", d["sha256"]):
        raise ContractError("INVALID_SHA256")


def load_manifest(path):
    p = absolute(str(path))
    doc, raw = read_json(p)
    if type(doc) is not dict or set(doc) - {"schema", "scope", "output_root", "tasks", "dispatch_order"}:
        raise ContractError("INVALID_MANIFEST_FIELDS")
    if doc.get("schema") != SCHEMA or doc.get("scope") != "SYNTHETIC_ONLY":
        raise ContractError("SYNTHETIC_SCOPE_ONLY")
    root = absolute(doc.get("output_root"))
    if root.resolve() != root or root.is_symlink() or not root.parent.is_dir():
        raise ContractError("CANONICAL_OUTPUT_ROOT_WITH_EXISTING_PARENT_REQUIRED")
    tasks = doc.get("tasks")
    if type(tasks) is not list or not 1 <= len(tasks) <= 4096:
        raise ContractError("TASK_COUNT_1_TO_4096_REQUIRED")
    ids = set()
    required = {"task_id", "executable", "argv", "inputs", "env", "cost_hint", "limits", "semantic_identity"}
    allowed = required | {"expected_output_sha256", "library_pins"}
    for t in tasks:
        if type(t) is not dict or not required <= set(t) or set(t) - allowed:
            raise ContractError("INVALID_TASK_FIELDS")
        tid = t["task_id"]
        if type(tid) is not str or not re.fullmatch("[A-Za-z0-9_-]{1,64}", tid) or tid in ids:
            raise ContractError("DUPLICATE_OR_INVALID_TASK_ID")
        ids.add(tid)
        identity_spec(t["executable"])
        if type(t["inputs"]) is not list or len(t["inputs"]) > 128:
            raise ContractError("INVALID_INPUT_LIST")
        if type(t.get("library_pins", [])) is not list or len(t.get("library_pins", [])) > 128:
            raise ContractError("INVALID_LIBRARY_LIST")
        seen = set()
        for f in t["inputs"] + t.get("library_pins", []):
            identity_spec(f)
            if f["path"] in seen:
                raise ContractError("DUPLICATE_INPUT_OR_LIBRARY")
            seen.add(f["path"])
        argv = t["argv"]
        if (type(argv) is not list or not 2 <= len(argv) <= 128 or
            any(type(a) is not str or "\0" in a or len(a) > 16384 for a in argv) or
            argv[0] != t["executable"]["path"] or argv.count("OUTPUT_PATH") != 1 or
            any("OUTPUT_PATH" in a and a != "OUTPUT_PATH" for a in argv)):
            raise ContractError("EXACT_ARGV_AND_ONE_OUTPUT_PATH_REQUIRED")
        # All file-like absolute argv operands are explicitly identity-bound.
        if any(a.startswith("/") and a != argv[0] and a not in seen for a in argv):
            raise ContractError("UNDECLARED_ABSOLUTE_ARGV_INPUT")
        env = t["env"]
        if (type(env) is not dict or len(env) > 64 or
            any(type(k) is not str or not re.fullmatch("[A-Za-z_][A-Za-z0-9_]*", k) or
                type(v) is not str or "\0" in v or len(v) > 16384 for k, v in env.items())):
            raise ContractError("INVALID_EXPLICIT_ENV")
        if any(env.get(k, "1") != "1" for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")):
            raise ContractError("ONE_INNER_THREAD_REQUIRED")
        if type(t["semantic_identity"]) is not dict:
            raise ContractError("SEMANTIC_IDENTITY_REQUIRED")
        integer(t["cost_hint"], 0, 10**15, "COST_HINT")
        lim = t["limits"]
        if type(lim) is not dict or set(lim) != {"wall_seconds", "address_space_bytes", "rss_bytes", "poll_ms", "max_output_bytes"}:
            raise ContractError("EXACT_LIMIT_FIELDS_REQUIRED")
        integer(lim["wall_seconds"], 1, 86400, "WALL_SECONDS")
        integer(lim["address_space_bytes"], 64 << 20, 64 << 30, "ADDRESS_SPACE")
        integer(lim["rss_bytes"], 16 << 20, lim["address_space_bytes"], "RSS")
        integer(lim["poll_ms"], 10, 1000, "POLL_MS")
        integer(lim["max_output_bytes"], 1, 64 << 20, "OUTPUT_BYTES")
        if "expected_output_sha256" in t and not re.fullmatch("[0-9a-f]{64}", t["expected_output_sha256"]):
            raise ContractError("INVALID_EXPECTED_PAYLOAD_HASH")
    order = sorted(range(len(tasks)), key=lambda i: (-tasks[i]["cost_hint"], tasks[i]["task_id"]))
    if "dispatch_order" in doc and (type(doc["dispatch_order"]) is not list or
        any(type(i) is not int for i in doc["dispatch_order"]) or doc["dispatch_order"] != order):
        raise ContractError("DISPATCH_MUST_BE_COMPLETE_LONGEST_COST_FIRST_ORDER")
    doc["dispatch_order"] = order
    doc["_manifest_sha256"] = sha(raw)
    doc["_manifest_path"] = str(p)
    return doc


def file_identity(path, maximum=MAX_FILE):
    p = Path(path)
    before = p.stat()
    if p.is_symlink() or not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
        raise ContractError("UNSAFE_OR_OVERSIZED_FILE")
    h, n = hashlib.sha256(), 0
    with p.open("rb") as f:
        opened = os.fstat(f.fileno())
        if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            raise ContractError("FILE_CHANGED_AT_OPEN")
        while True:
            block = f.read(65536)
            if not block:
                break
            n += len(block)
            if n > maximum:
                raise ContractError("FILE_GREW_OVER_LIMIT")
            h.update(block)
    after = p.stat()
    if n != before.st_size or (before.st_ino, before.st_mtime_ns, before.st_size) != (after.st_ino, after.st_mtime_ns, after.st_size):
        raise ContractError("FILE_CHANGED_DURING_HASH")
    return {"path": str(p), "bytes": n, "sha256": h.hexdigest()}


def verify_files(task):
    total = 0
    for f in [task["executable"]] + task["inputs"] + task.get("library_pins", []):
        total += f["bytes"]
        if total > 2 << 30:
            raise ContractError("TOTAL_INPUT_HASH_BUDGET")
        got = file_identity(f["path"])
        if got != f:
            raise ContractError("INPUT_EXECUTABLE_OR_LIBRARY_IDENTITY_MISMATCH")
    if not os.access(task["executable"]["path"], os.X_OK):
        raise ContractError("EXECUTABLE_PERMISSION_REQUIRED")


def executor_identity():
    return sha(encoded({n: sha((HERE/n).read_bytes()) for n in ("core.py", "guard.py", "worker.py")}))


def task_identity(task):
    # Scheduling estimates do not change the exact payload identity.
    return sha(encoded({k: v for k, v in task.items() if k != "cost_hint"}))


def run_identity(plan):
    return {"schema": "WU088_EXACT_TASK_RUN_V1", "manifest_sha256": plan["_manifest_sha256"],
            "executor_sha256": executor_identity(), "scope": plan["scope"],
            "tasks": [{"index": i, "task_id": t["task_id"], "task_sha256": task_identity(t)}
                      for i, t in enumerate(plan["tasks"])]}


def atomic_json(path, data):
    p = Path(path)
    expected = encoded(data) + b"\n"
    fd, tmp = tempfile.mkstemp(prefix=".atomic_", dir=p.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(expected); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, p)
        dfd = os.open(p.parent, os.O_RDONLY | os.O_DIRECTORY)
        try: os.fsync(dfd)
        finally: os.close(dfd)
        if p.read_bytes() != expected:
            raise ContractError("ATOMIC_METADATA_READBACK_MISMATCH")
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


@contextmanager
def lock(path):
    p = Path(path)
    if p.is_symlink():
        raise ContractError("SYMLINK_LOCK")
    fd = os.open(p, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        try: fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc: raise ContractError("TASK_OR_RUN_BUSY") from exc
        yield
    finally:
        os.close(fd)


def initialize(plan):
    root = Path(plan["output_root"])
    root.mkdir(mode=0o700, exist_ok=True)
    if root.is_symlink() or not root.is_dir():
        raise ContractError("INVALID_RUN_ROOT")
    # Short blocking initialization avoids a false failure when MPI ranks enter together.
    init = root / "RUN.lock"
    fd = os.open(init, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        expected = run_identity(plan)
        record = root / "RUN.json"
        if record.exists():
            actual, _ = read_json(record)
            if actual != expected:
                raise ContractError("RUN_MANIFEST_OR_EXECUTOR_IDENTITY_MISMATCH")
        else:
            if any(x.name != "RUN.lock" for x in root.iterdir()):
                raise ContractError("UNBOUND_NONEMPTY_RUN_DIRECTORY")
            atomic_json(record, expected)
        for name in ("tasks", "locks"):
            p = root / name
            p.mkdir(mode=0o700, exist_ok=True)
            if p.is_symlink() or not p.is_dir():
                raise ContractError("INVALID_RUN_SUBDIRECTORY")
    finally:
        os.close(fd)
    return root, expected


def base_record(plan, index, run):
    task = plan["tasks"][index]
    return {"schema": "WU088_EXACT_TASK_CHECKPOINT_V1", "scope": plan["scope"],
            "task_index": index, "task_id": task["task_id"],
            "task_sha256": task_identity(task), "manifest_sha256": plan["_manifest_sha256"],
            "executor_sha256": run["executor_sha256"]}


def verify_complete(plan, index, run, directory):
    task = plan["tasks"][index]
    if directory.is_symlink() or not directory.is_dir():
        raise ContractError("MISSING_OR_UNSAFE_TASK_DIRECTORY")
    record, _ = read_json(directory / "checkpoint.json", 1 << 20)
    if record.get("state") != "COMPLETE" or any(record.get(k) != v for k, v in base_record(plan, index, run).items()):
        raise ContractError("PARTIAL_FAILED_OR_STALE_CHECKPOINT")
    if record.get("guard", {}).get("returncode") != 0 or record.get("guard", {}).get("reason") != "CHILD_EXIT":
        raise ContractError("COMPLETION_WITHOUT_SUCCESSFUL_CHILD")
    actual_argv = [str(directory / "work/payload.bin") if x == "OUTPUT_PATH" else x for x in task["argv"]]
    if record.get("argv") != actual_argv or record.get("env") != BASE_ENV | task["env"]:
        raise ContractError("CHECKPOINT_ARGV_ENV_MISMATCH")
    verify_files(task)
    payload = file_identity(directory / "payload.bin", task["limits"]["max_output_bytes"])
    if payload["bytes"] <= 0 or record.get("payload") != payload:
        raise ContractError("PAYLOAD_IDENTITY_MISMATCH")
    if task.get("expected_output_sha256", payload["sha256"]) != payload["sha256"]:
        raise ContractError("EXPECTED_PAYLOAD_MISMATCH")
    return record


def inconclusive(exc, **extra):
    return {"status": "INCONCLUSIVE", "reason": str(exc)[:1000], **extra}


def run_task(path, index):
    directory = record = None
    commit_attempted = False
    try:
        plan = load_manifest(path)
        integer(index, 0, len(plan["tasks"]) - 1, "TASK_INDEX")
        root, run = initialize(plan)
        task = plan["tasks"][index]
        with lock(root / "locks" / (task["task_id"] + ".lock")):
            directory = root / "tasks" / task["task_id"]
            if directory.exists():
                old = verify_complete(plan, index, run, directory)
                return {"status": "REUSED", "task_id": task["task_id"],
                        "payload_path": old["payload"]["path"], "payload_sha256": old["payload"]["sha256"]}
            directory.mkdir(mode=0o700)
            (directory / "work").mkdir(mode=0o700)
            record = base_record(plan, index, run)
            record["state"] = "RUNNING"
            atomic_json(directory / "checkpoint.json", record)
            verify_files(task)
            argv = [str(directory / "work/payload.bin") if x == "OUTPUT_PATH" else x for x in task["argv"]]
            env = BASE_ENV | task["env"]
            record["argv"], record["env"] = argv, env
            record["guard"] = guard.run(argv, str(directory / "work"), env, task["limits"],
                                        directory / "stdout.log", directory / "stderr.log")
            if record["guard"]["reason"] != "CHILD_EXIT" or record["guard"]["returncode"] != 0:
                raise ContractError("BACKEND_INCONCLUSIVE:" + record["guard"]["reason"])
            verify_files(task)
            source = directory / "work/payload.bin"
            payload = file_identity(source, task["limits"]["max_output_bytes"])
            if not payload["bytes"]:
                raise ContractError("EMPTY_PAYLOAD")
            if task.get("expected_output_sha256", payload["sha256"]) != payload["sha256"]:
                raise ContractError("EXPECTED_PAYLOAD_MISMATCH")
            with source.open("rb") as f: os.fsync(f.fileno())
            destination = directory / "payload.bin"
            os.replace(source, destination)
            payload["path"] = str(destination)
            record["payload"] = payload
            record["state"] = "COMPLETE"
            commit_attempted = True
            atomic_json(directory / "checkpoint.json", record)
            readback, _ = read_json(directory / "checkpoint.json", 1 << 20)
            if readback != record or file_identity(destination, task["limits"]["max_output_bytes"]) != payload:
                raise ContractError("CHECKPOINT_FINAL_READBACK_MISMATCH")
            return {"status": "COMPLETE", "task_id": task["task_id"],
                    "payload_path": str(destination), "payload_sha256": payload["sha256"],
                    "guard": record["guard"]}
    except (ContractError, OSError, ValueError, KeyError, TypeError) as exc:
        if record is not None and directory is not None and not commit_attempted:
            record["state"], record["reason"] = "INCONCLUSIVE", str(exc)[:1000]
            try:
                atomic_json(directory / "checkpoint.json", record)
            except (ContractError, OSError) as storage_error:
                record["checkpoint_write_error"] = str(storage_error)[:500]
        return inconclusive(exc, **({"guard": record["guard"]} if record and "guard" in record else {}))


def prepare_manifest(path):
    try:
        plan = load_manifest(path)
        root, run = initialize(plan)
        expected = {t["task_id"] for t in plan["tasks"]}
        if any(p.name not in expected for p in (root / "tasks").iterdir()):
            raise ContractError("EXTRA_OR_DUPLICATED_TASK_DIRECTORY")
        complete, missing = [], []
        for i, t in enumerate(plan["tasks"]):
            directory = root / "tasks" / t["task_id"]
            if directory.exists():
                with lock(root / "locks" / (t["task_id"] + ".lock")):
                    verify_complete(plan, i, run, directory)
                complete.append(i)
            else: missing.append(i)
        return {"status": "READY", "complete_indices": complete, "missing_indices": missing,
                "dispatch_order": plan["dispatch_order"], "manifest_sha256": plan["_manifest_sha256"]}
    except (ContractError, OSError, ValueError, KeyError, TypeError) as exc:
        return inconclusive(exc)


def collect(path):
    try:
        plan = load_manifest(path)
        root, run = initialize(plan)
        if {p.name for p in (root / "tasks").iterdir()} != {t["task_id"] for t in plan["tasks"]}:
            raise ContractError("MISSING_EXTRA_OR_DUPLICATED_TASK_SET")
        records = []
        for i, t in sorted(enumerate(plan["tasks"]), key=lambda pair: pair[1]["task_id"]):
            with lock(root / "locks" / (t["task_id"] + ".lock")):
                r = verify_complete(plan, i, run, root / "tasks" / t["task_id"])
            records.append({"task_id": t["task_id"], "task_sha256": r["task_sha256"],
                            "payload_sha256": r["payload"]["sha256"], "payload_bytes": r["payload"]["bytes"],
                            "payload_path": r["payload"]["path"]})
        canonical = [{k: v for k, v in r.items() if k != "payload_path"} for r in records]
        result = {"schema": "WU088_EXACT_TASK_COLLECTION_V1", "status": "COLLECTED",
                  "scope": "SYNTHETIC_ONLY", "declared_task_count": len(plan["tasks"]),
                  "complete_task_count": len(records), "manifest_sha256": plan["_manifest_sha256"],
                  "executor_sha256": run["executor_sha256"], "tasks": records,
                  "canonical_payload_digest": sha(encoded(canonical)),
                  "floating_reduction_performed": False, "payload_reserialized": False,
                  "scientific_validity_inferred": False}
        atomic_json(root / "COLLECTION.json", result)
        return result
    except (ContractError, OSError, ValueError, KeyError, TypeError) as exc:
        return inconclusive(exc)
