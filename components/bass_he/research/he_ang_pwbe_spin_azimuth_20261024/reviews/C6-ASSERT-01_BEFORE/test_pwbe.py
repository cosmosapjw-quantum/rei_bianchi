"""Frozen hand-oracle, independent spin-matrix and contract controls; no old suite."""
from fractions import Fraction as F
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch

import pwbe


class PWBEContract(unittest.TestCase):
    def close(self,a,b,rel=2e-13,absolute=2e-15):
        self.assertLessEqual(abs(a-b),max(absolute,rel*abs(b)),(a,b))

    def test_01_complex_hand_spin(self):
        c=pwbe.spin_channels(1+2j,3-1j)
        self.assertEqual(c,{'singlet':17.0,'triplet':13.0,'unpolarized':14.0})
        # Independently construct the four-spin M=D I-X P and Frobenius trace/4.
        D,X=1+2j,3-1j; swap=[0,2,1,3]
        trace=sum(abs((D if row==col else 0)-(X if row==swap[col] else 0))**2
                  for row in range(4) for col in range(4))/4
        self.close(trace,c['unpolarized'])

    def test_02_equal_amplitude_and_literal_Eq21(self):
        c=pwbe.spin_channels(2+1j,2+1j)
        self.assertEqual(c['triplet'],0);self.close(c['unpolarized'],5)
        # Printed real D^2+X^2-2DX is different from unpolarized D^2+X^2-DX.
        d=x=F(2); self.assertEqual(d*d+x*x-2*d*x,0)
        self.assertEqual(d*d+x*x-d*x,4)

    def test_03_azimuth_hand_fractions(self):
        expected={'I2':F(5,64),'I4':F(385,32768),'J2':F(-3,64),
                  'J4':F(-327,32768),'var_t':F(185,32768)}
        got=pwbe.azimuth_integrals(5,3)
        for k,v in expected.items():self.close(got[k],float(v))
        self.close(got['var_t'],got['I4']-got['I2']**2)

    def test_04_vector_source_hand_oracle(self):
        p=pwbe.pwbe_point(F(25,2),4,1,1/math.sqrt(2),0)
        for k,v in [('q2',5),('d',F(5,324)),('x',F(253,135252))]:
            self.close(p[k],float(v),absolute=2e-13 if k=='q2' else 2e-15)
        self.close(p['geometry']['DeltaA2'],1,absolute=2e-13)
        self.close(p['geometry']['DeltaB2'],13,absolute=2e-13)

    def test_05_transition_normalization_nuclear_subtractions(self):
        p=pwbe.pwbe_point(12.5,4,1,1/math.sqrt(2),0)
        # Exact reduced fractions are independent of the production difference formula.
        d,x=F(5,324),F(253,135252)
        w=float(d*d+x*x-d*x)
        expected=(32/math.pi**2)*(4*math.sqrt(8)/5)*w
        self.close(p['K'],expected)
        self.close(p['D'],math.sqrt(2)/math.pi**3*float(d))
        self.close(p['K'],(2*math.pi)**4*(4*math.sqrt(8)/5)*p['spin']['unpolarized'])
        nuclear_omitted=F(1,36)  # alpha*t for q²=5, DeltaA²=1
        self.assertNotEqual(float(d),float(nuclear_omitted))

    def test_06_positive_M0_polynomial_identity(self):
        for ma,mb in [(0.8,0.6),(-0.4,0.75),(1,0.2),(0.5,0.5)]:
            a=pwbe.pwbe_azimuth(100,40,ma,mb)
            self.assertGreaterEqual(a['M0'],0)
            self.close(a['M0'],a['M0_polynomial'],absolute=0)
            self.assertLessEqual(abs(a['cos_phi']),1+2e-12)
            self.assertLessEqual(abs(a['pair_dot']),1+2e-12)

    def test_07_b0_constant_uniform(self):
        a=pwbe.pwbe_azimuth(100,40,1,0.2)
        self.assertEqual(a['geometry']['b'],0)
        self.assertEqual(a['integrals']['J2'],0);self.assertEqual(a['integrals']['J4'],0)
        self.assertEqual(a['integrals']['var_t'],0);self.assertEqual(a['cos_phi'],0)
        for phi in [-1,0,1,math.pi]:
            self.close(pwbe.pwbe_point(100,40,1,.2,phi)['K'],a['Kbar'],absolute=0)
            self.close(pwbe.conditional_azimuth_pdf(100,40,1,.2,phi)['pdf'],1/(2*math.pi))

    def test_08_exact_outgoing_exchange(self):
        for phi in [.31,1.7,math.pi]:
            p=pwbe.pwbe_point(100,40,.8,.6,phi)
            q=pwbe.pwbe_point(100,59.5,.6,.8,-phi,ordered=False)
            self.close(p['D'],q['X'],rel=2e-12,absolute=0)
            self.close(p['X'],q['D'],rel=2e-12,absolute=0)
            self.close(p['K'],q['K'],rel=2e-12,absolute=0)

    def test_09_reflection_and_periodicity(self):
        p=pwbe.pwbe_point(100,40,-.4,.75,.71)
        for phi in [-.71,.71+8*math.pi]:
            self.close(pwbe.pwbe_point(100,40,-.4,.75,phi)['K'],p['K'],absolute=0)

    def test_10_equal_sharing_triplet_node(self):
        for phi in [0,.3,math.pi]:
            p=pwbe.pwbe_point(100,49.75,.5,.5,phi)
            self.close(p['d'],p['x'],absolute=0)
            scale=p['spin']['singlet'] or 1
            self.assertLessEqual(p['spin']['triplet']/scale,2e-13)
            self.close(p['K'],(2*math.pi)**4*(p['geometry']['kA']*p['geometry']['kB']/p['geometry']['k0'])*p['D']**2,absolute=0)

    def test_11_algebraic_zero_and_binary64_distinction(self):
        # Exact rational squared momenta: k0=3k, kA=kB=k, k²=1/7.
        q2=k2=F(1,7); t=1/(1+q2)**2;h=1/(1+k2)**2
        self.assertEqual(t-h,0)
        a=pwbe.pwbe_azimuth(F(9,14),F(1,14),1,1)
        self.assertGreaterEqual(a['M0'],0)  # tiny represented residual is not clipped.
        c=pwbe.conditional_azimuth_pdf(F(9,14),F(1,14),1,1,0)
        self.assertEqual(c['defined'],a['conditional_defined'])
        if not c['defined']:self.assertIsNone(c['pdf'])
        # Exercise the explicit computed-zero return contract independently of rounding.
        with patch.object(pwbe,'pwbe_azimuth',return_value={'conditional_defined':False}):
            self.assertIsNone(pwbe.conditional_azimuth_pdf(100,40,0,0,0)['pdf'])

    def test_12_invalid_energy_and_order(self):
        for E0,EB in [(.5,.1),(-1,.1),(100,0),(100,99.5),(100,70)]:
            with self.assertRaises(ValueError):pwbe.pwbe_point(E0,EB,0,0,0)
        self.assertGreaterEqual(pwbe.pwbe_point(100,70,0,0,0,ordered=False)['K'],0)

    def test_13_invalid_angles_nonfinite_and_types(self):
        for vals in [(100,40,1.01,0,0),(100,40,0,-1.01,0),(100,40,0,0,float('nan')),
                     (float('inf'),40,0,0,0),(True,40,0,0,0),(100,40,0,0,True)]:
            with self.assertRaises(ValueError):pwbe.pwbe_point(*vals)
        with self.assertRaises(ValueError):pwbe.pwbe_point(100,40,0,0,0,ordered=1)
        for z in [True,complex(float('inf'),1)]:
            with self.assertRaises(ValueError):pwbe.spin_channels(z,1)
        with self.assertRaises(ValueError):pwbe.spin_channels(1e308,1e308)
        with self.assertRaises(ValueError):pwbe.pwbe_point(1e308,1e307,0,0,0)

    def test_14_integral_domain_metadata_and_count(self):
        for a,b in [(0,0),(1,1),(1,-.1),(float('inf'),1)]:
            with self.assertRaises(ValueError):pwbe.azimuth_integrals(a,b)
        with self.assertRaises(ValueError):pwbe.azimuth_integrals(5,3,a_minus_b=2)
        with self.assertRaises(ValueError):pwbe.azimuth_integrals(5,3,a_minus_b=1,a_plus_b=8)
        p=pwbe.pwbe_point(100,49.75,.5,.5,0)
        self.assertEqual(p['geometry']['domain'],'ordered_equal_boundary')
        self.assertFalse(p['metadata']['source_Eq21_unpolarized_adopted'])
        self.assertFalse(p['metadata']['finite_mass_recoil_law'])
        self.assertIn('dE_B',p['metadata']['measure'])
        c=pwbe.pwbe_azimuth(100,40,.8,.6)
        q=pwbe.pwbe_point(100,40,.8,.6,.91)
        self.close(pwbe.conditional_azimuth_pdf(100,40,.8,.6,.91)['pdf'],q['K']/(2*math.pi*c['Kbar']),absolute=0)
        # Density already has the spin weights, equal boundary has no added half/count factor.
        self.close(p['K'],p['geometry']['P0']*p['w'],absolute=0)


if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(PWBEContract)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    out=Path(__file__).resolve().parents[1]/'results';out.mkdir(exist_ok=True)
    (out/'TEST_REPORT.json').write_text(json.dumps({'unit':'HE-ANG-PWBE-SPIN-AZIMUTH',
        'methods':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
        'passed':result.wasSuccessful(),'oracle':'root frozen hand fractions + independently constructed four-spin matrix; no old kernel',
        'zero_control':'Fraction analytic zero; binary64 residual not epsilon-clipped; computed-zero branch separately injected'},indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
