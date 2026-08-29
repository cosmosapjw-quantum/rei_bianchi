#!/usr/bin/env python3
"""Fresh-process three-lane adaptive supervisor with authenticated resume."""
from __future__ import annotations

import argparse
import array
import fcntl
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import secrets
import shutil
import signal
import stat
import struct
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent
REPO = STAGE.parents[1]
INPUT_LOCK = STAGE / "INPUT_LOCK.json"
DEFAULT_WORKER = HERE / "attempt_worker.py"
KERNEL = REPO / "stages" / (
    "Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_"
    "R1_R1_R1_R1_R1_CROSS_SITE_STATE_FEEDBACK_REMAINDER_AND_TABLE_EVENT_LOCK"
) / "analysis" / "interval_discrete_map.py"
THREAD_LIMITS = (
    "BLIS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
PREFLIGHT_CHECK_NAMES = (
    "git_head_readable",
    "tracked_worktree_clean",
    "integration_commit_is_ancestor",
    "predecessor_sha256sums",
    "predecessor_payloads_verify",
    "current_stage_payloads_verify",
    "predecessor_bundle_sha256",
    "predecessor_bundle_size",
    "predecessor_bundle_crc",
    "runtime_dependencies",
    "jax_absent_import_guard_required",
    "memory_for_three_workers",
    "runtime_contract_closed",
)
STATE_MAGIC = b"REIADP1\0"
HEADER_LENGTH = struct.Struct("<Q")
STATE_ARRAY_ORDER = (
    "population_lower",
    "population_upper",
    "log_temperature_lower",
    "log_temperature_upper",
)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


policy = _load("adaptive_history_supervisor_policy", HERE / "adaptive_policy.py")
runtime_contract = _load(
    "adaptive_history_supervisor_runtime_contract", HERE / "runtime_contract.py"
)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _pairs_no_duplicates(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def read_json(path: Path) -> Any:
    def reject_constant(value):
        raise ValueError(f"nonfinite JSON constant: {value}")

    return json.loads(
        Path(path).read_text(encoding="utf-8"),
        object_pairs_hook=_pairs_no_duplicates,
        parse_constant=reject_constant,
    )


def _fsync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_write(path: Path, payload: bytes) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{target.name}.tmp-",
            dir=target.parent,
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
        temporary = None
        _fsync_dir(target.parent)
    finally:
        if temporary is not None and temporary.is_file():
            temporary.unlink()


def atomic_json(path: Path, value: Any) -> None:
    atomic_write(path, canonical(value) + b"\n")


def immutable_write(path: Path, payload: bytes) -> None:
    target = Path(path)
    if target.exists():
        if target.is_file() and target.read_bytes() == payload:
            return
        raise FileExistsError(f"immutable payload collision: {target}")
    atomic_write(target, payload)


def _safe_rmtree(path: Path, root: Path) -> None:
    path = Path(path).resolve()
    root = Path(root).resolve()
    if path.parent != root or path == root or path.name in ("", ".", ".."):
        raise ValueError(f"refusing unsafe cleanup: {path}")
    if path.exists():
        shutil.rmtree(path)


def _copy(source: Path, destination: Path) -> str:
    if source.is_symlink() or not source.is_file():
        raise ValueError(f"invalid copy source: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as reader, destination.open("xb") as writer:
        shutil.copyfileobj(reader, writer, 1024 * 1024)
        writer.flush()
        os.fsync(writer.fileno())
    _fsync_dir(destination.parent)
    return sha_file(destination)


def _bounded_text(value: Any, limit: int = 65536) -> str:
    if value is None:
        text = ""
    elif isinstance(value, bytes):
        text = value.decode("utf-8", errors="replace")
    else:
        text = str(value)
    if len(text) > limit:
        text = text[:limit] + "\n...[truncated]"
    return text


def _task_dict(task) -> dict[str, int] | None:
    return None if task is None else task.as_dict()


def _task_load(value):
    if value is None:
        return None
    if (
        not isinstance(value, dict)
        or set(value) != {"depth", "left_tick", "right_tick"}
        or not all(type(value[name]) is int for name in value)
    ):
        raise ValueError("task must be an object")
    task = policy.IntervalTask(
        value["left_tick"], value["right_tick"], value["depth"]
    )
    if task.as_dict() != value:
        raise ValueError("noncanonical task")
    return task


def _cursor_dict(cursor) -> dict[str, Any]:
    return {
        "accepted_index": cursor.accepted_index,
        "accepted_tick": cursor.accepted_tick,
        "current": _task_dict(cursor.current),
        "pending": [_task_dict(task) for task in cursor.pending],
    }


def _cursor_load(value):
    if not isinstance(value, dict) or set(value) != {
        "accepted_index",
        "accepted_tick",
        "current",
        "pending",
    }:
        raise ValueError("invalid cursor schema")
    if not isinstance(value["pending"], list):
        raise ValueError("pending cursor tasks must be a list")
    if type(value["accepted_index"]) is not int or type(value["accepted_tick"]) is not int:
        raise ValueError("cursor counters must be canonical integers")
    cursor = policy.Cursor(
        value["accepted_index"],
        value["accepted_tick"],
        _task_load(value["current"]),
        tuple(_task_load(item) for item in value["pending"]),
    )
    if _cursor_dict(cursor) != value:
        raise ValueError("noncanonical cursor")
    return policy.validate_cursor(cursor)


def _relative_path(run_dir: Path, value: Any, *, prefix: str | None = None) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("invalid relative run path")
    relative = Path(value)
    if relative.is_absolute() or any(part in ("", ".", "..") for part in relative.parts):
        raise ValueError("run path must be canonical and relative")
    if relative.as_posix() != value:
        raise ValueError("noncanonical run path")
    if prefix is not None and not value.startswith(prefix):
        raise ValueError("run path has the wrong prefix")
    resolved = (run_dir / relative).resolve()
    if run_dir.resolve() not in resolved.parents:
        raise ValueError("run path escapes the owned directory")
    return resolved


def inspect_state(
    path: Path,
    *,
    expected_sha256: str,
    expected_size: int,
    expected_metadata: dict[str, Any],
    node_count: int = policy.STATE_NODE_COUNT,
) -> dict[str, Any]:
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("candidate state is not a regular file")
    expected_body = (2 * node_count * 5 + 2 * node_count) * 8
    if (
        not isinstance(expected_size, int)
        or expected_size < expected_body + len(STATE_MAGIC) + HEADER_LENGTH.size
        or expected_size > expected_body + 65536
        or path.stat().st_size != expected_size
    ):
        raise ValueError("candidate state has an impossible size")
    payload = path.read_bytes()
    if len(payload) != expected_size or sha_bytes(payload) != expected_sha256:
        raise ValueError("candidate state size or SHA-256 mismatch")
    prefix = len(STATE_MAGIC) + HEADER_LENGTH.size
    if len(payload) < prefix or payload[: len(STATE_MAGIC)] != STATE_MAGIC:
        raise ValueError("invalid state magic")
    (header_length,) = HEADER_LENGTH.unpack(payload[len(STATE_MAGIC) : prefix])
    end = prefix + header_length
    if end > len(payload):
        raise ValueError("truncated state header")
    try:
        header = json.loads(
            payload[prefix:end].decode("ascii"),
            object_pairs_hook=_pairs_no_duplicates,
        )
    except Exception as error:
        raise ValueError("invalid state header") from error
    expected_header = {
        "array_order": list(STATE_ARRAY_ORDER),
        "byte_order": "little",
        "dtype": "float64",
        "log_temperature_shape": [node_count],
        "metadata": expected_metadata,
        "population_shape": [node_count, 5],
        "schema": 1,
    }
    if header != expected_header:
        raise ValueError("state header or metadata mismatch")
    population_count = node_count * 5
    temperature_count = node_count
    expected_body = (2 * population_count + 2 * temperature_count) * 8
    if len(payload) - end != expected_body:
        raise ValueError("state array length mismatch")
    values = array.array("d")
    values.frombytes(payload[end:])
    if sys.byteorder != "little":
        values.byteswap()
    population_upper = population_count
    temperature_lower = 2 * population_count
    temperature_upper = temperature_lower + temperature_count
    for index in range(population_count):
        lower = values[index]
        upper = values[population_upper + index]
        if not math.isfinite(lower) or not math.isfinite(upper) or lower <= 0 or lower > upper:
            raise ValueError("invalid population interval in candidate state")
    for index in range(temperature_count):
        lower = values[temperature_lower + index]
        upper = values[temperature_upper + index]
        if not math.isfinite(lower) or not math.isfinite(upper) or lower > upper:
            raise ValueError("invalid temperature interval in candidate state")
    return header


class RunLock:
    """Persistent nonblocking process lock stored inside one run directory."""

    def __init__(self, run_dir: Path, *, create: bool = False) -> None:
        self.run_dir = Path(run_dir).resolve()
        self.create = create
        self.fd: int | None = None

    def acquire(self) -> "RunLock":
        if self.fd is not None:
            return self
        if self.create:
            self.run_dir.mkdir(parents=True, exist_ok=True)
        elif not self.run_dir.is_dir():
            raise FileNotFoundError(f"run directory does not exist: {self.run_dir}")
        flags = os.O_RDWR | getattr(os, "O_CLOEXEC", 0)
        if self.create:
            flags |= os.O_CREAT
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            fd = os.open(self.run_dir / ".RUN.lock", flags, 0o600)
        except FileNotFoundError as error:
            raise FileNotFoundError(
                f"owned run lock is missing: {self.run_dir / '.RUN.lock'}"
            ) from error
        os.set_inheritable(fd, False)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            os.close(fd)
            raise RuntimeError(
                f"run directory already has an active coordinator: {self.run_dir}"
            ) from error
        self.fd = fd
        try:
            self.identity()
        except BaseException:
            self.fd = None
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)
            raise
        return self

    def identity(self) -> dict[str, int]:
        if self.fd is None:
            raise RuntimeError("run lock is not held")
        descriptor = os.fstat(self.fd)
        path = os.lstat(self.run_dir / ".RUN.lock")
        if (
            not stat.S_ISREG(descriptor.st_mode)
            or not stat.S_ISREG(path.st_mode)
            or descriptor.st_nlink != 1
            or path.st_nlink != 1
            or (descriptor.st_dev, descriptor.st_ino) != (path.st_dev, path.st_ino)
        ):
            raise ValueError("owned run lock identity changed")
        return {"device": descriptor.st_dev, "inode": descriptor.st_ino}

    def close(self) -> None:
        fd = self.fd
        if fd is None:
            return
        self.fd = None
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)

    def __enter__(self) -> "RunLock":
        return self.acquire()

    def __exit__(self, _type, _value, _traceback) -> None:
        self.close()


class Coordinator:
    def __init__(
        self,
        *,
        run_dir: Path,
        workers: int = 3,
        worker_timeout: float = 900.0,
        worker_script: Path = DEFAULT_WORKER,
        worker_environment: dict[str, str] | None = None,
        resume: bool = False,
        progress: Callable[[dict[str, Any]], None] | None = None,
        runtime_contract_value: dict[str, Any] | None = None,
        _test_mode: bool = False,
        _repair: bool = True,
        _held_run_lock: RunLock | None = None,
    ) -> None:
        self.run_dir = Path(run_dir).resolve()
        self.workers = int(workers)
        self.worker_timeout = float(worker_timeout)
        self.worker_script = Path(worker_script).resolve()
        self.worker_environment = dict(worker_environment or {})
        self.progress = progress
        self.test_mode = _test_mode
        self.repair_mode = _repair
        self.preflight_sha: str | None = None
        if not isinstance(self.test_mode, bool) or not isinstance(self.repair_mode, bool):
            raise TypeError("_test_mode and _repair must be boolean")
        if self.test_mode:
            if runtime_contract_value is None or self.worker_script == DEFAULT_WORKER.resolve():
                raise ValueError("test mode requires an injected runtime and nonproduction worker")
            self.run_classification = "TEST_ONLY_NOT_SCIENCE"
        else:
            if (
                runtime_contract_value is not None
                or self.worker_script != DEFAULT_WORKER.resolve()
                or self.worker_environment
            ):
                raise ValueError("production execution forbids test runtime, worker, or environment injection")
            self.run_classification = "CANDIDATE_UNSEALED_LOCAL_EXECUTION"
        if not 1 <= self.workers <= 3 or self.worker_timeout <= 0:
            raise ValueError("invalid workers/timeout")
        if not self.worker_script.is_file():
            raise FileNotFoundError(self.worker_script)
        self.input_sha = sha_file(INPUT_LOCK)
        self.kernel_sha = sha_file(KERNEL)
        self.runtime = (
            dict(runtime_contract_value)
            if runtime_contract_value is not None
            else runtime_contract.build(REPO, STAGE)
        )
        self.runtime_sha = self.runtime.get("sha256")
        if not isinstance(self.runtime_sha, str) or len(self.runtime_sha) != 64:
            raise ValueError("invalid runtime contract")
        if not self.test_mode:
            files = self.runtime.get("files")
            if (
                not isinstance(files, dict)
                or files.get("analysis/attempt_worker.py") != sha_file(self.worker_script)
            ):
                raise ValueError("production worker does not match the runtime contract")
        self.marker = self.run_dir / "RUN_OWNER.json"
        self.control = self.run_dir / "CONTROL.json"
        self.latest = self.run_dir / "checkpoints" / "LATEST.json"
        self._lock_fd: int | None = None
        self._run_lock: RunLock | None = None
        self._owns_run_lock = False
        if _held_run_lock is not None:
            if (
                not isinstance(_held_run_lock, RunLock)
                or _held_run_lock.run_dir != self.run_dir
                or _held_run_lock.fd is None
            ):
                raise ValueError("borrowed run lock does not match the run directory")
            self._run_lock = _held_run_lock
            self._lock_fd = _held_run_lock.fd
            _held_run_lock.identity()
        else:
            self._acquire_run_lock(resume=resume)
        try:
            self._prepare_owned_directory(resume)
            for directory in (
                "checkpoints/generations",
                "checkpoints/snapshots",
                "data",
                "history",
                "history/transitions",
                "receipts",
                "work",
            ):
                path = self.run_dir / directory
                if self.repair_mode:
                    path.mkdir(parents=True, exist_ok=True)
                elif path.is_symlink() or not path.is_dir():
                    raise ValueError("validate-only run is missing a required directory")
            if resume and self._recover_incomplete_initialization():
                pass
            elif resume:
                self._validate_run_metadata()
                self._load()
            else:
                self._initialize_control_state()
        except BaseException:
            self.close()
            raise

    def _acquire_run_lock(self, *, resume: bool) -> None:
        marker_exists = (self.run_dir / "RUN_OWNER.json").exists()
        if not resume and not marker_exists and self.run_dir.exists():
            if not self.run_dir.is_dir():
                raise ValueError(f"run path is not a directory: {self.run_dir}")
            allowed = {".RUN.lock", "preflight.json"}
            if any(path.name not in allowed for path in self.run_dir.iterdir()):
                raise ValueError("new run directory contains foreign entries")
        lock = RunLock(self.run_dir, create=not resume and not marker_exists).acquire()
        self._run_lock = lock
        self._owns_run_lock = True
        self._lock_fd = lock.fd

    def close(self) -> None:
        lock = getattr(self, "_run_lock", None)
        if lock is None:
            return
        owns = getattr(self, "_owns_run_lock", False)
        self._run_lock = None
        self._lock_fd = None
        if owns:
            lock.close()

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def _run_metadata_value(self) -> dict[str, Any]:
        return {
            "classification": self.run_classification,
            "input_lock_sha256": self.input_sha,
            "lane_order": list(policy.LANE_ORDER),
            "predecessor_kernel_sha256": self.kernel_sha,
            "preflight_sha256": self.preflight_sha,
            "process_model": "fresh process per lane attempt",
            "run_id": self.run_id,
            "runtime_contract": self.runtime,
            "stage_id": policy.STAGE_ID,
            "thread_limits": {name: "1" for name in THREAD_LIMITS},
            "workers": self.workers,
        }

    def _initialize_control_state(self) -> None:
        metadata_path = self.run_dir / "RUN_METADATA.json"
        metadata = self._run_metadata_value()
        if metadata_path.exists():
            if metadata_path.is_symlink() or read_json(metadata_path) != metadata:
                raise ValueError("initial run metadata mismatch")
        else:
            immutable_write(metadata_path, canonical(metadata) + b"\n")
        self.cursor = policy.initial_cursor()
        self.states = {lane: None for lane in policy.LANE_ORDER}
        self.record_sha = None
        self.generation = None
        self.attempts = 0
        self.rejects = 0
        self.transition = 0
        self.transition_sha = None
        self.owned_generations = []
        self.status = "READY"
        self._persist("READY", initial=True, action="INITIAL")

    def _validate_run_metadata(self) -> None:
        path = self.run_dir / "RUN_METADATA.json"
        if path.is_symlink() or not path.is_file():
            raise ValueError("run metadata is missing or not a regular file")
        observed = read_json(path)
        expected = self._run_metadata_value()
        workers = observed.get("workers") if isinstance(observed, dict) else None
        expected["workers"] = workers
        if type(workers) is not int or not 1 <= workers <= 3 or observed != expected:
            raise ValueError("run metadata does not match the owned runtime")

    def _recover_incomplete_initialization(self) -> bool:
        transitions = self.run_dir / "history" / "transitions"
        if any(path.name.startswith("transition_") for path in transitions.iterdir()):
            return False
        if self.control.exists() or self.latest.exists():
            return False
        if not self.repair_mode:
            raise ValueError("incomplete initialization requires runner repair")
        expected_root = {
            ".RUN.lock",
            "RUN_METADATA.json",
            "RUN_OWNER.json",
            "checkpoints",
            "data",
            "history",
            "preflight.json",
            "receipts",
            "work",
        }
        observed_root = {path.name for path in self.run_dir.iterdir()}
        if not observed_root <= expected_root:
            raise ValueError("foreign entry in incomplete owned initialization")
        if not self.test_mode and "preflight.json" not in observed_root:
            raise ValueError("incomplete production initialization lacks preflight")
        if {path.name for path in (self.run_dir / "checkpoints").iterdir()} != {
            "generations",
            "snapshots",
        }:
            raise ValueError("foreign checkpoint entry in incomplete initialization")
        empty_directories = (
            self.run_dir / "checkpoints" / "generations",
            self.run_dir / "checkpoints" / "snapshots",
            self.run_dir / "data",
            self.run_dir / "receipts",
            self.run_dir / "work",
        )
        if any(any(directory.iterdir()) for directory in empty_directories):
            raise ValueError("incomplete initialization already contains run evidence")
        if {path.name for path in (self.run_dir / "history").iterdir()} != {
            "transitions"
        }:
            raise ValueError("incomplete initialization contains history")
        temporary_entries = list(transitions.iterdir())
        for path in temporary_entries:
            if (
                not re.fullmatch(
                    r"\.transition_[0-9]{8}\.json\.tmp-[A-Za-z0-9_-]+",
                    path.name,
                )
                or path.is_symlink()
                or not path.is_file()
                or not self.repair_mode
            ):
                raise ValueError("invalid incomplete transition temporary")
            path.unlink()
        if temporary_entries:
            _fsync_dir(transitions)
        self._initialize_control_state()
        return True

    def _prepare_owned_directory(self, resume: bool) -> None:
        if self.repair_mode:
            self.run_dir.mkdir(parents=True, exist_ok=True)
        elif not self.run_dir.is_dir():
            raise ValueError("validate-only run directory is missing")
        if self.marker.exists():
            if self.marker.is_symlink() or not self.marker.is_file():
                raise ValueError("invalid run ownership marker type")
            self._validate_preflight()
            marker = read_json(self.marker)
            expected = {
                "marker_schema": 1,
                "preflight_sha256": self.preflight_sha,
                "run_classification": self.run_classification,
                "run_id": marker.get("run_id") if isinstance(marker, dict) else None,
                "run_lock": self._run_lock.identity(),
                "runtime_contract_sha256": self.runtime_sha,
                "stage_id": policy.STAGE_ID,
            }
            if marker != expected or not isinstance(expected["run_id"], str) or len(expected["run_id"]) != 32:
                raise ValueError("invalid or foreign run ownership marker")
            self.run_id = expected["run_id"]
            if not resume:
                raise FileExistsError(f"owned run exists; pass resume=True: {self.run_dir}")
            return
        if resume:
            raise FileNotFoundError("cannot resume without RUN_OWNER.json")
        entries = [
            path
            for path in self.run_dir.iterdir()
            if path.name not in {".RUN.lock", "preflight.json"}
        ]
        if entries:
            raise ValueError("new run directory must be empty or contain only preflight.json")
        self._validate_preflight()
        self.run_id = secrets.token_hex(16)
        atomic_json(
            self.marker,
            {
                "marker_schema": 1,
                "preflight_sha256": self.preflight_sha,
                "run_classification": self.run_classification,
                "run_id": self.run_id,
                "run_lock": self._run_lock.identity(),
                "runtime_contract_sha256": self.runtime_sha,
                "stage_id": policy.STAGE_ID,
            },
        )

    def _validate_preflight(self) -> None:
        preflight = self.run_dir / "preflight.json"
        if self.test_mode and not preflight.exists():
            self.preflight_sha = None
            return
        if preflight.is_symlink() or not preflight.is_file():
            raise ValueError("production run requires a regular preflight receipt")
        value = read_json(preflight)
        expected_keys = {
            "all_passed",
            "calculation_started",
            "checks",
            "classification",
            "environment",
            "runtime_contract_sha256",
            "stage_id",
        }
        checks = value.get("checks") if isinstance(value, dict) else None
        environment = value.get("environment") if isinstance(value, dict) else None
        if (
            not isinstance(value, dict)
            or set(value) != expected_keys
            or value.get("all_passed") is not True
            or value.get("calculation_started") is not False
            or value.get("classification") != "PREFLIGHT_ONLY_NO_SCIENCE_RESULT"
            or value.get("stage_id") != policy.STAGE_ID
            or value.get("runtime_contract_sha256") != self.runtime_sha
            or not isinstance(checks, list)
            or tuple(
                check.get("name") if isinstance(check, dict) else None
                for check in checks
            )
            != PREFLIGHT_CHECK_NAMES
            or any(
                set(check) != {"expected", "name", "observed", "passed"}
                or check["passed"] is not True
                for check in checks
            )
            or not isinstance(environment, dict)
            or set(environment) != {"machine", "platform", "python"}
            or not all(isinstance(value, str) and value for value in environment.values())
        ):
            raise ValueError("preflight receipt does not match this runtime")
        self.preflight_sha = sha_file(preflight)

    def _control_value(self, status: str) -> dict[str, Any]:
        value = self._control_base(status)
        value["latest_transition_sha256"] = self.transition_sha
        return value

    def _control_base(self, status: str) -> dict[str, Any]:
        return {
            "attempted_endpoints": self.attempts,
            "classification": self.run_classification,
            "cursor": _cursor_dict(self.cursor),
            "input_lock_sha256": self.input_sha,
            "latest_generation": self.generation,
            "latest_record_sha256": self.record_sha,
            "owned_generations": list(self.owned_generations),
            "parent_states": self.states,
            "predecessor_kernel_sha256": self.kernel_sha,
            "preflight_sha256": self.preflight_sha,
            "rejected_attempts": self.rejects,
            "run_id": self.run_id,
            "runtime_contract_sha256": self.runtime_sha,
            "schema": 1,
            "stage_id": policy.STAGE_ID,
            "status": status,
            "transition_number": self.transition,
        }

    def _latest_value(self, control: dict[str, Any]) -> dict[str, Any]:
        return self._latest_for_control(control)

    def _latest_for_control(self, control: dict[str, Any]) -> dict[str, Any]:
        cursor = _cursor_load(control["cursor"])
        return {
            "accepted_index": cursor.accepted_index,
            "accepted_tick": cursor.accepted_tick,
            "classification": control["classification"],
            "control_state": control,
            "latest_generation": control["latest_generation"],
            "latest_transition_sha256": control["latest_transition_sha256"],
            "record_path": None if control["latest_generation"] is None else f"{control['latest_generation']}/record.json",
            "record_sha256": control["latest_record_sha256"],
            "run_id": control["run_id"],
            "runtime_contract_sha256": control["runtime_contract_sha256"],
            "schema": 1,
            "stage_id": control["stage_id"],
            "states": control["parent_states"],
            "transition_number": control["transition_number"],
        }

    def _persist(
        self,
        status: str,
        *,
        initial: bool = False,
        action: str,
        evidence: dict[str, str] | None = None,
    ) -> None:
        policy.validate_cursor(self.cursor)
        if not initial:
            self.transition += 1
        self.status = status
        base = self._control_base(status)
        transition = {
            "action": action,
            "control_state": base,
            "evidence": dict(evidence or {}),
            "previous_transition_sha256": self.transition_sha,
            "transition_number": self.transition,
            "transition_schema": 1,
        }
        payload = canonical(transition) + b"\n"
        transition_path = (
            self.run_dir
            / "history"
            / "transitions"
            / f"transition_{self.transition:08d}.json"
        )
        immutable_write(transition_path, payload)
        self.transition_sha = sha_bytes(payload)
        control = self._control_value(status)
        atomic_json(self.latest, self._latest_value(control))
        atomic_json(self.control, control)

    def _validate_generation_owner(self, directory: Path, relative: str) -> None:
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError("generation is not an owned directory")
        owner = read_json(directory / "GENERATION_OWNER.json")
        expected = {
            "generation": relative,
            "owner_schema": 1,
            "run_id": self.run_id,
            "runtime_contract_sha256": self.runtime_sha,
            "stage_id": policy.STAGE_ID,
        }
        if owner != expected:
            raise ValueError("generation ownership mismatch")

    def _validate_history_chain(
        self, accepted_index: int, *, allow_unpublished: bool = False
    ) -> tuple[str | None, int]:
        prior_sha = None
        prior_tick = 0
        expected_parents = {lane: "INITIAL" for lane in policy.LANE_ORDER}
        history_root = self.run_dir / "history"
        expected_names = {f"accepted_{index:08d}.json" for index in range(1, accepted_index + 1)}
        observed_names = {path.name for path in history_root.glob("accepted_*.json") if path.is_file()}
        allowed_name_sets = [expected_names]
        if allow_unpublished:
            allowed_name_sets.append(
                expected_names | {f"accepted_{accepted_index + 1:08d}.json"}
            )
        if observed_names not in allowed_name_sets:
            raise ValueError("history record set mismatch")
        for index in range(1, accepted_index + 1):
            path = history_root / f"accepted_{index:08d}.json"
            record_bytes = path.read_bytes()
            record = read_json(path)
            if record.get("accepted_index") != index or record.get("previous_record_sha256") != prior_sha:
                raise ValueError("history hash-chain mismatch")
            if record.get("record_schema") != 1 or record.get("stage_id") != policy.STAGE_ID:
                raise ValueError("history schema mismatch")
            if record.get("input_lock_sha256") != self.input_sha or record.get("predecessor_kernel_sha256") != self.kernel_sha or record.get("runtime_contract_sha256") != self.runtime_sha:
                raise ValueError("history provenance mismatch")
            task = _task_load(record.get("interval"))
            if task is None or task.left_tick != prior_tick:
                raise ValueError("history interval discontinuity")
            cursor_after = _cursor_load(record.get("cursor_after"))
            if cursor_after.accepted_index != index or cursor_after.accepted_tick != task.right_tick:
                raise ValueError("history cursor mismatch")
            lanes = record.get("lanes")
            if not isinstance(lanes, dict) or set(lanes) != set(policy.LANE_ORDER):
                raise ValueError("history lane set mismatch")
            parents = {lane: lanes[lane].get("parent_state_sha256") for lane in policy.LANE_ORDER}
            if parents != expected_parents:
                raise ValueError("history parent state chain mismatch")
            decision = policy.validate_and_decide(
                task=task,
                accepted_index=index,
                parent_state_sha256=parents,
                input_lock_sha256=self.input_sha,
                predecessor_kernel_sha256=self.kernel_sha,
                runtime_contract_sha256=self.runtime_sha,
                envelopes=lanes.values(),
            )
            if decision.action != "ACCEPT":
                raise ValueError("history contains a nonaccepted record")
            expected_parents = {
                lane: lanes[lane]["candidate_state"]["sha256"]
                for lane in policy.LANE_ORDER
            }
            prior_sha = sha_bytes(record_bytes)
            prior_tick = task.right_tick
        return prior_sha, prior_tick

    def _validate_loaded_state(
        self,
        control: dict[str, Any],
        latest: dict[str, Any],
        *,
        allow_unpublished: bool = False,
    ) -> None:
        cursor = self.cursor
        if latest != self._latest_value(control):
            raise ValueError("LATEST does not canonically mirror CONTROL")
        if cursor.accepted_index == 0:
            if self.generation is not None or self.record_sha is not None or any(value is not None for value in self.states.values()):
                raise ValueError("initial cursor published accepted state")
            chain_sha, chain_tick = self._validate_history_chain(
                0, allow_unpublished=allow_unpublished
            )
            if chain_sha is not None or chain_tick != 0:
                raise ValueError("initial history mismatch")
            return
        expected_generation = f"generations/g-{cursor.accepted_index:08d}-tick-{cursor.accepted_tick:06d}"
        if self.generation != expected_generation or self.generation not in self.owned_generations:
            raise ValueError("latest generation identity mismatch")
        generation = _relative_path(self.run_dir / "checkpoints", self.generation, prefix="generations/g-")
        self._validate_generation_owner(generation, self.generation)
        record_path = generation / "record.json"
        if sha_file(record_path) != self.record_sha:
            raise ValueError("latest record hash mismatch")
        chain_sha, chain_tick = self._validate_history_chain(
            cursor.accepted_index, allow_unpublished=allow_unpublished
        )
        if chain_sha != self.record_sha or chain_tick != cursor.accepted_tick:
            raise ValueError("latest record/history mismatch")
        record = read_json(record_path)
        if record != read_json(self.run_dir / "history" / f"accepted_{cursor.accepted_index:08d}.json"):
            raise ValueError("latest generation/history payload mismatch")
        for lane in policy.LANE_ORDER:
            state = self.states.get(lane)
            expected_relative = f"checkpoints/{self.generation}/{lane}.state"
            if not isinstance(state, dict) or state.get("path") != expected_relative:
                raise ValueError(f"latest state path mismatch for lane {lane}")
            if record["lanes"][lane].get("candidate_state") != state:
                raise ValueError(f"record/state reference mismatch for lane {lane}")
            state_path = _relative_path(self.run_dir, state["path"], prefix="checkpoints/generations/g-")
            metadata = {
                "accepted_index": cursor.accepted_index,
                "endpoint_tick": cursor.accepted_tick,
                "input_lock_sha256": self.input_sha,
                "job_key": record["lanes"][lane]["job_key"],
                "lane": lane,
                "parent_state_sha256": record["lanes"][lane]["parent_state_sha256"],
                "predecessor_kernel_sha256": self.kernel_sha,
                "runtime_contract_sha256": self.runtime_sha,
                "stage_id": policy.STAGE_ID,
            }
            inspect_state(
                state_path,
                expected_sha256=state["sha256"],
                expected_size=state["size_bytes"],
                expected_metadata=metadata,
            )

    def _validate_snapshots(self) -> None:
        root = self.run_dir / "checkpoints" / "snapshots"
        expected_indices = {
            index for index in range(1, self.cursor.accepted_index + 1) if index % 64 == 0
        }
        if self.cursor.current is None and self.cursor.accepted_index:
            expected_indices.add(self.cursor.accepted_index)
        observed = {}
        for path in list(root.iterdir()):
            if path.is_symlink() or not path.is_dir():
                raise ValueError("foreign snapshot entry")
            if path.name.startswith("."):
                owner_path = path / "TEMPORARY_OWNER.json"
                owner = read_json(owner_path) if owner_path.is_file() else None
                expected_name = owner.get("generation_name") if isinstance(owner, dict) else None
                if (
                    not isinstance(expected_name, str)
                    or not path.name.startswith(f".{expected_name}.tmp-")
                    or owner != self._temporary_owner(expected_name)
                ):
                    raise ValueError("foreign temporary snapshot")
                if not self.repair_mode:
                    raise ValueError("temporary snapshot requires runner repair")
                _safe_rmtree(path, root)
                continue
            if not path.name.startswith("g-"):
                raise ValueError("foreign snapshot entry")
            record = read_json(path / "record.json")
            index = record.get("accepted_index")
            tick = record.get("interval", {}).get("right_tick") if isinstance(record.get("interval"), dict) else None
            if not isinstance(index, int) or not isinstance(tick, int) or path.name != f"g-{index:08d}-tick-{tick:06d}":
                raise ValueError("snapshot name/record mismatch")
            if index in observed:
                raise ValueError("duplicate snapshot index")
            observed[index] = path
            relative = f"generations/{path.name}"
            self._validate_generation_owner(path, relative)
            history = self.run_dir / "history" / f"accepted_{index:08d}.json"
            if not history.is_file() or path.joinpath("record.json").read_bytes() != history.read_bytes():
                raise ValueError("snapshot/history mismatch")
            for lane in policy.LANE_ORDER:
                reference = record["lanes"][lane]["candidate_state"]
                metadata = {
                    "accepted_index": index,
                    "endpoint_tick": tick,
                    "input_lock_sha256": self.input_sha,
                    "job_key": record["lanes"][lane]["job_key"],
                    "lane": lane,
                    "parent_state_sha256": record["lanes"][lane]["parent_state_sha256"],
                    "predecessor_kernel_sha256": self.kernel_sha,
                    "runtime_contract_sha256": self.runtime_sha,
                    "stage_id": policy.STAGE_ID,
                }
                inspect_state(
                    path / f"{lane}.state",
                    expected_sha256=reference["sha256"],
                    expected_size=reference["size_bytes"],
                    expected_metadata=metadata,
                )
        if set(observed) != expected_indices:
            raise ValueError("snapshot set mismatch")

    def _validate_control_base(self, control: Any, number: int):
        expected_keys = {
            "attempted_endpoints",
            "classification",
            "cursor",
            "input_lock_sha256",
            "latest_generation",
            "latest_record_sha256",
            "owned_generations",
            "parent_states",
            "predecessor_kernel_sha256",
            "preflight_sha256",
            "rejected_attempts",
            "run_id",
            "runtime_contract_sha256",
            "schema",
            "stage_id",
            "status",
            "transition_number",
        }
        if not isinstance(control, dict) or set(control) != expected_keys:
            raise ValueError("transition journal control schema mismatch")
        immutable = {
            "classification": self.run_classification,
            "input_lock_sha256": self.input_sha,
            "predecessor_kernel_sha256": self.kernel_sha,
            "preflight_sha256": self.preflight_sha,
            "run_id": self.run_id,
            "runtime_contract_sha256": self.runtime_sha,
            "schema": 1,
            "stage_id": policy.STAGE_ID,
            "transition_number": number,
        }
        for name, expected in immutable.items():
            if control.get(name) != expected:
                raise ValueError(f"transition journal mismatch: {name}")
        cursor = _cursor_load(control["cursor"])
        counters = (control["attempted_endpoints"], control["rejected_attempts"])
        if not all(type(value) is int and value >= 0 for value in counters):
            raise ValueError("transition journal counters are invalid")
        states = control["parent_states"]
        if not isinstance(states, dict) or set(states) != set(policy.LANE_ORDER):
            raise ValueError("transition journal lane state set mismatch")
        owned = control["owned_generations"]
        if (
            not isinstance(owned, list)
            or len(set(owned)) != len(owned)
            or not isinstance(control["status"], str)
        ):
            raise ValueError("transition journal status or generation ledger is invalid")
        for relative in owned:
            _relative_path(
                self.run_dir / "checkpoints", relative, prefix="generations/g-"
            )
        generation = control["latest_generation"]
        record_sha = control["latest_record_sha256"]
        if generation is not None:
            _relative_path(
                self.run_dir / "checkpoints", generation, prefix="generations/g-"
            )
        if record_sha is not None and (
            not isinstance(record_sha, str)
            or len(record_sha) != 64
            or any(character not in "0123456789abcdef" for character in record_sha)
        ):
            raise ValueError("transition journal record SHA-256 is invalid")
        if (generation is None) != (record_sha is None):
            raise ValueError("transition journal generation/record mismatch")
        return cursor

    @staticmethod
    def _same_checkpoint(left: dict[str, Any], right: dict[str, Any]) -> bool:
        names = (
            "latest_generation",
            "latest_record_sha256",
            "owned_generations",
            "parent_states",
        )
        return all(left[name] == right[name] for name in names)

    def _validate_transition_step(
        self,
        previous: dict[str, Any],
        current: dict[str, Any],
        action: str,
    ) -> None:
        before = _cursor_load(previous["cursor"])
        after = _cursor_load(current["cursor"])
        attempts_before = previous["attempted_endpoints"]
        rejects_before = previous["rejected_attempts"]
        attempts_after = current["attempted_endpoints"]
        rejects_after = current["rejected_attempts"]
        if action == "ACCEPT":
            expected = policy.advance_after_accept(before)
            expected_generation = (
                f"generations/g-{expected.accepted_index:08d}-"
                f"tick-{expected.accepted_tick:06d}"
            )
            if (
                after != expected
                or attempts_after != attempts_before + 1
                or rejects_after != rejects_before
                or current["status"] != "RUNNING"
                or current["latest_generation"] != expected_generation
                or current["owned_generations"]
                != previous["owned_generations"] + [expected_generation]
                or any(current["parent_states"][lane] is None for lane in policy.LANE_ORDER)
            ):
                raise ValueError("invalid ACCEPT transition journal step")
            return
        if action == "BISECT":
            if before.current is None:
                raise ValueError("completed cursor cannot be bisected")
            task = before.current
            midpoint = task.left_tick + task.width_ticks // 2
            expected = policy.cursor_after_bisection(
                before,
                policy.IntervalTask(task.left_tick, midpoint, task.depth + 1),
                policy.IntervalTask(midpoint, task.right_tick, task.depth + 1),
            )
            if (
                after != expected
                or attempts_after != attempts_before + 1
                or rejects_after != rejects_before + 1
                or current["status"] != "RUNNING"
                or not self._same_checkpoint(previous, current)
            ):
                raise ValueError("invalid BISECT transition journal step")
            return
        blocked = {
            "BLOCKED_PROTOCOL": ("BLOCKED_PROTOCOL", 0),
            "BLOCKED_TRANSPORT": ("BLOCKED_TRANSPORT", 0),
            "BLOCKED_TABLE_EVENT": ("BLOCKED_TABLE_EVENT", 1),
            "BLOCKED_MINIMUM_STEP": ("BLOCKED_MINIMUM_STEP", 1),
            "STOP_TABLE_EVENT": ("BLOCKED_TABLE_EVENT", 1),
            "STOP_MINIMUM_STEP": ("BLOCKED_MINIMUM_STEP", 1),
        }
        if action in blocked:
            expected_status, reject_delta = blocked[action]
            if (
                after != before
                or attempts_after != attempts_before + 1
                or rejects_after != rejects_before + reject_delta
                or current["status"] != expected_status
                or not self._same_checkpoint(previous, current)
            ):
                raise ValueError(f"invalid {action} transition journal step")
            return
        if action in {"PAUSED_LIMIT", "PAUSED_ATTEMPT_LIMIT", "COMPLETE_UNSEALED"}:
            if (
                after != before
                or attempts_after != attempts_before
                or rejects_after != rejects_before
                or current["status"] != action
                or not self._same_checkpoint(previous, current)
            ):
                raise ValueError(f"invalid {action} transition journal step")
            return
        raise ValueError(f"unsupported transition journal action: {action}")

    def _validate_transition_evidence(
        self,
        previous: dict[str, Any],
        current: dict[str, Any],
        action: str,
        evidence: dict[str, str],
    ) -> str | None:
        attempt_actions = {
            "ACCEPT",
            "BISECT",
            "BLOCKED_PROTOCOL",
            "BLOCKED_TRANSPORT",
            "BLOCKED_TABLE_EVENT",
            "BLOCKED_MINIMUM_STEP",
            "STOP_TABLE_EVENT",
            "STOP_MINIMUM_STEP",
        }
        if action not in attempt_actions:
            if evidence:
                raise ValueError("status-only transition published attempt evidence")
            return None
        expected_evidence_keys = {
            "attempt_receipt_path",
            "attempt_receipt_sha256",
        }
        if action == "ACCEPT":
            expected_evidence_keys.update(
                {"accepted_record_path", "accepted_record_sha256"}
            )
        if set(evidence) != expected_evidence_keys:
            raise ValueError("attempt transition lacks canonical receipt evidence")
        before = _cursor_load(previous["cursor"])
        if before.current is None:
            raise ValueError("completed cursor published attempt evidence")
        attempt_number = current["attempted_endpoints"]
        expected_relative = (
            "receipts/"
            f"attempt_{attempt_number:08d}_{before.current.left_tick:06d}_"
            f"{before.current.right_tick:06d}.json"
        )
        if evidence["attempt_receipt_path"] != expected_relative:
            raise ValueError("transition receipt path mismatch")
        path = _relative_path(
            self.run_dir,
            evidence["attempt_receipt_path"],
            prefix="receipts/attempt_",
        )
        if (
            path.is_symlink()
            or not path.is_file()
            or sha_file(path) != evidence["attempt_receipt_sha256"]
        ):
            raise ValueError("transition receipt evidence is missing or changed")
        receipt = read_json(path)
        expected_keys = {
            "action",
            "accepted_parent_index",
            "accepted_parent_tick",
            "attempt_number",
            "classification",
            "interval",
            "jobs",
            "processes",
            "run_id",
            "runtime_contract_sha256",
            "stage_id",
        }
        if not isinstance(receipt, dict) or set(receipt) != expected_keys:
            raise ValueError("transition receipt schema mismatch")
        exact = {
            "action": action,
            "accepted_parent_index": before.accepted_index,
            "accepted_parent_tick": before.accepted_tick,
            "attempt_number": attempt_number,
            "classification": self.run_classification,
            "interval": before.current.as_dict(),
            "run_id": self.run_id,
            "runtime_contract_sha256": self.runtime_sha,
            "stage_id": policy.STAGE_ID,
        }
        for name, expected in exact.items():
            if receipt[name] != expected:
                raise ValueError(f"transition receipt mismatch: {name}")
        jobs = receipt["jobs"]
        processes = receipt["processes"]
        if (
            not isinstance(jobs, dict)
            or set(jobs) != set(policy.LANE_ORDER)
            or not all(isinstance(value, str) and len(value) == 64 for value in jobs.values())
            or not isinstance(processes, list)
            or len(processes) != len(policy.LANE_ORDER)
        ):
            raise ValueError("transition receipt lane evidence mismatch")
        if action == "ACCEPT":
            accepted_index = _cursor_load(current["cursor"]).accepted_index
            expected_record_relative = f"history/accepted_{accepted_index:08d}.json"
            if evidence["accepted_record_path"] != expected_record_relative:
                raise ValueError("accepted record evidence path mismatch")
            record_path = _relative_path(
                self.run_dir,
                evidence["accepted_record_path"],
                prefix="history/accepted_",
            )
            if (
                record_path.is_symlink()
                or not record_path.is_file()
                or sha_file(record_path) != evidence["accepted_record_sha256"]
                or evidence["accepted_record_sha256"]
                != current["latest_record_sha256"]
            ):
                raise ValueError("accepted record evidence is missing or changed")
            accepted_record = read_json(record_path)
            if (
                accepted_record.get("interval") != before.current.as_dict()
                or accepted_record.get("cursor_after") != current["cursor"]
            ):
                raise ValueError("accepted record evidence does not match transition")
            record_lanes = accepted_record.get("lanes")
            if (
                not isinstance(record_lanes, dict)
                or set(record_lanes) != set(policy.LANE_ORDER)
                or any(
                    record_lanes[lane].get("job_key") != jobs[lane]
                    for lane in policy.LANE_ORDER
                )
            ):
                raise ValueError("transition receipt jobs do not bind the accepted record")
        return evidence["attempt_receipt_path"]

    def _validate_unpublished_receipt(
        self, relative: str, control: dict[str, Any]
    ) -> None:
        before = _cursor_load(control["cursor"])
        if before.current is None:
            raise ValueError("completed checkpoint has an unpublished attempt receipt")
        attempt_number = control["attempted_endpoints"] + 1
        expected_relative = (
            "receipts/"
            f"attempt_{attempt_number:08d}_{before.current.left_tick:06d}_"
            f"{before.current.right_tick:06d}.json"
        )
        if relative != expected_relative:
            raise ValueError("unexpected pre-journal attempt receipt")
        path = _relative_path(self.run_dir, relative, prefix="receipts/attempt_")
        if path.is_symlink() or not path.is_file():
            raise ValueError("pre-journal attempt receipt is not a regular file")
        receipt = read_json(path)
        expected_keys = {
            "action",
            "accepted_parent_index",
            "accepted_parent_tick",
            "attempt_number",
            "classification",
            "interval",
            "jobs",
            "processes",
            "run_id",
            "runtime_contract_sha256",
            "stage_id",
        }
        actions = {
            "ACCEPT",
            "BISECT",
            "BLOCKED_PROTOCOL",
            "BLOCKED_TRANSPORT",
            "STOP_MINIMUM_STEP",
            "STOP_TABLE_EVENT",
        }
        if (
            not isinstance(receipt, dict)
            or set(receipt) != expected_keys
            or receipt["action"] not in actions
            or receipt["accepted_parent_index"] != before.accepted_index
            or receipt["accepted_parent_tick"] != before.accepted_tick
            or receipt["attempt_number"] != attempt_number
            or receipt["classification"] != self.run_classification
            or receipt["interval"] != before.current.as_dict()
            or receipt["run_id"] != self.run_id
            or receipt["runtime_contract_sha256"] != self.runtime_sha
            or receipt["stage_id"] != policy.STAGE_ID
        ):
            raise ValueError("pre-journal attempt receipt metadata mismatch")
        jobs = receipt["jobs"]
        processes = receipt["processes"]
        if (
            not isinstance(jobs, dict)
            or set(jobs) != set(policy.LANE_ORDER)
            or not isinstance(processes, list)
            or len(processes) != len(policy.LANE_ORDER)
            or {row.get("lane") for row in processes if isinstance(row, dict)}
            != set(policy.LANE_ORDER)
        ):
            raise ValueError("pre-journal attempt receipt lane set mismatch")
        for lane in policy.LANE_ORDER:
            parent = control["parent_states"][lane]
            if parent is None:
                parent_sha = "INITIAL"
            elif isinstance(parent, dict) and isinstance(parent.get("sha256"), str):
                parent_sha = parent["sha256"]
            else:
                raise ValueError("pre-journal attempt parent state mismatch")
            expected_job = policy.job_key(
                lane=lane,
                task=before.current,
                accepted_index=before.accepted_index + 1,
                parent_state_sha256=parent_sha,
                input_lock_sha256=self.input_sha,
                predecessor_kernel_sha256=self.kernel_sha,
                runtime_contract_sha256=self.runtime_sha,
            )
            if jobs[lane] != expected_job:
                raise ValueError("pre-journal attempt receipt job mismatch")

    def _validate_transition_journal(self) -> list[dict[str, Any]]:
        self._unpublished_receipt: str | None = None
        root = self.run_dir / "history" / "transitions"
        entries = list(root.iterdir())
        removed_temporary = False
        for path in list(entries):
            owned_temporary = re.fullmatch(
                r"\.transition_[0-9]{8}\.json\.tmp-[A-Za-z0-9_-]+",
                path.name,
            )
            if not owned_temporary:
                continue
            if path.is_symlink() or not path.is_file():
                raise ValueError("invalid transition journal temporary entry")
            if not self.repair_mode:
                raise ValueError("transition journal repair is required")
            path.unlink()
            entries.remove(path)
            removed_temporary = True
        if removed_temporary:
            _fsync_dir(root)
        if not entries:
            raise FileNotFoundError("cannot resume without transition journal")
        for path in entries:
            if path.is_symlink() or not path.is_file():
                raise ValueError("foreign transition journal entry")
        expected_names = {
            f"transition_{number:08d}.json" for number in range(len(entries))
        }
        if {path.name for path in entries} != expected_names:
            raise ValueError("transition journal set is not contiguous")
        previous_sha = None
        controls: list[dict[str, Any]] = []
        receipt_paths: set[str] = set()
        for number in range(len(entries)):
            path = root / f"transition_{number:08d}.json"
            payload = path.read_bytes()
            row = read_json(path)
            if not isinstance(row, dict) or set(row) != {
                "action",
                "control_state",
                "evidence",
                "previous_transition_sha256",
                "transition_number",
                "transition_schema",
            }:
                raise ValueError("transition journal record schema mismatch")
            if (
                row["transition_schema"] != 1
                or type(row["transition_number"]) is not int
                or row["transition_number"] != number
                or row["previous_transition_sha256"] != previous_sha
                or not isinstance(row["action"], str)
                or not isinstance(row["evidence"], dict)
                or not all(
                    isinstance(key, str) and isinstance(value, str)
                    for key, value in row["evidence"].items()
                )
            ):
                raise ValueError("transition journal chain mismatch")
            control = row["control_state"]
            cursor = self._validate_control_base(control, number)
            if number == 0:
                if (
                    row["action"] != "INITIAL"
                    or row["evidence"]
                    or cursor != policy.initial_cursor()
                    or control["attempted_endpoints"] != 0
                    or control["rejected_attempts"] != 0
                    or control["status"] != "READY"
                    or control["latest_generation"] is not None
                    or control["latest_record_sha256"] is not None
                    or control["owned_generations"]
                    or any(value is not None for value in control["parent_states"].values())
                ):
                    raise ValueError("invalid initial transition journal record")
            else:
                self._validate_transition_step(controls[-1], control, row["action"])
                evidence_path = self._validate_transition_evidence(
                    controls[-1], control, row["action"], row["evidence"]
                )
                if evidence_path is not None:
                    if evidence_path in receipt_paths:
                        raise ValueError("duplicate transition receipt evidence")
                    receipt_paths.add(evidence_path)
            previous_sha = sha_bytes(payload)
            published = dict(control)
            published["latest_transition_sha256"] = previous_sha
            controls.append(published)
        observed_receipts = {
            path.relative_to(self.run_dir).as_posix()
            for path in (self.run_dir / "receipts").glob("attempt_*.json")
            if path.is_file() and not path.is_symlink()
        }
        missing_receipts = receipt_paths - observed_receipts
        extra_receipts = observed_receipts - receipt_paths
        if missing_receipts or len(extra_receipts) > 1:
            raise ValueError("attempt receipt set does not match transition journal")
        if extra_receipts:
            if not self.repair_mode:
                raise ValueError("pre-journal attempt requires runner repair")
            self._unpublished_receipt = next(iter(extra_receipts))
            self._validate_unpublished_receipt(
                self._unpublished_receipt, controls[-1]
            )
        return controls

    def _load(self) -> None:
        controls = self._validate_transition_journal()
        control = controls[-1]
        encoded_controls = [canonical(value) for value in controls]
        control_index = None
        if self.control.is_file():
            observed_control = canonical(read_json(self.control))
            try:
                control_index = encoded_controls.index(observed_control)
            except ValueError as error:
                raise ValueError("CONTROL is not a validated transition journal head") from error
        latest_index = None
        if self.latest.is_file():
            observed_latest = read_json(self.latest)
            if not isinstance(observed_latest, dict):
                raise ValueError("LATEST must be an object")
            embedded = observed_latest.get("control_state")
            try:
                latest_index = encoded_controls.index(canonical(embedded))
            except ValueError as error:
                raise ValueError("LATEST is not a validated transition journal head") from error
            if observed_latest != self._latest_for_control(embedded):
                raise ValueError("LATEST is not the canonical journal projection")
        head = len(controls) - 1
        previous = head - 1 if head else None
        allowed_pairs = {(head, head), (None, head)}
        if previous is None:
            allowed_pairs.add((None, None))
        else:
            allowed_pairs.update({(previous, previous), (previous, head)})
        if (control_index, latest_index) not in allowed_pairs:
            raise ValueError("impossible CONTROL/LATEST publication order")
        self.cursor = _cursor_load(control.get("cursor"))
        self.states = control.get("parent_states")
        if not isinstance(self.states, dict) or set(self.states) != set(policy.LANE_ORDER):
            raise ValueError("wrong lane state set")
        self.record_sha = control.get("latest_record_sha256")
        self.generation = control.get("latest_generation")
        self.attempts = control.get("attempted_endpoints")
        self.rejects = control.get("rejected_attempts")
        self.transition = control.get("transition_number")
        self.transition_sha = control.get("latest_transition_sha256")
        self.status = control.get("status")
        self.owned_generations = control.get("owned_generations")
        if not all(type(value) is int and value >= 0 for value in (self.attempts, self.rejects, self.transition)):
            raise ValueError("invalid resume counters")
        if self.attempts < self.cursor.accepted_index + self.rejects:
            raise ValueError("attempt counters are inconsistent")
        if not isinstance(self.status, str) or not isinstance(self.owned_generations, list) or len(set(self.owned_generations)) != len(self.owned_generations):
            raise ValueError("invalid resume status or generation ledger")
        for relative in self.owned_generations:
            _relative_path(self.run_dir / "checkpoints", relative, prefix="generations/g-")
        expected_latest = self._latest_for_control(control)
        self._validate_loaded_state(
            control, expected_latest, allow_unpublished=True
        )
        self._recover_unpublished_generations()
        self._recover_unpublished_receipt()
        self._validate_loaded_state(control, expected_latest)
        self._validate_snapshots()
        latest_matches = self.latest.is_file() and read_json(self.latest) == expected_latest
        control_matches = self.control.is_file() and read_json(self.control) == control
        if not self.repair_mode and (not latest_matches or not control_matches):
            raise ValueError("checkpoint mirrors require runner repair")
        if not latest_matches:
            atomic_json(self.latest, expected_latest)
        if not control_matches:
            atomic_json(self.control, control)

    def _parent(self, lane: str) -> dict[str, Any]:
        state = self.states[lane]
        if state is None:
            return {"kind": "INITIAL", "path": None, "sha256": "INITIAL"}
        path = _relative_path(self.run_dir, state["path"], prefix="checkpoints/generations/g-")
        return {"kind": "STATE", "path": str(path), "sha256": state["sha256"]}

    def _job(self, lane: str, task) -> dict[str, Any]:
        parent = self._parent(lane)
        index = self.cursor.accepted_index + 1
        key = policy.job_key(
            lane=lane,
            task=task,
            accepted_index=index,
            parent_state_sha256=parent["sha256"],
            input_lock_sha256=self.input_sha,
            predecessor_kernel_sha256=self.kernel_sha,
            runtime_contract_sha256=self.runtime_sha,
        )
        return {
            "accepted_index": index,
            "input_lock_sha256": self.input_sha,
            "interval": task.as_dict(),
            "job_key": key,
            "lane": lane,
            "parent": parent,
            "predecessor_kernel_sha256": self.kernel_sha,
            "runtime_contract_sha256": self.runtime_sha,
            "stage_id": policy.STAGE_ID,
            "worker_job_schema": 1,
        }

    def _env(self) -> dict[str, str]:
        environment = os.environ.copy()
        environment.update(self.worker_environment)
        environment.pop("PYTHONHOME", None)
        environment.pop("PYTHONPATH", None)
        for name in THREAD_LIMITS:
            environment[name] = "1"
        environment["PYTHONHASHSEED"] = "0"
        environment["PYTHONNOUSERSITE"] = "1"
        environment["XLA_FLAGS"] = "--xla_cpu_multi_thread_eigen=false intra_op_parallelism_threads=1"
        return environment

    def _worker(self, lane: str, directory: Path, job: dict[str, Any]) -> dict[str, Any]:
        job_path = directory / f"{lane}.job.json"
        result_path = directory / f"{lane}.result.json"
        state_path = directory / f"{lane}.state"
        atomic_json(job_path, job)
        command = [
            sys.executable,
            str(self.worker_script),
            "--job",
            str(job_path),
            "--result",
            str(result_path),
            "--state",
            str(state_path),
        ]
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=self._env(),
                close_fds=True,
                start_new_session=True,
            )
            try:
                stdout, stderr = process.communicate(timeout=self.worker_timeout)
            except subprocess.TimeoutExpired as error:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                except OSError:
                    if process.poll() is None:
                        process.kill()
                try:
                    stdout, stderr = process.communicate(
                        timeout=min(1.0, max(0.1, self.worker_timeout))
                    )
                except subprocess.TimeoutExpired as drain_error:
                    stdout = (
                        drain_error.stdout
                        if drain_error.stdout is not None
                        else error.stdout
                    )
                    stderr = (
                        drain_error.stderr
                        if drain_error.stderr is not None
                        else error.stderr
                    )
                    for stream in (process.stdout, process.stderr):
                        if stream is not None:
                            try:
                                stream.close()
                            except OSError:
                                pass
                    try:
                        process.wait(timeout=0.1)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                return {
                    "lane": lane,
                    "process_status": "TIMEOUT",
                    "returncode": None,
                    "stderr": _bounded_text(stderr),
                    "stdout": _bounded_text(stdout),
                }
        except OSError as error:
            return {
                "error": f"{type(error).__name__}: {error}",
                "lane": lane,
                "process_status": "LAUNCH_ERROR",
                "returncode": None,
                "stderr": "",
                "stdout": "",
            }
        row = {
            "lane": lane,
            "process_status": "EXITED",
            "returncode": process.returncode,
            "stdout": _bounded_text(stdout),
            "stderr": _bounded_text(stderr),
        }
        if process.returncode != 0:
            return row
        if result_path.is_symlink() or not result_path.is_file():
            row["process_status"] = "MISSING_RESULT"
            return row
        if result_path.stat().st_size > 64 * 1024 * 1024:
            row["process_status"] = "INVALID_RESULT"
            row["error"] = "worker result exceeds 64 MiB"
            return row
        try:
            row["envelope"] = read_json(result_path)
        except Exception as error:
            row["process_status"] = "INVALID_RESULT"
            row["error"] = f"{type(error).__name__}: {error}"
            return row
        row["state_path"] = str(state_path)
        return row

    def _validate_candidate(self, row: dict[str, Any], job: dict[str, Any]) -> None:
        envelope = row["envelope"]
        state_path = Path(row["state_path"])
        if envelope.get("lane") != row["lane"]:
            raise ValueError("scheduled lane/envelope mismatch")
        if envelope.get("scientific_accept") is not True:
            if state_path.exists():
                raise ValueError("rejected worker wrote a candidate state")
            return
        candidate = envelope.get("candidate_state")
        if not isinstance(candidate, dict):
            raise ValueError("accepted worker lacks candidate state")
        if Path(candidate.get("path", "")).resolve() != state_path.resolve():
            raise ValueError("candidate state path mismatch")
        metadata = {
            "accepted_index": job["accepted_index"],
            "endpoint_tick": job["interval"]["right_tick"],
            "input_lock_sha256": self.input_sha,
            "job_key": job["job_key"],
            "lane": job["lane"],
            "parent_state_sha256": job["parent"]["sha256"],
            "predecessor_kernel_sha256": self.kernel_sha,
            "runtime_contract_sha256": self.runtime_sha,
            "stage_id": policy.STAGE_ID,
        }
        inspect_state(
            state_path,
            expected_sha256=candidate.get("sha256"),
            expected_size=candidate.get("size_bytes"),
            expected_metadata=metadata,
        )

    def _attempt(self, task, directory: Path):
        jobs = {lane: self._job(lane, task) for lane in policy.LANE_ORDER}
        rows = []
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            futures = {
                pool.submit(self._worker, lane, directory, job): lane
                for lane, job in jobs.items()
            }
            for future in as_completed(futures):
                lane = futures[future]
                try:
                    rows.append(future.result())
                except Exception as error:
                    rows.append(
                        {
                            "error": f"{type(error).__name__}: {error}",
                            "lane": lane,
                            "process_status": "SUPERVISOR_WAIT_ERROR",
                            "returncode": None,
                            "stderr": "",
                            "stdout": "",
                        }
                    )
        rows.sort(key=lambda value: policy.LANE_ORDER.index(value["lane"]))
        if any(
            row.get("process_status") != "EXITED" or row.get("returncode") != 0
            for row in rows
        ):
            return jobs, rows, None, "BLOCKED_TRANSPORT"
        try:
            for row in rows:
                self._validate_candidate(row, jobs[row["lane"]])
            parents = {lane: jobs[lane]["parent"]["sha256"] for lane in policy.LANE_ORDER}
            decision = policy.validate_and_decide(
                task=task,
                accepted_index=self.cursor.accepted_index + 1,
                parent_state_sha256=parents,
                input_lock_sha256=self.input_sha,
                predecessor_kernel_sha256=self.kernel_sha,
                runtime_contract_sha256=self.runtime_sha,
                envelopes=[row["envelope"] for row in rows],
                maximum_depth=policy.MAXIMUM_DEPTH,
            )
        except (KeyError, TypeError, ValueError) as error:
            rows[0]["protocol_error"] = f"{type(error).__name__}: {error}"
            return jobs, rows, None, "BLOCKED_PROTOCOL"
        return jobs, rows, decision, None

    def _receipt(self, task, jobs, rows, action: str) -> dict[str, str]:
        value = {
            "action": action,
            "accepted_parent_index": self.cursor.accepted_index,
            "accepted_parent_tick": self.cursor.accepted_tick,
            "attempt_number": self.attempts,
            "classification": self.run_classification,
            "interval": task.as_dict(),
            "jobs": {lane: jobs[lane]["job_key"] for lane in policy.LANE_ORDER},
            "processes": rows,
            "run_id": self.run_id,
            "runtime_contract_sha256": self.runtime_sha,
            "stage_id": policy.STAGE_ID,
        }
        relative = (
            "receipts/"
            f"attempt_{self.attempts:08d}_{task.left_tick:06d}_{task.right_tick:06d}.json"
        )
        payload = canonical(value) + b"\n"
        immutable_write(self.run_dir / relative, payload)
        return {
            "attempt_receipt_path": relative,
            "attempt_receipt_sha256": sha_bytes(payload),
        }

    def _generation_owner(self, relative: str) -> dict[str, Any]:
        return {
            "generation": relative,
            "owner_schema": 1,
            "run_id": self.run_id,
            "runtime_contract_sha256": self.runtime_sha,
            "stage_id": policy.STAGE_ID,
        }

    def _temporary_owner(self, name: str) -> dict[str, Any]:
        return {
            "generation_name": name,
            "owner_schema": 1,
            "run_id": self.run_id,
            "runtime_contract_sha256": self.runtime_sha,
            "stage_id": policy.STAGE_ID,
        }

    def _recover_unpublished_generations(self) -> None:
        root = self.run_dir / "checkpoints" / "generations"
        known = set(self.owned_generations)
        for path in list(root.iterdir()):
            if path.is_symlink() or not path.is_dir():
                raise ValueError("foreign generation-root entry")
            if path.name.startswith("."):
                owner_path = path / "TEMPORARY_OWNER.json"
                owner = read_json(owner_path) if owner_path.is_file() else None
                expected_name = owner.get("generation_name") if isinstance(owner, dict) else None
                if (
                    not isinstance(expected_name, str)
                    or not expected_name.startswith("g-")
                    or not path.name.startswith(f".{expected_name}.tmp-")
                    or owner != self._temporary_owner(expected_name)
                ):
                    raise ValueError("foreign temporary generation")
                if getattr(self, "_unpublished_receipt", None) is None:
                    raise ValueError("temporary generation lacks a pre-journal receipt")
                if not self.repair_mode:
                    raise ValueError("temporary generation requires runner repair")
                _safe_rmtree(path, root)
                continue
            relative = f"generations/{path.name}"
            if relative in known:
                self._validate_generation_owner(path, relative)
                continue
            self._validate_generation_owner(path, relative)
            record_path = path / "record.json"
            record = read_json(record_path)
            expected_index = self.cursor.accepted_index + 1
            expected_task = self.cursor.current
            if (
                expected_task is None
                or record.get("accepted_index") != expected_index
                or record.get("interval") != expected_task.as_dict()
                or record.get("previous_record_sha256") != self.record_sha
                or record.get("runtime_contract_sha256") != self.runtime_sha
                or path.name != f"g-{expected_index:08d}-tick-{expected_task.right_tick:06d}"
            ):
                raise ValueError("foreign unpublished generation")
            if getattr(self, "_unpublished_receipt", None) is None:
                raise ValueError("unpublished generation lacks a pre-journal receipt")
            if not self.repair_mode:
                raise ValueError("unpublished generation requires runner repair")
            history = self.run_dir / "history" / f"accepted_{expected_index:08d}.json"
            if history.exists():
                if history.is_symlink() or history.read_bytes() != record_path.read_bytes():
                    raise ValueError("unpublished history collision")
                history.unlink()
                _fsync_dir(history.parent)
            snapshot = self.run_dir / "checkpoints" / "snapshots" / path.name
            if snapshot.exists():
                self._validate_generation_owner(snapshot, relative)
                if snapshot.joinpath("record.json").read_bytes() != record_path.read_bytes():
                    raise ValueError("unpublished snapshot collision")
                _safe_rmtree(snapshot, snapshot.parent)
            _safe_rmtree(path, root)

    def _recover_unpublished_receipt(self) -> None:
        relative = getattr(self, "_unpublished_receipt", None)
        if relative is None:
            return
        if not self.repair_mode:
            raise ValueError("pre-journal attempt requires runner repair")
        path = _relative_path(self.run_dir, relative, prefix="receipts/attempt_")
        if path.is_symlink() or not path.is_file():
            raise ValueError("pre-journal attempt receipt disappeared during recovery")
        path.unlink()
        _fsync_dir(path.parent)
        self._unpublished_receipt = None

    def _commit(self, task, rows, next_cursor, evidence: dict[str, str]) -> None:
        name = f"g-{next_cursor.accepted_index:08d}-tick-{next_cursor.accepted_tick:06d}"
        relative = f"generations/{name}"
        root = self.run_dir / "checkpoints" / "generations"
        target = root / name
        if target.exists():
            self._validate_generation_owner(target, relative)
            if self.generation == relative:
                raise ValueError("duplicate committed generation")
            _safe_rmtree(target, root)
        temporary = Path(tempfile.mkdtemp(prefix=f".{name}.tmp-", dir=root))
        try:
            atomic_json(temporary / "TEMPORARY_OWNER.json", self._temporary_owner(name))
            states = {}
            science = {}
            by_lane = {row["lane"]: row for row in rows}
            for lane in policy.LANE_ORDER:
                row = by_lane[lane]
                envelope = row["envelope"]
                destination = temporary / f"{lane}.state"
                observed = _copy(Path(row["state_path"]), destination)
                if observed != envelope["candidate_state"]["sha256"]:
                    raise ValueError("state changed during commit")
                reference = {
                    "format": envelope["candidate_state"]["format"],
                    "node_count": envelope["candidate_state"]["node_count"],
                    "path": str(Path("checkpoints") / relative / f"{lane}.state"),
                    "sha256": observed,
                    "size_bytes": destination.stat().st_size,
                }
                states[lane] = reference
                science[lane] = {
                    key: value
                    for key, value in envelope.items()
                    if key != "telemetry"
                }
                science[lane]["candidate_state"] = reference
            record = {
                "accepted_index": next_cursor.accepted_index,
                "classification": self.run_classification,
                "cursor_after": _cursor_dict(next_cursor),
                "input_lock_sha256": self.input_sha,
                "interval": task.as_dict(),
                "lane_order": list(policy.LANE_ORDER),
                "lanes": science,
                "predecessor_kernel_sha256": self.kernel_sha,
                "previous_record_sha256": self.record_sha,
                "record_schema": 1,
                "runtime_contract_sha256": self.runtime_sha,
                "stage_id": policy.STAGE_ID,
            }
            record_bytes = canonical(record) + b"\n"
            record_sha = sha_bytes(record_bytes)
            atomic_write(temporary / "record.json", record_bytes)
            atomic_json(temporary / "GENERATION_OWNER.json", self._generation_owner(relative))
            (temporary / "TEMPORARY_OWNER.json").unlink()
            _fsync_dir(temporary)
            os.replace(temporary, target)
            temporary = None
            _fsync_dir(root)
            immutable_write(
                self.run_dir / "history" / f"accepted_{next_cursor.accepted_index:08d}.json",
                record_bytes,
            )
            if next_cursor.accepted_index % 64 == 0 or next_cursor.current is None:
                self._publish_snapshot(target, name, relative, record_sha)
            self.cursor = next_cursor
            self.states = states
            self.record_sha = record_sha
            self.generation = relative
            if relative not in self.owned_generations:
                self.owned_generations.append(relative)
            transition_evidence = dict(evidence)
            transition_evidence.update(
                {
                    "accepted_record_path": (
                        f"history/accepted_{next_cursor.accepted_index:08d}.json"
                    ),
                    "accepted_record_sha256": record_sha,
                }
            )
            self._persist(
                "RUNNING", action="ACCEPT", evidence=transition_evidence
            )
            self._prune()
        finally:
            if temporary is not None and temporary.exists():
                _safe_rmtree(temporary, root)

    def _prune(self) -> None:
        root = self.run_dir / "checkpoints" / "generations"
        retained = set(self.owned_generations[-2:])
        for relative in self.owned_generations:
            if relative in retained:
                continue
            path = _relative_path(self.run_dir / "checkpoints", relative, prefix="generations/g-")
            if path.exists():
                self._validate_generation_owner(path, relative)
                _safe_rmtree(path, root)

    def _publish_snapshot(self, source: Path, name: str, relative: str, record_sha: str) -> None:
        root = self.run_dir / "checkpoints" / "snapshots"
        target = root / name
        if target.exists():
            self._validate_generation_owner(target, relative)
            if sha_file(target / "record.json") != record_sha:
                raise ValueError("snapshot collision")
            return
        temporary = Path(tempfile.mkdtemp(prefix=f".{name}.tmp-", dir=root))
        try:
            atomic_json(temporary / "TEMPORARY_OWNER.json", self._temporary_owner(name))
            for path in source.iterdir():
                if path.name == "TEMPORARY_OWNER.json":
                    continue
                _copy(path, temporary / path.name)
            (temporary / "TEMPORARY_OWNER.json").unlink()
            _fsync_dir(temporary)
            os.replace(temporary, target)
            temporary = None
            _fsync_dir(root)
        finally:
            if temporary is not None and temporary.exists():
                _safe_rmtree(temporary, root)

    def _summary(self, status: str) -> dict[str, Any]:
        policy.validate_cursor(self.cursor)
        return {
            "accepted_endpoints": self.cursor.accepted_index,
            "accepted_tick": self.cursor.accepted_tick,
            "attempted_endpoints": self.attempts,
            "calculation_complete": self.cursor.current is None,
            "classification": self.run_classification,
            "final_state_sha256": {
                lane: state["sha256"] if state else None
                for lane, state in self.states.items()
            },
            "latest_generation": self.generation,
            "latest_record_sha256": self.record_sha,
            "rejected_attempts": self.rejects,
            "run_id": self.run_id,
            "runtime_contract_sha256": self.runtime_sha,
            "schema": 1,
            "stage_id": policy.STAGE_ID,
            "status": status,
            "unaudited_or_unimplemented": [
                "production table-event localization/rebuild",
                "sparse rank/named modes",
                "independent endpoint containment",
                "whole-history ledger closeout",
            ],
        }

    def _finish(
        self,
        status: str,
        *,
        evidence: dict[str, str] | None = None,
        action: str | None = None,
    ) -> dict[str, Any]:
        self._persist(status, action=action or status, evidence=evidence)
        summary = self._summary(status)
        atomic_json(self.run_dir / "data" / "results.json", summary)
        return summary

    def run(self, *, max_accepted: int | None = None, max_attempts: int | None = None):
        if max_accepted is not None and max_accepted <= 0:
            raise ValueError("max_accepted must be positive")
        if max_attempts is not None and max_attempts <= 0:
            raise ValueError("max_attempts must be positive")
        accepted_this_run = 0
        attempted_this_run = 0
        while self.cursor.current is not None:
            if max_accepted is not None and accepted_this_run >= max_accepted:
                return self._finish("PAUSED_LIMIT")
            if max_attempts is not None and attempted_this_run >= max_attempts:
                return self._finish("PAUSED_ATTEMPT_LIMIT")
            task = self.cursor.current
            self.attempts += 1
            attempted_this_run += 1
            with tempfile.TemporaryDirectory(
                prefix=f"attempt-{self.attempts:08d}-", dir=self.run_dir / "work"
            ) as raw:
                jobs, rows, decision, blocked = self._attempt(task, Path(raw))
                if blocked:
                    evidence = self._receipt(task, jobs, rows, blocked)
                    return self._finish(blocked, evidence=evidence)
                evidence = self._receipt(task, jobs, rows, decision.action)
                if self.progress:
                    self.progress(
                        {
                            "accepted_endpoints": self.cursor.accepted_index,
                            "action": decision.action,
                            "attempted_endpoints": self.attempts,
                            "interval": task.as_dict(),
                        }
                    )
                if decision.action == "ACCEPT":
                    self._commit(
                        task,
                        rows,
                        policy.advance_after_accept(self.cursor),
                        evidence,
                    )
                    accepted_this_run += 1
                elif decision.action == "BISECT":
                    self.rejects += 1
                    self.cursor = policy.cursor_after_bisection(
                        self.cursor, decision.left_child, decision.right_child
                    )
                    self._persist("RUNNING", action="BISECT", evidence=evidence)
                elif decision.action == "STOP_TABLE_EVENT":
                    self.rejects += 1
                    return self._finish(
                        "BLOCKED_TABLE_EVENT",
                        evidence=evidence,
                        action="STOP_TABLE_EVENT",
                    )
                elif decision.action == "STOP_MINIMUM_STEP":
                    self.rejects += 1
                    return self._finish(
                        "BLOCKED_MINIMUM_STEP",
                        evidence=evidence,
                        action="STOP_MINIMUM_STEP",
                    )
                else:
                    raise RuntimeError(f"unsupported decision: {decision.action}")
        return self._finish("COMPLETE_UNSEALED")


def _progress(value: dict[str, Any]) -> None:
    print(json.dumps(value, sort_keys=True), flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--worker-timeout", type=float, default=900)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-accepted", type=int)
    parser.add_argument("--max-attempts", type=int)
    args = parser.parse_args()
    with Coordinator(
        run_dir=Path(args.run_dir),
        workers=args.workers,
        worker_timeout=args.worker_timeout,
        resume=args.resume,
        progress=_progress,
    ) as coordinator:
        summary = coordinator.run(
            max_accepted=args.max_accepted, max_attempts=args.max_attempts
        )
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)
    return 0 if summary["status"] in {
        "COMPLETE_UNSEALED",
        "PAUSED_LIMIT",
        "PAUSED_ATTEMPT_LIMIT",
    } else 2


if __name__ == "__main__":
    raise SystemExit(main())
