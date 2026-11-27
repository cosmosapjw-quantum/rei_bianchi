"""Exact nonaligned age convolution and outward signed scalar propagation.

The general arithmetic API assumes an explicitly declared all-starts full-A
certificate. The saved-case wrapper verifies the actual pinned R11 result bytes.
Metadata checks bind a premise; they do not prove an external physical premise.
No predecessor module, generator calculation, matrix exponential, or ODE is used.
"""
from __future__ import annotations

from bisect import bisect_left, bisect_right
from collections.abc import Mapping, Sequence
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
import re

from positive_arithmetic import BITS, DEGREE, DomainError, bernstein_weights, down, up

MAX_INPUT_BITS = 1024
MAX_CELLS = 192
MAX_REFINED_CELLS = 2048
MAX_BLOCKS = 8
MAX_OVERLAP_TERMS = 200000
R11_SHA256 = "80ed0f8df5c785e47ce737acb8b029485db54b543d57498bf182427093f29b1b"
SAVED_CASE_IDS = (
    "two_state_no_reaction",
    "two_state_nonlinear",
    "two_state_coarse_source_defect",
    "saved_native_nine_state_K_conditional_feedback",
)


def Q(value):
    if isinstance(value, bool) or not isinstance(value, (int, str, Fraction)):
        raise DomainError("Exact int, Fraction, or rational text required; float/bool forbidden")
    if isinstance(value, str) and len(value) > 1200:
        raise DomainError("Input rational text exceeds the finite domain")
    try:
        result = Fraction(value)
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise DomainError("Invalid exact scalar") from exc
    if max(abs(result.numerator).bit_length(), result.denominator.bit_length()) > MAX_INPUT_BITS:
        raise DomainError("Input exceeds 1024-bit numerator/denominator limit")
    return result


def _int(value, low, high, name):
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise DomainError(f"{name} must be an integer in [{low},{high}]")
    return value


def _sequence(value):
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))


def _vector(value, name, length=None, nonnegative=False):
    if not _sequence(value):
        raise DomainError(name + " must be a finite sequence")
    if length is not None and len(value) != length:
        raise DomainError(name + " dimension mismatch")
    out = tuple(Q(v) for v in value)
    if nonnegative and any(v < 0 for v in out):
        raise DomainError(name + " must be nonnegative")
    return out


def _grid(value, name):
    if not _sequence(value) or not 2 <= len(value) <= MAX_CELLS + 1:
        raise DomainError(name + " must have 1..192 exact positive-length cells")
    result = _vector(value, name)
    if any(a >= b for a, b in zip(result, result[1:])):
        raise DomainError(name + " must be strictly increasing without duplicate knots")
    return result


def _forcing(value, cells, name):
    if _sequence(value):
        return _vector(value, name, cells, True)
    scalar = Q(value)
    if scalar < 0:
        raise DomainError(name + " must be nonnegative")
    return (scalar,) * cells


def _binding(value):
    if not isinstance(value, Mapping):
        raise DomainError("Explicit same-source/family/state/clock binding required")
    out = deepcopy(dict(value))
    for name in ("family_id", "clock", "source_sha256", "norm"):
        if not isinstance(out.get(name), str) or not out[name].strip():
            raise DomainError("Missing binding " + name)
    if not re.fullmatch(r"[0-9a-f]{64}", out["source_sha256"]):
        raise DomainError("Malformed binding source SHA256")
    if out["norm"] != "l1_on_kerP":
        raise DomainError("Only zero-mass l1 residual normalization is accepted")
    ids = out.get("state_ids")
    if (not _sequence(ids) or not 1 <= len(ids) <= 13 or
            any(not isinstance(x, str) or not x for x in ids) or len(set(ids)) != len(ids)):
        raise DomainError("Binding requires 1..13 unique ordered state IDs")
    out["state_ids"] = list(ids)
    return out


