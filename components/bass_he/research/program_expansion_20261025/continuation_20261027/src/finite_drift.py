"""Same-law quadratic H--He heating, reusing INTAKE01 pair/caloric adapters.

The calculation is a conditional Taylor model, not a fitted angular law or a
certified physical finite-drift solver. See THEORY_KO.md for the exact identities.
The invariant equations apply to distinct elastic species; this adapter retains
the inherited H--He source domain and input evidence contract.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import importlib.util
import math
from numbers import Real
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PREVIOUS = ROOT.parent / "continuation_20261025"


def _load(name, relative, expected):
    path = PREVIOUS / relative
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise RuntimeError(f"Inherited dependency identity changed: {relative}")
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


PAIR = _load("he_drift02_intake01_pair", "pair_source/h_he_intake.py",
             "f32a8079c1c182c79f46073dbe3e10e41875394e6959dabcb8bb7f80022909d7")
CALORIC = _load("he_drift02_intake01_caloric", "exchange/exchange_closure.py",
                "533c49838d03572b106168cd9333a20e1b4a7d06f88d5f3727f8b80c5b96f262")


def _finite(value, name, *, positive=False):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite real scalar")
    try:
        value = float(value)
    except (OverflowError, ValueError) as error:
        raise ValueError(f"{name} is not representable in binary64") from error
    if not math.isfinite(value) or (positive and value <= 0.0):
        raise ValueError(f"{name} must be finite" + (" and positive" if positive else ""))
    return value


def _vec(value, name):
    try:
        out = tuple(_finite(x, name) for x in value)
    except TypeError as error:
        raise ValueError(f"{name} must have three finite real components") from error
    if len(out) != 3:
        raise ValueError(f"{name} must have three components")
    return out


def _dot(a, b):
    return math.fsum(x * y for x, y in zip(a, b))


@dataclass(frozen=True)
class QuadraticDriftResult:
    T_star_K: float
    thermal_relative_variance_m2_s2: float
    relative_drift_m_s: tuple[float, float, float]
    drift_ratio_squared: float
    maximum_drift_ratio: float
    q12_over_q11: float
    beta: float
    linear_drag_kg_m3_s: float
    heat_exchange_H_W_m3: float
    quadratic_heat_H_W_m3: float
    quadratic_heat_He_W_m3: float
    centered_heat_H_W_m3: float
    centered_heat_He_W_m3: float
    force_H_N_m3: tuple[float, float, float]
    force_He_N_m3: tuple[float, float, float]
    raw_kinetic_H_W_m3: float
    raw_kinetic_He_W_m3: float
    bulk_power_W_m3: float
    drift_dissipation_W_m3: float
    energy_balance_residual_W_m3: float
    temperature_rate_H_K_s: float | None
    temperature_rate_He_K_s: float | None
    q11_value_evidence: str
    q12_value_evidence: str
    mass_binding_evidence: str
    same_law_evidence: str
    small_drift_contract: str
    particle_source_H_m3_s: float = 0.0
    particle_source_He_m3_s: float = 0.0
    binding_energy_source_W_m3: float = 0.0
    nonthermal_energy_source_W_m3: float = 0.0
    force_order: str = "linear; omitted O(|U|^3) at fixed input state"
    heat_order: str = "quadratic; omitted O(|U|^4) at fixed input state"
    remainder_bound_certified: bool = False
    calibrated_source_uncertainty: None = None
    physical_provider_admitted: bool = False
    basis: str = "DERIVED_CONDITIONAL_SAME_LAW_MAXWELLIAN_TAYLOR_MODEL"

    def to_dict(self):
        return asdict(self)


def conditional_h_he_drift(
    *, T_H_K, T_He_K, n_H_m3, n_He_m3, mass_H_kg, mass_He_kg,
    velocity_H_m_s, velocity_He_m_s, q11_m2, q12_m2,
    q11_temperature_K, q12_temperature_K, q11_value_evidence,
    q12_value_evidence, mass_binding_evidence, same_law_evidence,
    maximum_drift_ratio, small_drift_contract,
):
    """Return first-order force and second-order species-centered elastic heat.

    Same-law evidence is a supplied hypothesis/provenance, not automatically an
    admission. The caller's drift cutoff bounds |U|/s, not a truncation error.
    Opposite raw kinetic sources follow only after including species bulk work.
    Thermal particle count is conserved; binding/nonthermal reservoirs are idle.
    """
    # Normalize the new public interface before entering the unchanged baseline.
    T_H_K, T_He_K, n_H_m3, n_He_m3, mass_H_kg, mass_He_kg, q11_m2, q11_temperature_K = (
        _finite(value, name) for value, name in (
            (T_H_K, "T_H_K"), (T_He_K, "T_He_K"),
            (n_H_m3, "n_H_m3"), (n_He_m3, "n_He_m3"),
            (mass_H_kg, "mass_H_kg"), (mass_He_kg, "mass_He_kg"),
            (q11_m2, "q11_m2"), (q11_temperature_K, "q11_temperature_K")))
    base = PAIR.conditional_h_he_moments(
        T_H_K=T_H_K, T_He_K=T_He_K, n_H_m3=n_H_m3, n_He_m3=n_He_m3,
        mass_H_kg=mass_H_kg, mass_He_kg=mass_He_kg,
        q11_m2=q11_m2, q11_temperature_K=q11_temperature_K,
        q11_value_evidence=q11_value_evidence,
        mass_binding_evidence=mass_binding_evidence,
    )
    q12 = _finite(q12_m2, "q12_m2", positive=True)
    qtemp = _finite(q12_temperature_K, "q12_temperature_K", positive=True)
    if qtemp != base.T_star_K:
        raise ValueError("Q12 must have exactly the same T_star as Q11")
    for value, name in ((q12_value_evidence, "q12_value_evidence"),
                        (same_law_evidence, "same_law_evidence"),
                        (small_drift_contract, "small_drift_contract")):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must identify its evidence or hypothesis")
    cutoff = _finite(maximum_drift_ratio, "maximum_drift_ratio", positive=True)
    if cutoff >= 1.0:
        raise ValueError("Declare a small-drift cutoff below unity; this is not an error certificate")
    ua, ub = _vec(velocity_H_m_s, "velocity_H"), _vec(velocity_He_m_s, "velocity_He")
    try:
        u = _vec((x - y for x, y in zip(ua, ub)), "relative velocity")
        u2 = _finite(_dot(u, u), "relative speed squared")
        if any(u) and u2 == 0.0:
            raise ValueError("Nonzero relative speed squared underflowed")
        s2 = _finite(PAIR.KB_J_K * base.T_star_K / base.reduced_mass_kg,
                     "relative thermal variance", positive=True)
        drift2 = _finite(u2 / s2, "drift ratio squared")
        if u2 > 0.0 and drift2 == 0.0:
            raise ValueError("Nonzero drift ratio underflowed")
        if math.sqrt(drift2) > cutoff:
            raise ValueError("Relative drift exceeds the caller's declared Taylor domain")
        scale = max(mass_H_kg, mass_He_kg)
        aa, bb = mass_H_kg / scale, mass_He_kg / scale
        fa, fb = aa / (aa + bb), bb / (aa + bb)
        beta = fa * fb * ((T_H_K - T_He_K) / base.T_star_K)
        ratio = _finite(q12 / q11_m2, "Q12/Q11", positive=True)
        zeta = 2.5 - 3.0 * ratio
        k = base.linear_drag_kg_m3_s
        dissipated = _finite(k * u2, "drift dissipation")
        if k > 0.0 and u2 > 0.0 and dissipated == 0.0:
            raise ValueError("Nonzero drift dissipation underflowed")
        dha = _finite(dissipated * (fb + beta * zeta), "quadratic H heat")
        dhb = _finite(dissipated * (fa - beta * zeta), "quadratic He heat")
        qa = _finite(base.heat_a_W_m3 + dha, "centered H heat")
        qb = _finite(base.heat_b_W_m3 + dhb, "centered He heat")
        ra = _vec((-k * x for x in u), "H force")
        rb = tuple(-x for x in ra)
        if k > 0.0 and any(u) and not any(ra):
            raise ValueError("Nonzero force underflowed")
        bulk_a, bulk_b = _dot(ua, ra), _dot(ub, rb)
        ea, eb = _finite(qa + bulk_a, "raw H power"), _finite(qb + bulk_b, "raw He power")
        bulk = _finite(math.fsum((bulk_a, bulk_b)), "bulk power")
        residual = _finite(math.fsum((ea, eb)), "total kinetic power residual")
    except (OverflowError, ZeroDivisionError) as error:
        raise ValueError("Derived drift moments exceed binary64 representability") from error

    def temperature_rate(label, density, temp, heat):
        if density == 0.0:
            return None  # no temperature is assigned to an absent population
        row = CALORIC.monatomic_caloric(label, density, 0.0, temp,
                                       population_pool="thermal")
        result = CALORIC.temperature_rhs(
            [row], temperature_k=temp, expansion_s=0.0,
            pressure_pa=density * PAIR.KB_J_K * temp,
            centered_heat_w_m3=heat, shear_work_w_m3=0.0,
            heat_flux_divergence_w_m3=0.0,
            common_temperature_contract="single species translational temperature; no interspecies common-T assumption",
        )
        return _finite(result["temperature_rate_k_s"], label + " temperature rate")

    return QuadraticDriftResult(
        base.T_star_K, s2, u, drift2, cutoff, ratio, beta, k,
        base.heat_a_W_m3, dha, dhb, qa, qb, ra, rb, ea, eb, bulk,
        dissipated, residual,
        temperature_rate("H", n_H_m3, T_H_K, qa),
        temperature_rate("He", n_He_m3, T_He_K, qb),
        q11_value_evidence, q12_value_evidence, mass_binding_evidence,
        same_law_evidence, small_drift_contract,
    )
