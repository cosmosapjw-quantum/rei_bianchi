#!/usr/bin/env python3
"""One-pass, local C10 evidence recovery. This program never runs physics.

Only NPZ validation imports NumPy. All original files and processes are read-only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import shutil
import socket
import sys
import tarfile
import time
import zipfile
import zlib

CASE_ID = 'quench_Li_Be_union_aug_TZ_occ_list_v6'
RUN = Path('runs/threeelectron_v6') / CASE_ID
SOURCE = Path('code/microphysics_driver_v6.py')
CONTRACT = Path('CONTRACT_MICROPHYSICS_V6_THREEE.json')
FROZEN = {
    'source': '31cdd14df59ffc6208561cb3c61ff4bd114240c380693ff5789e14441e7c091c',
    'contract': 'cf7b06ad72815513e799be253539bdfecfb9102c1fc586589003e8b6fd364e4d',
    'input': '289520d8aed460cdee460f5497762b0c613f003bd6ba43bb505416d945995097',
}
BACKEND = 'unpenalized_direct_spin1_occupied_list_capable_RDM_spin'
CASE = {
    'basis': 'aug-cc-pvtz', 'basis_elements': ['Li', 'Be'],
    'contract_id': 'R9-FCI-BO-QUENCH-RESPONSE-v6-threeelectron-occupation-list',
    'contract_sha256': FROZEN['contract'], 'final_charge': 1, 'final_symbol': 'Be',
    'id': CASE_ID, 'initial_charge': 0, 'initial_symbol': 'Li', 'kind': 'quench',
    'memory_gib': 24.0, 'nelec': [2, 1], 'resource_gated': True, 'spin': 1,
    'threads': 12,
}
LIMITS = {'norm_error': 1e-10, 'orthogonality_inf': 1e-8,
          'rdm_trace_error': 1e-8, 'spin_error': 1e-6,
          'original_H_residual_Eh': 1e-7}


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def read_json(path):
    return json.loads(Path(path).read_text())


def stat_key(path):
    s = Path(path).stat()
    return [s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def fingerprint(path):
    """Detect normal writer activity across hashing; no adversarial model."""
    path = Path(path)
    record = {'path': str(path)}
    try:
        before = stat_key(path)
        digest = sha(path)
        after = stat_key(path)
        record.update(sha256=digest, size=after[2], stat=after, stable=before == after)
    except OSError as e:
        record.update(stable=False, error=str(e))
    return record


def finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate(receipt_path, input_path, source_path, contract_path, expected=FROZEN):
    """Validate receipt gates and independently check archive-level invariants."""
    gates = []
    evidence = {}

    def gate(name, measured, passed, limit=None):
        # Preserve nonfinite/malformed observations without emitting invalid JSON.
        if isinstance(measured, float) and not math.isfinite(measured):
            measured = str(measured)
        item = {'name': name, 'measured': measured, 'pass': bool(passed)}
        if limit is not None:
            item['limit'] = limit
        gates.append(item)

    def eq(name, measured, wanted):
        same_type = type(measured) is type(wanted) if isinstance(wanted, (bool, int)) else True
        gate(name, measured, same_type and measured == wanted)

    def number(name, measured, limit=None):
        gate(name, measured, finite_number(measured) and (limit is None or 0 <= measured <= limit), limit)

    try:
        receipt_path, input_path = Path(receipt_path), Path(input_path)
        data_path = receipt_path.parent / 'data.npz'
        paths = {'receipt': receipt_path, 'input': input_path, 'source': source_path,
                 'contract': contract_path, 'data': data_path}
        before = {name: fingerprint(path) for name, path in paths.items()}
        evidence.update(before)
        for name, item in before.items():
            eq(name + '.stable_before', item['stable'], True)
        r, case = read_json(receipt_path), read_json(input_path)
        eq('case.frozen_semantics', case, CASE)
        eq('receipt.case', r.get('case'), case)
        for name in ('source', 'contract', 'input'):
            eq(name + '.byte_sha256', before[name].get('sha256'), expected[name])
        eq('receipt.case_sha256', r.get('case_sha256'),
           hashlib.sha256(json.dumps(case, sort_keys=True).encode()).hexdigest())
        eq('receipt.input_sha256', r.get('input_sha256'), expected['input'])
        eq('receipt.runtime.source_sha256', r.get('runtime', {}).get('source_sha256'), expected['source'])
        eq('receipt.data_sha256', r.get('data_sha256'), before['data'].get('sha256'))
        eq('receipt.status', r.get('status'), 'finite_model_computed')
        eq('receipt.exit_code', r.get('exit_code'), 0)
        eq('receipt.finite_model_numerics_passed', r.get('finite_model_numerics_passed'), True)
        def recursive_numerics(value, prefix):
            if isinstance(value, dict):
                for key, item in value.items():
                    if key == 'finite_model_numerics_passed':
                        eq(prefix + '.' + key, item, True)
                    recursive_numerics(item, prefix + '.' + key)
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    recursive_numerics(item, prefix + '.' + str(index))
        recursive_numerics(r, 'recursive')
        n, ao = r.get('retained_ao_rank'), r.get('ao_rank')
        gate('retained_ao_rank', n, isinstance(n, int) and n >= 64)
        gate('ao_rank', ao, isinstance(ao, int) and isinstance(n, int) and ao >= n)
        for role in ('parent', 'daughter'):
            s = r.get(role, {})
            eq(role + '.finite_model_numerics_passed', s.get('finite_model_numerics_passed'), True)
            eq(role + '.nelec', s.get('nelec'), [2, 1])
            eq(role + '.norb', s.get('norb'), n)
            eq(role + '.solver_backend', s.get('solver_backend'), BACKEND)
            for key in ('E_BO_Eh', 'E_electronic_Eh', 'spin_squared'):
                number(role + '.' + key, s.get(key))
            spin_squared = s.get('spin_squared')
            gate(role + '.spin_squared_target_error', spin_squared,
                 finite_number(spin_squared) and abs(spin_squared - 0.75) <= 1e-6, 1e-6)
            checks = s.get('checks', {})
            for key, limit in LIMITS.items():
                number(role + '.checks.' + key, checks.get(key), limit)
            eq(role + '.checks.fci_converged', checks.get('fci_converged'), True)
        for key in ('daughter_energy_mean_Eh', 'daughter_energy_second_moment_Eh2', 'daughter_energy_variance_Eh2'):
            number(key, r.get(key))
        for key in ('closure_error', 'ground_complement_overlap'):
            number('receipt.checks.' + key, r.get('checks', {}).get(key), 1e-10)
        import numpy as np
        if not isinstance(n, int) or not isinstance(ao, int) or n < 1 or ao < n:
            raise ValueError('invalid retained/AO dimensions')
        shapes = {key: (n * (n - 1) // 2, n) for key in ('CI_parent', 'CI_daughter_ground', 'CI_complement')}
        shapes.update(common_orbital_matrix=(ao, n), AO_overlap_eigenvalues=(ao,),
                      rdm1_parent=(n, n), rdm1_daughter=(n, n))
        with data_path.open('rb') as archive_file, np.load(archive_file, allow_pickle=False) as archive:
            arrays = {}
            for key, shape in shapes.items():
                a = archive[key]
                eq('npz.' + key + '.shape', list(a.shape), list(shape))
                gate('npz.' + key + '.finite', bool(np.all(np.isfinite(a))), np.all(np.isfinite(a)))
                arrays[key] = a
            ci, cf, q = [arrays[k] for k in ('CI_parent', 'CI_daughter_ground', 'CI_complement')]
            for role, a in [('parent', ci), ('daughter', cf)]:
                number('recomputed.' + role + '.norm_error', float(abs(np.vdot(a, a) - 1)), 1e-10)
                trace = np.trace(arrays['rdm1_' + role])
                number('recomputed.' + role + '.rdm_trace_error', float(abs(trace - 3)), 1e-8)
            A = np.vdot(cf, ci)
            p, comp = float(abs(A) ** 2), float(np.vdot(q, q).real)
            number('recomputed.q_identity_error', float(np.linalg.norm(q - (ci - A * cf))), 1e-10)
            number('recomputed.closure_error', abs(p + comp - 1), 1e-10)
            number('recomputed.ground_complement_overlap', float(abs(np.vdot(cf, q))), 1e-10)
            gate('recomputed.P_range', p, math.isfinite(p) and -1e-10 <= p <= 1 + 1e-10)
            gate('recomputed.complement_range', comp, math.isfinite(comp) and -1e-10 <= comp <= 1 + 1e-10)
            for key, actual in [('P_ground', p), ('A_ground_real', float(A.real)),
                                ('unresolved_excitation_including_bound_probability', comp)]:
                measured = r.get(key)
                gate('receipt.' + key + '.agreement', measured,
                     finite_number(measured) and abs(measured - actual) <= 1e-10, 1e-10)
        for name, path in paths.items():
            after = fingerprint(path)
            eq(name + '.stable_after', after.get('sha256') == before[name].get('sha256')
               and after.get('stat') == before[name].get('stat') and after['stable'], True)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ImportError,
            OverflowError, EOFError, zipfile.BadZipFile, zlib.error) as e:
        gate('validation_exception', str(e), False)
    return {'passed': bool(gates) and all(g['pass'] for g in gates), 'gates': gates,
            'evidence': evidence,
            'scope': 'finite common-space Li to Be+ ground projection and unresolved complement only',
            'independent_checks': 'archive invariants; original-H residual and AO metric are recorded solver gates',
            'physical_closure': 'all eight physical closure flags remain open'}


def find_attempts(root, extra_roots=(), max_files=20000, max_depth=5):
    """Bounded scan; incomplete/denied scans never constitute proven absence."""
    root = Path(root)
    candidates = {root / RUN} if (root / RUN).exists() else set()
    errors, roots, count = [], [root / 'runs'] + [Path(p).resolve() for p in extra_roots], 0
    for search in roots:
        if not search.exists():
            if search != root / 'runs' or not root.is_dir():
                errors.append({'path': str(search), 'error': 'search root unavailable'})
            continue
        def onerror(e):
            errors.append({'path': str(search), 'error': str(e)})
        for current, dirs, files in os.walk(search, onerror=onerror):
            current = Path(current)
            depth = len(current.relative_to(search).parts)
            if depth >= max_depth and dirs:
                errors.append({'path': str(current), 'error': 'bounded search depth exceeded'})
                dirs[:] = []
            count += len(files)
            if count > max_files:
                errors.append({'path': str(search), 'error': 'bounded search file limit exceeded'})
                break
            if current.name == CASE_ID:
                candidates.add(current)
            for name in ('input.json', 'receipt.json'):
                if name not in files:
                    continue
                path = current / name
                try:
                    payload = read_json(path)
                    case = payload.get('case', payload)
                    if case.get('id') == CASE_ID or (name == 'input.json' and sha(path) == FROZEN['input']):
                        candidates.add(current)
                except (OSError, ValueError, AttributeError) as e:
                    # Unreadable run records can conceal an attempt; malformed unrelated files cannot prove missing.
                    errors.append({'path': str(path), 'error': str(e)})
    populated = []
    for candidate in sorted(candidates):
        try:
            if any(candidate.iterdir()):
                populated.append(candidate)
        except OSError as e:
            errors.append({'path': str(candidate), 'error': str(e)})
    return populated, errors, [str(p) for p in roots]


def process_snapshot(root, attempts, proc_root=Path('/proc')):
    errors, matches = [], []
    driver = str((Path(root) / SOURCE).resolve())
    try:
        uptime = float((proc_root / 'uptime').read_text().split()[0])
        ticks = os.sysconf('SC_CLK_TCK')
        processes = list(proc_root.iterdir())
    except OSError as e:
        return [], [str(e)]
    outputs = {str(p.resolve()) for p in attempts}
    inputs = {str((p / 'input.json').resolve()) for p in attempts}
    for entry in processes:
        if not entry.name.isdigit() or int(entry.name) == os.getpid():
            continue
        try:
            raw = (entry / 'cmdline').read_bytes()
            args = [x.decode(errors='replace') for x in raw.split(b'\0') if x]
            if not args:
                continue
            # Only resolve cwd after a command token could be this driver. A
            # denied unrelated daemon cwd is not unavailable target evidence.
            if not any(Path(a).name == SOURCE.name for a in args):
                continue
            cwd = os.readlink(entry / 'cwd')
            resolved = [str((Path(cwd) / a).resolve()) if not a.startswith('/') else str(Path(a).resolve()) for a in args]
            if driver not in resolved:
                continue
            def option(name):
                return args[args.index(name) + 1] if name in args and args.index(name) + 1 < len(args) else None
            def absolute(value):
                return str((Path(cwd) / value).resolve()) if value else None
            out, inp = absolute(option('--out')), absolute(option('--case-file'))
            is_worker = 'case' in args and inp in inputs and out in outputs
            only_filters = []
            if '--only' in args:
                for value in args[args.index('--only') + 1:]:
                    if value.startswith('--'):
                        break
                    only_filters.append(value)
            includes_target = '--only' not in args or any(value in CASE_ID for value in only_filters)
            output_contains_target = out is not None and any(str(Path(p).parent) == out for p in outputs)
            if out is not None and not output_contains_target and 'run' in args:
                deck = Path(out) / 'case_deck.json'
                if deck.exists():
                    deck_cases = read_json(deck)
                    if not isinstance(deck_cases, list):
                        raise ValueError('case_deck.json is not a case list')
                    output_contains_target = any(case == CASE for case in deck_cases)
            is_supervisor = ('run' in args and includes_target and output_contains_target
                             and absolute(option('--contract')) == str((Path(root) / CONTRACT).resolve())
                             and out is not None)
            if not (is_worker or is_supervisor):
                continue
            fields = (entry / 'stat').read_text().rsplit(')', 1)[1].split()
            state, start = fields[0], int(fields[19])
            elapsed = max(0.0, uptime - start / ticks)
            matches.append({'pid': int(entry.name), 'start_ticks': start, 'state': state,
                            'elapsed_s': elapsed, 'command': args, 'cwd': cwd,
                            'worker': is_worker, 'supervisor': is_supervisor,
                            'active': state not in ('Z', 'X'), 'output': out,
                            'wall_supervisor_anomaly': elapsed > 7200,
                            'status': (entry / 'status').read_text()})
        except FileNotFoundError:
            # Normal /proc exit race. It is not a denied inspection.
            continue
        except (OSError, ValueError) as e:
            errors.append({'pid': int(entry.name), 'error': str(e)})
    return matches, errors


def classify(attempts, processes, blocked=False):
    if blocked:
        return 'unknown', 'inspection unavailable; no launch'
    terminal = [a for a in attempts if a['terminal']]
    active = [p for p in processes if p['active']]
    if len(terminal) > 1:
        return 'conflict', 'multiple terminal attempts; retain every attempt, no automatic choice'
    if active:
        # Same worker/supervisor may still be writing/finalizing one receipt.
        active_paths = {p['output'] for p in active}
        foreign = [a for a in terminal if a['path'] not in active_paths and str(Path(a['path']).parent) not in active_paths]
        if foreign:
            return 'conflict', 'active attempt and independent terminal attempt coexist'
        return 'in-progress', 'matching active worker/supervisor; no second launch or termination'
    if terminal:
        valid = terminal[0]['validation'].get('passed', False)
        if valid and terminal[0]['stable']:
            return 'complete-success', 'stable terminal receipt and data pass all frozen gates'
        if not terminal[0]['stable']:
            return 'unknown', 'terminal artifacts changed during inspection; acceptance deferred'
        return 'complete-fail', 'terminal receipt/data failed recovery gates; preserve and diagnose, no replay'
    if attempts:
        return 'stale', 'attempt evidence remains without terminal receipt or active process; no replay'
    return 'missing', 'bounded actual search found no attempt; historical launch still prevents replay'


def runtime_identity():
    versions = {}
    for name in ('numpy', 'scipy', 'pyscf', 'h5py', 'mpmath'):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    try:
        boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    except OSError as e:
        boot = 'unavailable: ' + str(e)
    return {'utc': utc(), 'hostname': socket.gethostname(), 'python': sys.version,
            'executable': sys.executable, 'platform': platform.platform(), 'kernel_boot_id': boot,
            'packages': versions, 'cpu_count': os.cpu_count(),
            'meminfo': Path('/proc/meminfo').read_text() if Path('/proc/meminfo').exists() else None}


def inspect(root, extra_roots=()):
    root = Path(root).resolve()
    paths, errors, searches = find_attempts(root, extra_roots)
    processes, proc_errors = process_snapshot(root, paths)
    errors += proc_errors
    identities = {}
    for name, path in [('source', root / SOURCE), ('contract', root / CONTRACT)]:
        item = fingerprint(path)
        item['expected_sha256'] = FROZEN[name]
        item['identity_passed'] = item.get('sha256') == FROZEN[name] and item['stable']
        identities[name] = item
        if 'error' in item:
            errors.append({'path': str(path), 'error': item['error']})
    attempts = []
    for path in paths:
        artifacts = []
        try:
            for item in sorted(path.rglob('*')):
                if item.is_file():
                    artifacts.append(fingerprint(item))
        except OSError as e:
            errors.append({'path': str(path), 'error': str(e)})
        receipt = path / 'receipt.json'
        input_identity = fingerprint(path / 'input.json')
        input_identity['expected_sha256'] = FROZEN['input']
        input_identity['identity_passed'] = (input_identity.get('sha256') == FROZEN['input']
                                             and input_identity['stable'])
        validation = validate(receipt, path / 'input.json', root / SOURCE, root / CONTRACT) if receipt.exists() else {'passed': False, 'reason': 'no terminal receipt'}
        stable = bool(artifacts) and all(a['stable'] for a in artifacts)
        attempts.append({'path': str(path), 'terminal': receipt.exists(), 'stable': stable,
                         'input_identity': input_identity,
                         'validation': validation, 'artifacts': artifacts})
    runtime, reason = classify(attempts, processes, bool(errors))
    identity_passed = all(i['identity_passed'] for i in identities.values())
    if runtime == 'complete-success' and not identity_passed:
        runtime, reason = 'complete-fail', 'immutable source/contract byte identity mismatch'
    accepted = runtime == 'complete-success'
    return {'schema': 'C10-recovery-1', 'observed_utc': utc(), 'root': str(root),
            'case_id': CASE_ID, 'search_roots': searches, 'search_errors': errors,
            'runtime_class': runtime, 'reason': reason, 'identity': identities,
            'processes': processes, 'attempts': attempts, 'all_roots_accessible': not errors,
            'claim_verdict': 'finite-model-accepted' if accepted else 'not-admitted',
            'validation': {'passed': accepted, 'file': 'validation.json'},
            'durable_storage': {'status': 'not-published', 'destinations': []},
            'next_execution': 'No automatic launch. Diagnose actual failure or unrecoverable absence and follow the separate bounded manual template.',
            'historical_evidence': {'archive_sha256': '725cf8bf53d366b179d41708c4efc9477b29c6c6e0a748ac2d3585dbe33709a1',
                                    'observation': 'Unit2 running snapshot only; not current runtime or terminal evidence'},
            'scientific_scope': 'finite common-space Li to Be+ projection only; all eight physical closure flags open'}


def copy_checked(source, destination):
    before = fingerprint(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copyfile(source, destination)
        after = fingerprint(source)
        copied = fingerprint(destination)
        stable = (before['stable'] and after['stable'] and copied['stable']
                  and before.get('stat') == after.get('stat')
                  and before.get('sha256') == after.get('sha256') == copied.get('sha256'))
        return {'source': str(source), 'destination': str(destination), 'stable': stable,
                'before': before, 'after': after, 'copied_sha256': copied.get('sha256')}
    except OSError as e:
        return {'source': str(source), 'destination': str(destination), 'stable': False, 'error': str(e)}


def write_evidence(observation, out, collect=False, command=None):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    dump(out / 'runtime_identity.json', runtime_identity())
    dump(out / 'process_snapshot.json', observation['processes'])
    copies = []
    if collect:
        for index, attempt in enumerate(observation['attempts']):
            source_dir = Path(attempt['path'])
            for artifact in attempt['artifacts']:
                source = Path(artifact['path'])
                active_process = any(p['active'] for p in observation['processes'])
                if source.suffix == '.npz' and (observation['runtime_class'] in ('in-progress', 'unknown')
                                               or active_process or not artifact['stable']):
                    copies.append({'source': str(source), 'skipped': 'changing/nonterminal NPZ is not a terminal result', 'stable': True})
                    continue
                destination = out / 'attempts' / ('%03d' % index) / source.relative_to(source_dir)
                copied = copy_checked(source, destination)
                copied['stable'] = (copied['stable'] and copied.get('before', {}).get('sha256') == artifact.get('sha256')
                                    and copied.get('before', {}).get('stat') == artifact.get('stat'))
                copies.append(copied)
            for name in ('case_deck.json', 'run_manifest.json', 'manifest.json', 'SHA256SUMS', 'summary.json'):
                source = source_dir.parent / name
                if source.is_file():
                    copies.append(copy_checked(source, out / 'attempts' / ('%03d' % index) / 'parent' / name))
        # Identity recheck is essential after copying, even if source was initially valid.
        post = inspect(observation['root'], observation['search_roots'][1:])
        dump(out / 'post_collection_inspection.json', post)
        unstable = any(not c['stable'] for c in copies)
        if post['runtime_class'] != observation['runtime_class'] or unstable:
            observation['runtime_class'] = 'unknown'
            observation['claim_verdict'] = 'not-admitted'
            observation['validation']['passed'] = False
            observation['reason'] = 'source mutation/state transition during collection; acceptance deferred'
        observation['post_collection_runtime_class'] = post['runtime_class']
    observation['collection'] = {'performed': collect, 'files': copies,
                                 'nonterminal_snapshot': observation['runtime_class'] in ('in-progress', 'stale', 'missing', 'unknown', 'conflict')}
    dump(out / 'validation.json', {a['path']: a['validation'] for a in observation['attempts']})
    dump(out / 'inspection.json', observation)
    (out / 'STATUS.md').write_text(
        '# C10 recovery observation\n\n'
        f"Observed UTC: {observation['observed_utc']}\n\n"
        f"runtime_class: {observation['runtime_class']}\n\n"
        f"claim_verdict: {observation['claim_verdict']}\n\n"
        f"validation: {observation['validation']['passed']}\n\n"
        'durable_storage: not-published\n\n'
        f"Reason: {observation['reason']}\n\n"
        'Historical Unit2 snapshot is separate from this observation. No solver was launched.\n'
        'No iterative checkpoint is available; data.tmp.npz is evidence only.\n'
        'All eight physical closure flags remain open.\n')
    stdout = json.dumps({'runtime_class': observation['runtime_class'], 'out': str(out),
                         'reason': observation['reason']}, sort_keys=True) + '\n'
    exit_code = 2 if observation['runtime_class'] in ('unknown', 'conflict') else 0
    (out / 'collector.stdout.log').write_text(stdout)
    (out / 'collector.stderr.log').write_text('')
    dump(out / 'collector_execution.json', {'command': command or sys.argv, 'exit_code': exit_code,
                                           'stdout': 'collector.stdout.log', 'stderr': 'collector.stderr.log',
                                           'purpose': 'collector exit 0 does not imply numerical acceptance'})
    manifest = []
    for path in sorted(out.rglob('*')):
        if path.is_file():
            manifest.append(f"{sha(path)}  {path.relative_to(out)}")
    (out / 'SHA256SUMS').write_text('\n'.join(manifest) + '\n')
    archive = out.parent / (out.name + '.tar.gz')
    if archive.exists():
        raise FileExistsError('refusing to replace recovery archive: ' + str(archive))
    with tarfile.open(archive, 'w:gz') as tar:
        tar.add(out, arcname=out.name)
    dump(out.parent / (out.name + '.archive.json'), {'path': str(archive), 'size': archive.stat().st_size,
                                                  'sha256': sha(archive), 'durable_storage': 'not-published'})
    return stdout, exit_code


def parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''NCP commands (run locally on NCP; no remote session is created):
  python3 recover_c10.py inspect --root /root/REI_MICROPHYSICS_R9_20261015 --out /root/REI_C10_RECOVERY_<UTC>
  python3 recover_c10.py collect --root /root/REI_MICROPHYSICS_R9_20261015 --out /root/REI_C10_COLLECTION_<UTC>

Use a never-existing --out. collect copies stable evidence and creates a sibling
tar.gz plus archive checksum/size receipt; publication remains a separate action.
Only NPZ validation needs NumPy. Frozen physics requires requirements.lock.
No command runs the solver, retries, terminates workers, or changes original files.''')
    sub = p.add_subparsers(dest='action', required=True)
    for action in ('inspect', 'collect'):
        q = sub.add_parser(action)
        q.add_argument('--root', type=Path, required=True)
        q.add_argument('--out', type=Path, required=True)
        q.add_argument('--extra-run-root', action='append', default=[], type=Path)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        # Keep collector outputs outside all searched run trees.
        observation = inspect(args.root, args.extra_run_root)
        for path in observation['search_roots']:
            if args.out.resolve().is_relative_to(Path(path).resolve()):
                raise ValueError('--out must be outside searched run trees')
        stdout, code = write_evidence(observation, args.out, args.action == 'collect')
        print(stdout, end='')
        return code
    except (OSError, ValueError) as e:
        print('ERROR: ' + str(e), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
