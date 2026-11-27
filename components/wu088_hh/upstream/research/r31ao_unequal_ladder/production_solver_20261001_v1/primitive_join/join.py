"""Conditional exact primitive join and complete-coverage assembly boundary.

Receipts establish identity and reported arithmetic, not independent execution
or target-enclosure proof. No scientific/production gate can be admitted here.
"""
from fractions import Fraction as Q
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
COUNT = 2592
MAX_BYTES = 32 * 1024 * 1024
BITS = 8192


class JoinError(ValueError): pass


def canonical(obj):
    try: return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')
    except (ValueError, TypeError, RecursionError) as exc: raise JoinError('finite JSON data required') from exc


def digest(obj): return hashlib.sha256(canonical(obj)).hexdigest()


def keys(obj, required):
    if type(obj) is not dict or set(obj) != set(required): raise JoinError('missing/extra object keys')


def sha(value):
    if type(value) is not str or not re.fullmatch('[0-9a-f]{64}', value): raise JoinError('lowercase SHA-256 required')
    return value


def rational(value):
    if type(value) is not str or len(value) > 5000 or not re.fullmatch(r'(?:0|-?[1-9][0-9]*)(?:/[1-9][0-9]*)?', value):
        raise JoinError('bounded canonical rational required')
    parts = value.split('/')
    if any(len(part.lstrip('-')) > 2467 for part in parts): raise JoinError('integer allocation cap')
    q = Q(value)
    if str(q) != value or max(q.numerator.bit_length(), q.denominator.bit_length()) > BITS:
        raise JoinError('rational canonical/bit cap')
    return q


def bounded(q):
    if max(q.numerator.bit_length(), q.denominator.bit_length()) > BITS: raise JoinError('intermediate bit cap')
    return q


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec); sys.modules[name] = obj
    previous = sys.dont_write_bytecode; sys.dont_write_bytecode = True
    try: spec.loader.exec_module(obj)
    finally: sys.dont_write_bytecode = previous
    return obj


endpoint = _load('_wu088_join_endpoint', ROOT / 'endpoint_tasks/planner.py')
native = _load('_wu088_join_native', ROOT / 'native_driver/driver.py')


def modules_identity():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (
        ROOT/'endpoint_tasks/planner.py', ROOT/'native_driver/driver.py', HERE/'join.py')}


def sealed(obj, field):
    if field not in obj or digest({k:v for k,v in obj.items() if k != field}) != sha(obj[field]):
        raise JoinError('canonical document identity mismatch: ' + field)


class Context:
    """One verified plan/build/limits tuple; shared by all independent tasks."""
    def __init__(self, plan, manifest, limits, *, source_archive_bytes=None):
        try:
            endpoint.validate_plan(plan, source_archive_bytes=source_archive_bytes)
            native.limits_checked(limits)
            sealed(manifest, 'manifest_sha256')
            if manifest['schema'] != 'WU088_NATIVE_DRIVER_BUILD_V1': raise JoinError('native build schema')
            if manifest['source'] != native.source_identity(): raise JoinError('native source identity changed')
            if any(manifest[k] != plan[k] for k in ('archive_sha256', 'input_record_sha256')):
                raise JoinError('mixed archived input/record identity')
            for key in ('binary_sha256', 'backend_provenance_sha256'): sha(manifest[key])
        except (ValueError, KeyError, TypeError, OSError) as exc:
            raise JoinError('join context rejected: ' + str(exc)) from exc
        self.plan = json.loads(canonical(plan)); self.manifest = json.loads(canonical(manifest))
        self.limits = dict(limits)
        self.identity = {
            'plan_sha256': plan['plan_sha256'], 'build_manifest_sha256': manifest['manifest_sha256'],
            'archive_sha256': plan['archive_sha256'], 'input_record_sha256': plan['input_record_sha256'],
            'window': plan['window'], 'native_limits': self.limits,
            'native_binary_sha256': manifest['binary_sha256'],
            'backend_provenance_sha256': manifest['backend_provenance_sha256'],
            'native_source_sha256': manifest['source']['sha256'],
            'endpoint_binding_sha256': plan['binding_sha256'], 'module_hashes': modules_identity()}
        self.identity = json.loads(canonical(self.identity))
        self.sha256 = digest(self.identity)


def _index(value):
    if type(value) is not int or not 0 <= value < COUNT: raise JoinError('primitive index out of range')
    return value


