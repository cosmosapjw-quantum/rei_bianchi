"""PHYS90 metadata-only identity, read-only resume, create-only output helpers."""
from pathlib import Path
import hashlib
import json
UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
CONTRACT_SHA = '45d7b94544cf801619aa723c79be35c05e3ca2b023e2e94e8985f4c20758a20c'

def canonical(obj):
    return (json.dumps(obj, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def encode(obj):
    from fractions import Fraction
    if isinstance(obj, Fraction): return str(obj)
    if isinstance(obj, dict): return {k: encode(v) for k,v in obj.items()}
    if isinstance(obj, (list,tuple)): return [encode(v) for v in obj]
    return obj

def check_input_blob(data, expected_bytes, expected_sha):
    if len(data)!=expected_bytes or sha(data)!=expected_sha:
        raise ValueError('ACTUAL_SOURCE_IDENTITY_MISMATCH')

def identity():
    raw = (UNIT/'CONTRACT.json').read_bytes()
    if sha(raw) != CONTRACT_SHA: raise ValueError('FROZEN_CONTRACT_MISMATCH')
    contract = json.loads(raw)
    files = json.loads((UNIT/'implementation/FROZEN_FILES.json').read_text())['files']
    required = {'CONTRACT.json','theory/COVARIANCE_CELL_AND_CONSUMER_KO.md',
                'source/kernel.py','source/primary.py','source/reference.py','source/evidence.py','source/leased_call.py'}
    if not required <= set(files): raise ValueError('INCOMPLETE_FROZEN_FILES')
    for name,digest in files.items():
        if sha((UNIT/name).read_bytes()) != digest: raise ValueError('FROZEN_FILE_MISMATCH:'+name)
    for item in contract['inputs']:
        data = (REPO/item['path']).read_bytes()
        check_input_blob(data,item['bytes'],item['sha256'])
    binding = {'unit_id':contract['unit_id'],'parent_head':contract['baseline']['head'],
               'contract_sha256':CONTRACT_SHA,'code_files':files,'inputs':contract['inputs']}
    return {'sha256':sha(canonical(binding)), 'binding':binding}

def resume(output, kind, expected):
    output = Path(output)
    raw = (output/'MANIFEST.json').read_bytes(); manifest=json.loads(raw)
    if manifest['status']!='COMPLETE' or manifest['kind']!=kind or manifest['identity']!=expected:
        raise ValueError('RESUME_IDENTITY_OR_STATUS_MISMATCH')
    for name,digest in manifest['payload_sha256'].items():
        if Path(name).name!=name or sha((output/name).read_bytes())!=digest:
            raise ValueError('RESUME_PAYLOAD_MISMATCH:'+name)
    return {'status':'SKIP_COMPLETE_READ_ONLY','kind':kind,'scientific_imports':0,
            'scientific_callbacks':0,'writes':0,'identity':expected['sha256'],'manifest_sha256':sha(raw)}

def fresh(output):
    output=Path(output)
    if output.exists(): raise FileExistsError('CREATE_ONLY_OUTPUT_ALREADY_EXISTS')
    output.mkdir(parents=True)
    return output

def publish(output,kind,binding,payloads):
    hashes={}
    for name,obj in payloads.items():
        raw=obj if isinstance(obj,bytes) else canonical(encode(obj))
        with (output/name).open('xb') as f: f.write(raw)
        hashes[name]=sha(raw)
    with (output/'MANIFEST.json').open('xb') as f:
        f.write(canonical({'status':'COMPLETE','kind':kind,'identity':binding,'payload_sha256':hashes,
            'old_science_calls':0,'ENDF_decode':0,'eigh':0,'ODE':0,'integrals':0,'benchmark':0,
            'HH_R10':'OFF','production':'NOT_ISSUED'}))

def main_args(kind):
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--resume',action='store_true')
    if kind=='reference': p.add_argument('--primary-output',type=Path,required=True)
    return p.parse_args()
