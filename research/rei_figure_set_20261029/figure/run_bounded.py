#!/usr/bin/env python3
"""Single no-retry rendering attempt, 0.85 CPU-s self ceiling including startup.

Controller must account actual rusage (including this wrapper) against the
existing cumulative ledger. This script does not grant or reset any budget.
"""
import json, os, resource, runpy, signal, sys, time
from pathlib import Path

def cpu():
    u=resource.getrusage(resource.RUSAGE_SELF);return u.ru_utime+u.ru_stime

root=Path(__file__).resolve().parents[1]
receipt=root/'outputs'/'FIGURE_ATTEMPT_RESULT.json'
start=time.monotonic();status='FAILED';error=None
def exhausted(signum,frame):raise TimeoutError('0.85 CPU-second renderer process ceiling')
signal.signal(signal.SIGPROF,exhausted)
signal.setitimer(signal.ITIMER_PROF,max(.001,.85-cpu()))
try:
    sys.path.insert(0,str(root/'figure'))
    sys.argv=[str(root/'figure'/'build_figures.py'),str(root/'outputs'/'plot_data.json'),str(root/'figures')]
    runpy.run_path(sys.argv[0],run_name='__main__');status='WRITTEN_PENDING_REVIEW'
except BaseException as e:
    error=type(e).__name__+': '+str(e)
finally:
    signal.setitimer(signal.ITIMER_PROF,0)
    data={'status':status,'error':error,'renderer_process_cpu_before_receipt_s':cpu(),'wall_before_receipt_s':time.monotonic()-start,'ceiling_s':.85,'receipt_tail_cpu':'UNKNOWN_NOT_ZERO; controller external rusage is final','retry':False}
    receipt.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data))
if status!='WRITTEN_PENDING_REVIEW':sys.exit(1)
