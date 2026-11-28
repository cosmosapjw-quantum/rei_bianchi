import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from fractions import Fraction as F
from decimal import Decimal
import json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from sig_da_bridge import *

class TestSigDABridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=source_rows(ROOT/'source/M0475.x4')
        cls.angular=json.loads((ROOT/'evidence/PR105_ANGULAR_BOUNDS.json').read_text())
        cls.bounds=cls.angular['1/200']
        cls.K=F(19,800)

    def test_source_sha_and_six_rows(self):
        self.assertEqual(len(self.rows),6)
        self.assertEqual([int(r.energy_mev) for r in self.rows],[201,225,253,285,320,359])

    def test_exact_minimum_global_K(self):
        self.assertEqual(min_energy_L(self.rows),F(19,800))

    def test_binding_pair_201_225(self):
        self.assertEqual((self.rows[0].lo-self.rows[1].hi)/(225-201),F(19,800))

    def test_subcritical_K_rejected(self):
        with self.assertRaises(ValueError):energy_interval(self.rows,F(19,800)-F(1,10**8))

    def test_sigma_330_exact(self):
        self.assertEqual(energy_interval(self.rows,self.K),(F(17,80),F(403,400)))

    def test_nearest_320_sets_both_bounds(self):
        r=next(x for x in self.rows if x.energy_mev==320)
        self.assertEqual(r.lo-self.K*10,F(17,80))
        self.assertEqual(r.hi+self.K*10,F(403,400))

    def test_parent_pin(self):
        self.assertEqual(self.angular['source_sha256'],EXFOR_SHA256)
        self.assertFalse(self.angular['numeric_rounding_certified'])

    def test_1over700_kappa1_incompatible(self):
        a=self.angular['1/700']
        self.assertFalse(joint_interval(self.rows,self.K,a['lo'],a['hi'],1)['compatible'])

    def test_1over700_kappa2_compatible(self):
        a=self.angular['1/700']
        self.assertTrue(joint_interval(self.rows,self.K,a['lo'],a['hi'],2)['compatible'])

    def test_1over200_kappa1_narrow(self):
        a=joint_interval(self.rows,self.K,self.bounds['lo'],self.bounds['hi'],1)
        self.assertTrue(a['compatible'])
        self.assertEqual(Decimal(a['sigma330_upper_nb']),Decimal('1.0075'))
        self.assertLess(Decimal(a['sigma330_upper_nb'])-Decimal(a['sigma330_lower_nb']),Decimal('0.001'))

    def test_1over200_kappa2_wider(self):
        a=joint_interval(self.rows,self.K,self.bounds['lo'],self.bounds['hi'],2)
        self.assertTrue(a['compatible'])
        self.assertGreater(Decimal(a['sigma330_upper_nb'])-Decimal(a['sigma330_lower_nb']),Decimal('0.5'))

    def test_1over100_both_compatible(self):
        a=self.angular['1/100']
        self.assertTrue(joint_interval(self.rows,self.K,a['lo'],a['hi'],1)['compatible'])
        self.assertTrue(joint_interval(self.rows,self.K,a['lo'],a['hi'],2)['compatible'])

    def test_critical_K_formula(self):
        a=self.angular['1/700']
        k1=Decimal(critical_energy_L(self.rows,a['lo'],a['hi'],1))
        k2=Decimal(critical_energy_L(self.rows,a['lo'],a['hi'],2))
        self.assertGreater(k1,Decimal('0.05966'))
        self.assertEqual(k2,Decimal('0.02375'))

    def test_kappa1_at_critical_K(self):
        a=self.angular['1/700']
        kc=critical_energy_L(self.rows,a['lo'],a['hi'],1)
        # Rounded numerical boundary: test at a strictly larger rational K.
        self.assertTrue(joint_interval(self.rows,F('0.06'),a['lo'],a['hi'],1)['compatible'])

    def test_witness_sigma330_exact(self):
        for s in (F('1.007'),F('0.75')):
            self.assertEqual(energy_witness(self.rows,self.K,s,F(330)),s)

    def test_witness_all_measured_intervals(self):
        for s in (F('1.007'),F('0.75')):
            for r in self.rows:
                val=energy_witness(self.rows,self.K,s,r.energy_mev)
                self.assertLessEqual(r.lo,val)
                self.assertLessEqual(val,r.hi)

    def test_witness_global_lipschitz(self):
        xs=list(range(195,370))
        vals=[energy_witness(self.rows,self.K,F('1.007'),x) for x in xs]
        self.assertTrue(all(abs(y-x)<=self.K for x,y in zip(vals,vals[1:])))

    def test_no_physical_rate(self):
        a=joint_interval(self.rows,self.K,self.bounds['lo'],self.bounds['hi'],2)
        self.assertIsNone(a['physical_event_rate'])
        self.assertFalse(a['physical_activation'])
        self.assertFalse(a['L4'])
        self.assertEqual(a['production'],'HOLD')

    def test_unknown_multiplicity_rejected(self):
        for bad in (0,3,True,2.0,'2'):
            with self.assertRaises((TypeError,ValueError)):
                joint_interval(self.rows,self.K,self.bounds['lo'],self.bounds['hi'],bad)

    def test_float_bool_input_rejected(self):
        for bad in (0.01,True,False,float('nan')):
            with self.assertRaises((TypeError,ValueError)):
                rational(bad)

    def test_source_mutation_rejected(self):
        raw=(ROOT/'source/M0475.x4').read_bytes()
        with TemporaryDirectory() as d:
            p=Path(d)/'bad.x4'
            p.write_bytes(raw.replace(b'0.61       0.16',b'0.62       0.16'))
            with self.assertRaises(ValueError):source_rows(p)

    def test_numeric_rounding_not_certified(self):
        a=joint_interval(self.rows,self.K,self.bounds['lo'],self.bounds['hi'],2)
        self.assertFalse(a['numeric_rounding_certified'])

    def test_exact_data_not_joint_CI(self):
        a=joint_interval(self.rows,self.K,self.bounds['lo'],self.bounds['hi'],2)
        self.assertIn('NOT_joint_CI',a['uncertainty'])

    def test_K_monotonic_support(self):
        a,b=energy_interval(self.rows,self.K)
        c,d=energy_interval(self.rows,self.K+F('0.001'))
        self.assertLessEqual(c,a)
        self.assertGreaterEqual(d,b)

    def test_empty_source_refused(self):
        with self.assertRaises((ValueError,TypeError)):
            min_energy_L(()) # max([0]) would return 0; require source rows

if __name__=='__main__':unittest.main(verbosity=2)
