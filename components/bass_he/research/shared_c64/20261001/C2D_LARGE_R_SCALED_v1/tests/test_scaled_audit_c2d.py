"""Manufactured scalar records only: no eigensolves or physical integrals."""
import copy
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'code'))
from scaled_audit import pair_audit, quartet_audit

CONTRACT = json.loads((ROOT / 'CONTRACT.json').read_text())


def manufactured(profile='base', radius=64, tier='profiles_by_R'):
    cfg = copy.deepcopy(CONTRACT[tier][str(radius)][profile])
    energies = [-2., -.5]
    gap = energies[1] - energies[0]
    lo, lb = .186 * radius, -.248 / radius ** 2
    momentum = 3 * (lo - lb) / radius
    if profile != 'tail':
        edges = [1 + 2 * cfg['radial_extent'] / radius * (j / cfg['radial_elements']) ** 2
                 for j in range(cfg['radial_elements'] + 1)]
    else:
        base = CONTRACT[tier][str(radius)]['base']
        n, k = base['radial_elements'], cfg['radial_elements'] - base['radial_elements']
        edges = [1 + 60 / radius * (j / n) ** 2 for j in range(n + 1)]
        edges += [1 + 2 / radius * (30 + 10 * j / k) for j in range(1, k + 1)]
    states = []
    for sector in (0, 1):
        phase = {'algorithm': CONTRACT['phase']['algorithm']}
        for axis in ('radial', 'angular'):
            phase[axis] = {'dominant_index': 0, 'dominant_coordinate': 1.1 if axis == 'radial' else .99,
                           'dominant_value': 1., 'negative_l2_fraction': 0.,
                           'quadrature_points': cfg[axis + '_elements'] * cfg['quadrature_order']}
        states.append({'m': sector, 'R': radius, 'ZA': 1., 'ZB': 2., 'energy': energies[sector],
                       'config': copy.deepcopy(cfg), 'actual_radial_edges': list(edges),
                       'actual_radial_elements': len(edges) - 1, 'xi_max': edges[-1],
                       'residuals': {'radial_discrete_relative': 1e-14, 'angular_discrete_relative': 1e-14,
                                     'matching_absolute': 1e-12},
                       'separation_radial': 1., 'separation_angular': -1., 'phase': phase})
    d = {'L_O_bar': lo, 'L_B_bar': lb, 'p_x_bar': momentum, 'dipole_x': momentum / gap,
         'norm_g': 1., 'norm_b': 1.}
    ta = -gap * lb / radius
    f = {'L_O_bar': lo, 'L_B_bar': lb, 'T_A': ta, 'T_B': ta + 3 * gap * lo / (2 * radius), 'gap': gap}
    return {'R': radius, 'energies': energies, 'states': states,
            'direct': {str(q): dict(d) for q in CONTRACT['operators']['direct_orders']},
            'force': {str(q): dict(f) for q in CONTRACT['operators']['force_orders']},
            'dark': {str(q): {'L_dark_O_bar': 0.} for q in CONTRACT['operators']['phi_nodes']}}


