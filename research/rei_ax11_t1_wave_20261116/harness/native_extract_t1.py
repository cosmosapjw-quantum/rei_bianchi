#!/usr/bin/env python3
"""Stream closed native T1 histories, keeping original query brackets only.

No evolution, extrapolation, tolerance modification, or baseline regeneration.
Raw post-checkpoint tails remain in their original files and are excluded from
the admitted sample. Four-neighbor windows support a separate interpolation
sensitivity diagnostic on the cloud; primary interpolation stays unchanged.
"""
import argparse
import base64
from collections import deque
import gzip
import hashlib
import json
import math
from pathlib import Path
import resource
import time

FHE = .2454 / (4 * (1 - .2454))
EPS = 2.220446049250313e-16
LEDGER_NAMES = ['photon_count', 'augmented_energy_eV_per_H', 'J1_eV_per_H',
                'source_N_per_H', 'source_U_eV_per_H', 'absorbed_N_per_H',
                'escape_U_eV_per_H', 'boundary_N_per_H', 'boundary_U_eV_per_H',
                'thermal_work_eV_per_H', 'photon_work_eV_per_H',
                'signed_CMB_input_eV_per_H', 'DR_events_per_H',
                'CE_cap_eV_per_H', 'excluded_DR_eV_per_H'] + [
                    f'{kind}_{k}_per_H' for k in range(3)
                    for kind in ['RR_events', 'CI_events', 'photo_events', 'CI_floor_events']]


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def dump(path, value):
    data = (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()
    require(not path.exists(), 'OUTPUT_ALREADY_EXISTS:' + str(path))
    path.write_bytes(data)


def checkpoint(path):
    lines = path.read_text().splitlines()
    require(lines[0] == 'AXBI_CHECKPOINT_V2', 'CHECKPOINT_FORMAT')
    state = list(map(float, lines[1].split()))
    counts = list(map(int, lines[2].split()))
    require(len(state) == 11 and len(counts) == 6, 'CHECKPOINT_FIELDS')
    return {'a': state[0], 'time_s': state[1], 'x_HII': state[3],
            'x_HeII': state[4], 'x_HeIII': state[5], 'wall_s': state[10],
            'accepted': counts[0], 'trials': counts[1], 'rejects': counts[2],
            'RHS': counts[4], 'comparisons': counts[5], 'sha256': sha(path)}


def scan_ledgers(folder, case, cp, durable_rows, clean):
    """Inspect every saved balance, including the initial row of each segment."""
    path = folder / 'ledgers.csv'
    h = hashlib.sha256()
    raw = kept = 0
    last_time = None
    maxima = {}
    terminal = {}
    with path.open('rb') as stream:
        header = next(stream)
        h.update(header)
        require(header.decode().strip() == 'case_id,time_s,ledger_name,residual,tolerance,status',
                'LEDGER_HEADER')
        for line in stream:
            h.update(line)
            raw += 1
            fields = line.decode().rstrip('\n').split(',')
            require(len(fields) == 6 and fields[0] == case, 'LEDGER_ROW')
            t = float(fields[1])
            if t > cp['time_s']:
                continue
            name = fields[2]
            value = float(fields[3])
            require(name == LEDGER_NAMES[kept % len(LEDGER_NAMES)], 'LEDGER_ORDER')
            require(math.isfinite(t) and math.isfinite(value), 'NONFINITE_LEDGER')
            if kept % len(LEDGER_NAMES) == 0:
                require(last_time is None or t > last_time, 'LEDGER_NONMONOTONE_TIME')
                last_time = t
            else:
                require(t == last_time, 'LEDGER_BATCH_CLOCK_MISMATCH')
            if name in LEDGER_NAMES[:3]:
                tolerance = float(fields[4])
                require(math.isfinite(tolerance) and tolerance > 0., 'LEDGER_TOLERANCE')
                require(fields[5] == 'PASS' and abs(value) <= tolerance, 'FAILED_SAVED_LEDGER')
                ratio = abs(value) / tolerance
                if name not in maxima or ratio > maxima[name]['max_abs_residual_over_tolerance']:
                    maxima[name] = {'max_abs_residual_over_tolerance': ratio,
                                    'residual': value, 'tolerance': tolerance, 'time_s': t}
            else:
                require(fields[4] == '' and fields[5] == 'VALUE', 'LEDGER_VALUE_CONTRACT')
            terminal[name] = value
            kept += 1
    require(kept == durable_rows * len(LEDGER_NAMES) and last_time == cp['time_s'],
            'MISSING_DURABLE_LEDGER_ROWS')
    if clean:
        require(raw == kept, 'ORPHAN_LEDGER_ON_CLEAN_SEGMENT')
    return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': h.hexdigest(),
            'raw_rows': raw, 'durable_rows': kept, 'excluded_raw_tail_rows': raw - kept,
            'maximum_ratios': maxima, 'terminal_values': terminal}


