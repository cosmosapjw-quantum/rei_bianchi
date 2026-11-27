#!/usr/bin/env python3
"""Bounded PHYS81 nuclear verifier; root must run it under the shared lease.

This script has no ODE, reaction rate, Maxwell average, stopping model, normal-
frame transport or external write.  It never writes reviewed source or data.
Its numerical oracle uses a 180-digit square root and bounded bisection of
E_gamma + sqrt(M_f^2 + E_gamma^2) = W, not the implementation's split formula.
The oracle is a high-precision numerical comparison, not an interval proof.
The output file is created exclusively to preserve the first run receipt.
"""
from __future__ import annotations

import argparse
from dataclasses import fields, FrozenInstanceError
from datetime import datetime, timezone
from decimal import (
    Context, Decimal, DivisionByZero, InvalidOperation, Overflow, ROUND_DOWN,
    ROUND_FLOOR, ROUND_HALF_EVEN, ROUND_UP, Underflow, localcontext,
)
import hashlib
import inspect
import json
from pathlib import Path
import sys
import traceback
from types import ModuleType
from unittest.mock import patch


D = Decimal
DEFAULT_UNIT = Path("/tmp/phys81_work_20261023/WU088_HH/research/hh_phys81_atomic_nuclear_source_contract_20261023")
THEORY = Path("/tmp/phys81_intake/nuclear_theory/NUCLEAR_RECOIL_THEORY_KO.md")
SELECTED_ROWS = Path("/tmp/phys81_intake/nuclear_theory/NIST_CODATA2022_RELEVANT_ROWS.txt")
EXPECTED_HASHES = {
    "source": "e8b7ad216113932d0844e424ca6e5e17dd644e07ca883e463c0c6c325c4fcf0e",
    "mass_table": "ee87900f698e59029a1aafce3d4184870ccc6fa16a8ba50326bd13a10de60aaf",
    "theory": "566b5cb4f2b704e9553d5aa558372599d65ffe9dcf9dda90ab28ae1cb09eba18",
    "selected_primary_rows": "b2c5b86f1d2e8068418d200d5e12d3b28e2bb8dc930f3ddecbcb905ed304abce",
}

# Independently transcribed from the supplied official-table row evidence.
# These are rounded CODATA recommendations, never exact physical masses.
# species: (A, Z, mass energy MeV, u(MeV), kg, u(kg))
EXPECTED_MASSES = {
    "n": (1, 0, "939.56542194", "0.00000048", "1.67492750056e-27", "0.00000000085e-27"),
    "p": (1, 1, "938.27208943", "0.00000029", "1.67262192595e-27", "0.00000000052e-27"),
    "d": (2, 1, "1875.61294500", "0.00000058", "3.3435837768e-27", "0.0000000010e-27"),
    "t": (3, 1, "2808.92113668", "0.00000088", "5.0073567512e-27", "0.0000000016e-27"),
    "h": (3, 2, "2808.39161112", "0.00000088", "5.0064127862e-27", "0.0000000016e-27"),
}
EXPECTED_REACTIONS = {
    "np_d_gamma": (("n", "p"), "d", (-1, -1, 1, 0, 0)),
    "nd_t_gamma": (("n", "d"), "t", (-1, 0, -1, 1, 0)),
    "pd_h_gamma": (("p", "d"), "h", (0, -1, -1, 0, 1)),
}
K_CASES = ("0", "1e-12", "0.001", "1", "1000")
ZETA_CASES = ("0", "0.5", "1")
SPECIES = ("n", "p", "d", "t", "h")


def oracle_context():
    return Context(prec=180, rounding=ROUND_HALF_EVEN, Emin=-999999, Emax=999999,
                   traps=[InvalidOperation, DivisionByZero, Overflow, Underflow])


