#!/usr/bin/env python3
"""One-shot HALF_PLUS launcher. Preparation and --preflight never start science.

--launch requires a fresh controller release after independent launcher review.
The bound science output and raw directory are created only by the executable.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[6]
OWN = Path(__file__).resolve().parent
BASE = ROOT / 'research/axbi_goal_20261014/driver/full/half_plus_continuation_001'
AUTH = ROOT / 'research/axbi_goal_20261014/driver/full/epoch_recovery_001/plus/classifier_repair_001/AUTHORITY.json'
REVIEW = BASE / 'INDEPENDENT_BINDING_REVIEW.json'
AUTH_SHA = '517461debeda6a1ce669c4bce643a3adc521d12c917f393a4460b518d8ae54a4'
REVIEW_SHA = '40fd012799db0cafa7ec3ff9ff3d96a9abd7d1376ec6a057a352053c6354a1fc'
PLUS = ROOT / 'research/axbi_goal_20261014/driver/full/epoch_recovery_001/plus/recovery_001/runtime_001/POST_PLUS_RECEIPT.json'
OUT = ROOT / 'research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_HALF_PLUS_continuation_001'
RAW = ROOT / 'research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_HALF_PLUS_continuation_001_raw'
MIB = 1024 * 1024
EXPECTED = {
    'authority': (BASE / 'AUTHORITY.json', '381197bc970eff137879500e7528e57e7e0d9d9fc8538528d802201760d47907'),
    'binding': (BASE / 'EXECUTION.binding', '6db5f0c8dca77e920f0fb670d6ed0bd7b11667054381c790f0efdb6fb1278704'),
    'binding_authority': (BASE / 'EXECUTION_AUTHORITY.binding', 'c0a9387df574dffe32da34b45a6fbdda49591cdbc4ed793b5f403f4377a8527e'),
    'binary': (ROOT / 'research/axbi_goal_20261014/driver/full/signed_continuation_001/repair_001/target/release/examples/axbi_signed_resource_continuation', '4243c744af3f3237ad0ca570b14fad8db4344f33be8fc29d8da9cfda8e811c74'),
    'predecessor_return': (ROOT / 'research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_HALF_PLUS/RETURN.txt', '9858eea30daa645c6771bcb1766e2fccda34d77a34d5908ccf07bc55488659c4'),
    'predecessor_checkpoint': (ROOT / 'research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_HALF_PLUS/checkpoint.txt', '4922d47a22aea178dccf889d36da50d1ba35a6fa473bc5b532f547fe8d015150'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


def durable(path, record):
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('x') as file:
        json.dump(record, file, indent=2, sort_keys=True)
        file.write('\n')
        file.flush()
        os.fsync(file.fileno())
    os.replace(tmp, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def proc_record(pid):
    p = Path('/proc') / str(pid)
    try:
        stat = (p / 'stat').read_text()
        after = stat.rsplit(')', 1)[1].split()
        argv = [x.decode(errors='replace') for x in (p / 'cmdline').read_bytes().split(b'\0') if x]
        rss_kib = 0
        for line in (p / 'status').read_text().splitlines():
            if line.startswith('VmRSS:'):
                rss_kib = int(line.split()[1])
                break
        return {'pid': pid, 'pgid': int(after[2]), 'start_ticks': int(after[19]),
                'argv': argv, 'rss_kib': rss_kib}
    except (FileNotFoundError, ProcessLookupError):
        return None


def process_inventory():
    records = []
    for name in os.listdir('/proc'):
        if name.isdigit():
            record = proc_record(int(name))
            if record:
                records.append(record)
    return records


def is_science(record):
    argv = record['argv']
    return bool(argv) and Path(argv[0]).name.startswith('axbi_')


OWNERS = {'run_campaign.py', 'recover_queue.py', 'post_cap_dispatch.py',
          'post_plus_dispatch.py', 'post_plus_epoch_dispatch.py', 'recover_plus.py',
          'repaired_adapter.py', 'launcher.py'}


def scheduler_script(argv):
    if not argv:
        return None
    first = Path(argv[0]).name
    if first.endswith('.py'):
        return first
    if not first.startswith('python'):
        return None
    i = 1
    # Only actual interpreter option slots are skipped; never inspect data operands.
    while i < len(argv) and argv[i] in ('-u', '-B', '-E', '-I', '-s', '-S'):
        i += 1
    if i < len(argv) and argv[i].endswith('.py'):
        return Path(argv[i]).name
    return None


def bytes_under(path):
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    return sum(p.stat().st_size for p in path.rglob('*') if p.is_file())


def preflight():
    if sha(AUTH) != AUTH_SHA or sha(REVIEW) != REVIEW_SHA:
        raise RuntimeError('RELEASE_OR_REVIEW_IDENTITY_CHANGED')
    release = json.loads(AUTH.read_text())['HALF_PLUS_release']
    review = json.loads(REVIEW.read_text())
    plus = json.loads(PLUS.read_text())
    if review.get('binding_review') != 'PASS' or plus.get('status') != 'STOPPED_FOR_CLASSIFICATION':
        raise RuntimeError('REVIEW_OR_PLUS_STOP_NOT_PRESERVED')
    if plus.get('PLUS_attempted_starts') != 2 or plus.get('total_full_starts') != 7:
        raise RuntimeError('PLUS_ACCOUNTING_CHANGED')
    identities = {}
    for name, (path, expected) in EXPECTED.items():
        observed = sha(path)
        if observed != expected:
            raise RuntimeError('FROZEN_IDENTITY_CHANGED:' + name)
        identities[name] = observed
    if OUT.exists() or RAW.exists():
        raise RuntimeError('BOUND_OUTPUT_OR_RAW_EXISTS')
    if (OWN / 'RESERVATION.json').exists() or (OWN / 'PROCESS_ACK.json').exists():
        raise RuntimeError('ALREADY_RESERVED_NO_RETRY')
    records = process_inventory()
    old_observer = [r for r in records if r['pid'] == 1840885]
    old_group = [r for r in records if r['pgid'] == 1843269]
    if old_observer or old_group:
        # Without the original start tick, fail closed; never call a reused PID old work.
        raise RuntimeError('OLD_PID_OR_GROUP_OCCUPIED_NEEDS_START_IDENTITY')
    active = [r for r in records if is_science(r)]
    owners = [r for r in records if scheduler_script(r['argv']) in OWNERS and r['pid'] != os.getpid()]
    if active or owners:
        raise RuntimeError('ACTIVE_SCIENCE_OR_SCHEDULER_OWNER')
    free = shutil.disk_usage(OUT.parent).free
    mem_available_kib = next(int(x.split()[1]) for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:'))
    cpu0 = 0 in os.sched_getaffinity(0)
    if free < 4096 * MIB + 128 * MIB or mem_available_kib * 1024 < 2 * 1024**3 or not cpu0:
        raise RuntimeError('LOCAL_RESOURCE_NOT_AVAILABLE')
    if release['argv'][8:11] != ['/usr/bin/taskset', '-c', '0']:
        raise RuntimeError('FROZEN_CPU_ARGV_CHANGED')
    return {'utc': utc(), 'identities': identities, 'old_observer_pid': 1840885,
            'old_solver_pgid': 1843269, 'old_observer_and_group_absent': True,
            'active_local_science_groups': [], 'active_local_scheduler_owners': [],
            'output_absent': True, 'raw_absent': True, 'disk_free_bytes': free,
            'mem_available_kib': mem_available_kib, 'cpu0_allowed': cpu0,
            'outer_argv': release['argv'], 'scientific_admission': 'NOT_ISSUED'}


def validate_controller_release(path):
    release = json.loads(path.read_text())
    now = time.time()
    if release.get('decision') != 'AUTHORIZE_ONE_HALF_PLUS_START' or release.get('launcher_sha256') != sha(Path(__file__)):
        raise RuntimeError('INDEPENDENT_LAUNCHER_RELEASE_MISSING')
    if not all(release.get(k) is True for k in ('remote_checked', 'pending_checked', 'exclusive_launch_owner', 'plus_aborted_reservation_reconciled')):
        raise RuntimeError('GLOBAL_HANDOFF_NOT_RELEASED')
    if not isinstance(release.get('remote_observation'), dict) or not release.get('remote_observation'):
        raise RuntimeError('REMOTE_OBSERVATION_MISSING')
    if release.get('science_count_after_reservation', 3) > 2:
        raise RuntimeError('SHARED_MAX_TWO')
    when = release.get('observed_unix_s')
    if not isinstance(when, (int, float)) or now - when < 0 or now - when > 300:
        raise RuntimeError('REMOTE_PENDING_OBSERVATION_STALE')
    return release


def launch(release_path):
    controller = validate_controller_release(release_path)
    check = preflight()
    authority = json.loads(AUTH.read_text())['HALF_PLUS_release']
    argv = authority['argv']
    if argv != check['outer_argv'] or argv[-1] != EXPECTED['binding'][1]:
        raise RuntimeError('OUTER_ARGV_CHANGED')
    before_ack_accounting = {
        'original_starts': 5, 'ZERO_continuation_starts': 1,
        'PLUS_reserved_attempts': 2, 'PLUS_observed_starts': 1,
        'HALF_PLUS_attempts': 1, 'HALF_PLUS_observed_starts': 0,
        'full_observed_starts': 7, 'pilot_starts': 3,
        'history_observed_starts': 10,
    }
    after_ack_accounting = authority['accounting_after_Popen']
    reservation = {'utc': utc(), 'status': 'RESERVED_BEFORE_POPEN', 'one_start_no_retry': True,
                   'outer_argv': argv, 'preflight': check,
                   'controller_release_sha256': sha(release_path),
                   'accounting': before_ack_accounting,
                   'projected_only_if_Popen_succeeds': after_ack_accounting}
    with (OWN / 'RESERVATION.json').open('x') as stream:
        json.dump(reservation, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    env = os.environ.copy()
    env.update(authority['environment'])
    started = time.monotonic()
    proc = None
    reason = None
    try:
        with (OWN / 'stdout.log').open('xb') as stdout, (OWN / 'stderr.log').open('xb') as stderr:
            proc = subprocess.Popen(argv, cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                    stdout=stdout, stderr=stderr, start_new_session=True,
                                    close_fds=True)
            identity = proc_record(proc.pid)
            durable(OWN / 'PROCESS_ACK.json', {'utc': utc(), 'pid': proc.pid, 'pgid': proc.pid,
                    'start_ticks': identity['start_ticks'] if identity else None,
                    'argv': argv, 'status': 'PROCESS_ACKNOWLEDGED',
                    'accounting': after_ack_accounting})
            while proc.poll() is None:
                own = [r for r in process_inventory() if r['pgid'] == proc.pid]
                rss_bytes = sum(r['rss_kib'] for r in own) * 1024
                science_bytes = bytes_under(OUT)
                launcher_bytes = bytes_under(OWN) + bytes_under(RAW)
                elapsed = time.monotonic() - started
                if rss_bytes > 2147483648:
                    reason = 'RSS_CAP'
                elif science_bytes > 3968 * MIB:
                    reason = 'SCIENCE_OUTPUT_CAP'
                elif launcher_bytes > 128 * MIB:
                    reason = 'LAUNCHER_OUTPUT_CAP'
                elif science_bytes + launcher_bytes > 4096 * MIB:
                    reason = 'COMBINED_OUTPUT_CAP'
                elif elapsed > 10800:
                    reason = 'WALL_CAP'
                if reason:
                    # Only the acknowledged, still-live owned process group is signalled.
                    os.killpg(proc.pid, signal.SIGKILL)
                    break
                time.sleep(1)
            code = proc.wait()
        terminal = {'utc': utc(), 'status': 'TERMINAL_NEEDS_SCIENTIFIC_CLASSIFICATION',
                    'exit_code': code, 'stop_reason': reason,
                    'elapsed_wall_s': time.monotonic() - started,
                    'return_path': str(OUT / 'RETURN.txt') if (OUT / 'RETURN.txt').exists() else None,
                    'time_log_path': str(OWN / 'time.log') if (OWN / 'time.log').exists() else None,
                    'output_bytes': bytes_under(OUT), 'launcher_and_raw_bytes': bytes_under(OWN) + bytes_under(RAW),
                    'scientific_admission': 'NOT_ISSUED', 'automatic_retry': False,
                    'accounting': after_ack_accounting}
        durable(OWN / 'TERMINAL_RECEIPT.json', terminal)
        return code
    except BaseException as error:
        if proc is not None and proc.poll() is None:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
        durable(OWN / 'TERMINAL_RECEIPT.json', {'utc': utc(), 'status': 'LAUNCHER_EXCEPTION',
                'error': repr(error), 'process_acknowledged': proc is not None,
                'scientific_admission': 'NOT_ISSUED', 'automatic_retry': False,
                'accounting': after_ack_accounting if proc is not None else before_ack_accounting})
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--launch', action='store_true')
    parser.add_argument('--release', type=Path)
    args = parser.parse_args()
    if args.preflight == args.launch:
        parser.error('select exactly one of --preflight or --launch')
    if args.preflight:
        print(json.dumps(preflight(), indent=2))
        return 0
    if args.release is None:
        parser.error('--launch requires --release')
    return launch(args.release)


if __name__ == '__main__':
    raise SystemExit(main())
