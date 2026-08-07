#!/usr/bin/env python3
"""State-derived four-owner opacity/current law for R1B-R2B-R1.

Canonical group-total opacity and current remain authoritative.  A nonnegative
raw response is recomputed from the current material state for explicit H I,
He I and He II, while the effective-HI subgrid response is inherited as an
external time-dependent closure.  Raw responses are conditioned onto the
canonical totals before any owner/node disintegration.

The primary subgrid node measure is the predeclared local-neutral-hazard law;
the two historical alternatives remain auditors and are never selected after
seeing results.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib.util
import math
from pathlib import Path
import sys
from typing import Any, Mapping

import numpy as np
import pandas as pd

MPC_CM = 3.085677581491367e24
NH0_CM3 = 1.88e-7
YHE = 0.079
GROUPS = ("G1", "G2a", "G2b", "G3")
COMPONENTS = (
    "EFFECTIVE_HI_SUBGRID",
    "EXPLICIT_HI_ATOMIC",
    "EXPLICIT_HEI_ATOMIC",
    "EXPLICIT_HEII_ATOMIC",
)
RESOLVED_SOURCE = {
    "EFFECTIVE_HI_SUBGRID": (0, 0, 0),
    "EXPLICIT_HI_ATOMIC": (1, 0, 1),
    "EXPLICIT_HEI_ATOMIC": (0, 1, 1),
    "EXPLICIT_HEII_ATOMIC": (0, 1, 1),
}
SUPPORT = {
    ("EFFECTIVE_HI_SUBGRID", "G1"),
    ("EFFECTIVE_HI_SUBGRID", "G2a"),
    ("EXPLICIT_HI_ATOMIC", "G2b"),
    ("EXPLICIT_HI_ATOMIC", "G3"),
    ("EXPLICIT_HEI_ATOMIC", "G2a"),
    ("EXPLICIT_HEI_ATOMIC", "G2b"),
    ("EXPLICIT_HEI_ATOMIC", "G3"),
    ("EXPLICIT_HEII_ATOMIC", "G3"),
}


@dataclass(frozen=True)
class OwnerLawResult:
    owner_table: pd.DataFrame
    node_allocations: dict[tuple[str, str], np.ndarray]
    node_support: dict[tuple[str, str], np.ndarray]
    node_hashes: dict[tuple[str, str], str]
    metadata: dict[str, Any]


def _hash(values: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(np.asarray(values, dtype="<f8")).tobytes()).hexdigest()


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
    total = float(total)
    values = {name: float(raw.get(name, 0.0)) for name in COMPONENTS}
    if total < 0.0 or not math.isfinite(total):
        raise ValueError("authoritative opacity must be finite and nonnegative")
    if any(v < 0.0 or not math.isfinite(v) for v in values.values()):
        raise ValueError("raw owner response must be finite and nonnegative")
    support = math.fsum(values.values())
    if support == 0.0:
        if total != 0.0:
            raise ValueError("nonzero authoritative opacity on zero raw support")
        return {name: 0.0 for name in COMPONENTS}
    conditioned = {name: total * values[name] / support for name in COMPONENTS}
    positive = [name for name in COMPONENTS if values[name] > 0.0]
    conditioned[positive[-1]] += total - math.fsum(conditioned.values())
    return conditioned


def _allocate(total: float, measure: np.ndarray) -> np.ndarray:
    h = np.asarray(measure, dtype=float)
    if h.ndim != 1 or np.any(~np.isfinite(h)) or np.any(h < 0.0):
        raise ValueError("node measure must be finite and nonnegative")
    support = math.fsum(float(x) for x in h)
    if support == 0.0:
        if total != 0.0:
            raise ValueError("nonzero owner current on zero node support")
        return np.zeros_like(h)
    out = float(total) * h / support
    positive = np.flatnonzero(h > 0.0)
    out[positive[-1]] += float(total) - math.fsum(float(x) for x in out)
    return out


def _normalize_stage_root(path: Path) -> Path:
    p = Path(path)
    if p.exists():
        return p
    candidate = p.parent / "stages" / p.name
    if candidate.exists():
        return candidate
    raise FileNotFoundError(p)


class StateDerivedOwnerLaw:
    def __init__(self, *, r1_root: Path, r2a_root: Path, initial_state: Any) -> None:
        self.r1_root = _normalize_stage_root(Path(r1_root))
        self.r2a_root = _normalize_stage_root(Path(r2a_root))
        self.initial_state = initial_state
        self.forcing = pd.read_csv(
            self.r1_root / "data" / "bdf_replay" / "canonical_time_resolved_forcing_nodes.csv"
        ).sort_values(["interval_index", "node_index"]).reset_index(drop=True)
        self.owner_reference = pd.read_csv(
            self.r2a_root / "data" / "time_resolved_owner_split.csv"
        )
        atomic = pd.read_csv(
            self.r1_root / "data" / "atomic_moments" / "verner_gray_and_limit_moments.csv"
        )
        self.sigma = {
            (str(r.species), str(r.group)): float(r.gray_sigma_cm2)
            for r in atomic.itertuples()
            if bool(r.supported)
        }
        source_dir = self.r1_root / "inputs" / "canonical_b2c2a_r1_src"
        if str(source_dir.resolve()) not in sys.path:
            sys.path.insert(0, str(source_dir.resolve()))
        self.b2c1a = __import__("hi_transmission_kernel_b2c1a")

    @staticmethod
    def _row_key(rec: Mapping[str, Any]) -> tuple[int, int]:
        return int(rec["interval_index"]), int(rec["node_index"])

    def _external_subgrid_raw(self, rec: Mapping[str, Any], group: str) -> float:
        interval, node = self._row_key(rec)
        sub = self.owner_reference[
            (self.owner_reference["interval_index"] == interval)
            & (self.owner_reference["node_index"] == node)
            & (self.owner_reference["group"] == group)
            & (self.owner_reference["component"] == "EFFECTIVE_HI_SUBGRID")
        ]
        if len(sub) != 1:
            raise RuntimeError(f"missing external subgrid response for {(interval, node, group)}")
        return float(sub.iloc[0]["raw_component_kappa_cMpc_inv"])

    def _global_raw(self, rec: Mapping[str, Any], state: pd.DataFrame, group: str) -> dict[str, float]:
        n_h = math.fsum(float(x) for x in (state["N_HI"] + state["N_HII"]).to_numpy())
        n_he = math.fsum(
            float(x)
            for x in (state["N_HeI"] + state["N_HeII"] + state["N_HeIII"]).to_numpy()
        )
        if n_h <= 0.0 or n_he <= 0.0:
            raise ValueError("material nuclei totals must be positive")
        x_hii = math.fsum(float(x) for x in state["N_HII"].to_numpy()) / n_h
        x_hei = math.fsum(float(x) for x in state["N_HeI"].to_numpy()) / n_he
        x_heii = math.fsum(float(x) for x in state["N_HeII"].to_numpy()) / n_he
        z = float(rec["z_mid"])
        a = 1.0 / (1.0 + z)
        n_h_phys = NH0_CM3 * (1.0 + z) ** 3
        n_he_phys = YHE * n_h_phys
        raw = {name: 0.0 for name in COMPONENTS}
        if ("EFFECTIVE_HI_SUBGRID", group) in SUPPORT:
            raw["EFFECTIVE_HI_SUBGRID"] = self._external_subgrid_raw(rec, group)
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
                a * n_he_phys * x_heii * self.sigma[("HeII", group)] * MPC_CM
            )
        return raw

    def _subgrid_measure(self, rec: Mapping[str, Any], state: pd.DataFrame, group: str) -> np.ndarray:
        if group not in {"G1", "G2a"}:
            return np.zeros(len(state), dtype=float)
        z = float(rec["z_mid"])
        w = state["W_node"].to_numpy(dtype=float)
        volume = w * MPC_CM**3 / (1.0 + z) ** 3
        n_h_total = (state["N_HI"] + state["N_HII"]).to_numpy(dtype=float)
        n_hi = np.divide(
            state["N_HI"].to_numpy(dtype=float),
            volume,
            out=np.zeros(len(state), dtype=float),
            where=volume > 0.0,
        )
        x_hii = np.divide(
            state["N_HII"].to_numpy(dtype=float),
            n_h_total,
            out=np.zeros(len(state), dtype=float),
            where=n_h_total > 0.0,
        )
        n_he_total = (state["N_HeI"] + state["N_HeII"] + state["N_HeIII"]).to_numpy(dtype=float)
        x_heii = np.divide(
            state["N_HeII"].to_numpy(dtype=float),
            n_he_total,
            out=np.zeros(len(state), dtype=float),
            where=n_he_total > 0.0,
        )
        x_heiii = np.divide(
            state["N_HeIII"].to_numpy(dtype=float),
            n_he_total,
            out=np.zeros(len(state), dtype=float),
            where=n_he_total > 0.0,
        )
        sigma = self.sigma[("HI", group)]
        gamma_hi = float(rec["Gamma_HI_s-1"])
        gray_sigma = float(self.b2c1a.gray_sigma_hi()[0])
        chi = float(self.b2c1a.calibrate_chi_jeans(z, gamma_hi, gray_sigma)["chi_J"])
        n_h_phys = np.divide(n_h_total, volume, out=np.zeros_like(n_h_total), where=volume > 0.0)
        length = chi * self.b2c1a.jeans_length_cm(
            n_h_phys,
            state["T_K"].to_numpy(dtype=float),
            x_hii,
            x_heii,
            x_heiii,
        )
        transmission = np.exp(-0.5 * np.clip(n_hi * sigma * length, 0.0, 745.0))
        # W_node converts the local hazard into the fixed comoving measure.
        return w * n_hi * sigma * transmission

    def _node_measure(self, rec: Mapping[str, Any], state: pd.DataFrame, group: str, component: str) -> np.ndarray:
        if (component, group) not in SUPPORT:
            return np.zeros(len(state), dtype=float)
        if component == "EFFECTIVE_HI_SUBGRID":
            return self._subgrid_measure(rec, state, group)
        if component == "EXPLICIT_HI_ATOMIC":
            species = state["N_HI"].to_numpy(dtype=float)
            sigma = self.sigma[("HI", group)]
        elif component == "EXPLICIT_HEI_ATOMIC":
            species = state["N_HeI"].to_numpy(dtype=float)
            sigma = self.sigma[("HeI", group)]
        elif component == "EXPLICIT_HEII_ATOMIC":
            species = state["N_HeII"].to_numpy(dtype=float)
            sigma = self.sigma[("HeII", group)]
        else:
            raise KeyError(component)
        return species * sigma

    def evaluate(self, *, forcing_row: Mapping[str, Any], state_frame: pd.DataFrame) -> OwnerLawResult:
        state = state_frame.copy()
        required = {
            "N_HI", "N_HII", "N_HeI", "N_HeII", "N_HeIII",
            "U_resolved", "T_K", "W_node", "macro_index",
        }
        missing = required - set(state.columns)
        if missing:
            raise KeyError(f"state frame missing columns: {sorted(missing)}")
        material = state[["N_HI", "N_HII", "N_HeI", "N_HeII", "N_HeIII", "U_resolved", "T_K"]].to_numpy(dtype=float)
        if np.any(~np.isfinite(material)) or np.any(material[:, :6] < 0.0) or np.any(material[:, 6] <= 0.0):
            raise ValueError("state frame is outside the positive material cone")

        owner_rows: list[dict[str, Any]] = []
        allocations: dict[tuple[str, str], np.ndarray] = {}
        supports: dict[tuple[str, str], np.ndarray] = {}
        hashes: dict[tuple[str, str], str] = {}
        max_kappa_residual = 0.0
        max_current_residual = 0.0

        for group in GROUPS:
            kappa_total = float(forcing_row[f"kappa_{group}_cMpc-1"])
            current_total = float(forcing_row[f"absorption_{group}_s-1_cMpc-3"])
            raw = self._global_raw(forcing_row, state, group)
            conditioned = _condition(kappa_total, raw)
            phi = current_total / kappa_total if kappa_total > 0.0 else 0.0
            group_kappa = 0.0
            group_current = 0.0
            for component in COMPONENTS:
                kappa = conditioned[component]
                current = phi * kappa
                fraction = kappa / kappa_total if kappa_total > 0.0 else 0.0
                measure = self._node_measure(forcing_row, state, group, component)
                allocation = _allocate(current, measure)
                key = (group, component)
                allocations[key] = allocation
                supports[key] = measure > 0.0
                hashes[key] = _hash(allocation)
                owner_rows.append(
                    {
                        "group": group,
                        "component": component,
                        "conditioned_kappa_cMpc_inv": kappa,
                        "authoritative_kappa_cMpc_inv": kappa_total,
                        "owner_current_s_inv_cMpc3": current,
                        "authoritative_current_s_inv_cMpc3": current_total,
                        "conditioned_fraction": fraction,
                        "raw_component_kappa_cMpc_inv": raw[component],
                    }
                )
                group_kappa += kappa
                group_current += current
            max_kappa_residual = max(
                max_kappa_residual,
                abs(group_kappa - kappa_total) / max(abs(kappa_total), 1.0e-300),
            )
            max_current_residual = max(
                max_current_residual,
                abs(group_current - current_total) / max(abs(current_total), 1.0),
            )

        metadata = {
            "classification": "STATE_DERIVED_FOUR_OWNER_LAW",
            "primary_subgrid_lane": "LOCAL_NEUTRAL_HAZARD_PRIMARY",
            "auditor_lanes": [
                "RECOMBINATION_WEIGHTED_AUDITOR",
                "SCRIPT_SELF_SHIELDING_AUDITOR",
            ],
            "post_hoc_lane_selection_used": False,
            "authoritative_total_amplitude": "CANONICAL_B2C2A_R1",
            "subgrid_global_response": "EXTERNALLY_FORCED_TIME_DEPENDENT_EFFECTIVE_HI",
            "resolved_response": "CURRENT_MATERIAL_STATE_VERNER_GRAY",
            "max_kappa_sum_relative_residual": max_kappa_residual,
            "max_current_sum_relative_residual": max_current_residual,
            "clipping_used": False,
            "per_node_fit_used": False,
        }
        return OwnerLawResult(
            owner_table=pd.DataFrame(owner_rows),
            node_allocations=allocations,
            node_support=supports,
            node_hashes=hashes,
            metadata=metadata,
        )
