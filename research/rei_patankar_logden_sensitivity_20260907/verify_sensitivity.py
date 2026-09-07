#!/usr/bin/env python3
"""Exact research oracle for Patankar denominator sensitivity, not production."""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / 'research/rei_thermochemistry_error_transport_20260907/verify_bounds.py'
spec = importlib.util.spec_from_file_location('rei_logden_exact_helper', HELPER)
if spec is None or spec.loader is None:
    raise RuntimeError('EXACT_HELPER_UNAVAILABLE')
R = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = R
spec.loader.exec_module(R)
MPRK = ROOT / ('stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R1_'
               'POSITIVITY_CONSERVATIVE_SECOND_ORDER_THERMOCHEMISTRY_PREFLIGHT/analysis/mprk22.py')
MEASUREMENTS = {}


def vector(values, n):
    if len(values) != n:
        raise ValueError('SHAPE')
    return [R.exact(x) for x in values]


def column_matrix(flux):
    k = R.matrix(flux)
    n = len(k)
    if any(k[j][j] != 0 for j in range(n)):
        raise ValueError('NONZERO_SELF_TRANSFER')
    for j in range(n):
        k[j][j] = -sum(k[i][j] for i in range(n) if i != j)
    return k


def stage(flux, d, b, h, w=None):
    f = R.matrix(flux)
    n = len(f)
    d, b = vector(d, n), vector(b, n)
    if any(x <= 0 for x in d) or any(x < 0 for x in b):
        raise ValueError('POPULATION_DOMAIN')
    if any(x < 0 for row in f for x in row):
        raise ValueError('NEGATIVE_FLUX')
    k = column_matrix(f)
    a = [[k[i][j]/d[j] for j in range(n)] for i in range(n)]
    p = R.resolvent(a, h, w)
    return p, R.mv(p, b), a


def response(flux, d, b, h, df, dd, db, w=None):
    p, v, a = stage(flux, d, b, h, w)
    n = len(v)
    d, dd, db = vector(d, n), vector(dd, n), vector(db, n)
    kdf = column_matrix(df)
    r = [dd[j]/d[j] for j in range(n)]
    base = R.mv(p, db)
    fpart = [h*x for x in R.mv(p, R.mv(kdf, [v[j]/d[j] for j in range(n)]))]
    dpart = R.mv(R.minus(R.eye(n), p), [v[j]*r[j] for j in range(n)])
    total = [base[i]+fpart[i]+dpart[i] for i in range(n)]
    return total, dpart, fpart


def wn(v, w):
    return sum(wi*abs(vi) for wi, vi in zip(w, v))


def add(u, v):
    return [x+y for x, y in zip(u, v)]


def sub(u, v):
    return [x-y for x, y in zip(u, v)]


def zeros(n):
    return [[Q(0) for _ in range(n)] for _ in range(n)]


def hflux(forward, reverse):
    return [[Q(0), forward*0+reverse], [forward, Q(0)]]


@dataclass(frozen=True)
class Dual:
    val: Q
    dot: Q = Q(0)

    def __post_init__(self):
        object.__setattr__(self, 'val', R.exact(self.val))
        object.__setattr__(self, 'dot', R.exact(self.dot))

    @staticmethod
    def coerce(x):
        return x if isinstance(x, Dual) else Dual(R.exact(x))

    def __add__(self, other):
        z = self.coerce(other)
        return Dual(self.val+z.val, self.dot+z.dot)

    __radd__ = __add__

    def __neg__(self):
        return Dual(-self.val, -self.dot)

    def __sub__(self, other):
        return self + (-self.coerce(other))

    def __rsub__(self, other):
        return self.coerce(other) - self

    def __mul__(self, other):
        z = self.coerce(other)
        return Dual(self.val*z.val, self.dot*z.val+self.val*z.dot)

    __rmul__ = __mul__

    def __truediv__(self, other):
        z = self.coerce(other)
        return Dual(self.val/z.val, (self.dot*z.val-self.val*z.dot)/(z.val*z.val))

    def __rtruediv__(self, other):
        return self.coerce(other) / self


def closed(forward, reverse, d, b, h):
    # Separate closed-form two-state solve; works for Fraction or Dual inputs.
    a, beta = forward/d[0], reverse/d[1]
    det = 1+h*(a+beta)
    return [((1+h*beta)*b[0]+h*beta*b[1])/det,
            (h*a*b[0]+(1+h*a)*b[1])/det]


