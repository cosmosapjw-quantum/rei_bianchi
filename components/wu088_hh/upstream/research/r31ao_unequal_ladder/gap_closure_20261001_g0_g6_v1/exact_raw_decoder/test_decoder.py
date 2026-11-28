"""Synthetic-only fixtures. Independent binary64 oracle uses stdlib struct in tests."""
import hashlib
import json
import random
import struct
import unittest
from unittest.mock import patch
from dataclasses import replace
from fractions import Fraction as F

from exact_raw_decoder import DecodeError, LayoutAuthority, decode_npy_bytes, inspect_npy_header


def npy(payload, descr='<f8', shape=(1,), order=False, version=(1, 0), header=None):
    lead = b'\x93NUMPY' + bytes(version)
    width = 2 if version == (1, 0) else 4
    text = header if header is not None else repr({'descr': descr, 'fortran_order': order, 'shape': shape})
    enc = text.encode('utf8' if version == (3, 0) else 'latin1')
    enc += b' ' * ((-(len(lead) + width + len(enc) + 1)) % 64) + b'\n'
    return lead + len(enc).to_bytes(width, 'little') + enc + payload


def words(*values, size=8, endian='little'):
    return b''.join(v.to_bytes(size, endian) for v in values)


def authority(data, layout='x87_80', endian='little', value_offset=0):
    return LayoutAuthority(layout=layout, byte_order=endian, component_bytes=16,
        value_offset=value_offset, complex_component_order='real_imag',
        scope='SYNTHETIC_FIXTURE_ONLY', evidence_id='HAND_ENCODED_GOLDEN_FIXTURE',
        evidence_sha256=(hashlib.sha256(b'synthetic fixture specification').hexdigest(),),
        bound_npy_sha256=hashlib.sha256(data).hexdigest())


def x87(significand, exponent, sign=0, padding=b'\0'*6, endian='little'):
    return ((sign << 79) | (exponent << 64) | significand).to_bytes(10, endian) + padding


