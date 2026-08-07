#!/usr/bin/env python3
"""Array-native state-conditioned owner and node allocation kernel.

This module is a drop-in numerical oracle for the DataFrame-based R2B-R2
``DynamicOwnerKernel``.  It preserves the inherited physics and arithmetic
conventions while removing DataFrame construction, groupby/filtering, and
per-row Python object allocation from the adaptive hot path.

Authoritative group-total opacity/current remain external inputs.  The current
material state determines explicit atomic raw responses and all node measures;
the effective-HI global amplitude remains externally locked.  Unsupported
owner/group pairs are structural exact zero.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import importlib.util
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np

try:
    from r2b_r2a_tensorized import (
        ArrayState,
        TensorizedInputs,
        GROUPS,
        OWNERS,
        SPECIES,
        MPC_CM,
    )
except ImportError:  # loaded by path outside the test module namespace
    _HERE = Path(__file__).resolve().parent
    _SPEC = importlib.util.spec_from_file_location(
        "r2b_r2a_tensorized", _HERE / "tensorized_inputs.py"
    )
    if _SPEC is None or _SPEC.loader is None:
        raise ImportError("cannot load tensorized_inputs.py")
    _MODULE = importlib.util.module_from_spec(_SPEC)
    sys.modules[_SPEC.name] = _MODULE
    _SPEC.loader.exec_module(_MODULE)
    ArrayState = _MODULE.ArrayState
    TensorizedInputs = _MODULE.TensorizedInputs
    GROUPS = _MODULE.GROUPS
    OWNERS = _MODULE.OWNERS
    SPECIES = _MODULE.SPECIES
    MPC_CM = _MODULE.MPC_CM

NH0_CM3 = 1.88e-7
YHE = 0.079
LANES = (
    "LOCAL_NEUTRAL_HAZARD_PRIMARY",
    "RECOMBINATION_WEIGHTED_AUDITOR",
    "SCRIPT_SELF_SHIELDING_AUDITOR",
)


@dataclass(frozen=True)
class OwnerEvaluation:
    owner_kappa: np.ndarray      # [owner, group]
    owner_current: np.ndarray    # [owner, group]
    owner_fraction: np.ndarray   # [owner, group]
    node_current: np.ndarray     # [owner, group, node]
    node_fraction: np.ndarray    # [owner, group, node]
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


def _condition(total: float, raw: np.ndarray) -> np.ndarray:
    total = float(total)
    values = np.asarray(raw, dtype=np.float64)
    if values.shape != (4,):
        raise ValueError("owner raw response must have shape [4]")
    if not math.isfinite(total) or total < 0.0:
        raise ValueError("authoritative total must be finite and nonnegative")
    if np.any(~np.isfinite(values)) or np.any(values < 0.0):
        raise ValueError("raw owner responses must be finite and nonnegative")
    support = math.fsum(float(v) for v in values)
    if support == 0.0:
        if total != 0.0:
            raise ValueError("nonzero authoritative total on zero owner support")
        return np.zeros(4, dtype=np.float64)
    out = total * values / support
    target = int(np.argmax(values))
    out[target] += total - math.fsum(float(v) for v in out)
    return out


def _allocate(total: float, measure: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    h = np.asarray(measure, dtype=np.float64)
    if h.ndim != 1 or np.any(~np.isfinite(h)) or np.any(h < 0.0):
        raise ValueError("node measure must be finite and nonnegative")
    support = float(np.sum(h, dtype=np.float64))
    if support == 0.0:
        if float(total) != 0.0:
            raise ValueError("nonzero current on zero node support")
        zeros = np.zeros_like(h)
        return zeros.copy(), zeros
    q = h / support
    target = int(np.argmax(h))
    q[target] += 1.0 - float(np.sum(q, dtype=np.float64))
    current = float(total) * q
    current[target] += float(total) - float(np.sum(current, dtype=np.float64))
    return q, current


class ArrayOwnerKernel:
    """Array-native parity implementation of the locked four-owner law."""

    def __init__(
        self,
        *,
        inputs: TensorizedInputs,
        b2c1a: Any,
        b2c0: Any,
        gray_sigma_hi: float,
        chi_cache: dict[tuple[float, float], float] | None = None,
    ) -> None:
        self.inputs = inputs
        self.b2c1a = b2c1a
        self.b2c0 = b2c0
        self.gray_sigma_hi = float(gray_sigma_hi)
        self._chi_cache = {} if chi_cache is None else chi_cache

    @classmethod
    def from_repo(cls, *, repo_root: Path, inputs: TensorizedInputs) -> "ArrayOwnerKernel":
        root = Path(repo_root)
        source = (
            root
            / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R1_CANONICAL_TIME_RESOLVED_GROUP_BOUNDARY_FLUX_DYNAMIC_OPACITY_AND_HEATING_MOMENT_EXTRACTION_LOCK_RERUN_V2"
            / "inputs/canonical_b2c2a_r1_src"
        )
        b2c0 = _load_module(
            "r2b_r2a_phase_space_kernel_b2c0",
            source / "phase_space_kernel_b2c0.py",
        )
        # The B2C1A module internally loads its own source-identical B2C0 module.
        b2c1a = _load_module(
            "r2b_r2a_hi_transmission_kernel_b2c1a",
            source / "hi_transmission_kernel_b2c1a.py",
        )
        return cls(
            inputs=inputs,
            b2c1a=b2c1a,
            b2c0=b2c0,
            gray_sigma_hi=float(b2c1a.gray_sigma_hi()[0]),
        )

    def permuted(self, permutation: np.ndarray) -> "ArrayOwnerKernel":
        perm = np.asarray(permutation, dtype=np.int64)
        n = self.inputs.state0.node_count
        if perm.shape != (n,) or not np.array_equal(np.sort(perm), np.arange(n)):
            raise ValueError("permutation must contain every node exactly once")

        def frozen(a: np.ndarray) -> np.ndarray:
            out = np.ascontiguousarray(a[perm])
            out.setflags(write=False)
            return out

        new_inputs = replace(
            self.inputs,
            state0=ArrayState(
                np.ascontiguousarray(self.inputs.state0.values[:, perm]),
                np.ascontiguousarray(self.inputs.state0.temperature_K[perm]),
            ),
            node_weight=frozen(self.inputs.node_weight),
            delta_total=frozen(self.inputs.delta_total),
            macro_index=frozen(self.inputs.macro_index),
            comoving_volume_cm3=frozen(self.inputs.comoving_volume_cm3),
        )
        return ArrayOwnerKernel(
            inputs=new_inputs,
            b2c1a=self.b2c1a,
            b2c0=self.b2c0,
            gray_sigma_hi=self.gray_sigma_hi,
            chi_cache=self._chi_cache,
        )

    @staticmethod
    def _validate_state(state: ArrayState, expected_nodes: int) -> None:
        if state.node_count != expected_nodes:
            raise ValueError("state node count mismatch")
        if np.any(~np.isfinite(state.values)) or np.any(state.values < 0.0):
            raise ValueError("state lies outside the positive material cone")
        if np.any(~np.isfinite(state.temperature_K)) or np.any(state.temperature_K <= 0.0):
            raise ValueError("temperature lies outside the positive cone")

    def _global_raw(self, *, interval: int, node: int, state: ArrayState) -> np.ndarray:
        y = state.values
        n_h = float(np.sum(y[0] + y[1], dtype=np.float64))
        n_he = float(np.sum(y[2] + y[3] + y[4], dtype=np.float64))
        if n_h <= 0.0 or n_he <= 0.0:
            raise ValueError("material nuclei totals must be positive")
        x_hii = float(np.sum(y[1], dtype=np.float64)) / n_h
        x_hei = float(np.sum(y[2], dtype=np.float64)) / n_he
        # Preserve the locked R2B-R2 convention: HeII abundance per hydrogen.
        x_heii_per_h = float(np.sum(y[3], dtype=np.float64)) / n_h
        z = float(self.inputs.z_mid[interval, node])
        a = 1.0 / (1.0 + z)
        n_h_phys = NH0_CM3 * (1.0 + z) ** 3
        n_he_phys = YHE * n_h_phys
        raw = np.zeros((4, 4), dtype=np.float64)
        raw[0] = self.inputs.external_subgrid[interval, node]
        for gi in range(4):
            if self.inputs.owner_support[1, gi]:
                raw[1, gi] = (
                    a * n_h_phys * (1.0 - x_hii)
                    * self.inputs.sigma_cm2[0, gi] * MPC_CM
                )
            if self.inputs.owner_support[2, gi]:
                raw[2, gi] = (
                    a * n_he_phys * x_hei
                    * self.inputs.sigma_cm2[1, gi] * MPC_CM
                )
            if self.inputs.owner_support[3, gi]:
                raw[3, gi] = (
                    a * n_he_phys * x_heii_per_h
                    * self.inputs.sigma_cm2[2, gi] * MPC_CM
                )
        raw *= self.inputs.owner_support
        return raw

    def _subgrid_lane_measures(
        self, *, interval: int, node: int, state: ArrayState, group_index: int
    ) -> dict[str, np.ndarray]:
        n = state.node_count
        if group_index not in (0, 1):
            zeros = np.zeros(n, dtype=np.float64)
            return {lane: zeros.copy() for lane in LANES}
        y = state.values
        z = float(self.inputs.z_mid[interval, node])
        w = self.inputs.node_weight
        # comoving_volume_cm3 = W_i Mpc^3; convert to proper volume.
        volume = self.inputs.comoving_volume_cm3 / (1.0 + z) ** 3
        n_h_total_count = y[0] + y[1]
        n_he_total_count = y[2] + y[3] + y[4]
        n_h = np.divide(n_h_total_count, volume, out=np.zeros(n), where=volume > 0.0)
        n_hi = np.divide(y[0], volume, out=np.zeros(n), where=volume > 0.0)
        n_hii = np.divide(y[1], volume, out=np.zeros(n), where=volume > 0.0)
        n_heii = np.divide(y[3], volume, out=np.zeros(n), where=volume > 0.0)
        n_heiii = np.divide(y[4], volume, out=np.zeros(n), where=volume > 0.0)
        x_hii = np.divide(y[1], n_h_total_count, out=np.zeros(n), where=n_h_total_count > 0.0)
        x_heii = np.divide(y[3], n_he_total_count, out=np.zeros(n), where=n_he_total_count > 0.0)
        x_heiii = np.divide(y[4], n_he_total_count, out=np.zeros(n), where=n_he_total_count > 0.0)
        sigma = float(self.inputs.sigma_cm2[0, group_index])
        gamma = float(self.inputs.gamma_hi[interval, node])
        chi_key = (z, gamma)
        if chi_key not in self._chi_cache:
            self._chi_cache[chi_key] = float(
                self.b2c1a.calibrate_chi_jeans(z, gamma, self.gray_sigma_hi)["chi_J"]
            )
        length = self._chi_cache[chi_key] * self.b2c1a.jeans_length_cm(
            n_h,
            state.temperature_K,
            x_hii,
            x_heii,
            x_heiii,
        )
        tau = n_hi * sigma * length
        if np.any(~np.isfinite(tau)) or np.any(tau < 0.0):
            raise ValueError("subgrid optical depth must be finite and nonnegative")
        with np.errstate(under="ignore"):
            primary = w * n_hi * sigma * np.exp(-0.5 * tau)

        ne = n_hii + n_heii + 2.0 * n_heiii
        recombination = w * self.b2c0.alpha_b_hii(state.temperature_K) * ne * n_hii
        nss = self.b2c1a.self_shielding_density_cm3(
            state.temperature_K, gamma, self.gray_sigma_hi
        )
        attenuation = 1.0 - self.b2c1a.rahmati_gamma_ratio(n_h, nss)
        self_shielding = w * n_hi * sigma * np.maximum(attenuation, 1.0e-12)
        return {
            "LOCAL_NEUTRAL_HAZARD_PRIMARY": np.asarray(primary, dtype=np.float64),
            "RECOMBINATION_WEIGHTED_AUDITOR": np.asarray(recombination, dtype=np.float64),
            "SCRIPT_SELF_SHIELDING_AUDITOR": np.asarray(self_shielding, dtype=np.float64),
        }

    def _measure(
        self,
        *,
        interval: int,
        node: int,
        state: ArrayState,
        owner_index: int,
        group_index: int,
        lane: str,
        subgrid_cache: dict[int, dict[str, np.ndarray]],
    ) -> np.ndarray:
        n = state.node_count
        if not bool(self.inputs.owner_support[owner_index, group_index]):
            return np.zeros(n, dtype=np.float64)
        if owner_index == 0:
            if group_index not in subgrid_cache:
                subgrid_cache[group_index] = self._subgrid_lane_measures(
                    interval=interval,
                    node=node,
                    state=state,
                    group_index=group_index,
                )
            return subgrid_cache[group_index][lane]
        species_index = owner_index - 1
        state_index = (0, 2, 3)[species_index]
        return state.values[state_index] * self.inputs.sigma_cm2[species_index, group_index]

    def _global_raw_values(
        self,
        *,
        z: float,
        external_subgrid: np.ndarray,
        state: ArrayState,
    ) -> np.ndarray:
        y = state.values
        n_h = float(np.sum(y[0] + y[1], dtype=np.float64))
        n_he = float(np.sum(y[2] + y[3] + y[4], dtype=np.float64))
        if n_h <= 0.0 or n_he <= 0.0:
            raise ValueError("material nuclei totals must be positive")
        x_hii = float(np.sum(y[1], dtype=np.float64)) / n_h
        x_hei = float(np.sum(y[2], dtype=np.float64)) / n_he
        # Preserve the locked R2B-R2 convention: HeII abundance per hydrogen.
        x_heii_per_h = float(np.sum(y[3], dtype=np.float64)) / n_h
        redshift = float(z)
        a = 1.0 / (1.0 + redshift)
        n_h_phys = NH0_CM3 * (1.0 + redshift) ** 3
        n_he_phys = YHE * n_h_phys
        external = np.asarray(external_subgrid, dtype=np.float64)
        if external.shape != (4,) or np.any(~np.isfinite(external)) or np.any(external < 0.0):
            raise ValueError("external subgrid raw response must have shape [4]")
        raw = np.zeros((4, 4), dtype=np.float64)
        raw[0] = external
        for gi in range(4):
            if self.inputs.owner_support[1, gi]:
                raw[1, gi] = (
                    a * n_h_phys * (1.0 - x_hii)
                    * self.inputs.sigma_cm2[0, gi] * MPC_CM
                )
            if self.inputs.owner_support[2, gi]:
                raw[2, gi] = (
                    a * n_he_phys * x_hei
                    * self.inputs.sigma_cm2[1, gi] * MPC_CM
                )
            if self.inputs.owner_support[3, gi]:
                raw[3, gi] = (
                    a * n_he_phys * x_heii_per_h
                    * self.inputs.sigma_cm2[2, gi] * MPC_CM
                )
        raw *= self.inputs.owner_support
        return raw

    def _subgrid_measure_values(
        self,
        *,
        z: float,
        gamma_hi: float,
        state: ArrayState,
        group_index: int,
        lane: str,
    ) -> np.ndarray:
        n = state.node_count
        if group_index not in (0, 1):
            return np.zeros(n, dtype=np.float64)
        y = state.values
        redshift = float(z)
        gamma = float(gamma_hi)
        w = self.inputs.node_weight
        volume = self.inputs.comoving_volume_cm3 / (1.0 + redshift) ** 3
        n_h_total_count = y[0] + y[1]
        n_he_total_count = y[2] + y[3] + y[4]
        n_h = np.divide(n_h_total_count, volume, out=np.zeros(n), where=volume > 0.0)
        n_hi = np.divide(y[0], volume, out=np.zeros(n), where=volume > 0.0)
        n_hii = np.divide(y[1], volume, out=np.zeros(n), where=volume > 0.0)
        n_heii = np.divide(y[3], volume, out=np.zeros(n), where=volume > 0.0)
        n_heiii = np.divide(y[4], volume, out=np.zeros(n), where=volume > 0.0)
        x_hii = np.divide(y[1], n_h_total_count, out=np.zeros(n), where=n_h_total_count > 0.0)
        x_heii = np.divide(y[3], n_he_total_count, out=np.zeros(n), where=n_he_total_count > 0.0)
        x_heiii = np.divide(y[4], n_he_total_count, out=np.zeros(n), where=n_he_total_count > 0.0)
        sigma = float(self.inputs.sigma_cm2[0, group_index])
        if lane == "LOCAL_NEUTRAL_HAZARD_PRIMARY":
            chi_key = (redshift, gamma)
            if chi_key not in self._chi_cache:
                self._chi_cache[chi_key] = float(
                    self.b2c1a.calibrate_chi_jeans(redshift, gamma, self.gray_sigma_hi)["chi_J"]
                )
            length = self._chi_cache[chi_key] * self.b2c1a.jeans_length_cm(
                n_h, state.temperature_K, x_hii, x_heii, x_heiii
            )
            tau = n_hi * sigma * length
            if np.any(~np.isfinite(tau)) or np.any(tau < 0.0):
                raise ValueError("subgrid optical depth must be finite and nonnegative")
            with np.errstate(under="ignore"):
                return np.asarray(w * n_hi * sigma * np.exp(-0.5 * tau), dtype=np.float64)
        if lane == "RECOMBINATION_WEIGHTED_AUDITOR":
            ne = n_hii + n_heii + 2.0 * n_heiii
            return np.asarray(
                w * self.b2c0.alpha_b_hii(state.temperature_K) * ne * n_hii,
                dtype=np.float64,
            )
        if lane == "SCRIPT_SELF_SHIELDING_AUDITOR":
            nss = self.b2c1a.self_shielding_density_cm3(
                state.temperature_K, gamma, self.gray_sigma_hi
            )
            attenuation = 1.0 - self.b2c1a.rahmati_gamma_ratio(n_h, nss)
            return np.asarray(
                w * n_hi * sigma * np.maximum(attenuation, 1.0e-12),
                dtype=np.float64,
            )
        raise KeyError(lane)

    def evaluate_values(
        self,
        *,
        kappa_total: np.ndarray,
        current_total: np.ndarray,
        external_subgrid: np.ndarray,
        z: float,
        gamma_hi: float,
        state: ArrayState,
        lane: str,
    ) -> OwnerEvaluation:
        if lane not in LANES:
            raise KeyError(f"unknown predeclared lane {lane!r}")
        self._validate_state(state, self.inputs.state0.node_count)
        kappa_values = np.asarray(kappa_total, dtype=np.float64)
        current_values = np.asarray(current_total, dtype=np.float64)
        if kappa_values.shape != (4,) or current_values.shape != (4,):
            raise ValueError("authoritative forcing totals must have shape [4]")
        raw = self._global_raw_values(
            z=float(z), external_subgrid=np.asarray(external_subgrid), state=state
        )
        owner_kappa = np.zeros((4, 4), dtype=np.float64)
        owner_current = np.zeros((4, 4), dtype=np.float64)
        owner_fraction = np.zeros((4, 4), dtype=np.float64)
        node_fraction = np.zeros((4, 4, state.node_count), dtype=np.float64)
        node_current = np.zeros_like(node_fraction)
        max_kappa = max_current = max_node = 0.0
        subgrid_cache: dict[int, np.ndarray] = {}
        for gi in range(4):
            conditioned = _condition(float(kappa_values[gi]), raw[:, gi])
            owner_kappa[:, gi] = conditioned
            phi = float(current_values[gi] / kappa_values[gi]) if kappa_values[gi] > 0.0 else 0.0
            owner_current[:, gi] = phi * conditioned
            if kappa_values[gi] > 0.0:
                owner_fraction[:, gi] = conditioned / kappa_values[gi]
            for oi in range(4):
                if not bool(self.inputs.owner_support[oi, gi]):
                    measure = np.zeros(state.node_count, dtype=np.float64)
                elif oi == 0:
                    if gi not in subgrid_cache:
                        subgrid_cache[gi] = self._subgrid_measure_values(
                            z=float(z), gamma_hi=float(gamma_hi), state=state,
                            group_index=gi, lane=lane,
                        )
                    measure = subgrid_cache[gi]
                else:
                    species_index = oi - 1
                    state_index = (0, 2, 3)[species_index]
                    measure = (
                        state.values[state_index]
                        * self.inputs.sigma_cm2[species_index, gi]
                    )
                q, allocated = _allocate(owner_current[oi, gi], measure)
                node_fraction[oi, gi] = q
                node_current[oi, gi] = allocated
                node_sum = float(np.sum(allocated, dtype=np.float64))
                max_node = max(
                    max_node,
                    abs(node_sum - owner_current[oi, gi])
                    / max(abs(owner_current[oi, gi]), 1.0),
                )
            ksum = float(np.sum(owner_kappa[:, gi], dtype=np.float64))
            jsum = float(np.sum(owner_current[:, gi], dtype=np.float64))
            max_kappa = max(
                max_kappa,
                abs(ksum - kappa_values[gi]) / max(abs(kappa_values[gi]), 1.0e-300),
            )
            max_current = max(
                max_current,
                abs(jsum - current_values[gi]) / max(abs(current_values[gi]), 1.0),
            )
        unsupported = ~self.inputs.owner_support.astype(bool)
        owner_kappa[unsupported] = 0.0
        owner_current[unsupported] = 0.0
        owner_fraction[unsupported] = 0.0
        node_fraction[unsupported] = 0.0
        node_current[unsupported] = 0.0
        return OwnerEvaluation(
            owner_kappa=owner_kappa,
            owner_current=owner_current,
            owner_fraction=owner_fraction,
            node_current=node_current,
            node_fraction=node_fraction,
            max_kappa_residual=max_kappa,
            max_current_residual=max_current,
            max_node_residual=max_node,
        )

    def evaluate(
        self,
        *,
        interval: int,
        node: int,
        state: ArrayState,
        lane: str,
    ) -> OwnerEvaluation:
        if not (0 <= interval < 5 and 0 <= node < 17):
            raise IndexError("forcing index out of range")
        return self.evaluate_values(
            kappa_total=self.inputs.kappa[interval, node],
            current_total=self.inputs.absorption[interval, node],
            external_subgrid=self.inputs.external_subgrid[interval, node],
            z=float(self.inputs.z_mid[interval, node]),
            gamma_hi=float(self.inputs.gamma_hi[interval, node]),
            state=state,
            lane=lane,
        )
