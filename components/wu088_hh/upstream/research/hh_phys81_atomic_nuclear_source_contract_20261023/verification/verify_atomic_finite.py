#!/usr/bin/env python3
"""Bounded independent PHYS81 checks, to be run by root under the shared lease.

This file is not a completed numerical result.  Compilation does not import
the reviewed modules.  The run evaluates the new finite-window wrapper, its
added moment/derivative paths, and pointwise parcel/Jacobian equations; it
calls the retained C22D provider only once, at the new parent maximum
temperature.  It runs no ODE and no old suite.

Independent quadrature uses the original literal PL data, linear slopes, and
an exponential scaled at each selected window floor.  It does not call the
implementation's J0/J1/J2/J3 moments.  Numerical checks certify these selected
binary64 evaluations, not physical cross-section completeness or accuracy.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
import hashlib
import importlib
import json
import math
from pathlib import Path
import resource
import sys
import time
import traceback


LOCAL_UNIT = Path(__file__).resolve().parents[1]
DEFAULT_UNIT = (LOCAL_UNIT if (LOCAL_UNIT / "source/finite_ci.py").is_file() else
                Path("/tmp/phys81_work_20261023/WU088_HH/research/hh_phys81_atomic_nuclear_source_contract_20261023"))
EV_J_REF = 1.602176634e-19
KB_J_K_REF = 1.380649e-23
KB_EV_K_REF = KB_J_K_REF / EV_J_REF
ME_KG_REF = 9.1093837139e-31
A0_M_REF = 5.29177210544e-11
C_REF = 100.0 * math.sqrt(8.0 * EV_J_REF / (math.pi * ME_KG_REF))
EXPECTED_VENDOR_CODE = "859cdf616ffa165c9fb3c3372d2202f5449e4b9a74a289a725fe456e26eb55b2"
EXPECTED_VENDOR_TABLE = "7a87a2c9f2116ee36c0786b379dac08e1f4d92a49504fe542e6aa71cbb279bae"
ACTUAL_PARENT_TMAX_K = 25370.66308424773


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def close(actual: float, expected: float, *, rtol=3e-11, atol=0.0, label="value") -> float:
    require(math.isfinite(actual) and math.isfinite(expected), f"{label}: nonfinite comparison")
    error = abs(actual - expected)
    require(error <= atol + rtol * abs(expected),
            f"{label}: actual={actual:.17g}, expected={expected:.17g}, error={error:.5g}")
    return error / max(abs(expected), 1e-300)


def close_vector(actual, expected, *, rtol=3e-11, atol=0.0, label="vector") -> float:
    require(len(actual) == len(expected), label + ": length mismatch")
    return max((close(float(a), float(b), rtol=rtol, atol=atol, label=f"{label}[{i}]")
                for i, (a, b) in enumerate(zip(actual, expected))), default=0.0)


def split_quad(function, upper: float, quad):
    """Integrate in local exponential coordinate without missing a thin layer."""
    points = [0.0] + [x for x in (1.0, 4.0, 16.0, 64.0, 256.0) if x < upper] + [upper]
    values, errors = [], []
    for left, right in zip(points[:-1], points[1:]):
        value, error = quad(function, left, right, epsabs=1e-14, epsrel=3e-13, limit=80)
        values.append(value)
        errors.append(error)
    return math.fsum(values), math.fsum(errors)


def reference_moments(energy, sigma, temperature: float, quad):
    """Window-floor-scaled M1/M2 by slope PL quadrature, in eV and cm^2."""
    theta = KB_EV_K_REF * temperature
    floor = float(energy[0])
    scale = max(float(x) for x in sigma)
    accum = {1: [], 2: []}
    errors = {1: [], 2: []}
    for i in range(len(energy) - 1):
        left, right = float(energy[i]), float(energy[i + 1])
        sl, sr = float(sigma[i]) / scale, float(sigma[i + 1]) / scale
        if sl == 0.0 and sr == 0.0:
            continue
        width = right - left
        weight = theta * math.exp(-(left - floor) / theta)
        if weight == 0.0:
            continue
        slope = (sr - sl) / width
        for power in (1, 2):
            def integrand(x, power=power):
                delta = theta * x
                return (left + delta)**power * (sl + slope * delta) * math.exp(-x)
            value, error = split_quad(integrand, width / theta, quad)
            accum[power].append(weight * value)
            errors[power].append(weight * error)
    first, second = math.fsum(accum[1]), math.fsum(accum[2])
    require(first > 0.0 and second > 0.0, "independent scaled moments must be positive")
    log_rate = math.log(C_REF) + math.log(scale) - 1.5 * math.log(theta) - floor / theta + math.log(first)
    mean = second / first
    dlog_rate = (mean / theta - 1.5) / temperature
    return {
        "logK_cm3_s": log_rate,
        "mean_incoming_eV": mean,
        "dlogK_dT_per_K": dlog_rate,
        "M1_scaled": first,
        "M2_scaled": second,
        "quadrature_error_M1_scaled": math.fsum(errors[1]),
        "quadrature_error_M2_scaled": math.fsum(errors[2]),
        "reference_floor_eV": floor,
        "sigma_scale_cm2": scale,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit", type=Path, default=DEFAULT_UNIT)
    parser.add_argument("--registry", type=Path, help="Defaults to the unit's active ADMITTED_FINITE_CI_REGISTRY.json")
    parser.add_argument("--literal", type=Path, help="Defaults to the unit's immutable literal CSV copy")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--only", action="append", default=[], metavar="CHECK_ID",
                        help="Run only named check group(s), for a diagnosed correction without replaying completed groups")
    args = parser.parse_args()
    if args.registry is None:
        args.registry = args.unit / "source_data/ADMITTED_FINITE_CI_REGISTRY.json"
    if args.literal is None:
        args.literal = args.unit / "source_data/PHYS81_CI_FINITE_WINDOW_LITERAL_DATA.csv"
    started = time.monotonic()
    report = {
        "schema": "PHYS81_INDEPENDENT_ATOMIC_VERIFIER_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "command_argv": sys.argv,
        "scope": "New finite PL wrapper, J3/mean/derivatives, seeded parcel pointwise lift/RHS/Jacobian and guards; no ODE",
        "old_science_suites_executed": 0,
        "vendor_rate_evaluations": 0,
        "selected_check_groups": args.only or "ALL_NEW_GROUPS",
        "source_identity": {},
        "checks": {},
        "physical_rate_admission": "NOT_ISSUED",
    }

    def check(name, function):
        if args.only and name not in args.only:
            report["checks"][name] = {"status": "NOT_RUN_SCOPED", "reason": "Excluded by explicit --only selection"}
            return
        try:
            details = function()
            report["checks"][name] = {"status": "PASS", "details": details}
        except Exception as exc:
            report["checks"][name] = {
                "status": "FAIL", "exception": type(exc).__name__, "message": str(exc),
                "traceback": traceback.format_exc(),
            }

    try:
        import numpy as np
        import scipy
        from scipy.integrate import quad

        report["environment"] = {"python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__}
        sys.path.insert(0, str(args.unit / "source"))
        ci = importlib.import_module("finite_ci")
        vendor = importlib.import_module("vendor.ci_finite_c22d")
        parcel_module = importlib.import_module("parcel")
        registry_module = importlib.import_module("registry")
        registry = json.loads(args.registry.read_text())
        with args.literal.open(newline="") as stream:
            literal = list(csv.DictReader(stream))
        for path in [args.unit / "CONTRACT.json", args.unit / "theory/ATOMIC_DERIVATION_KO.md",
                     args.unit / "source/finite_ci.py", args.unit / "source/vendor/ci_finite_c22d.py",
                     args.unit / "source/vendor/CCC_TICS_1S.txt", args.unit / "source/vendor/REUSE.json",
                     args.unit / "source/parcel.py", args.unit / "source/registry.py",
                     args.unit / "verification/LI7_SOURCE_CORRECTION.json",
                     args.registry, args.literal, Path(__file__)]:
            report["source_identity"][str(path)] = {"sha256": sha256(path), "bytes": path.stat().st_size}

        require(sha256(args.literal) == registry["literal_csv_sha256"], "literal CSV hash disagrees with registry")
        require(sha256(args.unit / "source/vendor/ci_finite_c22d.py") == EXPECTED_VENDOR_CODE, "vendor code identity changed")
        require(sha256(args.unit / "source/vendor/CCC_TICS_1S.txt") == EXPECTED_VENDOR_TABLE, "vendor table identity changed")
        require(registry["status"] == "ADMITTED_EXPLICIT_FINITE_MODEL_ONLY", "active finite-model admission required")
        curves = {row["project_label"]: row for row in registry["source_curves"]}
        models, originals = {}, {}
        for species in ("H1", "He4", "Li7"):
            selected = [row for row in literal if row["project_nuclide_label"] == species]
            curve = curves[species]
            energy = np.array([float(row["incident_energy_eV_literal"]) for row in selected])
            sigma = np.array([float(row["cross_section_literal"]) for row in selected])
            units = {row["cross_section_unit"] for row in selected}
            expected_hash = curve.get("raw_source_sha256", curve.get("raw_member_sha256", curve.get("raw_html_sha256")))
            require({row["raw_source_sha256"] for row in selected} == {expected_hash}, f"{species}: literal provenance mismatch")
            if species == "H1":
                require(units == {"a0^2"}, "H literal unit")
                sigma *= (100.0 * A0_M_REF)**2
                model = ci.FiniteWindowCI.from_c22d_hydrogen(Ichemical_eV=float(curve["chemical_I_eV"]))
            else:
                require(units == {"cm^2"}, f"{species}: literal unit")
                model = ci.FiniteWindowCI(
                    species=species, energy_eV=energy, sigma_cm2=sigma,
                    source_identity="sha256:" + expected_hash,
                    Ichemical_eV=float(curve["chemical_I_eV"]),
                    lower_eV=float(curve["allowed_window_eV"][0]),
                    upper_eV=float(curve["allowed_window_eV"][1]),
                )
            require(np.array_equal(model.energy_eV, energy), f"{species}: energy transcription mismatch")
            require(np.array_equal(model.sigma_cm2, sigma), f"{species}: sigma conversion/transcription mismatch")
            require((model.lower_eV, model.upper_eV) == tuple(map(float, curve["allowed_window_eV"])),
                    f"{species}: registry window mismatch")
            originals[species] = (energy, sigma)
            models[species] = model

        expected_models = dict(models)
        admitted = registry_module.load_rates()
        require(tuple(model.species for model in admitted) == ("H1", "He4", "Li7"), "active loader species order")
        models = {model.species: model for model in admitted}

        def check_active_loader():
            require(tuple(model.species for model in admitted) == ("H1", "He4", "Li7"), "active loader species order")
            rows = []
            for actual in admitted:
                expected = expected_models[actual.species]
                require(np.array_equal(actual.energy_eV, expected.energy_eV), "loader energy identity")
                require(np.array_equal(actual.sigma_cm2, expected.sigma_cm2), "loader sigma identity")
                require(actual.Ichemical_eV == expected.Ichemical_eV, "loader chemical defect identity")
                require((actual.lower_eV, actual.upper_eV) == (expected.lower_eV, expected.upper_eV), "loader window identity")
                require(registry["literal_csv_sha256"] in actual.source_identity, "loader source identity omits literal hash")
                require(curves[actual.species]["chemical_source_sha256"] in actual.source_identity,
                        "loader source identity omits chemical-source hash")
                rows.append({"species": actual.species, "chemical_I_eV": actual.Ichemical_eV,
                             "source_identity": actual.source_identity})
            return rows
        check("active_registry_loader_binding_and_Li7_propagation", check_active_loader)

        def check_source_chemistry():
            result = []
            for species, model in models.items():
                coverage = model.coverage()
                require(model.lower_eV > model.Ichemical_eV, f"{species}: expected distinct source floor and chemical I")
                require(coverage["full_physical_rate_available"] is False, "coverage full-rate flag")
                require(coverage["mean_incoming_energy_is_additional_heat_loss"] is False, "incoming energy counted twice")
                result.append({"species": species, "lower_eV": model.lower_eV, "Ichemical_eV": model.Ichemical_eV,
                               "gap_eV": model.lower_eV - model.Ichemical_eV})
            return result
        check("source_chemical_separation", check_source_chemistry)

        def check_new_moments():
            result = []
            for species, model in models.items():
                for temperature in (255.0, ACTUAL_PARENT_TMAX_K, 50000.0):
                    rate = model.evaluate(temperature)
                    reference = reference_moments(*originals[species], temperature, quad)
                    log_error = abs(rate.logK_cm3_s - reference["logK_cm3_s"])
                    require(log_error <= 4e-11, f"{species}/{temperature}: log K quadrature mismatch")
                    mean_error = close(rate.mean_incoming_eV, reference["mean_incoming_eV"], label="mean incoming E")
                    derivative_error = close(rate.dlogK_dT_per_K, reference["dlogK_dT_per_K"], atol=2e-14, label="d logK/dT")
                    if rate.K_cm3_s > 0.0:
                        close(rate.K_cm3_s, math.exp(reference["logK_cm3_s"]), label="K")
                    else:
                        require(rate.float64_underflow and math.exp(reference["logK_cm3_s"]) == 0.0, "underflow classification")
                    expected_dK = (0.0 if reference["dlogK_dT_per_K"] == 0.0 else
                                   math.copysign(math.exp(reference["logK_cm3_s"] + math.log(abs(reference["dlogK_dT_per_K"]))), reference["dlogK_dT_per_K"]))
                    close(rate.dK_dT_cm3_s_K, expected_dK, atol=5e-324, label="dK/dT")
                    result.append({"species": species, "T_K": temperature, "logK_abs_error": log_error,
                                   "mean_relative_error": mean_error, "dlog_relative_error": derivative_error,
                                   "underflow": bool(rate.float64_underflow), "reference": reference})
            return result
        check("new_M2_mean_and_derivative_quadrature", check_new_moments)

        def check_J3():
            points = np.array([0.0, 1e-12, 0.125, np.nextafter(0.5, 0.0), 0.5,
                               np.nextafter(0.5, 1.0), 1.0, 4.0, 16.0, 1000.0, 1e6])
            actual = ci._moment3(points)
            records = []
            for y, value in zip(points, actual):
                if y == 0.0:
                    reference, error, tail_bound = 0.25, 0.0, 0.0
                elif y <= 16.0:
                    reference, error = quad(lambda t: t**3 * math.exp(-float(y) * t), 0.0, 1.0,
                                            epsabs=1e-14, epsrel=3e-13)
                    tail_bound = 0.0
                else:
                    cap = min(float(y), 100.0)
                    integral, raw_error = split_quad(lambda u: u**3 * math.exp(-u), cap, quad)
                    reference, error = integral / y**4, raw_error / y**4
                    tail_bound = (0.0 if y <= cap else
                                  math.exp(-cap) * (cap**3 + 3 * cap**2 + 6 * cap + 6) / y**4)
                require(abs(float(value) - reference) <= 3e-12 * abs(reference) + 10 * error + tail_bound,
                        f"J3 independent quadrature mismatch at y={y}")
                records.append({"y": float(y), "actual": float(value), "reference": float(reference),
                                "absolute_error": abs(float(value) - reference), "reference_tail_bound": float(tail_bound)})
            return records
        check("new_J3_branch_and_scaled_large_argument", check_J3)

        def check_derivative_difference():
            rows = []
            temperature = ACTUAL_PARENT_TMAX_K
            step = 1e-4 * temperature
            for species, model in models.items():
                values = [model.evaluate(temperature + multiple * step).logK_cm3_s for multiple in (-2, -1, 1, 2)]
                finite_difference = (values[0] - 8 * values[1] + 8 * values[2] - values[3]) / (12 * step)
                analytic = model.evaluate(temperature).dlogK_dT_per_K
                error = close(analytic, finite_difference, rtol=3e-8, atol=2e-12, label="five-point log derivative")
                rows.append({"species": species, "T_K": temperature, "step_K": step,
                             "analytic": analytic, "five_point": finite_difference, "relative_error": error})
            return rows
        check("new_log_derivative_five_point_difference", check_derivative_difference)

        def check_vendor_equivalence():
            original = vendor.CCCFiniteH1CI(args.unit / "source/vendor/CCC_TICS_1S.txt")
            reference = original.evaluate(ACTUAL_PARENT_TMAX_K)
            report["vendor_rate_evaluations"] += 1
            new = models["H1"].evaluate(ACTUAL_PARENT_TMAX_K)
            error = close(new.K_cm3_s, reference.q_cm3_s, rtol=5e-13, label="new-temperature H vendor equivalence")
            close(new.log10K_cm3_s, reference.log10_q_cm3_s, rtol=0.0, atol=2e-13, label="log10 H vendor equivalence")
            return {"T_K": ACTUAL_PARENT_TMAX_K, "new_K": new.K_cm3_s, "retained_K": reference.q_cm3_s,
                    "relative_error": error, "retained_provider_calls": 1,
                    "purpose": "New wrapper unit conversion and newly needed parent Tmax; no retained science suite replay"}
        check("retained_H_single_new_temperature_equivalence", check_vendor_equivalence)

        def check_synthetic_paths():
            records = []
            for label, energy, sigma, temperature in [
                ("zero_prefix", [1.0, 2.0, 3.0, 4.0], [0.0, 0.0, 1e-16, 0.0], 255.0),
                ("negative_temperature_derivative", [1.0, 2.0], [1e-16, 1e-16], 50000.0),
            ]:
                model = ci.FiniteWindowCI(label, energy, sigma, "synthetic:" + label, 0.5, energy[0], energy[-1])
                value = model.evaluate(temperature)
                reference = reference_moments(energy, sigma, temperature, quad)
                close(value.logK_cm3_s, reference["logK_cm3_s"], rtol=0.0, atol=4e-11, label=label + " logK")
                close(value.mean_incoming_eV, reference["mean_incoming_eV"], label=label + " mean")
                if label == "negative_temperature_derivative":
                    require(value.dK_dT_cm3_s_K < 0.0, "negative derivative branch not reached")
                records.append({"case": label, "T_K": temperature, "logK": value.logK_cm3_s,
                                "mean_eV": value.mean_incoming_eV, "dK_dT": value.dK_dT_cm3_s_K})
            # Artificial cross-section scale isolates representability logic.
            # It has no physical-data interpretation and is labelled synthetic.
            helium = models["He4"]
            base = helium.evaluate(255.0)
            target_log = math.log(float(np.nextafter(0.0, 1.0))) - 1.0
            factor = math.exp(target_log - base.logK_cm3_s)
            synthetic = ci.FiniteWindowCI("synthetic", helium.energy_eV, helium.sigma_cm2 * factor,
                                         "synthetic:underflow_derivative", helium.Ichemical_eV,
                                         helium.lower_eV, helium.upper_eV)
            value = synthetic.evaluate(255.0)
            require(value.K_cm3_s == 0.0 and value.float64_underflow, "synthetic rate underflow not reached")
            require(value.dK_dT_cm3_s_K > 0.0, "representable derivative lost when rate underflows")
            records.append({"case": "rate_underflow_with_representable_derivative", "logK": value.logK_cm3_s,
                            "K": value.K_cm3_s, "dK_dT": value.dK_dT_cm3_s_K})
            return records
        check("new_generic_zero_prefix_signed_derivative_and_underflow", check_synthetic_paths)

        def check_guards():
            template = dict(species="synthetic", energy_eV=[1.0, 2.0], sigma_cm2=[1e-16, 2e-16],
                            source_identity="synthetic:guards", Ichemical_eV=0.5, lower_eV=1.0, upper_eV=2.0)
            cases = {
                "empty_species": {"species": ""}, "unstripped_species": {"species": " H1"},
                "empty_identity": {"source_identity": ""}, "one_point": {"energy_eV": [1.0]},
                "matrix": {"energy_eV": [[1.0, 2.0]]}, "boolean_energy": {"energy_eV": [True, 2.0]},
                "boolean_sigma": {"sigma_cm2": [True, 1e-16]}, "nan_energy": {"energy_eV": [1.0, math.nan]},
                "infinite_sigma": {"sigma_cm2": [1e-16, math.inf]}, "complex_energy": {"energy_eV": [1.0, 2.0 + 0j]},
                "string_energy": {"energy_eV": ["1.0", 2.0]}, "duplicate_energy": {"energy_eV": [1.0, 1.0], "upper_eV": 1.0},
                "descending_energy": {"energy_eV": [1.0, 0.5, 2.0], "sigma_cm2": [1e-16, 1e-16, 1e-16]},
                "shape_mismatch": {"sigma_cm2": [1e-16, 1e-16, 1e-16]}, "negative_sigma": {"sigma_cm2": [1e-16, -1e-16]},
                "all_zero_sigma": {"sigma_cm2": [0.0, 0.0]}, "chemical_above_floor": {"Ichemical_eV": 1.1},
                "chemical_zero": {"Ichemical_eV": 0.0}, "chemical_boolean": {"Ichemical_eV": True},
                "wrong_endpoint": {"lower_eV": 1.1}, "upper_nan": {"upper_eV": math.nan},
            }
            rejected = []
            for label, changed in cases.items():
                try:
                    ci.FiniteWindowCI(**(template | changed))
                except ValueError as exc:
                    rejected.append({"case": label, "exception": str(exc)})
                else:
                    raise AssertionError("constructor accepted invalid case " + label)
            model = ci.FiniteWindowCI(**template)
            temperatures = {"bool": True, "nan": math.nan, "inf": math.inf, "below": 254.999,
                            "above": 50000.001, "complex": 300.0 + 0j, "string": "300", "vector": np.array([300.0])}
            for label, value in temperatures.items():
                try:
                    model.evaluate(value)
                except ValueError as exc:
                    rejected.append({"case": "temperature_" + label, "exception": str(exc)})
                else:
                    raise AssertionError("accepted invalid temperature " + label)
            for label, flag in (("full_physical_rate_requested", True), ("nonbool_full_rate_flag", 1)):
                try:
                    model.evaluate(300.0, full_physical_rate=flag)
                except ValueError as exc:
                    rejected.append({"case": label, "exception": str(exc)})
                else:
                    raise AssertionError("accepted " + label)
            return rejected
        check("new_constructor_and_evaluation_domain_guards", check_guards)

        def check_immutable_contents():
            energy = np.array([1.0, 2.0])
            sigma = np.array([1e-16, 2e-16])
            model = ci.FiniteWindowCI("synthetic", energy, sigma, "synthetic:immutable", 0.5, 1.0, 2.0)
            energy[0], sigma[0] = 99.0, 99.0
            require(model.energy_eV[0] == 1.0 and model.sigma_cm2[0] == 1e-16, "caller aliases retained")
            checked = []
            for name in ("energy_eV", "sigma_cm2", "_left", "_width", "_sigma_l", "_sigma_r"):
                array = getattr(model, name)
                require(not array.flags.writeable, name + " writeable flag")
                try:
                    array[0] = 3.0
                except ValueError:
                    pass
                else:
                    raise AssertionError(name + " content mutable")
                try:
                    array.setflags(write=True)
                except ValueError:
                    pass
                else:
                    raise AssertionError(name + " writeable flag can be enabled")
                checked.append(name)
            try:
                model.lower_eV = 0.0
            except (FrozenInstanceError, AttributeError):
                pass
            else:
                raise AssertionError("frozen field reassignment accepted")
            return {"checked_arrays": checked, "caller_input_copy_isolation": True,
                    "scope": "Ordinary Python mutation and array data bytes; not an adversarial object-model sandbox"}
        check("new_immutable_array_contents_and_copy_isolation", check_immutable_contents)

        # Balanced abundances are an explicit synthetic conditioning input.
        # They make every species column resolvable by finite differences and
        # are not claimed to be cosmological or natural isotope abundances.
        rates = tuple(models[species] for species in ("H1", "He4", "Li7"))
        parcel_B = np.array([1.0, 0.2, 0.1])
        parcel_X0 = parcel_B * np.array([0.05, 0.03, 0.01])
        parcel_nref = 73.0
        parcel = parcel_module.HazardParcel(rates, parcel_B, parcel_X0, ACTUAL_PARENT_TMAX_K, parcel_nref)
        chemical = np.array([model.Ichemical_eV for model in rates])
        neutral0 = parcel_B - parcel_X0
        thermal_c = 1.5 * KB_EV_K_REF
        initial_particles = math.fsum(parcel_B) + math.fsum(parcel_X0)
        independent_u0 = thermal_c * ACTUAL_PARENT_TMAX_K * initial_particles

        def independent_lift(z):
            neutral = np.array([n0 * math.exp(-float(zi)) for n0, zi in zip(neutral0, z)])
            increment = np.array([n0 * (-math.expm1(-float(zi))) for n0, zi in zip(neutral0, z)])
            ions = parcel_X0 + increment
            electrons = math.fsum(ions)
            particles = math.fsum(parcel_B) + electrons
            chemical_increment = math.fsum(float(i * d) for i, d in zip(chemical, increment))
            energy = independent_u0 - chemical_increment
            return {"N": neutral, "X": ions, "dX": increment, "xe": electrons, "Ng": particles,
                    "u": energy, "T": energy / (thermal_c * particles), "dUchem": chemical_increment}

        def check_parcel_pointwise():
            close(parcel.u0, independent_u0, rtol=3e-15, label="parcel u0")
            close_vector(parcel.Ichemical_eV, chemical, rtol=0.0, atol=0.0, label="parcel chemical propagation")
            records = []
            for name, z in (("initial", np.zeros(3)),
                            ("tiny_positive_hazard", np.array([1e-18, 2e-18, 3e-18])),
                            ("interior", np.array([0.013, 0.021, 0.017]))):
                reference = independent_lift(z)
                actual = parcel.lift(z)
                for actual_key, reference_key in (("neutral_abundance", "N"), ("ion_abundance", "X"),
                                                  ("ion_increment", "dX")):
                    close_vector(actual[actual_key], reference[reference_key], rtol=3e-13, label=name + ":" + actual_key)
                for actual_key, reference_key in (("xe", "xe"), ("N_g", "Ng"), ("u", "u"), ("T", "T"),
                                                  ("chemical_energy_increment_eV_per_reference_H", "dUchem")):
                    close(float(actual[actual_key]), float(reference[reference_key]), rtol=3e-13,
                          label=name + ":" + actual_key)
                coefficients = np.array([model.evaluate(reference["T"]).K_cm3_s for model in rates])
                expected_hazard_rhs = parcel_nref * reference["xe"] * coefficients
                actual_hazard_rhs = parcel.rhs(0.0, z)
                close_vector(actual_hazard_rhs, expected_hazard_rhs, rtol=3e-12, label=name + ":hazard_rhs")
                w = np.concatenate((reference["N"] / parcel_B, reference["X"] / parcel_B,
                                    np.array([reference["u"] / independent_u0])))
                full_state = parcel.full_lift(w)
                close_vector(full_state["neutral_abundance"], reference["N"], rtol=3e-13, label=name + ":full_N")
                close_vector(full_state["ion_abundance"], reference["X"], rtol=3e-13, label=name + ":full_X")
                close(full_state["T"], reference["T"], rtol=3e-13, label=name + ":full_T")
                fraction_flux = reference["N"] / parcel_B * expected_hazard_rhs
                energy_rate = -math.fsum(float(i * n * dz) for i, n, dz in
                                        zip(chemical, reference["N"], expected_hazard_rhs)) / independent_u0
                pushforward = np.concatenate((-fraction_flux, fraction_flux, np.array([energy_rate])))
                full_rhs = parcel.full_rhs(0.0, w)
                rhs_error = close_vector(full_rhs, pushforward, rtol=4e-12, label=name + ":full_rhs_vs_pushforward")
                if name == "tiny_positive_hazard":
                    require(np.all(actual["ion_increment"] > 0.0), "tiny hazards lost their positive ion increments")
                    require(actual["chemical_energy_increment_eV_per_reference_H"] > 0.0,
                            "tiny chemical increment lost before energy subtraction")
                records.append({"case": name, "z": z.tolist(), "T_K": float(actual["T"]),
                                "xe": float(actual["xe"]), "full_rhs_max_relative_error": rhs_error,
                                "ion_increment": actual["ion_increment"].tolist()})
            return {"input_scope": "Balanced synthetic abundances for pointwise conditioning, real admitted finite rates",
                    "B": parcel_B.tolist(), "X0": parcel_X0.tolist(), "nref_cm3": parcel_nref,
                    "chemical_I_eV": chemical.tolist(), "cases": records}
        check("new_parcel_lift_and_original_equation_pushforward", check_parcel_pointwise)

        def check_parcel_jacobian():
            z = np.array([0.013, 0.021, 0.017])
            reference = independent_lift(z)
            analytic = parcel.jac(0.0, z)
            evaluations = [model.evaluate(reference["T"]) for model in rates]
            coefficients = np.array([value.K_cm3_s for value in evaluations])
            derivatives = np.array([value.dK_dT_cm3_s_K for value in evaluations])
            dTdz = -reference["N"] * (chemical + thermal_c * reference["T"]) / (thermal_c * reference["Ng"])
            chain_rule = parcel_nref * (np.outer(coefficients, reference["N"])
                                        + reference["xe"] * np.outer(derivatives, dTdz))
            close_vector(analytic.ravel(), chain_rule.ravel(), rtol=4e-12, atol=1e-300, label="Jacobian chain rule")
            step = 2e-5
            finite_difference = np.empty((3, 3))
            temperature_difference = np.empty(3)
            for j in range(3):
                direction = np.zeros(3)
                direction[j] = step
                states = [z + multiple * direction for multiple in (-2, -1, 1, 2)]
                values = [parcel.rhs(0.0, state) for state in states]
                finite_difference[:, j] = (values[0] - 8 * values[1] + 8 * values[2] - values[3]) / (12 * step)
                temperatures = [parcel.lift(state)["T"] for state in states]
                temperature_difference[j] = (temperatures[0] - 8 * temperatures[1] + 8 * temperatures[2] - temperatures[3]) / (12 * step)
            row_scales = np.maximum(np.max(np.abs(analytic), axis=1), np.max(np.abs(finite_difference), axis=1))
            row_errors = np.max(np.abs(analytic - finite_difference), axis=1) / np.maximum(row_scales, 1e-300)
            require(np.all(row_errors <= 5e-8), "pointwise analytic Jacobian disagrees with five-point RHS derivative")
            close_vector(dTdz, temperature_difference, rtol=3e-8, atol=1e-7, label="EOS temperature gradient")
            singular_values = np.linalg.svd(analytic, compute_uv=False)
            require(singular_values[-1] <= 1e-12 * singular_values[0], "sampled Jacobian rank exceeds two at numerical precision")
            return {"z": z.tolist(), "step": step, "analytic": analytic.tolist(),
                    "five_point": finite_difference.tolist(), "row_scaled_errors": row_errors.tolist(),
                    "dTdz": dTdz.tolist(), "dTdz_five_point": temperature_difference.tolist(),
                    "singular_values": singular_values.tolist(),
                    "rank_scope": "Pointwise numerical consistency; the rank bound is independently derived in the review"}
        check("new_parcel_analytic_Jacobian_and_temperature_gradient", check_parcel_jacobian)

        def check_full_state_independence():
            w = parcel.initial_full()
            w[0] = 1.05
            w[4] *= 1.2
            w[6] = 0.97
            state = parcel.full_lift(w)
            neutral = parcel_B * w[:3]
            ions = parcel_B * w[3:6]
            electrons = math.fsum(ions)
            particles = math.fsum(neutral) + 2.0 * electrons
            energy = independent_u0 * float(w[6])
            temperature = energy / (thermal_c * particles)
            close_vector(state["neutral_abundance"], neutral, rtol=3e-15, label="off-manifold neutral decode")
            close_vector(state["ion_abundance"], ions, rtol=3e-15, label="off-manifold ion decode")
            close(state["u"], energy, rtol=3e-15, label="independent thermal coordinate")
            close(state["N_g"], particles, rtol=3e-15, label="independent particle count")
            close(state["T"], temperature, rtol=3e-15, label="independent EOS decode")
            require(state["neutral_abundance"][0] > parcel.B[0], "full neutral fraction was clipped/projected")
            require(not np.array_equal(neutral + ions, parcel_B), "chosen full-state sample accidentally conserved nuclei")
            coefficients = np.array([model.evaluate(temperature).K_cm3_s for model in rates])
            event_flux = parcel_nref * electrons * neutral * coefficients
            expected = np.concatenate((-event_flux / parcel_B, event_flux / parcel_B,
                                       np.array([-math.fsum(chemical * event_flux) / independent_u0])))
            error = close_vector(parcel.full_rhs(0.0, w), expected, rtol=4e-12, label="off-manifold original RHS")
            return {"normalized_full_state": w.tolist(), "T_K": state["T"],
                    "nucleus_sum_per_species": (neutral + ions).tolist(), "configured_B": parcel_B.tolist(),
                    "full_rhs_max_relative_error": error, "projection_used": False}
        check("new_original_seven_state_decode_without_projection", check_full_state_independence)

        def check_parcel_endpoint_roundtrip():
            records = []
            for temperature in (255.0, 50000.0):
                endpoint = parcel_module.HazardParcel(rates, parcel_B, parcel_X0, temperature, parcel_nref)
                hazard_T = endpoint.lift(np.zeros(3))["T"]
                full_T = endpoint.full_lift(endpoint.initial_full())["T"]
                close(hazard_T, temperature, rtol=3e-15, label="endpoint hazard EOS roundtrip")
                close(full_T, temperature, rtol=3e-15, label="endpoint original EOS roundtrip")
                records.append({"T0_K": temperature, "hazard_T_K": hazard_T, "full_T_K": full_T})
            return records
        check("new_parcel_initial_temperature_endpoint_roundtrip", check_parcel_endpoint_roundtrip)

        def check_parcel_guards_and_immutability():
            template = dict(rates=rates, abundance_total=parcel_B, initial_ions=parcel_X0,
                            T0_K=ACTUAL_PARENT_TMAX_K, nref_cm3=parcel_nref)
            cases = {
                "rates_not_tuple": {"rates": list(rates)}, "wrong_rate_count": {"rates": rates[:2]},
                "invalid_rate_object": {"rates": (rates[0], rates[1], object())},
                "zero_total": {"abundance_total": [1.0, 0.0, 0.1]},
                "negative_total": {"abundance_total": [1.0, -0.2, 0.1]},
                "boolean_total": {"abundance_total": [True, 0.2, 0.1]},
                "negative_ion": {"initial_ions": [-0.1, 0.01, 0.01]},
                "no_initial_neutral": {"initial_ions": parcel_B.copy()},
                "unseeded_outside_selected_API": {"initial_ions": [0.0, 0.0, 0.0]},
                "wrong_total_shape": {"abundance_total": [1.0, 0.2]},
                "zero_density": {"nref_cm3": 0.0}, "boolean_density": {"nref_cm3": True},
                "nonfinite_density": {"nref_cm3": math.inf}, "boolean_T0": {"T0_K": True},
                "low_T0": {"T0_K": 254.999}, "high_T0": {"T0_K": 50000.001},
            }
            rejected = []
            for label, changes in cases.items():
                try:
                    parcel_module.HazardParcel(**(template | changes))
                except ValueError as exc:
                    rejected.append({"case": label, "exception": str(exc)})
                else:
                    raise AssertionError("parcel constructor accepted " + label)
            state_cases = {
                "negative_hazard": lambda: parcel.lift([-1e-20, 0.0, 0.0]),
                "boolean_hazard": lambda: parcel.lift([False, 0.0, 0.0]),
                "complex_hazard": lambda: parcel.lift([0j, 0.0, 0.0]),
                "nonfinite_hazard": lambda: parcel.lift([math.inf, 0.0, 0.0]),
                "wrong_hazard_shape": lambda: parcel.lift([0.0, 0.0]),
                "negative_thermal_state": lambda: parcel.full_lift([1.0, 1.0, 1.0, 0.1, 0.1, 0.1, -1.0]),
                "zero_thermal_state": lambda: parcel.full_lift([1.0, 1.0, 1.0, 0.1, 0.1, 0.1, 0.0]),
                "wrong_full_shape": lambda: parcel.full_lift([1.0, 1.0, 1.0]),
                "nonfinite_time": lambda: parcel.rhs(math.nan, [0.0, 0.0, 0.0]),
                "boolean_time": lambda: parcel.jac(True, [0.0, 0.0, 0.0]),
            }
            for label, call in state_cases.items():
                try:
                    call()
                except ValueError as exc:
                    rejected.append({"case": label, "exception": str(exc)})
                else:
                    raise AssertionError("parcel accepted " + label)
            input_B, input_X0 = parcel_B.copy(), parcel_X0.copy()
            immutable = parcel_module.HazardParcel(rates, input_B, input_X0, ACTUAL_PARENT_TMAX_K, parcel_nref)
            input_B[0], input_X0[0] = 99.0, 99.0
            require(immutable.B[0] == parcel_B[0] and immutable.X0[0] == parcel_X0[0], "parcel caller aliases retained")
            for name in ("B", "X0", "N0", "Ichemical_eV"):
                array = getattr(immutable, name)
                try:
                    array.setflags(write=True)
                except ValueError:
                    pass
                else:
                    raise AssertionError("parcel array can become writeable: " + name)
            return {"rejected_cases": rejected, "copy_isolation": True,
                    "seed_contract": "xe0>0 selected API; xe0=0 is a mathematical absorbing state outside this active API"}
        check("new_seeded_parcel_domains_and_immutable_inputs", check_parcel_guards_and_immutability)

        def check_parcel_neutral_underflow_flag():
            synthetic_rates = tuple(ci.FiniteWindowCI(
                f"synthetic{i}", [1.0, 2.0], [1e-16, 1e-16], f"synthetic:saturation{i}", 0.01, 1.0, 2.0
            ) for i in range(3))
            synthetic = parcel_module.HazardParcel(synthetic_rates, parcel_B, parcel_X0, ACTUAL_PARENT_TMAX_K, parcel_nref)
            state = synthetic.lift([800.0, 801.0, 802.0])
            require(state["neutral_underflow"] and np.all(state["neutral_underflow_mask"]), "saturation underflow was not flagged")
            require(np.all(state["neutral_abundance"] == 0.0), "unexpected synthetic saturation representation")
            close_vector(state["ion_abundance"], parcel_B, rtol=3e-15, label="saturated ion abundance")
            return {"input_scope": "Artificial small chemical defects preserve the temperature domain at saturation",
                    "T_K": state["T"], "neutral": state["neutral_abundance"].tolist(),
                    "underflow_flag": bool(state["neutral_underflow"]),
                    "underflow_mask": state["neutral_underflow_mask"].tolist()}
        check("new_parcel_saturation_reports_neutral_underflow", check_parcel_neutral_underflow_flag)

    except Exception as exc:
        report["setup_failure"] = {"exception": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
    unknown_groups = sorted(set(args.only) - set(report["checks"]))
    if unknown_groups and "setup_failure" not in report:
        report["selection_error"] = {"unknown_check_groups": unknown_groups}
    failed = ("setup_failure" in report or "selection_error" in report
              or any(item["status"] == "FAIL" for item in report["checks"].values()))
    report["status"] = "FAIL" if failed else "PASS_SCOPED"
    report["elapsed_wall_s"] = time.monotonic() - started
    usage = resource.getrusage(resource.RUSAGE_SELF)
    report["resource_usage"] = {"user_cpu_s": usage.ru_utime, "system_cpu_s": usage.ru_stime, "maxrss_platform_units": usage.ru_maxrss}
    report["exit_code"] = 1 if failed else 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    print(json.dumps({"status": report["status"], "output": str(args.output),
                      "checks_executed": sum(item["status"] != "NOT_RUN_SCOPED" for item in report["checks"].values()),
                      "vendor_rate_evaluations": report["vendor_rate_evaluations"], "elapsed_wall_s": report["elapsed_wall_s"]}))
    return report["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
