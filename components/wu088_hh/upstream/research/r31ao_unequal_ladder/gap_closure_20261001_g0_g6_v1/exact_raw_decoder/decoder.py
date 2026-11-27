"""Strict bounded NPY decoding using only integers and Fraction.

This module verifies structural consistency of caller-supplied layout authority.
It does not establish historical ABI evidence by accepting an authority object.
The historical evidence review and its exact NPY hash binding are external gates.
No current-host dtype, ctypes, float, NumPy, native probe, or scientific callback
is used. NPY object/structured/integer/unsupported real dtypes are rejected.
"""
from __future__ import annotations

import ast
import hashlib
import itertools
import json
import re
from dataclasses import dataclass
from fractions import Fraction


class DecodeError(ValueError):
    """Malformed, unsupported, nonfinite, unbound, or over-budget input."""


@dataclass(frozen=True)
class Header:
    version: tuple[int, int]
    descr: str
    shape: tuple[int, ...]
    fortran_order: bool
    payload_offset: int
    item_bytes: int
    element_count: int
    byte_order: str
    scalar_kind: str


@dataclass(frozen=True)
class LayoutAuthority:
    """Declared reviewed layout, bound to one exact NPY member's byte hash.

    layout: 'x87_80' (10 meaningful bytes in each 16-byte component), or
    'ieee_binary128' (16 meaningful bytes). value_offset describes where the
    meaningful bytes begin in each component; all other bytes are provenance
    padding. byte_order applies to meaningful bytes and must match descr.
    Evidence hashes identify archived witnesses, not live host assumptions.
    SYNTHETIC_FIXTURE_ONLY never establishes a historical producer layout.
    """
    layout: str
    byte_order: str
    component_bytes: int
    value_offset: int
    complex_component_order: str
    scope: str
    evidence_id: str
    evidence_sha256: tuple[str, ...]
    bound_npy_sha256: str


@dataclass(frozen=True)
class DecodedArray:
    shape: tuple[int, ...]
    values_c_order: tuple
    canonical_sha256: str
    raw_npy_sha256: str
    payload_sha256: str
    header: Header
    negative_zero_c_order: tuple[tuple[bool, ...], ...]
    padding_hex_c_order: tuple[tuple[str, ...], ...]
    authority_scope: str
    authority_evidence_id: str | None


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inspect_npy_header(data: bytes, *, max_elements: int = 1_000_000) -> Header:
    """Read/validate header and payload length without interpreting values.

    The 16-byte alignment floor permits historical NPY writers; current
    NumPy 2.3.5 uses 64-byte alignment. Bounds: 10,000-byte header, 32 axes,
    each axis <= 2**63-1, and explicit element cap. Scalar shape () has one
    element, and any zero dimension gives zero elements.
    """
    if type(data) is not bytes or type(max_elements) is not int or max_elements < 0:
        raise DecodeError('bytes input and nonnegative integer cap required')
    if len(data) < 10 or data[:6] != b'\x93NUMPY':
        raise DecodeError('invalid or truncated NPY magic')
    version = tuple(data[6:8])
    if version not in ((1, 0), (2, 0), (3, 0)):
        raise DecodeError('unsupported NPY version')
    width = 2 if version == (1, 0) else 4
    if len(data) < 8 + width:
        raise DecodeError('truncated header length')
    header_length = int.from_bytes(data[8:8 + width], 'little')
    offset = 8 + width + header_length
    if not 1 <= header_length <= 10_000 or offset > len(data) or offset % 16:
        raise DecodeError('invalid, truncated, unaligned, or over-budget header')
    header_bytes = data[8 + width:offset]
    if not header_bytes.endswith(b'\n'):
        raise DecodeError('NPY header must end in newline')
    try:
        text = header_bytes.decode('utf8' if version == (3, 0) else 'latin1')
        # A strict literal dictionary only: reject comments/trailing code and
        # duplicate keys before ast.literal_eval could collapse duplicates.
        expression = text[:-1].rstrip(' ')
        if not expression.startswith('{') or not expression.endswith('}') or '\n' in expression or '\r' in expression:
            raise DecodeError('header must be one literal dictionary')
        node = ast.parse(expression, mode='eval').body
        if not isinstance(node, ast.Dict) or len(node.keys) != 3:
            raise DecodeError('exactly three header fields required')
        keys = [ast.literal_eval(k) for k in node.keys]
        if len(set(keys)) != 3 or set(keys) != {'descr', 'fortran_order', 'shape'}:
            raise DecodeError('unknown or duplicate header field')
        meta = ast.literal_eval(node)
    except (SyntaxError, ValueError, TypeError, RecursionError, MemoryError) as exc:
        raise DecodeError('invalid bounded NPY dictionary') from exc
    shape, order, descr = meta['shape'], meta['fortran_order'], meta['descr']
    if type(shape) is not tuple or len(shape) > 32 or type(order) is not bool:
        raise DecodeError('invalid shape or fortran_order')
    if any(type(n) is not int or n < 0 or n > (1 << 63) - 1 for n in shape):
        raise DecodeError('shape dimensions must be bounded nonnegative integers')
    count = 1
    if 0 in shape:
        count = 0
    else:
        for n in shape:
            count *= n
            if count > max_elements:
                raise DecodeError('element cap exceeded')
    if count > max_elements:
        raise DecodeError('element cap exceeded')
    if type(descr) is not str or not re.fullmatch(r'[<>](f8|f16|c16|c32)', descr):
        raise DecodeError('unsupported dtype or non-explicit endianness')
    item_bytes = int(descr[2:])
    if len(data) - offset != count * item_bytes:
        raise DecodeError('payload length does not equal shape times itemsize')
    return Header(version, descr, shape, order, offset, item_bytes, count,
                  'little' if descr[0] == '<' else 'big', descr[1])


