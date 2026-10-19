#!/usr/bin/env python3
"""Reconstructed R1 physical/source/clock and fixed-node comparators.

No historical reported answer is an input. The constant-opacity comparator is
defined by the archived binary64 tau rule, while continuous source ratios and
the variable-opacity reference use the independently reconstructed geometry.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import datetime
from decimal import Decimal, localcontext
import json
from pathlib import Path
import platform
import time
import numpy as np
from decimal_oracles_r1 import phi, point
from independent_birth_reference import Fixture, first_step, gauss, sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--parent', type=Path, required=True)
    ap.add_argument('--reference', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    f = Fixture(args.parent)
    rules = {int(r['rule_id']): r for r in f.rules}
    grouped = defaultdict(list)
    for r in f.templates:
        grouped[int(r['rule_id'])].append(r['midpoint_rate_com3_s'])
    births = first_step(f.files['BIRTHS'])
    birth_groups = defaultdict(list)
    for r in births:
        birth_groups[(int(r['rule_id']), r['actual_birth_time_s'], r['target_age_x'])].append(r['born_count_com3'])
    with localcontext() as ctx:
        ctx.prec = 90
        dt = point(f.dt)
        rates = {k: sum(map(point, v), Decimal(0)) for k, v in grouped.items()}
        tau = {k: point(r['tau']) for k, r in rules.items()}
        C0 = sum((rates[k] * dt * phi(tau[k]) for k in rates), Decimal(0))
        c1_actual, c1_target = Decimal(0), Decimal(0)
        for (key, t, age), values in birth_groups.items():
            mass = sum(map(point, values), Decimal(0))
            exact_age = (dt - point(t)) / dt
            c1_actual += mass * (-tau[key] * exact_age).exp()
            c1_target += mass * (-tau[key] * point(age)).exp()
        continuous = []
        frozen_gl = []
        for n in (64, 128):
            q, w = gauss(n)
            ratio = f.source_ratio(q)
            value = sum(float(rates[k]) * f.dt * float(np.sum(w * ratio * np.exp(-float(tau[k]) * (1-q)))) for k in rates)
            continuous.append({'degree': n, 'N_com3': value})
        for n in (2, 4, 8, 16, 32, 64):
            q, w = gauss(n)
            value = sum(float(rates[k]) * f.dt * float(np.sum(w * np.exp(-float(tau[k]) * (1-q)))) for k in rates)
            frozen_gl.append({'degree': n, 'N_com3': value, 'relative_bias_vs_C0': float((point(value)-C0)/C0)})
        ref = json.loads(args.reference.read_text())
        c2 = point(ref['executions'][-1]['result']['survival'])
        c1 = point(continuous[-1]['N_com3'])
        data = {
            'constant_midpoint_source_opacity_C0_decimal90': str(C0),
            'actual_source_constant_opacity_C1_continuous': continuous,
            'actual_source_constant_opacity_C1_matched_exact_clock_decimal90': str(c1_actual),
            'same_birth_weights_target_age_C1_decimal90': str(c1_target),
            'actual_source_variable_opacity_C2': float(c2),
            'C1_source_shift_relative': float((c1-C0)/C0),
            'C2_physical_transport_shift_relative': float((c2-c1)/c1),
            'matched_birth_vs_continuous_C1_relative': float((c1_actual-c1)/c1),
            'clock_intervention_relative': float((c1_actual-c1_target)/c1_target),
            'C1_continuous_64_to_128_relative': (continuous[0]['N_com3']-continuous[-1]['N_com3'])/continuous[-1]['N_com3'],
            'fixed_gauss_birth_comparator': frozen_gl,
            'tau_range': [float(min(tau.values())), float(max(tau.values()))],
            'end_volume_over_anchor_minus_one': float(f.geometry.at(np.array([1.]))[2][0]/f.anchor-1),
            'birth_rows': len(births), 'unique_clock_groups': len(birth_groups),
        }
    receipt = {
        'version': 'BR06_THEORY_RECOVERY_R1', 'status': 'COMPLETED_FRESH_RECOVERY_EXECUTION',
        'historical_pass_inherited': False,
        'scope': 'Actual BR05 step1 spectral/gas fixture. C0/C1/C2 are different physical comparators, not three discretizations of one problem. Fixed GL bias is not the BR02 frozen table rerun.',
        'definition': 'All stored decimal input tokens are parsed to binary64, then lifted exactly with Decimal.from_float. C0 uses stored rule tau and exact sum of midpoint source label rates. Matched actual age is computed in Decimal from exact binary64 dt and actual_birth_time_s; target age is the exact binary64 target_age_x. Opacity remains fixed in C1. Source weights are held identical in the clock intervention.',
        'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'python': platform.python_version(),
        'source_sha256': sha(__file__), 'decimal_module_sha256': sha(Path(__file__).with_name('decimal_oracles_r1.py')),
        'independent_module_sha256': sha(Path(__file__).with_name('independent_birth_reference.py')),
        'inputs': {str(p): sha(p) for p in f.files.values()},
        'variable_reference': str(args.reference), 'variable_reference_sha256': sha(args.reference),
        'results': data, 'wall_s': time.perf_counter()-start,
        'interpretation': {
            'H1_clock_or_path_dominance': 'The actual clock intervention is evaluated directly. The ~80 ppm C1/C0 and C2/C1 shifts describe actual source time dependence and physical geometry/comoving dilution; they must not be called native path errors.',
            'cohort_age': 'Exact frozen survivor mass does not imply exact age moments when fitted weights/nodes depend on tau.',
            'precision_scope': 'Decimal90 eliminates rounded-input ambiguity in scalar and matched-clock comparisons. SciPy Gaussian refinement provides empirical convergence for continuous source dependence; this receipt is not an interval proof.'
        }
    }
    out=args.output/'SOURCE_COMPARATORS_RECOVERY_R1.json'
    out.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'output':str(out),'sha256':sha(out),'wall_s':receipt['wall_s'],'results':data}))


if __name__=='__main__':
    main()
