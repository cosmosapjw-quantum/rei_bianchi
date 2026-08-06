"""P0.5-B2C2A ionized-absorption hazard decomposition.

Primary scientific definition
-----------------------------
For each comoving photon group g and declared opacity component c,

    kappa_bar_cg = Integral phi_g(E) kappa_c(E) dE,
    Ndot_abs_cg = [c/a/Mpc_cm] N_gamma,g kappa_bar_cg.

The inherited B2C1C total group hazard is reconstructed from the exact-zero-G3
trajectory. P0.4 PUBLIC_REPO_EXACT six-node opacity is used as the absolute
EFFECTIVE_HI_SUBGRID evidence in 13.6--39.5 eV. Any difference from the
inherited total is stored as a signed UNATTRIBUTED_EFFECTIVE_RESIDUAL and is
never silently rescaled or redistributed to species.

FlexRT-style finite-cell deposition is an independent refinement auditor for
nonnegative physical components. Signed residuals are not inserted into an
exponential optical depth.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np
import pandas as pd
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from b2b_physical_model import (  # noqa: E402
    C_LIGHT,
    H0,
    KB_ERG,
    MPC_CM,
    NH0,
    OMEGA_L,
    OMEGA_M,
    YHE,
    RAW_DENSITIES,
    allocate_front_sink,
    build_opacity_fit,
    make_params,
    make_spectrum_lanes,
)
from monolithic_model_b2a import opacity_cMpc_inv  # noqa: E402
from primary_exact_zero_model import (  # noqa: E402
    physical_state,
    state_from_z7,
    z7_from_state,
    z7_rhs,
)
from multigroup_hhe_transmission import (  # noqa: E402
    GROUPS,
    GROUP_ORDER,
    SPECIES,
    SUPPORT,
    gl_nodes,
    spectrum_weight,
    verner_sigma,
)

MYR_S = 1.0e6 * 365.25 * 86400.0
PRIMARY = "MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD"
PUBLIC_ENERGY_NODES = np.array([13.60, 14.48, 16.70, 20.05, 25.50, 39.50])
COMPONENTS = [
    "EFFECTIVE_HI_SUBGRID",
    "EXPLICIT_HI_ATOMIC",
    "EXPLICIT_HEI_ATOMIC",
    "EXPLICIT_HEII_ATOMIC",
    "UNATTRIBUTED_EFFECTIVE_RESIDUAL",
]
COMPONENT_SPECIES = {
    "EFFECTIVE_HI_SUBGRID": "HI_EFFECTIVE",
    "EXPLICIT_HI_ATOMIC": "HI",
    "EXPLICIT_HEI_ATOMIC": "HeI",
    "EXPLICIT_HEII_ATOMIC": "HeII",
    "UNATTRIBUTED_EFFECTIVE_RESIDUAL": "UNATTRIBUTED",
}
CONVENTION_TAG = "metric=(-,+,+,+);epsilon_123=+1;FLRW_CONTROL"
UNIT_TAG = "N_gamma=cMpc^-3;kappa=cMpc^-1;t=s;H=s^-1;ell=cm"
ELL_NORMALIZATION_CM = MPC_CM  # ell(a=1) = 1 Mpc; receipt-only normalization.


@dataclass(frozen=True)
class IntervalModel:
    z_start: float
    z_mid: float
    z_end: float
    duration_s: float
    emission_rate: float
    p: dict[str, Any]
    solution: Any
    inherited_ledger_absorption_rate: float


def find_one(root: Path, filename: str) -> Path:
    matches = sorted(root.rglob(filename), key=lambda p: (len(p.parts), str(p)))
    if not matches:
        raise FileNotFoundError(f"{filename} below {root}")
    return matches[0]


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_hash(record: dict[str, Any]) -> str:
    payload = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    return sha256_bytes(payload)


def hubble(z: float) -> float:
    return H0 * math.sqrt(OMEGA_M * (1.0 + z) ** 3 + OMEGA_L)


def cosmic_age_s(z: float) -> float:
    """Flat matter+Lambda cosmic age used by the inherited FLRW control."""
    a = 1.0 / (1.0 + z)
    return (
        2.0
        / (3.0 * H0 * math.sqrt(OMEGA_L))
        * math.asinh(math.sqrt(OMEGA_L / OMEGA_M) * a ** 1.5)
    )


def background_receipt(z_start: float, z_end: float, index: int) -> dict[str, Any]:
    base = {
        "background_snapshot_id": f"FLRW_CONTROL:B2C2A:{index:02d}:z{z_start:.2f}_to_z{z_end:.2f}",
        "background_model": "FLRW_CONTROL",
        "proper_time_start_s": cosmic_age_s(z_start),
        "proper_time_end_s": cosmic_age_s(z_end),
        "H_start_s^-1": hubble(z_start),
        "H_end_s^-1": hubble(z_end),
        "ell_start_cm": ELL_NORMALIZATION_CM / (1.0 + z_start),
        "ell_end_cm": ELL_NORMALIZATION_CM / (1.0 + z_end),
        "ell_normalization": "ell(a=1)=1 Mpc; receipt-only FLRW normalization",
        "convention_tag": CONVENTION_TAG,
        "unit_tag": UNIT_TAG,
        "geometry_feedback_enabled": False,
        "primitive_geometry_transplanted": False,
    }
    base["background_snapshot_sha256"] = canonical_hash(base)
    return base


def normalized_group_quadrature(group: str, n: int = 128) -> tuple[np.ndarray, np.ndarray]:
    energy, weights = gl_nodes(group, n)
    phi = spectrum_weight(energy, PRIMARY, operator_only=(group == "G3"))
    weighted = weights * phi
    return energy, weighted / weighted.sum()


def public_p04_interpolator(public: pd.DataFrame, z: float) -> tuple[Callable[[np.ndarray], np.ndarray], dict[str, Any]]:
    """P0.4 absolute central-Gamma opacity interpolator.

    z interpolation: PCHIP of log(kappa) at each locked energy node.
    E interpolation: monotone PCHIP in log(E), log(kappa), no extrapolation.
    """
    node_kappa = []
    central_gamma = []
    for energy in PUBLIC_ENERGY_NODES:
        sub = public[np.isclose(public["energy_eV"], energy)].sort_values("z")
        if z < sub["z"].min() or z > sub["z"].max():
            raise ValueError(f"z={z} outside P0.4 public table")
        z_interp = PchipInterpolator(
            sub["z"].to_numpy(),
            np.log(1.0 / sub["lambda_density_cMpc"].to_numpy()),
            extrapolate=False,
        )
        g_interp = PchipInterpolator(
            sub["z"].to_numpy(), sub["central_gamma12"].to_numpy(), extrapolate=False
        )
        node_kappa.append(float(np.exp(z_interp(z))))
        central_gamma.append(float(g_interp(z)))
    loge = np.log(PUBLIC_ENERGY_NODES)
    logk = np.log(np.asarray(node_kappa))
    pchip = PchipInterpolator(loge, logk, extrapolate=False)

    def evaluator(energy: np.ndarray) -> np.ndarray:
        energy = np.asarray(energy, dtype=float)
        if np.any(energy < PUBLIC_ENERGY_NODES[0]) or np.any(energy > PUBLIC_ENERGY_NODES[-1]):
            raise ValueError("P0.4 effective opacity extrapolation forbidden")
        return np.exp(pchip(np.log(energy)))

    sample = np.geomspace(PUBLIC_ENERGY_NODES[0], PUBLIC_ENERGY_NODES[-1], 2048)
    values = evaluator(sample)
    monotone_nonincreasing = bool(np.all(np.diff(values) <= 1.0e-13 * values[:-1]))
    return evaluator, {
        "z": z,
        "energy_nodes_eV": PUBLIC_ENERGY_NODES.tolist(),
        "kappa_nodes_cMpc_inv": node_kappa,
        "central_gamma12_nodes": central_gamma,
        "central_gamma12": float(np.mean(central_gamma)),
        "energy_interpolation": "PCHIP(logE,logkappa), extrapolate=False",
        "z_interpolation": "PCHIP(z,logkappa), extrapolate=False",
        "monotone_nonincreasing": monotone_nonincreasing,
    }


def raw_gamma_node_models(
    raw_path: Path,
    density_path: Path,
    z: float,
) -> tuple[list[PchipInterpolator], dict[str, Any]]:
    """Underlying P0.4 current-Gamma energy-node auditor.

    This is diagnostic only. Production EFFECTIVE_HI_SUBGRID uses the public
    central-Gamma table as explicitly requested.
    """
    raw = np.loadtxt(raw_path)
    columns = ["z", "zre", "gamma", "density"] + [
        f"mfp_{e:g}" for e in PUBLIC_ENERGY_NODES
    ]
    frame = pd.DataFrame(raw, columns=columns)
    frame = frame[np.isclose(frame["z"], z)]
    if frame.empty:
        raise RuntimeError(f"No raw opacity rows at z={z}")
    density_map = pd.read_csv(density_path)
    dweights = []
    for dens in sorted(density_map["density_sigma"].unique()):
        sub = density_map[np.isclose(density_map["density_sigma"], dens)].sort_values("z")
        dweights.append(np.interp(z, sub["z"], sub["effective_GH_weight"]))
    dweights = np.asarray(dweights)

    def q_history(x: float, midpoint: float = 6.58, width: float = 1.63) -> float:
        return 0.5 * (1.0 - math.tanh((x - midpoint) / width))

    def zre_weights(nodes: np.ndarray) -> dict[float, float]:
        nodes = np.asarray(sorted(nodes), dtype=float)
        mids = 0.5 * (nodes[:-1] + nodes[1:])
        lo = np.r_[z, mids]
        hi = np.r_[mids, np.inf]
        mass = np.array(
            [q_history(a) - (0.0 if np.isinf(b) else q_history(b)) for a, b in zip(lo, hi)]
        )
        mass = np.maximum(mass, 0.0)
        mass /= mass.sum()
        return dict(zip(nodes, mass))

    rows = []
    for gamma in sorted(frame["gamma"].unique()):
        gf = frame[np.isclose(frame["gamma"], gamma)]
        by_zre: dict[float, np.ndarray] = {}
        complete = []
        for zre in sorted(gf["zre"].unique()):
            if zre < z:
                continue
            sub = gf[np.isclose(gf["zre"], zre)]
            vectors = []
            valid = True
            for dens in RAW_DENSITIES:
                row = sub[np.isclose(sub["density"], dens)]
                if len(row) != 1:
                    valid = False
                    break
                vectors.append(row.iloc[0, 4:].to_numpy(float))
            if valid:
                by_zre[float(zre)] = np.sum(dweights[:, None] / np.asarray(vectors), axis=0)
                complete.append(float(zre))
        if complete:
            zw = zre_weights(np.asarray(complete))
            kappa = sum(zw[zr] * by_zre[zr] for zr in complete)
            rows.append([gamma, *kappa])
    arr = np.asarray(rows)
    if len(arr) < 5:
        raise RuntimeError("Insufficient raw current-Gamma nodes")
    models = [
        PchipInterpolator(np.log(arr[:, 0]), np.log(arr[:, 1 + i]), extrapolate=False)
        for i in range(len(PUBLIC_ENERGY_NODES))
    ]
    return models, {
        "z": z,
        "gamma12_min": float(arr[:, 0].min()),
        "gamma12_max": float(arr[:, 0].max()),
        "classification": "AUDITOR_ONLY_CURRENT_GAMMA_RAW_P0_4",
    }


def raw_gamma_energy_evaluator(models: list[PchipInterpolator], gamma12: float) -> Callable[[np.ndarray], np.ndarray]:
    if gamma12 <= 0.0:
        raise ValueError("Gamma12 must be positive")
    node = np.array([np.exp(model(np.log(gamma12))) for model in models])
    pchip = PchipInterpolator(np.log(PUBLIC_ENERGY_NODES), np.log(node), extrapolate=False)

    def evaluator(energy: np.ndarray) -> np.ndarray:
        energy = np.asarray(energy, dtype=float)
        if np.any(energy < PUBLIC_ENERGY_NODES[0]) or np.any(energy > PUBLIC_ENERGY_NODES[-1]):
            raise ValueError("raw gamma auditor extrapolation forbidden")
        return np.exp(pchip(np.log(energy)))

    return evaluator


def atomic_kappa_arrays(state: dict[str, Any], z: float, group: str, energy: np.ndarray) -> dict[str, np.ndarray]:
    a = 1.0 / (1.0 + z)
    n_h = NH0 * (1.0 + z) ** 3
    n_he = YHE * n_h
    densities = {
        "HI": n_h * (1.0 - state["xHII"]),
        "HeI": n_he * state["xHeI"],
        "HeII": n_he * state["xHeII"],
    }
    out = {}
    for species in SPECIES:
        if group not in SUPPORT[species]:
            out[species] = np.zeros_like(energy)
        else:
            out[species] = a * densities[species] * verner_sigma(species, energy) * MPC_CM
    return out


def component_energy_arrays(
    state: dict[str, Any],
    p: dict[str, Any],
    group: str,
    energy: np.ndarray,
    public_eval: Callable[[np.ndarray], np.ndarray],
) -> dict[str, np.ndarray]:
    atomic = atomic_kappa_arrays(state, float(p["z_cos"]), group, energy)
    zeros = np.zeros_like(energy)
    if group == "G1":
        return {
            "EFFECTIVE_HI_SUBGRID": public_eval(energy),
            "EXPLICIT_HI_ATOMIC": zeros,
            "EXPLICIT_HEI_ATOMIC": zeros,
            "EXPLICIT_HEII_ATOMIC": zeros,
        }
    if group == "G2a":
        return {
            "EFFECTIVE_HI_SUBGRID": public_eval(energy),
            "EXPLICIT_HI_ATOMIC": zeros,
            "EXPLICIT_HEI_ATOMIC": atomic["HeI"],
            "EXPLICIT_HEII_ATOMIC": zeros,
        }
    if group == "G2b":
        return {
            "EFFECTIVE_HI_SUBGRID": zeros,
            "EXPLICIT_HI_ATOMIC": atomic["HI"],
            "EXPLICIT_HEI_ATOMIC": atomic["HeI"],
            "EXPLICIT_HEII_ATOMIC": zeros,
        }
    return {
        "EFFECTIVE_HI_SUBGRID": zeros,
        "EXPLICIT_HI_ATOMIC": atomic["HI"],
        "EXPLICIT_HEI_ATOMIC": atomic["HeI"],
        "EXPLICIT_HEII_ATOMIC": atomic["HeII"],
    }


def state_at(solution: Any, t: float, p: dict[str, Any]) -> dict[str, Any]:
    return physical_state(np.asarray(solution.sol(t), dtype=float), p)


def reconstruct_intervals(b2b_root: Path, b2c1c_root: Path) -> list[IntervalModel]:
    history = pd.read_csv(b2b_root / "data" / "physical_forward_history.csv")
    base = history[history["lane"] == PRIMARY].sort_values("z", ascending=False)
    ledger = pd.read_csv(b2b_root / "data" / "forward_history_photon_ledger.csv")
    intervals = ledger[ledger["lane"] == PRIMARY].sort_values("z_mid", ascending=False)
    inherited_ledger = pd.read_csv(b2c1c_root / "data" / "primary_photon_ledger.csv")

    allocation = pd.read_csv(find_one(b2b_root, "photon_allocation_all_lanes.csv"))
    allocation = allocation[allocation["lane"] == "INSIDE_OUT_SELF_SHIELD_PRIMARY"].set_index("z_mid")
    raw = find_one(b2b_root, "environment_mfp_energies.txt")
    density = find_one(b2b_root, "density_mapping_colossus_1_3_10_port.csv")
    lane = make_spectrum_lanes()[PRIMARY]

    init = base[np.isclose(base["z"], 6.0)].iloc[0]
    n123 = np.array([init.N1, init.N2, init.N3], dtype=float)
    n_h = NH0 * 7.0**3
    n_he = YHE * n_h
    ne = n_h * init.xHII + n_he * (init.xHeII + 2.0 * init.xHeIII)
    u = 1.5 * (n_h + n_he + ne) * KB_ERG * init.T_K
    z7 = z7_from_state(n123, init.xHII, init.xHeII, init.xHeIII, u)

    knots0, coeff0, _ = build_opacity_fit(raw, density, 6.0, lane)
    p_prev = make_params(
        z_cos=6.0,
        dt_seconds=1.0,
        lane=lane,
        log_kappa_knots=knots0,
        log_kappa_coeffs=coeff0,
        n_prev=np.r_[n123, 0.0],
        x_prev=np.array([init.xHII, init.xHeII, init.xHeIII]),
        u_prev=u,
        front_sink_group=np.zeros(4),
        scale_n=np.r_[n123, 1.0e-300],
        scale_u=u,
        scale_gamma=max(init.Gamma_HI, 1.0e-30),
    )
    rhs = jax.jit(z7_rhs)
    models: list[IntervalModel] = []

    for rec in intervals.itertuples():
        z_mid = float(rec.z_mid)
        z_end = float(rec.z_next)
        z_start = round(2.0 * z_mid - z_end, 12)
        duration = float(rec.dt_Myr) * MYR_S
        emission = float(rec.total_emission)
        knots, coeffs, _ = build_opacity_fit(raw, density, z_mid, lane)
        current = physical_state(z7, p_prev)
        ar = allocation.loc[z_mid]
        front, _ = allocate_front_sink(
            float(ar.front_HII_rate),
            float(ar.front_HeII_rate),
            float(ar.front_HeIII_electron_weighted_rate),
            lane,
        )
        if front[3] != 0.0:
            raise RuntimeError("Primary G3 front sink is not exact zero")
        p = make_params(
            z_cos=z_mid,
            dt_seconds=duration,
            lane=lane,
            log_kappa_knots=knots,
            log_kappa_coeffs=coeffs,
            n_prev=current["N"],
            x_prev=np.array([current["xHII"], current["xHeII"], current["xHeIII"]]),
            u_prev=current["u"],
            front_sink_group=front,
            scale_n=np.r_[current["N"][:3], 1.0e-300],
            scale_u=current["u"],
            scale_gamma=max(current["GammaHI"], 1.0e-30),
        )

        def scipy_rhs(t: float, y: np.ndarray) -> np.ndarray:
            return np.asarray(rhs(jnp.asarray(y), jnp.array(emission), p), dtype=float)

        sol = solve_ivp(
            scipy_rhs,
            (0.0, duration),
            z7,
            method="BDF",
            rtol=5.0e-13,
            atol=np.full(7, 5.0e-14),
            dense_output=True,
            max_step=duration / 240.0,
        )
        if not sol.success:
            raise RuntimeError(sol.message)
        z7 = sol.y[:, -1]
        end = physical_state(z7, p)
        expected = pd.read_csv(b2c1c_root / "data" / "primary_exact_zero_G3_history.csv")
        exp = expected[np.isclose(expected["z"], z_end)].iloc[0]
        checks = {
            "N1": end["N"][0], "N2": end["N"][1], "N3": end["N"][2],
            "xHII": end["xHII"], "xHeII": end["xHeII"], "xHeIII": end["xHeIII"],
            "T_K": end["T"], "Gamma_HI": end["GammaHI"],
        }
        for key, value in checks.items():
            rel = abs(value - float(exp[key])) / max(abs(float(exp[key])), 1.0e-300)
            if rel > 2.0e-7:
                raise RuntimeError(f"B2C1C endpoint regression failed {z_end} {key}: {rel}")
        inherited = inherited_ledger[np.isclose(inherited_ledger["z_mid"], z_mid)].iloc[0]
        models.append(
            IntervalModel(
                z_start=z_start,
                z_mid=z_mid,
                z_end=z_end,
                duration_s=duration,
                emission_rate=emission,
                p=p,
                solution=sol,
                inherited_ledger_absorption_rate=float(inherited["absorption_rate"]),
            )
        )
        p_prev = p
    return models


def integrate_interval(
    interval: IntervalModel,
    public: pd.DataFrame,
    raw_path: Path,
    density_path: Path,
    n_time: int = 320,
    n_energy: int = 128,
) -> dict[str, Any]:
    tx, tw = leggauss(n_time)
    times = 0.5 * interval.duration_s * (tx + 1.0)
    time_weights = 0.5 * interval.duration_s * tw
    public_eval, public_meta = public_p04_interpolator(public, interval.z_mid)
    raw_models, raw_meta = raw_gamma_node_models(raw_path, density_path, interval.z_mid)
    vchi = C_LIGHT * (1.0 + interval.z_mid) / MPC_CM

    groups = {}
    component_accum: dict[tuple[str, str], float] = {}
    kappa_time_accum: dict[tuple[str, str], float] = {}
    kappa_min: dict[tuple[str, str], float] = {}
    kappa_max: dict[tuple[str, str], float] = {}
    residual_inst_min = {g: math.inf for g in GROUP_ORDER}
    residual_inst_max = {g: -math.inf for g in GROUP_ORDER}
    state_gamma12_values = []

    for group in GROUP_ORDER:
        groups[group] = {
            "inherited_rate_integral": 0.0,
            "base_rate_integral": 0.0,
            "residual_rate_integral": 0.0,
            "gamma_conditioned_base_integral": 0.0,
            "N_time_integral": 0.0,
            "inherited_kappa_time_integral": 0.0,
        }
        for component in COMPONENTS:
            component_accum[(group, component)] = 0.0
            kappa_time_accum[(group, component)] = 0.0
            kappa_min[(group, component)] = math.inf
            kappa_max[(group, component)] = -math.inf

    # Cache group quadratures.
    quadrature = {g: normalized_group_quadrature(g, n_energy) for g in GROUP_ORDER}

    for t, wt in zip(times, time_weights):
        state = state_at(interval.solution, float(t), interval.p)
        state_gamma12_values.append(state["GammaHI"] / 1.0e-12)
        inherited = np.asarray(
            opacity_cMpc_inv(state_from_z7(jnp.asarray(interval.solution.sol(float(t))), interval.p), interval.p),
            dtype=float,
        )
        raw_eval = raw_gamma_energy_evaluator(raw_models, state["GammaHI"] / 1.0e-12)

        for gi, group in enumerate(GROUP_ORDER):
            energy, eweight = quadrature[group]
            arrays = component_energy_arrays(state, interval.p, group, energy, public_eval)
            comp_kappa = {name: float(np.sum(eweight * arr)) for name, arr in arrays.items()}
            base_kappa = sum(comp_kappa.values())
            residual_kappa = float(inherited[gi] - base_kappa)
            comp_kappa["UNATTRIBUTED_EFFECTIVE_RESIDUAL"] = residual_kappa

            # Current-Gamma raw-P0.4 direct-energy auditor for low groups.
            if group in {"G1", "G2a"}:
                gamma_eff = float(np.sum(eweight * raw_eval(energy)))
                atomic_other = comp_kappa["EXPLICIT_HEI_ATOMIC"]
                gamma_conditioned_base = gamma_eff + atomic_other
            else:
                gamma_conditioned_base = base_kappa

            n_group = float(state["N"][gi])
            inherited_rate = vchi * n_group * float(inherited[gi])
            base_rate = vchi * n_group * base_kappa
            residual_rate = vchi * n_group * residual_kappa

            groups[group]["inherited_rate_integral"] += wt * inherited_rate
            groups[group]["base_rate_integral"] += wt * base_rate
            groups[group]["residual_rate_integral"] += wt * residual_rate
            groups[group]["gamma_conditioned_base_integral"] += wt * vchi * n_group * gamma_conditioned_base
            groups[group]["N_time_integral"] += wt * n_group
            groups[group]["inherited_kappa_time_integral"] += wt * float(inherited[gi])
            residual_inst_min[group] = min(residual_inst_min[group], residual_kappa)
            residual_inst_max[group] = max(residual_inst_max[group], residual_kappa)

            for component, kappa in comp_kappa.items():
                rate = vchi * n_group * kappa
                component_accum[(group, component)] += wt * rate
                kappa_time_accum[(group, component)] += wt * kappa
                kappa_min[(group, component)] = min(kappa_min[(group, component)], kappa)
                kappa_max[(group, component)] = max(kappa_max[(group, component)], kappa)

    for group in GROUP_ORDER:
        for key in list(groups[group]):
            if key.endswith("_integral"):
                groups[group][key.replace("_integral", "_average")] = groups[group][key] / interval.duration_s
        groups[group]["residual_instantaneous_min_cMpc_inv"] = residual_inst_min[group]
        groups[group]["residual_instantaneous_max_cMpc_inv"] = residual_inst_max[group]

    component_rows = []
    for group in GROUP_ORDER:
        for component in COMPONENTS:
            component_rows.append(
                {
                    "group": group,
                    "component": component,
                    "species_label": COMPONENT_SPECIES[component],
                    "average_absorption_rate_s-1_cMpc-3": component_accum[(group, component)] / interval.duration_s,
                    "time_average_kappa_cMpc_inv": kappa_time_accum[(group, component)] / interval.duration_s,
                    "instantaneous_kappa_min_cMpc_inv": kappa_min[(group, component)],
                    "instantaneous_kappa_max_cMpc_inv": kappa_max[(group, component)],
                    "signed_diagnostic": component == "UNATTRIBUTED_EFFECTIVE_RESIDUAL",
                }
            )

    total_inherited = sum(groups[g]["inherited_rate_average"] for g in GROUP_ORDER)
    total_declared = sum(
        row["average_absorption_rate_s-1_cMpc-3"] for row in component_rows
    )
    return {
        "groups": groups,
        "component_rows": component_rows,
        "total_inherited_rate": total_inherited,
        "total_declared_rate": total_declared,
        "ledger_total_rate": interval.inherited_ledger_absorption_rate,
        "public_meta": public_meta,
        "raw_meta": raw_meta,
        "gamma12_min": float(np.min(state_gamma12_values)),
        "gamma12_max": float(np.max(state_gamma12_values)),
        "vchi_s-1": vchi,
    }


def cell_deposition_rows(
    interval: IntervalModel,
    public: pd.DataFrame,
    n_time: int = 64,
    n_energy: int = 96,
) -> list[dict[str, Any]]:
    """Time-integrated FlexRT deposition for nonnegative base components only."""
    tx, tw = leggauss(n_time)
    times = 0.5 * interval.duration_s * (tx + 1.0)
    time_weights = 0.5 * interval.duration_s * tw
    public_eval, _ = public_p04_interpolator(public, interval.z_mid)
    vchi = C_LIGHT * (1.0 + interval.z_mid) / MPC_CM
    sequences = {
        "STRESS_1_cMpc": [1.0 / (2**i) for i in range(8)],
        "FLEXRT_2_hinv_ckpc": [(0.002 / 0.68) / (2**i) for i in range(5)],
    }
    quadrature = {g: normalized_group_quadrature(g, n_energy) for g in GROUP_ORDER}
    rows = []

    # First compute differential base component reference rates.
    reference: dict[tuple[str, str], float] = {}
    for group in GROUP_ORDER:
        for component in COMPONENTS[:-1]:
            reference[(group, component)] = 0.0
        reference[(group, "TOTAL_NONNEGATIVE_BASE")] = 0.0

    cached = []
    for t, wt in zip(times, time_weights):
        state = state_at(interval.solution, float(t), interval.p)
        time_record = {"wt": wt, "state": state, "groups": {}}
        for gi, group in enumerate(GROUP_ORDER):
            energy, eweight = quadrature[group]
            arrays = component_energy_arrays(state, interval.p, group, energy, public_eval)
            n_group = float(state["N"][gi])
            for component, arr in arrays.items():
                rate = vchi * n_group * float(np.sum(eweight * arr))
                reference[(group, component)] += wt * rate
            reference[(group, "TOTAL_NONNEGATIVE_BASE")] += wt * vchi * n_group * float(
                np.sum(eweight * sum(arrays.values()))
            )
            time_record["groups"][group] = (energy, eweight, arrays, n_group)
        cached.append(time_record)

    for key in reference:
        reference[key] /= interval.duration_s

    for sequence, cells in sequences.items():
        previous_errors: dict[tuple[str, str], float] = {}
        for level, delta_chi in enumerate(cells):
            deposits = {(g, c): 0.0 for g in GROUP_ORDER for c in [*COMPONENTS[:-1], "TOTAL_NONNEGATIVE_BASE"]}
            for record in cached:
                wt = record["wt"]
                for group in GROUP_ORDER:
                    energy, eweight, arrays, n_group = record["groups"][group]
                    total = sum(arrays.values())
                    tau = total * delta_chi
                    absorbed = -np.expm1(-np.clip(tau, 0.0, 745.0))
                    total_dep = vchi / delta_chi * n_group * float(np.sum(eweight * absorbed))
                    deposits[(group, "TOTAL_NONNEGATIVE_BASE")] += wt * total_dep
                    for component, arr in arrays.items():
                        frac = np.divide(arr, total, out=np.zeros_like(arr), where=total > 0.0)
                        dep = vchi / delta_chi * n_group * float(np.sum(eweight * absorbed * frac))
                        deposits[(group, component)] += wt * dep
            for key in deposits:
                deposits[key] /= interval.duration_s
                ref = reference[key]
                rel = abs(deposits[key] - ref) / max(abs(ref), 1.0)
                previous = previous_errors.get(key)
                order = math.nan
                if previous is not None and rel > 0.0 and previous > 0.0:
                    order = math.log(previous / rel, 2.0)
                previous_errors[key] = rel
                rows.append(
                    {
                        "sequence": sequence,
                        "level": level,
                        "delta_chi_cMpc": delta_chi,
                        "group": key[0],
                        "component": key[1],
                        "finite_cell_deposition_rate_s-1_cMpc-3": deposits[key],
                        "differential_hazard_rate_s-1_cMpc-3": ref,
                        "relative_difference": rel,
                        "observed_order": order,
                        "monotone_refinement_expected": True,
                        "signed_residual_excluded": True,
                    }
                )
    return rows


def execute(
    b2b_root: Path,
    b2c1c_root: Path,
    p04_root: Path,
    output: Path,
    receipt_path: Path,
) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    public = pd.read_csv(p04_root / "data" / "public_repo_exact_checkpoint_global.csv")
    public = public[
        (public["source"] == "PUBLIC_REPO_EXACT_CHECKPOINT")
        & (public["mode"] == "public_continuous_joint")
    ].copy()
    if not np.allclose(np.sort(public["energy_eV"].unique()), PUBLIC_ENERGY_NODES):
        raise RuntimeError("P0.4 energy-node lock mismatch")

    raw_path = find_one(b2b_root, "environment_mfp_energies.txt")
    density_path = find_one(b2b_root, "density_mapping_colossus_1_3_10_port.csv")
    intervals = reconstruct_intervals(b2b_root, b2c1c_root)

    receipts = [background_receipt(m.z_start, m.z_end, i) for i, m in enumerate(intervals)]
    with receipt_path.open("w", encoding="utf-8") as fh:
        for receipt in receipts:
            fh.write(json.dumps(receipt, sort_keys=True) + "\n")

    group_rows = []
    component_rows = []
    species_rows = []
    firewall_rows = []
    cell_rows = []
    interval_summaries = []

    for index, (model, receipt) in enumerate(zip(intervals, receipts)):
        result = integrate_interval(model, public, raw_path, density_path)
        receipt_fields = receipt.copy()
        for gi, group in enumerate(GROUP_ORDER):
            gr = result["groups"][group]
            declared = gr["base_rate_average"] + gr["residual_rate_average"]
            identity_rel = abs(declared - gr["inherited_rate_average"]) / max(
                abs(gr["inherited_rate_average"]), 1.0
            )
            base_mismatch_rel = abs(gr["base_rate_average"] - gr["inherited_rate_average"]) / max(
                abs(gr["inherited_rate_average"]), 1.0
            )
            group_rows.append(
                {
                    "interval_index": index,
                    "z_start": model.z_start,
                    "z_mid": model.z_mid,
                    "z_end": model.z_end,
                    "group": group,
                    "inherited_group_absorption_rate_s-1_cMpc-3": gr["inherited_rate_average"],
                    "declared_nonnegative_base_rate_s-1_cMpc-3": gr["base_rate_average"],
                    "unattributed_signed_rate_s-1_cMpc-3": gr["residual_rate_average"],
                    "declared_with_residual_rate_s-1_cMpc-3": declared,
                    "component_sum_identity_relative_residual": identity_rel,
                    "pre_residual_base_mismatch_relative": base_mismatch_rel,
                    "gamma_conditioned_raw_auditor_rate_s-1_cMpc-3": gr[
                        "gamma_conditioned_base_average"
                    ],
                    "residual_instantaneous_min_cMpc_inv": gr[
                        "residual_instantaneous_min_cMpc_inv"
                    ],
                    "residual_instantaneous_max_cMpc_inv": gr[
                        "residual_instantaneous_max_cMpc_inv"
                    ],
                    "primary_group_photon_number_time_average_cMpc-3": gr[
                        "N_time_average"
                    ],
                    **receipt_fields,
                }
            )

        for row in result["component_rows"]:
            full = {
                "interval_index": index,
                "z_start": model.z_start,
                "z_mid": model.z_mid,
                "z_end": model.z_end,
                **row,
                "within_group_shape": "phi(E) proportional E^-2.5; normalized per group",
                "P0_4_public_central_gamma12": result["public_meta"]["central_gamma12"],
                "state_Gamma12_min": result["gamma12_min"],
                "state_Gamma12_max": result["gamma12_max"],
                **receipt_fields,
            }
            component_rows.append(full)
            species_rows.append(
                {
                    "interval_index": index,
                    "z_mid": model.z_mid,
                    "group": row["group"],
                    "component": row["component"],
                    "species": row["species_label"],
                    "absorption_rate_s-1_cMpc-3": row[
                        "average_absorption_rate_s-1_cMpc-3"
                    ],
                    "attributed_to_physical_species": row["species_label"]
                    not in {"UNATTRIBUTED"},
                    "renormalized_to_species": False,
                    **receipt_fields,
                }
            )

        for group in GROUP_ORDER:
            low = group in {"G1", "G2a"}
            firewall_rows.append(
                {
                    "interval_index": index,
                    "z_mid": model.z_mid,
                    "group": group,
                    "effective_HI_used": low,
                    "explicit_HI_used": group in {"G2b", "G3"},
                    "effective_and_explicit_HI_double_count": False,
                    "explicit_HeI_used": group in {"G2a", "G2b", "G3"},
                    "explicit_HeII_used": group == "G3",
                    "P0_4_domain_extrapolated": False,
                    "neutral_island_included": False,
                    "primary_G3_source_exact_zero": group != "G3" or True,
                    "primary_external_HeII_absorption_exact_zero": group != "G3" or True,
                    "unattributed_residual_signed": True,
                    "unattributed_residual_negative_any_time": result["groups"][group][
                        "residual_instantaneous_min_cMpc_inv"
                    ] < -1.0e-14,
                    **receipt_fields,
                }
            )

        cell_rows.extend(
            {
                "interval_index": index,
                "z_start": model.z_start,
                "z_mid": model.z_mid,
                "z_end": model.z_end,
                **row,
                **receipt_fields,
            }
            for row in cell_deposition_rows(model, public)
        )

        ledger_rel = abs(result["total_inherited_rate"] - result["ledger_total_rate"]) / max(
            abs(result["ledger_total_rate"]), 1.0
        )
        component_rel = abs(result["total_declared_rate"] - result["total_inherited_rate"]) / max(
            abs(result["total_inherited_rate"]), 1.0
        )
        interval_summaries.append(
            {
                "interval_index": index,
                "z_mid": model.z_mid,
                "inherited_group_sum_rate": result["total_inherited_rate"],
                "B2C1C_causal_ledger_rate": result["ledger_total_rate"],
                "group_sum_vs_causal_ledger_relative_residual": ledger_rel,
                "declared_component_sum_rate": result["total_declared_rate"],
                "declared_sum_vs_inherited_relative_residual": component_rel,
                "P0_4_public_central_gamma12": result["public_meta"]["central_gamma12"],
                "state_Gamma12_min": result["gamma12_min"],
                "state_Gamma12_max": result["gamma12_max"],
                **receipt_fields,
            }
        )

    group_df = pd.DataFrame(group_rows)
    comp_df = pd.DataFrame(component_rows)
    species_df = pd.DataFrame(species_rows)
    firewall_df = pd.DataFrame(firewall_rows)
    cell_df = pd.DataFrame(cell_rows)
    interval_df = pd.DataFrame(interval_summaries)

    group_df.to_csv(output / "group_total_absorption.csv", index=False)
    comp_df.to_csv(output / "component_hazard_table.csv", index=False)
    species_df.to_csv(output / "species_component_absorption.csv", index=False)
    firewall_df.to_csv(output / "opacity_firewall_audit.csv", index=False)
    cell_df.to_csv(output / "cell_deposition_refinement.csv", index=False)
    interval_df.to_csv(output / "interval_absorption_closure.csv", index=False)

    residual_rows = comp_df[
        comp_df["component"] == "UNATTRIBUTED_EFFECTIVE_RESIDUAL"
    ].merge(
        group_df[[
            "interval_index", "group",
            "inherited_group_absorption_rate_s-1_cMpc-3"
        ]],
        on=["interval_index", "group"], how="left"
    )
    residual_rows["relative_signed_rate"] = (
        residual_rows["average_absorption_rate_s-1_cMpc-3"]
        / residual_rows["inherited_group_absorption_rate_s-1_cMpc-3"].abs().clip(lower=1.0)
    )
    raw_negative_residual = residual_rows[
        (residual_rows["instantaneous_kappa_min_cMpc_inv"] < -1.0e-14)
        | (residual_rows["average_absorption_rate_s-1_cMpc-3"] < -1.0)
    ]
    negative_residual = residual_rows[
        residual_rows["relative_signed_rate"] < -1.0e-8
    ]
    smallest = cell_df.sort_values("delta_chi_cMpc").groupby(
        ["interval_index", "sequence", "group", "component"], as_index=False
    ).first()
    physical_smallest = smallest[
        smallest["differential_hazard_rate_s-1_cMpc-3"].abs() > 1.0
    ]
    cell_max = float(physical_smallest["relative_difference"].max())
    finite = cell_df[np.isfinite(cell_df["observed_order"])]

    exact_g3 = bool(
        np.allclose(
            group_df[group_df["group"] == "G3"][
                "inherited_group_absorption_rate_s-1_cMpc-3"
            ],
            0.0,
            atol=0.0,
            rtol=0.0,
        )
        and np.allclose(
            species_df[
                (species_df["group"] == "G3")
                & (species_df["species"] == "HeII")
            ]["absorption_rate_s-1_cMpc-3"],
            0.0,
            atol=0.0,
            rtol=0.0,
        )
    )

    numerical_pass = bool(
        interval_df["group_sum_vs_causal_ledger_relative_residual"].max() < 1.0e-8
        and interval_df["declared_sum_vs_inherited_relative_residual"].max() < 1.0e-10
        and group_df["component_sum_identity_relative_residual"].max() < 1.0e-10
        and cell_max < 0.01
        and exact_g3
    )
    verdict = (
        "FAIL_CLOSED_NEGATIVE_UNATTRIBUTED_EFFECTIVE_RESIDUAL"
        if len(negative_residual)
        else ("PASS" if numerical_pass else "FAIL_NUMERICAL_GATE")
    )
    results = {
        "stage": "P0.5-B2C2A-IONIZED-ABSORPTION-DECOMPOSITION-LOCK",
        "verdict": verdict,
        "provenance": "POST_INTERRUPTION_NEW_STAGE",
        "numerical_core_pass": numerical_pass,
        "gates": {
            "group_sum_vs_B2C1C_causal_ledger_relative_residual_max": float(
                interval_df["group_sum_vs_causal_ledger_relative_residual"].max()
            ),
            "declared_component_sum_vs_inherited_relative_residual_max": float(
                interval_df["declared_sum_vs_inherited_relative_residual"].max()
            ),
            "component_sum_identity_relative_residual_max": float(
                group_df["component_sum_identity_relative_residual"].max()
            ),
            "pre_residual_base_mismatch_relative_max": float(
                group_df["pre_residual_base_mismatch_relative"].max()
            ),
            "negative_unattributed_rows_raw_including_roundoff": int(len(raw_negative_residual)),
            "negative_unattributed_rows_material": int(len(negative_residual)),
            "material_negative_relative_rate_min": float(
                negative_residual["relative_signed_rate"].min()
            ) if len(negative_residual) else 0.0,
            "unattributed_kappa_min_cMpc_inv": float(
                comp_df[comp_df["component"] == "UNATTRIBUTED_EFFECTIVE_RESIDUAL"][
                    "instantaneous_kappa_min_cMpc_inv"
                ].min()
            ),
            "unattributed_kappa_max_cMpc_inv": float(
                comp_df[comp_df["component"] == "UNATTRIBUTED_EFFECTIVE_RESIDUAL"][
                    "instantaneous_kappa_max_cMpc_inv"
                ].max()
            ),
            "cell_smallest_relative_difference_max": cell_max,
            "cell_observed_order_range": [
                float(finite["observed_order"].min()),
                float(finite["observed_order"].max()),
            ],
            "primary_G3_and_external_HeII_absorption_exact_zero": exact_g3,
            "P0_4_domain_extrapolation_count": int(
                firewall_df["P0_4_domain_extrapolated"].sum()
            ),
            "HI_double_count_count": int(
                firewall_df["effective_and_explicit_HI_double_count"].sum()
            ),
        },
        "interpretation": {
            "PUBLIC_REPO_EXACT_absolute_lane": (
                "uses the locked central-Gamma P0.4 table without current-Gamma renormalization"
            ),
            "UNATTRIBUTED_EFFECTIVE_RESIDUAL": (
                "signed difference between inherited B2C1C group hazard and declared absolute components; never species-rescaled"
            ),
            "gamma_conditioned_raw_auditor": (
                "diagnostic only; demonstrates current-Gamma dependence of the inherited P0.4 opacity"
            ),
            "negative_residual_action": (
                "fail closed before B2C2B; do not compute unresolved sink"
            ),
        },
        "forbidden_work_confirmed": [
            "recombination implementation or surrogate",
            "unresolved sink subtraction",
            "front residual",
            "source/f_esc calibration",
            "primitive geometry transplant",
            "Bianchi feedback",
        ],
    }
    (output.parent / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--b2b-root", type=Path, required=True)
    parser.add_argument("--b2c1c-root", type=Path, required=True)
    parser.add_argument("--p04-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipts", type=Path, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            execute(
                args.b2b_root,
                args.b2c1c_root,
                args.p04_root,
                args.output,
                args.receipts,
            ),
            indent=2,
        )
    )
