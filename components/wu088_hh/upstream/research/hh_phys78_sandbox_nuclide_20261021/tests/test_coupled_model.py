"""Small coupled equation controls; no ODE integration is launched by tests."""
from pathlib import Path
import math
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"source"))
import atomic_network as atomic
import coupled_model as cm


class ExactIsotropicKinetic:
    """Known dust/radiation limits for independent local equation controls."""
    def moments(self, x, b):
        if b != 0:
            raise ValueError("This test reference is restricted to b=0")
        return {"rho_m": math.exp(-3*x), "pbar_m": 0., "pi_m": 0.,
                "rho_r": math.exp(-4*x), "pbar_r": math.exp(-4*x)/3., "pi_r": 0.}


def model(sigma=0., uv=1.):
    return cm.CoupledModel({"id": "local-equation-control", "sigma0_F_signed": sigma,
                            "A_m": 0., "A_r": 0., "uv_scale": uv},
                           kinetic_model=ExactIsotropicKinetic())


class CoupledModelTests(unittest.TestCase):
    def test_initial_frobenius_axis_and_hamiltonian(self):
        for sigma in (-.1, 0., .1):
            m = model(sigma)
            e = m.environment(0., m.initial_state)
            self.assertAlmostEqual(math.sqrt(6)*e["s_over_H"], sigma, delta=2e-16)
            self.assertAlmostEqual(e["H"]**2/(cm.H0**2*(e["rho_total"]+cm.OMEGA_LAMBDA)
                                                   +e["s"]**2), 1., delta=3e-16)
            self.assertAlmostEqual(e["T_K"], 300., delta=6e-14)

    def test_reference_H_density_recovers_baryon_rest_budget(self):
        m = model()
        for x in (0., .3, cm.X_END):
            e = m.environment(x, m.initial_state)
            ratio = e["eV_density_norm"]*m.rest_energy_per_H
            self.assertAlmostEqual(ratio/(cm.OMEGA_B/e["a"]**3), 1., delta=4e-16)

    def test_gray_atomic_and_reservoir_energy_exchange_cancels(self):
        m = model(.1)
        y = m.initial_state.copy()
        for uv in (0., .5, 2.):
            m.case["uv_scale"] = uv
            dy, e = m.evaluate(0., y)
            balance = (dy[cm.I_U]+m.atomic.binding_eV@dy[cm.S_Y]+dy[cm.S_U].sum()
                       +dy[cm.I_R]+dy[cm.I_RESERVOIR]+2*y[cm.I_U]+y[cm.S_U].sum()+y[cm.I_R])
            self.assertLess(abs(e["energy_balance_rel"]), 5e-16)
            self.assertAlmostEqual(balance, e["energy_balance_abs_eV_per_H_x"])
            np.testing.assert_allclose(atomic.ISOTOPE_SUM @ dy[cm.S_Y], 0,
                                       rtol=0, atol=2e-17*max(abs(dy[cm.S_Y])))

    def test_trace_tolerances_scale_with_inventory_and_requested_accuracy(self):
        m = model()
        atol = m.absolute_tolerances()
        li = atomic.SPECIES_INDEX["Li6_I"]
        h = atomic.SPECIES_INDEX["H1_I"]
        self.assertAlmostEqual(atol[cm.S_Y][li]/atol[cm.S_Y][h],
                               atomic.DEFAULT_INVENTORY["Li6"], delta=1e-29)
        np.testing.assert_allclose(m.absolute_tolerances(cm.DEFAULT_RTOL/10), atol/10,
                                   rtol=2e-16, atol=0)

    def test_state_domains_reject_undeclared_projection(self):
        m = model()
        for index in (cm.I_U, cm.I_RESERVOIR, cm.S_N.start, cm.S_U.start):
            y = m.initial_state.copy()
            y[index] = -1e-12
            with self.assertRaises(ValueError):
                m.evaluate(0., y)
        y = m.initial_state.copy()
        y[cm.S_U.start+2] = y[cm.S_N.start+2]*65.
        with self.assertRaisesRegex(ValueError, "EMAX_EXCEEDED"):
            m.evaluate(0., y)

    def test_absent_neutron_roundoff_has_explicit_bound_without_projection(self):
        m = model()
        y = m.initial_state.copy()
        index = cm.S_Y.start+atomic.SPECIES_INDEX["n"]
        y[index] = -5.893667266498666e-39
        dy, point = m.evaluate(0., y)
        self.assertEqual(y[index], -5.893667266498666e-39)
        self.assertEqual(dy[index], 0.)
        self.assertEqual(point["atomic"].diagnostics["negative_stage_coordinates"], 1)
        y[index] = -2*cm.STAGE_ABSENT_ISOTOPE_ABSOLUTE
        with self.assertRaisesRegex(ValueError, "NEGATIVITY_BOUND_EXCEEDED"):
            m.evaluate(0., y)

    def test_scaled_solver_coordinates_preserve_physical_energy_and_nuclei(self):
        m = model()
        scaled = m.initial_state/m.solver_scales
        dy = m.solver_rhs(0., scaled)*m.solver_scales
        reference = m.evaluate(0., m.initial_state)[0]
        np.testing.assert_allclose(dy, reference, rtol=3e-16, atol=1e-30)
        balance = (dy[cm.I_U]+m.atomic.binding_eV@dy[cm.S_Y]+dy[cm.S_U].sum()
                   +dy[cm.I_R]+dy[cm.I_RESERVOIR]+2*m.initial_state[cm.I_U]
                   +m.initial_state[cm.S_U].sum())
        self.assertLess(abs(balance), 1e-16)
        self.assertGreater(m.solver_scales[cm.S_Y][atomic.SPECIES_INDEX["n"]], 0.)

    def test_invalid_newton_trial_is_rejected_without_state_repair(self):
        m = model()
        scaled = m.initial_state/m.solver_scales
        scaled[cm.I_U] = -1.
        self.assertTrue(np.isnan(m.solver_rhs(0., scaled)).all())
        self.assertEqual(scaled[cm.I_U], -1.)
        self.assertEqual(m.rejected_domain_stage_count, 1)
        with self.assertRaisesRegex(ValueError, "NONPOSITIVE_GAS"):
            m.evaluate(0., scaled*m.solver_scales)


if __name__ == "__main__":
    unittest.main(verbosity=2)
