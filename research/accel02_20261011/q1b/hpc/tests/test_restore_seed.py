import hashlib
import json
from pathlib import Path
import sys
import zipfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from restore_private_seed import PREFIX, MANIFEST, restore


def kit(tmp_path, *, bad=False, unsafe=False, bad_pin=False, bad_seed=False):
    payloads = {PREFIX+'seed/CHECKPOINTS/gen-00000001/manifest.json': b'{}\n',
                PREFIX+('seed/../../../../escape' if unsafe else 'seed/program'): b'synthetic\n'}
    rows = [{'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
             'mode': 0o755 if name.endswith('program') else 0o644} for name, data in payloads.items()]
    if bad:
        rows[-1]['sha256'] = '0' * 64
    metadata = {'files': rows, 'seed_relative_path': PREFIX+'seed',
                'checkpoint_relative_path': PREFIX+'seed/CHECKPOINTS/gen-00000001',
                'checkpoint_manifest_sha256': rows[0]['sha256']}
    if bad_pin:
        metadata['checkpoint_manifest_sha256'] = '0'*64
    if bad_seed:
        metadata['seed_relative_path'] = PREFIX+'../../escape'
    zpath = tmp_path/'seed.zip'
    with zipfile.ZipFile(zpath, 'w') as z:
        for name, data in payloads.items():
            z.writestr(name, data)
        z.writestr(MANIFEST, json.dumps(metadata))
    return zpath, hashlib.sha256(zpath.read_bytes()).hexdigest()


def test_missing_only_restore_retains_bytes_and_mode(tmp_path):
    archive, digest = kit(tmp_path)
    repo = tmp_path/'repo'; repo.mkdir()
    first = restore(archive, repo, digest)
    p = repo/'seed/program'; before = p.stat().st_mtime_ns
    assert p.stat().st_mode & 0o111
    second = restore(archive, repo, digest)
    assert first['created_files'] == second['preserved_existing_files'] == 2
    assert second['created_files'] == 0 and p.stat().st_mtime_ns == before
    p.write_text('different')
    with pytest.raises(ValueError, match='EXISTING_FILE_DIFFERS'):
        restore(archive, repo, digest)


@pytest.mark.parametrize('kwargs', [{'bad': True}, {'unsafe': True}, {'bad_pin': True}, {'bad_seed': True}])
def test_preflight_failure_leaves_repo_empty(tmp_path, kwargs):
    archive, digest = kit(tmp_path, **kwargs)
    repo = tmp_path/'repo'; repo.mkdir()
    with pytest.raises(ValueError):
        restore(archive, repo, digest)
    assert list(repo.iterdir()) == []


def test_size_limit_applies_before_manifest_read(tmp_path):
    archive, digest = kit(tmp_path)
    repo = tmp_path/'repo'; repo.mkdir()
    with pytest.raises(ValueError, match='UNCOMPRESSED_LIMIT'):
        restore(archive, repo, digest, max_bytes=1)
    assert list(repo.iterdir()) == []
