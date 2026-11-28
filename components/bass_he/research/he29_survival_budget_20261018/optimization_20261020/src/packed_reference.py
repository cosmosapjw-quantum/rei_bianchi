"""ABI2 opt-in adapter reusing the pinned VigilODE integration algorithm.

RHS/time derivative callbacks remain the verified ABI1 Python implementation.
Only physical Jacobian preparation/storage and repeated JVP evaluation change.
Every solve retains all 19 ledger variables and the original error norm.
"""
from __future__ import annotations

import ctypes as ct
import hashlib
import json
from pathlib import Path
import sys
import traceback

import numpy as np

LANE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LANE.parent / "vigilode_20261019" / "src"))
from vigilode_callbacks import SegmentCallbacks, finite_vector, validate_model
from vigilode_reference import (He29Stats, DOUBLE_PTR, RHS_CALLBACK, JVP_CALLBACK,
                                 VigilODEFailure, BASELINE_CODE, VIGILODE_SOURCE)
from optimized_model import prepare_jacobian

ABI_VERSION = 2
PREPARE_CALLBACK = ct.CFUNCTYPE(ct.c_int32, ct.c_void_p, ct.c_double,
    DOUBLE_PTR, ct.c_size_t, DOUBLE_PTR, DOUBLE_PTR)
