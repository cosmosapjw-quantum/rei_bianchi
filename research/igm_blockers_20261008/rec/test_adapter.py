import copy
from fractions import Fraction as F
import unittest
import adapter


class ActualREC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = adapter.candidate()

    def test_actual_endpoint_electrons_eos_and_components(self):
        p = adapter.validate(self.packet)
        h,y,z,w = map(F,p['gas_state_exact'])
        nh,nhe = F(p['n_H']),F(p['n_He'])
        ne = nh*h+nhe*(y+2*z)
        self.assertEqual(F(p['n_e']), ne)
        self.assertEqual(F(p['x_e_per_H']), ne/nh)
        kb = F.from_float(p['source_context']['constants']['kb_erg_k'])
        self.assertEqual(F(p['Tgas']),2*w/(3*kb*(1+nhe/nh+ne/nh)))
        self.assertEqual(F(p['radiation_components']['CMB_bath']['Trad']),
                         F.from_float(p['source_context']['background'][5]))
        self.assertEqual(len(p['radiation_components']['ionizing_finite_grid']['rows_binary64_hex']),2440)
        self.assertFalse(p['whole_radiation_blackbody'])
        self.assertEqual(p['density_conversion_count'],0)

    def test_negative_refusals(self):
        cases = [
            ('epoch',lambda p:p.update(epoch_ln_a_exact='0'),'EPOCH_MISMATCH'),
            ('gas',lambda p:p['gas_state_exact'].__setitem__(0,'0'),'GAS_STATE_MISMATCH'),
            ('source',lambda p:p['source_context'].update(source_model='other'),'SOURCE_PROVIDER_STATE_IDENTITY_MISMATCH'),
            ('provider',lambda p:p['source_context'].update(photo_provider='other'),'SOURCE_PROVIDER_STATE_IDENTITY_MISMATCH'),
            ('photon_epoch',lambda p:p['radiation_components']['ionizing_finite_grid'].update(epoch_ln_a_exact='0'),'MISSING_OR_MISMATCHED_ACTUAL_SPECTRUM'),
            ('spectrum',lambda p:p['radiation_components']['ionizing_finite_grid']['rows_binary64_hex'][0].__setitem__(2,'0000000000000000'),'MISSING_OR_MISMATCHED_ACTUAL_SPECTRUM'),
            ('absent_spectrum',lambda p:p['radiation_components'].pop('ionizing_finite_grid'),'MISSING_OR_MISMATCHED_ACTUAL_SPECTRUM'),
            ('absent_CMB',lambda p:p['radiation_components'].pop('CMB_bath'),'MISSING_OR_MISMATCHED_CMB_TRAD'),
            ('absent_Trad',lambda p:p['radiation_components']['CMB_bath'].pop('Trad'),'MISSING_OR_MISMATCHED_CMB_TRAD'),
            ('electrons',lambda p:p.update(n_e='0'),'ELECTRON_DENSITY_MISMATCH'),
            ('electron_fraction',lambda p:p.update(x_e_per_H='0'),'ELECTRON_FRACTION_MISMATCH'),
            ('double_density',lambda p:p.update(density_conversion_count=1),'DOUBLE_DENSITY_CONVERSION'),
            ('gas_temperature',lambda p:p.update(Tgas='1'),'EOS_TEMPERATURE_MISMATCH'),
            ('blackbody_whole',lambda p:p.update(whole_radiation_blackbody=True),'WHOLE_RADIATION_BLACKBODY_FORBIDDEN'),
            ('GateI',lambda p:p.update(consumer_gate_I='PASS'),'UNAUTHORIZED_GATE_PROMOTION'),
            ('matched',lambda p:p.update(matched_evolution='PASS'),'UNAUTHORIZED_GATE_PROMOTION'),
            ('physical',lambda p:p.update(physical='PASS'),'UNAUTHORIZED_GATE_PROMOTION'),
            ('moment_substitute',lambda p:p['radiation_components']['ionizing_finite_grid'].update(rows_binary64_hex=[],integrated_A_div_dt='1'),'MISSING_OR_MISMATCHED_ACTUAL_SPECTRUM'),
        ]
        for name, mutate, code in cases:
            with self.subTest(name=name):
                p = copy.deepcopy(self.packet); mutate(p)
                with self.assertRaisesRegex(ValueError,'^'+code+'$'):
                    adapter.validate(p)

    def test_exact_six_moments_and_PR87_signed_projection(self):
        result = adapter.arithmetic()
        self.assertEqual(result['scope'],adapter.ARITHMETIC_SCOPE)
        self.assertEqual(result['row_count'],2440)
        self.assertTrue(result['six_finite_arithmetic_bounds_pass'])
        self.assertEqual(result['extra_calls'],dict(observer=0,provider=0,RHS=0,history=0))
        self.assertEqual(result['continuum_error'],'UNKNOWN')
        self.assertEqual(result['physical'],'HOLD')
        self.assertTrue(any(F(v)!=0 for v in result['signed_binary64_minus_exact']['Gamma']))
        for kind in ('Gamma','incident_Ecal'):
            for exact,rounded,delta in zip(result['exact_six_moments'][kind],
                                          result['ordered_binary64_moments'][kind],
                                          result['signed_binary64_minus_exact'][kind]):
                self.assertEqual(F(rounded)-F(exact),F(delta))

    def test_input_unchanged(self):
        original = copy.deepcopy(self.packet)
        output = adapter.validate(self.packet)
        self.assertEqual(original,self.packet)
        self.assertIsNot(output,self.packet)


if __name__ == '__main__': unittest.main()
