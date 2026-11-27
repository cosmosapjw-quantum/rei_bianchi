#!/usr/bin/env python3
"""Complete the optional validated L64 coefficient using only new j=37..64.

The default command only reads pinned inputs and prints a plan.  --run launches
independent process workers, each carrying two Volterra profiles backward on
152 panels.  PHYS68/69 certificates supply j=0..36 without any old integration.
FLINT precision is process-global, so numerical kernels never share threads.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal, ROUND_CEILING, ROUND_HALF_EVEN, localcontext
from fractions import Fraction as F
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import re
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"
SOURCE_SHA = "f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
OLD_PATH = "research/hh_phys68_20261019/profiles/run_l28_t65_completed/CERTIFICATE.json"
OLD_SHA = "ddaae206009a276def281af5526851ceb717baf2e0de5f8472552a9db340de9a"
BAND_PATH = "research/hh_phys69_20261019/band/run_j29_36_t65/CERTIFICATE.json"
BAND_SHA = "e123f084bea390a25162826f306c115d683b7c9fd3157b15967c88814787d0c8"
MODES = tuple(range(37, 65))
PANELS = 152
D1_GOAL, D2_GOAL = F("1e-45"), F("1e-62")
THREAD_KEYS = ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
               "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS")
_WORKER_RESOURCE = {"resource_limits_applied": False}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def same(actual, expected, label):
    if canonical(actual) != canonical(expected):
        raise ValueError(label + " mismatch")


def integer(value, low=None, high=None):
    if type(value) is int:
        answer = value
    elif type(value) is str and re.fullmatch(r"[+-]?[0-9]+", value):
        answer = int(value)
    else:
        raise ValueError("exact integer required; floats and bools refused")
    if low is not None and answer < low or high is not None and answer > high:
        raise ValueError("integer outside the permitted domain")
    return answer


def exact(value):
    if type(value) not in (int, str, F):
        raise ValueError("exact integer/string/Fraction required")
    return F(value)


def rational(value):
    value = exact(value)
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def read_rational(value):
    if not isinstance(value, dict) or set(value) != {"numerator", "denominator"}:
        raise ValueError("rational record required")
    den = integer(value["denominator"], 1)
    return F(integer(value["numerator"]), den)


def dyadic(value):
    if not isinstance(value, dict) or set(value) != {"mantissa", "exponent2"}:
        raise ValueError("dyadic record required")
    if type(value["exponent2"]) is not int:
        raise ValueError("exact integer exponent required")
    exponent = integer(value["exponent2"], -262144, 262144)
    return F(integer(value["mantissa"])) * F(2) ** exponent


def real_ball(value):
    if not isinstance(value, dict) or not {"midpoint", "radius"} <= set(value):
        raise ValueError("real ball record required")
    mid, rad = dyadic(value["midpoint"]), dyadic(value["radius"])
    if rad < 0:
        raise ValueError("negative radius")
    return mid, rad


def box(value):
    if not isinstance(value, dict) or set(value) != {"real", "imag"}:
        raise ValueError("complex rectangular ball required")
    return tuple(real_ball(value[c]) for c in ("real", "imag"))


def contains(outer, inner):
    return all(om - rr <= im - ir and im + ir <= om + rr
               for (om, rr), (im, ir) in zip(outer, inner))


def zero_record():
    r = {"display": "0", "midpoint": {"mantissa": "0", "exponent2": 0},
         "radius": {"mantissa": "0", "exponent2": 0}}
    return {"real": r, "imag": r}


def upward(value, digits=30):
    value = exact(value)
    if value < 0:
        raise ValueError("nonnegative upper bound required")
    with localcontext() as context:
        context.prec, context.rounding = digits, ROUND_CEILING
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def write_new(path, value):
    """Publish a complete immutable JSON file with an atomic no-replace link."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                         allow_nan=False) + "\n"
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    committed = created = False
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as stream:
            created = True
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        # Both names are on the same filesystem. Unlike replace(), link()
        # refuses to overwrite any existing immutable target, including a link.
        os.link(temporary, path)
        committed = True
    finally:
        if created:
            temporary.unlink(missing_ok=True)
        if committed:
            descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)


