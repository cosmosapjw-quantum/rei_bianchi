"""Exact-flow conditional energy ledger for source-verified GL2022 H+ + HD exchange.

This file does NOT supply physical Q, reverse rates, new source rates or an
astrophysical thermal history. All reported bath terms are *affine coefficients*
that become a physical heat prediction only after energy-owner/source admission.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import argparse
import json
import math
from typing import Sequence

from research.wu_hd_source_bound_r18_20261029.src.native_rates import (
    NativeGrid, PDF_SHA256, load_native_grid, SourceContractError,
)
from research.wu_hd_nominal_exchange_r19_20261029.src.nominal_exchange import (
    _state, ModelContractError, STATE_ORDER,
)
from research.wu_hd_source_grid_r20_20261029.src.grid_exposure import (
    Segment, GridFlow, evolve_source_grid,
)

K_B_J_PER_K = 1.380649e-23  # exact 2019 SI numerical constant, float in this implementation
NU = (-1, -1, +1, +1)
_H = (1, 1, 0, 2)
_D = (0, 1, 1, 0)
_CHARGE = (1, 0, 1, 0)
_LEDGER_ISSUER = object()


def _regular_nonnegative_finite(x: object, label: str) -> float:
    if type(x) not in (float, int) or not math.isfinite(float(x)) or float(x) < 0.0:
        raise ModelContractError(f"{label}: nonnegative finite scalar required")
    return float(x)


@dataclass(frozen=True)
class ConditionalCaloricLedger:
    """Source-qualified extent plus thermodynamic geometry, with Q unissued."""

    reaction_extent_events_per_ref_m3: float
    total_particles_per_ref_m3: float
    initial_temperature_K: int
    final_temperature_K: int
    volume_ratio_final: float
    pressure_work_by_material_J_per_ref_m3: float
    thermal_internal_change_J_per_ref_m3: float
    bath_known_intercept_J_per_ref_m3: float
    source_pdf_sha256: str
    reaction_temperature_nodes_K: tuple[int, ...]
    _issuer: object = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self._issuer is not _LEDGER_ISSUER or self.source_pdf_sha256 != PDF_SHA256:
            raise SourceContractError("caloric ledger must be issued through verified source flow")

    @property
    def source_Q_coefficient_events_per_ref_m3(self) -> float:
        return self.reaction_extent_events_per_ref_m3

    def as_json(self) -> dict:
        return {
            "schema": "wu.r21.conditional_caloric_ledger.v1",
            "state_order": list(STATE_ORDER),
            "source": {"source_pdf_sha256": self.source_pdf_sha256,
                       "method": "SQM", "temperature_nodes_K": list(self.reaction_temperature_nodes_K),
                       "physical_rate_uncertainty": None,
                       "reaction": "H+ + HD(v0,j2) -> D+ + H2(v0,j1)"},
            "caloric_model": {"ideal_classical_translational_degrees_per_particle": 3,
                              "k_B_J_K_exact_decimal": "1.380649e-23",
                              "other_internal_degrees_modelled": False,
                              "pressure_law": "p=n_tot*k_B*T",
                              "volume_ratio_final": self.volume_ratio_final,
                              "initial_temperature_K": self.initial_temperature_K,
                              "final_temperature_K": self.final_temperature_K},
            "affine_bath_delta_per_reference_m3": {
                "symbolic_relation": "DeltaB_J_per_ref_m3 = coefficient_events_per_ref_m3 * Q_event_J_per_event + intercept_J_per_ref_m3",
                "coefficient_events_per_ref_m3": self.source_Q_coefficient_events_per_ref_m3,
                "intercept_J_per_ref_m3": self.bath_known_intercept_J_per_ref_m3,
                "mechanical_work_by_material_J_per_ref_m3": self.pressure_work_by_material_J_per_ref_m3,
                "translational_internal_change_J_per_ref_m3": self.thermal_internal_change_J_per_ref_m3,
                "total_particle_number_per_ref_m3": self.total_particles_per_ref_m3,
                "physical_Q_event_J_per_event": None,
                "physical_bath_delta_J_per_ref_m3": None,
            },
            "admission": {"physical_state_energy_Q": False,
                          "named_owner_consumer": False,
                          "thermal_history_external": True,
                          "HH_R10": "OFF", "production": "NOT_ISSUED", "L4": False},
        }


def build_ledger(grid: NativeGrid, initial_m_minus3: Sequence[float],
                 segments: Sequence[Segment]) -> tuple[GridFlow, ConditionalCaloricLedger]:
    """Compute source-locked extent, ideal-gas translational change, exact p dV.

    Physical Q is deliberately not an input, so no physical heat can be emitted.
    Temperature jumps are external bath actions with continuous volume.
    """
    if type(grid) is not NativeGrid or grid.source_sha256 != PDF_SHA256:
        raise SourceContractError("verified R18 original source grid required")
    n0 = _state(initial_m_minus3)
    segs = tuple(segments)
    if not segs or any(type(s) is not Segment for s in segs):
        raise ModelContractError("nonempty typed R20 source-grid segments required")
    result = evolve_source_grid(grid, n0, segs)
    n_total = math.fsum(n0)
    Tinitial, Tfinal = segs[0].temperature_K, segs[-1].temperature_K
    # Since nu·1 == 0, comoving N_total is constant at arbitrary v.
    expected_total = math.fsum(result.final_state_m_minus3)*result.volume_ratio
    total_tolerance = 4e-13 * max(1.0, abs(n_total))
    if abs(expected_total - n_total) > total_tolerance:
        raise ModelContractError("comoving total particle conservation failed")
    zterms = []
    for s in segs:
        z = s.theta_s * s.duration_s
        if not math.isfinite(z):
            raise ModelContractError("nonfinite pressure-work log volume increment")
        zterms.append(s.temperature_K * z)
    # Includes expansion/contraction; signed sum is intentionally preserved.
    mech = n_total * K_B_J_PER_K * math.fsum(zterms)
    du_trans = 1.5 * n_total * K_B_J_PER_K * (Tfinal - Tinitial)
    intercept = -math.fsum((mech, du_trans))
    if not all(math.isfinite(x) for x in (mech,du_trans,intercept)):
        raise ModelContractError("thermodynamic ledger overflow")
    ledger = ConditionalCaloricLedger(
        reaction_extent_events_per_ref_m3=result.extent_reference_m_minus3,
        total_particles_per_ref_m3=n_total,
        initial_temperature_K=Tinitial, final_temperature_K=Tfinal,
        volume_ratio_final=result.volume_ratio,
        pressure_work_by_material_J_per_ref_m3=mech,
        thermal_internal_change_J_per_ref_m3=du_trans,
        bath_known_intercept_J_per_ref_m3=intercept,
        source_pdf_sha256=result.source_pdf_sha256,
        reaction_temperature_nodes_K=result.temperature_nodes_K,
        _issuer=_LEDGER_ISSUER,
    )
    return result, ledger


def source_chemical_energy_release_from_qualified_levels(
    energies_J_per_particle: Sequence[float], *, source_admitted: bool = False
) -> float:
    """Formal Q from independently supplied e_i; never marks it as physical.

    Although this function computes a number from synthetic input, physical-source
    admission is not supported in R21. source_admitted=True is intentionally rejected.
    """
    if source_admitted:
        raise SourceContractError("physical state energies not admitted in R21")
    if len(energies_J_per_particle) != 4:
        raise ModelContractError("four exact state energy labels required")
    energies = []
    for i, e in enumerate(energies_J_per_particle):
        if type(e) not in (int,float) or not math.isfinite(float(e)):
            raise ModelContractError(f"energy[{i}] must be finite")
        energies.append(float(e))
    q = math.fsum((-nu*e for nu,e in zip(NU,energies)))
    if not math.isfinite(q):
        raise ModelContractError("formal Q overflow")
    return q


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-pdf", type=Path, required=True)
    parser.add_argument("--schedule-json", type=Path, required=True)
    parser.add_argument("--initial-m3", type=float, nargs=4, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.schedule_json.read_text(encoding="utf-8"))
        if (type(data) is not dict or data.get("schema") != "wu.r20.schedule.v1"
                or type(data.get("segments")) is not list):
            raise ModelContractError("source-grid schedule contract mismatch")
        segs = []
        for row in data["segments"]:
            if type(row) is not dict or set(row) != {"temperature_K","duration_s","theta_s"}:
                raise ModelContractError("exact R20 schedule segment fields required")
            segs.append(Segment(**row))
        grid = load_native_grid(args.source_pdf)
        flow, ledger = build_ledger(grid, args.initial_m3, segs)
        output = {"ledger": ledger.as_json(), "source_flow": flow.as_json()}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as target:
            json.dump(output,target,indent=2)
            target.write("\n")
        return 0
    except (SourceContractError, ModelContractError, ValueError, OSError, TypeError) as exc:
        print(f"{type(exc).__name__}: {exc}",file=__import__('sys').stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
