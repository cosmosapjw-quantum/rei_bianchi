"""A2-only manufactured grammar and previously reviewed word-boundary tests."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT/'code'))
import hex_intake as new
spec = importlib.util.spec_from_file_location('old_a2_test', UNIT/'evidence'/'execution'/'A1_before'/'pre_A2_hex_intake.py')
old = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = old
spec.loader.exec_module(old)


class A2LiteralTests(unittest.TestCase):
    def outcome(self, module, body):
        try:
            return ('OK', module.parse_insert('INSERT INTO tmat VALUES('+body+');'))
        except ValueError:
            return ('ValueError',)

    def test_same_numeric_literal_grammar(self):
        valid = ['1,0,-1,+2,3.,.4,5e-2,6E+3,0.65,0,-1.2,2', ' 1 , 0\t,0,1,0,0,0,0,1e-05,0,-133.2739,2.522678 ', '.1,+.2,-.3,1.,01,0e0']
        invalid = ['', ',1', '1,', '1,,2', '1+2,0', 'nan,1', 'inf,0', '0x1,0', '1d0,0', '1;2', '1e,0', '1e+,0', '.,0', '--1,0']
        for body in valid+invalid:
            self.assertEqual(self.outcome(old, body), self.outcome(new, body), body)
        for body in valid:
            self.assertEqual(self.outcome(new, body)[0], 'OK')
        for body in invalid:
            self.assertEqual(self.outcome(new, body)[0], 'ValueError')

    def test_blob_and_null_fallback_unchanged(self):
        for body in ["1,0,0,0,0,2,0,0,X'"+'00'*16+"'", '1,NULL,2', "1,X'',2", "1,X'0',2", "1,X'gg',2"]:
            self.assertEqual(self.outcome(old, body), self.outcome(new, body))

    def catalogue(self, line):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'SYNTHETIC.sql'
            path.write_text(line)
            return new.catalogue(path, dialect='hex-lines')

    def test_schema_integer_finite_and_word_boundary_gates(self):
        row = 'INSERT INTO tmat VALUES(1,0,0,1,0,0,0,0,0.65,0,1,2)'
        self.assertEqual(self.catalogue(row)['status'], 'SOURCE_INPUT_PENDING')
        for bad in [row.replace('(1,0,0,', '(1.0,0,0,'), row.replace('0.65', '1e309'), row.replace(',1,2)', ',1)'), row.replace('VALUES', '(ni,mi,li,nf,lf,mf,L,S,Ei,ell,Re_T_ell,Im_T_ell) VALUES'), 'INSERTfoo VALUES(1)', row+';'+row, row.replace('VALUES(', 'VALUES(\n')]:
            with self.assertRaises(ValueError): self.catalogue(bad)


if __name__ == '__main__':
    unittest.main(verbosity=2)
