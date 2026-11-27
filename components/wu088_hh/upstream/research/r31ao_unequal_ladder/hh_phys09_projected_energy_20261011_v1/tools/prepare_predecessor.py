"""Verify and extract the preserved PHYS08 archive without executing its code."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = 'WU088_HH_PHYS08_WEIGHTED_SOURCE_NCP_HANDOFF_20261011_v1_sha_84ec6694a01e.zip'
SHA = '84ec6694a01ec711eb2f55542f718bb1f091a5547ab4ce809503089bd18c2b9b'
PREFIX = 'HH_PHYS08_20261011_v1'
MANIFEST_SHA = '4631c91add9a8e226ef781967cc131d38df1bb3dd583d4d00e504cc1d6bef0dd'


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--dest',type=Path,required=True)
    args=parser.parse_args()
    if not args.dest.is_absolute() or args.dest.exists():
        raise ValueError('absolute create-only destination required')
    archive=ROOT/'predecessor'/NAME
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=SHA:
        raise ValueError('predecessor archive SHA mismatch')
    with zipfile.ZipFile(archive)as z:
        names=z.namelist()
        if len(names)!=len(set(names)) or len(names)!=133:
            raise ValueError('predecessor layout')
        for info in z.infolist():
            p=PurePosixPath(info.filename)
            if p.is_absolute() or '..' in p.parts or not p.parts or p.parts[0]!=PREFIX or info.is_dir() or ((info.external_attr>>16)&0o170000)==0o120000:
                raise ValueError('unsafe predecessor archive member')
        mb=z.read(PREFIX+'/MANIFEST.json')
        if hashlib.sha256(mb).hexdigest()!=MANIFEST_SHA:
            raise ValueError('predecessor manifest mismatch')
        m=json.loads(mb)
        expected={PREFIX+'/'+r['path']for r in m['files']}|{PREFIX+'/MANIFEST.json',PREFIX+'/SHA256SUMS'}
        if set(names)!=expected:
            raise ValueError('predecessor members differ from manifest')
        for row in m['files']:
            b=z.read(PREFIX+'/'+row['path'])
            if len(b)!=row['bytes'] or hashlib.sha256(b).hexdigest()!=row['sha256']:
                raise ValueError('predecessor payload mismatch: '+row['path'])
        args.dest.mkdir(parents=True,exist_ok=False)
        for info in z.infolist():
            p=args.dest/info.filename
            p.parent.mkdir(parents=True,exist_ok=True)
            with p.open('xb')as f:f.write(z.read(info.filename))
    print(json.dumps({'status':'PREDECESSOR_BYTES_VERIFIED_EXTRACTED','package':str(args.dest/PREFIX),
        'archive_sha256':SHA,'manifest_sha256':MANIFEST_SHA,'payloads':len(m['files']),
        'scientific_executions':0,'native_calls':0},indent=2))


if __name__=='__main__':main()
