#!/usr/bin/env python3
"""NCP adapter tests using explicitly synthetic child processes only.

NO PHYSICS IS COMPUTED. The fake child's result is a one-scalar fixture.
These tests exercise fresh-result comparison, source lock, output collision
and timeout preservation, not the scientific engine or an NCP host.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import subprocess
import sys
import time

from local_enclosure import atomic_json
from ncp_execute import numerical_digest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/ncp_boundary_fixtures'

STUB = '''import argparse,json,hashlib,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--package',type=Path);p.add_argument('--output',type=Path);p.add_argument('--subdivisions');p.add_argument('--precision');a=p.parse_args()
mode=MODE_VALUE
if mode=='timeout':time.sleep(3)
r=json.loads((a.package/'evidence/N512_P60.json').read_text())
r['fixture_only']=True
r['identity']={'source_sha256_before_run':{n:hashlib.sha256((a.package/n).read_bytes()).hexdigest() for n in ['code/local_enclosure.py','code/directed_interval.py','PLAN.json','inputs/SIX_CONTROLS.json']}}
if mode=='mismatch':r['controls'][0]['fixture_scalar']='2'
if mode=='source_mismatch':r['identity']['source_sha256_before_run']['code/local_enclosure.py']='0'*64
a.output.write_text(json.dumps(r))
print('SYNTHETIC_BOUNDARY_FIXTURE_ONLY_NO_SCIENTIFIC_RUN')
'''


def create_fixture(mode):
    p = OUT / mode / 'package'
    (p / 'code').mkdir(parents=True)
    (p / 'inputs').mkdir(); (p / 'evidence').mkdir()
    for name in ('ncp_execute.py', 'directed_interval.py'):
        shutil.copyfile(ROOT / 'code' / name, p / 'code' / name)
    (p / 'code/local_enclosure.py').write_text(STUB.replace('MODE_VALUE', repr(mode)))
    (p / 'PLAN.json').write_text('{"fixture_only":true}\n')
    (p / 'inputs/SIX_CONTROLS.json').write_text('{"fixture_only":true}\n')
    baseline = {'fixture_only': True, 'controls': [{'key': ['TEST_FIXTURE_ONLY', 0, 0, 0],
                'fixture_scalar': '1', 'elapsed_seconds': 0}], 'rounding_operation_counts': {'fixture': 1},
                'source_unchanged_during_run': True, 'compatibility_failures': [],
                'saved_firstvariation_containment_failures': [], 'peak_RSS_KiB': 1}
    atomic_json(p / 'evidence/N512_P60.json', baseline)
    files = ['code/ncp_execute.py', 'code/directed_interval.py', 'code/local_enclosure.py',
             'PLAN.json', 'inputs/SIX_CONTROLS.json', 'evidence/N512_P60.json']
    lock = {'fixture_only': True, 'files': [{'path': n, 'bytes': (p / n).stat().st_size,
             'sha256': hashlib.sha256((p / n).read_bytes()).hexdigest()} for n in files],
             'baseline_numerical_sha256': numerical_digest(baseline)}
    atomic_json(p / 'EXECUTION_LOCK.json', lock)
    return p


def main():
    OUT.mkdir(exist_ok=False)
    checks, runs = [], []
    def run(mode, p, target, timeout=10):
        cmd = [sys.executable, str(p / 'code/ncp_execute.py'), '--package', str(p),
               '--out', str(target), '--execute', '--timeout', str(timeout)]
        started = time.perf_counter()
        proc = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=20)
        record = {'mode': mode, 'command': cmd, 'actual_exit': proc.returncode,
                  'elapsed_seconds': time.perf_counter() - started, 'fixture_only': True}
        (OUT / (mode + '.stdout.txt')).write_text(proc.stdout)
        (OUT / (mode + '.stderr.txt')).write_text(proc.stderr)
        runs.append(record)
        return proc
    for mode in ('pass', 'mismatch', 'source_mismatch', 'timeout', 'lock_mismatch'):
        p = create_fixture(mode); target = p.parent / 'result'
        if mode == 'lock_mismatch':
            (p / 'inputs/SIX_CONTROLS.json').write_text('{"tampered_fixture":true}\n')
        result = run(mode, p, target, 1 if mode == 'timeout' else 10)
        report = json.loads((target / 'NCP_RESULT.json').read_text())
        if mode == 'pass':
            checks.append({'id': 'fresh_fixture_success', 'pass': result.returncode == 0 and report['new_output_parity_checked']})
            parity = json.loads((target / 'PARITY.json').read_text())
            checks.append({'id': 'fresh_fixture_actually_compared', 'pass': parity['fresh_output_compared'] and parity['fresh_as_run_source_matches_execution_lock']})
            before = hashlib.sha256((target / 'NCP_RESULT.json').read_bytes()).hexdigest()
            collision = run('collision', p, target)
            after = hashlib.sha256((target / 'NCP_RESULT.json').read_bytes()).hexdigest()
            checks.append({'id': 'existing_output_rejected_unchanged', 'pass': collision.returncode != 0 and before == after})
        elif mode == 'mismatch':
            parity = json.loads((target / 'PARITY.json').read_text())
            checks.append({'id': 'fresh_output_mismatch_rejected', 'pass': result.returncode != 0 and not parity['bitwise_numerical_json_parity']})
        elif mode == 'source_mismatch':
            checks.append({'id': 'fresh_as_run_source_mismatch_rejected', 'pass': result.returncode != 0 and 'producer/input identities' in report['error']})
        elif mode == 'timeout':
            checks.append({'id': 'timeout_preserved', 'pass': result.returncode != 0 and report['status'] == 'TIMEOUT' and report['actual_exit'] is None and (target / 'stderr.txt').exists()})
        else:
            checks.append({'id': 'input_tamper_rejected_before_child', 'pass': result.returncode != 0 and report['new_host_scientific_runs'] == 0 and not (target / 'RESULTS.json').exists()})
    summary = {'schema': 'bass-he-e13c4-ncp-adapter-fixtures-v1', 'fixture_only': True,
               'scientific_calculations': 0, 'actual_NCP_execution': False,
               'checks': checks, 'passed': sum(c['pass'] for c in checks),
               'failed': sum(not c['pass'] for c in checks), 'actual_fixture_runs': runs,
               'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'adapter_sha256': hashlib.sha256((ROOT / 'code/ncp_execute.py').read_bytes()).hexdigest()}
    atomic_json(OUT / 'SUMMARY.json', summary)
    print(json.dumps({'passed': summary['passed'], 'failed': summary['failed'], 'scientific_calculations': 0, 'actual_NCP_execution': False}))
    return 0 if summary['failed'] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
