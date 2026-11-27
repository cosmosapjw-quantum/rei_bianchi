#!/usr/bin/env python3
"""Source-locked, fail-closed restore of one BASS_HE NCP start bundle.

No credentials, network requests, or rewriting of canonical archives.
"""
from __future__ import annotations
import argparse, hashlib, io, json, os, pathlib, shutil, sys, tempfile, zipfile

EXPECTED_FILES = (
    'NCP_LOCAL_CODEX_BASS_HE_HEAVY_HANDOFF_20261008_KO.md',
    'NCP_LOCAL_CODEX_BASS_HE_HEAVY_DAG_20261008.json',
    'INPUTS.json',
    'START_HERE_KO.md',
    'ncp_intake.py',
    'packages/BASS_HE_RCT03E6_ALL_EPOCH_20261008_v1.zip',
    'packages/BASS_HE_RCT03E7_CONSUMER_ADOPTION_20261008_v1.zip',
    'packages/BASS_HE_RCT03E8_PHOTO_SOURCE_20261008_v1.zip',
)
INNER_NAMES = tuple(x for x in EXPECTED_FILES if x.startswith('packages/'))

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def canonical_name(name):
    pp=pathlib.PurePosixPath(name)
    if not name or name.startswith('/') or '\\' in name or '..' in pp.parts or any(not p for p in pp.parts):
        raise ValueError('UNSAFE_ZIP_NAME:'+name)
    return name

def check_zip(blob, expected_payload=None):
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        names=[i.filename for i in z.infolist() if not i.is_dir()]
        if len(set(names))!=len(names):raise ValueError('DUPLICATE_ZIP_ENTRY')
        if any((i.external_attr >> 16) & 0o170000 == 0o120000 for i in z.infolist()):
            raise ValueError('SYMLINK_ZIP_ENTRY')
        for n in names:canonical_name(n)
        if 'MANIFEST.json' not in names:raise ValueError('MANIFEST_MISSING')
        manifest=json.loads(z.read('MANIFEST.json'))
        d=manifest.get('files',manifest.get('payloads'))
        if not isinstance(d,dict):raise ValueError('INVALID_PAYLOAD_MANIFEST')
        if set(d) != set(names)-{'MANIFEST.json'}:raise ValueError('PAYLOAD_SET_MISMATCH')
        if expected_payload is not None and set(d)!=set(expected_payload):raise ValueError('BUNDLE_SET_MISMATCH')
        for n,entry in d.items():
            with z.open(n) as f:
                h=hashlib.sha256();size=0
                while chunk:=f.read(1024*1024):h.update(chunk);size+=len(chunk)
            if size!=entry['bytes'] or h.hexdigest()!=entry['sha256']:
                raise ValueError('PAYLOAD_HASH_MISMATCH:'+n)
        return z,manifest,names

def validate(blob):
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        names=[i.filename for i in z.infolist() if not i.is_dir()]
        if len(names)!=len(set(names)):raise ValueError('DUPLICATE_ENTRY')
        for n in names:canonical_name(n)
        if set(names)!=set(EXPECTED_FILES)|{'MANIFEST.json'}:
            raise ValueError('OUTER_CONTENT_MISMATCH')
        man=json.loads(z.read('MANIFEST.json'))
        if man.get('schema')!='bass-he.ncp-start-bundle.v1':raise ValueError('WRONG_SCHEMA')
        if set(man['files'])!=set(EXPECTED_FILES):raise ValueError('MANIFEST_NAMES_MISMATCH')
        for n,meta in man['files'].items():
            # streaming verifies CRC and actual digest
            h=hashlib.sha256();total=0
            with z.open(n) as f:
                while block:=f.read(1024*1024):h.update(block);total+=len(block)
            if total!=meta['bytes'] or h.hexdigest()!=meta['sha256']:
                raise ValueError('OUTER_SHA256_FAIL:'+n)
            if n in INNER_NAMES:
                b=z.read(n)
                with zipfile.ZipFile(io.BytesIO(b)) as inner:
                    inner_names=[i.filename for i in inner.infolist() if not i.is_dir()]
                    for a in inner_names:canonical_name(a)
                    if len(inner_names)!=len(set(inner_names)):raise ValueError('INNER_DUPLICATE')
                    mm=json.loads(inner.read('MANIFEST.json'))
                    items=mm.get('files',mm.get('payloads'))
                    if set(items)!=set(inner_names)-{'MANIFEST.json'}:
                        raise ValueError('INNER_SET_MISMATCH:'+n)
                    for iname,record in items.items():
                        d=inner.read(iname)
                        if len(d)!=record['bytes'] or sha256(d)!=record['sha256']:
                            raise ValueError('INNER_HASH_FAIL:'+n+':'+iname)
    return man

