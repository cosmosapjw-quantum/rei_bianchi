"""Execute the four owner-approved, unmodified programs once, with durable caps."""
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import time

ROOT = Path('/root/REI_PR171_READY_20261018_001')
PACKET = json.loads((ROOT / 'APPROVED_EXECUTION_PACKET.json').read_text())
AS = PACKET['control']['per_solve_AS_bytes']
RSS = PACKET['control']['per_case_process_tree_RSS_bytes']
OUT = PACKET['control']['aggregate_output_bytes']
PAGE = os.sysconf('SC_PAGE_SIZE')
TICKS = os.sysconf('SC_CLK_TCK')

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def write(name, value):
    path = ROOT / name
    temporary = path.with_name(path.name + '.writing')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)

def members(group):
    rows = []
    for name in os.listdir('/proc'):
        if not name.isdigit():
            continue
        try:
            raw = Path('/proc', name, 'stat').read_text()
            fields = raw[raw.rfind(')') + 2:].split()
            if int(fields[2]) == group:
                rows.append({'pid': int(name), 'state': fields[0],
                             'rss_bytes': int(fields[21]) * PAGE,
                             'cpu_s': (int(fields[11]) + int(fields[12])) / TICKS,
                             'threads': int(fields[17])})
        except (OSError, ValueError, IndexError):
            pass
    return rows

def output_bytes():
    total = 0
    for directory in ('outputs', 'logs'):
        for here, _, files in os.walk(ROOT / directory):
            for name in files:
                try:
                    total += (Path(here) / name).stat().st_size
                except FileNotFoundError:
                    pass
    return total

def limits():
    resource.setrlimit(resource.RLIMIT_AS, (AS, AS))
    resource.setrlimit(resource.RLIMIT_FSIZE, (OUT, OUT))

def kill_group(group):
    try:
        os.killpg(group, signal.SIGKILL)
    except ProcessLookupError:
        pass

def semantic(command):
    args = command['argv']
    if command['name'].endswith('_reference'):
        destination = Path(args[3])
        result = json.loads((destination / 'solver_return.json').read_text())
        if result['status'] != 'SCOPED_NUMERICAL_EXECUTION_COMPLETE':
            return {'failure': 'RETURNED_SCIENTIFIC_HOLD', 'solver_return': result}
        if result['calls'] > command['RHS_cap']:
            return {'failure': 'RHS_CAP', 'solver_return': result}
        setup = json.loads((destination / 'setup.json').read_text())
        expected = {'birth_count': int(args[args.index('--birth-panels') + 1]),
                    'n_mu': 8, 'source_subdivisions': 8,
                    'transport_cells': int(args[args.index('--transport-cells') + 1])}
        if any(setup[k] != v for k, v in expected.items()):
            return {'failure': 'CONFIG_BINDING', 'expected': expected}
        ledger = json.loads((destination / 'ledgers.json').read_text())
    else:
        destination = Path(args[3])
        result = None
        ledger = None
    endpoint = json.loads((destination / 'endpoint.json').read_text())
    for key in ('N', 'U', 'temperature_K', 'proper_time_s'):
        if not math.isfinite(endpoint[key]):
            return {'failure': 'NONFINITE_ENDPOINT', 'field': key}
    return {'failure': None, 'solver_return': result, 'ledgers': ledger,
            'endpoint': {key: endpoint[key] for key in
                         ('N', 'U', 'temperature_K', 'proper_time_s')},
            'observation_rows': len(json.loads((destination / 'observations.json').read_text()))}

