"""SI moment and caloric adapters for HE's selected-source continuation.

These functions do not generate cross sections, infer an angular law from scalar
rates, evolve an IVP, or compile WU reactions. See THEORY_KO.md for the conventions.
Provider admission is an external evidence record; algebraic checks never create it.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import fsum, isfinite
from typing import Iterable, Mapping

K_B = 1.380649e-23  # J/K, exact SI defining value
Vec3 = tuple[float, float, float]
Mat3 = tuple[Vec3, Vec3, Vec3]


class ContractError(ValueError):
    """Input does not satisfy the explicitly declared interface contract."""


def _finite(x: float, name: str) -> float:
    if isinstance(x, bool) or not isfinite(x):
        raise ContractError(f"{name} must be a finite real scalar")
    return float(x)


def _positive(x: float, name: str) -> float:
    value = _finite(x, name)
    if value <= 0:
        raise ContractError(f"{name} must be positive")
    return value


def _vec(x: Iterable[float], name: str) -> Vec3:
    result = tuple(_finite(v, name) for v in x)
    if len(result) != 3:
        raise ContractError(f"{name} must have three components")
    return result


def _dot(a: Vec3, b: Vec3) -> float:
    return fsum(a[i] * b[i] for i in range(3))


def _mat(a: Iterable[Iterable[float]], name: str) -> Mat3:
    result = tuple(_vec(row, name) for row in a)
    if len(result) != 3:
        raise ContractError(f"{name} must be 3 by 3")
    if any(result[i][j] != result[j][i] for i in range(3) for j in range(3)):
        raise ContractError(f"{name} must be symmetric")
    return result


@dataclass(frozen=True)
class ConservativeSource:
    """Raw kinetic moments, all per proper volume and proper time.

    mass_kg_m3_s = m_s Gamma_s; momentum_kg_m2_s2 is the conservative
    raw source R_s; kinetic_w_m3 excludes binding/rest-mass energy.
    """

    mass_kg_m3_s: float
    momentum_kg_m2_s2: Vec3
    kinetic_w_m3: float

    def centered(self, bulk_m_s: Vec3) -> dict[str, object]:
        u = _vec(bulk_m_s, "bulk_m_s")
        s = _finite(self.mass_kg_m3_s, "mass source")
        r = _vec(self.momentum_kg_m2_s2, "raw momentum source")
        e = _finite(self.kinetic_w_m3, "raw kinetic source")
        drag = tuple(r[i] - u[i] * s for i in range(3))
        # With raw R the mass term is PLUS. With F=R-u*S it is MINUS.
        q = e - _dot(u, r) + 0.5 * _dot(u, u) * s
        return {"centered_heat_w_m3": q, "acceleration_source_kg_m2_s2": drag}

    def change_frame(self, boost_m_s: Vec3) -> ConservativeSource:
        """New velocities v'=v-boost. Transform reactive raw moments."""
        w = _vec(boost_m_s, "boost_m_s")
        s = _finite(self.mass_kg_m3_s, "mass source")
        r = _vec(self.momentum_kg_m2_s2, "raw momentum source")
        e = _finite(self.kinetic_w_m3, "raw kinetic source")
        return ConservativeSource(
            s, tuple(r[i] - w[i] * s for i in range(3)),
            e - _dot(w, r) + 0.5 * _dot(w, w) * s,
        )


@dataclass(frozen=True)
class AngularTransport:
    """Complete-COM-angle sigma_0, sigma_1, sigma_2 in m^2.

    sigma_0=int d_sigma; sigma_l=int(1-P_l(cos chi)) d_sigma for l=1,2.
    These may be supplied moments. They are not inferred from thermal rates.
    """

    sigma0_m2: float
    sigma1_m2: float
    sigma2_m2: float

    def validate(self) -> None:
        s0, s1, s2 = (_finite(x, "cross section") for x in (
            self.sigma0_m2, self.sigma1_m2, self.sigma2_m2))
        if min(s0, s1, s2) < 0:
            raise ContractError("transport cross sections must be nonnegative")
        if s0 == 0:
            if s1 != 0 or s2 != 0:
                raise ContractError("zero measure has zero transport moments")
            return
        # Exact algebraic Hausdorff conditions for the first two cosine moments.
        mean = 1.0 - s1 / s0
        second = 1.0 - 2.0 * s2 / (3.0 * s0)
        if not (-1 <= mean <= 1 and mean * mean <= second <= 1):
            raise ContractError("sigma_0/1/2 fail the cosine moment cone")


