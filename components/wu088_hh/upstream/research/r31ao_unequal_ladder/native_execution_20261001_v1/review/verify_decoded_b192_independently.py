"""Independent bit-formula check of the bounded B192 decoder outputs.

This verifier does not import the production decoder or NumPy. It validates
the already reviewed exact archive scope, then compares each exported dyadic.
"""
import ast
from fractions import Fraction as Q
import hashlib
import itertools
import json
from pathlib import Path
import zipfile

HERE=Path(__file__).resolve().parent
INTAKE=HERE.parent/'intake'
REPO=HERE.parents[3]
RAW=REPO.parents[1]/'native_execution_intake/b192_raw'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def real(slot,extended):
    bits=int.from_bytes(slot,'little')
    if extended:
        significand=bits&((1<<64)-1)
        exponent=(bits>>64)&0x7fff
        negative=bool((bits>>79)&1)
        assert exponent!=0x7fff
        assert bool(significand>>63)==bool(exponent)
        power=(exponent if exponent else 1)-16383-63
        padding=slot[10:].hex()
    else:
        exponent=(bits>>52)&0x7ff
        negative=bool(bits>>63)
        assert exponent!=0x7ff
        significand=(bits&((1<<52)-1))+(1<<52 if exponent else 0)
        power=(exponent if exponent else 1)-1023-52
        padding=''
    value=Q(-significand if negative else significand)*Q(2)**power
    return value,negative and not significand,padding


def main():
    review=json.loads((HERE/'B192_BYTE_AND_SOURCE_REVIEW.json').read_text())
    assert review['bounded_historical_layout_admitted'] is True
    approved={r['archive']:r['archive_sha256'] for r in review['npz_member_binding_observations']}
    bindings=json.loads((INTAKE/'B192_MEMBER_BINDINGS.json').read_text())
    decoded=INTAKE/'decoded'
    manifest=json.loads((decoded/'FILE_HASHES.json').read_text())
    for item in manifest:
        raw=(decoded/item['path']).read_bytes()
        assert len(raw)==item['bytes'] and sha(raw)==item['sha256']
    element_total=component_total=0;rows=[]
    for archive_record in bindings['records']:
        name=archive_record['local_basename']
        archive_bytes=(RAW/name).read_bytes()
        assert sha(archive_bytes)==approved[name]
        with zipfile.ZipFile(RAW/name) as archive:
            for member in archive_record['npy_members']:
                raw=archive.read(member['member']);assert sha(raw)==member['sha256']
                assert raw[:8]==b'\x93NUMPY\x01\x00'
                size=int.from_bytes(raw[8:10],'little')
                h=ast.literal_eval(raw[10:10+size].decode('ascii'));payload=raw[10+size:]
                if h['descr']=='<i8':continue
                extended=h['descr'] in ('<f16','<c32')
                complex_value=h['descr']=='<c32'
                scalar_size=16 if extended else 8
                item_size=scalar_size*(2 if complex_value else 1)
                folder=decoded/archive_record['role'];stem=member['member'].removesuffix('.npy')
                export=json.loads((folder/(stem+'.exact_dyadic.json')).read_text())
                provenance=json.loads((folder/(stem+'.provenance.json')).read_text())
                shape=h['shape'];assert export['shape']==list(shape)
                count=0
                for idx in itertools.product(*(range(n) for n in shape)):
                    if h['fortran_order']:
                        physical=0;stride=1
                        for i,n in zip(idx,shape):physical+=i*stride;stride*=n
                    else:
                        physical=0
                        for i,n in zip(idx,shape):physical=physical*n+i
                    item=payload[physical*item_size:(physical+1)*item_size]
                    parts=[real(item[s:s+scalar_size],extended) for s in range(0,item_size,scalar_size)]
                    values=[p[0] for p in parts]
                    if not complex_value:values.append(Q(0))
                    exported=[Q(int(mantissa,16))*Q(2)**power for mantissa,power in export['values'][count]]
                    assert values==exported
                    assert provenance['negative_zero_c_order'][count]==[p[1] for p in parts]
                    assert provenance['padding_hex_c_order'][count]==[p[2] for p in parts]
                    count+=1;component_total+=len(parts)
                assert count==len(export['values'])
                element_total+=count
                rows.append({'archive':name,'member':member['member'],'logical_elements':count,
                             'exact_bit_formula_matches':True,'padding_and_signed_zero_match':True,
                             'semantic_memory_order_matches':True})
    assert len(rows)==12 and element_total==4586
    result={'status':'PASS_INDEPENDENT_RAW_BITS_TO_EXPORTED_DYADICS',
            'review_sha256':sha((HERE/'B192_BYTE_AND_SOURCE_REVIEW.json').read_bytes()),
            'decode_result_sha256':sha((decoded/'DECODE_RESULT.json').read_bytes()),
            'runner_sha256':sha((INTAKE/'decode_reviewed_b192.py').read_bytes()),
            'checked_manifest_files':len(manifest),'checked_members':len(rows),
            'checked_logical_elements':element_total,'checked_real_components':component_total,
            'details':rows,'production_decoder_imported':False,'numpy_imported':False,
            'host_float_casts':0,'source_producer_rerun':False,'continuum_error_certified':False,
            'scientific_admission':False,'production_admission':False}
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=='__main__':main()
