"""New bounded P/Q-completion algebra fixture; no dynamics integration."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time

import numpy as np

ATOL = 2.0e-12
RTOL = 0.0
SEED = 20261001
HBAR_FIXTURE = 0.7  # Arbitrary consistent fixture units, not a physical-constant estimate.


def atomic_create(path, data):
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    try:
        with temporary.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def main():
    source = Path(__file__).resolve()
    evidence = source.parent.parent / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    result_path = evidence / "PQ_COMPLETION_CHECK.json"
    log_path = evidence / "PQ_COMPLETION_CHECK_LOG.txt"
    if result_path.exists() or log_path.exists():
        raise SystemExit("Refusing to overwrite P/Q-completion evidence")
    started = datetime.now(timezone.utc).isoformat()
    tic = time.perf_counter()
    rng = np.random.default_rng(SEED)

    def random_complex(shape):
        return rng.standard_normal(shape) + 1j * rng.standard_normal(shape)

    unitary, _ = np.linalg.qr(random_complex((8, 8)))
    y, z = unitary[:, :6], unitary[:, 6:]
    raw_a = random_complex((6, 6))
    connection_a = (raw_a - raw_a.conj().T) / 2
    connection_b = random_complex((2, 6))
    dot_y = y @ connection_a + z @ connection_b
    projector_p = y @ y.conj().T
    projector_q = np.eye(8) - projector_p
    dot_p = dot_y @ y.conj().T + y @ dot_y.conj().T
    gamma = dot_p @ projector_p - projector_p @ dot_p + y @ connection_a @ y.conj().T
    dot_z = -y @ connection_b.conj().T
    joint = np.column_stack((y, z))
    dot_joint = np.column_stack((dot_y, dot_z))
    raw_h = random_complex((8, 8))
    hamiltonian = (raw_h + raw_h.conj().T) / 2
    effective = joint.conj().T @ hamiltonian @ joint - 1j * HBAR_FIXTURE * joint.conj().T @ gamma @ joint
    k_pp, k_pq = effective[:6, :6], effective[:6, 6:]
    k_qp, k_qq = effective[6:, :6], effective[6:, 6:]
    a, b = random_complex((6,)), random_complex((2,))
    amplitudes = np.r_[a, b]
    dot_amplitudes = -1j * effective @ amplitudes / HBAR_FIXTURE
    p_norm_derivative = float(2 * np.vdot(a, dot_amplitudes[:6]).real)
    q_norm_derivative = float(2 * np.vdot(b, dot_amplitudes[6:]).real)
    exchange_p = float(2 * np.vdot(a, k_pq @ b).imag / HBAR_FIXTURE)
    exchange_q = float(2 * np.vdot(b, k_qp @ a).imag / HBAR_FIXTURE)

    def maximum_absolute(value):
        return float(np.max(np.abs(np.asarray(value))))

    residuals = {
        "joint_basis_orthonormal": maximum_absolute(joint.conj().T @ joint - np.eye(8)),
        "projector_idempotence": maximum_absolute(projector_p @ projector_p - projector_p),
        "gamma_antihermitian": maximum_absolute(gamma.conj().T + gamma),
        "gamma_y_equals_dot_y": maximum_absolute(gamma @ y - dot_y),
        "q_gamma_q_zero": maximum_absolute(projector_q @ gamma @ projector_q),
        "gamma_z_equals_minus_y_bdagger": maximum_absolute(gamma @ z - dot_z),
        "joint_derivative_equals_gamma_joint": maximum_absolute(dot_joint - gamma @ joint),
        "effective_hamiltonian_hermitian": maximum_absolute(effective - effective.conj().T),
        "k_qp_projected_residual": maximum_absolute(k_qp - z.conj().T @ (hamiltonian @ y - 1j * HBAR_FIXTURE * dot_y)),
        "k_pq_adjoint_of_k_qp": maximum_absolute(k_pq - k_qp.conj().T),
        "k_qq_no_internal_connection": maximum_absolute(k_qq - z.conj().T @ hamiltonian @ z),
        "p_block_norm_exchange": maximum_absolute(p_norm_derivative - exchange_p),
        "q_block_norm_exchange": maximum_absolute(q_norm_derivative - exchange_q),
        "opposite_cross_block_exchange": maximum_absolute(exchange_p + exchange_q),
        "total_norm_derivative_zero": maximum_absolute(p_norm_derivative + q_norm_derivative),
    }
    finite = all(np.isfinite(value) for value in residuals.values())
    maximum_residual = max(residuals.values())
    passed = finite and maximum_residual <= ATOL
    exit_code = 0 if passed else 1
    lines = [
        "Scope: one new P/Q-completion algebra fixture; no ODE, exponential, or physical propagation.",
        f"seed={SEED}; ambient=8; P_rank=6; Q_rank=2; hbar_fixture={HBAR_FIXTURE}",
        f"absolute_tolerance={ATOL}; relative_tolerance={RTOL}",
        *[f"{name}: {value:.17g}" for name, value in residuals.items()],
        f"p_norm_derivative: {p_norm_derivative:.17g}",
        f"q_norm_derivative: {q_norm_derivative:.17g}",
        f"max_absolute_residual: {maximum_residual:.17g}",
        f"status={'PASS' if passed else 'FAIL'}; exit_code={exit_code}",
    ]
    log_bytes = ("\n".join(lines) + "\n").encode()
    atomic_create(log_path, log_bytes)
    record = {
        "scope": "NEW_A1B_EXACT_P_Q_EXTENSION_ALGEBRA_FIXTURE",
        "status": "PASS" if passed else "FAIL",
        "exit_code": exit_code,
        "command": [sys.executable, "-B", str(source)],
        "cwd": str(Path.cwd()),
        "started_at_utc": started,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "wall_seconds": time.perf_counter() - tic,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "random_seed": SEED,
        "fixture_dimensions": {"ambient": 8, "P": 6, "Q": 2},
        "hbar_fixture": HBAR_FIXTURE,
        "hbar_interpretation": "arbitrary consistent fixture units; not a measured physical constant",
        "absolute_tolerance": ATOL,
        "relative_tolerance": RTOL,
        "residuals": residuals,
        "all_residuals_finite": finite,
        "maximum_absolute_residual": maximum_residual,
        "p_norm_derivative": p_norm_derivative,
        "q_norm_derivative": q_norm_derivative,
        "source_identity": {"path": source.name, "bytes": source.stat().st_size, "sha256": hashlib.sha256(source.read_bytes()).hexdigest()},
        "log_identity": {"path": log_path.name, "bytes": len(log_bytes), "sha256": hashlib.sha256(log_bytes).hexdigest()},
        "existing_tests_rerun": False,
        "physical_propagation_executed": False,
        "ode_or_exponential_executed": False,
        "claim_ceiling": "instantaneous finite-dimensional coherent P/Q block algebra and norm exchange, not physical collision convergence",
    }
    atomic_create(result_path, (json.dumps(record, indent=2, allow_nan=False) + "\n").encode())
    print(log_bytes.decode(), end="")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
