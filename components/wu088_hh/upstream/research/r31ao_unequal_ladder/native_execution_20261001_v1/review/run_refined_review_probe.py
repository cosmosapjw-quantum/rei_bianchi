"""Build and execute one independent probe with bounded resources and byte evidence."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import subprocess
import time

HERE=Path(__file__).resolve().parent
LADDER=HERE.parents[1]
OLD=LADDER/'gap_closure_20261001_g0_g6_v1'
FLAGS=['-std=c++17','-O3','-fno-fast-math','-fno-associative-math',
       '-fno-unsafe-math-optimizations','-ffp-contract=off','-Wall','-Wextra','-Werror=return-type']


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path,value):
    with Path(path).open('x') as stream:
        json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')


def limits():
    resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    resource.setrlimit(resource.RLIMIT_FSIZE,(16*1024**2,16*1024**2))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--prefix',type=Path,required=True)
    parser.add_argument('--provenance',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--mode',choices=['refined'],required=True)
    args=parser.parse_args()
    prefix=args.prefix.resolve();provenance=args.provenance.resolve();out=args.out.resolve()
    out.mkdir(parents=False,exist_ok=False)
    gatepath=LADDER/'host_synthetic_readiness_20261001_v1/provenance_gate.py'
    spec=importlib.util.spec_from_file_location('review_backend_gate',gatepath)
    gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
    backend=gate.verify_backend(provenance,prefix)
    env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','LD_LIBRARY_PATH':str(prefix/'lib'),
         'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
    if args.mode=='cache':
        source=HERE/'actual_callback_cache_probe.cpp'
        sources=[source,LADDER/'ncp64_acceleration_20261001_v1/native_cache/cached_callback.cpp',
                 OLD/'validated_callback/assembly.cpp']
    else:
        source=HERE/'refined_interval_probe.cpp'
        sources=[source,OLD/'validated_callback/callback.cpp',HERE.parent/'refining_petras.cpp']
    bound=sources+[OLD/'validated_callback/callback.cpp',OLD/'validated_callback/callback.hpp',
                   OLD/'validated_callback/assembly.hpp',OLD/'interior_pilot/petras_host.hpp',
                   HERE/'generated_input/frozen107_generated.hpp',gatepath,Path(__file__)]
    if args.mode=='cache': bound.append(LADDER/'ncp64_acceleration_20261001_v1/native_cache/cached_callback.hpp')
    identities={str(p.relative_to(LADDER)):sha(p) for p in bound}
    binary=out/'probe'
    command=['/usr/bin/g++',*FLAGS,'-I'+str(prefix/'include'),'-I'+str(HERE/'generated_input'),
             '-I'+str(OLD/'validated_callback'),*[str(p) for p in sources],
             '-L'+str(prefix/'lib'),'-Wl,-rpath,'+str(prefix/'lib'),'-lflint','-lmpfr','-lgmp','-o',str(binary)]
    record={'mode':args.mode,'command':command,'flags':FLAGS,'source_sha256':identities,
            'backend_provenance_sha256':sha(provenance),'backend_status':backend['verification']['status'],
            'compiler':gate.file_identity(Path('/usr/bin/g++').resolve()),
            'compiler_version':subprocess.check_output(['/usr/bin/g++','--version'],text=True),
            'affinity':sorted(os.sched_getaffinity(0)),'memory_cap_bytes':1024**3,'wall_cap_seconds':120,
            'scientific_admission':False,'production_admission':False}
    start=time.monotonic_ns()
    with (out/'compile.stdout').open('xb') as stdout,(out/'compile.stderr').open('xb') as stderr:
        build=subprocess.run(command,stdout=stdout,stderr=stderr,env=env,timeout=120,preexec_fn=limits)
    record['build_returncode']=build.returncode;record['build_nanoseconds']=time.monotonic_ns()-start
    if build.returncode:
        save(out/'REVIEW_RUN.json',record);raise SystemExit(build.returncode)
    record['binary_sha256']=sha(binary)
    ldd=subprocess.check_output(['/usr/bin/ldd',str(binary)],env=env,text=True,timeout=15)
    (out/'linkage.log').write_text(ldd)
    record['linkage']=gate.verify_linkage(ldd,{name:item['binary_path'] for name,item in backend['libraries'].items()})
    gate.verify_backend(provenance,prefix)
    start=time.monotonic_ns()
    with (out/'run.stdout').open('xb') as stdout,(out/'run.stderr').open('xb') as stderr:
        run=subprocess.run([str(binary)],stdout=stdout,stderr=stderr,env=env,timeout=120,preexec_fn=limits)
    record['run_returncode']=run.returncode;record['run_nanoseconds']=time.monotonic_ns()-start
    record['run_stdout_sha256']=sha(out/'run.stdout');record['run_stderr_sha256']=sha(out/'run.stderr')
    try: record['result']=json.loads((out/'run.stdout').read_text())
    except json.JSONDecodeError: record['result']=None
    record['source_bytes_unchanged']=identities=={str(p.relative_to(LADDER)):sha(p) for p in bound}
    record['backend_unchanged_after']=gate.verify_backend(provenance,prefix)['verification']['status']=='BYTE_CHAIN_VERIFIED'
    save(out/'REVIEW_RUN.json',record)
    result=record.get('result') or {}
    print(json.dumps({'mode':args.mode,'run_returncode':run.returncode,'result_status':result.get('status'),
                      'unique_callback_cases':result.get('unique_callback_cases'),
                      'paired_comparisons':result.get('paired_comparisons'),
                      'refined_enclosure_matches_analytic_and_direct':result.get('refined_enclosure_matches_analytic_and_direct'),
                      'run_nanoseconds':record['run_nanoseconds']}),flush=True)
    raise SystemExit(run.returncode)


if __name__=='__main__':main()
