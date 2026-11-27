"""Pinned, bounded read-only support for this C1 source snapshot."""
from pathlib import Path
import hashlib, importlib.util, json, sys

LOCK_SHA = '22e6fbb3802edc878f090f511539d777a30e11e9fde66aeadb2ed4bb60ec368f'
VENDOR_SHA = {
    'engine': 'e10f206d63be1a99a441780108619574605014a9b01b3b327e21fecb18c5b9cc',
    'decoder': 'bf1867616af07a670d61cd75c7ca0655c99e0be13fd6a73e9a4654f5fc0986f1',
}
MAX_FILE = 2 * 1024 * 1024

class BindingError(ValueError):
    """Malformed, unbound or changed data; no result may be admitted."""

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def read_bytes(root: Path, relative: str) -> bytes:
    root = Path(root).resolve()
    p = Path(relative)
    if p.is_absolute() or '..' in p.parts:
        raise BindingError('unsafe source path')
    target = root / p
    if any((root / Path(*p.parts[:i])).is_symlink() for i in range(1, len(p.parts)+1)):
        raise BindingError('symlink source not allowed')
    if not target.is_file() or target.stat().st_size > MAX_FILE:
        raise BindingError('missing or oversized source: ' + relative)
    return target.read_bytes()

def _pairs(items):
    out = {}
    for k,v in items:
        if k in out:
            raise BindingError('duplicate JSON key')
        out[k] = v
    return out

def loads(data, *, tokens=False):
    def reject(value):
        raise BindingError('nonfinite JSON number: ' + value)
    try:
        return json.loads(data, object_pairs_hook=_pairs,
                          parse_float=str if tokens else float, parse_constant=reject)
    except (ValueError, TypeError, RecursionError) as exc:
        raise BindingError('invalid bounded JSON') from exc

def verify_sources(root):
    data = read_bytes(root, 'SOURCE_LOCK.json')
    if sha(data) != LOCK_SHA:
        raise BindingError('SOURCE_LOCK identity changed')
    lock = loads(data)
    seen = set()
    for row in lock['files']:
        if row['path'] in seen:
            raise BindingError('duplicate locked path')
        seen.add(row['path'])
        blob = read_bytes(root,row['path'])
        if len(blob) != row['bytes'] or sha(blob) != row['sha256']:
            raise BindingError('source identity mismatch: ' + row['path'])
    return lock

def vendor(name):
    if name not in VENDOR_SHA:
        raise BindingError('unsupported vendor module')
    p = Path(__file__).resolve().parent / 'vendor' / (name + '.py')
    if p.is_symlink() or sha(p.read_bytes()) != VENDOR_SHA[name]:
        raise BindingError('vendor identity changed')
    key = '_wu088_c1_pinned_' + name
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key,p)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]
