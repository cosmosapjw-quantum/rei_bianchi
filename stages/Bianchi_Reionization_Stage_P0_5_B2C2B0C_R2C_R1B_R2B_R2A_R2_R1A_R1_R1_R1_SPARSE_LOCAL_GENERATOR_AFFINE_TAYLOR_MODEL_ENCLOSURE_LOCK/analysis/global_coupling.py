"""Low-rank global coupling contract for the owner and node-allocation law.

The material branch parameters remain node-local.  Only two normalization
operations communicate between nodes:

* global owner amplitudes depend on three scalar material moments; and
* each supported owner/group node allocation has one scalar support sum.

The Jacobian of ``q_i=h_i/sum_j h_j`` is a local diagonal action plus one
rank-one nonlocal mode.  No dense node-by-node matrix is required.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import importlib.util
import sys
from pathlib import Path

import numpy as np

GROUPS = ("G1", "G2a", "G2b", "G3")
OWNERS = (
    "EFFECTIVE_HI_SUBGRID",
    "EXPLICIT_HI_ATOMIC",
    "EXPLICIT_HEI_ATOMIC",
    "EXPLICIT_HEII_ATOMIC",
)
MPC_CM = 3.085677581491367e24
NH0_CM3 = 1.88e-7
YHE = 0.079


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _vector(value, *, name: str) -> np.ndarray:
    out = np.ascontiguousarray(np.asarray(value, dtype=np.float64))
    if out.ndim != 1 or not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be a finite vector")
    return out


def normalized_measure_jvp(measure: np.ndarray, perturbation: np.ndarray) -> np.ndarray:
    """Exact derivative of ``measure / sum(measure)`` in one direction."""

    local, nonlocal_mode = normalized_measure_jvp_decomposition(measure, perturbation)
    return np.ascontiguousarray(local + nonlocal_mode)


def normalized_measure_jvp_decomposition(
    measure: np.ndarray, perturbation: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Return local diagonal and one rank-one normalization contributions."""

    h = _vector(measure, name="measure")
    dh = _vector(perturbation, name="perturbation")
    if h.shape != dh.shape:
        raise ValueError("measure and perturbation shapes differ")
    if np.any(h < 0.0):
        raise ValueError("measure must be nonnegative")
    support = float(np.sum(h, dtype=np.float64))
    if not support > 0.0:
        raise ValueError("normalization support must be positive")
    q = h / support
    local = dh / support
    nonlocal_mode = -q * (float(np.sum(dh, dtype=np.float64)) / support)
    return np.ascontiguousarray(local), np.ascontiguousarray(nonlocal_mode)


def _raw_owner_response(
    *,
    moments: np.ndarray,
    z: float,
    external_subgrid: np.ndarray,
    sigma_cm2: np.ndarray,
    support: np.ndarray,
) -> np.ndarray:
    x_hii, x_hei, x_heii_per_h = map(float, moments)
    a = 1.0 / (1.0 + float(z))
    n_h_phys = NH0_CM3 * (1.0 + float(z)) ** 3
    n_he_phys = YHE * n_h_phys
    raw = np.zeros((4, 4), dtype=np.float64)
    raw[0] = np.asarray(external_subgrid, dtype=np.float64)
    for gi in range(4):
        if support[1, gi]:
            raw[1, gi] = a * n_h_phys * (1.0 - x_hii) * sigma_cm2[0, gi] * MPC_CM
        if support[2, gi]:
            raw[2, gi] = a * n_he_phys * x_hei * sigma_cm2[1, gi] * MPC_CM
        if support[3, gi]:
            raw[3, gi] = a * n_he_phys * x_heii_per_h * sigma_cm2[2, gi] * MPC_CM
    return np.ascontiguousarray(raw * support)


def _raw_owner_derivatives(
    *, z: float, sigma_cm2: np.ndarray, support: np.ndarray
) -> np.ndarray:
    """Derivative of raw owner responses w.r.t. the three global moments."""

    a = 1.0 / (1.0 + float(z))
    n_h_phys = NH0_CM3 * (1.0 + float(z)) ** 3
    n_he_phys = YHE * n_h_phys
    deriv = np.zeros((3, 4, 4), dtype=np.float64)
    deriv[0, 1] = -a * n_h_phys * sigma_cm2[0] * MPC_CM
    deriv[1, 2] = a * n_he_phys * sigma_cm2[1] * MPC_CM
    deriv[2, 3] = a * n_he_phys * sigma_cm2[2] * MPC_CM
    return np.ascontiguousarray(deriv * support[None, :, :])


def _conditioned_fraction(raw: np.ndarray) -> np.ndarray:
    values = np.asarray(raw, dtype=np.float64)
    out = np.zeros_like(values)
    for gi in range(values.shape[1]):
        total = float(np.sum(values[:, gi], dtype=np.float64))
        if total > 0.0:
            out[:, gi] = values[:, gi] / total
    return np.ascontiguousarray(out)


