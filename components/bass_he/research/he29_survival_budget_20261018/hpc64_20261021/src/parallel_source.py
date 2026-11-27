"""Exact HE28 source-table rows, parallel construction and immutable cache.

Only proper-time table construction changes.  Each spawned process evaluates
the original ExactSource.source_moments with an owner-free model.  In-row
arithmetic and canonical interval/row digest order are unchanged.  The native
ODE, packed Jacobian, positivity, physical gates and ledger norm are inherited.
"""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import platform
import sys
import time

LANE = Path(__file__).resolve().parents[1]
HE29 = LANE.parent
REPO = HE29.parents[1]
sys.path.insert(0, str(HE29 / "optimization_20261020/src"))
from optimized_model import OptimizedRefinedSourceModel
from refined_source import GridSpec, RefinedSourceModel, ExactSource
import numpy as np
import scipy

THREAD_VARIABLES = ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                    "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS", "RAYON_NUM_THREADS")
CACHE_SCHEMA = "he29.exact_source_table_cache.v1"
_WORKER_MODEL = None
_WORKER_ERROR = None


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def require_single_threads():
    actual = {key: os.environ.get(key) for key in THREAD_VARIABLES}
    if any(value != "1" for value in actual.values()):
        raise ValueError("HE29_TABLE_SINGLE_THREAD_ENV: " + repr(actual))
    return actual


def runtime_identity():
    return {"python": sys.version, "numpy": np.__version__,
            "scipy": scipy.__version__, "machine": platform.machine(),
            "byteorder": sys.byteorder, "threads": require_single_threads()}


def source_identity():
    """Read the preserved parent source contract plus changed adapter bytes."""
    expected = json.loads((HE29 / "provenance/PARENT_SHA256.json").read_text())
    result = {}
    for relative, wanted in expected.items():
        path = REPO / relative
        got = sha256_file(path)
        if path.is_symlink() or got != wanted:
            raise ValueError("HE29_TABLE_PARENT_SOURCE: " + relative)
        result[relative] = got
    for path in (HE29 / "optimization_20261020/src/optimized_model.py", Path(__file__)):
        if path.is_symlink():
            raise ValueError("HE29_TABLE_SOURCE_SYMLINK")
        result[str(path.relative_to(REPO))] = sha256_file(path)
    return result


def array_sha(array):
    return hashlib.sha256(np.asarray(array, dtype="<f8").tobytes(order="C")).hexdigest()


def model_identity(model):
    return {"spec": asdict(model.spec), "source_count_hex": float(model.source_count).hex(),
            "source_table_nodes": int(model.source_table_nodes), "K": int(model.K),
            "cut_bounds_sha256": array_sha(model._cut_bounds),
            "Eref_sha256": array_sha(model.Eref), "mu0_sha256": array_sha(model.mu0),
            "weights_sha256": array_sha(model.weights)}


def cache_contract(model):
    return {"schema": CACHE_SCHEMA, "model": model_identity(model),
            "runtime": runtime_identity(), "sources": source_identity()}


def cache_key(contract):
    return hashlib.sha256(canonical_json(contract)).hexdigest()


def table_layout(model):
    """The original long-interval rule, guard and linspace, without rounding."""
    long = np.diff(model._cut_bounds) > 1e-6 * model.t_end
    rows = {}
    for index, (left, right) in enumerate(zip(model._cut_bounds[:-1], model._cut_bounds[1:])):
        if long[index]:
            guard = 1e-10 * (right - left)
            rows[index] = np.linspace(left + guard, right - guard,
                                      model.source_table_nodes + 1)
    return rows


def table_digest(model, tables):
    """Exact original digest; packaging/runtime metadata do not enter it."""
    h = hashlib.sha256(json.dumps(asdict(model.spec), sort_keys=True).encode())
    h.update(model._cut_bounds.astype("<f8").tobytes())
    h.update(np.array([model.source_count, model.source_table_nodes], dtype="<f8").tobytes())
    for index in sorted(tables):
        ts, values = tables[index]
        h.update(np.array([index], dtype="<i8").tobytes())
        h.update(ts.astype("<f8").tobytes())
        h.update(values.astype("<f8").tobytes())
    h.update(bytes([True]))
    return h.hexdigest()


