"""Bounded receipt intake, not a physics implementation or admission token."""

import math
import hashlib
from decimal import Decimal

REACTION = "R_CX:He2+_H1s:He+1s_H+"
CLOSURE = "EXPLICIT_CONDITIONAL_ESCAPE_MEAN_ENERGY_V1"
ORIGIN = "CALLER_SUPPLIED_NO_ATOMIC_MOMENT"
ORDER = ["HI", "HII", "HeI", "HeII", "HeIII", "e"]
NU = [-1, 1, 0, 1, -1, 0]
PROFILES = [
    ("KF96_HEIII_HI_RCT_NOMINAL_V1", "kf", "1.00E-14", 1000, 10000000,
     "0e7c8a846112e14ec8d761fe7b9d978e65b4c30456e0d31829c52724e91a4ff6"),
    ("GM25_W82_RCX_CONSTANT_200_10000_K_V1", "gm", "1.70E-13", 200, 10000,
     "529ae325622718b48292c3b748a7850ccb315733b28bff930388f00915f2d217"),
]


def expect(actual, expected, label):
    # In particular, JSON zero is not a false admission flag or a null moment.
    if type(actual) is not type(expected) or actual != expected:
        raise ValueError(label)


def fields(record, expected, label):
    for key, value in expected.items():
        if key not in record:
            raise ValueError(f"{label}.{key}: missing")
        expect(record[key], value, f"{label}.{key}")


def verify_saved(base, observations):
    """Verify saved input bytes before interpreting any imported receipt."""
    for item in observations:
        if not item.get("local_path"):
            continue
        expect(item["status"], 200, "input fetch status")
        try:
            value = (base / item["local_path"]).read_bytes()
        except OSError as exc:
            raise ValueError(f"missing input: {item['local_path']}") from exc
        expect(hashlib.sha256(value).hexdigest(), item["sha256"], item["local_path"])


