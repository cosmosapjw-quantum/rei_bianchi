"""Exact finite compact-interior geometry and trusted-normalization collection.

This module does not validate native receipt files, launch workers, add endpoint
bounds, or grant scientific admission. See README.md for the trust boundary.
"""
from fractions import Fraction
import copy
import hashlib
import json
import re


class CollectionError(ValueError):
    pass


WINDOW_KEYS = ('l_t', 'T_t', 'l_u', 'T_u')
BINDING_KEYS = ('global_endpoint_plan_sha256', 'archive_sha256', 'input_record_sha256', 'build_manifest_sha256',
                'build_source_sha256', 'validator_source_sha256')
PARTS = ('real', 'imag')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def checked_hash(value):
    if type(value) is not str or not re.fullmatch(r'[0-9a-f]{64}', value):
        raise CollectionError('canonical SHA-256 required')
    return value


def integer(value, lo, hi, label):
    if type(value) is not int or not lo <= value <= hi:
        raise CollectionError('bounded integer required: ' + label)
    return value


def dyadic(token):
    if type(token) is not str or len(token) > 5000 or not re.fullmatch(
            r'(0|-?[1-9][0-9]*)(/[1-9][0-9]*)?', token):
        raise CollectionError('bounded canonical rational required')
    # Bound digits before int conversion, including Python's own digit limit.
    if any(len(s.lstrip('-')) > 2467 for s in token.split('/')):
        raise CollectionError('dyadic integer bit cap')
    try:
        value = Fraction(token)
    except (ValueError, ZeroDivisionError) as exc:
        raise CollectionError('invalid dyadic') from exc
    n, d = value.numerator, value.denominator
    if str(value) != token or max(abs(n).bit_length(), d.bit_length()) > 8192:
        raise CollectionError('canonical dyadic bit cap')
    if d & (d - 1):
        raise CollectionError('non-dyadic denominator')
    return value


def log_window(window):
    if type(window) is not dict or set(window) != set(WINDOW_KEYS):
        raise CollectionError('exact physical window required')
    out = {}
    for key in WINDOW_KEYS:
        value = dyadic(window[key])
        n, d = value.numerator, value.denominator
        if n <= 0 or n & (n - 1) or max(n.bit_length(), d.bit_length()) > 512:
            raise CollectionError('bounded positive power-of-two endpoint required')
        out[key] = n.bit_length() - d.bit_length()
    if out['l_t'] >= out['T_t'] or out['l_u'] >= out['T_u']:
        raise CollectionError('ordered nonempty window required')
    return out


def _axis(lo, hi, step):
    return list(range(lo, hi, step)) + [hi]


def plan_grid(global_window, index, global_radius_exp, max_log_step=3, max_tiles=16):
    """Create geometry only. More than 16 tiles is never executable here."""
    integer(index, 0, 2591, 'primitive index')
    integer(global_radius_exp, -1024, 0, 'global radius exponent')
    integer(max_log_step, 1, 8, 'log step')
    integer(max_tiles, 1, 16, 'pilot tile cap')
    logs = log_window(global_window)
    t = _axis(logs['l_t'], logs['T_t'], max_log_step)
    u = _axis(logs['l_u'], logs['T_u'], max_log_step)
    count = (len(t) - 1) * (len(u) - 1)
    if count > max_tiles:
        raise CollectionError('TILE_COUNT_EXCEEDS_PILOT_CAP: ' + str(count))
    tile_exp = global_radius_exp - (count - 1).bit_length()
    # The pinned native driver cannot request a tighter exponent than -1024.
    if tile_exp < -1024:
        raise CollectionError('per-tile exponent outside native contract')
    tiles = []
    for i in range(len(t) - 1):
        for j in range(len(u) - 1):
            coords = (t[i], t[i + 1], u[j], u[j + 1])
            tiles.append({'tile_id': len(tiles),
                          'window': {k: str(Fraction(2) ** x)
                                     for k, x in zip(WINDOW_KEYS, coords)},
                          'log2_window': dict(zip(WINDOW_KEYS, coords))})
    return {'schema': 'WU088_EXACT_FINITE_TILE_PLAN_V1',
            'global_window': copy.deepcopy(global_window), 'primitive_index': index,
            'global_radius_exp': global_radius_exp, 'tile_radius_exp': tile_exp,
            'precision_bits': 128, 'max_log_step': max_log_step,
            'max_tiles': max_tiles, 'log2_t_axis': t, 'log2_u_axis': u,
            'tile_count': count, 'tiles': tiles, 'endpoint_included': False,
            'bindings': None}


def _geometry(plan):
    try:
        rebuilt = plan_grid(plan['global_window'], plan['primitive_index'],
                            plan['global_radius_exp'], plan['max_log_step'],
                            plan['max_tiles'])
    except (KeyError, TypeError) as exc:
        raise CollectionError('malformed plan') from exc
    actual = copy.deepcopy(plan)
    actual.pop('plan_sha256', None)
    actual['bindings'] = None
    if canonical(actual) != canonical(rebuilt):
        raise CollectionError('plan geometry or coverage mismatch')
    return rebuilt


def bind_plan(plan, **bindings):
    """Pin upstream authority supplied by the native-receipt adapter."""
    geometry = _geometry(plan)
    if set(bindings) != set(BINDING_KEYS):
        raise CollectionError('exact upstream binding keys required')
    geometry['bindings'] = {k: checked_hash(bindings[k]) for k in BINDING_KEYS}
    geometry['plan_sha256'] = sha(geometry)
    return geometry


