#!/usr/bin/env python3
"""One approved attempt; 4 s reservation, combined measured ceiling 3.5 CPU s.
No run authorization is conferred by this file. Root must supply --go after
explicit owner approval for cumulative temporary ceiling 70 CPU s.
"""
import argparse,json,os,resource,runpy,signal,sys,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--go',required=True,choices=['OWNER_APPROVED_CUMULATIVE_70']);p.add_argument('--data',required=True);p.add_argument('--out',required=True);a=p.parse_args()
o=Path(a.out);o.mkdir(parents=True,exist_ok=True)
# Exclusive creation prevents accidental automatic repeat of this planned unit.
with (o/'ATTEMPT_STARTED.json').open('x') as f:json.dump({'reservation_cpu_s':4,'combined_cpu_ceiling_s':3.5,'memory_bytes':536870912,'wall_ceiling_s':60,'retry':False},f)
resource.setrlimit(resource.RLIMIT_AS,(536870912,536870912))
def expired(sig,frame):raise TimeoutError('Bounded render limit reached')
signal.signal(signal.SIGALRM,expired);signal.alarm(60)
signal.signal(signal.SIGPROF,expired)
u=resource.getrusage(resource.RUSAGE_SELF);signal.setitimer(signal.ITIMER_PROF,max(.001,3.40-u.ru_utime-u.ru_stime))
start=time.monotonic();status='FAILED';error=None
try:
    sys.path.insert(0,str(Path(__file__).parent));sys.argv=['build_figures.py',a.data,a.out]
    runpy.run_path(str(Path(__file__).with_name('build_figures.py')),run_name='__main__')
    # Cheap mechanical checks only; independent scientific/visual review separate.
    m=json.loads((o/'FIGURE_METADATA.json').read_text());assert len(m['figures'])==12
    for f in m['figures']:
        for panel in f['panels']:assert panel['xscale']==panel['yscale']=='log'
        for ext in ['pdf','svg','png']:assert (o/(f['stem']+'.'+ext)).stat().st_size>0
    status='WRITTEN_PENDING_INDEPENDENT_REVIEW'
except BaseException as e:error=type(e).__name__+': '+str(e)
finally:
    signal.alarm(0);signal.setitimer(signal.ITIMER_PROF,0)
    u=resource.getrusage(resource.RUSAGE_SELF);c=resource.getrusage(resource.RUSAGE_CHILDREN);total=u.ru_utime+u.ru_stime+c.ru_utime+c.ru_stime
    if total>3.5:status='CEILING_EXCEEDED'
    result=dict(status=status,error=error,combined_cpu_before_receipt_s=total,wall_before_receipt_s=time.monotonic()-start,reservation_cpu_s=4,ceiling_cpu_s=3.5,receipt_tail='Controller external rusage must debit final total',retry=False)
    (o/'ATTEMPT_RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if status!='WRITTEN_PENDING_INDEPENDENT_REVIEW':sys.exit(1)