class Recorder:
    def __init__(self):
        self.checks = []

    def check(self, name, condition, detail=None):
        row = {"name": name, "passed": bool(condition)}
        if detail is not None:
            row["detail"] = detail
        self.checks.append(row)

    def equal(self, name, actual, expected):
        self.check(name, actual == expected,
                   {"actual": str(actual), "expected": str(expected)})

    def close(self, name, actual, expected, scale=None):
        with localcontext(oracle_context()):
            scale = max(D(1), abs(expected)) if scale is None else max(D(1), abs(scale))
            # A fixed 128 nominal last-place units at 80 significant digits.
            # The scale is explicitly recorded, including MeV^2 for invariants.
            tolerance = D(128) * D(1).scaleb(scale.adjusted() + 1 - 80)
            error = abs(actual - expected)
            self.check(name, error <= tolerance, {
                "actual": str(actual), "expected": str(expected),
                "absolute_error": str(error), "scale": str(scale),
                "absolute_tolerance": str(tolerance),
            })

    def reject(self, name, callback, expected_exception, message=None):
        try:
            callback()
        except Exception as exc:
            self.check(name, isinstance(exc, expected_exception) and
                       (message is None or message in str(exc)),
                       {"exception": type(exc).__name__, "message": str(exc)})
        else:
            self.check(name, False, {"exception": None})


def independent_reference(reaction_id, kinetic):
    reactants, product, _ = EXPECTED_REACTIONS[reaction_id]
    with localcontext(oracle_context()):
        initial = sum((D(EXPECTED_MASSES[s][2]) for s in reactants), D(0))
        final = D(EXPECTED_MASSES[product][2])
        W = initial + kinetic
        low, high = D(0), W - final
        # Solve the un-squared energy equation directly.  p*c = E_gamma.
        for iterations in range(1, 641):
            midpoint = (low + high) / 2
            if midpoint == low or midpoint == high:
                break
            residual = midpoint + (final * final + midpoint * midpoint).sqrt() - W
            if residual == 0:
                low = high = midpoint
                break
            if residual < 0:
                low = midpoint
            else:
                high = midpoint
        photon = (low + high) / 2
        recoil = (final * final + photon * photon).sqrt() - final
        return {
            "initial": initial, "final": final, "Q": initial - final, "W": W,
            "available": W - final, "photon": photon, "recoil": recoil,
            "iterations": iterations, "last_bracket_width": high - low,
            "reference_energy_residual": photon + final + recoil - W,
        }


def source_and_counts(module, record):
    masses = module.load_nuclear_masses()
    record.equal("species_order", module.SPECIES_ORDER, SPECIES)
    record.equal("species_set", set(masses), set(EXPECTED_MASSES))
    record.equal("source_pin_exposed", module.SOURCE_SHA256, EXPECTED_HASHES["mass_table"])
    for species, expected in EXPECTED_MASSES.items():
        mass = masses[species]
        actual = (mass.A, mass.Z, mass.energy_equivalent_MeV,
                  mass.standard_uncertainty_MeV, mass.mass_kg, mass.standard_uncertainty_kg)
        wanted = (*expected[:2], *(D(x) for x in expected[2:]))
        record.equal("mass_row." + species, actual, wanted)
    record.equal("predefined_channels_only", set(module.REACTIONS), set(EXPECTED_REACTIONS))
    for name, (reactants, product, stoich) in EXPECTED_REACTIONS.items():
        reaction = module.REACTIONS[name]
        record.equal(name + ".reactants_product", (reaction.reactants, reaction.product), (reactants, product))
        record.equal(name + ".stoichiometry", reaction.stoichiometry, stoich)
        baryons = sum(EXPECTED_MASSES[s][0] * nu for s, nu in zip(SPECIES, reaction.stoichiometry))
        charge = sum(EXPECTED_MASSES[s][1] * nu for s, nu in zip(SPECIES, reaction.stoichiometry))
        total = sum(reaction.stoichiometry)
        record.equal(name + ".independent_A_Z_nucleus_count", (baryons, charge, total), (0, 0, -1))
        record.equal(name + ".declared_counts", (
            reaction.delta_baryon_number, reaction.delta_nuclear_charge,
            reaction.delta_nuclear_particle_count, reaction.delta_derived_electron_count,
        ), (0, 0, -1, 0))
    record.reject("source_rows_immutable", lambda: masses.__setitem__("n", None), (TypeError, AttributeError))
    record.reject("source_row_fields_immutable", lambda: setattr(masses["n"], "A", 2), FrozenInstanceError)