def join_rectangle(interior, radius):
    """Disk |tail|<=B enlarges each rectangular component by B exactly once."""
    keys(interior, ('real', 'imag'))
    b = rational(radius)
    if b < 0: raise JoinError('negative tail radius')
    out = {}
    for part in ('real', 'imag'):
        lo, hi = native.dyadic_interval(interior[part])
        bounded(lo); bounded(hi)
        out[part] = {'lo': str(bounded(lo-b)), 'hi': str(bounded(hi+b))}
    return out


def join_task(context, tail, interior):
    if not isinstance(context, Context): raise JoinError('verified Context required')
    try:
        endpoint.validate_result(context.plan, tail)
        if tail['status'] != 'CONDITIONAL_TAIL_BOUND': raise JoinError('endpoint did not return a bound')
        index = _index(tail['index']); task = context.plan['tasks'][index]
        sealed(interior, 'result_sha256')
        native.validate_result({k:v for k,v in interior.items() if k not in ('wrapper','result_sha256')}, plan=context.plan, task=task,
                               manifest=context.manifest, limits=context.limits)
        wrapper = interior['wrapper']
        expected_wrapper = {
            'schema': 'WU088_NATIVE_INTERIOR_WRAPPER_V1',
            'build_manifest_sha256': context.manifest['manifest_sha256'],
            'native_limits': context.limits, 'native_execution_observed': True,
            'scope': 'CONDITIONAL_COMPACT_INTERIOR_ONLY',
            'endpoint_plan_module_sha256': context.identity['module_hashes']['endpoint_tasks/planner.py'],
            'historical_abi_admission': False, 'independent_scientific_review': False,
            'evidence_contract':'SOURCE_BOUND_NATIVE_OUTPUT_ASSUMED_NOT_INDEPENDENTLY_REPLAYED',
            'validation_level':'BYTE_IDENTITY_AND_REPORTED_RADIUS_ONLY'}
        keys(wrapper, (*expected_wrapper, 'command', 'native_stdout_sha256'))
        for key, value in expected_wrapper.items():
            if type(wrapper[key]) is not type(value) or wrapper[key] != value: raise JoinError('mixed execution identity: '+key)
        sha(wrapper['native_stdout_sha256'])
        command = wrapper['command']
        expected_args = [str(index), *[context.plan['window'][k] for k in ('l_t','T_t','l_u','T_u')],
            *[str(context.limits[k]) for k in ('precision_bits','radius_exp','relative_goal','max_evaluations',
                'max_integration_calls','wall_seconds','queued_panels','degree_limit')], task['task_sha256'],context.plan['plan_sha256']]
        if type(command) is not list or len(command) != 16 or type(command[0]) is not str or Path(command[0]).name != 'primitive_worker' or command[1:] != expected_args:
            raise JoinError('native task/window/cap command mismatch')
        # Independent of the native parser's permissiveness, reject repeated
        # endpoint/normalization flags before any uncertainty can be combined.
        if any(interior[k] is not False for k in ('endpoint_included','normalization_applied','full_domain_integral')):
            raise JoinError('interior already includes endpoint/assembly')
        rectangle = join_rectangle(interior['rectangle'], tail['endpoint_radius'])
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        raise JoinError('primitive join rejected: '+str(exc)) from exc
    result = {
        'schema': 'WU088_FULL_DOMAIN_PRIMITIVE_V1', 'status': 'CONDITIONAL_FULL_DOMAIN_PRIMITIVE',
        'index': index, 'indices': task['indices'], 'task_sha256': task['task_sha256'],
        'execution_identity': context.identity, 'execution_identity_sha256': context.sha256,
        'endpoint_result_sha256': tail['result_sha256'], 'interior_result_sha256': interior['result_sha256'],
        'interior_rectangle': interior['rectangle'], 'endpoint_radius': tail['endpoint_radius'],
        'rectangle': rectangle, 'endpoint_additions': 1, 'normalization_applied': False,
        'accounting': endpoint.ACCOUNTING, 'endpoint_evidence_contract': tail['evidence_contract'],
        'native_evidence_contract': wrapper['evidence_contract'],
        'validation_level': 'IDENTITY_AND_REPORTED_ARITHMETIC_ONLY',
        'scientific_admission': False, 'production_admission': False}
    result['result_sha256'] = digest(result)
    return result


