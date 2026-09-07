#!/usr/bin/env python3
"""Small exact stage identities only; never imports/executes production source.

Uses the existing research matrix algebra, not a replacement REI solver.
Physical rates below are independent symbolic event operands with rational
fixture values. No actual atomic-rate evaluation or native execution occurs.
"""
from fractions import Fraction as F
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ALGEBRA = HERE.parent / 'rei_thermochemistry_error_transport_20260907/verify_bounds.py'
spec = importlib.util.spec_from_file_location('rei_existing_research_algebra', ALGEBRA)
alg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alg)


def addv(a, b):
    return [x+y for x, y in zip(a, b)]


def generator(flux, denominator):
    n = len(denominator)
    if any(d <= 0 for d in denominator):
        raise ValueError('POSITIVE_DENOMINATOR_REQUIRED')
    a = [[F(flux[i][j])/denominator[j] for j in range(n)] for i in range(n)]
    for j in range(n):
        a[j][j] = -sum(a[i][j] for i in range(n) if i != j)
    return a


def event_edges():
    # Nine event channels, matching event_uncertainty_operator.py:115-134.
    ion_h, ion_he1, ion_he2, hb, he2g, he2b, he3g, he3n2, cas = map(F, range(1, 10))
    y, y2a, y2b, z, v, f = F(1, 3), F(1, 5), F(2, 5), F(1, 2), F(2, 7), F(1, 10)
    ell, m, p = F(57, 40), F(737, 1000), F(24, 25)
    w = ell-m+m*y
    ah = v*w+(1-v)*f*z
    ahe = v*m*(1-y)+(1-v)*f*(1-z)
    return {
        (1, 0): ion_h+he2g*y+he2b*p+he3g*(1-y2a-y2b)+he3n2+cas*ah,
        (0, 1): hb,
        (3, 2): ion_he1+he2g*(1-y)+he3g*y2b+cas*ahe,
        (2, 3): he2g+he2b,
        (4, 3): ion_he2+he3g*y2a,
        (3, 4): he3g+he3n2+cas,
    }


def event_flux():
    out = [[F(0)]*5 for _ in range(5)]
    for (i, j), q in event_edges().items():
        out[i][j] = q
    return out


