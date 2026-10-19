#!/usr/bin/env python3
"""Pointwise two-block comparison scales from actually evaluated native states.

This does not turn three Jacobians into a tube bound or a trajectory estimate.
It reports the characteristic rate of each frozen nonnegative comparison block.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        p.error('output already exists')
    raw = a.input.read_bytes()
    data = json.loads(raw)
    if data['schema'] != 'rei.run16.recorded-state-feedback.v1' or data['native_ivp_solves'] != 0:
        raise ValueError('recorded-state diagnostic required')
    rows = []
    for r in data['records']:
        mu = r['fixed_depth_gas_block']['inf_logarithmic_norm']
        b = r['depth_coupling']['B_inf_norm']
        c = r['depth_coupling']['C_inf_norm']
        if not all(math.isfinite(x) for x in (mu, b, c)) or min(b, c) < 0:
            raise ValueError('finite matrix measure and nonnegative block norms required')
        lam = (mu+math.sqrt(mu*mu+4*b*c))/2
        independent = max(np.linalg.eigvals(np.array([[mu, b], [c, 0.]]))).real
        gap = abs(lam-independent)
        if gap > 1e-14*max(1., abs(lam)):
            raise AssertionError('comparison eigenvalue identity failed')
        beta = lam/c if c > 0 else None
        rows.append({'z': r['z'], 'event_side': r['event_side'],
            'gas_matrix_measure_per_z': mu, 'depth_to_gas_norm_per_z': b,
            'gas_to_depth_norm_per_z': c, 'frozen_comparison_eigenvalue_per_z': lam,
            'point_optimal_depth_weight': beta, 'eigenvalue_identity_abs_gap': float(gap),
            'unweighted_gas_matrix_induced_inf_norm_per_z': r['gas_jacobian']['induced_inf_norm']})
    result = {'schema': 'rei.run16.frozen-point-block-comparison.v1',
        'status': 'DERIVED_AND_NUMERICALLY_CHECKED_POINT_SCALES', 'records': rows,
        'input_sha256': hashlib.sha256(raw).hexdigest(),
        'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'command': [sys.executable, *sys.argv], 'native_rhs_calls': 0,
        'conditions_for_a_trajectory_bound': [
            'continuous full-state reconstruction and residual bounds including source events',
            'matrix measure and B,C norm enclosures throughout an admissible tube',
            'one fixed compatible norm or explicit derivative of a time-dependent scaling',
            'separate continuous-source quadrature forcing defect'],
        'scope': 'No global stability constant, nonlinear contraction or continuum error bound is inferred from point data.'}
    with a.output.open('x') as f:
        json.dump(result, f, indent=2, allow_nan=False)
        f.write('\n')
    print(json.dumps({'output': str(a.output), 'records': rows}))


if __name__ == '__main__':
    main()
