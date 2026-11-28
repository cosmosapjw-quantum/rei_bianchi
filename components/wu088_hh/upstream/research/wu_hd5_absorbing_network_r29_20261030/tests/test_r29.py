"""WU R29 targeted physics, provenance and software regression tests."""
import hashlib,json,math,sys,unittest,zipfile
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from src import network as n

class NetworkTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.grid=n.load_grid();cls.atlas=n.make_atlas(cls.grid)
 def test_01_full_R28_original_identity(self):
    p=ROOT/'archives/WU_R28_GL2022_PHYSICAL_SOURCE_ORIGINAL_20261030.zip'
    self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),'58cb66e566c2481603933f2ee6894f7fe3b05864847285c458ba8cbebadfb8ea')
    with zipfile.ZipFile(p) as z:
        self.assertIsNone(z.testzip()); self.assertEqual(len(z.namelist()),50)
        self.assertEqual(hashlib.sha256(z.read('sources/GL2022_CSIC_supplement.pdf')).hexdigest(),'a65b1cba4208552e7eac6341b462487b23c5afe79f3ba0d2ca009fdee7dd1754')
 def test_02_source_scope(self):
    self.assertEqual(len(n.TEMPS),7);self.assertEqual(len(self.grid.q),350);self.assertEqual(len(self.grid.down),70)
    self.assertNotIn(1505,n.TEMPS);self.assertNotIn(2505,n.TEMPS);self.assertNotIn(15,n.TEMPS)
 def test_03_no_printed_imputation(self):
    for T,j,k in self.grid.q:self.assertGreater(self.grid.q[(T,j,k)],0)
    for key in self.grid.down:self.assertGreater(self.grid.down[key],0)
 def test_04_wrong_temperature_rejected(self):
    with self.assertRaises(ValueError):n.run_case(self.grid,1505,'raw_SQM',1.,2)
 def test_05_wrong_level_rejected(self):
    with self.assertRaises(ValueError):n.run_case(self.grid,105,'raw_SQM',1.,5)
 def test_06_wrong_rate_token_rejected(self):
    for s in ['0.00(00)','0.00(0)','1.58(10','NaN(11)']:
        with self.assertRaises(n.SourceError):n.decode_token(s)
 def test_07_wrong_policy_rejected(self):
    with self.assertRaises(ValueError):n.reaction_vector(self.grid,105,2,'fantasy')
 def test_08_positive_chem_and_radiation(self):
    for T in n.TEMPS:
        for J in n.LEVELS:
            self.assertGreater(sum(n.reaction_vector(self.grid,T,J,'raw_SQM')),0)
        for J in range(1,5):self.assertGreater(self.grid.A[J],0)
 def test_09_source_measured_reference(self):
    self.assertAlmostEqual(n.reference_density(self.grid,105,'Eq6-7_spin_effective'),3954.41818210718,places=6)
 def test_10_lte_detailed_balance(self):
    for T in n.TEMPS:
        for policy in n.POLICIES:
            G,C,F,k=n.assemble(self.grid,T,policy,n.reference_density(self.grid,T,policy)); weights=np.array([(2*j+1)*math.exp(-(self.grid.energies_cm1[j]-self.grid.energies_cm1[0])*100*n.PLANCK*n.SPEED_LIGHT/(n.BOLTZMANN*T)) for j in n.LEVELS]);weights/=sum(weights)
            self.assertLess(np.linalg.norm(C@weights,ord=np.inf),1e-17)
 def test_11_reaction_sink_and_column_conservation(self):
    G,C,F,k=n.assemble(self.grid,105,'raw_SQM',2300)
    self.assertTrue(np.allclose(G.sum(axis=0)+k,0,rtol=1e-12,atol=1e-18))
    self.assertTrue(np.allclose(C.sum(axis=0),0,rtol=1e-12,atol=1e-18))
 def test_12_all_210_cases(self):
    self.assertEqual(len(self.atlas),210)
    for x in self.atlas:
        self.assertTrue(0<=x['probability_one_or_more_photons_before_exchange']<=1)
        self.assertTrue(0<=x['restricted_H2_v0_odd_Jprime_probability']<=1)
        self.assertTrue(x['expected_photons_before_exchange']>=0)
        self.assertAlmostEqual(sum(x['restricted_H2_v0_product_Jprime_probabilities']),1,places=9)
        self.assertAlmostEqual(sum(x['restricted_exchange_reaction_level_probabilities']),1,places=9)
 def test_13_first_event_vs_later_photons(self):
    grid=self.grid;T=105;policy='Eq6-7_spin_effective';nH=n.reference_density(grid,T,policy)
    G,C,F,k=n.assemble(grid,T,policy,nH)
    first_direct=grid.A[2]/(-G[2,2]);later=n.run_case(grid,T,policy,1.,2)['probability_one_or_more_photons_before_exchange']
    self.assertGreater(later,first_direct)
    self.assertGreater(later,0.47)
 def test_14_num_real_rates_not_just_synthetic(self):
    source=json.loads((ROOT/'sources/GL2022_700_SOURCE.json').read_text());self.assertEqual(source['pdf_sha256'],'a65b1cba4208552e7eac6341b462487b23c5afe79f3ba0d2ca009fdee7dd1754')
    self.assertEqual(source['shape'],[10,7,10])
 def test_15_selected_ode_reference(self):
    g=self.grid;T=255;policy='Eq6-7_spin_effective';nH=n.reference_density(g,T,policy)
    G,_,_,chem=n.assemble(g,T,policy,nH);init=np.zeros(5);init[4]=1
    from scipy.integrate import solve_ivp
    t_end=1e9
    sol=solve_ivp(lambda t,x:G@x,(0,t_end),init,rtol=2e-10,atol=2e-13,method='DOP853',dense_output=False)
    self.assertTrue(sol.success);self.assertLess(max(abs(sol.y[:,-1])),5e-9)
    self.assertGreater(min(sol.y[:,-1]),-1e-12)
 def test_16_negative_source_tamper(self):
    v=n.SHA['inelastic'];n.SHA['inelastic']='0'*64
    try:
        with self.assertRaises(n.SourceError):n.read_verified('inelastic')
    finally:n.SHA['inelastic']=v
 def test_17_raw_not_effective_spin_policy(self):
    raw=n.reaction_vector(self.grid,105,2,'raw_SQM');spin=n.reaction_vector(self.grid,105,2,'Eq6-7_spin_effective')
    self.assertTrue(np.allclose(spin[::2],raw[::2]/4,rtol=1e-14))
    self.assertTrue(np.allclose(spin[1::2],3*raw[1::2]/4,rtol=1e-14))
 def test_20_explicit_upward_counterfactual(self):
    from src.counterfactual import downward_only
    g=self.grid
    p0,count0=downward_only(g,105,'Eq6-7_spin_effective')
    self.assertAlmostEqual(p0,0.10682600817662444,places=10)
    self.assertLess(p0,n.run_case(g,105,'Eq6-7_spin_effective',1.,2)['probability_one_or_more_photons_before_exchange'])
    self.assertGreater(count0,0)
 def test_19_lab_1984_printed_line_consistency(self):
    cross=json.loads((ROOT/'results/LAB1984_2011_CROSSWALK.json').read_text())
    self.assertEqual(cross['CDMS_minus_1984_cm1'],'0.000958')
    self.assertTrue(cross['absolute_delta_smaller_than_single_published_pm'])
    self.assertTrue(cross['not_a_statistical_independence_or_model_validation'])
 def test_18_first_photon_inequality(self):
    for x in self.atlas:
        G,_,_,_=n.assemble(self.grid,x['T_K'],x['policy'],x['nHplus_cm3']);j=x['initial_J'];first=self.grid.A[j]/(-G[j,j]) if j>0 else 0
        self.assertGreaterEqual(x['probability_one_or_more_photons_before_exchange']+1e-12,first)

if __name__=='__main__':unittest.main()