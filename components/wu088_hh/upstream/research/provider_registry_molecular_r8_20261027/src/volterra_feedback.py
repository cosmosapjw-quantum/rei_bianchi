"""R8: two positive Volterra passes from certified saved R7 cell bounds.

No generator, ODE, or old scientific runner is evaluated here. Inputs must
already refer to one compatible, uniformly nonexpansive nominal family.
The caller verifies saved-envelope/cap membership against frozen JSON.
All arithmetic bounds are upward dyadic128; final minima preserve exact
saved bounds without re-rounding, so no-worse statements are literal.
"""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from functools import lru_cache
import hashlib
import importlib.util
from pathlib import Path
import sys

R7_CORE_SHA256 = "002a66a30961b21e566a940462468c9ea8e1bc868d98549d3ea79d164c239957"
R7_PRIMARY_SHA256 = "6eaf3c0eed7968cf4023180e15373a180bb5b1bab2e56cd4a8547387ed337a15"
BITS, SCALE, MAX_CELLS = 128, 1 << 128, 192
MAX_INTEGER_BITS = 8192


class DomainError(ValueError):
    """The fixed finite arithmetic or evidence contract is not satisfied."""


def Q(value):
    if isinstance(value, (bool, float)):
        raise DomainError("Binary floats and booleans are not exact inputs")
    if not isinstance(value, (int, str, Fraction)):
        raise DomainError("Require an integer, Fraction, or exact numeric string")
    if isinstance(value, str) and (len(value) > 4096 or "e" in value.lower()):
        raise DomainError("Use a bounded integer, decimal, or rational string")
    try:
        out = Fraction(value)
    except (ValueError, ZeroDivisionError, TypeError) as exc:
        raise DomainError("Invalid exact scalar") from exc
    if max(abs(out.numerator).bit_length(), out.denominator.bit_length()) > MAX_INTEGER_BITS:
        raise DomainError("Exact scalar exceeds the finite integer-size domain")
    return out


