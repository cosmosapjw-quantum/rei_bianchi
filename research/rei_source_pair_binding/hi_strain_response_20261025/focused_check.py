"""One root-GO child: new R/R_M integration and eight frozen control groups."""
import csv
import json
import math
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path

from reuse.stress_source import Interval, enclose, from_record, record
from strain_response import (scalar, matrix, trace, T, radial_terms, coefficients,
                             strain_tensor, source_jvp, number_energy_derivatives,
                             tensor_payload, directions14)

HERE = Path(__file__).resolve().parent
ZERO = ((0, 0, 0), (0, 0, 0), (0, 0, 0))
IDENTITY = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
SHEAR = ((1, 0, 0), (0, -1, 0), (0, 0, 0))
DSHEAR = ((0, 0, 0), (0, 1, 0), (0, 0, -1))


def require(condition, label):
    if not condition:
        raise AssertionError(label)


def dec(value):
    return Decimal(value.numerator) / Decimal(value.denominator)


def interval_from_payload(payload):
    return Interval(from_record(payload["lo"]), from_record(payload["hi"]))


def stable_pair(coarse, fine, label):
    require(fine.nested_in(coarse), label + " P160 nested in P128")
    a, b = coarse.certified(), fine.certified()
    require(a["status"] == b["status"] == "CERTIFIED_BINARY64", label + " finite binary64 certificates")
    require(a["value"].hex() == b["value"].hex(), label + " P128/P160 identical binary64")


def expect_tensor(tensor, expected, label):
    for i in range(3):
        for j in range(3):
            target = F(expected[i][j])
            require(tensor[i][j].contains(target), label + " exact containment")
            rounded = tensor[i][j].certified()
            require(rounded["status"] == "CERTIFIED_BINARY64" and rounded["value"] == float(target),
                    label + " certified literal rounding")


def plain_add(A, B):
    return [[A[i][j] + B[i][j] for j in range(3)] for i in range(3)]


def multiply(A, B):
    return [[sum((A[i][k] * B[k][j] for k in range(3)), F(0)) for j in range(3)] for i in range(3)]


def transpose(A):
    return [list(row) for row in zip(*A)]


def rotate(O, B):
    return multiply(multiply(O, B), transpose(O))


def rejected(call, label):
    try:
        call()
    except (ValueError, TypeError, OverflowError):
        return
    raise AssertionError("invalid input accepted: " + label)


def angular_derivative(B):
    """Hand w=2,k=M=1: original tensor identity, not reduced C formula."""
    B = matrix(B)
    answer = [[F(0) for _ in range(3)] for _ in range(3)]
    for angular_weight, nn in directions14():
        Bnn, nnB = multiply(B, nn), multiply(nn, B)
        nBn = sum((B[a][b] * nn[a][b] for a in range(3) for b in range(3)), F(0))
        for i in range(3):
            for j in range(3):
                answer[i][j] += angular_weight * 3 * (-trace(B) * nn[i][j] - Bnn[i][j] - nnB[i][j]
                                                       + F(3, 4) * nn[i][j] * nBn)
    return answer


def finite_14_transport(epsilon, diagonal):
    """Decimal100 finite ray fixture; not an exact continuous-sphere integral."""
    epsilon = dec(epsilon)
    d = [dec(F(v)) for v in diagonal]
    scales = [(-epsilon * v).exp() for v in d]
    dilution = (-epsilon * sum(d, Decimal(0))).exp()
    tensor = [[Decimal(0) for _ in range(3)] for _ in range(3)]
    for angular_weight, nn in directions14():
        # Hand k=M=1 => q=3, initial radial weight=2.
        energy = (Decimal(1) + 3 * sum((scales[i] ** 2 * dec(nn[i][i]) for i in range(3)), Decimal(0))).sqrt()
        for i in range(3):
            for j in range(3):
                tensor[i][j] += dec(angular_weight) * dilution * 6 * scales[i] * scales[j] * dec(nn[i][j]) / energy
    return tensor