@dataclass(frozen=True)
class TransportSource:
    """Explicit source qualification for one labelled, elastic species pair."""

    source_id: str
    immutable_locator: str
    projectile_id: str
    target_id: str
    energy_min_j: float
    energy_max_j: float
    full_com_angular_support: bool
    axisymmetric_about_relative_velocity: bool
    finite_mass_source_validated: bool
    count_convention: str
    evidence_status: str
    uncertainty_locator: str

    def check(self, relative_energy_j: float, purpose: str) -> None:
        e = _finite(relative_energy_j, "relative energy")
        lo = _finite(self.energy_min_j, "lower source energy")
        hi = _finite(self.energy_max_j, "upper source energy")
        if lo < 0 or hi < lo or not lo <= e <= hi:
            raise ContractError("energy outside declared COM-relative source support")
        if not all((self.source_id, self.immutable_locator,
                    self.projectile_id, self.target_id, self.uncertainty_locator)):
            raise ContractError("source, species and uncertainty provenance are required")
        if not self.full_com_angular_support:
            raise ContractError("a finite angular window cannot enter the full-angle map")
        if not self.axisymmetric_about_relative_velocity:
            raise ContractError("nonaxisymmetric source requires tensor angular moments")
        if self.count_convention != "labelled_pair_once":
            raise ContractError("supplier must resolve event versus inclusive count")
        if purpose not in {"conditional_algebra", "physical_evaluation"}:
            raise ContractError("declare conditional_algebra or physical_evaluation")
        if purpose == "physical_evaluation" and (
            self.evidence_status != "physical_admitted" or
            not self.finite_mass_source_validated
        ):
            raise ContractError("physical evaluation requires an independently admitted source")


def elastic_moment_kernel(
    mass_a_kg: float, mass_b_kg: float, velocity_a_m_s: Vec3,
    velocity_b_m_s: Vec3, angular: AngularTransport, source: TransportSource,
    *, purpose: str,
) -> dict[str, object]:
    """Exact angle-integrated, finite-mass Newtonian elastic moment map.

    Outputs are cross-section weighted event increments, NOT volumetric rates.
    The distribution owner still supplies int f_a f_b |g| (...) d^3v_a d^3v_b.
    No speed quadrature, source extrapolation, or time evolution occurs here.
    """
    ma = _positive(mass_a_kg, "mass_a_kg")
    mb = _positive(mass_b_kg, "mass_b_kg")
    va, vb = _vec(velocity_a_m_s, "velocity_a"), _vec(velocity_b_m_s, "velocity_b")
    # Fractions and reduced mass can be representable when ma+mb overflows.
    mass_scale = max(ma, mb)
    scaled_a, scaled_b = ma / mass_scale, mb / mass_scale
    scaled_sum = scaled_a + scaled_b
    aa, bb = scaled_a / scaled_sum, scaled_b / scaled_sum
    mu = _positive(min(ma, mb) / (1.0 + min(ma, mb) / mass_scale), "reduced mass")
    g = _vec((va[i] - vb[i] for i in range(3)), "derived relative velocity")
    v = _vec((aa * va[i] + bb * vb[i] for i in range(3)), "derived COM velocity")
    try:
        g2 = _finite(_dot(g, g), "derived relative speed squared")
        v_dot_g = _finite(_dot(v, g), "derived COM-relative contraction")
    except (OverflowError, ValueError) as error:
        raise ContractError("derived velocity moments exceed binary64 representability") from error
    relative_energy = _finite(0.5 * mu * g2, "derived relative kinetic energy")
    source.check(relative_energy, purpose)
    angular.validate()
    dp = tuple(-mu * angular.sigma1_m2 * x for x in g)
    de = -mu * angular.sigma1_m2 * v_dot_g
    gg_stf = tuple(tuple(g[i] * g[j] - (g2 / 3 if i == j else 0)
                         for j in range(3)) for i in range(3))
    vg = tuple(tuple(v[i] * g[j] + g[i] * v[j] for j in range(3))
               for i in range(3))
    ba = tuple(tuple(-mu * (angular.sigma1_m2 * vg[i][j] +
                            bb * angular.sigma2_m2 * gg_stf[i][j])
                     for j in range(3)) for i in range(3))
    bb_tensor = tuple(tuple(mu * (angular.sigma1_m2 * vg[i][j] -
                                 aa * angular.sigma2_m2 * gg_stf[i][j])
                            for j in range(3)) for i in range(3))
    total_stf = tuple(tuple(-mu * angular.sigma2_m2 * gg_stf[i][j]
                           for j in range(3)) for i in range(3))
    _vec(dp, "derived momentum moment")
    _finite(de, "derived kinetic moment")
    for tensor in (ba, bb_tensor, total_stf):
        for row in tensor:
            _vec(row, "derived second moment")
    return {
        "source_id": source.source_id, "evidence_status": source.evidence_status,
        "purpose": purpose, "relative_energy_j": relative_energy,
        "momentum_a_kg_m3_s": dp,
        "momentum_b_kg_m3_s": tuple(-x for x in dp),
        "kinetic_a_j_m2": de, "kinetic_b_j_m2": -de,
        "second_moment_a_j_m2": ba, "second_moment_b_j_m2": bb_tensor,
        "total_stf_j_m2": total_stf,
        "unit_note": "momentum unit is (kg m/s)*m^2; energy/tensor unit is J*m^2",
    }


