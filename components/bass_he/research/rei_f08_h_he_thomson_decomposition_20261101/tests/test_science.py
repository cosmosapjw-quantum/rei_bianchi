import csv,gzip,importlib.util,json,math,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location("science_he_s0",ROOT/"science.py")
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
class NativeS0HeTests(unittest.TestCase):
 def test_original_source_shas_and_status(self):
  sc=m.verify()
  self.assertEqual(sc["time"]["t_end_s"],1e13)
  self.assertEqual(sc["initial_state"]["fHe"],.083)
 def test_original_two_history_electron_source_match(self):
  sc=m.verify()
  for run in ("BI","FLRW"):
   h,err,rel=m.history(run,sc)
   self.assertEqual(len(h),16001)
   self.assertLessEqual(err,2e-18);self.assertLessEqual(rel,5e-14)
   self.assertEqual(h[0]["time_s"],0.)
   self.assertEqual(h[-1]["time_s"],1e13)
 def test_original_f05_he_ratio_not_reused(self):
  sc=m.verify()
  self.assertNotEqual(sc["initial_state"]["fHe"],0.079)
 def test_photoionization_s0_has_no_direct_helium_photons(self):
  rs=m.csv_rows(m.SRC/"S0_BI-curve.csv.gz")
  self.assertTrue(all(float(r["gamma_HeI_per_s"])==0 and float(r["gamma_HeII_per_s"])==0 for r in rs))
 def test_source_helium_population_physical(self):
  sc=m.verify();a,_,_=m.history("BI",sc)
  self.assertGreater(a[0]["He_electron_fraction"],.1)
  self.assertLess(a[0]["He_electron_fraction"],.2)
  self.assertTrue(all(0<r["He_electron_fraction"]<1 for r in a))
 def test_species_screen_trapezoid_limit(self):
  sc=m.verify();a,_,_=m.history("BI",sc);s=m.Screen(a,"ne_He_proper_cm3")
  self.assertAlmostEqual(s.integral(1e13),0.,delta=1e-20)
  y=math.fsum((s.n[k]+s.n[k+1])*(s.t[k+1]-s.t[k])/2 for k in range(len(s.t)-1))
  self.assertAlmostEqual(s.integral(0),y,delta=abs(y)*1e-13)
 def test_source_clock_guard(self):
  sc=m.verify();a,_,_=m.history("BI",sc);s=m.Screen(a,"ne_H_proper_cm3")
  for t in (-1,1e13+1):
   with self.assertRaises(ValueError):s.eval(t)
 def test_original_ray_species_sum_replays(self):
  sc=m.verify();b,_,_=m.history("BI",sc);f,_,_=m.history("FLRW",sc)
  B={s:m.Screen(b,"ne_"+s+"_proper_cm3") for s in ("H","He")}
  F={s:m.Screen(f,"ne_"+s+"_proper_cm3") for s in ("H","He")}
  rays=m.csv_rows(m.SRC/"ORIGINAL_F08_S0_BIANCHI_THOMSON_SKY.csv.gz")
  for idx in (0,8,128,512,1024,2048,5376,10751):
   q=m.sky_row(rays[idx],B,F,sc["background"]["H_mean_per_s"])
   for lab in ("BI","FLRW"):
    self.assertAlmostEqual(q["tau_"+lab+"_H"]+q["tau_"+lab+"_He"],float(rays[idx]["tau_"+lab]),delta=6e-18)
 def test_all_published_rows_count_checksum_and_physical_range(self):
  j=json.loads((ROOT/"results/RESULT.json").read_text())
  self.assertEqual(j["source_history_rows"],32002)
  self.assertEqual(j["source_sky_rows"],10752)
  self.assertEqual(j["canonical_delta"],0)
  self.assertEqual(j["production"],"HOLD")
  self.assertEqual(m.sha(ROOT/"results/ORIGINAL_F08_S0_H_HE_THOMSON_SKY_10752.csv.gz"),j["species_ray_csv_sha256"])
  self.assertEqual(m.sha(ROOT/"results/ORIGINAL_F08_S0_H_HE_PROPER_ELECTRONS_32002.csv.gz"),j["species_history_csv_sha256"])
  self.assertEqual(len(j["quad_summary"]),12)
  self.assertTrue(all(0<x["He_tau_fraction_of_mean"]<1 for x in j["quad_summary"]))
 def test_invalid_pinned_hash_is_rejected(self):
  orig=m.SHAS["S0_BI-curve.csv.gz"]
  try:
   m.SHAS["S0_BI-curve.csv.gz"]="0"*64
   with self.assertRaises(ValueError):m.verify()
  finally:m.SHAS["S0_BI-curve.csv.gz"]=orig
 def test_wrong_owner_identity_is_rejected(self):
  old=m.SOURCE_PAIR_ID
  try:
   m.SOURCE_PAIR_ID="frozen-wrong-owner"
   with self.assertRaises(ValueError):m.verify()
  finally:m.SOURCE_PAIR_ID=old
 def test_visibility_shared_attenuation(self):
  j=json.loads((ROOT/"results/RESULT.json").read_text())
  p=ROOT/"results/ORIGINAL_F08_S0_H_HE_THOMSON_SKY_10752.csv.gz"
  with gzip.open(p,"rt") as f:
   for r in csv.DictReader(f):
    for part in ("H","He"):
     self.assertGreater(float(r["tau_BI_"+part]),0)
     self.assertGreater(float(r["visibility_BI_"+part]),0)
    self.assertAlmostEqual(float(r["He_tau_BI_fraction"])+float(r["tau_BI_H"])/(float(r["tau_BI_H"])+float(r["tau_BI_He"])),1.,delta=1e-14)
if __name__=="__main__":unittest.main()
