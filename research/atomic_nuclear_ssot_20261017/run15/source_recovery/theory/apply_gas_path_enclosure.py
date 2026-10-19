"""Apply a measured continuous-interpolant density deviation to the old envelope."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

from subh_survivor_enclosure import PrescribedRun13
import subh_survivor_enclosure


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gas-comparison', type=Path, required=True)
    ap.add_argument('--run13-root', type=Path, required=True)
    ap.add_argument('--panels', type=int, default=128)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    start = time.perf_counter()
    comparison = json.loads(args.gas_comparison.read_bytes())
    if comparison['status'] != 'NUMERICALLY_CHECKED_CONDITIONAL_CONTINUOUS_INTERPOLANT_BOUND':
        raise ValueError('measured conditional continuous-interpolant comparison required')
    if (comparison['new_IVP_runs'] != 0 or comparison['new_path']['validation']['status'] != 'COMPLETE'
            or comparison['new_path']['validation']['new_event_intervals_this_command'] != 0):
        raise ValueError('completed read-only trajectory validation required')
    model = PrescribedRun13(args.run13_root)
    for relative, expected in comparison['old_path']['input_identities'].items():
        if model.identities.get(relative) != expected:
            raise ValueError('original envelope gas path/source identity differs: ' + relative)
    for relative, expected in comparison['new_path']['input_identities'].items():
        if sha(Path(comparison['new_path']['root']) / relative) != expected:
            raise ValueError('completed new gas input changed: ' + relative)
    epsilon = comparison['comparison']['epsilon_abs_relative_upper']
    result = model.total_enclosure(args.panels, neutral_relative_uncertainty=epsilon)
    receipt = {
        'schema': 'rei.run15.transferred_prescribed_gas_enclosure.v1',
        'status': 'NUMERICALLY_CHECKED_CONDITIONAL_ENCLOSURE_FOR_DEFINED_NEW_PCHIP_PATH',
        'gas_comparison_sha256': sha(args.gas_comparison),
        'script_sha256': sha(Path(__file__)),
        'enclosure_script_sha256': sha(Path(subh_survivor_enclosure.__file__)),
        'command': [sys.executable, *sys.argv], 'cwd': str(Path.cwd()),
        'measured_interpolant_epsilon': epsilon, 'result': result,
        'source_normalization': 'original m2 first-cell marginal, finite 160 births and exact native GL8 reflection pairs',
        'new_path': comparison['new_path']['root'],
        'conditional_derivation': 'Since |n_new_PCHIP/n_old_PCHIP-1|<=epsilon, replace old H-opacity lower/upper bounds by factors (1-epsilon)/(1+epsilon). Positive tails remain covered by H-only upper survival.',
        'new_IVP_runs': 0, 'directed_rounding_certificate': False,
        'actual_ODE_path_between_boundaries': 'NOT_ESTABLISHED',
        'continuous_source_nonlinear_gas_feedback': 'NOT_ESTABLISHED',
        'wall_s': time.perf_counter() - start,
    }
    with args.output.open('x') as handle:
        handle.write(json.dumps(receipt, indent=2, allow_nan=False) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
