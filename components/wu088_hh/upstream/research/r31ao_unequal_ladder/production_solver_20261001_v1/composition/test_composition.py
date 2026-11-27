"""Analytic synthetic fixtures, not archived HH scientific input."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction as Q


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('utf-8')


def bound(data):
    return {'sha256': hashlib.sha256(canonical(data)).hexdigest(), 'data': data}


def matrix(rows=47, cols=2, diagonal='0'):
    return [[[diagonal if i == j else '0', '0'] for j in range(cols)] for i in range(rows)]


def disks(rows=47, cols=2, radius='0'):
    return [[{'center': ['0', '0'], 'radius': radius} for j in range(cols)] for i in range(rows)]


def request():
    raw = {'D_col': matrix(diagonal='1/1000'), 'D_row': matrix(2, 47, '1/1000')}
    models = {}
    for name, value in [('R31AK', '0'), ('R31Z', '1/500'), ('R31AD', '3/1000')]:
        models[name] = {'D_col': matrix(diagonal=value), 'D_row': matrix(2, 47, value),
                        'K': matrix(diagonal=value)}
    return {'schema': 'WU088_T5_COMPOSITION_REQUEST_V1',
            'inputs': {'raw': bound(raw), 'models': bound(models),
                       'target_disks': bound({'D_col': disks(), 'D_row': disks(2, 47)})}}


class CompositionTests(unittest.TestCase):
    def test_sharp_identity_counterexample(self):
        from adapter import compose
        result = compose(request())
        self.assertEqual(result['source_residuals']['D_col']['interval'],
                         {'lo': '1/1000', 'hi': '1/1000', 'endpoints': 'EXACT_RATIONAL'})
        # Independent analytic eigenvalue: ||a I_2||_2=a, not sqrt(2)*a.
        from fractions import Fraction as Q
        epsilon = Q(result['epsilon']['Dmax'])
        self.assertLess(epsilon, Q(1, 800))
        self.assertGreater(2 * Q(1, 1000)**2, Q(1, 800)**2)

    def test_nonzero_disks_analytic_radius(self):
        from adapter import compose
        req = request()
        data = req['inputs']['target_disks']['data']
        # Only the leading 2x2 block has uncertain entries: rho=2r exactly.
        for key in ('D_col', 'D_row'):
            for i in range(2):
                for j in range(2):
                    data[key][i][j]['radius'] = '1/100000'
        req['inputs']['target_disks'] = bound(data)
        result = compose(req)
        self.assertEqual(result['source_residuals']['D_col']['rho_upper'], '1/50000')
        self.assertEqual(result['source_residuals']['D_col']['interval']['hi'], '51/50000')
        self.assertLess(Q(result['epsilon']['Dmax']), Q(1, 800))

    def test_k_cancellation_and_independent_model(self):
        from adapter import compose
        result = compose(request())
        self.assertEqual(result['epsilon']['K'], '0')
        self.assertEqual(result['separate_block_epsilon_K'], '1/1000')
        # Every model has C=R†, yet its independent stored K is nonzero.
        self.assertEqual(result['target_model_errors']['R31Z']['K']['lo'], '1/500')
        self.assertTrue(result['arithmetic']['stored_model_K_preserved'])

    def test_complex_k_conjugation(self):
        from adapter import compose
        req = request()
        raw = {'D_col': matrix(), 'D_row': matrix(2, 47)}
        target = {'D_col': disks(), 'D_row': disks(2, 47)}
        raw['D_col'][0][0] = ['7', '1']
        raw['D_row'][0][0] = ['1', '7']
        target['D_col'][0][0]['center'] = ['7', '1']
        target['D_row'][0][0]['center'] = ['1', '7']
        req['inputs']['raw'], req['inputs']['target_disks'] = bound(raw), bound(target)
        result = compose(req)
        # (7+i - conjugate(1+7i))/2 = 3+4i; rank-one norm is exactly 5.
        self.assertEqual(result['epsilon']['K'], '0')
        self.assertEqual(result['target_model_errors']['R31AK']['K']['lo'], '5')
        self.assertEqual(result['target_model_errors']['R31AK']['K']['hi'], '5')

    def test_direct_intersection_resolves_wide_raw_tube(self):
        from adapter import compose
        result = compose(request())
        comparison = result['comparisons']['PRIMARY']
        self.assertEqual(comparison['represented_gap']['Dmax']['lo'], '0')
        self.assertEqual(comparison['represented_gap_tube']['Dmax']['lo'], '-1/500')
        self.assertEqual(comparison['represented_gap_tube']['Dmax']['hi'], '1/500')
        self.assertEqual(comparison['intersection']['Dmax']['lo'], '1/500')
        self.assertEqual(comparison['intersection']['Dmax']['hi'], '1/500')
        self.assertTrue(comparison['decision']['real_sufficient_condition'])

    def test_strict_tolerance_equality_is_not_improvement(self):
        from adapter import compose, gram
        req = request()
        models = req['inputs']['models']['data']
        for name in ('R31Z', 'R31AD'):
            for key, shape in [('D_col', (47, 2)), ('D_row', (2, 47)), ('K', (47, 2))]:
                models[name][key] = matrix(*shape, diagonal=str(gram.TOLERANCE))
        req['inputs']['models'] = bound(models)
        result = compose(req)
        for comparison in result['comparisons'].values():
            decision = comparison['decision']
            self.assertTrue(all(decision['weak_nonworsening'].values()))
            self.assertFalse(any(decision['strict_improvement'].values()))
            self.assertEqual(decision['status'], 'CONDITIONAL_REAL_PARETO_NOT_SUPPORTED')

    def test_weak_negative_tolerance_equality_is_inclusive(self):
        from adapter import compose, gram
        req = request()
        models = req['inputs']['models']['data']
        models['R31AK']['K'] = matrix(diagonal=str(gram.TOLERANCE))
        for name in ('R31Z', 'R31AD'):
            models[name]['K'] = matrix()
        req['inputs']['models'] = bound(models)
        result = compose(req)
        for comparison in result['comparisons'].values():
            decision = comparison['decision']
            self.assertTrue(decision['weak_nonworsening']['K'])
            self.assertFalse(decision['strict_improvement']['K'])
            self.assertTrue(decision['strict_improvement']['Dmax'])
            self.assertTrue(decision['real_sufficient_condition'])

    def test_uncertain_boundary_is_unresolved(self):
        from adapter import compose, gram
        req = request()
        target = req['inputs']['target_disks']['data']
        target['D_col'][0][0]['radius'] = '1/1000'
        target['D_row'][0][0]['radius'] = '1/1000'
        models = req['inputs']['models']['data']
        for name in ('R31Z', 'R31AD'):
            for key, shape in [('D_col', (47, 2)), ('D_row', (2, 47)), ('K', (47, 2))]:
                models[name][key] = matrix(*shape, diagonal=str(gram.TOLERANCE))
        req['inputs']['models'], req['inputs']['target_disks'] = bound(models), bound(target)
        result = compose(req)
        self.assertEqual(result['comparisons']['PRIMARY']['decision']['status'], 'DECISION_BOUND_UNRESOLVED')

    def test_no_admission_from_documentary_hashes(self):
        from adapter import compose
        req = request()
        req['evidence_refs'] = {key: 'a' * 64 for key in (
            'target_binding_sha256', 'historical_abi_sha256',
            'final_entry_certificate_sha256', 'model_identity_sha256')}
        result = compose(req)
        for key, value in result['admission'].items():
            if key != 'reason':
                self.assertIs(value, False)
        self.assertIs(result['comparisons']['PRIMARY']['decision']['machine_predicate_certified'], False)

    def test_identity_mismatch_rejected(self):
        from adapter import compose, ContractError
        req = request()
        req['inputs']['raw']['data']['D_col'][0][0] = ['1', '0']
        with self.assertRaisesRegex(ContractError, 'SHA-256 mismatch'):
            compose(req)

    def test_noncanonical_and_nonfinite_values_rejected(self):
        from adapter import compose, ContractError
        for token in ('NaN', 'inf', '1.0', '01', '-0', '2/4', '1/1', '1/0', 0.5, True, 0, None):
            with self.subTest(token=token):
                req = request()
                data = req['inputs']['raw']['data']
                data['D_col'][0][0][0] = token
                req['inputs']['raw'] = bound(data)
                with self.assertRaises(ContractError):
                    compose(req)

    def test_negative_radius_rejected(self):
        from adapter import compose, ContractError
        req = request()
        data = req['inputs']['target_disks']['data']
        data['D_col'][0][0]['radius'] = '-1'
        req['inputs']['target_disks'] = bound(data)
        with self.assertRaises(ContractError):
            compose(req)

    def test_wrong_shape_and_extra_missing_keys_rejected(self):
        from adapter import compose, ContractError
        changes = []
        req = request(); req['inputs']['raw']['data']['D_col'].pop(); req['inputs']['raw'] = bound(req['inputs']['raw']['data']); changes.append(req)
        req = request(); req['inputs']['models']['data']['R31AK'].pop('K'); req['inputs']['models'] = bound(req['inputs']['models']['data']); changes.append(req)
        req = request(); req['inputs']['raw']['data']['K'] = matrix(); req['inputs']['raw'] = bound(req['inputs']['raw']['data']); changes.append(req)
        req = request(); req['rigorous'] = True; changes.append(req)
        req = request(); req['evidence_refs'] = {'admitted': True}; changes.append(req)
        req = request(); req.pop('inputs'); changes.append(req)
        for req in changes:
            with self.subTest(keys=list(req)):
                with self.assertRaises(ContractError):
                    compose(req)

    def test_resource_caps_fail_closed(self):
        from adapter import compose, ResourceLimit, CAPS
        for key, value in [('max_operations', 1), ('max_integer_bits', 4), ('max_work_bits', 2),
                           ('max_precision', 1), ('max_operations', CAPS['max_operations'] + 1)]:
            req = request(); req['limits'] = {key: value}
            with self.subTest(key=key, value=value):
                with self.assertRaises(ResourceLimit):
                    compose(req)
        req = request(); req['precision'] = 4097
        with self.assertRaises(ResourceLimit):
            compose(req)

    def test_large_rational_rejected_before_integer_conversion(self):
        from adapter import compose, ResourceLimit
        req = request()
        data = req['inputs']['raw']['data']
        data['D_col'][0][0][0] = '9' * 100000
        req['inputs']['raw'] = bound(data)
        with self.assertRaisesRegex(ResourceLimit, 'token allocation'):
            compose(req)

    def test_default_precision_and_determinism(self):
        from adapter import compose
        first, second = compose(request()), compose(request())
        self.assertEqual(first, second)
        self.assertEqual(first['arithmetic']['precision'], 128)

    def test_dependency_source_corruption_blocks_import(self):
        from adapter import GRAM_PATH, GRAM_RELATIVE
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            copied = root / 'production' / 'composition' / 'adapter.py'
            copied.parent.mkdir(parents=True)
            copied.write_bytes(Path(__file__).with_name('adapter.py').read_bytes())
            dependency = root / GRAM_RELATIVE
            dependency.parent.mkdir(parents=True)
            dependency.write_bytes(GRAM_PATH.read_bytes() + b'\n# corrupted fixture\n')
            result = subprocess.run([sys.executable, str(copied), '--help'], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b'immutable exact-Gram source SHA mismatch', result.stderr)

    def test_global_operation_budget_not_reset_per_norm(self):
        from adapter import compose, ResourceLimit
        req = request()
        total = compose(req)['arithmetic']['operations_used']
        self.assertGreater(total, 10000)
        req['limits'] = {'max_operations': total - 1}
        with self.assertRaises(ResourceLimit):
            compose(req)
        req['limits']['max_operations'] = total
        self.assertEqual(compose(req)['arithmetic']['operations_used'], total)

    def test_parser_duplicates_float_nan_and_size(self):
        from adapter import parse_request, ContractError, ResourceLimit, MAX_DOCUMENT_BYTES
        for text in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}', '{"x":1.0}',
                     '{"x":1e4}', '{', '{"x":12345678901}'):
            with self.subTest(text=text):
                with self.assertRaises(ContractError):
                    parse_request(text.encode())
        with self.assertRaises(ResourceLimit):
            parse_request(b' ' * (MAX_DOCUMENT_BYTES + 1))

    def test_cli_roundtrip_create_only_and_error_return(self):
        adapter = Path(__file__).with_name('adapter.py')
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / 'input.json', Path(directory) / 'result.json'
            source.write_bytes(canonical(request()))
            command = [sys.executable, str(adapter), '--input', str(source), '--output', str(output)]
            first = subprocess.run(command, capture_output=True)
            self.assertEqual(first.returncode, 0, first.stderr.decode())
            data = output.read_bytes()
            self.assertEqual(json.loads(data)['status'], 'CONDITIONAL_NUMERICAL_BOUNDS_COMPUTED')
            second = subprocess.run(command, capture_output=True)
            self.assertEqual(second.returncode, 2)
            self.assertEqual(output.read_bytes(), data)
            self.assertIs(json.loads(second.stderr)['production_admitted'], False)
            source.write_text('{"schema":NaN}')
            invalid = subprocess.run(command[:-2], capture_output=True)
            self.assertEqual(invalid.returncode, 2)
            self.assertEqual(invalid.stdout, b'')

    def test_empty_intersection_is_contract_failure(self):
        from adapter import _intersection, gram, ContractError
        with self.assertRaisesRegex(ContractError, 'empty'):
            _intersection(gram.Interval(Q(0), Q(1)), gram.Interval(Q(2), Q(3)))


if __name__ == '__main__':
    unittest.main(verbosity=2)