def _validate_authority(authority: LayoutAuthority | None, header: Header, raw_hash: str) -> LayoutAuthority:
    if not isinstance(authority, LayoutAuthority):
        raise DecodeError('explicit reviewed extended-layout authority required')
    if authority.layout not in ('x87_80', 'ieee_binary128'):
        raise DecodeError('unsupported explicitly supplied extended layout')
    if authority.scope not in ('SYNTHETIC_FIXTURE_ONLY', 'HISTORICAL_PRODUCER_LAYOUT_REVIEWED'):
        raise DecodeError('authority scope is not admitted')
    hashes = authority.evidence_sha256
    if (not isinstance(hashes, tuple) or not hashes or
            any(type(s) is not str or not re.fullmatch('[0-9a-f]{64}', s) for s in hashes) or
            type(authority.evidence_id) is not str or not authority.evidence_id.strip()):
        raise DecodeError('explicit evidence identity and SHA256 witnesses required')
    if authority.bound_npy_sha256 != raw_hash:
        raise DecodeError('layout authority is not bound to these NPY bytes')
    if authority.byte_order != header.byte_order:
        raise DecodeError('layout authority endianness contradicts NPY descr')
    if type(authority.component_bytes) is not int or authority.component_bytes != 16:
        raise DecodeError('only explicitly described 16-byte extended components supported')
    meaningful = 10 if authority.layout == 'x87_80' else 16
    if type(authority.value_offset) is not int or not 0 <= authority.value_offset <= 16 - meaningful:
        raise DecodeError('invalid meaningful-byte offset')
    if authority.complex_component_order != 'real_imag':
        raise DecodeError('only explicitly reviewed real-then-imag layout supported')
    return authority


def _dyadic(sign: int, significand: int, exponent: int) -> Fraction:
    numerator = -significand if sign else significand
    return Fraction(numerator << exponent, 1) if exponent >= 0 else Fraction(numerator, 1 << -exponent)


def _ieee(word: int, fraction_bits: int, exponent_bits: int):
    sign = word >> (fraction_bits + exponent_bits)
    fraction = word & ((1 << fraction_bits) - 1)
    exponent = (word >> fraction_bits) & ((1 << exponent_bits) - 1)
    if exponent == (1 << exponent_bits) - 1:
        raise DecodeError('nonfinite represented component')
    bias = (1 << (exponent_bits - 1)) - 1
    significand = fraction if exponent == 0 else (1 << fraction_bits) | fraction
    power = (1 if exponent == 0 else exponent) - bias - fraction_bits
    return _dyadic(sign, significand, power), bool(sign and significand == 0)


