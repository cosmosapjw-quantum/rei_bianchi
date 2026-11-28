"""Verified-library loader and endpoint-only VigilODE reference adapter.

This is an optional third-method canary. It cannot mark any of the four
Radau/DOP853 baseline pairs complete. The Rust library is loaded only after
its build receipt and local source hashes have been checked.
"""
from __future__ import annotations

import ctypes as ct
from hashlib import sha256
import json
from pathlib import Path
import traceback

import numpy as np

from vigilode_callbacks import SegmentCallbacks, finite_vector, validate_model

BASELINE_CODE = "1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f"
VIGILODE_SOURCE = "a21d573980f66fe02891bd216153443b5352f921"
LANE = Path(__file__).resolve().parents[1]
ABI_VERSION = 1
DOUBLE_PTR = ct.POINTER(ct.c_double)
RHS_CALLBACK = ct.CFUNCTYPE(ct.c_int32, ct.c_void_p, ct.c_double,
                          DOUBLE_PTR, ct.c_size_t, DOUBLE_PTR)
JVP_CALLBACK = ct.CFUNCTYPE(ct.c_int32, ct.c_void_p, ct.c_double,
                          DOUBLE_PTR, DOUBLE_PTR, ct.c_size_t, DOUBLE_PTR)


class He29Stats(ct.Structure):
    _fields_ = [
        ("abi_version", ct.c_uint32), ("status", ct.c_int32),
        ("dimension", ct.c_size_t), ("final_u", ct.c_double),
        *[(k, ct.c_size_t) for k in ("output_samples", "internal_steps",
          "output_clipped_steps", "attempts", "accepted_macro_steps", "rejected_macro_steps")],
        *[(k, ct.c_uint64) for k in ("rhs_evaluations", "jvp_vectors", "linear_iterations",
          "direct_factorizations", "callback_rhs_calls", "callback_jvp_calls",
          "callback_partial_u_calls")],
        ("json_required_bytes", ct.c_size_t),
    ]


