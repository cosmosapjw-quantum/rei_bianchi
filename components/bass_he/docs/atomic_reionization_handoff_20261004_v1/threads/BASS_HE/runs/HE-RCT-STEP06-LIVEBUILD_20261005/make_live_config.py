"""Generate a fresh worker-bound config; never migrate a previous checkpoint.

The original controller remains byte-identical. Only its legacy dependency labels
are replaced by the explicit current-library build identity. Numerical inputs and
synthetic closure conventions are inherited unchanged from that controller.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'staging/controller'))
import restart

def verify_sources() -> None:
    manifest = json.loads((ROOT / 'inputs/PINNED_BUILD_FILES.json').read_text())
    for name, rec in manifest.items():
        data = (ROOT / 'staging' / name).read_bytes()
        if len(data) != rec['bytes'] or hashlib.sha256(data).hexdigest() != rec['sha256']:
            raise ValueError('SOURCE_IDENTITY_CHANGED:' + name)

def make_live_contract(worker: Path, source: str = 'KF96', offset: float = 0.) -> dict:
    verify_sources()
    pin = json.loads((ROOT / 'INPUT_PIN.json').read_text())
    c = restart.make_contract(worker, source=source, offset=offset)
    c.pop('dependency_archive_sha256')
    c.update(dependency_commit=pin['consumer_commit'],
             dependency_root_tree=pin['consumer_tree'],
             dependency_source_tree=pin['consumer_library_src_tree'],
             supplier_addon_archive_sha256=pin['supplier_addon_archive_sha256'],
             build_scope='CURRENT_FULL_LIBRARY_STATIC_RCT_CALLER',
             owner_dispatcher_adoption=False)
    return c

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source', choices=['OFF', 'KF96'], default='OFF')
    parser.add_argument('--offset-ev', type=float, default=0.)
    args = parser.parse_args()
    if args.offset_ev not in (-1., 0., 1.):
        parser.error('this delivery covers only synthetic Q-1/Q/Q+1 validation closures')
    config = make_live_contract(args.worker.resolve(), args.source, args.offset_ev)
    with args.output.open('x') as stream:
        json.dump(config, stream, indent=2)
        stream.write('\n')
