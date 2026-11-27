"""Small cooperative Linux runner for the frozen 28-case REI pilot only."""
from __future__ import annotations
import argparse
import fcntl
import hashlib
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'vendor' / 'resources'))
from c21k_scheduler import resource_snapshot, acquire_cpu, THREAD_ENV
from bass_resources import _cpu_counters
GIB = 1 << 30
LEASES = Path('/tmp/cosmosapjw_hpc64_cpu_leases')


def observe(sample_seconds=.12):
    snapshot = resource_snapshot()
    cpus = [c for c in snapshot['affinity_cpu_ids'] if c != 55]
    first = _cpu_counters(cpus)
    started = time.monotonic()
    time.sleep(max(.12, sample_seconds))
    second = _cpu_counters(cpus)
    busy = {}
    for cpu in cpus:
        a, b = first.get(cpu), second.get(cpu)
        busy[cpu] = (max(0., min(1., 1 - (b[1]-a[1])/(b[0]-a[0])))
                     if a and b and b[0] > a[0] else 1.)
    snapshot.update(cpu_busy=busy, cpu_sample_seconds=time.monotonic()-started)
    return snapshot


def capacity(snapshot, pending, active=0, max_workers=64):
    cpus = sorted(set(snapshot['affinity_cpu_ids']) - {55},
                  key=lambda c: snapshot['cpu_busy'].get(c, 1.))
    quota = snapshot['cpu_quota']
    ceiling = min(64, len(cpus), math.floor(quota) if quota is not None else len(cpus))
    reserve_cpu = 2 if ceiling >= 8 else 1
    # Actual observed occupancy is charged even for jobs outside the lease protocol.
    busy = sum(snapshot['cpu_busy'].get(c, 1.) for c in cpus)
    cpu_new = max(0, math.floor(ceiling - min(ceiling, busy) - reserve_cpu))
    total = min(128*GIB, snapshot['memory_limit_bytes'])
    reserve_ram = max(4*GIB, math.ceil(total / 8))
    free = max(0, min(total, snapshot['memory_available_bytes']) - reserve_ram - active*GIB)
    slots = min(pending, max(0, max_workers-active), max(0, ceiling-reserve_cpu-active), cpu_new, free//GIB)
    return {'cpu_ids': cpus, 'new_workers': int(slots), 'cpu_ceiling': ceiling,
            'cpu_reserve': reserve_cpu, 'memory_reserve_bytes': reserve_ram,
            'per_job_budget_bytes': GIB, 'observed_busy_cpu_equivalents': busy}


def select_cpu(directory, cpus, occupied=()):
    for cpu in cpus:
        if cpu in occupied or cpu == 55:
            continue
        lease = acquire_cpu(directory, cpu)
        if lease is not None:
            return cpu, lease
    return None


def acquire_job(directory, identity):
    handle = (Path(directory) / ("rei_job_" + identity + ".lock")).open("a+b")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        return None
    return handle


def _worker(config, out, cpu, campaign="pilot"):
    os.environ.update(THREAD_ENV)
    os.sched_setaffinity(0, {cpu})
    import importlib
    api=importlib.import_module(campaign)
    api.write_case(config, Path(out))


def reusable(config, path, campaign="pilot"):
    import importlib
    pilot=importlib.import_module(campaign)
    try:
        return pilot.completed_result(config, Path(path))
    except (OSError, ValueError, KeyError):
        return False


def run(out, max_workers=64, seconds=60, dry_plan=False, lease_dir=LEASES, campaign="pilot"):
    import importlib
    pilot=importlib.import_module(campaign)
    cases = pilot.case_grid()
    out = Path(out).resolve()
    lease_dir = Path(lease_dir)
    if not dry_plan:
        out.mkdir(parents=True, exist_ok=True)
        lease_dir.mkdir(parents=True, exist_ok=True)
    statuses, pending = {}, []
    for config in cases:
        identity = pilot.case_identity(config)
        local = out / (config['case_id'] + '.json')
        registry = lease_dir / ('rei_' + identity + '.receipt.json')
        path = local
        if not reusable(config, path, campaign) and registry.exists():
            try:
                path = Path(json.loads(registry.read_text())['path'])
            except (OSError, ValueError, KeyError):
                path = local
        if reusable(config, path, campaign):
            statuses[config['case_id']] = {'status':'REUSED_COMPLETE', 'path':str(path)}
        else:
            pending.append((config, identity, registry))
    snapshot = observe()
    plan = capacity(snapshot, len(pending), max_workers=max_workers)
    if dry_plan:
        return {'status':'DRY_PLAN', 'pending':len(pending), 'reused':statuses, 'snapshot':snapshot, 'capacity':plan}
    ctx = mp.get_context('spawn')
    active = {}
    deadline = time.monotonic() + seconds
    try:
        while pending or active:
            for key, task in list(active.items()):
                proc, cpu_lock, job_lock, config, registry = task
                if proc.is_alive():
                    continue
                proc.join()
                path = out / (key + '.json')
                good = proc.exitcode == 0 and reusable(config, path, campaign)
                statuses[key] = {'status':'COMPLETE' if good else 'FAILED', 'path':str(path), 'exitcode':proc.exitcode}
                if good:
                    registry.write_text(json.dumps({'path':str(path), 'identity':pilot.case_identity(config)})+'\n')
                cpu_lock.close(); job_lock.close(); del active[key]
            if time.monotonic() >= deadline:
                break
            snapshot = observe()
            plan = capacity(snapshot, len(pending), len(active), max_workers)
            admitted = 0
            for item in list(pending):
                if admitted >= plan['new_workers']:
                    break
                config, identity, registry = item
                key = config['case_id']
                job_lock = acquire_job(lease_dir, identity)
                if job_lock is None:
                    statuses[key] = {'status':'DEFERRED', 'reason':'same_identity_running'}
                    pending.remove(item)
                    continue
                # Recheck under global job lock: another output root may just have completed.
                if registry.exists():
                    try:
                        prior = Path(json.loads(registry.read_text())['path'])
                        if reusable(config, prior, campaign):
                            statuses[key] = {'status':'REUSED_COMPLETE', 'path':str(prior)}
                            pending.remove(item); job_lock.close(); continue
                    except (OSError, ValueError, KeyError):
                        pass
                selected = select_cpu(lease_dir, plan['cpu_ids'], [t[0]._rei_cpu for t in active.values()])
                if selected is None:
                    job_lock.close(); break
                cpu, cpu_lock = selected
                proc = ctx.Process(target=_worker, args=(config, str(out), cpu, campaign))
                proc._rei_cpu = cpu
                try:
                    proc.start()
                except BaseException:
                    cpu_lock.close(); job_lock.close(); raise
                active[key] = (proc, cpu_lock, job_lock, config, registry)
                pending.remove(item); admitted += 1
            if not active and pending and not admitted:
                break
            if active:
                time.sleep(.05)
    finally:
        for key, (proc, cpu_lock, job_lock, config, registry) in active.items():
            if proc.is_alive():
                proc.terminate()  # Only this runner's direct child; science worker spawns no children.
            proc.join(timeout=2)
            if proc.is_alive():
                proc.kill(); proc.join()
            statuses[key] = {'status':'TIMED_OUT', 'exitcode':proc.exitcode}
            timeout_path = out / (key + '.runner_timeout.json')
            timeout_path.write_text(json.dumps({'config':config, 'identity':pilot.case_identity(config), 'status':'TIMED_OUT', 'cpu':proc._rei_cpu})+'\n')
            cpu_lock.close(); job_lock.close()
    for config, _, _ in pending:
        statuses[config['case_id']] = {'status':'DEFERRED', 'reason':'bounded_budget_or_capacity'}
    report = {'statuses':statuses, 'snapshot':snapshot, 'capacity':plan,
              'semantics':'Cooperating-runner leases only; other load observed, never signalled.'}
    (out / 'RUNNER_REPORT.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--campaign', choices=['pilot','split_pilot'],default='pilot')
    p.add_argument('--out', type=Path, default=ROOT/'data/results/cases')
    p.add_argument('--max-workers', type=int, default=64)
    p.add_argument('--time-budget-seconds', type=float, default=60)
    p.add_argument('--dry-plan', action='store_true')
    a = p.parse_args()
    if not 1 <= a.max_workers <= 64 or not 0 < a.time_budget_seconds <= 3600:
        p.error('workers 1..64 and bounded seconds (0,3600] required')
    print(json.dumps(run(a.out, a.max_workers, a.time_budget_seconds, a.dry_plan, campaign=a.campaign), indent=2))

if __name__ == '__main__':
    main()
