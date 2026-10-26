"""Typed public-history adapter and Table 1 photon moment operator.

The reference series are simulation statistics, never an incident exposure.
No interpolation, mass weighting, UVB completion, or photon trace is inferred.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
EV_TO_ERG = 1.602176634e-12
TRUE_C_CM_S = 29979245800.0
SPEED_CM_S = {"true_c": TRUE_C_CM_S, "transport_reduced_0.2c": .2*TRUE_C_CM_S}
SPECIES = ("HI", "HeI", "HeII")
THRESHOLDS_EV = (13.6, 24.59, 54.42)
STOICHIOMETRY = ((-1, 0, 0), (1, 0, 0), (0, -1, 0),
                 (0, 1, -1), (0, 0, 1), (1, 1, 1))
LEFT_VECTORS = ((1, 1, 0, 0, 0, 0), (0, 0, 1, 1, 1, 0),
                (0, 1, 0, 1, 2, -1))


class DomainError(ValueError):
    """An input lacks physical units, provenance, or supported domain."""


def _finite(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise DomainError(f"{name} must be a finite real number")
    return float(value)


def _positive(value: float, name: str) -> float:
    value = _finite(value, name)
    if value <= 0:
        raise DomainError(f"{name} must be positive")
    return value


@dataclass(frozen=True)
class ReferenceSeries:
    source_url: str
    source_sha256: str
    quantity: str
    units: str
    redshift_domain: tuple[float, float]
    sampling: str
    weighting: str
    statistic: str
    population: str
    regime: str
    validation_flags: tuple[str, ...]
    raw_column_names: tuple[str, ...]
    rows: tuple[tuple[float, ...], ...]  # Original row order and native grid.


_FILES = {
    "HI": ("HI_reion_lumina.txt", "xHI", "dimensionless", "volume-weighted subbox fraction", "median and spatial quantiles", "125 subboxes of side 100 cMpc", "H reionization", 8, "decreasing"),
    "HeIII": ("HeIII_reion_lumina.txt", "xHeIII", "dimensionless", "volume-weighted subbox fraction", "median; interval labels unresolved", "125 subboxes of side 100 cMpc", "He reionization", 8, "decreasing"),
    "SFRD": ("sfrd_lumina.txt", "SFRD", "Msun yr^-1 cMpc^-3", "cosmic volume", "model prediction", "stellar source population", "global", 2, "decreasing"),
    "tau": ("tau_cmb_vs_z_lumina.txt", "tau_cmb", "dimensionless", "proper-electron-density integral; mass-weighted input", "cumulative model prediction", "observer to redshift z", "global", 2, "increasing"),
}


def parse_series(raw: bytes, *, source_url: str, expected_sha256: str,
                 quantity: str) -> ReferenceSeries:
    """Parse exact source bytes, preserving their ordering and declared labels."""
    if quantity not in _FILES:
        raise DomainError(f"unknown reference quantity {quantity}")
    if not source_url or not expected_sha256 or sha256(raw).hexdigest() != expected_sha256:
        raise DomainError("reference source URL or exact byte identity missing/mismatched")
    filename, q, units, weighting, statistic, population, regime, columns, order = _FILES[quantity]
    if not source_url.endswith("/" + filename):
        raise DomainError("source URL does not identify the selected table")
    lines = raw.decode("utf-8").splitlines()
    if not lines or not lines[0].startswith("#"):
        raise DomainError("missing native column header")
    if quantity in ("HI", "HeIII"):
        if not all(x in lines[0] for x in ("Volume weighted", "median", "15p87", "84p13", "2p275", "97p725", "min", "max")):
            raise DomainError("fraction header conflicts with declared schema")
        names = ("#z", *lines[0].split(":", 1)[1].split())
    else:
        names = ("z", "SFRD[Msun/yr/cMpc^3]") if quantity == "SFRD" else ("z", "tau_cmb")
        if names[1] not in lines[0]:
            raise DomainError("table header conflicts with declared schema")
    if len(names) != columns:
        raise DomainError("raw source header column count mismatch")
    rows = []
    for line in lines[1:]:
        if not line.strip() or line.startswith("#"):
            continue
        cells = line.split()
        if len(cells) != columns:
            raise DomainError("wrong numeric column count")
        try:
            row = tuple(_finite(float(x), "table entry") for x in cells)
        except ValueError as exc:
            raise DomainError("invalid table number") from exc
        if row[0] < 0 or (rows and not ((row[0] < rows[-1][0]) if order == "decreasing" else (row[0] > rows[-1][0]))):
            raise DomainError("redshift domain/order invalid")
        if quantity in ("HI", "HeIII") and any(not 0 <= x <= 1 for x in row[1:]):
            raise DomainError("fraction out of range")
        rows.append(row)
    if not rows:
        raise DomainError("empty numeric table")
    invalid = sum(not (r[6] <= r[4] <= r[2] <= r[1] <= r[3] <= r[5] <= r[7]) for r in rows) if quantity in ("HI", "HeIII") else 0
    flags = (f"invalid_quantile_order:{invalid}", "interval_labels_unresolved", "median_only") if quantity == "HeIII" else (("valid_declared_quantiles",) if quantity == "HI" and invalid == 0 else (("invalid_quantile_order",) if invalid else ()))
    return ReferenceSeries(source_url, expected_sha256, q, units,
                           (min(rows[0][0], rows[-1][0]), max(rows[0][0], rows[-1][0])),
                           f"native strictly {order} grid; no extrapolation", weighting,
                           statistic, population, regime, flags, names, tuple(rows))


def load_public_series(data_dir: Path = ROOT / "data") -> dict[str, ReferenceSeries]:
    provenance = json.loads((data_dir / "fetch_attempts.json").read_text())
    entries = {r["filename"]: r for r in provenance["results"]}
    return {key: parse_series((data_dir / spec[0]).read_bytes(),
                              source_url=entries[spec[0]]["url"],
                              expected_sha256=entries[spec[0]]["sha256"], quantity=key)
            for key, spec in _FILES.items()}


def hii_complement(hi: ReferenceSeries) -> ReferenceSeries:
    if hi.quantity != "xHI" or "valid_declared_quantiles" not in hi.validation_flags:
        raise DomainError("HI complement requires validated source quantiles")
    # Median, p15.87, p84.13, p2.275, p97.725, minimum, maximum.
    rows = tuple((r[0], 1-r[1], 1-r[3], 1-r[2], 1-r[5], 1-r[4], 1-r[7], 1-r[6]) for r in hi.rows)
    return ReferenceSeries(hi.source_url, hi.source_sha256, "xHII=1-xHI", hi.units,
                           hi.redshift_domain, hi.sampling, hi.weighting,
                           "transformed subbox median and reversed spatial quantiles", hi.population,
                           hi.regime, ("valid_declared_quantiles", "complement_of_HI"),
                           hi.raw_column_names, rows)


def benchmark_panels(series: dict[str, ReferenceSeries]) -> dict:
    """Native coordinates for four panels; no fits, alignment, or electron estimate."""
    hi, he, sfrd, tau = (series[k] for k in ("HI", "HeIII", "SFRD", "tau"))
    h_ion = hii_complement(hi)
    return {
        "HI_and_HII": {"z": [r[0] for r in hi.rows], "HI": [r[1:] for r in hi.rows],
                       "HII_complement": [r[1:] for r in h_ion.rows],
                       "columns": hi.raw_column_names[1:], "spatial_quantiles_not_likelihood": True,
                       "source_sha256": hi.source_sha256},
        "HeIII": {"z": [r[0] for r in he.rows], "median_only": [r[1] for r in he.rows],
                  "validation_flags": he.validation_flags, "source_sha256": he.source_sha256},
        "SFRD": {"z": [r[0] for r in sfrd.rows], "value": [r[1] for r in sfrd.rows],
                 "units": sfrd.units, "source_sha256": sfrd.source_sha256},
        "tau": {"z": [r[0] for r in tau.rows], "value": [r[1] for r in tau.rows],
                "source_sha256": tau.source_sha256,
                "paper_reported_Planck_reference_constraint": {"mean": .054, "sigma": .007, "type": "reference_constraint_not_table_uncertainty"}},
    }


@dataclass(frozen=True)
class MomentRow:
    regime: str
    lo: float
    hi: float
    mean: float
    sigma: tuple[float, float, float]
    excess: tuple[Optional[float], Optional[float], Optional[float]]
    template: str
    active_species: tuple[str, ...]


def load_moments(path: Path = ROOT / "source" / "radiation_moments.json") -> tuple[MomentRow, ...]:
    data = json.loads(path.read_text())
    if data["species"] != list(SPECIES) or len(data["rows"]) != 7 or data["units"] != {"lo":"eV", "hi":"eV", "mean":"eV", "sigma":"cm2", "excess":"eV"}:
        raise DomainError("moment source schema mismatch")
    rows = []
    for i, r in enumerate(data["rows"]):
        if r["regime"] != ("early" if i < 6 else "late") or not (_positive(r["lo"], "lower edge") < _positive(r["mean"], "mean energy") < _positive(r["hi"], "upper edge")):
            raise DomainError("moment row regime/energy invalid")
        if len(r["sigma"]) != 3 or len(r["excess"]) != 3:
            raise DomainError("moment row shape invalid")
        sigma = tuple(_finite(v, "cross section") for v in r["sigma"])
        excess = tuple(None if v is None else _finite(v, "excess energy") for v in r["excess"])
        if any(v < 0 for v in sigma) or any(v is not None and v < 0 for v in excess):
            raise DomainError("negative moment")
        active = tuple(r.get("active_species", SPECIES))
        if active != (SPECIES if i < 6 else ("HeII",)) or not r["template"]:
            raise DomainError("unsupported active species/template")
        if any(excess[SPECIES.index(s)] is None for s in active if sigma[SPECIES.index(s)] > 0):
            raise DomainError("null active heating moment")
        rows.append(MomentRow(r["regime"], r["lo"], r["hi"], r["mean"], sigma, excess, r["template"], active))
    return tuple(rows)


@dataclass(frozen=True)
class IncidentPhotonExposure:
    phi: tuple[float, ...]
    units: str
    frame: str
    regime: str
    z: float
    spectral_template_identity: tuple[str, ...]
    speed_convention: str
    validity_domain: tuple[float, float]
    source_identity: str
    temporal_trace_identity: str


def validate_exposure(exposure: IncidentPhotonExposure, rows: tuple[MomentRow, ...]) -> tuple[MomentRow, ...]:
    z = _finite(exposure.z, "redshift")
    if z < 0 or exposure.regime != ("early" if z > 4.75 else "late"):
        raise DomainError("redshift/regime branch mismatch")
    selected = tuple(r for r in rows if r.regime == exposure.regime)
    if (exposure.units != "photon cm^-2 s^-1" or exposure.frame != "proper" or
        exposure.speed_convention not in SPEED_CM_S or
        not exposure.source_identity or not exposure.temporal_trace_identity or
        len(exposure.validity_domain) != 2):
        raise DomainError("incident units, frame, speed, source, or trace identity missing")
    zlo, zhi = (_finite(x, "validity domain") for x in exposure.validity_domain)
    if not (0 <= zlo <= z <= zhi):
        raise DomainError("incident redshift outside validity domain")
    if len(exposure.phi) != len(selected) or exposure.spectral_template_identity != tuple(r.template for r in selected):
        raise DomainError("incident row count or template identity mismatch")
    if any(_finite(p, "incident phi") < 0 for p in exposure.phi):
        raise DomainError("negative incident photon exposure")
    return selected


def exposure_from_proper_energy_density(u_erg_cm3: tuple[float, ...], c_rate_cm_s: float,
                                        *, metadata: dict, rows: tuple[MomentRow, ...]) -> IncidentPhotonExposure:
    """Only explicit proper erg/cm^3 with the caller's declared speed maps to phi."""
    if metadata.get("energy_density_units") != "erg cm^-3" or metadata.get("energy_density_frame") != "proper":
        raise DomainError("energy density requires proper erg cm^-3 conversion")
    selected = tuple(r for r in rows if r.regime == metadata.get("regime"))
    if len(u_erg_cm3) != len(selected):
        raise DomainError("energy density bin count mismatch")
    c_rate = _positive(c_rate_cm_s, "c_rate_cm_s")
    if metadata.get("speed_convention") not in SPEED_CM_S or c_rate != SPEED_CM_S[metadata["speed_convention"]]:
        raise DomainError("numeric c_rate does not match declared speed convention")
    if any(_finite(u, "energy density") < 0 for u in u_erg_cm3):
        raise DomainError("negative energy density")
    phi = tuple(c_rate * u / (r.mean * EV_TO_ERG) for u, r in zip(u_erg_cm3, selected))
    try:
        exposure = IncidentPhotonExposure(phi, "photon cm^-2 s^-1", "proper", metadata["regime"],
                 metadata["z"], tuple(metadata["spectral_template_identity"]),
                 metadata["speed_convention"], tuple(metadata["validity_domain"]),
                 metadata["source_identity"], metadata["temporal_trace_identity"])
    except (KeyError, TypeError) as exc:
        raise DomainError("energy-density conversion metadata incomplete") from exc
    validate_exposure(exposure, rows)
    return exposure


