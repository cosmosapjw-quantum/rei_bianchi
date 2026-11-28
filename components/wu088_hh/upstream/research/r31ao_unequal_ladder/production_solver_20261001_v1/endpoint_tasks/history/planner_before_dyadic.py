"""Bounded exact endpoint component; never a full target/scientific certificate.

Canonical primitive indexing/parameters are a transcription of the pinned
assembly.cpp. Existing source modules are checked before import. The CLI runs
one selected task in a hard wall/address-space limited subprocess. Imported
evaluate_task has cooperative limits; use run_task for hard process isolation.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
from fractions import Fraction as Q

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'gap_closure_20261001_g0_g6_v1'
EXPECTED={
    'endpoint_bound/engine.py':'227174bce527bd43a823e5fccab54cdf57f66569fb9dafe3ce920d85640f4537',
    'frozen_input/adapter.py':'82e6e96157761be7e8423c7908c501bb66086b735374ce0679836ca1b69c7b48',
    'frozen_input/FROZEN107_HEADER_SPEC.json':'71ff0c2315f4281835ff7c2736553dc9abbe4324e538e4a634bf54430b2534c8',
    'exact_raw_decoder/__init__.py':'99d80eb4f2707f9e546d1a7b3c8be7486978c5a320f76c0b1af9d05c4148159f',
    'exact_raw_decoder/decoder.py':'bf1867616af07a670d61cd75c7ca0655c99e0be13fd6a73e9a4654f5fc0986f1',
    'validated_callback/assembly.cpp':'313abcfe04550f0badc8e48501735a8b15a21d7babdefa63b6aded0ea4a2bede',
    'validated_callback/callback.cpp':'06dabab65432c868190032726853ab92a0d0d504128500cfb352c2a749258964',
}
ACCOUNTING='(outside_t x all_u) disjoint_union (inside_t x outside_u)'
EVIDENCE_CONTRACT='SOURCE_BOUND_ENGINE_OUTPUT_ASSUMED_NOT_INDEPENDENTLY_REPLAYED'
VALIDATION_LEVEL='IDENTITY_AND_REPORTED_ARITHMETIC_ONLY'
SCHEMA='WU088_ENDPOINT_TASK_PLAN_V1'
DEFAULT_CAPS={'wall_seconds':30,'memory_bytes':512*1024*1024,
              'max_engine_calls':128,'max_result_bits':16384}
MAX_JSON=8*1024*1024
MAX_RESULT=2*1024*1024


class EndpointError(ValueError):pass
class LimitReached(RuntimeError):pass


def encoded(obj):
    return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')


def digest(obj):return hashlib.sha256(encoded(obj)).hexdigest()


def source_hashes():
    for name,wanted in EXPECTED.items():
        if hashlib.sha256((OLD/name).read_bytes()).hexdigest()!=wanted:
            raise EndpointError('pinned source hash mismatch: '+name)
    return {**EXPECTED,'endpoint_tasks/planner.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


source_hashes()


def _import(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    previous=sys.dont_write_bytecode;sys.dont_write_bytecode=True
    try:spec.loader.exec_module(module)
    finally:sys.dont_write_bytecode=previous
    return module


for name,rel in (('exact_raw_decoder','exact_raw_decoder/__init__.py'),
                 ('exact_raw_decoder.decoder','exact_raw_decoder/decoder.py')):
    if name in sys.modules and Path(sys.modules[name].__file__).resolve()!=(OLD/rel).resolve():
        raise EndpointError('ambiguous decoder import origin')
sys.path.insert(0,str(OLD))
try:adapter=_import(OLD/'frozen_input/adapter.py','_wu088_endpoint_frozen_adapter')
finally:sys.path.remove(str(OLD))
engine=_import(OLD/'endpoint_bound/engine.py','_wu088_endpoint_exact_engine')


def integer(value,lo,hi,name):
    if type(value) is not int or not lo<=value<=hi:raise EndpointError('invalid '+name)
    return value


def rational(token,*,bits=4096,dyadic=False):
    if type(token) is not str or len(token)>6000 or not re.fullmatch(r'-?(0|[1-9][0-9]*)(/[1-9][0-9]*)?',token):
        raise EndpointError('canonical rational string required')
    q=Q(token)
    if str(q)!=token or max(q.numerator.bit_length(),q.denominator.bit_length())>bits:
        raise EndpointError('rational canonical form/bit cap')
    if dyadic and q.denominator&(q.denominator-1):raise EndpointError('dyadic rational required')
    return q


def _keys(obj,names,label):
    if type(obj) is not dict or set(obj)!=set(names):raise EndpointError('exact '+label+' keys required')


def primitive_index(active,field,orbital,ia,ib):
    for v,n,name in ((active,1,'active'),(field,2,'field'),(orbital,2,'orbital'),(ia,11,'ia'),(ib,11,'ib')):
        integer(v,0,n,name)
    return ((((active*3+field)*3+orbital)*12+ia)*12+ib)


def _inputs(record,source_archive_bytes):
    try:adapter.generate_cpp(record,source_archive_bytes=source_archive_bytes)
    except (ValueError,TypeError,KeyError,AttributeError) as exc:raise EndpointError('input record rejected: '+str(exc)) from exc
    fields=record['fields']
    values={name:[rational(x,dyadic=True) for x in fields[name]['values']]
            for name in ('exponents','C','v')}
    if any(x<=0 for x in values['exponents']) or values['v'][0]==0:raise EndpointError('positive exponents/nonzero v required')
    terms=[]
    for i in range(9):
        for j in range(9):
            for k in range(9):
                c=values['C'][(i*9+j)*9+k]
                if c:terms.append({'i':i,'j':j,'k':k,'coefficient':str(c)})
    if not 1<=len(terms)<=107:raise EndpointError('source requires 1..107 nonzero stored real terms')
    return values,terms


def build_plan(record,window,*,precision_bits=64,panels=4,caps=None,source_archive_bytes=None):
    integer(precision_bits,16,512,'precision_bits');integer(panels,1,32,'panels')
    _keys(window,('l_t','T_t','l_u','T_u'),'window')
    w={k:rational(v,bits=256,dyadic=True) for k,v in window.items()}
    if not 0<w['l_t']<w['T_t'] or not 0<w['l_u']<w['T_u']:raise EndpointError('invalid positive cutoff rectangle')
    if caps is None:caps={}
    if type(caps) is not dict or not set(caps)<=set(DEFAULT_CAPS):raise EndpointError('unknown caps')
    caps={**DEFAULT_CAPS,**caps}
    integer(caps['wall_seconds'],1,300,'wall_seconds')
    integer(caps['memory_bytes'],128*1024*1024,2*1024**3,'memory_bytes')
    integer(caps['max_engine_calls'],1,256,'max_engine_calls')
    integer(caps['max_result_bits'],128,16384,'max_result_bits')
    values,terms=_inputs(record,source_archive_bytes)
    shared={'schema':SCHEMA,'scope':record['scope'],'input_record_sha256':record['canonical_record_sha256'],
            'archive_sha256':record['archive_sha256'],'source_hashes':source_hashes(),'window':dict(window),
            'terms':terms,'precision_bits':precision_bits,'panels':panels,'caps':caps}
    binding=digest(shared);tasks=[]
    for active in range(2):
        for field in range(3):
            for orbital in range(3):
                for ia in range(12):
                    for ib in range(12):
                        parameters={'a':str(values['exponents'][ia]),'b':str(values['exponents'][ib]),'mu':'1',
                                    'q1':str(values['v'][0]) if active else '0',
                                    'q2':'0' if active else str(values['v'][0]),
                                    'd1':['-2','0','-3/4'] if active else ['0','0','0'],
                                    'd2':['0','0','0'] if active else ['-2','0','-3/4']}
                        task={'index':primitive_index(active,field,orbital,ia,ib),
                              'indices':{'active':active,'field':field,'orbital':orbital,'ia':ia,'ib':ib},
                              'parameters':parameters,'binding_sha256':binding}
                        task['task_sha256']=digest(task);tasks.append(task)
    plan={**shared,'input_record':record,'binding_sha256':binding,'tasks':tasks,
          'scientific_admission':False,'component':'UNNORMALIZED_POSITIVE_DOMAIN_ENDPOINT_ONLY'}
    plan['plan_sha256']=digest(plan)
    if len(encoded(plan))>MAX_JSON:raise EndpointError('plan exceeds JSON byte cap')
    # Detach mutable caller objects: subsequent record/window edits cannot alter plan.
    return json.loads(encoded(plan))


def validate_plan(plan,*,source_archive_bytes=None):
    if type(plan) is not dict:raise EndpointError('plan object required')
    try:
        expected=build_plan(plan['input_record'],plan['window'],precision_bits=plan['precision_bits'],
                            panels=plan['panels'],caps=plan['caps'],source_archive_bytes=source_archive_bytes)
    except (KeyError,TypeError) as exc:raise EndpointError('malformed plan') from exc
    if plan!=expected:raise EndpointError('plan source/input/task/coverage identity mismatch')
    return plan


def complex_abs_upper(real,imag,precision_bits=64):
    integer(precision_bits,16,512,'precision_bits')
    x,y=rational(real),rational(imag)
    return engine.sqrt_bounds(x*x+y*y,precision_bits).hi


def _base_result(plan,index):
    integer(index,0,2591,'task index')
    return {'schema':'WU088_ENDPOINT_TASK_RESULT_V1','scope':plan['scope'],'index':index,
            'plan_sha256':plan['plan_sha256'],'task_sha256':plan['tasks'][index]['task_sha256'],
            'input_record_sha256':plan['input_record_sha256'],'archive_sha256':plan['archive_sha256'],
            'window':plan['window'],'accounting':ACCOUNTING,
            'evidence_contract':EVIDENCE_CONTRACT,'validation_level':VALIDATION_LEVEL,
            'component':'UNNORMALIZED_POSITIVE_DOMAIN_ENDPOINT_ONLY','scientific_admission':False,
            'status':'INCONCLUSIVE_EXECUTION','endpoint_radius':None,'terms':[],
            'engine_calls':0,'elapsed_ns':0,'reason':None}


def _finish(result):
    result['result_sha256']=digest(result)
    if len(encoded(result))>MAX_RESULT:raise LimitReached('result byte cap')
    return result


def evaluate_task(plan,index,*,source_archive_bytes=None):
    validate_plan(plan,source_archive_bytes=source_archive_bytes)
    result=_base_result(plan,index);start=time.monotonic_ns();caps=plan['caps']
    task=plan['tasks'][index];par=task['parameters'];ids=task['indices']
    a,b,mu=(Q(par[k]) for k in ('a','b','mu'));d1=tuple(map(Q,par['d1']));d2=tuple(map(Q,par['d2']))
    l_t,T_t,l_u,T_u=(Q(plan['window'][k]) for k in ('l_t','T_t','l_u','T_u'))
    bits=plan['precision_bits'];panels=plan['panels'];majorants={};masses={};total=Q(0)
    def check(q=None):
        if time.monotonic_ns()-start>caps['wall_seconds']*10**9:raise LimitReached('cooperative wall cap')
        if q is not None and max(q.numerator.bit_length(),q.denominator.bit_length())>caps['max_result_bits']:
            raise LimitReached('exact result bit cap')
    def dispatch(fn,*args,**kwargs):
        check()
        if result['engine_calls']>=caps['max_engine_calls']:raise LimitReached('engine call cap')
        result['engine_calls']+=1
        value=fn(*args,**kwargs);check();return value
    try:
        for term in plan['terms']:
            i,j,k=(term[n] for n in ('i','j','k'))
            if k not in majorants:
                majorants[k]=dispatch(engine.gaussian_field_majorant,a,b,d1,d2,k,
                    ('s','px','pz')[ids['orbital']],('O','G1','G2')[ids['field']],bits)
            if (i,j) not in masses:
                masses[i,j]=dispatch(engine.complement_bound,i,j,mu,a,b,l_t,T_t,l_u,T_u,Q(1),bits,panels)['bound']
            c=abs(Q(term['coefficient']));C=majorants[k];mass=masses[i,j]
            check(C);check(mass)
            contribution=c*C*mass;check(contribution);total+=contribution;check(total)
            result['terms'].append({'i':i,'j':j,'k':k,'coefficient_abs':str(c),
                'field_majorant':str(C),'complement_mass_bound':str(mass),'contribution':str(contribution)})
        result.update(status='CONDITIONAL_TAIL_BOUND',endpoint_radius=str(total))
    except (LimitReached,engine.ResourceLimit,MemoryError) as exc:
        result.update(status='INCONCLUSIVE_RESOURCE_LIMIT',endpoint_radius=None,reason=str(exc)[:256])
    result['elapsed_ns']=time.monotonic_ns()-start
    try:return _finish(result)
    except LimitReached:
        result.update(status='INCONCLUSIVE_RESOURCE_LIMIT',endpoint_radius=None,terms=[],reason='result byte cap')
        return _finish(result)


def validate_result(plan,result):
    if type(result) is not dict:raise EndpointError('result object required')
    try:
        base=_base_result(plan,result['index'])
        _keys(result,(*base.keys(),'result_sha256'),'result')
        for key in set(base)-{'status','endpoint_radius','terms','engine_calls','elapsed_ns','reason'}:
            if result[key]!=base[key]:raise EndpointError('result binding mismatch: '+key)
        if digest({k:v for k,v in result.items() if k!='result_sha256'})!=result['result_sha256']:
            raise EndpointError('result SHA mismatch')
        integer(result['engine_calls'],0,plan['caps']['max_engine_calls'],'engine_calls')
        integer(result['elapsed_ns'],0,10**15,'elapsed_ns')
        if result['status']=='CONDITIONAL_TAIL_BOUND':
            radius=rational(result['endpoint_radius'],bits=plan['caps']['max_result_bits'])
            if radius<0 or result['reason'] is not None or len(result['terms'])!=len(plan['terms']):raise EndpointError('incomplete bound evidence')
            total=Q(0)
            for term,proof in zip(plan['terms'],result['terms']):
                _keys(proof,('i','j','k','coefficient_abs','field_majorant','complement_mass_bound','contribution'),'term evidence')
                if any(type(proof[k]) is not int or proof[k]!=term[k] for k in ('i','j','k')):raise EndpointError('term coverage/order mismatch')
                c,C,mass,v=(rational(proof[k],bits=plan['caps']['max_result_bits']) for k in
                    ('coefficient_abs','field_majorant','complement_mass_bound','contribution'))
                if c!=abs(Q(term['coefficient'])) or C<0 or mass<0 or v!=c*C*mass:raise EndpointError('invalid term arithmetic')
                total+=v
            if total!=radius:raise EndpointError('bound sum mismatch')
        elif result['status'] not in ('INCONCLUSIVE_RESOURCE_LIMIT','INCONCLUSIVE_EXECUTION') or result['endpoint_radius'] is not None:
            raise EndpointError('invalid failure status/radius')
    except (KeyError,TypeError,AttributeError) as exc:raise EndpointError('malformed result') from exc
    return result


def collect(plan,results,*,source_archive_bytes=None):
    validate_plan(plan,source_archive_bytes=source_archive_bytes)
    if type(results) is not list or len(results)>2592:raise EndpointError('bounded result list required')
    seen={}
    for result in results:
        validate_result(plan,result);index=result['index']
        if index in seen:raise EndpointError('duplicate primitive result')
        seen[index]=result
    accepted=[i for i in sorted(seen) if seen[i]['status']=='CONDITIONAL_TAIL_BOUND']
    missing=[i for i in range(2592) if i not in seen];inconclusive=[i for i in sorted(seen) if i not in accepted]
    return {'schema':'WU088_ENDPOINT_COVERAGE_V1','status':'COMPLETE_CONDITIONAL_ENDPOINT_COVERAGE' if len(accepted)==2592 else 'INCOMPLETE_ENDPOINT_COVERAGE',
            'plan_sha256':plan['plan_sha256'],'accepted_count':len(accepted),'missing_count':len(missing),
            'missing_indices':missing,'inconclusive_indices':inconclusive,
            'ordered_result_sha256':[seen[i]['result_sha256'] for i in sorted(seen)],
            'evidence_contract':EVIDENCE_CONTRACT,'validation_level':VALIDATION_LEVEL,'scientific_admission':False}


def read_json(path):
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:raise EndpointError('duplicate JSON key')
            d[k]=v
        return d
    def no_float(_):raise EndpointError('JSON float/nonfinite number forbidden')
    path=Path(path)
    if path.stat().st_size>MAX_JSON:raise EndpointError('JSON file exceeds cap')
    with path.open('rb') as f:raw=f.read(MAX_JSON+1)
    if len(raw)>MAX_JSON:raise EndpointError('JSON file exceeds cap')
    return json.loads(raw,object_pairs_hook=pairs,parse_float=no_float,parse_constant=no_float)


def write_new(path,obj):
    data=encoded(obj)+b'\n'
    if len(data)>MAX_JSON:raise EndpointError('output exceeds byte cap')
    with Path(path).open('xb') as f:f.write(data)


def archive_bytes(path):
    if path is None:return None
    if Path(path).stat().st_size>adapter.MAX_ARCHIVE:raise EndpointError('NPZ byte cap')
    with Path(path).open('rb') as f:data=f.read(adapter.MAX_ARCHIVE+1)
    if len(data)>adapter.MAX_ARCHIVE:raise EndpointError('NPZ byte cap')
    return data


def run_task(plan_path,index,result_path,*,resume=False,npz_path=None,execute_pinned=False):
    plan=read_json(plan_path);archive=archive_bytes(npz_path)
    validate_plan(plan,source_archive_bytes=archive);integer(index,0,2591,'task index')
    result_path=Path(result_path)
    if result_path.exists():
        if not resume:raise EndpointError('create-only result exists; use explicit resume')
        result=validate_result(plan,read_json(result_path))
        if result['index']!=index or result['status']!='CONDITIONAL_TAIL_BOUND':raise EndpointError('resume requires matching completed result; use new attempt path')
        return result
    if plan['scope']=='FROZEN107_PINNED' and not execute_pinned:
        raise EndpointError('pinned evaluation requires explicit --execute-pinned-endpoint; plan-only default')
    command=[sys.executable,'-B',str(Path(__file__).resolve()),'_worker',str(Path(plan_path).resolve()),str(index)]
    if npz_path:command+=['--npz',str(Path(npz_path).resolve())]
    environment={k:v for k,v in os.environ.items() if k in ('PATH','HOME','LANG','LC_ALL','TZ')}
    environment.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    started=time.monotonic_ns();process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
        env=environment,start_new_session=True)
    try:
        stdout,stderr=process.communicate(timeout=plan['caps']['wall_seconds'])
        if process.returncode not in (0,2) or len(stdout)>MAX_RESULT:raise EndpointError('worker exit/output refusal: '+str(process.returncode))
        result=json.loads(stdout);validate_result(plan,result)
        if result['index']!=index:raise EndpointError('worker substituted requested task index')
        wanted_code=0 if result['status']=='CONDITIONAL_TAIL_BOUND' else 2
        if process.returncode!=wanted_code:raise EndpointError('worker exit/status mismatch')
    except subprocess.TimeoutExpired:
        os.killpg(process.pid,signal.SIGKILL);process.communicate()
        result=_base_result(plan,index);result.update(status='INCONCLUSIVE_RESOURCE_LIMIT',reason='hard process wall deadline')
        result['elapsed_ns']=time.monotonic_ns()-started;_finish(result)
    except (ValueError,UnicodeError) as exc:
        result=_base_result(plan,index);result.update(reason=str(exc)[:256],elapsed_ns=time.monotonic_ns()-started);_finish(result)
    write_new(result_path,result);return result


def main():
    cli=argparse.ArgumentParser(description=__doc__);sub=cli.add_subparsers(dest='command',required=True)
    p=sub.add_parser('plan');p.add_argument('--npz',required=True);p.add_argument('--expected-sha256',required=True)
    p.add_argument('--scope',choices=('SYNTHETIC_ONLY','FROZEN107_PINNED'),required=True);p.add_argument('--output',required=True)
    for name,default in (('l-t','1/4'),('T-t','4'),('l-u','1/4'),('T-u','4')):p.add_argument('--'+name,default=default)
    p.add_argument('--precision-bits',type=int,default=64);p.add_argument('--panels',type=int,default=4)
    p.add_argument('--wall-seconds',type=int,default=30);p.add_argument('--memory-mib',type=int,default=512)
    p=sub.add_parser('run');p.add_argument('--plan',required=True);p.add_argument('--task-index',type=int,required=True)
    p.add_argument('--output',required=True);p.add_argument('--npz');p.add_argument('--resume',action='store_true')
    p.add_argument('--execute-pinned-endpoint',action='store_true')
    p=sub.add_parser('collect');p.add_argument('--plan',required=True);p.add_argument('--results',nargs='+',required=True)
    p.add_argument('--output',required=True);p.add_argument('--npz')
    p=sub.add_parser('_worker');p.add_argument('plan');p.add_argument('index',type=int);p.add_argument('--npz')
    args=cli.parse_args()
    if args.command=='plan':
        data=archive_bytes(args.npz);record=adapter.decode_npz(data,expected_archive_sha256=args.expected_sha256,scope=args.scope)
        plan=build_plan(record,{'l_t':args.l_t,'T_t':args.T_t,'l_u':args.l_u,'T_u':args.T_u},
            precision_bits=args.precision_bits,panels=args.panels,
            caps={'wall_seconds':args.wall_seconds,'memory_bytes':args.memory_mib*1024**2},source_archive_bytes=data)
        write_new(args.output,plan);print(json.dumps({'status':'PLANNED_ONLY','tasks':2592,'plan_sha256':plan['plan_sha256']}));return 0
    if args.command=='_worker':
        import resource
        resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
        plan=read_json(args.plan);cap=plan['caps']
        integer(cap['memory_bytes'],128*1024**2,2*1024**3,'memory_bytes');integer(cap['wall_seconds'],1,300,'wall_seconds')
        resource.setrlimit(resource.RLIMIT_AS,(cap['memory_bytes'],cap['memory_bytes']))
        resource.setrlimit(resource.RLIMIT_CPU,(cap['wall_seconds']+1,cap['wall_seconds']+2))
        result=evaluate_task(plan,args.index,source_archive_bytes=archive_bytes(args.npz))
    elif args.command=='run':
        result=run_task(args.plan,args.task_index,args.output,resume=args.resume,npz_path=args.npz,
                        execute_pinned=args.execute_pinned_endpoint)
    else:
        result=collect(read_json(args.plan),[read_json(p) for p in args.results],source_archive_bytes=archive_bytes(args.npz))
        write_new(args.output,result)
    print(encoded(result).decode('ascii'))
    return 0 if result['status'] in ('CONDITIONAL_TAIL_BOUND','COMPLETE_CONDITIONAL_ENDPOINT_COVERAGE') else 2


if __name__=='__main__':
    try:raise SystemExit(main())
    except (EndpointError,adapter.AdapterError,ValueError,OSError) as exc:
        print(json.dumps({'status':'INVALID_ENDPOINT_TASK_INPUT','reason':str(exc)[:512],'scientific_admission':False}),file=sys.stderr)
        raise SystemExit(2)
