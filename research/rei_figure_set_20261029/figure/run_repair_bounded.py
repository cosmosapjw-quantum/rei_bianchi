#!/usr/bin/env python3
"""Authorized one-pass readability repair; adaptive 0.31 combined CPU ceiling.

Total reservation0.35 CPU seconds includes0.04 timer-granularity/receipt tail.
No retry. Existing attempt1 files are moved intact before any replacement.
"""
import json, resource, runpy, signal, sys, time
from pathlib import Path

root=Path(__file__).resolve().parents[1]
def usage():
    p=resource.getrusage(resource.RUSAGE_SELF);c=resource.getrusage(resource.RUSAGE_CHILDREN)
    return {'parent_cpu_s':p.ru_utime+p.ru_stime,'children_cpu_s':c.ru_utime+c.ru_stime,'combined_cpu_s':p.ru_utime+p.ru_stime+c.ru_utime+c.ru_stime}
def exhausted(signum,frame):raise TimeoutError('Readability repair adaptive combined CPU ceiling')
start=time.monotonic();status='FAILED';error=None
signal.signal(signal.SIGPROF,exhausted)
signal.setitimer(signal.ITIMER_PROF,max(.001,.30-usage()['parent_cpu_s']))
try:
    existing=root/'figures';prior=root/'outputs'/'attempt1_figures'
    if prior.exists():raise FileExistsError('attempt1 preservation destination exists; no overwrite')
    existing.rename(prior)
    sys.path.insert(0,str(root/'figure'))
    sys.argv=[str(root/'figure'/'build_figures.py'),str(root/'outputs'/'plot_data.json'),str(root/'figures')]
    runpy.run_path(sys.argv[0],run_name='__main__');status='REPAIRED_PENDING_REVIEW'
except BaseException as e:error=type(e).__name__+': '+str(e)
finally:
    signal.setitimer(signal.ITIMER_PROF,0)
    data={'status':status,'error':error,**usage(),'wall_s':time.monotonic()-start,'combined_ceiling_s':.31,'parent_prechild_ceiling_s':.30,'raster_child_ceiling':'max(0.001,0.30-parent CPU at launch)','total_reservation_s':.35,'tail_and_timer_granularity_reserve_s':.04,'retry':False,'initial_attempt':'outputs/attempt1_figures retained unchanged'}
    (root/'outputs'/'FIGURE_REPAIR_RESULT.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data))
if status!='REPAIRED_PENDING_REVIEW':sys.exit(1)