def finite_controls():
    with localcontext() as context:
        context.prec = 100
        diagonal = (F(1), F(-1), F(1, 2))
        B = [[diagonal[i] if i == j else F(0) for j in range(3)] for i in range(3)]
        target = strain_tensor(Interval.point(F(51, 4)), B)
        derivative = [[dec(target[i][j].lo) for j in range(3)] for i in range(3)]
        previous = None
        results = []
        for power in (8, 9, 10):
            h = F(1, 2 ** power)
            hd = dec(h)
            plus, minus = finite_14_transport(h, diagonal), finite_14_transport(-h, diagonal)
            err = sum((((plus[i][j] - minus[i][j]) / (2 * hd) - derivative[i][j]) ** 2
                       for i in range(3) for j in range(3)), Decimal(0)).sqrt()
            ratio = err / previous if previous is not None else None
            if ratio is not None:
                require(ratio <= Decimal("0.3"), "finite14 centered error contraction")
            # Eq6 b=1, |t|=1/2, W=3; both one-sided endpoints.
            bound = hd ** 2 / 2 * ((Decimal("0.5") + 3) ** 2 + 2) * (Decimal("2.5") * hd).exp() * 3
            endpoint_errors = []
            for sign, transported in ((1, plus), (-1, minus)):
                remainder = sum(((transported[i][j] - Decimal(int(i == j))
                                  - sign * hd * derivative[i][j]) ** 2
                                 for i in range(3) for j in range(3)), Decimal(0)).sqrt()
                require(remainder <= bound, "finite14 one-sided Eq6 remainder")
                endpoint_errors.append(str(remainder))
            results.append({"h": record(h), "centered_derivative_F_error": str(err),
                            "error_ratio": str(ratio) if ratio is not None else None,
                            "one_sided_remainder_errors": endpoint_errors, "Eq6_bound": str(bound)})
            previous = err
        return results


