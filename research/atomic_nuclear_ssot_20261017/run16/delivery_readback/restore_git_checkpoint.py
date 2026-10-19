#!/usr/bin/env python3
"""Read-only remote retrieval into a new isolated checkout; no science executed."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import os
import subprocess
import time
import traceback

ROOT = Path('/tmp/rei_run16_work/readback')
REPO = ROOT / 'git_checkout'
SHA = '2cc5e0862dbe9770ef83c0b2437e27627ec26524'
TREE = 'e27bea710a9e398311c6728fcbe22625a93e13e2'
SCOPE = 'research/atomic_nuclear_ssot_20261017/run16'

def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

def identity(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

def main():
    if REPO.exists() or REPO.is_symlink() or (ROOT / 'git_logs').exists():
        raise ValueError('new isolated checkout required')
    logs = ROOT / 'git_logs'
    logs.mkdir()
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0')
    receipt = {'schema': 'rei.run16.isolated_git_checkpoint_readback.v1', 'status': 'IN_PROGRESS',
               'created_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'remote_commit': SHA,
               'expected_tree': TREE, 'checkout': str(REPO), 'scope': SCOPE,
               'script': identity(Path(__file__)), 'commands': [], 'native_IVP_runs': 0,
               'quadrature_executions': 0, 'test_suite_executions': 0}
    def run(name, argv):
        out, err = logs / (name + '.stdout.txt'), logs / (name + '.stderr.txt')
        print(json.dumps({'stage': name, 'status': 'STARTED'}), flush=True)
        started = time.monotonic()
        with out.open('xb') as stdout, err.open('xb') as stderr:
            result = subprocess.run(argv, cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                    stdout=stdout, stderr=stderr, timeout=120)
        row = {'stage': name, 'argv': argv, 'cwd': str(ROOT), 'exit_code': result.returncode,
               'seconds': time.monotonic() - started,
               'environment_overrides': {'GIT_OPTIONAL_LOCKS': '0', 'GIT_TERMINAL_PROMPT': '0'},
               'stdout': {'path': str(out.relative_to(ROOT)), **identity(out)},
               'stderr': {'path': str(err.relative_to(ROOT)), **identity(err)}}
        receipt['commands'].append(row)
        save(logs / (name + '.command.json'), row)
        print(json.dumps({'stage': name, 'exit_code': result.returncode}), flush=True)
        if result.returncode:
            raise RuntimeError('single Git blocker: ' + name)
        return out.read_text().strip()
    try:
        run('01_init', ['git', 'init', str(REPO)])
        git = ['git', '-C', str(REPO)]
        run('02_remote', git + ['remote', 'add', 'origin', 'https://github.com/cosmosapjw-quantum/rei_bianchi'])
        run('03_sparse_init', git + ['sparse-checkout', 'init', '--cone'])
        run('04_sparse_set', git + ['sparse-checkout', 'set', SCOPE])
        run('05_fetch_checkpoint', git + ['fetch', '--depth=1', '--filter=blob:none', 'origin', SHA])
        run('06_checkout', git + ['checkout', '--detach', 'FETCH_HEAD'])
        head = run('07_head', git + ['rev-parse', 'HEAD'])
        tree = run('08_tree', git + ['rev-parse', 'HEAD^{tree}'])
        if head != SHA or tree != TREE:
            raise ValueError('published commit/tree mismatch')
        receipt.update(status='EXACT_GIT_CHECKPOINT_RESTORED', head=head, tree=tree)
    except Exception as exc:
        receipt.update(status='BLOCKED_SINGLE_ATTEMPT', error_type=type(exc).__name__,
                       error=str(exc), traceback=traceback.format_exc())
    save(ROOT / 'GIT_RESTORE_RECEIPT.json', receipt)
    print(json.dumps({'status': receipt['status'], 'receipt': str(ROOT / 'GIT_RESTORE_RECEIPT.json')}), flush=True)
    return 0 if receipt['status'] == 'EXACT_GIT_CHECKPOINT_RESTORED' else 1

if __name__ == '__main__':
    raise SystemExit(main())