def validate_joined(context, result):
    expected = {'schema','status','index','indices','task_sha256','execution_identity','execution_identity_sha256',
        'endpoint_result_sha256','interior_result_sha256','interior_rectangle','endpoint_radius','rectangle',
        'endpoint_additions','normalization_applied','accounting','endpoint_evidence_contract','validation_level',
        'native_evidence_contract','scientific_admission','production_admission','result_sha256'}
    keys(result, expected); sealed(result,'result_sha256')
    index = _index(result['index']); task = context.plan['tasks'][index]
    fixed = {'schema':'WU088_FULL_DOMAIN_PRIMITIVE_V1','status':'CONDITIONAL_FULL_DOMAIN_PRIMITIVE',
        'indices':task['indices'],'task_sha256':task['task_sha256'], 'execution_identity':context.identity,
        'execution_identity_sha256':context.sha256,'endpoint_additions':1,'normalization_applied':False,
        'accounting':endpoint.ACCOUNTING,'endpoint_evidence_contract':'SOURCE_BOUND_ENGINE_OUTPUT_ASSUMED_NOT_INDEPENDENTLY_REPLAYED',
        'native_evidence_contract':'SOURCE_BOUND_NATIVE_OUTPUT_ASSUMED_NOT_INDEPENDENTLY_REPLAYED',
        'validation_level':'IDENTITY_AND_REPORTED_ARITHMETIC_ONLY','scientific_admission':False,'production_admission':False}
    for key,value in fixed.items():
        if type(result[key]) is not type(value) or result[key] != value: raise JoinError('joined binding mismatch: '+key)
    for key in ('endpoint_result_sha256','interior_result_sha256'): sha(result[key])
    if result['rectangle'] != join_rectangle(result['interior_rectangle'], result['endpoint_radius']):
        raise JoinError('joined rectangle arithmetic mismatch')
    return result


def collect(context, results):
    """Require all 2592 exactly once; incomplete coverage never emits an initializer."""
    seen = {}
    for result in results:
        if len(seen) >= COUNT: raise JoinError('coverage count cap')
        validate_joined(context,result)
        if result['index'] in seen: raise JoinError('duplicate primitive index')
        seen[result['index']] = result
    if set(seen) != set(range(COUNT)): raise JoinError('incomplete primitive coverage: '+str(COUNT-len(seen)))
    record = {'schema':'WU088_FULL_DOMAIN_PRIMITIVE_COVERAGE_V1',
        'status':'COMPLETE_CONDITIONAL_PRIMITIVE_COVERAGE',
        'execution_identity':context.identity,'execution_identity_sha256':context.sha256,
        'ordered_result_sha256':[seen[i]['result_sha256'] for i in range(COUNT)],
        'rectangles':[seen[i]['rectangle'] for i in range(COUNT)],'primitive_count':COUNT,
        'normalization_applied':False,'endpoint_additions':1,
        'validation_level':'IDENTITY_AND_REPORTED_ARITHMETIC_ONLY',
        'endpoint_evidence_contract':'SOURCE_BOUND_ENGINE_OUTPUT_ASSUMED_NOT_INDEPENDENTLY_REPLAYED',
        'native_evidence_contract':'SOURCE_BOUND_NATIVE_OUTPUT_ASSUMED_NOT_INDEPENDENTLY_REPLAYED',
        'scientific_admission':False,'production_admission':False}
    record['coverage_sha256']=digest(record)
    if len(canonical(record)) > MAX_BYTES: raise JoinError('coverage output byte cap')
    return record


