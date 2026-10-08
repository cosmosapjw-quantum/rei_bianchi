#!/usr/bin/env python3
"""Verify pinned local archives; optionally reconstruct fresh source, never run science."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, stat, zipfile

HERE = Path(__file__).resolve().parent
PROJECTS = {
    'canonical_ledger':'rei-ledger-admission-v1',
    'real_native_caller':'rei-ledger-real-caller-v1',
    'live_native_restart':'rei-receiver-restart-v1',
    'frozen_checkpoint':'rei-continuous-checkpoint-v1',
    'midpoint_records':'rei-midpoint-record-v1',
    'species_sidecar_dependency':'rei-species-energy-sidecar-v1',
}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive-dir', type=Path, required=True)
    p.add_argument('--destination', type=Path)
    p.add_argument('--verify-only', action='store_true')
    a = p.parse_args()
    if a.verify_only == (a.destination is not None):
        p.error('choose exactly one of --verify-only or --destination')
    if a.destination is not None and a.destination.exists():
        p.error('destination must not exist; archived runtime directories are not run seeds')
    artifacts = json.loads((HERE/'ARTIFACTS.json').read_text())
    source_map = json.loads((HERE/'SOURCE_MAP.json').read_text())
    notices = json.loads((HERE/'LICENSE_ORIGINS.json').read_text())
    license_files = {}
    for row in notices:
        blob = (HERE/row['public_path']).read_bytes()
        if len(blob) != row['bytes'] or hashlib.sha256(blob).hexdigest() != row['sha256']:
            raise ValueError('license notice identity mismatch')
        license_files[row['public_path']] = blob
    found = {}
    source = {}
    for item in artifacts:
        archive = a.archive_dir/item['file_name']
        data = archive.read_bytes()
        if len(data) != item['bytes'] or hashlib.sha256(data).hexdigest() != item['sha256']:
            raise ValueError('archive identity mismatch: '+item['file_name'])
        with zipfile.ZipFile(archive) as z:
            if z.testzip() is not None:
                raise ValueError('archive CRC failure: '+item['file_name'])
            for info in z.infolist():
                rel = PurePosixPath(info.filename)
                if rel.is_absolute() or '..' in rel.parts:
                    raise ValueError('unsafe archive member')
                if stat.S_IFMT(info.external_attr >> 16) == stat.S_IFLNK:
                    raise ValueError('archive symlink')
                if info.is_dir() or len(rel.parts)<2:
                    continue
                tail = PurePosixPath(*rel.parts[1:])
                # Drop forensic state, logs, results and old failure trees.
                if any(x in {'evidence','logs','results','target','__pycache__'} for x in tail.parts):
                    continue
                keep = tail.suffix in {'.rs','.toml','.lock','.cfg','.py'} or 'inputs' in tail.parts or ('tests' in tail.parts and tail.suffix in {'.csv','.tsv'}) or 'LICENSE' in tail.name.upper() or tail.name.upper().startswith('COPYING')
                if not keep:
                    continue
                key = PROJECTS[item['scope']]+'/'+str(tail)
                blob = z.read(info)
                found[key] = hashlib.sha256(blob).hexdigest()
                if not a.verify_only:
                    source[key] = blob
    for row in source_map['files']:
        if found.get(row['restore_path']) != row['sha256']:
            raise ValueError('source map mismatch: '+row['restore_path'])
        if row['source']['kind']=='payload':
            blob = (HERE/row['source']['path']).read_bytes()
            if hashlib.sha256(blob).hexdigest()!=row['sha256']:
                raise ValueError('public source payload mismatch')
    if not a.verify_only:
        # Supplement exact archived source with pinned upstream notices; retain
        # any notices already present in the archive without overwriting them.
        for project in PROJECTS.values():
            for name, blob in license_files.items():
                source.setdefault(project+'/'+name, blob)
        source.update(license_files)
        a.destination.mkdir(parents=True, exist_ok=False)
        for key, blob in source.items():
            dst = a.destination/key
            dst.parent.mkdir(parents=True, exist_ok=True)
            with dst.open('xb') as out:
                out.write(blob)
    print(json.dumps({'archives':len(artifacts),'mapped_source_files_verified':len(source_map['files']),'fresh_source_files_available':len(found),'pinned_license_notices_verified':len(license_files),'science_runs':0,'mode':'verify-only' if a.verify_only else 'fresh-source-materialization'}))

if __name__=='__main__':
    main()
