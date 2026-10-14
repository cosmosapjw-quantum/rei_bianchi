#!/usr/bin/env python3
"""One read-only reduction of the four frozen short-history pilot outputs."""
import csv
import hashlib
import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / 'runs' / '8ccb39fd2384'
RAW = ROOT / 'raw'
CASES = ('ZERO_DIRECT', 'ZERO_TABLE', 'PLUS_DIRECT', 'PLUS_TABLE')
FIELDS = ('a', 'time_s', 'b', 'x_HII', 'x_HeII', 'x_HeIII', 'w_erg_per_H',
          'next_dln_a', 'max_newton_residual', 'last_error', 'wall_elapsed_s')
COUNTS = ('accepted', 'attempts', 'rejects', 'consecutive_rejects', 'rhs', 'comparisons')
LEDGERS = ('source_n', 'source_u', 'absorbed_n', 'escaped_u', 'boundary_n',
           'boundary_u', 'thermal_work', 'photon_work', 'cmb_input', 'dr_events',
           'ce_cap_ev', 'excluded_dr_ev', 'rr_0', 'rr_1', 'rr_2', 'ci_0', 'ci_1',
           'ci_2', 'photo_0', 'photo_1', 'photo_2', 'ci_floor_0', 'ci_floor_1', 'ci_floor_2')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bits(x):
    return struct.pack('!d', x)


def must(condition, message):
    if not condition:
        raise ValueError(message)


def kv(path):
    out = {}
    for line in path.read_text().splitlines():
        key, value = line.split('=', 1)
        out[key] = value
    return out


def load_surface(path):
    lines = path.read_text().splitlines()
    must(len(lines) == 6 and lines[0] == 'AXBI_CHECKPOINT_V2', f'checkpoint shape {path}')
    x = list(map(float, lines[1].split()))
    n = list(map(int, lines[2].split()))
    l = list(map(float, lines[3].split()))
    p = list(map(float, lines[4].split()))
    must(len(x) == len(FIELDS) and len(n) == len(COUNTS) and len(l) == len(LEDGERS), f'checkpoint fields {path}')
    return {'state': dict(zip(FIELDS, x)), 'counts': dict(zip(COUNTS, n)),
            'ledgers': dict(zip(LEDGERS, l)), 'photons': p, 'initial_energy': float(lines[5])}


def verify_output_hashes(case):
    directory = RUNS / case
    lines = (RAW / case / 'output_sha256.txt').read_text().splitlines()
    for line in lines:
        digest, name = line.split('  ', 1)
        path = directory / name
        must(path.is_file() and sha(path) == digest, f'copy hash {case} {name}')
    must(len(lines) == len([p for p in directory.rglob('*') if p.is_file()]), f'copy file count {case}')
    return {'files': len(lines), 'manifest_sha256': sha(RAW / case / 'output_sha256.txt')}


def read_time(path):
    data = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith('User time (seconds):'):
            data['user_s'] = float(line.split(':', 1)[1])
        elif line.startswith('System time (seconds):'):
            data['system_s'] = float(line.split(':', 1)[1])
        elif line.startswith('Elapsed (wall clock) time'):
            value = line.rsplit(': ', 1)[1]
            parts = [float(x) for x in value.split(':')]
            data['wall_s'] = parts[-1] + (parts[-2] * 60 if len(parts) > 1 else 0) + (parts[-3] * 3600 if len(parts) > 2 else 0)
        elif line.startswith('Maximum resident set size (kbytes):'):
            data['peak_rss_kib'] = int(line.split(':', 1)[1])
        elif line.startswith('Exit status:'):
            data['exit'] = int(line.split(':', 1)[1])
    must(len(data) == 5, f'time fields {path}')
    return data


def ledger_check(path):
    with path.open(newline='') as f:
        rows = list(csv.DictReader(f))
    must(rows, f'empty ledgers {path}')
    failures = [x for x in rows if x['status'] == 'FAIL']
    must(not failures, f'ledger FAIL {path} {failures[0] if failures else ""}')
    metrics = {}
    for name in ('photon_count', 'augmented_energy_eV_per_H', 'J1_eV_per_H'):
        selected = [x for x in rows if x['ledger_name'] == name]
        must(selected and all(x['status'] == 'PASS' for x in selected), f'ledger status {path} {name}')
        ratios = [abs(float(x['residual'])) / max(float(x['tolerance']), 1e-300) for x in selected]
        metrics[name] = {'rows': len(selected), 'max_fraction_of_declared_tolerance': max(ratios)}
    return metrics


