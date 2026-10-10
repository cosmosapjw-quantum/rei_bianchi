"""Create-only Q1A evidence overlay; no solver or reference replay."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    base = root / 'research/accel02_20261011'
    files = {p for p in base.rglob('*') if p.is_file()
             and 'target' not in p.parts and '__pycache__' not in p.parts
             and p.suffix not in ('.zip', '.pyc')}
    for name in ['background.py', 'hm12_data.py', 'sources/emissivity.out', 'sources/UVB.out']:
        files.add(root / 'research/physical_provider_20261010' / name)
    files.add(base / 'n1/native/target/release/rei_n1_native')
    payloads = []
    entries = []
    for p in sorted(files):
        data = p.read_bytes()
        name = 'repos/rei_bianchi/' + p.relative_to(root).as_posix()
        mode = p.stat().st_mode
        payloads.append((name, data, mode))
        entries.append(dict(path=name, bytes=len(data), sha256=sha(data), unix_mode=mode))
    results = {}
    for run in sorted((base/'q1a/evidence').glob('GAUSS*')):
        if run.is_dir():
            result = run/'RESULT.json'
            results[run.name] = json.loads(result.read_text())['status'] if result.exists() else 'INCOMPLETE'
    manifest = dict(schema='rei.q1a.checkpoint.v1', stage=args.stage,
        published_restore_base='b29063d75ca86b7c1b777422d5482cc7f1d7ca29',
        local_head=subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip(),
        files=entries, q1a_run_statuses=results, solver_replays_in_packaging=0,
        scope='Evidence overlay; not scientific admission. Restore over published base; preserve executable modes.',
        snapshot_semantics='Each member is individually read and hashed. In-progress run files are diagnostic, not a certified resumable solver checkpoint.')
    if args.output.exists():
        raise FileExistsError(args.output)
    with zipfile.ZipFile(args.output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data, mode in payloads:
            info = zipfile.ZipInfo(name)
            info.create_system = 3
            info.external_attr = mode << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
        archive.writestr('MANIFEST.json', json.dumps(manifest, indent=2)+'\n')
    with zipfile.ZipFile(args.output) as archive:
        assert archive.testzip() is None
        for item in entries:
            assert sha(archive.read(item['path'])) == item['sha256']
            assert archive.getinfo(item['path']).external_attr >> 16 == item['unix_mode']
    receipt = dict(path=str(args.output.resolve()), bytes=args.output.stat().st_size,
        sha256=sha(args.output.read_bytes()), stage=args.stage, manifest_members=len(entries),
        crc_and_member_hashes='PASS', remote_status='NOT_UPLOADED')
    args.output.with_suffix('.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt))

if __name__ == '__main__':
    main()