@dataclass(frozen=True)
class CaloricSpecies:
    """One explicitly thermal particle population at the supplied common T.

    For non-LTE level populations use translation only and let REC own explicit
    level energy. Equilibrium molecular internal terms may be in epsilon/cv
    only when their component IDs are absent from independent reservoirs.
    """

    species_id: str
    number_m3: float
    number_source_m3_s: float
    epsilon_j: float
    cv_particle_j_k: float
    temperature_k: float
    caloric_source: str
    population_pool: str
    included_internal_components: tuple[str, ...] = ()


def monatomic_caloric(species_id: str, number_m3: float,
                      number_source_m3_s: float, temperature_k: float,
                      *, population_pool: str) -> CaloricSpecies:
    t = _positive(temperature_k, "temperature_k")
    return CaloricSpecies(species_id, number_m3, number_source_m3_s,
                          1.5 * K_B * t, 1.5 * K_B, t,
                          "derived ideal nonrelativistic translational energy", population_pool)


def temperature_rhs(
    species: Iterable[CaloricSpecies], *, temperature_k: float,
    expansion_s: float, pressure_pa: float, centered_heat_w_m3: float,
    shear_work_w_m3: float, heat_flux_divergence_w_m3: float,
    common_temperature_contract: str,
    independent_internal_components: Iterable[str] = (),
) -> dict[str, float]:
    """Local common-bulk ideal-mixture chain rule; no IVP or LTE inference.

    e=sum n_s epsilon_s(T), C_V=sum n_s c_v,s(T), Dn_s+Theta*n_s=Gamma_s.
    Q must already be the centered source of the SAME thermal pool.
    """
    t = _positive(temperature_k, "temperature_k")
    theta = _finite(expansion_s, "expansion")
    p = _finite(pressure_pa, "pressure")
    if p < 0 or not common_temperature_contract:
        raise ContractError("nonnegative pressure and a common-temperature contract are required")
    rows = tuple(species)
    if not rows or len({r.species_id for r in rows}) != len(rows):
        raise ContractError("explicit, unique thermal population IDs are required")
    excluded = set(independent_internal_components)
    included: set[str] = set()
    for row in rows:
        n = _finite(row.number_m3, "number density")
        c = _finite(row.cv_particle_j_k, "per-particle heat capacity")
        eps = _finite(row.epsilon_j, "caloric energy")
        _finite(row.number_source_m3_s, "number source")
        if (n < 0 or c < 0 or eps < 0 or row.temperature_k != t or
                row.population_pool != "thermal"):
            raise ContractError("invalid caloric state or mismatched evaluation temperature")
        if not row.species_id or not row.caloric_source:
            raise ContractError("species identity and caloric provenance are required")
        for component in row.included_internal_components:
            if component in excluded or component in included:
                raise ContractError("internal-energy component has two owners")
            included.add(component)
    cv = fsum(row.number_m3 * row.cv_particle_j_k for row in rows)
    _positive(cv, "volumetric heat capacity")
    count_power = fsum(row.epsilon_j * row.number_source_m3_s for row in rows)
    power = (_finite(centered_heat_w_m3, "centered heat") - theta * p
             - _finite(shear_work_w_m3, "shear contraction")
             - _finite(heat_flux_divergence_w_m3, "heat flux divergence") - count_power)
    return {
        "temperature_rate_k_s": power / cv, "heat_capacity_j_m3_k": cv,
        "number_m3": fsum(row.number_m3 for row in rows),
        "number_source_m3_s": fsum(row.number_source_m3_s for row in rows),
        "particle_count_power_w_m3": count_power,
        "caloric_energy_j_m3": fsum(row.number_m3 * row.epsilon_j for row in rows),
    }