class DecoderTests(unittest.TestCase):
    def test_binary64_goldens_all_versions(self):
        p = words(0x3ff0000000000000, 0xc004000000000000, 1, 0x0010000000000000,
                  0x7fefffffffffffff, 0, 0x8000000000000000)
        want = (F(1), F(-5, 2), F(1, 1 << 1074), F(1, 1 << 1022),
                F((1 << 53)-1) * (1 << 971), F(0), F(0))
        for version in ((1, 0), (2, 0), (3, 0)):
            with self.subTest(version=version):
                d = decode_npy_bytes(npy(p, shape=(7,), version=version))
                self.assertEqual(d.values_c_order, want)
                self.assertEqual(d.negative_zero_c_order, ((False,),)*6 + ((True,),))

    def test_binary64_independent_oracle(self):
        rng = random.Random(20261001)
        bits = [rng.getrandbits(64) for _ in range(1000)]
        bits = [b for b in bits if (b >> 52) & 2047 != 2047]
        d = decode_npy_bytes(npy(words(*bits), shape=(len(bits),)))
        expected = tuple(F(*struct.unpack('<d', words(b))[0].as_integer_ratio()) for b in bits)
        self.assertEqual(d.values_c_order, expected)

    def test_complex128_big_endian(self):
        p = words(0x3ff0000000000000, 0xbff0000000000000, 0, 0x8000000000000000, endian='big')
        d = decode_npy_bytes(npy(p, descr='>c16', shape=(2,)))
        self.assertEqual(d.values_c_order, ((F(1), F(-1)), (F(0), F(0))))
        self.assertEqual(d.negative_zero_c_order, ((False, False), (False, True)))

    def test_asymmetric_fortran_and_c_hash(self):
        # C 2x3 matrix [[1,2,3],[4,5,6]] stored F as [1,4,2,5,3,6].
        b = [0x3ff0000000000000, 0x4000000000000000, 0x4008000000000000,
             0x4010000000000000, 0x4014000000000000, 0x4018000000000000]
        a = decode_npy_bytes(npy(words(*b), shape=(2, 3)))
        f = decode_npy_bytes(npy(words(*(b[i] for i in (0, 3, 1, 4, 2, 5))), shape=(2, 3), order=True))
        self.assertEqual(a.values_c_order, tuple(map(F, range(1, 7))))
        self.assertEqual(a.values_c_order, f.values_c_order)
        self.assertEqual(a.canonical_sha256, f.canonical_sha256)
        self.assertNotEqual(a.raw_npy_sha256, f.raw_npy_sha256)

    def test_asymmetric_three_dimensional_fortran(self):
        # Coordinates encode x+2y+6z; F storage 0..11, C sequence differs.
        p = b''.join(struct.pack('<d', i) for i in range(12))
        d = decode_npy_bytes(npy(p, shape=(2, 3, 2), order=True))
        self.assertEqual(d.values_c_order, tuple(F(i) for i in (0, 6, 2, 8, 4, 10, 1, 7, 3, 9, 5, 11)))

    def test_scalar_and_empty(self):
        self.assertEqual(decode_npy_bytes(npy(words(0x3ff0000000000000), shape=())).values_c_order, (F(1),))
        self.assertEqual(decode_npy_bytes(npy(b'', shape=(2, 0, 3))).values_c_order, ())

    def test_empty_fortran_does_not_materialize_dimension_pools(self):
        # A zero payload may have enormous nonzero axes: element cap alone
        # does not bound itertools.product's eager input pool allocation.
        for shape in ((2**63-1,0), (0,2**63-1), (2**63-1,0,3), (3,2**63-1,0)):
            with self.subTest(shape=shape), patch('exact_raw_decoder.decoder.itertools.product',
                    side_effect=AssertionError('empty array must bypass Cartesian pools')):
                decoded = decode_npy_bytes(npy(b'', shape=shape, order=True), max_elements=0)
                self.assertEqual(decoded.values_c_order, ())
                self.assertEqual(decoded.shape, shape)

    def test_x87_goldens_and_padding(self):
        p = x87(1 << 63, 16383) + x87(1, 0) + x87(0, 0, sign=1)
        data = npy(p, '<f16', (3,))
        d = decode_npy_bytes(data, authority=authority(data))
        self.assertEqual(d.values_c_order, (F(1), F(1, 1 << 16445), F(0)))
        self.assertTrue(d.negative_zero_c_order[2][0])
        data2 = npy(x87(1 << 63, 16383, padding=b'ABCDEF') + p[16:], '<f16', (3,))
        d2 = decode_npy_bytes(data2, authority=authority(data2))
        self.assertEqual(d.canonical_sha256, d2.canonical_sha256)
        self.assertNotEqual(d.raw_npy_sha256, d2.raw_npy_sha256)
        self.assertEqual(d2.padding_hex_c_order[0], ('414243444546',))

    def test_x87_complex_and_big_endian(self):
        data = npy(x87(1 << 63, 16383, endian='big') + x87(1 << 63, 16384, sign=1, endian='big'), '>c32')
        d = decode_npy_bytes(data, authority=authority(data, endian='big'))
        self.assertEqual(d.values_c_order, ((F(1), F(-2)),))

    def test_x87_leading_padding_authority(self):
        data = npy(b'ABCDEF' + x87(1 << 63, 16383)[:10], '<f16')
        d = decode_npy_bytes(data, authority=authority(data, value_offset=6))
        self.assertEqual(d.values_c_order, (F(1),))
        self.assertEqual(d.padding_hex_c_order, (('414243444546',),))

    def test_binary128_goldens(self):
        vals = [(16383 << 112), 1, 1 << 127, (16383 << 112) | 1]
        data = npy(words(*vals, size=16), '<f16', (4,))
        d = decode_npy_bytes(data, authority=authority(data, 'ieee_binary128'))
        self.assertEqual(d.values_c_order, (F(1), F(1, 1 << 16494), F(0), F(1) + F(1, 1 << 112)))

    def test_canonical_known_payload(self):
        data = npy(words(0x3ff0000000000000, 0xc004000000000000), shape=(2,))
        expected = {'schema': 'EXACT_DYADIC_ARRAY_V1', 'shape': [2],
                    'values': [[['1', 0], ['0', 0]], [['-5', -1], ['0', 0]]]}
        expected_hash = hashlib.sha256(json.dumps(expected, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        self.assertEqual(decode_npy_bytes(data).canonical_sha256, expected_hash)

    def test_signed_zero_math_hash_and_raw_difference(self):
        a = decode_npy_bytes(npy(words(0)))
        b = decode_npy_bytes(npy(words(1 << 63)))
        self.assertEqual(a.canonical_sha256, b.canonical_sha256)
        self.assertNotEqual(a.raw_npy_sha256, b.raw_npy_sha256)

    def test_reject_binary64_nonfinite(self):
        for bits in (0x7ff0000000000000, 0xfff0000000000000, 0x7ff8000000000001, 0x7ff0000000000001):
            with self.subTest(bits=bits), self.assertRaises(DecodeError):
                decode_npy_bytes(npy(words(bits)))

    def test_reject_x87_noncanonical_and_nonfinite(self):
        for sig, exp in ((0, 1), (1 << 63, 0), (1 << 63, 32767), ((1 << 63)+1, 32767)):
            data = npy(x87(sig, exp), '<f16')
            with self.subTest(sig=sig, exp=exp), self.assertRaises(DecodeError):
                decode_npy_bytes(data, authority=authority(data))

    def test_reject_binary128_nonfinite(self):
        for frac in (0, 1, 1 << 111):
            data = npy(words((32767 << 112) | frac, size=16), '<f16')
            with self.subTest(frac=frac), self.assertRaises(DecodeError):
                decode_npy_bytes(data, authority=authority(data, 'ieee_binary128'))

    def test_authority_required_and_bound(self):
        data = npy(b'\0'*32, '<c32')
        with self.assertRaises(DecodeError): decode_npy_bytes(data)
        other = npy(b'\0'*16, '<f16')
        with self.assertRaises(DecodeError): decode_npy_bytes(data, authority=authority(other))
        with self.assertRaises(DecodeError): decode_npy_bytes(data, authority=authority(data, endian='big'))
        with self.assertRaises(DecodeError): decode_npy_bytes(data, authority=authority(data, layout='guess_complex256'))

    def test_reject_unsupported_dtype_endian(self):
        for descr in ('=f8', '|f8', '<f4', '<i8', '|O', 'complex256', '<V16'):
            with self.subTest(descr=descr), self.assertRaises(DecodeError):
                decode_npy_bytes(npy(b'\0'*8, descr))

    def test_reject_payload_truncation_and_trailing(self):
        for payload in (b'', b'\0'*7, b'\0'*9):
            with self.subTest(n=len(payload)), self.assertRaises(DecodeError):
                decode_npy_bytes(npy(payload))

    def test_reject_malformed_headers(self):
        headers = ["{'descr':'<f8','descr':'>f8','fortran_order':False,'shape':(1,)}",
                   "{'descr':'<f8','fortran_order':0,'shape':(1,)}",
                   "{'descr':'<f8','fortran_order':False,'shape':(-1,)}",
                   "{'descr':'<f8','fortran_order':False,'shape':(True,)}",
                   "{'descr':'<f8','fortran_order':False,'shape':[1]}",
                   "{'descr':'<f8','fortran_order':False,'shape':(1,), 'extra':1}",
                   "dict(descr='<f8', fortran_order=False, shape=(1,))",
                   "{'descr':'<f8','fortran_order':False,'shape':(1,)} # hidden comment"]
        for header in headers:
            with self.subTest(header=header), self.assertRaises(DecodeError):
                decode_npy_bytes(npy(b'\0'*8, header=header))

    def test_reject_magic_version_encoding_and_header_length(self):
        data = npy(b'\0'*8)
        bad = (b'WRONG!' + data[6:], data[:6]+b'\4\0'+data[8:], data[:8], data[:8]+b'\xff\xff'+data[10:], data[:127]+b' '+data[128:])
        for item in bad:
            with self.subTest(prefix=item[:12]), self.assertRaises(DecodeError): decode_npy_bytes(item)

    def test_resource_caps(self):
        with self.assertRaises(DecodeError): decode_npy_bytes(npy(words(0), shape=(1,)), max_elements=0)
        with self.assertRaises(DecodeError): decode_npy_bytes(npy(b'', shape=(1 << 70, 0)))
        with self.assertRaises(DecodeError): decode_npy_bytes(npy(b'', shape=(0,)*33))

    def test_header_inspection_does_not_decode_values(self):
        data = npy(words(0x7ff0000000000000))
        h = inspect_npy_header(data)
        self.assertEqual(h.shape, (1,))
        self.assertEqual(h.descr, '<f8')
        self.assertFalse(hasattr(h, 'values_c_order'))

    def test_x87_boundary_significands(self):
        pairs = [(1 << 63, 1), ((1 << 63)-1, 0), ((1 << 63)+1, 16383), ((1 << 64)-1, 32766)]
        data = npy(b''.join(x87(s, e) for s, e in pairs), '<f16', (4,))
        values = decode_npy_bytes(data, authority=authority(data)).values_c_order
        expected = (F(1, 1 << 16382), F((1 << 63)-1, 1 << 16445),
                    F(1) + F(1, 1 << 63), F((1 << 64)-1) * (1 << 16320))
        self.assertEqual(values, expected)

    def test_binary128_complex_big_endian_and_largest_finite(self):
        data = npy(words((16383 << 112), (1 << 127) | (32766 << 112) | ((1 << 112)-1),
                         size=16, endian='big'), '>c32')
        d = decode_npy_bytes(data, authority=authority(data, 'ieee_binary128', endian='big'))
        self.assertEqual(d.values_c_order, ((F(1), -F((1 << 113)-1) * (1 << 16271)),))

    def test_reject_malformed_authority(self):
        data = npy(x87(1 << 63, 16383), '<f16')
        good = authority(data)
        for kwargs in ({'scope':'CURRENT_HOST'}, {'evidence_id':''}, {'evidence_sha256':()},
                       {'evidence_sha256':('bad',)}, {'component_bytes':8},
                       {'value_offset':7}, {'complex_component_order':'imag_real'}):
            with self.subTest(kwargs=kwargs), self.assertRaises(DecodeError):
                decode_npy_bytes(data, authority=replace(good, **kwargs))

    def test_binary64_endian_math_identity(self):
        bits = (0x3ff0000000000000, 0xc004000000000000)
        a = decode_npy_bytes(npy(words(*bits), shape=(2,)))
        b = decode_npy_bytes(npy(words(*bits, endian='big'), '>f8', (2,)))
        self.assertEqual(a.canonical_sha256, b.canonical_sha256)
        self.assertNotEqual(a.payload_sha256, b.payload_sha256)

    def test_fortran_complex_padding_provenance_per_element(self):
        raw = [x87(1 << 63, 16383 + e, padding=bytes([e])*6) + x87(0, 0) for e in range(4)]
        data = npy(b''.join(raw[i] for i in (0, 2, 1, 3)), '<c32', (2, 2), True)
        d = decode_npy_bytes(data, authority=authority(data))
        self.assertEqual(d.values_c_order, tuple((F(1 << e), F(0)) for e in range(4)))
        self.assertEqual(d.padding_hex_c_order, tuple(((bytes([e])*6).hex(), '000000000000') for e in range(4)))

    def test_hash_shape_is_significant_and_kind_is_mathematical(self):
        real = decode_npy_bytes(npy(words(0x3ff0000000000000)))
        complex_ = decode_npy_bytes(npy(words(0x3ff0000000000000, 0), '<c16'))
        scalar = decode_npy_bytes(npy(words(0x3ff0000000000000), shape=()))
        self.assertEqual(real.canonical_sha256, complex_.canonical_sha256)
        self.assertNotEqual(real.canonical_sha256, scalar.canonical_sha256)

    def test_reject_v3_invalid_utf8_and_excess_header_budget(self):
        data = npy(words(0), version=(3, 0))
        bad = data[:13] + b'\xff' + data[14:]
        with self.assertRaises(DecodeError): decode_npy_bytes(bad)
        with self.assertRaises(DecodeError): decode_npy_bytes(npy(words(0), header=' '*10001+'{}'))


if __name__ == '__main__':
    unittest.main()
