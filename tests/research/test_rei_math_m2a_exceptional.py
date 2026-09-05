"""Frozen behavior tests for an independent exceptional-constraint oracle."""
import importlib.util
from pathlib import Path
import unittest
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
IMPL = ROOT / 'research/rei_math_m2a_exceptional/derive_exceptional.py'
_MODULE = None

class ExceptionalMomentumTests(unittest.TestCase):
    def setUp(self):
        global _MODULE
        self.assertTrue(IMPL.is_file(), 'M2A_IMPLEMENTATION_ABSENT')
        if _MODULE is None:
            spec = importlib.util.spec_from_file_location('rei_m2a', IMPL)
            _MODULE = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(_MODULE)
        self.mod = _MODULE
        self.d = _MODULE.derive()

    def zero(self, value):
        if isinstance(value, sp.MatrixBase):
            self.assertEqual(value.applyfunc(sp.simplify), sp.zeros(*value.shape))
        else:
            self.assertEqual(sp.simplify(value), 0)

    def fixture(self):
        d = self.d
        return {d['A']:1, d['N22']:3, d['N23']:0, d['N33']:-3, d['kappa']:1}

    def test_01_matrix_from_curvature(self):
        d = self.d
        A,a,b,c = (d[x] for x in ['A','N22','N23','N33'])
        target = sp.Matrix([[-3*A-b,-c],[a,b-3*A]])
        self.zero(d['L']-target)
        self.zero(d['carrier']-d['L']*d['sigma'])
        self.zero(d['momentum']+d['L']*d['sigma']+d['kappa']*d['q'])

    def test_02_determinant_and_trace(self):
        d = self.d
        self.zero(d['det']-(9*d['A']**2+d['N22']*d['N33']-d['N23']**2))
        self.zero(sp.trace(d['L'])+6*d['A'])

    def test_03_off_surface_projector_certificates(self):
        d = self.d
        A,L,D,P,Q = (d[x] for x in ['A','L','det','P','Q'])
        I = sp.eye(2)
        self.zero(L*L+6*A*L+D*I)
        self.zero(P*P-P+D*I/(36*A*A))
        self.zero(Q*Q-Q+D*I/(36*A*A))
        self.zero(L*Q+D*I/(6*A))
        self.zero(Q*L+D*I/(6*A))
        self.zero(L*d['general_solution']+d['kappa']*d['q']-d['kappa']*Q*d['q']+D*d['w']/(6*A))

    def test_04_generic_exceptional_chart(self):
        d = self.d
        sub = {d['N33']:(d['N23']**2-9*d['A']**2)/d['N22']}
        L,Q = (d[x].subs(sub) for x in ['L','Q'])
        self.zero(L.det())
        self.zero(L*Q)
        self.zero(Q*Q-Q)
        self.zero(sp.trace(Q)-1)
        self.assertEqual(L.rank(), 1)

    def test_05_compatible_and_incompatible_flux(self):
        d = self.d
        sub = self.fixture()
        good = dict(sub, **{})
        good.update({d['q'][0]:2,d['q'][1]:-2})
        bad = dict(sub)
        bad.update({d['q'][0]:1,d['q'][1]:1})
        self.zero((d['Q']*d['q']).subs(good))
        self.zero((d['L']*d['general_solution']+d['kappa']*d['q']).subs(good))
        self.assertEqual((d['Q']*d['q']).subs(bad),sp.Matrix([1,1]))

    def test_06_zero_N22_charts(self):
        d = self.d
        for b,q in [(3,(2,0)),(-3,(2,6))]:
            sub={d['A']:1,d['N22']:0,d['N23']:b,d['N33']:2,d['kappa']:1,d['q'][0]:q[0],d['q'][1]:q[1]}
            self.zero(d['det'].subs(sub))
            self.zero((d['Q']*d['q']).subs(sub))
            self.zero((d['L']*d['general_solution']+d['kappa']*d['q']).subs(sub))
            self.assertFalse(d['general_solution'].subs(sub).has(sp.zoo,sp.nan))

    def test_07_nonzero_flux_sign_mutation(self):
        d=self.d
        sub=self.fixture()
        sub.update({d['sigma'][0]:1,d['sigma'][1]:0,d['q'][0]:3,d['q'][1]:-3})
        self.zero(d['momentum'].subs(sub))
        old=(d['L']*d['sigma']-d['kappa']*d['q']).subs(sub)
        self.assertEqual(old,sp.Matrix([-6,6]))

    def test_08_free_shear_is_not_deleted(self):
        d=self.d
        S=sp.Symbol('S',nonzero=True,real=True)
        sub=self.fixture()
        sub.update({d['sigma'][0]:S,d['sigma'][1]:S,d['q'][0]:0,d['q'][1]:0})
        self.zero(d['momentum'].subs(sub))
        sub[d['sigma'][1]]=0
        self.assertEqual(d['momentum'].subs(sub),sp.Matrix([3*S,-3*S]))

    def test_09_near_exceptional_unbounded_solution(self):
        d=self.d
        e=sp.Symbol('delta',positive=True)
        L=d['L'].subs({d['A']:1,d['N22']:1,d['N23']:0,d['N33']:-9+e})
        self.zero(L.det()-e)
        exact=L.inv()*sp.Matrix([0,-1])
        self.zero(e*exact-sp.Matrix([9-e,3]))
        self.zero(L*sp.Matrix([1,0])+sp.Matrix([3,-1]))

    def test_10_claim_firewall(self):
        b=self.mod.claim_boundary()
        self.assertEqual(b['native_runtime'],'NOT_RUN')
        self.assertEqual(b['BASS_native_bridge'],'NOT_ADMITTED')
        self.assertEqual(b['constraint_propagation'],'NOT_PROVED')
        self.assertEqual(b['provider_export'],'NOT_AUTHORIZED')
        self.assertEqual(b['scope'],'ALGEBRAIC_CONSTRAINT_COMPATIBILITY_ONLY')
        self.assertEqual(b['visual_audit'],'PENDING_DIRECT_IMAGE_INSPECTION')

if __name__=='__main__':
    unittest.main(verbosity=2)
