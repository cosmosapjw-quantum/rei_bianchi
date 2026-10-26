"""One native PW19 HeII source node and its local conservative moment map.

The existing pinned provider supplies the spectrum and atomic cross section;
this module integrates only the selected finite support, without evolving gas.
"""
from __future__ import annotations

import math
from pathlib import Path
import sys

UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT / "intake" / "provider"))
sys.path.insert(0, str(UNIT.parent / "lumina_20261027" / "implementation"))
import spectral_photo_source as pw19
import lumina_adapter as lumina

CHI = 54.42
ELECTRON_CUT = 204.42
LATE_HIGH = 2000.0
ATOMIC_HIGH = 50000.0
BOUNDARIES = (CHI, ELECTRON_CUT, LATE_HIGH, ATOMIC_HIGH)
FIELDS = ("Phi_cm2_s", "Psi_eV_cm2_s", "Gamma_s", "K_eV_s", "A_eV_s")

# Positive 8- and 16-point Gauss-Legendre weights, in symmetric pairs.
_HALF_GAUSS = {
    8: ((.1834346424956498, .3626837833783620),
        (.5255324099163290, .3137066458778873),
        (.7966664774136267, .2223810344533745),
        (.9602898564975363, .1012285362903763)),
    16: ((.09501250983763744, .1894506104550685),
         (.2816035507792589, .1826034150449236),
         (.4580167776572274, .1691565193950025),
         (.6178762444026437, .1495959888165767),
         (.7554044083550030, .1246289712555339),
         (.8656312023878318, .09515851168249278),
         (.9445750230732326, .06225352393864789),
         (.9894009349916499, .02715245941175409)),
}


def _nodes(order):
    for x, w in _HALF_GAUSS[order]:
        yield -x, w
        yield x, w


def band_moments(spectrum, atom, low, high, order):
    """Integrate in ln E, split at every original source interpolation node."""
    if order not in _HALF_GAUSS or not CHI <= low < high <= ATOMIC_HIGH:
        raise ValueError("UNSUPPORTED_MOMENT_BAND_OR_ORDER")
    edges = (low, *(e for e in spectrum.energy_eV if low < e < high), high)
    terms = [[] for _ in FIELDS]
    for a, b in zip(edges, edges[1:]):
        half = math.log(b/a)/2
        centre = (math.log(a)+math.log(b))/2
        for x, w in _nodes(order):
            energy = math.exp(centre+half*x)
            exposure = half*w*spectrum.evaluate(energy)/(pw19.EV_ERG*energy)
            sigma = atom.sigma_cm2(energy)
            terms[0].append(exposure)
            terms[1].append(energy*exposure)
            terms[2].append(sigma*exposure)
            terms[3].append((energy-CHI)*sigma*exposure)
            terms[4].append(energy*sigma*exposure)
    return dict(zip(FIELDS, (math.fsum(t) for t in terms)))


def sum_moments(parts):
    return {key: math.fsum(p[key] for p in parts) for key in FIELDS}


def local_residual(n_heii_cm3, gamma_s, kinetic_eV_s):
    """A one-way external-source residual; kinetic energy is not yet heat."""
    if isinstance(n_heii_cm3, bool) or not isinstance(n_heii_cm3, (int, float)) or not math.isfinite(n_heii_cm3) or n_heii_cm3 < 0:
        raise ValueError("NONNEGATIVE_PHYSICAL_HEII_DENSITY_REQUIRED")
    return local_tangent(n_heii_cm3, gamma_s, kinetic_eV_s)


def local_tangent(v_n_cm3, gamma_s, kinetic_eV_s):
    """The signed density JVP has the same linear map as the residual."""
    if isinstance(v_n_cm3, bool) or not isinstance(v_n_cm3, (int, float)) or not math.isfinite(v_n_cm3):
        raise ValueError("FINITE_DENSITY_TANGENT_REQUIRED")
    j = v_n_cm3*gamma_s
    binding = v_n_cm3*CHI*gamma_s*pw19.EV_ERG
    primary = v_n_cm3*kinetic_eV_s*pw19.EV_ERG
    return {"species_cm3_s": (0.0, 0.0, 0.0, -j, j, j),
            "ion_erg_cm3_s": binding,
            "primary_erg_cm3_s": primary,
            "external_radiation_erg_cm3_s": -(binding+primary)}