def kinematics_and_partitions(module, record):
    summaries = []
    for reaction_id in EXPECTED_REACTIONS:
        for kinetic_text in K_CASES:
            kinetic = D(kinetic_text)
            prefix = reaction_id + ".K=" + kinetic_text
            ref = independent_reference(reaction_id, kinetic)
            event = module.capture_kinematics(reaction_id, incident_com_kinetic_MeV=kinetic)
            record.check(prefix + ".bounded_reference_converged", ref["iterations"] < 640)
            record.equal(prefix + ".incident_K", event.incident_com_kinetic_MeV, kinetic)
            for attr, key in (("initial_rest_energy_MeV", "initial"), ("final_rest_energy_MeV", "final"),
                              ("Q_MeV", "Q"), ("W_MeV", "W"), ("available_energy_MeV", "available")):
                record.equal(prefix + "." + attr, getattr(event, attr), ref[key])
            record.close(prefix + ".sqrt_root_photon", event.photon_energy_MeV, ref["photon"])
            record.close(prefix + ".sqrt_root_recoil", event.recoil_kinetic_MeV, ref["recoil"])
            with localcontext(oracle_context()):
                photon, recoil, final, W = event.photon_energy_MeV, event.recoil_kinetic_MeV, ref["final"], ref["W"]
                record.close(prefix + ".un_squared_energy_conservation",
                             photon + (final * final + photon * photon).sqrt() - W, D(0), W)
                record.close(prefix + ".mass_shell_momentum_invariant",
                             (final + recoil) ** 2 - photon ** 2 - final ** 2, D(0), W ** 2)
                record.close(prefix + ".independent_energy_split", photon + recoil, ref["available"], W)
                record.close(prefix + ".reported_split_roundoff", event.split_roundoff_MeV, D(0), W)
                record.check(prefix + ".positive_two_body_energies", D(0) < photon < W / 2 and recoil > 0)
            record.equal(prefix + ".event_source_identity", event.source_sha256, EXPECTED_HASHES["mass_table"])
            for zeta_text in ZETA_CASES:
                zeta = D(zeta_text)
                label = prefix + ".zeta=" + zeta_text
                part = module.partition_event(reaction_id, zeta=zeta, incident_com_kinetic_MeV=kinetic)
                with localcontext(oracle_context()):
                    # Reference recoil comes from the independent square-root solve.
                    expectations = {
                        "delta_rest_MeV": -ref["Q"],
                        "delta_thermal_MeV": zeta * ref["recoil"] - kinetic,
                        "delta_nonthermal_MeV": (1 - zeta) * ref["recoil"],
                        "delta_photon_MeV": ref["photon"],
                    }
                    for attr, expected in expectations.items():
                        record.close(label + "." + attr, getattr(part, attr), expected)
                    record.close(label + ".independent_ledger_sum",
                                 part.delta_rest_MeV + part.delta_thermal_MeV +
                                 part.delta_nonthermal_MeV + part.delta_photon_MeV, D(0), W)
                    record.close(label + ".reported_closure_roundoff", part.closure_residual_MeV, D(0), W)
                    record.equal(label + ".stored_zeta", part.zeta, zeta)
                    if zeta == 0:
                        record.equal(label + ".full_incident_K_debit", part.delta_thermal_MeV, -kinetic)
                    if zeta == 1:
                        record.equal(label + ".no_retained_recoil", part.delta_nonthermal_MeV, D(0))
            summaries.append({"reaction": reaction_id, "K_MeV": kinetic_text,
                              "Q_MeV": str(event.Q_MeV), "photon_MeV": str(event.photon_energy_MeV),
                              "recoil_MeV": str(event.recoil_kinetic_MeV),
                              "oracle_iterations": ref["iterations"],
                              "oracle_energy_residual_MeV": str(ref["reference_energy_residual"]),
                              "oracle_last_bracket_width_MeV": str(ref["last_bracket_width"])})
    return summaries


