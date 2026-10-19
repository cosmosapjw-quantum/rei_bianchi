"""Read-only comparison of COMPLETE RUN15 and RUN13 PCHIP neutral-H paths.

The exact-arithmetic inequality uses the union of interpolation knots, analytic
cubic extrema for the difference and a positive lower bound for the old path.
Binary64 evaluation uses explicit padding and a cancellation floor; it is not a
directed-rounding certificate. Neither interpolant is an enclosure of the true
IVP between its recorded points. No native RHS or solve_ivp call is made here.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

for _key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_key] = '1'
sys.dont_write_bytecode = True
import numpy as np
import scipy
from scipy.interpolate import PchipInterpolator

FROZEN_DRIVER_SHA256 = 'c175eaf604c52fcbe0b84831e34750d6c7edaa0827c99f69e94e5794d0d1c3f7'
RELATIVE_PADDING = 2e-11
CANCELLATION_FLOOR_ULPS = 256.0
MACHINE_EPSILON = np.finfo(float).eps


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checked_bytes(root: Path, name: str, expected: str | None = None) -> bytes:
    if Path(name).name != name:
        raise ValueError('ordinary local filename required')
    path = root / name
    if path.is_symlink() or not path.is_file():
        raise ValueError('missing or unsafe input: ' + name)
    raw = path.read_bytes()
    if expected is not None and sha_bytes(raw) != expected:
        raise ValueError('input hash mismatch: ' + name)
    return raw


def gas_chunk(root: Path, record: dict) -> tuple[np.ndarray, np.ndarray]:
    raw = checked_bytes(root, record['gas_file'], record['gas_sha256'])
    with np.load(io.BytesIO(raw), allow_pickle=False) as data:
        if set(data.files) != {'z', 'gas'}:
            raise ValueError('unexpected gas chunk arrays')
        z, gas = data['z'].copy(), data['gas'].copy()
    if (z.ndim != 1 or gas.shape != (len(z), 14) or len(z) < 1
            or not np.isfinite(z).all() or not np.isfinite(gas).all()
            or np.any(np.diff(z) <= 0) or np.any(gas[:, 1] <= 0)):
        raise ValueError('invalid neutral-H gas chunk')
    return z, gas[:, 1]


def load_new_path(out: Path, driver: Path, *, source_root: Path | None = None,
                  packet: Path | None = None, native_binary: Path | None = None
                  ) -> tuple[np.ndarray, np.ndarray, dict, Path, Path]:
    """Require final immutable marker and invoke only the frozen driver's validate."""
    out = out.resolve()
    marker_bytes = checked_bytes(out, 'checkpoint.json')
    marker = json.loads(marker_bytes)
    if marker.get('status') != 'COMPLETE' or marker.get('next_segment') != marker.get('total_segments'):
        raise ValueError('COMPLETE trajectory required; IN_PROGRESS is not a gas path result')
    identity_bytes = checked_bytes(out, 'RUN_IDENTITY.json', marker['run_identity_sha256'])
    identity = json.loads(identity_bytes)
    driver_raw = driver.read_bytes()
    if sha_bytes(driver_raw) != FROZEN_DRIVER_SHA256 or identity['locked_inputs']['driver_sha256'] != FROZEN_DRIVER_SHA256:
        raise ValueError('frozen native driver identity differs')
    locations = identity['input_locations']
    # Relocation changes filesystem locations only. The unchanged frozen
    # validator checks the same locked source, packet, binary and runtime bytes.
    source = Path(source_root if source_root is not None else locations['source_root']).resolve()
    packet_path = Path(packet if packet is not None else locations['packet']).resolve()
    binary_path = Path(native_binary if native_binary is not None else locations['native_binary']).resolve()
    command = [sys.executable, str(driver.resolve()), 'validate', '--packet', str(packet_path),
               '--native-binary', str(binary_path), '--out', str(out),
               '--source-root', str(source), '--rtol', str(marker['rtol'])]
    process = subprocess.run(command, capture_output=True, text=True, timeout=120, check=False)
    if process.returncode:
        raise ValueError('frozen run_joint validation failed: ' + process.stderr[-1200:])
    validation = json.loads(process.stdout.splitlines()[-1])
    if validation['status'] != 'COMPLETE' or validation['new_event_intervals_this_command'] != 0:
        raise ValueError('frozen validate did not confirm a read-only COMPLETE endpoint')
    if checked_bytes(out, 'checkpoint.json') != marker_bytes or checked_bytes(out, 'RUN_IDENTITY.json') != identity_bytes:
        raise ValueError('complete input markers changed during validation')
    zparts, yparts = [], []
    cursor = 0
    records = [marker['initial'], *marker['chunks']]
    identities = {'RUN_IDENTITY.json': sha_bytes(identity_bytes), 'checkpoint.json': sha_bytes(marker_bytes)}
    for index, record in enumerate(records):
        z, y = gas_chunk(out, record)
        identities[record['gas_file']] = record['gas_sha256']
        if index == 0:
            if z.tolist() != [0.0]:
                raise ValueError('gas history does not start at original IC')
            zparts.append(z)
            yparts.append(y)
        else:
            if (record['start_segment'] != cursor or record['end_segment'] - cursor != len(z) - 1
                    or z[0] != zparts[-1][-1] or y[0] != yparts[-1][-1]):
                raise ValueError('gas chunk coverage/boundary mismatch')
            cursor = record['end_segment']
            zparts.append(z[1:])
            yparts.append(y[1:])
    z, y = np.concatenate(zparts), np.concatenate(yparts)
    if (cursor != marker['total_segments'] or len(z) != marker['gas_event_points']
            or z[-1] != 1.0 or np.any(np.diff(z) <= 0)):
        raise ValueError('complete gas path coverage mismatch')
    if checked_bytes(out, 'checkpoint.json') != marker_bytes:
        raise ValueError('complete marker changed during gas read')
    provenance = {'root': str(out), 'validation_command': command, 'validation': validation,
                  'driver_sha256': FROZEN_DRIVER_SHA256,
                  'recorded_input_locations': locations,
                  'resolved_input_locations': {'source_root': str(source), 'packet': str(packet_path),
                                               'native_binary': str(binary_path)},
                  'input_identities': identities, 'packet_sha256': identity['locked_inputs']['packet_sha256'],
                  'native_binary_sha256': identity['locked_inputs']['native_binary_sha256'],
                  'event_points': len(z), 'interpolant': 'scipy.PchipInterpolator(z, native_scaled_Y_HI, extrapolate=False)'}
    return z, y, provenance, source, packet_path


