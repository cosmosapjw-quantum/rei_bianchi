"""Finite independent/negative checks for the AXBI diagnostic."""
import io, json, tempfile, unittest
from pathlib import Path
import numpy as np
import pandas as pd
from numpy.polynomial.legendre import leggauss
from background_stress import angular_moments, initial_angle_moments, forced_shear, AI, load

class PhysicsChecks(unittest.TestCase):
    def test_isotropic_limit_exact(self):
        M,F=angular_moments([0]); self.assertEqual(M[0],1); self.assertEqual(F[0],0)
    def test_initial_vs_local_angle(self):
        b=np.linspace(-.01,.01,31)
        a,c=angular_moments(b);d,e=initial_angle_moments(b)
        np.testing.assert_allclose(a,d,rtol=0,atol=1e-13)
        np.testing.assert_allclose(c,e,rtol=0,atol=1e-13)
    def test_exact_angular_energy_identity(self):
        mu,w=leggauss(96);w=w/2
        for b in [-.01,-.005,0,.005,.01]:
            D=(1-mu*mu)*np.exp(-2*b)+mu*mu*np.exp(4*b)
            Db=-2*(1-mu*mu)*np.exp(-2*b)+4*mu*mu*np.exp(4*b)
            Mb=np.sum(-2*Db/D**3*w)
            F=angular_moments([b],96)[1][0]
            self.assertLess(abs(Mb+2*F),5e-14)
    def test_small_b_coefficients(self):
        b=np.array([-.001,.001])
        M,F=angular_moments(b)
        Mp=1+8*b*b/5-16*b**3/21+8*b**4/35
        Fp=-8*b/5+8*b*b/7-16*b**3/35-40*b**4/231
        np.testing.assert_allclose(M,Mp,rtol=0,atol=2e-14)
        np.testing.assert_allclose(F,Fp,rtol=0,atol=2e-14)
    def test_stress_damps_prescribed_shear(self):
        b=np.linspace(-.01,.01,101)
        _,F=angular_moments(b)
        self.assertTrue(np.all(b*F<=1e-17))
    def test_pressure_positive_cone(self):
        M,F=angular_moments(np.linspace(-.1,.1,33))
        self.assertTrue(np.all((M+2*F)/3>0))
        self.assertTrue(np.all((M-F)/3>0))
    def test_linear_in_radiation_inventory(self):
        a=np.geomspace(AI,.2,101);b=.01*np.log(a/AI)
        d=forced_shear(a,b,.01,.000092)[2]
        h=forced_shear(a,b,.01,.000046)[2]
        np.testing.assert_array_equal(d,2*h)
    def test_hash_reject(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'bad.gz';p.write_bytes(b'wrong scenario')
            with self.assertRaisesRegex(ValueError,'SHA'):load(p)
    def test_nonfinite_reject(self):
        with self.assertRaises(ValueError):angular_moments([np.nan])
    def test_native_fixed_decimal_roundtrip(self):
        # Actual original native rate strings, not a synthetic physics input.
        h='0.00000000000000011835693720646417'
        s='-0.0000000000000000011835101980340537'
        d=pd.read_csv(io.StringIO('H,s\n'+h+','+s+'\n'),float_precision='round_trip')
        self.assertEqual(d.H.iloc[0],float(h));self.assertEqual(d.s.iloc[0],float(s))

if __name__=='__main__':unittest.main()
