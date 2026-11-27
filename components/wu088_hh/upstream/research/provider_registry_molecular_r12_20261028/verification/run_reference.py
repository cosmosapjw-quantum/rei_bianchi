#!/usr/bin/env python3
"""One-shot R12 independent primitive/Decimal reference.

No production or predecessor module is imported. Exact comparisons use Fraction.
Decimal160 closed forms corroborate exponential arithmetic with the pre-fixed
guard; they are not interval-reference computations or physical-error lowers.
This file is authored before freeze and is executed only by the root wrapper.
"""
from bisect import bisect_left, bisect_right
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import sys
import time
import traceback

BASE = Path(__file__).resolve().parents[1]
REPO = BASE.parents[1]
OUT = BASE / "raw/REFERENCE_RESULTS.json"
CONFIG = BASE / "verification/REFERENCE_INPUT.json"
FREEZE = BASE / "raw/PREEXECUTION_FREEZE.json"
GUARD = Decimal("1e-80")
PRECISION = 160


def utc():
    return datetime.now(timezone.utc).isoformat()


def rational(x):
    if isinstance(x, bool) or isinstance(x, float):
        raise TypeError("Exact input must not be boolean or binary float")
    if isinstance(x, Fraction):
        return x
    if isinstance(x, (str, int)):
        return Fraction(x)
    raise TypeError("Unsupported exact scalar: " + type(x).__name__)


def decimal(x):
    if isinstance(x, Decimal):
        return x
    x = rational(x)
    return Decimal(x.numerator) / Decimal(x.denominator)


def digest(raw):
    return sha256(raw).hexdigest()


def read_json(path):
    raw = Path(path).read_bytes()
    return json.loads(raw), {"bytes": len(raw), "sha256": digest(raw)}


def rational_rows(rows):
    return [[rational(x) for x in row] for row in rows]


class Audit:
    """Counts actual component outcomes; a group is not a fabricated assertion."""
    def __init__(self):
        self.checks = []
        self.components = Counter()
        self.failed_components = Counter()

    def group(self, label, kind, outcomes):
        count = 0
        failed = 0
        first = []
        for ok, detail in outcomes:
            count += 1
            if not ok:
                failed += 1
                if len(first) < 6:
                    first.append(detail)
        self.components[kind] += count
        self.failed_components[kind] += failed
        item = {"id": label, "kind": kind, "components": count,
                "failed_components": failed, "status": "PASS" if failed == 0 else "FAIL"}
        if first:
            item["first_failures"] = first
        self.checks.append(item)
        return failed == 0

    def one(self, label, kind, ok, detail=None):
        return self.group(label, kind, [(bool(ok), detail)])

    @property
    def failures(self):
        return sum(self.failed_components.values())


def exact_enclosed(value, lower, upper, label):
    lo, hi = rational(lower), rational(upper)
    return (lo <= value <= hi,
            {"component": label, "reference": str(value),
             "lower": str(lo), "upper": str(hi)})


def decimal_enclosed(value, lower, upper, label):
    lo = None if lower is None else decimal(lower)
    hi = decimal(upper)
    scale = max(Decimal(1), abs(value), abs(hi),
                Decimal(0) if lo is None else abs(lo))
    eps = GUARD * scale
    ok = value <= hi + eps and (lo is None or lo - eps <= value)
    return (ok, {"component": label, "reference": str(value),
                 "lower": None if lo is None else str(lo),
                 "upper": str(hi), "guard": str(eps)})


def qpower(q, exponent):
    if exponent < 0:
        raise ValueError("Kernel has no negative age exponent")
    return q ** exponent


@lru_cache(maxsize=None)
def primitive(q, tau, shifted_time):
    """Independent finite geometric primitive; no overlap implementation."""
    x = max(Fraction(0), shifted_time)
    n = x // tau
    finite_sum = sum((qpower(q, k) for k in range(n)), Fraction(0))
    return tau * finite_sum + qpower(q, n) * (x - n * tau)


def force_at(t, q, tau, source_knots, gr):
    return sum((g * (primitive(q, tau, t - a)
                     - primitive(q, tau, t - b))
                for a, b, g in zip(source_knots, source_knots[1:], gr)),
               Fraction(0))


def independent_grid(source_knots, observations, tau, old_knots):
    """All source-shift events, constructed independently from interval overlap."""
    t0, horizon = observations[0], observations[-1]
    knots = set(source_knots) | set(observations) | set(old_knots)
    origins = set(source_knots) | {t0}
    for a in origins:
        k = 0
        while a + k * tau <= horizon:
            shifted = a + k * tau
            if shifted >= t0:
                knots.add(shifted)
            k += 1
    return sorted(x for x in knots if t0 <= x <= horizon)


def cell_containing(left, right, knots):
    """Use an interior point, then prove both closed endpoints are included."""
    midpoint = (left + right) / 2
    j = bisect_right(knots, midpoint) - 1
    if not (0 <= j < len(knots) - 1
            and knots[j] <= left < right <= knots[j + 1]):
        raise ValueError("No single closed source/cap cell contains refined interval")
    return j


def exact_point_index(t, knots):
    i = bisect_left(knots, t)
    return i if i < len(knots) and knots[i] == t else None


