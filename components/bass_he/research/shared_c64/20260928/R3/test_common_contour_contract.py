import numpy as np
import pytest

from common_contour_contract import (
    kernel_disk_certificate,
    total_error_budget,
    hybrid_pruning_bound,
)


def event_matrix(dim, p, event):
    i, j, sink = event
    T = np.eye(dim)
    T[i, i] = 1 - p
    T[j, i] = p
    if not sink:
        T[i, j] = p
        T[j, j] = 1 - p
    return T


def observable_difference(p, q, events, y0, w):
    yt = np.asarray(y0, float)
    yq = np.asarray(y0, float)
    for pe, qe, ev in zip(p, q, events):
        yt = event_matrix(len(y0), pe, ev) @ yt
        yq = event_matrix(len(y0), qe, ev) @ yq
    return float(np.asarray(w, float) @ (yt - yq))


def test_kernel_disk_radius_is_nearest_rho_plane_singularity():
    R = np.array([3 + 4j, 2 + 0.5j, 4 + 1j])
    c = kernel_disk_certificate(R, rho_max=1.5)
    assert c['status'] == 'CERTIFIED_OPEN_DISK'
    assert c['r_star'] == pytest.approx(abs(2 + 0.5j))
    assert c['q_max'] == pytest.approx((1.5 / abs(2 + 0.5j)) ** 2)
    assert c['claim'] == 'EXACT_TAYLOR_GERM_RADIUS_NOT_MAXIMAL_REAL_RHO_INTERVAL'


def test_kernel_disk_fails_closed_at_boundary():
    R = np.array([2 + 0j, 3 + 1j])
    with pytest.raises(ValueError, match='rho_max must satisfy'):
        kernel_disk_certificate(R, rho_max=2.0)


def test_total_error_budget_requires_homotopy_authority():
    with pytest.raises(RuntimeError, match='homotopy'):
        total_error_budget(
            spectral=1e-6, quadrature=2e-6, interpolation=3e-6,
            roundoff=4e-12, homotopy_certified=False,
        )
    r = total_error_budget(
        spectral=1e-6, quadrature=2e-6, interpolation=3e-6,
        roundoff=4e-12, homotopy_certified=True,
    )
    assert r['total'] == pytest.approx(6.000004e-6)
    assert r['status'] == 'NUMERICAL_COMPONENTS_COMPOSED_HOMOTOPY_SEPARATELY_CERTIFIED'


def test_a_priori_hybrid_pruning_bound_covers_random_true_chains():
    rng = np.random.default_rng(20260928)
    for _ in range(300):
        dim = 4
        m = 10
        q = rng.uniform(0.05, 0.95, m)
        eps = rng.uniform(1e-5, 0.02, m)
        signed = rng.uniform(-1, 1, m) * eps
        p = np.clip(q + signed, 0.0, 1.0)
        # Ensure the promised error radii actually cover the clipped p.
        eps = np.maximum(eps, np.abs(p - q))
        events = [(k % dim, (k + 1) % dim, bool(k % 3 == 0)) for k in range(m)]
        y0 = rng.random(dim); y0 /= y0.sum()
        w = rng.random(dim)
        cert = hybrid_pruning_bound(q, eps, events, y0, w)
        actual = abs(observable_difference(p, q, events, y0, w))
        assert actual <= cert['observable_error_bound'] + 5e-14
        assert cert['observable_error_bound'] <= cert['global_l1_probability_bound'] + 5e-14


def test_pruning_bound_is_nontrivial_when_population_or_sensitivity_is_small():
    q = np.array([0.2, 0.3, 0.4])
    eps = np.array([1e-3, 1e-3, 1e-3])
    events = [(0, 1, False), (1, 2, False), (2, 3, True)]
    y0 = np.array([0.999, 0.001, 0.0, 0.0])
    w = np.array([1.0, 1.0, 1.0, 1.0])
    cert = hybrid_pruning_bound(q, eps, events, y0, w)
    assert cert['observable_error_bound'] == pytest.approx(0.0, abs=1e-15)
    assert cert['global_l1_probability_bound'] > 0


def test_invalid_probability_error_contract_fails_closed():
    q = [0.2]
    events = [(0, 1, False)]
    with pytest.raises(ValueError):
        hybrid_pruning_bound(q, [-1e-3], events, [1.0, 0.0], [0.0, 1.0])