BRIDGE_PATHS = frozenset(("rust_bridge/Cargo.toml", "rust_bridge/Cargo.lock",
    "rust_bridge/src/lib.rs", "rust_bridge/src/packed.rs",
    "rust_bridge/include/he29_optimized_bridge.h"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_build(library, receipt, lane=LANE):
    library, receipt = Path(library).resolve(strict=True), Path(receipt).resolve(strict=True)
    data = json.loads(receipt.read_text())
    required = dict(schema="he29.optimized.build.v1", status="COMPILED",
        abi_version=ABI_VERSION, vigilode_source=VIGILODE_SOURCE,
        baseline_code_revision=BASELINE_CODE)
    if any(data.get(k) != v for k, v in required.items()):
        raise ValueError("HE29_OPT_BUILD_CONTRACT")
    if data.get("library_sha256") != digest(library):
        raise ValueError("HE29_OPT_LIBRARY_HASH")
    sources = data.get("bridge_sources")
    if not isinstance(sources, dict) or set(sources) != BRIDGE_PATHS:
        raise ValueError("HE29_OPT_BRIDGE_SOURCE_PATHS")
    for name, sha in sources.items():
        if not isinstance(sha, str) or digest(Path(lane) / name) != sha:
            raise ValueError("HE29_OPT_BRIDGE_SOURCE_MISMATCH: " + name)
    return {**data, "receipt_sha256": digest(receipt)}


class PackedSegmentCallbacks(SegmentCallbacks):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counts["packed_preparations"] = 0

    def prepare(self, u, z):
        z = finite_vector(z, self.n, "scaled state")
        with np.errstate(over="ignore", invalid="ignore"):
            physical = finite_vector(z * self.scale, self.n, "physical state")
        t = self.time(u)
        prepare = getattr(self.model, "prepare_jacobian", None)
        result = prepare(t, physical) if callable(prepare) else prepare_jacobian(self.model, t, physical)
        if result.n != self.n:
            raise ValueError("HE29_OPT_PACKED_CALLBACK_DIMENSION")
        self.counts["packed_preparations"] += 1
        self.counts["jacobian_builds"] += 1
        return result


class PackedBridge:
    def __init__(self, library, receipt):
        self.identity = verify_build(library, receipt)
        self.library = ct.CDLL(str(Path(library).resolve()))
        abi = self.library.he29_vigilode_abi_version
        abi.argtypes, abi.restype = [], ct.c_uint32
        if abi() != ABI_VERSION:
            raise ValueError("HE29_OPT_ABI_VERSION")
        tail = [ct.c_double, ct.c_double, ct.c_size_t, DOUBLE_PTR,
                ct.POINTER(He29Stats), ct.POINTER(ct.c_char), ct.c_size_t]
        self._packed = self.library.he29_vigilode_segment_packed
        self._packed.argtypes = [ct.c_size_t, DOUBLE_PTR, RHS_CALLBACK,
            PREPARE_CALLBACK, RHS_CALLBACK, ct.c_void_p, DOUBLE_PTR,
            ct.c_double, ct.c_size_t, *tail]
        self._packed.restype = ct.c_int32
        self._legacy = self.library.he29_vigilode_segment
        self._legacy.argtypes = [ct.c_size_t, DOUBLE_PTR, RHS_CALLBACK,
            JVP_CALLBACK, RHS_CALLBACK, ct.c_void_p, *tail]
        self._legacy.restype = ct.c_int32

    def segment(self, callbacks, z0, *, mode="rust_packed", threads=1,
                initial_step=1/32, max_step=1., max_attempts=10000):
        if mode not in ("rust_packed", "python_csr"):
            raise ValueError("HE29_OPT_UNDECLARED_MODE")
        if type(threads) is not int or threads not in (1, 2, 4):
            raise ValueError("HE29_OPT_THREAD_SCOPE")
        if mode == "python_csr" and threads != 1:
            raise ValueError("HE29_OPT_LEGACY_SINGLE_THREAD")
        if (not np.isfinite([initial_step, max_step]).all()
                or not 0 < initial_step <= max_step <= 1
                or type(max_attempts) is not int or not 0 < max_attempts <= 100000):
            raise ValueError("HE29_OPT_STEP_BUDGET")
        if callbacks.n <= 23:
            raise ValueError("HE29_OPT_PACKED_DIMENSION")
        z0 = np.array(finite_vector(z0, callbacks.n, "initial state"), dtype=np.float64, order="C", copy=True)
        scale = np.array(finite_vector(callbacks.scale, callbacks.n, "scale"), dtype=np.float64, order="C", copy=True)
        if np.any(scale <= 0) or not np.isfinite(callbacks.dt) or callbacks.dt <= 0:
            raise ValueError("HE29_OPT_SCALE_OR_INTERVAL")
        counts_before = dict(callbacks.counts)
        output, stats, buffer = np.full_like(z0, np.nan), He29Stats(), ct.create_string_buffer(65536)
        failures = []

        def remember(exc):
            if not failures:
                failures.append(dict(error=repr(exc), traceback=traceback.format_exc()))
            return 1

        def invoke(method, u, z_ptr, n, out_ptr, vector_ptr=None):
            try:
                if n != callbacks.n or not z_ptr or not out_ptr:
                    raise ValueError("HE29_OPT_CALLBACK_ARITY")
                args = (u, np.ctypeslib.as_array(z_ptr, shape=(n,)))
                if vector_ptr is not None:
                    if not vector_ptr:
                        raise ValueError("HE29_OPT_NULL_DIRECTION")
                    args += (np.ctypeslib.as_array(vector_ptr, shape=(n,)),)
                value = finite_vector(method(*args), n, "callback output")
                np.ctypeslib.as_array(out_ptr, shape=(n,))[:] = value
                return 0
            except BaseException as exc:
                return remember(exc)

        def prepare(u, z_ptr, n, gas_ptr, photon_ptr):
            try:
                if n != callbacks.n or n <= 23 or not z_ptr or not gas_ptr or not photon_ptr:
                    raise ValueError("HE29_OPT_PREPARE_ARITY")
                packed = callbacks.prepare(u, np.ctypeslib.as_array(z_ptr, shape=(n,)))
                if packed.gas.shape != (n, 4) or packed.photon.shape != (12, n-23):
                    raise ValueError("HE29_OPT_PREPARE_SHAPE")
                np.ctypeslib.as_array(gas_ptr, shape=(4*n,))[:] = packed.gas.ravel()
                np.ctypeslib.as_array(photon_ptr, shape=(12*(n-23),))[:] = packed.photon.ravel()
                return 0
            except BaseException as exc:
                return remember(exc)

        rhs = RHS_CALLBACK(lambda context,u,z,n,out: invoke(callbacks.rhs,u,z,n,out))
        partial = RHS_CALLBACK(lambda context,u,z,n,out: invoke(callbacks.partial_u,u,z,n,out))
        common = (z0.size, z0.ctypes.data_as(DOUBLE_PTR), rhs)
        tail = (initial_step, max_step, max_attempts, output.ctypes.data_as(DOUBLE_PTR),
                ct.byref(stats), buffer, len(buffer))
        if mode == "rust_packed":
            callback = PREPARE_CALLBACK(lambda context,u,z,n,gas,photon: prepare(u,z,n,gas,photon))
            rc = self._packed(*common, callback, partial, None,
                scale.ctypes.data_as(DOUBLE_PTR), callbacks.dt, threads, *tail)
        else:
            callback = JVP_CALLBACK(lambda context,u,z,v,n,out: invoke(callbacks.jvp,u,z,n,out,v))
            rc = self._legacy(*common, callback, partial, None, *tail)
        raw = buffer.value.decode("utf-8", "replace")
        try:
            telemetry = json.loads(raw)
        except (TypeError, ValueError):
            telemetry = {"malformed_or_truncated_json": raw}
        if not isinstance(telemetry, dict):
            telemetry = {"invalid_json_object": raw}
        counts_delta = {name:value-counts_before.get(name, 0)
                        for name,value in callbacks.counts.items()}
        evidence = dict(returncode=rc, stats={name:getattr(stats,name) for name,_ in He29Stats._fields_},
            telemetry=telemetry, python_callbacks=counts_delta,
            python_callbacks_lifetime=dict(callbacks.counts), callback_failures=failures,
            requested_mode=mode, requested_threads=threads)
        valid = (rc == 0 and not failures and stats.status == 0 and stats.abi_version == ABI_VERSION
            and stats.dimension == z0.size and stats.final_u == 1. and stats.output_samples == 2
            and telemetry.get("success") is True and telemetry.get("vigilode_source") == VIGILODE_SOURCE
            and telemetry.get("dense_output_used") is False and telemetry.get("rtol") == 1e-10
            and telemetry.get("atol_scaled") == 1e-12 and np.isfinite(output).all())
        if mode == "rust_packed":
            valid = valid and (telemetry.get("threads") == threads and stats.callback_jvp_calls == 0
                and telemetry.get("jvp_mode") == "rust-packed-exact-state"
                and telemetry.get("packed_prepare_successes") == counts_delta["packed_preparations"])
        if not valid:
            state = output.tolist() if np.isfinite(output).all() else None
            raise VigilODEFailure("HE29_OPT_SEGMENT_NOT_ADMITTED", evidence, state)
        return output, evidence


def solve_packed(model, bridge, checkpoint, *, max_attempts=10000):
    """NCP canary path is sequential; no extra native job or tolerance change."""
    scale, initial, bounds = validate_model(model)
    z, records = initial / scale, []
    for index, (left, right) in enumerate(zip(bounds[:-1], bounds[1:])):
        model.set_interval(float(left), float(right))
        callbacks = PackedSegmentCallbacks(model, left, right, scale)
        prefix = dict(segment=index, left_s=float(left), right_s=float(right))
        try:
            next_z, evidence = bridge.segment(callbacks, z, threads=1, max_attempts=max_attempts)
        except VigilODEFailure as exc:
            checkpoint({**prefix, "complete":False, "evidence":exc.evidence,
                "last_completed_physical_state":(z*scale).tolist(), "partial_observed_scaled_state":exc.state})
            raise
        z = next_z
        checkpoint({**prefix, "complete":True, "evidence":evidence, "physical_state":(z*scale).tolist()})
        records.append({**prefix, "evidence":evidence})
    metadata = dict(method="VigilODE-RODAS5P-packed", rtol=1e-10, atol_scaled=1e-12,
        segment_count=len(records), t_end_s=float(model.t_end), vigilode_source=VIGILODE_SOURCE,
        dense_output_used=False, jacobian="original gas FD and analytic photon columns; packed Rust JVP",
        partial_time="reused bounded represented-time finite differences", threads=1,
        new_global_error_bound=False, segments=records,
        optimization_counts=dict(getattr(model, "optimization_counts", {})))
    return model.result(z*scale, metadata)
