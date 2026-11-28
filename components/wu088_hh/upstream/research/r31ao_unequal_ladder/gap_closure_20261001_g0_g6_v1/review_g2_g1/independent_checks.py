"""Read-only artifact review; hand-encoded synthetic bytes, no HH inputs."""
import hashlib
import json
import random
from dataclasses import replace
from fractions import Fraction

from exact_raw_decoder import LayoutAuthority, decode_npy_bytes, DecodeError


def npy(payload, descr, shape=(1,), fortran=False):
    header = repr({'descr':descr, 'fortran_order':fortran, 'shape':shape}).encode()
    header += b' ' * ((-10-len(header)-1) % 64) + b'\n'
    return b'\x93NUMPY\x01\x00' + len(header).to_bytes(2,'little') + header + payload


def auth(data, layout, endian='little', offset=0, scope='SYNTHETIC_FIXTURE_ONLY'):
    return LayoutAuthority(layout, endian, 16, offset, 'real_imag', scope,
                           'REVIEW_SYNTHETIC_ONLY', ('0'*64,), hashlib.sha256(data).hexdigest())


def main():
    rng = random.Random(2601001)
    count = 0
    for _ in range(200):
        sign, exponent, fraction = rng.randrange(2),rng.randrange(1,2047),rng.getrandbits(52)
        binary64 = (sign<<63)|(exponent<<52)|fraction
        extended_exponent = exponent-1023+16383
        x87 = (sign<<79)|(extended_exponent<<64)|((1<<52|fraction)<<11)
        binary128 = (sign<<127)|(extended_exponent<<112)|(fraction<<60)
        reference = decode_npy_bytes(npy(binary64.to_bytes(8,'little'),'<f8'))
        for layout, word, meaningful in [('x87_80',x87,10),('ieee_binary128',binary128,16)]:
            for endian,prefix in [('little','<'),('big','>')]:
                for offset in ([0,3,6] if layout=='x87_80' else [0]):
                    pad=bytes(rng.randrange(256) for _ in range(16-meaningful))
                    payload=pad[:offset]+word.to_bytes(meaningful,endian)+pad[offset:]
                    data=npy(payload,prefix+'f16')
                    got=decode_npy_bytes(data,authority=auth(data,layout,endian,offset))
                    assert got.values_c_order==reference.values_c_order
                    assert got.canonical_sha256==reference.canonical_sha256
                    count+=1
    # This demonstrates a trust boundary, not historical admission: a caller
    # can relabel identical fixture metadata. The module documentation warns
    # that validating an authority structure does not validate its evidence.
    data=npy(((16383<<64)|(1<<63)).to_bytes(10,'little')+b'ABCDEF','<f16')
    forged=auth(data,'x87_80',scope='HISTORICAL_PRODUCER_LAYOUT_REVIEWED')
    out=decode_npy_bytes(data,authority=forged)
    assert out.values_c_order==(Fraction(1),)
    assert out.authority_scope=='HISTORICAL_PRODUCER_LAYOUT_REVIEWED'
    refused=0
    for bad in [b'\x00'*7,b'\x00'*9]:
        try:
            decode_npy_bytes(npy(bad,'<f8'))
        except DecodeError:
            refused+=1
    assert refused==2
    return {'cross_format_equivalence_checks':count,'checked_endianness':['little','big'],
            'x87_offsets':[0,3,6],'all_passed':True,
            'authority_scope_is_caller_asserted_not_evidence_admission':True,
            'forged_historical_scope_structurally_accepted':True,
            'actual_historical_data_accessed':False,'project_level_independent_review_admitted':False}


if __name__=='__main__':
    print(json.dumps(main(),indent=2))