def geometry(spec, old_knots=()):
    q, tau = spec["q"], spec["tau"]
    source, observations = spec["source_knots"], spec["observations"]
    t0, horizon = observations[0], observations[-1]
    if not (0 <= q <= 1 and tau > 0 and t0 == source[0] and horizon == source[-1]):
        raise ValueError("Independent geometry premise failure")
    if any(a >= b for a, b in zip(source, source[1:])):
        raise ValueError("Nonincreasing source partition")
    if any(a >= b for a, b in zip(observations, observations[1:])):
        raise ValueError("Nonincreasing observation partition")
    if len(spec["gr"]) != len(source) - 1 or len(spec["ge"]) != len(source) - 1:
        raise ValueError("Source coefficient shape mismatch")
    if any(v < 0 for v in spec["gr"] + spec["ge"] + spec["initial"]):
        raise ValueError("Negative declared forcing/initial bound")
    times = independent_grid(source, observations, tau, old_knots)
    forces = [force_at(t, q, tau, source, spec["gr"]) for t in times]
    kernels = [qpower(q, (t - t0) // tau) for t in times]
    points = [h * spec["initial"][0] + f for h, f in zip(kernels, forces)]
    affines, rwholes, source_indices, cap_indices = [], [], [], []
    for i, (a, b) in enumerate(zip(times, times[1:])):
        h = qpower(q, (a - t0) // tau)
        left = h * spec["initial"][0] + forces[i]
        right_left_limit = h * spec["initial"][0] + forces[i + 1]
        affines.append((left, right_left_limit))
        rwholes.append(max(left, right_left_limit, points[i + 1]))
        source_indices.append(cell_containing(a, b, source))
        if old_knots:
            cap_indices.append(cell_containing(a, b, old_knots))
    point_map = [exact_point_index(t, times) for t in observations]
    if any(i is None for i in point_map):
        raise ValueError("Observation point missing from independent refinement")
    ranges = [(point_map[i], point_map[i + 1]) for i in range(len(point_map) - 1)]
    return {"times": times, "forces": forces, "kernels": kernels, "points": points,
            "affines": affines, "rwholes": rwholes,
            "source_indices": source_indices, "cap_indices": cap_indices,
            "point_map": point_map, "ranges": ranges}


@lru_cache(maxsize=None)
def closed_moments(d, width):
    """Decimal160 exp/closed phi forms, not the production Taylor series."""
    dd, dt = decimal(d), decimal(width)
    x = dd * dt
    ex = x.exp()
    if d == 0:
        return ex, dt, dt * dt / 2
    return ex, (ex - 1) / dd, (ex - 1 - x) / (dd * dd)


def affine_step(initial_e, c, d, ge, width, left_r, right_r):
    ex, phi1, phi2 = closed_moments(d, width)
    slope = (right_r - left_r) / width
    return (ex * initial_e + decimal(c * left_r + ge) * phi1
            + decimal(c * slope) * phi2)


def constant_step(initial_e, c, d, ge, width, radius):
    ex, phi1, unused_phi2 = closed_moments(d, width)
    return ex * initial_e + decimal(c * radius + ge) * phi1


def raw_reference(spec, geom):
    es = [decimal(spec["initial"][1])]
    whole_es = []
    for i, (a, b) in enumerate(zip(geom["times"], geom["times"][1:])):
        ge = spec["ge"][geom["source_indices"][i]]
        left, right = geom["affines"][i]
        endpoint = affine_step(es[-1], spec["c"], spec["d"], ge, b - a, left, right)
        envelope = constant_step(es[-1], spec["c"], spec["d"], ge, b - a,
                                 geom["rwholes"][i])
        whole_es.append(max(es[-1], envelope))
        es.append(endpoint)
    return {"E": es, "Ewhole": whole_es}


def source_spec(saved, variant):
    """Derive saved fixtures independently from pinned output, with exact compression."""
    raw = saved["raw"]
    delta = rational(raw["delta"])
    count = raw["cells"]
    horizon = count * delta
    full_gr = [rational(x) for x in raw["coefficients"]["g_r"]]
    full_ge = [rational(x) for x in raw["coefficients"]["g_e"]]
    if len(full_gr) != count or len(full_ge) != count:
        raise ValueError("Saved forcing length does not equal saved source cells")
    if len(set(full_gr)) != 1 or len(set(full_ge)) != 1:
        raise ValueError("Saved forcing is not exactly constant; compression invalid")
    if variant == "aligned":
        observations = [n * delta for n in range(count + 1)]
    elif variant == "nonaligned":
        observations = [Fraction(0)] + [
            (Fraction(n) + (Fraction(1, 3) if n % 2 else -Fraction(1, 5))) * delta
            for n in range(1, count)] + [horizon]
    else:
        raise ValueError("Unrecognized fixed observation grid variant")
    return {"q": rational(raw["q"]), "tau": rational(raw["tau"]),
            "c": rational(raw["coefficients"]["c"]),
            "d": rational(raw["coefficients"]["d"]),
            "gr": [full_gr[0]], "ge": [full_ge[0]],
            "initial": [rational(x) for x in raw["initial"]],
            "source_knots": [Fraction(0), horizon], "observations": observations,
            "binding": raw["binding"], "saved_id": saved["id"],
            "saved_delta": delta, "saved_cells": count}


def caps_from_saved(saved):
    old = saved["capped"]
    delta = rational(old["delta"])
    return {"knots": [i * delta for i in range(old["cells"] + 1)],
            "points": rational_rows(old["endpoints_upper"]),
            "wholes": rational_rows(old["whole_cells_upper"])}


def verify_freeze(audit, config):
    freeze, identity = read_json(FREEZE)
    audit.one("freeze.status", "metadata", freeze.get("status") == "PASS", freeze.get("status"))
    entries = freeze.get("files", [])
    paths = [entry["path"] for entry in entries]
    audit.one("freeze.unique_paths", "metadata", len(set(paths)) == len(paths))
    audit.group("freeze.required_files", "metadata",
                ((path in paths, {"missing": path})
                 for path in config["required_frozen_sources"]))
    outcomes = []
    for entry in entries:
        path = (REPO / entry["path"]).resolve()
        if not path.is_relative_to(REPO.resolve()):
            raise ValueError("Freeze path escapes repository")
        raw = path.read_bytes()
        outcomes.append((len(raw) == entry["bytes"],
                         {"path": entry["path"], "field": "bytes",
                          "observed": len(raw), "expected": entry["bytes"]}))
        outcomes.append((digest(raw) == entry["sha256"],
                         {"path": entry["path"], "field": "sha256",
                          "observed": digest(raw), "expected": entry["sha256"]}))
    audit.group("freeze.all_bytes", "metadata", outcomes)
    if audit.failures:
        raise ValueError("Frozen source identity check failed")
    return freeze, identity

def control_spec(control):
    source = [rational(x) for x in control["source_knots"]]
    cells = len(source) - 1

    def expanded(key):
        value = control[key]
        return ([rational(x) for x in value] if isinstance(value, list)
                else [rational(value)] * cells)

    return {"q": rational(control["q"]), "tau": rational(control["tau"]),
            "c": rational(control["c"]), "d": rational(control["d"]),
            "gr": expanded("g_r"), "ge": expanded("g_e"),
            "source_knots": source,
            "observations": [rational(x) for x in control["observation_knots"]],
            "initial": [rational(x) for x in control["initial"]],
            "state_count": control["state_count"], "control_id": control["id"]}


def old_membership(t, caps):
    point = exact_point_index(t, caps["knots"])
    cells = [j for j, (a, b) in enumerate(zip(caps["knots"], caps["knots"][1:]))
             if a <= t <= b]
    if not cells:
        raise ValueError("Point is outside old closed-cell domain")
    return point, cells


def point_cap_values(t, caps, component):
    point, cells = old_membership(t, caps)
    values = [caps["wholes"][j][component] for j in cells]
    if point is not None:
        values.append(caps["points"][point][component])
    return values


def clipped_reference(spec, geom, raw, caps):
    """Monotone ideal lower targets for outward upper-bound construction.

    Each clamp is intersection with an independently identified valid bound.
    Fractions are used for R. Decimal closed solutions are used for scalar E.
    The outputs are method-bound targets, never physical-error lower bounds.
    """
    n = len(geom["times"]) - 1
    rpoints = [spec["initial"][0]]
    epoints = [decimal(spec["initial"][1])]
    rwhole, ewhole, left_e_used, scalar_right = [], [], [], []
    for i in range(n):
        a, b = geom["times"][i:i + 2]
        old_j = geom["cap_indices"][i]
        radius = min(geom["rwholes"][i], caps["wholes"][old_j][0])
        old_e = decimal(caps["wholes"][old_j][1])
        erestrictions = [epoints[i], raw["E"][i], old_e]
        erestrictions.extend(decimal(x) for x in point_cap_values(a, caps, 1))
        incoming_e = min(erestrictions)
        rrestrictions = [rpoints[i], geom["points"][i], radius]
        rrestrictions.extend(point_cap_values(a, caps, 0))
        rpoints[i], epoints[i] = min(rrestrictions), incoming_e
        ge = spec["ge"][geom["source_indices"][i]]
        outgoing = constant_step(incoming_e, spec["c"], spec["d"], ge, b - a, radius)
        whole_e = min(raw["Ewhole"][i], max(incoming_e, outgoing), old_e)
        next_r = [geom["points"][i + 1], radius] + point_cap_values(b, caps, 0)
        next_e = [raw["E"][i + 1], outgoing, whole_e]
        next_e.extend(decimal(x) for x in point_cap_values(b, caps, 1))
        rpoints.append(min(next_r))
        epoints.append(min(next_e))
        rwhole.append(radius)
        ewhole.append(whole_e)
        left_e_used.append(incoming_e)
        scalar_right.append(outgoing)
    for i in range(n + 1):
        touching = [j for j in (i - 1, i) if 0 <= j < n]
        rpoints[i] = min([rpoints[i]] + [rwhole[j] for j in touching])
        epoints[i] = min([epoints[i]] + [ewhole[j] for j in touching])
    return {"R": rpoints, "E": epoints, "Rwhole": rwhole, "Ewhole": ewhole,
            "left_E": left_e_used, "scalar_right": scalar_right}


def check_aggregation(audit, label, layer, spec, geom):
    requested = layer["endpoints_upper"]
    refined = layer["refined_endpoints_upper"]
    wholes = layer["whole_cells_upper"]
    subwholes = layer["refined_whole_cells_upper"]
    rows = []
    for i, j in enumerate(geom["point_map"]):
        for k in (0, 1):
            rows.append((rational(requested[i][k]) == rational(refined[j][k]),
                         {"point": i, "component": k, "selected_refined": j}))
    if layer["endpoints_lower"] is not None:
        for i, j in enumerate(geom["point_map"]):
            for k in (0, 1):
                rows.append((rational(layer["endpoints_lower"][i][k])
                             == rational(layer["refined_endpoints_lower"][j][k]),
                             {"lower_point": i, "component": k}))
    for i, (lo, hi) in enumerate(geom["ranges"]):
        rows.append((lo < hi and geom["times"][lo] == spec["observations"][i]
                     and geom["times"][hi] == spec["observations"][i + 1],
                     {"closed_requested_cell": i, "range": [lo, hi]}))
        rows.append((sum((geom["times"][j + 1] - geom["times"][j]
                          for j in range(lo, hi)), Fraction(0))
                     == spec["observations"][i + 1] - spec["observations"][i],
                     {"gap_free_cell": i}))
        for k in (0, 1):
            expected = max(rational(subwholes[j][k]) for j in range(lo, hi))
            rows.append((rational(wholes[i][k]) == expected,
                         {"aggregate_cell": i, "component": k, "expected": str(expected)}))
    for i, whole in enumerate(subwholes):
        for k in (0, 1):
            rows.append((rational(whole[k]) >= max(rational(refined[i][k]),
                                                    rational(refined[i + 1][k])),
                         {"closed_endpoint_inclusion": i, "component": k}))
    audit.group(label + ".requested_and_closed_aggregation", "coverage", rows)


def check_weights(audit, label, sweep, spec, geom):
    widths = sorted(set(b - a for a, b in zip(geom["times"], geom["times"][1:])))
    observed = {rational(k): v for k, v in sweep["Bernstein_weights_by_length"].items()}
    audit.one(label + ".moment_width_keys", "coverage", set(widths) == set(observed))
    rows, zero_rows = [], []
    for width in widths:
        ex, p1, p2 = closed_moments(spec["d"], width)
        values = {"exp": ex, "phi": p1, "W0": p1 - p2 / decimal(width),
                  "W1": p2 / decimal(width)}
        for name, value in values.items():
            lo, hi = observed[width][name]
            rows.append(decimal_enclosed(value, lo, hi, str(width) + ":" + name))
        if spec["d"] == 0:
            for name, value in {"exp": Fraction(1), "phi": width,
                                "W0": width / 2, "W1": width / 2}.items():
                lo, hi = observed[width][name]
                zero_rows.append(exact_enclosed(value, lo, hi, str(width) + ":" + name))
    audit.group(label + ".closed_form_moments", "decimal", rows)
    if zero_rows:
        audit.group(label + ".zero_d_moments", "exact", zero_rows)


def check_caps(audit, label, sweep, spec, geom, raw_ref, caps, source_identity):
    layer, meta = sweep["capped"], sweep["caps"]
    ideal = clipped_reference(spec, geom, raw_ref, caps)
    metadata = [
        (meta["source_sha256"] == source_identity["sha256"], "source SHA"),
        (meta["case_id"] == spec["saved_id"], "case ID"),
        (meta["case_index"] == spec["saved_index"], "case index"),
        (meta["point_source_pointer"] == f"/hd_cases/{spec['saved_index']}/capped/endpoints_upper",
         "actual point source pointer"),
        (meta["whole_source_pointer"] == f"/hd_cases/{spec['saved_index']}/capped/whole_cells_upper",
         "actual whole source pointer"),
        ([rational(x) for x in meta["old_knots"]] == caps["knots"], "old exact clock"),
        (rational_rows(meta["old_points_upper"]) == caps["points"], "old point arrays"),
        (rational_rows(meta["old_whole_cells_upper"]) == caps["wholes"], "old whole arrays"),
        (meta["subcell_to_old_cell"] == geom["cap_indices"], "subcell cap map"),
        (layer["endpoints_lower"] is None and layer["refined_endpoints_lower"] is None,
         "no physical-error lower after cap"),
        (layer["R_memory_reset"] is False, "global forcing memory retained")
    ]
    audit.group(label + ".cap_source_identity", "metadata", metadata)
    coverage, exact, decimals = [], [], []
    production_points = rational_rows(layer["refined_endpoints_upper"])
    production_wholes = rational_rows(layer["refined_whole_cells_upper"])
    for i, t in enumerate(geom["times"]):
        old_point, cells = old_membership(t, caps)
        coverage.append((meta["refined_point_to_old_point"][i] == old_point,
                         {"point": i, "expected_old_point": old_point}))
        coverage.append((meta["refined_point_containing_old_closed_cells"][i] == cells,
                         {"point": i, "expected_closed_cells": cells}))
        exact.append((production_points[i][0] >= ideal["R"][i],
                      {"capped_R_lower_target": i, "target": str(ideal["R"][i])}))
        decimals.append(decimal_enclosed(ideal["E"][i], None, layer["refined_endpoints_upper"][i][1],
                                         "capped_E_point:" + str(i)))
        for k in (0, 1):
            exact.append((production_points[i][k] <=
                          rational(sweep["raw"]["refined_endpoints_upper"][i][k]),
                          {"capped_no_worse_raw_point": i, "component": k}))
            for v in point_cap_values(t, caps, k):
                exact.append((production_points[i][k] <= v,
                              {"point_cap_no_worse": i, "component": k, "cap": str(v)}))
    for i, (a, b) in enumerate(zip(geom["times"], geom["times"][1:])):
        old_j = geom["cap_indices"][i]
        coverage.append((caps["knots"][old_j] <= a < b <= caps["knots"][old_j + 1],
                         {"closed_subcell": i, "old_cell": old_j}))
        exact.append((production_wholes[i][0] >= ideal["Rwhole"][i],
                      {"capped_whole_R_lower_target": i}))
        decimals.append(decimal_enclosed(ideal["Ewhole"][i], None, layer["refined_whole_cells_upper"][i][1],
                                         "capped_whole_E:" + str(i)))
        for k in (0, 1):
            exact.append((production_wholes[i][k] <= caps["wholes"][old_j][k],
                          {"whole_cap_no_worse": i, "component": k}))
            exact.append((production_wholes[i][k] <=
                          rational(sweep["raw"]["refined_whole_cells_upper"][i][k]),
                          {"capped_no_worse_raw_whole": i, "component": k}))
        prop = layer["propagation"][i]
        coverage.append((prop["old_cell_index"] == old_j, {"propagation_cell": i}))
        exact.append((rational(prop["R_whole_used"]) == production_wholes[i][0],
                      {"propagation_R_identity": i}))
        decimals.append(decimal_enclosed(ideal["left_E"][i], None, prop["left_E_used"],
                                         "capped_incoming_E:" + str(i)))
        decimals.append(decimal_enclosed(ideal["scalar_right"][i], None,
                                         prop["unclipped_scalar_right_upper"],
                                         "capped_scalar_lower_target:" + str(i)))
        record_scalar = constant_step(decimal(prop["left_E_used"]), spec["c"], spec["d"],
                                      spec["ge"][geom["source_indices"][i]], b - a,
                                      rational(prop["R_whole_used"]))
        decimals.append(decimal_enclosed(record_scalar, None, prop["unclipped_scalar_right_upper"],
                                         "record_scalar_closed_form:" + str(i)))
        exact.append((rational(prop["whole_E_upper"]) == production_wholes[i][1],
                      {"propagation_whole_E_identity": i}))
    for i, j in enumerate(geom["point_map"]):
        old_point, unused_cells = old_membership(geom["times"][j], caps)
        coverage.append((meta["requested_point_to_old_point"][i] == old_point,
                         {"requested_old_point": i}))
    for i, (lo, hi) in enumerate(geom["ranges"]):
        cover = set(geom["cap_indices"][lo:hi])
        for k in (0, 1):
            old_cover_bound = max(caps["wholes"][j][k] for j in cover)
            exact.append((rational(layer["whole_cells_upper"][i][k]) <= old_cover_bound,
                          {"requested_old_closed_cover_no_worse": i, "component": k}))
    audit.group(label + ".closed_cap_coverage", "coverage", coverage)
    audit.group(label + ".exact_cap_bounds", "exact", exact)
    audit.group(label + ".capped_Decimal_lower_targets", "decimal", decimals)
    check_aggregation(audit, label + ".capped", layer, spec, geom)
    return ideal


def check_saved_reduction(audit, label, spec, geom, raw_ref, saved):
    """Only a new compatibility check against old immutable output, never replay."""
    old = saved["raw"]
    old_times = [i * rational(old["delta"]) for i in range(old["cells"] + 1)]
    location = {t: i for i, t in enumerate(geom["times"])}
    exact, decimals, coverage = [], [], []
    for j, t in enumerate(old_times):
        coverage.append((t in location, {"saved_point": j, "time": str(t)}))
        if t not in location:
            continue
        i = location[t]
        exact.append(exact_enclosed(geom["forces"][i], old["forcing_lower"][j],
                                   old["forcing_upper"][j], "old_F:" + str(j)))
        exact.append(exact_enclosed(geom["points"][i], old["endpoints_lower"][j][0],
                                   old["endpoints_upper"][j][0], "old_R:" + str(j)))
        decimals.append(decimal_enclosed(raw_ref["E"][i], old["endpoints_lower"][j][1],
                                         old["endpoints_upper"][j][1], "old_E:" + str(j)))
    audit.group(label + ".saved_R11_clock_reduction", "coverage", coverage)
    audit.group(label + ".saved_R11_exact_compatibility", "exact", exact)
    audit.group(label + ".saved_R11_E_compatibility", "decimal", decimals)


def check_case(audit, label, sweep, spec, source_identity, saved=None):
    caps = None if saved is None else caps_from_saved(saved)
    geom = geometry(spec, () if caps is None else caps["knots"])
    raw_ref = raw_reference(spec, geom)
    n, m = len(geom["times"]), len(spec["observations"])
    parameters, source = sweep["parameters"], sweep["source"]
    meta = [(sweep.get("schema") == "WU_R12_NONALIGNED_CONVOLUTION_V1", "schema"),
            (sweep["h0"] == 1, "h0"),
            (sweep["R_memory_reset"] is False, "forcing memory"),
            (sweep["physical_consumer_admitted"] is False, "physical ceiling"),
            (sweep["old_science_replay"] == 0, "old replay"),
            (sweep["new_ODE_calls"] == 0, "ODE"),
            (sweep["rounding"]["bits"] == 128 and sweep["rounding"]["degree"] == 96,
             "fixed dyadic128/Taylor96")]
    for key in ("q", "tau", "c", "d"):
        meta.append((rational(parameters[key]) == spec[key], key))
    meta.extend([
        ([rational(x) for x in parameters["initial"]] == spec["initial"], "initial"),
        (rational(parameters["t0"]) == spec["observations"][0], "t0"),
        (rational(parameters["T"]) == spec["observations"][-1], "T"),
        ([rational(x) for x in source["knots"]] == spec["source_knots"], "source knots"),
        ([rational(x) for x in source["g_r"]] == spec["gr"], "whole-source gr"),
        ([rational(x) for x in source["g_e"]] == spec["ge"], "whole-source ge"),
        ([rational(x) for x in sweep["requested_times"]] == spec["observations"], "requested clock"),
        (0 <= spec["c"] and len(geom["times"]) - 1 <= 2048, "finite contract")
    ])
    cert = parameters["certificate"]
    meta.extend([(rational(cert["q"]) == spec["q"], "certificate q"),
                 (rational(cert["tau"]) == spec["tau"], "certificate tau"),
                 ([rational(x) for x in cert["validity_interval"]]
                  == [spec["observations"][0], spec["observations"][-1]], "certificate interval")])
    for flag in ("uniform_all_starts", "same_family_composition", "remainder_l1_nonexpansive",
                 "zero_mass_forcing", "whole_domain_forcing"):
        meta.append((cert[flag] is True, flag))
    if saved is not None:
        meta.extend([
            (parameters["binding"] == spec["binding"], "exact saved binding"),
            (cert["binding"] == spec["binding"], "certificate binding"),
            (cert["source_sha256"] == source_identity["sha256"], "chosen q source"),
            (cert["source_pointer"] == f"/hd_cases/{spec['saved_index']}/raw/generator",
             "actual chosen-q certificate pointer"),
            (cert["scientific_status"] == "CERTIFIED_FULL_A_BLOCK", "full-A status"),
            (rational(saved["raw"]["generator"]["q"]) == spec["q"], "stored chosen rational q"),
            (saved["raw"]["generator"]["uniform_all_starts"] is True, "saved all starts"),
            (saved["raw"]["generator"]["nominal_K_rho_directly_transferred"] is False,
             "no nominal-only rho transfer"),
            (sweep["saved_case"]["constant_source_compression_exact"] is True, "exact compression"),
            (sweep["saved_case"]["nominal_K_recomputed"] is False
             and sweep["saved_case"]["native_exponential_recomputed"] is False, "saved source reused")
        ])
    else:
        meta.extend([(len(parameters["binding"]["state_ids"]) == spec["state_count"], "control state count"),
                     (sweep["capped"] is None and sweep["caps"] is None, "uncapped arithmetic control")])
    audit.group(label + ".premise_and_source_metadata", "metadata", meta)
    raw = sweep["raw"]
    shapes = [
        (len(sweep["refined_times"]) == n, "refined clock"),
        (len(raw["refined_endpoints_upper"]) == n, "refined upper"),
        (len(raw["refined_endpoints_lower"]) == n, "refined lower"),
        (len(raw["refined_whole_cells_upper"]) == n - 1, "refined whole"),
        (len(raw["endpoints_upper"]) == m, "requested upper"),
        (len(raw["endpoints_lower"]) == m, "requested lower"),
        (len(raw["whole_cells_upper"]) == m - 1, "requested whole"),
        (len(raw["R_affine_cells"]) == n - 1, "affine cells")
    ]
    if not audit.group(label + ".array_shapes", "coverage", shapes):
        return None
    audit.group(label + ".independent_event_grid", "exact",
                ((rational(value) == expected, {"knot": i, "expected": str(expected), "actual": value})
                 for i, (value, expected) in enumerate(zip(sweep["refined_times"], geom["times"]))))
    refinement = sweep["refinement"]
    audit.group(label + ".source_and_observation_coverage", "coverage", [
        (refinement["source_cell_indices"] == geom["source_indices"], "independent source cell map"),
        (refinement["requested_point_indices"] == geom["point_map"], "independent requested point map"),
        ([tuple(x) for x in refinement["requested_subcell_ranges"]] == geom["ranges"],
         "independent requested closed-cell cover"),
        (refinement["includes_all_source_translated_jumps"] is True, "translated jumps recorded")
    ])
    exact, decimals = [], []
    for key, values in (("kernel_at_refined", geom["kernels"]),
                        ("F_at_refined", geom["forces"]), ("R_at_refined", geom["points"])):
        if len(sweep["exact"][key]) != n:
            raise ValueError("Exact output array length mismatch: " + key)
        for i, value in enumerate(values):
            exact.append((rational(sweep["exact"][key][i]) == value,
                          {"field": key, "knot": i, "reference": str(value)}))
    for i, radius in enumerate(geom["points"]):
        exact.append(exact_enclosed(radius, raw["refined_endpoints_lower"][i][0],
                                   raw["refined_endpoints_upper"][i][0], "raw_R:" + str(i)))
        decimals.append(decimal_enclosed(raw_ref["E"][i], raw["refined_endpoints_lower"][i][1],
                                         raw["refined_endpoints_upper"][i][1], "raw_E:" + str(i)))
    for i, (left, right) in enumerate(geom["affines"]):
        rec = sweep["exact"]["R_affine_cells"][i]
        for key, value in (("L", left), ("V", right), ("whole_R", geom["rwholes"][i])):
            exact.append((rational(rec[key]) == value, {"cell": i, "field": key}))
        affine = raw["R_affine_cells"][i]
        exact.append(exact_enclosed(left, *affine["left_interval"], "affine_L:" + str(i)))
        exact.append(exact_enclosed(right, *affine["right_left_limit_interval"], "affine_V_left_limit:" + str(i)))
        exact.append((rational(raw["refined_whole_cells_upper"][i][0]) >= geom["rwholes"][i],
                      {"closed_R_max": i, "reference": str(geom["rwholes"][i])}))
        decimals.append(decimal_enclosed(raw_ref["Ewhole"][i], None,
                                         raw["refined_whole_cells_upper"][i][1],
                                         "closed_E_scalar_envelope:" + str(i)))
    audit.group(label + ".exact_primitive_and_R", "exact", exact)
    audit.group(label + ".raw_E_closed_forms", "decimal", decimals)
    check_weights(audit, label, sweep, spec, geom)
    check_aggregation(audit, label + ".raw", raw, spec, geom)
    capped_ref = None
    if caps is not None:
        capped_ref = check_caps(audit, label, sweep, spec, geom, raw_ref, caps, source_identity)
        check_saved_reduction(audit, label, spec, geom, raw_ref, saved)
    points = []
    for j in geom["point_map"]:
        rec = {"t": str(geom["times"][j]), "F_exact": str(geom["forces"][j]),
               "R_exact": str(geom["points"][j]), "E_Decimal160": str(raw_ref["E"][j])}
        if capped_ref is not None:
            rec["capped_E_ideal_lower_target"] = str(capped_ref["E"][j])
        points.append(rec)
    summary = {"id": label, "source_cells": len(spec["source_knots"]) - 1,
               "requested_cells": m - 1, "refined_cells": n - 1,
               "source_shift_breakpoints_checked": True, "h0": 1,
               "raw_reference_meaning": "chosen rational-q ideal comparison, not physical-error lower",
               "Decimal_reference_status": "GUARDED_CORROBORATION_NOT_INTERVAL_REFERENCE",
               "reference_requested_points": points}
    return {"spec": spec, "geometry": geom, "raw": raw_ref, "capped": capped_ref, "summary": summary}


def check_pair(audit, label, first, second, shift=Fraction(0), require_refinement=False,
               compare_observation_lists=True):
    if first is None or second is None:
        audit.one(label + ".available", "coverage", False, "A case could not be checked")
        return
    a, b = first["spec"], second["spec"]
    structural = [(a[k] == b[k], {"invariant": k})
                  for k in ("q", "tau", "c", "d", "gr", "ge", "initial")]
    structural.append(([t + shift for t in a["source_knots"]] == b["source_knots"],
                       "source translation"))
    if require_refinement:
        structural.append((set(a["observations"]).issubset(set(b["observations"])),
                           "fine observation partition contains coarse points"))
    elif compare_observation_lists:
        structural.append(([t + shift for t in a["observations"]] == b["observations"],
                           "observation translation"))
    audit.group(label + ".definition", "coverage", structural)
    lookup = {t: i for i, t in enumerate(second["geometry"]["times"])}
    audit.group(label + ".common_knot_coverage", "coverage",
                ((t + shift in lookup, {"missing_common_time": str(t + shift)})
                 for t in first["geometry"]["times"]))
    exact, decimals = [], []
    for i, t in enumerate(first["geometry"]["times"]):
        if t + shift not in lookup:
            continue
        j = lookup[t + shift]
        for key in ("forces", "points", "kernels"):
            exact.append((first["geometry"][key][i] == second["geometry"][key][j],
                          {"time": str(t), "translated": str(t + shift), "field": key}))
        decimals.append(decimal_enclosed(first["raw"]["E"][i],
                                         second["raw"]["E"][j], second["raw"]["E"][j],
                                         "common_ideal_E:" + str(t)))
    audit.group(label + ".common_exact_values", "exact", exact)
    audit.group(label + ".common_E_semantics", "decimal", decimals)


def check_discriminating_limits(audit, controls):
    # The two analytic controls have independent polynomial closed solutions.
    first = controls["q1_polynomial_nonaligned"]
    spec, geom, sweep = first["spec"], first["geometry"], first["observed"]
    audit.one("limit.q1_polynomial_premises", "metadata",
              spec["q"] == 1 and spec["d"] == 0 and len(spec["gr"]) == 1)
    rows = []
    for i, t in enumerate(geom["times"]):
        age = t - spec["observations"][0]
        rr = spec["initial"][0] + spec["gr"][0] * age
        ee = (spec["initial"][1] + (spec["c"] * spec["initial"][0] + spec["ge"][0]) * age
              + spec["c"] * spec["gr"][0] * age * age / 2)
        rows.append((geom["points"][i] == rr, {"q1_R": i}))
        rows.append(exact_enclosed(ee, sweep["raw"]["refined_endpoints_lower"][i][1],
                                   sweep["raw"]["refined_endpoints_upper"][i][1],
                                   "q1_polynomial_E:" + str(i)))
    audit.group("limit.q1_polynomial", "exact", rows)
    late = controls["q0_late_source_nonaligned"]
    spec, geom, sweep = late["spec"], late["geometry"], late["observed"]
    onset = Fraction(3, 4)
    audit.one("limit.q0_fresh_source_premises", "metadata",
              spec["q"] == 0 and spec["tau"] == Fraction(1, 3)
              and spec["source_knots"] == [0, onset, 1]
              and spec["gr"] == [0, 1] and spec["ge"] == [0, 0]
              and spec["initial"] == [0, 0] and spec["c"] == 1 and spec["d"] == 0)
    rows = []
    for i, t in enumerate(geom["times"]):
        age = max(Fraction(0), t - onset)
        rows.append((geom["forces"][i] == age, {"fresh_q0_F": i}))
        rows.append(exact_enclosed(age * age / 2,
                                   sweep["raw"]["refined_endpoints_lower"][i][1],
                                   sweep["raw"]["refined_endpoints_upper"][i][1],
                                   "fresh_q0_E:" + str(i)))
    audit.group("limit.q0_fresh_source", "exact", rows)
    jump = controls["block_jump_left_limit"]
    spec, geom = jump["spec"], jump["geometry"]
    witnesses = []
    for i, (a, b) in enumerate(zip(geom["times"], geom["times"][1:])):
        age = b - spec["observations"][0]
        if age > 0 and age % spec["tau"] == 0:
            expected_drop = ((spec["q"] ** (age // spec["tau"] - 1))
                             - (spec["q"] ** (age // spec["tau"]))) * spec["initial"][0]
            actual_drop = geom["affines"][i][1] - geom["points"][i + 1]
            witnesses.append((actual_drop == expected_drop and actual_drop > 0,
                              {"time": str(b), "left_limit_minus_point": str(actual_drop)}))
    audit.one("limit.left_jump_witness_exists", "coverage", bool(witnesses))
    audit.group("limit.left_jump_identity", "exact", witnesses)
    translated = controls["translated_source_breakpoints"]
    spec, geom = translated["spec"], translated["geometry"]
    shifted = [a + k * spec["tau"] for a in spec["source_knots"][1:-1]
               for k in range(1, 9)
               if spec["observations"][0] < a + k * spec["tau"] < spec["observations"][-1]
               and a + k * spec["tau"] not in spec["observations"]]
    audit.one("limit.nonobservation_translated_source_witness", "coverage", bool(shifted))
    audit.group("limit.nonobservation_translated_source_coverage", "exact",
                ((t in geom["times"], {"translated_source_knot": str(t)}) for t in shifted))
    positive = controls["near_zero_d_positive"]
    negative = controls["near_zero_d_negative"]
    audit.group("limit.signed_near_zero_premises", "metadata", [
        (positive["spec"]["d"] == Fraction(1, 10 ** 30), "positive d"),
        (negative["spec"]["d"] == -Fraction(1, 10 ** 30), "negative d"),
        (positive["geometry"]["times"] == negative["geometry"]["times"], "same exact grid")
    ])
    audit.group("limit.signed_near_zero_order", "decimal",
                ((neg <= pos + GUARD * max(Decimal(1), abs(pos), abs(neg)),
                  {"point": i, "positive": str(pos), "negative": str(neg)})
                 for i, (pos, neg) in enumerate(zip(positive["raw"]["E"], negative["raw"]["E"]))))
    singleton = controls["singleton_zero_residual"]
    audit.one("limit.singleton_dimension", "metadata", singleton["spec"]["state_count"] == 1)
    audit.group("limit.singleton_zero_mass_R", "exact",
                ((x == 0, {"point": i, "radius": str(x)})
                 for i, x in enumerate(singleton["geometry"]["points"])))
    audit.one("limit.near_one_q_exact", "exact",
              controls["near_one_q"]["spec"]["q"] == Fraction(2 ** 128 - 1, 2 ** 128))
    audit.one("limit.positive_d_exercised", "exact",
              controls["positive_d_nonaligned"]["spec"]["d"] > 0)


def main():
    if OUT.exists():
        raise SystemExit("Refuse to overwrite the first R12 reference result")
    cpu0, wall0 = time.process_time(), time.monotonic()
    audit = Audit()
    report = {
        "schema": "WU_R12_REFERENCE_RESULTS_V1", "unit": "WU_NONALIGNED_CONVOLUTION_R12",
        "started_utc": utc(), "reference_arithmetic": "Fraction exact J primitive and Decimal160 closed forms",
        "Decimal_precision": PRECISION, "guard": "1e-80*max(1,abs(reference),abs(lower),abs(upper))",
        "guard_fixed_before_execution": True, "reference_is_interval_arithmetic": False,
        "source_and_production_imports": 0, "cases": [], "controls": [],
        "scope": {"new_ODE_calls": 0, "old_science_replay": 0, "new_native_or_generator_calls": 0,
                  "new_sample_campaign": 0, "physical_consumer_admitted": False,
                  "capped_reference_lower_target_is_physical_lower": False},
        "resource": {"runs": 1, "CPU_limit_s": 60, "wall_limit_s": 90},
        "runner_sha256": digest(Path(__file__).read_bytes())
    }

    def budget():
        if time.process_time() - cpu0 > 58 or time.monotonic() - wall0 > 88:
            raise RuntimeError("R12 reference bounded pre-finalization stop")

    def case_counts(start, before, checked):
        if checked is None:
            return None
        summary = checked["summary"]
        local = audit.checks[start:]
        summary["check_count"] = len(local)
        summary["failure_count"] = sum(row["status"] == "FAIL" for row in local)
        summary["component_comparisons"] = {
            key: audit.components[key] - before.get(key, 0) for key in audit.components}
        summary["status"] = "PASS" if summary["failure_count"] == 0 else "FAIL"
        return summary

    try:
        config, config_id = read_json(CONFIG)
        report["input_sha256"] = config_id["sha256"]
        report["skill_context_used"] = config["skill_context_used"]
        audit.group("fixed_reference_contract", "metadata", [
            (config["schema"] == "WU_R12_FIXED_REFERENCE_INPUT_V1", "schema"),
            (config["unit"] == report["unit"], "unit"),
            (config["precision_decimal_digits"] == PRECISION, "precision"),
            (config["relative_guard"] == "1e-80", "fixed guard"),
            (config["reference_is_interval_arithmetic"] is False, "Decimal qualification"),
            (config["resource"] == {"runs": 1, "CPU_s": 60, "wall_s": 90}, "bounded resource"),
            (config["old_sample_campaign"]["atol_preserved"] == "2e-12"
             and config["old_sample_campaign"]["rtol_preserved"] == "2e-10"
             and config["old_sample_campaign"]["new_runs"] == 0, "old samples unchanged")
        ])
        freeze, freeze_id = verify_freeze(audit, config)
        report["freeze_sha256"] = freeze_id["sha256"]
        frozen = {entry["path"]: entry for entry in freeze["files"]}
        primary_input, pi_id = read_json(REPO / config["primary_input_path"])
        primary, primary_id = read_json(REPO / config["primary_result_path"])
        report["primary_result_identity"] = primary_id
        report["primary_input_identity"] = pi_id
        report["primary_was_not_in_prefreeze"] = config["primary_result_path"] not in frozen
        source_def = config["sources"]["R11_primary"]
        old_source, old_id = read_json(REPO / source_def["path"])
        report["reused_R11_primary_identity"] = old_id
        audit.group("pinned_source_identity", "metadata", [
            (old_id["bytes"] == source_def["bytes"], "R11 bytes"),
            (old_id["sha256"] == source_def["sha256"], "R11 SHA"),
            (old_source["status"] == source_def["expected_status"], "R11 status"),
            (source_def["path"] in frozen
             and frozen[source_def["path"]]["sha256"] == source_def["sha256"], "R11 actual frozen dependency"),
            (old_source["unit"] == "WU_FULL_GENERATOR_BLOCK_R11", "R11 unit")
        ])
        header = [
            (primary["schema"] == "WU_R12_PRIMARY_RESULTS_V1", "primary schema"),
            (primary["unit"] == report["unit"], "primary unit"),
            (primary["status"] == "PASS" and primary["failure_count"] == 0, "primary reported PASS"),
            (primary["check_count"] == len(primary["checks"]), "primary actual check count"),
            (all(x["status"] == "PASS" for x in primary["checks"]), "all saved primary checks"),
            (primary["freeze_sha256"] == freeze_id["sha256"], "same freeze"),
            (config["primary_result_path"] not in frozen, "new primary result is post-freeze"),
            (primary["input_sha256"] == pi_id["sha256"], "actual primary input"),
            (primary["source_sha256"]["R11_primary"] == source_def["sha256"], "primary uses pinned R11"),
            (primary_input["hd_case_ids"] == config["expected_HD_ids"], "fixed saved case order"),
            (primary_input["saved_grid_variants"] == config["expected_grid_variants"], "fixed variants"),
            (primary_input["saved_cells"] == config["expected_saved_cells"], "saved192-cell source"),
            ([c["id"] for c in primary_input["controls"]] == config["required_controls"], "fixed controls")
        ]
        for output_key, input_key in (("core_sha256", "core_path"),
                                      ("arithmetic_sha256", "arithmetic_path"),
                                      ("runner_sha256", "primary_runner_path")):
            rel = config[input_key]
            header.append((rel in frozen and primary[output_key] == frozen[rel]["sha256"],
                           "primary frozen " + output_key))
        contract_path = BASE / "CONTRACT.json"
        header.append((primary["contract_sha256"] == digest(contract_path.read_bytes()),
                       "same actual contract"))
        for key, expected in (("old_science_replay", 0), ("predecessor_module_imports", 0),
                              ("new_ODE_runs", 0), ("native_exponential_runs", 0),
                              ("new_generator_calculations", 0), ("new_saved_sample_campaign", 0),
                              ("physical_consumer_admitted", False),
                              ("raw_universal_superiority_claim", False)):
            header.append((primary["scope"][key] == expected, "scope:" + key))
        audit.group("primary_source_metadata", "metadata", header)
        if audit.failures:
            raise ValueError("Identity/source preconditions failed before new reference mathematics")
        budget()
        saved_by_id = {x["id"]: x for x in old_source["hd_cases"]}
        observed_saved = {x["id"]: x for x in primary["hd_cases"]}
        audit.group("saved_case_set", "metadata", [
            (list(observed_saved) == config["expected_HD_ids"], "saved output IDs"),
            (len(observed_saved) == len(primary["hd_cases"]), "unique saved IDs")
        ])
        saved_references = {}
        control_references = {}
        with localcontext() as ctx:
            ctx.prec = PRECISION
            for case_id in config["expected_HD_ids"]:
                record = observed_saved[case_id]
                saved = saved_by_id[case_id]
                audit.one(case_id + ".source_scope_preserved", "metadata",
                          record["source_scope"] == saved["source_scope"])
                audit.one(case_id + ".variant_set", "metadata",
                          list(record["variants"]) == config["expected_grid_variants"])
                by_variant = {}
                for variant in config["expected_grid_variants"]:
                    budget()
                    spec = source_spec(saved, variant)
                    spec["saved_index"] = config["expected_HD_ids"].index(case_id)
                    start, before = len(audit.checks), dict(audit.components)
                    checked = check_case(audit, case_id + ":" + variant,
                                         record["variants"][variant], spec, old_id, saved)
                    summary = case_counts(start, before, checked)
                    if summary is not None:
                        report["cases"].append(summary)
                    by_variant[variant] = checked
                saved_references[case_id] = by_variant
                check_pair(audit, case_id + ":observation_grid_invariance",
                           by_variant["aligned"], by_variant["nonaligned"],
                           compare_observation_lists=False)
            observed_controls = {x["id"]: x for x in primary["controls"]}
            audit.group("control_set", "metadata", [
                (list(observed_controls) == config["required_controls"], "control IDs"),
                (len(observed_controls) == len(primary["controls"]), "unique control IDs")
            ])
            for control_index, supplied in enumerate(primary_input["controls"]):
                budget()
                cid = supplied["id"]
                item = observed_controls[cid]
                audit.one(cid + ".actual_input_identity", "metadata",
                          item["parameters"] == supplied)
                control_result = item["result"]
                binding = control_result["parameters"]["binding"]
                cert = control_result["parameters"]["certificate"]
                audit.group(cid + ".arithmetic_control_scope", "metadata", [
                    (cert["scientific_status"] == "ARITHMETIC_CONTROL_PREMISE", "arithmetic premise only"),
                    (cert["source_sha256"] == pi_id["sha256"], "actual fixed control source"),
                    (binding["source_sha256"] == pi_id["sha256"], "bound control source"),
                    (cert["binding"] == binding, "same binding"),
                    (cert["source_pointer"] == "/controls/" + str(control_index), "control pointer")
                ])
                spec = control_spec(supplied)
                start, before = len(audit.checks), dict(audit.components)
                checked = check_case(audit, "control:" + cid, control_result, spec, old_id)
                summary = case_counts(start, before, checked)
                if checked is not None:
                    checked["observed"] = control_result
                    report["controls"].append(summary)
                    control_references[cid] = checked
            for pair in config["paired_controls"]:
                first = control_references[pair["base"]]
                second = control_references[pair["variant"]]
                if pair["relation"] == "clock_translation":
                    check_pair(audit, "paired:absolute_clock_translation", first, second,
                               shift=rational(pair["shift"]))
                else:
                    check_pair(audit, "paired:observation_refinement", first, second,
                               require_refinement=True)
            check_discriminating_limits(audit, control_references)
            budget()
        report["reference_math_completed"] = True
    except Exception as exc:
        audit.one("reference_execution_exception", "metadata", False,
                  {"type": type(exc).__name__, "message": str(exc)})
        report["execution_error"] = {"type": type(exc).__name__, "message": str(exc),
                                     "traceback": traceback.format_exc(limit=8)}
        report["reference_math_completed"] = False
    report["checks"] = audit.checks
    report["check_count"] = len(audit.checks)
    report["failure_count"] = sum(x["status"] == "FAIL" for x in audit.checks)
    report["component_comparisons"] = sum(audit.components.values())
    report["component_comparisons_by_kind"] = dict(audit.components)
    report["failed_components"] = audit.failures
    report["failed_components_by_kind"] = dict(audit.failed_components)
    report["first_failure"] = next((x for x in audit.checks if x["status"] == "FAIL"), None)
    report["status"] = "PASS" if audit.failures == 0 else "FAIL"
    report["finished_utc"] = utc()
    report["internal_CPU_before_serialization_s"] = time.process_time() - cpu0
    report["internal_wall_before_serialization_s"] = time.monotonic() - wall0
    report["complete_process_CPU_authority"] = "Root execute_once wrapper OS-process measurement, not this partial internal timer"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2, default=str)
        stream.write("\n")
    print(json.dumps({"status": report["status"], "checks": report["check_count"],
                      "component_comparisons": report["component_comparisons"],
                      "failed_components": report["failed_components"],
                      "output": str(OUT)}, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())


