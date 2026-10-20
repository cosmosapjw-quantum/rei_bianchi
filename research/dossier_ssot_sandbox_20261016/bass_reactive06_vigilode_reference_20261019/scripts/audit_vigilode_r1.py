#!/usr/bin/env python3
"""Fresh recovery audit of scalar VigilODE intervals at binary64 input points.

This is a newly reconstructed independent Decimal auditor, not restored bytes
of the pre-interruption auditor. Non-successful upstream outputs are retained
as refusals; they are never counted as enclosures or silently discarded.
"""
from __future__ import annotations
import argparse
import csv
import datetime
from decimal import Decimal, localcontext
import json
from pathlib import Path
import platform
import time
from decimal_oracles_r1 import j_jk, point, sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', type=Path, required=True)
    ap.add_argument('--adapter', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    source_rows = list(csv.DictReader(args.csv.open()))
    checks, refusals, counts = [], [], {}
    with localcontext() as ctx:
        ctx.prec = 110
        ctx.Emin = -999999999999999999
        ctx.Emax = 999999999999999999
        for row in source_rows:
            kind = row['kind']
            counts.setdefault(kind, {'rows': 0, 'enclosed': 0, 'refused': 0,
                                     'max_relative_width': Decimal(0)})
            counts[kind]['rows'] += 1
            if row['status'] != 'ok':
                refusals.append(row)
                counts[kind]['refused'] += 1
                continue
            tau, lo, hi = map(point, (row['tau'], row['lo'], row['hi']))
            j, k = int(row['j']), int(row['k'])
            exact = j_jk(tau, j, k)
            enclosed = 0 <= lo <= exact <= hi
            width = hi - lo
            relwidth = width / exact
            counts[kind]['enclosed'] += int(enclosed)
            counts[kind]['max_relative_width'] = max(counts[kind]['max_relative_width'], relwidth)
            checks.append({'kind': kind, 'tau_token': row['tau'], 'j': j, 'k': k,
                           'tau_exact_binary64': str(tau), 'reference_decimal110': str(exact),
                           'lo_exact_binary64': str(lo), 'hi_exact_binary64': str(hi),
                           'enclosed': enclosed, 'relative_width': str(relwidth)})
        for summary in counts.values():
            summary['max_relative_width'] = str(summary['max_relative_width'])
    failures = [row for row in checks if not row['enclosed']]
    expected_shape = len(source_rows) == 252 and counts.get('dyadic', {}).get('rows') == 126
    dyadic_complete = counts.get('dyadic', {}).get('enclosed') == 126 and counts['dyadic']['refused'] == 0
    receipt = {
        'version': 'BR06_THEORY_RECOVERY_R1',
        'status': 'PASS_FRESH_EXECUTION_SUCCESSFUL_INTERVALS' if not failures and expected_shape and dyadic_complete else 'FAIL',
        'historical_pass_inherited': False,
        'scope': 'Decimal110 containment of scalar moments only; no variable-geometry or whole-history enclosure is inferred',
        'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'python': platform.python_version(), 'precision_decimal_digits': 110,
        'source_sha256': sha(__file__), 'decimal_module_sha256': sha(Path(__file__).with_name('decimal_oracles_r1.py')),
        'input_csv': str(args.csv), 'input_csv_sha256': sha(args.csv),
        'adapter': str(args.adapter), 'adapter_sha256': sha(args.adapter),
        'input_rows': len(source_rows), 'counts': counts,
        'unsuccessful_rows_retained': refusals, 'failures': failures, 'checks': checks,
        'wall_s': time.perf_counter() - start,
        'code_boundary_review': {
            'reviewer': 'br06_theory; independent of R1 adapter author vigilode_review',
            'dyadic_formula': 'Checked two substitutions x=y/2 and x=(1+y)/2. Powers give exactly 2^(-j-k-1); the first sum expands (1+(1-y))^k and the second expands (1+y)^j. Both sums use old moments, all coefficients are nonnegative, and no interval of birth age is discarded.',
            'chronological_source': 'With u=1-x, j(u)=left*x+right*(1-x); code uses left*J10+right*J01 and leaves physical dt outside.',
            'width_gate': 'Code forms width with sub_up and tolerance with mul_down/add_down using nonnegative lower endpoint. Thus admitted width is no larger than abs_tol+rel_tol*the enclosed true nonnegative moment. Actual directed primitive correctness is an upstream obligation; Decimal checks are independent finite numerical evidence.',
            'positivity_intersection': 'Intersecting an interval enclosure with [0,infinity) preserves enclosure because the exact integral is nonnegative. Entirely negative intervals are refused.',
            'input_domain': 'Finite nonnegative tau and tolerances are checked. j,k are limited to <=2. Halving large finite tau by exactly representable powers of two gives a small argument; no large-tau cutoff or cohort replacement occurs.',
            'limitation': 'A successful direct core interval can be extremely wide. Containment alone does not meet an accuracy tolerance. Only dyadic outputs go through the adapter width gate.'
        }
    }
    out = args.output / 'VIGILODE_DECIMAL_RECOVERY_R1.json'
    out.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: receipt[k] for k in ('status', 'input_rows', 'counts', 'wall_s')} | {'output': str(out), 'sha256': sha(out)}))
    if receipt['status'] == 'FAIL':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
