"""One frozen production/verification pass, executed only by the bounded runner."""
import csv
import hashlib
import json
import math
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

from stress_source import (Interval, enclose, massive_terms, pressure_source,
                           rational, record, from_record)

HERE = Path(__file__).resolve().parent


def require(condition, label):
    if not condition:
        raise AssertionError(label)


def decimal_reference(atoms, mass):
    # Alternative algebra and fixed Decimal100; no dyadic accumulation reused.
    with localcontext() as context:
        context.prec = 100
        def dec(value):
            return Decimal(value.numerator) / Decimal(value.denominator)
        M = dec(mass)
        W = S = Decimal(0)
        for kinetic, weight in atoms:
            k, w = dec(kinetic), dec(weight)
            W += w * (2 * k - k * k / (k + M))
            S += w * k * k / ((k + M) * (k + M))
        return {"W": W, "S": S}


def relative_decimal_check(interval, reference, label):
    require(interval.contains(Fraction(reference)), label + " Decimal100 containment")
    rounded = interval.certified()
    require(rounded["status"] == "CERTIFIED_BINARY64", label + " stable binary64")
    with localcontext() as context:
        context.prec = 100
        relative = (abs(Decimal.from_float(rounded["value"]) - reference) / abs(reference)
                    if reference else Decimal(0))
    require(relative <= Decimal("2e-15"), label + " relative <=2e-15")
    return {"Decimal100": str(reference), "relative": str(relative), "containment": True}


def controls():
    names = []
    Wterms, Sterms = massive_terms([(0, 1), (2, 3)], "1")
    W, _ = enclose(Wterms, 160)
    S, _ = enclose(Sterms, 160)
    require(W.contains(Fraction(8)) and S.contains(Fraction(4, 3)), "hand W/S")
    source = pressure_source(W, S, "2", "3", "-1", "2", "3")
    expectations = {"pressure": Fraction(8, 3), "source": Fraction(16), "jvp": Fraction(32, 3)}
    for key, value in expectations.items():
        require(source[key].contains(value), "hand " + key)
        require(source[key].certified()["value"] == float(value), "hand rounding " + key)
    require((Interval.point(12) - W).contains(4), "hand D")
    names.append("hand_exact_W_S_D_pressure_source_mass_amplitude_JVP")
    for atoms in ([], [(0, 1)], [(1, 0)]):
        for terms in massive_terms(atoms, 1):
            zero, _ = enclose(terms, 160)
            require(zero.certified()["tag"] == "exact_zero", "empty/zero")
    names.append("empty_zero_measure")
    signed, _ = enclose([Fraction(1, 3), -Fraction(2, 7)], 160)
    require(signed.contains(Fraction(1, 21)), "signed direct enclosure")
    cancel, _ = enclose([Fraction(1), -Fraction(1)], 160)
    require(cancel.certified()["tag"] == "exact_zero", "exact cancellation")
    crossed = Interval(-Fraction(1, 2 ** 160), Fraction(1, 2 ** 160)).certified()
    require(crossed["status"] == "ROUNDING_UNRESOLVED" and not crossed["exact_zero"], "crossed zero")
    names.append("signed_direct_enclosure_cancellation_zero_classification")
    tiny_crossed = Interval(-Fraction(1, 2 ** 1100), Fraction(1, 2 ** 1100)).certified()
    require(tiny_crossed["status"] == "ROUNDING_UNRESOLVED" and not tiny_crossed["exact_zero"],
            "tiny crossing signed-zero endpoints")
    negative_tiny = Interval.point(-Fraction(1, 2 ** 1100)).certified()
    require(negative_tiny["status"] == "CERTIFIED_BINARY64"
            and negative_tiny["tag"] == "final_underflow_to_zero"
            and math.copysign(1.0, negative_tiny["value"]) == -1.0
            and not negative_tiny["exact_zero"], "negative underflow sign retained")
    names.append("tiny_crossing_unresolved_negative_underflow_sign")
    adjacent = Interval(Fraction.from_float(1.0), Fraction.from_float(math.nextafter(1.0, math.inf)))
    require(adjacent.certified()["status"] == "ROUNDING_UNRESOLVED", "adjacent float unresolved")
    names.append("adjacent_binary64_unresolved")
    invalid = [([(float('nan'), 1)], 1), ([(float('inf'), 1)], 1),
               ([(1, float('inf'))], 1), ([(-1, 1)], 1), ([(1, -1)], 1),
               ([(1, 1)], 0), ([(1, 1)], -1), ([(1, 1)], float('nan'))]
    for atoms, mass in invalid:
        try:
            massive_terms(atoms, mass)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid input accepted")
    names.append("nonfinite_negative_nonpositive_guards")
    try:
        Interval.point(Fraction(10 ** 400)).certified()
    except OverflowError:
        pass
    else:
        raise AssertionError("overflow accepted")
    names.append("overflow_rejected")
    for weight, expected in [(Fraction(1, 2 ** 1100), "final_underflow_to_zero"),
                             (Fraction(1, 2 ** 1070), "subnormal")]:
        tiny_terms, tiny_derivative = massive_terms([(1, weight)], 1)
        tiny, _ = enclose(tiny_terms, 160)
        deriv, _ = enclose(tiny_derivative, 160)
        pressure = pressure_source(tiny, deriv, 1, 1, 0, 0, 0)["pressure"]
        require(pressure.certified()["tag"] == expected, "new pressure " + expected)
    names.append("new_pressure_final_underflow_subnormal")
    return {"groups": names, "hand": {key: source[key].payload() for key in expectations},
            "signed_direct": signed.payload(), "crossed_zero": crossed,
            "tiny_crossing": tiny_crossed, "negative_underflow": negative_tiny,
            "adjacent_unresolved": adjacent.payload()}