def controls():
    groups = []
    Rterms, RMterms = radial_terms([(1, 2)], 1)
    R, _ = enclose(Rterms, 160)
    RM, _ = enclose(RMterms, 160)
    W, S = Interval.point(3), Interval.point(F(1, 2))
    coef = coefficients(W, S, R, RM)
    for label, observed, target in [("R", R, F(9, 4)), ("RM", RM, F(-3, 8)),
                                    ("C", coef["C"], F(51, 4)), ("CM", coef["CM"], F(23, 8)),
                                    ("kappa", coef["kappa"], F(17, 10)), ("Gamma", coef["Gamma"], F(17, 12))]:
        require(observed.contains(target), "hand literal " + label)
        require(observed.certified()["value"] == float(target), "hand float " + label)
    groups.append("hand_literal_R_RM_C_CM_kappa_Gamma")
    C, CM = coef["C"], coef["CM"]
    offdiag = ((0, F(1, 2), 0), (F(1, 2), 0, 0), (0, 0, 0))
    expect_tensor(strain_tensor(C, IDENTITY), [[F(-17, 4) if i == j else 0 for j in range(3)] for i in range(3)], "isotropic")
    expect_tensor(strain_tensor(C, SHEAR), ((F(-17, 10), 0, 0), (0, F(17, 10), 0), (0, 0, 0)), "shear")
    expect_tensor(strain_tensor(C, offdiag), ((0, F(-17, 20), 0), (F(-17, 20), 0, 0), (0, 0, 0)), "offdiagonal")
    combined = plain_add(IDENTITY, offdiag)
    combined_tensor = strain_tensor(C, combined)
    left, right = strain_tensor(C, IDENTITY), strain_tensor(C, offdiag)
    for i in range(3):
        for j in range(3):
            require(combined_tensor[i][j].lo == left[i][j].lo + right[i][j].lo, "tensor linearity")
    mean = sum((combined_tensor[i][i].lo for i in range(3)), F(0)) / 3
    require(mean == -F(51, 4) * trace(matrix(combined)) / 9, "trace decomposition")
    for i in range(3):
        for j in range(3):
            Btf = F(combined[i][j]) - (trace(matrix(combined)) / 3 if i == j else 0)
            require(combined_tensor[i][j].lo - (mean if i == j else 0) == -F(17, 10) * Btf, "STF decomposition")
    balance = number_energy_derivatives(2, 2, W, IDENTITY)
    require(balance["delta_N"].contains(-6) and balance["delta_K"].contains(-9), "number/energy literal derivatives")
    groups.append("trace_STF_linearity_isotropic_shear_offdiag_number_energy")
    O = ((F(3, 5), F(-4, 5), 0), (F(4, 5), F(3, 5), 0), (0, 0, 1))
    require(multiply(O, transpose(O)) == [list(r) for r in IDENTITY], "rational rotation orthogonal")
    tensor = strain_tensor(C, SHEAR)
    rotated_expected = rotate(O, [[v.lo for v in row] for row in tensor])
    expect_tensor(strain_tensor(C, rotate(O, SHEAR)), rotated_expected, "rotation covariance")
    groups.append("rational_orthogonal_rotation_covariance")
    source = source_jvp(C, CM, SHEAR, DSHEAR, 2, 3, -1, 2, 3)
    expect_tensor(source["Q"], ((F(-51, 5), 0, 0), (0, F(51, 5), 0), (0, 0, 0)), "Q literal")
    expect_tensor(source["JVP"], ((F(-43, 5), 0, 0), (0, F(-8, 5), 0), (0, 0, F(51, 5))), "full JVP literal")
    groups.append("amplitude_mass_strain_full_JVP_literals")
    for atoms in ([], [(0, 1)], [(1, 0)]):
        terms = radial_terms(atoms, 1)
        zero_R, _ = enclose(terms[0], 160)
        zero_RM, _ = enclose(terms[1], 160)
        zero = Interval.point(0)
        zcoef = coefficients(zero, zero, zero_R, zero_RM)
        require(zcoef["Gamma"] is None, "zero Gamma undefined")
        expect_tensor(strain_tensor(zcoef["C"], SHEAR), ZERO, "zero tensor")
    for atoms, mass in [([(True, 1)], 1), ([(1, False)], 1), ([(1, 1)], True),
                         ([(-1, 1)], 1), ([(1, -1)], 1), ([(1, 1)], 0), ([(1, 1)], -1),
                         ([(float("nan"), 1)], 1), ([(1, float("inf"))], 1), ([], float("nan"))]:
        rejected(lambda atoms=atoms, mass=mass: radial_terms(atoms, mass), "mass/k/w")
    for bad in [[], [[1, 0], [0, 1]], [[0, 1, 0], [0, 0, 0], [0, 0, 0]],
                [[True, 0, 0], [0, 0, 0], [0, 0, 0]], [[float("inf"), 0, 0], [0, 0, 0], [0, 0, 0]]]:
        rejected(lambda bad=bad: strain_tensor(C, bad), "matrix")
        rejected(lambda bad=bad: source_jvp(C, CM, SHEAR, bad, 1, 1, 0, 0, 0), "direction matrix")
    for args in [(-1, 1, 0, 0, 0), (1, -1, 0, 0, 0), (True, 1, 0, 0, 0),
                 (1, 1, float("nan"), 0, 0), (1, 1, 0, 0, False)]:
        rejected(lambda args=args: source_jvp(C, CM, SHEAR, ZERO, *args), "amplitude/direction")
    groups.append("zero_measure_undefined_Gamma_strict_scalar_matrix_amplitude_guards")
    rays = directions14()
    require(len(rays) == 14 and sum((w for w, _ in rays), F(0)) == 1, "14 normalized ray weights")
    for i in range(3):
        for j in range(3):
            second = sum((w * nn[i][j] for w, nn in rays), F(0))
            require(second == F(int(i == j), 3), "exact second angular moment")
            for a in range(3):
                for b in range(3):
                    fourth = sum((w * nn[i][j] * nn[a][b] for w, nn in rays), F(0))
                    target = F(int(i == j and a == b) + int(i == a and j == b) + int(i == b and j == a), 15)
                    require(fourth == target, "exact fourth angular moment")
    for B in (IDENTITY, SHEAR, offdiag, plain_add(SHEAR, offdiag)):
        expect_tensor(strain_tensor(C, B), angular_derivative(B), "unreduced14 tensor identity")
    groups.append("exact14_second_fourth_moments_unreduced_tensor_derivative")
    finite = finite_controls()
    groups.append("Decimal100_finite14_centered_convergence_and_Eq6_remainder")
    cancellation = source_jvp(Interval.point(15), Interval.point(15), SHEAR, ZERO, 1, 1, 1, 0, -1)
    require(all(v.certified()["tag"] == "exact_zero" for row in cancellation["JVP"] for v in row), "new JVP exact signed cancellation")
    tags = []
    for power, expected_tag in ((1100, "final_underflow_to_zero"), (1070, "subnormal")):
        tiny = F(1, 2 ** power)
        for sign in (-1, 1):
            B = ((0, F(sign, 2), 0), (F(sign, 2), 0, 0), (0, 0, 0))
            tag = strain_tensor(Interval.point(15 * tiny), B)[0][1].certified()
            require(tag["tag"] == expected_tag and not tag["exact_zero"], "new tensor tiny tag")
            require(math.copysign(1.0, tag["value"]) == -sign, "new tensor tiny sign")
            tags.append(tag)
    tiny = F(1, 2 ** 1100)
    unresolved = strain_tensor(Interval(-15 * tiny, 15 * tiny), offdiag)[0][1].certified()
    require(unresolved["status"] == "ROUNDING_UNRESOLVED", "new tensor tiny crossing unresolved")
    groups.append("new_tensor_cancellation_exact_zero_signed_underflow_subnormal_unresolved")
    require(len(groups) == 8, "eight new control groups")
    return {"groups": groups, "hand_coefficients": {key: value.payload() if value is not None else None for key, value in coef.items()},
            "hand_Q": tensor_payload(source["Q"]), "hand_JVP": tensor_payload(source["JVP"]),
            "angular14_fixture": [{"weight": record(w), "dyad": [[record(v) for v in row] for row in nn]}
                                  for w, nn in rays],
            "finite14": finite, "new_tensor_tiny_tags": tags, "new_tensor_crossing": unresolved}


