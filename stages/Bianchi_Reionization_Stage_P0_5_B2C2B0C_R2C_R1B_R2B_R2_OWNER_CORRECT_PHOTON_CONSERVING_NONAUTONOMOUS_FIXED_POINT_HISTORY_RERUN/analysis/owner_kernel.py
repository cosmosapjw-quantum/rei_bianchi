#!/usr/bin/env python3
"""Fast state-conditioned four-owner and node disintegration kernel.

Canonical total group opacity/current is authoritative.  Current material state
sets explicit atomic raw responses and all node measures.  The effective-HI
subgrid global amplitude remains external, while its node distribution is one
of three predeclared lanes.  No per-node fitting or post-hoc lane selection is
available in this module.
"""
from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import math
from pathlib import Path
import sys
from typing import Any, Mapping

import numpy as np
import pandas as pd

GROUPS = ("G1", "G2a", "G2b", "G3")
COMPONENTS = (
    "EFFECTIVE_HI_SUBGRID",
    "EXPLICIT_HI_ATOMIC",
    "EXPLICIT_HEI_ATOMIC",
    "EXPLICIT_HEII_ATOMIC",
)
SUPPORT = frozenset(
    {
        ("EFFECTIVE_HI_SUBGRID", "G1"),
        ("EFFECTIVE_HI_SUBGRID", "G2a"),
        ("EXPLICIT_HI_ATOMIC", "G2b"),
        ("EXPLICIT_HI_ATOMIC", "G3"),
        ("EXPLICIT_HEI_ATOMIC", "G2a"),
        ("EXPLICIT_HEI_ATOMIC", "G2b"),
        ("EXPLICIT_HEI_ATOMIC", "G3"),
        ("EXPLICIT_HEII_ATOMIC", "G3"),
    }
)
UNSUPPORTED = tuple(
    (component, group)
    for component in COMPONENTS
    for group in GROUPS
    if (component, group) not in SUPPORT
)
RESOLVED_SOURCE_FLAGS = {
    "EFFECTIVE_HI_SUBGRID": (0, 0, 0),
    "EXPLICIT_HI_ATOMIC": (1, 0, 1),
    "EXPLICIT_HEI_ATOMIC": (0, 1, 1),
    "EXPLICIT_HEII_ATOMIC": (0, 1, 1),
}
LANES = (
    "LOCAL_NEUTRAL_HAZARD_PRIMARY",
    "RECOMBINATION_WEIGHTED_AUDITOR",
    "SCRIPT_SELF_SHIELDING_AUDITOR",
)
MPC_CM = 3.085677581491367e24
NH0_CM3 = 1.88e-7
YHE = 0.079


@dataclass(frozen=True)
class OwnerKernelResult:
    owner_kappa: dict[tuple[str, str], float]
    owner_current: dict[tuple[str, str], float]
    owner_fraction: dict[tuple[str, str], float]
    node_current: dict[tuple[str, str], np.ndarray]
    node_fraction: dict[tuple[str, str], np.ndarray]
    resolved_source_flags: dict[str, tuple[int, int, int]]
    max_kappa_residual: float
    max_current_residual: float
    max_node_residual: float


def _load_module(name: str, path: Path) -> Any:
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _condition(total: float, raw: Mapping[str, float]) -> dict[str, float]:
    values = {component: float(raw.get(component, 0.0)) for component in COMPONENTS}
    if not math.isfinite(total) or total < 0.0:
        raise ValueError("authoritative total must be finite and nonnegative")
    if any(not math.isfinite(v) or v < 0.0 for v in values.values()):
        raise ValueError("raw owner responses must be finite and nonnegative")
    support = math.fsum(values.values())
    if support == 0.0:
        if total != 0.0:
            raise ValueError("nonzero authoritative total on zero owner support")
        return {component: 0.0 for component in COMPONENTS}
    out = {component: total * values[component] / support for component in COMPONENTS}
    positive = [component for component in COMPONENTS if values[component] > 0.0]
    out[positive[-1]] += total - math.fsum(out.values())
    return out


