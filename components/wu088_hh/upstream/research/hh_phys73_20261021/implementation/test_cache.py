#!/usr/bin/env python3
"""Bounded real-Coulomb cache checks; no HH panel or profile integrations.

The fixed two channels use radial 3 -> 5 nested grids only on [27,28].
An independent uncached preparation must produce an identical binary packet.
Run with an unused --out directory; all first results and failures are retained.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import struct
import time
import traceback
from unittest.mock import patch

import original_source as source
import coulomb_cache


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_checks(output):
    import mpmath as m
    import numpy as np
    import scipy

    output = Path(output)
    if output.is_symlink() or output.exists():
        raise ValueError('cache check requires a new ordinary output directory')
    output.mkdir(parents=True)
    dependencies = [Path(source.__file__), Path(coulomb_cache.__file__),
                    Path(source.__file__).with_name('analytic_screen_source.py'),
                    Path(__file__)]

    def source_hashes():
        return {p.name: digest(p) for p in dependencies}

    before = source_hashes()
    begin = time.perf_counter()
    checks = []
    preparations = {}
    result = dict(schema='PHYS73_COULOMB_CACHE_CHECK_V1',
                  started_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256_before=before,
                  versions=dict(python=platform.python_version(), mpmath=m.__version__,
                                numpy=np.__version__, scipy=scipy.__version__),
                  scope='L1 radial 3->5 on [27,28], dps40; sample preparation only',
                  old_panel_integrations=0, old_profile_integrations=0,
                  certified=False, HH_R10='OFF', checks=checks,
                  preparations=preparations)

    def check(name, condition, **detail):
        entry = dict(name=name, passed=bool(condition), **detail)
        checks.append(entry)
        if not condition:
            raise AssertionError(name)

    def prepare(label, request, cache):
        with patch.object(m, 'coulombf', wraps=m.coulombf) as ff, \
             patch.object(m, 'coulombg', wraps=m.coulombg) as gg:
            receipt = source.prepare(output / label, request, workers=1, cache=cache)
            actual = dict(coulombf=ff.call_count, coulombg=gg.call_count)
        preparations[label] = dict(receipt=receipt, actual_scalar_calls=actual)
        check(label + '_actual_call_counts',
              ff.call_count == gg.call_count and
              ff.call_count + gg.call_count == receipt['Coulomb_scalar_calls'],
              actual=actual, reported_scalar_calls=receipt['Coulomb_scalar_calls'])
        return receipt

    try:
        cache = output / 'coulomb_cache'
        coarse_request = source.validated_request(1, 3, 8, 28.0, 40)
        fine_request = source.validated_request(1, 5, 8, 28.0, 40)
        coarse = prepare('coarse_cached', coarse_request, cache)
        check('coarse_new_nodes', coarse['Coulomb_scalar_calls'] == 12 and
              coarse['cached_node_hits'] == 2,
              new_nodes=6, hits=coarse['cached_node_hits'],
              hit_semantics='includes within-call repeated B, even without disk cache')
        fine = prepare('fine_cached', fine_request, cache)
        check('nested_grid_reuses_coarse_nodes', fine['Coulomb_scalar_calls'] == 8 and
              fine['cached_node_hits'] == 8,
              new_nodes=4, hits=fine['cached_node_hits'])
        uncached = prepare('fine_uncached', fine_request, None)
        check('uncached_fine_counts', uncached['Coulomb_scalar_calls'] == 20 and
              uncached['cached_node_hits'] == 2,
              new_nodes=10, hits=uncached['cached_node_hits'])
        cached_packet = output / 'fine_cached/SOURCE_GREEN.bin'
        uncached_packet = output / 'fine_uncached/SOURCE_GREEN.bin'
        raw = cached_packet.read_bytes()
        check('cached_uncached_packet_bit_identity', raw == uncached_packet.read_bytes(),
              cached_sha256=digest(cached_packet), uncached_sha256=digest(uncached_packet))
        check('packet_shape_and_magic', raw[:8] == b'HHG73V01' and
              struct.unpack('<QQ', raw[8:24]) == (2, 5) and len(raw) == 24 + 48 * 2 * 5)

        protected = list((output / 'fine_cached').iterdir()) + list(cache.rglob('*.json'))
        protected_before = {str(p.relative_to(output)): digest(p) for p in protected}
        with patch.object(source, 'coulomb_task', side_effect=AssertionError('resume evaluated channel')) as task, \
             patch.object(m, 'coulombf', side_effect=AssertionError('resume evaluated F')) as ff, \
             patch.object(m, 'coulombg', side_effect=AssertionError('resume evaluated G')) as gg:
            reused = source.prepare(output / 'fine_cached', fine_request, workers=1, cache=cache)
        check('completed_prepare_resume_zero_evaluations',
              reused['this_invocation'] == 'REUSED_VERIFIED_NO_EVALUATIONS' and
              task.call_count == ff.call_count == gg.call_count == 0,
              actual_channel_calls=task.call_count, actual_F_calls=ff.call_count,
              actual_G_calls=gg.call_count)
        check('resume_preserves_existing_bytes', protected_before ==
              {str(p.relative_to(output)): digest(p) for p in protected})
        cache_files = list(cache.glob('*/ell_*.json'))
        check('one_cache_file_per_channel', len(cache_files) == 2)
        file = next(p for p in cache_files if p.name == 'ell_0000.json')
        original = file.read_bytes()
        for name, mode in [('changed_payload_rejected', 'payload'),
                           ('wrong_binding_with_valid_hash_rejected', 'binding')]:
            changed = json.loads(original)
            if mode == 'payload':
                radius = next(iter(changed['payload']['values']))
                changed['payload']['values'][radius][0] = '0'
            else:
                changed['payload']['binding']['dps'] = 41
                changed['payload_sha256'] = coulomb_cache.digest(changed['payload'])
            file.write_text(json.dumps(changed, sort_keys=True) + '\n')
            reason = None
            try:
                with patch.object(m, 'coulombf', side_effect=AssertionError('bad cache evaluated F')) as ff, \
                     patch.object(m, 'coulombg', side_effect=AssertionError('bad cache evaluated G')) as gg:
                    try:
                        source.prepare(output / name, fine_request, workers=1, cache=cache)
                    except ValueError as error:
                        reason = str(error)
                check(name, reason == 'Coulomb cache binding or hash mismatch' and
                      ff.call_count == gg.call_count == 0,
                      exception=reason, actual_F_calls=ff.call_count, actual_G_calls=gg.call_count)
            finally:
                file.write_bytes(original)
        check('tamper_test_restores_cache_bytes', file.read_bytes() == original)
        result['status'] = 'PASS'
    except Exception:
        result['status'] = 'FAIL'
        result['traceback'] = traceback.format_exc()
    finally:
        after = source_hashes()
        result['source_sha256_after'] = after
        result['source_stable_during_run'] = before == after
        if before != after:
            result['status'] = 'FAIL_SOURCE_CHANGED_DURING_CHECK'
        result['elapsed_seconds'] = time.perf_counter() - begin
        result['passed_checks'] = sum(c['passed'] for c in checks)
        result['total_checks'] = len(checks)
        result['actual_total_Coulomb_scalar_calls'] = sum(
            sum(p['actual_scalar_calls'].values()) for p in preparations.values())
        result['files_sha256'] = {
            str(p.relative_to(output)): digest(p) for p in sorted(output.rglob('*'))
            if p.is_file() and not p.is_symlink() and p.suffix != '.lock'
        }
        with (output / 'CACHE_CHECK_RECEIPT.json').open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write('\n')
    return result


def main():
    for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[name] = '1'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = run_checks(args.out)
    print(json.dumps({k: result[k] for k in ('status', 'passed_checks', 'total_checks',
                                           'elapsed_seconds', 'source_stable_during_run',
                                           'actual_total_Coulomb_scalar_calls')}, indent=2))
    if result['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