def main():
    assert PACKET['user_approval_received']
    assert not (ROOT / 'ALLOCATION.json').exists(), 'Existing allocation must be observed, never relaunched'
    binding = json.loads((ROOT / 'inputs/SOURCE_BINDING.json').read_text())
    for item in binding['payloads']:
        data = (ROOT / 'inputs' / item['path']).read_bytes()
        assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
    (ROOT / 'outputs').mkdir()
    (ROOT / 'logs').mkdir()
    started_epoch = time.time()
    started = time.monotonic()
    deadline = started + PACKET['control']['new_unit_wall_cap_s']
    allocation = {'node_id': PACKET['node_id'], 'owner_reply': PACKET['owner_reply'],
                  'start_epoch': started_epoch, 'start_utc': utc(),
                  'deadline_epoch': started_epoch + PACKET['control']['new_unit_wall_cap_s'],
                  'wall_cap_s': PACKET['control']['new_unit_wall_cap_s'],
                  'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                  'supervisor_pid': os.getpid(), 'old_allocations_reset': False,
                  'source_binding': binding, 'original_packet': PACKET}
    write('ALLOCATION.json', allocation)
    results = []
    status = {'state': 'RUNNING', 'allocation': allocation, 'commands': results,
              'scientific_admission': 'NOT_ISSUED', 'GOAL_DONE': False}
    write('STATUS.json', status)
    env = os.environ.copy()
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        env[key] = '1'
    for command in PACKET['commands']:
        case_started = time.monotonic()
        if case_started >= deadline:
            status['state'] = 'STOP_ALLOCATION_DEADLINE'
            break
        cap = min(command['cap_s'], deadline - case_started)
        name = command['name']
        stdout_path = ROOT / 'logs' / (name + '.stdout')
        stderr_path = ROOT / 'logs' / (name + '.stderr')
        record = {'name': name, 'argv': command['argv'], 'cwd': str(ROOT),
                  'started_utc': utc(), 'effective_wall_cap_s': cap,
                  'AS_bytes': AS, 'tree_RSS_cap_bytes': RSS,
                  'stdout': str(stdout_path), 'stderr': str(stderr_path)}
        peak_rss = 0
        peak_cpu = 0.0
        stop = None
        last_telemetry = 0.0
        with stdout_path.open('wb') as stdout, stderr_path.open('wb') as stderr:
            child = subprocess.Popen(command['argv'], cwd=ROOT, env=env,
                                     stdout=stdout, stderr=stderr,
                                     start_new_session=True, preexec_fn=limits)
            record.update(pid=child.pid, pgid=child.pid)
            status['current_command'] = record
            write('STATUS.json', status)
            while True:
                pid, wait_status, usage = os.wait4(child.pid, os.WNOHANG)
                if pid:
                    child.returncode = os.waitstatus_to_exitcode(wait_status)
                    break
                observed = members(child.pid)
                tree_rss = sum(x['rss_bytes'] for x in observed)
                peak_rss = max(peak_rss, tree_rss)
                peak_cpu = max(peak_cpu, sum(x['cpu_s'] for x in observed))
                elapsed = time.monotonic() - case_started
                size = output_bytes()
                if elapsed >= cap or time.monotonic() >= deadline:
                    stop = 'WALL_CAP'
                elif tree_rss > RSS:
                    stop = 'TREE_RSS_CAP'
                elif size > OUT:
                    stop = 'OUTPUT_CAP'
                if stop:
                    kill_group(child.pid)
                    _, wait_status, usage = os.wait4(child.pid, 0)
                    child.returncode = os.waitstatus_to_exitcode(wait_status)
                    break
                if time.monotonic() - last_telemetry >= 5:
                    record.update(elapsed_s=elapsed, tree_RSS_bytes=tree_rss,
                                  observed_tree_CPU_s=peak_cpu,
                                  process_tree=observed, aggregate_output_bytes=size)
                    write('STATUS.json', status)
                    last_telemetry = time.monotonic()
                time.sleep(0.20)
        residual = [x for x in members(child.pid) if x['state'] != 'Z']
        if residual:
            kill_group(child.pid)
            stop = stop or 'ORPHANED_HELPER_STOP'
        record.update(exit=child.returncode, wall_s=time.monotonic() - case_started,
                      CPU_user_s=usage.ru_utime, CPU_system_s=usage.ru_stime,
                      wait4_peak_RSS_bytes=usage.ru_maxrss * 1024,
                      observed_peak_tree_RSS_bytes=peak_rss,
                      observed_tree_CPU_s=peak_cpu, stop_reason=stop,
                      completed_utc=utc())
        if child.returncode == 0 and stop is None:
            try:
                record['semantic_return'] = semantic(command)
            except Exception as error:
                record['semantic_return'] = {'failure': 'RETURN_PARSE_OR_MISSING',
                                             'error': repr(error)}
        results.append(record)
        write('EXECUTION.json', results)
        if child.returncode or stop or record.get('semantic_return', {}).get('failure'):
            status['state'] = 'STOP_FIRST_FAILURE'
            break
    else:
        status['state'] = 'COMPLETE_APPROVED_FOUR_COMMANDS'
    status.pop('current_command', None)
    status.update(commands=results, wall_s=time.monotonic() - started,
                  completed_utc=utc(), aggregate_output_bytes=output_bytes(),
                  next_unstarted=[x['name'] for x in PACKET['commands'][len(results):]],
                  program_source_changes=0, controller_retries=0,
                  original_deadlines_reset=False)
    write('STATUS.json', status)
    write('RETURN.json', status)

if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        write('SUPERVISOR_FAILURE.json', {'utc': utc(), 'error': repr(error),
                                        'supervisor_pid': os.getpid(),
                                        'scientific_admission': 'NOT_ISSUED'})
        raise
