"""Physical and provenance tests for the fixed-geometry native H3+ dataset."""
import csv, hashlib, math, unittest, zipfile
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from generate import PES,MP,MD,EH_K,EXPECTED_NATIVE_SHA,EXPECTED_R38_ARCHIVE_SHA,jacobi_sides,interaction,midpoint_transform
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results'
PESLIB=PES(ROOT/'private_native/libh3plus.so')

def read_csv(path):
    with (OUT/path).open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))

class TestNativeThreeBodyScience(unittest.TestCase):
    def test_01_source_identity(self):
        p=ROOT/'private_native/h3plus.f'
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),EXPECTED_NATIVE_SHA)
        zp=ROOT/'source_r38/source_original/084307_1_supplements.zip'
        self.assertEqual(hashlib.sha256(zp.read_bytes()).hexdigest(),'a781d3b6f7d3cdffc210f2e8abd436e7378eb3716af80eb96b102a542eaba304')
    def test_02_parent_identity(self):
        p=ROOT/'source_r38/WU_R38_VELILLA_BO_R37_RECONCILIATION_20261031_SOURCE.zip'
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),EXPECTED_R38_ARCHIVE_SHA)
    def test_03_triangle_geometric_constraints(self):
        for R in (3.,6.,10.,25.):
            for c in (-.99,-.1,.55,.99):
                for ma,mb in ((MP,MD),(MP,MP)):
                    sides=jacobi_sides(R,1.4,c,ma,mb)
                    self.assertGreater(2*max(sides),0)
                    self.assertLess(2*max(sides),sum(sides))
                    self.assertAlmostEqual(sides[0],1.4)
    def test_04_permutation_invariance(self):
        cases=((1.45,2.8,3.1),(1.55,5.1,6.0),(4.2,3.4,2.0))
        from itertools import permutations
        for sides in cases:
            ref=PESLIB.e1(*sides)
            for p in permutations(sides):self.assertLess(abs(PESLIB.e1(*p)-ref),2e-11)
    def test_05_homonuclear_parity(self):
        for R in (4.,8.,20.,100.):
            for c in (.1,.4,.9):
                self.assertLess(abs(interaction(PESLIB,R,1.4,c,MP,MP)-interaction(PESLIB,R,1.4,-c,MP,MP)),2e-11)
    def test_06_exact_COM_translation(self):
        for R in (4.,8.,20.,90.):
            for c in (-.95,-.34,.2,.7,.99):
                v_hd=interaction(PESLIB,R,1.4,c,MP,MD)
                rm,cm=midpoint_transform(R,1.4,c,MP,MD)
                v_h2coord=interaction(PESLIB,rm,1.4,cm,MP,MP)
                self.assertLess(abs(v_hd-v_h2coord),2e-11)
        tab=read_csv('COM_MIDPOINT_TRANSLATION_192.csv')
        self.assertEqual(len(tab),192)
        self.assertLess(max(abs(float(q['residual_hartree'])) for q in tab),2e-11)
    def test_07_legendre_odd_parity(self):
        tab=read_csv('NATIVE_PES_LEGENDRE_168.csv')
        self.assertEqual(len(tab),168)
        h2=[x for x in tab if x['arrangement']=='Dplus_H2']
        self.assertLess(max(abs(float(x['Legendre_a1_hartree'])) for x in h2),2e-11)
        hd=[x for x in tab if x['arrangement']=='Hplus_HD' and x['r_index']=='1' and x['R_bohr']=='20']
        self.assertEqual(len(hd),1)
        self.assertGreater(abs(float(hd[0]['Legendre_a1_hartree'])),1e-8)
    def test_08_moments_independent_quadrature(self):
        x,w=leggauss(48)
        R=32.;r=1.4
        u=np.array([interaction(PESLIB,R,r,float(c),MP,MP) for c in x])
        a0=np.dot(w,u)/2
        tab=read_csv('NATIVE_PES_LEGENDRE_168.csv')
        target=next(q for q in tab if q['arrangement']=='Dplus_H2' and q['r_index']=='1' and float(q['R_bohr'])==32.)
        self.assertLess(abs(a0-float(target['Legendre_a0_hartree'])),2e-12)
    def test_09_isotropic_C4_stability(self):
        import json
        with (OUT/'SUMMARY.json').open() as f:
            v=json.load(f)
        c4=v['C4_isotropic_infinite_R_frozen_r_hartree_bohr4']
        self.assertTrue(2.4<c4<2.8)
        moments=read_csv('NATIVE_PES_LEGENDRE_168.csv')
        for R in ('110.0','160.0'):
            row=next(x for x in moments if x['arrangement']=='Dplus_H2' and x['r_index']=='1' and float(x['R_bohr'])==float(R))
            self.assertLess(abs(float(row['C4_iso_at_R_hartree_a0_4'])-c4),0.002)
    def test_10_mass_and_centrifugal_barrier(self):
        rows=read_csv('ISOTROPIC_C4_CENTRIFUGAL_24.csv')
        self.assertEqual(len(rows),24)
        mu_i=MP*(MP+MD)/(2*MP+MD)
        mu_f=MD*(2*MP)/(2*MP+MD)
        for ell in (1,2,3,5,9):
            a=next(x for x in rows if x['arrangement']=='Hplus_HD' and int(x['orbital_l'])==ell)
            b=next(x for x in rows if x['arrangement']=='Dplus_H2' and int(x['orbital_l'])==ell)
            self.assertAlmostEqual(float(a['mu_relative_me'])/mu_i,1.,places=12)
            self.assertAlmostEqual(float(b['mu_relative_me'])/mu_f,1.,places=12)
            self.assertAlmostEqual(float(a['barrier_K'])/float(b['barrier_K']),(mu_f/mu_i)**2,places=9)
            rad=float(a['barrier_R_bohr']); L=ell*(ell+1)
            self.assertLess(abs(rad*rad*L-4*mu_i*float(a['C4_iso_hartree_bohr4']))/(rad*rad*L),3e-12)
    def test_11_thermal_erratum_domain(self):
        tab=read_csv('PUBLISHED_THERMAL_ERRATUM_12.csv')
        self.assertEqual(len(tab),12)
        for row in tab:
            T=float(row['T_K'])
            self.assertTrue(100<=T<=400)
            corr=float(row['erratum_2021_corrected_total_fit_cm3_s'])
            self.assertLess(abs(corr/(9.94e-10*math.exp(-439/T))-1),1e-11)
            self.assertLess(float(row['erratum_over_original_fit']),0.6)
    def test_12_spin_metadata_source_lock(self):
        rows=read_csv('R38_TI_QM_ERRATUM_CHANNEL_70.csv')
        self.assertEqual(len(rows),70)
        self.assertEqual(len({(a['HD_j'],a['H2_jprime']) for a in rows}),70)
        for row in rows:
            jp=int(row['H2_jprime'])
            self.assertEqual(row['Lepers_2021_erratum_para_ortho_group'],('para' if jp%2==0 else 'ortho'))
            self.assertEqual(float(row['Lepers_2021_multiplier_for_2019_unweighted_state_rate']),(.25 if jp%2==0 else .75))
            self.assertEqual(row['rate_value_available'],'false')
    def test_13_original_source_grid_not_modified(self):
        rows=read_csv('NATIVE_PES_3BODY_JACOBI_5376.csv')
        self.assertEqual(len(rows),5376)
        self.assertTrue(all(math.isfinite(float(x['V_minus_h2_hartree'])) for x in rows))
        self.assertEqual(len({(x['arrangement'],x['r_index'],x['R_bohr'],x['cos_theta']) for x in rows}),5376)

if __name__=='__main__':unittest.main()
