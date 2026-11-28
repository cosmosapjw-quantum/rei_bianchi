"""Metadata and create-only results. Importing this module runs no science."""
from pathlib import Path
import hashlib
import json

UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
CONTRACT_SHA = 'd737abf473a8ee6ef2c98262d4c6bb463e5ac800aab7eb442ed56d4e56baf663'


def canonical(obj):
    return (json.dumps(obj, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    from fractions import Fraction
    from decimal import Decimal
    if isinstance(value, (Fraction, Decimal)):
        return str(value)
    if isinstance(value, dict):
        return {k: encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(v) for v in value]
    return value


def identity():
    contract_raw = (UNIT/'CONTRACT.json').read_bytes()
    if sha(contract_raw) != CONTRACT_SHA:
        raise ValueError('FROZEN_CONTRACT_MISMATCH')
    contract = json.loads(contract_raw)
    manifest = json.loads((UNIT/'implementation/FROZEN_FILES.json').read_text())
    for path, digest in manifest['files'].items():
        if sha((UNIT/path).read_bytes()) != digest:
            raise ValueError('FROZEN_FILE_MISMATCH:'+path)
    if sha((REPO/contract['source']['path']).read_bytes()) != contract['source']['sha256']:
        raise ValueError('SOURCE_MISMATCH')
    binding = {'parent_head': contract['parent_final_head'], 'parent_tree': contract['parent_final_tree'],
               'parent_scientific_identity': contract['parent_scientific_identity'],
               'contract_sha256': CONTRACT_SHA, 'source_sha256': contract['source']['sha256'],
               'code_files': manifest['files']}
    return {'sha256': sha(canonical(binding)), 'binding': binding}


def resume(output, kind, expected):
    """Metadata only: no kernel import, parser, eigensolve or result rewrite."""
    output = Path(output)
    manifest = json.loads((output/'MANIFEST.json').read_text())
    if manifest['kind'] != kind or manifest['identity'] != expected:
        raise ValueError('RESUME_IDENTITY_MISMATCH')
    for name, digest in manifest['payload_sha256'].items():
        if Path(name).name != name or sha((output/name).read_bytes()) != digest:
            raise ValueError('RESUME_PAYLOAD_MISMATCH')
    return {'status': 'SKIP_COMPLETE_READ_ONLY', 'kind': kind, 'scientific_callbacks': 0,
            'integrals': 0, 'rewrites': 0, 'identity': expected['sha256'],
            'manifest_sha256': sha((output/'MANIFEST.json').read_bytes())}


def publish(output, kind, binding, payloads):
    output = Path(output)
    if output.exists():
        raise FileExistsError('CREATE_ONLY_OUTPUT_ALREADY_EXISTS')
    output.mkdir(parents=True)
    hashes = {}
    for name, obj in payloads.items():
        raw = canonical(encode(obj))
        with (output/name).open('xb') as stream:
            stream.write(raw)
        hashes[name] = sha(raw)
    with (output/'MANIFEST.json').open('xb') as stream:
        stream.write(canonical({'kind': kind, 'identity': binding, 'payload_sha256': hashes,
                                'status': 'COMPLETE', 'old_science_calls': 0, 'integrals': 0,
                                'new_ODE': 0, 'benchmark': 0, 'HH_R10': 'OFF'}))


def main_args(kind):
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--resume', action='store_true')
    if kind == 'reference':
        p.add_argument('--primary-output', type=Path, required=True)
    return p.parse_args()