def guards_and_ownership(module, record):
    for index, reaction in enumerate(("", "pp_d_gamma", "np_d", None, [], 1, True)):
        record.reject("unknown_channel." + str(index), lambda r=reaction: module.capture_kinematics(r), ValueError)
    invalid_K = (-1, "-1e-900", True, False, None, [], {}, 1j, "NaN", "sNaN", "Infinity",
                 "-Infinity", "not-a-decimal", "", float("nan"), float("inf"))
    for index, value in enumerate(invalid_K):
        record.reject("invalid_K." + str(index),
                      lambda v=value: module.capture_kinematics("np_d_gamma", incident_com_kinetic_MeV=v), ValueError)
    for value in ("1e200", "1e1000000"):
        record.reject("unresolved_or_out_of_range_K." + value,
                      lambda v=value: module.capture_kinematics("np_d_gamma", incident_com_kinetic_MeV=v), ArithmeticError)
    invalid_zeta = ("-0.001", "1.0001", True, False, None, [], 1j, "NaN", "sNaN", "Infinity", "bad")
    for index, value in enumerate(invalid_zeta):
        record.reject("invalid_zeta." + str(index),
                      lambda v=value: module.partition_event("np_d_gamma", zeta=v), ValueError)
    record.reject("zeta_must_be_explicit", lambda: module.partition_event("np_d_gamma"), TypeError)
    record.reject("deposition_underflow_is_rejected",
                  lambda: module.partition_event("np_d_gamma", zeta="1e-1000200"), ArithmeticError)
    signature = inspect.signature(module.partition_event)
    record.check("zeta_required_keyword_only", signature.parameters["zeta"].default is inspect.Parameter.empty
                 and signature.parameters["zeta"].kind is inspect.Parameter.KEYWORD_ONLY)
    expected_metadata = {
        "thermal_particle_number_ownership": "unassigned", "physical_mass_values_exact": False,
        "empirical_rate_available": False, "nuclear_ode_available": False,
        "normal_frame_source_adapter_available": False, "finite_temperature_average_available": False,
        "HH_R10": "OFF", "production_admission": "NOT_ISSUED",
    }
    for name, value in expected_metadata.items():
        record.equal("scope_metadata." + name, module.API_METADATA.get(name), value)
    for klass in (module.CaptureReaction, module.CaptureKinematics, module.CaptureEventPartition):
        field_names = tuple(field.name for field in fields(klass))
        record.check("no_silent_thermal_number." + klass.__name__,
                     not any("thermal_particle" in name or "bath" in name for name in field_names), field_names)
    float_event = module.capture_kinematics("np_d_gamma", incident_com_kinetic_MeV=0.125)
    string_event = module.capture_kinematics("np_d_gamma", incident_com_kinetic_MeV="0.125")
    record.equal("documented_float_string_semantics", float_event, string_event)


def context_snapshot(context):
    return {"prec": context.prec, "rounding": context.rounding, "Emin": context.Emin,
            "Emax": context.Emax, "capitals": context.capitals, "clamp": context.clamp,
            "traps": {key.__name__: value for key, value in context.traps.items()},
            "flags": {key.__name__: value for key, value in context.flags.items()}}


def caller_context_independence(module, record):
    fixtures = (("np_d_gamma", "0"), ("nd_t_gamma", "0.001"), ("pd_h_gamma", "1"))
    baseline = [module.capture_kinematics(r, incident_com_kinetic_MeV=k) for r, k in fixtures]
    baseline_partition = module.partition_event("pd_h_gamma", zeta="0.5", incident_com_kinetic_MeV="1")
    profiles = ((2, ROUND_FLOOR, -2, 2, True, False),
                (7, ROUND_UP, -6, 6, False, True),
                (28, ROUND_DOWN, -999, 999, True, True))
    for index, (precision, rounding, emin, emax, traps, flags) in enumerate(profiles):
        with localcontext() as caller:
            caller.prec, caller.rounding, caller.Emin, caller.Emax = precision, rounding, emin, emax
            for signal in caller.traps:
                caller.traps[signal] = traps
                caller.flags[signal] = flags
            before = context_snapshot(caller)
            actual = [module.capture_kinematics(r, incident_com_kinetic_MeV=k) for r, k in fixtures]
            actual_partition = module.partition_event("pd_h_gamma", zeta="0.5", incident_com_kinetic_MeV="1")
            record.equal("caller_context." + str(index) + ".kinematics", actual, baseline)
            record.equal("caller_context." + str(index) + ".partition", actual_partition, baseline_partition)
            record.equal("caller_context." + str(index) + ".state_unchanged", context_snapshot(caller), before)
    # Rejected malformed text is recorded separately: parsing is outside the
    # implementation's fresh arithmetic context.  This is not a valid-output test.
    rejected_input_observations = []
    for invalid_trap in (False, True):
        with localcontext() as caller:
            caller.clear_flags()
            caller.traps[InvalidOperation] = invalid_trap
            try:
                module.capture_kinematics("np_d_gamma", incident_com_kinetic_MeV="not-a-decimal")
            except Exception as exc:
                record.check("malformed_text_rejected.trap=" + str(invalid_trap), isinstance(exc, ValueError))
                rejected_input_observations.append({"InvalidOperation_trap": invalid_trap,
                    "exception": type(exc).__name__, "message": str(exc),
                    "caller_InvalidOperation_flag": caller.flags[InvalidOperation]})
            else:
                record.check("malformed_text_rejected.trap=" + str(invalid_trap), False)
    return rejected_input_observations