def validate_coverage(coverage, context=None):
    keys(coverage, ('schema','status','execution_identity','execution_identity_sha256','ordered_result_sha256',
        'rectangles','primitive_count','normalization_applied','endpoint_additions','validation_level',
        'endpoint_evidence_contract','native_evidence_contract','scientific_admission','production_admission','coverage_sha256'))
    sealed(coverage,'coverage_sha256')
    if coverage['schema']!='WU088_FULL_DOMAIN_PRIMITIVE_COVERAGE_V1' or type(coverage['primitive_count']) is not int or coverage['primitive_count']!=COUNT or len(coverage['rectangles'])!=COUNT:
        raise JoinError('complete coverage required')
    if type(coverage['endpoint_additions']) is not int or coverage['endpoint_additions']!=1 or coverage['normalization_applied'] is not False:
        raise JoinError('already assembled or endpoint accounting mismatch')
    if coverage['status']!='COMPLETE_CONDITIONAL_PRIMITIVE_COVERAGE' or any(coverage[k] is not False for k in ('scientific_admission','production_admission')):
        raise JoinError('coverage admission/status mismatch')
    if digest(coverage['execution_identity'])!=sha(coverage['execution_identity_sha256']): raise JoinError('coverage execution identity')
    if context and coverage['execution_identity']!=context.identity: raise JoinError('mixed coverage execution identity')
    hashes=coverage['ordered_result_sha256']
    if type(hashes) is not list or len(hashes)!=COUNT or len(set(map(sha,hashes)))!=COUNT: raise JoinError('result hash coverage mismatch')
    if coverage['validation_level']!='IDENTITY_AND_REPORTED_ARITHMETIC_ONLY': raise JoinError('invalid evidence promotion')
    if coverage['endpoint_evidence_contract']!='SOURCE_BOUND_ENGINE_OUTPUT_ASSUMED_NOT_INDEPENDENTLY_REPLAYED' or coverage['native_evidence_contract']!='SOURCE_BOUND_NATIVE_OUTPUT_ASSUMED_NOT_INDEPENDENTLY_REPLAYED':
        raise JoinError('inherited conditional evidence contract mismatch')
    return coverage


def initializer(coverage):
    """Emit exact rational center/radius input for immutable native assembly."""
    validate_coverage(coverage)
    identity=coverage['execution_identity']
    lines=['#pragma once','#include "assembly.hpp"','#include <stdexcept>',
        '// Generated source-bound rational rectangles, not a scientific admission.',
        '#define WU088_PRIMITIVE_COVERAGE_SHA256 "'+sha(coverage['coverage_sha256'])+'"',
        '#define WU088_PRIMITIVE_EXECUTION_SHA256 "'+sha(coverage['execution_identity_sha256'])+'"',
        '#define WU088_PRIMITIVE_RECORD_SHA256 "'+sha(identity['input_record_sha256'])+'"',
        '#define WU088_PRIMITIVE_ARCHIVE_SHA256 "'+sha(identity['archive_sha256'])+'"',
        '#define WU088_ASSEMBLER_SOURCE_SHA256 "'+hashlib.sha256((HERE/'assembly_exporter.cpp').read_bytes()).hexdigest()+'"',
        'inline void wu088_set_component(arb_t out,const char* m,const char* r,slong p) {',
        ' wu088::Rational mid(m),rad(r); arb_t error; arb_init(error);',
        ' arb_set_fmpq(out,mid.value,p); arb_set_fmpq(error,rad.value,p);',
        ' arb_add_error(out,error); arb_clear(error);',
        ' if (!arb_is_finite(out)) throw std::runtime_error("nonfinite imported primitive");','}',
        'inline void load_real_domain_primitives(wu088::RealDomainPrimitiveIntegrals& raw,slong p) {',
        ' if(p<32 || p>4096) throw std::runtime_error("assembly precision cap");']
    for index, rectangle in enumerate(coverage['rectangles']):
        keys(rectangle,('real','imag'))
        for part,ref in [('real','acb_realref'),('imag','acb_imagref')]:
            keys(rectangle[part],('lo','hi'))
            lo,hi=(rational(rectangle[part][key]) for key in ('lo','hi'))
            if lo>hi: raise JoinError('reversed rectangle')
            mid,radius=bounded((lo+hi)/2),bounded((hi-lo)/2)
            lines.append(f' wu088_set_component({ref}(raw.unnormalized_real_domain_integrals[{index}].value),"{mid}","{radius}",p);')
    lines.append('}')
    code='\n'.join(lines)+'\n'
    if len(code.encode()) > MAX_BYTES: raise JoinError('initializer byte cap')
    return code


