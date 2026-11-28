import copy
import json
import tempfile
import unittest
from decimal import Decimal,localcontext,getcontext
getcontext().prec=90
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.state_branching import (
    PDF_SHA, PDF_BYTES, PRINTED_ZERO, EXPECTED_GRID_SHA256,
    SOURCE_STATUS, SourceError,source_record,extract_source_tokens,
    strict_source_record,parse_rate,build_result,piecewise_equal_reactants,sha256)
ROOT=Path(__file__).resolve().parents[1]
PDF=ROOT/'sources/GL2022_CSIC_supplement.pdf'
DATA=ROOT/'sources/GL2022_NATIVE_PRODUCT_GRID_R25.json'
RESULT=ROOT/'results/BRANCHING_NATIVE_R25.json'
HISTORY=ROOT/'results/TWO_SEGMENT_PRODUCT_HISTORY.json'
class TestOriginalGL2022Branching(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src=json.loads(DATA.read_text()); cls.r=build_result(cls.src)
    def test_original_pdf_exact(self):
        self.assertEqual(PDF.stat().st_size,PDF_BYTES)
        self.assertEqual(sha256(PDF),PDF_SHA)
    def test_original_100_tokens(self):
        self.assertEqual(extract_source_tokens(PDF),strict_source_record(self.src))
    def test_grid_shape(self):
        self.assertEqual(len(self.src['tokens_by_product_J']),10)
        self.assertTrue(all(len(x)==10 for x in self.src['tokens_by_product_J']))
    def test_native_original_105K_J1(self):
        self.assertEqual(self.src['tokens_by_product_J'][1][2],'1.15(10)')
        self.assertEqual(parse_rate('1.15(10)'),Decimal('1.15e-10'))
    def test_native_original_15K_J0(self):
        self.assertEqual(parse_rate(self.src['tokens_by_product_J'][0][0]),Decimal('2.23e-11'))
    def test_original_15K_printed_zeros(self):
        self.assertEqual([j for j in range(10) if self.src['tokens_by_product_J'][j][0]==PRINTED_ZERO],[6,7,8,9])
        self.assertIsNone(parse_rate(PRINTED_ZERO))
    def test_15K_does_not_admit_complete_branching(self):
        row=self.r['data'][0]
        self.assertEqual(row['coverage'],'PARTIAL_CENSORED_PRINTED_ZERO')
        self.assertIsNone(row['reported_total_rate_cm3_s'])
        self.assertIsNone(row['branch_fraction_J_conditional'])
        self.assertEqual(row['printed_zero_unqualified_J'],[6,7,8,9])
    def test_remaining_nine_temperatures_qualified_reported_set(self):
        self.assertEqual(sum(row['reported_total_rate_cm3_s'] is not None for row in self.r['data']),9)
        self.assertEqual(self.r['positive_printed_cells'],96)
    def test_105K_source_sum(self):
        self.assertEqual(Decimal(self.r['data'][2]['reported_total_rate_cm3_s']),Decimal('2.9180308002830054710000009610113e-10'))
    def test_105K_J1_fraction(self):
        j1=Decimal(self.r['data'][2]['branch_fraction_J_conditional'][1])
        self.assertTrue(Decimal('0.39410')<j1<Decimal('0.39411'))
    def test_255K_J1_fraction(self):
        j1=Decimal(self.r['data'][3]['branch_fraction_J_conditional'][1])
        self.assertTrue(Decimal('0.50475')<j1<Decimal('0.50477'))
    def test_55_3005_sum_to_one(self):
        for row in self.r['data'][1:]:
            with self.subTest(T=row['T_K']):
                self.assertLess(abs(sum(map(Decimal,row['branch_fraction_J_conditional']))-1),Decimal('1e-70'))
    def test_spin_and_state_average(self):
        for row in self.r['data'][1:]:
            with self.subTest(T=row['T_K']):
                f=list(map(Decimal,row['branch_fraction_J_conditional']))
                self.assertLess(abs(sum(f[j] for j in (1,3,5,7,9))-Decimal(row['ortho_fraction_J_odd_conditional'])),Decimal('1e-70'))
                self.assertLess(abs(sum(Decimal(j)*f[j] for j in range(10))-Decimal(row['mean_J_conditional'])),Decimal('1e-70'))
    def test_full_replay_json(self):
        self.assertEqual(self.r,json.loads(RESULT.read_text()))
    def test_physical_authority_strict_null(self):
        for k in ('physical_Q_event','physical_bath','reverse_rates','physical_rate_uncertainty','owner_ACK','full_A','source_native_PES_threshold'):
            self.assertIsNone(self.r[k],k)
        self.assertEqual(self.r['canonical_DAG'],'34/49_UNCHANGED')
    def test_literal_mutation_rejected(self):
        r=copy.deepcopy(self.src);r['tokens_by_product_J'][3][8]='9.99(10)'
        with self.assertRaises(SourceError):strict_source_record(r)
    def test_reaction_mutation_rejected(self):
        r=copy.deepcopy(self.src);r['channel']=r['channel'].replace('D+ + H2','H+ + HD')
        with self.assertRaises(SourceError):strict_source_record(r)
    def test_energy_promotion_rejected(self):
        for k in ('physical_Q_J_per_event','source_native_PES_threshold','physical_rate_uncertainty','owner_ACK'):
            r=copy.deepcopy(self.src);r[k]='0'
            with self.subTest(k=k),self.assertRaises(SourceError):strict_source_record(r)
    def test_parent_gate_mutation_rejected(self):
        r=copy.deepcopy(self.src);r['central_DAG']='35/49'
        with self.assertRaises(SourceError):strict_source_record(r)
    def test_pdf_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.pdf';b=PDF.read_bytes();p.write_bytes(b[:-1]+b'0')
            with self.assertRaises(SourceError):extract_source_tokens(p)
    def test_synthetic_scenario_invariants(self):
        r=json.loads(HISTORY.read_text())
        for k in ('H_nuclei','D_nuclei','charge','particles'):
            self.assertLess(abs(Decimal(r['conservation'][k+'_initial'])-Decimal(r['conservation'][k+'_final'])),Decimal('1e-60'))
        self.assertTrue(Decimal('.80')<Decimal(r['conversion_fraction'])<Decimal('.82'))
        self.assertEqual(r['owner_ACK'],None)
    def test_synthetic_scenario_replay(self):
        r=piecewise_equal_reactants(self.src,n0_m3=Decimal('1e6'),schedule=((105,Decimal('5e9')),(255,Decimal('5e9'))))
        self.assertEqual(r,json.loads(HISTORY.read_text()))
    def test_15K_chemistry_rejected(self):
        with self.assertRaises(SourceError):piecewise_equal_reactants(self.src,n0_m3=Decimal('1e6'),schedule=((15,Decimal('5e9')),))
    def test_off_grid_rejected(self):
        with self.assertRaises(ValueError):piecewise_equal_reactants(self.src,n0_m3=Decimal('1e6'),schedule=((100,Decimal('5e9')),))
    def test_two_same_segments_identical_to_one(self):
        a=piecewise_equal_reactants(self.src,n0_m3=Decimal('1e6'),schedule=((105,Decimal('1e9')),(105,Decimal('4e9'))))
        b=piecewise_equal_reactants(self.src,n0_m3=Decimal('1e6'),schedule=((105,Decimal('5e9')),))
        self.assertLess(abs(Decimal(a['end_Dplus_m3'])-Decimal(b['end_Dplus_m3'])),Decimal('1e-65'))
        for x,y in zip(a['end_H2_v0J0_to_J9_m3'],b['end_H2_v0J0_to_J9_m3']):
            self.assertLess(abs(Decimal(x)-Decimal(y)),Decimal('1e-65'))
    def test_order_memory_identity(self):
        with localcontext() as ctx:
            ctx.prec=70
            n=Decimal('1e6');t=Decimal('5e9')
            a=piecewise_equal_reactants(self.src,n0_m3=n,schedule=((105,t),(255,t)))
            b=piecewise_equal_reactants(self.src,n0_m3=n,schedule=((255,t),(105,t)))
            self.assertEqual(a['end_Dplus_m3'],b['end_Dplus_m3'])
            kA=Decimal(a['schedule'][0]['K_reported_m3_s']);kB=Decimal(a['schedule'][1]['K_reported_m3_s'])
            x=n*kA*t;y=n*kB*t
            factor=n*x*y*(x+y+2)/((x+1)*(y+1)*(x+y+1))
            sourceA=self.r['data'][2]['branch_fraction_J_conditional']
            sourceB=self.r['data'][3]['branch_fraction_J_conditional']
            for j in range(10):
                difference=Decimal(a['end_H2_v0J0_to_J9_m3'][j])-Decimal(b['end_H2_v0J0_to_J9_m3'][j])
                # sourceA/B printed at precision 75; 70-place independent context
                predicted=(Decimal(sourceA[j])-Decimal(sourceB[j]))*factor
                self.assertLess(abs(difference-predicted),Decimal('1e-55'),j)
            self.assertTrue(Decimal(a['end_H2_v0J0_to_J9_m3'][1])<Decimal(b['end_H2_v0J0_to_J9_m3'][1]))
    def test_independent_scipy_ivp(self):
        import numpy as np
        from scipy.integrate import solve_ivp
        r=build_result(self.src)
        target=json.loads(HISTORY.read_text())
        state=np.array([1e6,1e6,0]+[0]*10,dtype=float)
        for T in (105,255):
            ti=[r['data'][i]['T_K'] for i in range(10)].index(T)
            kj=np.array([float(parse_rate(self.src['tokens_by_product_J'][j][ti])*Decimal('1e-6')) for j in range(10)])
            K=float(kj.sum())
            dt=5e9
            def fun(u,z):
                q=z[0]*z[1]*dt
                return np.concatenate(([-K*q,-K*q,K*q],kj*q))
            ivp=solve_ivp(fun,(0.,1.),state,method='DOP853',rtol=3e-12,atol=1e-9)
            self.assertTrue(ivp.success)
            state=ivp.y[:,-1]
        oracle=np.array([float(target['end_Hplus_m3']),float(target['end_HD_v0J2_m3']),
                         float(target['end_Dplus_m3'])]+[float(v) for v in target['end_H2_v0J0_to_J9_m3']])
        self.assertLess(np.max(np.abs(state-oracle)),2e-5)

if __name__=='__main__':unittest.main()