def source_identity_guards(module, record, mass_path, mass_bytes):
    # In-memory read substitution exercises a changed file on the next API
    # call, including after earlier successful loads.  No file is modified.
    with patch.object(module.Path, "read_bytes", return_value=mass_bytes + b"\n"):
        for name, callback in (
            ("loader", module.load_nuclear_masses),
            ("kinematics", lambda: module.capture_kinematics("np_d_gamma")),
            ("partition", lambda: module.partition_event("np_d_gamma", zeta="0.5")),
        ):
            record.reject("source_tamper_rejected." + name, callback, ValueError, "SOURCE_IDENTITY_MISMATCH")
    record.equal("source_bytes_remain_unchanged", mass_path.read_bytes(), mass_bytes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit", type=Path, default=DEFAULT_UNIT)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit("Refusing to overwrite a completed or failed first-run receipt: " + str(args.out))
    record = Recorder()
    paths = {"source": args.unit / "source/nuclear_recoil.py",
             "mass_table": args.unit / "source_data/NUCLEAR_MASSES_CODATA2022.json",
             "theory": THEORY, "selected_primary_rows": SELECTED_ROWS}
    report = {"schema": "PHYS81_INDEPENDENT_NUCLEAR_VERIFIER_V1",
              "started_utc": datetime.now(timezone.utc).isoformat(),
              "execution_scope": "bounded new component validation; no ODE/rate/finite-T/stopping/transport",
              "lease": "acquisition and release are owned by the parent runner, not this script",
              "oracle": "180-digit Decimal square root plus at most 640 bisections per event",
              "oracle_independence": "no call to production formulas or intermediate outputs for reference energies",
              "oracle_is_interval_certificate": False,
              "mass_uncertainty_propagated": False,
              "mass_source_scope": "pinned saved transcription; official source retrieval evidence reused",
              "K_cases_MeV": K_CASES, "zeta_cases": ZETA_CASES,
              "planned_independent_reference_cases": 15, "planned_partition_cases": 45,
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "reviewed_hashes": {}, "checks": record.checks}
    try:
        payloads = {key: path.read_bytes() for key, path in paths.items()}
        for key, payload in payloads.items():
            digest = hashlib.sha256(payload).hexdigest()
            report["reviewed_hashes"][key] = {"path": str(paths[key]), "sha256": digest}
            record.equal("reviewed_identity." + key, digest, EXPECTED_HASHES[key])
        if not all(item["passed"] for item in record.checks):
            raise RuntimeError("REVIEWED_IDENTITY_CHANGED: no numerical checks are admitted for these bytes")
        module = ModuleType("phys81_reviewed_nuclear_component")
        module.__file__ = str(paths["source"].resolve())
        sys.modules[module.__name__] = module
        exec(compile(payloads["source"], module.__file__, "exec"), module.__dict__)
        source_and_counts(module, record)
        report["event_results"] = kinematics_and_partitions(module, record)
        guards_and_ownership(module, record)
        report["malformed_input_context_observations"] = caller_context_independence(module, record)
        source_identity_guards(module, record, paths["mass_table"], payloads["mass_table"])
    except Exception as exc:
        report["uncaught_exception"] = {"type": type(exc).__name__, "message": str(exc),
                                        "traceback": traceback.format_exc()}
        record.check("verifier_completed_without_uncaught_exception", False)
    report["finished_utc"] = datetime.now(timezone.utc).isoformat()
    report["checks_passed"] = sum(item["passed"] for item in record.checks)
    report["checks_failed"] = sum(not item["passed"] for item in record.checks)
    report["passed"] = report["checks_failed"] == 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False, default=str)
        stream.write("\n")
    print(json.dumps({"passed": report["passed"], "checks_passed": report["checks_passed"],
                      "checks_failed": report["checks_failed"], "receipt": str(args.out)}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
