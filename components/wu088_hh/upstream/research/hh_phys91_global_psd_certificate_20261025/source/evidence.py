"""PHYS91 metadata-only identity, create-only evidence and read-only resume."""
from pathlib import Path
import hashlib
import json
UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
CONTRACT_SHA = '361826f7940542e05c1461bf879d43808007aad092c58579c762dacce8ca5a39'
FROZEN_PATHS = {
    'CONTRACT.json', 'theory/GLOBAL_PSD_CERTIFICATE_KO.md', 'theory/WOLFRAM_INPUT.wl',
    'source/kernel.py', 'source/primary.py', 'source/reference.py',
    'source/evidence.py', 'source/leased_call.py',
}

def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def encode(value):
    from fractions import Fraction
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {k: encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(v) for v in value]
    return value

def check_input_blob(raw, expected_bytes, expected_sha):
    if len(raw) != expected_bytes or sha(raw) != expected_sha:
        raise ValueError('ACTUAL_SOURCE_IDENTITY_MISMATCH')

def identity():
    raw = (UNIT/'CONTRACT.json').read_bytes()
    if sha(raw) != CONTRACT_SHA:
        raise ValueError('FROZEN_CONTRACT_MISMATCH')
    contract = json.loads(raw)
    files = json.loads((UNIT/'implementation/FROZEN_FILES.json').read_text())['files']
    if set(files) != FROZEN_PATHS:
        raise ValueError('EXACT_FROZEN_EIGHT_FILES_REQUIRED')
    for name, digest in files.items():
        if sha((UNIT/name).read_bytes()) != digest:
            raise ValueError('FROZEN_FILE_MISMATCH:'+name)
    for item in contract['inputs']:
        check_input_blob((REPO/item['path']).read_bytes(), item['bytes'], item['sha256'])
    binding = {'unit_id': contract['unit_id'], 'parent_head': contract['baseline']['head'],
               'contract_sha256': CONTRACT_SHA, 'code_files': files, 'inputs': contract['inputs']}
    return {'sha256': sha(canonical(binding)), 'binding': binding}

def fresh(output):
    output = Path(output)
    if output.exists():
        raise FileExistsError('CREATE_ONLY_OUTPUT_ALREADY_EXISTS')
    output.mkdir(parents=True)
    return output

def write_json(output, name, value):
    if Path(name).name != name:
        raise ValueError('FLAT_OUTPUT_NAME_REQUIRED')
    raw = canonical(encode(value))
    with (output/name).open('xb') as stream:
        stream.write(raw)
    return {'path': name, 'bytes': len(raw), 'sha256': sha(raw)}

def publish(output, kind, binding, payloads):
    for name, value in payloads.items():
        if Path(name).name != name:
            raise ValueError('FLAT_OUTPUT_NAME_REQUIRED')
        raw = value if isinstance(value, bytes) else canonical(encode(value))
        with (output/name).open('xb') as stream:
            stream.write(raw)
    # Checkpoint files already written create-only are included as raw evidence.
    names = sorted(p.name for p in output.iterdir() if p.is_file())
    if 'MANIFEST.json' in names:
        raise FileExistsError('CREATE_ONLY_MANIFEST_ALREADY_EXISTS')
    hashes = {name: sha((output/name).read_bytes()) for name in names}
    write_json(output, 'MANIFEST.json', {
        'status': 'COMPLETE', 'kind': kind, 'identity': binding, 'payload_sha256': hashes,
        'raw_F_eigh': 0, 'old_science_callbacks': 0, 'old_pair_rescan': 0,
        'ENDF_decode': 0, 'ODE': 0, 'integrals': 0, 'benchmark': 0,
        'actual_matrix_repair': False, 'HH_R10': 'OFF', 'production': 'NOT_ISSUED',
    })

def resume(output, kind, expected):
    output = Path(output)
    raw = (output/'MANIFEST.json').read_bytes()
    manifest = json.loads(raw)
    if manifest['status'] != 'COMPLETE' or manifest['kind'] != kind or manifest['identity'] != expected:
        raise ValueError('RESUME_IDENTITY_OR_STATUS_MISMATCH')
    for name, digest in manifest['payload_sha256'].items():
        if Path(name).name != name or sha((output/name).read_bytes()) != digest:
            raise ValueError('RESUME_PAYLOAD_MISMATCH:'+name)
    return {'status': 'SKIP_COMPLETE_READ_ONLY', 'kind': kind,
            'scientific_imports': 0, 'scientific_callbacks': 0, 'writes': 0,
            'identity': expected['sha256'], 'manifest_sha256': sha(raw)}

def main_args(kind):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--resume', action='store_true')
    if kind == 'reference':
        parser.add_argument('--primary-output', type=Path, required=True)
    return parser.parse_args()

