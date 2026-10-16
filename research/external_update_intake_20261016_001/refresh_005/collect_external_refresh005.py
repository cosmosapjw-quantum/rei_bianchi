#!/usr/bin/python3
"""Bounded compact GitHub contents capture for pinned PR 151 and PR 99."""
import base64
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path('/home/cosmosapjw/Dropbox/bianchi/rei_bianchi')
PUB = ROOT / 'research/external_update_intake_20261016_001/refresh_005'
PRIVATE = Path('/home/cosmosapjw/REI_EXTERNAL_INTAKE_20261016_PUBLIC/refresh005')
REI = ('rei_bianchi', 'edead5026fdcc4217a9caec5106f7839c6aec5a5')
REC = ('rec_bianchi', 'a5e92bd17f1c0a1fd331ee203405d3971c444efb')
REC_PREFIX = 'research/rec_r3g_primordial_20261016/emla_to_z20_001/ncp_execution_001/'
REI_PREFIX = 'research/microphysics_r9_20261015/unit5_t4_resume_20261016/'
started = time.monotonic()
commands = []
files = []
missing = []
public_limit = 2 * 1024 * 1024
public_bytes = 0
private_bytes = 0

def gh_api(repo, endpoint):
    argv = ['gh', 'api', f'repos/cosmosapjw-quantum/{repo}/{endpoint}']
    p = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    commands.append({'argv': argv, 'exit_code': p.returncode, 'stdout_bytes': len(p.stdout), 'stderr': p.stderr.decode('utf-8', 'replace')[:500]})
    if p.returncode:
        missing.append({'repo': repo, 'endpoint': endpoint, 'reason': 'gh_api_failed', 'exit_code': p.returncode})
        return None
    try:
        return json.loads(p.stdout)
    except Exception as e:
        missing.append({'repo': repo, 'endpoint': endpoint, 'reason': 'invalid_json', 'detail': repr(e)})
        return None

def fetch(repo, sha, path, group):
    global public_bytes, private_bytes
    endpoint = f'contents/{path}?ref={sha}'
    item = gh_api(repo, endpoint)
    if item is None:
        return
    if item.get('encoding') != 'base64' or not isinstance(item.get('content'), str):
        missing.append({'repo': repo, 'path': path, 'reason': 'unexpected_contents_response'})
        return
    raw = base64.b64decode(item['content'])
    rel = Path(group) / path
    pubpath = PUB / rel
    privpath = PRIVATE / rel
    if public_bytes + len(raw) > public_limit:
        missing.append({'repo': repo, 'path': path, 'reason': 'public_metadata_cap', 'size_bytes': len(raw)})
        return
    pubpath.parent.mkdir(parents=True, exist_ok=True)
    privpath.parent.mkdir(parents=True, exist_ok=True)
    with open(pubpath, 'xb') as f: f.write(raw)
    with open(privpath, 'xb') as f: f.write(raw)
    digest = hashlib.sha256(raw).hexdigest()
    public_bytes += len(raw); private_bytes += len(raw)
    files.append({'repo': repo, 'commit': sha, 'path': path, 'public_path': str(rel), 'private_path': str(rel), 'size_bytes': len(raw), 'sha256': digest, 'source_api_path': endpoint, 'category': 'compact_source_metadata_or_review'})

def main():
    PUB.mkdir(parents=True, exist_ok=True)
    PRIVATE.mkdir(parents=True, exist_ok=False)
    # Fetch the exact compact REC artifacts pinned by the authority packet.
    rec_paths = [
        'U7_SCOPED_REVIEW.json', 'verification.json', 'source_manifest.json',
        'checkpoint_0012_stop.json', 'U7_RAW_BACKUP.json'
    ]
    for name in rec_paths:
        fetch('rec_bianchi', REC[1], REC_PREFIX + name, 'REC99')
    # Discover changed file names from the exact pinned PR head; fetch only compact
    # candidate/boundary JSON/Markdown source metadata under this approved PR.
    pr_meta = gh_api('rec_bianchi', 'pulls/99')
    if isinstance(pr_meta, dict) and (pr_meta.get('head') or {}).get('sha') != REC[1]:
        missing.append({'repo': 'rec_bianchi', 'path': 'pulls/99', 'reason': 'pinned_head_mismatch', 'observed_head': (pr_meta.get('head') or {}).get('sha'), 'expected_head': REC[1]})
        prfiles = None
    else:
        prfiles = gh_api('rec_bianchi', 'pulls/99/files?per_page=100')
    candidates = []
    if isinstance(prfiles, list):
        for entry in prfiles:
            path = entry.get('filename', '')
            low = path.lower()
            if any(k in low for k in ('boundary', 'candidate', 'q0z20', 'q0_z20')) and path.endswith(('.json', '.md')) and path != REC_PREFIX + 'U7_RAW_BACKUP.json':
                candidates.append(path)
        # Prefer explicit candidate/boundary artifact names; retain all matching
        # compact alternatives so the exact chosen candidate is reviewable.
        for path in sorted(set(candidates)):
            fetch('rec_bianchi', REC[1], path, 'REC99_PR_FILES')
    else:
        missing.append({'repo': 'rec_bianchi', 'path': 'pulls/99/files?per_page=100', 'reason': 'candidate_path_discovery_failed'})
    if not candidates:
        missing.append({'repo': 'rec_bianchi', 'path': None, 'reason': 'exact_q0z20_boundary_candidate_path_not_found_in_pinned_pr_file_list'})
    rei_paths = [
        'REPORT_KO.md', 'progress/DELIVERY_FINAL.json',
        'results/final_run/execution.json', 'results/final_run/native_fixture_config.json',
        'review/IMPLEMENTATION_REVIEW.json'
    ]
    for name in rei_paths:
        fetch('rei_bianchi', REI[1], REI_PREFIX + name, 'REI151')
    snapshot = {
        'schema': 'rei.external_update_intake.refresh005.snapshot.v1',
        'observed_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'repos': {
            'rei_bianchi': {'pinned_pr_head': REI[1], 'prior_head': 'c2928c...', 'source_status': 'new compact evidence captured; not production activation'},
            'rec_bianchi': {'pinned_pr_head': REC[1], 'prior_head': 'd0d5...', 'source_status': 'new compact evidence captured; not production activation'}
        },
        'commands': commands,
        'files': files,
        'candidate_boundary_paths_discovered': sorted(set(candidates)),
        'missing': missing,
        'resources': {'wall_seconds': round(time.monotonic()-started, 6), 'public_bytes': public_bytes, 'private_bytes': private_bytes, 'public_cap_bytes': public_limit},
        'requested_executor': 'historical worker-light Luna/low, no generation override',
        'observed_runtime': 'NOT_INDEPENDENTLY_OBSERVED'
    }
    out = json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True).encode()+b'\n'
    with open(PUB / 'SNAPSHOT.json', 'xb') as f: f.write(out)
    print(json.dumps({'files': len(files), 'missing': len(missing), 'candidate_paths': len(candidates), 'public_bytes': public_bytes, 'private_bytes': private_bytes, 'snapshot_bytes': len(out), 'wall_seconds': snapshot['resources']['wall_seconds']}, sort_keys=True))
    return 0 if not missing else 2

if __name__ == '__main__':
    sys.exit(main())
