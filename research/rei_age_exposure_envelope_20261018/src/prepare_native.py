"""Restore a frozen native owner into a task-owned copy and append accessors.

Accept an exact archived donor, or read immutable Git objects from --repo.
--native-input-dir accepts an exported frozen input directory, checked against
the same manifest; it is exclusive with --archive and --repo, not Git ancestry.
--fetch-missing permits public raw GitHub retrieval, always checked against the
153-file frozen SHA256 manifest. No existing owner worktree is modified.
"""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, subprocess, urllib.request, zipfile
from build_refined_sources import overlay, write_checked
from run_refinement import sha, read_json
from native_inputs import load_manifest
from moment_fit_diagnostic import instrument, diagnostic_identity
from subnormal_count_rounding import instrument_rounding, rounding_identity
from subnormal_moment_rounding import instrument_pair_rounding, pair_rounding_identity
from subnormal_pair_search import instrument_pair_search, search_rounding_identity


def safe_relative(name: str) -> str:
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name: raise ValueError('UNSAFE_PATH')
    return name

def prepare(root: Path, dest: Path, archive: Path|None=None, repo: Path|None=None,
            fetch_missing: bool=False, moment_diagnostics: bool=False,
            moment_rounding: str='none', native_input_dir: Path|None=None) -> dict:
    if native_input_dir is not None and (archive is not None or repo is not None):
        raise ValueError('NATIVE_INPUT_DIR_SOURCE_CONFLICT')
    if moment_rounding not in ('none','subnormal-count','subnormal-pair','subnormal-pair-search'):
        raise ValueError('MOMENT_ROUNDING_MODE')
    mode_identity=(search_rounding_identity if moment_rounding=='subnormal-pair-search' else
                   pair_rounding_identity if moment_rounding=='subnormal-pair' else rounding_identity)
    manifest=load_manifest(root,archive)
    for name, entry in read_json(root/'contracts/DONOR_IDENTITY.json').items():
        if sha(root/'donors/pr171'/name)!=entry['sha256']: raise ValueError('DONOR_FILE_SHA_MISMATCH: '+name)
    if archive is not None and sha(archive)!=manifest['archive_sha256']:
        raise ValueError('ARCHIVE_SHA_MISMATCH')
    completed=dest/'PREPARED_IDENTITY.json'
    if completed.exists():
        prior=read_json(completed)
        if prior['native_sha']!=manifest['native_sha']:
            raise ValueError('EXISTING_NATIVE_SHA_CONFLICT')
        if prior.get('moment_diagnostics',False)!=moment_diagnostics:
            raise ValueError('EXISTING_MOMENT_DIAGNOSTIC_MODE_CONFLICT')
        if moment_diagnostics and prior.get('moment_diagnostic_injection_sha256')!=diagnostic_identity():
            raise ValueError('EXISTING_MOMENT_DIAGNOSTIC_VERSION_CONFLICT')
        if prior.get('moment_rounding','none')!=moment_rounding:
            raise ValueError('EXISTING_MOMENT_ROUNDING_MODE_CONFLICT')
        if moment_rounding!='none' and prior.get('moment_rounding_injection_sha256')!=mode_identity():
            raise ValueError('EXISTING_MOMENT_ROUNDING_VERSION_CONFLICT')
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
            if native_input_dir is not None:
                source=native_input_dir/name
                if source.is_file(): data=source.read_bytes()
            elif donor is not None: data=donor.read('native_source/'+name)
            elif repo is not None:
                result=subprocess.run(['git','-C',str(repo),'show',manifest['native_sha']+':'+name],capture_output=True,timeout=30)
                if result.returncode==0:data=result.stdout
            if data is None and fetch_missing and native_input_dir is None:
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
    if moment_rounding=='subnormal-count':
        contents[p]=instrument_rounding(original,moment_diagnostics)+suffix
    elif moment_rounding=='subnormal-pair':
        contents[p]=instrument_pair_rounding(original,moment_diagnostics)+suffix
    elif moment_rounding=='subnormal-pair-search':
        contents[p]=instrument_pair_search(original,moment_diagnostics)+suffix
    else:
        contents[p]=(instrument(original) if moment_diagnostics else original)+suffix
    contents['rust/rei_microphysics/examples/positive_native.rs']=native.encode()
    contents['rust/rei_microphysics/examples/matrix_owner.rs']=owner.read_bytes()
    contents['positive_solver_refined.py']=solver.encode()
    for n,data in contents.items(): write_checked(dest/n,data)
    record={'schema':'rei.age_refinement.prepared.v1','native_sha':manifest['native_sha'],
            'original_input_count':len(manifest['files']),'native_compile':'NOT_RUN_BY_PREPARER',
            'accessor_original_prefix_sha256':hashlib.sha256(original).hexdigest(),
            'accessor_suffix_sha256':hashlib.sha256(suffix).hexdigest(),
            'outputs':{n:hashlib.sha256(data).hexdigest() for n,data in sorted(contents.items())}}
    if moment_diagnostics:
        record.update(moment_diagnostics=True,moment_diagnostic_injection_sha256=diagnostic_identity())
    if moment_rounding!='none':
        record.update(moment_rounding=moment_rounding,moment_rounding_injection_sha256=mode_identity())
    write_checked(completed,(json.dumps(record,indent=2,sort_keys=True)+'\n').encode())
    return record

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dest',type=Path,required=True);p.add_argument('--archive',type=Path)
    p.add_argument('--native-input-dir',type=Path)
    p.add_argument('--repo',type=Path);p.add_argument('--fetch-missing',action='store_true')
    p.add_argument('--moment-diagnostics',action='store_true')
    p.add_argument('--moment-rounding',choices=('none','subnormal-count','subnormal-pair','subnormal-pair-search'),default='none')
    a=p.parse_args()
    out=prepare(Path(__file__).resolve().parents[1],a.dest.resolve(),a.archive,a.repo,a.fetch_missing,a.moment_diagnostics,a.moment_rounding,native_input_dir=a.native_input_dir)
    print(json.dumps({'status':'PREPARED_NOT_COMPILED','native_sha':out['native_sha'],'files':len(out['outputs'])}))
if __name__=='__main__':main()