class QueryWindows:
    """Keep up to two rows before and one row after the first upper bracket."""
    def __init__(self, targets, coordinate, column):
        self.targets = targets
        self.coordinate = coordinate
        self.column = column
        self.next = 0
        self.windows = []
        self.pending = []

    def add(self, current, recent):
        for item in self.pending:
            item['rows'].append(current)
        self.pending = []
        while self.next < len(self.targets):
            query = self.targets[self.next]
            if query[self.coordinate] > current[self.column]:
                break
            item = {'query': query, 'rows': list(recent),
                    'endpoint_clip': False}
            self.windows.append(item)
            self.pending.append(item)
            self.next += 1

    def finish(self, first, last, recent):
        # Original helper permits only endpoint roundoff, not extrapolation.
        axis_tol = 8 * EPS * max(1., abs(first[self.column]), abs(last[self.column]))
        while self.next < len(self.targets):
            query = self.targets[self.next]
            if query[self.coordinate] > last[self.column] + axis_tol:
                break
            self.windows.append({'query': query, 'rows': list(recent),
                                 'endpoint_clip': True})
            self.next += 1
        return {'windows': self.windows,
                'unrepresented_query_count': len(self.targets) - self.next,
                'represented_query_count': self.next,
                'native_axis_domain': [first[self.column], last[self.column]],
                'endpoint_roundoff_allowance': axis_tol}


