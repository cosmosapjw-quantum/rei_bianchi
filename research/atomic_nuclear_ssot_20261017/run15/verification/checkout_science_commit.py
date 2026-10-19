#!/usr/bin/env python3
"""Create the exact new, sparse Git checkout; no scientific commands are run."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import os
import subprocess
import time
import traceback

ROOT = Path('/tmp/rei_run15_salvage/verification')
REPO = Path('/tmp/rei_run15_clean_git')
SHA = '6405bcba8ec654bf3ab98182be344cd8c3915b97'
TREE = 'be7a8473202b1800bc9f0dcdd3351e187fe32063'
URL = 'https://github.com/cosmosapjw-quantum/rei_bianchi'
SCOPES = ['research/atomic_nuclear_ssot_20261017/run13',
          'research/atomic_nuclear_ssot_20261017/run15']

def digest(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')

def main():
    logs = ROOT / 'checkout'
    if REPO.exists() or REPO.is_symlink() or logs.exists():
        raise ValueError('new checkout and evidence directories required')
    logs.mkdir()
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0')
    receipt = {'schema': 'rei.run15.postloss.scoped_git_checkout.v1',
               'status': 'IN_PROGRESS', 'remote': URL, 'expected_head': SHA,
               'expected_tree': TREE, 'checkout': str(REPO), 'sparse_scopes': SCOPES,
               'created_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
               'script': digest(Path(__file__)), 'commands': [],
               'native_IVP_runs': 0, 'tests': 0, 'scientific_calculations': 0}
    def run(name, argv):
        print(json.dumps({'stage': name, 'status': 'STARTED', 'argv': argv}), flush=True)
        out, err = logs / (name + '.stdout.txt'), logs / (name + '.stderr.txt')
        start = time.monotonic()
        with out.open('xb') as stdout, err.open('xb') as stderr:
            process = subprocess.run(argv, cwd='/tmp', env=env, stdin=subprocess.DEVNULL,
                                     stdout=stdout, stderr=stderr, timeout=180)
        row = {'stage': name, 'argv': argv, 'cwd': '/tmp', 'exit_code': process.returncode,
               'seconds': time.monotonic() - start,
               'environment_overrides': {'GIT_OPTIONAL_LOCKS': '0', 'GIT_TERMINAL_PROMPT': '0'},
               'stdout': {'path': out.name, **digest(out)}, 'stderr': {'path': err.name, **digest(err)}}
        receipt['commands'].append(row)
        save(logs / (name + '.command.json'), row)
        print(json.dumps({'stage': name, 'exit_code': process.returncode, 'seconds': row['seconds']}), flush=True)
        if process.returncode:
            raise RuntimeError('Git command failed: ' + name)
        return out.read_text().strip()
    try:
        run('01_init', ['git', 'init', str(REPO)])
        git = ['git', '-C', str(REPO)]
        run('02_remote', git + ['remote', 'add', 'origin', URL])
        run('03_sparse_init', git + ['sparse-checkout', 'init', '--cone'])
        run('04_sparse_set', git + ['sparse-checkout', 'set', *SCOPES])
        run('05_fetch_exact_D', git + ['fetch', '--depth=1', '--filter=blob:none', 'origin', SHA])
        run('06_checkout_exact_D', git + ['checkout', '--detach', 'FETCH_HEAD'])
        head = run('07_head', git + ['rev-parse', 'HEAD'])
        tree = run('08_tree', git + ['rev-parse', 'HEAD^{tree}'])
        if head != SHA or tree != TREE:
            raise ValueError('checkout identity differs from authorized published science commit')
        receipt.update(status='EXACT_SCIENCE_COMMIT_CHECKED_OUT', actual_head=head, actual_tree=tree)
    except Exception as exc:
        receipt.update(status='FAILED_OR_BLOCKED', error_type=type(exc).__name__,
                       error=str(exc), traceback=traceback.format_exc())
    save(ROOT / 'SCOPED_GIT_CHECKOUT_RECEIPT.json', receipt)
    print(json.dumps({'status': receipt['status'], 'receipt': str(ROOT / 'SCOPED_GIT_CHECKOUT_RECEIPT.json')}), flush=True)
    return 0 if receipt['status'] == 'EXACT_SCIENCE_COMMIT_CHECKED_OUT' else 1

if __name__ == '__main__':
    raise SystemExit(main())
