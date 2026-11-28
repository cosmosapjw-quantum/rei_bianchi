"""Compile/run the unchanged exporter with explicit zero primitive test values.

No endpoint/interior result or coverage receipt is manufactured. The synthetic
initializer supplies zero to every slot solely to exercise linear assembly.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--prefix',required=True);cli.add_argument('--provenance',required=True)
    cli.add_argument('--parameter-build',required=True);cli.add_argument('--output-directory',required=True)
    args=cli.parse_args()
    here=Path(__file__).resolve().parent
    spec=importlib.util.spec_from_file_location('assembly_fixture_host',here.parents[1]/'assembly_host.py')
    h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    join,gate,_=h.configured_modules()
    prefix=Path(args.prefix).resolve();provenance=Path(args.provenance).resolve()
    backend=gate.verify_backend(provenance,prefix)
    parameter_build=Path(args.parameter_build).resolve();manifest=h.read_json(parameter_build/'BUILD.json')
    h.sealed(manifest,'manifest_sha256',manifest['manifest_sha256'])
    compiler=manifest['compiler']
    if gate.file_identity(compiler['path'],compiler['sha256'])!=compiler:raise ValueError('compiler identity changed')
    header=h.read_bytes(parameter_build/'frozen107_generated.hpp')
    if h.digest(header)!=manifest['generated_header_sha256']:raise ValueError('Frozen107 parameter header identity mismatch')
    identity_header=h.read_bytes(parameter_build/'build_identity.hpp',4096)
    constants={'WU088_ARCHIVE_SHA256':manifest['archive_sha256'],'WU088_RECORD_SHA256':manifest['input_record_sha256'],
               'WU088_BUILD_SOURCE_SHA256':manifest['source']['sha256']}
    expected_header=('#pragma once\n'+''.join('#define '+k+' "'+h.sha(v)+'"\n' for k,v in constants.items())).encode()
    if identity_header!=expected_header:raise ValueError('parameter build identity header mismatch')
    source=h.PRODUCTION/'primitive_join/assembly_exporter.cpp';source_hash=h.digest(h.read_bytes(source))
    fixture={'schema':'WU088_ZERO_PRIMITIVE_EXPORTER_FIXTURE_V1',
        'scope':'SYNTHETIC_ZERO_PRIMITIVES_WITH_FROZEN107_PARAMETER_HEADER',
        'primitive_slot_count':2592,'each_primitive_value':'EXACT_ZERO_COMPLEX',
        'parameter_archive_sha256':manifest['archive_sha256'],'parameter_record_sha256':manifest['input_record_sha256'],
        'parameter_header_sha256':h.digest(header),'assembly_exporter_source_sha256':source_hash,
        'actual_HH_integrals_evaluated':0,'actual_primitive_coverage_claimed':False,
        'scientific_admission':False,'production_admission':False}
    fixture_sha=h.digest(h.canonical(fixture))
    execution_sha=h.digest(h.canonical({'fixture_sha256':fixture_sha,'precision_bits':128,'scope':'SYNTHETIC_EXPORTER_SMOKE_ONLY'}))
    generated=['#pragma once','#include "assembly.hpp"',
        '// SYNTHETIC ZERO PRIMITIVE FIXTURE. No HH integral/coverage receipt.',
        '#define WU088_PRIMITIVE_COVERAGE_SHA256 "'+fixture_sha+'"',
        '#define WU088_PRIMITIVE_EXECUTION_SHA256 "'+execution_sha+'"',
        '#define WU088_PRIMITIVE_ARCHIVE_SHA256 "'+manifest['archive_sha256']+'"',
        '#define WU088_PRIMITIVE_RECORD_SHA256 "'+manifest['input_record_sha256']+'"',
        '#define WU088_ASSEMBLER_SOURCE_SHA256 "'+source_hash+'"',
        'inline void load_real_domain_primitives(wu088::RealDomainPrimitiveIntegrals& raw,slong) {',
        ' for(auto& cell:raw.unnormalized_real_domain_integrals) acb_zero(cell.value);','}']
    primitive_header=('\n'.join(generated)+'\n').encode()
    out=Path(args.output_directory).resolve();out.mkdir(parents=False,exist_ok=False)
    for name,data in [('frozen107_generated.hpp',header),('build_identity.hpp',identity_header),
                      ('primitive_rectangles_generated.hpp',primitive_header)]:
        with (out/name).open('xb') as stream:stream.write(data)
    h.write_new(out/'SYNTHETIC_FIXTURE_SCOPE.json',fixture)
    command=h.compile_command(join,compiler['path'],out,prefix)
    build=h.bounded_process(command,h.environment(prefix/'lib'),h.BUILD_LIMITS,out/'build.stdout',out/'build.stderr')
    h.write_new(out/'BUILD_PROCESS.json',build)
    if build['exit_code']!=0 or build['timed_out']:raise RuntimeError('synthetic exporter compile failed; logs retained')
    binary=out/'assembly_exporter'
    linkage,link_process=h.linkage({'prefix':prefix,'gate':gate,'backend':backend},binary,out)
    run=h.bounded_process([str(binary),'128'],h.environment(prefix/'lib'),h.RUN_LIMITS,out/'native.stdout',out/'native.stderr')
    h.write_new(out/'RUN_PROCESS.json',run)
    if run['exit_code']!=0 or run['timed_out']:raise RuntimeError('synthetic exporter run failed; logs retained')
    final=h.parse_json(h.read_bytes(out/'native.stdout'))
    h.exact_keys(final,('schema','coverage_sha256','execution_identity_sha256','archive_sha256','input_record_sha256',
        'assembler_source_sha256','precision_bits','D_col','D_row','scientific_admission','production_admission'))
    fixed={'schema':'WU088_FINAL_D_RECTANGLES_V1','coverage_sha256':fixture_sha,'execution_identity_sha256':execution_sha,
        'archive_sha256':manifest['archive_sha256'],'input_record_sha256':manifest['input_record_sha256'],
        'assembler_source_sha256':source_hash,'precision_bits':128,'scientific_admission':False,'production_admission':False}
    for key,value in fixed.items():
        if type(final[key]) is not type(value) or final[key]!=value:raise AssertionError('exporter binding mismatch: '+key)
    complex_entries=scalar_intervals=0
    for name,rows,cols in [('D_col',47,2),('D_row',2,47)]:
        matrix=final[name]
        if type(matrix) is not list or len(matrix)!=rows or any(type(row) is not list or len(row)!=cols for row in matrix):
            raise AssertionError('exported matrix shape mismatch')
        for row in matrix:
            for rectangle in row:
                h.exact_keys(rectangle,('real','imag'))
                complex_entries+=1
                for part in ('real','imag'):
                    lo,hi=join.native.dyadic_interval(rectangle[part])
                    if lo!=0 or hi!=0:raise AssertionError('linear zero-primitive oracle failed')
                    scalar_intervals+=1
    if (complex_entries,scalar_intervals)!=(188,376):raise AssertionError('entry coverage mismatch')
    if h.digest(h.read_bytes(source))!=source_hash:raise RuntimeError('exporter source changed during compile/run')
    gate.verify_backend(provenance,prefix)
    record={'schema':'WU088_NATIVE_EXPORTER_SYNTHETIC_VERIFICATION_V1','status':'PASS',
        'created_utc':datetime.now(timezone.utc).isoformat(),'scope':fixture['scope'],
        'native_exporter_compiled':True,'native_exporter_executed':True,'actual_HH_integrals_evaluated':0,
        'actual_primitive_coverage_claimed':False,'actual_HH_final_D_claimed':False,
        'exact_zero_complex_entries':complex_entries,'exact_zero_scalar_intervals':scalar_intervals,
        'D_col_shape':[47,2],'D_row_shape':[2,47],'precision_bits':128,
        'fixture_sha256':fixture_sha,'execution_fixture_sha256':execution_sha,
        'coverage_field_semantics':'Synthetic fixture descriptor hash; not a successful HH coverage receipt',
        'compiler':compiler,'compiler_version':manifest['compiler_version'],
        'backend_provenance':h.identity(provenance),'backend_byte_chain_status':backend['verification']['status'],
        'source_sha256':{str(p.relative_to(h.LADDER)):h.digest(h.read_bytes(p)) for p in
            (source,h.OLD/'validated_callback/assembly.cpp',h.OLD/'validated_callback/callback.cpp')},
        'generated_header_sha256':h.digest(header),'synthetic_primitive_header_sha256':h.digest(primitive_header),
        'binary':h.identity(binary),'linkage':linkage,'build_process':build,'run_process':run,'linkage_process':link_process,
        'host':{'platform':platform.platform(),'machine':platform.machine()},
        'scientific_admission':False,'production_admission':False}
    h.write_new(out/'VERIFICATION.json',record)
    print(json.dumps({k:record[k] for k in ('status','native_exporter_compiled','native_exporter_executed',
        'exact_zero_complex_entries','exact_zero_scalar_intervals','actual_HH_final_D_claimed')}))


if __name__=='__main__':main()
