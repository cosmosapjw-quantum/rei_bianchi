#!/usr/bin/env python3
"""Summarize preserved C6 stdout; never build or execute scientific code."""
import json
from pathlib import Path
import re
from statistics import median

UNIT = Path(__file__).resolve().parent
RAW = 'evidence/C6_rate_tests_and_timings.stdout'


def summarize():
    groups = {}
    for line in (UNIT / RAW).read_text().splitlines():
        match = re.search(r'(POINT_BENCH|BENCH) (\{.*\})', line)
        if not match:
            continue
        row = json.loads(match[2])
        key = (match[1], row.get('distribution', 'point'), row['n'], row['method'])
        groups.setdefault(key, []).append(row)
    assert len(groups) == 19
    results = []
    for (kind, distribution, count, method), rows in groups.items():
        rows.sort(key=lambda row: row['sample'])
        assert [row['sample'] for row in rows] == [0, 1, 2]
        samples = [row['seconds'] for row in rows]
        baseline = 'legacy_double_direct' if kind == 'POINT_BENCH' else 'direct'
        reference_rows = groups[(kind, distribution, count, baseline)]
        reference_median = median(row['seconds'] for row in reference_rows)
        value = median(samples)
        saving_per_query = (reference_median - value) / count
        results.append({
            'kind': kind, 'distribution': distribution, 'n': count, 'method': method,
            'samples_seconds': samples, 'median_seconds': value,
            'min_seconds': min(samples), 'max_seconds': max(samples),
            'baseline_method': baseline, 'ratio_of_medians': reference_median / value,
            'construction_break_even_queries': (0.109192622 / saving_per_query
                if method.startswith('table_') and saving_per_query > 0 else None),
            'checksums': [row['checksum'] for row in rows],
        })
    return {
        'schema': 'rei.rate_table.local_timing_summary.v1',
        'execution_status': 'REUSED_C6_NO_NEW_SCIENTIFIC_RUN',
        'raw_stdout': RAW, 'cohort': 'local Rust 1.85.1',
        'aggregation': 'Three sequential samples per group; median and full min/max; ratio of medians, no uncertainty claim.',
        'timing_sample_count': 57,
        'construction_seconds': 0.109192622,
        'construction_source': 'evidence/R7_RESULTS.json selected 65537-node prototype; reused cost, not a new C6 construction measurement.',
        'construction_break_even_rule': 'C/(median_direct/n-median_method/n); null if no positive saving; indicative cross-probe amortization only.',
        'grid_payload_bytes': 8913016, 'total_table_payload_bytes': 9109624,
        'process_max_rss_kib': 18724,
        'rss_source': 'evidence/C6_rate_tests_and_timings.resources.json; process peak, not incremental table memory.',
        'results': results,
        'claim_ceiling': 'Coefficient and point-RHS microbenchmarks only; no SIMD, driver, trajectory, NCP64 or universal speedup claim.',
    }


if __name__ == '__main__':
    (UNIT / 'coding_evidence/C8_LOCAL_TIMINGS.json').write_text(
        json.dumps(summarize(), indent=2) + '\n')
    # Upstream stdout prints Rust Option as Some(x); decode only that known field.
    groups = {}
    for replicate in range(1, 4):
        raw = f'evidence/intake/upstream_pr178/C9_RUN{replicate}.stdout'
        for line in (UNIT / raw).read_text().splitlines():
            if not line.startswith('C9_FAIR_BENCH '):
                continue
            row = json.loads(re.sub(r'Some\(([^()]*)\)', r'\1', line.split(' ', 1)[1]))
            row.update(replicate=replicate, raw_stdout=raw)
            groups.setdefault((row['distribution'], row['N']), []).append(row)
    assert len(groups) == 4
    results = []
    for (distribution, count), rows in groups.items():
        assert [row['replicate'] for row in rows] == [1, 2, 3]
        result = {'distribution': distribution, 'n': count, 'workers': 4, 'replicates': rows}
        for field in ('direct4_median_s', 'table4_median_s', 'ratio', 'build_s', 'break_even'):
            values = [row[field] for row in rows]
            result[field] = {'median': median(values), 'min': min(values), 'max': max(values)}
        results.append(result)
    (UNIT / 'coding_evidence/C8_UPSTREAM_FAIR_TIMINGS.json').write_text(json.dumps({
        'schema': 'rei.rate_table.upstream_fair_timing_summary.v1',
        'execution_status': 'ADOPTED_EXISTING_EXECUTION_NO_LOCAL_REPLAY',
        'cohort': 'upstream PR178 Rust 1.94.1',
        'immutable_ref': '1579a5e4b0c3093bfd6942cc4914e29a00a71978',
        'aggregation': 'Median/min/max across three preserved run-level medians; inner timing samples are not exposed by these logs. No pooling with local Rust 1.85.1 or PR177.',
        'comparator': 'direct_parallel4 vs table_parallel4',
        'results': results,
    }, indent=2) + '\n')
