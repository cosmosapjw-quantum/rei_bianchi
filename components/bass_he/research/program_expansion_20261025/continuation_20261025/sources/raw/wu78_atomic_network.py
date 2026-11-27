"""Finite H/D/T/He3/He4/Li6/Li7 photoionization + radiative recombination.

This is an exploratory, isotropic reacting ideal-gas closure. Its 21 nuclear
and ionic slots include a neutron slot; free electrons follow exact charge
neutrality. Charge-state populations are not anisotropic kinetic stresses.
Collisional ionization, nuclear reactions, beta decay, charge exchange,
molecules, dielectronic recombination and secondary electrons are excluded.
The default neutron and tritium inventories are zero. In particular this
module does not activate HH_R10 or claim full primordial-network admission.

The six elemental transition coefficient rows below are exact decimal
literals from original author tables retained by rei_bianchi PR210, HEAD
e4c8133288614638792888367ca10b2ded3138ff. H/D/T, He3/He4 and Li6/Li7 share
elemental atomic coefficients and thresholds: this is an explicit isotope-
blind atomic approximation, not isotope-specific atomic structure.

Verner et al. (1996), ApJ 465, 487, DOI 10.1086/177435:
  https://www.pa.uky.edu/~verner/dima/photo/photo.dat
Verner & Ferland (1996), ApJS 103, 467, DOI 10.1086/192284:
  https://www.pa.uky.edu/~verner/dima/rec/table1.dat

Inputs use proper densities in cm^-3, Kelvin, eV, seconds and abundances
per reference H1 nucleus. No Hubble/time-coordinate conversion is inserted.
Radiative-recombination photons escape (Case A). Their mean kinetic capture
energy follows the Maxwellian derivative identity; see rr_rates(). A fixed
photo spectrum is prepared once; evolving photon numbers are supplied by the
caller. Energies above any active source fit's Emax are rejected.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

import numpy as np

C_CM_S = 2.99792458e10
EV_J = 1.602176634e-19
KB_EV_K = 1.380649e-23 / EV_J
SOURCE_HEAD = "e4c8133288614638792888367ca10b2ded3138ff"
SOURCE_REPOSITORY = "cosmosapjw-quantum/rei_bianchi"
SOURCE_SHA256 = MappingProxyType({
    "photo.dat": "a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389",
    "rec_table1.dat": "2382f6896fe58ee1da58c9bd563fd7d02c0d94410dbd4150767eed26a54f5091",
})
MODEL_SCOPE = "EXPLORATORY_ISOTROPIC_PI_RR_ISOTOPE_BLIND_CASE_A"
DEFAULT_TABLE_DIRECTORY = Path(__file__).resolve().parents[1]/"vendor"/"atomic"

# Order: H I, He I, He II, Li I, Li II, Li III. RR is capture TOWARD
# that ion, i.e. the ion with one fewer bound electron is its parent.
ELEMENT_IONS = ((1, 1), (2, 2), (2, 1), (3, 3), (3, 2), (3, 1))
# Eth/eV, Emax/eV, E0/eV, sigma0/Mb, ya, P, yw, y0, y1.
PHOTO_COEFFICIENTS = (
    (13.6, 50000., .4298, 54750., 32.88, 2.963, 0., 0., 0.),
    (24.59, 50000., 13.61, 949.2, 1.469, 3.188, 2.039, .4434, 2.136),
    (54.42, 50000., 1.72, 13690., 32.88, 2.963, 0., 0., 0.),
    (5.392, 64.39, 3.107, 62.45, 15.01, 4.895, 0., 0., 0.),
    (75.64, 50000., 20.06, 320.1, 7.391, 2.916, 0., 0., 0.),
    (122.5, 50000., 3.871, 6083., 32.88, 2.963, 0., 0., 0.),
)
# A/(cm^3 s^-1), b, T0/K, T1/K.
RR_COEFFICIENTS = (
    (7.982e-11, .748, 3.148, 703600.),
    (9.356e-10, .7892, .04266, 4677000.),
    (1.891e-10, .7524, 9.37, 2774000.),
    (1.036e-11, .388, 107.7, 11770000.),
    (1.112e-10, .6926, 24.37, 8323000.),
    (3.039e-10, .7539, 18.71, 6209000.),
)


def _readonly(values, dtype=np.float64):
    """Own immutable bytes, so callers cannot re-enable ndarray writeability."""
    a = np.ascontiguousarray(values, dtype=dtype)
    return np.frombuffer(a.tobytes(), dtype=a.dtype).reshape(a.shape)


@dataclass(frozen=True)
class Species:
    name: str
    isotope: str
    mass_number: int
    atomic_number: int
    charge: int


_ISOTOPE_DATA = (("H1", 1, 1), ("D", 2, 1), ("T", 3, 1),
                 ("He3", 3, 2), ("He4", 4, 2),
                 ("Li6", 6, 3), ("Li7", 7, 3))
_ROMAN = ("I", "II", "III", "IV")
SPECIES = tuple(Species(f"{iso}_{_ROMAN[q]}", iso, a, z, q)
                for iso, a, z in _ISOTOPE_DATA for q in range(z+1)) + (
                    Species("n", "n", 1, 0, 0),)
SPECIES_NAMES = tuple(s.name for s in SPECIES)
SPECIES_INDEX = MappingProxyType({s.name: i for i, s in enumerate(SPECIES)})
N_SPECIES = len(SPECIES)
CHARGE = _readonly([s.charge for s in SPECIES])
MASS_NUMBER = _readonly([s.mass_number for s in SPECIES])
ISOTOPES = tuple(s[0] for s in _ISOTOPE_DATA) + ("n",)
ISOTOPE_SUM = _readonly([[float(s.isotope == iso) for s in SPECIES]
                         for iso in ISOTOPES])
DEFAULT_HE4_MASS_FRACTION = .24709
_DEFAULT_D_H, _DEFAULT_HE3_H = 2.460e-5, 1.074e-5
_DEFAULT_LI6_H, _DEFAULT_LI7_H = 1.20e-14, 5.627e-10
# A-weighted inventory includes trace nuclei when converting Yp to He4/H1.
_DEFAULT_NON_HE4_MASS = (1. + 2*_DEFAULT_D_H + 3*_DEFAULT_HE3_H
                        + 6*_DEFAULT_LI6_H + 7*_DEFAULT_LI7_H)
DEFAULT_INVENTORY = MappingProxyType({"H1": 1., "D": _DEFAULT_D_H, "T": 0.,
    "He3": _DEFAULT_HE3_H,
    "He4": DEFAULT_HE4_MASS_FRACTION*_DEFAULT_NON_HE4_MASS
           /(4*(1-DEFAULT_HE4_MASS_FRACTION)),
    "Li6": _DEFAULT_LI6_H, "Li7": _DEFAULT_LI7_H, "n": 0.})


def _vector(values, size, label, *, require_nonnegative=True):
    v = np.asarray(values, dtype=np.float64)
    if v.shape != (size,) or not np.isfinite(v).all():
        raise ValueError(f"{label}_SHAPE_OR_NONFINITE")
    if require_nonnegative and np.any(v < 0):
        raise ValueError(f"{label}_NEGATIVE_NO_CLIPPING")
    return v


def neutral_abundances(isotope_abundances_per_H: Mapping[str, float] | None = None):
    """PRIMAT-median nuclear inventory, initially neutral; returned array mutable.

    These defaults are inputs, not a matched recombination or BBN donor. A supplied
    inventory must name every isotope; no omitted isotope is silently filled.
    """
    inventory = DEFAULT_INVENTORY if isotope_abundances_per_H is None else isotope_abundances_per_H
    if set(inventory) != set(ISOTOPES):
        raise ValueError("INVENTORY_MUST_NAME_ALL_ISOTOPES")
    values = _vector([inventory[k] for k in ISOTOPES], len(ISOTOPES), "INVENTORY")
    y = np.zeros(N_SPECIES)
    for iso, abundance in zip(ISOTOPES, values):
        y[SPECIES_INDEX["n" if iso == "n" else f"{iso}_I"]] = abundance
    return y


def verify_author_tables(directory):
    """Optional byte-identity check against retained original author tables."""
    result = {}
    for name, expected in SOURCE_SHA256.items():
        actual = hashlib.sha256((Path(directory)/name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError("AUTHOR_TABLE_SHA256_MISMATCH:" + name)
        result[name] = actual
    return result


def _verify_original_coefficients(directory):
    """Bind every embedded elemental literal to the exact retained source bytes."""
    verify_author_tables(directory)
    photo, rr = {}, {}
    for line in (Path(directory)/"photo.dat").read_text().splitlines():
        pieces = line.split()
        key = tuple(map(int, pieces[:2]))
        if key in ELEMENT_IONS:
            photo[key] = tuple(map(float, pieces[2:]))
    for line in (Path(directory)/"rec_table1.dat").read_text().splitlines():
        key = (int(line[9:11]), int(line[12:14]))
        if key in ELEMENT_IONS:
            rr[key] = tuple(float(line[a:b]) for a, b in
                            ((16, 25), (27, 33), (35, 44), (46, 55)))
    for i, key in enumerate(ELEMENT_IONS):
        if photo.get(key) != PHOTO_COEFFICIENTS[i] or rr.get(key) != RR_COEFFICIENTS[i]:
            raise ValueError("ORIGINAL_COEFFICIENT_LITERAL_MISMATCH:" + str(key))


def _verify_coefficient_inventory(path):
    obj = json.loads(Path(path).read_text())
    rows = obj["records"] if isinstance(obj, dict) else obj
    got = {}
    for row in rows:
        z = row.get("Z", row.get("atomic_number"))
        key = (z, row["electrons"])
        if key in ELEMENT_IONS:
            if key in got:
                raise ValueError("DUPLICATE_COEFFICIENT_ROW")
            got[key] = (tuple(row["photo"]), tuple(row["rr_toward"]))
    want = {key: (PHOTO_COEFFICIENTS[i], RR_COEFFICIENTS[i])
            for i, key in enumerate(ELEMENT_IONS)}
    if got != want:
        raise ValueError("COEFFICIENT_SOURCE_IDENTITY_MISMATCH")


def _element_photo_cross_sections(energies):
    result = np.zeros((len(ELEMENT_IONS), energies.size))
    for i, (eth, emax, e0, s0, ya, p, yw, y0, y1) in enumerate(PHOTO_COEFFICIENTS):
        if np.any(energies > emax):
            raise ValueError(f"PHOTO_FIT_EMAX_EXCEEDED:{ELEMENT_IONS[i]}:{emax}")
        mask = energies >= eth
        x = energies[mask]/e0 - y0
        y = np.hypot(x, y1)
        shape = (x-1.)**2 + yw*yw
        if np.any(y <= 0):
            raise ArithmeticError("PHOTO_FIT_NONPOSITIVE_Y")
        with np.errstate(divide="ignore"):
            log_sigma = (np.log(s0) + np.log(shape) + (.5*p-5.5)*np.log(y)
                         - p*np.log1p(np.sqrt(y/ya)) + np.log(1e-18))
        result[i, mask] = np.exp(log_sigma)  # Mb -> cm^2 exactly 10^-18.
    if np.any(result < 0) or not np.isfinite(result).all():
        raise ArithmeticError("PHOTO_FIT_INVALID_RESULT")
    return result


@dataclass(frozen=True)
class PreparedAtomicNetwork:
    photon_energy_eV: np.ndarray
    lower: np.ndarray
    upper: np.ndarray
    element_row: np.ndarray
    threshold_eV: np.ndarray
    photo_cross_section_cm2: np.ndarray
    photo_rate_per_photon_cm3_s: np.ndarray
    rr_coefficients: np.ndarray
    binding_eV: np.ndarray
    stoichiometry: np.ndarray
    species_jacobian_sparsity: np.ndarray

    def with_photon_energies(self, photon_energy_eV):
        """Recompute the gray cross sections without reparsing immutable tables.

        Geometry/redshift or injection can change the bin mean energy. These
        are new physical input energies, never a reuse of stale cross sections.
        The number of bins is fixed by the caller's prepared state layout.
        """
        energies = np.asarray(photon_energy_eV, dtype=np.float64)
        if (energies.shape != self.photon_energy_eV.shape
                or not np.isfinite(energies).all() or np.any(energies <= 0)):
            raise ValueError("DYNAMIC_PHOTON_ENERGY_SHAPE_OR_DOMAIN")
        if np.array_equal(energies, self.photon_energy_eV):
            return self
        photo = _element_photo_cross_sections(energies)[self.element_row]
        return replace(self, photon_energy_eV=_readonly(energies),
                       photo_cross_section_cm2=_readonly(photo),
                       photo_rate_per_photon_cm3_s=_readonly(C_CM_S*photo))

    def rr_rates(self, temperature_K):
        """(alpha/cm^3 s^-1, mean captured kinetic energy/eV, dlnalpha/dlnT).

        Maxwellian alpha(T) implies <E_capture> = kT(3/2+dlnalpha/dlnT).
        For VF96 this is evaluated as the manifestly positive equivalent
        kT/2 * [(1-b)/(1+sqrt(T/T0)) + (1+b)/(1+sqrt(T/T1))].
        This inferred kinetic moment belongs to the selected RR fit; it is
        not an independent cross-section or full recombination cooling model.
        """
        t = float(temperature_K)
        if not np.isfinite(t) or not 3. <= t <= 1e9:
            raise ValueError("RR_TEMPERATURE_OUTSIDE_3_TO_1E9_K")
        a, b, t0, t1 = self.rr_coefficients.T
        s0, s1 = np.sqrt(t/t0), np.sqrt(t/t1)
        log_rate = (np.log(a) - np.log(s0) - (1-b)*np.log1p(s0)
                    - (1+b)*np.log1p(s1))
        alpha = np.exp(log_rate)
        slope = -.5 - .5*(1-b)*s0/(1+s0) - .5*(1+b)*s1/(1+s1)
        capture = .5*KB_EV_K*t*((1-b)/(1+s0) + (1+b)/(1+s1))
        if (not np.isfinite(alpha).all() or np.any(alpha <= 0)
                or not np.isfinite(capture).all() or np.any(capture <= 0)):
            raise ArithmeticError("RR_INVALID_RATE_OR_CAPTURE_ENERGY")
        return alpha, capture, slope

    def rhs(self, T_K, nH_cm3, species_abundance_per_H, photon_number_cm3, **kwargs):
        return rhs(T_K, nH_cm3, species_abundance_per_H, photon_number_cm3,
                   prepared=self, **kwargs)


def prepare_network(photon_energy_eV=(18., 30., 60.), coefficient_path=None):
    """Prepare immutable source coefficients, transition indices and photon kernel."""
    energies = np.asarray(photon_energy_eV, dtype=np.float64)
    if (energies.ndim != 1 or energies.size == 0 or not np.isfinite(energies).all()
            or np.any(energies <= 0)):
        raise ValueError("PHOTON_ENERGIES_MUST_BE_FINITE_POSITIVE_VECTOR")
    if coefficient_path is None:
        _verify_original_coefficients(DEFAULT_TABLE_DIRECTORY)
    elif Path(coefficient_path).is_dir():
        _verify_original_coefficients(coefficient_path)
    else:
        _verify_coefficient_inventory(coefficient_path)
    photo = _element_photo_cross_sections(energies)
    row_of = {key: i for i, key in enumerate(ELEMENT_IONS)}
    lower, upper, rows = [], [], []
    binding = np.zeros(N_SPECIES)
    for i, species in enumerate(SPECIES):
        if species.charge == species.atomic_number:
            continue  # includes the inert neutron slot Z=0.
        row = row_of[(species.atomic_number, species.atomic_number-species.charge)]
        lower.append(i); upper.append(i+1); rows.append(row)
        binding[i+1] = binding[i] + PHOTO_COEFFICIENTS[row][0]
    lower, upper, rows = (np.asarray(v, dtype=int) for v in (lower, upper, rows))
    stoich = np.zeros((N_SPECIES, len(rows)))
    stoich[lower, np.arange(len(rows))] = -1.
    stoich[upper, np.arange(len(rows))] = 1.
    sparsity = np.zeros((N_SPECIES, N_SPECIES), dtype=bool)
    charged = np.flatnonzero(CHARGE)
    for lo, hi in zip(lower, upper):
        sparsity[np.ix_([lo, hi], np.unique(np.r_[lo, hi, charged]))] = True
    return PreparedAtomicNetwork(
        _readonly(energies), _readonly(lower, np.int64), _readonly(upper, np.int64),
        _readonly(rows, np.int64), _readonly(np.asarray(PHOTO_COEFFICIENTS)[rows, 0]),
        _readonly(photo[rows]), _readonly(C_CM_S*photo[rows]),
        _readonly(np.asarray(RR_COEFFICIENTS)[rows]), _readonly(binding),
        _readonly(stoich), _readonly(sparsity, bool))


@dataclass(frozen=True)
class AtomicRhs:
    d_species_per_H_dt: np.ndarray
    photo_absorbed_eV_per_H_s: float
    photo_heat_eV_per_H_s: float
    rr_kinetic_cooling_eV_per_H_s: float
    heat_eV_per_H_s: float
    rr_escape_eV_per_H_s: float
    photon_absorption_per_H_s: np.ndarray
    photon_absorption_cm3_s: np.ndarray
    electron_abundance_per_H: float
    electron_density_cm3: float
    nucleus_count_per_H: float
    nucleon_count_per_H: float
    binding_eV_per_H: float
    binding_derivative_eV_per_H_s: float
    d_electron_per_H_dt: float
    photo_event_per_H_s: np.ndarray
    rr_event_per_H_s: np.ndarray
    energy_ledger_residual_eV_per_H_s: float
    diagnostics: Mapping

    @property
    def dsdt(self):
        return self.d_species_per_H_dt


def rhs(T_K, nH_cm3, species_abundance_per_H, photon_number_cm3,
        photon_energy_eV=None, *, prepared: PreparedAtomicNetwork | None = None,
        allow_solver_extension=False, solver_extension_relative_tolerance=1e-10,
        solver_extension_scale_per_H=None):
    """Return proper-time number and energy rates without projecting input states.

    `photon_number_cm3[j]` is the number density integrated over gray bin j.
    The supplied photon energy is the actual energy used for both the cross
    section and absorption budget. Supplying changed energies recomputes their
    cross sections on the same layout. By default all populations must be
    nonnegative. `allow_solver_extension=True` admits a bounded polynomial
    extension to tiny negative solver stages, evaluating the RAW abundances
    without clipping. This is not a physical accepted-state check. Its bounds
    use each isotope's total, or caller-supplied fixed per-coordinate scales.
    Photon populations and derived electron density remain nonnegative.
    """
    if prepared is None:
        prepared = prepare_network((18., 30., 60.) if photon_energy_eV is None else photon_energy_eV)
    elif photon_energy_eV is not None:
        prepared = prepared.with_photon_energies(photon_energy_eV)
    nH = float(nH_cm3)
    if not np.isfinite(nH) or nH <= 0:
        raise ValueError("REFERENCE_H_DENSITY_MUST_BE_POSITIVE")
    y = _vector(species_abundance_per_H, N_SPECIES, "SPECIES",
                require_nonnegative=not allow_solver_extension)
    if allow_solver_extension:
        tolerance = float(solver_extension_relative_tolerance)
        if not np.isfinite(tolerance) or not 0 <= tolerance <= 1e-6:
            raise ValueError("SOLVER_EXTENSION_TOLERANCE_OUTSIDE_0_TO_1E-6")
        if solver_extension_scale_per_H is None:
            totals = ISOTOPE_SUM @ y
            if np.any(totals < 0):
                raise ValueError("SOLVER_EXTENSION_NEGATIVE_ISOTOPE_TOTAL")
            scales = ISOTOPE_SUM.T @ totals
        else:
            scales = _vector(solver_extension_scale_per_H, N_SPECIES, "SOLVER_EXTENSION_SCALE")
        if np.any(y < -tolerance*scales):
            raise ValueError("SOLVER_EXTENSION_NEGATIVITY_BOUND_EXCEEDED")
    photons = _vector(photon_number_cm3, len(prepared.photon_energy_eV), "PHOTONS")
    alpha, captured_energy, _ = prepared.rr_rates(T_K)
    xe = float(CHARGE @ y)
    if xe < 0:
        raise ValueError("NEGATIVE_DERIVED_ELECTRON_DENSITY")
    ne = nH*xe
    photo = y[prepared.lower, None]*prepared.photo_rate_per_photon_cm3_s*photons[None, :]
    rr = y[prepared.upper]*ne*alpha
    up = photo.sum(axis=1)
    dsdt = prepared.stoichiometry @ (up-rr)
    absorption = photo.sum(axis=0)
    photo_energy = float(absorption @ prepared.photon_energy_eV)
    photo_binding = float(up @ prepared.threshold_eV)
    # Direct excess avoids subtracting total absorbed energy and binding energy.
    photo_heat = float(np.sum(photo*(prepared.photon_energy_eV[None, :]
                                    - prepared.threshold_eV[:, None])))
    rr_kinetic = float(rr @ captured_energy)
    rr_binding = float(rr @ prepared.threshold_eV)
    escape = rr_binding + rr_kinetic
    heat = photo_heat - rr_kinetic
    dbinding = float(prepared.binding_eV @ dsdt)
    residual = photo_energy - heat - dbinding - escape
    values = np.r_[dsdt, absorption, photo_energy, photo_heat, rr_kinetic, escape,
                   heat, dbinding, residual, ne, xe]
    if not np.isfinite(values).all():
        raise ArithmeticError("NONFINITE_ATOMIC_RHS")
    diagnostics = MappingProxyType({
        "model_scope": MODEL_SCOPE, "source_head": SOURCE_HEAD,
        "state_projection": "NONE", "collisional_ionization": "EXCLUDED_MODEL_CHANNEL",
        "solver_extension": bool(allow_solver_extension),
        "negative_stage_coordinates": int(np.count_nonzero(y < 0)),
        "minimum_species_abundance_per_H": float(np.min(y)),
        "nuclear_reactions": "EXCLUDED_MODEL_CHANNEL", "beta_decay": "EXCLUDED_MODEL_CHANNEL",
        "charge_exchange": "EXCLUDED_MODEL_CHANNEL", "isotope_atomic_model": "ELEMENT_SHARED",
        "electron_closure": "CHARGE_NEUTRALITY", "gas_anisotropic_stress": "ZERO_IDEAL_FLUID_CLOSURE",
        "nucleus_derivative_per_H_s": float(dsdt.sum()),
        "nucleon_derivative_per_H_s": float(MASS_NUMBER @ dsdt),
        "isotope_derivative_per_H_s": tuple(float(v) for v in ISOTOPE_SUM @ dsdt),
        "photo_binding_eV_per_H_s": photo_binding,
        "rr_binding_eV_per_H_s": rr_binding,
        "particle_count_per_H": float(y.sum()+xe),
        "temperature_K": float(T_K), "HH_R10": "OFF", "production_admission": False,
    })
    return AtomicRhs(
        _readonly(dsdt), photo_energy, photo_heat, rr_kinetic, heat, escape,
        _readonly(absorption), _readonly(nH*absorption), xe, ne,
        float(y.sum()), float(MASS_NUMBER @ y), float(prepared.binding_eV @ y), dbinding,
        float(CHARGE @ dsdt), _readonly(photo), _readonly(rr), residual, diagnostics)
