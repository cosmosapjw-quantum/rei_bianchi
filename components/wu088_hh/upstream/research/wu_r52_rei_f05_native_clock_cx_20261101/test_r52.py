"""R52: scientific and executable regression tests for real native F05 nH, clock and CX."""
import csv,gzip,math,tempfile,unittest,shutil
from pathlib import Path
import numpy as np
import r52_rei_native_clock_kinetics as m

class TestR52(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.z,cls.vol,cls.nh,cls.den,cls.T0,cls.T1,cls.x0,cls.x1,cls.du=m.load_original()
  m.model_table=(cls.z["knots"],cls.z["lnkf"],cls.z["lnkb"])
  cls.res=__import__("json").loads((m.ROOT/"results/R52_RESULT.json").read_text())

 def test_immutable_real_original_source_identity(self):
  for k,sha in m.SHA.items():self.assertEqual(m.sha(m.SOURCE/k),sha)

 def test_original_rei_46080_cell_H_nuclei_exact(self):
  self.assertEqual(len(self.nh),m.N)
  self.assertTrue(np.array_equal(self.z["NH0"],self.nh))
  self.assertAlmostEqual(float(self.z["W"].sum()),1,delta=1e-14)

 def test_source_proper_volume_geometry_from_17_z_nodes(self):
  self.assertEqual(self.z["original_forcing_node_count"],17)
  self.assertEqual(self.z["source_first_z"],5.95)
  vv=self.z["W"]*m.MPC_CM**3/(1+5.95)**3
  self.assertTrue(np.array_equal(vv,self.vol))
  self.assertTrue(np.all(self.den>0))

 def test_source_original_tick_clock(self):
  self.assertAlmostEqual(self.z["dt"],4871848749.16828,delta=1e-2)
  self.assertAlmostEqual(self.z["t1"]-self.z["t0"],self.z["dt"],delta=1e-4)

 def test_source_savin_published_rate_nodes(self):
  a,b=m.savin_rate(np.array([10000.,2000.,50000.]),*m.model_table)
  self.assertAlmostEqual(float(a[0]),8.04e-9,delta=3e-22)
  self.assertAlmostEqual(float(b[0]),8.07e-9,delta=3e-22)
  self.assertTrue(np.all(a>0) and np.all(b>0))

 def test_savin_domain_fail_closed(self):
  with self.assertRaises(ValueError):m.savin_rate(np.array([1000.,201000.]),*m.model_table)
  with self.assertRaises(ValueError):m.savin_rate(np.array([float("nan")]),*m.model_table)

 def test_frozen_donor_zero_time_identity(self):
  x=np.array([.99,.999]);T=np.array([10000.,5000.]);den=np.array([1e-4,0.01]);y0=np.array([0.3,.4])
  y=m.rk4_coupled(y0,x,x,T,T,den,0.,"linear",16)
  self.assertTrue(np.array_equal(y,y0))

 def test_constant_donor_three_modes_equivalent(self):
  x=np.array([.99,.999]);T=np.array([10000.,5000.]);den=np.array([1e-4,0.01]);y0=np.array([.2,.3])
  ref=m.rk4_coupled(y0,x,x,T,T,den,self.z["dt"],"linear",64)
  self.assertTrue(np.allclose(ref,m.rk4_coupled(y0,x,x,T,T,den,self.z["dt"],"left",64),atol=1e-14,rtol=0))
  self.assertTrue(np.allclose(ref,m.rk4_coupled(y0,x,x,T,T,den,self.z["dt"],"right",64),atol=1e-14,rtol=0))

 def test_passive_limit_constant_donor_exact_exponential(self):
  x=np.array([.99,.5]);T=np.array([10000.,5000.]);den=np.array([1e-4,0.01]);y0=np.array([0.,1.])
  kf,kb=m.savin_rate(T,*m.model_table)
  lam=(kf*x+kb*(1-x))*den
  ystar=kf*x/(kf*x+kb*(1-x))
  want=ystar+(y0-ystar)*np.exp(-lam*self.z["dt"])
  got=m.rk4_coupled(y0,x,x,T,T,den,self.z["dt"],"linear",64,eta=0.)
  self.assertLess(float(np.max(np.abs(got-want))),2e-9)

 def test_native_real_data_all_rows_charge_and_energy(self):
  src=m.ROOT/"results/R52_ORIGINAL_REI_F05_REAL_PROPER_D_CX_46080.csv.gz"
  n=0
  with gzip.open(src,"rt",newline="") as f:
   reader=csv.DictReader(f)
   self.assertEqual(reader.fieldnames,m.COLS)
   for r in reader:
    self.assertEqual(int(r["node"]),n);n+=1
    dens=float(r["original_nH_proper_cm3"]);w=float(r["original_comoving_weight_W"]);Nh=float(r["original_NH_nuclei"])
    self.assertGreater(dens,0)
    self.assertAlmostEqual(dens*w*m.MPC_CM**3/(1+5.95)**3,Nh,delta=4e-14*Nh)
    for kind in ["neutral","ionized","eq160"]:
     y0=float(r["CX_y0_"+kind]);y1=float(r["CX_y_final_"+kind])
     self.assertGreaterEqual(y1,0);self.assertLessEqual(y1,1)
     corr=float(r["CX_Hplus_compensation_"+kind])
     heat=float(r["CX_net_energy_erg_per_H_"+kind])
     self.assertAlmostEqual(corr,-m.ETA*(y1-y0),delta=2e-18)
     self.assertAlmostEqual(heat,-m.ETA*m.E_REACTION_ERG*(y1-y0),delta=2e-30)
    self.assertLessEqual(abs(float(r["CX_electron_total_CX_excess_per_H_neutral"])),4e-16)
    self.assertLessEqual(abs(float(r["CX_electron_total_CX_excess_per_H_ionized"])),4e-16)
  self.assertEqual(n,m.N)

 def test_non_equilibrium_effect_is_physical_not_stationary_relabeling(self):
  s=self.res["source_physics"]
  self.assertLess(s["median_theta_CX"],.01)
  self.assertGreater(s["N_theta_below_001"],m.N//2)
  self.assertLess(s["initial_scenario"]["neutral"]["final_Dplus"]["median"],.01)
  self.assertGreater(s["initial_scenario"]["ionized"]["final_Dplus"]["median"],.99)

 def test_numerical_convergence_and_donor_sensitivity_recorded(self):
  v=self.res["source_physics"]
  self.assertLess(v["RK32vsRK64_max_abs"]["neutral"],1e-7)
  self.assertLess(v["RK32vsRK64_max_abs"]["ionized"],1e-7)
  self.assertTrue(math.isfinite(v["source_interpolation_sensitivity_maxabs_y0_neutral"]))

 def test_source_energy_sign_both_extreme_scenarios(self):
  s=self.res["source_physics"]["initial_scenario"]
  self.assertGreater(s["neutral"]["N_negative_gas_heat"],m.N//2)
  self.assertGreater(s["ionized"]["N_positive_gas_heat"],m.N//2)
  self.assertAlmostEqual(m.E_REACTION_ERG,0.0037*1.602176634e-12)

 def test_full_result_source_and_dag_no_promotions(self):
  r=self.res
  self.assertEqual(r["actual_original_nodes"],m.N)
  self.assertEqual(r["new_physics_column_count"],len(m.COLS))
  self.assertEqual(r["DAG"]["WU"],"34/49")
  self.assertEqual(r["DAG"]["REI_central"],"28/88")
  self.assertEqual(r["DAG"]["delta"],0)
  self.assertTrue(r["model_contract"]["no_Einstein_Boltzmann_coupling"])
  self.assertEqual(r["model_contract"]["tick161_HHe_material"],"NONAUTHORITATIVE_PREVIEW_ONLY")

 def test_original_source_mutation_detection_no_original_mutation(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/"test"
   shutil.copyfile(m.SOURCE/"SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv",p)
   p.write_bytes(p.read_bytes()+b"\\n")
   self.assertNotEqual(m.sha(p),m.SHA["SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv"])

if __name__=="__main__":unittest.main()