def _validate_plan(plan):
    if type(plan) is not dict:
        raise CollectionError('plan object required')
    _geometry(plan)
    if type(plan.get('bindings')) is not dict or set(plan['bindings']) != set(BINDING_KEYS):
        raise CollectionError('bound plan required')
    for value in plan['bindings'].values():
        checked_hash(value)
    payload = {k: v for k, v in plan.items() if k != 'plan_sha256'}
    if checked_hash(plan.get('plan_sha256')) != sha(payload):
        raise CollectionError('plan envelope digest mismatch')


def seal_normalized_record(record):
    """Integrity seal only; does NOT authenticate or validate native evidence."""
    if type(record) is not dict or 'record_sha256' in record:
        raise CollectionError('unsealed normalized object required')
    out = copy.deepcopy(record)
    out['record_sha256'] = sha(record)
    return out


def collect(plan, validatedtiles):
    """Collect only records already validated by the pinned upstream validator."""
    _validate_plan(plan)
    if type(validatedtiles) is not list or len(validatedtiles) != plan['tile_count']:
        raise CollectionError('complete tile coverage required')
    seen_ids, seen_receipts = set(), set()
    total = {part: [Fraction(0), Fraction(0)] for part in PARTS}
    tile_cap = Fraction(2) ** plan['tile_radius_exp']
    receipts = []
    for record in validatedtiles:
        if type(record) is not dict:
            raise CollectionError('normalized tile object required')
        tile_id = integer(record.get('tile_id'), 0, plan['tile_count'] - 1, 'tile ID')
        if tile_id in seen_ids:
            raise CollectionError('duplicate tile ID')
        seen_ids.add(tile_id)
        expected = {'schema': 'WU088_TRUSTED_NORMALIZED_TILE_V1',
                    'tile_id': tile_id, 'primitive_index': plan['primitive_index'],
                    'global_plan_sha256': plan['plan_sha256'],
                    'window': plan['tiles'][tile_id]['window'],
                    'requested_radius_exp': plan['tile_radius_exp'],
                    'precision_bits': 128, 'status': 'RADIUS_MET', 'accepted': True,
                    'endpoint_included': False, 'normalization_applied': False,
                    'bindings': plan['bindings']}
        extra = {'native_plan_sha256', 'native_receipt_sha256', 'rectangle',
                 'reported_radius', 'record_sha256'}
        if set(record) != set(expected) | extra:
            raise CollectionError('exact normalized tile keys required')
        for key, value in expected.items():
            if canonical(record[key]) != canonical(value):
                raise CollectionError('normalized tile contract mismatch: ' + key)
        payload = {k: v for k, v in record.items() if k != 'record_sha256'}
        if checked_hash(record['record_sha256']) != sha(payload):
            raise CollectionError('normalized envelope digest mismatch')
        native_plan = checked_hash(record['native_plan_sha256'])
        native_receipt = checked_hash(record['native_receipt_sha256'])
        if native_receipt in seen_receipts:
            raise CollectionError('duplicate native receipt')
        seen_receipts.add(native_receipt)
        if type(record['rectangle']) is not dict or set(record['rectangle']) != set(PARTS):
            raise CollectionError('exact rectangle components required')
        if type(record['reported_radius']) is not dict or set(record['reported_radius']) != set(PARTS):
            raise CollectionError('reported component radii required')
        for part in PARTS:
            interval = record['rectangle'][part]
            if type(interval) is not dict or set(interval) != {'lower', 'upper'}:
                raise CollectionError('exact interval endpoints required')
            lo, hi = dyadic(interval['lower']), dyadic(interval['upper'])
            radius = dyadic(record['reported_radius'][part])
            if lo > hi or radius != (hi - lo) / 2 or not 0 <= radius <= tile_cap:
                raise CollectionError('reported or serialized tile radius mismatch')
            total[part][0] += lo
            total[part][1] += hi
        receipts.append({'tile_id': tile_id, 'native_plan_sha256': native_plan,
                         'native_receipt_sha256': native_receipt,
                         'normalized_record_sha256': record['record_sha256']})
    if seen_ids != set(range(plan['tile_count'])):
        raise CollectionError('Cartesian coverage incomplete')
    cap = Fraction(2) ** plan['global_radius_exp']
    radii = {part: (total[part][1] - total[part][0]) / 2 for part in PARTS}
    if any(radius > cap for radius in radii.values()):
        raise CollectionError('actual exact sum exceeds global radius cap')
    output = {'schema': 'WU088_EXACT_TILED_COMPACT_INTERIOR_V1',
              'status': 'COMPLETE_COMPACT_INTERIOR_RADIUS_MET',
              'global_plan_sha256': plan['plan_sha256'],
              'global_window': copy.deepcopy(plan['global_window']),
              'primitive_index': plan['primitive_index'],
              'bindings': copy.deepcopy(plan['bindings']),
              'tile_count': plan['tile_count'], 'precision_bits': 128,
              'accepted_component_radius_exp': plan['global_radius_exp'],
              'rectangle': {p: {'lower': str(total[p][0]), 'upper': str(total[p][1])}
                            for p in PARTS},
              'component_radius': {p: str(radii[p]) for p in PARTS},
              'tiles': sorted(receipts, key=lambda r: r['tile_id']),
              'endpoint_included': False, 'normalization_applied': False,
              'full_domain_integral': False, 'scientific_admission': False,
              'production_admission': False,
              'validation_scope': 'TRUSTED_UPSTREAM_NORMALIZATION_EXACT_COLLECTION'}
    output['result_sha256'] = sha(output)
    return output
