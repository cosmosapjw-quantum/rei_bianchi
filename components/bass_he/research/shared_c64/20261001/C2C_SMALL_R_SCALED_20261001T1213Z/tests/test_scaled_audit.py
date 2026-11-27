"""Manufactured scalar records: no eigenstates or physical integrations."""
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


def manufactured(profile='base', radius=.03125, tier='profiles'):
    cfg = copy.deepcopy(CONTRACT[tier][profile])
    gap = 3.
    energies = [-4., -1.]
    lo = .35 * radius ** 3
    momentum = .8
    lb = lo - radius * momentum / 3
    if profile != 'tail':
        edges = [1 + 2 * cfg['radial_extent'] / radius * (j / cfg['radial_elements']) ** 2
                 for j in range(cfg['radial_elements'] + 1)]
    else:
        base = CONTRACT[tier]['base']
        n = base['radial_elements']
        k = cfg['radial_elements'] - n
        edges = [1 + 60 / radius * (j / n) ** 2 for j in range(n + 1)]
        edges += [1 + 2 / radius * (30 + 10 * j / k) for j in range(1, k + 1)]
    states = []
    for sector in (0, 1):
        states.append({'m': sector, 'R': radius, 'ZA': 1., 'ZB': 2.,
                       'energy': energies[sector], 'config': copy.deepcopy(cfg),
                       'actual_radial_edges': list(edges), 'actual_radial_elements': len(edges) - 1,
                       'xi_max': edges[-1],
                       'residuals': {'radial_discrete_relative': 1e-14,
                                     'angular_discrete_relative': 1e-14,
                                     'matching_absolute': 1e-12},
                       'separation_radial': 1., 'separation_angular': -1.})
    d = {'L_O_bar': lo, 'L_B_bar': lb, 'p_x_bar': momentum,
         'dipole_x': momentum / gap, 'norm_g': 1., 'norm_b': 1.}
    ta = -gap * lb / radius
    f = {'L_O_bar': lo, 'L_B_bar': lb, 'T_A': ta,
         'T_B': ta + 3 * gap * lo / (2 * radius), 'gap': gap}
    return {'R': radius, 'energies': energies, 'states': states,
            'direct': {str(q): dict(d) for q in CONTRACT['operators']['direct_orders']},
            'force': {str(q): dict(f) for q in CONTRACT['operators']['force_orders']},
            'dark': {str(q): {'L_dark_O_bar': 0.} for q in CONTRACT['operators']['phi_nodes']}}


