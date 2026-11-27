#!/usr/bin/env python3
"""Reuse the recorded analytic/cache N5 packet for one sweep and dense action."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
from unittest.mock import patch

import mpmath as m
import numpy as np

REPO=Path('/tmp/phys73_fullclone')
IMPLEMENTATION=REPO/'research/hh_phys73_20261021/implementation'
sys.path.insert(0,str(IMPLEMENTATION))
import original_source as source

HERE=Path(__file__).resolve().parent
PREPARED=HERE/'fine_cached'
OUT=HERE/'integrated'
BINARY=Path('/tmp/phys73_runtime/green_batch')

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    OUT.mkdir()
    checked=json.loads((HERE/'CACHE_CHECK_RECEIPT.json').read_text())
    current=sha(IMPLEMENTATION/'original_source.py')
    if current!=checked['source_sha256_after']['original_source.py']:
        raise ValueError('preparation generator source changed after cache validation')
    packet=PREPARED/'SOURCE_GREEN.bin'
    packet_sha=sha(packet)
    binding={str(p):sha(p) for p in [packet,PREPARED/'GRID.npz',PREPARED/'PREPARED.json',
                IMPLEMENTATION/'original_source.py',IMPLEMENTATION/'coulomb_cache.py',
                IMPLEMENTATION/'analytic_screen_source.py',
                REPO/'research/hh_phys73_20261021/native/green_batch.rs',BINARY,Path(__file__)]}
    receipt=dict(schema='PHYS73_ANALYTIC_CACHE_NATIVE_INTEGRATION_V1',
                 started_utc=datetime.now(timezone.utc).isoformat(),
                 status='STARTED',inputs_sha256=binding,executions=[],
                 scope='reuse L1 radial N5 on [27,28] dps40 prepared analytic source packet',
                 new_Coulomb_evaluations=0,new_panel_integrations=0,new_profile_integrations=0,
                 certified=False,physical_matched_xi=False,HH_R10='OFF')
    start=time.perf_counter()
    try:
        outputs={}
        with patch.object(m,'coulombf',side_effect=AssertionError('unexpected F evaluation')) as ff, \
             patch.object(m,'coulombg',side_effect=AssertionError('unexpected G evaluation')) as gg:
            for mode in ('sweep','dense'):
                output=OUT/f'{mode.upper()}.bin'
                command=[str(BINARY),str(packet),str(output),'--workers','2','--mode',mode,'--repeat','1']
                begin=time.perf_counter()
                child=subprocess.run(command,env={**os.environ,'HH_R10':'OFF'},text=True,
                                     capture_output=True,timeout=10)
                elapsed=time.perf_counter()-begin
                (OUT/f'{mode}.stdout.txt').write_text(child.stdout)
                (OUT/f'{mode}.stderr.txt').write_text(child.stderr)
                entry=dict(command=command,exit_code=child.returncode,process_wall_seconds=elapsed)
                receipt['executions'].append(entry)
                if child.returncode:raise RuntimeError(mode+' native action failed')
                entry['native_report']=json.loads(child.stdout)
                entry['output_sha256']=sha(output)
                entry['production_summary']=source.summarize(PREPARED,output)
                outputs[mode]=source.decode_output(output)
            receipt['observed_F_calls']=ff.call_count
            receipt['observed_G_calls']=gg.call_count
            if ff.call_count or gg.call_count:raise AssertionError('new Coulomb evaluation')
        scale=max(float(np.max(np.abs(outputs['dense']))),np.finfo(float).tiny)
        absolute=float(np.max(np.abs(outputs['sweep']-outputs['dense'])))
        relative=absolute/scale
        receipt['same_packet_sweep_dense_difference']=dict(maximum_absolute=absolute,
             relative_to_max_dense=relative,threshold=3e-12,
             bit_identity=outputs['sweep'].tobytes()==outputs['dense'].tobytes())
        if relative>3e-12:raise AssertionError('same-packet sweep/dense difference')
        if sha(packet)!=packet_sha:raise AssertionError('input packet mutated')
        receipt['status']='PASS_FINITE_PACKET_INTEGRATION'
    except Exception:
        receipt['status']='FAIL'
        receipt['traceback']=traceback.format_exc()
    finally:
        receipt['elapsed_seconds']=time.perf_counter()-start
        receipt['inputs_unchanged']=all(sha(path)==digest for path,digest in binding.items())
        if not receipt['inputs_unchanged']:receipt['status']='FAIL_INPUT_CHANGED_DURING_CHECK'
        receipt['files_sha256']={p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file()}
        with (OUT/'INTEGRATED_PIPELINE_RECEIPT.json').open('x') as stream:
            json.dump(receipt,stream,indent=2,sort_keys=True,allow_nan=False)
            stream.write('\n')
    print(json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False))
    if receipt['status']!='PASS_FINITE_PACKET_INTEGRATION':raise SystemExit(1)

if __name__=='__main__':main()
