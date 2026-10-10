"""Archive completed evidence without replaying a solver. Run from repository root."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument('--mode', choices=['raw', 'final'], required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
root = Path.cwd()
base = root / 'research/accel02_20261011'
run = base / 'n2/evidence/EVENT_COUPLED003_RECOVERED'
result = json.loads((run / 'RESULT.json').read_text())
assert (run / 'history.npz').is_file()
files = set()
if args.mode == 'raw':
    for name in ['RESULT.json', 'history.npz', 'IDENTITY.json', 'EVENTS.json',
                 'PROGRESS.json', 'driver_as_run.py', 'base_driver_as_run.py',
                 'FIRST_FAILURE.json', 'LAST_ACCEPTED.npz', 'RESTART.npz']:
        if (run / name).is_file():
            files.add(run / name)
    for part in ['n1', 'recovery']:
        files.update(p for p in (base / part).rglob('*') if p.is_file()
                     and 'target' not in p.parts and '__pycache__' not in p.parts)
    for name in ['n2/CONTRACT.md', 'integration/CONTRACT.json',
                 'integration/run_native_history.py', 'n2/run_event_coupled.py']:
        if (base / name).is_file():
            files.add(base / name)
else:
    files.update(p for p in base.rglob('*') if p.is_file()
                 and 'target' not in p.parts and '__pycache__' not in p.parts)
    for name in ['background.py', 'hm12_data.py',
                 'sources/emissivity.out', 'sources/UVB.out']:
        files.add(root / 'research/physical_provider_20261010' / name)
files.add(base / 'n1/native/target/release/rei_n1_native')
entries = []
payloads = []
for path in sorted(files):
    data = path.read_bytes()
    name = 'repos/rei_bianchi/' + path.relative_to(root).as_posix()
    entries.append(dict(path=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                        unix_mode=path.stat().st_mode))
    payloads.append((name, data, path.stat().st_mode))
manifest = dict(schema='rei_accel02_checkpoint_v1', mode=args.mode,
                published_restore_base='304afc3592ae60242e3bb72efc56d806519b4a60',
                local_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                run_status=result['status'], files=entries,
                scope='Evidence checkpoint; packaging does not grant scientific admission',
                solver_replays_in_packaging=0)
assert not args.output.exists(), 'create-only checkpoint'
with zipfile.ZipFile(args.output, 'w', compression=zipfile.ZIP_DEFLATED) as out:
    for name,data,mode in payloads:
        info=zipfile.ZipInfo(name)
        info.create_system=3
        info.external_attr=mode << 16
        info.compress_type=zipfile.ZIP_DEFLATED
        out.writestr(info,data)
    out.writestr('MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(args.output) as saved:
    assert saved.testzip() is None
    for entry in entries:
        assert hashlib.sha256(saved.read(entry['path'])).hexdigest()==entry['sha256']
        assert saved.getinfo(entry['path']).external_attr >> 16 == entry['unix_mode']
receipt=dict(path=str(args.output.resolve()), bytes=args.output.stat().st_size,
             sha256=hashlib.sha256(args.output.read_bytes()).hexdigest(),
             manifest_members=len(entries), crc_and_member_hashes='PASS',
             remote_status='NOT_UPLOADED')
args.output.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
