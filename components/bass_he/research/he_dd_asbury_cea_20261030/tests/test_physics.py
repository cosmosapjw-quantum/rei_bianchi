import importlib.util, math, pathlib, unittest, json, csv, hashlib
R=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("bp",R/"src/build_physics.py")
bp=importlib.util.module_from_spec(spec);spec.loader.exec_module(bp)
class PhysicsTests(unittest.TestCase):
 def test_data_count(self):
  s=bp.load_sources();self.assertEqual(len(s["asbury"]["measurements"]),2);self.assertEqual(len(s["cea"]["records"]),12)
 def test_campaign_count(self):
  self.assertEqual(bp.load_sources()["asbury"]["independent_experiments"],1)
 def test_absolute_units(self):
  self.assertEqual(1e-33/1e-33,1.0);self.assertEqual(bp.load_sources()["asbury"]["measurements"][0]["DA_nb_sr"],6.3)
 def test_mass_binding(self):
  self.assertAlmostEqual(bp.Q_MEV,23.8464782,8)
 def test_energy_consistency(self):
  for E,t in [(220.5,52.4),(265.3,53.2)]:
   a,b,_=bp.pair_birth(E,t);self.assertAlmostEqual(a+b,E-bp.Q_MEV,places=10)
 def test_kine_220(self):
  a,b,d=bp.pair_birth(220.5,52.4);self.assertAlmostEqual(a,118.9857832728,9);self.assertAlmostEqual(b,77.6677385272,9)
 def test_kine_265(self):
  a,b,d=bp.pair_birth(265.3,53.2);self.assertAlmostEqual(a,147.48222969125,9);self.assertAlmostEqual(b,93.97129210875,9)
 def test_pair_exchange(self):
  for E,t in [(220.5,52.4),(265.3,53.2)]:
   a,b,_=bp.pair_birth(E,t);c,d,_=bp.pair_birth(E,180-t);self.assertAlmostEqual(a,d,11);self.assertAlmostEqual(b,c,11)
 def test_threshold_reject(self):
  with self.assertRaises(ValueError):bp.pair_birth(1,45)
 def test_asbury_event_shape(self):
  s=bp.load_sources()
  for x in s["asbury"]["measurements"]:
   est=x["DA_nb_sr"]*bp.asbury_model_total_per_differential(x["theta_cm_deg"])
   self.assertLess(abs(est-x["sigma_event_model_nb"]),0.35)
 def test_cea_range(self):
  s=bp.load_sources()
  self.assertEqual(bp.interp_source_table(s["cea"]["records"],"H",100)[:2],(2.0,27.39))
  self.assertEqual(bp.interp_source_table(s["cea"]["records"],"He",150)[:2],(9.449,8.855))
 def test_cea_out_of_range(self):
  with self.assertRaises(ValueError):bp.interp_source_table(bp.load_sources()["cea"]["records"],"H",200)
 def test_cea_bracket(self):
  _,_,d=bp.interp_source_table(bp.load_sources()["cea"]["records"],"He",119)
  self.assertEqual(d,(100,125))
 def test_cea_monotonic(self):
  s=bp.load_sources()
  for t in ("H","He"):
   r=sorted((x for x in s["cea"]["records"] if x["target"]==t),key=lambda x:x["E_MeV"])
   self.assertTrue(all(x["range_g_cm2"]<y["range_g_cm2"] for x,y in zip(r,r[1:])))
   self.assertTrue(all(x["mass_stopping_MeV_cm2_g"]>y["mass_stopping_MeV_cm2_g"] for x,y in zip(r,r[1:])))
 def test_daughters(self):
  _,m,d=bp.build()
  self.assertEqual(len(m),2);self.assertEqual(len(d),4)
  self.assertTrue(all(0<x["K_birth_MeV"]<150 for x in d))
 def test_no_plasma_claim(self):
  p=bp.run()
  v=p["physical_claims"];self.assertIsNone(v["heat_rate"]);self.assertIsNone(v["R_event"])
  self.assertFalse(v["L4"]);self.assertEqual(p["dag"]["central"],"28/88");self.assertEqual(p["dag"]["HE_physical"],"14/18")
 def test_source_sha_record(self):
  s=bp.load_sources()
  self.assertEqual(s["pdf_sha256"]["PhysRev.137.B1214.pdf"],"954042ad95c1aab77a84b9a402ccf9dc213403723a93820d4aeebcddaa51d75c")
 def test_drake_energy_exclusion(self):
  s=bp.load_sources()
  self.assertEqual(s["drake"]["classification"],"atomic_eV_two_photon_not_MeV_gamma_nuclear_source")
 def test_geometry_tautology(self):
  # normalized angular event distribution f(mu)=15/4 mu^2(1-mu^2) has E(mu^2)=3/7
  self.assertAlmostEqual(((2/5)-(2/7))/((2/3)-(2/5)),3/7,14)

if __name__=="__main__":unittest.main()
