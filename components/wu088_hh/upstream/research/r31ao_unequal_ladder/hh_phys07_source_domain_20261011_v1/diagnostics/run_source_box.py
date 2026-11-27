#!/usr/bin/env python3
"""One bounded, source-derived reference stage; no native/root/time solver.

The owner executes this only after its execution contract is fixed.  Each call
performs exactly two source-box exports: whole X x Theta, then the fixed X
midpoint x Theta.  The second call is an arithmetic box evaluation, not a
nonlinear point solve.  --sigma-reference reuses immutable provider evidence.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from certified_interval import I
from hh_source_box import (ScalarChart, evaluate_box, family_json, interval_json,
                           isotropic_reference_family, parse_interval,
                           reference_cross_section, source_box_export)

SOURCE_FILES = (
    'ft03_interval.rs', 'ft03_rates.rs', 'ft03_controlled.rs', 'hhe_events.rs',
    'hh_primary_extension.rs', 'phys04_mixed.rs', 'phys04_transport.rs',
    'paired_runtime.rs', 'coupled_primary.rs', 'atomic_provider.rs',
    'interval_ad.rs', 'interval_math.rs',
)
GAS_BOX = tuple(I(Fraction(lo), Fraction(hi)) for lo, hi in (
    ('0.90', '0.93'), ('0.29', '0.31'), ('0.59', '0.61'), ('13', '14')))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, obj):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(obj, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def progress(stage, **kwargs):
    print(json.dumps({'progress': stage, **kwargs}, ensure_ascii=False), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--source-root', type=Path, required=True,
                        help='directory containing candidate/src')
    parser.add_argument('--source-commit', required=True)
    parser.add_argument('--dt', type=float, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--sigma-reference', type=Path)
    args = parser.parse_args()
    if args.dt not in (625000000.0, 1250000000.0):
        raise ValueError('only the fixed full or first-half diagnostic dt is admitted')
    if len(args.source_commit) != 40 or any(c not in '0123456789abcdef' for c in args.source_commit):
        raise ValueError('exact source commit identifier required')
    if args.output_dir.exists():
        raise FileExistsError('create-only output directory already exists')
    args.output_dir.mkdir(parents=True)
    started = datetime.now(timezone.utc).isoformat()
    start_perf = time.perf_counter()
    archived = json.loads(args.input.read_text(encoding='utf-8'))
    source_hashes = {p: sha(args.source_root / 'candidate' / 'src' / p) for p in SOURCE_FILES}
    identities = {
        'source_commit_declared_from_intake': args.source_commit,
        'source_files_sha256': source_hashes,
        'archived_input_path': str(args.input.resolve()),
        'archived_input_sha256': sha(args.input),
        'archived_seed_sha256': archived['seed']['sha256'],
        'source_port_sha256': sha(ROOT / 'src' / 'hh_source_box.py'),
        'interval_backend_sha256': sha(ROOT / 'src' / 'certified_interval.py'),
        'driver_sha256': sha(Path(__file__)),
        'no_remote_lookup_or_native_callback_in_this_driver': True,
    }
    save(args.output_dir / 'input_identities.json', identities)
    energies = tuple(float(row['energy_eV']) for row in archived['groups'])
    provider_evaluations = 0
    if args.sigma_reference is None:
        provider_chart = ScalarChart()
        sigma = tuple(tuple(I(reference_cross_section(e, a, provider_chart)) for a in range(3)) for e in energies)
        provider_evaluations = len(energies) * 3
        provider = {
            'schema': 'WU088_HH_PHYS07_CORRECT_ROUNDING_PROVIDER_REFERENCE_V1',
            'source_sha256': source_hashes['atomic_provider.rs'],
            'energy_hex': [e.hex() for e in energies],
            'sigma_cm2': [[interval_json(x) for x in row] for row in sigma],
            'reference_transcendental_leaves': provider_chart.transcendental_leaves,
            'reference_binary64_scalar_operations': provider_chart.scalar_operations,
            'native_provider_calls': 0,
            'native_libm_identity': 'UNRESOLVED_NOT_CALLED',
        }
        save(args.output_dir / 'provider_reference.json', provider)
        provider_reuse = None
    else:
        provider = json.loads(args.sigma_reference.read_text(encoding='utf-8'))
        if provider['source_sha256'] != source_hashes['atomic_provider.rs']:
            raise ValueError('provider source hash differs from reusable reference')
        if provider['energy_hex'] != [e.hex() for e in energies]:
            raise ValueError('provider reference energy leaves differ')
        if provider.get('native_provider_calls') != 0 or provider.get('native_libm_identity') != 'UNRESOLVED_NOT_CALLED':
            raise ValueError('unexpected provider reference semantics')
        sigma = tuple(tuple(parse_interval(z) for z in row) for row in provider['sigma_cm2'])
        provider_reuse = {'path': str(args.sigma_reference.resolve()), 'sha256': sha(args.sigma_reference), 'read_only_reuse_no_provider_arithmetic_replay': True}
        save(args.output_dir / 'provider_reuse.json', provider_reuse)
    progress('provider_reference_ready', new_reference_channel_calls=provider_evaluations, native_provider_calls=0)
    family, chart_audit = isotropic_reference_family(archived, args.dt, provider_sigmas=sigma)
    family.metadata['source_bindings'] = identities
    family.metadata['provider_reference'] = ({'path': 'provider_reference.json', 'sha256': sha(args.output_dir / 'provider_reference.json')} if provider_reuse is None else provider_reuse)
    save(args.output_dir / 'family.json', family_json(family))
    save(args.output_dir / 'chart_audit.json', chart_audit)
    progress('first_stage_family_ready', dt_s=args.dt, native_preBE_calls=0)
    whole = evaluate_box(family, GAS_BOX)
    whole_data = source_box_export(family, GAS_BOX, whole)
    save(args.output_dir / 'source_box.json', whole_data)
    progress('whole_source_box_saved', source_box_evaluations=1)
    centre = tuple(I((x.lo + x.hi) / 2) for x in GAS_BOX)
    at_centre = evaluate_box(family, centre)
    centre_data = source_box_export(family, centre, at_centre)
    centre_data['evaluation_domain'] = 'fixed gas-box midpoint x the full parameter Theta; not a point solver or parameter-point-only bound'
    save(args.output_dir / 'source_centre.json', centre_data)
    progress('source_centre_box_saved', source_box_evaluations=2)
    summary = {
        'schema': 'WU088_HH_PHYS07_SOURCE_REFERENCE_EXECUTION_V1',
        'started_utc': started,
        'finished_utc': datetime.now(timezone.utc).isoformat(),
        'wall_seconds_inside_driver': time.perf_counter() - start_perf,
        'source_model': 'FT03 + LCS91(lambda) + reduced photo Nbar+b B + expansion',
        'dt_s': args.dt,
        'parameter_coverage': {'lambda': [0, 1], 'b': [0, 1]},
        'gas_box': [interval_json(z) for z in GAS_BOX],
        'source_box_evaluations': 2,
        'source_box_evaluation_kinds': ['whole gas X x Theta', 'fixed X midpoint x Theta'],
        'new_reference_provider_channel_calls': provider_evaluations,
        'new_reference_provider_active_channels': sum(not (z.lo == z.hi == 0) for row in sigma for z in row) if provider_evaluations else 0,
        'native_calls': {'provider': 0, 'source_callback': 0, 'preBE': 0, 'endpoint': 0, 'BE_point': 0, 'root': 0, 'IVP': 0, 'heavy_atomic': 0},
        'old_science_suite_replays': 0,
        'whole_box_temperature_K': interval_json(whole['temperature'].v),
        'whole_box_minimum_photon_denominator': str(min(z.v.lo for z in whole['denominators'])),
        'fixed_gas_G_lambdab_exact_zero': whole_data['structural_fixed_gas_G_lambdab_zero'] and centre_data['structural_fixed_gas_G_lambdab_zero'],
        'native_source_tuple_binding': 'OPEN',
        'native_root_certified': False,
        'actual_HH_W': None,
        'actual_finite_interaction': None,
        'reference_uniform_root_decision': 'NOT_PERFORMED_BY_THIS_DRIVER',
        'input_identities_sha256': sha(args.output_dir / 'input_identities.json'),
        'provider_reference_reused': provider_reuse,
    }
    save(args.output_dir / 'run_summary.json', summary)
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
