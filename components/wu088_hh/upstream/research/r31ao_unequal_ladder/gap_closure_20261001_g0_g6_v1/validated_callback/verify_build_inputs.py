"""Pre-build identity gate; does not establish upstream source-to-binary equality."""
import hashlib,json,sys
from pathlib import Path

PINS={
    'flint':('3.4.0','108ab51a4dd33918ff3308f0c63a63616ae30a2c174d50c9188676e85011346f'),
    'gmp':('6.3.0','a3c2b80201b89e68616f4ad30bc66aee4927c3ce50e33929ca819d5c43538898'),
    'mpfr':('4.2.2','b67ba0383ef7e8a8563734e2e889ef5ec3c3b898a01d00fa0a6869ad81c6ce01'),
}

def verify(path):
    record=json.loads(Path(path).read_text())
    if record.get('verified_build_provenance') is not True:
        raise ValueError('backend build provenance not verified')
    for name,(version,sha) in PINS.items():
        item=record['libraries'][name]
        if item['version']!=version or item['source_archive_sha256']!=sha:
            raise ValueError(name+' pin mismatch')
        for role in ('source_archive','binary'):
            p=Path(item[role+'_path'])
            if not p.is_absolute() or not p.is_file():
                raise ValueError(name+' '+role+' must be an existing absolute file')
            digest=hashlib.sha256(p.read_bytes()).hexdigest()
            if digest!=item[role+'_sha256']:
                raise ValueError(name+' '+role+' byte mismatch')
        if not item.get('build_log_sha256') or not item.get('compiler') or not item.get('flags') or not item.get('abi'):
            raise ValueError(name+' incomplete compiler/flags/ABI/build-log binding')
    return record

if __name__=='__main__':
    verify(sys.argv[1])
    print('LOCAL_BACKEND_INPUT_IDENTITIES_MATCH; source-to-binary claim inherits supplied build authority')
