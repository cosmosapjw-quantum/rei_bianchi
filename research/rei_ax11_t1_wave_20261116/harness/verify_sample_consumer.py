#!/usr/bin/env python3
"""Check streaming consumption against full-array owner interpolation on saved native data."""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
import tempfile
import time

import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator

import analyze_t1_response as analysis
import native_extract_t1 as extract


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('saved_archive', type=Path)
    parser.add_argument('receipt', type=Path)
    args = parser.parse_args()
    begin = time.monotonic()
    owner = analysis.owner_module()
    fields = analysis.OBS + ['time_s']
    checks = []
    fixtures = {}
    with tempfile.TemporaryDirectory(prefix='ax11_consumer_check_') as temporary:
        root = Path(temporary)
        records = []
        frames = {}
        with tarfile.open(args.saved_archive) as archive:
            for case in ['ZERO', 'PLUS']:
                folder = root / 'cases' / case / 'segment_000'
                folder.mkdir(parents=True)
                for name in ['history.csv', 'ledgers.csv', 'checkpoint.start.txt', 'checkpoint.txt']:
                    member = f'time_preflight_results/{case}_T1_ORIGINAL_START/{name}'
                    data = archive.extractfile(member).read()
                    (folder / name).write_bytes(data)
                    fixtures[member] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
                records.append({'name': case + '_segment_000', 'status': 'FINISHED',
                                'output_directory': str(folder), 'summary': {'error': 'NONE'}})
                frame = pd.read_csv(folder / 'history.csv', float_precision='round_trip')
                frame['ln_a'] = np.log(frame.a)
                frame['xe_per_H'] = frame.ne_proper_cm3 / frame.nH_proper_cm3
                frames[case] = frame
        lower = max(frame.ln_a.iloc[0] for frame in frames.values())
        upper = min(frame.ln_a.iloc[-1] for frame in frames.values())
        us = np.linspace(lower, upper, 1001)
        end_t = min(frame.time_s.iloc[-1] for frame in frames.values())
        ts = np.linspace(0., end_t, 1001)
        grid = {'fixed_a': [{'index': i, 'ln_a': float(u), 'a': float(np.exp(u))}
                            for i, u in enumerate(us)],
                'fixed_t': [{'index': i, 'elapsed_time_s': float(t)} for i, t in enumerate(ts)]}
        (root / 'SAMPLING_GRID.json').write_text(json.dumps(grid))
        output = root / 'output'
        output.mkdir()
        for case in ['ZERO', 'PLUS']:
            result = extract.consume_case(root, case, grid, records, output)
            with gzip.open(result['path'], 'rt') as stream:
                packed = json.load(stream)
            frame = frames[case]
            for mode in ['fixed_a', 'fixed_t']:
                assert packed['samples'][mode]['represented_query_count'] == 1001
                reference_u = us if mode == 'fixed_a' else owner.interp(ts, frame.time_s, frame.ln_a)
                reference_alt_u = us if mode == 'fixed_a' else PchipInterpolator(frame.time_s, frame.ln_a)(ts)
                got = [analysis.interpolate_window(owner, packed, mode, item)
                       for item in packed['samples'][mode]['windows']]
                for field in fields:
                    expected = owner.field_at(frame, reference_u, field)
                    actual = np.array([item[0][field] for item in got])
                    err = float(np.max(abs(actual - expected)))
                    scale = max(float(np.max(abs(expected))), np.finfo(float).tiny)
                    allowance = 8 * abs(float(np.spacing(scale)))
                    assert err <= allowance, (case, mode, field, err, allowance)
                    checks.append({'case': case, 'mode': mode, 'field': field,
                                   'max_abs_difference_from_full_owner_interpolation': err,
                                   'roundoff_allowance': allowance,
                                   'all_1001_values_bit_equal': bool(np.array_equal(actual, expected))})
                    if field in analysis.OBS:
                        alt = PchipInterpolator(frame.ln_a, frame[field])(reference_alt_u)
                        actual_alt = np.array([item[1][field] for item in got])
                        assert np.max(abs(actual_alt - alt)) <= allowance
                bad = json.loads(json.dumps(packed['samples'][mode]['windows'][0]))
                if mode == 'fixed_a':
                    bad['query']['ln_a'] -= .1
                else:
                    bad['query']['elapsed_time_s'] = -1e10
                rejected = False
                try:
                    analysis.interpolate_window(owner, packed, mode, bad)
                except (AssertionError, ValueError):
                    rejected = True
                assert rejected, 'extrapolation mutant was accepted'
        # A corrupted continuation cannot be silently sorted or spliced.
        source = root / 'cases/PLUS/segment_000'
        bad_segment = root / 'cases/PLUS/segment_001'
        shutil.copytree(source, bad_segment)
        shutil.copyfile(source / 'checkpoint.txt', bad_segment / 'input_checkpoint.txt')
        bad_records = records + [{'name': 'PLUS_segment_001', 'status': 'FINISHED',
                                  'output_directory': str(bad_segment), 'summary': {'error': 'NONE'}}]
        rejected = False
        try:
            extract.consume_case(root, 'PLUS', grid, bad_records, output)
        except ValueError as error:
            rejected = str(error) == 'CONTINUATION_START_STATE'
        assert rejected, 'incorrect continuation boundary was admitted'
    receipt = {'status': 'PASS_SCOPED_SAVED_NATIVE_CONSUMER_CHECK',
               'review_provenance': 'same-author adversarial checks against unchanged owner full-array interpolation',
               'fixtures': fixtures, 'checks': checks,
               'extrapolation_mutants_rejected': 4, 'corrupt_continuation_mutants_rejected': 1,
               'new_native_evolution_runs': 0, 'new_physical_node_credit': 0,
               'wall_s': time.monotonic() - begin,
               'script_sha256': analysis.sha(__file__),
               'extractor_sha256': analysis.sha(extract.__file__),
               'analyzer_sha256': analysis.sha(analysis.__file__),
               'original_DAG': '10/17', 'expansion_DAG': '28/88'}
    assert not args.receipt.exists()
    args.receipt.write_text(json.dumps(receipt, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'status': receipt['status'], 'checked_field_modes': len(checks),
                      'bit_equal_field_modes': sum(item['all_1001_values_bit_equal'] for item in checks),
                      'wall_s': receipt['wall_s']}))


if __name__ == '__main__':
    main()