def main():
    provenance = json.loads((HERE / "inputs/INPUT_BINDING.json").read_text())
    for entry in provenance["immutable_files"]:
        path = HERE / entry["relative_path"]
        require(hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"], "immutable " + str(path))
    prior = json.loads((HERE / "inputs/prior_moments.json").read_text())
    old_raw = json.loads((HERE / "inputs/prior_stdout.jsonl").read_text().splitlines()[0])
    require(prior["moments"] == old_raw["moments"], "verbatim prior fields")
    atoms = []
    with (HERE / "inputs/photoelectron_atoms.csv").open(newline="") as stream:
        for row in csv.DictReader(stream):
            if row["redshift"] == "2.479" and row["channel"] == "HI":
                atoms.append((rational(float(row["kinetic_eV"])),
                              rational(float(row["number_weight_per_target_s"]))))
    require(len(atoms) == 4368 == prior["moments"]["atom_count"], "4368 selected atoms")
    L = from_record(prior["moments"]["maximum_kinetic"])
    K = from_record(prior["moments"]["K"])
    require(max(k for k, _ in atoms) == L, "saved actual support maximum")
    mass_source = json.loads((HERE / "inputs/mass_source.json").read_text())
    masses = [Fraction(m) for m in mass_source["sensitivity_points_eV"]]
    results = []
    all_intervals = []
    for index, mass in enumerate(masses):
        terms = massive_terms(atoms, mass)
        intervals = {}
        raw_intervals = {}
        for label, values in zip(("W", "S"), terms):
            coarse, cmeta = enclose(values, 128)
            fine, fmeta = enclose(values, 160)
            require(fine.nested_in(coarse), label + " P160 nested P128")
            coarse_rounding, fine_rounding = coarse.certified(), fine.certified()
            require(coarse_rounding["status"] == fine_rounding["status"] == "CERTIFIED_BINARY64",
                    label + " P128/P160 both finite certificates")
            require(coarse_rounding["value"].hex() == fine_rounding["value"].hex(),
                    label + " P128/P160 identical binary64")
            intervals[label] = {"P128": coarse.payload(), "P160": fine.payload(),
                                "P128_grid": cmeta, "P160_grid": fmeta, "nested": True}
            raw_intervals[label] = fine
        W, S = raw_intervals["W"], raw_intervals["S"]
        D = Interval.point(2 * K) - W
        ratio = D.divide_positive(W)
        require(K <= W.lo <= W.hi <= 2 * K, "K<=W<=2K")
        require(0 <= D.lo <= D.hi <= L * K / (L + mass), "defect support bound")
        require(ratio.hi <= L / (L + 2 * mass), "relative defect support bound")
        source = pressure_source(W, S, "2", "3", "-1", "2", "3")
        for key in ("pressure", "source", "jvp"):
            require(source[key].certified()["status"] == "CERTIFIED_BINARY64", key + " stable")
        reference = decimal_reference(atoms, mass)
        comparison = {key: relative_decimal_check(raw_intervals[key], reference[key], key)
                      for key in ("W", "S")}
        results.append({"mass_eV": str(mass_source["sensitivity_points_eV"][index]),
                        "intervals": intervals, "Decimal100_comparison": comparison,
                        "pressure_source": {key: source[key].payload() for key in ("pressure", "source", "jvp")},
                        "flux": source["flux"], "STF": source["STF"], "thermal_heat": None,
                        "defect": D.payload(), "relative_defect": ratio.payload(),
                        "support_bounds_certified": True})
        all_intervals.append(raw_intervals)
    minus, nominal, plus = all_intervals
    u = Fraction(mass_source["standard_uncertainty_eV"])
    require(minus["W"].hi <= nominal["W"].lo <= nominal["W"].hi <= plus["W"].lo, "mass monotonicity")
    forward = plus["W"] - nominal["W"]
    backward = nominal["W"] - minus["W"]
    tangent = nominal["S"].scale(u)
    require(forward.hi <= tangent.lo, "forward concavity")
    require(backward.lo >= tangent.hi, "backward concavity")
    result = {"schema": "REI_HI_MASSIVE_STRESS_RAW_V1", "unit": "HI_NATIVE_MASSIVE_STRESS_20261025",
              "observed_status": "PASS_SCOPED_FOCUSED_CHECKS", "scientific_admission": "ROOT_PENDING",
              "primary_rows": len(atoms), "precision_bits": [128, 160], "mass_results": results,
              "mass_sensitivity": {"forward": forward.payload(), "backward": backward.payload(),
                                   "uS": tangent.payload(), "monotonicity": True, "concavity": True,
                                   "interpretation": "standard-uncertainty probes; not confidence bounds"},
              "controls": controls(), "old_moments": prior["moments"], "old_tests_replayed": 0,
              "actual_density_history_IC_geometry": "UNRESOLVED", "L4_ready": False,
              "whole_model_completion": None, "thermal_heat": None}
    print(json.dumps(result, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