def validate(bundle):
    """Accept this delivered contract only; a changed contract needs new intake."""
    try:
        r, p, t = (bundle[k] for k in ("return", "providers", "theory"))
        fields(r, {"schema": "rei.he-f2-consumer-return.v1", "recipient_task": "HE-F2",
                   "HE_F2_completion_asserted_by_sender": False}, "return")
        fields(r["selection"], {"default": "OFF", "source_addition": False,
               "automatic_source_switch": False, "physical_admission": False,
               "primary_explicit_profile": PROFILES[0][0], "alternative": PROFILES[1][0],
               "paired_window_K": [1000, 10000], "new_FT03_guard_K": [30000, 110000],
               "GM25_with_new_FT03": "ERROR_OUTSIDE_SOURCE_DOMAIN"}, "selection")
        fields(r["implementation"], {"default_OFF_baseline": True,
               "FT03_base_rhs": "actual ft03_rhs with original temperature-dependent HG RR/CI/DR",
               "production_HHe_stepper_RCT_integration": False,
               "production_FT03_stepper_RCT_integration": False,
               "FT03_strict_underflow_representability_inherited_by_RCT": False}, "implementation")
        fields(r["closure"], {"id": CLOSURE, "input_origin": ORIGIN,
               "required_mean_energy_eV": "finite positive explicit input",
               "chemical": "-Q*R*eV_erg", "thermal": "(Q-Ebar)*R*eV_erg",
               "escaped": "Ebar*R*eV_erg", "primary_tracked_photon_injection": [0, 0, 0],
               "source_photon_moment": None, "source_heat_moment": None,
               "source_recoil_moment": None, "source_spectrum": None,
               "physical_admission": False}, "closure")
        fields(t["reaction"], {"id": REACTION, "species_order": ORDER, "stoichiometry": NU,
                              "primary_photon_count_per_event": 1}, "reaction")
        fields(t["closures"]["CountOnly"], {"thermal": None, "escaped_energy": None,
               "group_spectrum": None, "thermal_solver_admissible": False}, "CountOnly")
        fields(p["selection_policy"], {"default": "OFF", "mutual_exclusion": True,
                                       "same_reaction_sum_forbidden": True}, "policy")
        expect(len(p["records"]), 2, "provider count")
        for record, (pid, packet_key, coefficient, lo, hi, core) in zip(p["records"], PROFILES):
            fields(record, {"provider_id": pid, "process_id": REACTION,
                   "observable_kind": "thermal_rate", "units": "cm3 s-1",
                   "particle_distribution": "MAXWELL_COMMON_T_ZERO_DRIFT",
                   "species_in": {"HI": 1, "HeIII": 1}, "species_out": {"HII": 1, "HeII": 1},
                   "density_prefactor": "n_HI_proper_cm^-3 * n_HeIII_proper_cm^-3",
                   "consumer_admission": False, "physical_accuracy_certified": False,
                   "baseline_global_rct_enabled": False, "alternatives_are_additive": False,
                   "closure_id": CLOSURE}, pid)
            fields(record["domain"], {"minimum": lo, "maximum": hi, "units": "K"}, pid)
            fields(record["coefficient"], {"token": coefficient, "native_unit": "cm3 s-1",
                   "si_unit": "m3 s-1", "cgs_to_si_exact_factor": "1E-6"}, pid)
            expect(Decimal(record["coefficient"]["si_token"]), Decimal(coefficient)*Decimal("1E-6"), pid)
            fields(record["source_identity"], {"sha256": core, "sha256_kind": "supplier_code_not_paper",
                   "supplier_commit": r["producer_input"]["code_pin"]}, pid)
            fields(record["separate_event_stoichiometry"], {"species_order": ORDER,
                   "nu": NU, "density_applied": False}, pid)
            fields(record["energy_photon_closure"], {"status": "unresolved",
                   "source_photon_energy_moment_eV": None, "source_heat_moment_eV": None,
                   "source_recoil_moment_eV": None, "source_spectrum": None}, pid)
            packet = bundle[packet_key]
            fields(packet["request"], {"source_id": pid, "quantity": "thermal_rate"}, pid)
            fields(packet["source"], {"core_sha256": core, "physical_accuracy_certified": False}, pid)
            for rate in packet["records"]:
                fields(rate, {"source_id": pid, "unit": "m3 s-1", "photon_energy_moment": None,
                       "heat_moment": None, "recoil_moment": None}, pid)
                expect(Decimal(rate["rate_token"]), Decimal(coefficient)*Decimal("1E-6"), pid)
        final, review = bundle["final"], bundle["review"]
        fields(final, {"status": "PASS", "native_test_count": 116,
               "upstream_parent": r["publication"]["parent"]}, "final")
        expect([run["id"] for run in final["runs"]],
               ["final_crate", "independent_rct", "independent_ft03_rct"], "run IDs")
        for run in final["runs"]:
            expect(run["exit_code"], 0, "inherited run failed")
        fields(review, {"schema": "rei.he-rct-post-ft03-review.v1", "verdict": "confirmed",
               "open_blockers": 0, "source_parent": final["upstream_parent"]}, "review")
        identities = {item["path"]: item["sha256"] for item in final["file_identities"]}
        expect(len(identities), 9, "final identity count")
        reviewed = {item["path"]: item["sha256"] for item in review["source_identity_matches"]}
        expect(reviewed, identities, "final review identities")
        for key, oracle, count, calls in [("e2", "research/independent_rct_check.py", 12789, 422),
                                          ("e2x", "research/independent_ft03_rct_check.py", 212, 12)]:
            fields(bundle[key], {"status": "PASS", "failures": [], "native_exit_code": 0,
                   "checks": count, "native_calls": calls, "tolerance": "2E-12",
                   "oracle_sha256": identities[oracle],
                   "native_binary_sha256": identities["coding/rei_crate/target/debug/examples/he_rct_probe"]}, key)
        expect(len(bundle["cases"]), 9, "FT03 case count")
        for case in bundle["cases"]:
            native = case["native"]
            fields(native, {"ok": True, "kind": "ft03", "source": "KF96"}, "FT03 case")
            value = native["mean_escaped_photon_energy_ev"]
            if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                raise ValueError("finite positive Ebar required")
            fields(case, {"mean_origin": "RCT-E2X_SYNTHETIC_Q_OFFSET"}, "scenario")
            fields(native, {"closure_input_origin": ORIGIN, "physical_admission": False}, "scenario")
        return {"accepted": True, "scope": "EXPLICIT_CONDITIONAL_LOCAL_RHS_ONLY",
                "physical_admission": False, "time_integrator_admission": False,
                "baseline_RCT": "OFF", "uniform_underflow_certificate": False}
    except (KeyError, TypeError, ArithmeticError) as exc:
        raise ValueError(f"incomplete or malformed intake: {exc}") from exc
