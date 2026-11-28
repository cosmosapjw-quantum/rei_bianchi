"""Toy NPZ only; no Frozen107 payload access or native compilation."""
import copy
import hashlib
import io
import json
import struct
import warnings
import zipfile

from frozen_input.adapter import decode_npz, generate_cpp, AdapterError, SPEC, _record_digest
from frozen_input.test_adapter import fixture, npy


def decoded(data):
    return decode_npz(data, expected_archive_sha256=hashlib.sha256(data).hexdigest(),scope='SYNTHETIC_ONLY')


def archive(entries):
    stream=io.BytesIO()
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for info,data in entries:z.writestr(info,data)
    return stream.getvalue()


def main():
    entries=[(name,npy(name)) for name in SPEC]
    cases={}
    # Preserve member count so duplicate/path-specific gates are reached.
    cases['same_count_duplicate']=archive([(name,data) for name,data in entries if name!='v.npy']+[('pref.npy',npy('pref.npy'))])
    cases['same_count_path_traversal']=archive([(('../escape.npy' if name=='v.npy' else name),data) for name,data in entries])
    link=zipfile.ZipInfo('pref.npy');link.create_system=3;link.external_attr=0o120777<<16
    cases['symlink_entry']=archive([(link if name=='pref.npy' else name,data) for name,data in entries])
    cases['ratio_budget']=fixture({'pref.npy':b'x'*60000})
    cases['aggregate_size_budget']=fixture({name:b'x'*64000 for name in list(SPEC)[:5]})
    raw=bytearray(fixture(compression=zipfile.ZIP_STORED))
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        info=z.getinfo('pref.npy')
        offset=info.header_offset
        nlen,elen=struct.unpack_from('<HH',raw,offset+26)
        raw[offset+30+nlen+elen+info.file_size-1]^=1
    cases['crc_corruption']=bytes(raw)
    rejections={}
    for name,data in cases.items():
        try:decoded(data)
        except AdapterError as exc:rejections[name]=str(exc)
        else:raise AssertionError('unsafe ZIP case accepted: '+name)
    base=decoded(fixture())
    injections=[]
    for token in ['1\");system(\"x','0\n#include <x>','-0','01','1/3','1/0']:
        record=copy.deepcopy(base)
        record['fields']['pref']['values'][0]=token
        record['canonical_record_sha256']=_record_digest(record)
        try:generate_cpp(record)
        except AdapterError:injections.append(token)
        else:raise AssertionError('noncanonical/injection token accepted')
    cpp=generate_cpp(base)
    # The synthetic s_C/p_C fixture value at logical (ia,j) is ia*12+j+1.
    for field in ('s_C','p_C'):
        for ia,j in [(0,1),(1,0),(2,7),(11,11)]:
            index=ia*12+j
            assert f'out.{field}[{index}].set("{index+1}");' in cpp
    for i,j,k in [(0,0,0),(0,1,2),(1,0,0),(8,8,8)]:
        index=(i*9+j)*9+k
        assert f'out.donor_C[{index}].set("{index+1}");' in cpp
    assert 'out.z.set("3/4");' in cpp
    assert base['execution_authorized'] is False and base['scientific_authority'] is False
    return {'ZIP_refusals':rejections,'rational_token_refusals_after_rehash':injections,
            'Fortran_to_assembly_flat_index_checks':8,'donor_flat_index_checks':4,
            'synthetic_record_flags_false':True,'native_compile_performed':False,
            'actual_Frozen107_bytes_accessed':False}


if __name__=='__main__':print(json.dumps(main(),indent=2))
