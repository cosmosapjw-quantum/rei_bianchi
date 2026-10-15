from pathlib import Path
import hashlib,json,os,sys
root=Path('/root/REI_AXBI_GOAL_20261014_32d11e733155/performance/temperature_rate_table_001/ncp_validation_001')
counts={}
for name,base in [('source',root/'stage'),('toolchain',root/'toolchain')]:
    manifest=json.loads((root/'raw'/f'{name}_manifest.json').read_text())
    actual={str(p.relative_to(base)) for p in base.rglob('*') if p.is_file() or p.is_symlink()}
    missing=set(manifest)-actual
    extra=actual-set(manifest)
    if missing or extra:
        print(name,'SET_MISMATCH',len(missing),len(extra),sorted(missing)[:3],sorted(extra)[:3]);sys.exit(2)
    total=0
    for rel,expected in manifest.items():
        p=base/rel
        if isinstance(expected,str):
            got=hashlib.sha256(p.read_bytes()).hexdigest()
            if got!=expected:print(name,'HASH_MISMATCH',rel,got,expected);sys.exit(2)
            total+=p.stat().st_size
        elif 'sha256' in expected:
            got=hashlib.sha256(p.read_bytes()).hexdigest()
            if got!=expected['sha256']:print(name,'HASH_MISMATCH',rel,got,expected);sys.exit(2)
            total+=p.stat().st_size
        else:
            got=os.readlink(p)
            if got!=expected['link']:print(name,'LINK_MISMATCH',rel,got,expected);sys.exit(2)
    counts[name]={'files':len(manifest),'bytes':total}
print(json.dumps(counts,sort_keys=True))
