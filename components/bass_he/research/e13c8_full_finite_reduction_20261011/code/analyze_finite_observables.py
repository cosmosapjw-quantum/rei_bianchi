#!/usr/bin/env python3
"""Exact derived observables and ledger closure from the saved full OFF reduction."""
import argparse
import csv
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import time


def box(x):
    a, b = F(x['lo']), F(x['hi'])
    if a > b:
        raise ValueError('inverted interval')
    return a, b


def add(*xs):
    return tuple(sum((x[i] for x in xs), F(0)) for i in (0, 1))


def neg(x):
    return -x[1], -x[0]


def scale(x, k):
    if k < 0:
        raise ValueError('positive scale required')
    return x[0] * k, x[1] * k


def divide_positive(a, b):
    if a[0] < 0 or b[0] <= 0:
        raise ValueError('positive numerator and denominator required')
    return a[0] / b[1], a[1] / b[0]


def display(x):
    with localcontext() as c:
        c.prec = 24
        return str(Decimal(x.numerator) / Decimal(x.denominator))


def report(x):
    midpoint = (x[0] + x[1]) / 2
    width = x[1] - x[0]
    return {'lo': str(x[0]), 'hi': str(x[1]), 'width': str(width),
            'lo_display': display(x[0]), 'hi_display': display(x[1]),
            'midpoint_display': display(midpoint), 'width_display': display(width),
            'relative_full_width_display': display(width / abs(midpoint)) if midpoint else None,
            'relative_half_width_display': display(width / (2 * abs(midpoint))) if midpoint else None}


def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reduction', type=Path, required=True)
    ap.add_argument('--segments', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    started = time.monotonic()
    j = json.loads(a.reduction.read_bytes())
    if j['status'] != 'PASS_MECHANICAL_PENDING_INDEPENDENT_REVIEW':
        raise ValueError('full raw reduction gate required')
    if sha(a.segments) != '2a43dae808a0ca262dd175d2a1b74eeecc2c674d537f524bdba08e9d709076f7':
        raise ValueError('captured source identity mismatch')
    m = {k: box(v) for k, v in j['full_raw_candidate']['absolute'].items()}
    corr = {k: box(v) for k, v in j['full_raw_candidate']['correction'].items()}
    last = {}
    first = {}
    with a.segments.open(newline='') as f:
        for row in csv.DictReader(f):
            node = int(row['node'])
            key = int(row['step']), int(row['segment'])
            if row['mode'] != 'OFF':
                raise ValueError('unexpected mode')
            if node not in last or key > last[node][0]:
                last[node] = key, row
            if node not in first or key < first[node][0]:
                first[node] = key, row
    if set(last) != set(range(2440)) or any(float(x[1]['f0']) != 0 for x in first.values()):
        raise ValueError('fixed OFF/zero initial stock scope mismatch')
    lift = lambda x: F.from_float(float(x))
    eps = lift(1.602176634e-12)
    captured_energy = sum((lift(r['u']) * lift(r['weight']) / eps for _, r in last.values()), F(0))
    final_energy = add((captured_energy, captured_energy), corr['energy_eV'])
    chi = dict(zip(('HI', 'HeI', 'HeII'), map(lift, (13.598434599702, 24.587389011, 54.41776))))
    threshold = add(*(scale(m['A_' + sp], value) for sp, value in chi.items()))
    ledgers = {
        'number_P_plus_A_minus_QN': add(m['P_final'], m['A_total'], neg(m['QN'])),
        'energy_final_plus_B_plus_Z_minus_QE_minus_anchor': add(final_energy, m['B_total_eV'], m['Z_eV'], neg(m['QE_eV']), neg(m['anchor'])),
        'heat_H_minus_B_plus_threshold_energy': add(m['H_total_eV'], neg(m['B_total_eV']), threshold)
    }
    if any(not lo <= 0 <= hi for lo, hi in ledgers.values()):
        raise ValueError('whole finite ledger does not enclose zero')
    ratios = {
        'remaining_photons_per_injected_photon': divide_positive(m['P_final'], m['QN']),
        'absorptions_per_injected_photon': divide_positive(m['A_total'], m['QN']),
        'absorbed_energy_per_injected_energy': divide_positive(m['B_total_eV'], m['QE_eV']),
        'heat_per_injected_energy': divide_positive(m['H_total_eV'], m['QE_eV']),
        'threshold_energy_per_injected_energy': divide_positive(threshold, m['QE_eV'])
    }
    result = {
        'schema': 'bass-he-e13c8-finite-observable-analysis-v1',
        'status': 'PASS_EXACT_DERIVED_FINITE_ANALYSIS',
        'source_reduction_sha256': sha(a.reduction), 'source_segments_sha256': sha(a.segments),
        'scope': 'Same finite weighted OFF captured first-two-step conditional target; ratios are derived interval enclosures, not continuum efficiencies.',
        'observables': {k: report(v) for k, v in m.items()},
        'derived_final_energy_stock_eV': report(final_energy),
        'derived_threshold_energy_eV': report(threshold),
        'ledger_intervals': {k: {**report(v), 'contains_zero': True} for k, v in ledgers.items()},
        'ratios': {k: report(v) for k, v in ratios.items()},
        'method': 'Exact Fraction arithmetic. Captured final energy uses one binary64 lift of row u and weight, and one division by the exact binary64 lift of erg-per-eV; add the independently saved full correction interval. No numerical physics invocation.',
        'interval_intersection_used': False, 'kernel_invocations': 0,
        'full_width_is_not_physical_error': True,
        'elapsed_seconds': time.monotonic() - started
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with a.output.open('x') as f:
        json.dump(result, f, indent=2, sort_keys=True); f.write('\n')
    print(json.dumps({'status': result['status'], 'elapsed_seconds': result['elapsed_seconds'],
                      'ledger_checks': len(ledgers), 'kernel_invocations': 0}))


if __name__ == '__main__':
    main()
