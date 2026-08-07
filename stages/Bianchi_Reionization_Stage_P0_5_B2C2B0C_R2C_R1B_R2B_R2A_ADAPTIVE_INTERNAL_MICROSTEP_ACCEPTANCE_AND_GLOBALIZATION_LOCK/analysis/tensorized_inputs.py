#!/usr/bin/env python3
"""One-time immutable tensorization for the R2B-R2A adaptive hot path."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import struct
from typing import Mapping

import numpy as np
import pandas as pd

GROUPS = ("G1", "G2a", "G2b", "G3")
OWNERS = (
    "EFFECTIVE_HI_SUBGRID",
    "EXPLICIT_HI_ATOMIC",
    "EXPLICIT_HEI_ATOMIC",
    "EXPLICIT_HEII_ATOMIC",
)
SPECIES = ("HI", "HeI", "HeII")
STATE_FIELDS = ("N_HI", "N_HII", "N_HeI", "N_HeII", "N_HeIII", "U_resolved")
MPC_CM = 3.085677581491367e24

R1_NAME = "Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R1_CANONICAL_INITIAL_MATERIAL_STATE_AND_STATE_DERIVED_OWNER_LAW_LOCK"
R1B1_NAME = "Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R1_CANONICAL_TIME_RESOLVED_GROUP_BOUNDARY_FLUX_DYNAMIC_OPACITY_AND_HEATING_MOMENT_EXTRACTION_LOCK_RERUN_V2"


def _immutable(array: np.ndarray, dtype=np.float64) -> np.ndarray:
    out = np.ascontiguousarray(array, dtype=dtype)
    if np.any(~np.isfinite(out)):
        raise ValueError("tensorized input contains nonfinite values")
    out.setflags(write=False)
    return out


@dataclass(frozen=True)
class ArrayState:
    values: np.ndarray
    temperature_K: np.ndarray

    def __post_init__(self) -> None:
        if self.values.ndim != 2 or self.values.shape[0] != 6:
            raise ValueError("ArrayState.values must have shape [6,N]")
        if self.temperature_K.shape != (self.values.shape[1],):
            raise ValueError("temperature shape mismatch")
        if np.any(~np.isfinite(self.values)) or np.any(self.values < 0.0):
            raise ValueError("state values must be finite and nonnegative")
        if np.any(~np.isfinite(self.temperature_K)) or np.any(self.temperature_K <= 0.0):
            raise ValueError("temperature must be finite and positive")

    def mutable_copy(self) -> "ArrayState":
        return ArrayState(self.values.copy(), self.temperature_K.copy())

    @property
    def node_count(self) -> int:
        return int(self.values.shape[1])


@dataclass(frozen=True)
class TensorizedInputs:
    absorption: np.ndarray
    kappa: np.ndarray
    external_subgrid: np.ndarray
    time_s: np.ndarray
    z_mid: np.ndarray
    gamma_hi: np.ndarray
    thermal_rhs: np.ndarray
    state0: ArrayState
    node_weight: np.ndarray
    delta_total: np.ndarray
    macro_index: np.ndarray
    sigma_cm2: np.ndarray
    owner_support: np.ndarray
    comoving_volume_cm3: np.ndarray


def accepted_bytes(state: ArrayState, ledgers: Mapping[str, float]) -> bytes:
    header = json.dumps(
        {"state_shape": list(state.values.shape), "temperature_shape": list(state.temperature_K.shape),
         "ledgers": {str(k): float(v).hex() for k, v in sorted(ledgers.items())}},
        sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    out = bytearray(b"R2B-R2A-STATE\0")
    out += struct.pack("<Q", len(header)) + header
    out += np.ascontiguousarray(state.values, dtype="<f8").tobytes()
    out += np.ascontiguousarray(state.temperature_K, dtype="<f8").tobytes()
    return bytes(out)


def load_tensorized_inputs(*, repo_root: Path) -> TensorizedInputs:
    root = Path(repo_root)
    r1 = root / "stages" / R1_NAME
    r1b1 = root / "stages" / R1B1_NAME
    forcing = pd.read_csv(
        r1b1 / "data/bdf_replay/canonical_time_resolved_forcing_nodes.csv"
    ).sort_values(["interval_index", "node_index"]).reset_index(drop=True)
    if len(forcing) != 85:
        raise ValueError("canonical forcing must contain 85 rows")
    interval = forcing["interval_index"].to_numpy(int)
    node = forcing["node_index"].to_numpy(int)
    if not np.array_equal(interval, np.repeat(np.arange(5), 17)) or not np.array_equal(
        node, np.tile(np.arange(17), 5)
    ):
        raise ValueError("canonical forcing order is not 5x17")
    absorption = np.stack(
        [forcing[f"absorption_{g}_s-1_cMpc-3"].to_numpy(float) for g in GROUPS], axis=1
    ).reshape(5, 17, 4)
    kappa = np.stack(
        [forcing[f"kappa_{g}_cMpc-1"].to_numpy(float) for g in GROUPS], axis=1
    ).reshape(5, 17, 4)
    time_s = forcing["time_s"].to_numpy(float).reshape(5, 17)
    z_mid = forcing["z_mid"].to_numpy(float).reshape(5, 17)
    gamma_hi = forcing["Gamma_HI_s-1"].to_numpy(float).reshape(5, 17)
    thermal_rhs = forcing["thermal_thermal_rhs_erg_cm-3_s-1"].to_numpy(float).reshape(5, 17)

    owner = pd.read_csv(r1 / "data/owner_law_time_matrix.csv")
    external = np.zeros((5, 17, 4), dtype=float)
    for gi, group in enumerate(GROUPS):
        sub = owner[(owner["group"] == group) & (owner["component"] == "EFFECTIVE_HI_SUBGRID")]
        if len(sub) != 85:
            raise ValueError(f"external subgrid table incomplete for {group}")
        sub = sub.sort_values(["interval_index", "node_index"])
        external[:, :, gi] = sub["raw_component_kappa_cMpc_inv"].to_numpy(float).reshape(5, 17)

    npz = np.load(r1 / "data/initial_material_state_z6.npz")
    values = np.stack([np.asarray(npz[name], dtype=float) for name in STATE_FIELDS], axis=0)
    temperature = np.asarray(npz["T_K"], dtype=float)
    state = ArrayState(_immutable(values), _immutable(temperature))
    node_weight = _immutable(npz["W_node"])
    delta_total = _immutable(npz["delta_total"])
    macro_index = np.ascontiguousarray(npz["macro_index"], dtype=np.int64)
    macro_index.setflags(write=False)

    atomic = pd.read_csv(r1b1 / "data/atomic_moments/verner_gray_and_limit_moments.csv")
    sigma = np.zeros((3, 4), dtype=float)
    for si, species in enumerate(SPECIES):
        for gi, group in enumerate(GROUPS):
            row = atomic[(atomic["species"] == species) & (atomic["group"] == group)]
            if len(row) != 1:
                raise ValueError(f"atomic moment missing for {species}/{group}")
            rec = row.iloc[0]
            sigma[si, gi] = float(rec["gray_sigma_cm2"]) if bool(rec["supported"]) else 0.0
    owner_support = np.array(
        [
            [1, 1, 0, 0],  # effective HI subgrid
            [0, 0, 1, 1],  # explicit HI
            [0, 1, 1, 1],  # explicit HeI
            [0, 0, 0, 1],  # explicit HeII
        ], dtype=np.int8,
    )
    owner_support.setflags(write=False)
    comoving_volume = _immutable(node_weight * MPC_CM**3)

    nonnegative = (absorption, kappa, external, values, node_weight, delta_total, sigma)
    if any(np.any(x < 0.0) for x in nonnegative):
        raise ValueError("load-bearing input contains negative entries")
    return TensorizedInputs(
        absorption=_immutable(absorption),
        kappa=_immutable(kappa),
        external_subgrid=_immutable(external),
        time_s=_immutable(time_s),
        z_mid=_immutable(z_mid),
        gamma_hi=_immutable(gamma_hi),
        thermal_rhs=_immutable(thermal_rhs),
        state0=state,
        node_weight=node_weight,
        delta_total=delta_total,
        macro_index=macro_index,
        sigma_cm2=_immutable(sigma),
        owner_support=owner_support,
        comoving_volume_cm3=comoving_volume,
    )
