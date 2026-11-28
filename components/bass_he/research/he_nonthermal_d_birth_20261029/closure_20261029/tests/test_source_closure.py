"""New/affected tests; the prior28 tests remain preserved, not replayed."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from nonthermal_d_birth import birth_source,REQUIRED_CLASS,MEV_TO_J,K0_MEV
from named_d_birth_min import source
from energy_gain import SexticLaw,FULL_WITNESS

class FloatingAlias(float): pass

class AffectedExact(unittest.TestCase):
    def test_rate_subclass_rejected(self):
        for fn in (lambda x:birth_source(x,source_class=REQUIRED_CLASS),lambda x:source(x,REQUIRED_CLASS)):
            with self.assertRaises(ValueError):fn(FloatingAlias(0.5))
    def test_both_direction_paths_reject_inexact(self):
        for n in ((1.,0.,0.),(True,False,False),(FloatingAlias(1),0,0)):
            for fn in (lambda:birth_source('1',source_class=REQUIRED_CLASS,photon_direction=n),lambda:source('1',REQUIRED_CLASS,n)):
                with self.assertRaises(ValueError):fn()
    def test_exact_compatibility_and_independent_SI(self):
        self.assertEqual(MEV_TO_J,F('0.0000000000001602176634'))
        a=source(Decimal('1.5'),REQUIRED_CLASS,('3/5','4/5',0))
        self.assertEqual(a['S_Dfast'],3);self.assertEqual(a['residual_J_m3s'],0)
        self.assertEqual(a['S_fast_kin_J_m3s'],3*K0_MEV*MEV_TO_J)

class EnergyGain(unittest.TestCase):
    def setUp(self):self.law=SexticLaw(FULL_WITNESS)
    def test_frozen_input_normalization(self):
        self.assertEqual(self.law.normalization,F(14297,52500))
        self.assertEqual(self.law.even_moment(0),1)
        self.assertEqual(self.law.even_moment(1),F(24377,71485))
    def test_independent_beta_polynomial_moments(self):
        law=SexticLaw((1,0,0))
        for k in range(8):self.assertEqual(law.even_moment(k),F(3,(2*k+1)*(2*k+3)))
    def test_asymmetric_partition_conservation(self):
        bins=self.law.bins(('-1','-4/5','-1/5','2/5','1'))
        self.assertEqual(sum(b['number'] for b in bins),2)
        self.assertEqual(sum(b['first_x'] for b in bins),0)
        self.assertEqual(sum(b['second_x'] for b in bins),2*self.law.even_moment(1))
        self.assertTrue(all(b['number']>=0 and b['second_x']>=0 for b in bins))
    def test_midpoint_mutation_breaks_energy(self):
        bins=self.law.bins(('-1','-4/5','-1/5','2/5','1'))
        self.assertNotEqual(sum(b['number']*(b['lo_x']+b['hi_x'])/2 for b in bins),0)
    def test_partition_additivity(self):
        bins=self.law.bins(('-1','-1/3','1/7','1'));whole=self.law.bins((-1,1))[0]
        for k in ('number','first_x','second_x'):self.assertEqual(sum(b[k] for b in bins),whole[k])
    def test_family_positivity_domain(self):
        for a in ((0,0,0),(-1,1,1),(1,-5,5),(1,2),(1.,0,0)):
            with self.assertRaises(ValueError):SexticLaw(a)
    def test_partition_domain(self):
        for es in ((-1,0,0,1),(-1,2,1),(0,1),(-1.,1),()):
            with self.assertRaises(ValueError):self.law.bins(es)
    def test_zero_order_review_finding_retained(self):
        t=self.law.trace_enclosure(0);u=t['universal']
        self.assertGreater(t['raw_upper_MeV_per_event'],u['upper_MeV_per_event'])
        self.assertEqual(t['upper_MeV_per_event'],u['upper_MeV_per_event'])
        self.assertEqual(t['lower_MeV_per_event'],u['lower_MeV_per_event'])
    def test_exact_nested_remainder_and_intersection(self):
        ts=[self.law.trace_enclosure(n) for n in range(7)]
        for t in ts:
            self.assertEqual(t['raw_upper_MeV_per_event']-t['raw_lower_MeV_per_event'],t['raw_width_MeV_per_event'])
            self.assertGreaterEqual(t['lower_MeV_per_event'],t['universal']['lower_MeV_per_event'])
            self.assertLessEqual(t['upper_MeV_per_event'],t['universal']['upper_MeV_per_event'])
        for a,b in zip(ts,ts[1:]):
            self.assertGreaterEqual(b['lower_MeV_per_event'],a['lower_MeV_per_event'])
            self.assertLessEqual(b['upper_MeV_per_event'],a['upper_MeV_per_event'])
            self.assertLessEqual(b['raw_width_MeV_per_event'],a['r']*a['raw_width_MeV_per_event'])
    def test_order_domain_and_physical_state(self):
        for n in (-1,33,1.,True):
            with self.assertRaises(ValueError):self.law.trace_enclosure(n)
        t=self.law.trace_enclosure(4)
        self.assertIsNone(t['physical_event_rate']);self.assertFalse(t['physical_activation'])
        self.assertLess(t['width_MeV_per_event'],F(1,10**12))

if __name__=='__main__':unittest.main()