def _certificate(value, q, tau, t0, end, binding):
    if not isinstance(value, Mapping):
        raise DomainError("All-starts full-propagator certificate premise required")
    out = deepcopy(dict(value))
    for name in ("certificate_id", "source_pointer", "source_sha256", "family_scope"):
        if not isinstance(out.get(name), str) or not out[name].strip():
            raise DomainError("Missing certificate " + name)
    if not out["source_pointer"].startswith("/") or not re.fullmatch(r"[0-9a-f]{64}", out["source_sha256"]):
        raise DomainError("Malformed certificate source locator")
    if out.get("scientific_status") not in ("CERTIFIED_FULL_A_BLOCK", "ARITHMETIC_CONTROL_PREMISE"):
        raise DomainError("Certificate must explicitly describe a full-A block or arithmetic control premise")
    for name in ("uniform_all_starts", "same_family_composition", "remainder_l1_nonexpansive",
                 "zero_mass_forcing", "whole_domain_forcing"):
        if out.get(name) is not True:
            raise DomainError("Missing full-family premise " + name)
    if Q(out.get("q")) != q or Q(out.get("tau")) != tau:
        raise DomainError("Certificate q/tau differs from the supplied arithmetic parameters")
    interval = _vector(out.get("validity_interval"), "certificate validity interval", 2)
    if interval[0] > t0 or interval[1] < end or interval[0] >= interval[1]:
        raise DomainError("Certificate all-starts interval does not cover the exact sweep")
    if _binding(out.get("binding")) != binding:
        raise DomainError("Certificate family/state/clock binding mismatch")
    out["q"], out["tau"], out["validity_interval"] = q, tau, interval
    return out


def _saved_case(raw_bytes, case_id):
    if not isinstance(raw_bytes, bytes):
        raise DomainError("Original R11 result bytes are required")
    actual_sha = hashlib.sha256(raw_bytes).hexdigest()
    if actual_sha != R11_SHA256:
        raise DomainError("Actual R11 source byte SHA256 mismatch")
    if not isinstance(case_id, str) or case_id not in SAVED_CASE_IDS:
        raise DomainError("Unknown pinned R11 case ID")
    data = json.loads(raw_bytes)
    if data.get("status") != "PASS" or data.get("unit") != "WU_FULL_GENERATOR_BLOCK_R11":
        raise DomainError("Pinned R11 source must be the accepted primary result")
    cases = data.get("hd_cases")
    if not isinstance(cases, list) or [x.get("id") for x in cases] != list(SAVED_CASE_IDS):
        raise DomainError("Pinned R11 case ordering mismatch")
    index = SAVED_CASE_IDS.index(case_id)
    case = cases[index]
    raw, capped = case["raw"], case["capped"]
    n = _int(raw["cells"], 1, MAX_CELLS, "saved cells")
    dt, tau, q = Q(raw["delta"]), Q(raw["tau"]), Q(raw["q"])
    if dt <= 0 or tau <= 0 or not 0 <= q <= 1:
        raise DomainError("Saved clock or block coefficient is invalid")
    knots = tuple(i * dt for i in range(n + 1))
    initial = _vector(raw["initial"], "saved initial", 2, True)
    bind = _binding(raw["binding"])
    coefficients = raw["coefficients"]
    c, d = Q(coefficients["c"]), Q(coefficients["d"])
    gr, ge = (_forcing(coefficients[key], n, "saved " + key) for key in ("g_r", "g_e"))
    gen = raw["generator"]
    if (Q(gen["q"]) != q or Q(gen["tau"]) != tau or gen.get("uniform_all_starts") is not True or
            gen.get("nominal_K_rho_directly_transferred") is not False or _binding(gen["binding"]) != bind):
        raise DomainError("Saved full-A certificate identity mismatch")
    if (c < 0 or capped["cells"] != n or Q(capped["delta"]) != dt or Q(capped["tau"]) != tau or
            Q(capped["q"]) != q or _vector(capped["initial"], "capped initial", 2, True) != initial or
            _binding(capped["binding"]) != bind or Q(capped["coefficients"]["c"]) != c or
            Q(capped["coefficients"]["d"]) != d or
            _forcing(capped["coefficients"]["g_r"], n, "capped g_r") != gr or
            _forcing(capped["coefficients"]["g_e"], n, "capped g_e") != ge):
        raise DomainError("Saved raw/capped case source parameters differ")
    points = tuple(_vector(v, "saved point", 2, True) for v in capped["endpoints_upper"])
    whole = tuple(_vector(v, "saved whole cell", 2, True) for v in capped["whole_cells_upper"])
    if len(points) != n + 1 or len(whole) != n or points[0] != initial:
        raise DomainError("Saved cap length or initial identity mismatch")
    if any(points[i + e][k] > whole[i][k] for i in range(n) for e in (0, 1) for k in (0, 1)):
        raise DomainError("Saved closed-cell cap does not contain its point caps")
    return {"case_id": case_id, "case_index": index, "source_scope": case["source_scope"],
            "source_sha256": actual_sha, "q": q, "tau": tau, "c": c, "d": d,
            "initial": initial, "binding": bind, "knots": knots, "g_r": gr, "g_e": ge,
            "points": points, "whole": whole, "raw_saved": raw}


