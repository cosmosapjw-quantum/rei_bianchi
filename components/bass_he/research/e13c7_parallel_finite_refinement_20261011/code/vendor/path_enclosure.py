#!/usr/bin/env python3
"""E13C5: two captured three-segment tracks, with incoming error carried.

No gas advance, native calculation, or continuous ODE solver is called.
The unchanged E13C4 coefficients/Jet2 integrands provide local enclosures.
All candidate centers denote exact saved Decimal values, with a separate
outward error radius. Captured energy fields are erg and are converted with
the exact binary64 lift of the inherited eV-to-erg constant.
"""
import argparse
from datetime import datetime, timezone
from decimal import Decimal as D
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform
import resource
import sys
import time

import directed_interval as di
from directed_interval import IV, Jet2, value, response_j
from local_enclosure import Coefficients, SPECIES, integrands, atomic_json, sha, lift

KEYS = [('OFF', 1, 0, 0), ('OFF', 2, 0, 0), ('OFF', 2, 0, 1),
        ('OFF', 1, 700, 0), ('OFF', 2, 700, 0), ('OFF', 2, 700, 1)]
REUSED = {('OFF', 1, 0, 0), ('OFF', 2, 700, 1)}
MOMENTS = ['QN', 'QE_eV', 'A_total', 'B_total_eV', 'H_total_eV', 'Z_eV'] + [
    prefix + '_' + k + ('_eV' if prefix != 'A' else '')
    for prefix in ('A', 'B', 'H') for k in SPECIES]


def iv(obj):
    return IV(obj['lo'], obj['hi'])


