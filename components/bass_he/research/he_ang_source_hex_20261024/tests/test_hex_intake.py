"""Focused new dependencies only. Every SQL row/coefficient is SYNTHETIC."""
from fractions import Fraction as F
import hashlib
import lzma
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'code'))
import hex_intake as h


def oracle(coefficients, x, m=None):
    """Independent exact forward T recurrence; complex represented by pairs."""
    m = len(coefficients) if m is None else m
    t = 2*x-1
    polys = [F(1), t]
    for j in range(2, m):
        polys.append(2*t*polys[-1]-polys[-2])
    result = [F(0), F(0)]
    for j, z in enumerate(coefficients[:m]):
        for axis, component in enumerate((z.real, z.imag)):
            result[axis] += F.from_float(component)*polys[j]/(2 if j == 0 else 1)
    return tuple(result)


class ChebyshevSyntheticTests(unittest.TestCase):
    def test_c0_half_and_full_default(self):
        for x in (0, .25, .5, .75, 1):
            self.assertEqual(h.evaluate([6+4j], x), 3+2j)
        self.assertEqual(h.evaluate([2, 0, 2], .5), -1)

    def test_late_nonzero_rejects_first_small_cutoff(self):
        c = [2, 0, 2]
        self.assertEqual(h.evaluate(c, .5, m=2), 1)
        self.assertEqual(abs(h.evaluate(c, .5)-h.evaluate(c, .5, m=2)), 2)
        self.assertEqual(h.exact_tail(c, 2), F(2))
        self.assertEqual(h.select_terms(c, F(0)), 3)
        self.assertEqual(h.select_terms(c, F(1)), 3)
        self.assertEqual(h.select_terms(c, F(2)), 1)

    def test_complex_against_independent_exact_oracle(self):
        c = [2+4j, .5-.25j, -2+1j, .125+.5j, 0j, .25-.125j]
        for x in map(F, ('0', '1/4', '1/2', '3/4', '1')):
            exact = oracle(c, x)
            self.assertEqual(h.evaluate(c, float(x)), complex(float(exact[0]), float(exact[1])))
            for m in range(1, len(c)+1):
                truncated = oracle(c, x, m)
                l1_error = sum(abs(a-b) for a, b in zip(exact, truncated))
                self.assertLessEqual(l1_error, h.exact_tail(c, m))

    def test_tail_binary64_exact_and_whole_suffix(self):
        c = [2, .1+.2j, 0, .3j]
        self.assertEqual(h.exact_tail(c, 1), F.from_float(.1)+F.from_float(.2)+F.from_float(.3))
        self.assertEqual(h.select_terms(c, F.from_float(.3)), 2)
        self.assertEqual(h.select_terms(c, F.from_float(.3)-F(1, 2**60)), 4)

    def test_invalid_domains_tolerances_and_coefficients(self):
        for x in (-.01, 1.01, float('nan')):
            with self.assertRaises(ValueError): h.evaluate([2], x)
        for tol in (-1, float('inf'), True):
            with self.assertRaises(ValueError): h.select_terms([2], tol)
        for c in ([], [float('nan')], [complex(1, float('inf'))]):
            with self.assertRaises(ValueError): h.evaluate(c, .5)
        for m in (0, -1, 4, True):
            with self.assertRaises(ValueError): h.exact_tail([2, 0, 2], m)


class PayloadSyntheticTests(unittest.TestCase):
    def test_explicit_endian_encodings_and_source_schema(self):
        c = [2+4j, -.25+.5j]
        for endian, prefix in [('little', '<'), ('big', '>')]:
            blob = b''.join(struct.pack(prefix+'dd', z.real, z.imag) for z in c)
            row = h.decode_ionf_row((1, 0, 0, 0, 1, 5., 1, 1, blob), endian=endian, layout='binary64-real-imag')
            self.assertEqual(row.coefficients, tuple(c))
            self.assertEqual(row.normalized_coordinate(0), 0)
            self.assertEqual(row.normalized_coordinate(1), .5)
            self.assertEqual(row.normalized_coordinate(2), 1)
            for k in (-1, 3):
                with self.assertRaises(ValueError): row.normalized_coordinate(k)
            sql = 'INSERT OR REPLACE INTO "ionf" VALUES (1,0,0,0,1,5,1,1,X\''+blob.hex()+"');"
            table, columns, tokens = h.parse_insert(sql)
            self.assertEqual(table, 'ionf')
            self.assertIsNone(columns)
            self.assertEqual(h.decode_ionf_row(tokens, endian=endian, layout='binary64-real-imag'), row)

    def test_generic_decoder_is_not_h1_restricted(self):
        row = h.decode_ionf_row((2, 1, -1, 1, 0, .5, 0, 1, bytes(16)), endian='little', layout='binary64-real-imag')
        self.assertEqual((row.ni, row.li, row.mi), (2, 1, -1))

    def test_missing_bad_blob_no_abi_guess(self):
        for blob in (None, b'', b'123', "X''", "X'0'", "X'zz'", 'NULL'):
            with self.assertRaises(ValueError): h.decode_blob(blob, endian='little', layout='binary64-real-imag')
        for endian, layout in ((None, 'binary64-real-imag'), ('native', 'binary64-real-imag'), ('little', None), ('little', 'imag-real')):
            with self.assertRaises(ValueError): h.decode_blob(bytes(16), endian=endian, layout=layout)
        with self.assertRaises(ValueError): h.decode_blob(struct.pack('<dd', float('nan'), 0), endian='little', layout='binary64-real-imag')
        with self.assertRaisesRegex(ValueError, 'SOURCE_INPUT_PENDING'):
            h.decode_ionf_row(None, endian='little', layout='binary64-real-imag')

    def test_invalid_row_metadata(self):
        good = [1, 0, 0, 0, 0, 2., 0, 0, bytes(16)]
        for index, value in [(0, 0), (0, 1.0), (0, True), (1, 1), (2, 1), (3, -1), (4, 2), (5, 1), (5, float('inf')), (6, -1), (7, 1)]:
            bad = good.copy(); bad[index] = value
            with self.assertRaises(ValueError): h.decode_ionf_row(bad, endian='little', layout='binary64-real-imag')
        with self.assertRaises(ValueError): h.decode_ionf_row(good[:-1], endian='little', layout='binary64-real-imag')


