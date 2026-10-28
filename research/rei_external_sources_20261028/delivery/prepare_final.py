"""Package selected reviewed unit files; prior source archives remain references."""
import base64
import hashlib
import json
from pathlib import Path

UNIT = Path(__file__).resolve().parents[1]
DEST = UNIT / 'delivery'


def encoded(path):
    data = path.read_bytes()
    binary = path.suffix == '.png'
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'encoding': 'base64' if binary else 'utf-8',
            'content': base64.b64encode(data).decode() if binary else data.decode()}


def main():
    paths = list(UNIT.glob('*.md')) + list(UNIT.glob('*.json'))
    for directory in ('implementation', 'theory', 'review', 'outputs'):
        paths += [p for p in (UNIT / directory).rglob('*')
                  if p.is_file() and '__pycache__' not in p.parts
                  and p.suffix in {'.py', '.md', '.json', '.csv', '.txt', '.png'}]
    paths += [UNIT / 'sources/SOURCE_SYNTHESIS.md', UNIT / 'sources/SKILL_CONTEXT_USED.json',
              DEST / 'PREEXECUTION_PUBLICATION.json', Path(__file__).resolve()]
    public = {p.relative_to(UNIT).as_posix(): encoded(p) for p in sorted(set(paths))}
    # Retrieved article bodies stay local; curated synthesis is sufficient to reproduce code.
    private_paths = list((UNIT / 'intake').glob('*.json'))
    private = {p.relative_to(UNIT).as_posix(): encoded(p) for p in sorted(private_paths)}
    capsule = {'schema': 'REI_EXTERNAL_FINAL_CAPSULE_V1', 'unit': UNIT.name,
               'scientific_decision': 'PASS_SCOPED', 'source_base': '48c5656c3ff396edf61390214c40cbdcc203f172',
               'preexecution_commit': '3a70372726f2be5eb3fc0b28a503e23eb68b8932',
               'public_files': public, 'private_intake_files': private,
               'original_archives': 'Reference prior RUN_DELIVERY_RECEIPT.json and exact baseline input digests; no raw archive duplicated.',
               'literature': 'Retrieved full article bodies omitted, including private delivery. Curated synthesis, citations and own symbolic checks suffice for this code.',
               'final_receipt': 'Git-persisted additive metadata outside this frozen capsule; no circular inclusion.'}
    raw = (json.dumps(capsule, ensure_ascii=False, separators=(',', ':')) + '\n').encode()
    sha = hashlib.sha256(raw).hexdigest()
    name = 'REI_EXTERNAL_SOURCES_FINAL_20261028_' + sha[:12] + '.json'
    (DEST / name).write_bytes(raw)
    manifest = {'schema': 'REI_EXTERNAL_FROZEN_FILE_PLAN_V1', 'filename': name,
                'bytes': len(raw), 'sha256': sha, 'public_count': len(public),
                'private_count': len(private),
                'public_files': {k: {f: v[f] for f in ('bytes', 'sha256', 'encoding')} for k, v in public.items()}}
    (DEST / 'FROZEN_FILE_PLAN.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (DEST / 'public_payload.json').write_text(json.dumps(public, ensure_ascii=False) + '\n')
    print(json.dumps({k: manifest[k] for k in ('filename', 'bytes', 'sha256', 'public_count', 'private_count')}))


if __name__ == '__main__':
    main()