@dataclass(frozen=True)
class MomentResult:
    gamma_s: tuple[Optional[float], Optional[float], Optional[float]]
    heat_erg_s_target: tuple[Optional[float], Optional[float], Optional[float]]
    absorbed_erg_s_target: tuple[Optional[float], Optional[float], Optional[float]]
    active_species: tuple[str, ...]


def moment_operator(exposure: IncidentPhotonExposure, rows: tuple[MomentRow, ...]) -> MomentResult:
    selected = validate_exposure(exposure, rows)
    active = SPECIES if exposure.regime == "early" else ("HeII",)
    gamma, heat, absorbed = [], [], []
    for j, species in enumerate(SPECIES):
        if species not in active:
            gamma.append(None); heat.append(None); absorbed.append(None)
            continue
        terms = [(p*r.sigma[j], r.excess[j]) for p, r in zip(exposure.phi, selected) if species in r.active_species]
        gamma.append(math.fsum(rate for rate, _ in terms))
        heat.append(math.fsum(rate*excess*EV_TO_ERG for rate, excess in terms))
        absorbed.append(math.fsum(rate*(THRESHOLDS_EV[j]+excess)*EV_TO_ERG for rate, excess in terms))
    return MomentResult(tuple(gamma), tuple(heat), tuple(absorbed), active)


