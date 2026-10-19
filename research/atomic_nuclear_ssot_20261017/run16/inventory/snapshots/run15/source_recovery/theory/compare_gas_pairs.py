"""Compare validated complete RUN15 gas PCHIP pairs without an old18 baseline.

No IVP is run. The shared compare_interpolants function and frozen driver's
read-only validate action retain their existing numerical and physical scope.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
import time

from compare_gas_paths import load_new_path, compare_interpolants
import compare_gas_paths
import numpy as np
import scipy
from scipy.interpolate import PchipInterpolator


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--run15-root', type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument('--source-root', type=Path)
    ap.add_argument('--native-binary', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    started = time.perf_counter()
    run15 = args.run15_root.resolve()
    source = args.source_root or run15.parent/'run13/recovered'
    paths, identities = {}, {}
    common_metadata = None
    for label, packet_name in [('optical_n6_standard', 'optical_n6.json'),
                               ('optical_n8_standard', 'optical_n8.json'),
                               ('optical_n8_tight', 'optical_n8.json')]:
        z, y, provenance, _, _ = load_new_path(
            run15/'outputs'/label, run15/'scripts/run_joint.py', source_root=source,
            packet=run15/'inputs'/packet_name, native_binary=args.native_binary)
        packet = json.loads((run15/'inputs'/packet_name).read_bytes())
        metadata = {k: v for k, v in packet.items() if k != 'cohorts'}
        if common_metadata is None:
            common_metadata = metadata
        elif common_metadata != metadata:
            raise ValueError('gas paths do not share unchanged physical/source metadata')
        paths[label] = PchipInterpolator(z, y, extrapolate=False)
        identities[label] = provenance
    if (identities['optical_n8_standard']['packet_sha256'] != identities['optical_n8_tight']['packet_sha256']
            or not np.array_equal(paths['optical_n8_standard'].x, paths['optical_n8_tight'].x)):
        raise ValueError('n8 ODE-profile comparison requires the same packet and event grid')
    comparisons = []
    for denominator, numerator, interpretation in [
        ('optical_n6_standard', 'optical_n8_standard',
         'Finite spectral support order comparison between separately defined event-boundary PCHIPs; includes interpolation and finite ODE effects.'),
        ('optical_n8_standard', 'optical_n8_tight',
         'Same packet and event grid, two original ODE profiles; a finite interpolant comparison, not an exact solution error bound.')]:
        result = compare_interpolants(paths[denominator], paths[numerator])
        comparisons.append({'denominator_case': denominator, 'numerator_case': numerator,
                            'interpretation': interpretation, 'comparison': result})
    receipt = {'schema': 'rei.run15.direct_complete_gas_path_pairs.v1',
               'status': 'NUMERICALLY_CHECKED_CONDITIONAL_CONTINUOUS_INTERPOLANT_COMPARISONS',
               'command': [sys.executable, *sys.argv], 'cwd': str(Path.cwd()),
               'script_sha256': sha(Path(__file__)),
               'comparison_script_sha256': sha(Path(compare_gas_paths.__file__)),
               'environment': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__},
               'input_paths': identities, 'pairs': comparisons,
               'physical_source_metadata_equal': True,
               'n8_standard_tight_packet_and_event_grid_equal': True,
               'old_18_knot_path_used': False, 'new_IVP_runs': 0,
               'limits': ['Each epsilon bounds two specified interpolants using binary64 padded analytic polynomial extrema.',
                          'Near-identical paths can be dominated by the explicit cancellation floor.',
                          'No directed-rounding certificate, actual ODE between-boundary enclosure, or continuous-source feedback error bound.'],
               'wall_s': time.perf_counter() - started}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as handle:
        handle.write(json.dumps(receipt, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'output': str(args.output), 'pairs': [
        {'denominator': row['denominator_case'], 'numerator': row['numerator_case'],
         'epsilon': row['comparison']['epsilon_abs_relative_upper'],
         'observed_knot_maximum': row['comparison']['common_knot_checks']['maximum_relative_difference']}
        for row in comparisons], 'new_IVP_runs': 0, 'wall_s': receipt['wall_s']}))


if __name__ == '__main__':
    main()
