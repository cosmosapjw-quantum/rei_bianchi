import copy
from fractions import Fraction
import unittest
from schemas import SchemaError, bass_observable, rec_initial


def state():
    return {'density_units': 'proper cm^-3', 'density_conversion_count': 0,
            'species_denominators': {'x_HII': 'H nuclei', 'x_HeII': 'He nuclei', 'x_HeIII': 'He nuclei'},
            'n_H': '2', 'n_He': '1/4', 'x_HII': '1/2', 'x_HeII': '1/4', 'x_HeIII': '1/2'}


def base():
    return {'payload_scope': 'schema_fixture', 'source_identity': 'synthetic/source/v1',
            'state_identity': 'synthetic/state/v1', 'clock_authority': 'fixture normal-time owner',
            'frame_authority': 'fixture normal frame'}


def bass():
    return {**base(), 'time_units': 'normal seconds', 'normal_time_edges': ['0', '2'],
            'epoch_ln_a_exact': ['-2', '-1'], 'caller_observer_tail': '1/8',
            'observer_tail_authority': 'fixture caller', 'reconstruction': 'endpoint_linear_density',
            'c_m_s': '299792458', 'sigma_T_m2': '6.6524587e-29', 'rate_constants_authority': 'BASS intake fixture constants',
            'endpoint_states': [state(), state()], 'doppler_applied_count': 0, 'fixed_doppler_D': '2'}


def rec():
    return {**base(), **state(), 'epoch_ln_a_exact': '-1', 'temperature_units': 'K',
            'Tgas': '8000', 'Trad': '30', 'radiation_authority': 'fixture radiation owner',
            'gas_temperature_authority': 'fixture gas owner', 'radiation_model': 'blackbody',
            'n_e': '21/16', 'x_e_per_H': '21/32'}


class Schemas(unittest.TestCase):
    def reject(self, fn, packet, code):
        with self.assertRaises(SchemaError) as caught:
            fn(packet)
        self.assertEqual(caught.exception.code, code)

    def test_absent_histories_are_not_provided(self):
        for fn in (bass_observable, rec_initial):
            out = fn()
            self.assertEqual(out['payload_status'], 'NOT_PROVIDED')
            self.assertEqual(out['physical_admission'], 'HOLD')
            self.assertEqual((out['observer_calls'], out['provider_calls']), (0, 0))

    def test_bass_conversion_and_d_once(self):
        p = bass()
        before = copy.deepcopy(p)
        out = bass_observable(p)
        self.assertEqual(p, before)
        self.assertEqual(Fraction(out['proper_ne_m3'][0]), Fraction(1312500))
        oracle = Fraction(299792458) * Fraction(66524587, 10**36) * 1312500 * 2
        self.assertEqual(Fraction(out['endpoint_q_t_s1'][0]), oracle)
        self.assertEqual(out['density_conversion_count'], 1)
        self.assertEqual(out['doppler_applied_count'], 1)
        self.assertEqual(out['caller_observer_tail'], '1/8')

    def test_bass_bad_units_double_conversion_d_and_missing_clock(self):
        for field, value, code in [('time_units', 'redshift', 'MISSING_NORMAL_TIME_MAPPING'),
                                    ('doppler_applied_count', 1, 'DOUBLE_DOPPLER_APPLICATION'),
                                    ('normal_time_edges', ['1', '1'], 'NONINCREASING_NORMAL_TIME_EDGES'),
                                    ('caller_observer_tail', '-1', 'INVALID_OBSERVER_TAIL'),
                                    ('epoch_ln_a_exact', [], 'MISSING_EXACT_EPOCHS')]:
            p = bass(); p[field] = value
            self.reject(bass_observable, p, code)
        for field, value, code in [('density_conversion_count', 1, 'DOUBLE_DENSITY_CONVERSION'), ('density_units', 'comoving cm^-3', 'DENSITY_CONVENTION_MISMATCH')]:
            p = bass(); p['endpoint_states'][0][field] = value
            self.reject(bass_observable, p, code)

    def test_frozen_rate_preserves_supplied_rate(self):
        p = bass(); p.update(reconstruction='supplied_frozen_cell_rate', rate_units='s^-1 normal time', rate_authority='fixture rate owner', cell_q_t_s1=['3/7'], doppler_applied_count=1)
        out = bass_observable(p)
        self.assertEqual(out['cell_q_t_s1'], ['3/7'])
        self.assertEqual(out['density_conversion_count'], 'NOT_APPLICABLE')
        p['doppler_applied_count'] = 2
        self.reject(bass_observable, p, 'FROZEN_RATE_DOPPLER_NOT_ONCE')

    def test_rec_exact_initial_state_only(self):
        p = rec(); before = copy.deepcopy(p)
        out = rec_initial(p)
        self.assertEqual(p, before)
        self.assertEqual(out['n_e'], '21/16')
        self.assertEqual(out['Tgas'], '8000')
        self.assertEqual(out['Trad'], '30')
        self.assertEqual(out['matched_history_status'], 'NOT_PROVIDED')
        self.assertEqual(out['consumer_gate_I'], 'DEFERRED_CONSUMER')

    def test_rec_missing_authorities_epoch_temperature_and_state(self):
        for field, code in [('radiation_authority', 'MISSING_RADIATION_AUTHORITY'), ('epoch_ln_a_exact', 'MISSING_EPOCH'), ('Trad', 'MISSING_RADIATION_TEMPERATURE'), ('Tgas', 'MISSING_GAS_TEMPERATURE'), ('frame_authority', 'MISSING_FRAME_AUTHORITY')]:
            p = rec(); del p[field]
            self.reject(rec_initial, p, code)
        p = rec(); p['n_e'] = '1'
        self.reject(rec_initial, p, 'ELECTRON_DENSITY_MISMATCH')
        p = rec(); p.update(radiation_model='explicit_spectrum')
        self.reject(rec_initial, p, 'MISSING_RADIATION_SPECTRUM_IDENTITY')

    def test_never_claim_actual_history_admission(self):
        for fn, p in [(bass_observable, bass()), (rec_initial, rec())]:
            p['payload_scope'] = 'actual_history'
            self.reject(fn, p, 'ACTUAL_HISTORY_ADMISSION_NOT_IMPLEMENTED')


if __name__ == '__main__':
    unittest.main()