def consume_case(root, case, grid, records, output):
    selected = [r for r in records if r.get('name', '').startswith(case + '_segment_')]
    require(selected and all(r['status'] == 'FINISHED' for r in selected),
            'CASE_NOT_TERMINATED:' + case)
    previous = None
    last_cp = None
    first = None
    headers = None
    recent = deque(maxlen=3)
    milestones = {}
    all_upward_crossings = {str(level): [] for level in [.1, .5, .9]}
    maximum = {'hydrogen_sum': 0., 'helium_sum': 0.,
               'electron_charge_per_H': 0., 'comoving_hydrogen_relative': 0.}
    numeric_max = {}
    segments = []
    n = 0
    queues = None
    for segment_index, record in enumerate(selected):
        folder = Path(record.get('output_directory') or record['command'][3])
        require(folder == root / 'cases' / case / f'segment_{segment_index:03d}',
                'SEGMENT_SEQUENCE_OR_PATH')
        cp = checkpoint(folder / 'checkpoint.txt')
        cp_start = checkpoint(folder / 'checkpoint.start.txt')
        if last_cp is None:
            require(cp_start['accepted'] == 0 and cp_start['time_s'] == 0., 'NOT_FULL_IC')
        else:
            require(sha(folder / 'input_checkpoint.txt') == last_cp['sha256'],
                    'CONTINUATION_CHECKPOINT_IDENTITY')
            require(cp_start == last_cp, 'CONTINUATION_START_STATE')
        if 'checkpoint_sha256' in record:
            require(cp['sha256'] == record['checkpoint_sha256'], 'END_CHECKPOINT_IDENTITY')
        expected = cp['accepted'] - cp_start['accepted'] + 1
        keep = 0
        raw_rows = 0
        history_hash = hashlib.sha256()
        with (folder / 'history.csv').open('rb') as stream:
            line = next(stream)
            history_hash.update(line)
            new_headers = line.decode().strip().split(',')
            if headers is None:
                headers = new_headers
                keys = {key: i for i, key in enumerate(headers)}
                queues = {
                    'fixed_a': QueryWindows(grid['fixed_a'], 'a', keys['a']),
                    'fixed_t': QueryWindows(grid['fixed_t'], 'elapsed_time_s', keys['time_s']),
                }
            require(headers == new_headers, 'CHANGING_HISTORY_COLUMNS')
            for line in stream:
                history_hash.update(line)
                raw_rows += 1
                fields = line.decode().rstrip('\n').split(',')
                require(len(fields) == len(headers), 'MALFORMED_RAW_HISTORY')
                row = [fields[0]] + [float(x) for x in fields[1:]]
                require(row[0] == case, 'WRONG_CASE')
                require(all(math.isfinite(x) for x in row[1:]), 'NONFINITE_HISTORY')
                a, t = row[keys['a']], row[keys['time_s']]
                if raw_rows > expected:
                    # A killed/failing process may leave a post-checkpoint tail.
                    require(a >= cp['a'] and t >= cp['time_s'], 'UNEXPECTED_RAW_TAIL')
                    continue
                keep += 1
                require(a <= cp['a'] and t <= cp['time_s'], 'HISTORY_BEYOND_CHECKPOINT')
                if segment_index and raw_rows == 1:
                    require(row == previous, 'NONIDENTICAL_SEGMENT_BOUNDARY')
                    continue
                q = row[keys['q_ref']]
                require(q == (0. if case == 'ZERO' else .01), 'WRONG_Q')
                require(abs(row[keys['zbar']] - (1 / a - 1)) <= 1e-12, 'A_Z_MISMATCH')
                fractions = [row[keys[x]] for x in ['x_HI', 'x_HII', 'x_HeI', 'x_HeII', 'x_HeIII']]
                hi, hii, hei, heii, heiii = fractions
                require(min(fractions) >= 0. and max(fractions) <= 1., 'FRACTION_DOMAIN')
                nh, ne = row[keys['nH_proper_cm3']], row[keys['ne_proper_cm3']]
                require(nh > 0. and ne >= 0. and row[keys['temperature_K']] > 0., 'GAS_DOMAIN')
                if first is None:
                    first = row
                    require(t == 0. and a == 1 / 21, 'IC_DOMAIN')
                    density = nh * a**3
                if previous is not None:
                    require(a > previous[keys['a']] and t > previous[keys['time_s']],
                            'NONMONOTONE_HISTORY')
                    for level in [.1, .5, .9]:
                        label = str(level)
                        if previous[keys['x_HII']] < level <= hii:
                            crossing = {'level': level, 'lower_row': n - 1,
                                        'upper_row': n, 'rows': [previous, row]}
                            all_upward_crossings[label].append(crossing)
                            if label not in milestones:
                                milestones[label] = crossing
                residuals = {
                    'hydrogen_sum': abs(hi + hii - 1.),
                    'helium_sum': abs(hei + heii + heiii - 1.),
                    'electron_charge_per_H': abs(ne / nh - (hii + FHE * (heii + 2 * heiii))),
                    'comoving_hydrogen_relative': abs(nh * a**3 / density - 1.),
                }
                for key, value in residuals.items():
                    maximum[key] = max(maximum[key], value)
                for key in ['temperature_K', 'x_HII', 'photon_n_per_H', 'photon_u_eV_per_H']:
                    value = row[keys[key]]
                    if key not in numeric_max or value > numeric_max[key]['value']:
                        numeric_max[key] = {'value': value, 'a': a, 'time_s': t, 'row': n}
                recent.append(row)
                for query in queues.values():
                    query.add(row, recent)
                previous = row
                n += 1
        require(keep == expected, 'MISSING_DURABLE_HISTORY_ROWS')
        require(all(previous[keys[k]] == cp[k] for k in
                    ['a', 'time_s', 'x_HII', 'x_HeII', 'x_HeIII']), 'HISTORY_CHECKPOINT_STATE')
        if record.get('summary', {}).get('error') == 'NONE':
            require(raw_rows == expected, 'ORPHANS_ON_CLEAN_SEGMENT')
        ledger_stats = scan_ledgers(folder, case, cp, expected,
                                   record.get('summary', {}).get('error') == 'NONE')
        segments.append({'path': str(folder), 'history_bytes': (folder / 'history.csv').stat().st_size,
                         'history_sha256': history_hash.hexdigest(), 'raw_rows': raw_rows,
                         'durable_rows': keep, 'excluded_raw_tail_rows': raw_rows - keep,
                         'boundary_duplicate_removed': bool(segment_index),
                         'start_checkpoint': cp_start, 'end_checkpoint': cp,
                         'ledgers': ledger_stats})
        last_cp = cp
    require(n == last_cp['accepted'] + 1, 'COMPOSED_ACCEPTED_ROW_COUNT')
    require(max(maximum.values()) <= 1e-12, 'NUCLEI_CHARGE_DENSITY_TOLERANCE')
    result = {'schema': 'REI_AX11_T1_NATIVE_SAMPLE_BRACKETS_V1', 'case': case,
              'headers': headers, 'segments': segments, 'composed_rows': n,
              'first_row': first, 'last_row': previous,
              'endpoint_reached': previous[keys['a']] == .2,
              'nuclei_charge_density_residuals': maximum, 'native_maxima': numeric_max,
              'milestones': milestones, 'all_upward_crossings': all_upward_crossings,
              'samples': {mode: query.finish(first, previous, recent)
                          for mode, query in queues.items()},
              'grid_sha256': sha(root / 'SAMPLING_GRID.json'),
              'claim_scope': 'Native durable rows and sample brackets only; no evolution error bound.'}
    data = (json.dumps(result, separators=(',', ':'), allow_nan=False) + '\n').encode()
    path = output / (case + '_sample_brackets.json.gz')
    with path.open('xb') as stream:
        with gzip.GzipFile(filename='', mode='wb', fileobj=stream, mtime=0, compresslevel=1) as packed:
            packed.write(data)
    # The transfer file is mechanical, not a new scientific artifact.
    encoded = base64.encodebytes(path.read_bytes())
    (output / (path.name + '.b64')).write_bytes(encoded)
    return {'case': case, 'path': str(path), 'bytes': path.stat().st_size,
            'sha256': sha(path), 'composed_rows': n,
            'endpoint_reached': result['endpoint_reached'],
            'segments': segments, 'residuals': maximum,
            'sampling_counts': {k: v['represented_query_count'] for k, v in result['samples'].items()}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    begin, cpu = time.monotonic(), time.process_time()
    require(not args.output.exists(), 'OUTPUT_DIRECTORY_EXISTS')
    ledger = json.loads((args.root / 'RUN_LEDGER.json').read_text())
    require(ledger['status'] == 'T1_WAVE_FINISHED_WITH_RETAINED_OUTCOMES', 'WAVE_STILL_RUNNING')
    args.output.mkdir()
    try:
        grid = json.loads((args.root / 'SAMPLING_GRID.json').read_text())
        results = [consume_case(args.root, case, grid, ledger['records'], args.output)
                   for case in ['ZERO', 'PLUS']]
        receipt = {'status': 'NATIVE_DURABLE_HISTORY_EXTRACTED', 'cases': results,
                   'input_ledger_sha256': sha(args.root / 'RUN_LEDGER.json'),
                   'script_sha256': sha(Path(__file__)), 'CPU_s': time.process_time() - cpu,
                   'wall_s': time.monotonic() - begin,
                   'max_RSS_kB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   'original_DAG': '10/17', 'expansion_DAG': '28/88'}
        dump(args.output / 'EXTRACTION_RECEIPT.json', receipt)
        print(json.dumps(receipt, separators=(',', ':')))
    except BaseException as error:
        dump(args.output / 'EXTRACTION_FAILURE.json',
             {'error': repr(error), 'CPU_s': time.process_time() - cpu,
              'wall_s': time.monotonic() - begin, 'no_automatic_retry': True})
        raise


if __name__ == '__main__':
    main()
