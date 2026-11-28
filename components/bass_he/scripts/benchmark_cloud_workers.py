#!/usr/bin/env python3
"""Authorized host-only fresh PERF sweep; no science cache reuse."""
import argparse,json,os,sys
from pathlib import Path
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','NUMBA_NUM_THREADS'):os.environ[key]='1'
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from bass_he.cloud.benchmark import benchmark,PerfWorkload
from bass_he.cloud.contracts import CaseSpec
from bass_he.cloud.resources import inventory,worker_limit
from bass_he.cloud.storage import inspect_root_storage,admit_root_storage,write_fsync_probe
from bass_he.cloud.runtime import binding
from bass_he.cloud.memory_calibration import verify_memory_receipt
from bass_he.cloud.calibration import make_worker_receipt
import hashlib

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--profile',type=Path,required=True);ap.add_argument('--cases',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seed',type=int,default=20260928);ap.add_argument('--budget-seconds',type=int,default=900)
    a=ap.parse_args();profile=json.loads(a.profile.read_text());b=binding(Path(__file__).resolve().parents[1]);host=inventory(Path('/srv/bass-he'))
    mode=profile.get('storage_mode')
    if mode not in ('mounted_host','root_backed_host') or profile.get('source_commit')!=b.source_commit or profile.get('backend')!='python':raise RuntimeError('host runtime profile mismatch')
    if not a.out.resolve().is_relative_to('/srv/bass-he/runs'):raise RuntimeError('BLOCKED_DATA_MOUNT')
    if mode=='mounted_host' and not host.data_mount:raise RuntimeError('BLOCKED_DATA_MOUNT')
    if mode=='root_backed_host':admit_root_storage(inspect_root_storage());write_fsync_probe()
    cases=[CaseSpec(**item) for item in json.loads(a.cases.read_text())]
    if not cases or any(s.science_fields['source']!=b.scientific_source_id or s.science_fields['backend']!='python' for s in cases):raise ValueError('PERF case source/backend mismatch')
    if not profile.get('memory_calibration_receipt'):raise RuntimeError('BLOCKED_MEMORY_CALIBRATION')
    memory=verify_memory_receipt(profile['memory_calibration_receipt'],b)
    rss=memory['worker_rss_p95_bytes']
    sweep_profile={**profile,'workers':64}
    max_workers=worker_limit(sweep_profile,host,len(cases),rss)
    if max_workers<1:raise RuntimeError('no eligible host workers')
    class LimitedHost:usable_cpus=max_workers
    def capacity(ready,active=0):
        if mode=='root_backed_host':
            try:admit_root_storage(inspect_root_storage(),initial=False)
            except RuntimeError:return 0
        return worker_limit(sweep_profile,inventory(Path('/srv/bass-he')),ready,rss,active)
    workload=PerfWorkload(cases,b,a.out/'PERF',worker_cap=capacity)
    report=benchmark(profile,LimitedHost(),workload,a.budget_seconds,a.seed)
    a.out.mkdir(parents=True,exist_ok=True)
    result={'status':report.status,'selected':report.selected,'observations':report.observations,'seed':report.seed,'binding':b.identity(),'scientific_source_id':b.scientific_source_id,'memory_receipt_sha256':memory['sha256'],'thread_policy':b.thread_policy,'storage_mode':mode,'same_filesystem_as_root':mode=='root_backed_host','namespace':'PERF_NOT_SCIENCE'}
    dest=a.out/'WORKER_SWEEP.json'
    with dest.open('x') as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    if report.selected is not None:
        observations_sha256=hashlib.sha256(dest.read_bytes()).hexdigest()
        admission=make_worker_receipt(report.selected,b.identity(),b.thread_policy,memory['sha256'],observations_sha256)
        with (a.out/'ADMISSION_RECEIPT.json').open('x') as f:json.dump(admission,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    fd=os.open(a.out,os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
    print(json.dumps({'status':report.status,'selected':report.selected,'arms':len(report.observations)}))
    return 0 if report.status=='COMPLETE' else 2
if __name__=='__main__':raise SystemExit(main())
