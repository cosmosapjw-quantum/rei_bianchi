"""Targeted new CBA contracts only; no old suite import or replay."""
import cmath
import json
import math
from pathlib import Path
import unittest
import cba

UNIT = Path(__file__).resolve().parents[1]
TOL = json.loads((UNIT/'FROZEN_CONTRACT.json').read_text())['acceptance']['binary64_scaled_complex']


class CBAContracts(unittest.TestCase):
    def close(self, actual, expected, tol=TOL):
        self.assertLessEqual(abs(actual-expected)/max(1., abs(expected)), tol)

    def test_01_bad_scalars_and_vectors(self):
        for lam,q,p,e in [(0,[0,0,0],[0,0,1],1),(-1,[0,0,0],[0,0,1],1),
                          (1,[0,0],[0,0,1],1),(1,[0,0,1j],[0,0,1],1),
                          (1,[0,0,0],[0,0,0],1),(1,[0,0,0],[0,0,1],-1),
                          (float('nan'),[0,0,0],[0,0,1],1),(1,[float('inf'),0,0],[0,0,1],1),
                          (True,[0,0,0],[0,0,1],1),(1,[0,0,0],[0,0,1],1j)]:
            for fn in (cba.nordsieck_i,cba.overlap_k):
                with self.subTest(fn=fn.__name__,values=(lam,q,p,e)), self.assertRaises(ValueError):
                    fn(lam,q,p,e)
        for eta in [-1,1j,float('inf'),True]:
            with self.assertRaises(ValueError): cba.coulomb_normalizer(eta)
        with self.assertRaises(ValueError): cba.matched_overlap(1,[0,0],[0,0,1])

    def test_02_plane_wave_fourier_I(self):
        for lam,q in [(1.,(0,0,.2)),(1.4,(.3,-.2,.1))]:
            self.close(cba.nordsieck_i(lam,q,(0,0,.5),0),4*math.pi/(sum(v*v for v in q)+lam*lam))

    def test_03_plane_wave_fourier_K(self):
        for lam,q in [(1.,(0,0,.2)),(1.4,(.3,-.2,.1))]:
            A=sum(v*v for v in q)+lam*lam
            self.close(cba.overlap_k(lam,q,(0,0,.5),0),8*math.pi*lam/A**2)

    def test_04_branch_modulus(self):
        lam,q,pvec,eta=1.,(.3,0,-.9),(0,0,.7),1.2
        A=sum(v*v for v in q)+lam*lam; B=complex(A+2*sum(a*b for a,b in zip(q,pvec)),-2*lam*.7)
        I=cba.nordsieck_i(lam,q,pvec,eta)
        self.assertLess(cmath.phase(B),0)
        self.close(abs(I*A/(4*math.pi))**2,math.exp(2*eta*cmath.phase(B)))

    def test_05_nuclear_identity_at_fixed_eta(self):
        for lam,p,eta in [(1.,.5,.3),(1.4,1.2,.8),(1.,.25,0.)]:
            q=(0,0,-p); pv=(0,0,p)
            expected=2*cba.nordsieck_i(lam,q,pv,eta)*(lam-eta*p)/(p*p+lam*lam)
            self.close(cba.overlap_k(lam,q,pv,eta),expected)

    def test_06_matched_zero_is_exact(self):
        for lam,p in [(1.,.25),(1.4,.5),(1.,1.2)]:
            self.assertEqual(cba.matched_overlap(lam,(0,0,0),(0,0,p)),0j)
            self.assertEqual(cba.normalized_form_factor((0,0,0),(0,0,p),lam),0j)

    def test_07_moderate_matched_generic(self):
        for delta in [(.3,0,.2),(-.2,.4,.7),(1.,0,0)]:
            p=(0,0,.7);lam=1.4;q=tuple(a-b for a,b in zip(delta,p))
            self.close(cba.matched_overlap(lam,delta,p),cba.overlap_k(lam,q,p,lam/.7))

    def test_08_rotation_invariance(self):
        delta=(.2,-.3,.4); p=(.1,.2,.7)
        rotate=lambda v:(-v[1],v[0],v[2])
        self.close(cba.matched_overlap(1.,delta,p),cba.matched_overlap(1.,rotate(delta),rotate(p)))

    def test_09_gamma_strength_and_eta0(self):
        for eta in [0.,1e-8,.1,.7,2.,4.,10.]:
            self.close(abs(cba.coulomb_normalizer(eta))**2,cba.sommerfeld_strength(eta)/(2*math.pi)**3,
                       json.loads((UNIT/'FROZEN_CONTRACT.json').read_text())['acceptance']['normalized_strength_relative_or_abs_scaled'])
        self.close(cba.coulomb_normalizer(0),(2*math.pi)**-1.5)
        self.assertEqual(cba.sommerfeld_strength(0),1.)

    def test_10_plane_form_factor_keeps_nuclear_subtraction(self):
        delta=(.2,.1,.3);p=(0,0,.5);q=tuple(d-v for d,v in zip(delta,p))
        radial=lambda q:8*math.pi/(sum(v*v for v in q)+1)**2
        expected=(2*math.pi)**-1.5/math.sqrt(math.pi)*(radial(q)-radial(p))
        self.close(cba.normalized_form_factor(delta,p,eta=0),expected)
        self.assertNotEqual(radial(p),0.)

    def test_11_matched_form_factor_normalization(self):
        delta=(.4,.1,.2);p=(0,0,.5)
        self.close(cba.normalized_form_factor(delta,p),cba.coulomb_normalizer(2)/math.sqrt(math.pi)*cba.matched_overlap(1,delta,p))

    def test_12_delta_state_tdcs_coefficient(self):
        for model in ['cba','plane']:
            x=cba.direct_tdcs(250/27.2,5/27.2,(0,0,1),(.1,0,1),(.2,0,1),model)
            ratio=math.sqrt(2*x['Ef'])*math.sqrt(2*x['EB'])/math.sqrt(2*x['Ei'])
            delta_state=(2*math.pi)**4*ratio*abs(x['T_delta'])**2
            self.close(x['tdcs_au'],delta_state)
            self.assertGreaterEqual(x['tdcs_au'],0)
            self.assertEqual(x['units'],'a0^2/E_h')

    def test_13_tdcs_refuses_channel_endpoints_and_bad_models(self):
        for Ei,EB in [(1,.5),(.5,.1),(1,0),(1,-1),(float('inf'),.1)]:
            with self.assertRaises(ValueError): cba.direct_tdcs(Ei,EB,(0,0,1),(0,0,1),(0,0,1))
        with self.assertRaises(ValueError): cba.direct_tdcs(2,.3,(0,0,0),(0,0,1),(0,0,1))
        with self.assertRaises(ValueError): cba.direct_tdcs(2,.3,(0,0,1),(0,0,1),(0,0,1),'exchange')

    def test_14_direction_scaling_does_not_change_geometry(self):
        a=cba.direct_tdcs(2,.3,(0,0,1),(.1,0,1),(.3,0,1))
        b=cba.direct_tdcs(2,.3,(0,0,2),(.2,0,2),(.6,0,2))
        self.close(a['tdcs_au'],b['tdcs_au'])


if __name__=='__main__':
    import io
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(CBAContracts)
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    text=stream.getvalue();print(text,end='')
    path=UNIT/'results';path.mkdir(exist_ok=True)
    (path/'TEST_REPORT.json').write_text(json.dumps({'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'successful':result.wasSuccessful(),'log':text,'scope':'New CBA only; unchanged science replay0'},indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
