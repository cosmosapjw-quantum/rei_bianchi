"""Strict exact NPZ -> rational record -> typed C++ initializer.

Reading this module consumes canonical header metadata only. Functions never
grant execution authorization or scientific certificate admission.
"""
from __future__ import annotations
import argparse,hashlib,io,json,re,stat,zipfile,zlib
from fractions import Fraction
from pathlib import Path
from exact_raw_decoder.decoder import decode_npy_bytes,DecodeError

MAX_ARCHIVE=1024*1024
MAX_TOTAL=256*1024
MAX_MEMBER=64*1024
MAX_RATIO=500
BINDING_SHA256='3ca2c676095898cbe30d6fcc388c0e1d644fccd8b235dfe076be8e4001209ed4'
HEADER_SPEC_SHA256='71ff0c2315f4281835ff7c2736553dc9abbe4324e538e4a634bf54430b2534c8'


class AdapterError(ValueError): pass


def sha(data):return hashlib.sha256(data).hexdigest()


def _spec():
    raw=Path(__file__).with_name('FROZEN107_HEADER_SPEC.json').read_bytes()
    if sha(raw)!=HEADER_SPEC_SHA256:raise AdapterError('derived header metadata hash mismatch')
    model=json.loads(raw)
    if model['canonical_binding_sha256']!=BINDING_SHA256:raise AdapterError('canonical binding identity mismatch')
    spec={r['member']:{k:r[k] for k in ('shape','descr','fortran_order','payload_sha256')} for r in model['members']}
    return model['archive_sha256'],spec


FROZEN107_ARCHIVE_SHA256,SPEC=_spec()
NATIVE_FIELDS={'exponents':'exponents','s_C':'s_C','p_C':'p_C','C':'donor_C','phase_E':'phase_E','pref':'pref','v':'v'}


def _record_digest(record):
    body={k:v for k,v in record.items() if k!='canonical_record_sha256'}
    return sha(json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii'))


def decode_npz(data:bytes,*,expected_archive_sha256:str,scope:str):
    if type(data) is not bytes or len(data)>MAX_ARCHIVE:
        raise AdapterError('archive must be bytes within 1 MiB cap')
    if type(expected_archive_sha256) is not str or not re.fullmatch('[0-9a-f]{64}',expected_archive_sha256):
        raise AdapterError('explicit external lowercase SHA256 required')
    if sha(data)!=expected_archive_sha256:raise AdapterError('external archive SHA256 mismatch')
    if scope not in ('SYNTHETIC_ONLY','FROZEN107_PINNED'):raise AdapterError('explicit recognized scope required')
    if scope=='FROZEN107_PINNED' and expected_archive_sha256!=FROZEN107_ARCHIVE_SHA256:
        raise AdapterError('archive is not the pinned Frozen107 input')
    fields={}
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            infos=z.infolist()
            if len(infos)!=len(SPEC):raise AdapterError('required exact ZIP member count mismatch')
            if any(i.orig_filename!=i.filename or '\0' in i.orig_filename for i in infos):
                raise AdapterError('truncated or noncanonical original ZIP member path')
            names=[i.filename for i in infos]
            if len(set(names))!=len(names):raise AdapterError('duplicate ZIP member path')
            if set(names)!=set(SPEC):raise AdapterError('missing, extra or noncanonical member path')
            if sum(i.file_size for i in infos)>MAX_TOTAL:raise AdapterError('uncompressed archive budget exceeded')
            for info in infos:
                mode=info.external_attr>>16
                if info.is_dir() or stat.S_IFMT(mode) not in (0,stat.S_IFREG):raise AdapterError('nonregular ZIP entry')
                if info.flag_bits&1:raise AdapterError('encrypted ZIP entries unsupported')
                if info.compress_type not in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED):
                    raise AdapterError('unsupported bounded compression')
                if info.file_size>MAX_MEMBER or info.file_size<0 or info.compress_size<0:
                    raise AdapterError('member size cap exceeded')
                if info.file_size>MAX_RATIO*max(info.compress_size,1):raise AdapterError('compression ratio cap exceeded')
                with z.open(info) as member:raw=member.read(MAX_MEMBER+1)
                if len(raw)!=info.file_size or len(raw)>MAX_MEMBER:raise AdapterError('member length mismatch or cap exceeded')
                decoded=decode_npy_bytes(raw,max_elements=2401)
                wanted=SPEC[info.filename]
                header=decoded.header
                if (header.descr!=wanted['descr'] or header.descr!='<f8' or
                    list(decoded.shape)!=wanted['shape'] or header.fortran_order!=wanted['fortran_order']):
                    raise AdapterError('pinned binary64 shape/order/header mismatch')
                if scope=='FROZEN107_PINNED' and decoded.payload_sha256!=wanted['payload_sha256']:
                    raise AdapterError('pinned member payload SHA256 mismatch')
                name=info.filename[:-4]
                fields[name]={'shape':list(decoded.shape),'values':[str(q) for q in decoded.values_c_order],
                    'memory_order':'C_SEMANTIC_INDEX_ORDER','stored_fortran_order':header.fortran_order,
                    'negative_zero_c_order':[bool(x[0]) for x in decoded.negative_zero_c_order],
                    'raw_npy_sha256':decoded.raw_npy_sha256,'payload_sha256':decoded.payload_sha256,
                    'canonical_array_sha256':decoded.canonical_sha256}
    except (zipfile.BadZipFile,NotImplementedError,RuntimeError,EOFError,OSError,DecodeError,zlib.error) as exc:
        raise AdapterError('malformed or unsupported NPZ/NPY: '+str(exc)) from exc
    record={'schema':'WU088_FROZEN107_EXACT_RATIONAL_RECORD_V1','scope':scope,
        'archive_sha256':expected_archive_sha256,'canonical_binding_sha256':BINDING_SHA256,
        'input_byte_pin_verified':scope=='FROZEN107_PINNED','execution_authorized':False,
        'scientific_authority':False,'fields':fields,'z_exact':'3/4',
        'donor_nonzero_count':sum(x!='0' for x in fields['C']['values']),
        'decoder':'exact_raw_decoder.decoder.decode_npy_bytes',
        'native_target':'validated_callback/assembly.hpp::AssemblyInputs'}
    record['canonical_record_sha256']=_record_digest(record)
    return record