class StageChecks(unittest.TestCase):
    def test_S01_pinned_source_bytes(self):
        bindings = json.loads((HERE/'SOURCE_BINDINGS.json').read_text())
        for row in bindings['files']:
            with self.subTest(path=row['path']):
                self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(), row['sha256'])

    def test_S02_event_graph_and_three_population_solves(self):
        f0 = event_flux()
        y0 = list(map(F, [5, 7, 11, 13, 17]))
        h = F(1, 13)
        a0 = generator(f0, y0)
        pred = alg.mv(alg.resolvent(a0, h), y0)
        f1 = [[q*F(7, 6) for q in row] for row in f0]
        avg = [[(a+b)/2 for a, b in zip(ar, br)] for ar, br in zip(f0, f1)]
        ac = generator(avg, pred)
        for a, step in ((a0, h), (a0, h*F(2, 7)), (ac, h)):
            # 2/7 is only a rational step-scaling test; actual gamma is irrational.
            p = alg.resolvent(a, step)
            out = alg.mv(p, y0)
            self.assertEqual(sum(out[:2]), sum(y0[:2]))
            self.assertEqual(sum(out[2:]), sum(y0[2:]))
            self.assertTrue(all(x > 0 for x in out))
            self.assertEqual(alg.opnorm1(alg.conjugate(p, [F(2), F(2), F(3), F(3), F(3)])), 1)
            self.assertEqual(alg.mv(alg.minus(alg.eye(5), alg.times(step, a)), out), y0)
        self.assertEqual(alg.mv(a0, y0), [sum(f0[i])-sum(row[i] for row in f0) for i in range(5)])

    def test_S03_corrector_is_not_backward_euler_or_predictor_rhs(self):
        # Constant physical forward coefficient a=1, positive y0=(1,1), h=1.
        y0 = [F(1), F(1)]
        f0 = [[F(0), F(0)], [F(1), F(0)]]
        a0 = generator(f0, y0)
        pred = alg.mv(alg.resolvent(a0, 1), y0)
        f1 = [[F(0), F(0)], [pred[0], F(0)]]
        avg = [[(a+b)/2 for a, b in zip(ar, br)] for ar, br in zip(f0, f1)]
        ac = generator(avg, pred)
        correct = alg.mv(alg.resolvent(ac, 1), y0)
        wrong_rhs = alg.mv(alg.resolvent(ac, 1), pred)
        self.assertEqual(pred, [F(1, 2), F(3, 2)])
        self.assertEqual(ac[1][0], F(3, 2))
        self.assertEqual(correct, [F(2, 5), F(8, 5)])
        self.assertEqual(wrong_rhs, [F(1, 5), F(9, 5)])
        self.assertNotEqual(correct, pred)

    def test_S04_denominator_tangent_and_rust_lhs_sign(self):
        # q(theta)=(3+theta)/(2+2theta); exact dq(0)=-1.
        q, dq = F(3, 2), F(-1)
        y0, h = [F(1), F(1)], F(2, 3)
        a = alg.hydrogen(q, F(0)); da = alg.hydrogen(dq, F(0))
        p = alg.resolvent(a, h); z = alg.mv(p, y0)
        tangent = alg.mv(p, alg.mv(alg.times(h, da), z))
        # Independent quotient differentiation of z_HI=1/(1+h*q).
        closed = -h*dq/(1+h*q)**2
        self.assertEqual(tangent, [closed, -closed])
        self.assertEqual(closed, F(1, 6))
        dl = alg.times(-h, da)
        self.assertEqual(tangent, alg.mv(p, [-x for x in alg.mv(dl, z)]))
        wrong_da = alg.hydrogen(F(1, 2), F(0))  # omitted denominator derivative
        self.assertNotEqual(tangent, alg.mv(p, alg.mv(alg.times(h, wrong_da), z)))

    def test_S05_flux_denominator_variation_bound(self):
        f, g = F(3), F(7, 2)
        d, e, lower = F(2), F(5, 2), F(2)
        difference = abs(f/d-g/e)
        bound = abs(f-g)/lower+abs(g)*abs(d-e)/lower**2
        self.assertLessEqual(difference, bound)
        a, b = alg.hydrogen(f/d, 0), alg.hydrogen(g/e, 0)
        self.assertLessEqual(alg.opnorm1(alg.minus(a, b)), 2*bound)

    def test_S06_real_policy_jump_enters_population_edge(self):
        # Actual strict cell values on the sides of log10(T/K)=4.25.
        before, after = F(57, 200), F(61, 200)
        y, z, f = F(1, 2), F(1, 2), F(1, 10)
        w = F(57, 40)-F(737, 1000)+F(737, 1000)*y
        ah = lambda v: v*w+(1-v)*f*z
        jump = ah(after)-ah(before)
        self.assertEqual(jump, F(2013, 100000))
        # Unit cascade event operand and unit denominator, NOT measured REI rates.
        self.assertGreater(jump/F(1, 10**8), jump/F(1, 10**6))
        self.assertEqual(2*jump/F(1, 10**8), F(4026000))

    def test_S07_thermal_expansion_violates_closed_generator_hypothesis(self):
        # R=-2HU is the exact isolated expansion term, not a full-physics run.
        with self.assertRaisesRegex(ValueError, 'NOT_CONSERVATIVE'):
            alg.resolvent([[F(-2)]], F(1))
        # SDIRK2 at z=2Hh=4 has final numerator 5-4sqrt(2)<0.
        # Positive denominator: (1+gamma*z)^2=(5-2sqrt(2))^2.
        self.assertLess(F(5)**2, F(4)**2*2)
        self.assertGreater(F(5)**2, F(2)**2*2)
        # A positive log-T root cannot realize this negative final energy.

    def test_S08_thermal_block_sensitivity_keeps_cross_stage_term(self):
        # Rational operands for the derived triangular block differential.
        dg, df, c, bg, bf = F(2), F(3), F(5, 7), F(11), F(13)
        xg = bg/dg
        xf = (bf+c*xg)/df
        self.assertEqual(dg*xg, bg)
        self.assertEqual(-c*xg+df*xf, bf)
        self.assertNotEqual(xf, bf/df)
        self.assertEqual(xf, F(79, 14))

    def test_S09_step_doubling_is_not_a_defect_certificate(self):
        # Formal order-two map for u'=1: Psi_h(u)=u+h+h^3.
        # Even here the raw step difference underestimates the full-step defect.
        h = F(1, 10)
        full = h+h**3
        half_twice = h+2*(h/2)**3
        estimator = abs(full-half_twice)
        defect = abs(full-h)
        self.assertEqual(estimator, F(3, 4000))
        self.assertEqual(defect, F(1, 1000))
        self.assertLess(estimator, defect)

    def test_S10_nuclei_weights_do_not_conserve_particle_energy_weight(self):
        a = generator(event_flux(), list(map(F, [5, 7, 11, 13, 17])))
        for left in ([1, 1, 0, 0, 0], [0, 0, 1, 1, 1]):
            self.assertEqual([sum(left[i]*a[i][j] for i in range(5)) for j in range(5)], [0]*5)
        particles = [1, 2, 1, 2, 3]
        self.assertTrue(any(sum(particles[i]*a[i][j] for i in range(5)) != 0 for j in range(5)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(StageChecks)
    test_ids = [t.id() for t in suite]
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    record = {
        'status': 'PASS_STAGE_ALGEBRA_FIXTURES' if result.wasSuccessful() else 'FAIL_STAGE_ALGEBRA_FIXTURES',
        'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
        'skipped': len(result.skipped), 'test_ids': test_ids,
        'arithmetic': 'EXACT_FRACTION_AND_QUADRATIC_SIGN_COMPARISONS',
        'production_imports': False, 'actual_atomic_rates_evaluated': False,
        'native_invocations': 0, 'production_mapping_executable': False,
        'rate_derivative_bounds': 'UNKNOWN', 'rigorous_local_defect': 'UNKNOWN',
        'python': sys.version, 'executable': sys.executable,
        'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    args.report.write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(record, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