def _prepare_caps(raw_bytes, case_id, *, q, tau, c, d, initial, binding, source, gr, ge):
    saved = _saved_case(raw_bytes, case_id)
    if (saved["q"] != q or saved["tau"] != tau or saved["c"] != c or saved["d"] != d or
            saved["initial"] != initial or saved["binding"] != binding):
        raise DomainError("Cap source/case/parameters/family/state/clock binding mismatch")
    knots = saved["knots"]
    if source[0] != knots[0] or source[-1] != knots[-1]:
        raise DomainError("Cap clock coverage must equal the exact saved interval")
    for j, (left, right) in enumerate(zip(source, source[1:])):
        for old, (a, b) in enumerate(zip(knots, knots[1:])):
            if max(left, a) < min(right, b):
                if gr[j] != saved["g_r"][old] or ge[j] != saved["g_e"][old]:
                    raise DomainError("Forcing function differs from the pinned cap source")
    return saved


def _refined_grid(source, observation, tau, full_blocks, cap_knots):
    t0, end = source[0], source[-1]
    events = set(source) | set(observation) | set(cap_knots)
    for k in range(full_blocks + 1):
        shift = k * tau
        events.add(t0 + shift)
        for a in source:
            t = a + shift
            if t0 <= t <= end:
                events.add(t)
    result = tuple(sorted(events))
    if result[0] != t0 or result[-1] != end or len(result) - 1 > MAX_REFINED_CELLS:
        raise DomainError("Refined exact grid exceeds the 2048-cell domain or its horizon")
    return result


def _overlap_forcing(t, source, gr, tau, powers):
    total = Fraction(0)
    for j, (a, b) in enumerate(zip(source, source[1:])):
        for k, weight in enumerate(powers):
            length = min(b, t - k * tau) - max(a, t - (k + 1) * tau)
            if length > 0:
                total += gr[j] * weight * length
    return total


def _point_old_cells(t, knots):
    j = bisect_left(knots, t)
    if j < len(knots) and knots[j] == t:
        return tuple(i for i in (j - 1, j) if 0 <= i < len(knots) - 1)
    return (j - 1,)


def _aggregate(points, whole, selected):
    requested_points = [points[i] for i in selected]
    requested_whole = []
    for left, right in zip(selected, selected[1:]):
        if not 0 <= left < right <= len(whole):
            raise DomainError("Requested closed-cell refinement has a gap or reversed coverage")
        requested_whole.append(tuple(max(v[k] for v in whole[left:right]) for k in (0, 1)))
    return requested_points, requested_whole


