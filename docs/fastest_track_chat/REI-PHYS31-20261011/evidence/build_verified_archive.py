#!/usr/bin/env python3
"""Package a closed PHYS31 record and restore bytes only; never execute science."""
from pathlib import Path, PurePosixPath
from hashlib import sha256, sha1
from datetime import datetime, timezone
import json
import os
import stat
import zipfile

ROOT = Path('/workspace/scratch/603081e41728/phys31')
RELEASE = Path('/workspace/scratch/603081e41728/phys31_release')
ARCHIVE_ROOT = 'REI-PHYS31-20261011'
ARCHIVE = RELEASE / 'PHYS31_RESEARCH_PACKAGE.zip'
RESTORE = RELEASE / 'outer_restore_once'


def identity(path, relative_to=ROOT):
    data = path.read_bytes()
    return {
        'path': path.relative_to(relative_to).as_posix(),
        'bytes': len(data),
        'sha256': sha256(data).hexdigest(),
        'git_blob_sha': sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest(),
        'mode': stat.S_IMODE(path.stat().st_mode),
    }


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    # This is an owner packaging gate, not a second scientific decision.
    closeout = json.loads((ROOT / 'state/CLOSEOUT.json').read_text())
    gate = json.loads((ROOT / 'evidence/OWNER_FINAL_GATE.json').read_text())
    assert closeout['status'] == 'RESEARCH_CLOSED_PROMOTE_SCOPED'
    assert gate['status'] == 'GO_ADDITIVE_DOCS_AND_DELIVERY'
    assert gate['actual_review_decision'] == 'PROMOTE_SCOPED'
    assert gate['fatal_issue_count'] == 0
    assert gate['required_rework_count'] == 0
    authority = identity(ROOT / 'independent/DECISION_REVIEW.json')
    assert authority['sha256'] == gate['actual_review_sha256']
    freeze = json.loads((ROOT / 'evidence/CANDIDATE_FROZEN.json').read_text())
    for old in freeze['files']:
        current = identity(ROOT / old['path'])
        assert {key: current[key] for key in old} == old, old['path']

    assert not ARCHIVE.exists(), 'One archive construction: preserve any first failure before repair.'
    assert not RESTORE.exists(), 'Use a genuinely new outer restoration directory.'
    all_paths = sorted(ROOT.rglob('*'))
    assert not any(path.is_symlink() for path in all_paths)
    # Only the top-level MANIFEST is excluded; nested manifests remain payloads.
    payloads = [path for path in all_paths if path.is_file() and path != ROOT / 'MANIFEST.json']
    entries = [identity(path) for path in payloads]
    manifest = {
        'task': ARCHIVE_ROOT,
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'CLOSED_RESEARCH_PAYLOAD_MANIFEST',
        'files': entries,
        'payload_count_excluding_this_manifest': len(entries),
        'total_payload_bytes_excluding_this_manifest': sum(entry['bytes'] for entry in entries),
        'excluded': ['This top-level MANIFEST itself', 'Detached archive/publication/delivery receipts generated later'],
        'scientific_execution_from_packaging': 0,
    }
    write_json(ROOT / 'MANIFEST.json', manifest)
    all_payloads = payloads + [ROOT / 'MANIFEST.json']
    with zipfile.ZipFile(ARCHIVE, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(all_payloads):
            name = ARCHIVE_ROOT + '/' + path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 11, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | stat.S_IMODE(path.stat().st_mode)) << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    RESTORE.mkdir()
    expected_names = {ARCHIVE_ROOT + '/' + path.relative_to(ROOT).as_posix() for path in all_payloads}
    with zipfile.ZipFile(ARCHIVE) as archive:
        members = archive.infolist()
        names = [item.filename for item in members]
        assert len(names) == len(set(names))
        assert set(names) == expected_names
        for item in members:
            name = PurePosixPath(item.filename)
            assert not name.is_absolute() and '..' not in name.parts
            assert name.parts[0] == ARCHIVE_ROOT
            mode = item.external_attr >> 16
            assert stat.S_ISREG(mode)
            target = RESTORE / item.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(item))
            os.chmod(target, stat.S_IMODE(mode))

    restored_root = RESTORE / ARCHIVE_ROOT
    for path in all_payloads:
        rel = path.relative_to(ROOT)
        assert identity(path) == identity(restored_root / rel, restored_root), rel
    assert (restored_root / 'MANIFEST.json').read_bytes() == (ROOT / 'MANIFEST.json').read_bytes()
    receipt = {
        'task': ARCHIVE_ROOT,
        'status': 'LOCAL_OUTER_ARCHIVE_RESTORE_PASS',
        'observed_utc': datetime.now(timezone.utc).isoformat(),
        'archive': identity(ARCHIVE, RELEASE),
        'archive_root': ARCHIVE_ROOT,
        'payload_files_including_manifest': len(all_payloads),
        'manifest': identity(ROOT / 'MANIFEST.json'),
        'actual_restore_root': str(restored_root),
        'exact_path_set_SHA256_size_mode_verified': True,
        'restored_scientific_program_executions': 0,
        'PHYS31_scientific_main_total_unchanged': 2,
        'PHYS31_physical_k4_calls_total_unchanged': 16,
        'prior_scientific_runtime_replay': 'Already completed once; portability/REPLAY_RECEIPT.json',
        'same_host': True,
        'remote_full_archive_restore_claim': False,
        'receipt_is_detached_to_avoid_hash_cycle': True,
    }
    write_json(RELEASE / 'PHYS31_OUTER_PACKAGE_RECEIPT.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__':
    main()
