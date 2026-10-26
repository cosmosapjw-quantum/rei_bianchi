"""Exclusive PW19 HeII photo-rate provider for REC119's native 21-state callback.

The inherited AtomicNetwork.rates/evaluate implementations perform the actual
RHS and Jacobian. This subclass changes only their prepared photo coefficients.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np

UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT / "intake" / "rec119" / "code"))
from atomic_network import AtomicNetwork, C_M_S, EV_J, _readonly

SOURCE_UNIT = UNIT.parent / "lumina_resume_20261026"
MOMENTS = SOURCE_UNIT / "implementation" / "run01" / "MOMENTS.json"
MOMENTS_SHA256 = "4856cabb34ee24d3c626b795cb1098b228e752c857dda1dc874fe4583deb936e"
SPECTRUM = SOURCE_UNIT / "intake" / "provider" / "data" / "z_02.479000.csv"
SOURCE_SHA256 = "f93db0bb33dc6b7011cc0490f96253a489e5c7cd20cba99005b1461a3e56a5d1"
ROUTE = "PW19_z2.479_HeII_exclusive"
ISOTOPE_POLICY = "ElementalElectronicEquality_He3_He4_conditional"
EVENT_OWNER = "REC119_photo_HeII_one_owner"
BANDS = ((54.42, 204.42), (204.42, 2000.0), (2000.0, 50000.0))
HEII = (8, 11)
HEIII = (9, 12)
CHI_EV = 54.42


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_admitted_source():
    if _sha(MOMENTS) != MOMENTS_SHA256 or _sha(SPECTRUM) != SOURCE_SHA256:
        raise ValueError("ADMITTED_PW19_SOURCE_OR_MOMENTS_IDENTITY_MISMATCH")
    source = json.loads(MOMENTS.read_text())
    if (source["source"]["redshift"] != 2.479 or
        source["source"]["spectrum_sha256"] != SOURCE_SHA256 or
        source["source"]["atomic_channel"] != "HeII" or
        tuple(tuple(p["band_eV"]) for p in source["partition_moments"]) != BANDS):
        raise ValueError("ADMITTED_SOURCE_SCOPE_MISMATCH")
    for p in source["partition_moments"]:
        if not all(math.isfinite(p[k]) and p[k] > 0 for k in
                   ("Phi_cm2_s", "Psi_eV_cm2_s", "Gamma_s", "K_eV_s", "A_eV_s")):
            raise ValueError("NONPOSITIVE_OR_NONFINITE_NATIVE_MOMENT")
    with SPECTRUM.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    energy = tuple(float(row["E (eV)"]) for row in rows)
    spectral = tuple(float(row["I (erg/s/cm**2)"]) for row in rows)
    if (len(energy) != 626 or any(not math.isfinite(e) or e <= 0 for e in energy+spectral)
        or any(b <= a for a,b in zip(energy, energy[1:]))):
        raise ValueError("ORIGINAL_PW19_GRID_INVALID")
    return source, energy, spectral


class PW19HeIINetwork(AtomicNetwork):
    """REC119's unchanged rate/evaluate path with one selected external photo owner."""

    def __init__(self, *, source_z, source_route, isotope_policy, photo_owners,
                 uv_cutoff_eV=None):
        if source_z != 2.479 or source_route != ROUTE:
            raise ValueError("EXACT_PW19_SOURCE_NODE_AND_ROUTE_REQUIRED")
        if isotope_policy != ISOTOPE_POLICY:
            raise ValueError("EXPLICIT_INHERITED_ISOTOPE_EQUALITY_REQUIRED")
        if tuple(photo_owners) != (EVENT_OWNER,):
            raise ValueError("EXACTLY_ONE_SELECTED_PHOTO_EVENT_OWNER_REQUIRED")
        if uv_cutoff_eV is not None:
            raise ValueError("EXTERNAL_SOURCE_CANNOT_BE_TRUNCATED_AS_OLD_UV")
        self.source_z = source_z
        self.source_route = source_route
        self.isotope_policy = isotope_policy
        self.photo_owners = tuple(photo_owners)
        super().__init__(uv_cutoff_eV=uv_cutoff_eV)
        if (self.model["isotope_rate_policy"] !=
            "ElementalElectronicEquality explicitly enabled for H1/D/T, He3/He4, Li6/Li7; no isotope shift or isotope-resolved fit claimed"
            or tuple(self.names[i] for i in (*HEII, *HEIII)) !=
               ("He3II", "He4II", "He3III", "He4III")
            or any(self.transition_energy_eV[i] != CHI_EV for i in HEII)):
            raise ValueError("NATIVE_ISOTOPE_POLICY_SPECIES_OR_THRESHOLD_MISMATCH")

    def _prepare_spectrum(self, cutoff):
        if cutoff is not None:
            raise ValueError("EXTERNAL_SOURCE_CUTOFF_REJECTED")
        source, grid, spectral = load_admitted_source()
        self.admitted_moments = source
        self.original_spectrum_energy_eV = grid
        self.original_spectrum_S_erg_cm2_s_per_dlnE = spectral
        parts = source["partition_moments"]
        gamma = math.fsum(p["Gamma_s"] for p in parts)
        kinetic = math.fsum(p["K_eV_s"] for p in parts)
        absorbed = math.fsum(p["A_eV_s"] for p in parts)
        old = source["full_atomic_moments"]
        if any(abs(a-old[k])/old[k] > 2e-14 for a,k in
               ((gamma,"Gamma_s"),(kinetic,"K_eV_s"),(absorbed,"A_eV_s"))):
            raise ValueError("ADMITTED_PARTITION_SUM_MISMATCH")
        self.selected_Gamma_s = gamma
        self.selected_K_J_s = kinetic*EV_J
        self.selected_A_J_s = absorbed*EV_J
        self.selected_binding_J_s = CHI_EV*gamma*EV_J
        flux = np.array([p["Phi_cm2_s"]*1e4 for p in parts])
        means = np.array([p["Psi_eV_cm2_s"]/p["Phi_cm2_s"] for p in parts])
        self.photon_flux_bins_base = _readonly(flux)
        self.photon_energy_eV = _readonly(means)
        self.photon_bin_edges_eV = _readonly([b[0] for b in BANDS]+[BANDS[-1][1]])
        self.uv_config = {"selected_route": ROUTE, "source_z": 2.479,
                          "actual_energy_max_eV": 50000.0,
                          "actual_bin_count": 3,
                          "mean_energy_diagnostic_only": True,
                          "other_native_photo_routes": "OFF_BY_EXCLUSIVE_SELECTION_NOT_PHYSICAL_ZERO"}
        sigma_effective = np.zeros((self.size, len(parts)))
        for j,p in enumerate(parts):
            sigma_effective[list(HEII),j] = (p["Gamma_s"]/p["Phi_cm2_s"])*1e-4
        self.photo_sigma_m2 = _readonly(sigma_effective)
        self.li1s_photo_sigma_m2 = _readonly(np.zeros_like(sigma_effective))
        photo = np.zeros(self.size)
        absorb = np.zeros(self.size)
        primary = np.zeros(self.size)
        photo[list(HEII)] = gamma
        absorb[list(HEII)] = absorbed*EV_J
        primary[list(HEII)] = kinetic*EV_J
        self._photo_s = _readonly(photo)
        self._absorbed_W = _readonly(absorb)
        self._primary_W = _readonly(primary)
        self._core_W = _readonly(np.zeros(self.size))
        self._li1s_photo_s = _readonly(np.zeros(self.size))
        self._inner_absorbed_W = _readonly(np.zeros(self.size))
        self._Gphoto = _readonly(self._transition_matrix(self._photo_s, upward=True))

    def selected_photo_ledger(self, Y, nb, source_amplitude=1.0,
                              *, v=None, dnb=0.0, damplitude=0.0):
        """Selected event and open energy partners, plus a fixed-source JVP."""
        y = np.asarray(Y, dtype=float)
        direction = np.zeros(self.size) if v is None else np.asarray(v, dtype=float)
        if y.shape != (self.size,) or direction.shape != (self.size,) or not np.all(np.isfinite(y)) or not np.all(np.isfinite(direction)):
            raise ValueError("FINITE_NATIVE21_STATE_AND_TANGENT_REQUIRED")
        if not all(math.isfinite(float(w)) for w in (nb,source_amplitude,dnb,damplitude)) or nb < 0 or source_amplitude < 0:
            raise ValueError("NONNEGATIVE_DENSITY_AND_SOURCE_AMPLITUDE_REQUIRED")
        s = float(y[list(HEII)].sum())
        ds = float(direction[list(HEII)].sum())
        scalar = nb*source_amplitude*s
        tangent_scalar = nb*source_amplitude*ds+source_amplitude*s*dnb+nb*s*damplitude
        bands = []
        for p in self.admitted_moments["partition_moments"]:
            gamma = p["Gamma_s"]
            bind = CHI_EV*gamma*EV_J
            kinetic = p["K_eV_s"]*EV_J
            absorb = p["A_eV_s"]*EV_J
            bands.append({"band_eV": p["band_eV"],
                          "events_m3_s": scalar*gamma,
                          "binding_W_m3": scalar*bind,
                          "primary_W_m3": scalar*kinetic,
                          "external_radiation_W_m3": -scalar*absorb,
                          "tangent_events_m3_s": tangent_scalar*gamma,
                          "tangent_binding_W_m3": tangent_scalar*bind,
                          "tangent_primary_W_m3": tangent_scalar*kinetic,
                          "tangent_external_radiation_W_m3": -tangent_scalar*absorb})
        totals = {k: math.fsum(row[k] for row in bands) for k in
                  ("events_m3_s", "binding_W_m3", "primary_W_m3",
                   "external_radiation_W_m3", "tangent_events_m3_s",
                   "tangent_binding_W_m3", "tangent_primary_W_m3",
                   "tangent_external_radiation_W_m3")}
        return {"bands": bands, "total": totals,
                "native_Y_HeII_sum": s, "proper_nb_m3": float(nb),
                "source_amplitude": float(source_amplitude),
                "primary_is_thermal_heat": False,
                "electron_support_eV": [0.0, 49945.58],
                "radiation_above_atomic_domain": self.admitted_moments["radiation_exposure_outside_atomic"]["above_atomic_domain"],
                "uncertainty_ledger": self.admitted_moments["uncertainty_ledger"] |
                    {"isotope_rate_uncertainty": None}}

    def certify_full_kinetic_grid(self, maximum_eV=150.0):
        if maximum_eV < 49945.58:
            raise ValueError("FULL_SOURCE_ELECTRON_SUPPORT_EXCEEDS_GRID")
        return 49945.58