class ScaledAuditTests(unittest.TestCase):
    def test_manufactured_pair_and_both_quartet_tiers(self):
        for tier in ('profiles', 'fallback_profiles'):
            values = {p: manufactured(p, tier=tier) for p in ('base', 'h', 'p', 'tail')}
            audit = quartet_audit(values, CONTRACT)
            self.assertTrue(audit['pass'], audit)
            self.assertEqual(audit['checks']['matched_tier'], tier)
            self.assertFalse(audit['continuum_error_enclosure'])

    def test_raw_pass_scaled_force_lane_fail_at_smallest_R(self):
        value = manufactured()
        for f in value['force'].values():
            f['L_O_bar'] += 1e-10
        result = pair_audit(value, CONTRACT)
        self.assertTrue(result['gates']['direct_force_L_O_raw'])
        self.assertFalse(result['gates']['direct_force_L_O_scaled'])
        self.assertFalse(result['pass'])

    def test_origin_scaling_and_induced_momentum(self):
        value = manufactured()
        for d in value['direct'].values():
            d['L_B_bar'] += 5e-12
        result = pair_audit(value, CONTRACT)
        self.assertTrue(result['gates']['origin_raw'])
        self.assertFalse(result['gates']['origin_scaled'])
        value = manufactured()
        for d in value['direct'].values():
            d['dipole_x'] += 1e-9 / 3
        result = pair_audit(value, CONTRACT)
        self.assertTrue(result['gates']['momentum_raw'])
        self.assertFalse(result['gates']['momentum_scaled'])
        self.assertAlmostEqual(result['checks']['momentum_induced_L_O_scaled_abs'],
                               1e-9 / (3 * value['R'] ** 2), delta=1e-13)

    def test_three_orders_and_two_increments_are_required(self):
        value = manufactured()
        del value['direct']['16']
        result = pair_audit(value, CONTRACT)
        self.assertFalse(result['gates']['input_valid'])
        value = manufactured()
        value['direct']['16']['L_O_bar'] += 1e-10
        result = pair_audit(value, CONTRACT)
        self.assertFalse(result['gates']['direct_quadrature_scaled'])
        self.assertEqual(len(result['checks']['quadrature_increments']['direct']), 2)
        self.assertEqual(result['checks']['quadrature_increments']['direct'][1]['L_O_scaled_abs'], 0.)

    def test_tail_changed_interior_knots_fails_both_state_check(self):
        values = {p: manufactured(p) for p in ('base', 'h', 'p', 'tail')}
        for state in values['tail']['states']:
            state['actual_radial_edges'][4] += 1e-10
        result = quartet_audit(values, CONTRACT)
        self.assertTrue(result['pairs']['tail']['pass'])
        self.assertFalse(result['gates']['tail_inner_knots_exact'])
        self.assertFalse(result['pass'])

    def test_scaled_spatial_failure_retains_raw_pass(self):
        values = {p: manufactured(p) for p in ('base', 'h', 'p', 'tail')}
        for lane in ('direct', 'force'):
            for record in values['h'][lane].values():
                record['L_O_bar'] += 1e-9
                record['L_B_bar'] += 1e-9
        result = quartet_audit(values, CONTRACT)
        self.assertTrue(result['pairs']['h']['pass'])
        self.assertTrue(result['gates']['h_direct_L_O_raw'])
        self.assertFalse(result['gates']['h_direct_L_O_scaled'])

    def test_nonfinite_and_domain_mismatch_rejected(self):
        for mutation in ('nan', 'domain', 'energy', 'force_gap'):
            value = manufactured()
            if mutation == 'nan':
                value['direct']['32']['norm_g'] = math.nan
            elif mutation == 'domain':
                value['states'][1]['xi_max'] += 1.
            elif mutation == 'energy':
                value['states'][0]['energy'] += 1e-5
            else:
                value['force']['28']['gap'] += 1e-5
            self.assertFalse(pair_audit(value, CONTRACT)['gates']['input_valid'], mutation)

    def test_registered_fallback_uses_only_last_three_orders(self):
        value = manufactured()
        value['direct']['16']['L_O_bar'] += 1e-5
        for q in CONTRACT['operators']['fallback_direct_orders']:
            value['direct'][str(q)] = dict(value['direct']['32'])
        result = pair_audit(value, CONTRACT)
        self.assertTrue(result['pass'], result)
        self.assertEqual(result['terminal_orders']['direct'], [32, 40, 48])
        self.assertEqual(result['selected_orders']['direct'], 48)

    def test_every_direct_quantity_and_force_T_are_checked(self):
        for lane, key in [('direct', 'dipole_x'), ('force', 'T_A')]:
            value = manufactured()
            order = min(value[lane], key=int)
            value[lane][order][key] += 2e-8
            result = pair_audit(value, CONTRACT)
            self.assertFalse(result['gates'][lane + '_quadrature_raw'])

    def test_nonpositive_and_nonbound_are_not_admitted(self):
        value = manufactured()
        for lane in ('direct', 'force'):
            for record in value[lane].values():
                record['L_O_bar'] = 0.
        result = pair_audit(value, CONTRACT)
        self.assertFalse(result['gates']['positive_bright_L_O'])
        self.assertIsNone(result['conditions']['origin'])
        value = manufactured()
        value['energies'][1] = 1.
        value['states'][1]['energy'] = 1.
        for record in value['force'].values():
            record['gap'] = 5.
        result = pair_audit(value, CONTRACT)
        self.assertFalse(result['gates']['negative_bound_state_energies'])

    def test_scaled_bright_floor_does_not_reject_resolved_small_signal(self):
        value = manufactured()
        result = pair_audit(value, CONTRACT)
        self.assertLess(result['selected_direct']['L_O_bar'], 2e-5)
        self.assertTrue(result['gates']['bright_resolved_scaled'])
        for lane in ('direct', 'force'):
            for record in value[lane].values():
                record['L_O_bar'] = 1e-12
        result = pair_audit(value, CONTRACT)
        self.assertTrue(result['gates']['positive_bright_L_O'])
        self.assertFalse(result['gates']['bright_resolved_scaled'])


if __name__ == '__main__':
    unittest.main()