def load_old_path(source: Path, new_packet_path: Path) -> tuple[np.ndarray, np.ndarray, dict]:
    sys.path.insert(0, str(source / 'scripts'))
    from spectral_joint11 import SpectralModel, coalesce_reflections
    packet_path = source / 'inputs/spectral11/m2.json'
    packet_raw = packet_path.read_bytes()
    packet = json.loads(packet_raw)
    new_packet = json.loads(new_packet_path.read_bytes())
    if ({k: v for k, v in packet.items() if k != 'cohorts'}
            != {k: v for k, v in new_packet.items() if k != 'cohorts'}):
        raise ValueError('native physical/source metadata changed')
    model = SpectralModel(coalesce_reflections(packet))
    root = source / 'evidence/joint11_sided_m2_3e-11'
    raw = checked_bytes(root, 'checkpoint.json')
    marker = json.loads(raw)
    if (marker['status'] != 'COMPLETE' or marker['next_segment'] != 6241
            or marker['packet_sha256'] != sha_bytes(packet_raw)):
        raise ValueError('original completed RUN13 m2 source identity differs')
    identities = {'inputs/spectral11/m2.json': sha_bytes(packet_raw),
                  'evidence/joint11_sided_m2_3e-11/checkpoint.json': sha_bytes(raw)}
    knots = [(0., float(model.y0[1]))]
    for path in sorted(root.glob('checkpoint_*.npz')):
        segment = int(path.stem.split('_')[-1])
        state_raw = checked_bytes(root, path.name)
        with np.load(io.BytesIO(state_raw), allow_pickle=False) as data:
            state = data['state']
            if state.shape != (model.dim,) or not np.isfinite(state).all():
                raise ValueError('original gas state invalid')
            y = float(state[1])
        z = float(marker['segments'][segment - 1][1])
        knots.append((z, y))
        identities[str(path.relative_to(source))] = sha_bytes(state_raw)
    knots.sort()
    z, y = np.asarray(knots).T
    if len(z) != 18 or z[-1] != 1. or np.any(np.diff(z) <= 0) or np.any(y <= 0):
        raise ValueError('expected original 18 positive gas knots')
    return z, y, {'root': str(source), 'input_identities': identities, 'event_points': len(z),
                  'interpolant': 'scipy.PchipInterpolator(z, native_scaled_Y_HI, extrapolate=False)',
                  'same_physical_density_factor': 'n_HI = nH * Y_HI / exp(3 * dx * z); factors cancel in the ratio'}


