#!/usr/bin/env python3
"""Saved-helper coefficient diagnostics only; never run collocation or an oracle."""
import argparse
import csv
from decimal import Decimal as D, localcontext
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from run_control import atomic_bytes, identity

KEYS = [('OFF', 1, 0, 0), ('OFF', 1, 1162, 0), ('OFF', 1, 1976, 0),
        ('GM', 2, 1727, 0), ('GM', 2, 2333, 0), ('OFF', 2, 700, 1)]
SPECIES = ('HI', 'HeI', 'HeII')


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def key(row):
    return row['mode'], int(row['step']), int(row['node']), int(row['segment'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', required=True, type=Path)
    parser.add_argument('--coefficient', required=True, type=Path)
    parser.add_argument('--controls', required=True, type=Path)
    parser.add_argument('--parent', type=Path)
    parser.add_argument('--replay-fixture', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if bool(args.parent) == bool(args.replay_fixture):
        parser.error('supply exactly one of --parent or --replay-fixture')
    folder = args.output.parent
    owner_snapshot = folder / 'owner_local_enclosure_as_run.py'
    atomic_bytes(owner_snapshot, args.coefficient.read_bytes())
    source_identities = [identity(args.interval), identity(owner_snapshot), identity(args.controls)]
    if args.parent:
        base = args.parent / 'inputs' / 'e13c2'
        helper_path = base / 'code' / 'decimal_collocation.py'
        source_identities.append(identity(helper_path))
        helper_snapshot = folder / 'inherited_coefficient_definition_as_read.py'
        atomic_bytes(helper_snapshot, helper_path.read_bytes())
        helper_path = helper_snapshot
        original = base / 'inputs' / 'upstream_e13c1'
        captures, stages = {}, {}
        for mode in ('OFF', 'GM'):
            path = original / 'evidence' / 'capture' / mode / 'SEGMENTS.csv'
            source_identities.append(identity(path))
            with path.open(newline='') as stream:
                captures.update({key(row): row for row in csv.DictReader(stream)})
            path = original / 'inputs' / (mode + '_STAGES.csv')
            source_identities.append(identity(path))
            with path.open(newline='') as stream:
                stages.update({(mode, int(row['step'])): row for row in csv.DictReader(stream)})
        fixture = {'sources': source_identities[3:],
                   'controls': [{'key': list(k), 'row': captures[k], 'stage': stages[k[:2]]} for k in KEYS],
                   'original_csv_readback_when_fixture_created': True}
        atomic_bytes(folder / 'PINNED_CAPTURE_FIXTURE.json', (json.dumps(fixture, indent=2) + '\n').encode())
    else:
        fixture = json.loads(args.replay_fixture.read_text())
        helper_path = args.replay_fixture.parent / 'inherited_coefficient_definition_as_read.py'
        source_identities += [identity(args.replay_fixture), identity(helper_path)]
    # Load the exact owner interval snapshot under the module name required by
    # the owner's coefficient import, then load the captured coefficient source.
    di = load_module('directed_interval', args.interval)
    di.configure(60)
    owner = load_module('owner_coefficient_control', owner_snapshot)
    helper = load_module('inherited_coefficient_definition_only', helper_path)
    forbidden_calls = []

    def forbidden(*unused, **also_unused):
        forbidden_calls.append('forbidden_solver_function')
        raise RuntimeError('old solver, Gaussian rule, or collocation must not run in coefficient control')

    for name in ('collocate', 'gauss_rule', 'integrated_lagrange', 'solve_decimal',
                 'frozen_exact', 'j_integral', 'read_and_select', 'main'):
        if hasattr(helper, name):
            setattr(helper, name, forbidden)
    supplied = json.loads(args.controls.read_text())['controls']
    IV, Jet = di.IV, di.Jet2
    records, point_records = [], []
    max_point_relative_width = D(0)

    def check(identifier, passed, **detail):
        records.append({'check_id': identifier, 'passed': bool(passed), **detail})

    def point_contains(identifier, interval, reference, kind):
        check(identifier, interval.contains(reference), kind=kind,
              owner_interval=interval.json(), reference_decimal_110=str(reference),
              reference_is_rigorous_enclosure=False)

    check('EXACT_SIX_CONTROL_KEYS', [tuple(c['key']) for c in supplied] == KEYS)
    check('EXACT_INDEPENDENT_FIXTURE_KEYS', [tuple(c['key']) for c in fixture['controls']] == KEYS)
    for index, (control, captured) in enumerate(zip(supplied, fixture['controls'])):
        check(f'CAPTURED_ROW_IDENTITY_{index}', control['row'] == captured['row'])
        check(f'CAPTURED_STAGE_IDENTITY_{index}', control['stage'] == captured['stage'])
    if any(not r['passed'] for r in records):
        raise AssertionError('input identity failed before any coefficient evaluation')

    with localcontext() as context:
        context.prec = 110
        for index, (control, captured) in enumerate(zip(supplied, fixture['controls'])):
            numeric = helper.Coefficients(captured['row'], captured['stage'])
            interval_model = owner.Coefficients(control)
            check(f'CAPTURED_MASK_IDENTITY_{index}', interval_model.mask == numeric.mask)
            for point_index, point_text in enumerate(('0', '0.25', '0.5', '0.75', '1')):
                t = D(point_text)
                reference = numeric(t)
                observed = interval_model(IV(t))
                cell_number = min(int(t * 32), 31)
                cell = IV(D(cell_number) / 32, D(cell_number + 1) / 32)
                broad = interval_model(cell)
                jets = interval_model(Jet.variable(cell))
                point_jets = interval_model(Jet.variable(IV(t)))
                labels = ('E_eV', 'q', 'lambda_HI', 'lambda_HeI', 'lambda_HeII')
                refs = (reference[0], reference[1], *reference[2])
                points = (observed[0], observed[1], *observed[2])
                cells = (broad[0], broad[1], *broad[2])
                jet_values = (jets[0].v, jets[1].v, *(r.v for r in jets[2]))
                for label, ref, pv, cv, jv in zip(labels, refs, points, cells, jet_values):
                    point_contains(f'COEFFICIENT_POINT_{index}_{point_index}_{label}', pv, ref,
                                   'FINITE_HIGH_PRECISION_COEFFICIENT_DIAGNOSTIC')
                    point_contains(f'COEFFICIENT_CELL_{index}_{point_index}_{label}', cv, ref,
                                   'WHOLE_CELL_RANGE_AT_A_POINT_DIAGNOSTIC')
                    point_contains(f'COEFFICIENT_JET_VALUE_{index}_{point_index}_{label}', jv, ref,
                                   'WHOLE_CELL_JET_VALUE_AT_A_POINT_DIAGNOSTIC')
                    if ref:
                        max_point_relative_width = max(max_point_relative_width, (pv.hi - pv.lo) / abs(ref))
                for species_index, active in enumerate(numeric.mask):
                    if not active:
                        pv, cv, jv = points[species_index + 2], cells[species_index + 2], jets[2][species_index]
                        check(f'INACTIVE_EXACT_ZERO_{index}_{point_index}_{SPECIES[species_index]}',
                              pv.lo == pv.hi == cv.lo == cv.hi == jv.v.lo == jv.v.hi ==
                              jv.d1.lo == jv.d1.hi == jv.d2.lo == jv.d2.hi == 0)
                # Independent closed formulas for normalized-time derivatives of
                # energy and external source; no differentiation helper is used.
                h = numeric.h
                e, q = reference[:2]
                s = numeric.a + h * t
                radiation = numeric.omega_r * (-D(4) * s).exp()
                matter = numeric.omega_m * (-D(3) * s).exp()
                background = radiation + matter + numeric.omega_l
                b = 4 * radiation + 3 * matter
                c = 16 * radiation + 9 * matter
                logh_d1 = -b / (2 * background)
                logh_d2 = (c * background - b * b) / (2 * background * background)
                derivative_refs = {
                    'E_D1': (-h * e, point_jets[0].d1),
                    'E_D2': (h * h * e, point_jets[0].d2),
                    'q_D1': (h * q * (1 - logh_d1), point_jets[1].d1),
                    'q_D2': (h * h * q * ((1 - logh_d1) ** 2 - logh_d2), point_jets[1].d2),
                }
                for label, (ref, interval) in derivative_refs.items():
                    point_contains(f'COEFFICIENT_DERIVATIVE_{index}_{point_index}_{label}', interval, ref,
                                   'INDEPENDENT_CLOSED_FORM_E_AND_q_DERIVATIVE_DIAGNOSTIC')
                point_records.append({'key': control['key'], 't': point_text,
                                      'cell': cell.json(), 'energy_eV': str(e), 'source': str(q),
                                      'rates': [str(r) for r in reference[2]], 'mask': numeric.mask})
            for bad_t in ('-0.01', '1.01'):
                try:
                    interval_model(IV(bad_t))
                except ArithmeticError:
                    check(f'NORMALIZED_TIME_DOMAIN_{index}_{bad_t}', True)
                else:
                    check(f'NORMALIZED_TIME_DOMAIN_{index}_{bad_t}', False)

        # These are explicit mask-branch diagnostics; no physical trajectory is
        # evaluated at these synthetic energies. Captured masks remain fixed.
        low_model = owner.Coefficients(supplied[0])
        zero_sigma = low_model.sigma(1, Jet.variable(IV(35)))
        check('CAPTURED_INACTIVE_MASK_REMAINS_ZERO_ABOVE_CUTOFF',
              zero_sigma.v.lo == zero_sigma.v.hi == zero_sigma.d1.lo == zero_sigma.d1.hi ==
              zero_sigma.d2.lo == zero_sigma.d2.hi == 0,
              kind='SYNTHETIC_MASK_BRANCH_DIAGNOSTIC')
        edge = IV.from_binary64(13.6).lo
        for label, energy in (('BELOW', edge - D('1e-40')), ('AT', edge), ('ABOVE', edge + D('1e-40'))):
            image = low_model.sigma(0, IV(energy))
            check('CAPTURED_ACTIVE_MASK_ONE_SIDED_EXTENSION_' + label, image.lo > 0,
                  kind='SYNTHETIC_MASK_BRANCH_DIAGNOSTIC', energy_eV=str(energy))

    check('FORBIDDEN_OLD_SOLVER_CALL_COUNT_ZERO', not forbidden_calls)
    failed = [r['check_id'] for r in records if not r['passed']]
    result = {'schema': 'BASS_HE_E13C4_COEFFICIENT_CONTROL_V1',
              'role': 'independent numerical contributor; not final decision reviewer',
              'owner_interval_precision': 60, 'reference_precision': 110,
              'reference_point_count': len(point_records), 'fixed_controls': [list(k) for k in KEYS],
              'check_count': len(records), 'passed_count': len(records) - len(failed),
              'failed_check_ids': failed, 'checks': records, 'points': point_records,
              'max_owner_point_relative_interval_width': str(max_point_relative_width),
              'source_identities': source_identities,
              'original_captured_csv_readback_this_run': bool(args.parent),
              'forbidden_old_solver_calls': forbidden_calls,
              'shared_dependencies': ['exact binary64 constants', 'Verner fit parameter definitions',
                                      'captured affine gas path', 'analytic FLRW definition',
                                      'captured species/source masks', 'Decimal transcendental backend'],
              'independent_elements': ['new interval coefficient expression translation',
                                       'independently selected original CSV rows/stages',
                                       'closed-form energy and source first/second derivatives'],
              'claim_ceiling': 'Finite 110-digit coefficient diagnostics and source identity. These points are not a continuum enclosure proof. No independent species derivative reference and no continuous solution reference was computed.'}
    atomic_bytes(args.output, (json.dumps(result, indent=2) + '\n').encode())
    print(json.dumps({k: result[k] for k in ('reference_point_count', 'check_count', 'passed_count',
                                          'failed_check_ids', 'max_owner_point_relative_interval_width')}))
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
