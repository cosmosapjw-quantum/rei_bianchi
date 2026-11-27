"""Bounded synthetic scheduler interleaving; no scientific/native backend."""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "executor"))
import core
import guard

BACKEND = '''import os,pathlib,sys,time
p=pathlib.Path(sys.argv[1]); root=p.parent
(root/'ready').write_text('ready')
while not (root/'go').exists(): time.sleep(.001)
if os.fork(): os._exit(0)
p.write_bytes(b'PARTIAL_NOT_FINISHED\\n')
(root/'child_ready').write_text(str(os.getpid()))
time.sleep(10)
with p.open('ab') as f: f.write(b'FINAL_SUFFIX\\n')
'''


def main():
    original = guard.group_state
    source_hash = hashlib.sha256((ROOT / 'executor/guard.py').read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix='exit_race_', dir=Path(__file__).parent) as temporary:
        base = Path(temporary)
        backend = base / 'backend.py'
        backend.write_text(BACKEND)
        output = base / 'run'
        work = output / 'tasks/toy/work'
        manifest = base / 'manifest.json'
        python = str(Path(sys.executable).resolve())
        task = {'task_id': 'toy', 'executable': core.file_identity(python),
                'inputs': [core.file_identity(backend)], 'argv': [python, str(backend), 'OUTPUT_PATH'],
                'env': {}, 'cost_hint': 1, 'semantic_identity': {'kind': 'synthetic_partial_write'},
                'limits': {'wall_seconds': 5, 'address_space_bytes': 128 << 20,
                           'rss_bytes': 64 << 20, 'poll_ms': 10, 'max_output_bytes': 1 << 20}}
        manifest.write_text(json.dumps({'schema': core.SCHEMA, 'scope': 'SYNTHETIC_ONLY',
                                        'output_root': str(output), 'tasks': [task]}))
        first = True
        def interleave(pgid):
            nonlocal first
            if not first:
                return original(pgid)
            first = False
            deadline = time.monotonic() + 3
            while not (work / 'ready').exists():
                if time.monotonic() > deadline: raise RuntimeError('probe readiness timeout')
                time.sleep(.001)
            snapshot = original(pgid)
            # Suspend the observer after its actual snapshot. The leader then
            # forks/exits, before guard.run calls poll on that old snapshot.
            (work / 'go').write_text('go')
            while True:
                # waitid WNOWAIT observes child exit without reaping and does
                # not assume /proc and caller share a PID namespace.
                exited = os.waitid(os.P_PID, pgid, os.WEXITED | os.WNOHANG | os.WNOWAIT) is not None
                if exited and (work / 'child_ready').exists(): break
                if time.monotonic() > deadline: raise RuntimeError('probe child timeout')
                time.sleep(.001)
            return snapshot
        guard.group_state = interleave
        try:
            result = core.run_task(str(manifest), 0)
            collected = core.collect(str(manifest))
            payload = output / 'tasks/toy/payload.bin'
            report = {'probe': 'leader forks/exits between real group snapshot and poll',
                      'guard_sha256': source_hash, 'run_result': result,
                      'collector_status': collected['status'],
                      'committed_payload': payload.read_text() if payload.exists() else None,
                      'actual_HH_runs': 0, 'native_callback_runs': 0}
            print(json.dumps(report, indent=2))
        finally:
            guard.group_state = original


if __name__ == '__main__': main()
