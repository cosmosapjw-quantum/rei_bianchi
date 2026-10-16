"""Reproduce PR159 archived NCP endpoint and trace subset, byte-identically.
No native REI executable; reconstruct only immutable evidence from two tar layers.
"""
from pathlib import Path
import base64, hashlib, io, json, tarfile
import sys

EXPECTED_ARCHIVE='bf8aaffdae624a6de25d6f8e58fb8c7b3c166f331954d9b841907ab1bc061e4c'
OUTPUT=Path(__file__).parent/'evidence'/'raw'

def digest(b:bytes):return hashlib.sha256(b).hexdigest()

def recover(archive:Path, output:Path=OUTPUT):
    root_bytes=archive.read_bytes()
    assert digest(root_bytes)==EXPECTED_ARCHIVE, 'original cloud restoration identity'
    with tarfile.open(fileobj=io.BytesIO(root_bytes)) as outer:
        child_bytes=outer.extractfile('ncp_evidence/evidence-release.tar.gz').read()
    blobs=[]
    raw_blobs={}
    with tarfile.open(fileobj=io.BytesIO(child_bytes)) as t:
        entries=t.getnames()
        candidates=[n for n in entries if n.startswith('release_') and n.endswith('/result.json')]
        assert len(candidates)==22, f'Expected 22 executed cases, got {len(candidates)}'
        for name in sorted(candidates):
            parts=name.split('/')
            for basename in ('result.json','step_trace.csv'):
                src=f'{parts[0]}/{basename}'
                data=t.extractfile(src).read()
                out=output/src
                out.parent.mkdir(parents=True,exist_ok=True)
                out.write_bytes(data)
                blobs.append({'path':src,'sha256':digest(data),'size_bytes':len(data)})
                raw_blobs[src]=base64.b64encode(data).decode('ascii')
    receipt={'schema':'rei.bass.pr159.raw_readback.v1','original_archive_sha256':EXPECTED_ARCHIVE,
             'nested_evidence_tar_sha256':digest(child_bytes),'files':blobs,'case_count':22,
             'source':'PR159 verified original restore archive, not new NCP execution'}
    (output/'RAW_IDENTITY.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    (output.parent/'RAW_SNAPSHOT.json').write_text(json.dumps({'receipt':receipt,'base64_files':raw_blobs},sort_keys=True,separators=(',',':'))+'\n')
    return receipt

if __name__=='__main__':
    path=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/mnt/data/pr159_recovered/recovery-1f8619c2.tar.gz')
    rec=recover(path)
    print(json.dumps({'original':rec['original_archive_sha256'],'nested':rec['nested_evidence_tar_sha256'],
                      'files':len(rec['files']),'cases':rec['case_count']}))
