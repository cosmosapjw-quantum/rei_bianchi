"""Gamma-conditioned direct-opacity reconciliation for B2C2A-R1.

This stage preserves the inherited B2C2A fail-closed verdict and rebuilds the
opacity operator from:

  absolute normalization = PUBLIC_REPO_EXACT at central Gamma
  dimensionless response = raw P0.4 kappa(Gamma)/kappa(Gamma_central)

Two group closures are kept in parallel:

  DIRECT_ENERGY_GROUP        -- canonical candidate
  LEGACY_DISCRETE_NODE_GROUP -- byte/formula auditor

If their difference is material, the exact-zero-G3 history is re-evolved from
z=6. Numerical/operator residuals are never interpreted as physical
unresolved sinks.
"""

from __future__ import annotations

import argparse
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

from absorption_decomposition import (
    C_LIGHT,
    COMPONENTS,
    GROUP_ORDER,
    MPC_CM,
    MYR_S,
    NH0,
    PRIMARY,
    PUBLIC_ENERGY_NODES,
    YHE,
    atomic_kappa_arrays,
    background_receipt,
    component_energy_arrays,
    normalized_group_quadrature,
    public_p04_interpolator,
    raw_gamma_node_models,
    reconstruct_intervals,
    state_at,
)
from b2b_physical_model import (
    ENERGY_NODES,
    allocate_front_sink,
    build_opacity_fit,
    make_params,
    make_spectrum_lanes,
)
from monolithic_model_b2a import KB_ERG, opacity_cMpc_inv, pchip_eval
from primary_exact_zero_model import (
    physical_state,
    state_from_z7,
    z7_from_state,
    z7_rhs,
)

PHYSICAL_COMPONENTS = [
    "EFFECTIVE_HI_SUBGRID",
    "EXPLICIT_HI_ATOMIC",
    "EXPLICIT_HEI_ATOMIC",
    "EXPLICIT_HEII_ATOMIC",
]


def find_one(root: Path, filename: str) -> Path:
    matches = list(root.rglob(filename))
    if not matches:
        raise FileNotFoundError(f"{filename} below {root}")
    return sorted(matches, key=lambda p: (len(p.parts), str(p)))[0]


def legacy_discrete_weights(group: str) -> np.ndarray:
    lane = make_spectrum_lanes()[PRIMARY]
    if group == "G1":
        nodes = np.asarray(ENERGY_NODES[:4], dtype=float)
    elif group == "G2a":
        nodes = np.asarray(ENERGY_NODES[4:], dtype=float)
    else:
        raise ValueError(group)
    values = np.array([lane.within_group_shape(float(e)) for e in nodes])
    return values / values.sum()


@dataclass
class ResponseAnchoredOpacity:
    public: pd.DataFrame
    raw_path: Path
    density_path: Path
    z: float
    direct_nodes: int = 144

    def __post_init__(self) -> None:
        self.public_eval, self.public_meta = public_p04_interpolator(
            self.public, self.z
        )
        self.raw_models, self.raw_meta = raw_gamma_node_models(
            self.raw_path, self.density_path, self.z
        )
        self.public_nodes = np.asarray(
            self.public_meta["kappa_nodes_cMpc_inv"], dtype=float
        )
        self.central_gamma12 = float(self.public_meta["central_gamma12"])
        self.log_gamma_knots = np.asarray(self.raw_models[0].x, dtype=float)
        self.gamma_knots = np.exp(self.log_gamma_knots)
        self.gamma_min = float(self.gamma_knots.min())
        self.gamma_max = float(self.gamma_knots.max())
        self.raw_central_nodes = self.raw_node_kappa(self.central_gamma12)
        self._quadrature = {
            g: normalized_group_quadrature(g, self.direct_nodes)
            for g in ("G1", "G2a")
        }
        self._legacy_weights = {
            "G1": legacy_discrete_weights("G1"),
            "G2a": legacy_discrete_weights("G2a"),
        }

    def check_gamma(self, gamma12: float) -> None:
        if not (self.gamma_min <= gamma12 <= self.gamma_max):
            raise ValueError(
                f"Gamma12={gamma12} outside raw domain "
                f"[{self.gamma_min},{self.gamma_max}]"
            )

    def raw_node_kappa(self, gamma12: float) -> np.ndarray:
        self.check_gamma(gamma12)
        return np.array(
            [
                float(np.exp(model(np.log(gamma12))))
                for model in self.raw_models
            ],
            dtype=float,
        )

    def response_nodes(self, gamma12: float) -> np.ndarray:
        return self.raw_node_kappa(gamma12) / self.raw_central_nodes

    def conditioned_node_kappa(self, gamma12: float) -> np.ndarray:
        return self.public_nodes * self.response_nodes(gamma12)

    def conditioned_energy_evaluator(
        self, gamma12: float
    ) -> Callable[[np.ndarray], np.ndarray]:
        nodes = self.conditioned_node_kappa(gamma12)
        pchip = PchipInterpolator(
            np.log(PUBLIC_ENERGY_NODES), np.log(nodes), extrapolate=False
        )

        def evaluate(energy: np.ndarray) -> np.ndarray:
            e = np.asarray(energy, dtype=float)
            if np.any(e < PUBLIC_ENERGY_NODES[0]) or np.any(
                e > PUBLIC_ENERGY_NODES[-1]
            ):
                raise ValueError("Gamma-conditioned energy extrapolation")
            return np.exp(pchip(np.log(e)))

        return evaluate

    def legacy_group_kappa(
        self, gamma12: float, group: str, raw_absolute: bool = False
    ) -> float:
        nodes = (
            self.raw_node_kappa(gamma12)
            if raw_absolute
            else self.conditioned_node_kappa(gamma12)
        )
        if group == "G1":
            return float(nodes[:4] @ self._legacy_weights[group])
        if group == "G2a":
            return float(nodes[4:] @ self._legacy_weights[group])
        raise ValueError(group)

    def direct_group_kappa(self, gamma12: float, group: str) -> float:
        energy, weights = self._quadrature[group]
        evaluator = self.conditioned_energy_evaluator(gamma12)
        return float(np.sum(weights * evaluator(energy)))

    def direct_fit(self) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
        direct = np.array(
            [
                [
                    self.direct_group_kappa(float(gamma), "G1"),
                    self.direct_group_kappa(float(gamma), "G2a"),
                ]
                for gamma in self.gamma_knots
            ]
        )
        p1 = PchipInterpolator(
            self.log_gamma_knots, np.log(direct[:, 0]), extrapolate=False
        )
        p2 = PchipInterpolator(
            self.log_gamma_knots, np.log(direct[:, 1]), extrapolate=False
        )
        coeff = np.stack([p1.c, p2.c])
        table = pd.DataFrame(
            {
                "z": self.z,
                "Gamma12": self.gamma_knots,
                "kappa_G1_direct_cMpc_inv": direct[:, 0],
                "kappa_G2a_direct_cMpc_inv": direct[:, 1],
                "fit_G1_cMpc_inv": np.exp(p1(self.log_gamma_knots)),
                "fit_G2a_cMpc_inv": np.exp(p2(self.log_gamma_knots)),
            }
        )
        return self.log_gamma_knots.copy(), coeff, table


