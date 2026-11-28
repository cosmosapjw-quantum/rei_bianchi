"""Source-identity and physical first-event regression tests for R28."""
import hashlib
import json
import tempfile
import unittest
from collections import Counter
from decimal import Decimal as D, getcontext
getcontext().prec=90
from pathlib import Path
from src.parse_source import validate_original, parse_poppler, parse_fitz, source_catalog
from src.three_hazard import build, write, R27_SHA256

ROOT=Path(__file__).resolve().parents[1]
PDF=ROOT/'sources/GL2022_CSIC_supplement.pdf'
R27=ROOT/'sources/R27_SOURCE_REACTIVE_RADIATIVE.json'

class SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cells, cls.rows=build(PDF,R27)
    def test_pdf_original_identity(self):
        self.assertEqual(validate_original(PDF),'a65b1cba4208552e7eac6341b462487b23c5afe79f3ba0d2ca009fdee7dd1754')
    def test_r27_original_identity(self):
        self.assertEqual(hashlib.sha256(R27.read_bytes()).hexdigest(),R27_SHA256)
    def test_independent_pdf_extractors(self):
        self.assertEqual(parse_poppler(PDF),parse_fitz(PDF))
        self.assertEqual(len(parse_poppler(PDF)),1560)
    def test_exact_table_set_and_row_count(self):
        self.assertEqual({x['table'] for x in self.cells},set(range(12,29)))
        self.assertEqual(len(self.cells),1560)
        self.assertEqual(len({(x['table'],x['initial_v'],x['initial_J'],x['T_K']) for x in self.cells}),1560)
    def test_temperature_exact_nodes(self):
        self.assertEqual(set(x['T_K'] for x in self.cells),{15,55,105,255,505,1005,1505,2005,2505,3005})
        self.assertEqual(len(self.cells)//10,156)
    def test_malformed_source_not_repaired(self):
        bad=[x for x in self.cells if x['status']=='SOURCE_MALFORMED_TOKEN']
        self.assertEqual(len(bad),1)
        self.assertEqual((bad[0]['table'],bad[0]['initial_v'],bad[0]['initial_J'],bad[0]['T_K'],bad[0]['token']),(17,1,2,2005,'1.58(10'))
        self.assertIsNone(bad[0]['rate_cm3_s'])
    def test_suspect_exponent_not_repaired(self):
        x=[x for x in self.cells if x['status']=='SOURCE_SUSPECT_EXPONENT']
        self.assertEqual(len(x),1)
        self.assertEqual((x[0]['table'],x[0]['initial_J'],x[0]['T_K'],x[0]['token']),(12,1,1505,'1.91(11)'))
    def test_diagonal_not_labeled_inelastic(self):
        d=[x for x in self.cells if x['status']=='SOURCE_IDENTITY_DIAGONAL_PRINTED']
        self.assertEqual(len(d),10)
        self.assertTrue(all(x['initial_J']==x['final_J'] and x['initial_v']==x['final_v'] for x in d))
    def test_downward_coverage(self):
        self.assertEqual(len(self.rows),60)
        self.assertEqual(sum(len(x['downward_source_tokens']) for x in self.rows),210)
    def test_dag_protected_and_qualified_count(self):
        accepted=[x for x in self.rows if x['source_rate_status']=='SOURCE_POSITIVE_TRANSCRIBED_A']
        self.assertEqual(len(accepted),43)
        self.assertEqual(Counter(x['source_rate_status'] for x in self.rows),Counter({'PRINTED_ZERO_CENSORED':6,'SOURCE_SUSPECT_DUPLICATE':9,'SOURCE_SUSPECT_EXPONENT':1,'INELASTIC_SOURCE_HELD':1,'SOURCE_POSITIVE_TRANSCRIBED_A':43}))
        self.assertEqual(next(x for x in self.rows if x['J_initial']==1 and x['T_K']==1505)['source_rate_status'],'INELASTIC_SOURCE_HELD')
    def test_all_probabilities_conserve_and_upper(self):
        for x in self.rows:
            if x['source_rate_status']!='SOURCE_POSITIVE_TRANSCRIBED_A':
                self.assertIsNone(x['P_first_exchange_at_R27_ncrit']);continue
            p=[D(x[a]) for a in ('P_first_exchange_at_R27_ncrit','P_first_inelastic_at_R27_ncrit','P_first_radiative_at_R27_ncrit')]
            self.assertLess(abs(sum(p)-D(1)),D('1e-70'))
            self.assertTrue(all(D(0)<y<D(1) for y in p))
            self.assertLessEqual(p[0],D(x['P_exchange_density_infinity_upper_given_down']))
            self.assertLess(p[0],D('0.5'))
    def test_half_crossing_formula(self):
        for x in self.rows:
            if x['source_rate_status']!='SOURCE_POSITIVE_TRANSCRIBED_A':continue
            kx=D(x['K_exchange_Eq6_7_cm3_s']);kc=D(x['K_HD_inelastic_down_cm3_s'])
            crit=x['n_Hplus_for_P_first_exchange_half_cm_neg3']
            if kx>kc:
                self.assertIsNotNone(crit)
                n=D(crit);A=D(x['A_HD_J_to_Jminus1_s_inv']);p=n*kx/(n*(kx+kc)+A)
                self.assertLess(abs(p-D('0.5')),D('1e-70'))
            else:self.assertIsNone(crit)
    def test_explicit_105K_numerical(self):
        known={1:'6.01e-10',2:'1.143e-9',3:'1.222e-9',4:'1.3753e-9',6:'1.6457e-9'}
        for j,k in known.items():
            x=next(r for r in self.rows if r['J_initial']==j and r['T_K']==105)
            self.assertEqual(D(x['K_HD_inelastic_down_cm3_s']),D(k))
        self.assertIsNone(next(x for x in self.rows if x['J_initial']==5 and x['T_K']==105)['P_first_exchange_at_R27_ncrit'])
    def test_input_tampering_fails(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'r27.json';p.write_bytes(R27.read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'R27_SOURCE_HASH_MISMATCH'):build(PDF,p)
            z=Path(t)/'fake.pdf';z.write_bytes(PDF.read_bytes()+b' ')
            with self.assertRaises(ValueError):source_catalog(z)
    def test_reproducible_scientific_json(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t);summary=write(PDF,R27,out)
            self.assertEqual(summary['DAG']['after'],[34,49])
            self.assertIsNone(summary['physical_Q'])
            self.assertIsNone(summary['molecular_owner_ACK'])
            for f in ('INELASTIC_SOURCE_CELLS.json','THREE_HAZARD_ROWS.json','THREE_HAZARD_ROWS.csv','SUMMARY.json'):
                self.assertEqual((out/f).read_bytes(),(ROOT/'results'/f).read_bytes(),f)

if __name__=='__main__':unittest.main()