def _component(raw: bytes, endian: str, authority: LayoutAuthority | None):
    if authority is None:
        value, negative_zero = _ieee(int.from_bytes(raw, endian), 52, 11)
        return value, negative_zero, ''
    meaningful = 10 if authority.layout == 'x87_80' else 16
    offset = authority.value_offset
    word = int.from_bytes(raw[offset:offset + meaningful], endian)
    padding = raw[:offset] + raw[offset + meaningful:]
    if authority.layout == 'ieee_binary128':
        value, negative_zero = _ieee(word, 112, 15)
    else:
        sign, exponent = word >> 79, (word >> 64) & 32767
        significand = word & ((1 << 64) - 1)
        integer_bit = significand >> 63
        if exponent == 32767:
            raise DecodeError('nonfinite or unsupported x87 component')
        if (exponent == 0 and integer_bit != 0) or (exponent != 0 and integer_bit != 1):
            raise DecodeError('noncanonical x87 pseudo-denormal/unnormal encoding')
        value = _dyadic(sign, significand, (1 if exponent == 0 else exponent) - 16383 - 63)
        negative_zero = bool(sign and significand == 0)
    return value, negative_zero, padding.hex()


def _storage_indices(header: Header):
    if header.element_count == 0:
        return
    if not header.fortran_order or len(header.shape) < 2:
        yield from range(header.element_count)
        return
    strides, stride = [], 1
    for n in header.shape:
        strides.append(stride)
        stride *= n
    for index in itertools.product(*(range(n) for n in header.shape)):
        yield sum(i * s for i, s in zip(index, strides))


def _canonical_dyadic(value: Fraction):
    if not value:
        return ['0', 0]
    n, den = value.numerator, value.denominator
    if den & (den - 1):
        raise DecodeError('internal value is not dyadic')
    exponent = -(den.bit_length() - 1)
    # Strip all numerator powers of two; hexadecimal avoids Python's decimal
    # digit conversion limit for the largest finite extended values.
    magnitude = abs(n)
    shift = (magnitude & -magnitude).bit_length() - 1
    n >>= shift
    return [format(n, 'x'), exponent + shift]


def decode_npy_bytes(data: bytes, *, authority: LayoutAuthority | None = None,
                     max_elements: int = 1_000_000) -> DecodedArray:
    """Return exact finite values in logical C order with disjoint raw metadata.

    Real values are Fraction; complex values are (Fraction, Fraction). The
    canonical mathematical hash includes shape and complex pairs for all
    elements, so real x and complex x+0i hash equally; dtype/order/padding and
    signed zero are retained in header/provenance but do not alter math hash.
    This is not a certificate of continuous-target accuracy or ABI authority.
    """
    header = inspect_npy_header(data, max_elements=max_elements)
    raw_hash = _sha256(data)
    components = 2 if header.scalar_kind == 'c' else 1
    component_bytes = header.item_bytes // components
    if component_bytes == 16:
        authority = _validate_authority(authority, header, raw_hash)
    elif authority is not None:
        raise DecodeError('extended-layout authority cannot override binary64 descr')
    payload = data[header.payload_offset:]
    values, signs, paddings, canonical = [], [], [], []
    for index in _storage_indices(header):
        offset = index * header.item_bytes
        decoded = [_component(payload[offset + k * component_bytes:offset + (k + 1) * component_bytes],
                              header.byte_order, authority) for k in range(components)]
        re_value = decoded[0][0]
        im_value = decoded[1][0] if components == 2 else Fraction(0)
        values.append((re_value, im_value) if components == 2 else re_value)
        signs.append(tuple(c[1] for c in decoded))
        paddings.append(tuple(c[2] for c in decoded))
        canonical.append([_canonical_dyadic(re_value), _canonical_dyadic(im_value)])
    document = {'schema': 'EXACT_DYADIC_ARRAY_V1', 'shape': list(header.shape), 'values': canonical}
    canonical_hash = _sha256(json.dumps(document, sort_keys=True, separators=(',', ':')).encode('ascii'))
    return DecodedArray(header.shape, tuple(values), canonical_hash, raw_hash, _sha256(payload),
                        header, tuple(signs), tuple(paddings),
                        authority.scope if authority else 'NPY_EXPLICIT_BINARY64_FORMAT',
                        authority.evidence_id if authority else None)
