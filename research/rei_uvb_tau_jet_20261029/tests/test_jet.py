import importlib.util
import json
import math
import pathlib
import random
import unittest
import tempfile
from fractions import Fraction
import mpmath as mp

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('jet',ROOT/'code/jet.py')
jet=importlib.util.module_from_spec(spec)
spec.loader.exec_module(jet)

class TestLocalJet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=jet.produce()
        cls.rows=cls.data['entries']

    def test_01_source_lock(self):
        self.assertEqual(len(self.rows),7)
        self.assertEqual(self.data['source_git_blob'],'526773ad659171389466a629e1f127c61ada53cd')

    def test_02_rank_one_input(self):
        for r in self.rows:
            self.assertAlmostEqual(r['source_kappa_direct'],(r['z_mean']-3.6)*r['normalized_tau_xx_beta'],delta=1e-29)

    def test_03_all_redshift_clock(self):
        for r in self.rows:
            self.assertAlmostEqual(r['d_z_dx'],-(1+r['z_mean']),places=14)
            self.assertLess(r['normalized_det_x'],0)

    def test_04_exact_fraction_unknown_J_cancellation(self):
        rng=random.Random(11129)
        for _ in range(200):
            a=Fraction(rng.randrange(1,100),rng.randrange(1,101))
            d=Fraction(rng.randrange(-50,51),rng.randrange(1,101))
            u=Fraction(rng.randrange(-100,101),rng.randrange(1,101))
            zp=Fraction(rng.randrange(-50,-1),rng.randrange(1,101))
            det=a*(d*u+a*zp)-(d*a)*u
            self.assertEqual(det,a*a*zp)

    def test_05_zero_signal_degeneracy(self):
        self.assertEqual(jet.determinant_from_jet(0,1.2,7,-3),0)
        self.assertEqual(jet.determinant_from_jet(1,1.2,7,0),0)

    def test_06_parameter_dependent_geometry_counterexample(self):
        # W(a)=exp(beta)*W0 and fixed y0 !=0 gives a direct tau_x response.
        # Hence the zero-first-jet precondition fails and our determinant is not applicable.
        mp.mp.dps=60
        W0=mp.mpf('2'); y0=mp.mpf('0.8'); eps=mp.mpf('1e-20')
        first=(W0*mp.exp(eps)*y0-W0*mp.exp(-eps)*y0)/(2*eps)
        self.assertLess(abs(first-W0*y0),mp.mpf('1e-35'))
        self.assertNotEqual(first,0)

    def test_07_nonzero_initial_tangent_counterexample(self):
        # y0(beta)=y00+beta/3; W=2 fixed, so D_beta tau_x(t0)=2/3 !=0.
        W=Fraction(2); v0=Fraction(1,3)
        self.assertEqual(W*v0,Fraction(2,3))
        self.assertNotEqual(W*v0,0)

    def test_08_arbitrary_full_J_and_dB(self):
        rng=random.Random(121)
        for _ in range(100):
            W=rng.uniform(.1,10);Wp=rng.uniform(-3,3)
            b=[rng.uniform(-1,1) for _ in range(4)]
            q=[rng.uniform(-1,1) for _ in range(4)]
            J=[[rng.uniform(-2,2) for _ in range(4)] for _ in range(4)]
            db=[rng.uniform(-2,2) for _ in range(4)]
            d=rng.uniform(-1,2);dp=rng.uniform(-5,-.5)
            g=sum(q[i]*b[i] for i in range(4))
            u=2*Wp*g+W*sum(q[i]*(sum(J[i][j]*b[j] for j in range(4))+db[i]) for i in range(4))
            k3=d*u+W*dp*g
            det=(W*g)*k3-(W*d*g)*u
            self.assertAlmostEqual(det,(W*g)**2*dp,delta=1e-10*max(1,abs(det)))

    def test_09_high_precision_direct_taylor(self):
        # Independent analytic toy F(t,a)=s0 exp(L*(beta+kappa*(z(t)-3.6))),
        # tau_t=W*y, y(t0)=y0 independent a. No IVP integration.
        mp.mp.dps=120
        z=mp.mpf('3.603019593287379'); zp=mp.mpf('-0.2')
        s0=mp.mpf('0.0023'); W=mp.mpf('0.73'); L=mp.log(10)
        beta=mp.mpf('-0.04591874303144475');kappa=mp.mpf('0.0686617394805907')
        d=z-mp.mpf('3.6')
        def jetpair(b,k):
            f=s0*mp.exp(L*(b+k*d))
            return W*f, W*f*L*k*zp
        eps=mp.mpf('1e-35')
        b2=(jetpair(beta+eps,kappa)[0]-jetpair(beta-eps,kappa)[0])/(2*eps)
        k2=(jetpair(beta,kappa+eps)[0]-jetpair(beta,kappa-eps)[0])/(2*eps)
        b3=(jetpair(beta+eps,kappa)[1]-jetpair(beta-eps,kappa)[1])/(2*eps)
        k3=(jetpair(beta,kappa+eps)[1]-jetpair(beta,kappa-eps)[1])/(2*eps)
        det=b2*k3-k2*b3
        self.assertLess(abs(det-b2*b2*zp)/abs(b2*b2*zp),mp.mpf('1e-65'))

    def test_10_local_jet_not_global_tau(self):
        self.assertFalse(self.data['L4_ready'])
        self.assertEqual(self.data['new_ivp_count'],0)
        self.assertEqual(self.data['dag']['physical_delta'],0)
        self.assertIn('actual BASS K/nHref/H binding',self.data['not_claimed'])

    def test_11_invalid_inputs(self):
        for args in [(float('nan'),1.),(2.,1.),(4.,-1.),(3.,float('inf'))]:
            with self.assertRaises(ValueError):jet.mean_log_clock_jet(*args)

    def test_12_envelope_is_monotone_exact_image(self):
        saved=jet.load_saved()['entries']
        for row,orig in zip(self.rows,saved):
            for scope in ('deterministic','joint2_95'):
                lo,hi=orig['envelopes'][scope]['electron_per_Href_s']
                out=row[scope+'_normalized_absdet_interval']
                self.assertGreater(out[0],0)
                self.assertLessEqual(out[0],out[1])
                self.assertAlmostEqual(out[0],(1+row['z_mean'])*(math.log(10)*lo)**2,delta=1e-42)
                self.assertAlmostEqual(out[1],(1+row['z_mean'])*(math.log(10)*hi)**2,delta=1e-42)

    def test_13_bundled_source_standalone_restore(self):
        original=jet.SOURCE
        try:
            jet.SOURCE=jet.BUNDLED_SOURCE
            self.assertEqual(len(jet.load_saved()['entries']),7)
        finally:
            jet.SOURCE=original

    def test_14_corrupted_source_rejected(self):
        original=jet.SOURCE
        with tempfile.TemporaryDirectory() as temp:
            p=pathlib.Path(temp)/'RESULT.json'
            raw=jet.BUNDLED_SOURCE.read_bytes()
            p.write_bytes(raw[:-1]+(b'X' if raw[-1:]!=b'X' else b'Y'))
            try:
                jet.SOURCE=p
                with self.assertRaisesRegex(ValueError,'SHA256_MISMATCH'):
                    jet.load_saved()
            finally:
                jet.SOURCE=original

    def test_15_representative_numerical_anchor(self):
        r=self.rows[3]
        self.assertAlmostEqual(r['normalized_tau_xx_beta'],7.897347539553934e-16,delta=1e-29)
        self.assertAlmostEqual(r['normalized_det_x'],-2.87081577828772e-30,delta=1e-42)

if __name__=='__main__':unittest.main()