class LargeRScalarAuditTests(unittest.TestCase):
    def test_two_radii_two_tiers_are_admitted_without_continuum_claim(self):
        for radius in (32, 64):
            for tier in ('profiles_by_R', 'fallback_profiles_by_R'):
                values = {p: manufactured(p, radius, tier) for p in ('base', 'h', 'p', 'tail')}
                result = quartet_audit(values, CONTRACT)
                self.assertTrue(result['pass'], result)
                self.assertEqual(result['checks']['matched_tier'], tier)
                self.assertFalse(result['continuum_error_enclosure'])
                self.assertEqual(result['scaled']['Q_B']['direct'], .248)

    def test_QB_force_error_fails_scaled_despite_raw_pass(self):
        value = manufactured()
        for row in value['force'].values():
            row['L_B_bar'] += 1e-9
        result = pair_audit(value, CONTRACT)
        self.assertTrue(result['gates']['direct_force_L_B_raw'])
        self.assertFalse(result['gates']['direct_force_Q_B_scaled'])
        self.assertTrue(result['gates']['direct_force_Q_O_scaled'])
        self.assertEqual(result['checks']['direct_force_terminal_comparisons'], 9)

    def test_all_three_by_three_lane_combinations_are_checked(self):
        value = manufactured()
        value['force']['12']['L_B_bar'] += 3e-11
        value['direct']['16']['L_B_bar'] -= 3e-11
        result = pair_audit(value, CONTRACT)
        self.assertGreater(result['checks']['direct_force_scaled_abs']['Q_B'], 2e-7)
        self.assertFalse(result['gates']['direct_force_Q_B_scaled'])
        self.assertEqual(result['selected_direct']['L_B_bar'], result['selected_force']['L_B_bar'])

    def test_QB_quadrature_has_both_increments_and_separate_observables(self):
        value = manufactured()
        value['direct']['16']['L_B_bar'] += 1e-11
        result = pair_audit(value, CONTRACT)
        self.assertTrue(result['gates']['direct_quadrature_raw'])
        self.assertFalse(result['gates']['direct_quadrature_Q_B_scaled'])
        self.assertTrue(result['gates']['direct_quadrature_Q_O_scaled'])
        increments = result['checks']['quadrature_increments']['direct']
        self.assertEqual(len(increments), 2)
        self.assertGreater(increments[0]['scaled_abs']['Q_B'], 1e-8)
        self.assertEqual(increments[1]['scaled_abs']['Q_B'], 0.)

    def test_origin_and_momentum_have_distinct_large_R_amplification(self):
        value = manufactured()
        for row in value['direct'].values():
            row['L_B_bar'] += 5e-11
        result = pair_audit(value, CONTRACT)
        self.assertTrue(result['gates']['origin_raw'])
        self.assertTrue(result['gates']['origin_Q_O_scaled'])
        self.assertFalse(result['gates']['origin_Q_B_scaled'])
        value = manufactured()
        for row in value['direct'].values():
            row['dipole_x'] += 2e-12 / 1.5
        result = pair_audit(value, CONTRACT)
        self.assertTrue(result['gates']['momentum_raw'])
        self.assertTrue(result['gates']['momentum_Q_O_scaled'])
        self.assertFalse(result['gates']['momentum_Q_B_scaled'])
        self.assertAlmostEqual(result['checks']['momentum_scaled_abs']['Q_B'], 64 ** 3 * 2e-12 / 3, delta=1e-11)

    def test_phase_sign_and_sampled_negative_mass_are_scientific_gates(self):
        for key, mutation, gate in [('dominant_value', -1., 'phase_positive'),
                                    ('negative_l2_fraction', 2e-12, 'phase_negative_L2')]:
            value = manufactured()
            value['states'][1]['phase']['angular'][key] = mutation
            result = pair_audit(value, CONTRACT)
            self.assertTrue(result['gates']['input_valid'])
            self.assertFalse(result['gates'][gate])

    def test_phase_bad_algorithm_count_and_nonfinite_reject_input(self):
        for mutation in ('algorithm', 'count', 'nan', 'fraction'):
            value = manufactured()
            phase = value['states'][0]['phase']
            if mutation == 'algorithm':
                phase['algorithm'] = 'first_tail_value'
            elif mutation == 'count':
                phase['radial']['quadrature_points'] += 1
            elif mutation == 'nan':
                phase['angular']['dominant_value'] = math.nan
            else:
                phase['radial']['negative_l2_fraction'] = -1e-12
            self.assertFalse(pair_audit(value, CONTRACT)['gates']['input_valid'], mutation)

    def test_partial_fallback_is_rejected_complete_retains_original(self):
        value = manufactured()
        original = copy.deepcopy(value)
        value['direct']['16']['L_B_bar'] += 1e-5
        value['direct']['40'] = dict(value['direct']['32'])
        self.assertFalse(pair_audit(value, CONTRACT)['gates']['input_valid'])
        value['direct']['48'] = dict(value['direct']['32'])
        before = copy.deepcopy(value)
        result = pair_audit(value, CONTRACT)
        self.assertTrue(result['pass'], result)
        self.assertEqual(result['terminal_orders']['direct'], [32, 40, 48])
        self.assertEqual(value, before)
        self.assertNotEqual(value['direct']['16'], original['direct']['16'])

    def test_only_registered_profiles_for_this_radius_are_allowed(self):
        value = manufactured(radius=64)
        wrong = CONTRACT['profiles_by_R']['32']['base']
        for state in value['states']:
            state['config'] = copy.deepcopy(wrong)
        self.assertFalse(pair_audit(value, CONTRACT)['gates']['input_valid'])
        values = {p: manufactured(p) for p in ('base', 'h', 'p', 'tail')}
        values['p'] = manufactured('p', tier='fallback_profiles_by_R')
        result = quartet_audit(values, CONTRACT)
        self.assertFalse(result['gates']['same_registered_profile_tier'])

    def test_tail_requires_exact_original_64_or_128_cell_prefix(self):
        for tier in ('profiles_by_R', 'fallback_profiles_by_R'):
            values = {p: manufactured(p, tier=tier) for p in ('base', 'h', 'p', 'tail')}
            for state in values['tail']['states']:
                state['actual_radial_edges'][4] += 1e-10
            result = quartet_audit(values, CONTRACT)
            self.assertTrue(result['pairs']['tail']['pass'])
            self.assertFalse(result['gates']['tail_inner_knots_exact'])

    def test_QB_spatial_failure_is_reported_even_if_pair_and_raw_pass(self):
        values = {p: manufactured(p) for p in ('base', 'h', 'p', 'tail')}
        # Preserve the exact origin identity and direct/force agreement.
        for lane in ('direct', 'force'):
            for row in values['h'][lane].values():
                row['L_O_bar'] += 1e-9
                row['L_B_bar'] += 1e-9
        result = quartet_audit(values, CONTRACT)
        self.assertTrue(result['pairs']['h']['pass'], result['pairs']['h'])
        self.assertTrue(result['gates']['h_direct_L_B_raw'])
        self.assertFalse(result['gates']['h_direct_Q_B_scaled'])
        self.assertTrue(result['gates']['h_direct_Q_O_scaled'])

    def test_raw_other_observables_norm_dark_residual_energy_not_discarded(self):
        for kind in ('dipole', 'T_A', 'norm', 'dark', 'residual'):
            value = manufactured()
            if kind == 'dipole':
                value['direct']['16']['dipole_x'] += 2e-8
                gate = 'direct_quadrature_raw'
            elif kind == 'T_A':
                value['force']['12']['T_A'] += 2e-8
                gate = 'force_quadrature_raw'
            elif kind == 'norm':
                value['direct']['32']['norm_g'] += 2e-10
                gate = 'norm'
            elif kind == 'dark':
                value['dark']['32']['L_dark_O_bar'] = 2e-12
                gate = 'dark'
            else:
                value['states'][0]['residuals']['radial_discrete_relative'] = 2e-9
                gate = 'algebraic_residual'
            self.assertFalse(pair_audit(value, CONTRACT)['gates'][gate], kind)
        values = {p: manufactured(p) for p in ('base', 'h', 'p', 'tail')}
        for i in (0, 1):
            values['p']['energies'][i] += 2e-8
            values['p']['states'][i]['energy'] += 2e-8
        gap = values['p']['energies'][1] - values['p']['energies'][0]
        for f in values['p']['force'].values():
            f['gap'] = gap
        result = quartet_audit(values, CONTRACT)
        self.assertFalse(result['gates']['p_energy_raw'])

    def test_nonfinite_domain_energy_force_gap_and_malformed_inputs_fail_closed(self):
        for mutation in ('nan', 'domain', 'energy', 'force_gap'):
            value = manufactured()
            if mutation == 'nan':
                value['direct']['32']['norm_g'] = math.nan
            elif mutation == 'domain':
                value['states'][1]['xi_max'] += 1
            elif mutation == 'energy':
                value['states'][0]['energy'] += 1e-5
            else:
                value['force']['28']['gap'] += 1e-5
            self.assertFalse(pair_audit(value, CONTRACT)['gates']['input_valid'], mutation)
        for value in (None, [], {}, {'R': 18}, {'R': True}):
            self.assertFalse(pair_audit(value, CONTRACT)['pass'])

    def test_signed_brightness_and_resolution_are_not_replaced_by_abs(self):
        value = manufactured()
        for lane in ('direct', 'force'):
            for row in value[lane].values():
                row['L_B_bar'] = 1e-4
        result = pair_audit(value, CONTRACT)
        self.assertFalse(result['gates']['positive_bright_Q_B'])
        self.assertFalse(result['gates']['bright_resolved_Q_B_scaled'])
        value = manufactured()
        for lane in ('direct', 'force'):
            for row in value[lane].values():
                row['L_O_bar'] = 1e-6
        result = pair_audit(value, CONTRACT)
        self.assertTrue(result['gates']['positive_bright_Q_O'])
        self.assertFalse(result['gates']['bright_legacy_absolute_LO'])
        self.assertFalse(result['gates']['bright_resolved_Q_O_scaled'])


if __name__ == '__main__':
    unittest.main()
