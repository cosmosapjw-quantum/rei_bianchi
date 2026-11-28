#!/usr/bin/env python3
"""Small real C-ABI checks through the same HE29 Python bridge class.

This executes an analytic two-state model, not any historical HE28/HE29
campaign or VigilODE suite. It does not qualify the HE29 physical model.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import sys
import time

import numpy as np


class AnalyticModel:
    """Known nonautonomous scaled solution on a strict finite time domain."""

    def __init__(self, *, fail=False):
        self.left, self.right = 37.25, 37.625
        self.dt = self.right - self.left
        self.scale = np.array([3., 0.002])
        self.times = []
        self.fail = fail

    def normalized_time(self, t):
        if not self.left <= t <= self.right:
            raise ValueError("analytic model evaluated outside its domain")
        self.times.append(float(t))
        return (t - self.left) / self.dt

    def rhs(self, t, y):
        u = self.normalized_time(t)
        if self.fail:
            raise RuntimeError("injected HE29 bridge smoke callback failure")
        z = np.asarray(y) / self.scale
        f = np.array([-40. * (z[0] - (1. + u + u*u)) + 1. + 2.*u,
                      -3. * z[1] + 1. + 3.*u])
        return self.scale * f / self.dt

    def jac(self, t, y):
        self.normalized_time(t)
        return np.diag([-40., -3.]) / self.dt

    @staticmethod
    def exact(u):
        return np.array([1. + u + u*u, 2. * math.exp(-3.*u) + u])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--lane", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    sys.path.insert(0, str(args.lane / "src"))
    from vigilode_callbacks import SegmentCallbacks
    from vigilode_reference import VigilODEBridge, VigilODEFailure

    bridge = VigilODEBridge(args.library, args.receipt)
    cases = []
    def checked(name, operation):
        started = time.perf_counter()
        try:
            record = operation()
            record.update(name=name, status="PASS")
        except BaseException as exc:
            record = dict(name=name, status="FAIL", error=repr(exc))
            if isinstance(exc, VigilODEFailure):
                record["evidence"] = exc.evidence
                record["partial_observed_state"] = exc.state
        record["elapsed_seconds"] = time.perf_counter() - started
        cases.append(record)

    def analytic_endpoint():
        model = AnalyticModel()
        cb = SegmentCallbacks(model, model.left, model.right, model.scale)
        initial = model.exact(0.)
        # Probe both boundary stencils through the same callback object. The
        # physical RHS enforces the interval; no out-of-domain extrapolation.
        derivatives = [cb.partial_u(u, initial) for u in (0., 1.)]
        exact_derivatives = [np.array([42., 3.]), np.array([122., 3.])]
        edge_error = max(float(np.max(np.abs(a-b)))
                         for a, b in zip(derivatives, exact_derivatives))
        assert edge_error <= 1.e-6, ("partial-time edge derivative", edge_error)
        output, evidence = bridge.segment(cb, initial)
        error = float(np.max(np.abs(output - model.exact(1.))))
        # This small known-solution regression threshold is separate from all
        # HE29 physical gates and is not a solver-wide error bound.
        assert error <= 3.e-9, ("analytic scaled endpoint", error)
        assert evidence["stats"]["callback_rhs_calls"] > 0
        assert evidence["stats"]["callback_jvp_calls"] > 0
        assert evidence["stats"]["callback_partial_u_calls"] > 0
        assert evidence["stats"]["direct_factorizations"] == 0
        assert evidence["telemetry"]["error_estimate_is_global_bound"] is False
        assert min(model.times) >= model.left and max(model.times) <= model.right
        return dict(expected_scaled_endpoint=model.exact(1.).tolist(),
                    actual_scaled_endpoint=output.tolist(), max_absolute_scaled_error=error,
                    smoke_absolute_threshold=3.e-9, edge_derivative_max_absolute_error=edge_error,
                    min_physical_time=min(model.times), max_physical_time=max(model.times),
                    physical_interval=[model.left, model.right], evidence=evidence)

    def callback_failure():
        model = AnalyticModel(fail=True)
        cb = SegmentCallbacks(model, model.left, model.right, model.scale)
        try:
            bridge.segment(cb, model.exact(0.))
        except VigilODEFailure as exc:
            assert exc.evidence["returncode"] == 3, exc.evidence
            assert exc.evidence["stats"]["status"] == 3
            assert len(exc.evidence["callback_failures"]) == 1
            assert "injected HE29 bridge smoke" in exc.evidence["callback_failures"][0]["error"]
            assert exc.evidence["telemetry"]["success"] is False
            return dict(evidence=exc.evidence, partial_observed_scaled_state=exc.state)
        raise AssertionError("foreign callback failure was admitted")

    def partial_attempt():
        model = AnalyticModel()
        cb = SegmentCallbacks(model, model.left, model.right, model.scale)
        initial = model.exact(0.)
        try:
            bridge.segment(cb, initial, initial_step=1/128, max_step=1/128, max_attempts=1)
        except VigilODEFailure as exc:
            stats = exc.evidence["stats"]
            assert exc.evidence["returncode"] == 1 and stats["status"] == 1
            assert stats["attempts"] == 1 and stats["output_samples"] == 1
            assert stats["final_u"] == 0. and exc.state == initial.tolist()
            assert exc.evidence["telemetry"]["success"] is False
            assert not exc.evidence["callback_failures"]
            return dict(evidence=exc.evidence, partial_observed_scaled_state=exc.state,
                        partial_state_is_initial_observation=True)
        raise AssertionError("one sub-endpoint attempt was admitted as a complete segment")

    checked("analytic_nonautonomous_endpoint_and_domain_edges", analytic_endpoint)
    checked("python_exception_is_callback_failure", callback_failure)
    checked("attempt_limit_is_partial_observation", partial_attempt)
    files = [Path(__file__), args.lane / "src/vigilode_callbacks.py",
             args.lane / "src/vigilode_reference.py"]
    report = dict(schema="he29.vigilode.ffi-smoke.v1",
                  status="PASS" if all(c["status"] == "PASS" for c in cases) else "FAIL",
                  actual_rust_ffi_attempted=True, model="two-state analytic nonautonomous model",
                  scope="new bridge boundary only", he29_reference_cases_executed=0,
                  historical_suites_executed=0, new_physics_admission=False,
                  build_receipt_sha256=sha256(args.receipt.read_bytes()).hexdigest(),
                  library_sha256=sha256(args.library.read_bytes()).hexdigest(),
                  source_sha256={str(p.relative_to(args.lane)) if p.is_relative_to(args.lane)
                                 else p.name: sha256(p.read_bytes()).hexdigest() for p in files},
                  cases=cases)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": report["status"],
                      "cases": [{k: c[k] for k in ("name", "status", "elapsed_seconds")} for c in cases],
                      "output": str(args.output)}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
