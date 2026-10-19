#!/usr/bin/env python3
"""Create a deterministic, hashed recovery archive without mutating inputs."""
import argparse, hashlib, json, stat, zipfile
from pathlib import Path

def sha(b): return hashlib.sha256(b).hexdigest()
def main():
    a=argparse.ArgumentParser();a.add_argument('--root',type=Path,required=True);a.add_argument('--output',type=Path,required=True);a.add_argument('--original-run13',type=Path);a.add_argument('--git-head',required=True);a.add_argument('--only',action='append',default=[]);o=a.parse_args()
    root=o.root.resolve(); payload=[]
    for p in sorted(root.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(root)
        if any(x in ('toolchain','target','__pycache__','.git') for x in rel.parts):continue
        if p.suffix in ('.pyc','.xz') or p.name.startswith('SALVAGE_PUBLICATION_'):continue
        if o.only and rel.parts[0] not in o.only and rel.as_posix()!='INCIDENT_AND_RESULTS_20261019.json':continue
        if p.is_symlink():raise ValueError('symlink not admitted: '+str(rel))
        payload.append(('run15/'+rel.as_posix(),p.read_bytes()))
    if o.original_run13:
        b=o.original_run13.read_bytes()
        assert len(b)==41075268 and sha(b)=='6912c7f90dedaaee312d3fdc3248e4e8839409c0fb2944262de945e1b2f34e96'
        payload.append(('original/REI_ATOMIC_NUCLEAR_RUN13_M2_CONVERGENCE_20261018.zip',b))
    meta={'schema':'rei.run15.recovery_archive.v1','git_checkpoint':o.git_head,'original_RUN15_four_case_raw_states_included':False,'scope':'Read per-file evidence admission; partial source and transcript records are not recovered raw IVP states.','files':[{'path':n,'bytes':len(b),'sha256':sha(b)} for n,b in payload]}
    manifest=(json.dumps(meta,ensure_ascii=False,indent=2)+'\n').encode()
    payload.append(('MANIFEST.json',manifest))
    names=[n for n,b in payload]
    assert len(names)==len(set(names))
    with zipfile.ZipFile(o.output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,b in payload:
            zi=zipfile.ZipInfo(name,(2026,10,19,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=(stat.S_IFREG|0o644)<<16;z.writestr(zi,b)
    with zipfile.ZipFile(o.output) as z:
        assert z.testzip() is None
        for f in meta['files']:
            b=z.read(f['path']); assert len(b)==f['bytes'] and sha(b)==f['sha256']
    receipt={'archive':str(o.output.resolve()),'bytes':o.output.stat().st_size,'sha256':sha(o.output.read_bytes()),'manifest_sha256':sha(manifest),'payload_file_count':len(meta['files']),'CRC_and_all_manifest_files':'PASS','git_checkpoint':o.git_head,'original_RUN15_four_case_raw_states_included':False}
    o.output.with_suffix('.manifest.json').write_bytes(manifest)
    o.output.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))
if __name__=='__main__':main()