def fixed_request(j):
    j = integer(j, 37, 64)
    return {"min_ell": j, "max_ell": j, "ell": 21, "ellprime": 20,
            "outer": "65", "half_width": "1/8", "zero_free_radius": "1/4",
            "majorant_radius": "2", "degree": 96, "precision_bits": 768,
            "coefficient_bits": 2048, "d2_numerical_absolute_goal": "1e-64"}


def load_pinned(path, expected):
    data = Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError("pinned input SHA256 mismatch: " + Path(path).name)
    return json.loads(data)


def inherited(repo=ROOT):
    repo = Path(repo)
    if sha(repo / SOURCE) != SOURCE_SHA:
        raise ValueError("frozen source SHA256 mismatch")
    old, band = load_pinned(repo / OLD_PATH, OLD_SHA), load_pinned(repo / BAND_PATH, BAND_SHA)
    for cert, modes in ((old, list(range(29))), (band, list(range(29, 37)))):
        same(cert["full_intermediate_sum"], modes, "inherited modes")
        for key, want in (("source_sha256", SOURCE_SHA), ("m", 0), ("HH_R10", "OFF")):
            same(cert[key], want, key)
        same(cert["request"]["outer"], "65", "inherited radial cutoff")
        same([cert["request"]["ell"], cert["request"]["ellprime"]], [21, 20], "external pair")
        if read_rational(cert["D2_numerical_absolute_error_l1"]) != sum(r for _, r in box(cert["D2_B_cutoff"])):
            raise ValueError("inherited D2 numerical radius mismatch")
    same(old["status"], "CERTIFIED_GOALS_MET", "old certificate completion")
    same(band["status"], "CERTIFIED_BAND_NUMERICAL_GOAL_MET", "band certificate completion")
    # Immutable certificates have already passed their original full campaigns.
    # Bind the reused kernels without re-opening the 152 inherited panel files.
    eng = band["engine"]
    pins = {"src/wu088_hh/" + n: h for n, h in eng["phys68_reused_engine"]["files_sha256"].items()}
    pins.update({"src/wu088_hh/phys69_band_profiles.py": eng["band_source_sha256"],
                 "scripts/phys69_band_profiles.py": eng["band_cli_sha256"],
                 "scripts/phys68_ncp.py": eng["process_wrapper_sha256"],
                 SOURCE: SOURCE_SHA, OLD_PATH: OLD_SHA, BAND_PATH: BAND_SHA})
    for name, expected in pins.items():
        if sha(repo / name) != expected:
            raise ValueError("reused engine/input bytes changed: " + name)
    q = {**old["D1_B_cutoff"], **band["D1_q_B_cutoff"]}
    if len(q) != 73:
        raise ValueError("inherited unique D1 pair coverage changed")
    return old, band, q, pins


def plan(repo=ROOT, modes=MODES, workers=28):
    workers = integer(workers, 1, 28)
    modes = tuple(integer(j, 37, 64) for j in modes)
    if not modes or len(set(modes)) != len(modes):
        raise ValueError("nonempty distinct new modes required")
    modes = tuple(sorted(modes))
    _, _, _, pins = inherited(repo)
    return {"schema": "PHYS73_VALIDATED_L64_PLAN_V1", "status": "PLANNED_NOT_RUN",
            "new_modes": list(modes), "complete_target_modes": list(MODES),
            "workers": min(workers, len(modes)), "parallel_axis": "independent intermediate j processes",
            "requests": [fixed_request(j) for j in modes], "panels_per_new_mode": PANELS,
            "new_panels_if_complete": PANELS * len(modes), "inherited_panel_payloads_reintegrated": 0,
            "inherited_unique_D1_pairs": 73, "new_unique_D1_pairs": 2 * len(modes),
            "input_pins": pins, "D1_goal": "1e-45", "D2_goal": "1e-62",
            "per_mode_D2_numerical_budget": "1e-64",
            "original_L64_precision": {"degree": 96, "precision_bits": 768, "coefficient_bits": 2048},
            "original_all_angular_D2": "COMPLETE_REUSED; optional finite-L64 extension",
            "scientific_integrations": 0, "special_function_calls": 0, "HH_R10": "OFF"}


