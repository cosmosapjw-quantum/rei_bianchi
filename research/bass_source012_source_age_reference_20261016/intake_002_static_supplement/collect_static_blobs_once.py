#!/usr/bin/python3
"""One sequential bounded capture of two pinned SOURCE012 static JSON blobs."""
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path('/home/cosmosapjw/Dropbox/bianchi/rei_bianchi')
PUB = ROOT / 'research/bass_source012_source_age_reference_20261016/intake_002_static_supplement'
PRIVATE = Path('/home/cosmosapjw/REI_PRIVATE_SOURCE012_INPUTS_20261016/static_supplement_001')
PIN = '35d9747a0bbedcafdb568467ce7c1e7a25f965b6'
PRIOR_FILES = 409
PRIOR_BYTES = 7396570
PRIOR_WALL = 2.59
CUM_PRIVATE_CAP = 134217728
PUBLIC_CAP = 1048576
GIT = ['git', '-c', 'core.packedGitWindowSize=32m', '-c', 'core.packedGitLimit=64m']
TARGETS = [
    'configs/rei_fastest_v1/science_scenario_v1.json',
    'docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/ft03_first_interval.json',
]
started = time.monotonic()
cpu0 = time.process_time()
commands = []
files = []
missing = []
new_bytes = 0

def git(argv):
    p = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    commands.append({'argv': argv, 'exit_code': p.returncode, 'stdout_bytes': len(p.stdout), 'stderr': p.stderr.decode('utf-8', 'replace')[:700]})
    return p

def main():
    PUB.mkdir(parents=True, exist_ok=True)
    PRIVATE.mkdir(parents=True, exist_ok=False)
    status = 'HOLD'
    reason = None
    for rel in TARGETS:
        tree_cmd = GIT + ['ls-tree', '--full-tree', PIN, '--', rel]
        tree = git(tree_cmd)
        if tree.returncode:
            missing.append({'path': rel, 'stage': 'tree_metadata', 'exit_code': tree.returncode, 'reason': 'git_ls_tree_failed'})
            reason = 'FIRST_FAILURE_GIT_TREE_LOOKUP'; break
        line = tree.stdout.decode('utf-8', 'replace').strip()
        try:
            meta, observed_path = line.split('\t', 1)
            mode, kind, oid = meta.split(' ')
        except ValueError:
            missing.append({'path': rel, 'stage': 'tree_metadata', 'reason': 'blob_metadata_missing_or_malformed', 'raw': line[:500]})
            reason = 'FIRST_FAILURE_TREE_METADATA'; break
        if observed_path != rel or kind != 'blob':
            missing.append({'path': rel, 'stage': 'tree_metadata', 'reason': 'path_or_type_mismatch', 'observed_path': observed_path, 'observed_type': kind})
            reason = 'FIRST_FAILURE_TREE_METADATA'; break
        show_cmd = GIT + ['show', f'{PIN}:{rel}']
        captured = git(show_cmd)
        if captured.returncode:
            missing.append({'path': rel, 'stage': 'blob_capture', 'exit_code': captured.returncode, 'reason': 'git_show_failed'})
            reason = 'FIRST_FAILURE_GIT_BLOB_CAPTURE'; break
        data = captured.stdout
        git_oid = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        sha256 = hashlib.sha256()
        dest = PRIVATE / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if PRIOR_BYTES + new_bytes + len(data) > CUM_PRIVATE_CAP:
            missing.append({'path': rel, 'stage': 'copy', 'reason': 'cumulative_private_payload_cap', 'size_bytes': len(data)})
            reason = 'FIRST_FAILURE_PRIVATE_CAP'; break
        if git_oid != oid:
            missing.append({'path': rel, 'stage': 'copy', 'reason': 'git_blob_oid_mismatch', 'tree_oid': oid, 'computed_oid': git_oid})
            reason = 'FIRST_FAILURE_BLOB_IDENTITY'; break
        # Copy and update the SHA-256 incrementally; preserve exactly the Git blob bytes.
        with open(dest, 'xb') as f:
            for off in range(0, len(data), 1024 * 1024):
                chunk = data[off:off + 1024 * 1024]
                f.write(chunk); sha256.update(chunk)
        new_bytes += len(data)
        json_valid = True
        try:
            json.loads(data.decode('utf-8'))
        except Exception as e:
            json_valid = False
            missing.append({'path': rel, 'stage': 'json_parse', 'reason': 'captured_json_invalid', 'detail': repr(e)[:500]})
        files.append({'path': rel, 'private_path': str(dest), 'git_tree_blob_sha1': oid, 'copy_time_git_blob_sha1': git_oid, 'size_bytes': len(data), 'copy_time_sha256': sha256.hexdigest(), 'json_valid': json_valid})
        if not json_valid:
            reason = 'FIRST_FAILURE_JSON_PARSE'; break
    if not missing and len(files) == len(TARGETS):
        status = 'STATIC_DEPENDENCY_BUNDLE_COMPLETE'
    result = {
        'schema': 'rei.bass_source012.static_blob_supplement.manifest.v1',
        'status': status,
        'reason': reason,
        'native_base_source_pin': PIN,
        'targets': TARGETS,
        'files': files,
        'missing': missing,
        'commands': commands,
        'prior_collection': {'files': PRIOR_FILES, 'bytes': PRIOR_BYTES, 'wall_seconds': PRIOR_WALL},
        'supplement': {'files': len(files), 'bytes': new_bytes, 'wall_seconds': round(time.monotonic() - started, 6), 'cpu_seconds': round(time.process_time() - cpu0, 6)},
        'cumulative': {'files': PRIOR_FILES + len(files), 'bytes': PRIOR_BYTES + new_bytes, 'wall_seconds': PRIOR_WALL + round(time.monotonic() - started, 6), 'private_cap_bytes': CUM_PRIVATE_CAP},
        'scientific_reference_fields': {k: None for k in ['per_call_Gamma', 'heat', 'prepared_nodes', 'intermediate_old_state', 'successful_positive_independent_reference']},
        'claim_ceiling': 'Only static dependency capture status; no solver/reference/scientific admission.',
        'requested_executor': 'historical worker-light Luna/low, no generation override',
        'observed_runtime': 'NOT_INDEPENDENTLY_OBSERVED',
        'retry_performed': False,
        'native_deadline_renewed': False,
        'git_mutation': False,
    }
    out = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True).encode() + b'\n'
    if len(out) > PUBLIC_CAP:
        raise RuntimeError(f'public metadata cap exceeded: {len(out)}')
    with open(PUB / 'MANIFEST.json', 'xb') as f: f.write(out)
    print(json.dumps({'status': status, 'files': len(files), 'bytes': new_bytes, 'missing': len(missing), 'manifest_bytes': len(out), 'wall_seconds': result['supplement']['wall_seconds']}, sort_keys=True))
    return 0 if status == 'STATIC_DEPENDENCY_BUNDLE_COMPLETE' else 2

if __name__ == '__main__':
    try: sys.exit(main())
    except Exception as e:
        print('SUPPLEMENT_FATAL: '+repr(e), file=sys.stderr)
        sys.exit(3)
