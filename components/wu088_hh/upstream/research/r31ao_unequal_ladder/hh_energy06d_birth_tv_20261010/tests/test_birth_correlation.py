import sys, unittest, pathlib, tempfile, shutil, json
from fractions import Fraction
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from birth_correlation import inspect, EvidenceError

class PinnedBirthEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out=inspect(ROOT)

    def test_four_members_all_twelve_native_rows(self):
        self.assertEqual(self.out['native_products_checked'],12)
        self.assertEqual(len(self.out['members']),4)
        self.assertEqual(self.out['native_products_exact_mismatches'],0)

    def test_equal_full_half_birth_count_is_only_ideal_relation(self):
        for m in self.out['members']:
            self.assertEqual(m['exact_normalized_count_defect_fraction'],'0')
            self.assertNotEqual(m['native_f64_count_defect_fraction'],'0')

    def test_all_members_use_same_binary64_physical_source(self):
        self.assertEqual(self.out['fixed_source']['source_f64_hex'],(5e-15).hex())
        self.assertEqual(self.out['fixed_source']['energy_f64_hex'],(13.7).hex())
        self.assertEqual(self.out['member_count'],4)

    def test_exact_centered_time_moment(self):
        for m in self.out['members']:
            self.assertEqual(Fraction(m['centered_M1_normalized_fraction']),
                             -Fraction.from_float(3.125e-6)*625000000)

    def test_correct_directional_weight_provenance(self):
        for m in self.out['members']:
            self.assertTrue(m['full_half2_weights_binary64_identical'])
            self.assertEqual(m['directions'],128)
            self.assertEqual(m['stages_checked'],3)

    def test_bianchi_has_nonzero_angular_redistribution(self):
        for m in self.out['members']:
            p=m['angular_transport']['normalized_total_variation_fraction_of_total_birth']
            self.assertGreater(p,1e-9) if m['member']>=2 else self.assertLess(p,1e-12)

    def test_anisotropic_p2_birth_moment_not_confused_with_be(self):
        for m in self.out['members']:
            p2=m['angular_transport']['P2_axis_reference']['normalized_moment_fraction_of_total_birth']
            self.assertTrue(m['angular_transport']['P2_axis_reference']['strict_tv_bound_verified'])
            if m['member']>=2:
                self.assertGreater(p2,1e-14)
                self.assertLess(p2,1e-10)
            else:
                self.assertLess(abs(p2),1e-14)

    def test_signed_mass_preserving_difference(self):
        for m in self.out['members']:
            self.assertEqual(m['angular_transport']['signed_mass_fraction'],'0')
            self.assertEqual(Fraction(m['angular_transport']['positive_fraction']),
                             -Fraction(m['angular_transport']['negative_fraction']))

    def test_native_product_ledger_binary64_witness(self):
        for m in self.out['members']:
            self.assertEqual(m['native_ledger_per_stage_matches'],3)
            self.assertEqual(Fraction(m['native_f64_count_defect_fraction']),
                             Fraction(m['native_first_half_fraction'])+Fraction(m['native_second_half_fraction'])-Fraction(m['native_full_fraction']))

    def test_nonnegative_born_weights_and_positive_tv(self):
        for m in self.out['members']:
            self.assertGreater(m['angular_transport']['normalized_total_variation_fraction_of_total_birth'],0)
            self.assertGreaterEqual(m['angular_transport']['positive_fraction_float'],0)

    def test_equal_off_lcs_for_equal_background_source(self):
        self.assertEqual(self.out['members'][0]['angular_transport']['normalized_total_variation_fraction_of_total_birth'],
                         self.out['members'][1]['angular_transport']['normalized_total_variation_fraction_of_total_birth'])
        self.assertEqual(self.out['members'][2]['angular_transport']['normalized_total_variation_fraction_of_total_birth'],
                         self.out['members'][3]['angular_transport']['normalized_total_variation_fraction_of_total_birth'])

    def test_scientific_gates_must_remain_open(self):
        self.assertEqual(self.out['gate_status']['scientific_dispatch'],0)
        self.assertIsNone(self.out['gate_status']['new_coupled_root'])
        self.assertIsNone(self.out['gate_status']['full_box_analytic_certificate'])
        self.assertEqual(self.out['gate_status']['coverage'],'24/289')
        self.assertIsNone(self.out['gate_status']['epsilon_C'])
        self.assertIsNone(self.out['gate_status']['epsilon_R'])

    def test_c1_must_reject_bounded_series_as_full_box_admission(self):
        c=self.out['c1'];self.assertFalse(c['whole_physical_boxes_inclusion'])
        self.assertFalse(c['holomorphic_derivative_admission'])
        self.assertFalse(c['sign_rank_admission'])
        self.assertIsNone(c['authorization_record'])

    def test_guard_against_unverified_input_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            dst=pathlib.Path(td)
            (dst/'inputs').mkdir()
            for f in (ROOT/'inputs').glob('*.json*'):
                shutil.copyfile(f,dst/'inputs'/f.name)
            (dst/'inputs'/'source').mkdir()
            for f in (ROOT/'inputs'/'source').iterdir():
                shutil.copyfile(f,dst/'inputs'/'source'/f.name)
            p=dst/'inputs'/'BIRTH_LEDGER.json'
            p.write_bytes(p.read_bytes().replace(b'59029581035870577',b'59029581035870579',1))
            with self.assertRaises(EvidenceError): inspect(dst)

if __name__=='__main__':unittest.main()
