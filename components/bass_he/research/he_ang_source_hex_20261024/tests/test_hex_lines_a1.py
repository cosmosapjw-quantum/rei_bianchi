"""A1-only manufactured line-dialect controls; does not replay previous tests."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'code'))
import hex_intake as h

TMAT = 'INSERT INTO tmat VALUES(1,0,0,1,0,0,0,0,0.65,0,1,2)'
IONF = "INSERT OR REPLACE INTO ionf VALUES(1,0,0,0,0,2,0,0,X'"+'00'*16+"')"


class HexLinesA1Tests(unittest.TestCase):
    def fixture(self, text, dialect='hex-lines'):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'SYNTHETIC.sql'
            payload = text.encode()
            path.write_bytes(payload)
            report = h.catalogue(path, dialect=dialect)
            self.assertEqual(report['uncompressed_sha256'], hashlib.sha256(payload).hexdigest())
            self.assertFalse(report['sql_executed'])
            return report

    def test_boundaries_crlf_and_eof(self):
        payload = ('# synthetic\r\nBEGIN TRANSACTION\r\n'+TMAT+'\r\nCOMMIT').encode()
        for width in (1, 2, 7, 65536):
            stream, records = h.HexLinesStream(), []
            for offset in range(0, len(payload), width):
                records.extend(stream.feed(payload[offset:offset+width]))
            records.extend(stream.finish())
            self.assertEqual(records, ['BEGIN TRANSACTION', TMAT, 'COMMIT'])

    def test_optional_semicolon_known_records_and_absence(self):
        report = self.fixture('BEGIN TRANSACTION;\nCREATE TABLE tmat (ni INTEGER);\n'+TMAT+';\n-- synthetic\nCOMMIT;')
        self.assertEqual(report['statement_counts'], {'BEGIN': 1, 'CREATE': 1, 'INSERT': 1, 'COMMIT': 1})
        self.assertEqual(report['status'], 'SOURCE_INPUT_PENDING')
        self.assertEqual(report['ionf_rows'], 0)
        self.assertNotIn('cross_section', report)

    def test_schema_presence_and_no_h1_promotion(self):
        report = self.fixture(TMAT+'\n'+IONF)
        self.assertEqual(report['status'], 'RAW_H1_IONF_PRESENT_ABI_UNCONFIRMED')
        self.assertEqual(report['H1_initial_100']['ionf']['rows'], 1)
        non_h1 = self.fixture(IONF.replace('(1,0,0,', '(2,1,0,'))
        self.assertEqual(non_h1['status'], 'SOURCE_INPUT_PENDING')
        self.assertEqual(non_h1['ionf_rows'], 1)
        for bad in (TMAT.replace(',1,2)', ',1)'), IONF.replace('VALUES', '(cheb,ni,li,mi,L,S,Ei,l1,l2) VALUES')):
            with self.assertRaises(ValueError): self.fixture(bad)

    def test_multiline_multiple_values_multiple_statements_rejected(self):
        for bad in (TMAT.replace('VALUES(', 'VALUES(\n'), TMAT+', (1,2)', TMAT+';'+TMAT+';', 'INSERTfoo VALUES(1)', 'SELECT 1', 'CREATE TABLE unknown (a INTEGER)', 'CREATE TABLE tmat (\nni INTEGER)'):
            with self.assertRaises(ValueError): self.fixture(bad)

    def test_default_still_requires_semicolon_and_limits_unchanged(self):
        self.assertEqual(h.MAX_BYTES, 128*1024**2)
        self.assertEqual(h.MAX_STATEMENT, 8*1024**2)
        with self.assertRaises(ValueError): self.fixture(TMAT, dialect='semicolon')
        report = self.fixture(TMAT+';', dialect='semicolon')
        self.assertEqual(report['dialect'], 'semicolon')
        self.assertEqual(report['insert_row_counts'], {'tmat': 1})


if __name__ == '__main__':
    unittest.main(verbosity=2)