def initialize_worker(config, expected_model):
    global _WORKER_MODEL, _WORKER_ERROR
    _WORKER_MODEL, _WORKER_ERROR = None, None
    # Pool retries an initializer that raises.  Deliver a failed initializer as
    # a task error instead, so one bad configuration cannot cause a respawn loop.
    try:
        require_single_threads()
        _WORKER_MODEL = RefinedSourceModel(None, GridSpec(**config["spec"]),
            source_count=config["source_count"], source_table_nodes=config["nodes"],
            tabulate=False)
        if model_identity(_WORKER_MODEL) != expected_model:
            raise ValueError("HE29_TABLE_WORKER_MODEL_IDENTITY")
    except BaseException as exc:
        _WORKER_ERROR = repr(exc)


def compute_chunk(task):
    index, first, times = task
    if _WORKER_ERROR is not None:
        raise RuntimeError("HE29_TABLE_WORKER_INITIALIZATION: " + _WORKER_ERROR)
    if _WORKER_MODEL is None:
        raise RuntimeError("HE29_TABLE_WORKER_NOT_INITIALIZED")
    if not times or any(not math.isfinite(float(t)) for t in times):
        raise ValueError("HE29_TABLE_CHUNK_TIME")
    values = np.empty((len(times), _WORKER_MODEL.K), dtype=np.float64)
    report = None
    for offset, t in enumerate(times):
        values[offset], report = ExactSource.source_moments(_WORKER_MODEL, float(t))
    if not np.isfinite(values).all() or np.any(values < 0):
        raise ValueError("HE29_TABLE_CHUNK_POSITIVITY")
    return index, first, values, report, os.getpid()


def install_chunk(tables, seen, result):
    index, first, values, report, pid = result
    if type(index) is not int or index not in tables or type(first) is not int or first < 0:
        raise ValueError("HE29_TABLE_CHUNK_INDEX")
    values = np.asarray(values)
    destination = tables[index][1]
    if (values.dtype != np.dtype("float64") or values.ndim != 2
            or values.shape[0] < 1 or values.shape[1] != destination.shape[1]
            or first + len(values) > len(destination)
            or not np.isfinite(values).all() or np.any(values < 0)):
        raise ValueError("HE29_TABLE_CHUNK_SHAPE_OR_VALUE")
    stop = first + len(values)
    if np.any(seen[index][first:stop]):
        raise ValueError("HE29_TABLE_CHUNK_DUPLICATE")
    destination[first:stop] = values
    seen[index][first:stop] = True
    return index, stop - 1, report, pid


def construct_tables(model, *, max_workers, chunk_rows, max_wall_s):
    """One persistent spawn pool.  The parent process-group watchdog is final.

    Timeouts terminate this pool and preserve the failure.  The watchdog used by
    the enclosing command also bounds a child that fails to exit during join.
    """
    if type(max_workers) is not int or not 1 <= max_workers <= 64:
        raise ValueError("HE29_TABLE_WORKER_BUDGET")
    if type(chunk_rows) is not int or not 1 <= chunk_rows <= 1024:
        raise ValueError("HE29_TABLE_CHUNK_BUDGET")
    if not math.isfinite(max_wall_s) or max_wall_s <= 0:
        raise ValueError("HE29_TABLE_WALL_BUDGET")
    require_single_threads()
    layout = table_layout(model)
    tables = {i: (ts, np.empty((len(ts), model.K), dtype=np.float64)) for i, ts in layout.items()}
    seen = {i: np.zeros(len(ts), dtype=bool) for i, ts in layout.items()}
    tasks = [(i, first, ts[first:first + chunk_rows].tolist())
             for i, ts in layout.items() for first in range(0, len(ts), chunk_rows)]
    if not tasks:
        raise ValueError("HE29_TABLE_NO_LONG_INTERVALS")
    workers = min(max_workers, len(tasks))
    config = {"spec": asdict(model.spec), "source_count": float(model.source_count),
              "nodes": model.source_table_nodes}
    start = time.monotonic()
    pool = mp.get_context("spawn").Pool(workers, initializer=initialize_worker,
                                      initargs=(config, model_identity(model)))
    last = (-1, -1, None)
    pids = set()
    try:
        results = pool.imap_unordered(compute_chunk, tasks, chunksize=1)
        for _ in tasks:
            remaining = max_wall_s - (time.monotonic() - start)
            if remaining <= 0:
                raise TimeoutError("HE29_TABLE_WALL_BUDGET")
            index, row, report, pid = install_chunk(tables, seen, results.next(timeout=remaining))
            pids.add(pid)
            if (index, row) > last[:2]:
                last = index, row, report
        if not all(mask.all() for mask in seen.values()):
            raise ValueError("HE29_TABLE_MISSING_ROWS")
        pool.close()
        pool.join()
    except BaseException:
        pool.terminate()
        pool.join()
        raise
    if time.monotonic() - start > max_wall_s:
        raise TimeoutError("HE29_TABLE_WALL_BUDGET")
    return tables, last[2], {"start_method": "spawn", "workers_requested": max_workers,
        "workers_started_limit": workers, "worker_pids_observed": sorted(pids),
        "chunks": len(tasks), "chunk_rows": chunk_rows,
        "rows": sum(len(ts) for ts in layout.values()),
        "build_wall_s": time.monotonic() - start, "native_calls": 0,
        "physical_solver_runs": 0, "geometry_clock": "unchanged per-worker construction"}


