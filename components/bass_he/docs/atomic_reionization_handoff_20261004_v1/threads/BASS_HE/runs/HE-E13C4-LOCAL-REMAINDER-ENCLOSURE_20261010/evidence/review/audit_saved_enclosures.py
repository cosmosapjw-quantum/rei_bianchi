#!/usr/bin/env python3
"""Independent exact rational audit of saved E13C4 evidence; no solver imports."""
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import sys
import time

PACKAGE = Path(__file__).resolve().parents[2]
READS, CHECKS = {}, []


def load(rel):
    raw = (PACKAGE / rel).read_bytes()
    READS[rel] = {'path': rel, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                  'read_scope': 'complete JSON parsed; relevant fields audited by independent Fraction code'}
    return json.loads(raw)


def check(identifier, condition, detail=None):
    CHECKS.append({'id': identifier, 'pass': bool(condition), 'detail': detail})


def rational(value):
    return F.from_float(value) if isinstance(value, float) else F(value)


def interval(value):
    return rational(value['lo']), rational(value['hi'])


def isum(*ivs):
    return sum((x[0] for x in ivs), F(0)), sum((x[1] for x in ivs), F(0))


def neg(iv):
    return -iv[1], -iv[0]


def zero_in(iv):
    return iv[0] <= 0 <= iv[1]


def contained(inner, outer):
    return outer[0] <= inner[0] <= inner[1] <= outer[1]


def flatten(data, primary=False):
    if primary:
        out = {'P1': data['delta_P'], 'Z_eV': data['delta_redshift_eV'],
               'QN': data['delta_source_number'], 'QE_eV': data['delta_source_energy_eV'],
               'H_total_eV': data['delta_total_heat_eV']}
        groups = [('A', data['delta_A']), ('B', data['delta_B_eV']), ('H', data['delta_heat_eV'])]
    else:
        out = {k: data[k] for k in ('P1', 'Z_eV', 'QN', 'QE_eV', 'H_total_eV')}
        groups = [('A', data['A']), ('B', data['B_eV']), ('H', data['H_eV'])]
    for prefix, values in groups:
        for species, value in zip(('HI', 'HeI', 'HeII'), values):
            out[prefix + '_' + species + ('_eV' if prefix != 'A' else '')] = value
    return {k: rational(v) for k, v in out.items()}


def scan_intervals(obj, prefix=''):
    bad, count = [], 0
    if isinstance(obj, dict):
        if set(obj) == {'lo', 'hi'}:
            lo, hi = interval(obj)
            return ([] if lo <= hi else [prefix]), 1
        for key, value in obj.items():
            invalid, n = scan_intervals(value, prefix + '/' + str(key))
            bad += invalid; count += n
    elif isinstance(obj, list):
        for key, value in enumerate(obj):
            invalid, n = scan_intervals(value, prefix + '/' + str(key))
            bad += invalid; count += n
    elif isinstance(obj, float) and not math.isfinite(obj):
        bad.append(prefix + ': nonfinite float')
    return bad, count


