"""Bounded review oracle; only locally generated fixed synthetic NPY bytes."""
import ast
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import abi_witness as w


def dyadic(n, exponent):
    return Fraction(n * 2**exponent) if exponent >= 0 else Fraction(n, 2**(-exponent))


def parse_component(raw, byte_order, candidate):
    # Independent direct integer bit interpretation, without invoking G2.
    if candidate == 'x87_80':
        assert byte_order == 'little' and len(raw) == 16
        sig = int.from_bytes(raw[:8], 'little')
        se = int.from_bytes(raw[8:10], 'little')
        sign, exponent = se >> 15, se & 0x7fff
        assert exponent < 0x7fff
        assert exponent == 0 or sig >> 63 == 1
        value = dyadic(sig, (exponent or 1) - 16383 - 63)
    else:
        fraction_bits, exponent_bits, bias = ((52, 11, 1023) if candidate == 'IEEE_BINARY64'
                                             else (112, 15, 16383))
        assert candidate in ('IEEE_BINARY64', 'ieee_binary128')
        bits = int.from_bytes(raw, byte_order)
        sign = bits >> (fraction_bits + exponent_bits)
        exponent = (bits >> fraction_bits) & (2**exponent_bits - 1)
        fraction = bits & (2**fraction_bits - 1)
        assert exponent < 2**exponent_bits - 1
        sig = fraction + (2**fraction_bits if exponent else 0)
        value = dyadic(sig, (exponent or 1) - bias - fraction_bits)
    return (-value if sign else value), bool(sign and value == 0)


def main():
    out = Path(__file__).resolve().parent / 'current_probe'
    record = w.collect(out)
    assert record['status'] == 'CURRENT_SYNTHETIC_WITNESS_CAPTURED', record.get('blocker')
    assert record['actual_HH_payloads_read'] == 0 and record['native_builds'] == 0
    assert record['B03'] == 'RAW_ABI_AUTHORITY_BLOCKED'
    assert record['historical_layout_admitted'] is False
    assert len(record['sentinels']) == 8
    checked_components = 0
    candidates, byte_orders = set(), set()
    for sentinel in record['sentinels']:
        encoded = (out / sentinel['file']).read_bytes()
        assert sentinel['file_encoding'] == 'hex' and sentinel['file'].endswith('.npy.hex')
        raw = bytes.fromhex(encoded.decode('ascii'))
        assert len(raw) == sentinel['bytes'] <= w.MAX_SENTINEL_BYTES
        assert hashlib.sha256(raw).hexdigest() == sentinel['raw_npy_sha256']
        assert raw[:6] == b'\x93NUMPY' and raw[6:8] == b'\x01\x00'
        header_length = int.from_bytes(raw[8:10], 'little')
        header = ast.literal_eval(raw[10:10+header_length].decode('latin1'))
        payload = raw[10+header_length:]
        assert hashlib.sha256(payload).hexdigest() == sentinel['payload_sha256']
        assert header['shape'] == (2, 4)
        descr = header['descr']
        byte_order = {'<': 'little', '>': 'big'}[descr[0]]
        is_complex, item_bytes = descr[1] == 'c', int(descr[2:])
        component_bytes = item_bytes // (2 if is_complex else 1)
        label = sentinel['name'].rsplit('_', 1)[0]
        md = record['dtype_metadata'][label]
        nmant, minexp = md['finfo']['nmant'], md['finfo']['minexp']
        assert (nmant, minexp) in ((52, -1022), (63, -16382), (112, -16382))
        expected = [Fraction(0), Fraction(0), Fraction(1), Fraction(-2),
                    Fraction(2**nmant + 1, 2**nmant), dyadic(1, minexp),
                    dyadic(1, minexp-nmant), -dyadic(1, minexp-nmant)]
        perm = [2, 3, 0, 1, 6, 7, 4, 5]
        assert len(payload) == 8 * item_bytes
        for logical in range(8):
            row, col = divmod(logical, 4)
            storage = row + 2*col if header['fortran_order'] else logical
            for component in range(2 if is_complex else 1):
                start = storage*item_bytes + component*component_bytes
                value, negative_zero = parse_component(payload[start:start+component_bytes],
                                                        byte_order, sentinel['tested_candidate'])
                index = perm[logical] if component else logical
                assert value == expected[index], (sentinel['name'], logical, component)
                assert negative_zero == (index == 1)
                assert negative_zero == sentinel['negative_zero_c_order'][logical][component]
                checked_components += 1
        assert sentinel['authority_scope'] == 'CURRENT_SYNTHETIC_ONLY_NOT_HISTORICAL'
        candidates.add(sentinel['tested_candidate']); byte_orders.add(byte_order)
    # An apparently complete historical reference object must not become authority.
    document = {'schema': w.LINK_SCHEMA, 'producer_runtime': w.PRODUCER_RUNTIME,
                'output_archive_sha256': dict(w.OUTPUT_PINS),
                'producer_source_sha256': dict(w.PRODUCER_PINS),
                'references': [{'role': role, 'uri': 'https://example.org/' + role,
                                'sha256': str(i+1)*64, 'origin': 'INDEPENDENT_HISTORICAL_RECORD'}
                               for i, role in enumerate(w.REQUIRED_ROLES)]}
    historical = w.assess_historical_linkage(document, set())
    assert historical['status'] == 'REFERENCES_STRUCTURALLY_COMPLETE_REVIEW_REQUIRED'
    for flag in ('historical_layout_admitted', 'reference_contents_verified', 'independent_review_admitted'):
        assert historical[flag] is False
    assert historical['B03'] == 'RAW_ABI_AUTHORITY_BLOCKED'
    output_bytes = sum(p.stat().st_size for p in out.iterdir())
    assert output_bytes <= w.MAX_OUTPUT_BYTES
    assert json.loads((out / 'WITNESS.json').read_text()) == record
    print(json.dumps({'status': 'PASS_CURRENT_HOST_SYNTHETIC_ONLY',
                      'sentinels': 8, 'independently_bit_decoded_components': checked_components,
                      'candidates_exercised': sorted(candidates), 'byte_orders_exercised': sorted(byte_orders),
                      'output_bytes_including_report': output_bytes, 'historical_layout_admitted': False,
                      'reference_contents_verified': False, 'independent_review_admitted': False,
                      'actual_HH_payloads_read': 0, 'native_builds': 0}, sort_keys=True))


if __name__ == '__main__':
    main()
