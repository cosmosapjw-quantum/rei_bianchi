#!/usr/bin/env python3
"""Independent saved CSV transport/ranking validation, no raw path reread."""
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as F
import csv
import gzip
import hashlib
import json
from pathlib import Path
import time

BASE = Path('/workspace/scratch/7fd51143e473/BASS_HE_E13C5_FULL_FINITE_BUDGET_20261011_v1')
HERE = BASE / 'evidence/independent_review'
SOURCE = BASE / 'evidence/budget_control/EXEC01/WIDTH_RANKINGS.csv.gz'
MODES = ('OFF', 'KF', 'GM')
MOMENTS = ('Z_eV', 'QN', 'QE_eV') + tuple(p + '_' + s + ('' if p == 'A' else '_eV') for s in ('HI', 'HeI', 'HeII') for p in ('A', 'B', 'H'))
TOTALS = ('A_total', 'B_total_eV', 'H_total_eV')
KINDS = {'absolute': ('P_final', 'anchor') + MOMENTS + TOTALS, 'correction': ('P_final', 'energy_eV') + MOMENTS + TOTALS}
EXPECTED_GROUPS = [(m, kind, metric) for m in MODES for kind, metrics in KINDS.items() for metric in metrics]
COUNTS = Counter()
FAILURES = []

def check(kind, good, detail=None):
    COUNTS[kind] += 1
    if not good:
        FAILURES.append({'category': kind, 'detail': detail})

def main():
    begin = time.monotonic()
    oracle = json.loads((HERE / 'INDEPENDENT_ARITHMETIC.json').read_text())
    digest = hashlib.sha256()
    bytes_count = 0
    row_count = 0
    group_index = 0
    records = []

    def validate_group(key, records):
        mode, kind, metric = key
        name = kind + '/' + metric
        check('group_length', len(records) == 2440, key)
        check('group_node_coverage', [r[0] for r in records] == list(range(2440)), key)
        for ri, wi, variant in ((1, 3, 'original'), (2, 4, 'hybrid')):
            ordered = sorted(records, key=lambda r: r[ri])
            check('rank_permutation', [r[ri] for r in ordered] == list(range(1, 2441)), [*key, variant])
            check('nonnegative_widths', all(r[wi] >= 0 for r in ordered), [*key, variant])
            check('sorted_width_with_node_tiebreak', all((-a[wi], a[0]) <= (-b[wi], b[0]) for a, b in zip(ordered, ordered[1:])), [*key, variant])
            expected_width = F(oracle['diagnostics'][mode][name][variant + '_width' if variant == 'original' else 'hybrid_width'])
            check('whole_width_sum_matches_independent_raw', sum((r[wi] for r in ordered), F(0)) == expected_width, [*key, variant])
            independent_top = oracle['rankings'][mode][name][variant]
            for i, r in enumerate(ordered[:100]):
                check('top100_raw_node_and_width', r[0] == independent_top['top_nodes'][i] and r[wi] == F(independent_top['top_widths'][i]), [*key, variant, i + 1])

    with gzip.open(SOURCE, 'rb') as stream:
        first = stream.readline()
        digest.update(first)
        bytes_count += len(first)
        header = next(csv.reader([first.decode('utf-8')]))
        check('header', header == ['mode', 'kind', 'quantity', 'node', 'rank_old', 'rank_hybrid', 'old_width_exact', 'hybrid_width_exact', 'selected_S4', 'replacement_K2'])
        for line in stream:
            digest.update(line)
            bytes_count += len(line)
            row = next(csv.reader([line.decode('utf-8')]))
            if len(row) != 10:
                raise ValueError('INVALID_ROW_COLUMNS')
            mode, kind, metric = row[:3]
            key = (mode, kind, metric)
            n = int(row[3])
            check('exact_row_order', group_index < len(EXPECTED_GROUPS) and key == EXPECTED_GROUPS[group_index] and n == len(records), [*key, n])
            check('partition_membership', int(row[8]) == int(n in (0, 700, 1620, 2344)) and int(row[9]) == int(mode == 'OFF' and n in (0, 700)), [*key, n])
            records.append((n, int(row[4]), int(row[5]), F(row[6]), F(row[7])))
            row_count += 1
            if len(records) == 2440:
                validate_group(key, records)
                group_index += 1
                records = []
    check('complete_group_count', group_index == 102 and not records, group_index)
    check('complete_row_count', row_count == 248880, row_count)
    result = {'schema': 'independent-ranking-csv-review-v1', 'created_utc': datetime.now(timezone.utc).isoformat(), 'status': 'PASS' if not FAILURES else 'FAIL', 'check_count': sum(COUNTS.values()), 'check_counts': dict(COUNTS), 'failed_count': len(FAILURES), 'failures': FAILURES, 'rows': row_count, 'groups': group_index, 'decompressed_CSV': {'bytes': bytes_count, 'sha256': digest.hexdigest()}, 'gzip_file': {'bytes': SOURCE.stat().st_size, 'sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest()}, 'elapsed_seconds': time.monotonic() - begin, 'physical_executions': 0, 'additional_raw_PATHS_passes': 0}
    with (HERE / 'RANKING_CSV_REVIEW.json').open('x') as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps({k: result[k] for k in ('status', 'check_count', 'failed_count', 'decompressed_CSV', 'elapsed_seconds')}))

if __name__ == '__main__':
    main()
