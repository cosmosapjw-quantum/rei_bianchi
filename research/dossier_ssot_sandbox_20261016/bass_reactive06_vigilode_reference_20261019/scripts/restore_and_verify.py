#!/usr/bin/env python3
"""Restore BR06 into a new workspace and run the declared offline verification.

Requires an installed Rust/Cargo 1.94.1 (with Clippy/rustfmt) and Python scientific
dependencies for --mode verify. It neither installs software nor contacts a
network. Source, vendor and fixture identities are checked before execution.
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile
import time
import tomllib

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as stream:
        json.dump(value,stream,indent=2); stream.write('\n')

def copy_sources(src,dst):
    shutil.copytree(src,dst,ignore=shutil.ignore_patterns('target','__pycache__','*.pyc'))

def verify_fixture_hashes(root,work=None):
    records=json.loads((root/'evidence/recovery/SOURCE_AND_INPUT_RESTORE.json').read_text())['csvs']
    expected_names={'STEP1_'+key+'.csv' for key in ['STEPS','TEMPLATES','RULES','BIRTHS']}
    if {Path(rec['path']).name for rec in records}!=expected_names or len(records)!=4:
        raise ValueError('unexpected canonical step1 fixture inventory')
    checks=[]
    for rec in records:
        name=Path(rec['path']).name
        paths=[root/'inputs'/name]
        if work is not None:
            paths += [work/'inputs'/name,work/'reference_parent/evidence/native/monitor_n16_r8'/name.replace('STEP1_','MONITOR_')]
        for path in paths:
            if path.stat().st_size!=rec['bytes'] or sha(path)!=rec['sha256']:
                raise ValueError('canonical step1 fixture mismatch: '+str(path))
        checks.append({'name':name,'sha256':rec['sha256'],'copies_verified':len(paths)})
    return checks

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--mode',choices=['prepare','verify'],default='verify')
    args=ap.parse_args(); root=args.root.resolve(strict=True); work=args.work.resolve()
    if work.exists() or work.is_relative_to(root):
        raise ValueError('choose a new workspace outside the delivered source root')
    parent=json.loads((root/'contracts/PARENT_INPUT_SHA256.json').read_text())
    source_record=json.loads((root/'evidence/implementation/SOURCE_IDENTITY_FINAL.json').read_text())
    new={item['path']:item['sha256'] for item in source_record['source_files']}
    bootstrap=source_record['bootstrap_config']
    if sha(root/bootstrap['path'])!=bootstrap['sha256']:
        raise ValueError('bootstrap configuration mismatch')
    if len(parent)!=133 or len(new)!=10: raise ValueError('unexpected source inventory')
    for rel,expected in {**parent,**new}.items():
        if sha(root/rel)!=expected: raise ValueError('source mismatch: '+rel)
    verify_fixture_hashes(root)
    upstream=json.loads((root/'contracts/VIGILODE_SELECTED_SOURCE_IDENTITY.json').read_text())
    if len(upstream['files'])!=477: raise ValueError('unexpected selected VigilODE inventory')
    for rec in upstream['files']:
        if sha(root/'vendor/vigilode'/rec['path'])!=rec['sha256']:
            raise ValueError('VigilODE source mismatch: '+rec['path'])
    tar=root/'vendor/REGISTRY_99_CARGO_LOCKED.tar.gz'
    registry_archive=json.loads((root/'contracts/REGISTRY_ARCHIVE_IDENTITY.json').read_text())
    if sha(tar)!=registry_archive['sha256']: raise ValueError('registry archive mismatch')
    work.mkdir(parents=True)
    for name in ['br06','parent','inputs']: copy_sources(root/name,work/name)
    if sha(work/bootstrap['path'])!=bootstrap['sha256']:
        raise ValueError('restored bootstrap configuration mismatch')
    copy_sources(root/'vendor/vigilode',work/'vendor/vigilode')
    with tarfile.open(tar,'r:gz') as package:
        seen=set()
        for member in package:
            path=PurePosixPath(member.name)
            if (not member.isfile() or path.is_absolute() or '..' in path.parts
                or not path.parts or path.parts[0]!='registry' or member.name in seen):
                raise ValueError('unsafe/duplicate registry archive member')
            seen.add(member.name)
            destination=work/'vendor'/path
            destination.parent.mkdir(parents=True,exist_ok=True)
            with package.extractfile(member) as inp, destination.open('xb') as out:
                shutil.copyfileobj(inp,out)
    lock=tomllib.loads((work/'br06/Cargo.lock').read_text())
    directories={}
    for path in (work/'vendor/registry').iterdir():
        rec=tomllib.loads((path/'Cargo.toml').read_text())['package']
        directories[(rec['name'],rec['version'])]=path
    package_count=file_count=0
    for rec in lock['package']:
        if not rec.get('source','').startswith('registry+'): continue
        directory=directories[(rec['name'],rec['version'])]
        check=json.loads((directory/'.cargo-checksum.json').read_text())
        if check['package']!=rec['checksum']: raise ValueError('locked package checksum mismatch')
        for rel,expected in check['files'].items():
            if sha(directory/rel)!=expected: raise ValueError('vendor source checksum mismatch')
        package_count+=1; file_count+=len(check['files'])
    if package_count!=99: raise ValueError('unexpected locked registry count')
    # This is an exact step1 row subset, not the complete BR05 archive. The
    # independent reader explicitly selects step1; input hashes record the subset.
    reference_parent=work/'reference_parent'
    for name in ['crate','donor_input']: copy_sources(work/'parent'/name,reference_parent/name)
    native=reference_parent/'evidence/native/monitor_n16_r8'; native.mkdir(parents=True)
    for key in ['STEPS','TEMPLATES','RULES','BIRTHS']:
        shutil.copy2(work/'inputs'/('STEP1_'+key+'.csv'),native/('MONITOR_'+key+'.csv'))
    fixture_checks=verify_fixture_hashes(root,work)
    restoration={'schema':'rei.br06.fresh_restore.v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 'source_files_verified':143,'vigilode_selected_files_verified':477,
                 'registry_packages_verified':package_count,'registry_files_verified':file_count,
                 'fixture_hash_checks':fixture_checks,
                 'bootstrap_config_sha256':bootstrap['sha256'],
                 'work':str(work),'empty_cargo_home':True,'new_cargo_target':True,
                 'parent_reference_scope':'Exact step1 row subsets plus original source and donor; not the whole BR05 archive',
                 'mode':args.mode,'runs':[]}
    save(work/'RESTORE_IDENTITY.json',restoration)
    if args.mode=='prepare':
        print(json.dumps(restoration)); return
    environment=os.environ.copy()
    environment.update({'CARGO_HOME':str(work/'cargo_home'),'CARGO_TARGET_DIR':str(work/'target'),
                        'CARGO_NET_OFFLINE':'true','CARGO_BUILD_JOBS':'2','CARGO_INCREMENTAL':'0',
                        'CARGO_PROFILE_DEV_DEBUG':'0','CARGO_PROFILE_TEST_DEBUG':'0'})
    (work/'cargo_home').mkdir()
    versions={}
    for label,command in [('rustc',['rustc','--version']),('cargo',['cargo','--version']),('clippy',['cargo','clippy','--version'])]:
        versions[label]=subprocess.check_output(command,env=environment,text=True).strip()
    if not versions['rustc'].startswith('rustc 1.94.1 '): raise ValueError('Rust 1.94.1 required')
    save(work/'RUNTIME_VERSIONS.json',versions)
    def run(label,command,cwd,timeout=600):
        out=work/(label+'.stdout.log'); err=work/(label+'.stderr.log'); begin=time.monotonic()
        record={'label':label,'command':command,'cwd':str(cwd),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'timeout_s':timeout}
        save(work/(label+'.intent.json'),record)
        with out.open('xb') as stdout,err.open('xb') as stderr:
            try:
                result=subprocess.run(command,cwd=cwd,env=environment,stdout=stdout,stderr=stderr,timeout=timeout,check=False)
                code=result.returncode; status='PASS' if code==0 else 'COMMAND_FAILED'
            except subprocess.TimeoutExpired:
                code=None; status='WORK_BUDGET_TIMEOUT'
        record.update({'status':status,'exit_code':code,'wall_s':time.monotonic()-begin,
                       'stdout_sha256':sha(out),'stderr_sha256':sha(err)})
        save(work/(label+'.json'),record); restoration['runs'].append(record)
        print(json.dumps({'step':label,'status':status,'wall_s':record['wall_s']}),flush=True)
        if code!=0: raise RuntimeError(label+': '+status)
    run('PARENT_TESTS',['cargo','test','--locked','--offline','--all-targets'],work/'parent/br05')
    run('BR06_TESTS',['cargo','test','--locked','--offline','--all-targets'],work/'br06')
    run('BR06_CLIPPY',['cargo','clippy','--locked','--offline','--all-targets','--','-D','warnings'],work/'br06')
    run('PARENT_CLIPPY',['cargo','clippy','--locked','--offline','--all-targets','--','-D','warnings'],work/'parent/br05')
    run('SMALL_REFERENCE',['cargo','run','--locked','--offline','--bin','br06_reference','--',
                         'run','SIGNED_MINUS','gauss','1','8','4','8','16','original','8',str(work/'small_reference')],work/'br06')
    run('INDEPENDENT_REFERENCE',['python3',str(root/'scripts/independent_birth_reference.py'),'--parent',str(reference_parent),
                                 '--orders','64:64:8,128:128:16','--output',str(work/'independent_reference')],work)
    for rel,expected in {**parent,**new}.items():
        if sha(work/rel)!=expected: raise ValueError('restored source changed during verification: '+rel)
    restoration['status']='FRESH_OFFLINE_SOURCE_TEST_AND_REFERENCE_EXECUTIONS_PASSED'
    restoration['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    save(work/'FRESH_RESTORE_VERIFICATION.json',restoration)

if __name__=='__main__': main()
