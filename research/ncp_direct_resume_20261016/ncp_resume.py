#!/usr/bin/env python3
"""NCP-local observation and one mechanical profile preparation; stdlib only.

No command starts, resumes, signals, or changes the full science campaign.
The historical profile helper is retained, but its CLI is disabled: the one
authorized repair/build/diagnostic was completed and its allowance is exhausted.
"""
import argparse
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time

STAGE = Path('/root/REI_FLRW_COVARIANT_20261015_005')
PROFILE = Path('/root/REI_FLRW_HPC_PROFILE_20261015_003')
EPOCH = 1792075817.77407
DEADLINE = 1792119017.77407
SOURCE_SHA = '1a2268e3da98ed47159cb738762a1a3d3d17bdcb6806e611cbd2bc3c0c6eaff7'
BINARY_SHA = '4aa337414a275c66068a900b8349a4114ddc1b1eebad1d904b61cbbd3da84fd4'
CASES = ('FLRW_FULL_Q512_001', 'FLRW_FULL_Q1024_001')
BAD_NEWLINE = b'\\n    let started = Instant::now();'
GOOD_NEWLINE = b'\n    let started = Instant::now();'
GIB = 1024 ** 3


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write_new(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')


def read_json(path):
    try:
        return {'path': str(path), 'data': json.loads(path.read_text())}
    except (OSError, ValueError) as e:
        return {'path': str(path), 'read_error': str(e)}


def fields(path):
    return dict(line.split('=', 1) for line in path.read_text().splitlines()
                if line and not line.startswith('#'))


def checkpoint(path):
    try:
        with path.open() as f:
            version, values, counts = (next(f).strip() for _ in range(3))
        v, c = list(map(float, values.split())), list(map(int, counts.split()))
        if len(v) != 11 or len(c) != 6 or not all(math.isfinite(x) for x in v) or v[0] <= 0:
            raise ValueError('unexpected checkpoint shape/domain')
        return dict(path=str(path), version=version, a=v[0], zbar=1 / v[0] - 1,
                    accepted=c[0], attempts=c[1], rejections=c[2], rhs_evaluations=c[4],
                    comparisons=c[5], native_wall_s=v[10])
    except (OSError, ValueError, StopIteration) as e:
        return {'path': str(path), 'read_error': str(e)}


def inventory(root):
    result = {'path': str(root), 'exists': root.is_dir(), 'file_count': 0,
              'bytes': 0, 'files': [], 'read_errors': []}
    if not root.is_dir():
        return result
    def error(e):
        result['read_errors'].append(str(e))
    for directory, dirs, names in os.walk(root, followlinks=False, onerror=error):
        dirs[:] = sorted(d for d in dirs if not (Path(directory) / d).is_symlink())
        for name in sorted(names):
            p = Path(directory) / name
            if p.is_symlink():
                continue
            try:
                s = p.stat()
                result['files'].append({'path': str(p.relative_to(root)), 'bytes': s.st_size,
                                        'mtime_ns': s.st_mtime_ns})
                result['file_count'] += 1
                result['bytes'] += s.st_size
            except OSError as e:
                error(e)
    return result


def arg_value(argv, option):
    try:
        return argv[argv.index(option) + 1]
    except (ValueError, IndexError):
        return None


def process_role(argv, stage, campaign):
    """Match actual argv tokens and case/config/output binding, never saved PIDs."""
    binary = str(stage / 'target/release/examples/axbi_reionization')
    for case in CASES:
        config = str(campaign / 'launches' / (case + '.runtime.cfg'))
        output = str(campaign / 'runs' / case)
        if binary in argv and arg_value(argv, '--config') == config and arg_value(argv, '--output') == output and arg_value(argv, '--case') == case:
            return case
    for token in argv:
        p = Path(token)
        if p.name == 'full_control.py' and p.is_absolute() and (p.parent == stage or stage in p.parents):
            plan = arg_value(argv, '--plan')
            if plan and Path(plan).is_absolute() and stage in Path(plan).parents:
                return 'full_controller'
    return None


def process_observation(stage, campaign, proc_root=Path('/proc')):
    result = {'matched': [], 'host_process_count': 0, 'unreadable_process_count': 0,
              'match_rule': 'actual argv: exact native binary/config/output/case; stage-owned controller script/plan'}
    try:
        entries = list(proc_root.iterdir())
    except OSError as e:
        result['read_error'] = str(e)
        return result
    for p in entries:
        if not p.name.isdigit():
            continue
        result['host_process_count'] += 1
        try:
            argv = [x.decode(errors='replace') for x in (p / 'cmdline').read_bytes().split(b'\0') if x]
            role = process_role(argv, stage, campaign)
            if not role:
                continue
            v = (p / 'stat').read_text().rsplit(')', 1)[1].split()
            status = dict(line.split(':', 1) for line in (p / 'status').read_text().splitlines() if ':' in line)
            result['matched'].append({'pid': int(p.name), 'role': role, 'argv': argv,
                'state': v[0], 'start_ticks': int(v[19]),
                'cpu_s': (int(v[11]) + int(v[12])) / os.sysconf('SC_CLK_TCK'),
                'rss_bytes': int(v[21]) * os.sysconf('SC_PAGE_SIZE'), 'os_threads': int(v[17]),
                'allowed_cpus': status.get('Cpus_allowed_list', '').strip()})
        except (OSError, ValueError, IndexError):
            result['unreadable_process_count'] += 1
    result['matched_rss_bytes'] = sum(p['rss_bytes'] for p in result['matched'])
    result['matched_os_threads'] = sum(p['os_threads'] for p in result['matched'])
    result['matched_cpu_s'] = sum(p['cpu_s'] for p in result['matched'])
    return result


def status(stage, proc_root=Path('/proc')):
    stage = stage.resolve()
    campaign = stage / 'full_campaign001'
    epoch = read_json(campaign / 'campaign_epoch.json')
    ev = epoch.get('data', {})
    epoch_match = ev.get('first_full_launch_epoch') == EPOCH and ev.get('deadline_epoch') == DEADLINE
    processes = process_observation(stage, campaign, proc_root)
    cases = []
    try:
        binary_match = sha(stage / 'target/release/examples/axbi_reionization') == BINARY_SHA
    except OSError:
        binary_match = False
    for case in CASES:
        out = campaign / 'runs' / case
        receipt = read_json(campaign / 'launches' / (case + '.receipt.json'))
        rv = receipt.get('data', {})
        try:
            native = fields(out / 'RETURN.txt')
            source_match = sha(out / 'source_identity.txt') == SOURCE_SHA
            config_match = (out / 'config.cfg').read_bytes() == (campaign / 'launches' / (case + '.runtime.cfg')).read_bytes()
            complete = (native['status'] == 'COMPLETE_REPRESENTED_INTERVAL' and native['result'] == 'Ok(())'
                        and float(native['a']) == .2 and rv.get('returncode') == 0
                        and rv.get('native_completion_proof') is True and rv.get('stop_reason') is None
                        and rv.get('source_config_binary_bindings_match') is True
                        and rv.get('source_identity_sha256') == SOURCE_SHA and rv.get('binary_sha256') == BINARY_SHA
                        and source_match and config_match and binary_match and epoch_match)
            native_read = {'path': str(out / 'RETURN.txt'), 'data': native}
        except (OSError, KeyError, ValueError) as e:
            native_read, complete = {'path': str(out / 'RETURN.txt'), 'read_error': str(e)}, False
        live = any(p['role'] == case and p['state'] != 'Z' for p in processes['matched'])
        cases.append({'case': case, 'live_command_match': live, 'checkpoint': checkpoint(out / 'checkpoint.txt'),
                      'native_return': native_read, 'terminal_receipt': receipt,
                      'observed_terminal_completion_evidence': bool(complete and not live), 'artifacts': inventory(out)})
    live = any(p['state'] != 'Z' for p in processes['matched'])
    label = ('OBSERVED_LIVE_INCOMPLETE' if live else
             'OBSERVED_TERMINAL_NATIVE_COMPLETION_PENDING_REVIEW' if all(c['observed_terminal_completion_evidence'] for c in cases) and 'read_error' not in processes else
             'OBSERVED_INCOMPLETE_OR_UNAVAILABLE')
    resources = {'logical_cpus': os.cpu_count(), 'sample_kind': 'single_snapshot_no_busy_core_estimate'}
    try:
        resources['observer_allowed_cpus'] = sorted(os.sched_getaffinity(0))
        resources['disk_free_bytes'] = shutil.disk_usage(stage).free
        resources['host_memory_bytes'] = {k: int(v.strip().split()[0]) * 1024 for k, v in
            (line.split(':', 1) for line in (proc_root / 'meminfo').read_text().splitlines()) if k in ('MemTotal', 'MemAvailable')}
    except OSError as e:
        resources['read_error'] = str(e)
    return {'schema': 'rei.ncp_direct_status.v1', 'observed_utc': utc(), 'status': label,
        'stage': str(stage), 'stage_exists': stage.is_dir(), 'campaign': str(campaign),
        'frozen_epoch': EPOCH, 'frozen_deadline_epoch': DEADLINE, 'science_hard_stop_epoch': DEADLINE - 300,
        'epoch_readback': epoch, 'epoch_matches_frozen': epoch_match,
        'deadline_elapsed': time.time() >= DEADLINE, 'epoch_modified': False,
        'processes': processes, 'resources': resources, 'cases': cases,
        'controller_status': read_json(campaign / 'full_campaign.status.json'),
        'controller_terminal': read_json(campaign / 'full_campaign.receipt.json'),
        'scientific_admission': 'NOT_ISSUED', 'solver_launched_or_restarted': False,
        'limitation': 'Filesystem/proc snapshot may race; no missing/incomplete artifact establishes completion.'}


def repair_profile(source, destination, execute=False):
    source, destination = source.resolve(), destination.resolve()
    if destination.exists() or destination == source or source in destination.parents:
        raise ValueError('destination must be fresh and outside original source')
    original = source / 'src/hpc_profile.rs'
    data = original.read_bytes()
    if data.count(BAD_NEWLINE) != 1:
        raise ValueError('expected exactly one literal backslash-n before started statement')
    if not (source / 'Cargo.toml').is_file() or not (source / 'Cargo.lock').is_file():
        raise ValueError('original Cargo.toml and Cargo.lock are required; do not invent them')
    destination.mkdir(parents=True)
    copied = []
    # Only build inputs; never copy target caches, credentials, or installed toolchains.
    for name in ('Cargo.toml', 'Cargo.lock', 'build.rs', 'src', 'examples', 'benches', 'tests'):
        p = source / name
        if not p.exists():
            continue
        q = destination / name
        if p.is_dir():
            shutil.copytree(p, q)
        else:
            shutil.copy2(p, q)
        copied.append(name)
    preserved = destination / 'preserved_attempt003'
    preserved.mkdir()
    shutil.copy2(original, preserved / 'hpc_profile.rs.original')
    for p in sorted(source.iterdir()):
        # Preserve top-level caller/config/checkpoint/log/receipt inputs, not binaries/caches.
        if p.is_file() and p.name not in copied and (p.suffix in ('.py', '.sh', '.cfg', '.log', '.json', '.txt') or 'receipt' in p.name.lower()):
            shutil.copy2(p, preserved / p.name)
    repaired = destination / 'src/hpc_profile.rs'
    repaired.write_bytes(data.replace(BAD_NEWLINE, GOOD_NEWLINE))
    source_refs = []
    for i, line in enumerate(data.decode(errors='replace').splitlines(), 1):
        if re.search(r'/root/|/home/|checkpoint|config|std::env|args\(|max_rhs|rhs_evaluations|max_wall|10000|10_000', line, re.I):
            source_refs.append({'line': i, 'text': line})
    manifest_text = (source / 'Cargo.toml').read_text()
    path_dependencies = re.findall(r'\bpath\s*=\s*"([^"]+)"', manifest_text)
    result = {'schema': 'rei.ncp_profile_preparation.v1', 'prepared_utc': utc(), 'status': 'PREPARED_NOT_EXECUTED',
        'source': str(source), 'destination': str(destination), 'copied_build_inputs': copied,
        'repair': 'one literal backslash-n to newline immediately before let started = Instant::now();',
        'original_source_sha256': hashlib.sha256(data).hexdigest(), 'repaired_source_sha256': sha(repaired),
        'original_source_unchanged': original.read_bytes() == data, 'path_dependencies_to_inspect': path_dependencies,
        'original_cargo_config_present': (source / '.cargo/config.toml').exists() or (source / '.cargo/config').exists(),
        'source_ownership_and_limit_references': source_refs, 'profile_executed': False,
        'build': {'status': 'NOT_REQUESTED'},
        'profile_limits': {'wall_s': 60, 'rhs_max': 10000, 'address_space_bytes': 8 * GIB,
                           'cpus': list(range(16, 32)), 'worker_width_max': 16},
        'prerequisites': ['Inspect original caller and src/hpc_profile.rs to establish exact argument grammar, input config/checkpoint ownership, and a native hard RHS ceiling <=10000.',
            'Confirm copied Cargo path dependencies/assets exist; do not substitute dependencies or reuse an entire target cache.',
            'The historical caller and hard RHS enforcement have not been established by this preparer. Do not guess or invoke the profile.'],
        'next_codex_instructions': [
            'Read preserved_attempt003/hpc_profile.rs.original and every preserved caller/config/checkpoint; identify their exact referenced paths. Preserve both earlier attempt directories and all failure evidence.',
            'Before any diagnostic invocation, show the exact command and source lines enforcing <=10000 RHS and <=60 seconds, with worker width <=16, CPUs16-31, and AS<=8GiB. If not established, stop PREPARED and report the missing prerequisite.',
            'Only after those prerequisites and an actually successful pinned Rust1.94.1 offline build may one diagnostic run occur in fresh output paths. Do not run or restart full_control.py or axbi_reionization, or reset campaign_epoch.json.'],
        'scientific_admission': 'NOT_ISSUED'}
    if execute:
        cargo = shutil.which('cargo')
        cpus = set(range(16, 32))
        if not cargo:
            result['build'] = {'status': 'PREREQUISITE_MISSING', 'reason': 'cargo unavailable; no toolchain installation authorized'}
        elif not hasattr(os, 'sched_getaffinity') or not cpus <= os.sched_getaffinity(0):
            result['build'] = {'status': 'PREREQUISITE_MISSING', 'reason': 'required CPUs16-31 are unavailable'}
        else:
            import resource
            def bounded_build():
                os.sched_setaffinity(0, cpus)
                resource.setrlimit(resource.RLIMIT_AS, (8 * GIB, 8 * GIB))
            command = [cargo, '+1.94.1', 'build', '--offline', '--locked', '--release']
            env = os.environ.copy()
            env.update(CARGO_BUILD_JOBS='16', CARGO_TARGET_DIR=str(destination / 'target'),
                       RUSTUP_AUTO_INSTALL='0', RAYON_NUM_THREADS='16', OMP_NUM_THREADS='1',
                       OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
            started = time.monotonic()
            with (destination / 'repair_build.log').open('x') as log:
                try:
                    process = subprocess.Popen(command, cwd=destination, env=env, stdout=log,
                        stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, preexec_fn=bounded_build,
                        start_new_session=True)
                    try:
                        code = process.wait(timeout=300)
                    except BaseException:
                        try:
                            os.killpg(process.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                        process.wait()
                        raise
                    result['build'] = {'status': 'PASS' if code == 0 else 'FAIL',
                                       'returncode': code, 'command': command}
                except (OSError, subprocess.TimeoutExpired) as e:
                    result['build'] = {'status': 'FAIL', 'command': command, 'error': str(e)}
            result['build']['elapsed_s'] = time.monotonic() - started
            result['build']['log'] = str(destination / 'repair_build.log')
    write_new(destination / 'REPAIR_PREPARED.json', result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', nargs='?', default='status', choices=('status', 'repair-profile'))
    parser.add_argument('--stage', type=Path, default=STAGE)
    parser.add_argument('--output', type=Path, required=True, help='fresh JSON file; never overwrite')
    parser.add_argument('--source', type=Path, default=PROFILE)
    parser.add_argument('--destination', type=Path)
    parser.add_argument('--execute', action='store_true', help='historical option; repair-profile allowance is exhausted')
    args = parser.parse_args(argv)
    if args.action == 'repair-profile':
        # Current published evidence supersedes the earlier pending-repair handoff.
        # Reject before source inspection, destination creation, output write or build.
        # This consumed allowance is fixed even if the evidence is not copied beside
        # a standalone script; missing packaging cannot grant another execution.
        print(json.dumps({'status': 'ALREADY_COMPLETED', 'reason': 'ALLOWANCE_EXHAUSTED',
            'evidence_commit': '37ea9e601e173d2be6676bfa5ed02fab71192d94',
            'evidence': 'research/flrw_covariant_transport_20261015/resume_20261016_001/profile/public/MEASURED_RESULT.json',
            'remaining_builds': 0, 'remaining_runs': 0, 'repair_performed': False,
            'build_attempted': False, 'profile_executed': False, 'output_written': False}))
        return 3
    if args.output.exists():
        parser.error('--output must be a fresh path')
    if args.action == 'status':
        if args.execute or args.destination:
            parser.error('status is read-only; execution/destination options do not apply')
        # Keep observer output out of the campaign it observes.
        if args.stage.resolve() in args.output.resolve().parents:
            parser.error('--output must be outside the observed stage')
        value = status(args.stage)
    else:
        if args.destination is None:
            parser.error('repair-profile requires --destination')
        if args.source.resolve() in args.output.resolve().parents:
            parser.error('--output must be outside the preserved original profile stage')
        value = repair_profile(args.source, args.destination, args.execute)
    write_new(args.output, value)
    print(json.dumps({'status': value['status'], 'output': str(args.output), 'profile_executed': value.get('profile_executed', False)}))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print('ncp_resume: ' + str(exc), file=sys.stderr)
        raise SystemExit(2)
