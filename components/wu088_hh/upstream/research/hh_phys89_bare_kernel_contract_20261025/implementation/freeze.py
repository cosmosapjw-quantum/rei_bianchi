"""Metadata-only source freeze; never imports scientific implementation."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import sys

UNIT = Path(__file__).resolve().parents[1]


def main():
    files = sorted([*(UNIT/'source').glob('*.py'), *(UNIT/'verification').glob('*.py'),
                    *(UNIT/'delivery').glob('*.py'), Path(__file__)])
    manifest = {'schema': 'PHYS89_SOURCE_FREEZE_V1',
                'files': {p.relative_to(UNIT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
                'python': sys.version, 'numpy_distribution_version': importlib.metadata.version('numpy'),
                'scientific_imports': 0, 'scientific_executions': 0}
    target = UNIT/'implementation/FROZEN_FILES.json'
    with target.open('x') as stream:
        json.dump(manifest, stream, indent=2, sort_keys=True); stream.write('\n')


if __name__ == '__main__':
    main()
