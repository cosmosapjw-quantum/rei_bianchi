"""First NCP saved-data Rust gate build/run; no native source callback routes.

READY_NOT_RUN in PHYS08 research host (rustc absent). Invoke once on NCP.
Every stage writes raw output before status; no automatic retries or installs.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]


def now():
    return datetime.now(timezone.utc).isoformat()


def identity(path):
    p=Path(path)
    b=p.read_bytes()
    return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}


def emit(path, obj):
    with Path(path).open('x') as f:
        json.dump(obj,f,indent=2,allow_nan=False)
        f.write('\n')


def command(dest, argv, wall, memory):
    dest.mkdir(exist_ok=False)
    before=resource.getrusage(resource.RUSAGE_CHILDREN)
    started=now(); tick=time.monotonic(); timeout=False
    def limits():
        resource.setrlimit(resource.RLIMIT_AS,(memory*1024**2,)*2)
        resource.setrlimit(resource.RLIMIT_FSIZE,(8*1024**2,)*2)
        resource.setrlimit(resource.RLIMIT_CPU,(wall,)*2)
    with (dest/'stdout.txt').open('xb') as out,(dest/'stderr.txt').open('xb') as err:
        try:
            p=subprocess.run(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=out,stderr=err,
                timeout=wall,preexec_fn=limits,
                env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','RAYON_NUM_THREADS':'1'})
            exit_code=p.returncode
        except subprocess.TimeoutExpired:
            exit_code=124; timeout=True
        except OSError as exc:
            err.write((type(exc).__name__+': '+str(exc)+'\n').encode())
            exit_code=127
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    record={'argv':argv,'cwd':str(ROOT),'started_utc':started,'finished_utc':now(),
       'elapsed_seconds':time.monotonic()-tick,'exit_code':exit_code,'timeout':timeout,
       'limits':{'wall_seconds':wall,'address_space_MiB':memory,'output_MiB_each':8},
       'child_user_seconds_delta':after.ru_utime-before.ru_utime,
       'child_system_seconds_delta':after.ru_stime-before.ru_stime,
       'cumulative_child_maxrss_KiB_linux':after.ru_maxrss,
       'logs':[identity(dest/'stdout.txt'),identity(dest/'stderr.txt')]}
    emit(dest/'EXECUTION.json',record)
    return record


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--run-dir',required=True)
    a=p.parse_args()
    dest=Path(a.run_dir).expanduser().resolve()
    dest.mkdir(parents=True,exist_ok=False)
    bound=[ROOT/n for n in (
        'src/weighted_gate.rs','tests/weighted_gate_tests.rs','src/exact_weighted.py',
        'diagnostics/check_rust_output.py','tools/run_ncp_weighted.py',
        'results/weighted_corrected/GATE_INPUTS.tsv','results/weighted_corrected/GOLDEN_ORACLE.json',
        'results/weighted_corrected/WEIGHTED_RESULTS.json','SCIENTIFIC_CONTRACT.md','NCP_TASKS.json')]
    before=[identity(f) for f in bound]
    rustc=shutil.which('rustc')
    host={'created_utc':now(),'platform':platform.platform(),'machine':platform.machine(),
          'python':sys.version,'rustc_path':rustc,'cpu_affinity':sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else None,
          'inherited_RUSTFLAGS':os.environ.get('RUSTFLAGS'),
          'scope':'Only dependency-free rustc invocation and saved scalar-fixture gate; no Cargo/source/provider/solver.'}
    emit(dest/'HOST.json',host)
    records=[]; binary=dest/'weighted_gate_tests'; blocker=None
    if rustc is None:
        blocker='RUSTC_NOT_AVAILABLE_NO_INSTALL_ATTEMPT'
    else:
        records.append(command(dest/'compiler_identity',[rustc,'-vV'],10,512))
        if records[-1]['exit_code']!=0:
            blocker='COMPILER_IDENTITY_FAILED'
        else:
            records.append(command(dest/'build_first',[rustc,'--edition=2021','-C','opt-level=0',
                '-C','codegen-units=1','-C','overflow-checks=yes',
                str(ROOT/'tests/weighted_gate_tests.rs'),'-o',str(binary)],60,512))
            if records[-1]['exit_code']!=0:
                blocker='BUILD_FIRST_FAILED_PRESERVE_NO_AUTO_RETRY'
    binary_before=None
    if blocker is None:
        binary_before=identity(binary)
        records.append(command(dest/'gate_first',[str(binary),'--vectors',
            str(ROOT/'results/weighted_corrected/GATE_INPUTS.tsv')],10,128))
        if records[-1]['exit_code']!=0:
            blocker='GATE_FIRST_FAILED_PRESERVE_NO_AUTO_RETRY'
    if blocker is None:
        records.append(command(dest/'consumer_first',[sys.executable,str(ROOT/'diagnostics/check_rust_output.py'),
            '--oracle',str(ROOT/'results/weighted_corrected/GOLDEN_ORACLE.json'),
            '--output',str(dest/'gate_first/stdout.txt'),
            '--report',str(dest/'ORACLE_CHECK.json')],10,128))
        if records[-1]['exit_code']!=0:
            blocker='ORACLE_CONSUMER_FAILED_PRESERVE_NO_AUTO_RETRY'
    after=[identity(f) for f in bound]
    binary_after=identity(binary) if binary_before is not None else None
    if before!=after or binary_before!=binary_after:
        blocker='SOURCE_INPUT_OR_BINARY_MUTATED'
    if blocker is None:
        oraclecheck=json.loads((dest/'ORACLE_CHECK.json').read_text())
        if oraclecheck.get('status')!='PASS_SCOPED_OUTPUT_CONTAINMENT':
            raise ValueError('CONSUMER_EXIT_STATUS_CONFLICT')
        results=json.loads((ROOT/'results/weighted_corrected/WEIGHTED_RESULTS.json').read_text())
        gate_rows=[json.loads(s) for s in (dest/'gate_first/stdout.txt').read_text().splitlines() if s.strip()]
        gate_by_id={r['case_id']:r for r in gate_rows if r.get('kind')=='gate'}
        sidecar={'schema':'WU088_HH_PHYS08_NCP_ARCHIVED_WEIGHTED_SIDECAR_V1',
            'status':'RUST_SAVED_SCALAR_GATE_VALIDATED','created_utc':now(),
            'aggregation_authority':'PHYS08 exact rational consumer of archived signed NCP07 photo rate Jets',
            'gate_execution_authority':'This NCP binary on prebound scalar interval fixtures',
            'fresh_native_source_execution':False,'native_implicit_authority':False,
            'rows':[{'stage':s['stage'],'role':role,'source_input_identities':s['source_input_identities'],
                     'rust_gate':gate_by_id[s['stage']+'_'+role]}
                    for s in results['source_stages'] for role in ('P_N','P_M')],
            'oracle_check_identity':identity(dest/'ORACLE_CHECK.json'),
            'open':['native root','U/V/W/I','finite energy interaction','carried half','paired defect','time/continuum','full49','production']}
        emit(dest/'WEIGHTED_SOURCE_SIDECAR.json',sidecar)
    final={'schema':'WU088_HH_PHYS08_NCP_SAVED_GATE_RUN_V1',
        'status':'PASS_SCOPED' if blocker is None else 'BLOCKED','blocker':blocker,
        'created_utc':now(),'records':records,'source_inputs_before':before,'source_inputs_after':after,
        'source_inputs_unchanged':before==after,'binary_before':binary_before,'binary_after':binary_after,
        'rust_build_invocations':sum(any(str(x).endswith('weighted_gate_tests.rs') for x in r['argv']) for r in records),
        'fresh_source_routes_in_this_wrapper':0,'source_counter_basis':'No source bindings or commands; native source producer and inherited solver counters are not sampled.',
        'native_implicit_authority':False,'automatic_retry':False}
    emit(dest/'NCP_RUN.json',final)
    print(json.dumps({'status':final['status'],'blocker':blocker,'run_dir':str(dest)}))
    return 0 if blocker is None else 1


if __name__=='__main__':
    sys.exit(main())
