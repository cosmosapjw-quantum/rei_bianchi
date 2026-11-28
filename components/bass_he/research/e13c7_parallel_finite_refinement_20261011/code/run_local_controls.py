#!/usr/bin/env python3
"""Declared short local branch/precision or resolution controls, four workers."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from common import read, save

def child(args):
    from off_path_worker import Context
    os.sched_setaffinity(0, {args.cpu})
    ctx = Context(args.package)
    units = [(32, 60), (32, 80), (128, 60)] if args.mode == 'branch' else [(1024, 60)]
    for n, p in units:
        path = args.output_dir / ('N%d_P%d' % (n, p)) / ('node_%06d' % args.node)
        print(json.dumps(ctx.run(args.node, n, p, path, 'local'), sort_keys=True), flush=True)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--package', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--mode', choices=['branch', 'resolution'], required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--child', action='store_true')
    p.add_argument('--node', type=int)
    p.add_argument('--cpu', type=int)
    args = p.parse_args()
    if args.child:
        child(args)
        return
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    contract = read(args.package / 'RESEARCH_CONTRACT.json')
    nodes = contract['local_branch_control_nodes' if args.mode == 'branch' else 'local_resolution_diagnostic_nodes']
    cpus = sorted(os.sched_getaffinity(0))[:4]
    if len(cpus) < 4:
        raise RuntimeError('this declared local control layout requires four available CPUs')
    started = time.perf_counter()
    save(out / 'START.json', {'nodes': nodes, 'mode': args.mode, 'cpus': cpus, 'processes': 4, 'thread_per_process': 1,
         'automatic_retries': 0, 'transport': 'local subprocesses; not MPI'})
    processes = []
    for node, cpu in zip(nodes, cpus):
        argv = [sys.executable, str(Path(__file__).resolve()), '--package', str(args.package.resolve()), '--mode', args.mode,
                '--output-dir', str(out), '--child', '--node', str(node), '--cpu', str(cpu)]
        stdout = (out / ('node_%06d.stdout' % node)).open('xb')
        stderr = (out / ('node_%06d.stderr' % node)).open('xb')
        proc = subprocess.Popen(argv, stdout=stdout, stderr=stderr,
            env={**os.environ, 'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1', 'NUMEXPR_NUM_THREADS': '1'})
        processes.append((node, proc, stdout, stderr, argv))
    exits = []
    try:
        for node, proc, stdout, stderr, argv in processes:
            rc = proc.wait(timeout=560)
            stdout.close(); stderr.close()
            exits.append({'node': node, 'exit_code': rc, 'argv': argv})
            print(json.dumps({'node': node, 'exit_code': rc, 'mode': args.mode}), flush=True)
        save(out / 'DRIVER_RECEIPT.json', {'status': 'PASS_EXECUTION' if all(r['exit_code'] == 0 for r in exits) else 'FAIL_PRESERVED',
             'processes': exits, 'elapsed_seconds': time.perf_counter() - started, 'automatic_retries': 0})
        if any(r['exit_code'] for r in exits):
            raise RuntimeError('local control failed; see preserved child evidence')
    finally:
        for _, proc, stdout, stderr, _ in processes:
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=5)
            stdout.close(); stderr.close()

if __name__ == '__main__':
    main()
