"""New-scope targeted controls; no previous kernel or suite is imported."""
from fractions import Fraction
import itertools
import json
import math
from pathlib import Path
import unittest
import shell

UNIT = Path(__file__).resolve().parents[1]


class ShellTests(unittest.TestCase):
    def close(self, a, b, tolerance=1e-11, scale=None):
        denominator = max(1.0, abs(a), abs(b)) if scale is None else scale
        self.assertLessEqual(abs(a-b), tolerance * denominator)

    def vector_close(self, a, b):
        for x, y in zip(a, b): self.close(x, y)

    def test_01_jacobi_roundtrip_energy_and_momentum(self):
        for M in (1.0, 7/3, shell.PROTON_ELECTRON_MASS_RATIO):
            E0 = 3.0; P = (0, 0, math.sqrt(6))
            a, b = (0.2, -0.3, 0.7), (-0.4, 0.1, 0.6)
            j = shell.to_jacobi(E0, M, a, b)
            inv = shell.from_jacobi(E0, M, j['q'], j['k'])
            self.vector_close(inv['p_A'], a); self.vector_close(inv['p_B'], b)
            self.vector_close(tuple(a[i]+b[i]+inv['Q'][i] for i in range(3)), P)
            state = shell.shell_state(E0, 0.5, M, a, b)
            self.close(state['energy_identity_residual'], 0)

    def test_02_component_determinant_independent_basis(self):
        for M in (1.0, 5.0, 1836.152673426):
            zero = shell.to_jacobi(1, M, (0, 0, 0), (0, 0, 0))
            da = shell.to_jacobi(1, M, (1, 0, 0), (0, 0, 0))
            db = shell.to_jacobi(1, M, (0, 0, 0), (1, 0, 0))
            a, b = da['q'][0]-zero['q'][0], db['q'][0]-zero['q'][0]
            c, d = da['k'][0]-zero['k'][0], db['k'][0]-zero['k'][0]
            self.close(a*d-b*c, 1)

    def test_03_global_threshold_and_collapse(self):
        # M=1, nu=2/3, B=1/2 gives exact binary64 threshold E0=3/4.
        self.assertEqual(shell.phase_space_volume(0.5, 0.5, 1), 0)
        self.assertEqual(shell.phase_space_volume(0.75, 0.5, 1), 0)
        p = (0, 0, math.sqrt(1.5)/3)
        x = shell.shell_state(0.75, 0.5, 1, p, p)
        self.assertEqual(x['global_support'], 'COLLAPSED_ZERO_MEASURE')
        self.close(x['F'], 0)
        self.assertIsNone(shell.constant_weight_moments(0.75, 0.5, 1)['means'])

    def test_04_conditional_sphere_complete_square(self):
        E0, B, M = 2.0, 0.5, 3.0; a = (0.1, 0.2, 0.3)
        sphere = shell.conditional_sphere(E0, B, M, a)
        self.assertEqual(sphere['status'], 'SPHERE')
        for b in [(0.1, -0.2, 0.4), tuple(sphere['center'][i]+sphere['radius']*(i == 0) for i in range(3))]:
            state = shell.shell_state(E0, B, M, a, b)
            direct = sphere['H']-sphere['alpha']/2*sum((b[i]-sphere['center'][i])**2 for i in range(3))
            self.close(state['F'], direct)
        self.assertEqual(shell.conditional_sphere(1, 0.5, 1, (0, 0, 10))['status'], 'EMPTY')

    def test_05_all_ordinary_root_sign_classes(self):
        cases = [(2, 3, 1, 2, 0), (2, -3, 1, 0, 0),
                 (2, 0, -1, 1, 0), (2, 1, 0, 1, 1),
                 (2, -1, 0, 0, 1), (2, 0, 1, 0, 0)]
        for a, b, c, positive_count, zero_count in cases:
            exact_D = Fraction(b*b)-2*Fraction(a)*Fraction(c)
            result = shell.solve_coefficients(a, b, c)
            self.assertEqual(result['raw_discriminant'], float(exact_D))
            self.assertEqual(len(result['positive_roots']), positive_count)
            self.assertEqual(len(result['zero_endpoints']), zero_count)
            if exact_D < 0:
                self.assertEqual(result['status'], 'NO_REAL_ROOTS')
            else:
                for p in result['algebraic_roots']:
                    self.close(a*p*p/2-b*p+c, 0)

    def test_06_two_positive_hand_roots(self):
        pA = (0, 0, math.sqrt(2)/4)
        result = shell.solve_radial(1, 0.5, 1, pA, (0, 0, 1))
        expected = [(3*math.sqrt(2)-math.sqrt(10))/8, (3*math.sqrt(2)+math.sqrt(10))/8]
        self.assertEqual(len(result['positive_roots']), 2)
        for a, b in zip(result['positive_roots'], expected): self.close(a, b, 1e-10)
        for branch in result['branches']:
            self.close(shell.shell_state(1, 0.5, 1, pA, branch['p_B'])['F'], 0)

    def test_07_near_caustic_is_unresolved_without_clipping(self):
        for beta in (2.0, math.nextafter(2.0, 0.0), math.nextafter(2.0, math.inf)):
            result = shell.solve_coefficients(2, beta, 1)
            self.assertEqual(result['status'], 'NEAR_CAUSTIC_UNRESOLVED')
            self.assertEqual(result['raw_discriminant'], beta*beta-4)
            self.assertIsNone(result['radial_weight_sum'])
            self.assertEqual(result['positive_roots'], [])
        c = 2/3
        r = shell.solve_radial(1, 0.5, 1, (0, 0, math.sqrt(2)/4), (math.sqrt(1-c*c), 0, c))
        self.assertEqual(r['status'], 'NEAR_CAUSTIC_UNRESOLVED')
        self.assertIsNone(r['density_dEA_dOmegaA_dOmegaB'])
        absent = shell.solve_radial(1, 0.5, 1, (0, 0, math.sqrt(2)/4), (1, 0, 0))
        self.assertEqual(absent['status'], 'NO_REAL_ROOTS')

    def test_08_normalization_and_invalid_directions(self):
        n = shell.normalize_direction((0, 0, 3))
        self.assertEqual(n['unit'], (0, 0, 1)); self.assertEqual(n['input_norm'], 3)
        self.assertTrue(n['normalization_applied'])
        for v in [(0, 0, 0), (1, 2), (1, 2, 3, 4), (1, math.nan, 0), (1, math.inf, 0)]:
            with self.assertRaises(ValueError): shell.normalize_direction(v)

    def test_09_coarea_jacobian_hand_fixture(self):
        result = shell.solve_radial(1, 0.5, 1, (0, 0, math.sqrt(2)/4), (0, 0, 5))
        roots = [(3*math.sqrt(2)-math.sqrt(10))/8, (3*math.sqrt(2)+math.sqrt(10))/8]
        sqrtD = math.sqrt(10)/4
        expected = math.sqrt(2)/4*sum(p*p for p in roots)/sqrtD
        self.close(result['density_dEA_dOmegaA_dOmegaB'], expected, 1e-10)
        for branch in result['branches']:
            derivative = abs(2*branch['p']-3*math.sqrt(2)/4)
            self.close(branch['inverse_radial_derivative'], 1/derivative, 1e-10)

    def test_10_swap_preserves_shell_and_recoil(self):
        a, b = (0.2, -0.1, 0.7), (-0.4, 0.3, 0.5)
        x = shell.shell_state(3, 0.5, 7, a, b); y = shell.shell_state(3, 0.5, 7, b, a)
        self.close(x['F'], y['F']); self.vector_close(x['Q'], y['Q'])
        self.close(x['EA'], y['EB']); self.close(x['ER'], y['ER'])

    def test_11_positive76_all_monomials_through_degree4(self):
        nodes = shell.sphere76_nodes(); self.assertEqual(len(nodes), 76)
        self.assertTrue(all(w > 0 for _, w in nodes))
        for degree in range(5):
            for indices in itertools.combinations_with_replacement(range(6), degree):
                actual = math.fsum(w*math.prod(x[i] for i in indices) for x, w in nodes)
                counts = [indices.count(i) for i in set(indices)]
                expected = 1 if degree == 0 else 1/6 if degree == 2 and counts == [2] else \
                    1/16 if degree == 4 and counts == [4] else 1/48 if degree == 4 and sorted(counts) == [2, 2] else 0
                self.close(actual, expected)

    def test_12_lab_moments_from_positive_nodes(self):
        E0, B, M = 2.0, 0.5, 3.0
        z = shell.parameters(E0, B, M); actual = []
        for x, w in shell.sphere76_nodes():
            q = tuple(math.sqrt(2*z['nu']*z['epsilon'])*v for v in x[:3])
            k = tuple(math.sqrt(2*z['mu']*z['epsilon'])*v for v in x[3:])
            lab = shell.from_jacobi(E0, M, q, k)
            state = shell.shell_state(E0, B, M, lab['p_A'], lab['p_B'])
            self.close(state['F'], 0)
            actual.append((state, w))
        oracle = shell.constant_weight_moments(E0, B, M)
        for name in ('EA', 'EB', 'ER'):
            self.close(math.fsum(s[name]*w for s, w in actual), oracle['means'][name])
        variance = math.fsum(w*(s['ER']-oracle['means']['ER'])**2 for s, w in actual)
        self.close(variance, oracle['recoil_energy_variance'])
        self.close(oracle['energy_closure'], 0)

    def test_13_volume_homogeneity_binding_modes_and_mass_limit(self):
        v = shell.phase_space_volume(2, 0.5, 3)
        self.close(shell.phase_space_volume(6, 1.5, 3), 9*v, scale=9*v)
        limit = 4*math.pi**3*1.5**2; ratios = []
        for M in (10, 100, 10000, 1e10):
            ratios.append(shell.phase_space_volume(2, 0.5, M)/limit)
        self.assertTrue(all(a < b < 1 for a, b in zip(ratios, ratios[1:])))
        self.close(ratios[-1], 1, 1e-9)
        M = 3; mu = Fraction(M, M+1); nu = Fraction(M+1, M+2)
        self.close(shell.parameters(2, float(mu/2), M)['threshold_E0'], float(mu/(2*nu)))
        self.assertNotEqual(shell.phase_space_volume(2, 0.5, M), shell.phase_space_volume(2, float(mu/2), M))
        r = shell.solve_radial(2, 0.5, 1e12, (0, 0, 0.5), (1, 0, 0))
        self.close(r['positive_roots'][0], math.sqrt(2*(2-0.5-0.125)), 1e-10)
        self.close(r['density_dEA_dOmegaA_dOmegaB'], 0.5*r['positive_roots'][0], 1e-10)

    def test_14_invalid_physical_inputs_and_vectors(self):
        for E0, B, M in [(0, 0.5, 1), (-1, 0.5, 1), (1, 0, 1), (1, -1, 1),
                          (1, 0.5, 0), (1, 0.5, -1), (math.inf, 0.5, 1),
                          (1, math.nan, 1), (1, 0.5, math.inf)]:
            with self.assertRaises(ValueError): shell.phase_space_volume(E0, B, M)
        with self.assertRaises(ValueError): shell.to_jacobi(1, 1, (1, 2), (0, 0, 0))
        with self.assertRaises(ValueError): shell.from_jacobi(1, 1, (0, 0, math.nan), (0, 0, 0))


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ShellTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {'unit': 'HE-ANG-FINITEMASS-SHELL', 'methods': result.testsRun,
              'failures': len(result.failures), 'errors': len(result.errors),
              'status': 'PASS' if result.wasSuccessful() else 'FAIL',
              'old_suite_replays': 0, 'acceptance': 'Frozen tolerances unchanged'}
    path = UNIT/'results/TEST_REPORT.json'; path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists(): raise RuntimeError('preserve existing test report; no automatic replay')
    path.write_text(json.dumps(report, indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