@dataclass(frozen=True)
class PopulationSourceReceipt:
    """Already-compiled WU/CR count source; source_id is a canonical event/transfer ID."""

    source_id: str
    population_id: str
    pool: str
    number_rate_m3_s: float
    owner_repo: str
    source_locator: str


def project_population_sources(
    receipts: Iterable[PopulationSourceReceipt], canonical_owner_by_source: Mapping[str, str],
) -> dict[str, dict[str, float]]:
    """Separate thermal Gamma from nonthermal birth/removal without redoing stoichiometry."""
    seen: set[tuple[str, str]] = set()
    pools: dict[str, dict[str, list[float]]] = {"thermal": {}, "nonthermal": {}}
    population_pool: dict[str, str] = {}
    for receipt in receipts:
        key = (receipt.source_id, receipt.population_id)
        if (not all((receipt.source_id, receipt.population_id, receipt.owner_repo,
                     receipt.source_locator)) or key in seen or receipt.pool not in pools):
            raise ContractError("invalid or duplicate population source receipt")
        if canonical_owner_by_source.get(receipt.source_id) != receipt.owner_repo:
            raise ContractError("population source owner differs from canonical supplier")
        if population_pool.setdefault(receipt.population_id, receipt.pool) != receipt.pool:
            raise ContractError("one population identity cannot name thermal and nonthermal pools")
        seen.add(key)
        value = _finite(receipt.number_rate_m3_s, "population number source")
        pools[receipt.pool].setdefault(receipt.population_id, []).append(value)
    return {pool: {identity: fsum(values) for identity, values in rows.items()}
            for pool, rows in pools.items()}


@dataclass(frozen=True)
class EnergyAccount:
    account_id: str
    component_id: str  # physical energy component, independent of representation
    reservoir: str
    representation: str  # "evolved" or "population_derived"
    owner_repo: str


@dataclass(frozen=True)
class EnergyTransfer:
    """Consumer receipt for an existing canonical supplier transfer, in W/m^3."""

    transfer_id: str
    owner_repo: str
    source_account: str
    target_account: str
    power_w_m3: float
    source_locator: str


RESERVOIRS = frozenset({
    "thermal_kinetic", "bulk_kinetic", "nonthermal_kinetic", "chemical_binding",
    "internal_excitation", "nuclear_mass", "radiation_retained", "radiation_escaped",
    "neutrino_escaped", "external_work",
})


