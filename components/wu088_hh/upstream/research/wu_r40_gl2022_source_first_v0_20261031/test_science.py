#!/usr/bin/env python3
"""R40 targeted source, physical invariants, and independent mathematical checks."""
import csv, io, json, sys, unittest, zipfile
from pathlib import Path
import numpy as np
from mpmath import mp
from generate import (parse_pdf_token_tables, load_parent_emaa, first_hit, sha, compute, EXPECTED_EPAPS_SHA,EXPECTED_PDF_SHA)
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results'
def rows(file):
    with (OUT/file).open(newline='') as f:return list(csv.DictReader(f))
class R40Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t,cls.t11=parse_pdf_token_tables(ROOT/'input/H_HD_rate_Supplementary_Material.pdf')
        cls.mod,cls.data,cls.cross,cls.valid,cls.missing=load_parent_emaa(ROOT/'r36')
    def test_A_pdf_source(self):
        self.assertEqual(sha(ROOT/'input/H_HD_rate_Supplementary_Material.pdf'),EXPECTED_PDF_SHA)
        self.assertEqual(sha(ROOT/'input/original_214302_1_epaps.zip'),EXPECTED_EPAPS_SHA)
    def test_B_pdf_identical_prior_R36(self):
        with zipfile.ZipFile(ROOT/'input/WU_R36_SOURCE_ORIGINAL_20261030.zip') if (ROOT/'input/WU_R36_SOURCE_ORIGINAL_20261030.zip').exists() else zipfile.ZipFile(ROOT/'input/original_214302_1_epaps.zip') as z:
            name='sources/GL2022_CSIC_supplement.pdf' if 'sources/GL2022_CSIC_supplement.pdf' in z.namelist() else 'H_HD_rate_Supplementary_Material.pdf'
            self.assertEqual(sha(ROOT/'input/H_HD_rate_Supplementary_Material.pdf'),__import__('hashlib').sha256(z.read(name)).hexdigest())
    def test_C_all_700_pdf_table_tokens_exact(self):
        prior=json.loads((ROOT/'r33_Gl700_source.json').read_text())
        self.assertEqual(len(self.t),700)
        for (jp,j,T),tok in self.t.items():self.assertEqual(tok,prior['tokens_jprime_j_T'][jp][j][prior['temperature_nodes_K'].index(T)])
    def test_D_table11_exact_tokens(self):
        self.assertEqual(self.t11,json.loads((ROOT/'r33_Gl700_source.json').read_text())['table11_thermal_nominal_tokens'])
    def test_E_GL_source_suspect_unchanged(self):
        self.assertTrue(all(self.t[(0,5,T)]==self.t[(1,5,T)] for T in (15.,55.,105.,255.,505.,1005.,1505.,2005.,2505.,3005.)))
        self.assertEqual(self.t[(7,3,2505.)],'6.72(16)')
    def test_F_mismatch_50_source_lanes(self):
        self.assertEqual(len([z for z in self.cross if z['crosswalk_status']=='PRINTED_NUMERIC_MISMATCH']),50)
        self.assertEqual(len(self.missing),16)
    def test_G_rows_counts(self):
        self.assertEqual([len(rows(x)) for x in ('GL2022_PRINTED_REACTION_700.csv','TABLE11_RECONSTRUCTION_10.csv','FIRST_V0_HIT_BRANCHES_1680.csv','FIRST_V0_HIT_SUMMARY_140.csv','PAIR_ISOLATED_SENSITIVITY_490.csv')],[700,10,1680,140,490])
    def test_H_unit_probability(self):
        b=rows('FIRST_V0_HIT_BRANCHES_1680.csv');s={}
        for v in b:
            key=(v['T_K'],v['initial_J'],v['source_lane']);s[key]=s.get(key,0.)+float(v['P_first_v0_hit'])
        self.assertEqual(len(s),140)
        self.assertLess(max(abs(v-1) for v in s.values()),2e-13)
    def test_I_positive_passage_times(self):
        r=rows('FIRST_V0_HIT_SUMMARY_140.csv')
        self.assertTrue(all(float(v['mean_first_v0_time_at_n1_cm3_s'])>0 for v in r))
        self.assertLess(max(abs(float(v['p_sum'])-1) for v in r),2e-13)
    def test_J_old_v0_pair_structural_zero(self):
        g=[r for r in rows('PAIR_ISOLATED_SENSITIVITY_490.csv') if r['GL_discrepant_transition']=='0J2->0J0']
        self.assertEqual(len(g),70)
        self.assertTrue(all(float(v['only_that_pair_printed_vs_EMAA_P_L1'])==0 for v in g))
    def test_K_detect_high_sensitivity(self):
        b=rows('FIRST_V0_HIT_BRANCHES_1680.csv')
        vals={(float(x['T_K']),int(x['initial_J']),int(x['final_v0_J']),x['source_lane']):float(x['P_first_v0_hit']) for x in b}
        self.assertGreater(abs(vals[(55.,6,10,'GL_printed_hybrid')]-vals[(55.,6,10,'EMAA_primary')]),.075)
    def test_L_mpmath80_first_passage(self):
        mp.dps=80
        for T in (55.,105.,2505.):
            for overrides in (None,self.valid):
                d=first_hit(self.data,self.mod,T,overrides)
                Q=mp.matrix([[mp.mpf(str(y)) for y in row] for row in d['Q_uu']])
                R=mp.matrix([[mp.mpf(str(y)) for y in row] for row in d['Q_au']])
                for j in (0,4,6):
                    rhs=mp.matrix([int(k==j) for k in range(7)])
                    y=mp.lu_solve(-Q,rhs)
                    px=R*y
                    self.assertLess(max(abs(float(px[k])-d['B'][k,j]) for k in range(12)),1.0e-13)
    def test_M_thermal7_source_bounded_comparison(self):
        vals=rows('TABLE11_RECONSTRUCTION_10.csv')
        self.assertTrue(all(.97<float(v['ratio_reconstructed_over_printed'])<1.01 for v in vals))
    def test_N_provenance_lanes_not_owner_correction(self):
        s=json.loads((OUT/'SUMMARY.json').read_text())
        self.assertIn('NO', s['critical_boundary'][-1].upper())
        self.assertEqual(s['canonical_DAG'],'34/49_UNCHANGED')

if __name__=='__main__':unittest.main(verbosity=2)
