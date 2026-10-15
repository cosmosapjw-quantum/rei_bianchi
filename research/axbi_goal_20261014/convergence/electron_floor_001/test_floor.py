#!/usr/bin/env python3
"""Bounded metadata regression for the approved electron floor corrigendum."""
import array
import importlib.util
import json
import math
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEFORE = Path(__file__).resolve().parent / 'raw/compare_histories_before.py'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


old = load(BEFORE, 'floor_before')
new = load(ROOT / 'compare_histories.py', 'floor_after')
eps = Fraction(1, 10_000_000)
checks = []
for y_text in ('.2454', '.24', '.1', '.5'):
    y = Fraction(y_text)
    h, he = 1 - y, y / 4
    case = {'factors': (float(h), float(he))}
    xe_exact = eps * (h + 3 * he) / h
    ye_exact = eps * (h + 3 * he)
    xe = new.floor('xe', case)
    ye = new.floor('Y_electron', case)
    tolerance = 4 * math.ulp(float(xe_exact))
    assert abs(xe - float(xe_exact)) <= tolerance, (y_text, xe, xe_exact)
    assert abs(ye - float(ye_exact)) <= 4 * math.ulp(float(ye_exact))
    assert abs(float(h) * xe - ye) <= 4 * max(math.ulp(ye), math.ulp(float(h) * xe))
    for name in ('x_HI', 'x_HII', 'x_HeI', 'x_HeII', 'x_HeIII',
                 'Y_H_I', 'Y_H_II', 'Y_He_I', 'Y_He_II', 'Y_He_III',
                 'Y_electron', 'Tgas_K', 'ne_cm3', 'U0_eV_per_H', 'U2_eV_per_H'):
        assert new.floor(name, case) == old.floor(name, case), (y_text, name)
    checks.append({'YHe': y_text, 'h': str(h), 'he': str(he),
                   'xe_expected': str(xe_exact), 'xe_observed': xe,
                   'Y_electron_expected': str(ye_exact), 'Y_electron_observed': ye,
                   'h_times_xe_minus_Y_electron': float(h) * xe - ye})

# All numbers, sampled differences and milestone brackets must remain identical.
xs = array.array('d', [old.L0, (old.L0 + old.L1) / 2, old.L1])
def case(identifier, delta):
    return {'id': identifier, 'factors': (.75, .0625), 'series': {
        'L': xs, 'time_s': array.array('d', [0, 50 + delta, 100 + 2 * delta]),
        'x_HII': array.array('d', [0, .5, 1]),
        'xe': array.array('d', [0, .5 + delta / 10000, 1]),
        'Y_electron': array.array('d', [0, .375, .75]),
        'Tgas_K': array.array('d', [10, 15 + delta, 20])}}
ref, cand = case('R', 0), case('C', 1)
old_rows, old_summary, old_milestones = old.compare(ref, cand)
new_rows, new_summary, new_milestones = new.compare(ref, cand)
assert len(old_rows) == len(new_rows) == 4004
assert old_milestones == new_milestones
changes = []
for group, before, after in (('row', old_rows, new_rows),
                             ('summary', old_summary, new_summary)):
    for index, (left, right) in enumerate(zip(before, after)):
        differing = {key for key in left if left[key] != right[key]}
        if differing:
            assert left['observable'] == 'xe', (group, index, differing)
            assert differing == {'absolute_resolution_floor'}, (group, index, differing)
            changes.append({'group': group, 'index': index, 'observable': 'xe',
                            'old': left['absolute_resolution_floor'],
                            'new': right['absolute_resolution_floor']})
assert len(changes) == 1002, len(changes)
print(json.dumps({'status': 'PASS', 'fraction_checks': checks,
                  'rows': len(new_rows), 'summary': len(new_summary),
                  'milestones_equal': True, 'metadata_changes': len(changes),
                  'first_metadata_change': changes[0]}, indent=2))