def state_numpy(z7: np.ndarray, p: dict[str, Any]) -> dict[str, Any]:
    """Fast algebraically equivalent primary physical-state conversion."""
    n123 = np.exp(z7[:3])
    n = np.r_[n123, 0.0]
    xh = 1.0 / (1.0 + np.exp(-z7[3]))
    logits = np.array([0.0, z7[4], z7[5]], dtype=float)
    logits -= logits.max()
    he = np.exp(logits)
    he /= he.sum()
    u = float(np.exp(z7[6]))
    pref = C_LIGHT * (1.0 + float(p["z_cos"])) ** 3 / MPC_CM**3
    sigma_hi = np.asarray(p["sigma_HI"], dtype=float)
    sigma_hei = np.asarray(p["sigma_HeI"], dtype=float)
    sigma_heii = np.asarray(p["sigma_HeII"], dtype=float)
    gamma_h = pref * float(np.dot(sigma_hi, n))
    gamma_hei = pref * float(np.dot(sigma_hei, n))
    gamma_heii = pref * float(np.dot(sigma_heii, n))
    n_h = float(p["nH_phys"])
    n_he = float(p["nHe_phys"])
    ne = n_h * xh + n_he * (he[1] + 2.0 * he[2])
    T = 2.0 * u / (3.0 * KB_ERG * (n_h + n_he + ne))
    return {
        "N": n,
        "xHII": xh,
        "xHeI": he[0],
        "xHeII": he[1],
        "xHeIII": he[2],
        "u": u,
        "T": T,
        "ne": ne,
        "GammaHI": gamma_h,
        "GammaHeI": gamma_hei,
        "GammaHeII": gamma_heii,
    }


def legacy_formula_regression(
    response: ResponseAnchoredOpacity,
    raw_path: Path,
    density_path: Path,
    lane: Any,
) -> pd.DataFrame:
    knots, coeff, table = build_opacity_fit(
        raw_path, density_path, response.z, lane
    )
    rows = []
    for record in table.itertuples():
        gamma = float(record.Gamma12)
        for group, expected in [
            ("G1", float(record.kappa_G1_cMpc_inv)),
            ("G2a", float(record.kappa_G2a_cMpc_inv)),
        ]:
            reproduced = response.legacy_group_kappa(
                gamma, group, raw_absolute=True
            )
            rows.append(
                {
                    "z": response.z,
                    "Gamma12": gamma,
                    "group": group,
                    "expected_raw_legacy_kappa_cMpc_inv": expected,
                    "reproduced_raw_legacy_kappa_cMpc_inv": reproduced,
                    "relative_residual": abs(reproduced - expected)
                    / max(abs(expected), 1.0e-300),
                    "formula": "locked B2B sparse-node weighted opacity",
                }
            )
    return pd.DataFrame(rows)


