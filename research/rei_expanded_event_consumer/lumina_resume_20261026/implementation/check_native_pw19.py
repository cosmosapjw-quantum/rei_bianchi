"""Selected scientific assertions for one PW19 node and one HeII channel."""
import json
import math
import os
from pathlib import Path

import native_pw19_moments as native


def run():
    result = native.calculate()
    checks = []

    def check(name, residual, limit):
        passed = math.isfinite(residual) and residual <= limit
        checks.append({"name": name, "residual": residual, "limit": limit, "pass": passed})

    def relative(a, b):
        assert b > 0 and math.isfinite(b)
        return abs(a-b)/b

    def rejects(call, exception):
        try:
            call()
        except exception:
            return True
        return False

    parts = result["partition_moments"]
    late = result["late_band_moments"]
    full = result["full_atomic_moments"]
    for i, p in enumerate(parts):
        check(f"partition_{i}_finite_nonnegative", 0.0 if all(math.isfinite(p[k]) and p[k] >= 0 for k in native.FIELDS) else math.inf, 0.0)
        check(f"partition_{i}_positive_denominators", 0.0 if all(p[k] > 0 for k in native.FIELDS) else math.inf, 0.0)
        q = result["quadrature_residuals"][i]
        for k, v in q["GL8_GL16_relative"].items():
            check(f"partition_{i}_{k}_GL8_GL16", v, 2e-11)
        for k, v in q["GL16_analytic_relative"].items():
            check(f"partition_{i}_{k}_analytic", v, 2e-11)
        check(f"partition_{i}_absorption_energy", relative(p["A_eV_s"], native.CHI*p["Gamma_s"]+p["K_eV_s"]), 2e-14)
    for title, total, selected in (("late", late, parts[:2]), ("full", full, parts)):
        for key in native.FIELDS:
            check(f"{title}_{key}_additivity", relative(math.fsum(p[key] for p in selected), total[key]), 2e-14)
        check(f"{title}_absorption_energy", relative(total["A_eV_s"], native.CHI*total["Gamma_s"]+total["K_eV_s"]), 2e-14)

    ledgers = result["radiation_exposure_outside_atomic"]
    finite = result["finite_table_exposure"]
    for key, moment in (("Phi_cm2_s", "number_cm2_s"), ("Psi_eV_cm2_s", "energy_eV_cm2_s")):
        summed = math.fsum((ledgers["below_threshold"][moment], full[key], ledgers["above_atomic_domain"][moment]))
        check(f"finite_table_{key}_additivity", relative(summed, finite[moment]), 2e-14)
    check("below_threshold_physical_zero", 0.0 if ledgers["below_threshold"]["HeII_primary_Gamma_s"] == 0.0 else math.inf, 0.0)
    check("above_atomic_unknown_null", 0.0 if ledgers["above_atomic_domain"]["HeII_primary_Gamma_s"] is None else math.inf, 0.0)
    check("positive_excluded_tail", 0.0 if result["kinetic_support_eV"]["first_partition_excluded_positive_tail"]["Gamma_s"] > 0 else math.inf, 0.0)

    old = result["lumina_late"]
    check("frozen_late_HeII_only", 0.0 if old["active_species"] == ("HeII",) and old["inactive_HI_HeI_rates"] == [None, None] else math.inf, 0.0)
    check("lumina_Gamma_operator", relative(old["Gamma_s"], late["Phi_cm2_s"]*old["sigma_cm2"]), 2e-14)
    check("lumina_K_operator", relative(old["K_eV_s"], old["Gamma_s"]*old["excess_eV"]), 2e-14)
    check("lumina_absorption_identity", relative(old["A_eV_s"], native.CHI*old["Gamma_s"]+old["K_eV_s"]), 2e-14)
    check("template_defects_finite", 0.0 if all(math.isfinite(v) for v in result["template_signed_relative_defect"].values()) else math.inf, 0.0)

    gamma, kinetic = late["Gamma_s"], late["K_eV_s"]
    fixture = result["local_fixture"]
    r = fixture["residual"]
    species = r["species_cm3_s"]
    j = gamma
    check("He_nuclei_left_null", abs(math.fsum(species[2:5]))/j, 2e-14)
    check("charge_left_null", abs(math.fsum((species[1], species[3], 2*species[4], -species[5])))/j, 2e-14)
    check("electron_source", relative(species[5], j), 2e-14)
    absorbed_power = (native.CHI*gamma+kinetic)*native.pw19.EV_ERG
    check("total_energy_left_null", abs(math.fsum((r["ion_erg_cm3_s"], r["primary_erg_cm3_s"], r["external_radiation_erg_cm3_s"])))/absorbed_power, 2e-14)
    check("zero_density_exact", 0.0 if all(v == 0 for v in native.local_residual(0, gamma, kinetic)["species_cm3_s"]) and all(native.local_residual(0, gamma, kinetic)[k] == 0 for k in ("ion_erg_cm3_s", "primary_erg_cm3_s", "external_radiation_erg_cm3_s")) else math.inf, 0.0)
    check("zero_density_finite_JVP", 0.0 if all(math.isfinite(v) for v in native.local_tangent(.3, gamma, kinetic)["species_cm3_s"]) else math.inf, 0.0)
    h = 1e-4
    tangent = fixture["density_JVP"]
    plus, minus = (native.local_residual(1+h, gamma, kinetic), native.local_residual(1-h, gamma, kinetic))
    for i in (3, 4, 5):
        finite_difference = .3*(plus["species_cm3_s"][i]-minus["species_cm3_s"][i])/(2*h)
        check(f"species_{i}_JVP", abs(finite_difference-tangent["species_cm3_s"][i])/(.3*j), 2e-11)
    for key in ("ion_erg_cm3_s", "primary_erg_cm3_s", "external_radiation_erg_cm3_s"):
        finite_difference = .3*(plus[key]-minus[key])/(2*h)
        check(f"{key}_JVP", abs(finite_difference-tangent[key])/abs(tangent[key]), 2e-11)

    si = result["SI_handoff"]
    check("SI_Phi_sigma_rate", relative(si["incident_photon_exposure_m2_s"]*si["effective_sigma_m2"], si["Gamma_s"]), 2e-14)
    check("SI_density_primary_power", relative(si["fixture_n_HeII_m3"]*si["K_J_s_per_target"], si["fixture_primary_W_m3"]), 2e-14)
    check("SI_density_absorption_power", relative(si["fixture_n_HeII_m3"]*si["A_J_s_per_target"], -si["fixture_external_radiation_W_m3"]), 2e-14)
    check("SI_cgs_ion_conversion", relative(si["fixture_ion_W_m3"], r["ion_erg_cm3_s"]*.1), 2e-14)
    check("SI_cgs_radiation_conversion", relative(-si["fixture_external_radiation_W_m3"], -r["external_radiation_erg_cm3_s"]*.1), 2e-14)
    check("SI_number_residual_conversion", 0.0 if all(a == b*1e6 for a, b in zip(si["fixture_species_m3_s"], species)) else math.inf, 0.0)
    unknowns = result["uncertainty_ledger"]
    check("unknown_uncertainties_remain_null", 0.0 if all(unknowns[k] is None for k in ("provider_uncertainty", "physical_model_uncertainty", "interpolation_error_relative_to_unprovided_continuum", "global_physical_error_bound")) else math.inf, 0.0)

    atom = native.pw19.Verner96.from_table("HeII")
    check("reject_unlisted_z20", 0.0 if rejects(lambda: native.pw19.PW19Spectrum(20), ValueError) else math.inf, 0.0)
    check("reject_negative_density", 0.0 if rejects(lambda: native.local_residual(-1, gamma, kinetic), ValueError) else math.inf, 0.0)
    check("reject_above_atomic", 0.0 if rejects(lambda: atom.sigma_cm2(ATOMIC_HIGH_PLUS), ValueError) else math.inf, 0.0)
    check("reject_late_band_150eV_injection", 0.0 if rejects(lambda: native.certify_kinetic_grid(native.LATE_HIGH), native.lumina.DomainError) else math.inf, 0.0)
    check("reject_native_full_150eV_injection", 0.0 if rejects(lambda: native.certify_kinetic_grid(native.ATOMIC_HIGH), native.lumina.DomainError) else math.inf, 0.0)
    check("first_submeasure_grid_support", relative(native.certify_kinetic_grid(native.ELECTRON_CUT), 150), 2e-14)
    check("below_HeII_threshold_atomic_zero", 0.0 if atom.sigma_cm2(54.41) == 0.0 else math.inf, 0.0)
    return result, {"check_count": len(checks), "passed": all(c["pass"] for c in checks), "checks": checks,
                    "scope": "one PW19 z=2.479 HeII native source; no IVP or historic suite"}


ATOMIC_HIGH_PLUS = native.ATOMIC_HIGH + 1.0

if __name__ == "__main__":
    output = Path(os.environ["PW19_OUTPUT_DIR"])
    result, validation = run()
    (output / "MOMENTS.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    (output / "CHECKS.json").write_text(json.dumps(validation, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"passed": validation["passed"], "check_count": validation["check_count"],
                      "failed": [c for c in validation["checks"] if not c["pass"]]}, allow_nan=False))
    raise SystemExit(0 if validation["passed"] else 1)
