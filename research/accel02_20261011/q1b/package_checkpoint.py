"""Create-only, immutable-commit evidence overlay. No solver execution."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import zipfile


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--stage', required=True)
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    root = Path(__file__).resolve().parents[3]
    def git(*argv):
        return subprocess.check_output(['git', '-C', str(root), *argv])
    head = git('rev-parse', 'HEAD').decode().strip()
    tree = git('rev-parse', 'HEAD^{tree}').decode().strip()
    paths = ['research/accel02_20261011',
             'research/physical_provider_20261010/background.py',
             'research/physical_provider_20261010/hm12_data.py',
             'research/physical_provider_20261010/sources/emissivity.out',
             'research/physical_provider_20261010/sources/UVB.out',
             '.github/workflows/q1b-local.yml']
    payloads = []
    with tarfile.open(fileobj=io.BytesIO(git('archive', '--format=tar', head, *paths))) as tar:
        for member in tar:
            if member.isfile():
                payloads.append((member.name, tar.extractfile(member).read(), member.mode))
    for relative in ['research/accel02_20261011/n1/native/target/release/rei_n1_native',
                     'research/accel02_20261011/q1b/native/target/release/rei_q1b_cell_native_v1']:
        f = root / relative
        if f.exists():
            payloads.append((relative, f.read_bytes(), 0o755))
    entries = []
    with zipfile.ZipFile(args.output, 'x', compression=zipfile.ZIP_DEFLATED) as z:
        for name, data, mode in payloads:
            arc = 'repos/rei_bianchi/' + name
            zi = zipfile.ZipInfo(arc)
            zi.create_system = 3
            zi.external_attr = (0o100000 | mode) << 16
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, data)
            entries.append(dict(path=arc, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), unix_mode=mode))
        manifest = dict(schema='rei.q1b.checkpoint.v1', stage=args.stage, local_commit=head,
                        local_tree=tree, restore_base='8ffd1d22f933548f7643b57eb4f774ac87661e4e',
                        snapshot='Immutable committed source/evidence plus explicitly hashed available native binaries',
                        scope='Research overlay on published Git base; not standalone checkout or scientific admission',
                        files=entries, solver_executions=0)
        z.writestr('MANIFEST.json', json.dumps(manifest, indent=2)+'\n')
    with zipfile.ZipFile(args.output) as z:
        assert z.testzip() is None
        for e in entries:
            assert hashlib.sha256(z.read(e['path'])).hexdigest() == e['sha256']
            assert (z.getinfo(e['path']).external_attr >> 16) & 0o777 == e['unix_mode']
    receipt = dict(stage=args.stage, path=str(args.output.resolve()), bytes=args.output.stat().st_size,
                   sha256=hashlib.sha256(args.output.read_bytes()).hexdigest(),
                   local_commit=head, local_tree=tree, members=len(entries),
                   crc_and_member_hashes='PASS', remote_status='NOT_UPLOADED')
    args.output.with_suffix('.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