def _allocate(total: float, measure: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    h = np.asarray(measure, dtype=float)
    if h.ndim != 1 or np.any(~np.isfinite(h)) or np.any(h < 0.0):
        raise ValueError("node measure must be finite and nonnegative")
    support = math.fsum(float(x) for x in h)
    if support == 0.0:
        if total != 0.0:
            raise ValueError("nonzero current on zero node support")
        return np.zeros_like(h), np.zeros_like(h)
    q = h / support
    positive = np.flatnonzero(h > 0.0)
    q[positive[-1]] += 1.0 - math.fsum(float(x) for x in q)
    current = float(total) * q
    current[positive[-1]] += float(total) - math.fsum(float(x) for x in current)
    return q, current


class DynamicOwnerKernel:
    def __init__(
        self,
        *,
        initial_state: Mapping[str, np.ndarray],
        sigma: Mapping[tuple[str, str], float],
        original_law: Any,
    ) -> None:
        self.static = {
            name: np.asarray(initial_state[name]).copy()
            for name in ("W_node", "macro_index", "delta_total")
        }
        self.sigma = dict(sigma)
        self.original_law = original_law

    @classmethod
    def from_stage_inputs(
        cls,
        *,
        initial_state: Mapping[str, np.ndarray],
        atomic_moments_csv: Path,
        r1b_r1_stage: Path,
        r2a_stage: Path,
    ) -> "DynamicOwnerKernel":
        atomic = pd.read_csv(atomic_moments_csv)
        sigma = {
            (str(row.species), str(row.group)): float(row.gray_sigma_cm2)
            for row in atomic.itertuples()
            if bool(row.supported)
        }
        r1b_r1_stage = Path(r1b_r1_stage)
        state_law_module = _load_module(
            "r2b_r2_inherited_state_law",
            r1b_r1_stage.parent
            / "Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R1_CANONICAL_INITIAL_MATERIAL_STATE_AND_STATE_DERIVED_OWNER_LAW_LOCK"
            / "analysis/state_derived_owner_law.py",
        )
        # The inherited object supplies the exact Jeans and historical auditor
        # measures. Its external subgrid table is not used by this kernel.
        placeholder = type("Initial", (), {"frame": pd.DataFrame(initial_state)})()
        original = state_law_module.StateDerivedOwnerLaw(
            r1_root=r1b_r1_stage,
            r2a_root=Path(r2a_stage),
            initial_state=placeholder,
        )
        return cls(initial_state=initial_state, sigma=sigma, original_law=original)

    def _frame(self, state: Mapping[str, np.ndarray]) -> pd.DataFrame:
        required_dynamic = (
            "N_HI",
            "N_HII",
            "N_HeI",
            "N_HeII",
            "N_HeIII",
            "U_resolved",
            "T_K",
        )
        data: dict[str, np.ndarray] = dict(self.static)
        size = len(self.static["W_node"])
        for name in required_dynamic:
            value = np.asarray(state[name], dtype=float)
            if value.shape != (size,):
                raise ValueError(f"state field {name} has wrong shape")
            data[name] = value
        frame = pd.DataFrame(data)
        material = frame[list(required_dynamic)].to_numpy(float)
        if np.any(~np.isfinite(material)) or np.any(material[:, :6] < 0.0) or np.any(material[:, 6] <= 0.0):
            raise ValueError("state lies outside the positive material cone")
        return frame

    def _global_raw(
        self,
        *,
        forcing_row: Mapping[str, float],
        frame: pd.DataFrame,
        group: str,
        external_subgrid_raw: Mapping[str, float],
    ) -> dict[str, float]:
        n_h = math.fsum(float(x) for x in (frame["N_HI"] + frame["N_HII"]).to_numpy())
        n_he = math.fsum(
            float(x)
            for x in (frame["N_HeI"] + frame["N_HeII"] + frame["N_HeIII"]).to_numpy()
        )
        if n_h <= 0.0 or n_he <= 0.0:
            raise ValueError("material nuclei totals must be positive")
        x_hii = math.fsum(float(x) for x in frame["N_HII"].to_numpy()) / n_h
        x_hei = math.fsum(float(x) for x in frame["N_HeI"].to_numpy()) / n_he
        # Match the inherited convention: HeII abundance normalized per H.
        x_heii_per_h = math.fsum(float(x) for x in frame["N_HeII"].to_numpy()) / n_h
        z = float(forcing_row["z_mid"])
        a = 1.0 / (1.0 + z)
        n_h_phys = NH0_CM3 * (1.0 + z) ** 3
        n_he_phys = YHE * n_h_phys
        raw = {component: 0.0 for component in COMPONENTS}
        if ("EFFECTIVE_HI_SUBGRID", group) in SUPPORT:
            value = float(external_subgrid_raw.get(group, 0.0))
            if not math.isfinite(value) or value < 0.0:
                raise ValueError("external subgrid response must be finite and nonnegative")
            raw["EFFECTIVE_HI_SUBGRID"] = value
        if ("EXPLICIT_HI_ATOMIC", group) in SUPPORT:
            raw["EXPLICIT_HI_ATOMIC"] = (
                a * n_h_phys * (1.0 - x_hii) * self.sigma[("HI", group)] * MPC_CM
            )
        if ("EXPLICIT_HEI_ATOMIC", group) in SUPPORT:
            raw["EXPLICIT_HEI_ATOMIC"] = (
                a * n_he_phys * x_hei * self.sigma[("HeI", group)] * MPC_CM
            )
        if ("EXPLICIT_HEII_ATOMIC", group) in SUPPORT:
            raw["EXPLICIT_HEII_ATOMIC"] = (
                a * n_he_phys * x_heii_per_h * self.sigma[("HeII", group)] * MPC_CM
            )
        return raw

    def subgrid_measure(
        self,
        *,
        forcing_row: Mapping[str, float],
        state: Mapping[str, np.ndarray],
        group: str,
        lane: str,
    ) -> np.ndarray:
        if lane not in LANES:
            raise KeyError(f"unknown predeclared subgrid lane {lane!r}")
        frame = self._frame(state)
        measures = self.original_law.subgrid_lane_measures(
            forcing_row=forcing_row, state_frame=frame, group=group
        )
        return np.asarray(measures[lane], dtype=float)

    def _node_measure(
        self,
        *,
        forcing_row: Mapping[str, float],
        state: Mapping[str, np.ndarray],
        frame: pd.DataFrame,
        group: str,
        component: str,
        subgrid_lane: str,
    ) -> np.ndarray:
        if (component, group) not in SUPPORT:
            return np.zeros(len(frame), dtype=float)
        if component == "EFFECTIVE_HI_SUBGRID":
            return self.subgrid_measure(
                forcing_row=forcing_row, state=state, group=group, lane=subgrid_lane
            )
        if component == "EXPLICIT_HI_ATOMIC":
            return frame["N_HI"].to_numpy(float) * self.sigma[("HI", group)]
        if component == "EXPLICIT_HEI_ATOMIC":
            return frame["N_HeI"].to_numpy(float) * self.sigma[("HeI", group)]
        if component == "EXPLICIT_HEII_ATOMIC":
            return frame["N_HeII"].to_numpy(float) * self.sigma[("HeII", group)]
        raise KeyError(component)

    def evaluate(
        self,
        *,
        forcing_row: Mapping[str, float],
        state: Mapping[str, np.ndarray],
        external_subgrid_raw: Mapping[str, float],
        subgrid_lane: str,
    ) -> OwnerKernelResult:
        if subgrid_lane not in LANES:
            raise KeyError(subgrid_lane)
        frame = self._frame(state)
        owner_kappa: dict[tuple[str, str], float] = {}
        owner_current: dict[tuple[str, str], float] = {}
        owner_fraction: dict[tuple[str, str], float] = {}
        node_current: dict[tuple[str, str], np.ndarray] = {}
        node_fraction: dict[tuple[str, str], np.ndarray] = {}
        max_kappa = max_current = max_node = 0.0

        for group in GROUPS:
            kappa_total = float(forcing_row[f"kappa_{group}_cMpc-1"])
            current_total = float(forcing_row[f"absorption_{group}_s-1_cMpc-3"])
            raw = self._global_raw(
                forcing_row=forcing_row,
                frame=frame,
                group=group,
                external_subgrid_raw=external_subgrid_raw,
            )
            kappas = _condition(kappa_total, raw)
            phi = current_total / kappa_total if kappa_total > 0.0 else 0.0
            for component in COMPONENTS:
                key = (group, component)
                kappa = kappas[component]
                current = phi * kappa
                fraction = kappa / kappa_total if kappa_total > 0.0 else 0.0
                measure = self._node_measure(
                    forcing_row=forcing_row,
                    state=state,
                    frame=frame,
                    group=group,
                    component=component,
                    subgrid_lane=subgrid_lane,
                )
                q, allocated = _allocate(current, measure)
                owner_kappa[key] = kappa
                owner_current[key] = current
                owner_fraction[key] = fraction
                node_fraction[key] = q
                node_current[key] = allocated
                node_sum = math.fsum(float(x) for x in allocated)
                max_node = max(max_node, abs(node_sum - current) / max(abs(current), 1.0))
            ksum = math.fsum(owner_kappa[(group, c)] for c in COMPONENTS)
            jsum = math.fsum(owner_current[(group, c)] for c in COMPONENTS)
            max_kappa = max(max_kappa, abs(ksum - kappa_total) / max(abs(kappa_total), 1e-300))
            max_current = max(max_current, abs(jsum - current_total) / max(abs(current_total), 1.0))

        return OwnerKernelResult(
            owner_kappa=owner_kappa,
            owner_current=owner_current,
            owner_fraction=owner_fraction,
            node_current=node_current,
            node_fraction=node_fraction,
            resolved_source_flags=dict(RESOLVED_SOURCE_FLAGS),
            max_kappa_residual=max_kappa,
            max_current_residual=max_current,
            max_node_residual=max_node,
        )
