"""No numerical solver calls: preserved raw-evidence readback and refusal tests."""
import copy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('wu088_w3_collector_tested', HERE / 'collector.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


def reseal(record, key='record_sha256'):
    return c.sealed({k: v for k, v in record.items() if k != key}, key)


class CollectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = c.context()
        cls.plan = c.make_plan(cls.ctx)
        cls.records = c.import_w1(cls.ctx, cls.plan)

    def test_exact_reuse_same_rectangle_original_requests_and_partial_domain(self):
        result = c.collect_partial(self.plan, self.records)
        old = json.loads(c.fixed(c.W1_ROOT / 'COLLECTED.json', c.W1_COLLECTED_SHA))
        self.assertEqual(result['rectangle'], old['rectangle'])
        self.assertEqual(result['component_radius'], old['component_radius'])
        self.assertEqual(result['accepted_cell_ids'], [36,37,38,39,53,54,55,56,70,71,72,73,87,88,89,90])
        self.assertEqual(len(result['missing_cell_ids']), 273)
        self.assertFalse(result['global_complete'])
        self.assertFalse(result['endpoint_included'])
        self.assertEqual(result['domain'], 'UNION_OF_LISTED_ACCEPTED_CELLS_ONLY')
        self.assertEqual(result['missing_domain_contribution'], 'NOT_BOUNDED_OR_INCLUDED')
        self.assertEqual({r['origin']['requested_radius_exp'] for r in self.records}, {-52})
        self.assertTrue(all(Fraction(r['reported_radius'][p]) <= Fraction(2)**-57 for r in self.records for p in ('real','imag')))
        self.assertEqual(self.ctx['w1_ctx']['global_plan']['window'], {'l_t':'1/16','T_t':'256','l_u':'1/16','T_u':'256'})
        self.assertEqual(self.ctx['global_plan']['window'], c.GLOBAL_WINDOW)

    def test_empty_union_does_not_claim_zero_global_integral(self):
        result = c.collect_partial(self.plan, [])
        self.assertEqual(result['missing_cell_ids'], list(range(289)))
        self.assertFalse(result['full_domain_integral'])
        self.assertEqual(result['status'], 'PARTIAL_COMPACT_INTERIOR')

    def test_resealed_geometry_gap_rejected(self):
        plan = copy.deepcopy(self.plan)
        plan['cells'][20]['window']['l_t'] = '1/512'
        with self.assertRaises(ValueError):
            c.collect_partial(reseal(plan, 'plan_sha256'), [])

    def test_duplicate_cell_and_repeated_raw_receipt_rejected(self):
        with self.assertRaises(ValueError):
            c.collect_partial(self.plan, [self.records[0], self.records[0]])
        second = copy.deepcopy(self.records[1])
        second['native_receipt_sha256'] = self.records[0]['native_receipt_sha256']
        with self.assertRaises(ValueError):
            c.collect_partial(self.plan, [self.records[0], reseal(second)])

    def test_origin_request_must_not_be_relabelled(self):
        r = copy.deepcopy(self.records[0])
        r['origin']['requested_radius_exp'] = -57
        with self.assertRaises(ValueError):
            c.collect_partial(self.plan, [reseal(r)])

    def test_resealed_wrong_binding_or_status_rejected(self):
        for key, value in [('primitive_index', 1), ('accepted', False), ('endpoint_included', True), ('precision_bits', 64)]:
            r = copy.deepcopy(self.records[0]); r[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                c.collect_partial(self.plan, [reseal(r)])
        r = copy.deepcopy(self.records[0]); r['bindings']['archive_sha256'] = '0'*64
        with self.assertRaises(ValueError):
            c.collect_partial(self.plan, [reseal(r)])

    def test_reported_radius_and_serialized_cap_fail_closed(self):
        for mode in ('reported', 'wide', 'reversed'):
            r = copy.deepcopy(self.records[0])
            if mode == 'reported':
                r['reported_radius']['real'] = '0'
            elif mode == 'wide':
                r['rectangle']['real'] = {'lower':'0', 'upper':str(Fraction(2)**-55)}
                r['reported_radius']['real'] = str(Fraction(2)**-56)
            else:
                r['rectangle']['real'] = {'lower':'1', 'upper':'0'}
                r['reported_radius']['real'] = '-1/2'
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                c.collect_partial(self.plan, [reseal(r)])

    def test_invalid_id_and_noncanonical_number_rejected(self):
        for value in (True, -1, 289):
            r = copy.deepcopy(self.records[0]); r['cell_id'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                c.collect_partial(self.plan, [reseal(r)])
        for value in ('NaN', '1/3', '2/4', '01', '1e-10'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                c.rational(value)

    def test_new_normalization_rejects_old_window_and_outside_pilot(self):
        oldpath = c.W1_ROOT / 'raw/01.json'
        with self.assertRaises(ValueError):
            c.normalize_new(self.ctx, self.plan, 20, oldpath)
        for cell_id in (36, 0, 288):
            with self.subTest(cell_id=cell_id), self.assertRaises(ValueError):
                c.normalize_new(self.ctx, self.plan, cell_id, oldpath)

    def test_original_native_stdout_tamper_prevents_w1_reuse(self):
        runner = self.ctx['w1_runner']
        original_read = runner.read
        target = (c.W1_ROOT / 'raw/01.json.stdout').resolve()
        def read_tampered(path):
            payload = original_read(path)
            return payload + b' ' if Path(path).resolve() == target else payload
        with patch.object(runner, 'read', side_effect=read_tampered), self.assertRaises(ValueError):
            c.import_w1(self.ctx, self.plan)

    def test_exact_synthetic_added_rectangle_is_only_an_accepted_subset(self):
        # This is an integrity-contract fixture, not native execution evidence.
        origin = {'kind':'NEW_PILOT_RAW_EVIDENCE', 'old_W1_tile_id':None,
                  'requested_radius_exp':-57, 'new_native_execution':True,
                  'prepared_sha256':None, 'old_normalized_record_sha256':None,
                  'receipt_path':'/synthetic-test-only/no-native-execution.json'}
        fixture = c._record(self.plan, 20, {'real':{'lower':'1','upper':'1'}, 'imag':{'lower':'-2','upper':'-2'}},
                            {'real':'0','imag':'0'}, 'a'*64, 'b'*64, origin)
        output = c.collect_partial(self.plan, self.records + [fixture])
        base = c.collect_partial(self.plan, self.records)
        self.assertEqual(output['accepted_cell_count'], 17)
        self.assertEqual(len(output['missing_cell_ids']), 272)
        self.assertFalse(output['global_complete'])
        self.assertEqual(Fraction(output['rectangle']['real']['lower']), Fraction(base['rectangle']['real']['lower']) + 1)
        self.assertEqual(output['component_radius'], base['component_radius'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
