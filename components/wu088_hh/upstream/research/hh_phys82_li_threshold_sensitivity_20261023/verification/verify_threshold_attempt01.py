"""One create-only PHYS82 independent verification pass.

Run only through source/leased_call.py.  Gamma-free QAWS quadrature checks
the new gap at the six frozen temperatures; the old nine-row identity is
read, never replayed.  Synthetic runner fixtures are control-flow evidence
only and live outside the scientific results directory.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
from contextlib import ExitStack
import copy
import csv
from dataclasses import FrozenInstanceError, asdict, replace
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import sys
import traceback
from unittest.mock import patch

import numpy as np
import scipy
from scipy.integrate import quad

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from source import run_study as runner
from source import threshold_gap as gapmod
from source.vendor.phys81.finite_ci import FiniteWindowCI

FROZEN_T = (255.0, 777.0, 3200.0, 11000.0, 25370.66308424773, 50000.0)
I = 5.39172060034581
E0 = 6.0
DELTA = E0 - I
SIGMA0 = 5.18148e-17
P_W = (math.sqrt(91.0 / 3.0) - 1.0) / 4.0
KB = 1.380649e-23 / 1.602176634e-19
C = 100.0 * math.sqrt(8.0 * 1.602176634e-19 / (math.pi * 9.1093837139e-31))
EXPOSURES = (1.0e9, 1.0e11, 1.0e13)
GATE_QUAD = 1.0e-10
GATE_PL = 1.0e-10
GATE_FD = 1.0e-7
REFERENCE = {
    "L0": (1.0, 0, SIGMA0), "L1": (1.0, 1, SIGMA0),
    "W0": (P_W, 0, SIGMA0), "W1": (P_W, 1, SIGMA0),
    "ZA1969": (1.0, 0, 9.0e-17 * DELTA),
}
SCOPED_FILES = (
    "CONTRACT.json", "theory/THRESHOLD_CONSTRUCTION_KO.md",
    "source/threshold_gap.py", "source/run_study.py", "source/leased_call.py",
    "source/plot_study.py", "source/vendor/REUSE.json",
    "source/vendor/phys81/finite_ci.py",
    "source/vendor/phys81/vendor/ci_finite_c22d.py",
    "source/vendor/phys81/vendor/CCC_TICS_1S.txt",
    "source/vendor/phys78_run_pilot.py",
    "source_data/PHYS81_PARENT_REGISTRY.json", "source_data/PHYS81_LITERAL.csv",
    "source_data/PHYS81_SAVED_RATE_PROFILES.json",
    "source_data/LI_THRESHOLD_SOURCE_CONTRACT.json", "tests/verify_threshold.py",
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def create_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, allow_nan=False, indent=2)
        stream.write("\n")


class Audit:
    def __init__(self):
        self.checks = Counter()
        self.callbacks = Counter()
        self.maxima = {}
        self.failures = []
        self.records = {}

    def check(self, condition, category, name, detail=None):
        self.checks[category] += 1
        if not bool(condition):
            self.failures.append({"category": category, "name": name, "detail": detail})

    def metric(self, error, gate, category, name, detail=None):
        error = float(error)
        old = self.maxima.get(category)
        if old is None or error > old["value"]:
            self.maxima[category] = {"value": error, "case": name, "gate": gate}
        self.check(math.isfinite(error) and error <= gate, category, name,
                   {"error": error, "gate": gate, "context": detail})
        return error

    def reject(self, fn, name, exceptions=(ValueError,), category="guards"):
        try:
            fn()
        except exceptions:
            self.check(True, category, name)
        except Exception as exc:
            self.check(False, category, name, "wrong exception: " + repr(exc))
        else:
            self.check(False, category, name, "invalid input accepted")


def rel(a, b):
    return abs(a - b) / max(abs(b), sys.float_info.min)


def compare_rate(audit, actual, reference, prefix, name, gate):
    metrics = {
        "K_relative": rel(actual.K_cm3_s, reference["K"]),
        "logK_as_rate_relative": abs(math.expm1(actual.logK_cm3_s - reference["logK"])),
        "mean_relative": rel(actual.mean_incoming_eV, reference["mean"]),
        "excess_relative": rel(actual.mean_excess_over_chemical_eV, reference["excess"]),
        "dlog_scaled_relative": abs(actual.dlogK_dT_per_K - reference["dlog"]) /
            max(abs(reference["dlog"]), 1.0 / actual.temperature_K),
        "dK_scaled_relative": abs(actual.dK_dT_cm3_s_K - reference["dK"]) /
            max(abs(reference["dK"]), reference["K"] / actual.temperature_K),
    }
    for metric, value in metrics.items():
        audit.metric(value, gate, prefix + "." + metric, name)
    return metrics


def rate_dict(rate):
    return {"K": rate.K_cm3_s, "logK": rate.logK_cm3_s,
            "mean": rate.mean_incoming_eV,
            "excess": rate.mean_incoming_eV - I,
            "dlog": rate.dlogK_dT_per_K, "dK": rate.dK_dT_cm3_s_K}


def independent_gap(audit, temperature, p, q, amplitude, name):
    """QAWS t^p weighting; no gamma function or production moment formula."""
    theta = KB * temperature
    z = DELTA / theta

    def smooth(t, moment):
        energy = I + DELTA * t
        base = energy * (E0 / energy) ** q * math.exp(-z * t)
        return base if moment == 0 else base * (energy if moment == 1 else DELTA * t)

    integrals, estimates, nevals = [], [], []
    for moment in range(3):
        output = quad(lambda t: smooth(t, moment), 0.0, 1.0,
                      weight="alg", wvar=(p, 0.0), epsabs=1e-15,
                      epsrel=2e-13, limit=128, full_output=1)
        audit.callbacks["independent_QAWS_integrals"] += 1
        value, estimate, info = output[:3]
        audit.check(len(output) == 3 and value > 0.0,
                    "quadrature_status", f"{name}:{moment}",
                    None if len(output) == 3 else str(output[3]))
        audit.metric(estimate / value, GATE_QUAD,
                     "quad_reported_relative_error", f"{name}:{moment}")
        integrals.append(value)
        estimates.append(estimate / value)
        nevals.append(int(info["neval"]))
    flux, moment2, excess_moment = integrals
    # Independent physical prefactor and direct positive integral, not F_j.
    logK = math.log(C * amplitude * DELTA * flux / theta**1.5) - I / theta
    K = math.exp(logK)
    mean = moment2 / flux
    excess = excess_moment / flux
    dlog = (mean / theta - 1.5) / temperature
    return {"K": K, "logK": logK, "mean": mean, "excess": excess,
            "dlog": dlog, "dK": K * dlog,
            "quadrature_relative_error_estimates": estimates,
            "quadrature_function_evaluations": nevals}


def independent_total(baseline, gap, temperature):
    # Direct rates and raw reaction moments are safe throughout the frozen domain.
    K = baseline.K_cm3_s + gap["K"]
    mean = (baseline.K_cm3_s * baseline.mean_incoming_eV + gap["K"] * gap["mean"]) / K
    excess = (baseline.K_cm3_s * baseline.mean_excess_over_chemical_eV +
              gap["K"] * gap["excess"]) / K
    dlog = (mean / (KB * temperature) - 1.5) / temperature
    return {"K": K, "logK": math.log(K), "mean": mean, "excess": excess,
            "dlog": dlog, "dK": K * dlog}


def decimal_probability(hazard):
    """Independent high-precision expm1 for tiny hazards without cancellation."""
    if hazard == 0:
        return Decimal(0)
    if hazard >= Decimal("0.1"):
        return Decimal(1) - (-hazard).exp()
    term = hazard
    total = term
    for n in range(2, 256):
        term *= -hazard / Decimal(n)
        updated = total + term
        if updated == total:
            return total
        total = updated
    raise ArithmeticError("REFERENCE_PROBABILITY_SERIES_NOT_CONVERGED")


def verify_sources(audit):
    contract = json.loads((ROOT / "CONTRACT.json").read_text())
    audit.check(tuple(contract["verification_gates"]["verification_T_K"]) == FROZEN_T,
                "source_contract", "frozen_verification_temperatures")
    for key, expected in (("independent_gamma_free_quad_relative", GATE_QUAD),
                          ("PL_identity_relative", GATE_PL),
                          ("finite_difference_scaled_relative", GATE_FD)):
        audit.check(contract["verification_gates"][key] == expected,
                    "source_contract", key)
    audit.check(gapmod.ICHEMICAL_EV == I and gapmod.E0_EV == E0 and
                gapmod.SIGMA0_CM2 == SIGMA0 and gapmod.P_W == P_W and
                gapmod.KB_EV_K == KB and gapmod.MAXWELL_CM3_S_PER_CM2 == C,
                "source_contract", "independently_bound_constants")
    physical = contract["physical_contract"]
    audit.check(physical["HH_R10"] == "OFF" and physical["production_admission"] == "NOT_ISSUED"
                and physical["coupled_feedback_error_bound"] is False
                and physical["gas_anisotropic_stress"] == 0,
                "source_contract", "locked_physical_scope")
    for relative, expected in runner.PINNED_INPUTS.items():
        audit.check(sha(ROOT / relative) == expected, "byte_identity", relative)
    reuse = json.loads((ROOT / "source/vendor/REUSE.json").read_text())
    for item in reuse["files"]:
        path = ROOT / item["new_path"]
        audit.check(sha(path) == item["SHA256"] and path.stat().st_size == item["bytes"]
                    and item["relation"] == "BYTE_IDENTITY"
                    and item["science_reexecuted"] is False,
                    "byte_identity", "reuse:" + item["new_path"])
    profile, saved = runner.load_saved_li_rows(ROOT)
    expected_saved = (255.0, 300.0, 1000.0, 3000.0, 10000.0, 20000.0,
                      25370.66308424773, 35000.0, 50000.0)
    audit.check(tuple(sorted(saved)) == expected_saved, "saved_provenance", "nine_saved_rows")
    audit.check(profile["identity"]["files"]["source/finite_ci.py"] ==
                sha(ROOT / "source/vendor/phys81/finite_ci.py"),
                "saved_provenance", "parent_operator_hash")
    calls = []
    with patch.object(FiniteWindowCI, "evaluate", side_effect=lambda *a, **k: calls.append(1)):
        for temperature, row in saved.items():
            copied = runner.saved_baseline_rate(row, profile["science_id"])
            audit.callbacks["saved_baseline_provenance_copies"] += 1
            audit.check(copied.K_cm3_s == row["finite_K_cm3_s"]
                        and copied.mean_incoming_eV == row["finite_mean_incoming_eV"]
                        and copied.mean_excess_over_chemical_eV == row["finite_mean_excess_over_chemical_eV"]
                        and copied.dlogK_dT_per_K == row["finite_dlogK_dT_per_K"]
                        and copied.float64_underflow == row["finite_underflow"]
                        and copied.temperature_K == temperature
                        and copied.source_identity == "PHYS81_SAVED:" + profile["science_id"],
                        "saved_provenance", f"saved_copy:{temperature}")
    audit.check(not calls, "saved_provenance", "saved_copy_invokes_no_old_evaluation")
    with (ROOT / "source_data/PHYS81_LITERAL.csv").open(newline="") as stream:
        li_rows = [r for r in csv.DictReader(stream) if r["project_nuclide_label"] == "Li7"]
    baseline = runner.load_baseline_model(ROOT)
    audit.check(len(li_rows) == 13 and len(baseline.energy_eV) == 13,
                "source_join", "thirteen_original_knots")
    for index, row in enumerate(li_rows):
        audit.check(baseline.energy_eV[index] == float(row["incident_energy_eV_literal"])
                    and baseline.sigma_cm2[index] == float(row["cross_section_literal"]),
                    "source_join", f"unchanged_knot:{index}")
    audit.records["parent_saved_science_id"] = profile["science_id"]
    audit.records["verification_center_baseline_origins"] = {
        str(t): "PHYS81_SAVED" if t in saved else "NEW_VERIFICATION_TEMPERATURE"
        for t in FROZEN_T}
    return profile, saved, baseline


def verify_numeric(audit, profile, saved, baseline_model, models):
    baseline_cache, gap_cache, total_cache, references = {}, {}, {}, {}

    def baseline_at(t):
        if t not in baseline_cache:
            if t in saved:
                baseline_cache[t] = runner.saved_baseline_rate(saved[t], profile["science_id"])
                audit.callbacks["verification_center_saved_baseline_copies"] += 1
            else:
                baseline_cache[t] = gapmod.from_finite_rate(baseline_model.evaluate(t))
                audit.callbacks["new_unchanged_baseline_evaluations"] += 1
        return baseline_cache[t]

    def gap_at(name, t):
        key = (name, t)
        if key not in gap_cache:
            gap_cache[key] = models[name].evaluate(t)
            audit.callbacks["new_gap_evaluations"] += 1
        return gap_cache[key]

    def total_at(name, t):
        key = (name, t)
        if key not in total_cache:
            total_cache[key] = gapmod.combine_rates(baseline_at(t), gap_at(name, t))
            audit.callbacks["new_total_combinations"] += 1
        return total_cache[key]

    rows = []
    for temperature in FROZEN_T:
        baseline = baseline_at(temperature)
        for name, (p, q, amplitude) in REFERENCE.items():
            label = f"{name}@{temperature:.17g}K"
            reference = independent_gap(audit, temperature, p, q, amplitude, label)
            references[name, temperature] = reference
            gap, total = gap_at(name, temperature), total_at(name, temperature)
            eg = compare_rate(audit, gap, reference, "gap_quad", label, GATE_QUAD)
            et = compare_rate(audit, total, independent_total(baseline, reference, temperature),
                              "total_reference", label, GATE_QUAD)
            audit.check(I < gap.mean_incoming_eV < E0 < baseline.mean_incoming_eV < 15.0
                        and gap.mean_incoming_eV < total.mean_incoming_eV < baseline.mean_incoming_eV
                        and 0.0 < total.gap_fraction < 1.0
                        and total.K_cm3_s > max(gap.K_cm3_s, baseline.K_cm3_s),
                        "positivity_support", label)
            audit.check(gap.dlogK_dT_per_K < total.dlogK_dT_per_K < baseline.dlogK_dT_per_K,
                        "temperature_derivative_order", label)
            audit.check(gap.thermal_loss_per_event_eV == I and total.thermal_loss_per_event_eV == I,
                        "chemical_sink", label)
            rows.append({"T_K": temperature, "model": name, "reference": reference,
                         "gap_errors": eg, "total_errors": et})
    audit.records["independent_numerical_rows"] = rows

    # These are new p=1 operators, not repeated nine-temperature baseline tests.
    gap_pl = FiniteWindowCI("Li7", np.array([I, E0]), np.array([0.0, SIGMA0]),
                            "PHYS82_NEW_SINGLE_CELL_IDENTITY", I, I, E0)
    joined_pl = FiniteWindowCI("Li7", np.r_[I, baseline_model.energy_eV],
                               np.r_[0.0, baseline_model.sigma_cm2],
                               "PHYS82_NEW_14_KNOT_IDENTITY", I, I, 15.0)
    for temperature in FROZEN_T:
        ref_gap = gap_pl.evaluate(temperature)
        ref_total = joined_pl.evaluate(temperature)
        audit.callbacks["new_single_cell_PL_evaluations"] += 1
        audit.callbacks["new_joined_PL_evaluations"] += 1
        compare_rate(audit, gap_at("L0", temperature), rate_dict(ref_gap),
                     "p1q0_gap_PL", str(temperature), GATE_PL)
        compare_rate(audit, total_at("L0", temperature), rate_dict(ref_total),
                     "p1q0_joined_PL", str(temperature), GATE_PL)

    stencils = []
    for temperature in FROZEN_T:
        h = temperature * 5e-5
        if temperature == FROZEN_T[0]:
            offsets, weights = (0, 1, 2, 3, 4), (-25, 48, -36, 16, -3)
        elif temperature == FROZEN_T[-1]:
            offsets, weights = (0, -1, -2, -3, -4), (25, -48, 36, -16, 3)
        else:
            offsets, weights = (-2, -1, 0, 1, 2), (1, -8, 0, 8, -1)
        nodes = [temperature + offset * h for offset in offsets]
        audit.check(all(255.0 <= t <= 50000.0 for t in nodes), "FD_domain", str(temperature))
        audit.check(all(t == temperature or t not in runner.SAVED_TEMPERATURES for t in nodes),
                    "FD_domain", f"no_old_temperature_offsets:{temperature}")
        stencils.append({"center_T_K": temperature, "h_K": h, "nodes_T_K": nodes,
                         "weights_over_12h": list(weights), "order": 4})
        for name in models:
            for component, getter in (("gap", gap_at), ("total", total_at)):
                center = getter(name, temperature)
                values = [getter(name, t) for t in nodes]
                dlog_fd = math.fsum(w * v.logK_cm3_s for w, v in zip(weights, values)) / (12.0 * h)
                # Normalization avoids tiny K values while retaining a direct K difference.
                dK_over_K_fd = math.fsum(w * (v.K_cm3_s / center.K_cm3_s)
                                       for w, v in zip(weights, values)) / (12.0 * h)
                scale = max(abs(center.dlogK_dT_per_K), 1.0 / temperature)
                label = f"{component}:{name}@{temperature:.17g}K"
                audit.metric(abs(dlog_fd - center.dlogK_dT_per_K) / scale,
                             GATE_FD, "FD_logK_scaled_relative", label)
                audit.metric(abs(dK_over_K_fd - center.dK_dT_cm3_s_K / center.K_cm3_s) / scale,
                             GATE_FD, "FD_K_scaled_relative", label)
    audit.records["finite_difference_stencils"] = stencils

    for temperature in FROZEN_T:
        gs = {name: gap_at(name, temperature) for name in models}
        ts = {name: total_at(name, temperature) for name in models}
        for name in gapmod.MATCHED_MODEL_NAMES:
            audit.check(gs["W0"].K_cm3_s <= gs[name].K_cm3_s <= gs["L1"].K_cm3_s
                        and ts["W0"].K_cm3_s <= ts[name].K_cm3_s <= ts["L1"].K_cm3_s
                        and ts["L1"].mean_incoming_eV <= ts[name].mean_incoming_eV <= ts["W0"].mean_incoming_eV,
                        "pq_rectangle", f"{name}@{temperature}")
        middle = independent_gap(audit, temperature, (1.0 + P_W) / 2.0, 0.5, SIGMA0,
                                 f"INTERIOR_REFERENCE_ONLY@{temperature}")
        audit.check(gs["W0"].K_cm3_s < middle["K"] < gs["L1"].K_cm3_s,
                    "pq_rectangle", f"independent_interior@{temperature}")
        for zero, one in (("L0", "L1"), ("W0", "W1")):
            rg = gs[one].K_cm3_s / gs[zero].K_cm3_s
            rt = ts[one].K_cm3_s / ts[zero].K_cm3_s
            audit.check(1.0 < rg < E0 / I and
                        1.0 < rt < 1.0 + ts[zero].gap_fraction * (E0 / I - 1.0),
                        "q_ratio", f"{zero}/{one}@{temperature}")
        ratio = REFERENCE["ZA1969"][2] / SIGMA0
        audit.metric(rel(gs["ZA1969"].K_cm3_s / gs["L0"].K_cm3_s, ratio),
                     GATE_QUAD, "ZA_independent_amplitude_rate_ratio", str(temperature))
        audit.check(gs["ZA1969"].mean_incoming_eV == gs["L0"].mean_incoming_eV
                    and gs["ZA1969"].dlogK_dT_per_K == gs["L0"].dlogK_dT_per_K,
                    "ZA_shape_identity", str(temperature))
        for p in (1.0, P_W):
            z = DELTA / (KB * temperature)
            f0, f1, f2 = map(math.exp, gapmod.scaled_log_moments(p, z))
            audit.callbacks["explicit_scaled_moment_evaluations"] += 1
            audit.check(0.0 < f2 < f1 < f0 and f1 * f1 <= f0 * f2,
                        "scaled_moment_properties", f"order:{p}:{temperature}")
            for j, value in enumerate((f0, f1, f2)):
                audit.check(math.exp(-z) / (p + j + 1.0) <= value <= 1.0 / (p + j + 1.0),
                            "scaled_moment_properties", f"bounds:{p}:{temperature}:{j}")

    exposure_records = []
    for temperature in FROZEN_T:
        baseline = baseline_at(temperature)
        for name in models:
            gap = gap_at(name, temperature)
            for exposure in EXPOSURES:
                actual = gapmod.fixed_exposure(baseline, gap, exposure)
                audit.callbacks["fixed_exposure_evaluations"] += 1
                with localcontext() as context:
                    context.prec = 80
                    hb = Decimal.from_float(baseline.K_cm3_s) * Decimal.from_float(exposure)
                    hg = Decimal.from_float(gap.K_cm3_s) * Decimal.from_float(exposure)
                    pb, pg, pt = (decimal_probability(x) for x in (hb, hg, hb + hg))
                    survival = (-hb).exp()
                    delta = survival * pg
                    bound = survival * min(Decimal(1), hg)
                    reference_values = {
                        "baseline_probability": float(pb), "gap_alone_probability": float(pg),
                        "total_probability": float(pt), "delta_probability": float(delta),
                        "delta_probability_upper_bound": float(bound),
                        "delta_probability_unattenuated_upper_bound": float(min(Decimal(1), hg)),
                    }
                label = f"{name}@{temperature}:Lambda={exposure:.0e}"
                errors = {}
                for field, expected in reference_values.items():
                    value = getattr(actual, field)
                    # Relative where representable; underflow uses absolute error.
                    error = rel(value, expected) if expected > sys.float_info.min else abs(value - expected)
                    errors[field] = error
                    audit.metric(error, GATE_QUAD, "exposure_" + field, label)
                audit.check(0.0 <= actual.delta_probability <= actual.delta_probability_upper_bound
                            <= actual.delta_probability_unattenuated_upper_bound <= 1.0
                            and actual.baseline_probability <= actual.total_probability <= 1.0
                            and actual.prescribed_T_ne_only and not actual.coupled_feedback_error_bound,
                            "exposure_bounds", label)
                audit.metric(abs(actual.total_probability - actual.baseline_probability - actual.delta_probability),
                             2e-15, "exposure_probability_difference_absolute", label)
                exposure_records.append({"T_K": temperature, "model": name, "exposure": exposure,
                                         "errors": errors})
            zero = gapmod.fixed_exposure(baseline, gap, 0.0)
            audit.callbacks["zero_exposure_evaluations"] += 1
            audit.check(zero.total_probability == zero.delta_probability == zero.delta_probability_upper_bound == 0.0
                        and zero.delta_probability_float64_underflow is False,
                        "exposure_zero", f"{name}@{temperature}")
    audit.records["exposure_rows"] = exposure_records
    audit.records["new_baseline_temperatures_K"] = sorted(t for t in baseline_cache if t not in saved)
    audit.records["gap_evaluation_temperatures_K"] = sorted({t for _, t in gap_cache})
    return baseline_at(FROZEN_T[0]), gap_at("L0", FROZEN_T[0])


def verify_guards_and_join(audit, models, baseline, gap):
    points = np.array([0.0, I, I + DELTA * 1e-6, I + DELTA * 0.01,
                       I + DELTA * 0.1, I + DELTA * 0.5,
                       I + DELTA * 0.9, E0, np.nextafter(E0, math.inf), 15.0])
    cross_sections = {}
    for name, model in models.items():
        values = model.cross_section(points)
        audit.callbacks["cross_section_vector_evaluations"] += 1
        cross_sections[name] = values
        p, q, amplitude = REFERENCE[name]
        expected = np.array([amplitude * ((e - I) / DELTA)**p * (E0 / e)**q
                             if I < e <= E0 else 0.0 for e in points])
        audit.check(np.allclose(values, expected, rtol=2e-15, atol=0.0) and values[1] == 0.0
                    and values[7] == amplitude and np.all(values[2:8] > 0),
                    "source_join", "support_and_endpoint:" + name)
        audit.check(model.cross_section(E0) == amplitude, "source_join", "scalar_endpoint:" + name)
        audit.callbacks["cross_section_scalar_evaluations"] += 1
        coverage = model.coverage()
        audit.check(coverage["matched_CCC_endpoint"] is (name != "ZA1969")
                    and coverage["full_physical_rate_available"] is False
                    and coverage["model_envelope_is_physical_confidence_interval"] is False
                    and coverage["coupled_feedback_error_bound"] is False
                    and coverage["thermal_loss_per_event_eV"] == I,
                    "source_contract", "coverage:" + name)
        audit.reject(lambda v=values: v.__setitem__(0, 1.0), "cross_array_write:" + name,
                     exceptions=(ValueError,), category="immutability")
        audit.reject(lambda v=values: v.setflags(write=True), "cross_array_flags:" + name,
                     exceptions=(ValueError,), category="immutability")
        audit.reject(lambda m=model: setattr(m, "p", 9.0), "frozen_model:" + name,
                     exceptions=(FrozenInstanceError, AttributeError), category="immutability")
    for name in gapmod.MATCHED_MODEL_NAMES:
        audit.check(np.all(cross_sections["W0"] <= cross_sections[name])
                    and np.all(cross_sections[name] <= cross_sections["L1"]),
                    "pq_rectangle", "pointwise:" + name)
    audit.check(models["ZA1969"].amplitude_cm2 != SIGMA0
                and not models["ZA1969"].matched_CCC_endpoint
                and tuple(models) == tuple(REFERENCE), "source_join", "ZA_separate_amplitude")
    audit.reject(lambda: models.__setitem__("L0", None), "readonly_model_mapping",
                 exceptions=(TypeError, AttributeError), category="immutability")
    audit.reject(lambda: setattr(gap, "K_cm3_s", 0.0), "frozen_rate",
                 exceptions=(FrozenInstanceError, AttributeError), category="immutability")
    for bad in (True, False, "255", None, math.nan, math.inf, -1.0, 0.0, 254.99, 50000.01):
        audit.reject(lambda b=bad: models["L0"].evaluate(b), "temperature:" + repr(b))
    for bad in (True, "6", None, math.nan, math.inf, -0.1, [], [[6.0]], [True, 6.0], [5.8, math.nan]):
        audit.reject(lambda b=bad: models["L0"].cross_section(b), "energy:" + repr(b))
    for bad in (True, "1", None, math.nan, math.inf, -1.0):
        audit.reject(lambda b=bad: gapmod.fixed_exposure(baseline, gap, b), "exposure:" + repr(b))
    for flag in (True, 0, 1, "false", None):
        audit.reject(lambda b=flag: models["L0"].evaluate(255.0, full_physical_rate=b),
                     "full_flag_evaluate:" + repr(flag))
        audit.reject(lambda b=flag: models["L0"].cross_section(5.8, full_physical_rate=b),
                     "full_flag_cross_section:" + repr(flag))
        audit.reject(lambda b=flag: gapmod.combine_rates(baseline, gap, full_physical_rate=b),
                     "full_flag_combine:" + repr(flag))
        audit.reject(lambda b=flag: gapmod.fixed_exposure(baseline, gap, 1.0, full_physical_rate=b),
                     "full_flag_exposure:" + repr(flag))
    for kwargs in ({"p": True}, {"q": False}, {"p": 0.9}, {"p": P_W + 0.01},
                   {"q": 0.5}, {"amplitude_cm2": 0.0}, {"amplitude_cm2": SIGMA0 * 1.01},
                   {"Ichemical_eV": I + 0.01}, {"E0_eV": 6.1}, {"name": "UNKNOWN"},
                   {"matched_CCC_endpoint": False}, {"source_identity": " x"}):
        audit.reject(lambda k=kwargs: replace(models["L0"], **k), "model_contract:" + repr(kwargs))
    for p, z in ((True, 1.0), (0.9, 1.0), (P_W + 0.01, 1.0), (1.0, -1.0),
                 (1.0, math.nan), (1.0, True), ("1", 1.0)):
        audit.reject(lambda a=p, b=z: gapmod.scaled_log_moments(a, b), "moment_guard:" + repr((p, z)))
    for kwargs in ({"temperature_K": True}, {"K_cm3_s": -1.0}, {"logK_cm3_s": math.nan},
                   {"mean_incoming_eV": 0.0}, {"mean_excess_over_chemical_eV": -1.0},
                   {"gap_fraction": 0.5}, {"finite_window_only": False},
                   {"full_physical_rate_available": True}, {"species": "H1"},
                   {"float64_underflow": True}, {"derivative_float64_underflow": True}):
        audit.reject(lambda k=kwargs: replace(gap, **k), "rate_guard:" + repr(kwargs))
    audit.reject(lambda: gapmod.combine_rates(gap, baseline), "swapped_pair")
    audit.reject(lambda: gapmod.combine_rates(baseline, replace(gap, temperature_K=256.0)),
                 "mismatched_temperature")
    audit.reject(lambda: gapmod.combine_rates(asdict(baseline), gap), "mutable_dict_rate_pair")
    audit.reject(lambda: gapmod.fixed_exposure(gap, baseline, 1.0), "swapped_exposure_pair")
    # The explicit z=0 removable limit and derivative underflow helper are algebraic guards.
    for p in (1.0, P_W):
        values = gapmod.scaled_log_moments(p, 0.0)
        audit.check(all(abs(math.exp(v) * (p + j + 1.0) - 1.0) <= 2e-15
                        for j, v in enumerate(values)), "algebraic_limits", f"z0:{p}")
    k, dk = gapmod._rate_and_derivative(-750.0, 1e10)
    audit.check(k == 0.0 and dk > 0.0 and math.isfinite(dk), "algebraic_limits", "derivative_survives_rate_underflow")


def synthetic_result(identity, saved, profile):
    """Shape-valid artificial output; never scientific evidence or production output."""
    baseline_rows, rate_rows, exposure_rows, family_rows = [], [], [], []

    def blob(t, component, model, K, mean, fraction, source):
        dlog = (mean / (KB * t) - 1.5) / t
        logK = math.log(K)
        lower, upper = {"baseline": (6.0, 15.0), "gap": (I, 6.0), "total": (I, 15.0)}[component]
        return {"temperature_K": t, "K_cm3_s": K, "logK_cm3_s": logK,
                "mean_incoming_eV": mean, "mean_excess_over_chemical_eV": mean - I,
                "dK_dT_cm3_s_K": K * dlog, "dlogK_dT_per_K": dlog,
                "float64_underflow": False, "derivative_float64_underflow": False,
                "model": model, "component": component, "source_identity": source,
                "Ichemical_eV": I, "lower_eV": lower, "upper_eV": upper,
                "gap_fraction": fraction, "species": "Li7", "finite_window_only": True,
                "full_physical_rate_available": False,
                "log10K_cm3_s": logK / math.log(10.0), "thermal_loss_per_event_eV": I}

    for t in identity["temperatures_K"]:
        if t in saved:
            rate = runner._rate_blob(runner.saved_baseline_rate(saved[t], profile["science_id"]))
            origin, original = "PHYS81_SAVED", saved[t]
        else:
            rate = blob(t, "baseline", "CCC_6_15", 1e-9, 8.0, 0.0, "SYNTHETIC_FIXTURE")
            origin, original = "NEW_UNCHANGED_FINITE_OPERATOR", None
        baseline_rows.append({"T_K": t, "origin": origin, "rate": rate, "parent_saved_row": original})
        totals = {}
        for name in REFERENCE:
            kg = 0.25 * rate["K_cm3_s"]
            gap = blob(t, "gap", name, kg, 5.7, 1.0, "SYNTHETIC_FIXTURE")
            total = blob(t, "total", name, rate["K_cm3_s"] + kg,
                         0.8 * rate["mean_incoming_eV"] + 0.2 * 5.7, 0.2, "SYNTHETIC_FIXTURE")
            totals[name] = total
            rate_rows.append({"T_K": t, "model": name, "matched_CCC_family_member": name != "ZA1969",
                              "gap": gap, "total": total, "gap_fraction": 0.2,
                              "total_over_baseline": 1.25, "log_total_over_baseline": math.log(1.25)})
            for exposure in EXPOSURES:
                hb, hg = rate["K_cm3_s"] * exposure, kg * exposure
                survival = math.exp(-hb)
                exposure_rows.append({"T_K": t, "model": name, "exposure_cm3_inverse_s": exposure,
                                      "prescribed_T_ne_only": True, "coupled_feedback_error_bound": False,
                                      "baseline_probability": -math.expm1(-hb),
                                      "gap_alone_probability": -math.expm1(-hg),
                                      "total_probability": -math.expm1(-(hb + hg)),
                                      "delta_probability": survival * -math.expm1(-hg),
                                      "delta_probability_upper_bound": survival * min(1.0, hg),
                                      "delta_probability_unattenuated_upper_bound": min(1.0, hg)})
        family_rows.append({"T_K": t, "lower_rate_model": "W0", "upper_rate_model": "L1",
                            "lower_total_logK_cm3_s": totals["W0"]["logK_cm3_s"],
                            "upper_total_logK_cm3_s": totals["L1"]["logK_cm3_s"],
                            "is_physical_confidence_interval": False, "ZA1969_included": False})
    result = {"schema": runner.SCHEMA, "status": "COMPLETE_SCOPED",
              "fixture_class": "SYNTHETIC_CONTROL_FLOW_ONLY_NOT_SCIENTIFIC_EVIDENCE",
              "identity": identity, "science_id": runner._digest(identity),
              "counts": runner.EXPECTED_COUNTS, "models": runner._model_manifest(),
              "physical_contract": identity["physical_contract"], "baseline_rows": baseline_rows,
              "rate_rows": rate_rows, "exposure_rows": exposure_rows,
              "family_envelope_rows": family_rows}
    result["payload_sha256"] = runner._digest(result)
    return result


def make_fixture(path, identity, payload=None, *, output_present=True, complete=True, claim=True):
    path.mkdir(parents=True, exist_ok=False)
    output = path / "results/SYNTHETIC_CONTROL_FLOW_ONLY.json"
    science_id = runner._digest(identity)
    if claim:
        create_json(runner._claim_path(path, science_id), {
            "schema": "PHYS82_EXCLUSIVE_SCIENCE_ID_CLAIM_V1", "science_id": science_id,
            "output_relative_to_study": output.relative_to(path).as_posix()})
    identity_path, attempt_path, complete_path = runner._artifact_paths(output)
    create_json(identity_path, {"identity": identity, "science_id": science_id})
    create_json(attempt_path, {"science_id": science_id, "status": "STARTED"})
    if output_present:
        create_json(output, payload)
    if complete:
        create_json(complete_path, {"science_id": science_id, "status": "COMPLETE_SCOPED",
                                   "output_file_sha256": sha(output)})
    return output


def verify_runner(audit, profile, saved, fixture_dir):
    identity = runner.build_identity(ROOT)
    audit.check(len(identity["temperatures_K"]) == 72 and
                len(set(identity["temperatures_K"]) - set(saved)) == 63,
                "runner_design", "frozen_72_9_63_schedule")
    expected_counts = {"temperatures": 72, "saved_baseline_rows_reused": 9,
                       "new_baseline_evaluations": 63, "gap_evaluations": 360,
                       "combined_rate_rows": 360, "exposure_rows": 1080,
                       "matched_family_envelope_rows": 72,
                       "historical_completed_identity_reexecutions": 0, "ODE": 0, "benchmark": 0}
    audit.check(runner.EXPECTED_COUNTS == expected_counts, "runner_design", "production_design_counts")
    tree = ast.parse((ROOT / "source/run_study.py").read_text())
    run_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run_study")
    branch = next(n for n in ast.walk(run_node) if isinstance(n, ast.If)
                  and ast.unparse(n.test) == "temperature in saved_rows")
    body_calls = [ast.unparse(n.func) for n in ast.walk(ast.Module(body=branch.body, type_ignores=[]))
                  if isinstance(n, ast.Call)]
    else_calls = [ast.unparse(n.func) for n in ast.walk(ast.Module(body=branch.orelse, type_ignores=[]))
                  if isinstance(n, ast.Call)]
    audit.check("saved_baseline_rate" in body_calls and "baseline_model.evaluate" not in body_calls
                and "baseline_model.evaluate" in else_calls,
                "runner_design", "saved_branch_has_no_baseline_evaluation")
    for function_name in ("_resume", "validate_saved_output", "load_saved_li_rows"):
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == function_name)
        calls = [ast.unparse(n.func) for n in ast.walk(node) if isinstance(n, ast.Call)]
        audit.check(not any(call.endswith(".evaluate") or call in
                            ("combine_rates", "fixed_exposure", "named_models", "load_baseline_model")
                            for call in calls), "runner_design", "no_science_in:" + function_name)
    payload = synthetic_result(identity, saved, profile)
    complete_root = fixture_dir / "complete"
    complete_output = make_fixture(complete_root, identity, payload)
    incomplete_root = fixture_dir / "incomplete_claim"
    incomplete_output = make_fixture(incomplete_root, identity, output_present=False, complete=False)
    partial_root = fixture_dir / "partial_sidecar"
    partial_output = make_fixture(partial_root, identity, output_present=False, complete=False, claim=False)
    mismatched = copy.deepcopy(payload)
    mismatched["baseline_rows"][0]["origin"] = "NEW_UNCHANGED_FINITE_OPERATOR"
    mismatched["payload_sha256"] = runner._digest({k: v for k, v in mismatched.items() if k != "payload_sha256"})
    wrong_root = fixture_dir / "wrong_saved_origin"
    wrong_output = make_fixture(wrong_root, identity, mismatched)
    mutated = copy.deepcopy(payload)
    mutated["baseline_rows"][0]["parent_saved_row"]["finite_K_cm3_s"] *= 1.01
    mutated["payload_sha256"] = runner._digest({k: v for k, v in mutated.items() if k != "payload_sha256"})
    changed_root = fixture_dir / "changed_parent_row"
    changed_output = make_fixture(changed_root, identity, mutated)
    sentinels = Counter()

    def blocked(label):
        def fail(*args, **kwargs):
            sentinels[label] += 1
            raise AssertionError("SCIENTIFIC_CALLBACK_DURING_CONTROL_FLOW_CHECK:" + label)
        return fail

    with ExitStack() as stack:
        stack.enter_context(patch.object(runner, "build_identity", return_value=identity))
        stack.enter_context(patch.object(runner, "load_saved_li_rows", return_value=(profile, saved)))
        for target, attr in ((gapmod.ThresholdGap, "evaluate"), (FiniteWindowCI, "evaluate"),
                             (runner, "combine_rates"), (runner, "fixed_exposure"),
                             (runner, "named_models"), (runner, "load_baseline_model")):
            stack.enter_context(patch.object(target, attr, side_effect=blocked(attr)))
        skipped = runner.run_study(complete_root, complete_output)
        audit.callbacks["runner_no_science_skip_invocations"] += 1
        audit.check(skipped["status"] == "SKIPPED_IDENTICAL_COMPLETE" and
                    skipped["scientific_callbacks"] == 0,
                    "runner_no_replay", "same_output_skip")
        alternate = complete_root / "results/ALTERNATE_NAME.json"
        skipped_alt = runner.run_study(complete_root, alternate)
        audit.callbacks["runner_no_science_skip_invocations"] += 1
        audit.check(skipped_alt["status"] == "SKIPPED_IDENTICAL_COMPLETE" and
                    skipped_alt["output"] == str(complete_output) and not alternate.exists(),
                    "runner_no_replay", "renamed_output_does_not_replay")
        for label, root, output, errors in (
            ("incomplete_claim", incomplete_root, incomplete_output, (FileExistsError,)),
            ("partial_sidecars", partial_root, partial_output, (FileExistsError,)),
            ("wrong_old_origin", wrong_root, wrong_output, (ValueError,)),
            ("changed_old_row", changed_root, changed_output, (ValueError,)),
        ):
            audit.reject(lambda r=root, o=output: runner.run_study(r, o), label,
                         exceptions=errors, category="runner_no_replay")
            audit.callbacks["runner_no_science_rejection_invocations"] += 1
        audit.reject(lambda: runner.run_study(complete_root, fixture_dir / "OUTSIDE.json"),
                     "outside_results_output", category="runner_no_replay")
        audit.callbacks["runner_no_science_rejection_invocations"] += 1
    audit.check(not sentinels, "runner_no_replay", "zero_scientific_sentinel_callbacks", dict(sentinels))
    audit.records["runner_control_flow"] = {
        "fixture_class": "SYNTHETIC_CONTROL_FLOW_ONLY_NOT_SCIENTIFIC_EVIDENCE",
        "fixture_directory": str(fixture_dir), "scientific_callback_counts": dict(sentinels),
        "actual_production_run_study_scientific_calls": 0,
        "same_and_changed_output_skips": [skipped, skipped_alt],
    }
    for name, text in (("duplicate_keys.json", '{"x":1,"x":2}'),
                       ("nonfinite_json.json", '{"x":NaN}')):
        path = fixture_dir / name
        with path.open("x", encoding="utf-8") as handle:
            handle.write(text)
        audit.reject(lambda p=path: runner._read_json(p), "strict_json:" + name,
                     category="runner_design")
    create_only = fixture_dir / "create_only.json"
    runner._write_create(create_only, {"preserve": True})
    before = sha(create_only)
    audit.reject(lambda: runner._write_create(create_only, {"preserve": False}), "create_only_write",
                 exceptions=(FileExistsError,), category="runner_no_replay")
    audit.check(sha(create_only) == before, "runner_no_replay", "create_only_preserves_bytes")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fixtures", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    fixtures = args.fixtures.resolve()
    if not output.is_relative_to(ROOT / "verification"):
        raise ValueError("VERIFICATION_OUTPUT_MUST_BE_IN_UNIT_VERIFICATION")
    if not fixtures.is_relative_to(Path("/tmp/phys82_work_20261023/review")):
        raise ValueError("SYNTHETIC_FIXTURE_LOCATION_MUST_BE_REVIEW_DIRECTORY")
    attempt = Path(str(output) + ".attempt.json")
    if output.exists() or attempt.exists() or fixtures.exists():
        raise FileExistsError("VERIFICATION_IDENTITY_ALREADY_ATTEMPTED_INSPECT_NO_REPLAY")
    frozen_hashes = {name: sha(ROOT / name) for name in SCOPED_FILES}
    started = datetime.now(timezone.utc).isoformat()
    create_json(attempt, {"status": "STARTED", "started_utc": started,
                          "scoped_source_sha256": frozen_hashes,
                          "temperatures_K": FROZEN_T, "models": list(REFERENCE),
                          "fd_relative_step": 5e-5, "fd_order": 4,
                          "quad_method": "QUADPACK_QAWS_ALGEBRAIC_ENDPOINT_WEIGHT",
                          "gates": {"quadrature_relative": GATE_QUAD, "PL_relative": GATE_PL,
                                    "finite_difference_scaled_relative": GATE_FD},
                          "resource_budget": {"lease_GiB": 0.5, "threads": 1}})
    audit = Audit()
    error = None
    try:
        for env in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS"):
            audit.check(os.environ.get(env) == "1", "resources", env)
        profile, saved, baseline = verify_sources(audit)
        models = gapmod.named_models()
        base_rate, gap_rate = verify_numeric(audit, profile, saved, baseline, models)
        verify_guards_and_join(audit, models, base_rate, gap_rate)
        verify_runner(audit, profile, saved, fixtures)
    except Exception:
        error = traceback.format_exc()
        audit.failures.append({"category": "unexpected_exception", "traceback": error})
    final_hashes = {name: sha(ROOT / name) for name in SCOPED_FILES}
    audit.check(final_hashes == frozen_hashes, "byte_identity", "all_reviewed_sources_unchanged_during_pass")
    expected_callbacks = {"new_gap_evaluations": 150, "new_total_combinations": 150,
                          "new_unchanged_baseline_evaluations": 27,
                          "verification_center_saved_baseline_copies": 3,
                          "new_single_cell_PL_evaluations": 6,
                          "new_joined_PL_evaluations": 6,
                          "independent_QAWS_integrals": 108,
                          "fixed_exposure_evaluations": 90, "zero_exposure_evaluations": 30,
                          "saved_baseline_provenance_copies": 9,
                          "explicit_scaled_moment_evaluations": 12,
                          "cross_section_vector_evaluations": 5,
                          "cross_section_scalar_evaluations": 5,
                          "runner_no_science_skip_invocations": 2,
                          "runner_no_science_rejection_invocations": 5}
    audit.check(dict(audit.callbacks) == expected_callbacks, "callback_accounting", "observed_callback_counts",
                {"observed": dict(audit.callbacks), "expected": expected_callbacks})
    result = {
        "schema": "PHYS82_INDEPENDENT_VERIFICATION_V1",
        "status": "PASS_SCOPED" if not audit.failures else "FAIL_RETAINED_FOR_DIAGNOSIS",
        "started_utc": started, "completed_utc": datetime.now(timezone.utc).isoformat(),
        "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
        "scope": "New threshold-gap numerical operator and no-science saved-run controls",
        "counts": {"checks": sum(audit.checks.values()), "failures": len(audit.failures),
                   "checks_by_category": dict(audit.checks), "observed_callbacks": dict(audit.callbacks),
                   "historical_completed_identity_reexecutions": 0, "ODE": 0, "benchmark": 0,
                   "production_run_study_scientific_calls": 0, "recursive_reviewers": 0,
                   "remote_mutations": 0, "other_processes_terminated": 0},
        "error_maxima": audit.maxima, "source_sha256": frozen_hashes,
        "failures": audit.failures, "records": audit.records,
        "skill_context_used": {"name": "PhysMath Research Loop", "version": "1.3.0",
                               "sections": ["SKILL.md", "STAGE_SELECTION.md", "POLICY_INTEGRATION.md",
                                            "SUBAGENT_MODE.md", "CODING_LOOP.md:C6-C9"]},
        "claim_limits": {
            "quadrature_errors_are_continuum_certificates": False,
            "gap_coverage_physical": "OPEN", "tail_above_15_eV_physical": "OPEN",
            "model_envelope_is_physical_confidence_interval": False,
            "ZA1969_is_isotope_resolved_unsmeared_measurement": False,
            "coupled_feedback_error_bound": False, "strong_no_go_claimed": False,
            "HH_R10": "OFF", "production_admission": "NOT_ISSUED"},
    }
    create_json(output, result)
    print(json.dumps({"status": result["status"], "output": str(output),
                      "checks": result["counts"]["checks"], "failures": len(audit.failures),
                      "observed_callbacks": dict(audit.callbacks),
                      "error_maxima": audit.maxima}, indent=2))
    if error:
        print(error, file=sys.stderr)
    return 0 if not audit.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
