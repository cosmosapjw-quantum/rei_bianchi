"""C2c scalar continuation and parity audits, staged outside frozen package.

No solver imports, file reads, physical evaluations, or writes at import time.

API:
  continuation_audit(records, contract)
    records: arbitrary task_id -> overlap_integral.pair_overlap DATA.value.
    Groups are inferred from (R_left,R_right,m); q must be unique per group.
  parity_audit(records, references, contract)
    records and references: maps with keys '0','1','2','3', in the exact order
    of contract['parity_cases']; values are the corresponding physical result
    dicts (not whole DATA envelopes). The caller binds verified task and state
    identities before calling: direct result values do not contain R or q.

All acceptance criteria are empirical, with no continuum certificate.
Malformed or missing inputs fail closed and are reported separately.
Executing this file runs only manufactured scalar self-tests.
"""
import math


DIRECT_KEYS = ('L_O_bar', 'L_B_bar', 'p_x_bar', 'dipole_x', 'norm_g', 'norm_b')
FORCE_KEYS = ('L_O_bar', 'L_B_bar', 'T_A', 'T_B', 'gap')
OVERLAP_KEYS = ('overlap', 'normalized_overlap', 'left_domain_overlap',
                'right_domain_overlap', 'directional_difference_abs',
                'self_norm_left', 'self_norm_right', 'max_self_norm_error_abs')
INCREMENT_KEYS = ('left_domain_overlap', 'right_domain_overlap', 'normalized_overlap')


