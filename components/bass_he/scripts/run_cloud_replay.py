#!/usr/bin/env python3
"""Local durable cloud replay entrypoint; service invokes the same CLI."""
import argparse, json, os, sys
from pathlib import Path
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','NUMBA_NUM_THREADS'):os.environ[key]='1'
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from bass_he.cloud.runtime import binding
from bass_he.cloud.store import ResultStore
from bass_he.cloud.controller import Controller
from bass_he.cloud.export import export_checkpoint
from bass_he.cloud.resources import inventory,worker_limit
from bass_he.cloud.storage import inspect_root_storage,admit_root_storage,write_fsync_probe
from bass_he.cloud.memory_calibration import calibrate_memory,verify_memory_receipt
from bass_he.cloud.calibration import admit_calibrated_workers,verify_sweep_evidence
from bass_he.cloud.import_evidence import import_completed

ROOT=Path(__file__).resolve().parents[1]
def admit_storage(out,profile,bind=None):
    mode=profile.get('storage_mode')
    if mode in ('mounted_host','root_backed_host'):
        if not out.resolve().is_relative_to('/srv/bass-he/runs'):raise ValueError('run directory outside host storage')
        host=inventory(Path('/srv/bass-he'))
        if mode=='mounted_host':
            if not host.data_mount:raise RuntimeError('BLOCKED_DATA_MOUNT')
        else:
            admit_root_storage(inspect_root_storage())
            write_fsync_probe()
            if host.unknown_limits or host.usable_cpus is None or host.effective_memory is None or host.memory_current is None:raise RuntimeError('BLOCKED_UNKNOWN_RESOURCE_LIMIT')
        if not profile.get('memory_calibration_receipt'):raise RuntimeError('BLOCKED_MEMORY_CALIBRATION')
        if bind is None:raise RuntimeError('BLOCKED_MEMORY_CALIBRATION')
        memory=verify_memory_receipt(profile['memory_calibration_receipt'],bind)
        if profile.get('worker_rss_p95_bytes')!=memory['worker_rss_p95_bytes'] or profile.get('memory_receipt_sha256')!=memory['sha256']:
            raise RuntimeError('BLOCKED_MEMORY_CALIBRATION')
        worker_limit(profile,host,1,profile['worker_rss_p95_bytes'])
        class HostCapacity:
            pause_reason=None
            def __call__(self,ready,active=0):
                if mode=='root_backed_host':
                    try:admit_root_storage(inspect_root_storage(),initial=False)
                    except RuntimeError as exc:
                        self.pause_reason=str(exc);return 0
                self.pause_reason=None
                return worker_limit(profile,inventory(Path('/srv/bass-he')),ready,profile['worker_rss_p95_bytes'],active)
        return HostCapacity()
    if mode=='local_sandbox':
        if not out.resolve().is_relative_to('/tmp'):raise ValueError('local sandbox output must be under /tmp')
        return lambda ready,active=0:min(2,profile['workers'],ready)
    raise ValueError('unknown storage mode')
