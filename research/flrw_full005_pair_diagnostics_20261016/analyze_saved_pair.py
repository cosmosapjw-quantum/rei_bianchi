#!/usr/bin/env python3
"""Analyze already validated saved FULL005 histories, without rendering/solver.

Physical and ledger validation transfers from the bound successful prior receipt.
Only necessary history/abundance bytes are streamed once while hashing. Numeric
and alignment prerequisites are checked again; no ledger/checkpoint is opened.
"""
import argparse
import array
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'flrw_full005_postprocess_20261015'
sys.path.insert(0, str(BASE / 'vendor'))
import compare_histories as reader
from pair_diagnostics import diagnose_pair, write_diagnostics

DEFAULT_RECEIPT = BASE / 'completed_pair_20261016_001/results/POSTPROCESS_RECEIPT.json'
PRIOR_STATUS = 'CONDITIONAL_FULL_INTERVAL_DIAGNOSTIC_REVIEW_PENDING'
STRICT_STATUS = 'STRICT_COMPLETENESS_SOURCE_CONFIG_CHARGE_BARYON_LEDGER_CHECKS_PASS'
FROZEN_STATUS = 'FROZEN_ACTUAL_FULL005_SOURCE_BINARY_BASE_AND_RUNTIME_CONFIG_MATCH'


class Hold(ValueError):
    pass


def _require(condition, cause):
    if not condition:
        raise Hold(cause)


def _number(value, cause):
    result = float(value)
    _require(math.isfinite(result), 'HOLD_NONFINITE_VALUE: ' + cause)
    return result


def _small(spec, role):
    return reader.bound(spec, role)


def _rows(spec, role):
    desc = spec[role]
    digest = hashlib.sha256()
    with Path(desc['path']).open('rb') as stream:
        def lines():
            for line in stream:
                digest.update(line)
                yield line.decode('utf-8')
        yield from csv.DictReader(lines())
    _require(digest.hexdigest() == desc['sha256'], 'HOLD_INPUT_HASH_MISMATCH: ' + role)


def _relocate(original, runs_root, bindings_root):
    spec = json.loads(json.dumps(original))
    if runs_root is not None:
        for role in ('history', 'abundances', 'config', 'source_identity', 'terminal'):
            spec[role]['path'] = str(runs_root / spec['id'] / Path(spec[role]['path']).name)
    if bindings_root is not None:
        spec['binding']['path'] = str(bindings_root / Path(spec['binding']['path']).name)
    return spec


def _validate_prior(prior):
    _require(isinstance(prior, dict), 'HOLD_PRIOR_RECEIPT_SCHEMA')
    _require(prior.get('status') == PRIOR_STATUS, 'HOLD_PRIOR_POSTPROCESS_STATUS')
    specs = prior.get('validated_complete_inputs', [])
    _require(isinstance(specs, list) and len(specs) == 2
             and all(isinstance(s, dict) and isinstance(s.get('id'), str) for s in specs)
             and len({s['id'] for s in specs}) == 2,
             'HOLD_TWO_VALIDATED_CASES_REQUIRED')
    _require(prior.get('pair_source_relation') == 'BYTE_IDENTICAL_COMPILED_SOURCE',
             'HOLD_PRIOR_SOURCE_RELATION')
    for spec in specs:
        case = spec['id']
        for role in ('history', 'abundances', 'config', 'source_identity', 'terminal', 'binding'):
            desc = spec.get(role, {})
            _require(isinstance(desc, dict) and isinstance(desc.get('path'), str)
                     and isinstance(desc.get('sha256'), str) and len(desc['sha256']) == 64
                     and all(c in '0123456789abcdef' for c in desc['sha256']),
                     'HOLD_PRIOR_INPUT_DESCRIPTOR: ' + case + '.' + role)
        _require(prior['case_checks'][case]['status'] == STRICT_STATUS,
                 'HOLD_PRIOR_STRICT_CASE_CHECKS: ' + case)
        _require(prior['frozen_full005_checks'][case]['status'] == FROZEN_STATUS,
                 'HOLD_PRIOR_FROZEN_FULL005_CHECKS: ' + case)
        _require(spec['clock_origin'] == reader.CLOCK, 'HOLD_CLOCK_ORIGIN: ' + case)
        _require(spec['source_identity']['sha256'] == spec['expected_source_sha256']
                 == prior['case_checks'][case]['source_identity_sha256'],
                 'HOLD_PRIOR_SOURCE_BINDING: ' + case)
        _require(spec['config']['sha256'] == spec['expected_config_sha256']
                 == prior['case_checks'][case]['config_sha256'],
                 'HOLD_PRIOR_CONFIG_BINDING: ' + case)
        _require(spec['binding']['sha256'] == prior['case_checks'][case]['binding_sha256'],
                 'HOLD_PRIOR_CONTROLLER_BINDING: ' + case)
    _require(specs[0]['source_identity']['sha256'] == specs[1]['source_identity']['sha256'],
             'HOLD_CURRENT_SOURCE_RELATION')
    return specs