def log_abs_upper(x, terms=32):
    # For rational x>0 use the atanh series and a rigorous positive tail bound.
    x = R.exact(x)
    if x <= 0:
        raise ValueError('LOG_DOMAIN')
    if x < 1:
        x = 1/x
    z = (x-1)/(x+1)
    lower = 2*sum(z**(2*k+1)/Q(2*k+1) for k in range(terms))
    tail = 2*z**(2*terms+1)/(Q(2*terms+1)*(1-z*z))
    return lower+tail


class SensitivityChecks(unittest.TestCase):
    def test_D01_pinned_source_and_helper(self):
        data = MPRK.read_bytes()
        blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        self.assertEqual(blob, 'a3bf57e9ec09cc7cf5f5d221048cd02000a281b4')
        self.assertEqual(hashlib.sha256(HELPER.read_bytes()).hexdigest(),
                         'f7b7d7e474ee5877c223ef8ccd5b78659dc2214b0002ea11b247607b3dacaf6b')

    def test_D02_denominator_cancellation_against_implicit_tangent(self):
        f = [[0,3,0,0,0], [2,0,0,0,0], [0,0,0,3,0], [0,0,2,0,5], [0,0,0,4,0]]
        d, b = list(map(Q,[2,3,4,5,6])), list(map(Q,[1,2,3,4,5]))
        dd, h = [Q(1,3),Q(-1,7),Q(2,5),Q(-3,8),Q(1,9)], Q(2,7)
        p, v, a = stage(f,d,b,h)
        da = [[-a[i][j]*dd[j]/d[j] for j in range(5)] for i in range(5)]
        implicit = [h*x for x in R.mv(p,R.mv(da,v))]
        total, dp, _ = response(f,d,b,h,zeros(5),dd,[0]*5)
        self.assertEqual(total,implicit)
        self.assertEqual(dp,implicit)
        self.assertNotEqual(dp,[Q(0)]*5)
        self.assertEqual(sum(dp),0)

    def test_D03_total_tangent_against_independent_dual_closed_form(self):
        f, d, b, h = hflux(Q(2),Q(3)), [Q(4),Q(5)], [Q(6),Q(7)], Q(2,3)
        df, dd, db = hflux(Q(1,2),Q(-2,5)), [Q(1,7),Q(-1,11)], [Q(-1,3),Q(2,9)]
        total, _, _ = response(f,d,b,h,df,dd,db)
        out = closed(Dual(2,Q(1,2)),Dual(3,Q(-2,5)),
                     [Dual(x,dx) for x,dx in zip(d,dd)],
                     [Dual(x,dx) for x,dx in zip(b,db)],h)
        self.assertEqual([x.val for x in out],stage(f,d,b,h)[1])
        self.assertEqual([x.dot for x in out],total)

    def test_D04_exact_finite_denominator_identity(self):
        f = [[0,3,0],[2,0,5],[0,4,0]]
        d,e,b,h = [Q(2),Q(3),Q(4)],[Q(5),Q(2),Q(7)],[Q(1),Q(2),Q(3)],Q(7,11)
        pd,vd,_ = stage(f,d,b,h)
        pe,ve,_ = stage(f,e,b,h)
        rhs = R.mv(R.minus(R.eye(3),pd),[ve[j]*(d[j]/e[j]-1) for j in range(3)])
        self.assertEqual(sub(vd,ve),rhs)
        self.assertNotEqual(sub(vd,ve),[-x for x in rhs])

    def test_D05_weighted_column_norm_and_denominator_bound(self):
        f = [[0,3,0,0,0], [2,0,0,0,0], [0,0,0,3,0], [0,0,2,0,5], [0,0,0,4,0]]
        d,b,w,h = [Q(2),Q(3),Q(4),Q(5),Q(6)],[Q(1)]*5,[Q(2),Q(2),Q(7),Q(7),Q(7)],Q(5,2)
        p,v,_ = stage(f,d,b,h,w)
        for j in range(5):
            col = [Q(i==j)-p[i][j] for i in range(5)]
            self.assertEqual(wn(col,w),2*w[j]*(1-p[j][j]))
        r = [Q(1),Q(-1,2),Q(2,3),Q(-2),Q(1,7)]
        _,dp,_ = response(f,d,b,h,zeros(5),[d[j]*r[j] for j in range(5)],[0]*5,w)
        sharp = 2*sum(w[j]*v[j]*(1-p[j][j])*abs(r[j]) for j in range(5))
        self.assertLessEqual(wn(dp,w),sharp)
        self.assertLessEqual(sharp,2*sum(x*y for x,y in zip(w,b))*max(map(abs,r)))

    def test_D06_finite_relative_log_and_mass_bounds(self):
        f,b,h = hflux(Q(2),Q(3)),[Q(1,3),Q(2,3)],Q(7,5)
        for d,e in [([Q(1),Q(1)],[Q(2),Q(3,2)]),
                    ([Q(1,100),Q(1,50)],[Q(1,50),Q(1,75)]),
                    ([Q(1),Q(2)],[Q(1),Q(2)])]:
            pd,vd,_ = stage(f,d,b,h)
            pe,ve,_ = stage(f,e,b,h)
            error = R.norm1(sub(vd,ve))
            ratio = [abs(d[j]/e[j]-1) for j in range(2)]
            sharp = 2*sum(ve[j]*(1-pd[j][j])*ratio[j] for j in range(2))
            self.assertLessEqual(error,sharp)
            self.assertLessEqual(error,2)
            log_upper = max(log_abs_upper(e[j]/d[j]) for j in range(2))
            self.assertLessEqual(error,2*min(Q(1),log_upper))

    def test_D07_small_denominator_can_have_small_output_response(self):
        rows=[]
        for k in (0,3,6,12,18):
            eps=Q(1,10**k)
            f,d,b=hflux(Q(1),Q(0)),[eps,Q(1)],[Q(1),Q(1)]
            _,dp,_=response(f,d,b,Q(1),zeros(2),[eps,Q(0)],[0,0])
            gain=R.norm1(dp)
            self.assertEqual(gain,2*eps/(1+eps)**2)
            self.assertLessEqual(gain,4)
            coarse=4/eps
            self.assertGreaterEqual(coarse,gain)
            rows.append({'epsilon':str(eps),'exact_log_response':str(gain),'coarse_generator_bound':str(coarse)})
        MEASUREMENTS['one_way_small_denominator']=rows

    def test_D08_absolute_derivative_can_diverge(self):
        rows=[]
        for k in (0,3,6,12,18):
            eps=Q(1,10**k)
            f,d,b=hflux(Q(1),Q(1)),[eps,eps],[Q(1,2),Q(1,2)]
            _,rel,_=response(f,d,b,Q(1),zeros(2),[eps,Q(0)],[0,0])
            _,absolute,_=response(f,d,b,Q(1),zeros(2),[Q(1),Q(0)],[0,0])
            self.assertEqual(R.norm1(rel),1/(eps+2))
            self.assertEqual(R.norm1(absolute),1/(eps*(eps+2)))
            self.assertLessEqual(R.norm1(rel),Q(1,2))
            if k>=3:
                self.assertGreater(R.norm1(absolute),100)
            rows.append({'epsilon':str(eps),'relative_gain':str(R.norm1(rel)),'absolute_gain':str(R.norm1(absolute))})
        MEASUREMENTS['absolute_boundary_counterexample']=rows

    def test_D09_flux_feedback_cannot_be_discarded(self):
        f,df,d,b,h=hflux(Q(1),Q(2)),hflux(Q(1),Q(-1)),[Q(2),Q(3)],[Q(1),Q(1)],Q(2,5)
        total,dp,fp=response(f,d,b,h,df,[0,0],[0,0])
        _,v,_=stage(f,d,b,h)
        self.assertEqual(dp,[Q(0),Q(0)])
        self.assertEqual(total,fp)
        self.assertNotEqual(total,dp)
        bound=2*h*sum(v[j]/d[j]*sum(abs(df[i][j]) for i in range(2) if i!=j) for j in range(2))
        self.assertLessEqual(R.norm1(fp),bound)
        self.assertEqual(sum(fp),0)

    def test_D10_actual_mprk22_chain_against_dual_closed_form(self):
        def flux(y):
            return [[0,2*y[1]],[y[0]*(1+y[1]),0]]
        def vals(m):
            return [[x.val if isinstance(x,Dual) else Q(x) for x in row] for row in m]
        def dots(m):
            return [[x.dot if isinstance(x,Dual) else Q(0) for x in row] for row in m]
        y,dy,h=[Q(2,3),Q(1,3)],[Q(1,7),Q(-1,7)],Q(1,5)
        yd=[Dual(a,da) for a,da in zip(y,dy)]
        f0d=flux(yd)
        ypd=closed(f0d[1][0],f0d[0][1],yd,yd,h)
        f1d=flux(ypd)
        bard=[[(f0d[i][j]+f1d[i][j])/2 for j in range(2)] for i in range(2)]
        ycd=closed(bard[1][0],bard[0][1],ypd,yd,h)
        f0,df0=vals(f0d),dots(f0d)
        _,yp,_=stage(f0,y,y,h)
        dyp,_,_=response(f0,y,y,h,df0,dy,dy)
        self.assertEqual(dyp,[x.dot for x in ypd])
        f1m=flux([Dual(a,da) for a,da in zip(yp,dyp)])
        bar=R.times(Q(1,2),[[f0[i][j]+vals(f1m)[i][j] for j in range(2)] for i in range(2)])
        dbar=R.times(Q(1,2),[[df0[i][j]+dots(f1m)[i][j] for j in range(2)] for i in range(2)])
        dyc,dc,_=response(bar,yp,y,h,dbar,dyp,dy)
        self.assertEqual(stage(bar,yp,y,h)[1],[x.val for x in ycd])
        self.assertEqual(dyc,[x.dot for x in ycd])
        self.assertNotEqual(dyc,sub(dyc,dc))
        self.assertEqual(sum(dyc),sum(dy))
        MEASUREMENTS['mprk22_corrector_tangent']=[str(x) for x in dyc]

    def test_D11_zero_limits_and_invalid_domain(self):
        f,d,b=hflux(Q(2),Q(3)),[Q(2),Q(3)],[Q(1),Q(2)]
        db=[Q(1,3),Q(-1,5)]
        self.assertEqual(response(f,d,b,Q(0),f,[Q(1),Q(1)],db)[0],db)
        self.assertEqual(response(zeros(2),d,b,Q(2),zeros(2),[Q(1),Q(1)],db)[0],db)
        for bad_d,bad_b,bad_f in [([0,1],b,f),(d,[-1,2],f),(d,b,[[0,-1],[1,0]])]:
            with self.assertRaises(ValueError): stage(bad_f,bad_d,bad_b,Q(1))
        with self.assertRaisesRegex(ValueError,'EXACT_RATIONAL_REQUIRED'):
            stage(f,d,b,0.1)

    def test_D12_rhs_mass_and_denominator_sign_mutations(self):
        f,d,b,h=hflux(Q(2),Q(3)),[Q(2),Q(4)],[Q(1),Q(2)],Q(1,3)
        db=[Q(2),Q(-1)]
        total,dp,fp=response(f,d,b,h,zeros(2),[Q(1,2),Q(-1,3)],db)
        p,_,_=stage(f,d,b,h)
        self.assertEqual(sum(total),sum(db))
        self.assertEqual(sum(dp),0)
        self.assertNotEqual(total,sub(R.mv(p,db),dp))
        self.assertNotEqual(total,dp)
        self.assertEqual(fp,[Q(0),Q(0)])


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--report',required=True)
    args=parser.parse_args()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(SensitivityChecks)
    ids=[test.id() for test in suite]
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    success=result.wasSuccessful() and result.testsRun==12 and len(set(ids))==12 and not result.skipped
    record={'status':'PASS_CONDITIONAL_LOGDEN_SENSITIVITY_ORACLE' if success else 'FAIL_CONDITIONAL_LOGDEN_SENSITIVITY_ORACLE',
            'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
            'test_ids':ids,'arithmetic':'EXACT_FRACTION_AND_FORWARD_DUAL_SMALL_FIXTURES',
            'measurements':MEASUREMENTS,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'production_imports':False,'actual_atomic_rates_evaluated':False,
            'rate_derivative_bounds':'UNKNOWN','thermal_coupled_bound':'UNKNOWN','exact_flow_defect_rho':'UNKNOWN',
            'first_interval_admitted':False,'authority_effect':'NONE','python_version':sys.version}
    with Path(args.report).open('x',encoding='utf-8') as stream:
        json.dump(record,stream,indent=2,sort_keys=True)
        stream.write('\n')
    print(json.dumps(record,sort_keys=True))
    return 0 if success else 1


if __name__=='__main__':
    raise SystemExit(main())