def generate_cpp(record,*,source_archive_bytes=None):
    if record.get('schema')!='WU088_FROZEN107_EXACT_RATIONAL_RECORD_V1' or record.get('canonical_record_sha256')!=_record_digest(record):
        raise AdapterError('record schema or digest mismatch')
    if record.get('canonical_binding_sha256')!=BINDING_SHA256 or record.get('z_exact')!='3/4':
        raise AdapterError('binding or fixed geometry changed')
    scope=record.get('scope')
    if scope not in ('SYNTHETIC_ONLY','FROZEN107_PINNED'):raise AdapterError('record scope invalid')
    if not re.fullmatch('[0-9a-f]{64}',record.get('archive_sha256','')):raise AdapterError('invalid archive identity')
    if scope=='FROZEN107_PINNED' and record['archive_sha256']!=FROZEN107_ARCHIVE_SHA256:
        raise AdapterError('record has wrong Frozen107 identity')
    if scope=='FROZEN107_PINNED':
        if type(source_archive_bytes) is not bytes:
            raise AdapterError('pinned code generation requires original archive bytes')
        bound=decode_npz(source_archive_bytes,expected_archive_sha256=FROZEN107_ARCHIVE_SHA256,scope='FROZEN107_PINNED')
        if record!=bound:raise AdapterError('record does not equal exact decoding of pinned archive bytes')
    expected_names={name[:-4] for name in SPEC}
    if set(record['fields'])!=expected_names:raise AdapterError('record field set mismatch')
    for name,field in record['fields'].items():
        wanted=SPEC[name+'.npy'];count=1
        for n in wanted['shape']:count*=n
        if field.get('shape')!=wanted['shape'] or field.get('memory_order')!='C_SEMANTIC_INDEX_ORDER' or len(field['values'])!=count:
            raise AdapterError('record semantic shape/order mismatch')
        for token in field['values']:
            if type(token) is not str or len(token)>1024 or not re.fullmatch(r'-?(0|[1-9][0-9]*)(/[1-9][0-9]*)?',token):
                raise AdapterError('invalid bounded rational token')
            q=Fraction(token)
            if str(q)!=token or q.denominator&(q.denominator-1):raise AdapterError('canonical dyadic token required')
    function='load_synthetic_rational_record' if scope=='SYNTHETIC_ONLY' else 'load_frozen107_rational_record'
    lines=['#pragma once','#include "assembly.hpp"',
           '// Generated exact assignments; backend runtime and source-input admission remain separate.',
           '// scope='+scope,'// archive_sha256='+record['archive_sha256'],
           '// canonical_record_sha256='+record['canonical_record_sha256'],
           'inline void '+function+'(wu088::AssemblyInputs &out) {','    out=wu088::AssemblyInputs{};']
    for field,target in NATIVE_FIELDS.items():
        values=record['fields'][field]['values']
        for i,token in enumerate(values):
            slot=target if field in ('pref','v') else target+'['+str(i)+']'
            lines.append('    out.'+slot+'.set("'+token+'");')
    lines+=['    out.z.set("3/4");','}']
    return '\n'.join(lines)+'\n'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('npz');p.add_argument('--expected-sha256',required=True)
    p.add_argument('--scope',choices=['SYNTHETIC_ONLY','FROZEN107_PINNED'],required=True)
    p.add_argument('--record-out',required=True);p.add_argument('--cpp-out')
    a=p.parse_args();source=Path(a.npz)
    if source.stat().st_size>MAX_ARCHIVE:raise AdapterError('archive exceeds cap before reading')
    with source.open('rb') as f:archive=f.read(MAX_ARCHIVE+1)
    record=decode_npz(archive,expected_archive_sha256=a.expected_sha256,scope=a.scope)
    cpp=generate_cpp(record,source_archive_bytes=archive) if a.cpp_out else None
    with Path(a.record_out).open('x') as f:json.dump(record,f,indent=2);f.write('\n')
    if a.cpp_out:
        with Path(a.cpp_out).open('x') as f:f.write(cpp)


if __name__=='__main__':main()
