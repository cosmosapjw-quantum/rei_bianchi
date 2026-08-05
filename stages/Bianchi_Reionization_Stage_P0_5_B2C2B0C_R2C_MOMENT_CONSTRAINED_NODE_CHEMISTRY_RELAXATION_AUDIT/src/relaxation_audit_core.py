"""Core endpoint and refinement auditors for R2C.

This file deliberately separates the physics/reference map from repository I/O.
It operates on one macro's fixed micro-node support at a time.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from relaxation_operator import (  # noqa: E402
    K_B_ERG_PER_K,
    active_set_digest,
    advance_backward_euler,
    advance_exact,
    equilibrium_certificate,
    extensive_measures,
    infer_constant_equilibrium,
    project_currents,
    recover_intensives,
    to_builtin,
    total_variation_normalized,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))
from rei_bianchi.node_lift_operator import bernoulli_kl_mean_projection  # noqa: E402


@dataclass(frozen=True)
class InitialGlobalState:
    n_h_sink: float
    x_hii_sink: float
    temperature_sink_k: float
    z: float


@dataclass(frozen=True)
class NodeEndpoint:
    mass: np.ndarray
    x_hii: np.ndarray
    temperature_k: np.ndarray
    capacity: np.ndarray
    current: np.ndarray
    phi: np.ndarray
    n_h_cm3: np.ndarray
    p_mass: np.ndarray
    z: float
    construction_certificate: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        n = np.asarray(self.mass).size
        vectors = [self.x_hii, self.temperature_k, self.capacity, self.n_h_cm3, self.p_mass]
        if any(np.asarray(v).shape != (n,) for v in vectors):
            raise ValueError("all node vectors must have the same one-dimensional shape")
        if np.asarray(self.current).ndim != 2 or np.asarray(self.current).shape[0] != n:
            raise ValueError("current must be node-by-group")
        if np.asarray(self.phi).shape != (np.asarray(self.current).shape[1],):
            raise ValueError("phi must have one entry per active group")

    @property
    def ionized(self) -> np.ndarray:
        return np.asarray(self.mass, dtype=float) * np.asarray(self.x_hii, dtype=float)

    @property
    def thermal(self) -> np.ndarray:
        return (
            1.5
            * K_B_ERG_PER_K
            * np.asarray(self.mass, dtype=float)
            * np.asarray(self.temperature_k, dtype=float)
        )


@dataclass(frozen=True)
class NodeEquilibrium:
    mass: np.ndarray
    ionized: np.ndarray
    thermal: np.ndarray
    capacity: np.ndarray
    current: np.ndarray


def _project_initial_currents_blockwise(
    current: np.ndarray,
    capacity: np.ndarray,
    *,
    nodes_per_macro: int | None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Reconcile the constructed initial current with its scaled row capacity.

    Each block preserves its own active-group totals.  In the production stage
    a block is one inherited R2A/R2B macro, so no current or opacity moment is
    transported between macros.
    """
    prior = np.asarray(current, dtype=float)
    caps = np.asarray(capacity, dtype=float)
    if prior.ndim != 2 or caps.shape != (prior.shape[0],):
        raise ValueError("initial current/capacity shape mismatch")
    block = int(nodes_per_macro or prior.shape[0])
    if block <= 0 or prior.shape[0] % block:
        raise ValueError("nodes_per_macro must exactly divide the initial support")
    projected = np.empty_like(prior)
    block_certificates: list[dict[str, Any]] = []
    pre_slack = caps - np.sum(prior, axis=1)
    for start in range(0, prior.shape[0], block):
        stop = start + block
        totals = np.sum(prior[start:stop], axis=0)
        solution, cert = project_currents(prior[start:stop], totals, caps[start:stop])
        if solution is None:
            raise ValueError(
                "constructed initial current is blockwise infeasible without clipping: "
                f"block={start // block}, certificate={cert}"
            )
        projected[start:stop] = solution
        block_certificates.append({"block_index": start // block, **cert})
    post_slack = caps - np.sum(projected, axis=1)
    group_scale = np.maximum(np.abs(np.sum(prior, axis=0)), 1.0)
    group_residual = np.max(
        np.abs(np.sum(projected, axis=0) - np.sum(prior, axis=0)) / group_scale
    )
    scale = max(float(np.sum(np.abs(caps))), float(np.sum(np.abs(prior))), 1.0)
    certificate = {
        "pass": True,
        "projection_type": "BLOCKWISE_CONSTRAINED_KL_INITIAL_CURRENT",
        "block_count": len(block_certificates),
        "nodes_per_block": block,
        "preprojection_negative_row_count": int(np.count_nonzero(pre_slack < 0.0)),
        "postprojection_negative_row_count": int(np.count_nonzero(post_slack < -2.0e-11 * scale)),
        "minimum_preprojection_capacity_slack": float(np.min(pre_slack)),
        "minimum_postprojection_capacity_slack": float(np.min(post_slack)),
        "max_group_total_relative_residual": float(group_residual),
        "projection_generalized_kl_to_raw": float(
            sum(float(c.get("projection_generalized_kl_to_raw", 0.0)) for c in block_certificates)
        ),
        "maximum_block_capacity_relative_violation": float(
            max(float(c.get("max_capacity_relative_violation", 0.0)) for c in block_certificates)
        ),
        "clipping_used": False,
        "block_certificates": block_certificates,
    }
    return projected, to_builtin(certificate)


def construct_initial_endpoint(
    first: NodeEndpoint,
    initial: InitialGlobalState,
    *,
    nodes_per_macro: int | None = None,
) -> NodeEndpoint:
    """Construct the z-initial node state with minimum-information changes.

    The first R2B mass shape is retained exactly, the HII field is a Bernoulli
    I-projection to the locked initial global mean, and the thermal measure is
    rescaled to the locked initial H-weighted temperature.  Capacity follows
    the sink-mass scaling.  The inherited current/opacity moments are retained,
    but their node distribution is projected once per macro into the scaled
    row-capacity cone before time integration.
    """
    first_mass = np.asarray(first.mass, dtype=float)
    total = float(first_mass.sum())
    if total <= 0.0:
        raise ValueError("first endpoint has no positive H mass")
    mass = first_mass * (float(initial.n_h_sink) / total)
    x_hii, _ = bernoulli_kl_mean_projection(
        np.asarray(first.x_hii, dtype=float),
        mass,
        float(initial.x_hii_sink),
    )
    first_t = np.asarray(first.temperature_k, dtype=float)
    current_mean_t = float(np.dot(mass, first_t) / mass.sum())
    if current_mean_t <= 0.0:
        raise ValueError("first endpoint has nonpositive H-weighted temperature")
    temperature = first_t * (float(initial.temperature_sink_k) / current_mean_t)
    mass_ratio = float(initial.n_h_sink) / total
    capacity = np.asarray(first.capacity, dtype=float) * mass_ratio
    current, construction_certificate = _project_initial_currents_blockwise(
        np.asarray(first.current, dtype=float),
        capacity,
        nodes_per_macro=nodes_per_macro,
    )
    n_h = np.asarray(first.n_h_cm3, dtype=float) * (
        (1.0 + float(initial.z)) / (1.0 + float(first.z))
    ) ** 3
    p_mass = mass / float(mass.sum())
    return NodeEndpoint(
        mass=mass,
        x_hii=x_hii,
        temperature_k=temperature,
        capacity=capacity,
        current=current,
        phi=np.asarray(first.phi, dtype=float).copy(),
        n_h_cm3=n_h,
        p_mass=p_mass,
        z=float(initial.z),
        construction_certificate=construction_certificate,
    )


def infer_endpoint_equilibrium(
    previous: NodeEndpoint,
    target: NodeEndpoint,
    *,
    dt_myr: float,
    tau_myr: float,
    macro_mass_cap: float,
    macro_volume_cap: float,
) -> tuple[NodeEquilibrium, dict[str, Any]]:
    """Infer and certify the extensive constant equilibrium for one macro."""
    eq = NodeEquilibrium(
        mass=infer_constant_equilibrium(previous.mass, target.mass, dt_myr, tau_myr),
        ionized=infer_constant_equilibrium(previous.ionized, target.ionized, dt_myr, tau_myr),
        thermal=infer_constant_equilibrium(previous.thermal, target.thermal, dt_myr, tau_myr),
        capacity=infer_constant_equilibrium(previous.capacity, target.capacity, dt_myr, tau_myr),
        current=infer_constant_equilibrium(previous.current, target.current, dt_myr, tau_myr),
    )
    cert = equilibrium_certificate(
        eq.mass,
        eq.ionized,
        eq.thermal,
        eq.capacity,
        eq.current,
        macro_mass_cap=float(macro_mass_cap),
        macro_volume_cap=float(macro_volume_cap),
    )
    return eq, cert


def _l1_relative(value: np.ndarray, reference: np.ndarray) -> float:
    return float(
        np.sum(np.abs(np.asarray(value, dtype=float) - np.asarray(reference, dtype=float)))
        / max(float(np.sum(np.abs(reference))), 1.0)
    )


def _phi_at_fraction(phi0: np.ndarray, phi1: np.ndarray, fraction: float) -> np.ndarray:
    p0 = np.asarray(phi0, dtype=float)
    p1 = np.asarray(phi1, dtype=float)
    if np.any(p0 <= 0.0) or np.any(p1 <= 0.0):
        raise ValueError("current-Gamma flux must stay positive in active groups")
    return np.exp((1.0 - fraction) * np.log(p0) + fraction * np.log(p1))


def _physical_active_set(capacity: np.ndarray, current: np.ndarray) -> tuple[np.ndarray, float]:
    slack = np.asarray(capacity, dtype=float) - np.sum(np.asarray(current, dtype=float), axis=1)
    scale = max(float(np.sum(np.abs(capacity))), 1.0)
    active = np.flatnonzero(slack <= 1.0e-12 * scale).astype(np.int64)
    return active, float(np.min(slack))


def run_refinement(
    previous: NodeEndpoint,
    target: NodeEndpoint,
    equilibrium: NodeEquilibrium,
    *,
    dt_myr: float,
    tau_myr: float,
    refinement: int,
    interval_index: int,
    substep: int,
    macro_index: int,
    shape_lane: str,
) -> dict[str, Any]:
    """Run one backward-Euler/refinement family against the exact reference."""
    n = int(refinement)
    if n not in (1, 2, 4):
        raise ValueError("refinement must be one of 1,2,4")
    delta = float(dt_myr) / n
    m = np.asarray(previous.mass, dtype=float).copy()
    i = previous.ionized.copy()
    u = previous.thermal.copy()
    c = np.asarray(previous.capacity, dtype=float).copy()
    j = np.asarray(previous.current, dtype=float).copy()
    substeps: list[dict[str, Any]] = []
    passed = True
    failure_certificate: dict[str, Any] | None = None

    for k in range(1, n + 1):
        elapsed = k * delta
        fraction = elapsed / float(dt_myr)
        m = advance_backward_euler(m, equilibrium.mass, delta, tau_myr)
        i = advance_backward_euler(i, equilibrium.ionized, delta, tau_myr)
        u = advance_backward_euler(u, equilibrium.thermal, delta, tau_myr)
        c = advance_backward_euler(c, equilibrium.capacity, delta, tau_myr)
        j_raw = advance_backward_euler(j, equilibrium.current, delta, tau_myr)
        totals = np.sum(j_raw, axis=0)
        j_projected, projection = project_currents(j_raw, totals, c)
        if j_projected is None:
            passed = False
            failure_certificate = projection
            substeps.append(
                {
                    "shape_lane": shape_lane,
                    "interval_index": int(interval_index),
                    "substep": int(substep),
                    "macro_index": int(macro_index),
                    "tau_Myr": float(tau_myr),
                    "refinement": n,
                    "refined_substep": k,
                    "elapsed_Myr": elapsed,
                    "status": "FAIL_CLOSED_PROJECTION_INFEASIBLE",
                    "projection_certificate": projection,
                }
            )
            break
        j = j_projected

        m_ref = advance_exact(previous.mass, equilibrium.mass, elapsed, tau_myr)
        i_ref = advance_exact(previous.ionized, equilibrium.ionized, elapsed, tau_myr)
        u_ref = advance_exact(previous.thermal, equilibrium.thermal, elapsed, tau_myr)
        c_ref = advance_exact(previous.capacity, equilibrium.capacity, elapsed, tau_myr)
        j_ref_raw = advance_exact(previous.current, equilibrium.current, elapsed, tau_myr)
        j_ref, ref_projection = project_currents(j_ref_raw, np.sum(j_ref_raw, axis=0), c_ref)
        if j_ref is None:
            passed = False
            failure_certificate = {
                "certificate_type": "EXACT_REFERENCE_PROJECTION_INFEASIBLE",
                "nested": ref_projection,
                "clipping_used": False,
            }
            substeps.append(
                {
                    "shape_lane": shape_lane,
                    "interval_index": int(interval_index),
                    "substep": int(substep),
                    "macro_index": int(macro_index),
                    "tau_Myr": float(tau_myr),
                    "refinement": n,
                    "refined_substep": k,
                    "elapsed_Myr": elapsed,
                    "status": "FAIL_CLOSED_EXACT_REFERENCE_INFEASIBLE",
                    "projection_certificate": failure_certificate,
                }
            )
            break

        x, temperature = recover_intensives(m, i, u)
        phi = _phi_at_fraction(previous.phi, target.phi, fraction)
        kappa = np.divide(j, phi[None, :])
        exact_x, exact_temperature = recover_intensives(m_ref, i_ref, u_ref)
        active, min_slack = _physical_active_set(c, j)
        h_total = float(np.sum(m))
        h_ionized = float(np.sum(i))
        h_neutral = h_total - h_ionized
        errors = {
            "mass_l1_relative": _l1_relative(m, m_ref),
            "ionized_l1_relative": _l1_relative(i, i_ref),
            "thermal_l1_relative": _l1_relative(u, u_ref),
            "capacity_l1_relative": _l1_relative(c, c_ref),
            "current_l1_relative": _l1_relative(j, j_ref),
            "temperature_mass_weighted_relative": abs(
                float(np.dot(m, temperature) / max(np.sum(m), 1.0))
                - float(np.dot(m_ref, exact_temperature) / max(np.sum(m_ref), 1.0))
            )
            / max(abs(float(np.dot(m_ref, exact_temperature) / max(np.sum(m_ref), 1.0))), 1.0),
        }
        substeps.append(
            to_builtin(
                {
                    "shape_lane": shape_lane,
                    "interval_index": int(interval_index),
                    "substep": int(substep),
                    "macro_index": int(macro_index),
                    "tau_Myr": float(tau_myr),
                    "refinement": n,
                    "refined_substep": k,
                    "elapsed_Myr": elapsed,
                    "status": "PASS",
                    "errors_to_exact_reference": errors,
                    "projection": projection,
                    "exact_reference_projection": ref_projection,
                    "physical_active_capacity_count": int(active.size),
                    "physical_active_capacity_sha256": active_set_digest(active),
                    "minimum_capacity_slack": min_slack,
                    "H_nuclei_total": h_total,
                    "HII_nuclei_total": h_ionized,
                    "HI_nuclei_total": h_neutral,
                    "H_nuclei_identity_residual": h_total - h_ionized - h_neutral,
                    "thermal_measure_erg_cMpc3": float(np.sum(u)),
                    "temperature_min_K": float(np.nanmin(temperature)),
                    "temperature_max_K": float(np.nanmax(temperature)),
                    "current_G1_total": float(np.sum(j[:, 0])),
                    "current_G2a_total": float(np.sum(j[:, 1])),
                    "capacity_total": float(np.sum(c)),
                    "kappa_G1_total": float(np.sum(kappa[:, 0])),
                    "kappa_G2a_total": float(np.sum(kappa[:, 1])),
                    "phi_G1": float(phi[0]),
                    "phi_G2a": float(phi[1]),
                    "current_Gamma_residual_max": float(
                        np.max(np.abs(kappa * phi[None, :] - j))
                        / max(float(np.max(np.abs(j))), 1.0)
                    ),
                    "current_TV_to_exact_G1": total_variation_normalized(j[:, 0], j_ref[:, 0]),
                    "current_TV_to_exact_G2a": total_variation_normalized(j[:, 1], j_ref[:, 1]),
                    "xHII_min": float(np.nanmin(x)),
                    "xHII_max": float(np.nanmax(x)),
                }
            )
        )

    final_errors: dict[str, float]
    if passed:
        phi_final = np.asarray(target.phi, dtype=float)
        kappa_final = np.divide(j, phi_final[None, :])
        target_kappa = np.divide(target.current, phi_final[None, :])
        final_errors = {
            "mass_l1_relative": _l1_relative(m, target.mass),
            "ionized_l1_relative": _l1_relative(i, target.ionized),
            "thermal_l1_relative": _l1_relative(u, target.thermal),
            "capacity_l1_relative": _l1_relative(c, target.capacity),
            "current_l1_relative": _l1_relative(j, target.current),
            "opacity_l1_relative": _l1_relative(kappa_final, target_kappa),
        }
        final_errors["combined_extensive_l1_relative"] = max(
            final_errors["mass_l1_relative"],
            final_errors["ionized_l1_relative"],
            final_errors["thermal_l1_relative"],
            final_errors["capacity_l1_relative"],
            final_errors["current_l1_relative"],
        )
    else:
        final_errors = {
            "mass_l1_relative": math.nan,
            "ionized_l1_relative": math.nan,
            "thermal_l1_relative": math.nan,
            "capacity_l1_relative": math.nan,
            "current_l1_relative": math.nan,
            "opacity_l1_relative": math.nan,
            "combined_extensive_l1_relative": math.nan,
        }
    return to_builtin(
        {
            "pass": passed,
            "substeps": substeps,
            "final_errors": final_errors,
            "failure_certificate": failure_certificate,
        }
    )