@contextmanager
def lock(path):
    import fcntl
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError("lock path must not be a symlink")
    with path.open("a+") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("matching validated campaign/job is already active") from exc
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def numerical_modules(repo=ROOT):
    repo = Path(repo)
    sys.path.insert(0, str(repo / "src"))
    import flint
    if (flint.__version__, flint.__FLINT_VERSION__) != ("0.8.0", "3.3.1"):
        raise ValueError("requires python-flint0.8.0 / FLINT3.3.1")
    from wu088_hh import phys69_band_profiles as kernel
    return kernel


def initialize_worker(memory_gib):
    """Apply one process address-space ceiling; no process group is changed."""
    global _WORKER_RESOURCE
    if type(memory_gib) is not int:
        raise ValueError("integer worker memory GiB required")
    integer(memory_gib, 1, 16)
    if sys.platform != "linux":
        raise ValueError("bounded NCP worker requires Linux RLIMIT_AS")
    import resource
    requested = memory_gib * 1024**3
    _, hard = resource.getrlimit(resource.RLIMIT_AS)
    actual = requested if hard == resource.RLIM_INFINITY else min(requested, hard)
    resource.setrlimit(resource.RLIMIT_AS, (actual, actual))
    for key in THREAD_KEYS:
        os.environ[key] = "1"
    _WORKER_RESOURCE = {"resource_limits_applied": True, "requested_memory_gib": memory_gib,
                        "actual_address_space_limit_bytes": actual, "BLAS_threads": 1,
                        "process_group": os.getpgrp(), "process_id": os.getpid()}