def local_unit_coefficients(interpolant, left: float, right: float) -> np.ndarray:
    """Translate the cubic to interval left, then scale u=(z-left)/(right-left)."""
    index = min(len(interpolant.x) - 2, int(np.searchsorted(interpolant.x, left, side='right')) - 1)
    if index < 0 or left < interpolant.x[index] or right > interpolant.x[index + 1]:
        raise ValueError('common interval crosses an interpolation knot')
    c3, c2, c1, c0 = map(float, interpolant.c[:, index])
    shift = left - float(interpolant.x[index])
    width = right - left
    values = [math.fsum((c0, c1 * shift, c2 * shift * shift, c3 * shift ** 3)),
              math.fsum((c1, 2 * c2 * shift, 3 * c3 * shift * shift)) * width,
              math.fsum((c2, 3 * c3 * shift)) * width ** 2,
              c3 * width ** 3]
    if not np.isfinite(values).all():
        raise ValueError('nonfinite translated cubic')
    return np.asarray(values)


def cubic_extrema(coefficients: np.ndarray) -> tuple[float, float, list[float]]:
    """Endpoint and analytic derivative-root range of a cubic on [0,1]."""
    c = np.asarray(coefficients, dtype=float)
    if c.shape != (4,) or not np.isfinite(c).all():
        raise ValueError('finite cubic coefficients required')
    points = [0., 1.]
    a, b, d = 3 * c[3], 2 * c[2], c[1]
    scale = max(abs(a), abs(b), abs(d))
    roots = []
    if scale:
        a, b, d = a / scale, b / scale, d / scale
        if a == 0:
            if b != 0:
                roots = [-d / b]
        else:
            discriminant = math.fsum((b * b, -4 * a * d))
            disc_guard = 64 * MACHINE_EPSILON * (b * b + abs(4 * a * d))
            if discriminant >= -disc_guard:
                square = math.sqrt(max(0., discriminant))
                q = -.5 * (b + math.copysign(square, b))
                roots = [-b / (2 * a)] if q == 0 else [q / a, d / q]
        for root in roots:
            if -64 * MACHINE_EPSILON <= root <= 1 + 64 * MACHINE_EPSILON:
                points.append(min(1., max(0., float(root))))
    points = sorted(set(points))
    values = [math.fsum(float(c[k]) * u ** k for k in range(4)) for u in points]
    return min(values), max(values), points


