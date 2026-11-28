"""Bounded T5 numerical composition; never admits a scientific certificate.

All matrices are exact rational complex values. This adapter consumes final
entry disks; it does not generate those disks or authenticate their meaning.
The frozen Gram implementation is imported only after its SHA-256 is checked.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import tempfile


GRAM_RELATIVE = 'gap_closure_20261001_g0_g6_v1/exact_gram/engine.py'
GRAM_SHA256 = 'e10f206d63be1a99a441780108619574605014a9b01b3b327e21fecb18c5b9cc'
GRAM_PATH = Path(__file__).resolve().parents[2] / GRAM_RELATIVE
if hashlib.sha256(GRAM_PATH.read_bytes()).hexdigest() != GRAM_SHA256:
    raise RuntimeError('immutable exact-Gram source SHA mismatch')
_spec = importlib.util.spec_from_file_location('_production_t5_exact_gram', GRAM_PATH)
gram = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = gram
_old_bytecode = sys.dont_write_bytecode
try:
    sys.dont_write_bytecode = True
    _spec.loader.exec_module(gram)
finally:
    sys.dont_write_bytecode = _old_bytecode

ContractError = gram.ContractError
ResourceLimit = gram.ResourceLimit
MAX_DOCUMENT_BYTES = 2 * 1024 * 1024
CAPS = {'max_precision': 4096, 'max_integer_bits': 8192,
        'max_work_bits': 32768, 'max_operations': 150000}
MODELS = ('R31AK', 'R31Z', 'R31AD')
SHAPES = {'D_col': (47, 2), 'D_row': (2, 47), 'K': (47, 2)}
_RATIONAL = re.compile(r'(?:0|-?[1-9][0-9]*)(?:/[1-9][0-9]*)?\Z')
_HASH = re.compile(r'[0-9a-f]{64}\Z')


def canonical_bytes(value):
    """Canonical JSON encoding used by every input envelope SHA-256."""
    try:
        return json.dumps(value, sort_keys=True, separators=(',', ':'),
                          ensure_ascii=True, allow_nan=False).encode('utf-8')
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ContractError('JSON-compatible finite input required') from exc


def bind(data):
    """Bind exact JSON data bytes; hash identity is not evidence admission."""
    return {'sha256': hashlib.sha256(canonical_bytes(data)).hexdigest(), 'data': data}


def _keys(obj, required, optional=()):
    if type(obj) is not dict or not set(required) <= set(obj) or set(obj) - set(required) - set(optional):
        raise ContractError('missing/extra object keys or non-object value')


def _json_pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ContractError('duplicate JSON object key')
        out[key] = value
    return out


def _forbid_float(_):
    raise ContractError('JSON float/nonfinite token forbidden; use canonical rational strings')


def _json_integer(token):
    if len(token) > 10:
        raise ResourceLimit('JSON control integer token too long')
    return int(token)


def parse_request(payload):
    """Parse UTF-8 bytes with a 2 MiB bound, duplicate/float/NaN rejection."""
    if type(payload) is not bytes:
        raise ContractError('input document must be bytes')
    if len(payload) > MAX_DOCUMENT_BYTES:
        raise ResourceLimit('input document byte cap exceeded')
    try:
        return json.loads(payload.decode('utf-8'), object_pairs_hook=_json_pairs,
                          parse_float=_forbid_float, parse_constant=_forbid_float,
                          parse_int=_json_integer)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ContractError('malformed UTF-8 JSON document') from exc


def _limits(request):
    supplied = request.get('limits', {})
    _keys(supplied, (), CAPS)
    values = dict(CAPS)
    for key, value in supplied.items():
        if type(value) is not int or not 0 < value <= CAPS[key]:
            raise ResourceLimit('invalid or increased resource cap: ' + key)
        values[key] = value
    precision = request.get('precision', 128)
    if type(precision) is not int or not 1 <= precision <= values['max_precision']:
        raise ResourceLimit('precision must be a positive integer within the cap')
    return gram.Limits(max_entries=94, **values), precision


def _q(token, work):
    if type(token) is not str:
        raise ContractError('rational value must be a canonical string')
    # Before parsing integers, bound both token length and integer allocation.
    max_digits = (work.limits.max_integer_bits * 30103) // 100000 + 1
    if len(token) > 2 * max_digits + 2:
        raise ResourceLimit('rational token allocation cap exceeded')
    if not _RATIONAL.fullmatch(token):
        raise ContractError('invalid canonical rational token')
    parts = token.split('/')
    if any(len(part.lstrip('-')) > max_digits for part in parts):
        raise ResourceLimit('integer token allocation cap exceeded')
    numerator = int(parts[0])
    denominator = int(parts[1]) if len(parts) == 2 else 1
    if max(numerator.bit_length(), denominator.bit_length()) > work.limits.max_integer_bits:
        raise ResourceLimit('integer input bit cap exceeded')
    result = Q(numerator, denominator)
    if str(result) != token:
        raise ContractError('rational token must be reduced with canonical sign/zero')
    return work.check(result)


def _complex(value, work):
    if type(value) is not list or len(value) != 2:
        raise ContractError('complex value must be [real,imag] rational strings')
    return tuple(_q(part, work) for part in value)


def _matrix(value, shape, work, disks=False):
    m, n = shape
    if type(value) is not list or len(value) != m or any(type(row) is not list or len(row) != n for row in value):
        raise ContractError('matrix must have the fixed 47x2 or 2x47 row-major shape')
    out = []
    for row in value:
        converted = []
        for cell in row:
            if disks:
                _keys(cell, ('center', 'radius'))
                converted.append(gram.ComplexDisk(_complex(cell['center'], work), _q(cell['radius'], work)))
            else:
                converted.append(_complex(cell, work))
        out.append(converted)
    return out


def _envelope(value):
    _keys(value, ('sha256', 'data'))
    expected = value['sha256']
    if type(expected) is not str or not _HASH.fullmatch(expected):
        raise ContractError('lowercase SHA-256 input identity required')
    actual = hashlib.sha256(canonical_bytes(value['data'])).hexdigest()
    if actual != expected:
        raise ContractError('input payload SHA-256 mismatch')
    return value['data']


def _sharp(matrix, target, precision, work):
    center = [[disk.center for disk in row] for row in target]
    total = Q(0)
    for row in target:
        for disk in row:
            total = work.binary(total, work.binary(disk.radius, disk.radius, '*'), '+')
    rho = gram._sqrt(total, precision, work).hi
    norm = gram._norm(gram._subtract(matrix, center, work), precision, work)
    interval = gram.Interval(max(Q(0), work.binary(norm.lo, rho, '-')),
                             work.binary(norm.hi, rho, '+'))
    return {'interval': interval, 'center_norm': norm, 'rho_upper': rho}


def _k_disks(c, r, work):
    out = []
    for i in range(47):
        row = []
        for j in range(2):
            x, y = c[i][j], r[j][i]
            real = work.binary(work.binary(x.center[0], y.center[0], '-'), Q(1, 2), '*')
            imag = work.binary(work.binary(x.center[1], y.center[1], '+'), Q(1, 2), '*')
            radius = work.binary(work.binary(x.radius, y.radius, '+'), Q(1, 2), '*')
            row.append(gram.ComplexDisk((real, imag), radius))
        out.append(row)
    return out


def _gap(local, other, work):
    return gram.Interval(work.binary(other.lo, local.hi, '-'),
                         work.binary(other.hi, local.lo, '-'))


def _intersection(a, b):
    lo, hi = max(a.lo, b.lo), min(a.hi, b.hi)
    if lo > hi:
        raise ContractError('empty target/direct versus represented-gap intersection')
    return gram.Interval(lo, hi)


def _pareto(gaps):
    tolerance = gram.TOLERANCE
    weak = {metric: gaps[metric].lo >= -tolerance for metric in ('K', 'Dmax')}
    strict = {metric: gaps[metric].lo > tolerance for metric in ('K', 'Dmax')}
    sufficient = all(weak.values()) and any(strict.values())
    # Certified impossibility of the REAL conjunction, conditional on disks.
    impossible = (any(gaps[m].hi < -tolerance for m in ('K', 'Dmax')) or
                  all(gaps[m].hi <= tolerance for m in ('K', 'Dmax')))
    return {'status': ('CONDITIONAL_REAL_PARETO_SUFFICIENT' if sufficient else
                       'CONDITIONAL_REAL_PARETO_NOT_SUPPORTED' if impossible else
                       'DECISION_BOUND_UNRESOLVED'),
            'real_sufficient_condition': sufficient,
            'weak_nonworsening': weak, 'strict_improvement': strict,
            'tolerance': str(tolerance), 'tolerance_bits': f'{gram.TOLERANCE_BITS:016x}',
            'tolerance_semantics': 'EXACT_BINARY64_FROZEN_TOKEN',
            'machine_predicate_certified': False, 'scientific_claim_admitted': False}


def _serialize(value):
    if isinstance(value, gram.Interval):
        return value.to_json()
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize(item) for item in value]
    return value


def compose(request):
    """Return conditional exact bounds; reject malformed/over-budget input.

    Does not read raw scientific files, execute a source producer, authenticate
    archival ABI, or promote any project/provider/continuum certificate gate.
    """
    _keys(request, ('schema', 'inputs'), ('precision', 'limits', 'evidence_refs'))
    if request['schema'] != 'WU088_T5_COMPOSITION_REQUEST_V1':
        raise ContractError('unsupported request schema')
    encoded = canonical_bytes(request)
    if len(encoded) > MAX_DOCUMENT_BYTES:
        raise ResourceLimit('input document byte cap exceeded')
    limits, precision = _limits(request)
    work = gram._Work(limits)
    refs = request.get('evidence_refs', {})
    _keys(refs, (), ('target_binding_sha256', 'historical_abi_sha256',
                     'final_entry_certificate_sha256', 'model_identity_sha256'))
    if any(type(v) is not str or not _HASH.fullmatch(v) for v in refs.values()):
        raise ContractError('evidence references must be SHA-256 strings, not admission flags')
    inputs = request['inputs']
    _keys(inputs, ('raw', 'models', 'target_disks'))
    raw_json, models_json, disks_json = (_envelope(inputs[key]) for key in ('raw', 'models', 'target_disks'))
    _keys(raw_json, ('D_col', 'D_row'))
    _keys(disks_json, ('D_col', 'D_row'))
    _keys(models_json, MODELS)
    raw = {key: _matrix(raw_json[key], SHAPES[key], work) for key in ('D_col', 'D_row')}
    targets = {key: _matrix(disks_json[key], SHAPES[key], work, disks=True) for key in ('D_col', 'D_row')}
    models = {}
    for name in MODELS:
        _keys(models_json[name], ('D_col', 'D_row', 'K'))
        models[name] = {key: _matrix(models_json[name][key], SHAPES[key], work) for key in SHAPES}
    # These are raw and target K only. Each model K above remains independent.
    raw['K'] = gram._k(raw['D_col'], raw['D_row'], work)
    targets['K'] = _k_disks(targets['D_col'], targets['D_row'], work)
    residuals = {key: _sharp(raw[key], targets[key], precision, work) for key in SHAPES}
    uc, ur = (residuals[key]['interval'].hi for key in ('D_col', 'D_row'))
    separate_k = work.binary(work.binary(uc, ur, '+'), Q(1, 2), '*')
    epsilon = {'D_col': uc, 'D_row': ur,
               'K': min(residuals['K']['interval'].hi, separate_k), 'Dmax': max(uc, ur)}
    represented_errors, target_errors = {}, {}
    for name in MODELS:
        represented_errors[name] = {}
        target_errors[name] = {}
        for key in SHAPES:
            represented_errors[name][key] = gram._norm(gram._subtract(models[name][key], raw[key], work), precision, work)
            target_errors[name][key] = _sharp(models[name][key], targets[key], precision, work)['interval']
        for errors in (represented_errors[name], target_errors[name]):
            errors['Dmax'] = gram.interval_max(errors['D_col'], errors['D_row'])
    comparisons = {}
    for label, other in (('PRIMARY', 'R31Z'), ('SECONDARY', 'R31AD')):
        represented, direct, tubes, combined = {}, {}, {}, {}
        for metric in ('K', 'Dmax'):
            represented[metric] = _gap(represented_errors['R31AK'][metric], represented_errors[other][metric], work)
            direct[metric] = _gap(target_errors['R31AK'][metric], target_errors[other][metric], work)
            twice = work.binary(Q(2), epsilon[metric], '*')
            tubes[metric] = gram.Interval(work.binary(represented[metric].lo, twice, '-'),
                                          work.binary(represented[metric].hi, twice, '+'))
            combined[metric] = _intersection(direct[metric], tubes[metric])
        comparisons[label] = {'other_model': other, 'represented_gap': represented,
                              'direct_target_gap': direct, 'represented_gap_tube': tubes,
                              'intersection': combined, 'decision': _pareto(combined)}
    return _serialize({
        'schema': 'WU088_T5_COMPOSITION_RESULT_V1',
        'status': 'CONDITIONAL_NUMERICAL_BOUNDS_COMPUTED',
        'source_residuals': residuals, 'separate_block_epsilon_K': separate_k, 'epsilon': epsilon,
        'represented_model_errors': represented_errors, 'target_model_errors': target_errors,
        'comparisons': comparisons,
        'identity': {'request_canonical_sha256': hashlib.sha256(encoded).hexdigest(),
                     'input_canonical_sha256': {key: inputs[key]['sha256'] for key in inputs},
                     'adapter_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                     'gram_source_sha256': GRAM_SHA256, 'gram_source_relative': GRAM_RELATIVE,
                     'evidence_refs_unadmitted': refs},
        'arithmetic': {'backend': 'EXACT_INTEGER_SQRT_RATIONAL_ENCLOSURE',
                       'precision': precision, 'precision_semantics': 'ABSOLUTE_RADICAL_GRID_BITS',
                       'limits': vars(limits), 'operations_used': work.operations,
                       'shared_operation_budget': True, 'stored_model_K_preserved': True},
        'admission': {'rigorous': False, 'project_certification': False,
                      'continuous_target_certificate': False, 'historical_abi_admitted': False,
                      'backend_domain_input_evidence_admitted': False,
                      'machine_predicate_certified': False, 'production_admitted': False,
                      'independent_decision_review_admitted': False,
                      'reason': 'Conditional arithmetic only; external target disks, domain, source binding, ABI and independent review remain separate gates.'},
        'execution': {'source_producer_runs': 0, 'native_backend_runs': 0,
                       'archived_scientific_file_reads': 0,
                       'input_origin_authenticated': False}})


def _publish_new(path, payload):
    """Atomic create-only result: no replacement of an earlier return."""
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix='.composition-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        os.unlink(temporary)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    try:
        with args.input.open('rb') as stream:
            request = parse_request(stream.read(MAX_DOCUMENT_BYTES + 1))
        result = compose(request)
        payload = canonical_bytes(result) + b'\n'
        if args.output is None:
            sys.stdout.buffer.write(payload)
        else:
            _publish_new(args.output, payload)
        return 0
    except (ContractError, OSError) as exc:
        error = {'schema': 'WU088_T5_COMPOSITION_ERROR_V1', 'status': 'RESOURCE_LIMIT' if isinstance(exc, ResourceLimit) else 'INPUT_OR_OUTPUT_REJECTED',
                 'reason': str(exc), 'rigorous': False, 'production_admitted': False}
        print(json.dumps(error, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