def fsync_directory(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_json_once(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".partial")
    with temporary.open("xb") as stream:
        stream.write(canonical_json(value) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.link(temporary, path)
    finally:
        temporary.unlink()
    fsync_directory(path.parent)


def write_npy_once(path, array):
    with Path(path).open("xb") as stream:
        np.save(stream, np.asarray(array, dtype="<f8"), allow_pickle=False)
        stream.flush()
        os.fsync(stream.fileno())
    return {"name": Path(path).name, "bytes": Path(path).stat().st_size,
            "sha256": sha256_file(path)}


def publish_cache(folder, contract, model, tables, last_report, execution):
    """folder is exclusively reserved before construction; manifest commits it."""
    entries = []
    for index in sorted(tables):
        ts, values = tables[index]
        entries.append({"interval": index,
            "times": write_npy_once(folder / f"interval_{index:06d}_times.npy", ts),
            "values": write_npy_once(folder / f"interval_{index:06d}_values.npy", values)})
    manifest = {"schema": CACHE_SCHEMA, "key": cache_key(contract), "contract": contract,
        "table_sha256": table_digest(model, tables), "tables": entries,
        "last_source_moments": last_report, "execution": execution}
    write_json_once(folder / "MANIFEST.json", manifest)
    return manifest


def load_cache(folder, contract, model, *, expected_table_sha256=None):
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError("HE29_TABLE_CACHE_DIRECTORY")
    path = folder / "MANIFEST.json"
    if path.is_symlink() or not path.is_file():
        raise ValueError("HE29_TABLE_CACHE_INCOMPLETE")
    manifest = json.loads(path.read_text())
    if (manifest.get("schema") != CACHE_SCHEMA or manifest.get("key") != cache_key(contract)
            or manifest.get("contract") != contract):
        raise ValueError("HE29_TABLE_CACHE_IDENTITY")
    layout = table_layout(model)
    entries = manifest.get("tables")
    if not isinstance(entries, list) or [x.get("interval") for x in entries] != list(layout):
        raise ValueError("HE29_TABLE_CACHE_INTERVALS")
    tables = {}
    for entry in entries:
        index = entry["interval"]
        arrays = []
        for kind in ("times", "values"):
            item = entry[kind]
            name = f"interval_{index:06d}_{kind}.npy"
            file = folder / name
            if (item.get("name") != name or file.is_symlink() or not file.is_file()
                    or file.stat().st_size != item.get("bytes")
                    or sha256_file(file) != item.get("sha256")):
                raise ValueError("HE29_TABLE_CACHE_FILE: " + name)
            array = np.load(file, mmap_mode="r", allow_pickle=False)
            shape = (len(layout[index]),) if kind == "times" else (len(layout[index]), model.K)
            if array.dtype != np.dtype("<f8") or array.shape != shape or not array.flags.c_contiguous:
                raise ValueError("HE29_TABLE_CACHE_ARRAY")
            if not np.isfinite(array).all() or (kind == "values" and np.any(array < 0)):
                raise ValueError("HE29_TABLE_CACHE_ARRAY_VALUE")
            array.flags.writeable = False
            arrays.append(array)
        if not np.array_equal(arrays[0], layout[index]):
            raise ValueError("HE29_TABLE_CACHE_TIME_GRID")
        tables[index] = tuple(arrays)
    actual = table_digest(model, tables)
    if actual != manifest.get("table_sha256") or (expected_table_sha256 is not None and actual != expected_table_sha256):
        raise ValueError("HE29_TABLE_CACHE_DIGEST")
    return tables, manifest


class HPC64RefinedSourceModel(OptimizedRefinedSourceModel):
    """Original packed model with exactly ordered, reusable proper-time tables."""

    def __init__(self, owner, spec=None, *, cache_dir, max_workers=1, chunk_rows=64,
                 source_count=None, source_table_nodes=512,
                 max_table_bytes=2 * 1024**3, max_table_wall_s=600.,
                 expected_table_sha256=None, tabulate=True):
        if tabulate is not True:
            raise ValueError("HE29_HPC_MODEL_REQUIRES_TABLE")
        require_single_threads()
        super().__init__(owner, spec, source_count=source_count, tabulate=False,
                         source_table_nodes=source_table_nodes,
                         max_table_bytes=max_table_bytes, max_table_wall_s=max_table_wall_s)
        if self.table_estimate_bytes > max_table_bytes:
            raise MemoryError("HE29_TABLE_MEMORY_BUDGET")
        contract = cache_contract(self)
        root = Path(cache_dir).resolve()
        if root.is_relative_to(REPO):
            raise ValueError("HE29_TABLE_CACHE_MUST_BE_OUTSIDE_CHECKOUT")
        root.mkdir(parents=True, exist_ok=True)
        folder = root / cache_key(contract)
        start = time.monotonic()
        hit = folder.exists() or folder.is_symlink()
        if hit:
            tables, manifest = load_cache(folder, contract, self,
                                         expected_table_sha256=expected_table_sha256)
        else:
            folder.mkdir(exist_ok=False)
            fsync_directory(root)
            try:
                tables, last_report, execution = construct_tables(self,
                    max_workers=max_workers, chunk_rows=chunk_rows,
                    max_wall_s=max_table_wall_s)
                actual = table_digest(self, tables)
                if expected_table_sha256 is not None and actual != expected_table_sha256:
                    raise ValueError("HE29_TABLE_SAVED_REFERENCE_DIGEST_MISMATCH")
                if cache_contract(self) != contract:
                    raise ValueError("HE29_TABLE_IDENTITY_CHANGED_DURING_BUILD")
                manifest = publish_cache(folder, contract, self, tables, last_report, execution)
                tables, manifest = load_cache(folder, contract, self,
                                             expected_table_sha256=expected_table_sha256)
            except BaseException as exc:
                write_json_once(folder / "FAILURE.json", {"status": "PRESERVED_INCOMPLETE_CACHE",
                    "error": repr(exc), "contract": contract, "wall_s": time.monotonic() - start})
                raise
        self._source_tables = tables
        self.tabulated = True
        self.source_table_sha256 = manifest["table_sha256"]
        self.last_source_moments = manifest["last_source_moments"]
        self.source_diagnostics = self.last_source_moments
        self._opt_cache.clear()
        self.source_table_diagnostics = dict(self.source_table_diagnostics,
            tabulated_intervals=len(tables),
            direct_crossing_intervals=len(self._cut_bounds) - 1 - len(tables),
            build_wall_s=time.monotonic() - start)
        self.source_table_cache = {"status": "HIT_VERIFIED" if hit else "BUILT_AND_VERIFIED",
            "directory": str(folder), "key": cache_key(contract),
            "manifest_sha256": sha256_file(folder / "MANIFEST.json"),
            "table_sha256": self.source_table_sha256,
            "array_storage": "read-only npy mmap; allow_pickle=False",
            "estimated_table_allocation_bytes": self.table_estimate_bytes,
            "whole_process_rss_bound": False}
        self.source_table_execution = manifest["execution"]