def main():
    started = datetime.now(timezone.utc).isoformat()
    tick = time.perf_counter()
    own_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    plan = load('PLAN.json')
    selected = load('inputs/SIX_CONTROLS.json')
    decimal_old = load('inputs/e13c3/evidence/decimal/DECIMAL_RESULTS.json')
    oracle_old = load('inputs/e13c3/inputs/e13c2/evidence/ORACLE_RESULTS.json')
    primary_old = load('inputs/e13c3/evidence/local_gl12/RESULTS.json')
    for item in selected['sources']:
        raw = (PACKAGE / item['path']).read_bytes()
        check('SOURCE_HASH/' + item['path'], hashlib.sha256(raw).hexdigest() == item['sha256'])
    check('FIXED_SIX_KEYS', [c['key'] for c in selected['controls']] == plan['scope']['local_ids'])
    for c, d, o, p in zip(selected['controls'], decimal_old['results'], oracle_old['results'], primary_old['local_controls']):
        key = '/'.join(map(str, c['key']))
        check('INPUT_AND_SAVED_EVIDENCE/' + key,
              c['key'] == d['key'] == o['key'] == p['id']
              and c['row'] == d['input_row_exact_csv_strings'] == o['input_row_exact_csv_strings']
              and c['stage'] == d['stage_input_exact_csv_strings'] == o['stage_input_exact_csv_strings']
              and c['mask'] == d['fixed_absorber_support'] == o['fixed_absorber_support']
              and c['source_on'] == d['source_on']
              and c['saved_decimal_firstvariation'] == d['calculated_by_degree']['20']
              and c['saved_decimal_GL12'] == d['calculated_by_degree']['12']
              and c['saved_continuous_defect'] == d['saved_signed_reference']
              and c['saved_reference_order_gap'] == o['degree20_minus_degree12']
              and c['saved_primary_GL12'] == p)
        check('LOCAL_ZERO_AND_OUTFLOW/' + key, d['local_initial_correction'] == '0'
              and F(c['row']['outn']) == F(c['row']['oute']) == 0)
    runs = {}
    runtime = []
    for n, precision in ((32, 60), (128, 60), (512, 60), (32, 80)):
        label = f'N{n}_P{precision}'
        result = load('evidence/' + label + '.json')
        start = load('evidence/' + label + '_START.json')
        record = load(f'evidence/run_n{n}_p{precision}/RUN.json')
        checkpoint = load('evidence/' + label + '_CHECKPOINT.json')
        sources_match = all(hashlib.sha256((PACKAGE / k).read_bytes()).hexdigest() == v
                            for k, v in start['source_sha256_before_run'].items())
        check('RUN_IDENTITY/' + label, start == result['identity'] == checkpoint['identity']
              and sources_match and result['source_unchanged_during_run']
              and plan['created_utc'] < start['started_utc']
              and [c['key'] for c in result['controls']] == plan['scope']['local_ids']
              and checkpoint['completed_controls'] == result['controls'])
        log_ok = True
        for file in ('stdout', 'stderr'):
            path = f'evidence/run_n{n}_p{precision}/{file}.txt'
            raw = (PACKAGE / path).read_bytes()
            READS[path] = {'path': path, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                           'read_scope': 'full raw log bytes; stdout JSON lines parsed; stderr checked empty'}
            log_ok &= hashlib.sha256(raw).hexdigest() == record[file + '_sha256']
            if file == 'stdout':
                log_ok &= [json.loads(line)['key'] for line in raw.decode().splitlines()] == plan['scope']['local_ids']
            else:
                log_ok &= not raw
        check('ACTUAL_EXECUTION/' + label, record['actual_exit'] == 0 and record['status'] == 'COMPLETE'
              and result['elapsed_seconds'] < 180 and result['peak_RSS_KiB'] < 1024 * 1024
              and start['native_runs'] == start['gas_advances'] == start['old_continuous_solves'] == 0 and log_ok)
        bad, count = scan_intervals(result)
        check('INTERVAL_WELL_FORMED/' + label, not bad, {'count': count, 'invalid': bad})
        check('SAVED_COMPATIBILITY_FLAGS/' + label,
              not result['compatibility_failures'] and not result['saved_firstvariation_containment_failures']
              and len(result['saved_evidence_compatibility_checks']) == 168)
        for c, original in zip(result['controls'], selected['controls']):
            key = label + '/' + '/'.join(map(str, c['key']))
            exact = {k: interval(v) for k, v in c['exact_firstvariation_integral_enclosures'].items()}
            mid = {k: interval(v) for k, v in c['frozen_quadrature_midpoint_sum_enclosures'].items()}
            radii = {k: F(v) for k, v in c['validated_midpoint_truncation_radii'].items()}
            trunc = {k: F(v) for k, v in c['analytic_truncation_upper'].items()}
            bv = {k: interval(v) for k, v in c['variation_integral_enclosures'].items()}
            h = F.from_float(float(original['row']['h']))
            L = sum((F.from_float(float(original['row']['lambda_' + s])) for s in ('HI', 'HeI', 'HeII')), F(0))
            check('CAPTURED_DOMAIN/' + key, interval(c['frozen']['h']) == (h, h)
                  and contained((L, L), interval(c['frozen']['L']))
                  and F(c['domain']['active_heat_weight_min_eV']) >= 0
                  and F(c['domain']['H_min']) > 0 and F(c['domain']['q_min']) >= 0
                  and c['domain']['gas_checked_evaluations'] == c['domain']['positive_rate_evaluations'] == 2 * n
                  and c['cell_coverage']['whole_cell_derivative_evaluations'] == n
                  and c['cell_coverage']['midpoint_evaluations'] == n)
            check('MIDPOINT_ENCLOSURE_COMPOSITION/' + key,
                  all(radii[k] >= 0 and exact[k][0] <= mid[k][0] - radii[k]
                      and mid[k][1] + radii[k] <= exact[k][1] for k in exact))
            check('TRUNCATION_ARITHMETIC/' + key,
                  all(v >= 0 for v in trunc.values()) and trunc['QN'] == trunc['QE_eV'] == 0
                  and trunc['P1'] >= bv['B_r'][1] * bv['H_h'][1]
                  and trunc['Z_eV'] >= bv['B_r'][1] * bv['H_E'][1]
                  and trunc['A_total'] == trunc['P1']
                  and F(c['sup_photon_remainder_upper']) >= bv['B_r'][1] * bv['D_L'][1])
            alternatives_ok = True
            for obs, values in c['truncation_alternatives'].items():
                suffix = 'H_total' if obs == 'H_total_eV' else obs.removesuffix('_eV')
                effective, triangle = F(values['effective']), F(values['triangle'])
                alternatives_ok &= effective >= bv['B_r'][1] * bv['effective_' + suffix][1]
                alternatives_ok &= triangle >= bv['B_r'][1] * bv['triangle_' + suffix][1]
                alternatives_ok &= trunc[obs] == min(effective, triangle)
            check('EFFECTIVE_AND_TRIANGLE_BOUND_COMPOSITION/' + key, alternatives_ok)
            check('FIRSTVARIATION_LEDGER_INTERVALS/' + key,
                  zero_in(isum(exact['P1'], exact['A_total'], neg(exact['QN'])))
                  and zero_in(isum(exact['P1_energy_eV'], exact['B_total_eV'], exact['Z_eV'], neg(exact['QE_eV']))))
            inactive_ok = True
            for species, active in original['mask'].items():
                if not active:
                    for prefix in ('A', 'B', 'H'):
                        obs = prefix + '_' + species + ('_eV' if prefix != 'A' else '')
                        inactive_ok &= exact[obs] == (0, 0) and trunc[obs] == 0
            check('INACTIVE_EXACT_ZERO/' + key, inactive_ok)
            reference = flatten(original['saved_continuous_defect'])
            for lane, original_candidate in [('saved_E13C3_primary_GL12', flatten(original['saved_primary_GL12'], True)),
                                               ('saved_E13C3_Decimal_GL20', flatten(original['saved_decimal_firstvariation']))]:
                candidate_ok = floors_ok = True
                for obs, saved in c['saved_candidate_comparison'][lane].items():
                    candidate, ref = F(saved['candidate_value']), F(saved['saved_reference_value'])
                    eta = max(abs(candidate - endpoint) for endpoint in exact[obs])
                    full = F(saved['certified_candidate_to_true_defect_upper'])
                    reported_eta = F(saved['certified_candidate_to_exact_firstvariation_upper'])
                    gap = abs(candidate - ref)
                    candidate_ok &= candidate == original_candidate[obs] and ref == reference[obs]
                    candidate_ok &= reported_eta >= eta and full >= reported_eta + trunc[obs]
                    candidate_ok &= F(saved['certified_truncation_upper']) == trunc[obs]
                    candidate_ok &= saved['candidate_inside_firstvariation_interval'] == contained((candidate, candidate), exact[obs])
                    candidate_ok &= contained((gap, gap), interval(saved['observed_saved_reference_absolute_gap']))
                    candidate_ok &= gap <= full and exact[obs][0] - trunc[obs] <= ref <= exact[obs][1] + trunc[obs]
                    candidate_ok &= saved['reference_is_rigorous_enclosure'] is False
                    floor = F('1e-24') if 'eV' in obs else F('1e-25')
                    if abs(ref) < floor:
                        floors_ok &= saved['full_bound_over_saved_defect_abs_upper'] is None
                        floors_ok &= saved['relative_defect_status'] == 'UNRESOLVED_BELOW_FLOOR'
                    else:
                        floors_ok &= F(saved['full_bound_over_saved_defect_abs_upper']) >= full / abs(ref)
                    if interval(saved['observed_saved_reference_absolute_gap'])[0] < floor:
                        floors_ok &= saved['truncation_bound_over_observed_gap_upper'] is None
                        floors_ok &= saved['sharpness_status'] == 'UNRESOLVED_BELOW_FLOOR'
                    else:
                        floors_ok &= F(saved['truncation_bound_over_observed_gap_upper']) >= trunc[obs] / gap
                check('CANDIDATE_AND_REFERENCE_ARITHMETIC/' + key + '/' + lane, candidate_ok)
                check('FLOORS_AND_RATIO_ROUNDING/' + key + '/' + lane, floors_ok)
        runs[(n, precision)] = result
        runtime.append({'run': label, 'start': start['started_utc'], 'finish': result['finished_utc'],
                        'seconds': result['elapsed_seconds'], 'RSS_KiB': result['peak_RSS_KiB']})
    for coarse, fine in ((32, 128), (128, 512)):
        for ca, cb in zip(runs[(coarse, 60)]['controls'], runs[(fine, 60)]['controls']):
            key = '/'.join(map(str, ca['key']))
            check(f'REFINEMENT_NESTING_N{coarse}_N{fine}/' + key,
                  all(contained(interval(cb['exact_firstvariation_integral_enclosures'][k]), interval(v))
                      for k, v in ca['exact_firstvariation_integral_enclosures'].items()))
    for ca, cb in zip(runs[(32, 60)]['controls'], runs[(32, 80)]['controls']):
        check('PRECISION_INTERVAL_NESTING/' + '/'.join(map(str, ca['key'])),
              all(contained(interval(cb['exact_firstvariation_integral_enclosures'][k]), interval(v))
                  for k, v in ca['exact_firstvariation_integral_enclosures'].items()))
    failed = [x for x in CHECKS if not x['pass']]
    result = {'schema': 'bass-he-e13c4-independent-saved-audit-v1',
              'role': 'independent decision reviewer; no candidate authorship',
              'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
              'elapsed_seconds': time.perf_counter() - tick, 'argv': sys.argv,
              'producer_sha256_as_run': own_sha, 'owner_solver_imports': 0,
              'old_continuous_solves': 0, 'native_runs': 0, 'gas_advances': 0,
              'arithmetic': 'fractions.Fraction for exact saved-endpoint/ratio composition; no Decimal rounding or transcendental calls',
              'checks': CHECKS, 'passed': len(CHECKS) - len(failed), 'failed': failed,
              'runtime_observation': runtime,
              'execution_overlap': 'N32/P80 precision control overlaps N128/P60; the three P60 primaries are serial',
              'read_file_identities': list(READS.values()),
              'claim_ceiling': 'saved-evidence integrity and rational bound-composition audit; not a new continuum solve or a proof from numerical agreement'}
    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'passed': result['passed'], 'failed': failed, 'elapsed_seconds': result['elapsed_seconds']}))
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
