from __future__ import annotations
import unittest, sys, tempfile
from fractions import Fraction as Q
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import bridge as b

class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.w=('3/4','1/5','1/20');self.rho='1/2'
        self.y=['0']*17
        for i,v in [(1,'1/4'),(2,'1/8'),(3,'1/100'),(4,'1/200'),(5,'1/60'),(6,'1/80'),(7,'1/50'),(8,'1/80'),(9,'1/100'),(10,'1/25'),(11,'1/30'),(12,'1/40'),(13,'1/50'),(14,'1/90'),(15,'1/100'),(16,'1/120')]:self.y[i]=v
    def test_01_schema_source(self):self.assertEqual(len(b.parse_rows()),7)
    def test_02_charge_mapped_exact(self):self.assertEqual(b.projected_charge(self.y,self.rho,self.w),Q(self.rho)*(b.charge(self.y)-Q(self.y[6])))
    def test_03_augmented_exact(self):self.assertEqual(b.augmented_charge(self.y,self.rho,self.w),Q(self.rho)*b.charge(self.y))
    def test_04_seven_event_qS(self):
        S=b.photo_stoichiometry();self.assertEqual([sum((b.CHARGE[i]*S[i][k] for i in range(17))) for k in range(7)],[1]*7)
    def test_05_missing_T_event_only(self):self.assertEqual(b.event_charge_residual(self.rho,self.w),[Q(0),Q(0),-Q(self.rho),Q(0),Q(0),Q(0),Q(0)])
    def test_06_identity_any_weights(self):
        for w in [('1','2','3'),('1/11','1/13','1/17'),('3/4','1/5','1/20')]:
            self.assertEqual(b.augmented_charge(self.y,'2/3',w),Q(2,3)*b.charge(self.y))
    def test_07_source_rate_missing_T(self):
        s=b.source_defect(self.y,('2','3','5'),self.rho)
        self.assertEqual(s['electron_rate_per_nb_s']-s['projected_rate_per_nb_s'],s['remainder_rate_per_nb_s'])
        self.assertEqual(s['missing_T_event_per_Href_s'],Q(self.y[5])*2)
    def test_08_gamma_common_rescale_invariant(self):
        a=b.source_defect(self.y,('2','3','5'),self.rho)
        c=b.source_defect(self.y,('14','21','35'),self.rho)
        self.assertEqual(a['epsilon'],c['epsilon'])
    def test_09_upper_if_helium_positive(self):
        s=b.source_defect(self.y,('2','3','5'),self.rho)
        row=dict(H1_0=self.y[1],D_0=self.y[3],T_0=self.y[5])
        self.assertLessEqual(s['epsilon'],b.upper_fraction_from_row(row))
    def test_10_helium_zero_saturates_bound(self):
        s=b.source_defect(self.y,('2','0','0'),self.rho)
        row=dict(H1_0=self.y[1],D_0=self.y[3],T_0=self.y[5])
        self.assertEqual(s['epsilon'],b.upper_fraction_from_row(row))
    def test_11_zero_T_state(self):
        self.y[5]='0';self.y[6]='0'
        self.assertEqual(b.event_charge_residual(self.rho,self.w)[2],-Q(self.rho)) # structural failure remains
        self.assertEqual(b.source_defect(self.y,('2','3','5'),self.rho)['missing_T_event_per_Href_s'],0)
        self.assertEqual(b.projected_charge(self.y,self.rho,self.w),Q(self.rho)*b.charge(self.y))
    def test_12_minimal_one_scalar_counterexample(self):
        y2=list(self.y);y2[5]='0';y2[6]=str(Q(self.y[5])+Q(self.y[6]))
        self.assertEqual(b.map_state(self.y,self.rho,self.w),b.map_state(y2,self.rho,self.w))
        self.assertNotEqual(b.charge(self.y),b.charge(y2))
    def test_13_reject_float(self):
        with self.assertRaisesRegex(ValueError,'EXACT_INPUT'):b.isocharged_map(0.5,'1','1','1')
    def test_14_reject_invalid_weights(self):
        with self.assertRaisesRegex(ValueError,'POSITIVE'):b.isocharged_map('1','0','1','1')
    def test_15_reject_negative_rate(self):
        with self.assertRaisesRegex(ValueError,'NEGATIVE'):b.photo_rates(self.y,('1','-2','3'))
    def test_16_simplex_boundary_and_violation(self):
        self.assertTrue(b.admissible_charged_simplex(['1/2','1/4','1/4','1/8','1/8','1/8'],('1','1','1')))
        self.assertFalse(b.admissible_charged_simplex(['2','0','0','0','0','0'],('1','1','1')))
    def test_17_saved_pointwise_seven(self):self.assertEqual(len(b.endpoint_jet_report()['rows']),7)
    def test_18_saved_positive_rank_bound(self):
        for row in b.endpoint_jet_report()['rows']:
            self.assertGreater(Q(row['epsilon_upper_exact_fraction']),0)
            self.assertLess(Q(row['relative_twojet_defect_upper']),Q('1/100000000000000'))
    def test_19_twojet_rel_exact(self):
        for e in (Q(0),Q(1,4),Q(1,3),Q(1)):
            self.assertEqual(b.twojet_rel_defect_bound(e),1-(1-e)**2)
    def test_20_source_corruption_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'rows.json';p.write_bytes(b.DATA.read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'SHA_MISMATCH'):b.parse_rows(p)
    def test_21_physical_tau_refusal(self):
        with self.assertRaisesRegex(ValueError,'PHYSICAL_TAU_BLOCKED'):b.physical_tau()
    def test_22_normalization_sensitivity(self):
        self.assertNotEqual(b.map_state(self.y,'1/2',self.w),b.map_state(self.y,'1/3',self.w))
    def test_23_structure_baryon_number(self):
        S=b.photo_stoichiometry()
        for k in range(7):self.assertEqual(sum(S[i][k] for i in range(17)),0)
    def test_24_fixed_bounds_report(self):
        out=b.endpoint_jet_report()
        self.assertEqual(out['original_dag']['physical_delta'],0)
        self.assertEqual(out['ivp_count'],0)
if __name__=='__main__':unittest.main()
