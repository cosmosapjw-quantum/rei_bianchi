"""One-worker bounded RSS preflight, isolated from science run results."""
import hashlib, json, math, os, time
from pathlib import Path
from .contracts import task_id
from .resources import inventory
from .storage import inspect_root_storage,admit_root_storage,write_fsync_probe
from .store import ResultStore
from .supervisor import Supervisor


def _rss(pid):
    for line in Path(f'/proc/{pid}/status').read_text().splitlines():
        if line.startswith('VmRSS:'):return int(line.split()[1])*1024
    raise RuntimeError('worker VmRSS unavailable')


def _write_receipt(path,body):
    body={**body,'sha256':hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
    with path.open('xb') as f:
        f.write((json.dumps(body,sort_keys=True,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
    fd=os.open(path.parent,os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
    return body


def verify_memory_receipt(path,binding):
    data=json.loads(Path(path).read_text());body={k:v for k,v in data.items() if k!='sha256'}
    sha=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if sha!=data.get('sha256') or data.get('status')!='PASS' or data.get('binding')!=binding.identity() or data.get('scientific_source_id')!=binding.scientific_source_id or data.get('thread_policy')!=binding.thread_policy or data.get('worker_rss_p95_bytes',0)<=0:
        raise RuntimeError('BLOCKED_MEMORY_CALIBRATION')
    return data


def calibrate_memory(out,binding,spec,storage_mode='local_sandbox',interval=.05,deadline=120):
    out=Path(out)
    if interval<=0 or interval>.5 or deadline<=0 or deadline>120:raise ValueError('bounded calibration interval/deadline required')
    if storage_mode in ('mounted_host','root_backed_host') and not out.resolve().is_relative_to('/srv/bass-he/runs'):raise RuntimeError('BLOCKED_DATA_MOUNT')
    if storage_mode=='local_sandbox' and not out.resolve().is_relative_to('/tmp'):raise ValueError('local sandbox output must be under /tmp')
    if storage_mode not in ('mounted_host','root_backed_host','local_sandbox'):raise ValueError('invalid storage mode')
    if storage_mode=='root_backed_host':
        admit_root_storage(inspect_root_storage());write_fsync_probe()
    host=inventory(Path('/srv/bass-he'))
    if storage_mode in ('mounted_host','root_backed_host') and ((storage_mode=='mounted_host' and not host.data_mount) or host.unknown_limits or host.effective_memory is None or host.memory_current is None or host.memory_current>=.65*host.effective_memory):
        raise RuntimeError('BLOCKED_MEMORY_CALIBRATION')
    out.mkdir(parents=True,exist_ok=False)
    fd=os.open(out.parent,os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
    samples=[];service=[];next_sample=0.;store=ResultStore(out/'PERF_MEMORY',binding);su=Supervisor(binding,deadline=deadline)
    body={'schema':'bass_he.memory_calibration.v1','status':'BLOCKED_MEMORY_CALIBRATION',
          'binding':binding.identity(),'scientific_source_id':binding.scientific_source_id,
          'thread_policy':binding.thread_policy,'case_task_id':task_id(spec),'storage_mode':storage_mode,'same_filesystem_as_root':storage_mode=='root_backed_host',
          'sample_interval_seconds':interval,'baseline_controller_memory_bytes':host.memory_current,
          'namespace':'PERF_MEMORY_NOT_SCIENCE'}
    try:
        def observe(slots):
            nonlocal next_sample
            now=time.monotonic()
            if now<next_sample:return True
            next_sample=now+interval
            for slot in slots:
                if slot['process'].is_alive():
                    try:samples.append(_rss(slot['process'].pid))
                    except FileNotFoundError:pass # process exited between liveness and proc read
            if storage_mode in ('mounted_host','root_backed_host'):
                current=inventory(Path('/srv/bass-he'))
                if current.memory_current is None:return False
                service.append(current.memory_current)
                if current.memory_current>=.75*current.effective_memory:return False
            return True
        report=su.run_ready([spec],1,store,observe=observe)
        outcome=report.outcomes.get(task_id(spec))
        if report.failures or outcome is None or outcome.status!=('WRONG_PAIR' if spec.kind=='wrong_pair_check' else 'PASS') or len(samples)<3:
            body['reason']={'failures':report.failures,'outcome':outcome.status if outcome else None,'samples':len(samples)}
        else:
            ordered=sorted(samples)
            body.update(status='PASS',sample_count=len(samples),worker_rss_peak_bytes=ordered[-1],
                        worker_rss_p95_bytes=ordered[math.ceil(.95*len(ordered))-1],
                        service_memory_peak_bytes=max(service) if service else None)
    except BaseException as exc:
        body['reason']=repr(exc)
    finally:
        su.close();store.close()
    body.setdefault('sample_count',len(samples))
    body.setdefault('worker_rss_peak_bytes',max(samples) if samples else None)
    body.setdefault('worker_rss_p95_bytes',None)
    body.setdefault('service_memory_peak_bytes',max(service) if service else None)
    return _write_receipt(out/'MEMORY_CALIBRATION.json',body)