def read_case(case):
    d = RUNS / case
    copy = verify_output_hashes(case)
    must((RAW / case / 'exit').read_text().strip() == '0', f'exit {case}')
    ret = kv(d / 'RETURN.txt')
    must(ret['status'] == 'COMPLETE_REPRESENTED_INTERVAL' and ret['result'] == 'Ok(())', f'terminal {case}')
    surfaces = list(csv.DictReader((d / 'surfaces.csv').open(newline='')))
    must(len(surfaces) == 17 and [int(x['surface_id']) for x in surfaces] == list(range(17)), f'surface IDs {case}')
    states = [load_surface(d / f'surface_{i:02}.txt') for i in range(17)]
    grid = list(map(float, (d / 'energy_grid_eV.txt').read_text().split()))
    must(grid and all(math.isfinite(e) and e > 0 for e in grid), f'grid {case}')
    for i, (s, row) in enumerate(zip(states, surfaces)):
        must(bits(s['state']['a']) == bits(float(row['a'])), f'surface a {case} {i}')
        must(bits(s['state']['time_s']) == bits(float(row['time_s'])), f'surface time {case} {i}')
        must(len(s['photons']) % len(grid) == 0, f'grid vector {case} {i}')
        must(all(math.isfinite(v) and v >= 0 for v in s['photons']), f'photon sign {case} {i}')
        x, y, z = (s['state'][k] for k in ('x_HII', 'x_HeII', 'x_HeIII'))
        must(all(math.isfinite(v) and v >= 0 for v in (x, y, z)) and x <= 1 and y + z <= 1, f'gas fractions {case} {i}')
        must(all(math.isfinite(v) for v in s['state'].values()), f'nonfinite state {case} {i}')
        must(s['state']['max_newton_residual'] <= 1e-11, f'Newton {case} {i}')
        must(s['state']['last_error'] < 2e-4 and s['state']['last_error'] < 1e-5, f'local metric {case} {i}')
    must(bits(states[0]['state']['a']) == bits(1.0 / 21.0), f'start {case}')
    must(bits(states[-1]['state']['a']) == bits(1.0 / 20.8), f'end {case}')
    must(all(states[i]['state']['a'] < states[i + 1]['state']['a'] for i in range(16)), f'surface monotonic {case}')
    final = states[-1]['counts']
    must(int(ret['accepted']) == final['accepted'] and int(ret['attempts']) == final['attempts'] and int(ret['rhs_evaluations']) == final['rhs'], f'counter terminal {case}')
    coeff = kv(d / 'provider_counters.txt')
    must(int(coeff['coefficient_calls']) == int(surfaces[-1]['coefficient_calls']), f'coeff terminal {case}')
    must(int(coeff['coefficient_calls']) <= 5_000_000, f'coeff cap {case}')
    must(final['accepted'] <= 10_000 and final['attempts'] <= 30_000 and final['rhs'] <= 2_000_000, f'step cap {case}')
    time = read_time(RAW / case / 'time.log')
    must(time['exit'] == 0 and time['wall_s'] <= 600, f'wall {case}')
    size = sum(p.stat().st_size for p in d.rglob('*') if p.is_file())
    must(size <= 268435456, f'output cap {case}')
    return {'rows': surfaces, 'states': states, 'grid': grid, 'return': ret,
            'counters': coeff, 'time': time, 'bytes': size,
            'ledger_gate': ledger_check(d / 'ledgers.csv'), 'copy': copy}


def scalar_gate(ref, cand, absolute, relative):
    bound = absolute + relative * max(abs(ref), abs(cand))
    return {'reference': ref, 'candidate': cand, 'abs_delta': abs(ref - cand),
            'bound': bound, 'pass': math.isfinite(ref) and math.isfinite(cand) and abs(ref - cand) <= bound}


def compare_pair(direct, table):
    a, b = direct, table
    must(len(a['grid']) == len(b['grid']) and all(bits(x) == bits(y) for x, y in zip(a['grid'], b['grid'])), 'photon grid mismatch')
    worst = {}
    failures = []
    per_surface = []
    for i in range(17):
        ra, rb = a['rows'][i], b['rows'][i]
        sa, sb = a['states'][i], b['states'][i]
        must(int(ra['surface_id']) == int(rb['surface_id']) == i and bits(float(ra['a'])) == bits(float(rb['a'])), f'pair surface mismatch {i}')
        current = {'surface_id': i, 'a': float(ra['a']), 'fields': {}}
        for field, absolute, relative, va, vb in [
            ('x_HII', 1e-11, 1e-6, sa['state']['x_HII'], sb['state']['x_HII']),
            ('x_HeII', 1e-11, 1e-6, sa['state']['x_HeII'], sb['state']['x_HeII']),
            ('x_HeIII', 1e-11, 1e-6, sa['state']['x_HeIII'], sb['state']['x_HeIII']),
            ('ne_cm3', 1e-11, 1e-6, float(ra['ne_cm3']), float(rb['ne_cm3'])),
            ('Tgas_K', 1e-6, 1e-6, float(ra['Tgas_K']), float(rb['Tgas_K'])),
            ('thermal_eV_per_H', 1e-12, 1e-6, float(ra['thermal_eV_per_H']), float(rb['thermal_eV_per_H']))]:
            gate = scalar_gate(va, vb, absolute, relative)
            current['fields'][field] = gate
            if not gate['pass']:
                failures.append({'surface_id': i, 'field': field, **gate})
            previous = worst.get(field)
            if previous is None or gate['abs_delta'] / gate['bound'] > previous['fraction_of_bound']:
                worst[field] = {'surface_id': i, **gate, 'fraction_of_bound': gate['abs_delta'] / gate['bound']}
        pa, pb = sa['photons'], sb['photons']
        must(len(pa) == len(pb), f'photon vector size {i}')
        nl1 = sum(abs(x - y) for x, y in zip(pa, pb))
        nden = max(sum(pa), sum(pb), 1e-8)
        ul1 = sum(abs(x - y) * a['grid'][j % len(a['grid'])] for j, (x, y) in enumerate(zip(pa, pb)))
        ua = sum(x * a['grid'][j % len(a['grid'])] for j, x in enumerate(pa))
        ub = sum(x * a['grid'][j % len(a['grid'])] for j, x in enumerate(pb))
        uden = max(ua, ub, 1e-8)
        for field, value in [('photon_N_L1', nl1 / nden), ('photon_energy_L1', ul1 / uden)]:
            gate = {'normalized_L1': value, 'bound': 1e-6, 'pass': math.isfinite(value) and value <= 1e-6}
            current['fields'][field] = gate
            if not gate['pass']:
                failures.append({'surface_id': i, 'field': field, **gate})
            previous = worst.get(field)
            if previous is None or value > previous['normalized_L1']:
                worst[field] = {'surface_id': i, **gate}
        current['ledgers_max_abs_delta'] = max(abs(x - y) for x, y in zip(sa['ledgers'].values(), sb['ledgers'].values()))
        per_surface.append(current)
    return {'pass': not failures, 'failures': failures, 'worst': worst, 'surfaces': per_surface,
            'step_counts': {'direct': a['states'][-1]['counts'], 'table': b['states'][-1]['counts']}}


