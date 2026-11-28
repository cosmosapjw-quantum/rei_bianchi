"""Contract + source-bound conditional-science tests. No authority-source PES Q."""
import copy,json,unittest
from pathlib import Path
from decimal import Decimal,localcontext
from src.threshold_bound import (analyze,validate_source,nominal_printed_rate,
                                  bound_pair,SourceContractError)
from src.positive_witness import build_witness

ROOT=Path(__file__).resolve().parents[1]
SRC=json.loads((ROOT/'sources/GL2022_R18_EXACT_ROW.json').read_text())

class ConditionalSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=analyze(SRC)
    def test_contract(self):validate_source(SRC)
    def test_gl2022_sha(self):self.assertEqual(SRC['original_supplement_pdf_sha256'],'a65b1cba4208552e7eac6341b462487b23c5afe79f3ba0d2ca009fdee7dd1754')
    def test_ten_nodes(self):self.assertEqual(len(self.r['input_T_K']),10)
    def test_exact_printed_low(self):self.assertEqual(nominal_printed_rate('3.99(14)'),Decimal('3.99e-14'))
    def test_exact_printed_high(self):self.assertEqual(nominal_printed_rate('2.92(11)'),Decimal('2.92e-11'))
    def test_15K_rate_si(self):self.assertEqual(Decimal(self.r['input_k_m3_s'][0]),Decimal('3.99e-20'))
    def test_55K_rate_si(self):self.assertEqual(Decimal(self.r['input_k_m3_s'][1]),Decimal('2.92e-17'))
    def test_monotone_beta(self):self.assertTrue(all(Decimal(a)>Decimal(b) for a,b in zip(self.r['beta_inv_meV'],self.r['beta_inv_meV'][1:])))
    def test_tightest_pair(self):self.assertEqual(self.r['most_constraining_pair_T_K'],['15','55'])
    def test_nominal_bound(self):self.assertAlmostEqual(float(self.r['theta_nominal_upper_meV']),15.186303821758898,places=11)
    def test_rounding_upper(self):self.assertAlmostEqual(float(self.r['theta_nearest_display_rounding_upper_meV']),15.191573204773210,places=11)
    def test_pair_monotonicity(self):self.assertTrue(all(Decimal(x)>0 for x in self.r['adjacent_convexity_secant_increments_meV']))
    def test_all_45_pairs(self):self.assertEqual(Decimal(self.r['all_45_pair_min_upper_meV']),min(map(Decimal,self.r['adjacent_theta_upper_meV'])))
    def test_9_secants(self):self.assertEqual(len(self.r['adjacent_theta_upper_meV']),9)
    def test_no_physical_promotion(self):
        for k in ['GL2022_PES_native_threshold_meV','physical_Q_event_J','physical_bath_J','owner_ACK']:
            self.assertIsNone(self.r[k])
    def test_DAG_unchanged(self):self.assertEqual(self.r['DAG'],{'completed':34,'total':49,'promotions':0})
    def test_physical_candidate_exceeds_source_bound(self):self.assertGreater(Decimal(self.r['candidate_minus_nominal_bound_meV']),Decimal('5.75'))
    def test_factor_exceeds_25(self):self.assertGreater(Decimal(self.r['nominal_15K_to_max_ratio']),Decimal('25'))
    def test_scaling_spin_constant_does_not_move_threshold(self):
        b=list(map(Decimal,self.r['beta_inv_meV'][:2])); k=list(map(Decimal,self.r['input_k_m3_s'][:2]));
        self.assertEqual(bound_pair(b[0],k[0],b[1],k[1]),bound_pair(b[0],k[0]*Decimal('0.75'),b[1],k[1]*Decimal('0.75')))
    def test_wrong_channel_rejected(self):
        d=copy.deepcopy(SRC);d['channel']='H + HD -> D + H2'
        with self.assertRaises(SourceContractError):analyze(d)
    def test_changed_token_rejected(self):
        d=copy.deepcopy(SRC);d['rates']['printed_tokens'][0]='3.95(14)'
        with self.assertRaises(SourceContractError):analyze(d)
    def test_wrong_spin_rejected(self):
        d=copy.deepcopy(SRC);d['rates']['external_odd_J_spin_weight_applied']=True
        with self.assertRaises(SourceContractError):analyze(d)
    def test_wrong_energy_axis_rejected(self):
        d=copy.deepcopy(SRC);d['energy_axis_assumption']='ESTABLISHED'
        with self.assertRaises(SourceContractError):analyze(d)
    def test_premature_PES_Q_rejected(self):
        d=copy.deepcopy(SRC);d['gl2022_pes_native_threshold_meV']='15.2'
        with self.assertRaises(SourceContractError):analyze(d)
    def test_premature_bath_rejected(self):
        d=copy.deepcopy(SRC);d['physical_bath_J']='0'
        with self.assertRaises(SourceContractError):analyze(d)
    def test_wrong_supplement_sha_rejected(self):
        d=copy.deepcopy(SRC);d['original_supplement_pdf_sha256']='0'*64
        with self.assertRaises(SourceContractError):analyze(d)
    def test_wrong_last_temperature_rejected(self):
        d=copy.deepcopy(SRC);d['rates']['temperature_K'][-1]='4005'
        with self.assertRaises(SourceContractError):analyze(d)
    def test_nonpositive_rate_rejected(self):
        b=Decimal('1');
        with self.assertRaises(ValueError):bound_pair(b,Decimal('-1'),Decimal('0.5'),Decimal('1'))
    def test_source_immutable(self):
        old=json.dumps(SRC,sort_keys=True);analyze(SRC);self.assertEqual(old,json.dumps(SRC,sort_keys=True))

class NonidentificationWitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.w=build_witness(dps=125)
    def test_distinct_onsets(self):self.assertEqual((self.w['first_onset_meV'],self.w['second_onset_meV']),('20','12'))
    def test_strict_positivity(self):self.assertGreater(Decimal(self.w['minimum_alternative_high_energy_weight']),Decimal('0.5'))
    def test_low_energy_weight_positive(self):self.assertGreater(Decimal(self.w['added_12meV_weight']),0)
    def test_laplace_match(self):self.assertLess(Decimal(self.w['max_rel_Laplace_residual']),Decimal('1e-115'))
    def test_witness_not_real_source(self):self.assertIn('not GL2022',self.w['scope'])
    def test_no_PES_Q(self):self.assertIsNone(self.w['GL2022_PES_native_Q'])

if __name__=='__main__':unittest.main()
