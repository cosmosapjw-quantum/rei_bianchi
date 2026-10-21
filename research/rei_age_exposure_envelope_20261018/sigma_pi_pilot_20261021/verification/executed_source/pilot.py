#!/usr/bin/env python3
"""Bounded, resumable source-free LRS Sigma/Pi pilot. See README.md."""
import os
for _key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
             'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_key] = '1'
import argparse
import csv
import hashlib
import io
import json
import multiprocessing as mp
import queue
import resource
import time
import traceback
from pathlib import Path

import adapter as ad
import resources as rs
import numpy as np
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parent
LIMITS = {'sandbox': {'workers': 4, 'case_s': 30., 'child_s': 240., 'controller_s': 180.},
          'ncp': {'workers': 63, 'case_s': 60., 'child_s': 1800., 'controller_s': 1200.}}


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name+'.tmp.'+str(os.getpid()))
    temp.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')
    os.replace(temp, path)


def atomic_npz(path, **values):
    path = Path(path)
    temp = path.with_name(path.name+'.tmp.'+str(os.getpid()))
    with temp.open('wb') as stream:
        np.savez_compressed(stream, **values)
    os.replace(temp, path)


def input_manifest():
    ad.verify_source()
    return {'schema': 'sigma_pi_pilot.v1', 'source': ad.SOURCE,
            'contract_sha256': hashlib.sha256((ROOT/'PILOT_CONTRACT.md').read_bytes()).hexdigest(),
            'cases': ad.cases(), 'nominal_cases': 91, 'guard_cases': 3,
            'scope': 'source-free LRS subset of non-tilted Bianchi I; collisionless gamma/nu + canonical massive + cold dust + Lambda',
            'norms': {'Sigma_F': 'sqrt(6)*abs(s)/H', 'Sigma_half': 'Sigma_F/sqrt(2)',
                      'Pi_F_signed': 'sqrt(6)*(8*pi*G/c^2)*pi_s/H^2'},
            'scientific_admission': 'PRELIMINARY_PENDING_RESULT_REVIEW'}


def plan(output):
    output = Path(output)
    manifest = input_manifest()
    path = output/'MANIFEST.json'
    if path.exists():
        if json.loads(path.read_text()) != manifest:
            raise ValueError('RESUME_MANIFEST_MISMATCH')
    else:
        atomic_json(path, manifest)
    return manifest


def resume_state(output, case):
    folder = Path(output)/'cases'/case['id']
    config_file = folder/'INPUT.json'
    if config_file.exists() and json.loads(config_file.read_text()) != case:
        raise ValueError('RESUME_CASE_IDENTITY_MISMATCH:'+case['id'])
    outcome = folder/'RESULT.json'
    if outcome.exists():
        result = json.loads(outcome.read_text())
        if result.get('id') != case['id'] or result.get('config') != case['config']:
            raise ValueError('RESUME_RESULT_IDENTITY_MISMATCH:'+case['id'])
        if result['status'] == 'COMPLETED' and not (folder/'raw.npz').exists():
            raise ValueError('RESUME_COMPLETED_RAW_MISSING:'+case['id'])
        return result['status']
    if (folder/'ATTEMPT.json').exists():
        return 'INCOMPLETE_PRESERVED'
    return 'PENDING'