def _finite(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(name + ': finite real number required')
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(name + ': nonfinite')
    return value


def _positive(value, name):
    value = _finite(value, name)
    if value <= 0:
        raise ValueError(name + ': positive number required')
    return value


def _integer(value, name):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(name + ': integer required')
    return value


def _close_scalar(a, b):
    # Validate cached algebra, not a scientific quadrature tolerance. The
    # producer uses these same elementary formulas with binary64 scalars.
    return abs(a - b) <= 64 * 2.0 ** -53 * max(1., abs(a), abs(b))


def _read_overlap(record):
    radius_left = _positive(record['R_left'], 'R_left')
    radius_right = _positive(record['R_right'], 'R_right')
    if radius_left >= radius_right:
        raise ValueError('overlap edge must be in ascending R order')
    sector = _integer(record['m'], 'm')
    order = _integer(record['order'], 'order')
    values = {key: _finite(record[key], key) for key in OVERLAP_KEYS}
    norm_left = values['self_norm_left']
    norm_right = values['self_norm_right']
    if min(norm_left, norm_right) <= 0:
        raise ValueError('overlap self norms must be positive')
    mean = (values['left_domain_overlap'] + values['right_domain_overlap']) / 2
    normalized = mean / math.sqrt(norm_left * norm_right)
    directional = abs(values['left_domain_overlap'] - values['right_domain_overlap'])
    norm_error = max(abs(norm_left - 1), abs(norm_right - 1))
    for key, expected in [('overlap', mean), ('normalized_overlap', normalized),
                          ('directional_difference_abs', directional),
                          ('max_self_norm_error_abs', norm_error)]:
        if not math.isfinite(expected) or not _close_scalar(values[key], expected):
            raise ValueError('inconsistent cached overlap quantity: ' + key)
    phase = _integer(record['phase_factor_suggestion'], 'phase_factor_suggestion')
    if phase != (1 if mean >= 0 else -1):
        raise ValueError('cached phase suggestion disagrees with overlap sign')
    return (radius_left, radius_right, sector), order, values


def _step_audit(sequence, tolerance, minimum):
    """Records are already validated and sorted. Inspect last three only."""
    terminal = sequence[-3:]
    if len(terminal) != 3:
        raise ValueError('three overlap orders required')
    increments = [max(abs(high[2][key] - low[2][key]) for key in INCREMENT_KEYS)
                  for low, high in zip(terminal, terminal[1:])]
    max_direction = max(row[2]['directional_difference_abs'] for row in terminal)
    max_norm = max(row[2]['max_self_norm_error_abs'] for row in terminal)
    selected = terminal[-1][2]
    magnitude = abs(selected['normalized_overlap'])
    gates = {'two_quadrature_increments': max(increments) <= tolerance,
             'three_directional_checks': max_direction <= tolerance,
             'three_self_norm_checks': max_norm <= tolerance,
             'minimum_overlap': magnitude >= minimum,
             'cauchy_schwarz': magnitude <= 1 + tolerance}
    passed = all(gates.values())
    return {'pass': passed, 'gates': gates,
            'failed_gates': [key for key, ok in gates.items() if not ok],
            'terminal_orders': [row[0] for row in terminal],
            'selected_order': terminal[-1][0], 'selected': dict(selected),
            'quadrature_increments_abs': increments,
            'directional_difference_max_abs': max_direction,
            'self_norm_error_max_abs': max_norm,
            'phase_factor': (1 if selected['overlap'] >= 0 else -1) if passed else None,
            'status': 'PASS_FIXED_M_LOCAL_STEP' if passed else 'HOLD',
            'input_task_ids': [row[1] for row in sequence]}


def continuation_audit(records, contract):
    """Audit six local edge-sector groups and propagate phase in ascending R."""
    try:
        if not isinstance(records, dict):
            raise ValueError('task-id -> value mapping required')
        cfg = contract['continuation']
        tolerance = _positive(cfg['tolerance'], 'overlap tolerance')
        minimum = _positive(cfg['minimum_overlap'], 'minimum overlap')
        if minimum > 1:
            raise ValueError('minimum overlap must not exceed one')
        edge_list = [tuple(edge) for edge in cfg['edges']]
        if (edge_list != sorted(edge_list) or len(edge_list) != len(set(edge_list))
                or any(a <= 0 or a >= b for a, b in edge_list)
                or any(previous[1] != following[0] for previous, following in zip(edge_list, edge_list[1:]))):
            raise ValueError('contract edges must form a unique ascending chain')
        sectors = cfg['sectors']
        if sectors != [0, 1]:
            raise ValueError('registered sectors must be [0,1]')
        expected = {(left, right, sector) for left, right in edge_list for sector in sectors}
        initial = cfg['orders']
        fallback = cfg['fallback_orders']
        if len(initial) != 3 or initial != sorted(set(initial)) or fallback != sorted(set(fallback)):
            raise ValueError('invalid registered overlap order sequence')
        allowed = initial + fallback
        if allowed != sorted(set(allowed)):
            raise ValueError('overlap fallback must extend initial orders')
        if len(records) > contract['operational_limits']['overlap_edge_orders_max']:
            raise ValueError('overlap evaluation count exceeds registered cap')
        groups = {key: {} for key in expected}
        for task_id, record in records.items():
            if not isinstance(task_id, str) or not task_id:
                raise ValueError('nonempty task ID required')
            key, order, values = _read_overlap(record)
            if key not in expected or order not in allowed:
                raise ValueError('unregistered overlap edge/sector/order')
            if order in groups[key]:
                raise ValueError('duplicate overlap edge-sector-order')
            groups[key][order] = (order, task_id, values)
        rows = []
        row_by_group = {}
        for key in sorted(groups):
            by_order = groups[key]
            if not set(initial).issubset(by_order):
                raise ValueError('missing initial overlap orders at ' + repr(key))
            initial_audit = _step_audit([by_order[q] for q in initial], tolerance, minimum)
            added = [q for q in fallback if q in by_order]
            if added:
                if initial_audit['pass']:
                    raise ValueError('fallback supplied for already-passing edge ' + repr(key))
                if added != fallback[:len(added)]:
                    raise ValueError('overlap fallback skips a registered order')
            sequence = [by_order[q] for q in sorted(by_order)]
            row = {'R_left': key[0], 'R_right': key[1], 'm': key[2],
                   'initial_audit': initial_audit, 'fallback_orders_used': added,
                   **_step_audit(sequence, tolerance, minimum)}
            rows.append(row)
            row_by_group[key] = row
        radii = [edge_list[0][0]] + [edge[1] for edge in edge_list]
        chains = {}
        for sector in sectors:
            phase = 1
            chain = [{'R': radii[0], 'phase': phase, 'status': 'REFERENCE_PHASE'}]
            for left, right in edge_list:
                row = row_by_group[(left, right, sector)]
                phase = phase * row['phase_factor'] if phase is not None and row['pass'] else None
                chain.append({'R': right, 'phase': phase,
                              'status': 'ADOPTED' if phase is not None else 'HOLD'})
            chains[str(sector)] = chain
        coupling_phase = []
        for index, radius in enumerate(radii):
            g_phase = chains['0'][index]['phase']
            b_phase = chains['1'][index]['phase']
            coupling_phase.append({'R': radius,
                                   'factor': None if g_phase is None or b_phase is None else g_phase * b_phase})
        failed = [{'edge': [row['R_left'], row['R_right']], 'm': row['m'],
                   'failed_gates': row['failed_gates']} for row in rows if not row['pass']]
        return {'pass': not failed, 'input_valid': True, 'rows': rows, 'failed': failed,
                'edge_sector_count': len(rows), 'evaluation_count': len(records),
                'phase_chains': chains, 'coupling_phase': coupling_phase,
                'phase_reference': {'R': radii[0], 'm0': 1, 'm1': 1,
                                    'meaning': 'unmodified positive-meridional reference at smallest R'},
                'scope': 'local fixed-m physical overlap only; no hidden-crossing or rank-five certificate',
                'continuum_error_enclosure': False}
    except (KeyError, TypeError, ValueError, OverflowError, ZeroDivisionError, IndexError) as exc:
        return {'pass': False, 'input_valid': False, 'input_error': str(exc),
                'rows': [], 'failed': [{'failed_gates': ['input_valid']}],
                'phase_chains': None, 'coupling_phase': None}


def parity_audit(records, references, contract):
    """Compare four preregistered physical result dictionaries, by case index."""
    try:
        cases = contract['parity_cases']
        expected = {str(index) for index in range(len(cases))}
        if (len(cases) != 4 or not isinstance(records, dict) or not isinstance(references, dict)
                or set(records) != expected or set(references) != expected):
            raise ValueError('exactly four parity cases indexed as strings 0..3 required')
        raw_tolerance = _positive(contract['raw_criteria']['native_reference_operator_abs'], 'raw parity tolerance')
        scaled_tolerance = _positive(contract['scaled_criteria']['native_parity_abs'], 'scaled parity tolerance')
        rows = []
        for index, case in enumerate(cases):
            key = str(index)
            actual, reference = records[key], references[key]
            kind = case['kind']
            if kind not in ('direct', 'force', 'overlap'):
                raise ValueError('unregistered parity operator kind')
            quantities = DIRECT_KEYS if kind == 'direct' else FORCE_KEYS if kind == 'force' else OVERLAP_KEYS
            deltas = {quantity: abs(_finite(actual[quantity], 'actual.' + quantity)
                                    - _finite(reference[quantity], 'reference.' + quantity))
                      for quantity in quantities}
            if any(not math.isfinite(delta) for delta in deltas.values()):
                raise ValueError('overflow in parity delta')
            metadata_ok = True
            if kind == 'overlap':
                for record in (actual, reference):
                    group, order, _ = _read_overlap(record)
                    if group != (*case['edge'], case['sector']) or order != case['order']:
                        metadata_ok = False
                metadata_ok = metadata_ok and actual['phase_factor_suggestion'] == reference['phase_factor_suggestion']
            raw_max = max(deltas.values())
            scaled_lo = deltas['L_O_bar'] / _positive(case['R'], 'parity radius') ** 3 if kind != 'overlap' else None
            gates = {'physical_quantities_raw': raw_max <= raw_tolerance,
                     'case_metadata': metadata_ok}
            if kind != 'overlap':
                gates['L_O_scaled'] = scaled_lo <= scaled_tolerance
            rows.append({'case_index': index, 'case': dict(case), 'pass': all(gates.values()),
                         'gates': gates, 'failed_gates': [name for name, ok in gates.items() if not ok],
                         'quantity_deltas_abs': deltas, 'maximum_raw_delta_abs': raw_max,
                         'L_O_scaled_delta_abs': scaled_lo})
        return {'pass': all(row['pass'] for row in rows), 'input_valid': True,
                'rows': rows, 'failed_case_indices': [row['case_index'] for row in rows if not row['pass']],
                'raw_tolerance': raw_tolerance, 'scaled_L_O_tolerance': scaled_tolerance,
                'task_and_state_identity_binding': 'caller-required; scalar audit does not validate archive identity',
                'scope': 'same-state same-order native/reference numerical parity only'}
    except (KeyError, TypeError, ValueError, OverflowError, ZeroDivisionError) as exc:
        return {'pass': False, 'input_valid': False, 'input_error': str(exc),
                'rows': [], 'failed_case_indices': []}


def _self_test():
    import copy
    import unittest

    cfg = {'continuation': {'edges': [[.03125, .0625], [.0625, .125], [.125, .25]],
                            'sectors': [0, 1], 'orders': [16, 24, 32],
                            'fallback_orders': [48, 64], 'tolerance': 1e-7,
                            'minimum_overlap': .5},
           'operational_limits': {'overlap_edge_orders_max': 30},
           'raw_criteria': {'native_reference_operator_abs': 1e-11},
           'scaled_criteria': {'native_parity_abs': 1e-8},
           'parity_cases': [{'kind': 'direct', 'R': .25, 'order': 24},
                            {'kind': 'direct', 'R': .03125, 'order': 24},
                            {'kind': 'force', 'R': .03125, 'order': 20},
                            {'kind': 'overlap', 'edge': [.03125, .0625], 'sector': 0, 'order': 24}]}

    def overlap(left, right, sector, order, mean=.9, direction=0., norm_left=1., norm_right=1.):
        a, b = mean + direction / 2, mean - direction / 2
        mean = (a + b) / 2
        return {'R_left': left, 'R_right': right, 'm': sector, 'order': order,
                'overlap': mean, 'normalized_overlap': mean / math.sqrt(norm_left * norm_right),
                'left_domain_overlap': a, 'right_domain_overlap': b,
                'directional_difference_abs': abs(a - b), 'self_norm_left': norm_left,
                'self_norm_right': norm_right, 'max_self_norm_error_abs': max(abs(norm_left - 1), abs(norm_right - 1)),
                'phase_factor_suggestion': 1 if mean >= 0 else -1}

    def record_map():
        return {f'{edge_index}_{sector}_{order}': overlap(left, right, sector, order)
                for edge_index, (left, right) in enumerate(cfg['continuation']['edges'])
                for sector in (0, 1) for order in (16, 24, 32)}

    def parity_map():
        direct = dict(zip(DIRECT_KEYS, [1e-5, -.01, .8, .2, 1., 1.]))
        force = dict(zip(FORCE_KEYS, [1e-5, -.01, .9, .901, 3.]))
        return {'0': dict(direct), '1': dict(direct), '2': force,
                '3': overlap(.03125, .0625, 0, 24)}

    class ScalarTests(unittest.TestCase):
        def test_all_pass(self):
            result = continuation_audit(record_map(), cfg)
            self.assertTrue(result['pass'], result)
            self.assertEqual(result['edge_sector_count'], 6)
            self.assertEqual([row['factor'] for row in result['coupling_phase']], [1, 1, 1, 1])
            data = parity_map()
            self.assertTrue(parity_audit(data, copy.deepcopy(data), cfg)['pass'])

        def test_cumulative_negative_phase_and_stop_after_failure(self):
            records = record_map()
            for q in (16, 24, 32):
                records[f'0_0_{q}'] = overlap(.03125, .0625, 0, q, mean=-.9)
                records[f'1_0_{q}'] = overlap(.0625, .125, 0, q, mean=-.9)
            result = continuation_audit(records, cfg)
            self.assertEqual([row['phase'] for row in result['phase_chains']['0']], [1, -1, 1, 1])
            for q in (16, 24, 32):
                records[f'1_0_{q}'] = overlap(.0625, .125, 0, q, mean=.4)
            result = continuation_audit(records, cfg)
            self.assertFalse(result['pass'])
            self.assertEqual([row['phase'] for row in result['phase_chains']['0']], [1, -1, None, None])

        def test_last_three_auxiliary_checks_and_two_increments(self):
            records = record_map()
            records['0_0_16'] = overlap(.03125, .0625, 0, 16, direction=2e-7)
            result = continuation_audit(records, cfg)
            row = result['rows'][0]
            self.assertFalse(row['gates']['three_directional_checks'])
            self.assertEqual(row['quadrature_increments_abs'][1], 0.)

        def test_norm_recomputed_and_false_cache_rejected(self):
            records = record_map()
            records['0_0_16'] = overlap(.03125, .0625, 0, 16, norm_left=1 + 2e-7)
            self.assertFalse(continuation_audit(records, cfg)['pass'])
            records['0_0_16']['max_self_norm_error_abs'] = 0.
            self.assertFalse(continuation_audit(records, cfg)['input_valid'])

        def test_fallback_only_failed_edge(self):
            records = record_map()
            records['0_0_48'] = overlap(.03125, .0625, 0, 48)
            self.assertFalse(continuation_audit(records, cfg)['input_valid'])
            records['0_0_16'] = overlap(.03125, .0625, 0, 16, mean=.8)
            records['0_0_64'] = overlap(.03125, .0625, 0, 64)
            result = continuation_audit(records, cfg)
            self.assertTrue(result['pass'], result)
            self.assertEqual(result['rows'][0]['terminal_orders'], [32, 48, 64])
            self.assertFalse(result['rows'][0]['initial_audit']['pass'])

        def test_missing_duplicate_and_nonfinite_fail_closed(self):
            records = record_map()
            del records['0_0_16']
            self.assertFalse(continuation_audit(records, cfg)['input_valid'])
            records = record_map()
            records['duplicate'] = copy.deepcopy(records['0_0_16'])
            self.assertFalse(continuation_audit(records, cfg)['input_valid'])
            records = record_map()
            records['0_0_16']['normalized_overlap'] = math.nan
            self.assertFalse(continuation_audit(records, cfg)['input_valid'])

        def test_raw_pass_scaled_parity_fail(self):
            records, refs = parity_map(), parity_map()
            records['1']['L_O_bar'] += 1e-12
            result = parity_audit(records, refs, cfg)
            self.assertTrue(result['rows'][1]['gates']['physical_quantities_raw'])
            self.assertFalse(result['rows'][1]['gates']['L_O_scaled'])
            self.assertFalse(result['pass'])

        def test_force_T_and_overlap_self_norm_parity_checked(self):
            records, refs = parity_map(), parity_map()
            records['2']['T_A'] += 2e-11
            self.assertFalse(parity_audit(records, refs, cfg)['rows'][2]['pass'])
            records = parity_map()
            records['3'] = overlap(.03125, .0625, 0, 24, norm_left=1 + 2e-11)
            self.assertFalse(parity_audit(records, refs, cfg)['rows'][3]['pass'])

        def test_wrong_overlap_metadata_missing_case_and_bad_phase(self):
            records, refs = parity_map(), parity_map()
            records['3']['order'] = 32
            self.assertFalse(parity_audit(records, refs, cfg)['rows'][3]['gates']['case_metadata'])
            del records['0']
            self.assertFalse(parity_audit(records, refs, cfg)['input_valid'])
            records = record_map()
            records['0_0_16']['phase_factor_suggestion'] = -1
            self.assertFalse(continuation_audit(records, cfg)['input_valid'])

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ScalarTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == '__main__':
    _self_test()