def verify_new_certificate(directory, expected_binding):
    """Exact read-only hash/chain/coverage check; invokes no numerical kernel."""
    directory = Path(directory)
    req = expected_binding["request"]
    same(req, fixed_request(req["min_ell"]), "fixed one-j request")
    j, fingerprint = req["min_ell"], digest(expected_binding)
    request_file = json.loads((directory / "REQUEST.json").read_text())
    same(request_file.get("schema"), "PHYS69_BAND_REQUEST_V1", "request schema")
    same(request_file.get("binding"), expected_binding, "binding")
    same(request_file.get("fingerprint"), fingerprint, "request fingerprint")
    cert = json.loads((directory / "CERTIFICATE.json").read_text())
    fields = {"schema": "PHYS69_FINITE_T_BAND_CERTIFICATE_V1", "fingerprint": fingerprint,
              "request": req, "source_sha256": SOURCE_SHA, "engine": expected_binding["engine"],
              "scientific_execution": "COMPLETE", "full_intermediate_sum": [j],
              "Coulomb_modes": [20, 21, j], "pairs": [[20, j], [21, j]], "m": 0,
              "panel_count_required": PANELS, "HH_R10": "OFF",
              "radial_cutoff_error_included": False, "excluded_angular_error_included": False,
              "original_driven_xi_certified": False,
              "completed_PHYS68_intermediate_0_to_28_integrations": 0}
    for key, want in fields.items():
        same(cert.get(key), want, "certificate " + key)
    if len(cert["panels"]) != PANELS or len(list(directory.glob("panel_*.json"))) != PANELS:
        raise ValueError("complete 152-panel manifest required")
    state = {f"{a},{j}": zero_record() for a in (20, 21)}
    total = [[F(0), F(0)], [F(0), F(0)]]
    panel_pins = {}
    for index, item in enumerate(cert["panels"]):
        filename = f"panel_{index:04d}.json"
        same(item.get("index"), index, "panel index")
        same(item.get("file"), filename, "panel path")
        path = directory / filename
        if path.is_symlink():
            raise ValueError("saved panel must be an ordinary file")
        data = path.read_bytes()
        panel_pins[filename] = hashlib.sha256(data).hexdigest()
        saved = json.loads(data)
        payload = saved["payload"]
        for got in (saved.get("payload_sha256"), item.get("payload_sha256")):
            same(got, digest(payload), "payload SHA256")
        same(saved.get("fingerprint"), fingerprint, "panel fingerprint")
        same(saved.get("index"), index, "saved panel index")
        same(saved.get("right_state_sha256"), digest(state), "predecessor serialization hash")
        center = F(65) - F(2 * index + 1, 8)
        values = {"schema": "PHYS69_VALIDATED_BAND_VOLterra_PANEL_V1", "request": req,
                  "source_sha256": SOURCE_SHA, "center": str(center), "left": str(center - F(1, 8)),
                  "right": str(center + F(1, 8)), "half_width": "1/8",
                  "full_intermediate_sum": [j], "Coulomb_modes": [20, 21, j], "HH_R10": "OFF"}
        for key, want in values.items():
            same(payload.get(key), want, "panel " + key)
        same([row["pair"] for row in payload["pairs"]], [[20, j], [21, j]], "pair coverage")
        same([row["j"] for row in payload["second_Born_terms"]], [j], "D2 mode coverage")
        gates = payload["Coulomb_zero_free_lower"]
        same(sorted(gates), sorted(map(str, (20, 21, j))), "zero-free gate coverage")
        if any(real_ball(g)[0] - real_ball(g)[1] <= 0 for g in gates.values()):
            raise ValueError("nonpositive zero-free gate")
        for row in payload["pairs"]:
            key = ",".join(map(str, row["pair"]))
            if not contains(box(row["q_right"]), box(state[key])):
                raise ValueError("consumed q_right excludes its predecessor")
            box(row["q_left"])
            state[key] = row["q_left"]
        inc = box(payload["second_Born_increment"])
        if not contains(inc, box(payload["second_Born_terms"][0]["integral"])):
            raise ValueError("increment excludes its one-j term")
        for component in range(2):
            total[component][0] += inc[component][0]
            total[component][1] += inc[component][1]
    same(sorted(cert["D1_q_B_cutoff"]), sorted(state), "final D1 pair coverage")
    for key in state:
        if not contains(box(cert["D1_q_B_cutoff"][key]), box(state[key])):
            raise ValueError("final q boundary excludes saved carry")
    final = box(cert["D2_B_cutoff"])
    if not contains(final, total):
        raise ValueError("D2 certificate excludes exact saved increment sum")
    error = sum(rad for _, rad in final)
    same(cert["D2_numerical_absolute_error_l1"], rational(error), "D2 numerical radius")
    goal_met = error <= F(req["d2_numerical_absolute_goal"])
    same(cert.get("numerical_absolute_goal_met"), goal_met, "per-mode budget decision")
    same(cert.get("status"), "CERTIFIED_BAND_NUMERICAL_GOAL_MET" if goal_met
         else "VALID_BAND_ENCLOSURE_GOAL_NOT_MET", "per-mode status")
    return cert, {"status": "PASS_EXACT_NEW_PANEL_CHAIN", "j": j, "panels": PANELS,
                  "boundary_carries": 2 * PANELS, "certificate_sha256": sha(directory / "CERTIFICATE.json"),
                  "panel_file_sha256": panel_pins, "special_function_calls": 0,
                  "numerical_integrations": 0}


