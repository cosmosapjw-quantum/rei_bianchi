#!/usr/bin/env python3
"""Validate and package a stable local candidate without clobbering inputs."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tarfile
import tempfile

HERE=Path(__file__).resolve().parent

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 if spec is None or spec.loader is None:raise ImportError(path)
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

supervisor=load('adaptive_history_package_supervisor',HERE/'run_adaptive_history.py')

def sha(path):
 digest=hashlib.sha256()
 with Path(path).open('rb') as handle:
  for chunk in iter(lambda:handle.read(1024*1024),b''):digest.update(chunk)
 return digest.hexdigest()

def validate_stable_run(run,held_lock):
 run=Path(run).resolve();coordinator=None
 try:
  coordinator=supervisor.Coordinator(run_dir=run,resume=True,_repair=False,_held_run_lock=held_lock)
  control=supervisor.read_json(run/'CONTROL.json');latest=supervisor.read_json(run/'checkpoints/LATEST.json')
  if supervisor.canonical(control)!=supervisor.canonical(latest.get('control_state')):raise ValueError('CONTROL/LATEST must match before packaging')
  if control.get('status') in {'READY','RUNNING'}:raise ValueError('active or unfinalized run cannot be packaged')
  if control.get('classification')!='CANDIDATE_UNSEALED_LOCAL_EXECUTION':raise ValueError('test-only or foreign runs cannot be packaged')
  expected=coordinator._summary(control['status']);observed=supervisor.read_json(run/'data/results.json')
  if expected!=observed:raise ValueError('results summary does not match validated checkpoint')
  return coordinator,observed
 except Exception:
  if coordinator is not None:coordinator.close()
  raise

def select(run):
 required=[run/'CONTROL.json',run/'RUN_OWNER.json',run/'RUN_METADATA.json',run/'data/results.json'];files=[]
 for path in required:
  if path.is_symlink() or not path.is_file():raise FileNotFoundError(path)
 files.extend(required);files.extend(sorted(path for path in run.glob('*.json') if path.is_file() and not path.is_symlink()))
 for directory in ('history','receipts'):
  root=run/directory
  for path in sorted(root.rglob('*')):
   if path.is_symlink():raise ValueError(f'unsafe symlink in bundle evidence: {path}')
   if path.is_file():
    if path.suffix!='.json':raise ValueError(f'unexpected non-JSON evidence: {path}')
    files.append(path)
 snapshots=run/'checkpoints/snapshots'
 for path in sorted(snapshots.rglob('*')):
  if path.is_symlink():raise ValueError(f'unsafe symlink in snapshot evidence: {path}')
  if path.is_file():files.append(path)
 latest=run/'checkpoints/LATEST.json';files.append(latest);row=supervisor.read_json(latest)
 if row['latest_generation'] is not None:
  generation=run/'checkpoints'/row['latest_generation'];files.extend(sorted(path for path in generation.iterdir() if path.is_file() and not path.is_symlink()))
 unique={path.resolve():path.resolve() for path in files}
 for path in unique:
  if run.resolve() not in path.parents:raise ValueError(f'unsafe bundle path: {path}')
 return sorted(unique)

def _temporary_payload(directory,prefix,payload):
 with tempfile.NamedTemporaryFile(prefix=prefix,dir=directory,delete=False) as handle:
  path=Path(handle.name);handle.write(payload);handle.flush();os.fsync(handle.fileno())
 return path

def _publish_no_clobber(temporary,target):
 os.link(temporary,target)

def package(run,output):
 run=Path(run).resolve();output=Path(output).resolve()
 if output==run or run in output.parents:raise ValueError('package output must be outside the source run directory')
 receipt_path=output.with_suffix(output.suffix+'.receipt.json');checksum_path=output.with_suffix(output.suffix+'.sha256');targets=(output,receipt_path,checksum_path)
 if any(path.exists() for path in targets):raise FileExistsError('package output or sidecar already exists; choose a new name')
 with supervisor.RunLock(run) as held_lock:
  coordinator,result=validate_stable_run(run,held_lock);files=select(run);output.parent.mkdir(parents=True,exist_ok=True);temporaries=[];published=[]
  try:
   with tempfile.NamedTemporaryFile(prefix=f'.{output.name}.tmp-',dir=output.parent,delete=False) as raw:
    archive_tmp=Path(raw.name);temporaries.append(archive_tmp)
    with gzip.GzipFile(filename='',mode='wb',fileobj=raw,compresslevel=9,mtime=0) as zipped:
     with tarfile.open(fileobj=zipped,mode='w') as archive:
      for path in files:
       data=path.read_bytes();info=tarfile.TarInfo(str(path.relative_to(run)));info.size=len(data);info.mode=0o644;info.mtime=0;info.uid=info.gid=0;info.uname=info.gname='';archive.addfile(info,io.BytesIO(data))
    raw.flush();os.fsync(raw.fileno())
   bundle_sha=sha(archive_tmp);receipt={'bundle':output.name,'bundle_sha256':bundle_sha,'bundle_size_bytes':archive_tmp.stat().st_size,'included_file_count':len(files),'result_status':result['status'],'run_id':result['run_id'],'runtime_contract_sha256':result['runtime_contract_sha256'],'stage_id':result['stage_id']}
   receipt_tmp=_temporary_payload(output.parent,f'.{receipt_path.name}.tmp-',(json.dumps(receipt,indent=2,sort_keys=True)+'\n').encode());temporaries.append(receipt_tmp)
   checksum_tmp=_temporary_payload(output.parent,f'.{checksum_path.name}.tmp-',f'{bundle_sha}  {output.name}\n'.encode());temporaries.append(checksum_tmp)
   for temporary,target in zip(temporaries,targets):_publish_no_clobber(temporary,target);published.append((temporary,target))
   supervisor._fsync_dir(output.parent)
   return receipt
  except Exception:
   for temporary,target in reversed(published):
    try:
     if target.exists() and os.path.samestat(temporary.stat(),target.stat()):target.unlink()
    except OSError:pass
   raise
  finally:
   coordinator.close()
   for temporary in temporaries:
    try:temporary.unlink()
    except FileNotFoundError:pass

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--run-dir',required=True);parser.add_argument('--output',required=True);args=parser.parse_args();print(json.dumps(package(args.run_dir,args.output),indent=2,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