def export(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): export(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [export(v) for v in value]
    return value


def _size(value, low, high, name):
    if type(value) is not int or not low <= value <= high:
        raise DomainError(name + " is outside its finite integer range")
    return value


def _bits(bits):
    if type(bits) is not int or bits != BITS:
        raise DomainError("This R8 contract fixes 128 dyadic bits")


def _vec(values, size, name, nonnegative=True):
    if not isinstance(values, (tuple, list)) or len(values) != size:
        raise DomainError(name + " has the wrong finite vector shape")
    out = tuple(Q(x) for x in values)
    if nonnegative and any(x < 0 for x in out):
        raise DomainError(name + " must be nonnegative")
    return out


def _positive(value, name):
    out = Q(value)
    if out <= 0:
        raise DomainError(name + " must be positive")
    return out


def _up(value):
    if value < 0:
        raise DomainError("Positive arithmetic received a negative value")
    integer = -((-value.numerator * SCALE) // value.denominator)
    if integer.bit_length() > MAX_INTEGER_BITS:
        raise DomainError("A dyadic envelope exceeds the finite integer-size domain")
    return Fraction(integer, SCALE)


def _mul(left, right):
    return _up(left * right)


def _sum(values):
    total = Fraction(0)
    for value in values:
        total = _up(total + value)
    return total


def _sha(value):
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise DomainError("Require an explicit lowercase SHA256 identity")
    return value


def _binding(value):
    if not isinstance(value, dict):
        raise DomainError("A common nominal-family binding is required")
    result = {}
    for key in ("clock", "family_id"):
        if not isinstance(value.get(key), str) or not value[key].strip():
            raise DomainError("Missing " + key)
        result[key] = value[key]
    ids = value.get("state_ids")
    if not isinstance(ids, (list, tuple)) or not 1 <= len(ids) <= 16:
        raise DomainError("Require an ordered state identity list of length 1..16")
    if any(not isinstance(x, str) or not x for x in ids) or len(set(ids)) != len(ids):
        raise DomainError("State identities must be nonempty and distinct")
    result["state_ids"] = tuple(ids)
    result["source_sha256"] = _sha(value.get("source_sha256"))
    for key, expected in (("norm", "l1_on_kerP"), ("generator_scope", "nominal_K")):
        if value.get(key) != expected:
            raise DomainError("Incompatible " + key)
        result[key] = expected
    for key in ("uniform_all_starts", "nonexpansive", "same_family_composition"):
        if value.get(key) is not True:
            raise DomainError("The kernel requires " + key)
        result[key] = True
    return result


def kernel_ladder(delta, cells, certificates, *, binding, bits=128):
    """h[n] bounds the nominal propagator at every lag >= n*delta."""
    _bits(bits)
    delta = _positive(delta, "delta")
    cells = _size(cells, 1, MAX_CELLS, "cells")
    common = _binding(binding)
    if not isinstance(certificates, (list, tuple)) or not 1 <= len(certificates) <= 8:
        raise DomainError("Require one to eight saved block certificates")
    items, seen = [], set()
    for cert in certificates:
        if not isinstance(cert, dict) or _binding(cert.get("binding")) != common:
            raise DomainError("Certificate clock/state/family binding differs")
        identity = cert.get("id")
        if not isinstance(identity, str) or not identity or identity in seen:
            raise DomainError("Certificate identities must be distinct")
        seen.add(identity)
        H, rho = _positive(cert.get("H"), "certificate H"), Q(cert.get("rho"))
        if not 0 <= rho <= 1:
            raise DomainError("A nominal contraction must lie in [0,1]")
        steps = H / delta
        if steps.denominator != 1 or not 1 <= steps <= MAX_CELLS:
            raise DomainError("Certificate H must be an exact finite integer multiple of delta")
        items.append({"id": identity, "H": H, "rho": rho, "steps": int(steps)})
    h, witness = [Fraction(1)], [{"kind": "nonexpansive", "index": 0}]
    for n in range(1, cells + 1):
        candidates = [(h[n - 1], {"kind": "previous_lag", "index": n - 1})]
        for cert in items:
            m = cert["steps"]
            if m <= n:
                candidates.append((_mul(cert["rho"], h[n - m]),
                                   {"kind": "block_composition", "id": cert["id"], "index": n - m}))
        value, reason = min(candidates, key=lambda item: item[0])
        h.append(value)
        witness.append(reason)
    return {"h": tuple(h), "delta": delta, "cells": cells, "bits": bits,
            "certificates": items, "binding": common, "witness": witness}


@lru_cache(maxsize=1)
def _r7_negative_exp():
    """Import frozen definitions from verified source bytes; no R7 runner."""
    path = Path(__file__).resolve().parents[2] / "provider_registry_molecular_r7_20261027/src/nonlinear_feedback.py"
    source = path.read_bytes()
    if hashlib.sha256(source).hexdigest() != R7_CORE_SHA256:
        raise DomainError("Frozen R7 exponential dependency SHA256 differs")
    name = "_wu_r8_verified_r7_002a66a3"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None:
        raise DomainError("Cannot create the frozen dependency import")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module.exp_neg_enclosure


def coarse_step_factors(d, delta, *, bits=128):
    """Upper e=exp(d*delta), phi=integral exp(d*s)ds, without inversion at d=0."""
    _bits(bits)
    d, delta = Q(d), _positive(delta, "delta")
    if abs(d) * delta > 16:
        raise DomainError("The new exponential argument exceeds sixteen")
    if d == 0:
        return {"e_upper": Fraction(1), "phi_upper": _up(delta),
                "negative_exp_interval": (Fraction(1), Fraction(1)),
                "d": d, "delta": delta, "branch": "exact_d_zero", "bits": bits}
    iv = _r7_negative_exp()(abs(d) * delta, degree=48, bits=bits)
    if d < 0:
        e = min(Fraction(1), _up(iv.hi))
        phi = _up((1 - iv.lo) / (-d))
    else:
        if iv.lo <= 0:
            raise DomainError("A positive reciprocal exponential lower bound is required")
        e = _up(1 / iv.lo)
        phi = _up((e - 1) / d)
    return {"e_upper": e, "phi_upper": phi, "negative_exp_interval": (iv.lo, iv.hi),
            "d": d, "delta": delta, "branch": "negative_d" if d < 0 else "positive_d",
            "bits": bits, "degree": 48, "dependency_sha256": R7_CORE_SHA256}


def _point_caps(records, delta, cells):
    if not isinstance(records, (list, tuple)) or len(records) > 1024:
        raise DomainError("Require a finite saved-cap record list")
    caps, provenance = {}, []
    for record in records:
        if not isinstance(record, dict):
            raise DomainError("A saved cap must be a record")
        if record.get("source_kind") not in ("saved_R7_query", "saved_R7_endpoint"):
            raise DomainError("Only saved R7 certified bounds may cap an endpoint")
        if _sha(record.get("source_sha256")) != R7_PRIMARY_SHA256:
            raise DomainError("A cap does not identify the frozen R7 primary result")
        pointer = record.get("source_pointer")
        if not isinstance(pointer, str) or not pointer.startswith("/"):
            raise DomainError("A cap needs its original JSON pointer")
        t = Q(record.get("time"))
        index = t / delta
        if index.denominator != 1 or not 0 <= index <= cells:
            raise DomainError("A cap is not at an exact common stored clock")
        index = int(index)
        upper = _vec(record.get("upper"), 2, "stored cap")
        caps[index] = tuple(min(a, b) for a, b in zip(caps.get(index, upper), upper))
        provenance.append({**deepcopy(record), "index": index, "time": t, "upper": upper})
    return caps, provenance


def volterra_two_pass(B, g, delta, initial, baseline_cells, certificates, *,
                      binding, point_caps=(), bits=128):
    """Two monotone upper passes; baseline cells already hold on closed cells.

    The runner must verify baseline/cap membership against the pinned R7 JSON.
    R7 local queries use t0+query.t; true macro endpoints use w_next_upper.
    Saved reference actual errors are never admissible caps.
    """
    _bits(bits)
    if not isinstance(B, (list, tuple)) or len(B) != 2:
        raise DomainError("Comparison B must be 2 by 2")
    first, second = (_vec(row, 2, "B row", nonnegative=False) for row in B)
    a, b, c, d = first[0], first[1], second[0], second[1]
    if min(a, b, c) < 0:
        raise DomainError("Positive Volterra comparison requires a,b,c >= 0")
    gr, ge = _vec(g, 2, "forcing")
    R0, E0 = _vec(initial, 2, "initial errors")
    delta = _positive(delta, "delta")
    if not isinstance(baseline_cells, (list, tuple)):
        raise DomainError("Require a finite baseline cell array")
    cells = _size(len(baseline_cells), 1, MAX_CELLS, "cells")
    baseline = tuple(_vec(row, 2, "baseline whole-cell upper") for row in baseline_cells)
    if baseline[0][0] < R0 or baseline[0][1] < E0:
        raise DomainError("The initial baseline cell excludes the supplied initial bound")
    ladder = kernel_ladder(delta, cells, certificates, binding=binding, bits=bits)
    factors = coarse_step_factors(d, delta, bits=bits)
    caps, provenance = _point_caps(point_caps, delta, cells)
    h, e, phi = ladder["h"], factors["e_upper"], factors["phi_upper"]
    powers = [Fraction(1)]
    for _ in range(cells):
        powers.append(_mul(powers[-1], e))
    rweights = tuple(_mul(delta, value) for value in h)
    eweights = tuple(_mul(phi, value) for value in powers)
    previous, passes = baseline, []
    for pass_index in (1, 2):
        F = tuple(_sum((_mul(a, row[0]), _mul(b, row[1]), _up(gr))) for row in previous)
        L = tuple(_sum((_mul(c, row[0]), _up(ge))) for row in previous)
        whole, raw_ends = [], [(R0, E0)]
        for n in range(cells):
            rwhole = _sum([_mul(h[n], R0), _mul(delta, F[n])] +
                          [_mul(rweights[n - j - 1], F[j]) for j in range(n)])
            rend = _sum([_mul(h[n + 1], R0)] +
                        [_mul(rweights[n - j], F[j]) for j in range(n + 1)])
            initial_power = n if d <= 0 else n + 1
            lag_shift = 1 if d <= 0 else 0
            ewhole = _sum([_mul(powers[initial_power], E0), _mul(phi, L[n])] +
                          [_mul(eweights[n - j - lag_shift], L[j]) for j in range(n)])
            eend = _sum([_mul(powers[n + 1], E0)] +
                        [_mul(eweights[n - j], L[j]) for j in range(n + 1)])
            whole.append((min(previous[n][0], rwhole), min(previous[n][1], ewhole)))
            raw_ends.append((rend, eend))
        endpoints = tuple(tuple(min(value, caps[i][k]) if i in caps else value
                                for k, value in enumerate(pair)) for i, pair in enumerate(raw_ends))
        passes.append({"pass": pass_index, "whole_cells": tuple(whole),
                       "raw_endpoints": tuple(raw_ends), "endpoints": endpoints,
                       "F_upper": F, "L_upper": L,
                       "strictly_tightened_cell_components":
                           sum(whole[n][k] < previous[n][k] for n in range(cells) for k in range(2))})
        previous = tuple(whole)
    return {"schema": "WU_R8_POSITIVE_VOLTERRA_TWO_PASS_V1",
            "B": (first, second), "g": (gr, ge), "delta": delta, "cells": cells,
            "initial": (R0, E0), "baseline_cells": baseline, "kernel": ladder,
            "coarse_factors": factors, "passes": passes,
            "whole_cells": previous, "endpoints": passes[-1]["endpoints"],
            "cap_provenance": provenance, "baseline_expected_sha256": R7_PRIMARY_SHA256,
            "rounding": "upward dyadic128 arithmetic; final exact minima are not re-rounded",
            "physical_consumer_admitted": False, "new_generator_or_ODE_calls": 0}
