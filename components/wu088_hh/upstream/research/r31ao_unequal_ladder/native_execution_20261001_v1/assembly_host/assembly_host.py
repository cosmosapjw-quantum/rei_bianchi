"""Guarded final assembly build/run; conditional arithmetic, never promotion.

Consumes complete joined primitive coverage and verified preparation bytes.
There is no facility to manufacture coverage or reuse partial native output.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import resource
import signal
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
LADDER=HERE.parents[1]
PRODUCTION=LADDER/'production_solver_20261001_v1'
OLD=LADDER/'gap_closure_20261001_g0_g6_v1'
MAX_JSON=32*1024*1024
BUILD_LIMITS={'wall_seconds':300,'memory_mib':4096,'file_bytes':64*1024*1024}
RUN_LIMITS={'wall_seconds':60,'memory_mib':2048,'file_bytes':16*1024*1024,'precision_bits':128}


class HostError(ValueError): pass


class ChildFailure(HostError):
    def __init__(self,report):
        self.process_report=report
        super().__init__('hard wall deadline exceeded' if report['timed_out'] else 'child exited unsuccessfully: '+str(report['exit_code']))


def canonical(obj):
    try:return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')
    except (TypeError,ValueError,RecursionError) as exc:raise HostError('finite JSON required') from exc


def digest(data):return hashlib.sha256(data).hexdigest()
def sha(value):
    if type(value) is not str or not re.fullmatch('[0-9a-f]{64}',value):raise HostError('explicit lowercase SHA256 required')
    return value


def read_bytes(path,maximum=MAX_JSON):
    path=Path(path)
    if not path.is_file() or path.stat().st_size>maximum:raise HostError('bounded regular file required: '+str(path))
    with path.open('rb') as stream:data=stream.read(maximum+1)
    if len(data)>maximum:raise HostError('file grew beyond byte cap')
    return data


def parse_json(data):
    if type(data) is not bytes or len(data)>MAX_JSON:raise HostError('JSON byte cap')
    def pairs(values):
        out={}
        for key,value in values:
            if key in out:raise HostError('duplicate JSON key')
            out[key]=value
        return out
    def refuse(_):raise HostError('JSON float/nonfinite forbidden')
    try:return json.loads(data,object_pairs_hook=pairs,parse_float=refuse,parse_constant=refuse)
    except (ValueError,UnicodeError,RecursionError) as exc:raise HostError('invalid exact JSON') from exc


def read_json(path):return parse_json(read_bytes(path))
def write_new(path,obj):
    data=canonical(obj)+b'\n'
    if len(data)>MAX_JSON:raise HostError('JSON output byte cap')
    with Path(path).open('xb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())


def identity(path,maximum=64*1024*1024):
    path=Path(path).resolve(strict=True);data=read_bytes(path,maximum)
    return {'path':str(path),'size':len(data),'sha256':digest(data)}


def exact_keys(obj,names):
    if type(obj) is not dict or set(obj)!=set(names):raise HostError('missing/extra contract keys')


def sealed(obj,field,expected):
    if obj.get(field)!=sha(expected) or digest(canonical({k:v for k,v in obj.items() if k!=field}))!=expected:
        raise HostError('canonical identity mismatch: '+field)


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);obj=importlib.util.module_from_spec(spec)
    sys.modules[name]=obj;prior=sys.dont_write_bytecode;sys.dont_write_bytecode=True
    try:spec.loader.exec_module(obj)
    finally:sys.dont_write_bytecode=prior
    return obj


def verify_sources():
    pins=read_json(HERE/'dependency_pins.json')
    exact_keys(pins,('schema','files'))
    if pins['schema']!='WU088_ASSEMBLY_HOST_PINS_V1':raise HostError('source pin schema')
    for relative,wanted in pins['files'].items():
        path=(LADDER/relative).resolve()
        if not path.is_relative_to(LADDER) or digest(read_bytes(path))!=sha(wanted):raise HostError('immutable dependency changed: '+relative)
    return pins


def configured_modules(driver_module=None,driver_sha256=None):
    verify_sources()
    join=load_module('_wu088_guarded_assembly_join',PRODUCTION/'primitive_join/join.py')
    override=None
    if driver_module is not None:
        path=Path(driver_module).resolve(strict=True)
        if not path.is_relative_to(LADDER) or digest(read_bytes(path))!=sha(driver_sha256):raise HostError('driver override path/hash mismatch')
        join.native=load_module('_wu088_guarded_assembly_driver_override',path)
        for name in ('FLAGS','DEFAULT_LIMITS','source_identity','limits_checked','dyadic_interval'):
            if not hasattr(join.native,name):raise HostError('driver override lacks required interface: '+name)
        override=identity(path)
    elif driver_sha256 is not None:raise HostError('driver SHA supplied without module')
    gate=load_module('_wu088_guarded_assembly_provenance',LADDER/'host_synthetic_readiness_20261001_v1/provenance_gate.py')
    return join,gate,override


def source_identity(override=None):
    files=dict(verify_sources()['files'])
    for path in (HERE/'assembly_host.py',HERE/'dependency_pins.json'):
        files[str(path.relative_to(LADDER))]=digest(read_bytes(path))
    return {'files':files,'native_driver_override':override,'sha256':digest(canonical({'files':files,'override':override}))}


def configured_context(join,plan,manifest,limits,archive,override=None):
    """Also usable by a fixed-worker join producer, preserving one identity."""
    context=join.Context(plan,manifest,limits,source_archive_bytes=archive)
    if override:
        context.identity['native_driver_override']=override
        context.sha256=join.digest(context.identity)
    return context


def validate_limits(limits,build=False):
    defaults=BUILD_LIMITS if build else RUN_LIMITS
    exact_keys(limits,defaults)
    ranges={'wall_seconds':(1,3600),'memory_mib':(256,8192),'file_bytes':(4096,64*1024*1024),'precision_bits':(32,4096)}
    for name,value in limits.items():
        lo,hi=ranges[name]
        if type(value) is not int or not lo<=value<=hi:raise HostError('resource limit invalid: '+name)
    return dict(limits)


def environment(prefix):
    return {'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','LD_LIBRARY_PATH':str(prefix),
            'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}


def bounded_process(argv,env,limits,stdout_path,stderr_path):
    """Exec argv directly in a process group with wall/address-space/file caps."""
    if type(argv) is not list or not argv or any(type(x) is not str or '\x00' in x for x in argv):raise HostError('explicit argv list required')
    def cap():
        memory=limits['memory_mib']*1024*1024
        resource.setrlimit(resource.RLIMIT_AS,(memory,memory))
        resource.setrlimit(resource.RLIMIT_CORE,(0,0))
        resource.setrlimit(resource.RLIMIT_FSIZE,(limits['file_bytes'],limits['file_bytes']))
    started=time.monotonic_ns();timed_out=False
    with Path(stdout_path).open('xb') as stdout,Path(stderr_path).open('xb') as stderr:
        process=subprocess.Popen(argv,env=env,stdout=stdout,stderr=stderr,start_new_session=True,preexec_fn=cap)
        try:code=process.wait(timeout=limits['wall_seconds'])
        except subprocess.TimeoutExpired:
            os.killpg(process.pid,signal.SIGKILL);code=process.wait();timed_out=True
    return {'command':argv,'exit_code':code,'timed_out':timed_out,'elapsed_ns':time.monotonic_ns()-started,
            'stdout':identity(stdout_path,limits['file_bytes']),'stderr':identity(stderr_path,limits['file_bytes']),
            'limits':dict(limits)}


def checked_process(*args,**kwargs):
    report=bounded_process(*args,**kwargs)
    if report['timed_out'] or report['exit_code']!=0:raise ChildFailure(report)
    return report


def load_authority(paths,expected,driver_module=None,driver_sha256=None):
    exact_keys(paths,('plan','native_build_directory','native_limits','coverage','preparation','input_npz'))
    exact_keys(expected,('native_build_sha256','coverage_sha256','preparation_sha256'))
    join,gate,override=configured_modules(driver_module,driver_sha256)
    native_dir=Path(paths['native_build_directory']).resolve();prepared=Path(paths['preparation']).resolve()
    manifest=read_json(native_dir/'BUILD.json');sealed(manifest,'manifest_sha256',expected['native_build_sha256'])
    plan=read_json(paths['plan']);limits=read_json(paths['native_limits']);coverage=read_json(paths['coverage'])
    archive=read_bytes(paths['input_npz'],join.endpoint.adapter.MAX_ARCHIVE)
    context=configured_context(join,plan,manifest,limits,archive,override)
    join.validate_coverage(coverage,context)
    if coverage['coverage_sha256']!=sha(expected['coverage_sha256']):raise HostError('requested coverage identity mismatch')
    prep=read_json(prepared/'PREPARATION.json')
    if digest(canonical(prep))!=sha(expected['preparation_sha256']):raise HostError('requested preparation identity mismatch')
    header=read_bytes(prepared/'frozen107_generated.hpp')
    primitive=read_bytes(prepared/'primitive_rectangles_generated.hpp')
    native_header=read_bytes(native_dir/'frozen107_generated.hpp')
    if header!=native_header or digest(header)!=manifest['generated_header_sha256']:raise HostError('input header bytes changed')
    expected_primitive=join.initializer(coverage).encode()
    if primitive!=expected_primitive:raise HostError('primitive initializer differs from exact coverage')
    constants={'WU088_ARCHIVE_SHA256':context.identity['archive_sha256'],
        'WU088_RECORD_SHA256':context.identity['input_record_sha256'],'WU088_BUILD_SOURCE_SHA256':context.identity['native_source_sha256']}
    identity_header=('#pragma once\n'+''.join('#define '+k+' "'+sha(v)+'"\n' for k,v in constants.items())).encode()
    if any(read_bytes(path,4096)!=identity_header for path in (prepared/'build_identity.hpp',native_dir/'build_identity.hpp')):
        raise HostError('input identity header bytes changed')
    prefix=Path(manifest['prefix']).resolve();compiler=manifest['compiler']
    expected_command=compile_command(join,compiler['path'],prepared,prefix)
    required={'schema':'WU088_ASSEMBLY_PREPARATION_V1','status':'PREPARED_NATIVE_UNCOMPILED',
        'coverage_sha256':coverage['coverage_sha256'],'execution_identity_sha256':context.sha256,
        'generated_header_sha256':digest(header),'primitive_header_sha256':digest(primitive),
        'compile_command':expected_command,'assembly_exporter_sha256':digest(read_bytes(PRODUCTION/'primitive_join/assembly_exporter.cpp')),
        'compiler_identity_to_reverify':compiler,'backend_provenance_sha256':context.identity['backend_provenance_sha256'],
        'build_manifest_sha256':manifest['manifest_sha256'],'native_compiled':False,'native_executed':False,
        'scientific_admission':False,'production_admission':False}
    if prep!=required:raise HostError('preparation command/identity/schema mismatch')
    if gate.file_identity(compiler['path'],sha(compiler['sha256']))!=compiler:raise HostError('compiler identity changed')
    provenance=Path(manifest['backend_provenance'])
    if digest(read_bytes(provenance))!=context.identity['backend_provenance_sha256']:raise HostError('backend provenance changed')
    backend=gate.verify_backend(provenance,prefix)
    return {'join':join,'gate':gate,'override':override,'context':context,'coverage':coverage,'manifest':manifest,
            'preparation':prep,'backend':backend,'prefix':prefix,'headers':{
                'frozen107_generated.hpp':header,'primitive_rectangles_generated.hpp':primitive,'build_identity.hpp':identity_header}}


def compile_command(join,compiler,out,prefix):
    return [compiler,*join.native.FLAGS,'-I'+str(out),'-I'+str(OLD/'validated_callback'),'-I'+str(prefix/'include'),
        str(PRODUCTION/'primitive_join/assembly_exporter.cpp'),str(OLD/'validated_callback/assembly.cpp'),str(OLD/'validated_callback/callback.cpp'),
        '-L'+str(prefix/'lib'),'-Wl,-rpath,'+str(prefix/'lib'),'-lflint','-lmpfr','-lgmp','-o',str(out/'assembly_exporter')]


def linkage(authority,binary,out):
    report=checked_process(['/usr/bin/ldd',str(binary)],environment(authority['prefix']/'lib'),
        {'wall_seconds':15,'memory_mib':256,'file_bytes':1024*1024},out/'linkage.stdout',out/'linkage.stderr')
    text=read_bytes(out/'linkage.stdout',256*1024).decode('utf-8')
    checked=authority['gate'].verify_linkage(text,{k:v['binary_path'] for k,v in authority['backend']['libraries'].items()})
    return checked,report


def failure_record(out,stage,exc):
    path=out/'FAILURE.json'
    if not path.exists():write_new(path,{'schema':'WU088_ASSEMBLY_HOST_FAILURE_V1','stage':stage,'reason':str(exc),
        'status':'REFUSED_OR_RESOURCE_LIMIT','process':getattr(exc,'process_report',None),
        'scientific_admission':False,'production_admission':False})


def build(paths,expected,output_directory,*,limits=None,driver_module=None,driver_sha256=None):
    limits=validate_limits(BUILD_LIMITS if limits is None else limits,build=True)
    out=Path(output_directory).resolve();out.mkdir(parents=False,exist_ok=False)
    try:
        authority=load_authority(paths,expected,driver_module,driver_sha256)
        for name,data in authority['headers'].items():
            with (out/name).open('xb') as stream:stream.write(data)
        compiler=authority['manifest']['compiler']
        command=compile_command(authority['join'],compiler['path'],out,authority['prefix'])
        report=checked_process(command,environment(authority['prefix']/'lib'),limits,out/'build.stdout',out/'build.stderr')
        binary=out/'assembly_exporter'
        binary_identity=identity(binary)
        if read_bytes(binary)[:4]!=b'\x7fELF':raise HostError('compiler output is not ELF')
        linked,link_report=linkage(authority,binary,out)
        # Recheck source, input headers/compiler/backend after compilation.
        fresh=load_authority(paths,expected,driver_module,driver_sha256)
        if fresh['headers']!=authority['headers']:raise HostError('authority changed while compiling')
        for name,data in authority['headers'].items():
            if read_bytes(out/name)!=data:raise HostError('compiled header bytes changed during build')
        manifest={'schema':'WU088_ASSEMBLY_HOST_BUILD_V1','status':'BUILT_NOT_EXECUTED',
            'authority_paths':{k:str(Path(v).resolve()) for k,v in paths.items()},'expected':dict(expected),
            'native_driver_override':authority['override'],'source':source_identity(authority['override']),
            'compiler':compiler,'backend_provenance_sha256':authority['context'].identity['backend_provenance_sha256'],
            'binary':binary_identity,'linkage':linked,'build_process':report,'linkage_process':link_report,
            'header_sha256':{k:digest(v) for k,v in authority['headers'].items()},
            'coverage_sha256':authority['coverage']['coverage_sha256'],
            'execution_identity_sha256':authority['context'].sha256,
            'host':{'platform':platform.platform(),'machine':platform.machine(),'affinity':sorted(os.sched_getaffinity(0))},
            'native_compiled':True,'native_assembly_executed':False,'scientific_admission':False,'production_admission':False}
        manifest['build_sha256']=digest(canonical(manifest));write_new(out/'BUILD.json',manifest)
        return manifest
    except Exception as exc:
        failure_record(out,'BUILD',exc);raise


def validate_export(authority,final,precision):
    if type(final.get('precision_bits')) is not int or final['precision_bits']!=precision:raise HostError('export precision differs from requested execution')
    return authority['join'].import_final_disks(authority['context'],authority['coverage'],final,precision=precision)


def run(build_directory,expected_build_sha256,output_directory,*,limits=None):
    limits=validate_limits(RUN_LIMITS if limits is None else limits)
    out=Path(output_directory).resolve();out.mkdir(parents=False,exist_ok=False)
    try:
        directory=Path(build_directory).resolve();manifest=read_json(directory/'BUILD.json')
        sealed(manifest,'build_sha256',expected_build_sha256)
        if manifest.get('schema')!='WU088_ASSEMBLY_HOST_BUILD_V1' or manifest.get('native_compiled') is not True:
            raise HostError('guarded compiled build required')
        override=manifest['native_driver_override']
        authority=load_authority(manifest['authority_paths'],manifest['expected'],
            override['path'] if override else None,override['sha256'] if override else None)
        if manifest['source']!=source_identity(override):raise HostError('wrapper/dependency source changed after build')
        binary=directory/'assembly_exporter'
        if identity(binary)!=manifest['binary']:raise HostError('assembly binary changed after build')
        for name,wanted in manifest['header_sha256'].items():
            if digest(read_bytes(directory/name))!=wanted or digest(authority['headers'][name])!=wanted:raise HostError('compiled header identity changed')
        linked,link_report=linkage(authority,binary,out)
        if linked!=manifest['linkage']:raise HostError('runtime backend/system dependency identity changed')
        report=checked_process([str(binary),str(limits['precision_bits'])],environment(authority['prefix']/'lib'),
            limits,out/'native.stdout',out/'native.stderr')
        raw=read_bytes(out/'native.stdout',limits['file_bytes']);final=parse_json(raw)
        disks=validate_export(authority,final,limits['precision_bits'])
        # Recheck binary and runtime authority before publishing acceptance.
        if identity(binary)!=manifest['binary']:raise HostError('binary changed during execution')
        load_authority(manifest['authority_paths'],manifest['expected'],override['path'] if override else None,
                       override['sha256'] if override else None)
        write_new(out/'FINAL_D_RECTANGLES.json',final);write_new(out/'FINAL_D_DISKS.json',disks)
        result={'schema':'WU088_ASSEMBLY_HOST_RUN_V1','status':'CONDITIONAL_FINAL_D_ASSEMBLY_RECORDED',
            'build_sha256':expected_build_sha256,'coverage_sha256':authority['coverage']['coverage_sha256'],
            'execution_identity_sha256':authority['context'].sha256,'process':report,'linkage_process':link_report,
            'final_rectangle_canonical_sha256':digest(canonical(final)),'disk_import_sha256':digest(canonical(disks)),
            'native_assembly_execution_observed':True,'scope':'ASSEMBLY_OF_SUPPLIED_COVERAGE_ONLY',
            'upstream_endpoint_evidence_contract':authority['coverage']['endpoint_evidence_contract'],
            'upstream_native_evidence_contract':authority['coverage']['native_evidence_contract'],
            'independent_execution_proven':False,'historical_abi_admission':False,
            'scientific_admission':False,'production_admission':False}
        result['result_sha256']=digest(canonical(result));write_new(out/'RUN.json',result)
        return result
    except Exception as exc:
        failure_record(out,'RUN',exc);raise


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='mode',required=True)
    b=sub.add_parser('build')
    for name in ('plan','native-build-directory','native-limits','coverage','preparation','input-npz',
                 'native-build-sha256','coverage-sha256','preparation-sha256','output-directory'):
        b.add_argument('--'+name,required=True)
    b.add_argument('--limits-json');b.add_argument('--driver-module');b.add_argument('--driver-sha256')
    r=sub.add_parser('run');r.add_argument('--build-directory',required=True);r.add_argument('--build-sha256',required=True)
    r.add_argument('--output-directory',required=True);r.add_argument('--limits-json')
    args=parser.parse_args()
    try:
        limits=read_json(args.limits_json) if args.limits_json else None
        if args.mode=='build':
            paths={k:getattr(args,k) for k in ('plan','native_build_directory','native_limits','coverage','preparation','input_npz')}
            expected={k:getattr(args,k) for k in ('native_build_sha256','coverage_sha256','preparation_sha256')}
            result=build(paths,expected,args.output_directory,limits=limits,driver_module=args.driver_module,driver_sha256=args.driver_sha256)
        else:result=run(args.build_directory,args.build_sha256,args.output_directory,limits=limits)
        print(json.dumps({'status':result['status'],'identity':result.get('build_sha256',result.get('result_sha256')),
            'scientific_admission':False,'production_admission':False}));return 0
    except (ValueError,OSError,KeyError,TypeError,subprocess.SubprocessError) as exc:
        print(json.dumps({'status':'ASSEMBLY_HOST_REFUSED','reason':str(exc),'scientific_admission':False}),file=sys.stderr);return 2


if __name__=='__main__':raise SystemExit(main())
