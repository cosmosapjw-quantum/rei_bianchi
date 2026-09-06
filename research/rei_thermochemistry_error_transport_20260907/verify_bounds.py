#!/usr/bin/env python3
"""Exact small-matrix research checks, not a production chemistry solver."""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import unittest


def exact(x):
    if type(x) not in (int, F):
        raise ValueError('EXACT_RATIONAL_REQUIRED')
    return F(x)


def matrix(rows):
    n = len(rows)
    if not 1 <= n <= 8 or any(len(row) != n for row in rows):
        raise ValueError('SQUARE_SMALL_MATRIX_REQUIRED')
    return [[exact(x) for x in row] for row in rows]


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def mm(a, b):
    return [[sum(a[i][k]*b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]


def mv(a, v):
    return [sum(x*y for x, y in zip(row, v)) for row in a]


def minus(a, b):
    return [[x-y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def times(t, a):
    return [[t*x for x in row] for row in a]


def inverse(a):
    a = matrix(a)
    n = len(a)
    aug = [row + ident for row, ident in zip(a, eye(n))]
    for col in range(n):
        pivot = next((i for i in range(col, n) if aug[i][col]), None)
        if pivot is None:
            raise ValueError('SINGULAR_MATRIX')
        aug[col], aug[pivot] = aug[pivot], aug[col]
        scale = aug[col][col]
        aug[col] = [x/scale for x in aug[col]]
        for i in range(n):
            if i != col:
                scale = aug[i][col]
                aug[i] = [x-scale*y for x, y in zip(aug[i], aug[col])]
    return [row[n:] for row in aug]


def norm1(v):
    return sum(abs(x) for x in v)


def opnorm1(a):
    return max(sum(abs(a[i][j]) for i in range(len(a))) for j in range(len(a[0])))


def conjugate(a, w):
    return [[w[i]*a[i][j]/w[j] for j in range(len(a))] for i in range(len(a))]


def resolvent(a, h, w=None):
    a = matrix(a)
    h = exact(h)
    w = [F(1)]*len(a) if w is None else [exact(x) for x in w]
    if h < 0 or len(w) != len(a) or any(x <= 0 for x in w):
        raise ValueError('DOMAIN')
    if any(a[i][j] < 0 for i in range(len(a)) for j in range(len(a)) if i != j):
        raise ValueError('NOT_METZLER')
    if any(sum(w[i]*a[i][j] for i in range(len(a))) != 0 for j in range(len(a))):
        raise ValueError('NOT_CONSERVATIVE')
    return inverse(minus(eye(len(a)), times(h, a)))


def hydrogen(a, b):
    return matrix([[-a, b], [a, -b]])


def nonlinear(s):
    q = hydrogen(s*s, F(0))
    return mv(resolvent(q, 1), [1-s, s])


class BoundChecks(unittest.TestCase):
    def test_B01_hydrogen_closed_form(self):
        a, b, h = F(2), F(3), F(1, 5)
        d = 1+h*(a+b)
        closed = [[(1+h*b)/d, h*b/d], [h*a/d, (1+h*a)/d]]
        p = resolvent(hydrogen(a, b), h)
        self.assertEqual(p, closed)
        self.assertEqual(p, [[F(4,5), F(3,10)], [F(1,5), F(7,10)]])
        self.assertEqual(mm(minus(eye(2), times(h, hydrogen(a,b))), p), eye(2))

    def test_B02_hydrogen_helium_simplexes(self):
        q = matrix([[-2,3,0,0,0], [2,-3,0,0,0],
                    [0,0,-2,3,0], [0,0,2,-7,5], [0,0,0,4,-5]])
        for h in (F(0), F(1,100), F(1), F(1000)):
            p = resolvent(q, h)
            self.assertTrue(all(x >= 0 for row in p for x in row))
            self.assertEqual(opnorm1(p), 1)
            u = [F(1,4), F(3,4), F(1,3), F(1,2), F(1,6)]
            out = mv(p, u)
            self.assertEqual(sum(out[:2]), 1)
            self.assertEqual(sum(out[2:]), 1)

    def test_B03_weighted_conservation(self):
        q = hydrogen(F(2), F(3))
        w = [F(2), F(3)]
        a = [[q[i][j]*w[j]/w[i] for j in range(2)] for i in range(2)]
        p = resolvent(a, F(7,3), w)
        self.assertEqual(opnorm1(conjugate(p, w)), 1)
        self.assertEqual([sum(w[i]*p[i][j] for i in range(2)) for j in range(2)], w)

    def test_B04_resolvent_identity_and_sign_mutant(self):
        a, b, h = hydrogen(F(2), F(3)), hydrogen(F(5), F(7)), F(2,7)
        pa, pb = resolvent(a,h), resolvent(b,h)
        lhs = minus(pa,pb)
        rhs = times(h, mm(mm(pa,minus(a,b)),pb))
        self.assertEqual(lhs, rhs)
        self.assertNotEqual(lhs, times(-1,rhs))

    def test_B05_two_input_bound_and_fixed_map(self):
        a, b, h = hydrogen(F(2), F(3)), hydrogen(F(5), F(7)), F(1,7)
        u, v = [F(1,3),F(2,3)], [F(3,4),F(1,4)]
        pa, pb = resolvent(a,h), resolvent(b,h)
        error = norm1([x-y for x,y in zip(mv(pa,u),mv(pb,v))])
        bound = norm1([x-y for x,y in zip(u,v)]) + h*opnorm1(minus(a,b))*norm1(v)
        self.assertLessEqual(error,bound)
        same = norm1([x-y for x,y in zip(mv(pa,u),mv(pa,v))])
        self.assertLessEqual(same,norm1([x-y for x,y in zip(u,v)]))

    def test_B06_feedback_expansion_counterexample(self):
        s, t = F(1,4), F(1,2)
        us, ut = nonlinear(s), nonlinear(t)
        self.assertEqual(us[1], F(5,17))
        self.assertEqual(ut[1], F(3,5))
        self.assertEqual(sum(us),1)
        self.assertEqual(sum(ut),1)
        self.assertTrue(all(x>=0 for x in us+ut))
        gain = norm1([x-y for x,y in zip(ut,us)])/(2*(t-s))
        self.assertEqual(gain,F(104,85))
        self.assertGreater(gain,1)
        self.assertLessEqual(gain,3)

    def test_B07_composed_defect_budget(self):
        alpha, eta, e0 = [F(3,2),F(2),F(1)], [F(1,100),F(1,50),F(0)], F(1,20)
        running=e0
        for a,e in zip(alpha,eta):
            running=a*running+e
        def product(seq):
            ans=F(1)
            for x in seq: ans*=x
            return ans
        closed=product(alpha)*e0+sum(eta[j]*product(alpha[j+1:]) for j in range(len(eta)))
        self.assertEqual(running,closed)
        self.assertEqual(closed,F(19,100))
        self.assertGreater(closed,e0+sum(eta))

    def test_B08_equilibrium_zero_and_absorbing_rates(self):
        for h in (F(0),F(1),F(1000000)):
            self.assertEqual(resolvent(hydrogen(F(0),F(0)),h),eye(2))
            p=resolvent(hydrogen(F(2),F(3)),h)
            self.assertEqual(mv(p,[F(3,5),F(2,5)]),[F(3,5),F(2,5)])
            self.assertEqual(mv(resolvent(hydrogen(F(2),F(0)),h),[F(0),F(1)]),[F(0),F(1)])

    def test_B09_wrong_sign_and_transpose_mutants(self):
        q=hydrogen(F(2),F(3))
        wrong=inverse(minus(eye(2),times(F(-1,10),q)))
        self.assertTrue(any(x<0 for row in wrong for x in row))
        transposed=[list(row) for row in zip(*q)]
        with self.assertRaisesRegex(ValueError,'NOT_CONSERVATIVE'):
            resolvent(transposed,F(1,10))

    def test_B10_invalid_domain_rejected(self):
        for q,h in [([[-1,-1],[1,1]],1), ([[-1,2],[2,-2]],1), (hydrogen(1,2),-1)]:
            with self.assertRaises(ValueError): resolvent(q,h)
        for h in (True,0.1):
            with self.assertRaisesRegex(ValueError,'EXACT_RATIONAL_REQUIRED'):
                resolvent(hydrogen(1,2),h)
        with self.assertRaisesRegex(ValueError,'SQUARE_SMALL_MATRIX_REQUIRED'):
            resolvent([[1,2,3]],1)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--report',required=True)
    args=parser.parse_args()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BoundChecks)
    ids=[test.id() for test in suite]
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    passed=result.testsRun-len(result.failures)-len(result.errors)-len(result.skipped)
    success=result.wasSuccessful() and result.testsRun==10 and not result.skipped and len(set(ids))==10
    record={'status':'PASS_REI_CONDITIONAL_RESOLVENT_ORACLE' if success else 'FAIL_REI_CONDITIONAL_RESOLVENT_ORACLE',
            'tests':result.testsRun,'passed':passed,'failures':len(result.failures),
            'errors':len(result.errors),'skipped':len(result.skipped),'test_ids':ids,
            'arithmetic':'EXACT_FRACTION_SMALL_FIXTURES',
            'nonlinear_expansion_ratio':str(norm1([x-y for x,y in zip(nonlinear(F(1,2)),nonlinear(F(1,4)))])/F(1,2)),
            'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'python_version':sys.version,'production_imports':False,
            'production_mapping_verified':False,'actual_atomic_rates_used':False,
            'first_interval_admitted':False,'runtime_authorization_effect':'NONE'}
    with Path(args.report).open('x',encoding='utf-8') as output:
        json.dump(record,output,indent=2,sort_keys=True)
        output.write('\n')
    print(json.dumps(record,sort_keys=True))
    return 0 if success else 1


if __name__=='__main__':
    raise SystemExit(main())
