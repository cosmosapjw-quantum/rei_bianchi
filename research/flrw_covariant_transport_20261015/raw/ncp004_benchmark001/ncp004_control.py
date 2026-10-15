#!/usr/bin/env python3
"""Fresh immutable stage003 build and finite parity/scaling measurement only."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time

TASK = Path('/root/REI_FLRW_COVARIANT_20261015_004')
STAGE = TASK / 'stage'
TC = Path('/root/REI_AXBI_GOAL_20261014_32d11e733155/performance/temperature_rate_table_001/ncp_validation_001/toolchain')
BINARY = TASK / 'target/release/examples/axbi_reionization'
BENCHMARK = TASK / 'target/release/examples/axbi_background_cache'
FIXTURE = Path('/root/REI_FLRW_COVARIANT_20261015_002/runs/FLRW_SPLIT_PILOT_Q128_001')
MEMORY = 8 * 1024**3
OUTPUT = 256 * 1024**2

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write_new(p, obj):
    with p.open('x') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')

def environment():
    env = os.environ.copy()
    env.update(RUSTC=str(TC/'bin/rustc'), RUSTDOC=str(TC/'bin/rustdoc'),
               LD_LIBRARY_PATH=str(TC/'lib'), CARGO_TARGET_DIR=str(TASK/'target'),
               CARGO_BUILD_JOBS='8', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1',
               MKL_NUM_THREADS='1', RAYON_NUM_THREADS='1')
    return env

def verify_source():
    for line in (STAGE/'SOURCE_SHA256SUMS.txt').read_text().splitlines():
        expected, relative = line.split('  ', 1)
        if sha(STAGE/relative) != expected:
            raise RuntimeError('staged source byte identity mismatch: '+relative)

def source_identity():
    driver = STAGE/'rust/rei_microphysics/src/axbi_driver.rs'
    body = driver.read_text().split('pub fn compiled_identity() -> String {',1)[1].split('fn ledger_values',1)[0]
    inputs = re.findall(r'include_str!\(\s*"([^"]+)"\s*\)',body)
    return '\nAXBI_SOURCE_BOUNDARY\n'.join((driver.parent/p).read_text() for p in inputs).encode()

def build():
    verify_source()
    command = ['taskset','-c','0-7','prlimit',f'--as={MEMORY}','--',str(TC/'bin/cargo'),
               'build','--release','--locked','--offline','--manifest-path',
               str(STAGE/'rust/rei_microphysics/Cargo.toml'),'--example','axbi_reionization',
               '--example','axbi_background_cache']
    started = time.monotonic()
    with (TASK/'build.log').open('x') as log:
        result = subprocess.run(command,env=environment(),stdout=log,stderr=subprocess.STDOUT,timeout=180)
    receipt = dict(command=command,returncode=result.returncode,wall_s=time.monotonic()-started,
                   source_identity_sha256=hashlib.sha256(source_identity()).hexdigest(),
                   binary_sha256=sha(BINARY) if BINARY.exists() else None,
                   benchmark_binary_sha256=sha(BENCHMARK) if BENCHMARK.exists() else None,
                   source_manifest_sha256=sha(STAGE/'SOURCE_SHA256SUMS.txt'))
    write_new(TASK/'build_receipt.json',receipt)
    print(json.dumps(receipt),flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)

def directory_bytes(root):
    total = 0
    for p in root.rglob('*'):
        try:
            if p.is_file(): total += p.stat().st_size
        except FileNotFoundError:
            pass
    return total

def process_sample(pid):
    """Process CPU totals already include all pthreads, never add task totals."""
    pending, ticks, rss, threads, pids = [pid], 0, 0, 0, []
    while pending:
        p = pending.pop()
        try:
            stat = Path(f'/proc/{p}/stat').read_text().rsplit(')',1)[1].split()
            ticks += int(stat[11])+int(stat[12])
            threads += int(stat[17])
            rss += int(stat[21])*os.sysconf('SC_PAGE_SIZE')
            pids.append(p)
            pending.extend(map(int,Path(f'/proc/{p}/task/{p}/children').read_text().split()))
        except (FileNotFoundError,ProcessLookupError):
            pass
    return dict(cpu_ticks=ticks,cpu_s=ticks/os.sysconf('SC_CLK_TCK'),rss_bytes=rss,
                os_threads=threads,pids=pids)

def benchmark():
    verify_source()
    built = json.loads((TASK/'build_receipt.json').read_text())
    identity = source_identity()
    if built['returncode'] or built['benchmark_binary_sha256']!=sha(BENCHMARK) or built['source_identity_sha256']!=hashlib.sha256(identity).hexdigest():
        raise RuntimeError('benchmark source/build binding mismatch')
    cfg = FIXTURE/'config.cfg'
    checkpoint = FIXTURE/'checkpoints/00004080.txt'
    if sha(checkpoint)!='f092e606727ad25ac8bc9819e77aee6ae2e2a622590de6b1e401983ec16404df':
        raise RuntimeError('immutable fixture mismatch')
    if sha(cfg)!='e358acb6930a0a230b4ffd4556609f3865b04794ff463d0a131b801e0b636874':
        raise RuntimeError('immutable fixture config mismatch')
    out = TASK/'benchmark001'
    if out.exists(): raise RuntimeError('fresh diagnostic output required')
    command = ['timeout','--signal=TERM','--kill-after=5s','55s','taskset','-c','0-7',
               'prlimit',f'--as={MEMORY}',f'--fsize={OUTPUT}','--',str(BENCHMARK),str(cfg),str(checkpoint),str(out)]
    write_new(TASK/'benchmark_binding.json',dict(command=command,source_identity_sha256=built['source_identity_sha256'],
        binary_sha256=sha(BENCHMARK),fixture_sha256=sha(checkpoint),config_sha256=sha(cfg),
        fixture_role='EXPERIMENT_INITIALSTATE_NOT_PRODUCTION_RESUME',logical_cpus=list(range(8)),
        cache_modes=[0,1],transport_threads=8,memory_cap_bytes=MEMORY,output_cap_bytes=OUTPUT,
        wall_cap_s=60,clock_ticks_per_s=os.sysconf('SC_CLK_TCK'),utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
    started = time.monotonic()
    peak = 0
    stop_reason = None
    samples = []
    with (TASK/'benchmark.log').open('x') as log, (TASK/'benchmark_telemetry.jsonl').open('x') as telemetry:
        proc = subprocess.Popen(command,env=environment(),stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        print(json.dumps(dict(status='BENCHMARK_LAUNCHED',pid=proc.pid,controller_pid=os.getpid(),task=str(TASK))),flush=True)
        usage = None
        while True:
            finished, status, ru = os.wait4(proc.pid, os.WNOHANG)
            if finished:
                proc.returncode = os.waitstatus_to_exitcode(status)
                usage = ru
                break
            elapsed = time.monotonic()-started
            sample = process_sample(proc.pid)
            sample['wall_s']=elapsed
            sample['output_bytes']=directory_bytes(out) if out.exists() else 0
            peak=max(peak,sample['rss_bytes'])
            samples.append(sample)
            telemetry.write(json.dumps(sample)+'\n');telemetry.flush()
            if elapsed>=60 or sample['output_bytes']>=OUTPUT:
                stop_reason='EXTERNAL_WALL_CAP' if elapsed>=60 else 'OUTPUT_CAP'
                os.killpg(proc.pid,signal.SIGTERM)
                try: proc.wait(timeout=10)
                except subprocess.TimeoutExpired: os.killpg(proc.pid,signal.SIGKILL)
                break
            time.sleep(.1)
        code=proc.wait()
    summary=json.loads((out/'summary.json').read_text()) if (out/'summary.json').exists() else None
    receipt=dict(returncode=code,stop_reason=stop_reason,wall_s=time.monotonic()-started,
        peak_process_tree_rss_bytes=peak,observed_cpu_s=max((s['cpu_s'] for s in samples),default=0),
        sample_count=len(samples),output_bytes=directory_bytes(out) if out.exists() else 0,
        source_identity_readback_equal=(out/'source_identity.txt').exists() and (out/'source_identity.txt').read_bytes()==identity,
        config_readback_equal=(out/'input_config.cfg').exists() and (out/'input_config.cfg').read_bytes()==cfg.read_bytes(),
        checkpoint_readback_equal=(out/'input_checkpoint.txt').exists() and (out/'input_checkpoint.txt').read_bytes()==checkpoint.read_bytes(),
        summary=summary, process_cpu_s_exact_wait4=None if usage is None else usage.ru_utime+usage.ru_stime, peak_rss_bytes_wait4=None if usage is None else usage.ru_maxrss*1024)
    write_new(TASK/'benchmark_receipt.json',receipt)
    print(json.dumps(receipt),flush=True)
    if code or stop_reason or not all(receipt[k] for k in ['source_identity_readback_equal','config_readback_equal','checkpoint_readback_equal']):
        raise SystemExit(code or 1)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['build','benchmark'])
    args=parser.parse_args()
    build() if args.action=='build' else benchmark()
