#!/usr/bin/python3
"""One-pass, stdlib-only capture of frozen SOURCE012 inputs; never executes source."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path('/home/cosmosapjw/Dropbox/bianchi/rei_bianchi')
PUB = REPO / 'research/bass_source012_source_age_reference_20261016/intake_001'
PRIVATE = Path('/home/cosmosapjw/REI_PRIVATE_SOURCE012_INPUTS_20261016')
SUPPLIER = '553ce556d9f8662290c000ec675c7e6007c9d895'
NATIVE = '35d9747a0bbedcafdb568467ce7c1e7a25f965b6'
PREFIX = 'research/rei_source_age_native_owner_bind_20261016/'
ELF = Path('/tmp/rei-source-age-native-owner-bind/native/rust/rei_microphysics/target/release/examples/source_age_campaign')
ELF_SHA = '9d052a5b5e6a22372f4214325a1f2246f98387907f5055c50ee5a844dc3f6f55'
ELF_SIZE = 1093552
MAX_PRIVATE = 134217728
MAX_PUBLIC = 2097152
start = time.monotonic()
cpu0 = time.process_time()
result = {
    'schema': 'rei.bass_source012_source_age_reference.collection.v1',
    'status': 'HOLD', 'reason': None,
    'supplier_commit': SUPPLIER, 'native_base_source_pin': NATIVE,
    'supplier_overlay_relation': 'separate supplier overlay/accessor; native pin is base, not full compiled ELF identity',
    'files': [], 'missing': [], 'commands': [], 'resources': {},
    'requested_executor': 'historical COSTROUTE01 worker-light Luna/low, no generation override',
    'observed_runtime': 'NOT_INDEPENDENTLY_OBSERVED',
    'scientific_decision': 'NOT_MADE_BY_COLLECTOR',
}

def record_cmd(argv, rc, data):
    result['commands'].append({'argv': argv, 'exit_code': rc, 'returned_bytes': len(data)})
    return data

def git_bytes(revpath):
    argv = ['git', 'show', revpath]
    p = subprocess.run(argv, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    record_cmd(argv, p.returncode, p.stdout)
    if p.returncode:
        result['missing'].append({'path': revpath, 'reason': 'git_show_failed', 'exit_code': p.returncode, 'stderr': p.stderr.decode('utf-8', 'replace')[:500]})
        return None
    return p.stdout

def put(root, rel, data, category):
    dest = root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, 'xb') as f:
        f.write(data)
    result['files'].append({'category': category, 'path': str(dest.relative_to(root)), 'size_bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})

def selected_supplier_paths():
    argv = ['git', 'ls-tree', '-r', '--name-only', SUPPLIER, PREFIX]
    p = subprocess.run(argv, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    record_cmd(argv, p.returncode, p.stdout)
    if p.returncode:
        result['missing'].append({'path': PREFIX, 'reason': 'git_ls_tree_failed', 'exit_code': p.returncode})
        return []
    paths = [x.decode() for x in p.stdout.splitlines() if x]
    chosen = set()
    compact = {'BACKUP_RECEIPT.json', 'HANDOFF_KO.md', 'INDEPENDENT_REVIEW.json', 'README_KO.md', 'RESULT_STATUS.json', 'SOURCE_IDENTITY.json', 'SOURCE_SURVEY.json', 'THEORY_KO.md', 'WORKER_RETURN_CONTRACT.json', 'analyze_refinement.py', 'campaign.rs', 'independent_solver.py', 'install_accessor.py', 'native_owner.rs', 'prepare_native.py', 'prepared_node_accessor.patch', 'prepared_node_accessor.rs', 'run_local.sh', 'source_matched_solver.py', 'source_reference.rs', 'terminal_cut_regression.py'}
    explicit = {
        'evidence/repaired_ncp/history.csv',
        'evidence/repaired_source_reference/source_setup_q-0.1.json',
        'evidence/repaired_source_reference/source_native_q-0.1_level1.json',
        'evidence/repaired_source_reference/source_native_q-0.1_level2.json',
        'evidence/repaired_source_reference/source_native_q-0.1_level4.json',
        'evidence/source_matched_first_failure.stderr',
        'evidence/repaired_source_reference/first_invalid_trial_q-0.1.npy',
        'evidence/refinement_summary.json',
    }
    explicit.update(f'evidence/repaired_ncp/snapshot_q-0.1_axis1_level{n}.txt' for n in (1, 2, 4))
    for path in paths:
        rel = path[len(PREFIX):]
        if '/' not in rel or rel in compact or rel.startswith('contracts/') or rel in explicit:
            chosen.add(path)
    return sorted(chosen)

def native_files_and_includes():
    # Enumerate only pinned Rust crate tracked sources. No archive extraction.
    argv = ['git', 'ls-tree', '-r', '--name-only', NATIVE, 'rust/rei_microphysics']
    p = subprocess.run(argv, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    record_cmd(argv, p.returncode, p.stdout)
    if p.returncode:
        result['missing'].append({'path': 'rust/rei_microphysics', 'reason': 'native_ls_tree_failed', 'exit_code': p.returncode})
        return [], []
    files = [x.decode() for x in p.stdout.splitlines() if x]
    # Include crate source/config/lock only, excluding build and generated output trees.
    chosen = [x for x in files if not any(seg in x.split('/') for seg in ('target', '.git'))]
    deps = set()
    pat = re.compile(rb'include_(?:str|bytes)!\s*\(\s*"([^"\n]+)"\s*\)', re.S)
    for path in chosen:
        if not path.endswith('.rs'):
            continue
        blob = git_bytes(f'{NATIVE}:{path}')
        if blob is None:
            continue
        for match in pat.finditer(blob):
            raw = match.group(1).decode('utf-8', 'replace')
            if raw.startswith('/'):
                result['missing'].append({'path': path, 'dependency': raw, 'reason': 'absolute_include_requires_review'})
                continue
            resolved = os.path.normpath(os.path.join(os.path.dirname(path), raw))
            deps.add(resolved)
    return chosen, sorted(deps)

def main():
    PUB.mkdir(parents=True, exist_ok=True)
    PRIVATE.mkdir(parents=True, exist_ok=False)
    supplier_paths = selected_supplier_paths()
    priv_bytes = pub_bytes = 0
    for path in supplier_paths:
        blob = git_bytes(f'{SUPPLIER}:{path}')
        if blob is None:
            continue
        rel = path[len(PREFIX):]
        if priv_bytes + len(blob) > MAX_PRIVATE:
            result['missing'].append({'path': rel, 'reason': 'private_payload_cap'})
            continue
        put(PRIVATE / 'supplier', rel, blob, 'supplier_overlay_or_evidence')
        priv_bytes += len(blob)
    native_paths, deps = native_files_and_includes()
    for path in native_paths:
        blob = git_bytes(f'{NATIVE}:{path}')
        if blob is None:
            continue
        rel = path.removeprefix('rust/rei_microphysics/')
        if priv_bytes + len(blob) > MAX_PRIVATE:
            result['missing'].append({'path': path, 'reason': 'private_payload_cap'})
            continue
        put(PRIVATE / 'native_base', rel, blob, 'native_base_source')
        priv_bytes += len(blob)
    for path in deps:
        blob = git_bytes(f'{NATIVE}:{path}')
        if blob is None:
            continue
        if priv_bytes + len(blob) > MAX_PRIVATE:
            result['missing'].append({'path': path, 'reason': 'private_payload_cap'})
            continue
        put(PRIVATE / 'native_static_dependencies' / Path(path).name, blob, 'native_static_dependency')
        priv_bytes += len(blob)
    # The designated ELF is copied once, hashing as it is copied. Never execute it.
    elf_dest = PRIVATE / 'native_overlay_binary/source_age_campaign'
    elf_dest.parent.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256(); n = 0
    try:
        with open(ELF, 'rb') as src, open(elf_dest, 'xb') as dst:
            while True:
                chunk = src.read(1024 * 1024)
                if not chunk: break
                n += len(chunk); h.update(chunk); dst.write(chunk)
        elf_sha = h.hexdigest()
        result['files'].append({'category': 'supplier_overlay_compiled_elf_copy_only', 'path': str(elf_dest.relative_to(PRIVATE)), 'size_bytes': n, 'sha256': elf_sha, 'executed': False})
        priv_bytes += n
        if n != ELF_SIZE or elf_sha != ELF_SHA:
            result['missing'].append({'path': str(ELF), 'reason': 'elf_size_or_sha_mismatch', 'observed_size': n, 'observed_sha256': elf_sha, 'expected_size': ELF_SIZE, 'expected_sha256': ELF_SHA})
    except Exception as e:
        result['missing'].append({'path': str(ELF), 'reason': 'elf_copy_failed', 'detail': repr(e)})
    result['resources'] = {'private_payload_bytes': priv_bytes, 'private_payload_cap_bytes': MAX_PRIVATE, 'public_metadata_cap_bytes': MAX_PUBLIC, 'native_base_source_files': len(native_paths), 'static_dependency_paths': deps, 'supplier_selected_files': len(supplier_paths), 'wall_seconds': round(time.monotonic() - start, 6), 'cpu_seconds': round(time.process_time() - cpu0, 6)}
    if priv_bytes > MAX_PRIVATE:
        result['missing'].append({'reason': 'private_payload_cap_exceeded', 'observed_bytes': priv_bytes})
    if result['missing']:
        result['reason'] = 'MISSING_OR_IDENTITY_OR_RESOURCE_HOLD'
    else:
        result['status'] = 'COLLECTION_COMPLETE'
        result['reason'] = None
    out = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True).encode() + b'\n'
    if len(out) > MAX_PUBLIC:
        result['status'] = 'HOLD'; result['reason'] = 'PUBLIC_METADATA_CAP'
        result['missing'].append({'reason': 'public_metadata_cap', 'observed_bytes': len(out), 'cap_bytes': MAX_PUBLIC})
        out = json.dumps({'schema': result['schema'], 'status': 'HOLD', 'reason': result['reason'], 'missing': result['missing'], 'resources': result['resources']}, ensure_ascii=False, indent=2).encode() + b'\n'
    with open(PUB / 'COLLECTION_MANIFEST.json', 'xb') as f:
        f.write(out)
    print(json.dumps({'status': result['status'], 'supplier_selected_files': len(supplier_paths), 'native_base_files': len(native_paths), 'static_dependencies': len(deps), 'missing_count': len(result['missing']), 'private_payload_bytes': priv_bytes, 'manifest_bytes': len(out)}, sort_keys=True))
    return 0 if result['status'] == 'COLLECTION_COMPLETE' else 2

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        # Preserve the exception as a compact factual failure if possible; no retry.
        print('COLLECTOR_FATAL: ' + repr(e), file=sys.stderr)
        sys.exit(3)
