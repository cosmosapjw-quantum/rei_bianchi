#!/usr/bin/env python3
"""Hybrid batched Newton/continuation solver for one positive material microstep."""
from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import math
from pathlib import Path
import sys
from typing import Any

import jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np
from scipy.optimize import least_squares


def _load_sibling(stem: str):
    name = f"r2b_r2_{stem}"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(f"{stem}.py"))
    if spec is None or spec.loader is None:
        raise ImportError(stem)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


micro = _load_sibling("microphysics")


@dataclass(frozen=True)
class ImplicitContext:
    params: np.ndarray
    parent_coordinates: np.ndarray
    N_H: np.ndarray
    N_He: np.ndarray


@dataclass(frozen=True)
class ImplicitResult:
    state: Any | None
    converged: np.ndarray
    residual_norm: np.ndarray
    iterations: np.ndarray
    certificates: list[dict[str, Any]]

    @property
    def max_residual(self) -> float:
        finite = self.residual_norm[np.isfinite(self.residual_norm)]
        return float(np.max(finite)) if finite.size else math.inf


def _residual_single(q: Any, p: Any) -> Any:
    # p: parent fractions/U, nuclei, volume, photo rates/heat, Hubble, dt, U scale.
    xh0, xheii0, xheiii0, U0, nh, nhe, volume, ph, phei, pheii, heat, hubble, dt, uscale = p
    nhi, nhii, nhei, nheii, nheiii, U, _T = micro._decode_jax(q, nh, nhe)
    dpop = micro._population_rhs_single(q, nh, nhe, volume, ph, phei, pheii)
    dU = micro._thermal_rhs_single(q, nh, nhe, volume, heat, hubble)
    return jnp.array(
        [
            nhii / nh - xh0 - dt * dpop[1] / nh,
            nheii / nhe - xheii0 - dt * dpop[3] / nhe,
            nheiii / nhe - xheiii0 - dt * dpop[4] / nhe,
            (U - U0 - dt * dU) / uscale,
        ],
        dtype=q.dtype,
    )


_batch_residual = jax.jit(jax.vmap(_residual_single, in_axes=(0,0)))
_batch_jacobian = jax.jit(jax.vmap(jax.jacfwd(_residual_single, argnums=0), in_axes=(0,0)))
_scalar_residual_jit = jax.jit(_residual_single)
_scalar_jacobian_jit = jax.jit(jax.jacfwd(_residual_single, argnums=0))


def make_context(
    *,
    parent: Any,
    proper_volume_cm3: np.ndarray,
    photo: Any,
    redshift: float,
    hubble_s_inv: float,
    dt_seconds: float,
) -> ImplicitContext:
    del redshift  # rates require only the proper volume and Hubble at this stage.
    size = parent.size
    photo.validate(size)
    volume = np.asarray(proper_volume_cm3, dtype=float)
    if volume.shape != (size,) or np.any(~np.isfinite(volume)) or np.any(volume <= 0.0):
        raise ValueError("proper volume must be finite and positive")
    dt = float(dt_seconds)
    H = float(hubble_s_inv)
    if not math.isfinite(dt) or dt < 0.0 or not math.isfinite(H) or H < 0.0:
        raise ValueError("invalid duration or Hubble rate")
    nh, nhe = np.asarray(parent.N_H), np.asarray(parent.N_He)
    xh0 = np.asarray(parent.N_HII) / nh
    xheii0 = np.asarray(parent.N_HeII) / nhe
    xheiii0 = np.asarray(parent.N_HeIII) / nhe
    U0 = np.asarray(parent.U_resolved)
    uscale = np.maximum.reduce(
        [np.abs(U0), np.abs(dt * np.asarray(photo.heating_erg_s)), np.full(size, 1e-300)]
    )
    params = np.column_stack(
        [
            xh0, xheii0, xheiii0, U0, nh, nhe, volume,
            np.asarray(photo.HI), np.asarray(photo.HeI), np.asarray(photo.HeII),
            np.asarray(photo.heating_erg_s), np.full(size, H), np.full(size, dt), uscale,
        ]
    )
    return ImplicitContext(
        params=params,
        parent_coordinates=micro.state_to_coordinates(parent),
        N_H=nh,
        N_He=nhe,
    )


def scalar_residual(q: np.ndarray, context: ImplicitContext, *, index: int) -> np.ndarray:
    return np.asarray(_scalar_residual_jit(jnp.asarray(q), jnp.asarray(context.params[int(index)])))


def scalar_jacobian(q: np.ndarray, context: ImplicitContext, *, index: int) -> np.ndarray:
    return np.asarray(_scalar_jacobian_jit(jnp.asarray(q), jnp.asarray(context.params[int(index)])))


def _norm(residual: np.ndarray) -> np.ndarray:
    return np.max(np.abs(residual), axis=1)