def main():
    binding = json.loads((ROOT / 'RUN_BINDING.json').read_text())
    must(sha(ROOT / 'target/release/axbi_temperature_rate_integration') == binding['binary_sha256'], 'binary binding')
    must(sha(ROOT.parent / 'temperature_rate_table_001/data/rates.bin') == binding['table_sha256'], 'table binding')
    data = {case: read_case(case) for case in CASES}
    pairs = {'ZERO': compare_pair(data['ZERO_DIRECT'], data['ZERO_TABLE']),
             'PLUS': compare_pair(data['PLUS_DIRECT'], data['PLUS_TABLE'])}
    time = {}
    for prefix in ('ZERO', 'PLUS'):
        d, t = data[prefix + '_DIRECT'], data[prefix + '_TABLE']
        wall_d, wall_t = d['time']['wall_s'], t['time']['wall_s']
        time[prefix] = {'direct_wall_s': wall_d, 'table_wall_s': wall_t,
                        'table_over_direct_wall': wall_t / wall_d,
                        'wall_savings_direct_minus_table': wall_d - wall_t,
                        'direct_cpu_s': d['time']['user_s'] + d['time']['system_s'],
                        'table_cpu_s': t['time']['user_s'] + t['time']['system_s'],
                        'table_load_s': float(t['counters']['load_s']),
                        'direct_peak_rss_kib': d['time']['peak_rss_kib'],
                        'table_peak_rss_kib': t['time']['peak_rss_kib']}
    result = {'schema': 'rei.axbi.temperature_rate_trajectory_comparison.v1',
              'scope': 'finite_binary64_short_history_zbar20_to19.8_four_single_runs',
              'source_binding_sha256': sha(ROOT / 'RUN_BINDING.json'),
              'cases': {k: {'return': v['return'], 'counters': v['counters'], 'time': v['time'],
                            'output_bytes': v['bytes'], 'ledger_gate': v['ledger_gate'],
                            'output_copy': v['copy']} for k, v in data.items()},
              'pairs': pairs, 'numerical_pass': all(x['pass'] for x in pairs.values()),
              'per_step_ledger': 'driver tentative guard completed; only cumulative output residuals independently reduced',
              'signed_response_resolution': 'HOLD_NO_INDEPENDENT_RESOLUTION_ERROR_OR_FLOOR',
              'scientific_admission': 'NOT_ISSUED'}
    performance = {'schema': 'rei.axbi.temperature_rate_performance_receipt.v1',
                   'scope': 'one_run_per_backend_per_case_same_NCP_host_ordered',
                   'times': time, 'construction_s': 'NOT_MEASURED_IN_THIS_WORK; predecessor evidence separate',
                   'amortization': 'NO_MEASURED_AMORTIZATION' if all(x['wall_savings_direct_minus_table'] <= 0 for x in time.values()) else 'CONDITIONAL_POSITIVE_SAVINGS_ONLY',
                   'claim_ceiling': 'No whole campaign speedup or long-history extrapolation'}
    (ROOT / 'TRAJECTORY_COMPARISON.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    (ROOT / 'PERFORMANCE_RECEIPT.json').write_text(json.dumps(performance, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'numerical_pass': result['numerical_pass'], 'pair_worst': {k: v['worst'] for k, v in pairs.items()},
                      'performance': time, 'amortization': performance['amortization']}, indent=2))


if __name__ == '__main__':
    main()