class CatalogueSyntheticTests(unittest.TestCase):
    # Shapes/field order from actual Hex v2.02 amplitudes.cpp; values manufactured.
    TMAT = 'INSERT OR REPLACE INTO "tmat" VALUES (1,0,0,1,0,0,0,0,0.65,0,1.0,2.0);\n'
    IONF = "INSERT OR REPLACE INTO 'ionf' VALUES (1,0,0,0,0,2.0,0,0,X'"+'00'*16+"');\n"

    def fixture(self, payload, xz=False, cap=h.MAX_BYTES):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/('manufactured.sql.xz' if xz else 'manufactured.sql')
            encoded = lzma.compress(payload) if xz else payload
            path.write_bytes(encoded)
            report = h.catalogue(path, max_bytes=cap)
            self.assertEqual(report['compressed_sha256'], hashlib.sha256(encoded).hexdigest())
            self.assertEqual(report['uncompressed_sha256'], hashlib.sha256(payload).hexdigest())
            self.assertEqual(report['compressed_bytes'], len(encoded))
            self.assertEqual(report['uncompressed_bytes'], len(payload))
            return report

    def test_absent_ionf_pending_not_zero(self):
        report = self.fixture(('BEGIN;\n-- manufactured\n'+self.TMAT+'COMMIT;').encode())
        self.assertEqual(report['status'], 'SOURCE_INPUT_PENDING')
        self.assertEqual(report['ionf_rows'], 0)
        self.assertNotIn('cross_section', report)
        self.assertFalse(report['sql_executed'])
        self.assertEqual(report['H1_initial_100']['tmat']['Ei_min_Ry'], .65)

    def test_actual_writer_shapes_xz_identity(self):
        payload = ('/* manufactured */\nBEGIN;\n'+self.TMAT+self.TMAT.replace('0.65','1.25')+self.IONF+'COMMIT;').encode()
        report = self.fixture(payload, xz=True)
        self.assertEqual(report['status'], 'RAW_H1_IONF_PRESENT_ABI_UNCONFIRMED')
        self.assertEqual(report['insert_row_counts'], {'tmat': 2, 'ionf': 1})
        self.assertEqual(report['statement_counts'], {'BEGIN': 1, 'INSERT': 3, 'COMMIT': 1})
        self.assertEqual(report['H1_initial_100']['tmat']['Ei_max_Ry'], 1.25)
        self.assertEqual(report['H1_initial_100']['ionf']['rows'], 1)

    def test_non_h1_payload_does_not_admit_h1(self):
        report = self.fixture(self.IONF.replace('(1,0,0,', '(2,1,0,').encode())
        self.assertEqual(report['status'], 'SOURCE_INPUT_PENDING')
        self.assertEqual(report['ionf_rows'], 1)
        self.assertEqual(report['H1_initial_100']['ionf']['rows'], 0)

    def test_explicit_schema_fail_closed_malformed(self):
        cols = ','.join(h.IONF_COLUMNS)
        report = self.fixture(self.IONF.replace('VALUES', '('+cols+') VALUES').encode())
        self.assertEqual(report['ionf_rows'], 1)
        bad_statements = (self.IONF.replace('VALUES', '(cheb,ni,li,mi,L,S,Ei,l1,l2) VALUES'), self.TMAT.replace(',2.0', ''), 'INSERT INTO ionf VALUES (1,2);', 'BEGIN', "SELECT 'unterminated;")
        for sql in bad_statements:
            with self.assertRaises(ValueError): self.fixture(sql.encode())
        with self.assertRaises(ValueError): self.fixture(self.TMAT.encode(), cap=10)

    def test_run_lexer_all_chunk_boundaries_comments_quoted_semicolons(self):
        payload = b"# synthetic\n-- comment\nSELECT 'a;''b';/* ; */SELECT 2;"
        for width in (1, 2, 3, 7, 65536):
            parser, statements = h.StatementStream(), []
            for start in range(0, len(payload), width):
                statements.extend(parser.feed(payload[start:start+width]))
            parser.finish()
            self.assertEqual(statements, ["SELECT 'a;''b';", 'SELECT 2;'])

    def test_comment_is_token_separator_and_trailing_comment_allowed(self):
        parser = h.StatementStream()
        statements = list(parser.feed(b'SELECT/*comment*/2;--tail'))
        parser.finish()
        self.assertEqual(statements, ['SELECT 2;'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
