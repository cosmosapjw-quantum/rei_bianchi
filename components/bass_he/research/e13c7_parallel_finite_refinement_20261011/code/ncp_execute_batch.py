#!/usr/bin/env python3
"""One sealed heavy MPI batch plus durable return packaging; no budget replay."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import sys
import time
import traceback
import zipfile
from common import canonical, read, save, save_bytes, sha
from parallel_batch import verify_closure

def stop_child_group(proc):
    """Quiesce the launcher (which quiesces its rank groups) before packaging."""
    if proc is None:
        return {'child_started':False,'quiesced':True}
    if proc.poll() is not None:
        return {'child_started':True,'already_exited':True,'returncode':proc.returncode,'quiesced':True}
    actions=[]
    for sig,wait_seconds in ((signal.SIGTERM,15),(signal.SIGKILL,10)):
        try:
            os.killpg(proc.pid,sig)
            actions.append(sig.name)
        except ProcessLookupError:
            pass
        try:
            proc.wait(timeout=wait_seconds)
            return {'child_started':True,'actions':actions,'returncode':proc.returncode,'quiesced':True}
        except subprocess.TimeoutExpired:
            continue
    raise RuntimeError('launcher group did not quiesce; return packaging is unsafe')

def interrupted(signum, frame):
    raise InterruptedError('heavy wrapper received '+signal.Signals(signum).name)

def make_return(output, package):
    """Archive actual completed/failed bytes; never infer a successful batch."""
    snap = output / 'PINNED_EXECUTION'
    snap.mkdir(exist_ok=False)
    for name in ('EXECUTION_LOCK.json', 'SOURCE_LOCK.json', 'inputs/WORK_PLAN.json', 'RESEARCH_CONTRACT.json', 'SCIENTIFIC_CONTRACT.md'):
        save_bytes(snap / name, (package / name).read_bytes())
    files = sorted(p for p in output.rglob('*') if p.is_file())
    for p in files:
        if p.is_symlink() or not p.resolve().is_relative_to(output):
            raise ValueError('unsafe return path')
    manifest = {str(p.relative_to(output)): {'bytes':p.stat().st_size,'sha256':sha(p)} for p in files}
    save(output / 'RETURN_MANIFEST.json', {'schema':'bass-he-e13c7-return-manifest-v1', 'files':manifest,
         'full_global_fraction_reduction':'NOT_RUN_PENDING_CHAT_INTAKE', 'provider_attestation':'NOT_ASSERTED'})
    files.append(output / 'RETURN_MANIFEST.json')
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    temporary = output.parent / ('BASS_HE_E13C7_HEAVY_MPI_RETURN_' + timestamp + '.zip.partial')
    with zipfile.ZipFile(temporary, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as z:
        for p in sorted(files):
            z.write(p, arcname=str(p.relative_to(output)))
    # Check actual decompressed member bytes, not only a name/size listing.
    with zipfile.ZipFile(temporary) as z:
        if len(z.namelist()) != len(set(z.namelist())):
            raise ValueError('duplicate return ZIP member')
        for name, rec in manifest.items():
            h=hashlib.sha256(); count=0
            with z.open(name) as f:
                for b in iter(lambda:f.read(1024*1024),b''):
                    h.update(b); count+=len(b)
            if count != rec['bytes'] or h.hexdigest() != rec['sha256']:
                raise ValueError('return ZIP member identity mismatch: '+name)
    digest = sha(temporary)
    final = temporary.with_name(temporary.name.removesuffix('.zip.partial') + '_sha_' + digest[:12] + '.zip')
    os.link(temporary, final); temporary.unlink()
    with final.open('rb') as f:
        os.fsync(f.fileno())
    receipt = {'archive':str(final), 'bytes':final.stat().st_size, 'sha256':digest, 'members':len(files),
        'manifest_sha256':sha(output/'RETURN_MANIFEST.json'), 'member_bytes_checked':len(manifest),
        'cloud_backup':'PENDING_CALLER_UPLOAD_AND_READBACK'}
    save(output.parent / (final.name + '.RECEIPT.json'), receipt)
    return receipt

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--package',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--execution-lock-sha256',required=True)
    p.add_argument('--ranks',default='auto')
    p.add_argument('--resume-from',type=Path)
    p.add_argument('--retry-incomplete-nodes')
    a=p.parse_args(); root=a.package.resolve(); out=a.output_dir.resolve()
    if out==root or out.is_relative_to(root/'inputs') or out.is_relative_to(root/'code'):
        raise ValueError('output cannot replace pinned input or source directories')
    out.mkdir(parents=True,exist_ok=False)
    started=time.perf_counter(); child_started=False; rc=None; error=None; proc=None; cleanup=None
    old_term=signal.signal(signal.SIGTERM,interrupted)
    try:
        before=verify_closure(root,a.execution_lock_sha256)
        plan=read(root/'inputs/WORK_PLAN.json')
        if plan['status']!='SEALED_FOR_HEAVY_NCP' or len(plan['ncp_nodes'])!=2331:
            raise ValueError('sealed 2331-path heavy plan required')
        argv=[sys.executable,str(root/'code/parallel_batch.py'),'launch','--package',str(root),
            '--output-dir',str(out/'BATCH'),'--execution-lock-sha256',a.execution_lock_sha256,
            '--transport','mpi','--scope','ncp','--ranks',a.ranks]
        root_option=os.geteuid()==0
        if root_option:
            argv.append('--allow-openmpi-root')
        if a.resume_from:
            argv+=['--resume-from',str(a.resume_from.resolve())]
        if a.retry_incomplete_nodes:
            if not a.resume_from:
                raise ValueError('explicit incomplete-node retry requires a prior batch')
            argv+=['--retry-incomplete-nodes',a.retry_incomplete_nodes]
        save(out/'ATTEMPT_START.json',{'schema':'bass-he-e13c7-heavy-attempt-v1',
            'started_utc':datetime.now(timezone.utc).isoformat(),'hostname':platform.node(),
            'provider_attestation':'NOT_ASSERTED','python':sys.version,'effective_uid':os.geteuid(),
            'openmpi_root_option_selected_for_observed_uid':root_option,'argv':argv,
            'source_execution_before':before,'new_batch_scope_paths':2331,
            'full_global_fraction_reduction':'NOT_RUN_RETURN_TO_CHAT',
            'automatic_retries':0,'old_scientific_replays':0})
        with (out/'MPI_BATCH.stdout').open('xb') as stdout, (out/'MPI_BATCH.stderr').open('xb') as stderr:
            proc=subprocess.Popen(argv,stdout=stdout,stderr=stderr,start_new_session=True)
            child_started=True
            try:
                rc=proc.wait(timeout=plan['limits']['batch_wall_seconds']+180)
            except subprocess.TimeoutExpired:
                raise TimeoutError('heavy batch wrapper wall limit; no automatic retry')
        if rc!=0:
            raise RuntimeError('heavy MPI launcher returned nonzero exit: '+str(rc))
        complete=read(out/'BATCH/BATCH_COMPLETE.json')
        if complete['work']['nodes']!=plan['ncp_nodes'] or complete['work']['N']!=plan['primary_N'] or complete['work']['precision']!=plan['precision']:
            raise ValueError('completed batch scope mismatch')
        if complete['new_validated_path_calls']+complete['reused_completed_paths']!=2331:
            raise ValueError('completed batch path accounting mismatch')
        after=verify_closure(root,a.execution_lock_sha256)
        if before!=after:
            raise ValueError('source/input execution closure changed during heavy batch')
        save(out/'ATTEMPT_COMPLETE.json',{'status':'COMPLETE_HEAVY_PATHS_PENDING_CHAT_REDUCTION_AND_REVIEW',
            'execution_lock_sha256':a.execution_lock_sha256,'batch_collection_semantic_sha256':complete['collection_semantic_sha256'],
            'new_scientific_path_calls':complete['new_validated_path_calls'],'reused_completed_paths':complete['reused_completed_paths'],
            'new_coefficient_evaluations':complete['new_coefficient_evaluations'],'mpi_child_exit_code':rc,
            'elapsed_seconds':time.perf_counter()-started,'source_execution_after':after,
            'global_budget_invocations':0,'prior_scientific_reruns':0,'automatic_retries':0,
            'physical':'HOLD','continuum':'HOLD','production':'HOLD','receiver':'HOLD'})
    except BaseException as exc:
        error=exc
        # Preserve the original failure, then stop all active computation before
        # enumerating or archiving any files that workers could still change.
        failure_traceback=traceback.format_exc()
        try:
            cleanup=stop_child_group(proc)
        except BaseException as cleanup_exc:
            save(out/'CLEANUP_FAILURE.json',{'original_error_type':type(exc).__name__,'original_error':str(exc),
                'cleanup_error_type':type(cleanup_exc).__name__,'cleanup_error':str(cleanup_exc),
                'return_packaging':'NOT_RUN_OUTPUT_MAY_STILL_CHANGE','automatic_retries':0})
            raise
        rc=proc.returncode if proc is not None else rc
        save(out/'ATTEMPT_FAILURE.json',{'status':'FAIL_PRESERVED_NO_AUTOMATIC_RETRY','error_type':type(exc).__name__,
            'error':str(exc),'traceback':failure_traceback,'mpi_child_started':child_started,
            'mpi_child_exit_code':rc,'elapsed_seconds':time.perf_counter()-started,
            'full_global_fraction_reduction':'NOT_RUN','automatic_retries':0,'cleanup':cleanup})
    finally:
        signal.signal(signal.SIGTERM,old_term)
    receipt=make_return(out,root)
    print(json.dumps({'status':'FAIL_PRESERVED' if error else 'COMPLETE_HEAVY_PATHS_PENDING_CHAT_REDUCTION_AND_REVIEW',
                      'return':receipt},sort_keys=True),flush=True)
    return 1 if error else 0

if __name__=='__main__':
    raise SystemExit(main())
