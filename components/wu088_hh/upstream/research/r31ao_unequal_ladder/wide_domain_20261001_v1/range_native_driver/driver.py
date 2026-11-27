"""Bounded Frozen107 primitive build/run boundary; no scientific admission.

Build once per exact input, then launch one run command per endpoint-plan task.
Independent processes fit the existing NCP dispatcher. No MPI reduction or
floating-point serialization is performed here.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
import time

HERE=Path(__file__).resolve().parent
LADDER=HERE.parents[1]
OLD=LADDER/'gap_closure_20261001_g0_g6_v1'
READINESS=LADDER/'host_synthetic_readiness_20261001_v1'
PLAN_MODULE=LADDER/'production_solver_20261001_v1/endpoint_tasks/planner.py'
MAX_JSON=16*1024*1024
FLAGS=['-std=c++17','-O3','-fno-fast-math','-ffp-contract=off','-Wall','-Wextra','-Werror=return-type']
DEFAULT_LIMITS={'precision_bits':128,'radius_exp':-48,'relative_goal':64,
                'max_evaluations':20000,'max_integration_calls':1024,
                'wall_seconds':30,'queued_panels':64,'degree_limit':64,
                'memory_mib':1024}

class DriverError(ValueError): pass
def real_domain_margin(a,b,window):
    """Exact source guard, not quadrature tolerance or complex-box admission.

    On the real rectangle sigma >= (1/(a+T_t)+1/(b+T_u))/2.
    Native guards must still verify their entire computed complex input balls.
    """
    if type(a) not in (int,Fraction) or type(b) not in (int,Fraction) or a<=0 or b<=0:
        raise DriverError('positive exact exponents required')
    if type(window) is not dict or set(window)!={'l_t','T_t','l_u','T_u'}:
        raise DriverError('exact compact window required')
    try:
        values={key:Fraction(token) for key,token in window.items() if type(token) is str and len(token)<=320}
    except (ValueError,ZeroDivisionError) as exc:raise DriverError('invalid exact window') from exc
    if set(values)!=set(window) or any(str(values[k])!=window[k] for k in values):
        raise DriverError('canonical rational window required')
    if any(max(q.numerator.bit_length(),q.denominator.bit_length())>512 or q.denominator&(q.denominator-1) for q in values.values()):
        raise DriverError('bounded dyadic window required')
    if not 0<values['l_t']<values['T_t'] or not 0<values['l_u']<values['T_u']:
        raise DriverError('ordered positive compact window required')
    a,b=Fraction(a),Fraction(b)
    sigma_min=(1/(a+values['T_t'])+1/(b+values['T_u']))/2
    return min(Fraction(1),values['l_t'],values['l_u'],sigma_min)/(1<<20)

def log2_window(window):
    """Only exact canonical powers of two; no approximate logarithms."""
    if type(window) is not dict or set(window)!={'l_t','T_t','l_u','T_u'}:
        raise DriverError('exact compact window required')
    output={}
    for key,token in window.items():
        if type(token) is not str or len(token)>320 or not re.fullmatch(r'[1-9][0-9]*(/[1-9][0-9]*)?',token):
            raise DriverError('canonical positive power-of-two endpoint required')
        value=Fraction(token)
        n,d=value.numerator,value.denominator
        if str(value)!=token or max(n.bit_length(),d.bit_length())>512 or n&(n-1) or d&(d-1):
            raise DriverError('bounded canonical power-of-two endpoint required')
        output[key]=n.bit_length()-d.bit_length()
    if output['l_t']>=output['T_t'] or output['l_u']>=output['T_u']:
        raise DriverError('unordered log window')
    return output

def digest(data): return hashlib.sha256(data).hexdigest()
def canonical(value): return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')
def checked_hash(value):
    if type(value) is not str or re.fullmatch('[0-9a-f]{64}',value) is None:
        raise DriverError('explicit lowercase SHA256 required')
    return value
def read_bytes(path,maximum=MAX_JSON):
    path=Path(path)
    if not path.is_file() or path.stat().st_size>maximum: raise DriverError('bounded regular file required: '+str(path))
    with path.open('rb') as stream: data=stream.read(maximum+1)
    if len(data)>maximum: raise DriverError('file grew past size cap')
    return data
def _pairs(pairs):
    out={}
    for k,v in pairs:
        if k in out: raise DriverError('duplicate JSON key')
        out[k]=v
    return out
def parse_json(data):
    if type(data) is not bytes or len(data)>MAX_JSON: raise DriverError('JSON byte cap')
    try:
        return json.loads(data,object_pairs_hook=_pairs,parse_float=lambda _: (_ for _ in ()).throw(DriverError('JSON float forbidden')),
                          parse_constant=lambda _: (_ for _ in ()).throw(DriverError('nonfinite JSON forbidden')))
    except (UnicodeError,json.JSONDecodeError,RecursionError) as exc: raise DriverError('malformed JSON') from exc
def write_new(path,record):
    with Path(path).open('xb') as stream: stream.write(json.dumps(record,indent=2,sort_keys=True).encode()+b'\n')
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path); obj=importlib.util.module_from_spec(spec)
    sys.modules[name]=obj; spec.loader.exec_module(obj); return obj
def verify_sources():
    pins=parse_json(read_bytes(HERE/'dependency_pins.json'))
    if pins.get('schema')!='WU088_NATIVE_DRIVER_SOURCE_PINS_V1': raise DriverError('source pin schema')
    for relative,expected in pins['files'].items():
        path=(LADDER/relative).resolve()
        if not path.is_relative_to(LADDER): raise DriverError('source pin path escape')
        if digest(read_bytes(path))!=checked_hash(expected): raise DriverError('immutable dependency hash mismatch: '+relative)
    return pins['files']
def dependencies():
    verify_sources()
    if str(OLD) not in sys.path: sys.path.insert(0,str(OLD))
    for name,relative in [('exact_raw_decoder','exact_raw_decoder/__init__.py'),
                          ('exact_raw_decoder.decoder','exact_raw_decoder/decoder.py')]:
        if name in sys.modules and Path(sys.modules[name].__file__).resolve()!=(OLD/relative).resolve():
            raise DriverError('preloaded decoder module has another source path')
    return (module('wu088_native_frozen_adapter',OLD/'frozen_input/adapter.py'),
            module('wu088_native_provenance_gate',READINESS/'provenance_gate.py'))
def source_identity():
    files=dict(verify_sources())
    for path in (HERE/'driver.py',HERE/'primitive_worker.cpp',HERE/'dependency_pins.json',HERE/'log_map.hpp',HERE/'diagnostics.hpp',HERE/'range_petras.cpp',HERE/'range_petras.hpp'):
        files[str(path.relative_to(LADDER))]=digest(read_bytes(path))
    return {'files':files,'sha256':digest(canonical(files))}
def preflight(prefix,provenance):
    prefix=Path(prefix).resolve()
    result={'schema':'WU088_NATIVE_DRIVER_PREFLIGHT_V1','native_executed':False,
            'scientific_admission':False,'production_admission':False,'ready':False,
            'compiler':shutil.which('g++'),'prefix':str(prefix),'failures':[]}
    if not result['compiler']: result['failures'].append('g++ unavailable')
    for relative in ['include/flint/flint.h','lib/libflint.so','lib/libgmp.so','lib/libmpfr.so']:
        if not (prefix/relative).is_file(): result['failures'].append('missing pinned-prefix '+relative)
    if not Path(provenance).is_file(): result['failures'].append('backend build provenance record unavailable')
    if result['failures']: return result
    try:
        _,gate=dependencies()
        record=gate.verify_backend(Path(provenance),prefix)
        result['backend_verification']=record['verification']['status']
        result['ready']=True
    except (ValueError,OSError,KeyError,TypeError) as exc: result['failures'].append(str(exc))
    return result
def build_configuration(callback_mode='cached'):
    if callback_mode not in ('baseline','cached'):raise DriverError('explicit baseline/cached callback mode required')
    # cached_callback.cpp includes the immutable baseline TU exactly once.
    kernel=(OLD/'validated_callback/callback.cpp' if callback_mode=='baseline' else
            LADDER/'ncp64_acceleration_20261001_v1/native_cache/cached_callback.cpp')
    return {'callback_mode':callback_mode,'mode_flags':['-DWU088_USE_CACHED='+str(int(callback_mode=='cached'))],
            'sources':[str(p) for p in (HERE/'primitive_worker.cpp',kernel,
                OLD/'validated_callback/assembly.cpp',HERE/'range_petras.cpp')]}

def build(npz,prefix,provenance,outdir,*,callback_mode='cached'):
    configuration=build_configuration(callback_mode)
    check=preflight(prefix,provenance)
    if not check['ready']: raise DriverError('NATIVE_BUILD_NOT_EXECUTED: '+ '; '.join(check['failures']))
    adapter,gate=dependencies(); raw=read_bytes(npz,adapter.MAX_ARCHIVE)
    record=adapter.decode_npz(raw,expected_archive_sha256=adapter.FROZEN107_ARCHIVE_SHA256,scope='FROZEN107_PINNED')
    initializer=adapter.generate_cpp(record,source_archive_bytes=raw)
    prefix=Path(prefix).resolve(); provenance=Path(provenance).resolve(); outdir=Path(outdir).resolve()
    outdir.mkdir(parents=False,exist_ok=False)
    (outdir/'frozen107_generated.hpp').write_text(initializer)
    source=source_identity()
    constants={'WU088_ARCHIVE_SHA256':record['archive_sha256'],'WU088_RECORD_SHA256':record['canonical_record_sha256'],
               'WU088_BUILD_SOURCE_SHA256':source['sha256']}
    (outdir/'build_identity.hpp').write_text('#pragma once\n'+''.join('#define '+k+' "'+checked_hash(v)+'"\n' for k,v in constants.items()))
    compiler=Path(check['compiler']).resolve(); binary=outdir/'primitive_worker'
    command=[str(compiler),*FLAGS,*configuration['mode_flags'],'-I'+str(outdir),'-I'+str(OLD/'validated_callback'),
             '-I'+str(prefix/'include'),*configuration['sources'],
             '-L'+str(prefix/'lib'),'-Wl,-rpath,'+str(prefix/'lib'),'-lflint','-lmpfr','-lgmp','-o',str(binary)]
    env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','LD_LIBRARY_PATH':str(prefix/'lib')}
    with (outdir/'build.stdout').open('xb') as so,(outdir/'build.stderr').open('xb') as se:
        completed=subprocess.run(command,env=env,stdout=so,stderr=se,timeout=300,check=False)
    if completed.returncode: raise DriverError('native compilation failed; logs retained in '+str(outdir))
    backend=gate.verify_backend(provenance,prefix)
    ldd=subprocess.run(['/usr/bin/ldd',str(binary)],env=env,capture_output=True,text=True,timeout=15,check=True)
    (outdir/'linkage.log').write_text(ldd.stdout)
    linkage=gate.verify_linkage(ldd.stdout,{n:v['binary_path'] for n,v in backend['libraries'].items()})
    manifest={'schema':'WU088_LOG2_RANGE_NATIVE_DRIVER_BUILD_V1','source':source,'archive_sha256':record['archive_sha256'],
              'input_record_sha256':record['canonical_record_sha256'],'binary_sha256':digest(read_bytes(binary)),
              'binary':'primitive_worker','prefix':str(prefix),'backend_provenance':str(provenance),
              'backend_provenance_sha256':digest(read_bytes(provenance)),'compiler':gate.file_identity(compiler),
              'command':command,'flags':FLAGS,'callback_mode':callback_mode,
              'callback_mode_flags':configuration['mode_flags'],'callback_sources':configuration['sources'],'linkage':linkage,
              'compiler_version':subprocess.run([str(compiler),'--version'],capture_output=True,text=True,timeout=5,check=True).stdout,
              'host':{'platform':platform.platform(),'machine':platform.machine(),
                      'affinity':sorted(os.sched_getaffinity(0))},
              'generated_header_sha256':digest(initializer.encode()),
              'native_primitive_executed':False,'scientific_admission':False,'production_admission':False}
    manifest['manifest_sha256']=digest(canonical(manifest)); write_new(outdir/'BUILD.json',manifest)
    return manifest
def limits_checked(value):
    if type(value) is not dict or set(value)!=set(DEFAULT_LIMITS): raise DriverError('exact native limits keys required')
    ranges={'precision_bits':(64,1024),'radius_exp':(-1024,0),'relative_goal':(16,1024),
            'max_evaluations':(1,1000000),'max_integration_calls':(1,100000),'wall_seconds':(1,3600),
            'queued_panels':(1,4096),'degree_limit':(1,1024),'memory_mib':(256,8192)}
    for k,(lo,hi) in ranges.items():
        if type(value[k]) is not int or not lo<=value[k]<=hi: raise DriverError('native limit out of range: '+k)
    if value['relative_goal']>value['precision_bits']: raise DriverError('relative goal exceeds precision')
    return dict(value)
def dyadic_interval(value):
    if type(value) is not dict or set(value)!={'lower_mantissa','upper_mantissa','exponent2'}: raise DriverError('exact interval fields required')
    nums=[]
    for key in ('lower_mantissa','upper_mantissa','exponent2'):
        token=value[key]
        if type(token) is not str or len(token)>2500 or not re.fullmatch(r'0|-?[1-9][0-9]*',token): raise DriverError('canonical integer endpoint required')
        v=int(token)
        if v.bit_length()>8192: raise DriverError('endpoint integer bit cap')
        nums.append(v)
    lo,hi,p=nums
    if lo>hi or abs(p)>8192: raise DriverError('unordered interval or exponent cap')
    scale=Fraction(2)**p
    return Fraction(lo)*scale,Fraction(hi)*scale
def validate_result(result,*,plan,task,manifest,limits):
    expected={'schema':'WU088_LOG2_RANGE_INTERIOR_RESULT_V1','index':task['index'],
              'task_sha256':task['task_sha256'],'plan_sha256':plan['plan_sha256'],
              'archive_sha256':manifest['archive_sha256'],'input_record_sha256':manifest['input_record_sha256'],
              'build_source_sha256':manifest['source']['sha256'],'precision_bits':limits['precision_bits'],
              'accepted_component_radius_exp':limits['radius_exp'],'status':'RADIUS_MET','accepted':True,
              'coordinate_map':'LOG2_EXACT_POWER_ENDPOINTS_V1',
              'endpoint_included':False,'normalization_applied':False,'full_domain_integral':False,
              'scientific_admission':False,'production_admission':False}
    if type(result) is not dict or set(result)!=set(expected)|{'rectangle','dispatched_evaluations','integration_calls',
            'analytic_box_refusals','callback_calls','callback_refusals','flint_status','diagnostics'}:
        raise DriverError('exact native result keys required')
    for k,v in expected.items():
        if type(result.get(k)) is not type(v) or result[k]!=v: raise DriverError('native result mismatch: '+k)
    if type(result.get('rectangle')) is not dict or set(result['rectangle'])!={'real','imag'}: raise DriverError('native rectangle schema')
    for part in ('real','imag'):
        lo,hi=dyadic_interval(result['rectangle'][part])
        if (hi-lo)/2>Fraction(2)**limits['radius_exp']: raise DriverError('serialized component radius exceeds accepted cap')
    for key,cap in [('dispatched_evaluations',limits['max_evaluations']),('integration_calls',limits['max_integration_calls']),
                    ('callback_calls',limits['max_evaluations']),('callback_refusals',limits['max_evaluations']),
                    ('analytic_box_refusals',4*limits['max_evaluations'])]:
        if type(result.get(key)) is not int or not 0<=result[key]<=cap: raise DriverError('reported resource cap mismatch')
    if type(result.get('flint_status')) is not int or result['flint_status']!=0: raise DriverError('FLINT success status required')
    expected_diag={'preflight_calls','preflight_nonfinite','nonfinite_order1','nonfinite_order0_range','nonfinite_order0_exact',
        'selected_point_inner','selected_uniform_inner','inner_radius_met','inner_radius_too_wide','inner_no_convergence',
        'inner_nonfinite','inner_resource_limit','inner_invalid_contract','inner_enclosure_available','outer_order1_calls','outer_order0_range_calls',
        'outer_order0_exact_calls','outer_order1_failures','outer_order0_range_failures','outer_order0_exact_failures',
        'outer_refinable_failures','outer_fatal_failures','peak_active_integrations'}
    diag=result['diagnostics']
    if type(diag) is not dict or set(diag)!={'counters','inner_outcomes','failure_samples'} or type(diag['counters']) is not dict or set(diag['counters'])!=expected_diag:
        raise DriverError('diagnostic counter keys mismatch')
    for key,value in diag['counters'].items():
        if type(value) is not int or not 0<=value<=2*limits['max_evaluations']:raise DriverError('diagnostic counter bounds')
    if diag['counters']['peak_active_integrations']>2:raise DriverError('invalid diagnostic integration depth')
    matrix=diag['inner_outcomes']
    if type(matrix) is not list or len(matrix)!=3:raise DriverError('diagnostic outer categories')
    for row in matrix:
        if type(row) is not list or len(row)!=2:raise DriverError('diagnostic selection categories')
        for outcomes in row:
            if type(outcomes) is not list or len(outcomes)!=7 or any(type(v) is not int or not 0<=v<=limits['max_evaluations'] for v in outcomes):
                raise DriverError('diagnostic outcomes')
    samples=diag['failure_samples']
    if type(samples) is not list or len(samples)>8:raise DriverError('diagnostic sample cap')
    for sample in samples:
        keys={'outer_order','precision_bits','absolute_tolerance_exp','accepted_component_radius_exp','relative_goal',
              'outer_exact','uniform_inner','truncated','status','reason','outer_real','outer_imag','flint_status','inner_return'}
        if type(sample) is not dict or set(sample)!=keys:raise DriverError('diagnostic sample schema')
        if any(type(sample[k]) is not bool for k in ('outer_exact','uniform_inner','truncated')):raise DriverError('diagnostic boolean')
        if any(type(sample[k]) is not str or len(sample[k])>2048 for k in ('status','reason','outer_real','outer_imag')):raise DriverError('diagnostic string cap')
        for k in ('outer_order','precision_bits','absolute_tolerance_exp','accepted_component_radius_exp','relative_goal','flint_status'):
            if type(sample[k]) is not int or abs(sample[k])>4096:raise DriverError('diagnostic integer cap')
        inner=sample['inner_return']
        if type(inner) is not dict or set(inner)!={'observed','finite','truncated','flint_status','real','imag','real_radius','imag_radius'}:
            raise DriverError('diagnostic inner snapshot schema')
        if any(type(inner[k]) is not bool for k in ('observed','finite','truncated')):raise DriverError('diagnostic snapshot boolean')
        if type(inner['flint_status']) is not int or not -1<=inner['flint_status']<=100:raise DriverError('diagnostic snapshot status')
        if any(type(inner[k]) is not str or len(inner[k])>2048 for k in ('real','imag','real_radius','imag_radius')):raise DriverError('diagnostic snapshot string')
    return result
def execute_bound_native(command,env,limits,binding,out,plan,task,manifest):
    def child_limits():
        memory=limits['memory_mib']*1024*1024
        resource.setrlimit(resource.RLIMIT_AS,(memory,memory))
        resource.setrlimit(resource.RLIMIT_CORE,(0,0))
        resource.setrlimit(resource.RLIMIT_FSIZE,(MAX_JSON,MAX_JSON))
    # Time only this process launch/wait/termination. Build, validation and
    # provenance checks are outside the measured interval. Integer nanoseconds.
    with tempfile.TemporaryDirectory(prefix='wu088-log2-interior-') as temporary:
        with (Path(temporary)/'stdout').open('w+b') as so,(Path(temporary)/'stderr').open('w+b') as se:
            started=time.monotonic_ns(); timed_out=False
            try:
                process=subprocess.Popen(command,env=env,stdout=so,stderr=se,start_new_session=True,preexec_fn=child_limits)
                binding['native_execution_observed']=True
                try: code=process.wait(timeout=limits['wall_seconds']+5)
                except subprocess.TimeoutExpired:
                    timed_out=True
                    os.killpg(process.pid,signal.SIGKILL); code=process.wait()
            except OSError as exc:
                binding['elapsed_wall_ns']=time.monotonic_ns()-started
                rejection={'schema':'WU088_LOG2_NATIVE_INTERIOR_REJECTION_V1','reason':'PROCESS_LAUNCH_FAILED',
                           'index':task['index'],'plan_sha256':plan['plan_sha256'],'task_sha256':task['task_sha256'],
                           'error':str(exc),'wrapper':binding,'accepted':False,
                           'scientific_admission':False,'production_admission':False}
                write_new(out,rejection); raise DriverError('native process launch failed') from exc
            binding['elapsed_wall_ns']=time.monotonic_ns()-started
            binding['returncode']=code
            so.seek(0); payload=so.read(MAX_JSON+1); se.seek(0); stderr=se.read(MAX_JSON+1)
    binding['native_stdout_sha256']=digest(payload);binding['native_stderr_sha256']=digest(stderr)
    failure='EXTERNAL_WALL_CAP' if timed_out else ('NONZERO_NATIVE_EXIT' if code else None)
    if not failure:
        try: result=validate_result(parse_json(payload),plan=plan,task=task,manifest=manifest,limits=limits)
        except (ValueError,TypeError,KeyError) as exc: failure='INVALID_NATIVE_OUTPUT';binding['validation_error']=str(exc)
    if failure:
        rejection={'schema':'WU088_LOG2_NATIVE_INTERIOR_REJECTION_V1','reason':failure,'returncode':code,
                   'index':task['index'],'plan_sha256':plan['plan_sha256'],'task_sha256':task['task_sha256'],
                   'native_stdout':payload[:MAX_JSON].decode('utf-8','replace'),
                   'native_stderr':stderr[:MAX_JSON].decode('utf-8','replace'),
                   'wrapper':binding,'accepted':False,'scientific_admission':False,'production_admission':False}
        rejection['result_sha256']=digest(canonical(rejection));write_new(out,rejection)
        raise DriverError('NATIVE_REJECTED '+failure+' exit '+str(code))
    result['wrapper']=binding
    result['result_sha256']=digest(canonical(result)); write_new(out,result)
    return result
def _run_task(npz,plan_path,expected_plan_sha,index,build_dir,expected_build_sha,limits,out):
    if os.path.lexists(out): raise DriverError('output already exists; completed/partial task is not rerun')
    limits=limits_checked(limits); adapter,gate=dependencies()
    manifest=parse_json(read_bytes(Path(build_dir)/'BUILD.json'))
    body={k:v for k,v in manifest.items() if k!='manifest_sha256'}
    if manifest.get('manifest_sha256')!=checked_hash(expected_build_sha) or digest(canonical(body))!=expected_build_sha:
        raise DriverError('build manifest identity mismatch')
    if manifest.get('source')!=source_identity(): raise DriverError('driver/dependency source changed since build')
    if manifest.get('schema')!='WU088_LOG2_RANGE_NATIVE_DRIVER_BUILD_V1': raise DriverError('build schema mismatch')
    configuration=build_configuration(manifest.get('callback_mode'))
    if manifest.get('callback_mode_flags')!=configuration['mode_flags'] or manifest.get('callback_sources')!=configuration['sources']:
        raise DriverError('callback compilation mode/source mismatch')
    raw=read_bytes(npz,adapter.MAX_ARCHIVE)
    record=adapter.decode_npz(raw,expected_archive_sha256=adapter.FROZEN107_ARCHIVE_SHA256,scope='FROZEN107_PINNED')
    if manifest['archive_sha256']!=record['archive_sha256'] or manifest['input_record_sha256']!=record['canonical_record_sha256']:
        raise DriverError('build is bound to another source input')
    plan=parse_json(read_bytes(plan_path))
    if plan.get('plan_sha256')!=checked_hash(expected_plan_sha): raise DriverError('external plan identity mismatch')
    planner=module('wu088_native_endpoint_planner',PLAN_MODULE)
    planner.validate_plan(plan,source_archive_bytes=raw)
    if plan['scope']!='FROZEN107_PINNED' or plan['input_record_sha256']!=record['canonical_record_sha256']:
        raise DriverError('native task requires exact Frozen107 plan')
    if type(index) is not int or not 0<=index<2592: raise DriverError('task index out of range')
    log_window=log2_window(plan['window'])
    task=plan['tasks'][index]
    if task['index']!=index: raise DriverError('canonical task ordering changed')
    prefix=Path(manifest['prefix']); provenance=Path(manifest['backend_provenance'])
    if digest(read_bytes(provenance))!=manifest['backend_provenance_sha256']: raise DriverError('backend provenance changed')
    backend=gate.verify_backend(provenance,prefix)
    binary=Path(build_dir).resolve()/'primitive_worker'
    if digest(read_bytes(binary))!=manifest['binary_sha256']: raise DriverError('native binary changed')
    env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','LD_LIBRARY_PATH':str(prefix/'lib'),
         'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
    ldd=subprocess.run(['/usr/bin/ldd',str(binary)],env=env,capture_output=True,text=True,timeout=15,check=True)
    linkage=gate.verify_linkage(ldd.stdout,{n:v['binary_path'] for n,v in backend['libraries'].items()})
    if linkage!=manifest['linkage']: raise DriverError('runtime dependency byte identity changed')
    command=[str(binary),str(index),*[plan['window'][k] for k in ('l_t','T_t','l_u','T_u')],
             *[str(limits[k]) for k in ('precision_bits','radius_exp','relative_goal','max_evaluations',
                 'max_integration_calls','wall_seconds','queued_panels','degree_limit')],task['task_sha256'],plan['plan_sha256']]
    binding={'schema':'WU088_LOG2_NATIVE_INTERIOR_WRAPPER_V1','build_manifest_sha256':expected_build_sha,
             'binary_sha256':manifest['binary_sha256'],'build_source':manifest['source'],
             'archive_sha256':manifest['archive_sha256'],'input_record_sha256':manifest['input_record_sha256'],
             'native_limits':limits,'command':command,'coordinate_map':'LOG2_EXACT_POWER_ENDPOINTS_V1',
             'physical_window':dict(plan['window']),'log2_window':log_window,
             'backend_provenance_sha256':manifest['backend_provenance_sha256'],'linkage':linkage,
             'native_execution_observed':False,'scope':'CONDITIONAL_COMPACT_INTERIOR_ONLY',
             'evidence_contract':'SOURCE_BOUND_NATIVE_OUTPUT_ASSUMED_NOT_INDEPENDENTLY_REPLAYED',
             'validation_level':'BYTE_IDENTITY_AND_REPORTED_RADIUS_ONLY',
             'endpoint_plan_module_sha256':digest(read_bytes(PLAN_MODULE)),
             'historical_abi_admission':False,'independent_scientific_review':False}
    return execute_bound_native(command,env,limits,binding,out,plan,task,manifest)

def run_task(npz,plan_path,expected_plan_sha,index,build_dir,expected_build_sha,limits,out):
    if os.path.lexists(out): raise DriverError('output already exists; completed/partial task is not rerun')
    # Atomic task ownership prevents two dispatcher retries from computing the
    # same output concurrently. A claim left by a crashed wrapper is fail-closed
    # and requires inspection; it is never automatically deleted on startup.
    claim=Path(str(out)+'.claim')
    descriptor=os.open(claim,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        os.write(descriptor,str(os.getpid()).encode('ascii'))
        return _run_task(npz,plan_path,expected_plan_sha,index,build_dir,expected_build_sha,limits,out)
    finally:
        os.close(descriptor); claim.unlink()
def main():
    parser=argparse.ArgumentParser(description=__doc__); sub=parser.add_subparsers(dest='mode',required=True)
    p=sub.add_parser('preflight'); p.add_argument('--flint-prefix',required=True); p.add_argument('--backend-provenance',required=True)
    p=sub.add_parser('build'); p.add_argument('--input-npz',required=True); p.add_argument('--flint-prefix',required=True)
    p.add_argument('--backend-provenance',required=True); p.add_argument('--output-directory',required=True)
    p.add_argument('--callback-mode',choices=('baseline','cached'),default='cached')
    p=sub.add_parser('run'); p.add_argument('--input-npz',required=True); p.add_argument('--plan',required=True)
    p.add_argument('--plan-sha256',required=True); p.add_argument('--task-index',type=int,required=True)
    p.add_argument('--build-directory',required=True); p.add_argument('--build-sha256',required=True)
    p.add_argument('--limits-json'); p.add_argument('--output',required=True)
    args=parser.parse_args()
    try:
        if args.mode=='preflight':
            result=preflight(args.flint_prefix,args.backend_provenance); print(json.dumps(result,indent=2)); return 0 if result['ready'] else 2
        if args.mode=='build': result=build(args.input_npz,args.flint_prefix,args.backend_provenance,args.output_directory,callback_mode=args.callback_mode)
        else: result=run_task(args.input_npz,args.plan,args.plan_sha256,args.task_index,args.build_directory,args.build_sha256,
                             parse_json(read_bytes(args.limits_json)) if args.limits_json else DEFAULT_LIMITS,args.output)
        print(json.dumps({'status':'BUILD_RECORDED' if args.mode=='build' else 'CONDITIONAL_INTERIOR_RECORDED',
                          'identity':result.get('manifest_sha256',result.get('result_sha256')),
                          'scientific_admission':False,'production_admission':False})); return 0
    except (ValueError,OSError,KeyError,TypeError,subprocess.SubprocessError) as exc:
        print('NATIVE_DRIVER_REFUSED: '+str(exc),file=sys.stderr); return 2
if __name__=='__main__': raise SystemExit(main())