def nonaligned_sweep(q, tau, c, d, g_r, g_e, source_knots, observation_knots, initial, *,
                     binding, certificate, cap_source_bytes=None, cap_case_id=None,
                     bits=BITS, degree=DEGREE):
    """Enclose one fixed-q comparison on exact source/observation partitions.

The supplied certificate is a declared premise, not independently reproved here.
Optional caps require actual pinned R11 source bytes and the identical saved case.
"""
    _int(bits, BITS, BITS, "bits")
    _int(degree, DEGREE, DEGREE, "degree")
    q, tau, c, d = (Q(v) for v in (q, tau, c, d))
    if not 0 <= q <= 1 or tau <= 0 or c < 0:
        raise DomainError("Require q in[0,1], tau>0 and c>=0")
    source = _grid(source_knots, "source knots")
    observation = _grid(observation_knots, "observation knots")
    t0, end = source[0], source[-1]
    if observation[0] != t0 or observation[-1] != end:
        raise DomainError("Source and observation partitions must cover the same exact interval")
    horizon = end - t0
    blocks = horizon // tau
    if blocks > MAX_BLOCKS:
        raise DomainError("More than eight complete kernel blocks")
    if abs(d) * horizon > 16:
        raise DomainError("Absolute d times the complete horizon exceeds16")
    init = _vector(initial, "initial", 2, True)
    gr, ge = (_forcing(v, len(source) - 1, name) for v, name in ((g_r, "g_r"), (g_e, "g_e")))
    bind = _binding(binding)
    cert = _certificate(certificate, q, tau, t0, end, bind)
    if len(bind["state_ids"]) == 1 and (init[0] != 0 or any(gr)):
        raise DomainError("Singleton zero-mass residual requires R0=g_r=0")
    if (cap_source_bytes is None) != (cap_case_id is None):
        raise DomainError("Cap source bytes and exact case ID must be supplied together")
    caps = None
    if cap_source_bytes is not None:
        caps = _prepare_caps(cap_source_bytes, cap_case_id, q=q, tau=tau, c=c, d=d, initial=init,
                             binding=bind, source=source, gr=gr, ge=ge)
    cap_knots = caps["knots"] if caps is not None else ()
    refined = _refined_grid(source, observation, tau, blocks, cap_knots)
    overlap_terms = len(refined) * (len(source) - 1) * (blocks + 1)
    if overlap_terms > MAX_OVERLAP_TERMS:
        raise DomainError("Exact overlap enumeration exceeds200000 terms")
    powers = [Fraction(1)]
    for _ in range(blocks):
        powers.append(powers[-1] * q)
    kernel = [powers[(t - t0) // tau] for t in refined]
    forcing = [_overlap_forcing(t, source, gr, tau, powers) for t in refined]
    rexact = [h * init[0] + f for h, f in zip(kernel, forcing)]
    rl, ru = [down(v) for v in rexact], [up(v) for v in rexact]
    rl[0] = ru[0] = init[0]
    el, eu = [init[1]], [init[1]]
    raw_whole, affine, exact_affine, source_indices, weights = [], [], [], [], {}
    for i, (left, right) in enumerate(zip(refined, refined[1:])):
        source_index = bisect_right(source, left) - 1
        if not (0 <= source_index < len(source) - 1 and source[source_index] <= left < right <= source[source_index + 1]):
            raise DomainError("Refined cell crosses or misses a source cell")
        source_indices.append(source_index)
        length = right - left
        if length not in weights:
            weights[length] = bernstein_weights(d, length)
        w = weights[length]
        e, w0, w1, phi = (w[key] for key in ("exp", "W0", "W1", "phi"))
        lexact = rexact[i]
        vexact = kernel[i] * init[0] + forcing[i + 1]
        vl, vu = down(vexact), up(vexact)
        rs = max(ru[i], vu, ru[i + 1])
        el.append(down(e[0] * el[-1] + c * (w0[0] * rl[i] + w1[0] * vl) + phi[0] * ge[source_index]))
        eu.append(up(e[1] * eu[-1] + c * (w0[1] * ru[i] + w1[1] * vu) + phi[1] * ge[source_index]))
        constant_end = up(e[1] * eu[i] + phi[1] * (c * rs + ge[source_index]))
        raw_whole.append((rs, max(eu[i], eu[i + 1], constant_end)))
        affine.append({"left_interval": (rl[i], ru[i]), "right_left_limit_interval": (vl, vu),
                       "source_cell_index": source_index, "length": length})
        exact_affine.append({"L": lexact, "V": vexact,
                             "whole_R": max(lexact, vexact, rexact[i + 1])})
    raw_low, raw_high = list(zip(rl, el)), list(zip(ru, eu))
    selected = [bisect_left(refined, t) for t in observation]
    if any(refined[i] != t for i, t in zip(selected, observation)):
        raise DomainError("Requested observation knot is not an exact refined knot")
    requested_raw, requested_whole = _aggregate(raw_high, raw_whole, selected)
    requested_low = [raw_low[i] for i in selected]
    raw_result = {"endpoints_lower": requested_low, "endpoints_upper": requested_raw,
                  "whole_cells_upper": requested_whole, "refined_endpoints_lower": raw_low,
                  "refined_endpoints_upper": raw_high, "refined_whole_cells_upper": raw_whole,
                  "R_affine_cells": affine,
                  "lower_endpoint_meaning": "chosen rational-q ideal comparison only; never physical-error lower"}
    cap_result, cap_record = None, None
    if caps is not None:
        old_knots, old_points, old_whole = caps["knots"], caps["points"], caps["whole"]
        point_index = {t: i for i, t in enumerate(old_knots)}
        point_map = [point_index.get(t) for t in refined]
        point_cells = [_point_old_cells(t, old_knots) for t in refined]
        whole_map = []
        for left, right in zip(refined, refined[1:]):
            old = bisect_right(old_knots, left) - 1
            if not (0 <= old < len(old_whole) and old_knots[old] <= left < right <= old_knots[old + 1]):
                raise DomainError("Old closed-cell cap does not cover a refined subcell")
            whole_map.append(old)

        def point_candidates(i, component):
            values = [old_whole[j][component] for j in point_cells[i]]
            if point_map[i] is not None:
                values.append(old_points[point_map[i]][component])
            return values

        out_points, out_whole, propagation = [init], [], []
        for i, (left, right) in enumerate(zip(refined, refined[1:])):
            old = whole_map[i]
            w = weights[right - left]
            e, phi = w["exp"], w["phi"]
            rs = min(raw_whole[i][0], old_whole[old][0])
            left_e = min([out_points[i][1], eu[i], old_whole[old][1]] + point_candidates(i, 1))
            left_r = min([out_points[i][0], ru[i], rs] + point_candidates(i, 0))
            out_points[i] = (left_r, left_e)
            scalar_right = up(e[1] * left_e + phi[1] * (c * rs + ge[source_indices[i]]))
            es = min(raw_whole[i][1], max(left_e, scalar_right), old_whole[old][1])
            right_r = min([ru[i + 1], rs] + point_candidates(i + 1, 0))
            right_e = min([eu[i + 1], scalar_right, es] + point_candidates(i + 1, 1))
            out_whole.append((rs, es))
            out_points.append((right_r, right_e))
            propagation.append({"old_cell_index": old, "left_E_used": left_e, "R_whole_used": rs,
                                "unclipped_scalar_right_upper": scalar_right, "whole_E_upper": es,
                                "right_E_before_output_neighbor_intersection": right_e})
        for i in range(len(out_points)):
            adjacent = out_whole[max(0, i - 1):min(len(out_whole), i + 1)]
            out_points[i] = tuple(min([out_points[i][k]] + [row[k] for row in adjacent]) for k in (0, 1))
        requested_cap, requested_cap_whole = _aggregate(out_points, out_whole, selected)
        cap_result = {"endpoints_lower": None, "endpoints_upper": requested_cap,
                      "whole_cells_upper": requested_cap_whole, "refined_endpoints_lower": None,
                      "refined_endpoints_upper": out_points, "refined_whole_cells_upper": out_whole,
                      "propagation": propagation, "R_memory_reset": False,
                      "lower_endpoint_meaning": "no lower enclosure asserted after source-backed conditional upper-cap intersection"}
        cap_record = {"source_sha256": R11_SHA256, "case_id": caps["case_id"],
                      "case_index": caps["case_index"],
                      "point_source_pointer": f"/hd_cases/{caps['case_index']}/capped/endpoints_upper",
                      "whole_source_pointer": f"/hd_cases/{caps['case_index']}/capped/whole_cells_upper",
                      "old_knots": old_knots, "old_points_upper": old_points, "old_whole_cells_upper": old_whole,
                      "subcell_to_old_cell": whole_map, "refined_point_to_old_point": point_map,
                      "refined_point_containing_old_closed_cells": point_cells,
                      "requested_point_to_old_point": [point_map[i] for i in selected],
                      "transfer_rule": "whole closed-cell interval inclusion; point only exact rational equality; no interpolation"}
    return {"schema": "WU_R12_NONALIGNED_CONVOLUTION_V1",
            "parameters": {"q": q, "tau": tau, "c": c, "d": d, "initial": init,
                           "t0": t0, "T": end, "binding": bind, "certificate": cert},
            "source": {"knots": source, "g_r": gr, "g_e": ge},
            "requested_times": observation, "refined_times": refined,
            "exact": {"kernel_at_refined": kernel, "F_at_refined": forcing, "R_at_refined": rexact,
                      "R_affine_cells": exact_affine, "kernel_powers": powers},
            "refinement": {"source_cell_indices": source_indices, "requested_point_indices": selected,
                           "requested_subcell_ranges": list(zip(selected, selected[1:])),
                           "includes_all_source_translated_jumps": True,
                           "right_endpoint_limit": "approach the right endpoint from the LEFT"},
            "Bernstein_weights_by_length": {str(length): value for length, value in weights.items()},
            "raw": raw_result, "capped": cap_result, "caps": cap_record,
            "h0": 1, "R_memory_reset": False,
            "work": {"source_cells": len(source) - 1, "observation_cells": len(observation) - 1,
                     "refined_cells": len(refined) - 1, "full_blocks": blocks,
                     "overlap_terms": overlap_terms, "distinct_Bernstein_lengths": len(weights)},
            "rounding": {"bits": bits, "degree": degree, "R_kernel_and_F": "exact Fraction",
                         "scalar_E": "outward dyadic128 copied R11 positive Taylor96 Bernstein moments"},
            "physical_consumer_admitted": False, "old_science_replay": 0, "new_ODE_calls": 0}


def saved_case_sweep(r11_source_bytes, case_id, grid_variant="aligned"):
    """Run the new convolution on one actual R11 saved conditional case.

Reads only the supplied original result bytes. Both raw and source-capped R12
outputs are returned on one common exact refinement. No old runner is imported.
"""
    saved = _saved_case(r11_source_bytes, case_id)
    old_knots = saved["knots"]
    if len(old_knots) != 193:
        raise DomainError("The saved-case contract requires the actual192-cell input")
    if grid_variant == "aligned":
        observation = old_knots
    elif grid_variant == "nonaligned":
        delta = old_knots[1] - old_knots[0]
        observation = (old_knots[0],) + tuple((Fraction(n) + (Fraction(1, 3) if n % 2 else -Fraction(1, 5))) * delta
                                             for n in range(1, 192)) + (old_knots[-1],)
    else:
        raise DomainError("Unknown saved grid variant")
    if not (all(x == saved["g_r"][0] for x in saved["g_r"]) and
            all(x == saved["g_e"][0] for x in saved["g_e"])):
        raise DomainError("Saved one-cell compression requires exact constant g_r and g_e")
    certificate = {"certificate_id": "R11_saved_full_A_" + case_id,
                   "scientific_status": "CERTIFIED_FULL_A_BLOCK",
                   "source_sha256": R11_SHA256,
                   "source_pointer": f"/hd_cases/{saved['case_index']}/raw/generator",
                   "q": saved["q"], "tau": saved["tau"],
                   "validity_interval": (old_knots[0], old_knots[-1]),
                   "uniform_all_starts": True, "same_family_composition": True,
                   "remainder_l1_nonexpansive": True, "zero_mass_forcing": True, "whole_domain_forcing": True,
                   "family_scope": "R11 fixed K/pi/destruction and every measurable w in the same certified whole box",
                   "binding": deepcopy(saved["binding"])}
    result = nonaligned_sweep(saved["q"], saved["tau"], saved["c"], saved["d"],
                              saved["g_r"][0], saved["g_e"][0],
                              (old_knots[0], old_knots[-1]), observation, saved["initial"],
                              binding=saved["binding"], certificate=certificate,
                              cap_source_bytes=r11_source_bytes, cap_case_id=case_id)
    result["saved_case"] = {"case_id": case_id, "case_index": saved["case_index"],
                            "source_sha256": R11_SHA256, "source_scope": saved["source_scope"],
                            "grid_variant": grid_variant, "constant_source_compression_exact": True,
                            "old_source_cells": len(old_knots) - 1, "new_source_cells": 1,
                            "nominal_K_recomputed": False, "native_exponential_recomputed": False}
    return result


def export(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Mapping):
        return {str(k): export(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [export(v) for v in value]
    return value