def project_energy_transfers(
    accounts: Iterable[EnergyAccount], transfers: Iterable[EnergyTransfer],
    canonical_owner_by_transfer: Mapping[str, str],
) -> dict[str, object]:
    """Project already-compiled supplier transfers without duplicating WU logic.

    Each transfer has one owner and two opposite signed legs. A population-derived
    account returns an expected derivative witness, never an independent evolved RHS.
    """
    account_rows = tuple(accounts)
    by_id = {a.account_id: a for a in account_rows}
    if (len(by_id) != len(account_rows) or
            len({a.component_id for a in account_rows}) != len(account_rows)):
        raise ContractError("duplicate account or physical energy component identity")
    for a in account_rows:
        if (not a.account_id or not a.component_id or not a.owner_repo or a.reservoir not in RESERVOIRS or
                a.representation not in {"evolved", "population_derived"}):
            raise ContractError("invalid account identity, owner, reservoir or representation")
        if a.representation == "population_derived" and a.reservoir not in {
            "chemical_binding", "internal_excitation", "nuclear_mass"
        }:
            raise ContractError("this adapter only derives internal/rest energy from populations")
    seen: set[str] = set()
    postings: dict[str, list[float]] = {key: [] for key in by_id}
    for transfer in transfers:
        if not transfer.transfer_id or transfer.transfer_id in seen:
            raise ContractError("duplicate or empty canonical transfer identity")
        seen.add(transfer.transfer_id)
        if (not transfer.owner_repo or
                canonical_owner_by_transfer.get(transfer.transfer_id) != transfer.owner_repo):
            raise ContractError("transfer owner differs from canonical supplier owner")
        if not transfer.source_locator or transfer.source_account == transfer.target_account:
            raise ContractError("transfer provenance and two distinct accounts are required")
        if transfer.source_account not in by_id or transfer.target_account not in by_id:
            raise ContractError("untracked energy endpoint")
        power = _finite(transfer.power_w_m3, "transfer power")
        if power < 0:
            raise ContractError("reverse transfer endpoints rather than supplying negative power")
        postings[transfer.source_account].append(-power)
        postings[transfer.target_account].append(power)
    rates = {key: fsum(value) for key, value in postings.items()}
    return {
        "evolved_rhs_w_m3": {k: v for k, v in rates.items()
                              if by_id[k].representation == "evolved"},
        "population_derivative_witness_w_m3": {k: v for k, v in rates.items()
                                               if by_id[k].representation == "population_derived"},
        "all_accounts_rate_w_m3": rates,
        "conservation_residual_w_m3": fsum(rates.values()),
        "consumed_transfer_ids": sorted(seen),
    }


@dataclass(frozen=True)
class SpeciesPressure:
    species_id: str
    mass_density_kg_m3: float
    velocity_m_s: Vec3
    central_pressure_pa: Mat3


def common_bulk_pressure(species: Iterable[SpeciesPressure]) -> dict[str, object]:
    """Exact mixture projection for already-admitted symmetric species pressures.

    This algebraic adapter does not certify positive moment realizability or infer
    common T/u. The consumer must retain the input state's existing moment-cone gate.
    """
    rows = tuple(species)
    if not rows or len({r.species_id for r in rows}) != len(rows):
        raise ContractError("unique species pressures are required")
    checked = []
    for row in rows:
        rho = _finite(row.mass_density_kg_m3, "mass density")
        u, p = _vec(row.velocity_m_s, "species velocity"), _mat(row.central_pressure_pa, "pressure")
        if rho < 0 or (rho == 0 and any(x != 0 for rr in p for x in rr)):
            raise ContractError("negative density or pressure in an absent species")
        checked.append((rho, u, p))
    rho_total = fsum(r[0] for r in checked)
    _positive(rho_total, "total mass density")
    bulk = tuple(fsum(rho * u[i] for rho, u, _ in checked) / rho_total for i in range(3))
    total = tuple(tuple(fsum(p[i][j] + rho * (u[i] - bulk[i]) * (u[j] - bulk[j])
                             for rho, u, p in checked)
                        for j in range(3)) for i in range(3))
    scalar = fsum(total[i][i] for i in range(3)) / 3
    stf = tuple(tuple(total[i][j] - (scalar if i == j else 0)
                       for j in range(3)) for i in range(3))
    drift_energy = 0.5 * fsum(rho * _dot(tuple(u[i] - bulk[i] for i in range(3)),
                                        tuple(u[i] - bulk[i] for i in range(3)))
                              for rho, u, _ in checked)
    return {"bulk_m_s": bulk, "pressure_pa": total, "scalar_pressure_pa": scalar,
            "stf_pressure_pa": stf, "drift_energy_j_m3": drift_energy}