def _worker(commands, replies):
    try:
        os.nice(10)
    except OSError:
        pass
    ad.verify_source()
    while True:
        task = commands.get()
        if task is None:
            break
        case, folder = task
        folder = Path(folder)
        begin = time.monotonic()
        result = {'id': case['id'], 'config': case['config'], 'exit': 1,
                  'status': 'FAILED', 'checks': {}}
        sol = None
        try:
            obj = ad.model(case['config'])
            # Same source DOP853 call and tolerances; retained here to save
            # partial solver states before any source/adapter validation raises.
            integrate_start = time.monotonic()
            sol = solve_ivp(obj.rhs, (0, obj.source.xmax), obj.initial_state(),
                t_eval=np.linspace(0, obj.source.xmax, 121), method='DOP853',
                rtol=3e-11, atol=3e-13)
            result['solver_wall_s'] = time.monotonic()-integrate_start
            atomic_npz(folder/'raw.npz', x=sol.t, raw_y=sol.y)
            result.update(nfev=int(sol.nfev), solver_message=sol.message)
            if not sol.success:
                raise RuntimeError('SOURCE_SOLVER_FAILED:'+sol.message)
            out = ad.observables(obj, sol)
            atomic_npz(folder/'raw.npz', x=sol.t, raw_y=sol.y, **out)
            checks = ad.validate(case['config'], sol, out)
            result.update(checks=checks, initial={k: float(v[0]) for k, v in out.items()},
                          endpoint={k: float(v[-1]) for k, v in out.items()},
                          maxima={'Hamiltonian_construction_residual': float(np.max(out['Hamiltonian_construction_residual']))})
            result['status'] = 'COMPLETED' if all(checks.values()) else 'FAILED_VALIDATION'
            result['exit'] = 0 if result['status'] == 'COMPLETED' else 2
        except BaseException as exc:
            result['error'] = str(exc)
            result['traceback'] = traceback.format_exc()
        result['worker_wall_s'] = time.monotonic()-begin
        result['peak_rss_bytes'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
        result['worker_pid'] = os.getpid()
        atomic_json(folder/'RESULT.json', result)
        replies.put((os.getpid(), case['id']))


def _approval(path, manifest):
    review = json.loads(Path(path).read_text())
    if review.get('decision') not in ('PASS', 'PASS_SCOPED_EXECUTION'):
        raise ValueError('CONTRACT_REVIEW_NOT_PASS')
    if review.get('contract_sha256') != manifest['contract_sha256']:
        raise ValueError('CONTRACT_REVIEW_IDENTITY_MISMATCH')
    return review


def run(output, profile, requested, resume, approval):
    output = Path(output)
    started = time.monotonic()
    manifest = plan(output)
    review = _approval(approval, manifest)
    limits = LIMITS[profile]
    if requested is not None and requested < 1:
        raise ValueError('max-workers must be positive')
    states = {case['id']: resume_state(output, case) for case in manifest['cases']}
    if not resume and any(v != 'PENDING' for v in states.values()):
        raise ValueError('EXISTING_ATTEMPTS_REQUIRE_RESUME')
    pending = [c for c in manifest['cases'] if states[c['id']] == 'PENDING']
    receipts = output/'controllers'
    receipts.mkdir(parents=True, exist_ok=True)
    previous = [json.loads(p.read_text()) for p in receipts.glob('*.json')]
    # ATTEMPT charge is the conservative supervisor launch-to-observation wall.
    charged = 0.
    for case in manifest['cases']:
        path = output/'cases'/case['id']/'ATTEMPT.json'
        if path.exists():
            attempt = json.loads(path.read_text())
            if attempt['profile'] == profile:
                charged += attempt.get('charged_wall_s', limits['case_s'])
    old_elapsed = sum(r['controller_elapsed_s'] for r in previous if r['profile'] == profile)
    controller_cap = max(0., limits['controller_s']-old_elapsed)
    ctx = mp.get_context('spawn')
    replies = ctx.Queue()
    workers = {}
    active = {}
    samples = []
    sampler = rs.Sampler()
    stop_reason = 'CASE_SET_EXHAUSTED'
    runid = str(time.time_ns())

    def start_worker():
        commands = ctx.Queue()
        process = ctx.Process(target=_worker, args=(commands, replies))
        process.start()
        workers[process.pid] = (process, commands)
        return process.pid

    def finish(pid, status=None):
        nonlocal charged
        item = active.pop(pid)
        elapsed = time.monotonic()-item['start']
        charged += elapsed
        attempt = item['attempt']
        attempt.update(charged_wall_s=elapsed, supervisor_outcome=status or 'WORKER_RETURNED')
        folder = item['folder']
        atomic_json(folder/'ATTEMPT.json', attempt)
        if status is not None:
            # Stop only this controller's own worker, preserving partial files.
            process, commands = workers.pop(pid)
            process.terminate()
            process.join(timeout=2)
            if process.is_alive():
                process.kill()
                process.join(timeout=2)
            if not (folder/'RESULT.json').exists():
                atomic_json(folder/'RESULT.json', {'id': item['case']['id'],
                    'config': item['case']['config'], 'status': status, 'exit': 124,
                    'error': 'Supervisor bound; partial files and input preserved.'})

    try:
        while pending or active:
            now = time.monotonic()
            elapsed = now-started
            sample = sampler.sample(profile, requested)
            if not samples or now-samples[-1]['observed_monotonic'] >= 1:
                samples.append(sample)
            for pid in list(active):
                process = workers[pid][0]
                if not process.is_alive():
                    finish(pid, 'FAILED_WORKER_EXIT')
                elif now-active[pid]['start'] >= limits['case_s']:
                    finish(pid, 'FAILED_CASE_TIMEOUT')
            while True:
                try:
                    pid, caseid = replies.get_nowait()
                except queue.Empty:
                    break
                if pid in active and active[pid]['case']['id'] == caseid:
                    finish(pid)
            if elapsed >= controller_cap:
                stop_reason = 'CONTROLLER_CAP'
                break
            reserved = charged+len(active)*limits['case_s']
            slot_count = sample['slots']
            while pending and len(active) < slot_count and reserved+limits['case_s'] <= limits['child_s']:
                # Enough remaining controller time for a full per-case allowance.
                if controller_cap-(time.monotonic()-started) < limits['case_s']:
                    stop_reason = 'CONTROLLER_LAUNCH_RESERVATION'
                    pending = pending  # retained as pending in readback
                    break
                idle = [p for p in workers if p not in active and workers[p][0].is_alive()]
                pid = idle[0] if idle else start_worker()
                case = pending.pop(0)
                folder = output/'cases'/case['id']
                folder.mkdir(parents=True, exist_ok=True)
                if resume_state(output, case) != 'PENDING':
                    continue
                # Exclusive only for the same case; never a host/global lock.
                try:
                    fd = os.open(folder/'write.lock', os.O_CREAT|os.O_EXCL|os.O_WRONLY, 0o600)
                except FileExistsError:
                    continue
                with os.fdopen(fd, 'w') as stream:
                    stream.write(str(os.getpid()))
                atomic_json(folder/'INPUT.json', case)
                attempt = {'id': case['id'], 'profile': profile, 'controller': runid,
                           'worker_pid': pid, 'per_case_cap_s': limits['case_s'],
                           'status': 'LAUNCHED', 'started_unix': time.time()}
                atomic_json(folder/'ATTEMPT.json', attempt)
                active[pid] = {'case': case, 'folder': folder, 'start': time.monotonic(), 'attempt': attempt}
                workers[pid][1].put((case, str(folder)))
                reserved += limits['case_s']
            if not active and pending:
                if charged+limits['case_s'] > limits['child_s']:
                    stop_reason = 'CHILD_WALL_LAUNCH_RESERVATION'
                    break
                if controller_cap-(time.monotonic()-started) < limits['case_s']:
                    stop_reason = 'CONTROLLER_LAUNCH_RESERVATION'
                    break
            time.sleep(.05)
    finally:
        for pid in list(active):
            finish(pid, 'INCOMPLETE_CONTROLLER_STOP')
        for pid, (process, commands) in workers.items():
            if process.is_alive():
                commands.put(None)
            process.join(timeout=2)
            if process.is_alive():
                process.terminate()
                process.join(timeout=2)
        states = {c['id']: resume_state(output, c) for c in manifest['cases']}
        receipt = {'profile': profile, 'controller_elapsed_s': time.monotonic()-started,
                   'previous_controller_elapsed_s': old_elapsed,
                   'cumulative_child_charged_wall_s': charged, 'stop_reason': stop_reason,
                   'states': states, 'resource_samples': samples,
                   'contract_review_decision': review['decision'],
                   'budget_accounting': 'supervisor launch to observed return; setup/queue overhead included conservatively',
                   'unrelated_process_actions': 0}
        atomic_json(receipts/(runid+'.json'), receipt)
        atomic_json(output/'STATUS.json', receipt)
    return receipt


def read_results(output):
    output = Path(output)
    manifest = plan(output)
    results = {}
    for case in manifest['cases']:
        status = resume_state(output, case)
        if status == 'COMPLETED':
            path = output/'cases'/case['id']/'RESULT.json'
            results[case['id']] = json.loads(path.read_text())
    return manifest, results


def check(output):
    manifest, results = read_results(output)
    nominal = [c for c in manifest['cases'] if not c['config']['guard']]
    guard_checks = []
    for case in (c for c in manifest['cases'] if c['config']['guard']):
        base = next(c for c in nominal if c['config']['Sigma_F_i'] == case['config']['Sigma_F_i']
                    and c['config']['Pi_F_signed_i'] == case['config']['Pi_F_signed_i'])
        if case['id'] not in results or base['id'] not in results:
            guard_checks.append({'id': case['id'], 'status': 'PENDING'})
            continue
        a, b = results[case['id']]['endpoint'], results[base['id']]['endpoint']
        delta = {k: abs(a[k]-b[k]) for k in ('Sigma_F', 'Pi_F_signed', 'b')}
        delta['H_relative'] = abs(a['H']/b['H']-1)
        guard_checks.append({'id': case['id'], 'status': 'PASS' if max(delta.values()) <= 2e-6 else 'FAIL',
                             'absolute_endpoint_differences': delta})
    states = {c['id']: resume_state(output, c) for c in manifest['cases']}
    all_complete = len(results) == 94
    report = {'nominal_completed': sum(c['id'] in results for c in nominal),
              'nominal_planned': 91, 'total_completed': len(results), 'total_planned': 94,
              'states': states, 'corner_stability': guard_checks,
              'numerical_gate': 'PASS_SCOPED_PRELIMINARY' if all_complete and all(
                  g['status'] == 'PASS' for g in guard_checks) else 'PARTIAL_OR_FAILED',
              'scientific_admission': 'PENDING_INDEPENDENT_RESULT_REVIEW',
              'brightness_scope': '64-node sample; not global positivity theorem',
              'Hamiltonian_scope': 'algebraic construction consistency only'}
    atomic_json(Path(output)/'CHECK.json', report)
    return report


def plot(output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    output = Path(output)
    manifest, results = read_results(output)
    nominal = [c for c in manifest['cases'] if not c['config']['guard']]
    report = check(output)
    rows = []
    for case in nominal:
        c = case['config']
        r = results.get(case['id'])
        row = {'id': case['id'], 'Sigma_F_initial_target': c['Sigma_F_i'],
               'Pi_F_initial_signed_target': c['Pi_F_signed_i'], 'stress_sign': c['stress_sign'],
               'state': resume_state(output, case)}
        if r:
            row.update({k+'_initial': v for k, v in r['initial'].items()})
            row.update({k+'_end': v for k, v in r['endpoint'].items()})
        rows.append(row)
    keys = list(dict.fromkeys(k for row in rows for k in row))
    with (output/'finite_grid.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, keys)
        writer.writeheader()
        writer.writerows(rows)
    fig, axes = plt.subplots(2, 3, figsize=(14, 8), constrained_layout=True)
    from matplotlib.colors import Normalize
    for col, observable in enumerate(('Sigma_F', 'Pi_F_signed', 'b')):
        vals = [r['endpoint'][observable] for r in results.values() if not r['config']['guard']]
        lo, hi = (min(vals), max(vals)) if vals else (0, 1)
        if lo == hi:
            hi = lo+1e-12
        norm = Normalize(lo, hi)
        for row, sign in enumerate((1, -1)):
            ax = axes[row, col]
            goodx, goody, goodv, badx, bady = [], [], [], [], []
            for case in nominal:
                c = case['config']
                if c['stress_sign'] not in (0, sign):
                    continue
                ix = ad.SIGMAS.index(c['Sigma_F_i'])
                iy = ad.PIS.index(abs(c['Pi_F_signed_i']))
                if case['id'] in results:
                    goodx.append(ix); goody.append(iy); goodv.append(results[case['id']]['endpoint'][observable])
                else:
                    badx.append(ix); bady.append(iy)
            points = ax.scatter(goodx, goody, c=goodv, cmap='viridis', norm=norm, s=110, marker='s')
            ax.scatter(badx, bady, marker='x', c='gray', s=35, label='pending/failed')
            fig.colorbar(points, ax=ax, label=observable+' at a=0.2 [dimensionless]')
            ax.set_xticks(range(7), [f'{v:g}' for v in ad.SIGMAS], rotation=45)
            ax.set_yticks(range(7), [f'{v:g}' for v in ad.PIS])
            ax.set(xlabel='initial Sigma_F', ylabel='initial |Pi_F|',
                   title=f'initial stress sign {sign:+d}: {observable}')
            ax.set_xlim(-.6, 6.6); ax.set_ylim(-.6, 6.6)
    fig.suptitle(f'Source-free LRS Bianchi I preliminary finite grid | a: 1/21 to 1/5\n'
                 f'{report["nominal_completed"]}/91 nominal IVPs; independent result review pending; cells are actual samples')
    fig.savefig(output/'sigma_pi_finite_grid.png', dpi=180)
    fig.savefig(output/'sigma_pi_finite_grid.pdf')
    plt.close(fig)
    return {'png': str(output/'sigma_pi_finite_grid.png'), 'pdf': str(output/'sigma_pi_finite_grid.pdf')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('plan', 'run', 'plot', 'check'))
    parser.add_argument('--output', type=Path, default=ROOT/'results')
    parser.add_argument('--profile', choices=('sandbox', 'ncp'), default='sandbox')
    parser.add_argument('--max-workers', type=int)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--review-approval', type=Path)
    args = parser.parse_args()
    if args.command == 'run':
        if not args.review_approval:
            parser.error('run requires --review-approval from the independent contract review')
        result = run(args.output, args.profile, args.max_workers, args.resume, args.review_approval)
    else:
        result = globals()[args.command](args.output)
    if args.command == 'plan':
        print(json.dumps({'nominal_cases': result['nominal_cases'], 'guard_cases': result['guard_cases'],
                          'contract_sha256': result['contract_sha256']}))
    elif args.command == 'run':
        from collections import Counter
        print(json.dumps({'states': dict(Counter(result['states'].values())),
                          'stop_reason': result['stop_reason'],
                          'controller_elapsed_s': result['controller_elapsed_s'],
                          'child_charged_s': result['cumulative_child_charged_wall_s']}))
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