def pack(obj):
    if isinstance(obj, IV):
        return obj.json()
    if isinstance(obj, D):
        return str(obj)
    if isinstance(obj, dict):
        return {k: pack(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [pack(v) for v in obj]
    return obj


def center(box):
    # A representative, not an exact-arithmetic claim about the midpoint.
    return di.NEAR.divide(di.NEAR.add(box.lo, box.hi), D(2))


def radius_about(box, point):
    return abs(box - IV(point)).hi


def symmetric(radius):
    radius = D(radius)
    if radius < 0:
        raise ArithmeticError('negative error radius')
    return IV(radius.copy_negate(), radius)


def exact_capture(v):
    return Fraction(D.from_float(float(v)))


def input_checks(data, old_controls):
    if [tuple(c['key']) for c in data['controls']] != KEYS:
        raise ValueError('two-track six-row identity changed')
    expected_masks = [(True, False, False)] * 3 + [(True, True, False)] * 2 + [(True, False, False)]
    expected_source = [True, True, False, True, True, True]
    checks = []
    for control, mask, source in zip(data['controls'], expected_masks, expected_source):
        r, s = control['row'], control['stage']
        tests = {
            'fixed_mask': tuple(control['mask'][k] for k in SPECIES) == mask,
            'fixed_source': control['source_on'] == source,
            'exact_width': exact_capture(r['a']) + exact_capture(r['h']) == exact_capture(r['b']),
            'within_stage': exact_capture(s['s0']) <= exact_capture(r['a']) < exact_capture(r['b']) <= exact_capture(s['s1']),
            'no_outflow': exact_capture(r['outn']) == exact_capture(r['oute']) == 0,
        }
        if tuple(control['key']) in REUSED:
            prior = next(x for x in old_controls if x['key'] == control['key'])
            tests['reused_exact_input_definition'] = all(control[k] == prior[k] for k in ('row', 'stage', 'mask', 'source_on'))
        checks.append({'key': control['key'], 'checks': tests})
    for offset in (0, 3):
        if exact_capture(data['controls'][offset]['row']['f0']) != 0:
            raise ValueError('primary initial condition is exact zero photon stock')
        for j in (offset, offset + 1):
            a, b = data['controls'][j]['row'], data['controls'][j + 1]['row']
            tests = {name: exact_capture(a[left]) == exact_capture(b[right]) for name, left, right in [
                ('time', 'b', 'a'), ('photon', 'n', 'f0'), ('eta', 'eta', 'eta'), ('weight', 'weight', 'weight')]}
            checks.append({'seam': [data['controls'][j]['key'], data['controls'][j + 1]['key']], 'checks': tests})
    if any(not all(item['checks'].values()) for item in checks):
        raise ValueError('captured identity/domain/stitch check failed')
    return checks


def local_integrals(control, n, cached):
    c = Coefficients(control)
    if tuple(control['key']) in REUSED:
        prior = next(x for x in cached['controls'] if x['key'] == control['key'])
        if prior['subdivisions'] != n or prior['precision_digits'] != di.PRECISION:
            raise ValueError('cached resolution or precision mismatch')
        return c, {
            'origin': 'REUSED_SEALED_E13C4_NO_COEFFICIENT_REEVALUATION',
            'new_coefficient_evaluations': 0,
            'domain': prior['domain'], 'cell_coverage': prior['cell_coverage'],
            'signed': {k: iv(v) for k, v in prior['exact_firstvariation_integral_enclosures'].items()},
            'bounds': {k: iv(v) for k, v in prior['variation_integral_enclosures'].items()},
            'midpoint': {k: iv(v) for k, v in prior['frozen_quadrature_midpoint_sum_enclosures'].items()},
            'midpoint_radius': prior['validated_midpoint_truncation_radii'],
            'max_abs_second_t_derivative': prior['max_abs_second_t_derivative']}
    midpoint, radii, bounds, max_d2 = {}, {}, {}, {}
    delta = IV(1) / n
    for j in range(n):
        left, right, mid = IV(j) / n, IV(j + 1) / n, IV(2 * j + 1) / (2 * n)
        field, local_bounds = integrands(c, Jet2.variable(IV(left.lo, right.hi)))
        middle, _ = integrands(c, mid)
        for k, jet in field.items():
            m2 = abs(jet.d2).hi
            midpoint[k] = midpoint.get(k, IV(0)) + c.h * delta * value(middle[k])
            radii[k] = radii.get(k, IV(0)) + c.h * IV(m2) / (24 * n ** 3)
            max_d2[k] = max(max_d2.get(k, D(0)), m2)
        for k, v in local_bounds.items():
            bounds[k] = bounds.get(k, IV(0)) + c.h * delta * v
    signed = {k: v + symmetric(radii[k].hi) for k, v in midpoint.items()}
    return c, {'origin': 'NEW_E13C5_LOCAL_INTEGRALS', 'new_coefficient_evaluations': c.evaluations,
               'domain': c.domain, 'cell_coverage': {'normalized_domain': ['0', '1'], 'dyadic_cells': n,
                  'whole_cell_derivative_evaluations': n, 'midpoint_evaluations': n},
               'signed': signed, 'bounds': bounds, 'midpoint': midpoint,
               'midpoint_radius': {k: v.hi for k, v in radii.items()}, 'max_abs_second_t_derivative': max_d2}


def frozen_outputs_and_gains(c):
    h, L, e0, f0, q = c.h, c.L, c.e0, c.f0, c.qf
    W = (-L * h).exp()
    jl, je, j1 = response_j(L, h), response_j(L + 1, h), response_j(IV(1), h)
    if L.lo == L.hi == 0:
        integral_p = f0 * h + q * h.square() / 2
        integral_ep = e0 * (f0 * j1 + q * (1 - (1 + h) * (-h).exp()))
    else:
        integral_p = f0 * jl + q * (h - jl) / L
        integral_ep = e0 * (f0 * je + q * (j1 - je) / L)
    frozen = {'P1': f0 * W + q * jl, 'Z_eV': integral_ep,
              'QN': q * h, 'QE_eV': e0 * q * j1}
    gains = {'P1': W, 'Z_eV': e0 * je, 'QN': IV(0), 'QE_eV': IV(0)}
    for i, k in enumerate(SPECIES):
        lf, chi = c.lf[i], c.chi[i]
        frozen['A_' + k] = lf * integral_p
        frozen['B_' + k + '_eV'] = lf * integral_ep
        frozen['H_' + k + '_eV'] = lf * (integral_ep - chi * integral_p)
        gains['A_' + k] = lf * jl
        gains['B_' + k + '_eV'] = lf * e0 * je
        gains['H_' + k + '_eV'] = lf * (e0 * je - chi * jl)
    for collection in (frozen, gains):
        for prefix in ('A', 'B', 'H'):
            suffix = '_eV' if prefix != 'A' else ''
            collection[prefix + '_total' + suffix] = sum((collection[prefix + '_' + k + suffix] for k in SPECIES), IV(0))
        collection['P1_energy_eV'] = c.endpoint_E * collection['P1']
    return frozen, gains


def captured_outputs(control, chi):
    r, eps = control['row'], lift(1.602176634e-12)
    cap = {'P1': lift(r['n']), 'P1_energy_eV': lift(r['u']) / eps,
           'Z_eV': lift(r['red']) / eps, 'QN': lift(r['qn']), 'QE_eV': lift(r['qe']) / eps}
    for i, k in enumerate(SPECIES):
        cap['A_' + k] = lift(r['A_' + k])
        cap['B_' + k + '_eV'] = lift(r['B_' + k]) / eps
        cap['H_' + k + '_eV'] = cap['B_' + k + '_eV'] - chi[i] * cap['A_' + k]
    for prefix in ('A', 'B', 'H'):
        suffix = '_eV' if prefix != 'A' else ''
        cap[prefix + '_total' + suffix] = sum((cap[prefix + '_' + k + suffix] for k in SPECIES), IV(0))
    return cap


def remainder_bounds(c, b, gains, incoming_center, incoming_radius):
    eta = IV(incoming_radius)
    if eta.lo < 0:
        raise ArithmeticError('negative incoming radius')
    S = (IV(incoming_center.copy_abs()) + eta + b['B_r']).hi
    T = {'P1': b['H_h'].hi, 'Z_eV': b['H_E'].hi, 'QN': D(0), 'QE_eV': D(0)}
    for prefix in ('A', 'B', 'H'):
        for k in SPECIES:
            name = prefix + '_' + k + ('_eV' if prefix != 'A' else '')
            T[name] = min(b['effective_' + prefix + '_' + k].hi, b['triangle_' + prefix + '_' + k].hi)
    # The ZERO-incoming mathematical remainder has R_A,total=-R_P.
    # Incoming uncertainty instead has gains 1-W and W, respectively.
    T['A_total'] = b['H_h'].hi
    T['B_total_eV'] = min(b['effective_B_total'].hi, (c.endpoint_E * b['H_h'] + b['H_E']).hi)
    T['H_total_eV'] = min(b['effective_H_total'].hi, b['triangle_H_total'].hi)
    T['P1_energy_eV'] = (c.endpoint_E * b['H_h']).hi
    incoming = {k: (abs(gains[k]) * eta).hi for k in T}
    nonlinear = {k: (IV(S) * IV(T[k])).hi for k in T}
    total = {k: (IV(incoming[k]) + IV(nonlinear[k])).hi for k in T}
    return {'S_upper': S, 'T_upper': T, 'incoming_upper': incoming,
            'nonlinear_upper': nonlinear, 'total_before_numerical_upper': total}


def segment(control, n, cached, incoming_center, incoming_radius):
    c, local = local_integrals(control, n, cached)
    frozen, gains = frozen_outputs_and_gains(c)
    captured = captured_outputs(control, c.chi)
    remainder = remainder_bounds(c, local['bounds'], gains, incoming_center, incoming_radius)
    first = {k: v + gains[k] * IV(incoming_center) for k, v in local['signed'].items()}
    representation = {k: frozen[k] - captured[k] for k in first}
    outputs = {}
    for k in first:
        represented = first[k] + representation[k]
        candidate = center(represented)
        numerical = radius_about(represented, candidate)
        bound = (IV(numerical) + IV(remainder['total_before_numerical_upper'][k])).hi
        corr = IV(candidate) + symmetric(bound)
        outputs[k] = {'candidate': candidate, 'radius': bound,
                      'numerical_and_representation_radius': numerical,
                      'centered_firstvariation_plus_representation_interval': represented,
                      'true_minus_captured_interval': corr,
                      'true_absolute_interval': captured[k] + corr}
    frozen_n = frozen['P1'] - c.f0 + frozen['A_total'] - frozen['QN']
    frozen_e = frozen['P1_energy_eV'] - c.e0 * c.f0 + frozen['B_total_eV'] + frozen['Z_eV'] - frozen['QE_eV']
    first_n = first['P1'] - IV(incoming_center) + first['A_total'] - first['QN']
    first_e = first['P1_energy_eV'] - c.e0 * IV(incoming_center) + first['B_total_eV'] + first['Z_eV'] - first['QE_eV']
    heat_checks = {k: first['H_' + k + '_eV'] - first['B_' + k + '_eV'] + c.chi[i] * first['A_' + k] for i, k in enumerate(SPECIES)}
    ledgers = {'frozen_number': frozen_n, 'frozen_energy_eV': frozen_e,
               'firstvariation_number': first_n, 'firstvariation_energy_eV': first_e,
               **{'firstvariation_heat_' + k: v for k, v in heat_checks.items()}}
    if any(not v.contains(D(0)) for v in ledgers.values()):
        raise ArithmeticError('segment ledger interval does not contain zero')
    return c, {'key': control['key'], 'incoming': {'center': incoming_center, 'radius': incoming_radius,
                      'interval': IV(incoming_center) + symmetric(incoming_radius)},
               'local': local, 'frozen': frozen, 'gains': gains, 'captured': captured,
               'native_energy_stock_minus_Eh_n_eV': captured['P1_energy_eV'] - c.endpoint_E * captured['P1'],
               'representation_exactfrozen_minus_captured': representation,
               'firstvariation_with_candidate_incoming': first, 'remainder': remainder,
               'outputs': outputs, 'ledger_enclosures': ledgers,
               'endpoint_energy_eV': c.endpoint_E, 'initial_energy_eV': c.e0,
               'frozen_Lh': c.L * c.h}


def accumulate(prior, outgoing):
    raw = IV(prior['candidate']) + IV(outgoing['candidate'])
    point = center(raw)
    radius = (IV(prior['radius']) + IV(outgoing['radius']) + IV(radius_about(raw, point))).hi
    return {'candidate': point, 'radius': radius, 'interval': IV(point) + symmetric(radius)}


def seam(left_control, right_control, left_result):
    a, b = left_control['row'], right_control['row']
    dE = lift(b['e0']) - left_result['endpoint_energy_eV']
    photon = left_result['outputs']['P1']
    corr = photon['true_minus_captured_interval']
    ncap = left_result['captured']['P1']
    gap = ncap - lift(b['f0'])
    raw_next = IV(photon['candidate']) + gap
    next_center = center(raw_next)
    next_radius = (IV(photon['radius']) + IV(radius_about(raw_next, next_center))).hi
    endpoints = [IV(x) * IV(y) for x in (dE.lo, dE.hi) for y in (corr.lo, corr.hi)]
    correction_anchor = dE * corr
    native_anchor = dE * ncap
    true_anchor = dE * (ncap + corr)
    data = {'left': left_control['key'], 'right': right_control['key'],
            'event': {'left_mask': left_control['mask'], 'right_mask': right_control['mask'],
                      'source_left': left_control['source_on'], 'source_right': right_control['source_on'],
                      'anchored_left': a['anchored'], 'anchored_right': b['anchored']},
            'DeltaE_eV': dE, 'captured_photon_stitch_residual': gap,
            'incoming_correction_to_anchor': corr, 'anchor_endpoint_products': endpoints,
            'correction_anchor_relative_to_captured_photon_eV': correction_anchor,
            'native_photon_anchor_eV': native_anchor, 'true_anchor_eV': true_anchor,
            'true_anchor_split_enclosure': native_anchor + correction_anchor,
            'next_incoming': {'center': next_center, 'radius': next_radius,
                              'interval': IV(next_center) + symmetric(next_radius)}}
    return data, next_center, next_radius


def run_track(controls, n, cached, checkpoint):
    started = time.perf_counter()
    inc_center, inc_radius = D(0), D(0)
    rows, seams = [], []
    cumulative = {k: {'candidate': D(0), 'radius': D(0), 'interval': IV(0)} for k in MOMENTS}
    captured_sum = {k: IV(0) for k in MOMENTS}
    anchor_sum = IV(0)
    initial_P, initial_E = lift(controls[0]['row']['f0']), lift(controls[0]['row']['e0'])
    for j, control in enumerate(controls):
        c, result = segment(control, n, cached, inc_center, inc_radius)
        for k in MOMENTS:
            cumulative[k] = accumulate(cumulative[k], result['outputs'][k])
            captured_sum[k] = captured_sum[k] + result['captured'][k]
        result['cumulative_moment_corrections'] = {k: dict(v) for k, v in cumulative.items()}
        result['cumulative_captured_moments'] = dict(captured_sum)
        rows.append(result)
        if j + 1 < len(controls):
            join, inc_center, inc_radius = seam(control, controls[j + 1], result)
            seams.append(join)
            anchor_sum = anchor_sum + join['true_anchor_eV']
        checkpoint(rows, seams)
    true_moments = {k: captured_sum[k] + cumulative[k]['interval'] for k in MOMENTS}
    final = rows[-1]['outputs']
    number = final['P1']['true_absolute_interval'] - initial_P + true_moments['A_total'] - true_moments['QN']
    energy = (final['P1_energy_eV']['true_absolute_interval'] - initial_E * initial_P
              + true_moments['B_total_eV'] + true_moments['Z_eV'] - true_moments['QE_eV'] - anchor_sum)
    heat = {k: true_moments['H_' + k + '_eV'] - true_moments['B_' + k + '_eV'] + c.chi[i] * true_moments['A_' + k] for i, k in enumerate(SPECIES)}
    if not number.contains(D(0)) or not energy.contains(D(0)) or any(not v.contains(D(0)) for v in heat.values()):
        raise ArithmeticError('stitched number/energy/heat ledger does not contain zero')
    return {'track': {'mode': 'OFF', 'node': controls[0]['key'][2]}, 'segments': rows, 'seams': seams,
            'final_photon': final['P1'], 'final_energy_stock_eV': final['P1_energy_eV'],
            'cumulative_moment_corrections': cumulative, 'cumulative_captured_moments': captured_sum,
            'true_moment_enclosures': true_moments, 'summed_true_anchor_eV': anchor_sum,
            'global_ledger_enclosures': {'number': number, 'energy_eV_with_anchor_subtracted': energy,
                                        **{'heat_' + k: v for k, v in heat.items()}},
            'elapsed_seconds': time.perf_counter() - started}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--package', type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument('--subdivisions', type=int, required=True)
    ap.add_argument('--precision', type=int, default=60)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    for target in (args.output, args.output.with_name(args.output.stem + '_START.json'), args.output.with_name(args.output.stem + '_CHECKPOINT.json')):
        if target.exists():
            raise FileExistsError('fresh numerical output path required: ' + str(target))
    if (args.subdivisions, args.precision) not in {(32, 60), (128, 60), (512, 60), (32, 80)}:
        raise ValueError('only predeclared N/P work units are allowed')
    di.configure(args.precision)
    resource.setrlimit(resource.RLIMIT_AS, (1024 ** 3, 1024 ** 3))
    package = args.package.resolve()
    input_file = package / 'inputs/PATH_CONTROLS.json'
    cache_file = package / f'inputs/e13c4/N{args.subdivisions}_P{args.precision}.json'
    old_inputs = package / 'inputs/e13c4/SIX_CONTROLS.json'
    data, cached, previous = [json.loads(p.read_text()) for p in (input_file, cache_file, old_inputs)]
    checks = input_checks(data, previous['controls'])
    sources = [Path(__file__).resolve(), Path(di.__file__).resolve(), package / 'code/local_enclosure.py',
               package / 'PLAN.json', input_file, cache_file, old_inputs]
    identity = {'started_utc': datetime.now(timezone.utc).isoformat(), 'argv': sys.argv,
                'source_sha256_before_run': {str(p.relative_to(package)): sha(p) for p in sources},
                'python': sys.version, 'platform': platform.platform(),
                'decimal_libmpdec_version': __import__('decimal').__libmpdec_version__,
                'subdivisions': args.subdivisions, 'precision_digits': args.precision,
                'native_runs': 0, 'gas_advances': 0, 'old_continuous_solves': 0, 'RSS_limit_MiB': 1024}
    atomic_json(args.output.with_name(args.output.stem + '_START.json'), identity)
    started = time.perf_counter()
    tracks = []
    def checkpoint(rows, seams):
        atomic_json(args.output.with_name(args.output.stem + '_CHECKPOINT.json'), pack({
            'identity': identity, 'completed_tracks': tracks, 'active_track_segments': rows, 'active_track_seams': seams}))
    for start in (0, 3):
        track = run_track(data['controls'][start:start + 3], args.subdivisions, cached, checkpoint)
        tracks.append(track)
        print(json.dumps(pack({'node': track['track']['node'], 'seconds': track['elapsed_seconds'],
              'final_photon_correction': track['final_photon']['candidate'], 'photon_radius': track['final_photon']['radius'],
              'total_heat_correction_eV': track['cumulative_moment_corrections']['H_total_eV']['candidate'],
              'total_heat_radius_eV': track['cumulative_moment_corrections']['H_total_eV']['radius']})), flush=True)
    unchanged = all(sha(package / p) == h for p, h in identity['source_sha256_before_run'].items())
    if not unchanged:
        raise RuntimeError('source changed during execution')
    result = {'schema': 'bass-he-e13c5-path-enclosure-v1', 'identity': identity,
              'finished_utc': datetime.now(timezone.utc).isoformat(), 'input_checks': checks, 'tracks': tracks,
              'new_coefficient_evaluations': sum(r['local']['new_coefficient_evaluations'] for t in tracks for r in t['segments']),
              'reused_local_enclosures': 2, 'new_local_enclosures': 4, 'rounding_operation_counts': di.COUNTS,
              'source_unchanged_during_run': unchanged, 'elapsed_seconds': time.perf_counter() - started,
              'peak_RSS_KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              'claim_ceiling': 'two OFF three-segment captured fixed-gas tracks; conditional arithmetic/analytic enclosures; exact real sum of captured segment moments, not native aggregate reduction or uniform full path',
              'physical': 'HOLD', 'production': 'HOLD', 'execution_host_role': 'EXTERNAL_RUNNER_REPORTS_HOST_ROLE'}
    atomic_json(args.output, pack(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