def _worker(job):
    j, output, repo, limit = job
    for key in THREAD_KEYS:
        os.environ[key] = "1"
    output, repo = Path(output), Path(repo)
    kernel = numerical_modules(repo)
    request = kernel.BandRequest(**fixed_request(j)).validate()
    binding = kernel.request_binding(repo / SOURCE, request)
    directory = output / "bands" / f"j{j:02d}"
    if directory.is_symlink():
        raise ValueError("job output must not be a symlink")
    start = time.monotonic()
    with lock(output / "locks" / f"j{j:02d}.lock"):
        complete = False
        if (directory / "CERTIFICATE.json").exists():
            prior = json.loads((directory / "CERTIFICATE.json").read_text())
            complete = prior.get("scientific_execution") == "COMPLETE"
        if complete:
            cert, check = verify_new_certificate(directory, binding)
            return {"j": j, "status": "REUSED_COMPLETE_VERIFIED", "new_panels": 0,
                    "reused_panels": PANELS, "certificate_sha256": check["certificate_sha256"],
                    "certificate": str(directory / "CERTIFICATE.json"),
                    "elapsed_seconds": time.monotonic() - start, "verification": check,
                    "resource": dict(_WORKER_RESOURCE)}
        # Existing partial output is checked by the original bound resume code.
        result = kernel.run_band_profiles(repo / SOURCE, directory, request,
                                          resume=(directory / "REQUEST.json").exists(),
                                          max_new_panels=limit)
        record = {"j": j, "status": result["status"],
                  "new_panels": result["panels_computed_this_call"],
                  "reused_panels": result["panels_reused_this_call"],
                  "certificate": str(directory / "CERTIFICATE.json"),
                  "certificate_sha256": sha(directory / "CERTIFICATE.json"),
                  "elapsed_seconds": time.monotonic() - start,
                  "resource": dict(_WORKER_RESOURCE)}
        if result["scientific_execution"] == "COMPLETE":
            _, record["verification"] = verify_new_certificate(directory, binding)
        return record


def combine_boxes(boxes, beta2, display_digits=30):
    """Exact deterministic addition with one radial tail and charged display error."""
    integer(display_digits, 1, 100)
    beta2 = exact(beta2)
    if beta2 < 0 or not boxes:
        raise ValueError("nonempty boxes and nonnegative radial error required")
    midpoint = tuple(sum((value[c][0] for value in boxes), F(0)) for c in range(2))
    if any(r < 0 for value in boxes for _, r in value):
        raise ValueError("negative component radius")
    numerical = sum((r for value in boxes for _, r in value), F(0))
    with localcontext() as context:
        context.prec, context.rounding = display_digits, ROUND_HALF_EVEN
        display = tuple(str(Decimal(v.numerator) / Decimal(v.denominator)) for v in midpoint)
    rounding = sum((abs(v - F(s)) for v, s in zip(midpoint, display)), F(0))
    error = numerical + beta2 + rounding
    return {"midpoint_exact": dict(zip(("real", "imag"), map(rational, midpoint))),
            "display_midpoint": dict(zip(("real", "imag"), display)),
            "numerical_error_l1": rational(numerical), "one_L64_radial_beta2": rational(beta2),
            "display_rounding_error_l1": rational(rounding),
            "absolute_error_about_display_midpoint": rational(error),
            "absolute_error_upper_decimal": upward(error),
            "fixed_goal": "1e-62", "goal_met": error <= D2_GOAL}