def run():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--bundle',type=pathlib.Path,required=True)
    ap.add_argument('--output',type=pathlib.Path)
    ap.add_argument('--verify-only',action='store_true')
    ap.add_argument('--expected-sha256',help='Optional full ZIP SHA256 from Git INPUTS.json')
    args=ap.parse_args()
    if not args.bundle.is_file():ap.error('input bundle file missing')
    blob=args.bundle.read_bytes()
    actual=sha256(blob)
    if args.expected_sha256 and actual!=args.expected_sha256:
        raise ValueError('BUNDLE_SHA256_MISMATCH '+actual)
    man=validate(blob)
    summary={'gate':'PAYLOAD_AND_NESTED_MANIFEST_VERIFIED','archive_sha256':actual,'bytes':len(blob),
             'files':len(man['files']),'nested_packages':list(INNER_NAMES)}
    if args.verify_only:
        print(json.dumps(summary,ensure_ascii=False,sort_keys=True));return
    if args.output is None:ap.error('--output required unless --verify-only')
    target=args.output.absolute()
    if target.exists():raise FileExistsError('OUTPUT_NOT_EMPTY_OR_ALREADY_EXISTS:'+str(target))
    target.parent.mkdir(parents=True,exist_ok=True)
    stage=pathlib.Path(tempfile.mkdtemp(prefix='.ncp-intake-',dir=str(target.parent)))
    try:
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            for name in EXPECTED_FILES:
                path=stage.joinpath(*pathlib.PurePosixPath(name).parts)
                path.parent.mkdir(parents=True,exist_ok=True)
                with z.open(name) as src,open(path,'xb') as dest:
                    shutil.copyfileobj(src,dest,1024*1024)
                    dest.flush();os.fsync(dest.fileno())
        # Restore each verified source ZIP to its own isolated namespace.
        for source in INNER_NAMES:
            basename=pathlib.PurePosixPath(source).name.removesuffix('.zip')
            source_dir=stage/'sources'/basename
            source_dir.mkdir(parents=True,exist_ok=False)
            with zipfile.ZipFile(stage/source) as inner:
                for entry in inner.infolist():
                    if entry.is_dir():continue
                    canonical_name(entry.filename)
                    output=source_dir.joinpath(*pathlib.PurePosixPath(entry.filename).parts)
                    output.parent.mkdir(parents=True,exist_ok=True)
                    with inner.open(entry) as src,open(output,'xb') as dst:
                        shutil.copyfileobj(src,dst,1024*1024)
                        dst.flush();os.fsync(dst.fileno())
        (stage/'RESTORE_VERIFICATION.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        os.rename(stage,target)
    except BaseException:
        shutil.rmtree(stage,ignore_errors=True)
        raise
    print(json.dumps({'restored_to':str(target),**summary},ensure_ascii=False,sort_keys=True))

if __name__=='__main__':
    try:run()
    except Exception as exc:
        print('NCP_INTAKE_FAILURE '+str(exc),file=sys.stderr)
        sys.exit(2)