def reconcile_on_legacy_history(
    intervals: list[Any],
    public: pd.DataFrame,
    raw_path: Path,
    density_path: Path,
    lane: Any,
    n_time: int = 96,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    residual_rows = []
    response_rows = []
    byte_rows = []

    for index, interval in enumerate(intervals):
        response = ResponseAnchoredOpacity(
            public, raw_path, density_path, interval.z_mid
        )
        byte_rows.append(
            legacy_formula_regression(response, raw_path, density_path, lane)
        )
        tx, tw = leggauss(n_time)
        times = 0.5 * interval.duration_s * (tx + 1.0)
        weights = 0.5 * interval.duration_s * tw
        accum = {
            (group, name): 0.0
            for group in ("G1", "G2a")
            for name in (
                "inherited",
                "reproduced_raw_legacy",
                "raw_model_legacy",
                "public_legacy",
                "public_direct",
            )
        }
        gamma_values = []

        for t, wt in zip(times, weights):
            z7 = np.asarray(interval.solution.sol(float(t)), dtype=float)
            state = state_numpy(z7, interval.p)
            gamma12 = state["GammaHI"] / 1.0e-12
            response.check_gamma(gamma12)
            gamma_values.append(gamma12)
            inherited = np.asarray(
                opacity_cMpc_inv(
                    state_from_z7(jnp.asarray(z7), interval.p), interval.p
                ),
                dtype=float,
            )
            vchi = C_LIGHT * (1.0 + interval.z_mid) / MPC_CM

            for gi, group in enumerate(("G1", "G2a")):
                n_group = state["N"][gi]
                atomic_other = 0.0
                if group == "G2a":
                    n_he = float(interval.p["nHe_phys"])
                    n_hei = n_he * state["xHeI"]
                    cMpc_per_cm = float(interval.p["cMpc_per_cm"])
                    atomic_other = (
                        n_hei
                        * float(np.asarray(interval.p["sigma_HeI"])[1])
                        * cMpc_per_cm
                    )
                xlog = jnp.log(jnp.array(gamma12))
                runtime_effective = float(
                    jnp.exp(
                        pchip_eval(
                            interval.p["log_kappa_knots"],
                            interval.p["log_kappa_pchip_coeffs"][gi],
                            xlog,
                        )
                    )
                )
                kappas = {
                    "inherited": float(inherited[gi]),
                    "reproduced_raw_legacy":
                        runtime_effective + atomic_other,
                    "raw_model_legacy":
                        response.legacy_group_kappa(
                            gamma12, group, raw_absolute=True
                        ) + atomic_other,
                    "public_legacy":
                        response.legacy_group_kappa(gamma12, group)
                        + atomic_other,
                    "public_direct":
                        response.direct_group_kappa(gamma12, group)
                        + atomic_other,
                }
                for name, kappa in kappas.items():
                    accum[(group, name)] += wt * vchi * n_group * kappa

        response_rows.append(
            {
                "z": interval.z_mid,
                "central_gamma12": response.central_gamma12,
                "gamma12_min": response.gamma_min,
                "gamma12_max": response.gamma_max,
                "trajectory_gamma12_min": float(np.min(gamma_values)),
                "trajectory_gamma12_max": float(np.max(gamma_values)),
                "central_response_max_abs_minus_one": float(
                    np.max(
                        np.abs(
                            response.response_nodes(
                                response.central_gamma12
                            )
                            - 1.0
                        )
                    )
                ),
                "public_anchor_nodes_cMpc_inv":
                    json.dumps(response.public_nodes.tolist()),
                "raw_central_nodes_cMpc_inv":
                    json.dumps(response.raw_central_nodes.tolist()),
                "density_averaging":
                    "effective_GH_weight; opacity average sum(w/lambda)",
                "zre_averaging":
                    "P(z_re|ionized,z) from locked tanh Q history",
                "eta_global_convention":
                    "P0.4 PUBLIC_REPO_EXACT/raw continuous joint convention",
                "extrapolation": "FORBIDDEN",
            }
        )

        for group in ("G1", "G2a"):
            averaged = {
                name: accum[(group, name)] / interval.duration_s
                for name in (
                    "inherited",
                    "reproduced_raw_legacy",
                    "raw_model_legacy",
                    "public_legacy",
                    "public_direct",
                )
            }
            inherited = averaged["inherited"]
            reproduction = averaged["reproduced_raw_legacy"]
            raw_model = averaged["raw_model_legacy"]
            raw_interpolator = raw_model - reproduction
            normalization = averaged["public_legacy"] - reproduction
            shape = averaged["public_direct"] - averaged["public_legacy"]
            canonical = averaged["public_direct"] - inherited
            row = {
                "history_provenance":
                    "B2C1C_LEGACY_HISTORY_AUDITOR_ONLY",
                "interval_index": index,
                "z_mid": interval.z_mid,
                "group": group,
                "Gamma12_min": float(np.min(gamma_values)),
                "Gamma12_max": float(np.max(gamma_values)),
                "raw_Gamma12_domain_min": response.gamma_min,
                "raw_Gamma12_domain_max": response.gamma_max,
                "inherited_raw_legacy_rate": inherited,
                "reproduced_raw_legacy_rate": reproduction,
                "raw_model_legacy_rate": raw_model,
                "LEGACY_RAW_RESPONSE_INTERPOLATOR_RESIDUAL_rate":
                    raw_interpolator,
                "LEGACY_RAW_RESPONSE_INTERPOLATOR_RESIDUAL_relative":
                    raw_interpolator / max(abs(inherited), 1.0),
                "public_anchored_legacy_rate": averaged["public_legacy"],
                "public_anchored_direct_rate": averaged["public_direct"],
                "legacy_reproduction_relative_residual":
                    abs(reproduction - inherited)
                    / max(abs(inherited), 1.0),
                "CENTRAL_GAMMA_NORMALIZATION_RESIDUAL_rate":
                    normalization,
                "CENTRAL_GAMMA_NORMALIZATION_RESIDUAL_relative":
                    normalization / max(abs(inherited), 1.0),
                "GROUP_SHAPE_DISCRETIZATION_RESIDUAL_rate": shape,
                "GROUP_SHAPE_DISCRETIZATION_RESIDUAL_relative":
                    shape / max(abs(inherited), 1.0),
                "CANONICAL_CHANGE_RESIDUAL_rate": canonical,
                "CANONICAL_CHANGE_RESIDUAL_relative":
                    canonical / max(abs(inherited), 1.0),
                "physical_unresolved_sink_interpretation_allowed": False,
            }
            rows.append(row)
            for name, rate, relative in [
                (
                    "LEGACY_RAW_RESPONSE_INTERPOLATOR_RESIDUAL",
                    raw_interpolator,
                    raw_interpolator / max(abs(inherited), 1.0),
                ),
                (
                    "CENTRAL_GAMMA_NORMALIZATION_RESIDUAL",
                    normalization,
                    row[
                        "CENTRAL_GAMMA_NORMALIZATION_RESIDUAL_relative"
                    ],
                ),
                (
                    "GROUP_SHAPE_DISCRETIZATION_RESIDUAL",
                    shape,
                    row[
                        "GROUP_SHAPE_DISCRETIZATION_RESIDUAL_relative"
                    ],
                ),
                (
                    "CANONICAL_CHANGE_RESIDUAL",
                    canonical,
                    row["CANONICAL_CHANGE_RESIDUAL_relative"],
                ),
            ]:
                residual_rows.append(
                    {
                        "history_provenance":
                            "B2C1C_LEGACY_HISTORY_AUDITOR_ONLY",
                        "interval_index": index,
                        "z_mid": interval.z_mid,
                        "group": group,
                        "residual_name": name,
                        "rate_s-1_cMpc-3": rate,
                        "relative_to_inherited": relative,
                        "registry_class":
                            "NUMERICAL_OR_OPERATOR_CLOSURE",
                        "physical_unresolved_sink": False,
                    }
                )

    return (
        pd.DataFrame(rows),
        pd.DataFrame(residual_rows),
        pd.DataFrame(response_rows),
        pd.concat(byte_rows, ignore_index=True),
    )


@dataclass
class CanonicalInterval:
    index: int
    z_start: float
    z_mid: float
    z_end: float
    duration_s: float
    emission_rate: float
    front_sink: np.ndarray
    p: dict[str, Any]
    solution: Any
    response: ResponseAnchoredOpacity


def re_evolve_direct_history(
    b2b_root: Path,
    b2c1c_root: Path,
    public: pd.DataFrame,
    raw_path: Path,
    density_path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, list[CanonicalInterval], pd.DataFrame]:
    lane = make_spectrum_lanes()[PRIMARY]
    old_history = pd.read_csv(
        b2c1c_root / "data" / "primary_exact_zero_G3_history.csv"
    )
    old_ledger = pd.read_csv(
        b2c1c_root / "data" / "primary_photon_ledger.csv"
    )
    forward = pd.read_csv(b2b_root / "data" / "forward_history_photon_ledger.csv")
    forward = forward[forward["lane"] == PRIMARY].sort_values(
        "z_mid", ascending=False
    )
    allocation = pd.read_csv(
        find_one(b2b_root, "photon_allocation_all_lanes.csv")
    )
    allocation = allocation[
        allocation["lane"] == "INSIDE_OUT_SELF_SHIELD_PRIMARY"
    ].set_index("z_mid")

    initial = old_history[np.isclose(old_history["z"], 6.0)].iloc[0]
    n123 = np.array([initial.N1, initial.N2, initial.N3], dtype=float)
    xh, x2, x3 = (
        float(initial.xHII),
        float(initial.xHeII),
        float(initial.xHeIII),
    )
    n_h = NH0 * 7.0**3
    n_he = YHE * n_h
    ne = n_h * xh + n_he * (x2 + 2.0 * x3)
    u = 1.5 * (n_h + n_he + ne) * KB_ERG * float(initial.T_K)
    z7 = z7_from_state(n123, xh, x2, x3, u)

    history_rows = [
        {
            "history_provenance": "CANONICAL_DIRECT_REEVOLVED",
            "z": 6.0,
            "N1": n123[0],
            "N2": n123[1],
            "N3": n123[2],
            "N4_exact": 0.0,
            "xHII": xh,
            "xHeI": 1.0 - x2 - x3,
            "xHeII": x2,
            "xHeIII": x3,
            "T_K": float(initial.T_K),
            "Gamma_HI": float(initial.Gamma_HI),
            "Gamma_HeII_exact": 0.0,
            "Gamma_HeI": math.nan,
        }
    ]
    ledger_rows = []
    intervals = []
    fit_rows = []
    rhs = jax.jit(z7_rhs)
    p_prev = None

    for index, rec in enumerate(forward.itertuples()):
        z_mid = float(rec.z_mid)
        z_end = float(rec.z_next)
        z_start = round(2.0 * z_mid - z_end, 12)
        duration = float(rec.dt_Myr) * MYR_S
        emission = float(rec.total_emission)

        response = ResponseAnchoredOpacity(
            public, raw_path, density_path, z_mid
        )
        knots, coeffs, table = response.direct_fit()
        table["group_operator"] = "DIRECT_ENERGY_GROUP"
        fit_rows.append(table)

        if p_prev is None:
            current_n = np.r_[n123, 0.0]
            current_x = np.array([xh, x2, x3])
            current_u = u
        else:
            current = state_numpy(z7, p_prev)
            current_n = current["N"]
            current_x = np.array(
                [current["xHII"], current["xHeII"], current["xHeIII"]]
            )
            current_u = current["u"]

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
            n_prev=current_n,
            x_prev=current_x,
            u_prev=current_u,
            front_sink_group=front,
            scale_n=np.r_[np.maximum(current_n[:3], 1.0e-300), 1.0e-300],
            scale_u=current_u,
            scale_gamma=max(float(history_rows[-1]["Gamma_HI"]), 1.0e-30),
        )

        def scipy_rhs(t: float, y: np.ndarray) -> np.ndarray:
            return np.asarray(
                rhs(jnp.asarray(y), jnp.array(emission), p), dtype=float
            )

        z7_start = z7.copy()
        solution = solve_ivp(
            scipy_rhs,
            (0.0, duration),
            z7,
            method="BDF",
            rtol=5.0e-13,
            atol=np.full(7, 5.0e-14),
            dense_output=True,
            max_step=duration / 240.0,
        )
        if not solution.success:
            raise RuntimeError(solution.message)
        z7 = solution.y[:, -1]
        start = state_numpy(z7_start, p)
        end = state_numpy(z7, p)
        if end["N"][3] != 0.0 or end["GammaHeII"] != 0.0:
            raise RuntimeError("Exact primary G3/GammaHeII constraint drifted")

        # Time-integrated photon ledger.
        tx, tw = leggauss(256)
        times = 0.5 * duration * (tx + 1.0)
        weights = 0.5 * duration * tw
        absorption_integrals = np.zeros(4)
        redshift_integral = 0.0
        gamma_values = []
        for t, wt in zip(times, weights):
            zz = np.asarray(solution.sol(float(t)), dtype=float)
            state_j = state_from_z7(jnp.asarray(zz), p)
            state_n = state_numpy(zz, p)
            gamma_values.append(state_n["GammaHI"] / 1.0e-12)
            kappa = np.asarray(opacity_cMpc_inv(state_j, p), dtype=float)
            vchi = C_LIGHT * (1.0 + z_mid) / MPC_CM
            absorption_integrals += wt * vchi * state_n["N"] * kappa
            red_out = np.asarray(p["redshift_coeff"], dtype=float) * float(
                p["Hubble"]
            )
            redshift_integral += wt * red_out[0] * state_n["N"][0]

        absorption_rates = absorption_integrals / duration
        absorption_total = float(absorption_rates.sum())
        storage = (
            float(end["N"][:3].sum()) - float(start["N"][:3].sum())
        ) / duration
        redshift_rate = redshift_integral / duration
        front_rate = float(front[:3].sum())
        residual = emission - (
            storage + absorption_total + redshift_rate + front_rate
        )
        ledger_rows.append(
            {
                "history_provenance": "CANONICAL_DIRECT_REEVOLVED",
                "interval_index": index,
                "z_start": z_start,
                "z_mid": z_mid,
                "z_end": z_end,
                "dt_Myr": duration / MYR_S,
                "emission_rate": emission,
                "storage_rate": storage,
                "ionized_absorption_rate": absorption_total,
                "threshold_redshift_loss_rate": redshift_rate,
                "front_absorption_rate": front_rate,
                "relative_photon_ledger_residual":
                    residual / max(abs(emission), 1.0),
                "absorption_G1_rate": absorption_rates[0],
                "absorption_G2a_rate": absorption_rates[1],
                "absorption_G2b_rate": absorption_rates[2],
                "absorption_G3_rate": absorption_rates[3],
                "Gamma12_min": float(np.min(gamma_values)),
                "Gamma12_max": float(np.max(gamma_values)),
                "raw_Gamma12_domain_min": response.gamma_min,
                "raw_Gamma12_domain_max": response.gamma_max,
                "N4_exact": end["N"][3],
                "Gamma_HeII_exact": end["GammaHeII"],
            }
        )
        history_rows.append(
            {
                "history_provenance": "CANONICAL_DIRECT_REEVOLVED",
                "z": z_end,
                "N1": end["N"][0],
                "N2": end["N"][1],
                "N3": end["N"][2],
                "N4_exact": end["N"][3],
                "xHII": end["xHII"],
                "xHeI": end["xHeI"],
                "xHeII": end["xHeII"],
                "xHeIII": end["xHeIII"],
                "T_K": end["T"],
                "Gamma_HI": end["GammaHI"],
                "Gamma_HeII_exact": end["GammaHeII"],
                "Gamma_HeI": end["GammaHeI"],
            }
        )
        intervals.append(
            CanonicalInterval(
                index=index,
                z_start=z_start,
                z_mid=z_mid,
                z_end=z_end,
                duration_s=duration,
                emission_rate=emission,
                front_sink=front,
                p=p,
                solution=solution,
                response=response,
            )
        )
        p_prev = p

    return (
        pd.DataFrame(history_rows),
        pd.DataFrame(ledger_rows),
        intervals,
        pd.concat(fit_rows, ignore_index=True),
    )


