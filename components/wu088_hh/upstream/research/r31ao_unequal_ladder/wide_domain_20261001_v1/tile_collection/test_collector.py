"""Analytic polynomial oracle and adversarial normalized-envelope fixtures."""
import copy
from fractions import Fraction as Q
import unittest
import collector as c


WINDOW = {'l_t': '1/16', 'T_t': '256', 'l_u': '1/16', 'T_u': '256'}
BINDINGS = {k: c.sha({'fixture_binding': k}) for k in c.BINDING_KEYS}


def integral(window):
    a, b, d, e = (Q(window[k]) for k in c.WINDOW_KEYS)
    # Independent antiderivatives for real F=t+2u and imaginary F=t*u.
    return {'real': (b*b-a*a)*(e-d)/2 + (b-a)*(e*e-d*d),
            'imag': (b*b-a*a)*(e*e-d*d)/4}


def fixtures():
    plan = c.bind_plan(c.plan_grid(WINDOW, 0, -48), **BINDINGS)
    records = []
    radius = Q(2) ** plan['tile_radius_exp']
    for tile in plan['tiles']:
        values = integral(tile['window'])
        record = {'schema': 'WU088_TRUSTED_NORMALIZED_TILE_V1',
                  'tile_id': tile['tile_id'], 'primitive_index': 0,
                  'global_plan_sha256': plan['plan_sha256'],
                  'window': copy.deepcopy(tile['window']),
                  'requested_radius_exp': plan['tile_radius_exp'],
                  'precision_bits': 128, 'status': 'RADIUS_MET', 'accepted': True,
                  'endpoint_included': False, 'normalization_applied': False,
                  'bindings': copy.deepcopy(plan['bindings']),
                  'native_plan_sha256': c.sha({'synthetic_plan': tile['tile_id']}),
                  'native_receipt_sha256': c.sha({'synthetic_receipt': tile['tile_id']}),
                  'rectangle': {p: {'lower': str(v-radius), 'upper': str(v+radius)}
                                for p, v in values.items()},
                  'reported_radius': {p: str(radius) for p in c.PARTS}}
        records.append(c.seal_normalized_record(record))
    return plan, records


def reseal(record):
    record.pop('record_sha256')
    return c.seal_normalized_record(record)


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.plan, self.records = fixtures()

    def reject(self, records=None, plan=None):
        with self.assertRaises(c.CollectionError):
            c.collect(self.plan if plan is None else plan,
                      self.records if records is None else records)

    def test_polynomial_oracle_exact_total_and_saturated_radius(self):
        out = c.collect(self.plan, list(reversed(self.records)))
        self.assertEqual(self.plan['tile_count'], 16)
        self.assertEqual(self.plan['tile_radius_exp'], -52)
        for part, exact in integral(WINDOW).items():
            lo, hi = (Q(out['rectangle'][part][key]) for key in ('lower', 'upper'))
            self.assertEqual((lo + hi)/2, exact)
            self.assertEqual((hi - lo)/2, Q(2)**-48)
        self.assertFalse(out['endpoint_included'])
        self.assertFalse(out['production_admission'])
        self.assertEqual(out['bindings']['global_endpoint_plan_sha256'],
                         BINDINGS['global_endpoint_plan_sha256'])

    def test_non_power_count_conservative_budget(self):
        p = c.plan_grid({'l_t':'1','T_t':'128','l_u':'1','T_u':'4'}, 2591, -48)
        self.assertEqual(p['tile_count'], 3)
        self.assertEqual(p['tile_radius_exp'], -50)
        self.assertEqual(p['log2_t_axis'], [0,3,6,7])

    def test_missing_tile(self):
        self.reject(self.records[:-1])

    def test_duplicate_id_and_missing_tile(self):
        self.records[-1] = copy.deepcopy(self.records[0])
        self.reject()

    def test_swapped_physical_coordinates(self):
        r = self.records[1]
        w = r['window']
        w['l_t'], w['l_u'] = w['l_u'], w['l_t']
        w['T_t'], w['T_u'] = w['T_u'], w['T_t']
        self.records[1] = reseal(r)
        self.reject()

    def test_outside_window(self):
        self.records[0]['window']['l_t'] = '1/32'
        self.records[0] = reseal(self.records[0])
        self.reject()

    def test_wrong_source_and_wrong_global_endpoint_plan(self):
        for key in ('build_source_sha256', 'global_endpoint_plan_sha256'):
            records = copy.deepcopy(self.records)
            records[0]['bindings'][key] = 'f'*64
            records[0] = reseal(records[0])
            self.reject(records)

    def test_corrupt_envelope(self):
        self.records[0]['rectangle']['real']['lower'] = '0'
        self.reject()

    def test_overwidth_even_after_reseal(self):
        r = self.records[0]
        lo = Q(r['rectangle']['real']['lower'])
        r['rectangle']['real']['upper'] = str(lo + Q(2)**-50)
        r['reported_radius']['real'] = str(Q(2)**-51)
        self.records[0] = reseal(r)
        self.reject()

    def test_reported_radius_cannot_hide_serialized_width(self):
        r = self.records[0]
        r['reported_radius']['imag'] = '0'
        self.records[0] = reseal(r)
        self.reject()

    def test_requested_radius_cannot_relax(self):
        self.records[0]['requested_radius_exp'] = -48
        self.records[0] = reseal(self.records[0])
        self.reject()

    def test_invalid_noncanonical_and_nondyadic_values(self):
        for value in ('0/2', '-0', '2/4', '1/3', 'NaN', '1e-20'):
            records = copy.deepcopy(self.records)
            records[0]['rectangle']['imag']['lower'] = value
            records[0] = reseal(records[0])
            self.reject(records)

    def test_endpoint_or_failed_tile_is_never_accepted(self):
        for key, value in (('endpoint_included', True), ('accepted', False),
                           ('status', 'NO_CONVERGENCE'), ('precision_bits', 64)):
            records = copy.deepcopy(self.records)
            records[0][key] = value
            records[0] = reseal(records[0])
            self.reject(records)

    def test_duplicate_raw_receipt(self):
        self.records[1]['native_receipt_sha256'] = self.records[0]['native_receipt_sha256']
        self.records[1] = reseal(self.records[1])
        self.reject()

    def test_corrupt_geometry_even_if_resealed(self):
        self.plan['tiles'][1]['window'] = self.plan['tiles'][0]['window'].copy()
        self.plan['plan_sha256'] = c.sha({k:v for k,v in self.plan.items() if k!='plan_sha256'})
        self.reject()

    def test_unbound_plan(self):
        self.reject(plan=c.plan_grid(WINDOW, 0, -48))

    def test_plan_caps_and_unsupported_endpoints(self):
        bad = [({'l_t':'1/256','T_t':str(2**192),'l_u':'1/256','T_u':str(2**192)},0,-48,3,16),
               (WINDOW,0,-48,0,16), (WINDOW,0,-48,9,16),
               (WINDOW,0,-48,3,17), (WINDOW,True,-48,3,16),
               (WINDOW,0,-1024,3,16),
               (dict(WINDOW,l_t='3/16'),0,-48,3,16)]
        for args in bad:
            with self.assertRaises(c.CollectionError):
                c.plan_grid(*args)


if __name__ == '__main__':
    unittest.main()
