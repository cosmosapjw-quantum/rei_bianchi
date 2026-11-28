"""One bounded child: literal synthetic fixtures, exact checks, first-failure preservation."""
import argparse
import copy
from fractions import Fraction
import json
from pathlib import Path
import traceback

import chem_ledger as ledger


def encode(value):
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, dict):
        return {(",".join(map(str, k)) if isinstance(k, tuple) else str(k)): encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    return value


class CheckFailure(Exception):
    pass


def encode_residuals(value):
    if isinstance(value, dict):
        return {(",".join(map(str, key)) if isinstance(key, tuple) else str(key)): encode_residuals(item) for key, item in value.items()}
    if type(value) is int:
        return encode(Fraction(value))
    return encode(value)


def execute(fixtures, rows):
    species = ledger.catalog(fixtures["species"])
    epsilon = fixtures["epsilon"]
    cases = fixtures["cases"]

    def check(name, category, expected, observed, inputs, residuals=None, intended_rejection=False):
        row = {"name": name, "category": category, "inputs": encode(inputs),
               "expected": encode(expected), "observed": encode(observed),
               "residuals": encode_residuals(residuals), "intended_rejection": intended_rejection,
               "physical_qualification": "SYNTHETIC_INTERFACE_ONLY",
               "pass": observed == expected}
        rows.append(row)
        if not row["pass"]:
            raise CheckFailure(name)

    def rejection(name, function, expected_reason, inputs, residuals=None):
        try:
            function()
            observed = "NO_REJECTION"
        except ledger.LedgerError as error:
            observed = str(error)
        actual_residuals = None
        if residuals is not None:
            nu = ledger.stoichiometry(inputs, species)
            actual_residuals = {"isotope_count": ledger.composition_delta(nu, species),
                                "charge": Fraction(sum(species[key].charge * value for key, value in nu.items())),
                                "energy": None}
        check(name, "guards", expected_reason, observed, inputs, actual_residuals, True)
        if residuals is not None:
            actual = {**actual_residuals, "isotope_count": {k: v for k, v in encode(actual_residuals["isotope_count"]).items() if v != 0}}
            expected = {**residuals, "isotope_count": {k: v for k, v in residuals["isotope_count"].items() if v != 0}}
            check(name + ":exact_residual", "guard_residual_identities", expected, actual, inputs)

    baseline = fixtures["baseline_expected"]
    check("catalog_21_populations", "catalog", 21, len(baseline), baseline)
    for name, (z, a, q) in baseline.items():
        s = species[name]
        check("catalog_" + name, "catalog", (((z, a, "ground"), 1), q, "ground", "material"),
              (s.composition[0], s.charge, s.state, s.pool), fixtures["species"][name])
        check("catalog_single_nucleus_" + name, "catalog", 1, len(s.composition), fixtures["species"][name])
    for name, pool in (("e_th", "electron_thermal"), ("e_fast", "electron_fast")):
        s = species[name]
        check("catalog_" + name, "catalog", ((), -1, "free", pool), s.key(), fixtures["species"][name])
    check("electron_pool_identity", "catalog", False, species["e_th"].key() == species["e_fast"].key(), ["e_th", "e_fast"])

    for case in cases:
        expected = case["expected"]
        observed = ledger.compile_reaction(case, species, epsilon)
        category = "positive_chemistry" if case["kind"] == "chemical" else "algebraic_nuclear"
        isotope_delta = {",".join(map(str, k)): v for k, v in observed["isotope_delta"].items() if v != 0}
        actual = {"nu": observed["nu"], "isotope_delta": isotope_delta,
                  "charge_delta": observed["charge_delta"], "baryon_delta": observed["baryon_delta"],
                  "delta_internal": observed["energy"]["delta_internal"] if observed["energy"] else None,
                  "energy_residual": observed["energy"]["residual"] if observed["energy"] else None}
        literal = dict(expected)
        for field in ("delta_internal", "energy_residual"):
            if literal[field] is not None:
                literal[field] = Fraction(literal[field])
        residuals = {"isotope_count": observed["isotope_delta"], "charge": Fraction(observed["charge_delta"]),
                     "energy": actual["energy_residual"]}
        check(case["id"], category, literal, actual, {"reaction": case, "epsilon": epsilon}, residuals)
        if "expected_photon" in case:
            photon = case["expected_photon"]
            expected_photon = {"qualification": "SYNTHETIC_SINGLE_ENERGY_PHOTON",
                               "count_per_event": Fraction(photon["count_per_event"]),
                               "energy_eV": Fraction(photon["energy_eV"]),
                               "energy_increment": Fraction(photon["energy_increment"]),
                               "energy_residual": Fraction(photon["energy_residual"])}
            check(case["id"] + ":photon_count", "radiation_count_identities", expected_photon,
                  observed["radiation_count"], case, {"energy": observed["radiation_count"]["energy_residual"]})
        else:
            check(case["id"] + ":photon_count_unspecified", "radiation_count_identities",
                  {"qualification": "UNQUALIFIED", "count_per_event": None, "energy_eV": None,
                   "energy_increment": None, "energy_residual": None}, observed["radiation_count"], case)
        if case["kind"] == "nuclear":
            check(case["id"] + ":energy_unqualified", "algebraic_nuclear", "UNQUALIFIED:ENERGY", observed["energy_status"], case)
        for rate in fixtures["rates"] + fixtures["signed_tangents"]:
            tangent = rate in fixtures["signed_tangents"]
            dx = ledger.source(case, species, rate, signed_tangent=tangent)
            expected_dx = {name: Fraction(n) * Fraction(rate) for name, n in expected["nu"].items()}
            identity = ledger.source_residuals(dx, species)
            expected_isotopes = {key: Fraction(value) * Fraction(rate) for key, value in expected["isotope_delta"].items() if Fraction(value) * Fraction(rate) != 0}
            actual_isotopes = {",".join(map(str, key)): value for key, value in identity["isotopes"].items() if value != 0}
            actual_identity = {"source": dx, "isotope_delta": actual_isotopes, "charge": identity["charge"], "baryon": identity["baryon"]}
            expected_identity = {"source": expected_dx, "isotope_delta": expected_isotopes, "charge": Fraction(0), "baryon": Fraction(0)}
            energy_residual = None
            if observed["energy"] is not None:
                internal_source = sum((Fraction(epsilon[name]) * value for name, value in dx.items()), Fraction(0))
                independent_reservoir_source = sum((Fraction(v) * Fraction(rate) for v in case["reservoirs"].values()), Fraction(0))
                energy_residual = internal_source + independent_reservoir_source
                actual_identity["energy"] = energy_residual
                expected_identity["energy"] = Fraction(0)
            check(case["id"] + (":JVP:" if tangent else ":source:") + rate,
                  "source_tangent_identities", expected_identity, actual_identity,
                  {"reaction": case, "rate": rate, "signed_tangent": tangent},
                  {"isotope_count": identity["isotopes"], "charge": identity["charge"], "energy": energy_residual})
            if "expected_photon" in case:
                photon = case["expected_photon"]
                actual_photon_source = ledger.radiation_source(case, rate, signed_tangent=tangent)
                expected_photon_source = {"qualification": "SYNTHETIC_SINGLE_ENERGY_PHOTON",
                                          "count_source": Fraction(photon["count_per_event"]) * Fraction(rate),
                                          "energy_source": Fraction(photon["energy_increment"]) * Fraction(rate),
                                          "energy_residual": Fraction(0)}
                check(case["id"] + ":photon_source:" + rate, "radiation_count_identities",
                      expected_photon_source, actual_photon_source, {"reaction": case, "rate": rate, "signed_tangent": tangent},
                      {"energy": actual_photon_source["energy_residual"]})
        if observed["energy"] is None:
            continue
        for index, shift in enumerate(fixtures["reference_shifts"]):
            lambdas = dict(shift)
            lambdas["isotopes"] = {tuple([int(p[0]), int(p[1]), p[2]]): value
                                    for key, value in shift["isotopes"].items() for p in [key.split(",")]}
            result = ledger.reference_delta(case, species, epsilon, "isotope_charge", lambdas)
            check(case["id"] + ":reference:" + str(index), "reference_identities",
                  {"original": Fraction(expected["delta_internal"]), "shifted": Fraction(expected["delta_internal"]), "residual": Fraction(0)},
                  result, {"reaction": case, "shift": shift}, {"energy": result["residual"]})
        rev = ledger.reverse(case)
        reverse_result = ledger.compile_reaction(rev, species, epsilon)
        expected_reverse = {"nu": {name: -value for name, value in expected["nu"].items()},
                            "Q": Fraction(expected["delta_internal"]),
                            "reservoirs": {name: -Fraction(value) for name, value in case["reservoirs"].items()},
                            "residual": Fraction(0)}
        actual_reverse = {"nu": reverse_result["nu"], "Q": reverse_result["energy"]["Q"],
                          "reservoirs": reverse_result["energy"]["reservoirs"], "residual": reverse_result["energy"]["residual"]}
        check(case["id"] + ":reverse", "reverse_identities", expected_reverse, actual_reverse, {"reaction": case, "reverse": rev}, {"energy": actual_reverse["residual"]})
        if "expected_photon" in case:
            photon = case["expected_photon"]
            expected_reverse_photon = {"qualification": "SYNTHETIC_SINGLE_ENERGY_PHOTON",
                                      "count_per_event": -Fraction(photon["count_per_event"]),
                                      "energy_eV": Fraction(photon["energy_eV"]),
                                      "energy_increment": -Fraction(photon["energy_increment"]),
                                      "energy_residual": Fraction(0)}
            check(case["id"] + ":photon_reverse", "radiation_count_identities", expected_reverse_photon,
                  reverse_result["radiation_count"], {"reaction": case, "reverse": rev},
                  {"energy": reverse_result["radiation_count"]["energy_residual"]})
        pair, orientation = ledger.reversible_pair_key(case, species)
        reverse_pair, reverse_orientation = ledger.reversible_pair_key(rev, species)
        check(case["id"] + ":pair_orientation", "event_identity", (pair, -orientation), (reverse_pair, reverse_orientation), {"reaction": case, "reverse": rev})

    def modified(case, **changes):
        result = copy.deepcopy(case)
        result.update(changes)
        return result

    pi = cases[0]
    swap = modified(pi, reactants=[["H1", 1]], products=[["D", 1]])
    rejection("reject_chemical_isotope_swap", lambda: ledger.conservation(swap, species), "ISOTOPE_NOT_CONSERVED", swap,
              {"isotope_count": {"1,1,ground": Fraction(-1), "1,2,ground": Fraction(1)}, "charge": Fraction(0), "energy": None})
    swap4 = modified(pi, reactants=[["H1", 1], ["He4", 1]], products=[["D", 1], ["He3", 1]])
    rejection("reject_element_baryon_preserving_isotope_swap", lambda: ledger.conservation(swap4, species), "ISOTOPE_NOT_CONSERVED", swap4)
    missing_e = modified(pi, products=[["H1p", 1]])
    rejection("reject_missing_electron", lambda: ledger.conservation(missing_e, species), "CHARGE_NOT_CONSERVED", missing_e,
              {"isotope_count": {"1,1,ground": Fraction(0)}, "charge": Fraction(1), "energy": None})
    double_e = modified(pi, products=[["H1p", 1], ["e_fast", 1], ["e_th", 1]])
    rejection("reject_double_electron", lambda: ledger.conservation(double_e, species), "CHARGE_NOT_CONSERVED", double_e,
              {"isotope_count": {"1,1,ground": Fraction(0)}, "charge": Fraction(-1), "energy": None})
    rejection("reject_neutralizing_source_duplication", lambda: ledger.neutralizing_diagnostic({}, species, True), "DUPLICATE_ELECTRON_SOURCE_RECONSTRUCTION", {"reconstructed_source": True})
    check("neutralizing_diagnostic_once", "guards", Fraction(0), ledger.neutralizing_diagnostic({"H1p": "2", "e_th": "1", "e_fast": "1"}, species), {"H1p": "2", "e_th": "1", "e_fast": "1"})
    bolometric = modified(pi, reservoirs={**pi["reservoirs"], "bolometric": "15"})
    energy = ledger.qualified_energy(bolometric, species, epsilon)
    check("reject_duplicate_bolometric_owner", "guards", Fraction(15), energy["residual"], bolometric,
          {"isotope_count": {"1,1,ground": Fraction(0)}, "charge": Fraction(0), "energy": energy["residual"]}, True)
    diagnostic = modified(pi, diagnostic_tallies={"bolometric": "15"})
    check("accept_diagnostic_bolometric", "guards", Fraction(0), ledger.qualified_energy(diagnostic, species, epsilon)["residual"], diagnostic, {"energy": Fraction(0)})
    unknown_eps = {**epsilon, "H1": "UNQUALIFIED"}
    check("unqualified_epsilon_not_zero", "guards", "UNQUALIFIED:EPSILON:H1", ledger.compile_reaction(pi, species, unknown_eps)["energy_status"], {"reaction": pi, "epsilon": unknown_eps}, intended_rejection=True)
    no_norm = modified(pi, normalization=None)
    rejection("unqualified_normalization", lambda: ledger.source(no_norm, species, "0"), "UNQUALIFIED:PROVIDER_NORMALIZATION", no_norm)
    no_provider = modified(pi, provider=None)
    rejection("missing_provider_is_not_supported_zero", lambda: ledger.source(no_provider, species, "0"), "UNQUALIFIED:MISSING_PROVIDER", no_provider)
    rejection("reject_negative_physical_rate", lambda: ledger.source(pi, species, "-2"), "NEGATIVE_PHYSICAL_RATE", {"reaction": pi, "rate": "-2"})
    alternate = modified(pi, provider="synthetic_alternative")
    rejection("reject_duplicate_ownership", lambda: ledger.register_ownership([pi, alternate], species), "OWNER_OVERLAP_UNRESOLVED:" + pi["ownership_slot"], [pi, alternate])
    inactive = modified(alternate, activation="alternative_inactive")
    check("accept_inactive_alternative", "guards", 1, len(ledger.register_ownership([pi, inactive], species)), [pi, inactive])
    for label, distinct in (("direction", ledger.reverse(pi)), ("process", modified(pi, process="distinct_process")),
                            ("energy_partition", modified(pi, energy_partition="separate_declared_partition")),
                            ("isotope", modified(pi, reactants=[["D", 1]], products=[["Dp", 1], ["e_fast", 1]]))):
        distinct["ownership_slot"] = pi["ownership_slot"]
        check("distinct_event_" + label, "event_identity", 2, len(ledger.register_ownership([pi, distinct], species)), [pi, distinct])
    formation = cases[3]
    catalyzed = modified(formation, reactants=[["H1", 2], ["e_th", 1]], products=[["H1H1", 1], ["e_th", 1]])
    check("catalyst_net_same", "event_identity", {"H1": -2, "H1H1": 1}, ledger.stoichiometry(catalyzed, species), catalyzed)
    check("catalyst_signature_distinct", "event_identity", False, ledger.directed_event_key(catalyzed, species) == ledger.directed_event_key(formation, species), [catalyzed, formation])
    doubled = modified(formation, reactants=[["H1", 4]], products=[["H1H1", 2]])
    check("doubled_event_not_gcd_reduced", "event_identity", {"H1": -4, "H1H1": 2}, ledger.stoichiometry(doubled, species), doubled)
    check("doubled_signature_distinct", "event_identity", False, ledger.directed_event_key(doubled, species) == ledger.directed_event_key(formation, species), [doubled, formation])
    permuted_species = dict(reversed(list(species.items())))
    enumerated = modified(formation, reactants=[["H1", 1], ["H1", 1]])
    check("species_and_enumeration_permutation", "event_identity", ledger.directed_event_key(formation, species), ledger.directed_event_key(enumerated, permuted_species), [formation, enumerated])
    multi = cases[5]
    permuted_reactants = modified(multi, reactants=list(reversed(multi["reactants"])), products=list(reversed(multi["products"])))
    check("reactant_order_permutation", "event_identity", ledger.directed_event_key(multi, species), ledger.directed_event_key(permuted_reactants, species), [multi, permuted_reactants])
    check("pool_changes_signature", "event_identity", False, species["e_th"].key() == species["e_fast"].key(), ["e_th", "e_fast"])
    changed_state = {**fixtures["species"]["H1"], "state": "distinct_synthetic_state"}
    check("state_changes_signature", "event_identity", False, species["H1"].key() == ledger.Species.from_record(changed_state).key(), changed_state)
    check("isomer_changes_signature_equal_energy", "event_identity", (False, True),
          (species["C12"].key() == species["C12m"].key(), epsilon["C12"] == epsilon["C12m"]), [fixtures["species"]["C12"], fixtures["species"]["C12m"]])
    ccase = next(c for c in cases if c["id"] == "12_C12C13_formation")
    cchanged = modified(ccase, reactants=[["C12m", 1], ["C13", 1]])
    check("isomer_changes_reaction_signature", "event_identity", False, ledger.directed_event_key(ccase, species) == ledger.directed_event_key(cchanged, species), [ccase, cchanged])
    invalid_charge = {**fixtures["species"]["H1"], "charge": 2}
    rejection("reject_charge_above_Z", lambda: ledger.Species.from_record(invalid_charge), "INVALID_MATERIAL_CHARGE_OR_COMPOSITION", invalid_charge)
    check("negative_ion_schema_only", "guards", -1, ledger.Species.from_record(fixtures["species"]["H1m"]).charge, {"species": fixtures["species"]["H1m"], "qualification": "SYNTHETIC_ONLY"})
    nuclear = cases[10]
    shift = {"charge": "2/3", "baryon": "5/7", "isotopes": {}}
    rejection("refuse_nuclear_isotope_reference", lambda: ledger.reference_delta(nuclear, species, epsilon, "isotope_charge", shift), "ISOTOPE_REFERENCE_NOT_APPLICABLE_TO_NUCLEAR", {"reaction": nuclear, "shift": shift})
    for index, shift in enumerate(fixtures["reference_shifts"]):
        result = ledger.reference_delta(nuclear, species, epsilon, "baryon_charge", shift)
        check("nuclear_algebra_baryon_charge_reference:" + str(index), "reference_identities", {"original": Fraction(0), "shifted": Fraction(0), "residual": Fraction(0)}, result,
              {"reaction": nuclear, "shift": shift, "qualification": "ALGEBRA_ONLY_NOT_NUCLEAR_Q"}, {"energy": result["residual"]})
    return {"baseline_populations": 21, "electron_rows": 2, "synthetic_extension_rows": 9,
            "catalog_rows": len(species), "physical_qualification": "NO_PHYSICAL_RATE_COVERAGE"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    fixtures = json.loads(Path(__file__).with_name("fixtures.json").read_text())
    rows, coverage, failure = [], None, None
    try:
        coverage = execute(fixtures, rows)
    except Exception as error:
        failure = {"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()}
    counts = {}
    for row in rows:
        counts[row["category"]] = counts.get(row["category"], 0) + 1
    result = {"schema": "REI_CHEM_LEDGER_RESULTS_V1", "status": "PASS" if failure is None else "FAIL",
              "checks_by_category": counts, "rows": rows, "catalog_coverage": coverage, "failure": failure,
              "claim_ceiling": "IMPLEMENTATION_CHECKED_FINITE_ISOTOPE_MOLECULAR_EVENT_INTERFACE_PENDING_INDEPENDENT_REVIEW",
              "global_physical_completion": None, "L4_ready": False,
              "physical_qualification": fixtures["physical_qualification"]}
    with (output / "results.json").open("x") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(json.dumps({"status": result["status"], "checks_by_category": counts, "failure": failure}))
    return int(failure is not None)


if __name__ == "__main__":
    raise SystemExit(main())