def load_saved_case(spec, prior_check):
    """Reuse physical checks, reconstruct the same 16 observable arrays."""
    paths = {role: _small(spec, role)
             for role in ('config', 'source_identity', 'terminal', 'binding')}
    binding = json.loads(paths['binding'].read_text())
    _require(binding.get('case') == spec['id']
             and binding.get('source_identity_sha256') == spec['expected_source_sha256']
             and binding.get('runtime_config_sha256', binding.get('config_sha256'))
             == spec['expected_config_sha256'], 'HOLD_CURRENT_CONTROLLER_BINDING')
    terminal = dict(line.split('=', 1) for line in paths['terminal'].read_text().splitlines()
                    if '=' in line)
    _require(terminal.get('status') == 'COMPLETE_REPRESENTED_INTERVAL',
             'HOLD_CURRENT_TERMINAL_STATUS')
    fields = ['L', 'time_s', 'xe', *reader.FIELDS, *('Y_' + k for k in reader.SPECIES)]
    series = {name: array.array('d') for name in fields}
    for row in _rows(spec, 'history'):
        _require(row['case_id'] == spec['id'], 'HOLD_HISTORY_CASE_ID')
        a = _number(row['a'], 'a')
        nh = _number(row['nH_proper_cm3'], 'nH')
        _require(a > 0 and nh > 0, 'HOLD_LOG_OR_DIVISION_DOMAIN')
        coordinate = math.log(a)
        clock = _number(row['time_s'], 'time_s')
        _require(not series['L'] or (coordinate > series['L'][-1]
                                     and clock > series['time_s'][-1]),
                 'HOLD_HISTORY_COORDINATE_OR_TIME_ORDER')
        series['L'].append(coordinate)
        series['time_s'].append(clock)
        series['xe'].append(_number(_number(row['ne_proper_cm3'], 'ne') / nh, 'xe'))
        for name, column in reader.FIELDS.items():
            series[name].append(_number(row[column], column))
    _require(len(series['L']) >= 2, 'HOLD_HISTORY_SHAPE')
    _require(series['L'][0] == reader.L0 and series['L'][-1] == reader.L1
             and series['time_s'][0] == 0, 'HOLD_FULL_INTERVAL_OR_CLOCK_ORIGIN')
    _require(len(series['L']) == prior_check['history_rows']
             and series['time_s'][-1] == prior_check['elapsed_time_s'],
             'HOLD_PRIOR_HISTORY_SHAPE_OR_ENDPOINT')
    index, pending, current_time = 0, set(), None

    def finish_block():
        _require(pending == set(reader.SPECIES), 'HOLD_ABUNDANCE_SPECIES_SHAPE')

    for row in _rows(spec, 'abundances'):
        _require(row['run_id'] == spec['id'], 'HOLD_ABUNDANCE_CASE_ID')
        stamp = _number(row['time_s'], 'abundance time')
        if current_time is not None and stamp != current_time:
            finish_block()
            index += 1
            pending = set()
        _require(index < len(series['L']) and stamp == series['time_s'][index],
                 'HOLD_ABUNDANCE_TIME_ALIGNMENT')
        species = row['species_id']
        _require(species in reader.SPECIES and species not in pending,
                 'HOLD_ABUNDANCE_SPECIES_ALIGNMENT')
        series['Y_' + species].append(_number(row['Ybaryon'], 'Y_' + species))
        pending.add(species)
        current_time = stamp
    finish_block()
    _require(index + 1 == len(series['L'])
             and all(len(values) == len(series['L']) for values in series.values()),
             'HOLD_SELECTED_ARRAY_ALIGNMENT')
    return {'id': spec['id'], 'series': series}