def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='command',required=True)
    p=sub.add_parser('preflight');p.add_argument('--env-out',type=Path)
    p=sub.add_parser('calibrate-memory');p.add_argument('--out',type=Path,required=True);p.add_argument('--storage-mode',choices=('mounted_host','root_backed_host','local_sandbox'),required=True);p.add_argument('--case',choices=('control','endpoint'),default='control')
    p=sub.add_parser('run');p.add_argument('--profile',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--workers',type=int,default=1);p.add_argument('--admit-calibrated-workers',type=Path);p.add_argument('--reuse-evidence',type=Path)
    for name in ('resume','status','export'):
        p=sub.add_parser(name);p.add_argument('--out',type=Path,required=True)
        if name=='resume':p.add_argument('--retry-failed',action='store_true')
    args=ap.parse_args();bind=binding(ROOT)
    if args.command=='preflight':
        if args.env_out:
            value={'schema':'bass_he.environment_provenance.v1','binding':bind.identity(),'source_commit':bind.source_commit,'source_tree':bind.source_tree,'packages':bind.packages,'thread_policy':bind.thread_policy}
            args.env_out.parent.mkdir(parents=True,exist_ok=True)
            with args.env_out.open('xb') as f:f.write((json.dumps(value,sort_keys=True,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
            fd=os.open(args.env_out.parent,os.O_DIRECTORY)
            try:os.fsync(fd)
            finally:os.close(fd)
        print(json.dumps({'status':'PASS','source_commit':bind.source_commit,'source_tree':bind.source_tree,'binding':bind.identity(),'accelerator':'ACCELERATOR_PAYLOAD_UNAVAILABLE'},sort_keys=True));return 0
    if args.command=='calibrate-memory':
        class BindingOnly:binding=bind
        controller=Controller(BindingOnly())
        try:spec=controller.initial_specs()[1] if args.case=='control' else next(iter(controller.endpoint_specs().values()))
        finally:controller.supervisor.close()
        receipt=calibrate_memory(args.out,bind,spec,args.storage_mode)
        print(json.dumps(receipt,sort_keys=True));return 0 if receipt['status']=='PASS' else 2
    out=args.out
    if args.command=='run':
        profile=json.loads(args.profile.read_text())
        if profile.get('artifact_kind')=='DESIGN_TARGET_NOT_EXECUTABLE_RUNNER_CONFIG':raise ValueError('design profile is not a runtime profile')
        if profile.get('backend')!='python' or profile.get('source_commit')!=bind.source_commit:raise ValueError('runtime profile binding mismatch')
        if profile.get('storage_mode') not in ('local_sandbox','mounted_host','root_backed_host'):raise ValueError('explicit storage_mode required')
        if args.workers<1 or args.workers>64:raise ValueError('worker count outside 1..64')
        memory=None
        if profile['storage_mode'] in ('mounted_host','root_backed_host'):
            if not profile.get('memory_calibration_receipt'):raise RuntimeError('BLOCKED_MEMORY_CALIBRATION')
            memory=verify_memory_receipt(profile['memory_calibration_receipt'],bind)
        rss=memory['worker_rss_p95_bytes'] if memory else profile.get('worker_rss_p95_bytes')
        memory_sha=memory['sha256'] if memory else None
        admission=None
        if args.workers>32:
            if not args.admit_calibrated_workers:raise ValueError('calibrated worker admission required above 32')
            admission=json.loads(args.admit_calibrated_workers.read_text())
            admit_calibrated_workers(args.workers,admission,bind.identity(),bind.thread_policy,memory_sha)
            verify_sweep_evidence(args.admit_calibrated_workers,admission)
        runtime_profile={'source_commit':bind.source_commit,'backend':'python','workers':args.workers,'storage_mode':profile['storage_mode'],'same_filesystem_as_root':profile['storage_mode']=='root_backed_host','worker_rss_p95_bytes':rss,'memory_calibration_receipt':profile.get('memory_calibration_receipt'),'memory_receipt_sha256':memory_sha,'controller_reserve_bytes':profile.get('controller_reserve_bytes',0),'memory_buffer_bytes':profile.get('memory_buffer_bytes',0),'calibrated_worker_receipt':str(args.admit_calibrated_workers) if admission else None,'calibrated_worker_sha256':admission['sha256'] if admission else None}
    else:runtime_profile=json.loads((out/'RUN_PROFILE.json').read_text())
    if runtime_profile['workers']>32:
        path=runtime_profile.get('calibrated_worker_receipt')
        if not path:raise ValueError('calibrated worker admission missing')
        admission=json.loads(Path(path).read_text())
        if admission.get('sha256')!=runtime_profile.get('calibrated_worker_sha256'):raise ValueError('calibrated worker receipt changed')
        admit_calibrated_workers(runtime_profile['workers'],admission,bind.identity(),bind.thread_policy,runtime_profile.get('memory_receipt_sha256'))
        verify_sweep_evidence(path,admission)
    cap=admit_storage(out,runtime_profile,bind)
    if args.command=='run':
        out.mkdir(parents=True,exist_ok=True)
        pf=out/'RUN_PROFILE.json'
        with pf.open('xb') as f:
            f.write((json.dumps(runtime_profile,sort_keys=True)+'\n').encode());f.flush();os.fsync(f.fileno())
        fd=os.open(out,os.O_DIRECTORY)
        try:os.fsync(fd)
        finally:os.close(fd)
    profile=runtime_profile
    store=ResultStore(out,bind)
    try:
        imported=import_completed(args.reuse_evidence,store) if args.command=='run' and args.reuse_evidence else 0
        if args.command=='status':
            rec=store.reconcile();print(json.dumps(rec.__dict__,sort_keys=True));return 0
        if args.command=='export':
            receipt=export_checkpoint(store,out/'exports');print(json.dumps(receipt.__dict__,sort_keys=True));return 0
        result=Controller(store,profile['workers'],worker_cap=cap,retry_failed=getattr(args,'retry_failed',False)).run()
        events=out/'EVENTS.jsonl'
        imported_total=sum(json.loads(line).get('type')=='IMPORTED_EVIDENCE' for line in events.read_text().splitlines()) if events.exists() else imported
        print(json.dumps({**result.__dict__,'imported_evidence':imported_total,'newly_imported_evidence':imported},sort_keys=True));return 0 if result.status=='PASS' else 1
    finally:store.close()
if __name__=='__main__':raise SystemExit(main())