class VigilODEFailure(RuntimeError):
    def __init__(self, message, evidence, state=None):
        super().__init__(message)
        self.evidence, self.state = evidence, state


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def verify_build(library, receipt, lane=LANE):
    library = Path(library).resolve(strict=True)
    receipt = Path(receipt).resolve(strict=True)
    data = json.loads(receipt.read_text())
    required = {"schema": "he29.vigilode.build.v1", "status": "COMPILED",
                "abi_version": ABI_VERSION, "vigilode_source": VIGILODE_SOURCE,
                "baseline_code_revision": BASELINE_CODE}
    if any(data.get(k) != v for k, v in required.items()):
        raise ValueError("HE29_VIGILODE_BUILD_CONTRACT")
    if data.get("library_sha256") != digest(library):
        raise ValueError("HE29_VIGILODE_LIBRARY_HASH")
    sources = data.get("bridge_sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("HE29_VIGILODE_SOURCE_RECEIPT_MISSING")
    expected_paths = {"rust_bridge/Cargo.toml", "rust_bridge/Cargo.lock",
                      "rust_bridge/src/lib.rs", "rust_bridge/include/he29_vigilode_bridge.h"}
    if set(sources) != expected_paths:
        raise ValueError("HE29_VIGILODE_SOURCE_RECEIPT_PATHS")
    for relative, expected in sources.items():
        path = Path(lane) / relative
        if not isinstance(expected, str) or digest(path) != expected:
            raise ValueError("HE29_VIGILODE_BRIDGE_SOURCE_MISMATCH: " + relative)
    return {**data, "receipt_sha256": digest(receipt)}


class VigilODEBridge:
    def __init__(self, library, receipt):
        self.identity = verify_build(library, receipt)
        self.library = ct.CDLL(str(Path(library).resolve()))
        abi = self.library.he29_vigilode_abi_version
        abi.argtypes, abi.restype = [], ct.c_uint32
        if abi() != ABI_VERSION:
            raise ValueError("HE29_VIGILODE_ABI_VERSION")
        self._solve = self.library.he29_vigilode_segment
        self._solve.argtypes = [ct.c_size_t, DOUBLE_PTR, RHS_CALLBACK, JVP_CALLBACK,
            RHS_CALLBACK, ct.c_void_p, ct.c_double, ct.c_double, ct.c_size_t,
            DOUBLE_PTR, ct.POINTER(He29Stats), ct.POINTER(ct.c_char), ct.c_size_t]
        self._solve.restype = ct.c_int32

    def segment(self, callbacks, z0, *, initial_step=1/32, max_step=1., max_attempts=10000):
        z0 = np.array(finite_vector(z0, callbacks.n, "initial scaled state"),
                      dtype=np.float64, order="C", copy=True)
        if (not np.isfinite([initial_step, max_step]).all()
                or not 0 < initial_step <= max_step <= 1
                or type(max_attempts) is not int or not 0 < max_attempts <= 100000):
            raise ValueError("HE29_VIGILODE_STEP_BUDGET")
        output = np.full_like(z0, np.nan)
        stats, buffer = He29Stats(), ct.create_string_buffer(65536)
        callback_failure = []

        def invoke(method, u, z_ptr, n, out_ptr, vector_ptr=None):
            # Never let a Python exception escape a foreign callback.
            try:
                if n != callbacks.n or not z_ptr or not out_ptr:
                    raise ValueError("HE29_VIGILODE_CALLBACK_ARITY")
                z = np.ctypeslib.as_array(z_ptr, shape=(n,))
                args = (u, z)
                if vector_ptr is not None:
                    if not vector_ptr:
                        raise ValueError("HE29_VIGILODE_NULL_DIRECTION")
                    args += (np.ctypeslib.as_array(vector_ptr, shape=(n,)),)
                value = finite_vector(method(*args), n, "callback output")
                np.ctypeslib.as_array(out_ptr, shape=(n,))[:] = value
                return 0
            except BaseException as exc:
                if not callback_failure:
                    callback_failure.append({"error": repr(exc), "traceback": traceback.format_exc()})
                return 1

        rhs = RHS_CALLBACK(lambda context, u, z, n, out:
                           invoke(callbacks.rhs, u, z, n, out))
        jvp = JVP_CALLBACK(lambda context, u, z, v, n, out:
                           invoke(callbacks.jvp, u, z, n, out, v))
        partial = RHS_CALLBACK(lambda context, u, z, n, out:
                               invoke(callbacks.partial_u, u, z, n, out))
        rc = self._solve(z0.size, z0.ctypes.data_as(DOUBLE_PTR), rhs, jvp, partial,
                         None, initial_step, max_step, max_attempts,
                         output.ctypes.data_as(DOUBLE_PTR), ct.byref(stats), buffer, len(buffer))
        raw = buffer.value.decode("utf-8", "replace")
        try:
            telemetry = json.loads(raw)
        except (ValueError, TypeError):
            telemetry = {"malformed_or_truncated_json": raw}
        if not isinstance(telemetry, dict):
            telemetry = {"invalid_json_object": raw}
        evidence = {"returncode": rc,
                    "stats": {name: getattr(stats, name) for name, _ in He29Stats._fields_},
                    "telemetry": telemetry, "python_callbacks": dict(callbacks.counts),
                    "callback_failures": callback_failure}
        valid = (rc == 0 and not callback_failure and stats.status == 0
                 and stats.abi_version == ABI_VERSION and stats.dimension == z0.size
                 and stats.final_u == 1. and stats.output_samples == 2
                 and telemetry.get("success") is True
                 and telemetry.get("vigilode_source") == VIGILODE_SOURCE
                 and telemetry.get("dense_output_used") is False
                 and telemetry.get("rtol") == 1e-10
                 and telemetry.get("atol_scaled") == 1e-12
                 and np.isfinite(output).all())
        if not valid:
            state = output.tolist() if np.isfinite(output).all() else None
            raise VigilODEFailure("HE29_VIGILODE_SEGMENT_NOT_ADMITTED", evidence, state)
        return output, evidence


def solve_vigilode(model, bridge, checkpoint, *, max_attempts=10000):
    """Advance original cutoff segments and retain each observed endpoint.

    ``checkpoint`` persists one record synchronously. Failure writes the last
    completed physical endpoint plus the returned partial solver evidence.
    No intermediate dense sample is used, and no state is clipped.
    """
    scale, initial, bounds = validate_model(model)
    z = initial / scale
    records = []
    for index, (left, right) in enumerate(zip(bounds[:-1], bounds[1:])):
        model.set_interval(float(left), float(right))
        cb = SegmentCallbacks(model, left, right, scale)
        prefix = {"segment": index, "left_s": float(left), "right_s": float(right)}
        try:
            next_z, evidence = bridge.segment(cb, z, max_attempts=max_attempts)
        except VigilODEFailure as exc:
            checkpoint({**prefix, "complete": False, "evidence": exc.evidence,
                        "last_completed_physical_state": (z * scale).tolist(),
                        "partial_observed_scaled_state": exc.state})
            raise
        z = next_z
        record = {**prefix, "complete": True, "evidence": evidence,
                  "physical_state": (z * scale).tolist()}
        checkpoint(record)
        records.append({**prefix, "evidence": evidence})
    metadata = {"method": "VigilODE-RODAS5P", "rtol": 1e-10, "atol_scaled": 1e-12,
                "segment_count": len(records), "t_end_s": float(model.t_end),
                "vigilode_source": VIGILODE_SOURCE, "dense_output_used": False,
                "jacobian": "unchanged parent sparse Jacobian, exact-state cache",
                "partial_time": "bounded represented-time finite differences",
                "new_global_error_bound": False, "segments": records}
    return model.result(z * scale, metadata)
