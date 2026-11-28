"""R53 tests: original REI photon/charge chemistry and source-owner budget."""
import csv,gzip,json,math,tempfile,shutil,unittest
from pathlib import Path
import numpy as np
import r53_photo_chemistry as m
import r53_photon_budget as budget

class TestR53(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.v=m.load()
  cls.out=json.loads((m.ROOT/"results/R53_RESULTS.json").read_text())
  cls.budget=json.loads((m.ROOT/"results/R53_PHOTON_BUDGET.json").read_text())

 def test_original_source_byte_hashes(self):
  z=m.require()
  for name,d in z["original_REI_CX_relevant_source_shas"].items():
   self.assertEqual(m.sha(m.SRC/name),d)

 def test_original_first_tick_proper_clock_and_ion_donors(self):
  self.assertEqual(self.v["count_forcing"],17)
  self.assertAlmostEqual(self.v["dt"],4871848749.16828,delta=.02)
  self.assertTrue(np.all(self.v["nH"]>0))
  self.assertTrue(np.all(self.v["ne0"]>=self.v["nH"]*self.v["x0"]*(1-1e-13)))

 def test_savin_rate_original_10000K_knot(self):
  a,b=m.savin(np.array([10000.]),self.v["knots"],self.v["forward"],self.v["reverse"])
  self.assertAlmostEqual(a[0],8.04e-9,delta=3e-22)
  self.assertAlmostEqual(b[0],8.07e-9,delta=3e-22)

 def test_source_H_recombination_B_and_A(self):
  x=np.array([3000.,1e4,5e4])
  A=m.case_alpha(x,"A");B=m.case_alpha(x,"B")
  self.assertTrue(np.all(A>=B))
  self.assertTrue(np.all(B>0))

 def test_case_invalid_fail_closed(self):
  with self.assertRaises(ValueError):m.case_alpha(np.array([10000.]),"C")
  with self.assertRaises(ValueError):m.case_alpha(np.array([-1.]),"B")
  with self.assertRaises(ValueError):m.savin(np.array([200001.]),self.v["knots"],self.v["forward"],self.v["reverse"])

 def test_synthetic_zero_time_does_nothing(self):
  ids=np.arange(3);v=self._small(ids)
  v["dt"]=0.
  y0=np.array([0.,.2,1.])
  r=m.integrate(v,y0,steps=4)
  self.assertTrue(np.array_equal(r["y"],y0))
  self.assertEqual(float(r["photo"].sum()),0.)
  self.assertEqual(float(r["recomb"].sum()),0.)

 def _small(self,idx):
  v=self.v
  d={k:(x[idx].copy() if isinstance(x,np.ndarray) and x.shape==(m.N,) else x)
     for k,x in v.items()}
  return d

 def test_photo_only_constant_analytic(self):
  idx=np.arange(3);v=self._small(idx)
  from scipy.interpolate import PchipInterpolator
  # source-controlled gamma replaced by mathematical positive constant test gamma
  v["gamma"]=lambda t:2e-13
  y0=np.array([0.,.3,.8])
  r=m.integrate(v,y0,steps=32,cx_scale=0,rr_scale=0)
  expected=1-(1-y0)*np.exp(-2e-13*v["dt"])
  self.assertLess(np.max(abs(r["y"]-expected)),2e-14)
  self.assertLess(np.max(abs(r["photo"]-(r["y"]-y0))),2e-14)
  self.assertLess(np.max(abs(r["cx"])),1e-18)

 def test_cx_only_global_recovers_R52(self):
  v=self.v
  z=m.integrate(v,np.zeros(m.N),gamma_scale=0,rr_scale=0,steps=64)
  self.assertLess(float(np.max(np.abs(z["y"]-v["baseR52neutral"]))),3e-12)

 def test_recomb_only_constant_analytic(self):
  ids=np.arange(3);v=self._small(ids)
  # x,T and ne constant to enable exact exponential
  v["x1"]=v["x0"].copy()
  v["T1"]=v["T0"].copy()
  v["ne1"]=v["ne0"].copy()
  v["gamma"]=lambda t:0.
  y0=np.array([.9,.4,.1])
  r=m.integrate(v,y0,case="B",steps=64,gamma_scale=0.,cx_scale=0.,eta=0.)
  expected=y0*np.exp(-m.case_alpha(v["T0"],"B")*v["ne0"]*v["dt"])
  self.assertLess(float(np.max(abs(r["y"]-expected))),2e-14)

 def test_charge_and_photo_recomb_partition(self):
  y0=np.zeros(m.N)
  r=m.integrate(self.v,y0,case="B",steps=64)
  self.assertLess(float(np.max(abs(r["y"]-r["cx"]-r["photo"]+r["recomb"]))),1e-12)
  self.assertLess(float(np.max(abs(self.v["x1"]-m.ETA*r["cx"]+m.ETA*r["y"]-self.v["x1"]-m.ETA*(r["photo"]-r["recomb"])))),4e-15)

 def test_full_46080_source_data_and_counts(self):
  count=0
  with gzip.open(m.ROOT/"results"/m.FNAME,"rt") as f:
   src=csv.DictReader(f)
   self.assertEqual(src.fieldnames,m.KEYS)
   for r in src:
    self.assertEqual(int(r["node"]),count);count+=1
    y=float(r["caseB_photo_y_final_neutral"])
    self.assertTrue(0<=y<=1)
    self.assertGreaterEqual(float(r["caseB_D_photoionizations_per_D_neutral"]),0)
    self.assertGreaterEqual(float(r["caseB_D_recombinations_per_D_neutral"]),0)
    self.assertAlmostEqual(float(r["caseB_D_radio_net_ion_per_D_neutral"]),
     float(r["caseB_D_photoionizations_per_D_neutral"])-float(r["caseB_D_recombinations_per_D_neutral"]),delta=1e-14)
  self.assertEqual(count,m.N)

 def test_full_owner_photon_budget_source_cells(self):
  count=0
  with gzip.open(m.ROOT/"results/R53_OWNER_PHOTON_BUDGET_46080.csv.gz","rt") as f:
   c=csv.DictReader(f)
   self.assertEqual(c.fieldnames,budget.COLS)
   for r in c:
    self.assertEqual(int(r["node"]),count);count+=1
    self.assertGreater(float(r["cloned_original_HI_photo_ionizations_per_cell"]),0)
    self.assertEqual(r["DI_photo_ratio_local_G1_relative_not_defined"],"NOT_DEFINED_NO_CELL_G1_OWNER")
  self.assertEqual(count,m.N)

 def test_photon_budget_materiality_is_not_conservation_certificate(self):
  b=self.budget
  self.assertTrue(b["new_source_sink_gt1percent_original_emission"])
  self.assertGreater(b["photon_demand_ratios"]["DI_neutral_over_source_emission"],.04)
  self.assertLess(b["photon_demand_ratios"]["DI_neutral_over_source_emission"],.06)
  self.assertTrue(b["not_a_proved_violation_of_photon_budget"])
  self.assertEqual(b["photons_debited_from_native_REI_owner"],"NO")

 def test_recomb_caseB_and_caseA_donor_closure_inequality(self):
  with gzip.open(m.ROOT/"results"/m.FNAME,"rt") as f:
   for r in csv.DictReader(f):
    self.assertGreaterEqual(float(r["caseB_photo_y_final_neutral"])+1e-12,float(r["caseA_photo_y_final_neutral"]))

 def test_closed_source_identity_and_no_central_promotion(self):
  r=self.out
  self.assertLess(r["numerical"]["no_radiation_R52_CX_only_max_abs_y_regression"],3e-12)
  self.assertEqual(r["DAG"]["WU"],"34/49")
  self.assertEqual(r["DAG"]["REI_central"],"28/88")
  self.assertEqual(r["original_admission"],"NOT_GRANTED")
  self.assertEqual(r["assumptions"]["D_gas_heating_from_photon_energy"],"NOT_COMPUTED")

 def test_negative_source_hash_tamper(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"source.csv"
   shutil.copyfile(m.SRC/"SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv",p)
   p.write_bytes(p.read_bytes()+b" ")
   self.assertNotEqual(m.sha(p),m.require()["original_REI_CX_relevant_source_shas"]["SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv"])

if __name__=="__main__":unittest.main()