def run(validated_receipt, output, runs_root=None, bindings_root=None):
    if output.exists():
        raise Hold('HOLD_FRESH_OUTPUT_REQUIRED')
    output.mkdir(parents=True)
    wall, cpu = time.perf_counter(), time.process_time()
    receipt = dict(schema_version=1, status='HOLD_NOT_COMPLETED', metrics=None,
                   solver_runs=0, renderer_runs=0, ledger_reads=0, checkpoint_reads=0,
                   actual_full005_admission='NOT_ISSUED',
                   prior_validated_receipt=str(validated_receipt.resolve()),
                   python=platform.python_version(), script_sha256=reader.hashfile(__file__))
    try:
        prior_bytes = validated_receipt.read_bytes()
        receipt['prior_validated_receipt_sha256'] = hashlib.sha256(prior_bytes).hexdigest()
        prior = json.loads(prior_bytes)
        originals = _validate_prior(prior)
        specs = [_relocate(s, runs_root, bindings_root) for s in originals]
        receipt['necessary_inputs'] = [{k: s[k] for k in
                                      ('id', 'history', 'abundances', 'config',
                                       'source_identity', 'terminal', 'binding')} for s in specs]
        cases = [load_saved_case(s, prior['case_checks'][s['id']]) for s in specs]
        result = diagnose_pair(*cases)
        write_diagnostics(result, output)
        receipt.update(status='PAIR_DIAGNOSTICS_COMPLETE', metrics=result,
                       input_kind=prior.get('input_kind', 'SAVED_VALIDATED_FULL005'),
                       newly_executed_checks=['Necessary input byte identities',
                           'Finite/order/shape/alignment numeric prerequisites',
                           'Binary64 full-overlap PL diagnostics'],
                       reused_checks=['Frozen FULL005 bindings', 'All-row H/He and baryon/charge checks',
                           'Ledger/checkpoint completeness and recorded tolerances'],
                       raw_stream_passes_per_role={'history': 1, 'abundances': 1})
    except (ValueError, OSError, KeyError, TypeError, AttributeError, csv.Error, reader.InputHold) as exc:
        receipt.update(status='HOLD_PAIR_DIAGNOSTICS_INPUT_OR_ARITHMETIC',
                       reason=str(exc), metrics=None)
        for name in ('full_pair_continuous_diagnostics.json', 'full_pair_continuous_summary.csv'):
            (output / name).unlink(missing_ok=True)
    receipt.update(wall_seconds=time.perf_counter() - wall, cpu_seconds=time.process_time() - cpu)
    (output / 'PAIR_DIAGNOSTICS_RECEIPT.json').write_text(
        json.dumps(receipt, indent=2, allow_nan=False) + '\n')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validated-receipt', type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--runs-root', type=Path)
    parser.add_argument('--bindings-root', type=Path)
    args = parser.parse_args()
    try:
        result = run(args.validated_receipt, args.output, args.runs_root, args.bindings_root)
    except Hold as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps({'status': result['status'], 'output': str(args.output)}, allow_nan=False))
    return 0 if result['status'] == 'PAIR_DIAGNOSTICS_COMPLETE' else 2


if __name__ == '__main__':
    raise SystemExit(main())