def compare_interpolants(old, new) -> dict:
    if (old.x[0] != new.x[0] or old.x[-1] != new.x[-1]
            or len(old.x) < 2 or len(new.x) < 2 or old.c.shape[0] != 4 or new.c.shape[0] != 4):
        raise ValueError('two cubic paths on the identical complete domain required')
    knots = np.unique(np.r_[old.x, new.x])
    records = []
    for left, right in zip(knots[:-1], knots[1:]):
        oldc = local_unit_coefficients(old, float(left), float(right))
        newc = local_unit_coefficients(new, float(left), float(right))
        diff = newc - oldc
        oldlo, oldhi, _ = cubic_extrema(oldc)
        newlo, _, _ = cubic_extrema(newc)
        difflo, diffhi, critical = cubic_extrema(diff)
        coefficient_scale = max(math.fsum(abs(float(v)) for v in oldc),
                                math.fsum(abs(float(v)) for v in newc), np.finfo(float).tiny)
        floor = CANCELLATION_FLOOR_ULPS * MACHINE_EPSILON * coefficient_scale
        old_lower = oldlo - floor
        if old_lower <= 0 or newlo - floor <= 0:
            raise ValueError('positive continuous neutral-H path not established')
        padded_difference = max(abs(difflo), abs(diffhi)) * (1 + RELATIVE_PADDING) + floor
        epsilon = padded_difference / old_lower * (1 + RELATIVE_PADDING)
        records.append([float(left), float(right), old_lower, oldhi + floor,
                        difflo, diffhi, floor, epsilon, len(critical)])
    table = np.asarray(records, dtype='<f8')
    worst = int(np.argmax(table[:, 7]))
    epsilon = float(table[worst, 7])
    # Direct SciPy evaluation, separate from coefficient translation/extrema code.
    indices = np.unique(np.linspace(0, len(knots) - 2, min(17, len(knots) - 1), dtype=int))
    samples = [float(knots[0]), float(knots[-1])]
    for index in indices:
        for fraction in (math.sqrt(2) - 1, 1 / math.sqrt(3)):
            samples.append(float(knots[index] + (knots[index + 1] - knots[index]) * fraction))
    ratios = np.abs((new(samples) - old(samples)) / old(samples))
    if not np.isfinite(ratios).all() or np.max(ratios) > epsilon:
        raise ValueError('independent point checks exceed polynomial envelope')
    knot_ratios = np.abs((new(knots) - old(knots)) / old(knots))
    if np.max(knot_ratios) > epsilon:
        raise ValueError('common-knot checks exceed polynomial envelope')
    return {'domain_z': [float(knots[0]), float(knots[-1])], 'common_intervals': len(records),
            'epsilon_abs_relative_upper': epsilon,
            'definition': 'abs(new_PCHIP/old_PCHIP - 1) <= epsilon on the entire common domain, conditional on evaluated polynomial envelopes',
            'worst_interval': {'z_left': records[worst][0], 'z_right': records[worst][1],
                               'positive_old_lower': records[worst][2],
                               'difference_raw_range': records[worst][4:6],
                               'absolute_cancellation_floor': records[worst][6]},
            'minimum_old_path_lower': float(table[:, 2].min()),
            'maximum_absolute_cancellation_floor': float(table[:, 6].max()),
            'relative_padding': RELATIVE_PADDING, 'cancellation_floor_ulps': CANCELLATION_FLOOR_ULPS,
            'float64_epsilon': MACHINE_EPSILON,
            'interval_table_float64_sha256': sha_bytes(table.tobytes()),
            'interval_table_columns': ['left', 'right', 'old_lower', 'old_upper', 'diff_lo', 'diff_hi', 'floor', 'epsilon', 'candidate_count'],
            'independent_point_checks': {'points': len(samples), 'maximum_relative_difference': float(np.max(ratios)), 'within_envelope': True},
            'common_knot_checks': {'points': len(knots), 'maximum_relative_difference': float(np.max(knot_ratios)), 'within_envelope': True},
            'directed_rounding_certificate': False,
            'actual_IVP_between_boundary_error_bound': 'NOT_ESTABLISHED'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--driver', type=Path, default=Path(__file__).with_name('run_joint.py'))
    parser.add_argument('--source-root', type=Path,
                        help='relocated immutable RUN13 source; defaults to recorded location')
    parser.add_argument('--packet', type=Path,
                        help='relocated byte-identical source packet; defaults to recorded location')
    parser.add_argument('--native-binary', type=Path,
                        help='relocated byte-identical native binary; defaults to recorded location')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    znew, ynew, new_id, source, packet = load_new_path(
        args.run, args.driver, source_root=args.source_root,
        packet=args.packet, native_binary=args.native_binary)
    if source in args.output.resolve().parents or args.run.resolve() in args.output.resolve().parents:
        raise ValueError('analysis receipt must be outside immutable trajectory/source directories')
    zold, yold, old_id = load_old_path(source, packet)
    result = compare_interpolants(PchipInterpolator(zold, yold, extrapolate=False),
                                 PchipInterpolator(znew, ynew, extrapolate=False))
    receipt = {'schema': 'rei.run15.pchip_gas_path_comparison.v1',
               'status': 'NUMERICALLY_CHECKED_CONDITIONAL_CONTINUOUS_INTERPOLANT_BOUND',
               'command': [sys.executable, *sys.argv], 'cwd': str(Path.cwd()),
               'script_sha256': sha_bytes(Path(__file__).read_bytes()),
               'environment': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__},
               'old_path': old_id, 'new_path': new_id, 'comparison': result,
               'new_IVP_runs': 0,
               'admitted_use': 'Use measured epsilon as neutral_relative_uncertainty in the existing RUN13 prescribed-gas envelope to cover the explicitly defined new PCHIP gas path, with unchanged source and geometry.',
               'unresolved': ['directed-rounding validation of polynomial extrema',
                              'actual ODE path error between stored event boundaries',
                              'continuous-source nonlinear gas feedback', 'angular and birth-time continua'],
               'wall_s': time.perf_counter() - started}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as handle:
        handle.write(json.dumps(receipt, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'status': receipt['status'], 'output': str(args.output),
                      'epsilon_abs_relative_upper': result['epsilon_abs_relative_upper'],
                      'old_points': len(zold), 'new_points': len(znew), 'new_IVP_runs': 0, 'wall_s': receipt['wall_s']}))


if __name__ == '__main__':
    main()
