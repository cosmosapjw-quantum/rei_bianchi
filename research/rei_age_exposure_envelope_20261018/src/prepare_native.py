"""Restore a frozen native owner into a task-owned copy and append accessors.

Accept an exact archived donor, or read immutable Git objects from --repo.
--fetch-missing permits public raw GitHub retrieval, always checked against the
153-file frozen SHA256 manifest. No existing owner worktree is modified.
"""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, subprocess, urllib.request, zipfile
from build_refined_sources import overlay, write_checked
from run_refinement import sha, read_json


def safe_relative(name: str) -> str:
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name: raise ValueError('UNSAFE_PATH')
    return name

def prepare(root: Path, dest: Path, archive: Path|None=None, repo: Path|None=None,
            fetch_missing: bool=False) -> dict:
    manifest=read_json(root/'contracts/NATIVE_INPUTS.json')
    for name, entry in read_json(root/'contracts/DONOR_IDENTITY.json').items():
        if sha(root/'donors/pr171'/name)!=entry['sha256']: raise ValueError('DONOR_FILE_SHA_MISMATCH: '+name)
    if archive is not None and sha(archive)!=manifest['archive_sha256']:
        raise ValueError('ARCHIVE_SHA_MISMATCH')
    completed=dest/'PREPARED_IDENTITY.json'
    if completed.exists():
        prior=read_json(completed)
        if prior['native_sha']!=manifest['native_sha']:
            raise ValueError('EXISTING_NATIVE_SHA_CONFLICT')
        for n,h in prior['outputs'].items():
            if not (dest/n).is_file() or sha(dest/n)!=h:
                raise ValueError('EXISTING_PREPARED_FILE_CONFLICT: '+n)
        # Verify the desired overlay matches today's source before accepting reuse.
        native,solver=overlay((root/'donors/pr171/positive_native.rs').read_bytes(),
                              (root/'donors/pr171/positive_solver.py').read_bytes())
        if (dest/'rust/rei_microphysics/examples/positive_native.rs').read_text()!=native or (dest/'positive_solver_refined.py').read_text()!=solver:
            raise ValueError('EXISTING_OVERLAY_VERSION_CONFLICT')
        return prior
    if dest.exists() and any(dest.iterdir()):
        raise FileExistsError('DESTINATION_NOT_EMPTY; select a new task scratch')
    contents={}
    donor=zipfile.ZipFile(archive) if archive is not None else None
    try:
        if donor is not None and donor.testzip() is not None: raise ValueError('ARCHIVE_CRC')
        for name,entry in manifest['files'].items():
            safe_relative(name);data=None
            if donor is not None: data=donor.read('native_source/'+name)
            elif repo is not None:
                result=subprocess.run(['git','-C',str(repo),'show',manifest['native_sha']+':'+name],capture_output=True,timeout=30)
                if result.returncode==0:data=result.stdout
            if data is None and fetch_missing:
                url='https://raw.githubusercontent.com/cosmosapjw-quantum/rei_bianchi/'+manifest['native_sha']+'/'+name
                with urllib.request.urlopen(url,timeout=30) as response: data=response.read(8*1024*1024)
            if data is None: raise FileNotFoundError('FROZEN_GIT_INPUT_MISSING: '+name)
            if hashlib.sha256(data).hexdigest()!=entry['sha256']: raise ValueError('FROZEN_INPUT_SHA_MISMATCH: '+name)
            contents[name]=data
    finally:
        if donor is not None: donor.close()
    d=root/'donors/pr171'
    native,solver=overlay((d/'positive_native.rs').read_bytes(),(d/'positive_solver.py').read_bytes())
    owner=d/'matrix_owner.rs'
    if sha(owner)!='02a776b67369926c4095a87b46fcf2087d91c7aaef010e29ec55676835e85104':
        raise ValueError('MATRIX_OWNER_SHA_MISMATCH')
    p='rust/rei_microphysics/src/axbi_covariant_transport.rs'
    original=contents[p]
    suffix=(d/'prepared_node_accessor.rs').read_bytes()+(d/'positive_accessor.rs').read_bytes()
    contents[p]=original+suffix
    contents['rust/rei_microphysics/examples/positive_native.rs']=native.encode()
    contents['rust/rei_microphysics/examples/matrix_owner.rs']=owner.read_bytes()
    contents['positive_solver_refined.py']=solver.encode()
    for n,data in contents.items(): write_checked(dest/n,data)
    record={'schema':'rei.age_refinement.prepared.v1','native_sha':manifest['native_sha'],
            'original_input_count':len(manifest['files']),'native_compile':'NOT_RUN_BY_PREPARER',
            'accessor_original_prefix_sha256':hashlib.sha256(original).hexdigest(),
            'accessor_suffix_sha256':hashlib.sha256(suffix).hexdigest(),
            'outputs':{n:hashlib.sha256(data).hexdigest() for n,data in sorted(contents.items())}}
    write_checked(completed,(json.dumps(record,indent=2,sort_keys=True)+'\n').encode())
    return record

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dest',type=Path,required=True);p.add_argument('--archive',type=Path)
    p.add_argument('--repo',type=Path);p.add_argument('--fetch-missing',action='store_true')
    a=p.parse_args()
    out=prepare(Path(__file__).resolve().parents[1],a.dest.resolve(),a.archive,a.repo,a.fetch_missing)
    print(json.dumps({'status':'PREPARED_NOT_COMPILED','native_sha':out['native_sha'],'files':len(out['outputs'])}))
if __name__=='__main__':main()