def assemble(repo, certificates):
    old, band, q, pins = inherited(repo)
    if set(certificates) != set(MODES):
        raise ValueError("all and only j37..64 certificates required")
    boxes = [box(old["D2_B_cutoff"]), box(band["D2_B_cutoff"])]
    new_pins = {}
    for j in MODES:
        cert, pin = certificates[j]
        same(cert["request"], fixed_request(j), "assembly one-j request")
        same(cert["scientific_execution"], "COMPLETE", "assembly completion")
        same(cert["full_intermediate_sum"], [j], "assembly mode coverage")
        boxes.append(box(cert["D2_B_cutoff"]))
        for key, value in cert["D1_q_B_cutoff"].items():
            if key in q:
                raise ValueError("overlapping inherited/new D1 pair")
            q[key] = value
        new_pins[str(j)] = pin
    expected_pairs = {",".join(map(str, sorted((a, j)))) for a in (20, 21) for j in range(65)}
    same(sorted(q), sorted(expected_pairs), "all129D1pair coverage")
    sys.path.insert(0, str(Path(repo) / "src"))
    from wu088_hh.phys66_radial_budget import certificate
    radial = certificate(Path(repo) / SOURCE, 64, "65", 2)
    beta1, beta2 = (row["radial_cutoff_bound"] for row in radial["terms"])
    d2 = combine_boxes(boxes, beta2)
    d1_errors = {key: sum(r for _, r in box(value)) + beta1 for key, value in q.items()}
    maximum = max(d1_errors.values())
    d1_met = maximum <= D1_GOAL
    return {"schema": "PHYS73_VALIDATED_L64_CERTIFICATE_V1",
            "status": "CERTIFIED_GOALS_MET" if d1_met and d2["goal_met"] else "VALID_ENCLOSURE_GOAL_NOT_MET",
            "scope": "finiteL64 m0 external21,20 D2 and129D1boundarypairs; allr>=27",
            "physics": {"B": "27", "k": "7/10", "E": "49/200", "eta_C": "-10/7",
                        "eta": "F*y", "xi": "F*y-phi", "V": "2*(1+1/d)*exp(-2*d)",
                        "d": "abs(r*n-(7/10)*zhat)", "Z": "+uprime*uinverse"},
            "source_sha256": SOURCE_SHA, "inherited_pins": pins, "new_certificate_sha256": new_pins,
            "finite_intermediate_modes": list(range(65)), "new_modes": list(MODES),
            "radial_cutoff": "65", "D2": d2,
            "D1_B_cutoff": q,
            "D1_B_full_radial_absolute_error_about_exact_midpoint": {k: rational(v) for k, v in sorted(d1_errors.items())},
            "D1_max_error": rational(maximum), "D1_max_error_upper_decimal": upward(maximum),
            "D1_one_radial_beta1_per_pair": rational(beta1), "D1_goal": "1e-45", "D1_goal_met": d1_met,
            "D1_display_claim": "Exact dyadic midpoint authority; no new rounded D1 decimal claim",
            "inherited_payloads_reintegrated": 0, "assembly_integrations": 0,
            "excluded_angular_error_included": False, "original_source_xi_certified": False,
            "PHYS69_all_angular_D2": "COMPLETE_REUSED", "PHYS71_D3": "COMPLETE_REUSED",
            "PHYS72_lambda1_remainder": "COMPLETE_REUSED", "HH_R10": "OFF"}


