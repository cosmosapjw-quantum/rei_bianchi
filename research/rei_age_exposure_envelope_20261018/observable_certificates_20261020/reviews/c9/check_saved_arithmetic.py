"""Independent readback of saved output; no exponential, solver, or benchmark rerun."""
import decimal
import hashlib
import json
import pathlib
import struct
from fractions import Fraction as F

HERE = pathlib.Path(__file__).resolve().parent
UNIT = HERE.parents[1]
R = UNIT / "results"
D = decimal.Decimal
decimal.getcontext().prec = 140

def load(name):
    return json.loads((R / name).read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    s, ref = load("STUDY.json"), load("DECIMAL_REFERENCE.json")
    assert s["nodes"] == ref["nodes"] == 57344
    assert s["passive_nodes"] == 4096
    assert s["rates"] == 1113
    assert s["PRODUCTION_SCIENTIFIC_ADMISSION"] == "NOT_ISSUED"
    assert ref["precision_digits"] == 100 and ref["all_exp_values_positive"]
    count = {"decimal_containment": 0, "decimal_upper_bound": 0,
             "rational_formula": 0, "center_radius": 0, "same_population_denominator": 0}

    def contain(x, interval):
        assert D.from_float(interval[0]) <= x <= D.from_float(interval[1])
        count["decimal_containment"] += 1

    def upper(x, u):
        assert x <= D.from_float(u)
        count["decimal_upper_bound"] += 1

    for i, case in enumerate(s["cases"]):
        clock = case["clock"]
        assert clock == [8, 16, 32, 64][i]
        for name, c in case["populations"].items():
            values = list(map(D, ref["case_references"][str(clock)][name]))
            for j in range(7):
                contain(values[j], c["observables"][j])
            contain(values[7], c["absorbed_number"])
            contain(values[8], c["absorbed_same_energy"])
            contain(D(0), c["photon_ledger"])
            contain(D(0), c["same_energy_ledger"])
            contain(values[2] / values[0], c["normalized_mean"])

    for i, pair in enumerate(s["pairs"]):
        assert pair["coarse"] == [8, 16, 32, 64][i] and pair["reference"] == 64
        for name, p in pair["populations"].items():
            r = ref["pair_references"][i]["populations"][name]
            signed = list(map(D, r["signed_difference"]))
            for j in range(7):
                contain(signed[j], p["signed_difference"][j])
                contain(signed[j], p["direct_case_difference"][j])
                upper(D(r["label_absolute_sum"][j]), p["label_absolute_upper"][j])
            for j in range(2):
                upper(abs(signed[j + 2]), p["moment_chosen_upper"][j])
                upper(abs(signed[j + 2]), p["moment_global_upper"][j])
                assert p["moment_chosen_upper"][j] == min(p["label_absolute_upper"][j + 2], p["moment_global_upper"][j])
            assert F(p["moment_global_upper"][1]) >= 2 * F(p["Amax_upper"]) * F(p["C_upper"])
            count["rational_formula"] += 1
            b = p["normalized_mean_bound"]
            actual = abs(D(r["normalized_mean_difference"]))
            contain(D(r["normalized_mean_difference"]), b["observed_signed_interval"])
            e0 = max(abs(x) for x in p["signed_difference"][0])
            na = s["cases"][i]["populations"][name]["observables"][0][0]
            nb = s["cases"][3]["populations"][name]["observables"][0][0]
            assert na > 0 and nb > 0 and b["status"] == "RESOLVED"
            for side, key in enumerate(["forward", "reverse"]):
                x = b[key]
                assert x["denominator_lo"] == [na, nb][side]
                count["same_population_denominator"] += 1
                mean = s["cases"][[3, i][side]]["populations"][name]["normalized_mean"]
                assert F(x["radius"]) >= max(abs(F(x["center"]) - F(v)) for v in mean)
                count["center_radius"] += 1
                assert x["E0"] == e0
                assert F(x["upper"]) >= (F(x["Bc"]) + F(x["radius"]) * F(x["E0"])) / F(x["denominator_lo"])
                count["rational_formula"] += 1
                upper(D(r["centered_absolute_sum"][side]), x["Bc"])
                upper(actual, x["upper"])
            assert F(b["global_upper"]) >= (F(p["C_upper"]) + F(p["Amax_upper"]) * F(p["label_absolute_upper"][0])) / F(min(na, nb))
            count["rational_formula"] += 1
            assert b["chosen_upper"] == min(b["forward"]["upper"], b["reverse"]["upper"], b["global_upper"])
            upper(actual, b["chosen_upper"])
            if name == "passive":
                assert signed[0] == 0 and signed[1] == 0
                assert all(x == 0 for x in signed[4:])
            if i == 3:
                assert all(x == 0 for x in signed) and b["chosen_upper"] == 0

    prior = R / "before_actual_request_cache/STUDY.json"
    floats = 0
    def same(a, b):
        nonlocal floats
        assert type(a) is type(b)
        if isinstance(a, dict):
            assert set(a) == set(b)
            for k in a: same(a[k], b[k])
        elif isinstance(a, list):
            assert len(a) == len(b)
            for x, y in zip(a, b): same(x, y)
        elif isinstance(a, float):
            assert struct.pack("!d", a) == struct.pack("!d", b)
            floats += 1
        else:
            assert a == b
    if prior.exists():
        old = json.loads(prior.read_text())
        for key in ["cases", "pairs"]: same(old[key], s[key])
    result = {"status": "PASS", "scope": "Saved raw output and saved Decimal reference only",
              "new_exponential_evaluations": 0, "new_native_runs": 0,
              "checks": count, "prior_cache_repair_scientific_float_bits_equal": floats,
              "input_artifacts": {str(p.relative_to(UNIT)): sha(p) for p in [R/"STUDY.json", R/"DECIMAL_REFERENCE.json"]},
              "PRODUCTION_SCIENTIFIC_ADMISSION": "NOT_ISSUED"}
    (HERE / "SAVED_ARITHMETIC_READBACK.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))

if __name__ == "__main__":
    main()
