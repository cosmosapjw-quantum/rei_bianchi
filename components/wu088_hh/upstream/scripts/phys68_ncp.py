#!/usr/bin/env python3
"""Prepare or explicitly run the optional PHYS68 finite-L64 extension.

Default: bounded mathematical preflight only. The completed L28 request is
not a selectable profile. A run delegates to the existing profile solver,
with exact source/request/engine/runtime binding and safe automatic resume.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))

import flint
from flint import ctx

from wu088_hh.phys63_lap_contract import source_guard
from wu088_hh.phys65_exterior_bounds import SOURCE_SHA
from wu088_hh.phys66_radial_budget import certificate as radial_certificate, to_jsonable
from wu088_hh.phys67_coulomb_certificate import complex_ball_record, dyadic_ball
from wu088_hh.phys68_angular import angular_taylor_coefficients
from wu088_hh.phys68_profiles import ProfileRequest, engine_identity
from wu088_hh.phys68_taylor import coulomb_taylor


FIXED_REQUEST = {
    "max_ell": 64, "ell": 21, "ellprime": 20, "outer": "65",
    "half_width": "1/8", "zero_free_radius": "1/4", "majorant_radius": "2",
    "degree": 96, "precision_bits": 768, "coefficient_bits": 2048,
    "d1_absolute_goal": "1e-45", "d2_absolute_goal": "1e-62",
}
FROZEN_SOURCE = ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"
PHYS66_LONGTAIL_ZIP_SHA256 = "34a59dfe3158c454811ed6e6f47c82357e502ef8cdef9ee5f14640b37f73a835"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read_request(path=None):
    payload = json.loads(Path(path).read_text()) if path is not None else dict(FIXED_REQUEST)
    if not isinstance(payload, dict) or set(payload) != set(FIXED_REQUEST):
        raise ValueError("complete fixed PHYS68 L64 request fields required")
    request = ProfileRequest(**payload).validate()
    if asdict(request) != FIXED_REQUEST:
        raise ValueError("only the fixed optional L64 extension is supported; completed L28 is excluded")
    return request


def binding_for(request, source):
    request.validate()
    if asdict(request) != FIXED_REQUEST:
        raise ValueError("unsupported request: this wrapper only prepares the fixed L64 extension")
    return {"request": asdict(request), "source_sha256": source_guard(source), "engine": engine_identity()}


def inspect_destination(out_root, binding):
    """Read-only selection; refuse incompatible/unbound output before a child starts."""
    base = Path(out_root).expanduser().resolve()
    fingerprint = digest(binding)
    output = base/("phys68_l64_"+fingerprint)
    if base.exists() and not base.is_dir():
        raise ValueError("output root must be a directory")
    if output.is_symlink() or (output.exists() and not output.is_dir()):
        raise ValueError("selected output must be an ordinary directory")
    resume = False
    if output.exists():
        request_path = output/"REQUEST.json"
        if request_path.exists():
            prior = json.loads(request_path.read_text())
            if (prior.get("schema") != "PHYS68_PROFILE_REQUEST_V1" or
                    prior.get("fingerprint") != fingerprint or prior.get("binding") != binding):
                raise ValueError("existing output request/source/engine/runtime fingerprint mismatch")
            resume = True
        elif any(output.iterdir()):
            raise ValueError("nonempty output has no bound REQUEST.json")
    # A previous result with identical scientific request but a different
    # engine/runtime needs explicit reconciliation, not an automatic new run.
    if base.is_dir():
        for path in base.glob("phys68_l64_*/REQUEST.json"):
            if path.parent == output:
                continue
            prior = json.loads(path.read_text())
            other = prior.get("binding", {})
            if (other.get("request") == binding["request"] and
                    other.get("source_sha256") == binding["source_sha256"]):
                raise ValueError("same scientific request exists with another engine/runtime; reconcile before a new run")
    return {"fingerprint": fingerprint, "output": str(output), "resume": resume,
            "output_exists": output.exists(), "profile_request_sha256": digest(binding["request"])}


def mathematical_preflight(request, source):
    """Four Coulomb disks and two angular Taylor calls, zero radial panels."""
    request.validate()
    if asdict(request) != FIXED_REQUEST:
        raise ValueError("unsupported preflight request")
    source_guard(source)
    if flint.__version__ != "0.8.0" or flint.__FLINT_VERSION__ != "3.3.1":
        raise ValueError("preflight requires python-flint 0.8.0 / FLINT 3.3.1; install the pinned runtime")
    begin = time.monotonic()
    center = Fraction(217, 8)
    rho = Fraction(request.zero_free_radius)
    big = Fraction(request.majorant_radius)
    gates = []
    for ell in (0, 20, 21, 64):
        disk = coulomb_taylor(ell, center, request.degree, big, request.precision_bits)
        lower = disk.zero_free_lower(rho)
        if not lower > 0:
            raise ArithmeticError(f"UNRESOLVED_ZERO_FREE_BOUND ell={ell}, center=217/8, rho=1/4")
        gates.append({"ell": ell, "center": "217/8", "radius": "1/4",
                      "strictly_positive": True, "zero_free_lower": dyadic_ball(lower)})
    angular = []
    for ell, ellprime in ((21, 64), (20, 64)):
        values = angular_taylor_coefficients(ell, ellprime, center, request.degree,
                                            request.precision_bits, request.coefficient_bits)
        if len(values) != request.degree+1 or not all(v.is_finite() for v in values):
            raise ArithmeticError("nonfinite or incomplete high-order angular Taylor result")
        with ctx.workprec(request.precision_bits):
            angular.append({"ell": ell, "ellprime": ellprime, "coefficient_count": len(values),
                            "all_finite": True, "coefficient_0": complex_ball_record(values[0]),
                            "coefficient_96": complex_ball_record(values[-1]),
                            "maximum_coefficient_ball_radius_upper": dyadic_ball(max(v.rad().upper() for v in values))})
    radial = radial_certificate(source, request.max_ell, request.outer, 2)
    beta2 = radial["terms"][1]["radial_cutoff_bound"]
    if not beta2 < Fraction(request.d2_absolute_goal):
        raise ValueError("analytic radial tail alone exceeds the fixed D2 absolute budget")
    return {"status": "PREFLIGHT_ONLY_PASS", "elapsed_seconds": time.monotonic()-begin,
            "source_sha256": SOURCE_SHA, "request": asdict(request),
            "versions": {"python": platform.python_version(), "python_flint": flint.__version__,
                         "flint": flint.__FLINT_VERSION__},
            "Coulomb_zero_free_gates": gates, "angular_taylor_probes": angular,
            "analytic_radial_tail_D2": to_jsonable(beta2), "radial_tail_below_D2_goal": True,
            "scientific_execution": {"Coulomb_disk_probes": 4, "angular_Taylor_probes": 2,
                                     "radial_panels": 0, "D1_integrations": 0, "D2_integrations": 0},
            "claim": "Selected kernel compatibility and zero-free preflight only; campaign goals remain unexecuted.",
            "scope": "OPTIONAL_FINITE_L64_EXTENSION_NOT_EXCLUDED_ANGULAR_CLOSURE", "HH_R10": "OFF"}


def solver_command(plan, request_path, source, python_executable=sys.executable):
    command = [str(python_executable), str(ROOT/"scripts/phys68_profiles.py"),
               "--source", str(Path(source).resolve()), "--out", plan["output"],
               "--request", str(Path(request_path).resolve())]
    if plan["resume"]:
        command.append("--resume")
    return command


@contextmanager
def campaign_lock(out_root, fingerprint):
    """Refuse concurrent wrapper submissions for this exact fingerprint."""
    import fcntl
    directory = Path(out_root).resolve()/"locks"
    directory.mkdir(parents=True, exist_ok=True)
    with (directory/(fingerprint+".lock")).open("a+") as stream:
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("a wrapper already owns this campaign fingerprint") from exc
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def invocation_lines(path):
    path = Path(path)
    return [line for line in path.read_text().splitlines() if line.strip()] if path.exists() else []


def new_child_invocation(path, previous_count, fingerprint):
    """Return only an appended invocation; a killed child cannot inherit an old success."""
    lines = invocation_lines(path)
    if len(lines) <= previous_count:
        return None
    result = json.loads(lines[-1])
    if result.get("fingerprint") not in (None, fingerprint):
        raise ValueError("new child invocation fingerprint differs from its launch")
    return result


def validate_limits(wall_seconds, memory_gib, ncp_limits=False):
    if type(wall_seconds) is not int or not 1 <= wall_seconds <= 86400:
        raise ValueError("integer wall_seconds in 1..86400 required")
    if type(memory_gib) is not int or not 1 <= memory_gib <= 128:
        raise ValueError("integer memory_gib in 1..128 required")
    if ncp_limits and platform.system() != "Linux":
        raise ValueError("--ncp-limits requires Linux resource.RLIMIT_AS")


def run_child(command, log_directory, wall_seconds=3600, memory_gib=4, ncp_limits=False,
              on_start=None):
    """Run one owned child with bounded wall time; optional Linux RLIMIT_AS."""
    validate_limits(wall_seconds, memory_gib, ncp_limits)
    logs = Path(log_directory)
    logs.mkdir(parents=True, exist_ok=False)
    environment = os.environ.copy()
    for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS"):
        environment[key] = "1"
    environment["PYTHONUNBUFFERED"] = "1"
    def constrain():
        if ncp_limits:
            import resource
            bound = memory_gib*1024**3
            resource.setrlimit(resource.RLIMIT_AS, (bound, bound))
            os.nice(10)
    started = time.monotonic()
    with (logs/"STDOUT.jsonl").open("w") as stdout, (logs/"STDERR.txt").open("w") as stderr:
        child = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=environment,
                                 start_new_session=True, preexec_fn=constrain if ncp_limits else None)
        if on_start is not None:
            on_start(child.pid)
        timed_out = False
        try:
            returncode = child.wait(timeout=wall_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(child.pid, signal.SIGTERM)
            try:
                returncode = child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                returncode = child.wait()
    return {"child_pid": child.pid, "returncode": returncode,
            "timed_out": timed_out, "wall_seconds_limit": wall_seconds,
            "elapsed_seconds": time.monotonic()-started,
            "memory_gib_limit": memory_gib if ncp_limits else None,
            "ncp_resource_limits_applied": ncp_limits,
            "single_process": True, "BLAS_threads": 1, "logs": str(logs)}


def _write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False)+"\n"
    if path.exists():
        if path.read_text() != payload:
            raise ValueError(f"refuse to overwrite a different saved object: {path.name}")
        return
    with path.open("x") as stream:
        stream.write(payload)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, help="complete exact fixed L64 request JSON")
    parser.add_argument("--source", type=Path, default=FROZEN_SOURCE)
    parser.add_argument("--out-root", type=Path, default=ROOT/"runs/phys68_ncp")
    parser.add_argument("--run", action="store_true", help="explicitly launch the optional L64 campaign after preflight")
    parser.add_argument("--wall-seconds", type=int, default=3600)
    parser.add_argument("--memory-gib", type=int, default=4)
    parser.add_argument("--ncp-limits", action="store_true", help="apply Linux address-space limit and nice10 to the solver child")
    args = parser.parse_args(argv)
    started = datetime.now(timezone.utc).isoformat()
    record = {"schema": "PHYS68_NCP_INVOCATION_V1", "started_utc": started,
              "run_explicitly_requested": args.run, "solver_started": False,
              "PHYS66_longtail_state": "NOT_SUBMITTED_BY_THIS_WRAPPER",
              "PHYS66_longtail_zip_sha256": PHYS66_LONGTAIL_ZIP_SHA256,
              "HH_R10": "OFF"}
    try:
        validate_limits(args.wall_seconds, args.memory_gib, args.ncp_limits)
        request = read_request(args.request)
        binding = binding_for(request, args.source)
        plan = inspect_destination(args.out_root, binding)
        record.update({"binding": binding, "plan": plan,
                       "wrapper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                       "input_request_file_sha256": hashlib.sha256(args.request.read_bytes()).hexdigest() if args.request else None})
        preflight = mathematical_preflight(request, args.source)
        # No kernel or operational engine bytes may change during a preflight.
        if binding_for(request, args.source) != binding:
            raise ValueError("engine/source/runtime changed during preflight")
        record["preflight"] = preflight
        token = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        receipts = Path(args.out_root).resolve()/"receipts"/plan["fingerprint"]
        request_path = Path(args.out_root).resolve()/"requests"/(plan["fingerprint"]+".json")
        _write_new(request_path, asdict(request))
        _write_new(receipts/(token+"_PREFLIGHT.json"), preflight)
        record["request_file"] = str(request_path)
        if not args.run:
            record["status"] = "PREPARED_NOT_SUBMITTED"
            code = 0
        else:
            with campaign_lock(args.out_root, plan["fingerprint"]):
                # Recheck after acquiring the lock, immediately before launch.
                plan = inspect_destination(args.out_root, binding)
                command = solver_command(plan, request_path, args.source)
                record["command"] = command
                invocations = Path(plan["output"])/"INVOCATIONS.jsonl"
                previous_count = len(invocation_lines(invocations))
                record["invocation_count_before_child"] = previous_count
                def mark_started(pid):
                    record.update({"solver_started": True, "child_pid": pid})
                child = run_child(command, receipts/(token+"_SOLVER"), args.wall_seconds,
                                  args.memory_gib, args.ncp_limits, mark_started)
                record["child"] = child
                current = new_child_invocation(invocations, previous_count, plan["fingerprint"])
                record["solver_new_invocation"] = current
                record["stored_panel_files_after_child"] = len(list(Path(plan["output"]).glob("panel_*.json")))
                code = 124 if child["timed_out"] else (0 if child["returncode"] == 0 and current is not None else 1)
                record["status"] = ("TIMEOUT_OUTPUT_RETAINED" if child["timed_out"] else
                                    current["status"] if current is not None else "CHILD_EXIT_WITHOUT_NEW_INVOCATION")
        record["finished_utc"] = datetime.now(timezone.utc).isoformat()
        record["exit_code"] = code
        _write_new(receipts/(token+"_INVOCATION.json"), record)
    except Exception as exc:
        record.update({"status": "FAILED_BEFORE_LAUNCH" if not record["solver_started"] else "CHILD_OR_RECORD_FAILURE",
                       "error_type": type(exc).__name__, "error": str(exc), "exit_code": 1,
                       "finished_utc": datetime.now(timezone.utc).isoformat()})
        code = 1
    print(json.dumps(record, sort_keys=True, ensure_ascii=False), flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