def run(output, workers=28, modes=MODES, max_new_panels=None, repo=ROOT, worker_memory_gib=2):
    spec = plan(repo, modes, workers)
    if type(worker_memory_gib) is not int:
        raise ValueError("integer worker memory GiB required")
    integer(worker_memory_gib, 1, 16)
    if max_new_panels is not None:
        if type(max_new_panels) is not int:
            raise ValueError("exact integer panel limit required")
        integer(max_new_panels, 0, PANELS)
    output = Path(output).expanduser()
    if output.is_symlink() or output.exists() and not output.is_dir():
        raise ValueError("output must be an ordinary directory")
    output = output.resolve()
    kernel = numerical_modules(repo)
    binding = {"schema": "PHYS73_VALIDATED_L64_BINDING_V1", "source_sha256": SOURCE_SHA,
               "inherited_pins": spec["input_pins"], "requests": [fixed_request(j) for j in MODES],
               "engine": kernel.engine_identity(), "driver_sha256": sha(__file__), "HH_R10": "OFF"}
    fingerprint = digest(binding)
    output.mkdir(parents=True, exist_ok=True)
    with lock(output / "CAMPAIGN.lock"):
        marker = output / "REQUEST.json"
        expected = {"binding": binding, "fingerprint": fingerprint}
        if marker.exists():
            same(json.loads(marker.read_text()), expected, "campaign source/request/engine/runtime")
        else:
            # A killed pre-publication write can leave only its temporary.
            # Ignore that uncommitted ordinary file; never parse or promote it.
            if any(p.name != "CAMPAIGN.lock" and not (
                    re.fullmatch(r"\.REQUEST\.json\.[0-9a-f]{32}\.tmp", p.name)
                    and p.is_file() and not p.is_symlink()) for p in output.iterdir()):
                raise ValueError("nonempty output has no bound campaign request")
            write_new(marker, expected)
        started = datetime.now(timezone.utc).isoformat()
        begin = time.monotonic()
        for key in THREAD_KEYS:
            os.environ[key] = "1"
        jobs = [(j, str(output), str(Path(repo).resolve()), max_new_panels) for j in spec["new_modes"]]
        records, failures = [], []
        with ProcessPoolExecutor(max_workers=spec["workers"], mp_context=multiprocessing.get_context("spawn"),
                                 initializer=initialize_worker, initargs=(worker_memory_gib,)) as pool:
            futures = {pool.submit(_worker, job): job[0] for job in jobs}
            for future in as_completed(futures):
                j = futures[future]
                try:
                    record = future.result()
                    records.append(record)
                except Exception as exc:
                    failures.append({"j": j, "error_type": type(exc).__name__, "error": str(exc)})
                    record = {"j": j, "status": "FAILED", "error": str(exc)}
                print(json.dumps({"event": "new_mode_complete", **{k: v for k, v in record.items() if k != "verification"}}, sort_keys=True), flush=True)
        all_certs = {}
        for j in MODES:
            path = output / "bands" / f"j{j:02d}" / "CERTIFICATE.json"
            if not path.exists() or json.loads(path.read_text()).get("scientific_execution") != "COMPLETE":
                continue
            request = kernel.BandRequest(**fixed_request(j)).validate()
            bound = kernel.request_binding(Path(repo) / SOURCE, request)
            cert, check = verify_new_certificate(path.parent, bound)
            all_certs[j] = cert, check["certificate_sha256"]
        final = None
        if len(all_certs) == len(MODES) and not failures:
            final = assemble(repo, all_certs)
            final_path = output / "CERTIFICATE.json"
            if final_path.exists():
                same(json.loads(final_path.read_text()), final, "immutable aggregate certificate")
            else:
                write_new(final_path, final)
        status = "FAILED_NO_FINAL_CERTIFICATE" if failures else final["status"] if final else "PARTIAL_CHECKPOINT_NO_FINAL_CERTIFICATE"
        record = {"schema": "PHYS73_VALIDATED_L64_EXECUTION_V1", "status": status,
                  "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
                  "elapsed_seconds": time.monotonic() - begin, "fingerprint": fingerprint,
                  "workers": spec["workers"], "modes_requested": spec["new_modes"],
                  "worker_memory_gib": worker_memory_gib,
                  "aggregate_worker_address_space_ceiling_gib": spec["workers"] * worker_memory_gib,
                  "mode_results": sorted(records, key=lambda x: x["j"]), "failures": failures,
                  "new_panels": sum(r["new_panels"] for r in records),
                  "reused_new_mode_panels": sum(r["reused_panels"] for r in records),
                  "inherited_panel_reintegrations": 0, "complete_new_modes": sorted(all_certs),
                  "NCP_identity": "caller host identity recorded by outer launcher; not inferred here",
                  "HH_R10": "OFF"}
        token = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "_" + uuid.uuid4().hex[:8]
        write_new(output / "invocations" / (token + ".json"), record)
        return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=28)
    parser.add_argument("--worker-memory-gib", type=int, default=2, help="Linux address-space ceiling per worker,1..16GiB")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--modes", type=int, nargs="+", default=list(MODES),
                        help="new-mode subset for bounded checkpoints; final result requires37..64")
    parser.add_argument("--max-new-panels", type=int, help="per-mode new-panel limit,0..152")
    args = parser.parse_args(argv)
    integer(args.worker_memory_gib, 1, 16)
    if not args.run:
        print(json.dumps(plan(ROOT, args.modes, args.workers), indent=2, sort_keys=True))
        return 0
    record = run(args.out, args.workers, args.modes, args.max_new_panels,
                 worker_memory_gib=args.worker_memory_gib)
    print(json.dumps({k: v for k, v in record.items() if k != "mode_results"}, indent=2, sort_keys=True))
    if record["failures"]:
        return 1
    return 2 if record["status"] == "VALID_ENCLOSURE_GOAL_NOT_MET" else 0


if __name__ == "__main__":
    raise SystemExit(main())
