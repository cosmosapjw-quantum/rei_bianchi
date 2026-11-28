"""Create-only GNU/OpenMPI build with explicit wrapper-file pins and receipts."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import resource
import signal
import shlex
import shutil
import subprocess
import time

HERE=Path(__file__).resolve().parent


class Refusal(ValueError):pass


def identity(path):
    p=Path(path)
    if not p.is_file() or p.stat().st_size>64*1024*1024:
        raise Refusal('bounded regular tool/source file required')
    h=hashlib.sha256();total=0
    with p.open('rb') as f:
        for data in iter(lambda:f.read(65536),b''):
            total+=len(data)
            if total>64*1024*1024:raise Refusal('identity file grew beyond cap')
            h.update(data)
    return {'invocation_path':str(p.absolute()),'resolved_path':str(p.resolve()),
            'bytes':p.stat().st_size,'sha256':h.hexdigest()}


def command(argv,output,label,receipt,timeout=60):
    # The compiler/wrapper is an explicitly pinned trusted local tool. No shell.
    start=time.monotonic()
    path=output/(label+'.log')
    def limits():resource.setrlimit(resource.RLIMIT_FSIZE,(8*1024*1024,8*1024*1024))
    timed_out=False;leftover=False
    with path.open('xb') as log:
        p=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,
                           cwd=output,env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1'),preexec_fn=limits)
        try:
            try:p.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out=True
                try:os.killpg(p.pid,signal.SIGTERM)
                except ProcessLookupError:pass
                try:p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    try:os.killpg(p.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    p.wait()
        finally:
            try:
                os.killpg(p.pid,0);leftover=True;os.killpg(p.pid,signal.SIGKILL)
            except ProcessLookupError:pass
    if path.stat().st_size>8*1024*1024:raise Refusal('tool log exceeded 8 MiB')
    text=path.read_text(errors='replace')
    receipt['commands'].append({'argv':argv,'exit_code':p.returncode,'timed_out':timed_out,'remaining_group_killed':leftover,
                               'seconds':time.monotonic()-start,'log':path.name})
    if p.returncode or timed_out or leftover:raise Refusal('tool failed/timed out/left group: '+label)
    return text


def build(args):
    output=args.output_dir
    if not output.is_absolute() or output.exists() or output.is_symlink() or not output.parent.is_dir():
        raise Refusal('absolute create-only build directory under an existing parent required')
    output.mkdir(mode=0o700)
    receipt={'schema':'WU088_MPI_FORTRAN_BUILD_V1','status':'INCOMPLETE','commands':[],
             'platform':platform.platform(),'python':platform.python_version(),
             'Fortran_compiled':False,'MPI_executed':False,'scientific_execution':False,
             'production_admitted':False,'independent_review_admitted':False}
    try:
        tools={key:getattr(args,key) or shutil.which(key) for key in ('mpifort','mpicc')}
        missing=[key for key,path in tools.items() if not path]
        if missing:raise Refusal('MISSING_TOOLCHAIN: '+','.join(missing))
        receipt['wrappers']={}
        for key,path in tools.items():
            if not Path(path).is_absolute():raise Refusal('absolute wrapper path required')
            pin=getattr(args,key+'_sha256')
            if not pin or not re.fullmatch('[0-9a-f]{64}',pin):raise Refusal('explicit wrapper SHA256 pin required: '+key)
            record=identity(path)
            if record['sha256']!=pin:raise Refusal('wrapper pin mismatch: '+key)
            version=command([path,'--showme:version'],output,key+'_mpi_version',receipt)
            if 'Open MPI' not in version:raise Refusal('OpenMPI wrapper required')
            record['openmpi_version']=version
            for option in ('command','compile','link'):
                record['showme_'+option]=command([path,'--showme:'+option],output,key+'_'+option,receipt)
            underlying=shlex.split(record['showme_command'])
            if len(underlying)!=1:raise Refusal('one direct compiler command required; compiler launch wrappers are not admitted')
            compiler=shutil.which(underlying[0])
            if compiler is None:raise Refusal('configured compiler absent')
            record['configured_compiler']=identity(compiler)
            record['compiler_version']=command([compiler,'--version'],output,key+'_compiler_version',receipt)
            if key=='mpifort' and 'GNU Fortran' not in record['compiler_version']:
                raise Refusal('GNU Fortran required for selected SIMD/vector-report flags')
            receipt['wrappers'][key]=record
        sources={name:identity(HERE/name) for name in ('dispatcher.f90','worker_spawn.c','worker_spawn.h')}
        receipt['sources']=sources
        common=['-O3','-fno-fast-math','-ffp-contract=off']
        command([tools['mpicc'],'-std=c11',*common,'-Wall','-Wextra','-Werror','-pedantic',
                 '-c',str(HERE/'worker_spawn.c'),'-o',str(output/'worker_spawn.o')],output,'compile_c',receipt)
        command([tools['mpifort'],*common,'-Wall','-Wextra','-fopenmp-simd','-ffree-line-length-none',
                 '-fopt-info-vec-all='+str(output/'integer_vectorization.txt'),'-J'+str(output),
                 str(HERE/'dispatcher.f90'),str(output/'worker_spawn.o'),'-o',str(output/'ncp64_dispatch')],
                output,'compile_fortran_link',receipt)
        for name,record in sources.items():
            if identity(HERE/name)['sha256']!=record['sha256']:raise Refusal('source changed during build')
        for key,path in tools.items():
            if identity(path)['sha256']!=receipt['wrappers'][key]['sha256']:raise Refusal('wrapper changed during build')
        receipt.update(status='BUILT_NOT_MPI_RUNTIME_VERIFIED',Fortran_compiled=True,
                       binary=identity(output/'ncp64_dispatch'),
                       vectorization_report=str(output/'integer_vectorization.txt'),
                       scientific_simd_claim=False,
                       pin_scope='wrapper file bytes pinned; compiler files/configuration captured; no claim of a fully pinned compiler dependency closure')
    except (Refusal,OSError,subprocess.TimeoutExpired) as exc:
        receipt['status']='REFUSED_OR_BUILD_FAILED';receipt['reason']=str(exc)
    (output/'BUILD.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',type=Path,required=True)
    for key in ('mpifort','mpicc'):
        p.add_argument('--'+key);p.add_argument('--'+key+'-sha256')
    args=p.parse_args()
    try:r=build(args)
    except (OSError,Refusal) as exc:p.exit(2,'REFUSED: '+str(exc)+'\n')
    print(json.dumps(r,indent=2))
    return 0 if r['status']=='BUILT_NOT_MPI_RUNTIME_VERIFIED' else 2


if __name__=='__main__':raise SystemExit(main())
