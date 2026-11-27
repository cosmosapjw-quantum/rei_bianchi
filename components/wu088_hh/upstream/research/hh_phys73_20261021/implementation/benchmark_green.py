#!/usr/bin/env python3
"""Paired finite-payload dense/sweep timing, including all failed attempts."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import time
import numpy as np
from original_source import decode_output,sha,write_new

def benchmark(binary,input_path,out,workers=1,blocks=4,repeat=3):
    if not 1<=workers<=64 or not 2<=blocks<=12 or not 1<=repeat<=20:
        raise ValueError('workers1..64,blocks2..12,repeat1..20 required')
    binary,input_path,out=Path(binary).resolve(),Path(input_path).resolve(),Path(out).resolve()
    out.mkdir(parents=True,exist_ok=False)
    records=[];comparisons=[];first=None
    configs=[('dense_serial','dense',1),('sweep_serial','sweep',1),('sweep_parallel','sweep',workers)]
    env=dict(os.environ,HH_R10='OFF')
    for block in range(blocks):
        order=configs if block%2==0 else list(reversed(configs))
        block_results={}
        for label,mode,count in order:
            stem=f'block_{block:02d}_{label}'
            output=out/(stem+'.bin')
            command=[str(binary),str(input_path),str(output),'--mode',mode,'--workers',str(count),'--repeat',str(repeat)]
            started=time.perf_counter()
            proc=subprocess.run(command,capture_output=True,env=env,timeout=180)
            wall=time.perf_counter()-started
            (out/(stem+'.stdout.txt')).write_bytes(proc.stdout)
            (out/(stem+'.stderr.txt')).write_bytes(proc.stderr)
            record=dict(block=block,label=label,command=command,exit_code=proc.returncode,process_wall_seconds=wall,
                        stdout_sha256=sha(out/(stem+'.stdout.txt')),stderr_sha256=sha(out/(stem+'.stderr.txt')))
            records.append(record)
            if proc.returncode:
                write_new(out/'FAILED_ATTEMPTS.json',records)
                raise ArithmeticError('benchmark child failed; first output and failure preserved')
            native=json.loads(proc.stdout)
            if (native.get('mode')!=mode or native.get('repeat')!=repeat or native.get('workers_requested')!=count
                    or native.get('certified') is not False or native.get('HH_R10')!='OFF'):
                raise ValueError('native timing contract mismatch')
            array=decode_output(output)
            if first is None:first=array.copy()
            if array.shape!=first.shape:raise ValueError('native output shape changed')
            error=float(np.max(np.abs(array-first)))/max(float(np.max(np.abs(first))),np.finfo(float).tiny)
            if error>3e-12:raise ArithmeticError('dense/sweep finite matrix discrepancy exceeds fixed check')
            record.update(native=native,output_sha256=sha(output),max_relative_to_first=error)
            block_results[label]=(native,array.copy(),sha(output))
        if block_results['sweep_serial'][2]!=block_results['sweep_parallel'][2]:
            raise ArithmeticError('worker-count output differs bitwise')
        med={name:statistics.median(value[0]['kernel_seconds']) for name,value in block_results.items()}
        comparisons.append(dict(block=block,median_seconds=med,
                         dense_to_sweep_serial=med['dense_serial']/med['sweep_serial'],
                         dense_to_sweep_parallel=med['dense_serial']/med['sweep_parallel'],
                         serial_to_parallel_sweep=med['sweep_serial']/med['sweep_parallel'],
                         sweep_worker_bit_identity=True))
    report=dict(schema='PHYS73_MATCHED_FINITE_PAYLOAD_BENCHMARK_V1',status='PASS_SCOPED',certified=False,
                platform=platform.platform(),hostname=platform.node(),input_sha256=sha(input_path),
                binary_sha256=sha(binary),driver_sha256=sha(__file__),
                blocks=blocks,repetitions=repeat,records=records,paired=comparisons,
                paired_median_ratios={name:statistics.median(row[name] for row in comparisons)
                  for name in ('dense_to_sweep_serial','dense_to_sweep_parallel','serial_to_parallel_sweep')},
                maximum_finite_matrix_relative_difference=max(r['max_relative_to_first'] for r in records),
                timing_includes='native arithmetic and worker spawn/join; process wall also recorded',
                timing_excludes='Coulomb preparation, input parsing/output writes in native kernel seconds',
                NCP_speedup_claim=False,HH_R10='OFF')
    write_new(out/'REPORT.json',report)
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('binary','input','out'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--workers',type=int,default=1);p.add_argument('--blocks',type=int,default=4)
    p.add_argument('--repeat',type=int,default=3);a=p.parse_args()
    r=benchmark(a.binary,a.input,a.out,a.workers,a.blocks,a.repeat)
    print(json.dumps({k:r[k] for k in ('status','paired_median_ratios','maximum_finite_matrix_relative_difference')},indent=2))

if __name__=='__main__':main()
