"""Only new focused tests. Do not rerun previous BASS_HE suites/IVPs."""
import sys
import unittest
from pathlib import Path
from dataclasses import replace
from fractions import Fraction as F
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from experiment_semantics import (
    ARENDS, SILVERMAN, MA, MD, SOURCE_SHA256, SOURCE_GIT_BLOB,
    exact, exact_s_comparison, examine_pair, match_forward_e,
    match_inverse_t, physical_bridge_inventory, s_forward, s_inverse,
)

class DetectorEventSemanticsTests(unittest.TestCase):
    def test_pinned_masses(self):
        self.assertEqual(MA, F('3727.3794118'))
        self.assertEqual(MD, F('1875.61294500'))
    def test_hash_metadata(self):
        self.assertEqual(SOURCE_SHA256, 'b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f')
        self.assertEqual(len(SOURCE_GIT_BLOB), 40)
    def test_invariant_330(self):
        self.assertEqual(s_forward(330), s_inverse(match_inverse_t(330)))
    def test_invariant_213(self):
        self.assertEqual(s_forward(213), s_inverse(match_inverse_t(213)))
    def test_inverse_376_to_213(self):
        self.assertLess(abs(float(match_forward_e(376)) - 213.12551760977376), 1e-12)
    def test_213_and_376_exact_mismatch(self):
        result = exact_s_comparison(213, 376)
        self.assertFalse(result['same_s'])
        self.assertNotEqual(result['delta_s_MeV2'], '0')
    def test_330_and_376_exact_mismatch(self):
        self.assertFalse(exact_s_comparison(330, 376)['same_s'])
    def test_exact_same_s_only_for_matching_energy(self):
        self.assertTrue(exact_s_comparison(330, match_inverse_t(330))['same_s'])
    def test_no_bogus_energy_tolerance(self):
        self.assertFalse(exact_s_comparison(213, match_inverse_t(213) + F(1, 10**9))['same_s'])
    def test_arends_only_exfor_not_original(self):
        self.assertEqual(ARENDS.record_kind, 'EXFOR_COMPILATION')
        self.assertIsNone(ARENDS.event_particle_normalization_definition)
    def test_silverman_abstract_not_raw_DA(self):
        self.assertEqual(SILVERMAN.record_kind, 'PUBLISHER_ABSTRACT')
        self.assertIsNone(SILVERMAN.raw_DA_nb_sr)
    def test_matching_s_is_not_matching_source(self):
        result = examine_pair(ARENDS, SILVERMAN, 213, match_inverse_t(213))
        self.assertTrue(result['same_s'])
        self.assertIn('INVERSE_RAW_DA_UNAVAILABLE', result['evidence_gaps'])
        self.assertIn('INVERSE_SOURCE_ROW_ENERGY_MISMATCH', result['evidence_gaps'])
        self.assertIsNone(result['kappa'])
        self.assertIsNone(result['R_event'])
    def test_source_actual_376_fails_213(self):
        result = examine_pair(ARENDS, SILVERMAN, 213, 376)
        self.assertIn('EXACT_INVARIANT_S_MISMATCH', result['evidence_gaps'])
        self.assertFalse(result['physical_activation'])
    def test_source_actual_376_fails_330(self):
        result = examine_pair(ARENDS, SILVERMAN, 330, 376)
        self.assertIn('EXACT_INVARIANT_S_MISMATCH', result['evidence_gaps'])
        self.assertIn('FORWARD_SOURCE_ROW_ENERGY_MISMATCH', result['evidence_gaps'])

    def test_source_energy_cannot_be_laundered(self):
        result = examine_pair(ARENDS, SILVERMAN, 330, match_inverse_t(330))
        self.assertTrue(result['same_s'])
        self.assertIn('FORWARD_SOURCE_ROW_ENERGY_MISMATCH', result['evidence_gaps'])
        self.assertIn('INVERSE_SOURCE_ROW_ENERGY_MISMATCH', result['evidence_gaps'])
    def test_missing_detector_efficiency(self):
        self.assertIn('coincidence_efficiency_definition', ARENDS.unresolved())
    def test_polarization_unresolved(self):
        self.assertIn('beam_polarization_definition', SILVERMAN.unresolved())
    def test_no_implicit_kappa_even_with_hypothetical_fulltext(self):
        invented = replace(ARENDS, original_fulltext_locator='HYPOTHETICAL_ONLY',
                           event_particle_normalization_definition='HYPOTHETICAL_ONLY')
        result = examine_pair(invented, SILVERMAN, 213, match_inverse_t(213))
        self.assertIsNone(result['kappa'])
    def test_bridge_missing_all_and_hold(self):
        result = physical_bridge_inventory({})
        self.assertEqual(len(result['missing_fields']), 10)
        self.assertFalse(result['physical_activation'])
        self.assertEqual(result['production'], 'HOLD')
    def test_bridge_some_source_does_not_activate(self):
        result = physical_bridge_inventory({'photon_phase_space_history': 'unverified_hint'})
        self.assertIn('photon_phase_space_history', result['present_fields'])
        self.assertIsNone(result['R_event'])
    def test_bridge_rejects_gate_override(self):
        for field in ('kappa', 'R_event', 'physical_activation', 'L4', 'production'):
            with self.subTest(field=field):
                with self.assertRaises(ValueError): physical_bridge_inventory({field: 1})
    def test_bridge_rejects_unregistered_input(self):
        with self.assertRaises(ValueError): physical_bridge_inventory({'fake_rate': 1})
    def test_bridge_does_not_activate_even_all_hints(self):
        from experiment_semantics import REQUIRED_PHYSICAL_INPUTS
        result = physical_bridge_inventory({k: 'unverified' for k in REQUIRED_PHYSICAL_INPUTS})
        self.assertEqual(result['missing_fields'], ())
        self.assertFalse(result['physical_activation'])
        self.assertIsNone(result['kappa'])
    def test_rounded_float_bool_rejected(self):
        for bad in (213.0, True, False):
            with self.subTest(bad=bad):
                with self.assertRaises(TypeError): exact(bad)
    def test_channel_swap_rejected(self):
        with self.assertRaises(ValueError): examine_pair(SILVERMAN, ARENDS, 213, 376)
    def test_negative_input_rejected(self):
        with self.assertRaises(ValueError): s_forward(-1)
        with self.assertRaises(ValueError): s_inverse(-1)

if __name__ == '__main__': unittest.main()