def import_final_disks(context, coverage, final, *, precision=128):
    """Native final D rectangles -> outward disks for composition.inputs.target_disks.

    The native receipt remains source-assumed; no generated hash admits its
    execution, enclosure provenance, physical adequacy, or historical ABI.
    """
    validate_coverage(coverage,context)
    keys(final,('schema','coverage_sha256','execution_identity_sha256','archive_sha256',
        'input_record_sha256','assembler_source_sha256','precision_bits','D_col','D_row',
        'scientific_admission','production_admission'))
    fixed={'schema':'WU088_FINAL_D_RECTANGLES_V1','coverage_sha256':coverage['coverage_sha256'],
        'execution_identity_sha256':context.sha256,'archive_sha256':context.identity['archive_sha256'],
        'input_record_sha256':context.identity['input_record_sha256'],
        'assembler_source_sha256':hashlib.sha256((HERE/'assembly_exporter.cpp').read_bytes()).hexdigest(),
        'scientific_admission':False,'production_admission':False}
    for key,value in fixed.items():
        if type(final[key]) is not type(value) or final[key]!=value: raise JoinError('final assembly binding mismatch: '+key)
    if type(final['precision_bits']) is not int or not 32<=final['precision_bits']<=4096: raise JoinError('assembly precision cap')
    if type(precision) is not int or not 1<=precision<=4096: raise JoinError('disk-conversion precision cap')
    composition=_load('_wu088_join_composition',ROOT/'composition/adapter.py')
    data={}
    for name,shape in [('D_col',(47,2)),('D_row',(2,47))]:
        value=final[name];m,n=shape
        if type(value) is not list or len(value)!=m or any(type(row) is not list or len(row)!=n for row in value): raise JoinError('final D shape mismatch')
        data[name]=[]
        for row in value:
            out=[]
            for rectangle in row:
                keys(rectangle,('real','imag')); centers=[]; squares=Q(0)
                for part in ('real','imag'):
                    lo,hi=native.dyadic_interval(rectangle[part]);bounded(lo);bounded(hi)
                    centers.append(str(bounded((lo+hi)/2)))
                    half=bounded((hi-lo)/2);squares=bounded(squares+bounded(half*half))
                radius=composition.gram.sqrt_interval(squares,precision=precision,
                    limits=composition.gram.Limits(max_integer_bits=BITS,max_work_bits=32768,max_operations=100000))
                out.append({'center':centers,'radius':str(radius.hi)})
            data[name].append(out)
    return {'schema':'WU088_FINAL_D_DISKS_IMPORT_V1','status':'CONDITIONAL_FINAL_D_DISKS',
        'target_disks':composition.bind(data),'final_rectangle_canonical_sha256':digest(final),
        'coverage_sha256':coverage['coverage_sha256'],'execution_identity_sha256':context.sha256,
        'endpoint_evidence_contract':coverage['endpoint_evidence_contract'],
        'native_evidence_contract':coverage['native_evidence_contract'],
        'scientific_admission':False,'production_admission':False}


def prepare_assembly(context,coverage,native_build_directory,output_directory):
    """Create headers + exact host compile argv after checking generated input bytes."""
    validate_coverage(coverage,context)
    directory=Path(native_build_directory).resolve()
    if read_json(directory/'BUILD.json')!=context.manifest: raise JoinError('native build manifest changed')
    header=native.read_bytes(directory/'frozen107_generated.hpp',MAX_BYTES)
    if hashlib.sha256(header).hexdigest()!=context.manifest['generated_header_sha256']:
        raise JoinError('frozen input header byte identity mismatch')
    constants={'WU088_ARCHIVE_SHA256':context.identity['archive_sha256'],
        'WU088_RECORD_SHA256':context.identity['input_record_sha256'],
        'WU088_BUILD_SOURCE_SHA256':context.identity['native_source_sha256']}
    expected=('#pragma once\n'+''.join('#define '+k+' "'+sha(v)+'"\n' for k,v in constants.items())).encode()
    if native.read_bytes(directory/'build_identity.hpp',4096)!=expected: raise JoinError('native build identity header mismatch')
    code=initializer(coverage).encode()
    compiler=context.manifest['compiler']
    if type(compiler) is not dict or type(compiler.get('path')) is not str or not Path(compiler['path']).is_absolute():
        raise JoinError('recorded absolute compiler identity required')
    sha(compiler['sha256'])
    out=Path(output_directory).resolve();out.mkdir(parents=False,exist_ok=False)
    (out/'frozen107_generated.hpp').write_bytes(header);(out/'build_identity.hpp').write_bytes(expected)
    (out/'primitive_rectangles_generated.hpp').write_bytes(code)
    prefix=Path(context.manifest['prefix']);old=ROOT.parent/'gap_closure_20261001_g0_g6_v1'
    command=[compiler['path'],*native.FLAGS,'-I'+str(out),'-I'+str(old/'validated_callback'),'-I'+str(prefix/'include'),
        str(HERE/'assembly_exporter.cpp'),str(old/'validated_callback/assembly.cpp'),str(old/'validated_callback/callback.cpp'),
        '-L'+str(prefix/'lib'),'-Wl,-rpath,'+str(prefix/'lib'),'-lflint','-lmpfr','-lgmp','-o',str(out/'assembly_exporter')]
    receipt={'schema':'WU088_ASSEMBLY_PREPARATION_V1','status':'PREPARED_NATIVE_UNCOMPILED',
        'coverage_sha256':coverage['coverage_sha256'],'execution_identity_sha256':context.sha256,
        'generated_header_sha256':hashlib.sha256(header).hexdigest(),
        'primitive_header_sha256':hashlib.sha256(code).hexdigest(),'compile_command':command,
        'assembly_exporter_sha256':hashlib.sha256((HERE/'assembly_exporter.cpp').read_bytes()).hexdigest(),
        'compiler_identity_to_reverify':compiler,'backend_provenance_sha256':context.identity['backend_provenance_sha256'],
        'build_manifest_sha256':context.manifest['manifest_sha256'],
        'native_compiled':False,'native_executed':False,'scientific_admission':False,'production_admission':False}
    write_new(out/'PREPARATION.json',receipt)
    return receipt


