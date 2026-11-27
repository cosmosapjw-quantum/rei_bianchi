"""New manufactured embedding checks; no molecular eigensolves or old-suite replay."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from optimized_solver import PartialWaveState, MultiStateResult, RESIDUAL_DEFINITION, _polynomials
from multistate_provider import save_sector, load_sector
from common_embedding import (EmbeddingError, build_common_grid, embed_state,
                              write_source_binding, snapshot_from_archives)
from projector import TargetSpec, ValidationTolerances, validate_snapshot, Role


def polynomial_sector(m, *, R=1., mesh=(0., .4, 1.), mass_scale=1.):
    """Normalized u=sqrt(30) r(1-r), orthogonal A_lm across root ordinals."""
    mesh = np.asarray(mesh, dtype=np.float64)
    count = 6 if m == 0 else 3
    ls = np.arange(m, m+count, dtype=np.int64)
    nodes, _ = _polynomials(2)
    radii = np.concatenate([lo+(hi-lo)*(nodes+1)/2 if j == 0 else
                            (lo+(hi-lo)*(nodes+1)/2)[1:]
                            for j, (lo, hi) in enumerate(zip(mesh[:-1], mesh[1:]))])
    radial = np.sqrt(30.)*radii*(1-radii)
    energies = [-2., -.5, -.45, -.4, .1, .2] if m == 0 else [-.43, .15, .3]
    states = []
    for ordinal, energy in enumerate(energies):
        coef = np.zeros((count, len(radii)), dtype=np.float64)
        coef[ordinal] = radial
        metadata = {"origin_center": "O", "origin_shift_center_to_O": 0.,
                    "units": "a_A,E_A", "radial_quadrature": 4, "source_ordinal": ordinal,
                    "residual_definition": RESIDUAL_DEFINITION}
        states.append(PartialWaveState(R, 1., 2., m, ls.copy(), mesh.copy(), 2, coef,
                                      energy, 1e-14, mass_scale, 1., metadata))
    vectors = np.column_stack([s.coefficients[:, 1:-1].ravel() for s in states])
    metadata = {"residual_definition": RESIDUAL_DEFINITION, "backend": "manufactured-test",
                "source_files_sha256": {"test_common_embedding.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}
    return MultiStateResult(tuple(states), np.diag(energies), np.eye(count)*mass_scale, vectors, metadata)


class CommonEmbeddingTests(unittest.TestCase):
    def setUp(self):
        self.a = polynomial_sector(0)
        self.b = polynomial_sector(1, mesh=(0., .25, .7, 1.))
        self.states = self.a.states+self.b.states

    def archives(self, directory, *, a=None, b=None):
        out = []
        for name, result in (("m0", self.a if a is None else a), ("m1", self.b if b is None else b)):
            path = Path(directory)/(name+".npz")
            identity = save_sector(result, path, "manufactured/"+name)
            out.append(load_sector(path, identity["source_sha256"]))
        return tuple(out)

    def test_polynomial_exact_norm_and_union_mesh(self):
        grid = build_common_grid(self.states)
        self.assertTrue(np.array_equal(grid.boundaries, [0., .25, .4, .7, 1.]))
        for state in self.states:
            v = embed_state(state, grid)
            self.assertLess(abs(np.vdot(v, grid.weights*v)-1), 3e-14)
        self.assertTrue(np.all(grid.weights > 0))
        self.assertTrue(np.all(grid.r > 0))

    def test_full_cross_sector_gram_and_conjugacy(self):
        grid = build_common_grid(self.states)
        zero = [embed_state(s, grid) for s in self.a.states]
        plus = [embed_state(s, grid) for s in self.b.states]
        minus = [embed_state(s, grid, m_signed=-1) for s in self.b.states]
        frame = np.column_stack(zero+plus+minus)
        self.assertLess(np.max(np.abs(frame.conj().T@(grid.weights[:, None]*frame)-np.eye(12))), 3e-14)
        for p, n in zip(plus, minus):
            np.testing.assert_array_equal(n, p.conj())

    def test_bright_dark_phase_normalization(self):
        grid = build_common_grid(self.states)
        p = embed_state(self.b.states[0], grid)
        n = embed_state(self.b.states[0], grid, m_signed=-1)
        bright, dark = (p+n)/np.sqrt(2), (p-n)/(1j*np.sqrt(2))
        self.assertLess(np.max(np.abs(bright.imag)), 1e-15)
        self.assertLess(np.max(np.abs(dark.imag)), 1e-15)
        self.assertLess(abs(np.vdot(bright, grid.weights*dark)), 1e-14)
        self.assertLess(abs(np.vdot(dark, grid.weights*dark)-1), 1e-14)

    def test_cross_R_different_mesh_identical_physical_function(self):
        other = polynomial_sector(0, R=2., mesh=(0., .1, .8, 1.))
        grid = build_common_grid(self.a.states+other.states)
        a, b = embed_state(self.a.states[0], grid), embed_state(other.states[0], grid)
        self.assertLess(np.max(np.abs(a-b)), 2e-15)
        self.assertLess(abs(np.vdot(a, grid.weights*b)-1), 2e-14)

    def test_exact_r_squared_observable_and_indicator_partition(self):
        grid = build_common_grid(self.states, radial_order=4, extra_radial_knots=(.5,))
        v = embed_state(self.a.states[0], grid)
        r = np.repeat(grid.r, len(grid.eta)*len(grid.phi))
        self.assertLess(abs(np.vdot(v, grid.weights*r*r*v)-2/7), 1e-14)
        self.assertLess(abs(np.vdot(v, grid.weights*(r >= .5)*v)-.5), 1e-14)

    def test_grid_owns_readonly_arrays(self):
        grid = build_common_grid(self.states)
        self.a.states[0].boundaries[1] = .3
        self.assertTrue(np.array_equal(grid.boundaries, [0., .25, .4, .7, 1.]))
        for a in (grid.r, grid.eta, grid.phi, grid.weights, grid.boundaries):
            with self.assertRaises(ValueError):
                a[0] = 0

    def test_origin_units_and_box_rejection(self):
        for key, value in (("origin_center", "B"), ("origin_shift_center_to_O", 1.), ("units", "unknown")):
            bad = polynomial_sector(0).states[0]
            bad.metadata[key] = value
            with self.assertRaises(EmbeddingError):
                build_common_grid((bad,))
        bad = polynomial_sector(0).states[0]
        bad.boundaries[-1] = 2.
        with self.assertRaises(EmbeddingError):
            build_common_grid((bad, self.a.states[0]))

    def test_quadrature_alias_and_budget_rejection(self):
        for kwargs in ({"radial_order": 2}, {"eta_order": 5}, {"phi_count": 2},
                       {"max_points": 10}, {"extra_radial_knots": (1.,)}):
            with self.assertRaises(EmbeddingError):
                build_common_grid(self.states, **kwargs)

    def test_invalid_complex_coefficients_endpoint_and_mass_order(self):
        for alteration in ("complex", "endpoint", "order"):
            s = polynomial_sector(0).states[0]
            if alteration == "complex":
                s.coefficients = s.coefficients.astype(np.complex128)
            elif alteration == "endpoint":
                s.coefficients[0, 0] = 1.
            else:
                s.metadata["radial_quadrature"] = 2
            with self.assertRaises(EmbeddingError):
                build_common_grid((s,))

    def test_grid_cannot_embed_unregistered_mesh_or_signed_sector(self):
        grid = build_common_grid(self.states)
        other = polynomial_sector(0, mesh=(0., .3, 1.)).states[0]
        with self.assertRaises(EmbeddingError):
            embed_state(other, grid)
        with self.assertRaises(EmbeddingError):
            embed_state(self.a.states[0], grid, m_signed=1)

    def test_source_bound_snapshot_and_actual_galerkin_operator(self):
        with tempfile.TemporaryDirectory() as directory:
            archives = self.archives(directory)
            grid = build_common_grid(self.states)
            binding = Path(directory)/"binding.json"
            identity = write_source_binding(archives, binding, source_id="manufactured/pair")
            result = snapshot_from_archives(archives, grid, source_binding_path=binding, gram_identity_atol=1e-12)
            snap = result.snapshot
            self.assertEqual(snap.representation.source_sha256, hashlib.sha256(binding.read_bytes()).hexdigest())
            self.assertEqual(identity["bytes"], binding.stat().st_size)
            self.assertEqual(len(snap.selected_indices), 5)
            self.assertEqual(len(snap.guard_indices), 7)
            np.testing.assert_array_equal(np.diag(snap.selected_projected_operator), [-.5, -.45, -.4, -.43, -.43])
            for state in snap.states:
                if state.m:
                    partner = next(x for x in snap.states if x.state_id == state.known_degenerate_partners[0])
                    self.assertEqual(partner.energy, state.energy)
                    self.assertEqual(partner.residual_norm, state.residual_norm)
                    self.assertEqual(partner.role, state.role)
            diagnostics = validate_snapshot(snap, TargetSpec.large_R_rank5(),
                ValidationTolerances(1e-12, 1e-12, 1e-10, .01), backend="reference")
            self.assertEqual(diagnostics.selected_rank, 5)
            self.assertFalse(result.provenance["pointwise_PDE_H_apply"])

    def test_source_binding_create_only_and_source_mutation_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            archives = self.archives(directory)
            path = Path(directory)/"binding.json"
            write_source_binding(archives, path, source_id="manufactured/pair")
            with self.assertRaises(FileExistsError):
                write_source_binding(archives, path, source_id="manufactured/pair")
            with archives[0].source_path.open("ab") as stream:
                stream.write(b"changed")
            with self.assertRaises(ValueError):
                snapshot_from_archives(archives, build_common_grid(self.states), source_binding_path=path, gram_identity_atol=1e-12)

    def test_loaded_metadata_mutation_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            archives = self.archives(directory)
            archives[0].result.states[0].metadata["origin_center"] = "B"
            with self.assertRaises(EmbeddingError):
                write_source_binding(archives, Path(directory)/"binding.json", source_id="manufactured/pair")

    def test_equal_norm_coefficient_swap_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            archives = self.archives(directory)
            path = Path(directory)/"binding.json"
            write_source_binding(archives, path, source_id="manufactured/pair")
            left, right = archives[0].result.states[:2]
            left.coefficients, right.coefficients = right.coefficients, left.coefficients
            with self.assertRaises(EmbeddingError):
                snapshot_from_archives(archives, build_common_grid(self.states), source_binding_path=path, gram_identity_atol=1e-12)

    def test_binding_substitution_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            archives = self.archives(directory)
            path = Path(directory)/"binding.json"
            write_source_binding(archives, path, source_id="manufactured/pair")
            obj = json.loads(path.read_bytes())
            obj["archives"][0]["sha256"] = "0"*64
            path.write_text(json.dumps(obj))
            with self.assertRaises(EmbeddingError):
                snapshot_from_archives(archives, build_common_grid(self.states), source_binding_path=path, gram_identity_atol=1e-12)

    def test_mass_form_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            archives = self.archives(directory, a=polynomial_sector(0, mass_scale=2.))
            path = Path(directory)/"binding.json"
            write_source_binding(archives, path, source_id="manufactured/pair")
            with self.assertRaises(EmbeddingError):
                snapshot_from_archives(archives, build_common_grid(self.states), source_binding_path=path, gram_identity_atol=1e-12)

    def test_one_R_required_for_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            archives = self.archives(directory, b=polynomial_sector(1, R=2.))
            path = Path(directory)/"binding.json"
            write_source_binding(archives, path, source_id="manufactured/pair")
            with self.assertRaises(EmbeddingError):
                snapshot_from_archives(archives, build_common_grid(self.states), source_binding_path=path, gram_identity_atol=1e-12)


if __name__ == "__main__":
    unittest.main()