def decimal_reference(atoms, mass):
    with localcontext() as context:
        context.prec = 100
        M = dec(mass)
        R = RM = Decimal(0)
        for kinetic, weight in atoms:
            k, w = dec(kinetic), dec(weight)
            E = k + M
            b = M / E
            factor = 1 - b * b
            R += w * E * factor * factor
            RM += w * factor * (factor - 4 * M * k / (E * E))
        return {"R": R, "RM": RM}


def decimal_check(interval, reference, label):
    require(interval.contains(F(reference)), label + " Decimal100 exact-rational containment")
    rounding = interval.certified()
    require(rounding["status"] == "CERTIFIED_BINARY64", label + " certificate")
    with localcontext() as context:
        context.prec = 100
        relative = abs(Decimal.from_float(rounding["value"]) - reference) / abs(reference) if reference else Decimal(0)
    require(relative <= Decimal("2e-15"), label + " <=2e-15")
    return {"Decimal100": str(reference), "relative": str(relative), "containment": True}


def main():
    contract = json.loads((HERE / "authority/IMPLEMENTATION_CONTRACT.json").read_bytes())
    prior_raw = json.loads((HERE / "inputs/prior_massive_stdout.jsonl").read_bytes())
    mass_string = contract["inputs"]["mass_eV"]
    matching = [row for row in prior_raw["mass_results"] if row["mass_eV"] == mass_string]
    require(len(matching) == 1, "exact nominal mass string selection")
    saved = matching[0]
    prior = json.loads((HERE / "inputs/prior_moments.json").read_bytes())["moments"]
    require(prior == prior_raw["old_moments"], "verbatim saved A/K/L and prior fields")
    atoms = []
    with (HERE / "inputs/photoelectron_atoms.csv").open(newline="") as stream:
        for row in csv.DictReader(stream):
            if row["redshift"] == "2.479" and row["channel"] == "HI":
                atoms.append((scalar(float(row["kinetic_eV"])), scalar(float(row["number_weight_per_target_s"]))))
    require(len(atoms) == 4368 == prior["atom_count"], "actual4368 selected native atoms")
    M = scalar(mass_string)
    A, K, L = (from_record(prior[key]) for key in ("A", "K", "maximum_kinetic"))
    require(max(k for k, _ in atoms) == L, "same stored support L")
    terms = radial_terms(atoms, M)
    by_precision, grids = {}, {}
    for P in (128, 160):
        W = interval_from_payload(saved["intervals"]["W"]["P" + str(P)])
        S = interval_from_payload(saved["intervals"]["S"]["P" + str(P)])
        R, Rgrid = enclose(terms[0], P)
        RM, RMgrid = enclose(terms[1], P)
        by_precision[P] = {"W": W, "S": S, "R": R, "RM": RM, **coefficients(W, S, R, RM)}
        grids[P] = {"R": Rgrid, "RM": RMgrid}
    all_intervals = {}
    for label in ("R", "RM", "C", "CM", "kappa", "Gamma", "RoverW", "RoverC"):
        coarse, fine = by_precision[128][label], by_precision[160][label]
        stable_pair(coarse, fine, label)
        all_intervals[label] = {"P128": coarse.payload(), "P160": fine.payload(), "nested": True, "stable_binary64": True}
    v = by_precision[160]
    betaL2 = L * (L + 2 * M) / (L + M) ** 2
    require(v["R"].lo >= 0 and v["R"].hi <= betaL2 * v["W"].lo, "R finite support enclosure")
    require(v["C"].lo > 0 and v["C"].lo >= (5 - betaL2) * v["W"].hi and v["C"].hi <= 5 * v["W"].lo, "C support enclosures")
    require(F(4, 3) <= v["Gamma"].lo <= v["Gamma"].hi <= F(5, 3), "Gamma physical interval")
    require(L < 2 * M and v["RM"].hi < 0 and v["CM"].lo > 0, "native RMnegative CMpositive")
    reference = decimal_reference(atoms, M)
    with localcontext() as context:
        context.prec = 100
        reference["C"] = 5 * Decimal(saved["Decimal100_comparison"]["W"]["Decimal100"]) - reference["R"]
        reference["CM"] = 5 * Decimal(saved["Decimal100_comparison"]["S"]["Decimal100"]) - reference["RM"]
    comparison = {label: decimal_check(v[label], reference[label], label) for label in ("R", "RM", "C", "CM")}
    tensors = source_jvp(v["C"], v["CM"], SHEAR, DSHEAR, 2, 3, -1, 2, 3)
    response = strain_tensor(v["C"], SHEAR)
    balance = number_energy_derivatives(A, K, v["W"], SHEAR)
    tensor_records = {key: tensor_payload(value) for key, value in {"strain": response, **tensors}.items()}
    require(all(entry["rounding"]["status"] == "CERTIFIED_BINARY64" for tensor in tensor_records.values()
                for row in tensor for entry in row), "native every tensor component certified")
    result = {"schema": "REI_HI_STRAIN_RESPONSE_RAW_V1", "unit": contract["unit"],
              "observed_status": "PASS_SCOPED_FOCUSED_CHECKS", "scientific_admission": "ROOT_PENDING",
              "primary_rows": len(atoms), "mass_eV": mass_string, "precision_bits": [128, 160],
              "new_native_integrals": ["R", "RM"], "old_native_integrals_recomputed": 0,
              "intervals": all_intervals, "grids": grids, "Decimal100_comparison": comparison,
              "reused_W_S_intervals": saved["intervals"], "saved_moments": prior, "beta_support_squared": record(betaL2),
              "support_bounds_certified": True, "tensor_controls": {"a": 2, "X": 3, "da": -1, "dX": 2, "dM": 3,
                  "B": SHEAR, "dB": DSHEAR, "classification": "synthetic amplitude/strain directions, not actual cohort history"},
              "native_tensors": tensor_records, "native_number_energy_derivatives": {k: value.payload() for k, value in balance.items()},
              "controls": controls(), "old_tests_replayed": 0, "actual_HI_history_geometry_clock_IC": "OPEN_INPUT_DEPENDENCY",
              "L4_ready": False, "whole_model_completion": None, "thermal_heat": None}
    print(json.dumps(result, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
