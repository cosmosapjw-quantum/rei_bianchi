import importlib.util, pathlib, unittest
import numpy as np
P=pathlib.Path(__file__).resolve().parents[1]/'code/ferrett_window.py'
spec=importlib.util.spec_from_file_location('tested_ferrett',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class TestPhysicalScope(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records,cls.epochs,cls.summary=m.generate()
    def test_original_identity(self):
        self.assertEqual(m.sha(m.ARCHIVE.read_bytes()),m.SHA_PR287)
    def test_original_shape_and_epochs(self):
        self.assertEqual(len(self.records),1544)
        self.assertEqual(len(self.epochs),193)
        self.assertEqual({r['isotope'] for r in self.records},{'Li6I','Li7I'})
        self.assertEqual({r['bin_index'] for r in self.records},{54,55,56,57})
    def test_no_extrapolation(self):
        for e in (79.999,99.001,70,110):
            with self.assertRaises(ValueError):m.fractions(e)
    def test_exact_87ev_table(self):
        f=m.fractions(87.)
        self.assertAlmostEqual(f['sigma_triplet_Mb'],.89,places=13)
        self.assertAlmostEqual(f['sigma_singlet_plus_3P_unresolved_Mb'],.51,places=13)
        self.assertAlmostEqual(f['ratio_triplet_1s2s_to_measured_core'],.89/1.75,places=13)
    def test_87ev_satellite_consistency(self):
        f=m.fractions(87.)
        self.assertAlmostEqual(f['ratio_n3_satellite_to_measured_core'],.30/1.75,places=13)
        self.assertAlmostEqual(f['ratio_other_unresolved_to_measured_core'],.05/1.75,places=13)
    def test_sum_one_and_bounds(self):
        for t in m.TABLE:
            f=m.fractions(t[0]);vals=[f['ratio_triplet_1s2s_to_measured_core'],f['ratio_singlet_1s2s_upper_to_measured_core'],f['ratio_n3_satellite_to_measured_core'],f['ratio_other_unresolved_to_measured_core']]
            self.assertTrue(all(0<=v<=1 for v in vals));self.assertAlmostEqual(sum(vals),1.,places=14)
    def test_nonnegative_original_rate(self):
        self.assertTrue(all(q['native_K_events_per_baryon_s']>=0 for q in self.records))
    def test_singlet_lower_is_zero(self):
        self.assertTrue(all(q['conditional_2E1_singlet_event_rate_lower']==0 for q in self.records))
    def test_event_channel_conservation(self):
        for row in self.records:
            a=row['native_K_events_per_baryon_s'];b=sum(row[k] for k in ['conditional_M1_triplet_event_rate','conditional_2E1_singlet_event_rate_upper','conditional_satellite_n3_event_rate','conditional_other_event_rate']);self.assertLessEqual(abs(a-b),1e-14*max(a,1e-100))
    def test_actual_window_subset(self):
        s=self.summary;self.assertGreater(s['measured_window_over_all_K_native_event_fraction'],0);self.assertLess(s['measured_window_over_all_K_native_event_fraction'],1)
    def test_native_integral_count_conservation(self):
        vals=self.summary['integrals_per_original_baryon'];v=vals['triplet_M1_conditional_events']+vals['singlet_2E1_upper_conditional_events']+vals['n3_satellite_conditional_events']+vals['other_unresolved_events'];self.assertLessEqual(abs(v-vals['window_native_events']),1e-13*vals['window_native_events'])
    def test_empirically_supported_stratum(self):
        a=self.summary['direct_R31_measured_regime_80_to_92_5_eV'];b=self.summary['integrals_per_original_baryon'];self.assertLess(a['native_window_source_events'],b['window_native_events']);self.assertEqual(self.summary['higher_e_93_to_99_regime_natively_selected_rows'],386)
    def test_193_epoch_order_positive_H(self):
        self.assertEqual([v['epoch'] for v in self.epochs],list(range(193)))
        self.assertTrue(all(r['H_s']>0 for r in self.epochs))
    def test_source_corruption_rejected(self):
        original=m.SHA_PR287
        try:
            m.SHA_PR287='0'*64
            with self.assertRaisesRegex(ValueError,'PR287_WHOLE_ARCHIVE_SHA_MISMATCH'):m.original_rows()
        finally:m.SHA_PR287=original
    def test_empirical_not_full_source_equivalence(self):
        self.assertTrue(self.summary['conditional_native_BASS_fraction_projection_not_same_cross_section_source_owner'])
        self.assertEqual(self.summary['physical_DAG_before_after']['canonical_delta'],0)
        self.assertEqual(self.summary['new_ivps'],0)

if __name__=='__main__':unittest.main()
