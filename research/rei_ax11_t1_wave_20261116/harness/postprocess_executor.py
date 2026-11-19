#!/usr/bin/env python3
"""Bind extraction/backup to the actual remaining original finite allocation.

Run only after the T1 controller has closed its ledger. The remaining science
caps are not enlarged. No native evolution, retry, or raw-file mutation occurs.
"""
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

from native_archive_t1 import identity


def save(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temp.replace(path)


def require(value, message):
    if not value:
        raise ValueError(message)


def main():
    root = Path(sys.argv[1]).resolve()
    begin, cpu0 = time.monotonic(), time.process_time()
    old = json.loads((root / 'RUN_LEDGER.json').read_text())
    require(old['status'] == 'T1_WAVE_FINISHED_WITH_RETAINED_OUTCOMES', 'NATIVE_WAVE_STILL_RUNNING')
    started = root / 'POSTPROCESS_STARTED.json'
    require(not started.exists(), 'POSTPROCESS_ALREADY_STARTED_NO_AUTOMATIC_RETRY')
    allocation = json.loads((root / 'ALLOCATION.json').read_text())
    prior = old['current_allocation_debit']
    available_cpu = allocation['caps']['aggregate_CPU_s'] - prior['CPU_s']
    available_wall = allocation['caps']['aggregate_sum_job_wall_s'] - prior['wall_s']
    # Reserve the launcher's own CPU/non-child wall separately from children.
    child_pool = min(1800, math.floor(min(available_cpu, available_wall) - 10))
    require(child_pool >= 120, 'INSUFFICIENT_REMAINING_POSTPROCESS_ALLOCATION')
    expected = json.loads((root / 'POSTPROCESS_PACKAGE_MANIFEST.json').read_text())
    for relative, spec in expected.items():
        got = identity(root / relative)
        require(got['sha256'] == spec['sha256'] and got['bytes'] == spec['bytes'],
                'POSTPROCESS_PACKAGE_IDENTITY:' + relative)
    binding = {'schema': 'REI_AX11_T1_POSTPROCESS_BINDING_V1',
               'closed_native_ledger_sha256': identity(root / 'RUN_LEDGER.json')['sha256'],
               'package_manifest_sha256': identity(root / 'POSTPROCESS_PACKAGE_MANIFEST.json')['sha256'],
               'prior_current_allocation_debit': prior,
               'original_aggregate_CPU_s': allocation['caps']['aggregate_CPU_s'],
               'original_aggregate_sum_wall_s': allocation['caps']['aggregate_sum_job_wall_s'],
               'available_CPU_s': available_cpu, 'available_sum_wall_s': available_wall,
               'controller_CPU_and_nonchild_wall_reservation_s': 10,
               'child_CPU_and_sum_wall_pool_s': child_pool,
               'extract_initial_cap_s': min(600, child_pool // 3),
               'archive_cap_rule': 'remaining child pool after actual extraction debit; max1200s',
               'max_child_memory_bytes': 2 * 1024**3,
               'starts': {'prior_native_setup_and_export': 1, 'this_controller': 1,
                          'maximum_children': 2, 'total_ceiling': 8},
               'automatic_retries': 0, 'new_evolution_starts': 0,
               'historical_accumulated_cost': 'UNKNOWN retained',
               'original_DAG': '10/17', 'expansion_DAG': '28/88'}
    save(root / 'POSTPROCESS_BINDING.json', binding)
    save(started, {'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'pid': os.getpid()})
    resource.setrlimit(resource.RLIMIT_CPU, (30, 18000))
    work = root / 'postprocess_logs_v1'
    work.mkdir()
    records = []
    state = {'status': 'POSTPROCESS_RUNNING', 'binding': binding, 'records': records}

    def run(name, command, cap):
        require(cap >= 10, 'CHILD_BUDGET_TOO_SMALL')
        usage = work / (name + '.usage.json')
        log = work / (name + '.log')
        actual = ['/usr/bin/time', '-q', '-f',
                  '{"user_s":%U,"system_s":%S,"elapsed_s":%e,"max_RSS_kB":%M,"exit":%x}',
                  '-o', str(usage), '/usr/bin/prlimit',
                  f'--cpu={cap - 2}:{cap - 1}', '--as=2147483648:2147483648', '--'] + command
        record = {'name': name, 'command': command, 'CPU_cap_s': cap,
                  'OS_CPU_soft_s': cap - 2, 'OS_CPU_hard_s': cap - 1, 'wall_cap_s': cap,
                  'status': 'STARTED'}
        records.append(record)
        save(root / 'POSTPROCESS_LEDGER.json', state)
        start = time.monotonic()
        with log.open('xb') as stream:
            process = subprocess.Popen(actual, stdout=stream, stderr=subprocess.STDOUT,
                                       start_new_session=True)
            record['pid'] = process.pid
            try:
                code = process.wait(timeout=cap - 3)
            except subprocess.TimeoutExpired:
                record['external_wall_termination'] = True
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    code = process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    code = process.wait()
        elapsed = time.monotonic() - start
        measured = None
        try:
            measured = json.loads(usage.read_text())
        except (ValueError, FileNotFoundError):
            pass
        record.update(returncode=code, wall_s=elapsed, status='FINISHED',
                      usage=measured, measured_CPU_available=measured is not None,
                      CPU_s=(measured['user_s'] + measured['system_s']) if measured else cap,
                      CPU_debit_is_cap_if_unmeasured=measured is None,
                      log_sha256=identity(log)['sha256'])
        save(root / 'POSTPROCESS_LEDGER.json', state)
        return record

    try:
        extract = run('extract', [sys.executable, str(root / 'harness/native_extract_t1.py'),
                                  str(root), str(root / 'analysis_v1')], binding['extract_initial_cap_s'])
        remaining = math.floor(child_pool - max(extract['CPU_s'], extract['wall_s']))
        if remaining >= 30:
            # Back up failures as well as successful analyses.
            run('archive', [sys.executable, str(root / 'harness/native_archive_t1.py'), str(root),
                            str(root / 'exports_v1'),
                            '/home/cosmosapjw/Dropbox/bianchi/rei_ax11_t1_wave_20261116_v1_archive'],
                min(1200, remaining))
        else:
            state['archive_deferred'] = 'INSUFFICIENT_REMAINING_CHILD_POOL'
        charged_cpu = sum(x['CPU_s'] for x in records) + 10
        charged_wall = sum(x['wall_s'] for x in records) + 10
        state.update(status='POSTPROCESS_FINISHED_WITH_RETAINED_OUTCOMES',
                     charged_CPU_s=charged_cpu, charged_sum_wall_s=charged_wall,
                     controller_actual_CPU_s=time.process_time() - cpu0,
                     controller_actual_nonchild_wall_s=time.monotonic() - begin - sum(x['wall_s'] for x in records),
                     current_allocation_CPU_s=prior['CPU_s'] + charged_cpu,
                     current_allocation_sum_wall_s=prior['wall_s'] + charged_wall,
                     original_DAG='10/17', expansion_DAG='28/88')
        require(state['controller_actual_CPU_s'] < 10, 'CONTROLLER_CPU_RESERVATION_EXCEEDED')
        require(state['controller_actual_nonchild_wall_s'] < 10, 'CONTROLLER_WALL_RESERVATION_EXCEEDED')
        require(state['current_allocation_CPU_s'] <= allocation['caps']['aggregate_CPU_s'], 'GLOBAL_CPU_CAP')
        require(state['current_allocation_sum_wall_s'] <= allocation['caps']['aggregate_sum_job_wall_s'], 'GLOBAL_WALL_CAP')
        save(root / 'POSTPROCESS_LEDGER.json', state)
        print(json.dumps(state, separators=(',', ':')))
    except BaseException as error:
        state.update(status='POSTPROCESS_FAILURE_PRESERVED_NO_RETRY', error=repr(error),
                     controller_actual_CPU_s=time.process_time() - cpu0,
                     controller_elapsed_wall_s=time.monotonic() - begin)
        save(root / 'POSTPROCESS_LEDGER.json', state)
        raise


if __name__ == '__main__':
    main()