def _conditioned_fraction_jacobian(raw: np.ndarray, draw: np.ndarray) -> np.ndarray:
    values = np.asarray(raw, dtype=np.float64)
    derivatives = np.asarray(draw, dtype=np.float64)
    jac = np.zeros_like(derivatives)
    for parameter in range(derivatives.shape[0]):
        for gi in range(values.shape[1]):
            support_sum = float(np.sum(values[:, gi], dtype=np.float64))
            if support_sum <= 0.0:
                continue
            ds = float(np.sum(derivatives[parameter, :, gi], dtype=np.float64))
            jac[parameter, :, gi] = (
                derivatives[parameter, :, gi] / support_sum
                - values[:, gi] * ds / support_sum**2
            )
    return np.ascontiguousarray(jac)


@dataclass(frozen=True)
class GlobalCouplingAudit:
    owner_amplitude_moment_names: tuple[str, ...]
    owner_amplitude_jacobian_rank: int
    owner_amplitude_rank_upper_bound: int
    maximum_owner_jacobian_relative_residual: float
    normalization_channel_names: tuple[str, ...]
    normalization_channel_count: int
    global_rank_upper_bound: int
    source_safe_local_rank_lower_bound: int
    global_to_local_rank_ratio: float
    dense_global_matrix_required: bool
    owner_support_matrix: tuple[tuple[int, ...], ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def audit_global_coupling(repo_root: Path) -> GlobalCouplingAudit:
    repo = Path(repo_root).resolve()
    stage = Path(__file__).resolve().parents[1]
    tensor_stage = next(repo.glob("stages/*R2A_ADAPTIVE_INTERNAL_MICROSTEP*"))
    tensor = _load("sparse_global_tensorized", tensor_stage / "analysis/tensorized_inputs.py")
    inputs = tensor.load_tensorized_inputs(repo_root=repo)
    state = inputs.state0
    y = state.values
    n_h = float(np.sum(y[0] + y[1], dtype=np.float64))
    n_he = float(np.sum(y[2] + y[3] + y[4], dtype=np.float64))
    moments = np.asarray(
        [
            float(np.sum(y[1], dtype=np.float64)) / n_h,
            float(np.sum(y[2], dtype=np.float64)) / n_he,
            float(np.sum(y[3], dtype=np.float64)) / n_h,
        ],
        dtype=np.float64,
    )
    z = float(inputs.z_mid[0, 0])
    support = np.asarray(inputs.owner_support, dtype=np.float64)
    raw = _raw_owner_response(
        moments=moments,
        z=z,
        external_subgrid=inputs.external_subgrid[0, 0],
        sigma_cm2=inputs.sigma_cm2,
        support=support,
    )
    draw = _raw_owner_derivatives(z=z, sigma_cm2=inputs.sigma_cm2, support=support)
    analytic = _conditioned_fraction_jacobian(raw, draw).reshape(3, -1).T

    finite = np.empty_like(analytic)
    eps = 1.0e-8
    for parameter in range(3):
        plus = moments.copy()
        minus = moments.copy()
        plus[parameter] += eps
        minus[parameter] -= eps
        q_plus = _conditioned_fraction(
            _raw_owner_response(
                moments=plus,
                z=z,
                external_subgrid=inputs.external_subgrid[0, 0],
                sigma_cm2=inputs.sigma_cm2,
                support=support,
            )
        )
        q_minus = _conditioned_fraction(
            _raw_owner_response(
                moments=minus,
                z=z,
                external_subgrid=inputs.external_subgrid[0, 0],
                sigma_cm2=inputs.sigma_cm2,
                support=support,
            )
        )
        finite[:, parameter] = ((q_plus - q_minus) / (2.0 * eps)).reshape(-1)
    residual = float(
        np.max(np.abs(finite - analytic))
        / max(float(np.max(np.abs(analytic))), np.finfo(float).tiny)
    )
    scale = max(float(np.linalg.norm(analytic, ord=2)), np.finfo(float).tiny)
    rank = int(np.linalg.matrix_rank(analytic, tol=1.0e-12 * scale))

    channels = tuple(
        f"{OWNERS[oi]}:{GROUPS[gi]}"
        for oi in range(4)
        for gi in range(4)
        if bool(inputs.owner_support[oi, gi])
    )
    source = _load("sparse_global_source_generators", stage / "analysis/source_generators.py")
    local_rank = int(source.build_source_rhs_taylor(repo).rank_lower_bound)
    global_upper = 3 + len(channels)
    return GlobalCouplingAudit(
        owner_amplitude_moment_names=(
            "global_x_HII",
            "global_x_HeI",
            "global_x_HeII_per_H",
        ),
        owner_amplitude_jacobian_rank=rank,
        owner_amplitude_rank_upper_bound=3,
        maximum_owner_jacobian_relative_residual=residual,
        normalization_channel_names=channels,
        normalization_channel_count=len(channels),
        global_rank_upper_bound=global_upper,
        source_safe_local_rank_lower_bound=local_rank,
        global_to_local_rank_ratio=float(global_upper / local_rank),
        dense_global_matrix_required=False,
        owner_support_matrix=tuple(tuple(int(v) for v in row) for row in inputs.owner_support),
    )


__all__ = [
    "GlobalCouplingAudit",
    "audit_global_coupling",
    "normalized_measure_jvp",
    "normalized_measure_jvp_decomposition",
]