def photo_heating(result: MomentResult, target_density_cm3: dict[str, float]) -> float:
    if set(target_density_cm3) != set(result.active_species):
        raise DomainError("target densities must specify exactly active species; UVB owns inactive routes")
    density = {s: _finite(n, "density") for s, n in target_density_cm3.items()}
    if any(n < 0 for n in density.values()):
        raise DomainError("negative target density")
    return math.fsum(density[s]*result.heat_erg_s_target[SPECIES.index(s)] for s in result.active_species)


def energy_opacity_cm2(row: MomentRow, species: str) -> Optional[float]:
    """Energy-density opacity σE=σN(threshold+excess)/mean E.

    Inactive routes have no adopted heat/energy operator, even with a listed
    cross section in the late HeII-only transported branch.
    """
    if species not in SPECIES:
        raise DomainError("unknown species")
    if species not in row.active_species:
        return None
    j = SPECIES.index(species)
    return row.sigma[j] * (THRESHOLDS_EV[j]+row.excess[j]) / row.mean


def kinetic_support(exposure: IncidentPhotonExposure, rows: tuple[MomentRow, ...],
                    species: str, maximum_eV: float = 150.0) -> tuple[tuple[int, float], ...]:
    """Certify full primary-electron support; mean excess is never a bound."""
    selected = validate_exposure(exposure, rows)
    if species not in SPECIES or species not in (SPECIES if exposure.regime == "early" else ("HeII",)):
        raise DomainError(f"inactive or unknown kinetic route {species}")
    limit = _positive(maximum_eV, "electron grid maximum")
    j = SPECIES.index(species)
    support = tuple((i, r.hi-THRESHOLDS_EV[j]) for i, (p, r) in enumerate(zip(exposure.phi, selected)) if p > 0 and r.sigma[j] > 0)
    for i, upper in support:
        if upper > limit:
            raise DomainError(f"{exposure.regime} row {i} {species} upper support {upper:.12g} eV exceeds {limit:.12g} eV")
    return support


def helium_electron_projection(x_hii: float, x_hei: float, x_heii: float,
                               x_heiii: float, *, Yp: float = .24) -> float:
    vals = tuple(_finite(v, "helium/electron fraction") for v in (x_hii, x_hei, x_heii, x_heiii))
    if any(not 0 <= v <= 1 for v in vals) or not math.isclose(sum(vals[1:]), 1.0, rel_tol=1e-12, abs_tol=1e-14):
        raise DomainError("helium charge-state simplex invalid; independent HeII required")
    yp = _finite(Yp, "Yp")
    if not 0 < yp < 1:
        raise DomainError("primordial helium mass fraction invalid")
    return vals[0] + yp/(4*(1-yp))*(vals[2]+2*vals[3])


def reaction_source(fluxes_cm3_s: tuple[float, float, float]) -> tuple[float, ...]:
    if len(fluxes_cm3_s) != 3:
        raise DomainError("three signed reaction fluxes required")
    fluxes = tuple(_finite(v, "reaction flux") for v in fluxes_cm3_s)
    return tuple(math.fsum(a*b for a, b in zip(row, fluxes)) for row in STOICHIOMETRY)
