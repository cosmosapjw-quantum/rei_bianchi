"""Prepared public build-evidence packager. Execute only after root publishes build content SHA."""
import argparse,hashlib,io,json,re,subprocess,time,zipfile
from pathlib import Path,PurePosixPath
ROOT='research/bass_source012_source_age_reference_20261016/preparation_002_build/'
CANON={f'research/flrw_covariant_transport_20261015/{n}.json' for n in ('LATEST_RESUME','HANDOFF','NEXT_DAG')}
CAP=4*1024*1024

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--content-commit',required=True);parser.add_argument('--archive-path',required=True)
    args=parser.parse_args();start=time.monotonic();deadline=start+30
    if not re.fullmatch('[0-9a-f]{40}',args.content_commit):raise ValueError('exact full content SHA required')
    def show(path):
        remain=deadline-time.monotonic()
        if remain<=0:raise TimeoutError('30s packaging bound')
        return subprocess.check_output(['git','-c','core.packedGitWindowSize=32m','-c','core.packedGitLimit=64m','show',args.content_commit+':'+path],timeout=remain)
    selection_path=ROOT+'PUBLIC_SELECTION.json';selection_raw=show(selection_path);selection=json.loads(selection_raw)
    members={selection_path:(selection_raw,None)}
    for item in selection['files']:
        path=item['path'];parts=PurePosixPath(path).parts
        if path.startswith('/') or '..' in parts or path in members or not(path.startswith(ROOT) or path in CANON):raise ValueError('selection path outside owned public scope')
        if any(part in ('target','cache','__pycache__','native_raw','private') for part in parts):raise ValueError('excluded payload')
        data=show(path)
        if len(data)!=item['bytes']:raise ValueError('committed member size mismatch')
        members[path]=(data,item['sha256'])
    manifest={'content_commit':args.content_commit,'selection_path':selection_path,'scope':'public build-preparation evidence and current canonical metadata only; private restore/target/ELF excluded','private_members':0,'old_archive_or_ELF_read':False,'members':[{'path':name,'bytes':len(data),'expected_sha256':expected} for name,(data,expected) in members.items()]}
    members['ARCHIVE_MANIFEST.json']=((json.dumps(manifest,indent=2)+'\n').encode(),None)
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for name,(data,expected) in members.items():
            if time.monotonic()>=deadline:raise TimeoutError('30s packaging bound')
            archive.writestr(name,data)
    if len(buffer.getbuffer())>CAP:raise ValueError('4MiB archive cap')
    archive_path=Path(args.archive_path);archive_path.parent.mkdir(parents=True,exist_ok=True)
    with archive_path.open('xb') as stream:stream.write(buffer.getbuffer())
    verified=[]
    with zipfile.ZipFile(archive_path) as archive:
        if set(archive.namelist())!=set(members):raise ValueError('member set mismatch')
        for name,(original,expected) in members.items():
            if time.monotonic()>=deadline:raise TimeoutError('30s packaging bound')
            decoded=archive.read(name) # checks member CRC once
            digest=hashlib.sha256(decoded).hexdigest() # each member SHA once
            if expected is not None and digest!=expected:raise ValueError('committed selection SHA mismatch: '+name)
            if expected is None and decoded!=original:raise ValueError('selection/internal manifest mismatch')
            verified.append({'path':name,'bytes':len(decoded),'sha256':digest})
    digest=hashlib.sha256(archive_path.read_bytes()).hexdigest()
    print(json.dumps({'status':'PUBLIC_PREPARATION_ARCHIVE_VERIFIED','content_commit':args.content_commit,'archive_path':str(archive_path),'archive_bytes':archive_path.stat().st_size,'archive_sha256':digest,'archive_cap_bytes':CAP,'members':len(verified),'private_members':0,'per_member_SHA_and_CRC':'PASS_ONCE','wall_seconds':time.monotonic()-start,'old_archives_rehashed':False,'old_private_or_ELF_included':False,'upload':False,'git_mutation':False,'member_manifest':verified},indent=2))
if __name__=='__main__':main()
