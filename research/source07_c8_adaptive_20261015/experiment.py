#!/usr/bin/env python3
"""Adaptive order selection without age pooling, C8 limited oracle test."""
import json,time,sys,types
from pathlib import Path
base=Path(__file__).resolve().parents[1]/'source07_c8_quadrature_20261015/compare.py'
code=base.read_text().split('\nrows=[]\n')[0]
ns={'__file__':str(base),'__name__':'c8_reference'}
exec(compile(code,str(base),'exec'),ns)
import numpy as np
calc=ns['calc']
rows=[]
for q in (-.01,0.,.01):
    truth=calc(q,'quad',0)
    baseline=time.perf_counter(); _=calc(q,'quad',0); tbase=time.perf_counter()-baseline
    prev=None; chosen=None
    for order in (4,8,16,32):
        start=time.perf_counter(); value=calc(q,'gauss',order); elapsed=time.perf_counter()-start
        norm=np.maximum(np.abs(value),1e-30)
        metric=float(np.max(np.abs(value[[0,1,3]]-prev[[0,1,3]])/norm[[0,1,3]])) if prev is not None else None
        actual=float(np.max(np.abs(value[[0,1,3]]-truth[[0,1,3]])/np.maximum(np.abs(truth[[0,1,3]]),1e-30)))
        rows.append({'q':q,'order':order,'successive_estimate':metric,'reference_error_max':actual,'time_sec':elapsed,'quad_time_sec':tbase})
        if metric is not None and metric<1e-8:
            chosen=order;break
        prev=value
    assert chosen is not None
    assert rows[-1]['reference_error_max']<1e-8
    print('q',q,'selected',chosen,'actual error',rows[-1]['reference_error_max'],'elapsed',rows[-1]['time_sec'],'baseline',tbase,flush=True)
Path(__file__).with_name('results.json').write_text(json.dumps(rows,indent=2)+'\n')