def conditioned_component_arrays(
    interval: CanonicalInterval,
    state: dict[str, Any],
    group: str,
    energy: np.ndarray,
) -> dict[str, np.ndarray]:
    evaluator = interval.response.conditioned_energy_evaluator(
        state["GammaHI"] / 1.0e-12
    )
    return component_energy_arrays(
        state, interval.p, group, energy, evaluator
    )


def decompose_canonical_history(
    intervals: list[CanonicalInterval],
    n_time: int = 96,
    n_energy: int = 128,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    group_rows = []
    component_rows = []
    fit_rows = []
    quadrature = {
        g: normalized_group_quadrature(g, n_energy)
        for g in GROUP_ORDER
    }

    for interval in intervals:
        tx, tw = leggauss(n_time)
        times = 0.5 * interval.duration_s * (tx + 1.0)
        weights = 0.5 * interval.duration_s * tw
        group_acc = {g: 0.0 for g in GROUP_ORDER}
        comp_acc = {
            (g, c): 0.0
            for g in GROUP_ORDER
            for c in PHYSICAL_COMPONENTS
        }
        comp_min = {
            (g, c): math.inf
            for g in GROUP_ORDER
            for c in PHYSICAL_COMPONENTS
        }
        fit_error = []

        for t, wt in zip(times, weights):
            zz = np.asarray(interval.solution.sol(float(t)), dtype=float)
            state = state_numpy(zz, interval.p)
            state_j = state_from_z7(jnp.asarray(zz), interval.p)
            fitted = np.asarray(
                opacity_cMpc_inv(state_j, interval.p), dtype=float
            )
            vchi = C_LIGHT * (1.0 + interval.z_mid) / MPC_CM

            for gi, group in enumerate(GROUP_ORDER):
                energy, eweight = quadrature[group]
                arrays = conditioned_component_arrays(
                    interval, state, group, energy
                )
                kappas = {
                    c: float(np.sum(eweight * arr))
                    for c, arr in arrays.items()
                }
                direct_total = sum(kappas.values())
                n_group = state["N"][gi]
                rate = vchi * n_group * direct_total
                group_acc[group] += wt * rate
                if abs(fitted[gi]) > 0:
                    fit_error.append(
                        abs(direct_total - fitted[gi])
                        / abs(fitted[gi])
                    )
                for component, kappa in kappas.items():
                    comp_acc[(group, component)] += (
                        wt * vchi * n_group * kappa
                    )
                    comp_min[(group, component)] = min(
                        comp_min[(group, component)], kappa
                    )

        fit_rows.append(
            {
                "interval_index": interval.index,
                "z_mid": interval.z_mid,
                "direct_quadrature_vs_tabled_fit_relative_residual_max":
                    float(max(fit_error) if fit_error else 0.0),
            }
        )
        for group in GROUP_ORDER:
            total = group_acc[group] / interval.duration_s
            group_rows.append(
                {
                    "history_provenance": "CANONICAL_DIRECT_REEVOLVED",
                    "interval_index": interval.index,
                    "z_mid": interval.z_mid,
                    "group": group,
                    "total_absorption_rate_s-1_cMpc-3": total,
                    "component_sum_rate_s-1_cMpc-3": sum(
                        comp_acc[(group, c)] / interval.duration_s
                        for c in PHYSICAL_COMPONENTS
                    ),
                }
            )
            for component in PHYSICAL_COMPONENTS:
                component_rows.append(
                    {
                        "history_provenance":
                            "CANONICAL_DIRECT_REEVOLVED",
                        "interval_index": interval.index,
                        "z_mid": interval.z_mid,
                        "group": group,
                        "component": component,
                        "absorption_rate_s-1_cMpc-3":
                            comp_acc[(group, component)]
                            / interval.duration_s,
                        "minimum_kappa_cMpc_inv":
                            comp_min[(group, component)],
                        "physical_component": True,
                        "unresolved_sink_interpretation":
                            "NOT_COMPUTED_IN_R1",
                    }
                )

    group_df = pd.DataFrame(group_rows)
    group_df["component_sum_relative_residual"] = (
        (
            group_df["component_sum_rate_s-1_cMpc-3"]
            - group_df["total_absorption_rate_s-1_cMpc-3"]
        ).abs()
        / group_df["total_absorption_rate_s-1_cMpc-3"].abs().clip(
            lower=1.0
        )
    )
    return group_df, pd.DataFrame(component_rows), pd.DataFrame(fit_rows)


def flexrt_refinement(
    intervals: list[CanonicalInterval],
    n_time: int = 32,
    n_energy: int = 96,
) -> pd.DataFrame:
    rows = []
    quadrature = {
        g: normalized_group_quadrature(g, n_energy)
        for g in GROUP_ORDER
    }
    sequences = {
        "STRESS_1_cMpc": [1.0 / 2**i for i in range(9)],
        "FLEXRT_2_hinv_ckpc": [
            (0.002 / 0.68) / 2**i for i in range(6)
        ],
    }

    for interval in intervals:
        tx, tw = leggauss(n_time)
        times = 0.5 * interval.duration_s * (tx + 1.0)
        weights = 0.5 * interval.duration_s * tw
        cache = []
        reference = {
            (g, c): 0.0
            for g in GROUP_ORDER
            for c in [*PHYSICAL_COMPONENTS, "TOTAL_PHYSICAL"]
        }
        for t, wt in zip(times, weights):
            zz = np.asarray(interval.solution.sol(float(t)), dtype=float)
            state = state_numpy(zz, interval.p)
            vchi = C_LIGHT * (1.0 + interval.z_mid) / MPC_CM
            item = {"wt": wt, "state": state, "vchi": vchi, "groups": {}}
            for gi, group in enumerate(GROUP_ORDER):
                energy, eweight = quadrature[group]
                arrays = conditioned_component_arrays(
                    interval, state, group, energy
                )
                n_group = state["N"][gi]
                total = sum(arrays.values())
                for component, arr in arrays.items():
                    reference[(group, component)] += (
                        wt
                        * vchi
                        * n_group
                        * float(np.sum(eweight * arr))
                    )
                reference[(group, "TOTAL_PHYSICAL")] += (
                    wt
                    * vchi
                    * n_group
                    * float(np.sum(eweight * total))
                )
                item["groups"][group] = (
                    eweight, arrays, total, n_group
                )
            cache.append(item)

        for key in reference:
            reference[key] /= interval.duration_s

        for sequence, cells in sequences.items():
            previous = {}
            for level, delta in enumerate(cells):
                deposits = {key: 0.0 for key in reference}
                for item in cache:
                    wt = item["wt"]
                    vchi = item["vchi"]
                    for group in GROUP_ORDER:
                        eweight, arrays, total, n_group = item["groups"][group]
                        tau = total * delta
                        absorbed = -np.expm1(-np.clip(tau, 0.0, 745.0))
                        deposits[(group, "TOTAL_PHYSICAL")] += (
                            wt
                            * vchi
                            / delta
                            * n_group
                            * float(np.sum(eweight * absorbed))
                        )
                        for component, arr in arrays.items():
                            frac = np.divide(
                                arr,
                                total,
                                out=np.zeros_like(arr),
                                where=total > 0,
                            )
                            deposits[(group, component)] += (
                                wt
                                * vchi
                                / delta
                                * n_group
                                * float(
                                    np.sum(eweight * absorbed * frac)
                                )
                            )
                for key, integral in deposits.items():
                    value = integral / interval.duration_s
                    ref = reference[key]
                    rel = abs(value - ref) / max(abs(ref), 1.0)
                    order = math.nan
                    if key in previous and rel > 0 and previous[key] > 0:
                        order = math.log(previous[key] / rel, 2.0)
                    previous[key] = rel
                    rows.append(
                        {
                            "history_provenance":
                                "CANONICAL_DIRECT_REEVOLVED",
                            "interval_index": interval.index,
                            "z_mid": interval.z_mid,
                            "sequence": sequence,
                            "level": level,
                            "delta_chi_cMpc": delta,
                            "group": key[0],
                            "component": key[1],
                            "finite_cell_deposition_rate": value,
                            "differential_hazard_rate": ref,
                            "relative_difference": rel,
                            "observed_order": order,
                        }
                    )
    return pd.DataFrame(rows)


def compare_histories(
    canonical: pd.DataFrame, legacy_path: Path
) -> pd.DataFrame:
    legacy = pd.read_csv(legacy_path)
    columns = [
        "N1", "N2", "N3", "xHII", "xHeII", "xHeIII",
        "T_K", "Gamma_HI",
    ]
    merged = canonical.merge(
        legacy[
            [
                "z", "N1", "N2", "N3", "N4_exact",
                "xHII", "xHeI", "xHeII", "xHeIII",
                "T_K", "Gamma_HI", "Gamma_HeI",
                "Gamma_HeII_exact",
            ]
        ],
        on="z",
        suffixes=("_direct", "_legacy"),
    )
    for column in columns:
        merged[f"{column}_relative_difference"] = (
            merged[f"{column}_direct"] / merged[f"{column}_legacy"] - 1.0
        )
    return merged


def execute(
    b2b_root: Path,
    b2c1c_root: Path,
    b2c2a_root: Path,
    p04_root: Path,
    output: Path,
) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    public = pd.read_csv(
        p04_root / "data" / "public_repo_exact_checkpoint_global.csv"
    )
    public = public[
        (public["source"] == "PUBLIC_REPO_EXACT_CHECKPOINT")
        & (public["mode"] == "public_continuous_joint")
    ].copy()
    raw_path = find_one(b2b_root, "environment_mfp_energies.txt")
    density_path = find_one(
        b2b_root, "density_mapping_colossus_1_3_10_port.csv"
    )
    lane = make_spectrum_lanes()[PRIMARY]

    legacy_intervals = reconstruct_intervals(b2b_root, b2c1c_root)
    reconciliation, residual_registry, response_audit, byte_regression = (
        reconcile_on_legacy_history(
            legacy_intervals,
            public,
            raw_path,
            density_path,
            lane,
        )
    )
    reconciliation.to_csv(
        output / "operator_reconciliation_on_legacy_history.csv",
        index=False,
    )
    residual_registry.to_csv(
        output / "numerical_residual_registry.csv", index=False
    )
    response_audit.to_csv(
        output / "raw_response_anchor_audit.csv", index=False
    )
    byte_regression.to_csv(
        output / "legacy_operator_byte_formula_regression.csv",
        index=False,
    )

    max_change = float(
        reconciliation["CANONICAL_CHANGE_RESIDUAL_relative"].abs().max()
    )
    changed = max_change > 1.0e-3

    canonical_history, canonical_ledger, canonical_intervals, fit_tables = (
        re_evolve_direct_history(
            b2b_root, b2c1c_root, public, raw_path, density_path
        )
    )
    canonical_history.to_csv(
        output / "canonical_direct_history.csv", index=False
    )
    canonical_ledger.to_csv(
        output / "canonical_direct_photon_ledger.csv", index=False
    )
    fit_tables.to_csv(
        output / "gamma_conditioned_group_fit_tables.csv", index=False
    )

    group_df, component_df, fit_audit = decompose_canonical_history(
        canonical_intervals
    )
    group_df.to_csv(
        output / "reconciled_group_total_absorption.csv", index=False
    )
    component_df.to_csv(
        output / "reconciled_physical_component_absorption.csv",
        index=False,
    )
    fit_audit.to_csv(
        output / "direct_group_fit_audit.csv", index=False
    )

    cell_df = flexrt_refinement(canonical_intervals)
    cell_df.to_csv(
        output / "cell_deposition_refinement.csv", index=False
    )

    history_compare = compare_histories(
        canonical_history,
        b2c1c_root / "data" / "primary_exact_zero_G3_history.csv",
    )
    history_compare.to_csv(
        output / "history_reconciliation_comparison.csv", index=False
    )

    central_response = float(
        response_audit["central_response_max_abs_minus_one"].max()
    )
    legacy_reproduction = float(
        reconciliation[
            "legacy_reproduction_relative_residual"
        ].max()
    )
    byte_max = float(byte_regression["relative_residual"].max())
    ledger_max = float(
        canonical_ledger[
            "relative_photon_ledger_residual"
        ].abs().max()
    )
    component_sum_max = float(
        group_df["component_sum_relative_residual"].max()
    )
    direct_fit_max = float(
        fit_audit[
            "direct_quadrature_vs_tabled_fit_relative_residual_max"
        ].max()
    )
    negative = component_df[
        (component_df["minimum_kappa_cMpc_inv"] < -1.0e-14)
        | (component_df["absorption_rate_s-1_cMpc-3"] < -1.0)
    ]
    gamma_domain = bool(
        (
            canonical_ledger["Gamma12_min"]
            >= canonical_ledger["raw_Gamma12_domain_min"]
        ).all()
        and (
            canonical_ledger["Gamma12_max"]
            <= canonical_ledger["raw_Gamma12_domain_max"]
        ).all()
    )
    exact_g3 = bool(
        (canonical_history["N4_exact"] == 0.0).all()
        and (canonical_history["Gamma_HeII_exact"] == 0.0).all()
        and (canonical_ledger["absorption_G3_rate"] == 0.0).all()
    )
    smallest = (
        cell_df.sort_values("delta_chi_cMpc")
        .groupby(
            ["interval_index", "sequence", "group", "component"],
            as_index=False,
        )
        .first()
    )
    nonzero = smallest[
        smallest["differential_hazard_rate"].abs() > 1.0
    ]
    cell_max = float(nonzero["relative_difference"].max())
    orders = cell_df[np.isfinite(cell_df["observed_order"])]
    order_range = [
        float(orders["observed_order"].min()),
        float(orders["observed_order"].max()),
    ]
    endpoint_cols = [
        c for c in history_compare.columns
        if c.endswith("_relative_difference")
    ]
    endpoint_max = float(
        history_compare[endpoint_cols].abs().to_numpy().max()
    )

    passed = bool(
        central_response < 1.0e-12
        and legacy_reproduction < 1.0e-12
        and byte_max < 1.0e-12
        and ledger_max < 1.0e-8
        and component_sum_max < 1.0e-8
        and direct_fit_max < 0.01
        and len(negative) == 0
        and gamma_domain
        and exact_g3
        and cell_max < 0.01
    )
    verdict = (
        "PASS_B2C2B_AUTHORIZED"
        if passed
        else "FAIL_CLOSED_R1_RECONCILIATION"
    )
    decision = {
        "canonical_operator_before":
            "LEGACY_RAW_ABSOLUTE_DISCRETE_NODE",
        "canonical_operator_after":
            "PUBLIC_ANCHORED_RAW_GAMMA_RESPONSE_DIRECT_ENERGY_GROUP",
        "canonical_operator_changed": changed,
        "max_operator_change_relative_on_legacy_history": max_change,
        "history_action":
            "REEVOLVED_FROM_Z6_DO_NOT_MIX"
            if changed
            else "NO_REEVOLUTION_NEEDED",
        "legacy_history_status": "AUDITOR_ONLY",
        "canonical_history_status": "PRODUCTION_CANDIDATE",
        "B2C2B_authorized": passed,
    }
    (output.parent / "HISTORY_RECONCILIATION_DECISION.json").write_text(
        json.dumps(decision, indent=2), encoding="utf-8"
    )
    results = {
        "stage":
            "P0.5-B2C2A-R1-GAMMA-CONDITIONED-DIRECT-OPACITY-RECONCILIATION",
        "verdict": verdict,
        "provenance":
            "RUNTIME_INTERRUPTION_RECOVERY_RECONSTRUCTED",
        "inherited_B2C2A_verdict":
            "FAIL_CLOSED_NEGATIVE_UNATTRIBUTED_EFFECTIVE_RESIDUAL",
        "gates": {
            "central_response_max_abs_minus_one": central_response,
            "legacy_history_reproduction_relative_residual_max":
                legacy_reproduction,
            "legacy_byte_formula_relative_residual_max": byte_max,
            "canonical_operator_change_relative_max": max_change,
            "canonical_history_photon_ledger_relative_residual_max":
                ledger_max,
            "canonical_component_sum_relative_residual_max":
                component_sum_max,
            "direct_quadrature_vs_tabled_fit_relative_residual_max":
                direct_fit_max,
            "physical_component_nonnegative": len(negative) == 0,
            "material_negative_physical_component_count":
                int(len(negative)),
            "raw_Gamma_domain_pass": gamma_domain,
            "primary_G3_and_external_HeII_exact_zero": exact_g3,
            "cell_smallest_relative_difference_max": cell_max,
            "cell_observed_order_range": order_range,
            "history_endpoint_relative_difference_max": endpoint_max,
        },
        "operator_decomposition": {
            "normalization":
                "PUBLIC central-Gamma absolute anchor x raw dimensionless response",
            "group_shape_primary": "DIRECT_ENERGY_GROUP",
            "legacy_auditor":
                "LEGACY_DISCRETE_NODE_GROUP byte/formula reproduction",
            "residual_registry": "numerical_residual_registry.csv",
            "physical_unresolved_sink_interpretation": False,
        },
        "history_reconciliation": decision,
        "B2C2B_authorization":
            "AUTHORIZED" if passed else "DENIED",
        "forbidden_work_confirmed": [
            "unresolved sink subtraction",
            "front allocation",
            "source/f_esc calibration",
            "recombination implementation",
            "primitive geometry transplant",
            "Bianchi feedback",
        ],
    }
    (output.parent / "results.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--b2b-root", type=Path, required=True)
    parser.add_argument("--b2c1c-root", type=Path, required=True)
    parser.add_argument("--b2c2a-root", type=Path, required=True)
    parser.add_argument("--p04-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            execute(
                args.b2b_root,
                args.b2c1c_root,
                args.b2c2a_root,
                args.p04_root,
                args.output,
            ),
            indent=2,
        )
    )