def _batched_newton(
    q0: np.ndarray,
    params: np.ndarray,
    *,
    tolerance: float,
    max_iterations: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    q = np.asarray(q0, dtype=float).copy()
    n = len(q)
    iterations = np.zeros(n, dtype=int)
    converged = np.zeros(n, dtype=bool)
    residual_norm = np.full(n, math.inf)
    alphas = (1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625)
    for _ in range(int(max_iterations)):
        residual = np.asarray(_batch_residual(jnp.asarray(q), jnp.asarray(params)))
        residual_norm = _norm(residual)
        finite = np.all(np.isfinite(residual), axis=1)
        newly = finite & (residual_norm <= tolerance)
        converged |= newly
        active = finite & ~converged
        if not np.any(active):
            break
        idx = np.flatnonzero(active)
        jac = np.asarray(_batch_jacobian(jnp.asarray(q[idx]), jnp.asarray(params[idx])))
        try:
            delta = np.linalg.solve(jac, (-residual[idx])[..., None])[..., 0]
        except np.linalg.LinAlgError:
            delta = np.stack([np.linalg.lstsq(a, -b, rcond=None)[0] for a, b in zip(jac, residual[idx])])
        # Numerical trust region in unconstrained coordinates; physical states
        # remain strictly positive through the transform and are never clipped.
        delta = np.clip(delta, -4.0, 4.0)
        best_q = q[idx].copy()
        best_norm = residual_norm[idx].copy()
        accepted = np.zeros(len(idx), dtype=bool)
        for alpha in alphas:
            trial = q[idx] + alpha * delta
            rtrial = np.asarray(_batch_residual(jnp.asarray(trial), jnp.asarray(params[idx])))
            ntrial = _norm(rtrial)
            improve = np.isfinite(ntrial) & (ntrial < best_norm)
            best_q[improve] = trial[improve]
            best_norm[improve] = ntrial[improve]
            accepted |= improve
        q[idx] = best_q
        iterations[idx] += 1
        # A stalled node is left for continuation/trust-region fallback.
        if not np.any(accepted):
            break
    residual = np.asarray(_batch_residual(jnp.asarray(q), jnp.asarray(params)))
    residual_norm = _norm(residual)
    converged = np.all(np.isfinite(residual), axis=1) & (residual_norm <= tolerance)
    return q, converged, residual_norm, iterations


def _fallback_one(
    q_parent: np.ndarray,
    q_seed: np.ndarray,
    param: np.ndarray,
    *,
    tolerance: float,
) -> tuple[np.ndarray, bool, float, int]:
    target_dt = float(param[12])
    q = np.asarray(q_seed, dtype=float)
    total_nfev = 0
    # Timestep homotopy avoids asking the nonlinear solver to cross a stiff
    # ionization front in one trust-region step.
    for lam in (1/16, 1/8, 1/4, 1/2, 1.0):
        pp = np.asarray(param, dtype=float).copy()
        pp[12] = target_dt * lam
        pp[13] = max(abs(pp[3]), abs(pp[12] * pp[10]), 1e-300)
        fun = lambda x: np.asarray(_scalar_residual_jit(jnp.asarray(x), jnp.asarray(pp)))
        jac = lambda x: np.asarray(_scalar_jacobian_jit(jnp.asarray(x), jnp.asarray(pp)))
        result = least_squares(
            fun,
            q,
            jac=jac,
            method="trf",
            xtol=1e-12,
            ftol=1e-12,
            gtol=1e-12,
            max_nfev=120,
            x_scale="jac",
        )
        total_nfev += int(result.nfev)
        q = np.asarray(result.x)
        norm = float(np.max(np.abs(fun(q))))
        if not np.isfinite(norm) or norm > max(tolerance, 1e-10):
            # Retry this continuation point from the exact parent coordinate.
            result2 = least_squares(
                fun,
                np.asarray(q_parent),
                jac=jac,
                method="trf",
                xtol=1e-13,
                ftol=1e-13,
                gtol=1e-13,
                max_nfev=240,
                x_scale="jac",
            )
            total_nfev += int(result2.nfev)
            q = np.asarray(result2.x)
            norm = float(np.max(np.abs(fun(q))))
        if not np.isfinite(norm) or norm > max(tolerance, 1e-10):
            return q, False, norm, total_nfev
    final_norm = float(np.max(np.abs(_scalar_residual_jit(jnp.asarray(q), jnp.asarray(param)))))
    return q, bool(np.isfinite(final_norm) and final_norm <= tolerance), final_norm, total_nfev


def solve_implicit_batch(
    *,
    parent: Any,
    proper_volume_cm3: np.ndarray,
    photo: Any,
    redshift: float,
    hubble_s_inv: float,
    dt_seconds: float,
    tolerance: float = 1e-10,
    max_newton_iterations: int = 20,
    enable_fallback: bool = True,
) -> ImplicitResult:
    context = make_context(
        parent=parent,
        proper_volume_cm3=proper_volume_cm3,
        photo=photo,
        redshift=redshift,
        hubble_s_inv=hubble_s_inv,
        dt_seconds=dt_seconds,
    )
    n = parent.size
    if float(dt_seconds) == 0.0:
        return ImplicitResult(
            state=parent,
            converged=np.ones(n, dtype=bool),
            residual_norm=np.zeros(n),
            iterations=np.zeros(n, dtype=int),
            certificates=[{} for _ in range(n)],
        )
    q, conv, norms, iters = _batched_newton(
        context.parent_coordinates,
        context.params,
        tolerance=tolerance,
        max_iterations=max_newton_iterations,
    )
    certificates: list[dict[str, Any]] = [{} for _ in range(n)]
    if enable_fallback and np.any(~conv):
        for i in np.flatnonzero(~conv):
            qi, ok, norm, nfev = _fallback_one(
                context.parent_coordinates[i], q[i], context.params[i], tolerance=tolerance
            )
            q[i], conv[i], norms[i] = qi, ok, norm
            iters[i] += nfev
    for i in np.flatnonzero(~conv):
        certificates[int(i)] = {
            "classification": "NONFINITE_RESIDUAL" if not np.isfinite(norms[i]) else "NEWTON_NONCONVERGENCE",
            "node_index": int(i),
            "residual": float(norms[i]),
            "iterations": int(iters[i]),
            "clipping_used": False,
        }
    state = micro.coordinates_to_state(q, N_H=context.N_H, N_He=context.N_He)
    return ImplicitResult(
        state=state,
        converged=conv,
        residual_norm=norms,
        iterations=iters,
        certificates=certificates,
    )
