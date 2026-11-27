import numpy as np
from reduced_parity import reduced_blocks, reduced_rotation_batch, reduced_dop853, collapsed_from_parity


def test_l1_parity_hamiltonian():
    even, odd = reduced_blocks(1, 2.0)
    np.testing.assert_allclose(even, [[0, -1], [-1, 2]])
    np.testing.assert_allclose(odd, [[2]])


def test_l2_parity_couplings():
    even, odd = reduced_blocks(2, 3.0)
    np.testing.assert_allclose(even, [[0, -np.sqrt(3), 0], [-np.sqrt(3), 3, -1], [0, -1, 12]])
    np.testing.assert_allclose(odd, [[3, -1], [-1, 12]])


def test_l1_collapse_distinguishes_even_author_column_one():
    t = 0.3
    u = np.array([[np.sqrt(1-t), -np.sqrt(t)], [np.sqrt(t), np.sqrt(1-t)]])
    collapsed = collapsed_from_parity(u, np.array([[1.0]]))
    np.testing.assert_allclose(collapsed, [[1-t, t/2], [t, 1-t/2]], atol=1e-15)
    assert np.isclose(abs(u[0, 1])**2, t, atol=1e-15)


def test_inactive_queries_are_identity():
    for trajectory in ('STRAIGHT','COULOMB'):
        out = reduced_rotation_batch(2, 1, [0.5, 5.0], [3.0, 3.0], trajectory=trajectory, cutoff='CPC', steps=64)
        np.testing.assert_allclose(out['P'], np.broadcast_to(np.eye(2), (2, 2, 2)))
        assert not any(out['entered'])


def test_reduced_magnus_and_separate_dop853_agree():
    for trajectory, steps in (('STRAIGHT', 128), ('COULOMB', 512)):
        out = reduced_rotation_batch(3, 2, [5.0], [0.05], trajectory=trajectory, cutoff='AUTHOR', steps=steps)
        audit = reduced_dop853(3, 2, 5.0, 0.05, trajectory=trajectory, cutoff='AUTHOR')
        assert np.max(abs(out['P'][0] - audit['P'])) < 1e-8
        assert out['unitarity_defect'] < 5e-13
        assert audit['unitarity_defect'] < 5e-13


def test_query_manifest_is_complete_and_exact():
    import json
    from pathlib import Path
    m = json.loads(Path('QUERY_MANIFEST.json').read_text())
    assert m['rho_count'] == 300
    assert m['r10g_new_rho_count'] == 60
    assert m['r10f_outer_rho_count'] == 240
    assert m['active_query_count'] == len(m['active_queries']) == 3270
    assert len({tuple(x) for x in m['active_queries']}) == 3270


def test_molecular_x_gauge_and_parity_blocks_l1_l2():
    import math
    from scipy.linalg import expm
    from arseny_reimpl.rotational import angular_momentum_operators
    for l in (1, 2):
        m, lx, lz = angular_momentum_operators(l)
        ly = -1j * (lz @ lx - lx @ lz)
        V = expm(-1j * math.pi / 2 * ly)
        np.testing.assert_allclose(V.conj().T @ lx @ V, lz, atol=2e-15)
        np.testing.assert_allclose(V.conj().T @ lz @ V, -lx, atol=2e-15)
        even = np.zeros((2*l+1, l+1), complex)
        odd = np.zeros((2*l+1, l), complex)
        even[l, 0] = 1
        for k in range(1, l+1):
            even[l+k, k] = even[l-k, k] = 1 / np.sqrt(2)
            odd[l+k, k-1] = 1 / np.sqrt(2)
            odd[l-k, k-1] = -1 / np.sqrt(2)
        H = 2.0 * (lz @ lz) - lx
        want_even, want_odd = reduced_blocks(l, 2.0)
        np.testing.assert_allclose(even.conj().T @ H @ even, want_even, atol=2e-15)
        np.testing.assert_allclose(odd.conj().T @ H @ odd, want_odd, atol=2e-15)
        np.testing.assert_allclose(even.conj().T @ H @ odd, 0, atol=2e-15)


def test_current_approach_events_cannot_populate_positive_m():
    from arseny_reimpl.eq50_scoped import ordered_scoped_branches, branch_state_indices
    from arseny_reimpl.state_index import enumerate_states
    support = {2}
    for branch in reversed(ordered_scoped_branches()):
        i, j = (x-1 for x in branch_state_indices(branch))
        prior = support.copy()
        if i in prior:
            support.add(j)
        if branch.state_b[0] != 3 and j in prior:
            support.add(i)
    assert support == {0, 2, 5, 7}
    positive_m = {j-1 for j, N, l, m in enumerate_states(3) if m > 0}
    assert not support & positive_m
