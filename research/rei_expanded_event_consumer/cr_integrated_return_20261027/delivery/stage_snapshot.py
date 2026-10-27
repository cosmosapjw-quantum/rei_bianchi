"""Pack one explicit checkpoint; no scientific imports or recursive discovery.

Archive and its adjacent packing receipt must be outside this owned unit.
One postcreation CRC verification is performed and recorded for reuse.
"""
import time
CPU_START=time.process_time()
WALL_START=time.perf_counter()
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile

UNIT=Path(__file__).resolve().parent.parent


def inside(path,parent):
    try: path.relative_to(parent); return True
    except ValueError: return False


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',required=True)
    parser.add_argument('--commit',required=True)
    parser.add_argument('--paths-json',required=True,help='explicit repo-relative list JSON; - reads stdin')
    parser.add_argument('--archive',required=True)
    parser.add_argument('--root',required=True)
    args=parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*',args.stage): raise ValueError('explicit stage identity required')
    if not re.fullmatch(r'[0-9a-f]{40}',args.commit): raise ValueError('full commit SHA required')
    root=Path(args.root).resolve(); archive=Path(args.archive).resolve()
    if inside(archive,UNIT): raise ValueError('checkpoint archive must be outside owned unit')
    receipt=archive.with_name(archive.name+'.packing_receipt.json')
    if archive.exists() or receipt.exists(): raise FileExistsError('preserve existing archive and receipt')
    config=json.loads(sys.stdin.read() if args.paths_json=='-' else Path(args.paths_json).read_text())
    paths=config['paths'] if isinstance(config,dict) else config
    if not isinstance(paths,list) or not paths: raise ValueError('nonempty explicit paths list required')
    members=[]; names=set()
    for raw in paths:
        if not isinstance(raw,str): raise ValueError('path must be string')
        rel=PurePosixPath(raw)
        if rel.is_absolute() or '..' in rel.parts or str(rel)!=raw or raw in ('','.'):
            raise ValueError('repo-relative file path required: '+raw)
        if raw=='ARCHIVE_AUTHORITY.json' or raw in names: raise ValueError('duplicate or reserved archive path: '+raw)
        path=root/raw
        if not path.is_file(): raise ValueError('explicit file missing: '+raw)
        if path.resolve() in (archive,receipt): raise ValueError('archive/receipt cannot include itself')
        names.add(raw); members.append((raw,path,path.stat().st_size))
    authority={'schema':'REI_EXPLICIT_STAGE_SNAPSHOT_V1','stage':args.stage,'commit':args.commit,
        'payload_files':len(members),'archive_entries':len(members)+1,
        'payload_bytes':sum(size for _,_,size in members),
        'paths':[raw for raw,_,_ in members],
        'scope':'explicit file snapshot; scientific admission is owned by root',
        'recursive_discovery':False}
    archive.parent.mkdir(parents=True,exist_ok=True)
    status='STARTED'; failure=None; crc_passes=0; archive_sha=None; archive_bytes=None
    try:
        with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for raw,path,_ in members: z.write(path,arcname=raw)
            z.writestr('ARCHIVE_AUTHORITY.json',json.dumps(authority,indent=2)+'\n')
        # Exactly one postcreation CRC verification pass; consumers reuse receipt.
        with zipfile.ZipFile(archive,'r') as z:
            bad=z.testzip(); crc_passes=1
            if bad is not None: raise ValueError('CRC failure: '+bad)
            if len(z.infolist())!=len(members)+1: raise ValueError('entry count mismatch')
        digest=hashlib.sha256()
        with archive.open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''): digest.update(chunk)
        archive_sha=digest.hexdigest(); archive_bytes=archive.stat().st_size
        status='PACKED_CRC_VERIFIED'
    except BaseException as exc:
        failure={'type':type(exc).__name__,'message':str(exc)}
    record={'status':status,'stage':args.stage,'commit':args.commit,
        'archive':str(archive),'sha256':archive_sha,'archive_bytes':archive_bytes,
        'payload_files':len(members),'archive_entries':len(members)+1,
        'payload_bytes':authority['payload_bytes'],'CRC_verification_passes':crc_passes,
        'failure':failure,'CPU_s_before_receipt_tail':time.process_time(),
        'CPU_s_since_module_entry':time.process_time()-CPU_START,
        'wall_s_since_module_entry':time.perf_counter()-WALL_START,
        'budget_owner':'PRESENTATION','scientific_execution':False,
        'unknown_remote_tool_LLM_cost':'UNKNOWN_NOT_ZERO',
        'verification_reuse':'reuse this one CRC result; do not run another CRC pass'}
    # This sibling receipt is excluded automatically from future owned-unit paths.
    with receipt.open('x') as f: f.write(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2),flush=True)
    return 0 if status=='PACKED_CRC_VERIFIED' else 1

if __name__=='__main__': raise SystemExit(main())
