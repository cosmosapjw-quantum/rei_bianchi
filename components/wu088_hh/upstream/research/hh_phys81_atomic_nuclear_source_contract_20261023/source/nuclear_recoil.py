"""Mass-pinned two-body radiative-capture kinematics in the event COM frame.

Only n+p -> d+gamma, n+d -> t+gamma and p+d -> h+gamma are defined;
h is the bare helion (He3 nucleus).  No empirical rate, population source,
temperature evolution, thermal particle ownership or normal-frame adapter
is supplied.  A supplied nonzero incident COM kinetic energy is an event
input, not a Maxwellian average or a finite-temperature closure.

All energies are Decimal MeV, computed from one consistent CODATA 2022
displayed mass-energy column.  Those recommendations have uncertainties
and rounding; 80-digit arithmetic does not make their physical values
exact.  The common mass covariance is not supplied or propagated here.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import (
    Context, Decimal, DecimalException, DivisionByZero, InvalidOperation,
    Overflow, ROUND_HALF_EVEN, Underflow, localcontext,
)
import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Mapping


SOURCE_SHA256 = "ee87900f698e59029a1aafce3d4184870ccc6fa16a8ba50326bd13a10de60aaf"
SOURCE_FILENAME = "NUCLEAR_MASSES_CODATA2022.json"
DECIMAL_PRECISION = 80
SPECIES_ORDER = ("n", "p", "d", "t", "h")

API_METADATA = MappingProxyType({
    "schema": "PHYS81_CAPTURE_COM_EVENT_V1",
    "frame": "one reaction event center-of-momentum frame",
    "energy_unit": "MeV",
    "mass_convention": "bare nuclear ground-state rest masses",
    "source_adjustment": "2022 CODATA",
    "source_sha256": SOURCE_SHA256,
    "source_file": SOURCE_FILENAME,
    "source_url": "https://physics.nist.gov/cuu/Constants/Table/allascii.txt",
    "source_paper_doi": "10.1103/RevModPhys.97.025002",
    "source_pin_scope": "saved transcription bytes, not origin HTML/PDF bytes",
    "arithmetic": "Decimal; ROUND_HALF_EVEN; local context independent of caller",
    "arithmetic_precision_digits": DECIMAL_PRECISION,
    "arithmetic_exponent_limits": (-999999, 999999),
    "derived_uncertainty": "not propagated; common mass covariance unavailable",
    "physical_mass_values_exact": False,
    "empirical_rate_available": False,
    "nuclear_ode_available": False,
    "normal_frame_source_adapter_available": False,
    "finite_temperature_average_available": False,
    "thermal_particle_number_ownership": "unassigned",
    "isotope_substitution": "none; only the three predefined bare-nucleus channels",
    "photon_partition": "escaping photon reservoir in partition_event",
    "recoil_deposition": "caller-supplied zeta required by partition_event",
    "incident_kinetic_ledger": "partition_event debits supplied COM K from thermal reservoir",
    "production_admission": "NOT_ISSUED",
    "HH_R10": "OFF",
})


@dataclass(frozen=True, slots=True)
class NuclearMass:
    """One immutable source row; uncertainties are input metadata only."""

    species: str
    source_symbol: str
    A: int
    Z: int
    energy_equivalent_MeV: Decimal
    standard_uncertainty_MeV: Decimal
    mass_kg: Decimal
    standard_uncertainty_kg: Decimal


@dataclass(frozen=True, slots=True)
class CaptureReaction:
    """Total nuclear-particle count includes free n and p; it is not bath count."""

    reaction_id: str
    reactants: tuple[str, str]
    product: str
    stoichiometry: tuple[int, int, int, int, int]
    delta_baryon_number: int = 0
    delta_nuclear_charge: int = 0
    delta_nuclear_particle_count: int = -1
    delta_derived_electron_count: int = 0


REACTIONS = MappingProxyType({
    "np_d_gamma": CaptureReaction(
        "np_d_gamma", ("n", "p"), "d", (-1, -1, 1, 0, 0)),
    "nd_t_gamma": CaptureReaction(
        "nd_t_gamma", ("n", "d"), "t", (-1, 0, -1, 1, 0)),
    "pd_h_gamma": CaptureReaction(
        "pd_h_gamma", ("p", "d"), "h", (0, -1, -1, 0, 1)),
})

_SOURCE_ROWS = MappingProxyType({
    "m_n": ("n", 1, 0),
    "m_p": ("p", 1, 1),
    "m_d": ("d", 2, 1),
    "m_t": ("t", 3, 1),
    "m_h": ("h", 3, 2),
})


def _arithmetic_context() -> Context:
    # Construct a fresh context so neither global context nor shared mutable
    # decimal flags can alter an evaluation.  Inexact rounding is expected;
    # numerical range failures are rejected rather than clipped.
    return Context(
        prec=DECIMAL_PRECISION, rounding=ROUND_HALF_EVEN,
        Emin=-999999, Emax=999999,
        traps=[InvalidOperation, DivisionByZero, Overflow, Underflow],
    )


def _decimal_scalar(value, name: str) -> Decimal:
    """Accept Decimal, built-in int/float or decimal strings, never bool.

    Float inputs mean their Python decimal-string representation.  Callers
    requiring preservation of supplied decimal digits should use Decimal
    or strings.  Other numeric containers/types are intentionally rejected.
    """
    if isinstance(value, bool) or not isinstance(value, (Decimal, int, float, str)):
        raise ValueError(f"{name}_REQUIRES_DECIMAL_INT_FLOAT_OR_STRING_NOT_BOOL")
    try:
        number = value if isinstance(value, Decimal) else Decimal(str(value))
    except (DecimalException, ValueError) as exc:
        raise ValueError(f"{name}_INVALID_DECIMAL") from exc
    if not number.is_finite():
        raise ValueError(f"{name}_MUST_BE_FINITE")
    return number


def _reaction(reaction_id: str) -> CaptureReaction:
    if not isinstance(reaction_id, str) or reaction_id not in REACTIONS:
        raise ValueError("UNKNOWN_PREDEFINED_CAPTURE_REACTION")
    return REACTIONS[reaction_id]


def _validate_stoichiometry(masses: Mapping[str, NuclearMass]) -> None:
    """Check all predefined channels against the admitted source A/Z data."""
    for reaction in REACTIONS.values():
        if len(reaction.reactants) != 2 or reaction.product not in masses:
            raise ValueError("CAPTURE_REQUIRES_TWO_NUCLEI_TO_ONE_NUCLEUS")
        expected = tuple(
            int(species == reaction.product) - reaction.reactants.count(species)
            for species in SPECIES_ORDER
        )
        if expected != reaction.stoichiometry:
            raise ValueError("CAPTURE_STOICHIOMETRY_MISMATCH")
        delta_A = sum(masses[s].A * nu for s, nu in zip(SPECIES_ORDER, expected))
        delta_Z = sum(masses[s].Z * nu for s, nu in zip(SPECIES_ORDER, expected))
        delta_count = sum(expected)
        if (delta_A, delta_Z, delta_count) != (0, 0, -1):
            raise ValueError("CAPTURE_BARYON_CHARGE_OR_NUCLEAR_COUNT_MISMATCH")
        if (
            reaction.delta_baryon_number != delta_A
            or reaction.delta_nuclear_charge != delta_Z
            or reaction.delta_derived_electron_count != delta_Z
            or reaction.delta_nuclear_particle_count != delta_count
        ):
            raise ValueError("CAPTURE_DECLARED_COUNTS_MISMATCH")


def load_nuclear_masses() -> Mapping[str, NuclearMass]:
    """Read and hash-check the fixed source each time; return immutable rows.

    No caller-supplied mass table, neutral-atom substitution or source cache
    is admitted.  A changed on-disk source therefore fails on the next call.
    """
    path = Path(__file__).resolve().parents[1] / "source_data" / SOURCE_FILENAME
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("CODATA2022_SOURCE_IDENTITY_MISMATCH")
    document = json.loads(raw.decode("utf-8"))
    if (
        document.get("schema") != "PHYS81_COLD_CAPTURE_PRIMARY_MASSES_V1"
        or document.get("adjustment") != "2022 CODATA"
        or document.get("mass_convention")
        != "bare nuclear ground-state rest masses; not neutral atomic masses"
    ):
        raise ValueError("CODATA2022_SOURCE_CONVENTION_MISMATCH")
    rows = document.get("rows")
    if not isinstance(rows, list) or len(rows) != len(_SOURCE_ROWS):
        raise ValueError("CODATA2022_SOURCE_ROW_COUNT_MISMATCH")
    masses = {}
    for row in rows:
        symbol = row.get("symbol")
        if symbol not in _SOURCE_ROWS:
            raise ValueError("CODATA2022_UNKNOWN_NUCLEAR_SPECIES")
        species, A, Z = _SOURCE_ROWS[symbol]
        if species in masses or type(row.get("A")) is not int or type(row.get("Z")) is not int:
            raise ValueError("CODATA2022_DUPLICATE_SPECIES_OR_INVALID_A_Z")
        if (row["A"], row["Z"]) != (A, Z):
            raise ValueError("CODATA2022_A_Z_MISMATCH")
        values = []
        for field in (
            "energy_equivalent_MeV", "standard_uncertainty_MeV",
            "kg", "standard_uncertainty_kg",
        ):
            if not isinstance(row.get(field), str):
                raise ValueError("CODATA2022_DECIMAL_STRING_REQUIRED")
            value = _decimal_scalar(row[field], field.upper())
            if value <= 0:
                raise ValueError("CODATA2022_MASS_AND_UNCERTAINTY_MUST_BE_POSITIVE")
            values.append(value)
        masses[species] = NuclearMass(species, symbol, A, Z, *values)
    if set(masses) != set(SPECIES_ORDER):
        raise ValueError("CODATA2022_NUCLEAR_SPECIES_SET_MISMATCH")
    immutable = MappingProxyType(masses)
    _validate_stoichiometry(immutable)
    return immutable


@dataclass(frozen=True, slots=True)
class CaptureKinematics:
    """One event result; roundoff is arithmetic, not a physical uncertainty."""

    reaction: CaptureReaction
    incident_com_kinetic_MeV: Decimal
    initial_rest_energy_MeV: Decimal
    final_rest_energy_MeV: Decimal
    Q_MeV: Decimal
    W_MeV: Decimal
    available_energy_MeV: Decimal
    photon_energy_MeV: Decimal
    recoil_kinetic_MeV: Decimal
    split_roundoff_MeV: Decimal
    source_sha256: str = SOURCE_SHA256
    arithmetic_precision_digits: int = DECIMAL_PRECISION

    @property
    def metadata(self) -> Mapping:
        return API_METADATA


def capture_kinematics(
    reaction_id: str, *, incident_com_kinetic_MeV=0,
) -> CaptureKinematics:
    """Evaluate the exact two-body formula with finite Decimal arithmetic.

    Let Mi and Mf below denote rest energies in MeV, not masses in kg.
    Q=Mi-Mf, W=Mi+K and Delta=Q+K.  Energy-momentum conservation gives
    E_gamma=Delta*(1-Delta/(2*W)) and K_R=Delta**2/(2*W).
    K=0 is the cold COM limit.  K>=0 is supplied, never inferred from T.
    """
    reaction = _reaction(reaction_id)
    kinetic = _decimal_scalar(incident_com_kinetic_MeV, "INCIDENT_COM_KINETIC_MEV")
    if kinetic < 0:
        raise ValueError("INCIDENT_COM_KINETIC_MEV_MUST_BE_NONNEGATIVE")
    masses = load_nuclear_masses()
    try:
        with localcontext(_arithmetic_context()):
            initial = sum(
                (masses[s].energy_equivalent_MeV for s in reaction.reactants),
                Decimal(0),
            )
            final = masses[reaction.product].energy_equivalent_MeV
            Q = initial - final
            W = initial + kinetic
            available = Q + kinetic
            if Q <= 0 or W <= 0 or not 0 < available < W:
                raise ArithmeticError("CAPTURE_ENERGY_DOMAIN_INVALID_OR_UNRESOLVED")
            ratio = available / (Decimal(2) * W)
            # Multiplication after the bounded ratio avoids an unnecessary
            # Delta**2 intermediate while evaluating the same exact formula.
            recoil = available * ratio
            photon = available * (Decimal(1) - ratio)
            residual = photon + recoil - available
            if not all(v.is_finite() for v in (initial, final, Q, W, available, recoil, photon, residual)):
                raise ArithmeticError("CAPTURE_NONFINITE_ARITHMETIC")
            if photon <= 0 or recoil <= 0:
                raise ArithmeticError("CAPTURE_NONPOSITIVE_OUTPUT_ENERGY")
    except DecimalException as exc:
        raise ArithmeticError("CAPTURE_DECIMAL_ARITHMETIC_OUT_OF_RANGE") from exc
    return CaptureKinematics(
        reaction, kinetic, initial, final, Q, W, available,
        photon, recoil, residual,
    )


@dataclass(frozen=True, slots=True)
class CaptureEventPartition:
    """Signed COM event ledger with explicit caller deposition assignment.

    A positive thermal increment is energy deposited into the designated
    thermal reservoir.  Supplied K is debited from that reservoir; accepting
    that assignment is the caller's precondition.  No bath particle count,
    stochastic reaction rate, photon transport or frame boost is implied.
    """

    kinematics: CaptureKinematics
    zeta: Decimal
    delta_rest_MeV: Decimal
    delta_thermal_MeV: Decimal
    delta_nonthermal_MeV: Decimal
    delta_photon_MeV: Decimal
    closure_residual_MeV: Decimal

    @property
    def metadata(self) -> Mapping:
        return API_METADATA


def partition_event(
    reaction_id: str, *, zeta, incident_com_kinetic_MeV=0,
) -> CaptureEventPartition:
    """Return an optional ledger; zeta in [0,1] must be explicitly supplied.

    Delta_rest=-Q; Delta_thermal=zeta*K_R-K;
    Delta_nonthermal=(1-zeta)*K_R; Delta_photon=E_gamma.
    Their analytic sum is zero.  The stored closure residual reports finite
    Decimal roundoff without forcing a zero or redistributing that residual.
    No automatic heating, thermal-number equation or source adapter exists.
    """
    deposition = _decimal_scalar(zeta, "ZETA")
    if not 0 <= deposition <= 1:
        raise ValueError("ZETA_MUST_LIE_IN_CLOSED_UNIT_INTERVAL")
    event = capture_kinematics(
        reaction_id, incident_com_kinetic_MeV=incident_com_kinetic_MeV,
    )
    try:
        with localcontext(_arithmetic_context()):
            rest = -event.Q_MeV
            thermal = deposition * event.recoil_kinetic_MeV - event.incident_com_kinetic_MeV
            nonthermal = (Decimal(1) - deposition) * event.recoil_kinetic_MeV
            photon = event.photon_energy_MeV
            residual = rest + thermal + nonthermal + photon
            if not all(v.is_finite() for v in (rest, thermal, nonthermal, photon, residual)):
                raise ArithmeticError("CAPTURE_PARTITION_NONFINITE_ARITHMETIC")
    except DecimalException as exc:
        raise ArithmeticError("CAPTURE_PARTITION_DECIMAL_ARITHMETIC_OUT_OF_RANGE") from exc
    return CaptureEventPartition(event, deposition, rest, thermal, nonthermal, photon, residual)


__all__ = (
    "API_METADATA", "SOURCE_SHA256", "DECIMAL_PRECISION", "SPECIES_ORDER",
    "REACTIONS", "NuclearMass", "CaptureReaction", "CaptureKinematics",
    "CaptureEventPartition", "load_nuclear_masses", "capture_kinematics",
    "partition_event",
)
