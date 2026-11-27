"""New affected finite-mass/phase/normalization contracts only."""
import io
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch
import fm_cba as fm
from io_utils import atomic_json

UNIT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((UNIT / 'FROZEN_CONTRACT.json').read_bytes().decode('utf-8'))
TOL = CONTRACT['analysis']['normalization_scaled_tolerance']


class FiniteMassContracts(unittest.TestCase):
    def close(self, a, b, tolerance=TOL):
        self.assertLessEqual(abs(a-b) / max(1., abs(b)), tolerance)

    def test_01_mass_and_binding(self):
        for M in [1., 2., 10., 1836.152673426]:
            z = fm.finite_mass_parameters(M)
            self.close(z['a'] + z['b'], 1.)
            self.close(z['lambda'], z['mu'])
            self.close(z['binding'], M / (2*(M+1)))
        self.assertEqual(fm.finite_mass_parameters(1)['binding'], .25)

    def test_02_reject_invalid_mass_and_kernel_inputs(self):
        for M in [0., -1., True, float('inf'), float('nan'), 1j, '2']:
            with self.subTest(M=M), self.assertRaises(ValueError): fm.finite_mass_parameters(M)
        for D, k in [((0, 0), (0, 0, .7)), ((0, 0, .3), (0, 0, 0)),
                     ((0, float('nan'), 1), (0, 0, 1))]:
            with self.assertRaises(ValueError): fm.finite_form_factor(2, D, k)

    def test_03_shifted_potential_geometry(self):
        z = fm.finite_mass_parameters(2)
        X, R, r = (.2, -.1, .3), (.7, .4, -.2), (.3, -.5, .8)
        xA = tuple(X[i] + z['nu']*R[i] for i in range(3))
        xB = tuple(X[i] - R[i]/z['T'] + z['a']*r[i] for i in range(3))
        xN = tuple(X[i] - R[i]/z['T'] - z['b']*r[i] for i in range(3))
        for i in range(3):
            self.close(xA[i]-xB[i], R[i]-z['a']*r[i])
            self.close(xA[i]-xN[i], R[i]+z['b']*r[i])

    def test_04_two_phase_obligation(self):
        M, D, k = 2., (.3, .1, .2), (0, 0, .7)
        z = fm.finite_mass_parameters(M)
        plus, minus = fm.overlap_terms(M, D, k)
        Nc = fm.cba.coulomb_normalizer(z['mu']/.7)
        expected = Nc*math.sqrt(z['mu']**3/math.pi)*(plus-minus)
        self.close(fm.finite_form_factor(M, D, k), expected)
        self.assertGreater(abs(minus), 1e-6)
        self.assertGreater(abs(expected-Nc*math.sqrt(z['mu']**3/math.pi)*plus), 1e-6)

    def test_05_equal_mass_transverse_symmetry_and_zero(self):
        for D in [(.3, .1, 0), (1e-14, 0, 0), (0, 0, 0)]:
            self.assertEqual(fm.finite_form_factor(1, D, (0, 0, .7)), 0j)
        self.assertEqual(fm.finite_form_factor(2, (0, 0, 0), (0, 0, .7)), 0j)

    def test_06_reduced_mass_coulomb_normalization(self):
        for M in [1., 2., 1836.152673426]:
            z = fm.finite_mass_parameters(M); eta = z['mu']/.7
            Nc = fm.cba.coulomb_normalizer(eta)
            self.close(abs(Nc)**2, fm.cba.sommerfeld_strength(eta)/(2*math.pi)**3)
            plus, minus = fm.overlap_terms(M, (.3, .1, .2), (0, 0, .7))
            self.close(abs(fm.finite_form_factor(M, (.3, .1, .2), (0, 0, .7)))**2,
                       abs(Nc)**2*z['mu']**3/math.pi*abs(plus-minus)**2)

    def test_07_jacobi_energy_and_lab_mapping(self):
        for M in [1., 2., 1836.152673426]:
            x = fm.jacobi_tdcs(3., .2, M, (.1, 0, 1), (.4, .2, 1))
            s = fm.shell.shell_state(3., x['binding'], M, x['p_A'], x['p_B'])
            self.close(s['F'], 0, CONTRACT['analysis']['kinematics_scaled_tolerance'])
            self.close(s['energy_identity_residual'], 0, CONTRACT['analysis']['kinematics_scaled_tolerance'])
            for i in range(3): self.close(x['Delta'][i], x['P'][i]-x['p_A'][i])

    def test_08_flux_delta_state_and_Jacobi_density(self):
        x = fm.jacobi_tdcs(3., .2, 2., (.1, 0, 1), (.4, .2, 1))
        d2 = fm.cba._dot(x['Delta'], x['Delta'])
        Tdelta = (4*math.pi/d2)/(2*math.pi)**3*x['F']
        self.close(x['W'], (2*math.pi)**4/x['incident_speed']*abs(Tdelta)**2)
        J = x['mu']*x['nu']*math.hypot(*x['q'])*math.hypot(*x['k'])*x['W']
        self.close(x['tdcs_au'], J)
        w = fm.invariant_weight(3., 2., x['p_A'], x['p_B'])
        self.close(w['W'], x['W'])

    def test_09_two_positive_lab_branches_weighted_separately(self):
        pA = (0., 0., math.sqrt(2)/10)
        x = fm.lab_tdcs(1., 1., pA, (.1, 0, 1))
        self.assertEqual(len(x['branches']), 2)
        self.assertTrue(all(b['p'] > 0 for b in x['branches']))
        self.assertNotEqual(x['branches'][0]['W'], x['branches'][1]['W'])
        self.close(x['density'], sum(b['density_contribution'] for b in x['branches']))
        for b in x['branches']: self.close(b['shell_residual'], 0.)

    def test_10_near_caustic_propagates_without_fake_zero(self):
        radial = {'status': 'NEAR_CAUSTIC_UNRESOLVED', 'branches': []}
        with patch.object(fm.shell, 'solve_radial', return_value=radial):
            x = fm.lab_tdcs(1., 1., (0, 0, .1), (0, 0, 1))
        self.assertIsNone(x['density'])
        self.assertEqual(x['status'], 'NEAR_CAUSTIC_UNRESOLVED')

    def test_11_empty_lab_support(self):
        x = fm.lab_tdcs(.1, 1., (0, 0, .1), (0, 0, 1))
        self.assertEqual(x['density'], 0.)
        self.assertEqual(x['branches'], [])

    def test_12_explicit_continuum_endpoint(self):
        E0, M, pA = 1., 2., (0, 0, .1)
        c = tuple((p-a)/(M+1) for p, a in zip((0, 0, math.sqrt(2)), pA))
        radial = {'status': 'SIMPLE_ROOTS', 'p_A_norm': .1,
                  'branches': [{'p': math.hypot(*c), 'p_B': c, 'radial_weight': 1.}]}
        with patch.object(fm.shell, 'solve_radial', return_value=radial):
            x = fm.lab_tdcs(E0, M, pA, (0, 0, 1))
        self.assertEqual(x['status'], 'CONTINUUM_ENDPOINT_EXCLUDED')
        self.assertIsNone(x['density'])

    def test_13_channel_endpoint_rejection(self):
        for E0, Er in [(.1, .01), (1., 0.), (1., .5), (-1., .1), (float('inf'), .1)]:
            with self.assertRaises(ValueError): fm.jacobi_tdcs(E0, Er, 1., (0, 0, 1), (0, 0, 1))
        with self.assertRaises(ValueError): fm.jacobi_tdcs(2., .1, 2., (0, 0, 0), (0, 0, 1))
        with self.assertRaises(ValueError): fm.invariant_weight(1., 2., (0, 0, math.sqrt(2)), (0, 0, 1))
        with self.assertRaises(ValueError): fm.lab_tdcs(1., 2., (0, 0, math.sqrt(2)), (0, 0, 1))
        for nq, nk in [((1.7e308, 1.7e308, 0), (0, 0, 1)),
                       ((0, 0, 1), (1.7e308, 1.7e308, 0))]:
            with self.assertRaises(ValueError): fm.jacobi_tdcs(3., .2, 2., nq, nk)

    def test_14_infinite_mass_link(self):
        nq, nk = (.1, 0, 1), (.4, 0, 1)
        finite = fm.jacobi_tdcs(3., .2, 1e12, nq, nk)
        parent = fm.cba.direct_tdcs(3., .2, (0, 0, 1), nq, nk)
        # A finite-M approximation tolerance, not a uniform limit certificate.
        self.assertLess(abs(finite['tdcs_au']-parent['tdcs_au'])/max(1., abs(parent['tdcs_au'])), 1e-10)

    def test_15_direction_scaling_and_energy_label(self):
        x = fm.jacobi_tdcs(3., .2, 2., (.1, 0, 1), (.4, 0, 1))
        y = fm.jacobi_tdcs(3., .2, 2., (.2, 0, 2), (.8, 0, 2))
        self.close(x['tdcs_au'], y['tdcs_au'])
        self.assertIn('not lab EB', x['energy_label'])
        self.assertEqual(x['measure'], 'dEr dOmega_k dOmega_q')

    def test_16_frozen_parent_and_dependency_identities(self):
        from io_utils import identity
        manifest = json.loads((UNIT/'evidence/preparation/PREPARATION_MANIFEST.json').read_bytes().decode('utf-8'))
        workspace = UNIT.parents[2]
        for relative, expected in manifest['external_inputs'].items():
            self.assertEqual(identity(workspace/relative), expected)

    def test_17_lab_A_zero_endpoint_is_not_fake_zero(self):
        result = fm.lab_tdcs(3., 2., (0, 0, 0), (0, 0, 1))
        self.assertEqual(result['status'], 'LAB_A_ZERO_ENDPOINT')
        self.assertIsNone(result['density'])
        # Momentum-density weight has its own domain and remains defined here.
        self.assertGreaterEqual(fm.invariant_weight(3., 2., (0, 0, 0), (.1, .2, .4))['W'], 0.)


if __name__ == '__main__':
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(FiniteMassContracts))
    print(stream.getvalue(), end='')
    atomic_json(UNIT/'results/TEST_REPORT.json', {'tests_run': result.testsRun,
                'failures': len(result.failures), 'errors': len(result.errors),
                'successful': result.wasSuccessful(), 'log': stream.getvalue(),
                'scope': 'New affected finite-M model only; old suite replay0'})
    raise SystemExit(0 if result.wasSuccessful() else 1)
