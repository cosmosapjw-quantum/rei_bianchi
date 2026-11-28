"""Source-qualified molecular coefficients and exact finite-state algebra.

This module evaluates two published formulae at the 29 contracted native nodes.
It does not admit a coefficient to a physical consumer, infer a Q, or evolve an IVP.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

BASE = Path(__file__).resolve().parent
PACKET_SHA256 = "40e2fbd73d451c0c8116b4ca9bd4db4d2e43e4cdf8967988a2fea551f99ce35e"
RA = "BENNETT2003_LIH_SPONTANEOUS_RA_TABLE3"
HD = "GONZALEZ_LEZANA2022_HD_HPLUS_DESTRUCTION_THERMAL"
TIQM = "HONVAULT2013_CORRECTED_HD_FORMATION_TIQM"
SQM = "HONVAULT2013_CORRECTED_HD_FORMATION_SQM"
ORTHO = "BOVINO2009_LIH_H_TO_LI_ORTHO_H2_TABLE1"
PARA = "BOVINO2009_LIH_H_TO_LI_PARA_H2_TABLE1"


class Unqualified(ValueError):
    pass


def exact(value):
    if isinstance(value, Fraction):
        return value
    if type(value) not in (int, str):
        raise ValueError("EXACT_INTEGER_OR_DECIMAL_STRING_REQUIRED")
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError("FINITE_RATIONAL_REQUIRED") from exc


def load_packet():
    data = (BASE / "sources/MOLECULAR_SOURCE_PACKET.json").read_bytes()
    if hashlib.sha256(data).hexdigest() != PACKET_SHA256:
        raise ValueError("FROZEN_SOURCE_PACKET_CHANGED")
    return json.loads(data)


def source_index(packet=None):
    packet = load_packet() if packet is None else packet
    rows = packet["rows"]
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("DUPLICATE_SOURCE_VARIANT")
    return {r["id"]: r for r in rows}


def native_value(row):
    """Read decimal source coefficients exactly; no interpolation or spin factors."""
    if "k" in row:
        return exact(row["k"])
    return exact(row["k_mantissa"]) * exact(row["k_scale"])


def evaluate_source_fit(provider_id, temperature_K, *, extra_spin_factor=None):
    """Faithfully sample the source formula at its contracted printed comparison nodes.

    A returned value has SOURCE_FORMULA_SAMPLE status, never physical-rate admission.
    Bovino's printed fit-unit conflict and all uncontracted temperatures fail closed.
    """
    source = source_index()[provider_id]
    t = exact(temperature_K)
    if t <= 0:
        raise ValueError("POSITIVE_TEMPERATURE_REQUIRED")
    if extra_spin_factor is not None:
        raise Unqualified("SOURCE_STATISTICAL_WEIGHT_ALREADY_INCLUDED_OR_UNBOUND")
    if provider_id not in (RA, HD):
        raise Unqualified("NO_ADOPTED_FORMULA_FOR_THIS_SOURCE")
    if t not in {exact(row["T"]) for row in source["native_rows"]}:
        raise Unqualified("OUTSIDE_CONTRACTED_NATIVE_SAMPLE_NODES")
    T = float(t)
    fit = source["native_fit"]
    if provider_id == RA:
        p = fit["parameters"]
        z = T / float(p["T_scale_K"])
        denominator = float(p["a"]) * z ** float(p["b"]) + float(p["c"]) * z ** float(p["d"])
        value = (float(p["offset"]) + 1.0 / denominator) * float(p["k_scale"])
    else:
        value = float(fit["alpha"]) * math.exp(-float(fit["gamma"]) / T)
    if not (math.isfinite(value) and value > 0):
        raise ArithmeticError("NONPOSITIVE_OR_NONFINITE_SOURCE_FORMULA")
    return {"provider_id": provider_id, "T_K": str(t), "k_cm3_s": value,
            "status": "SOURCE_FORMULA_SAMPLE", "physical_rate_admitted": False,
            "state_distribution_bound": False, "Q_admitted": False,
            "source_packet_sha256": PACKET_SHA256}


def select_source_candidates(provider_ids):
    """Candidate choice only. This never activates a physical reaction."""
    ids = list(provider_ids)
    if len(ids) != len(set(ids)):
        raise Unqualified("DUPLICATE_SOURCE_SELECTION")
    index = source_index()
    if any(i not in index for i in ids):
        raise ValueError("UNKNOWN_SOURCE_VARIANT")
    if TIQM in ids and SQM in ids:
        raise Unqualified("TIQM_SQM_ARE_METHOD_ALTERNATIVES")
    if ORTHO in ids and PARA in ids:
        raise Unqualified("BOVINO_SPIN_SUM_NORMALIZATION_UNBOUND")
    return {"selected_candidates": ids, "activation": False}


def request_physical_rate(provider_id):
    source_index()[provider_id]
    raise Unqualified("PHYSICAL_STATE_NORMALIZATION_UNCERTAINTY_AND_CONSUMER_NOT_ADMITTED")


def positive_lift(total, weights):
    X = exact(total)
    p = tuple(exact(v) for v in weights)
    if X < 0 or not p or any(v < 0 for v in p) or sum(p) != 1:
        raise ValueError("NONNEGATIVE_TOTAL_AND_NORMALIZED_POSITIVE_LIFT_REQUIRED")
    return tuple(X * v for v in p)


def destruction_defect(populations, weights, state_rates, collider):
    """Exact rational instantiation of the conditional state-lift theorem.

    Inputs are declared mathematical values. The source packet supplies no such
    complete state-rate vector and lift; this function cannot create that binding.
    """
    x = tuple(exact(v) for v in populations)
    d = tuple(exact(v) for v in state_rates)
    h = exact(collider)
    if not x or len(x) != len(d) or len(x) != len(weights):
        raise ValueError("MATCHED_NONEMPTY_STATE_VECTORS_REQUIRED")
    if h < 0 or any(v < 0 for v in x + d):
        raise ValueError("NONNEGATIVE_STATE_INPUTS_REQUIRED")
    X = sum(x)
    lifted = positive_lift(X, weights)
    pi = tuple(exact(v) for v in weights)
    k = sum(di * p for di, p in zip(d, pi))
    J = h * sum(di * xi for di, xi in zip(d, x))
    approximate = h * k * X
    residual = tuple(xi - yi for xi, yi in zip(x, lifted))
    bound = h * (max(d) - min(d)) * sum(abs(v) for v in residual) / 2
    return {"total": X, "effective_k_for_declared_lift": k, "exact_flux": J,
            "lift_flux": approximate, "defect": J - approximate,
            "half_spread_L1_bound": bound,
            "uniform_scalar_closure": h == 0 or max(d) == min(d),
            "physical_source_binding": False}


def conditional_event_flux_per_reference(k_cm3_s, nA_cm3, nB_cm3, nref_cm3):
    """Dimensional identity for distinct reactants; no physical source binding."""
    k, a, b, ref = map(exact, (k_cm3_s, nA_cm3, nB_cm3, nref_cm3))
    if min(k, a, b) < 0 or ref <= 0:
        raise ValueError("NONNEGATIVE_DENSITIES_AND_POSITIVE_REFERENCE_REQUIRED")
    return {"value": k * a * b / ref,
            "unit": "events_per_reference_nucleus_per_proper_second",
            "distinct_reactants": True, "physical_source_binding": False}