def certify_kinetic_grid(high_photon_eV, max_kinetic_eV=150.0):
    if high_photon_eV-CHI > max_kinetic_eV:
        raise lumina.DomainError("FULL_PRIMARY_ELECTRON_SUPPORT_EXCEEDS_GRID")
    return high_photon_eV-CHI


def calculate():
    spectrum = pw19.PW19Spectrum(2.479)
    atom = pw19.Verner96.from_table("HeII")
    partitions = []
    quadrature_residuals = []
    for lo, hi in zip(BOUNDARIES, BOUNDARIES[1:]):
        m8 = band_moments(spectrum, atom, lo, hi, 8)
        m16 = band_moments(spectrum, atom, lo, hi, 16)
        analytic = spectrum.photon_flux_moments(lo, hi)
        quadrature_residuals.append({
            "band_eV": [lo, hi],
            "GL8_GL16_relative": {key: abs(m8[key]-m16[key])/m16[key]
                                 for key in ("Gamma_s", "K_eV_s", "A_eV_s")},
            "GL16_analytic_relative": {
                "Phi_cm2_s": abs(m16["Phi_cm2_s"]-analytic["number_cm2_s"])/analytic["number_cm2_s"],
                "Psi_eV_cm2_s": abs(m16["Psi_eV_cm2_s"]-analytic["energy_eV_cm2_s"])/analytic["energy_eV_cm2_s"]},
        })
        partitions.append({"band_eV": [lo, hi], **m16})

    full = sum_moments(partitions)
    late = sum_moments(partitions[:2])
    below = spectrum.photon_flux_moments(spectrum.energy_eV[0], CHI)
    above = spectrum.photon_flux_moments(ATOMIC_HIGH, spectrum.energy_eV[-1])
    finite_table = spectrum.photon_flux_moments(spectrum.energy_eV[0], spectrum.energy_eV[-1])
    rows = lumina.load_moments()
    late_row = rows[-1]
    incident = lumina.IncidentPhotonExposure(
        (late["Phi_cm2_s"],), "photon cm^-2 s^-1", "proper", "late", 2.479,
        (late_row.template,), "true_c", (2.479, 2.479),
        "PW19_v1.0.0:z_02.479000:finite_late_band",
        "instantaneous_node_no_temporal_history")
    template = lumina.moment_operator(incident, rows)
    gamma_l = template.gamma_s[2]
    k_l = template.heat_erg_s_target[2]/pw19.EV_ERG
    absorbed_l = template.absorbed_erg_s_target[2]/pw19.EV_ERG
    return {
        "source": {"redshift": spectrum.redshift, "spectrum_sha256": spectrum.source_sha256,
                   "atomic_channel": atom.channel, "frame": "isotropic_bath_rest",
                   "time_basis": "proper_second", "source_release_DOI": "10.5281/zenodo.15367103"},
        "partition_moments": partitions, "late_band_moments": late, "full_atomic_moments": full,
        "quadrature_residuals": quadrature_residuals,
        "uncertainty_ledger": {
            "provider_uncertainty": None, "physical_model_uncertainty": None,
            "interpolation_error_relative_to_unprovided_continuum": None,
            "quadrature_actual_GL8_GL16_relative": quadrature_residuals,
            "floating_actual_absorption_identity_eV_s": [
                p["A_eV_s"]-CHI*p["Gamma_s"]-p["K_eV_s"] for p in partitions],
            "floating_actual_finite_table_count_residual_cm2_s": math.fsum((below["number_cm2_s"], full["Phi_cm2_s"], above["number_cm2_s"]))-finite_table["number_cm2_s"],
            "floating_actual_finite_table_energy_residual_eV_cm2_s": math.fsum((below["energy_eV_cm2_s"], full["Psi_eV_cm2_s"], above["energy_eV_cm2_s"]))-finite_table["energy_eV_cm2_s"],
            "global_physical_error_bound": None,
        },
        "effective_late_coefficients": {"sigma_cm2": late["Gamma_s"]/late["Phi_cm2_s"],
                                        "excess_eV": late["K_eV_s"]/late["Gamma_s"]},
        "lumina_late": {"active_species": template.active_species,
                        "inactive_HI_HeI_rates": [template.gamma_s[0], template.gamma_s[1]],
                        "sigma_cm2": late_row.sigma[2], "excess_eV": late_row.excess[2],
                        "Gamma_s": gamma_l, "K_eV_s": k_l, "A_eV_s": absorbed_l},
        "template_signed_relative_defect": {
            "delta_Gamma": (gamma_l-late["Gamma_s"])/late["Gamma_s"],
            "delta_K": (k_l-late["K_eV_s"])/late["K_eV_s"],
            "delta_abs": (absorbed_l-late["A_eV_s"])/late["A_eV_s"]},
        "radiation_exposure_outside_atomic": {
            "below_threshold": {"band_eV": [spectrum.energy_eV[0], CHI], **below,
                                "HeII_primary_Gamma_s": 0.0, "atomic_status": "physically_zero_below_threshold"},
            "above_atomic_domain": {"band_eV": [ATOMIC_HIGH, spectrum.energy_eV[-1]], **above,
                                    "HeII_primary_Gamma_s": None, "atomic_status": "unknown_above_50000_eV"}},
        "finite_table_exposure": finite_table,
        "kinetic_support_eV": {"first_partition_max": 150.0,
                               "late_full_max": LATE_HIGH-CHI,
                               "atomic_full_max": ATOMIC_HIGH-CHI,
                               "first_partition_excluded_positive_tail": sum_moments(partitions[1:])},
        "local_fixture": {"n_HeII_cm3": 1.0, "v_n_cm3": .3,
                          "residual": local_residual(1.0, late["Gamma_s"], late["K_eV_s"]),
                          "density_JVP": local_tangent(.3, late["Gamma_s"], late["K_eV_s"])},
        "SI_handoff": {
            "event_owner": "one_HeII_photoionization_from_PW19_2.479",
            "species_order": ("HI", "HII", "HeI", "HeII", "HeIII", "e"),
            "frame": "isotropic_bath_rest", "time_basis": "proper_second",
            "source_redshift": 2.479, "photon_band_eV": [CHI, LATE_HIGH],
            "excluded_native_supported_photon_band_eV": [LATE_HIGH, ATOMIC_HIGH],
            "incident_photon_exposure_m2_s": late["Phi_cm2_s"]*1e4,
            "effective_sigma_m2": (late["Gamma_s"]/late["Phi_cm2_s"])*1e-4,
            "Gamma_s": late["Gamma_s"],
            "K_J_s_per_target": late["K_eV_s"]*1.602176634e-19,
            "A_J_s_per_target": late["A_eV_s"]*1.602176634e-19,
            "fixture_n_HeII_m3": 1e6,
            "fixture_v_n_m3": .3e6,
            "fixture_species_m3_s": [x*1e6 for x in local_residual(1.0, late["Gamma_s"], late["K_eV_s"])["species_cm3_s"]],
            "fixture_primary_W_m3": late["K_eV_s"]*pw19.EV_ERG*.1,
            "fixture_ion_W_m3": CHI*late["Gamma_s"]*pw19.EV_ERG*.1,
            "fixture_external_radiation_W_m3": -(CHI*late["Gamma_s"]+late["K_eV_s"])*pw19.EV_ERG*.1,
            "conversion": {"per_cm2_to_per_m2": 1e4, "cm2_to_m2": 1e-4,
                           "per_cm3_to_per_m3": 1e6, "eV_to_J": 1.602176634e-19,
                           "erg_cm3_s_to_W_m3": .1},
        },
    }