def read_json(path):
    def pairs(values):
        out={}
        for key,value in values:
            if key in out: raise JoinError('duplicate JSON key')
            out[key]=value
        return out
    def refuse(_): raise JoinError('JSON float/nonfinite forbidden')
    with Path(path).open('rb') as stream: data=stream.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES: raise JoinError('document byte cap')
    try: return json.loads(data,object_pairs_hook=pairs,parse_float=refuse,parse_constant=refuse)
    except (ValueError,UnicodeError,RecursionError) as exc: raise JoinError('invalid JSON') from exc


def write_new(path,value):
    data=canonical(value)+b'\n'
    if len(data)>MAX_BYTES: raise JoinError('output byte cap')
    with Path(path).open('xb') as stream: stream.write(data)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('join','collect','prepare','import'))
    parser.add_argument('--plan',required=True); parser.add_argument('--build-manifest',required=True)
    parser.add_argument('--limits',required=True); parser.add_argument('--npz')
    parser.add_argument('--endpoint-result'); parser.add_argument('--interior-result')
    parser.add_argument('--joined-list'); parser.add_argument('--initializer'); parser.add_argument('--output',required=True)
    parser.add_argument('--coverage'); parser.add_argument('--build-directory'); parser.add_argument('--final-rectangles')
    parser.add_argument('--precision',type=int,default=128)
    args=parser.parse_args()
    try:
        archive=endpoint.archive_bytes(args.npz)
        context=Context(read_json(args.plan),read_json(args.build_manifest),read_json(args.limits),source_archive_bytes=archive)
        if args.mode=='join':
            if not args.endpoint_result or not args.interior_result: raise JoinError('two component results required')
            result=join_task(context,read_json(args.endpoint_result),read_json(args.interior_result))
        elif args.mode=='collect':
            paths=read_json(args.joined_list)
            if type(paths) is not list or len(paths)!=COUNT or any(type(p) is not str for p in paths): raise JoinError('2592 result paths required')
            result=collect(context,(read_json(path) for path in paths))
            if args.initializer:
                code=initializer(result)
                with Path(args.initializer).open('x') as stream: stream.write(code)
        elif args.mode=='prepare':
            if not args.coverage or not args.build_directory: raise JoinError('coverage and native build directory required')
            result=prepare_assembly(context,read_json(args.coverage),args.build_directory,args.output)
            print(json.dumps({'status':result['status'],'scientific_admission':False,'production_admission':False}))
            return 0
        else:
            if not args.coverage or not args.final_rectangles: raise JoinError('coverage and final native rectangles required')
            result=import_final_disks(context,read_json(args.coverage),read_json(args.final_rectangles),precision=args.precision)
        write_new(args.output,result)
        print(json.dumps({'status':result['status'],'scientific_admission':False,'production_admission':False}))
        return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print(json.dumps({'status':'JOIN_REFUSED','reason':str(exc),'scientific_admission':False}),file=sys.stderr)
        return 2


if __name__=='__main__': raise SystemExit(main())
