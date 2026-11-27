"""New packed-assembly/cache regression checks, with no native chemistry.

The inherited scientific suites are not invoked. The owner below is an
explicit manufactured response used only to compare changed execution paths.
"""
import os
from pathlib import Path
import sys
import unittest

for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"
import numpy as np
from scipy.sparse import lil_matrix

LANE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LANE / "src"))
sys.path.insert(0, str(LANE / "benchmarks"))
from optimized_model import (PackedJacobian, OptimizedRefinedSourceModel,
    prepare_jacobian, PHOTON_LEDGER_ROWS)
from profile_jacobian import DensityOnlyOwner, AssemblyFixture
from refined_source import RefinedSourceModel, GridSpec
from physics import Model, neutral, Y_HE, EV_ERG


class ManufacturedOwner(DensityOnlyOwner):
    def __init__(self):
        self.calls = 0

    def point(self, a, gas, gamma, heat):
        self.calls += 1
        absorbed = neutral(gas) * gamma
        return dict(fraction_dt=np.array((absorbed[0],
            (absorbed[1]-absorbed[2])/Y_HE, absorbed[2]/Y_HE)),
            w_dt_ev_per_h_s=float(np.dot(neutral(gas), heat))/EV_ERG,
            escape=0., cmb=0., ci=np.zeros(3), rr=np.zeros(3), dr=0.)


def interval(model, t):
    bounds = np.r_[0., model.breakpoints, model.t_end]
    i = max(0, min(len(bounds)-2, int(np.searchsorted(bounds, t)-1)))
    model.set_interval(float(bounds[i]), float(bounds[i+1]))
    return bounds, i


class OptimizedModelChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = RefinedSourceModel(ManufacturedOwner(), GridSpec(m=4), tabulate=False)
        cls.optimized = OptimizedRefinedSourceModel(ManufacturedOwner(), GridSpec(m=4), tabulate=False)

    def test_owned_coefficients_and_canonical_zero_pruning(self):
        k, n = 3, 26
        gas = np.arange(n*4, dtype=float).reshape(n, 4) / 17
        photon = np.arange(12*k, dtype=float).reshape(12, k) / 19
        gas[::2, 2] = -0.; photon[::2, 1] = 0.
        packed = PackedJacobian(gas, photon)
        matrix = lil_matrix((n, n)); matrix[:, :4] = gas
        for j in range(k):
            matrix[:4, 4+j] = photon[:4, j, None]
            matrix[4+j, 4+j] = photon[4, j]
            for row, ledger in enumerate(PHOTON_LEDGER_ROWS):
                matrix[k+4+ledger, 4+j] = photon[row+5, j]
        original, candidate = matrix.tocsr(), packed.csr()
        for name in ("data", "indices", "indptr"):
            np.testing.assert_array_equal(getattr(original, name), getattr(candidate, name))
        self.assertTrue(candidate.has_canonical_format)
        self.assertEqual(candidate[:, k+4:].nnz, 0)
        gas[:] = 0.; photon[:] = 0.
        self.assertGreater(np.count_nonzero(packed.gas), 0)
        self.assertFalse(packed.gas.flags.writeable)
        self.assertFalse(packed.photon.flags.writeable)
        self.assertEqual(packed.nbytes, (16*k+92)*8)

    def test_invalid_coefficient_storage_fails(self):
        for gas, photon in ((np.zeros((23,4)),np.zeros((12,0))),
                (np.zeros((24,3)),np.zeros((12,1))),
                (np.full((24,4), np.nan),np.zeros((12,1))),
                (np.zeros((24,4)),np.full((12,1), np.inf))):
            with self.subTest(shape=gas.shape):
                with self.assertRaisesRegex(ValueError, "PACKED_SHAPE_OR_FINITE"):
                    PackedJacobian(gas, photon)

    def test_original_constructor_and_full_rhs_preserved(self):
        old, new = self.original, self.optimized
        self.assertEqual(old.source_table_sha256, new.source_table_sha256)
        for name in ("Eref", "mu0", "weights", "scale", "_cut_bounds"):
            np.testing.assert_array_equal(getattr(old, name), getattr(new, name))
        t = old.t_end * .431
        interval(old, t); interval(new, t)
        state = old.initial_state(); state[4:4+old.K] = old.scale[4:4+old.K] * .3
        np.testing.assert_array_equal(old.rhs(t, state), new.rhs(t, state))
        self.assertGreater(new.optimization_counts["geometry_hits"], 0)
        self.assertGreater(new.optimization_counts["sigma_hits"], 0)

    def test_full_manufactured_rhs_jacobian_exact(self):
        old, new = self.original, self.optimized
        t = old.t_end * .431
        interval(old, t); interval(new, t)
        state = old.initial_state(); state[4:4+old.K] = old.scale[4:4+old.K] * .3
        counts = old.owner.calls, new.owner.calls
        a, b = old.jac(t, state), new.jac(t, state)
        self.assertEqual((old.owner.calls-counts[0], new.owner.calls-counts[1]), (5,5))
        for name in ("data", "indices", "indptr"):
            np.testing.assert_array_equal(getattr(a, name), getattr(b, name))

    def test_finite_difference_admissibility_flip_preserved(self):
        model = self.original; t = model.t_end * .431
        interval(model, t)
        fixture = AssemblyFixture(model)
        state = model.initial_state(); state[:3] = (1., .3, .7)
        a = Model.jac(fixture, t, state)
        b = prepare_jacobian(fixture, t, state).csr()
        self.assertEqual(fixture.calls, 10)
        for name in ("data", "indices", "indptr"):
            np.testing.assert_array_equal(getattr(a, name), getattr(b, name))

    def test_exact_time_and_interval_cache_invalidation(self):
        model = self.optimized; t = model.t_end * .431
        bounds, i = interval(model, t)
        a = model.sigma(t)
        self.assertIs(a, model.sigma(t))
        self.assertIsNot(a, model.sigma(np.nextafter(t, np.inf)))
        a = model.sigma(t)
        model.set_interval(float(bounds[i]), float(bounds[i+1]))
        self.assertIsNot(a, model.sigma(t))
        for entry in model.geometry(t):
            self.assertFalse(entry.flags.writeable)
        with self.assertRaisesRegex(ValueError, "HE29_OPT_TIME"):
            model.geometry(np.nan)

    def test_crossing_endpoint_mask_changes_are_not_cached_across_intervals(self):
        old, new = self.original, self.optimized
        bounds = np.r_[0., old.breakpoints, old.t_end]
        i = len(bounds)//2
        for left, right in ((bounds[i-1],bounds[i]), (bounds[i],bounds[i+1])):
            old.set_interval(float(left),float(right)); new.set_interval(float(left),float(right))
            np.testing.assert_array_equal(old.sigma(float(bounds[i])), new.sigma(float(bounds[i])))

    def test_nonfinite_state_scale_and_rates_fail(self):
        model = self.original; t = model.t_end*.431
        fixture = AssemblyFixture(model); state = model.initial_state()
        bad = state.copy(); bad[7] = np.inf
        with self.assertRaisesRegex(ValueError, "STATE"):
            prepare_jacobian(fixture, t, bad)
        fixture.scale[0] = 0
        with self.assertRaisesRegex(ValueError, "SCALE"):
            prepare_jacobian(fixture, t, state)
        fixture.scale[0] = 1e-5
        fixture.rates = lambda t,g: (1.,1.,np.ones(model.K),np.zeros(model.K),np.full((model.K,3), np.nan))
        with self.assertRaisesRegex(ValueError, "LAMBDA"):
            prepare_jacobian(fixture, t, state)

    def test_finite_trial_coefficients_keep_original_domain(self):
        model = self.original; t = model.t_end*.431
        fixture = AssemblyFixture(model); state = model.initial_state()
        fixture.rates = lambda t,g: (1.,1.,np.full(model.K, 20.),
            np.zeros(model.K),np.tile(np.array([-1., 2., -3.]), (model.K,1)))
        a = Model.jac(fixture, t, state)
        b = prepare_jacobian(fixture, t, state).csr()
        for name in ("data", "indices", "indptr"):
            np.testing.assert_array_equal(getattr(a, name), getattr(b, name))


if __name__ == "__main__":
    unittest.main(verbosity=2)
