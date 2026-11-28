"""Bounded synthetic and metadata-only witness tests; no HH inputs."""
import importlib.util
import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

import abi_witness as w


class LinkageTests(unittest.TestCase):
    def good(self):
        return {
            'schema': w.LINK_SCHEMA,
            'producer_runtime': w.PRODUCER_RUNTIME,
            'output_archive_sha256': dict(w.OUTPUT_PINS),
            'producer_source_sha256': dict(w.PRODUCER_PINS),
            'references': [dict(role=role, uri='https://example.org/independent/' + role,
                sha256=str(i + 1) * 64, origin='INDEPENDENT_HISTORICAL_RECORD')
                for i, role in enumerate(w.REQUIRED_ROLES)],
        }

    def test_missing_never_closes_b03(self):
        r = w.assess_historical_linkage(None, set())
        self.assertEqual(r['status'], 'MISSING_HISTORICAL_LINKAGE')
        self.assertFalse(r['historical_layout_admitted'])
        self.assertEqual(r['B03'], 'RAW_ABI_AUTHORITY_BLOCKED')

    def test_boolean_and_self_hash_are_not_authority(self):
        for d in ({'verified': True}, self.good()):
            r = w.assess_historical_linkage(d, {'1' * 64})
            self.assertEqual(r['status'], 'INVALID_HISTORICAL_LINKAGE_REFERENCES')
            self.assertFalse(r['historical_layout_admitted'])

    def test_wrong_recorded_producer_rejected(self):
        d = self.good()
        d['output_archive_sha256']['OD'] = 'a' * 64
        self.assertEqual(w.assess_historical_linkage(d, set())['status'],
                         'INVALID_HISTORICAL_LINKAGE_REFERENCES')

    def test_complete_references_require_independent_review(self):
        r = w.assess_historical_linkage(self.good(), set())
        self.assertEqual(r['status'], 'REFERENCES_STRUCTURALLY_COMPLETE_REVIEW_REQUIRED')
        self.assertFalse(r['historical_layout_admitted'])
        self.assertFalse(r['reference_contents_verified'])
        self.assertEqual(r['B03'], 'RAW_ABI_AUTHORITY_BLOCKED')

    def test_no_payload_manifest_api(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'array.npy'
            p.write_bytes(b'\x93NUMPY')
            with self.assertRaises(w.Refusal):
                w.read_link_manifest(p)


class BoundTests(unittest.TestCase):
    def test_hash_budget_rejects_before_large_read(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'x'
            p.write_bytes(b'abcd')
            with self.assertRaises(w.Refusal):
                w.Budget(max_file_bytes=3).identity(p, 'test')

    def test_missing_numpy_records_blocker_without_install(self):
        with tempfile.TemporaryDirectory() as d:
            def absent():
                raise ModuleNotFoundError('synthetic missing NumPy')
            r = w.collect(Path(d) / 'out', numpy_loader=absent)
            self.assertEqual(r['status'], 'NUMPY_UNAVAILABLE')
            self.assertEqual(r['synthetic_payloads_generated'], 0)
            self.assertFalse(r['historical_layout_admitted'])

    def test_create_only_output(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(w.Refusal):
                w.collect(Path(d))

    def test_show_config_cap(self):
        s = w.CappedText(3)
        with self.assertRaises(w.Refusal):
            s.write('1234')

    def test_manifest_byte_cap(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'links.json'
            p.write_bytes(b' ' * (w.MAX_MANIFEST_BYTES + 1))
            with self.assertRaises(w.Refusal):
                w.read_link_manifest(p)


@unittest.skipUnless(importlib.util.find_spec('numpy'), 'NumPy absent: runtime probe blocked')
class SyntheticTests(unittest.TestCase):
    def test_current_witness_exact_bytes_and_fortran_order(self):
        import numpy as np
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'probe'
            r = w.collect(root)
            self.assertEqual(r['status'], 'CURRENT_SYNTHETIC_WITNESS_CAPTURED')
            self.assertEqual(r['numpy_version'], np.__version__)
            self.assertFalse(r['historical_layout_admitted'])
            self.assertEqual(r['actual_HH_payloads_read'], 0)
            self.assertEqual(len(r['sentinels']), 8)
            by = {s['name']: s for s in r['sentinels']}
            a = by['float64_C']
            decoder = w.load_decoder()
            v = decoder.decode_npy_bytes(bytes.fromhex((root / a['file']).read_text('ascii')))
            self.assertEqual(v.values_c_order[4], Fraction(2**52 + 1, 2**52))
            self.assertEqual(v.values_c_order[6], Fraction(1, 2**1074))
            self.assertEqual(v.negative_zero_c_order[1], (True,))
            for prefix in ('float64', 'longdouble', 'complex128', 'clongdouble'):
                c, f = by[prefix + '_C'], by[prefix + '_F']
                self.assertFalse(c['header']['fortran_order'])
                self.assertTrue(f['header']['fortran_order'])
                self.assertEqual(c['canonical_sha256'], f['canonical_sha256'])
                self.assertEqual(c['expected_values'], f['expected_values'])
                self.assertEqual(c['verification'], 'EXACT_DYADICS_AND_SIGNED_ZERO_MATCH')
                self.assertEqual(c['decoded_values'], c['expected_values'])
            self.assertTrue(r['identities'])
            roles = {x['role'] for x in r['identities']}
            self.assertIn('numpy_write_array_implementation', roles)
            self.assertIn('numpy_save_implementation', roles)
            self.assertTrue((root / 'numpy_show_config.txt').is_file())
            self.assertEqual(json.loads((root / 'WITNESS.json').read_text()), r)

    def test_expected_subnormal_is_independent_of_host_float(self):
        _, v, signs = w.real_sentinel_spec(63, -16382)
        self.assertEqual(v[4], Fraction(2**63 + 1, 2**63))
        self.assertEqual(v[6], Fraction(1, 2**16445))
        self.assertTrue(signs[1])

    def test_lost_negative_zero_is_refused(self):
        import numpy as np
        md = {name: w.dtype_metadata(np, dtype) for name, dtype in
              [('float64', np.float64), ('longdouble', np.longdouble),
               ('complex128', np.complex128), ('clongdouble', np.clongdouble)]}
        _, raw, expected, signs, _, meta = next(w.fixed_sentinels(np, md))
        decoder = w.load_decoder()
        h = decoder.inspect_npy_header(raw)
        b = bytearray(raw)
        # The second binary64 component is -0; erase only its sign.
        b[h.payload_offset + 8:h.payload_offset + 16] = bytes(8)
        with self.assertRaises(w.Refusal):
            w.decode_generated(decoder, bytes(b), expected, signs, meta, 'a' * 64)

    def test_no_layout_candidate_from_dtype_name_alone(self):
        with self.assertRaises(w.Refusal):
            w.real_sentinel_spec(1000000, -16382)


if __name__ == '__main__':
    unittest.main()
