#!/usr/bin/env python3
"""Canonical positive material-state lifts for R1B-R2B-R1.

The initial state uses the exact CANONICAL_DIRECT_REEVOLVED z=6 history row.
For audit-only dense snapshots, the BDF forcing row supplies the instantaneous
species fractions and thermal energy.  In both cases the fixed two-scale
hierarchy is only a positive spatial shape prior.  One positive global thermal
normalization closes the canonical total internal energy; there is no per-node
fit or clipping.
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
K_B_ERG_K = 1.380649e-16
NH0_CM3 = 1.88e-7
YHE = 0.079


@dataclass(frozen=True)
class InitialMaterialState:
    frame: pd.DataFrame
    metadata: dict[str, Any]
    array_hashes: dict[str, str]


def _array_hash(values: np.ndarray) -> str:
    payload = np.ascontiguousarray(np.asarray(values, dtype="<f8")).tobytes()
    return hashlib.sha256(payload).hexdigest()


def _normalize_stage_root(path: Path) -> Path:
    p = Path(path)
    if p.exists():
        return p
    candidate = p.parent / "stages" / p.name
    if candidate.exists():
        return candidate
    raise FileNotFoundError(p)


def _load_hierarchy(r1_root: Path, r2a_root: Path) -> Any:
    source_dir = r1_root / "inputs" / "canonical_b2c2a_r1_src"
    upstream = r2a_root / "inputs" / "upstream"
    for entry in (str(upstream.resolve()), str(source_dir.resolve())):
        if entry not in sys.path:
            sys.path.insert(0, entry)
    path = upstream / "hierarchical_two_scale_closure.py"
    name = "r2b_r1_hierarchy"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _fixed_micro(hierarchy: Any, path: Path) -> Any:
    data = np.load(path)
    return hierarchy.FixedMicroTemplate(
        n_delta=int(data["n_delta"]),
        n_t=int(data["n_t"]),
        w_delta=np.asarray(data["w_delta"], dtype=float),
        w_temperature=np.asarray(data["w_temperature"], dtype=float),
        u_delta=np.asarray(data["u_delta"], dtype=float),
        u_temperature=np.asarray(data["u_temperature"], dtype=float),
        weight_lock_redshift=float(data["weight_lock_redshift"]),
    )


def _build_material_state(
    *,
    r1_root: Path,
    r2a_root: Path,
    z: float,
    x_hii: float,
    x_hei: float,
    x_heii: float,
    x_heiii: float,
    temperature_shape_K: float,
    gamma_hi_s_inv: float,
    target_u_erg_cMpc3: float,
    source_history_kind: str,
    source_metadata: Mapping[str, Any] | None = None,
) -> InitialMaterialState:
    if not (0.0 <= x_hii <= 1.0):
        raise RuntimeError("invalid hydrogen fraction")
    if min(x_hei, x_heii, x_heiii) < 0.0:
        raise RuntimeError("negative helium fraction")
    if abs(x_hei + x_heii + x_heiii - 1.0) > 5.0e-13:
        raise RuntimeError("helium simplex does not close")
    if not math.isfinite(temperature_shape_K) or temperature_shape_K <= 0.0:
        raise RuntimeError("invalid temperature")
    if not math.isfinite(target_u_erg_cMpc3) or target_u_erg_cMpc3 <= 0.0:
        raise RuntimeError("invalid target internal energy")

    hierarchy = _load_hierarchy(r1_root, r2a_root)
    hstate = hierarchy.B2C0.HistoryState(
        z=float(z),
        x_hii=float(x_hii),
        x_heii=float(x_heii),
        x_heiii=float(x_heiii),
        temperature=float(temperature_shape_K),
        gamma_hi=float(gamma_hi_s_inv),
    )
    upstream = r2a_root / "inputs" / "upstream"
    macro_template = pd.read_csv(upstream / "fixed_macro_parcel_template_z6.csv")
    mapping = pd.read_csv(upstream / "density_mapping_colossus_1_3_10_port.csv")
    macro = hierarchy.macro_measure(float(z), mapping, macro_template)
    micro = _fixed_micro(hierarchy, upstream / "fixed_micro_parcel_template_z6.npz")
    nodes, _means, diagnostics = hierarchy.construct_hierarchy(
        hstate, macro, micro, closure_variant="BASELINE"
    )
    if len(nodes) != 46080:
        raise RuntimeError(f"unexpected hierarchy size: {len(nodes)}")

    w = nodes["W_node"].to_numpy(dtype=float)
    delta = nodes["delta_total"].to_numpy(dtype=float)
    mass_measure = w * delta
    if np.any(~np.isfinite(mass_measure)) or np.any(mass_measure < 0.0):
        raise RuntimeError("non-finite or negative node mass measure")
    if abs(float(math.fsum(mass_measure)) - 1.0) > 2.0e-13:
        raise RuntimeError("node mass measure does not close")

    n_h_global = NH0_CM3 * MPC_CM**3
    n_he_global = YHE * n_h_global
    n_h_node = n_h_global * mass_measure
    n_he_node = n_he_global * mass_measure

    frame = nodes[
        [
            "macro_index",
            "micro_index",
            "parcel_label",
            "W_node",
            "W_macro",
            "w_micro",
            "delta_total",
            "T_K",
            "xHII",
            "xHeI",
            "xHeII",
            "xHeIII",
        ]
    ].copy()
    frame["N_HI"] = n_h_node * (1.0 - frame["xHII"].to_numpy(dtype=float))
    frame["N_HII"] = n_h_node * frame["xHII"].to_numpy(dtype=float)
    frame["N_HeI"] = n_he_node * frame["xHeI"].to_numpy(dtype=float)
    frame["N_HeII"] = n_he_node * frame["xHeII"].to_numpy(dtype=float)
    frame["N_HeIII"] = n_he_node * frame["xHeIII"].to_numpy(dtype=float)

    electron = (
        frame["N_HII"].to_numpy(dtype=float)
        + frame["N_HeII"].to_numpy(dtype=float)
        + 2.0 * frame["N_HeIII"].to_numpy(dtype=float)
    )
    particles = n_h_node + n_he_node + electron
    prior_temperature = frame["T_K"].to_numpy(dtype=float)
    raw_u = 1.5 * K_B_ERG_K * particles * prior_temperature
    raw_total = float(math.fsum(raw_u))
    if raw_total <= 0.0:
        raise RuntimeError("non-positive prior thermal energy")
    thermal_factor = float(target_u_erg_cMpc3) / raw_total
    if not math.isfinite(thermal_factor) or thermal_factor <= 0.0:
        raise RuntimeError("invalid thermal normalization factor")
    frame["U_resolved"] = raw_u * thermal_factor
    frame["T_K"] = prior_temperature * thermal_factor

    state_columns = [
        "N_HI",
        "N_HII",
        "N_HeI",
        "N_HeII",
        "N_HeIII",
        "U_resolved",
        "T_K",
    ]
    values = frame[state_columns].to_numpy(dtype=float)
    if np.any(~np.isfinite(values)) or np.any(values[:, :6] < 0.0) or np.any(values[:, 6] <= 0.0):
        raise RuntimeError("non-physical material state")

    hashes = {name: _array_hash(frame[name].to_numpy(dtype=float)) for name in state_columns}
    metadata: dict[str, Any] = {
        "classification": "CANONICAL_NODE_MATERIAL_STATE",
        "source_redshift": float(z),
        "source_history_kind": source_history_kind,
        "source_temperature_shape_K": float(temperature_shape_K),
        "source_gamma_HI_s-1": float(gamma_hi_s_inv),
        "node_count": int(len(frame)),
        "global_H_nuclei_cMpc-3": float(n_h_global),
        "global_He_nuclei_cMpc-3": float(n_he_global),
        "global_xHII": float(x_hii),
        "global_xHeI": float(x_hei),
        "global_xHeII": float(x_heii),
        "global_xHeIII": float(x_heiii),
        "global_U_resolved_erg_cMpc-3": float(target_u_erg_cMpc3),
        "thermal_normalization_factor": float(thermal_factor),
        "raw_prior_U_erg_cMpc-3": raw_total,
        "k_B_erg_K-1": K_B_ERG_K,
        "Mpc_cm": MPC_CM,
        "NH0_cm-3": NH0_CM3,
        "Y_He_by_number": YHE,
        "clipping_used": False,
        "per_node_fit_used": False,
        "hierarchy_weight_sum": float(diagnostics["weight_sum"]),
        "hierarchy_mass_density_sum": float(diagnostics["mass_density_sum"]),
    }
    if source_metadata:
        metadata.update(dict(source_metadata))
    return InitialMaterialState(frame=frame, metadata=metadata, array_hashes=hashes)


def build_initial_material_state(*, r1_root: Path, r2a_root: Path) -> InitialMaterialState:
    """Construct the unique locked z=6 material state under the stage policy."""
    r1_root = _normalize_stage_root(Path(r1_root))
    r2a_root = _normalize_stage_root(Path(r2a_root))
    history = pd.read_csv(
        r1_root / "data" / "bdf_replay" / "canonical_bdf_replayed_history.csv"
    )
    z6 = history[np.isclose(history["z"], 6.0, rtol=0.0, atol=0.0)]
    if len(z6) != 1:
        raise RuntimeError(f"expected exactly one canonical z=6 row, found {len(z6)}")
    row = z6.iloc[0]
    if str(row["history_provenance"]) != "CANONICAL_DIRECT_REEVOLVED":
        raise RuntimeError("z=6 source is not CANONICAL_DIRECT_REEVOLVED")

    x_hii = float(row["xHII"])
    x_heii = float(row["xHeII"])
    x_heiii = float(row["xHeIII"])
    x_hei = 1.0 - x_heii - x_heiii
    temperature = float(row["T_K"])
    gamma_hi = float(row["Gamma_HI"])
    n_h_global = NH0_CM3 * MPC_CM**3
    n_he_global = YHE * n_h_global
    global_electrons = n_h_global * x_hii + n_he_global * (x_heii + 2.0 * x_heiii)
    global_particles = n_h_global + n_he_global + global_electrons
    target_u = 1.5 * K_B_ERG_K * global_particles * temperature

    result = _build_material_state(
        r1_root=r1_root,
        r2a_root=r2a_root,
        z=6.0,
        x_hii=x_hii,
        x_hei=x_hei,
        x_heii=x_heii,
        x_heiii=x_heiii,
        temperature_shape_K=temperature,
        gamma_hi_s_inv=gamma_hi,
        target_u_erg_cMpc3=target_u,
        source_history_kind="CANONICAL_DIRECT_REEVOLVED",
        source_metadata={"source_temperature_K": temperature},
    )
    return result


def build_material_snapshot_from_forcing_row(
    *, forcing_row: Mapping[str, Any], r1_root: Path, r2a_root: Path
) -> InitialMaterialState:
    """Audit-only node lift of one canonical BDF dense forcing row.

    This is a snapshot disintegration, not a time integration.  The global
    thermal density `u_erg_cm3` is converted to an extensive energy in one
    comoving Mpc^3 at the row's interpolated redshift.
    """
    r1_root = _normalize_stage_root(Path(r1_root))
    r2a_root = _normalize_stage_root(Path(r2a_root))
    rec = dict(forcing_row)
    fraction = float(rec["fraction"])
    z = float(rec["z_start"]) + fraction * (float(rec["z_end"]) - float(rec["z_start"]))
    target_u = float(rec["u_erg_cm3"]) * MPC_CM**3 / (1.0 + z) ** 3
    return _build_material_state(
        r1_root=r1_root,
        r2a_root=r2a_root,
        z=z,
        x_hii=float(rec["xHII"]),
        x_hei=float(rec["xHeI"]),
        x_heii=float(rec["xHeII"]),
        x_heiii=float(rec["xHeIII"]),
        temperature_shape_K=float(rec["T_K"]),
        gamma_hi_s_inv=float(rec["Gamma_HI_s-1"]),
        target_u_erg_cMpc3=target_u,
        source_history_kind="CANONICAL_BDF_DENSE_FORCING",
        source_metadata={
            "interval_index": int(rec["interval_index"]),
            "node_index": int(rec["node_index"]),
            "fraction": fraction,
            "z_mid_opacity_coordinate": float(rec["z_mid"]),
        },
    )
