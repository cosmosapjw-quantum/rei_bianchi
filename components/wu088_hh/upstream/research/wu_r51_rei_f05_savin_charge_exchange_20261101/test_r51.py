#!/usr/bin/env python3
"""Targeted R51 Savin REI original science and adversarial regression tests."""
import csv, gzip, hashlib, json, math, shutil, tempfile, unittest
from pathlib import Path
import r51_savin_f05 as m

R=m.ROOT
RESULT=json.loads((R/"results/R51_RESULTS.json").read_text())
SOURCE_TABLE,SOURCE_FITS=m.require_sources()

class TestR51SourcePhysics(unittest.TestCase):
 def test_frozen_original_inputs_and_source_knots(self):
  self.assertEqual(len(SOURCE_TABLE),47)
  for name,want in m.SHA.items():
   self.assertEqual(m.sha(m.SOURCES/name),want)
  self.assertEqual(SOURCE_TABLE[0][0],1)
  self.assertEqual(SOURCE_TABLE[-1][0],200000)

 def test_published_table_knots_exact_interpolation(self):
  for T,kf,kb in SOURCE_TABLE[1:]:
   if T>=2.7:
    self.assertAlmostEqual(m.interp_published(SOURCE_TABLE,T,1),kf,delta=4e-15*kf)
    self.assertAlmostEqual(m.interp_published(SOURCE_TABLE,T,2),kb,delta=4e-15*kb)

 def test_intermediate_source_rates_positive(self):
  for T in [3,5,25,345,2500,5555,10000,36789,150000,200000]:
   self.assertGreater(m.interp_published(SOURCE_TABLE,T,1),0)
   self.assertGreater(m.interp_published(SOURCE_TABLE,T,2),0)

 def test_frozen_domain_rejection(self):
  for T in [0,2.69,200000.001,float("nan"),float("inf")]:
   for fn in (lambda t:m.interp_published(SOURCE_TABLE,t,1),
              lambda t:m.alpha_fit(SOURCE_FITS["forward_a1"],t)):
    with self.subTest(T=T):
     with self.assertRaises(ValueError):fn(T)

 def test_original_fit_disagreement_sign(self):
  T=10000.
  source0=m.interp_published(SOURCE_TABLE,T,1)
  source1=m.interp_published(SOURCE_TABLE,T,2)
  fit0=m.alpha_fit(SOURCE_FITS["forward_a1"],T)
  fit1=m.alpha_fit(SOURCE_FITS["reverse_a2"],T)
  self.assertAlmostEqual(source0,8.04e-9,delta=8.04e-9*3e-15)
  self.assertAlmostEqual(source1,8.07e-9,delta=8.07e-9*3e-15)
  self.assertLess(source0,source1)
  self.assertGreater(fit0,fit1)
  self.assertLess(abs(fit0/source0-1),SOURCE_FITS["source_reported_fit_accuracy_relative_upper"]["forward"])
  self.assertLess(abs(fit1/source1-1),SOURCE_FITS["source_reported_fit_accuracy_relative_upper"]["reverse"])

 def test_stationary_balance(self):
  for x in [1e-4,0.25,0.9,0.993,0.99997]:
   a,b=m.exposure_coeff(7.7e-9,7.8e-9,x)
   y,f,r,lam=m.stationary(7.7e-9,7.8e-9,x)
   self.assertAlmostEqual(y+f,1,delta=1e-14)
   self.assertAlmostEqual(a*(1-y)-b*y,0,delta=1e-22)
   self.assertAlmostEqual(f/(1-x),r,delta=2e-11)
   self.assertEqual(lam,a+b)

 def test_exact_H_D_electron_charge_conservation(self):
  for x in [0.10,0.5,0.993,0.99997,0.999997]:
   for y0 in [0,0.2,0.8,1]:
    yd,xh=m.charge_conserving_eq(7.7e-9,7.8e-9,x,m.ETA_D,y0)
    self.assertGreaterEqual(yd,0)
    self.assertLessEqual(yd,1)
    self.assertGreaterEqual(xh,0)
    self.assertLessEqual(xh,1)
    self.assertAlmostEqual(xh+m.ETA_D*yd,x+m.ETA_D*y0,delta=3e-16)
    self.assertAlmostEqual(7.7e-9*(1-yd)*xh-7.8e-9*yd*(1-xh),0,delta=1e-21)

 def test_reverse_endothermicity_energy_sign(self):
  en=m.ETA_D*m.DELTA_E_ERG
  self.assertGreater(en,0)
  self.assertEqual(m.energy_per_H_from_CX(0,1),-en)
  self.assertEqual(m.energy_per_H_from_CX(1,0),en)
  self.assertEqual(m.energy_per_H_from_CX(.5,.5),0)

 def test_source_generator_per_density_and_no_clock(self):
  x=.99;kf=1e-8;kb=1e-8
  a,b=m.exposure_coeff(kf,kb,x)
  self.assertAlmostEqual(a,kf*x)
  self.assertAlmostEqual(b,kb*(1-x))
  self.assertEqual(m.stationary(kf,kb,x)[3],kf*x+kb*(1-x))
  self.assertTrue(RESULT["modeled_CX_scope"]["NO_PROPER_NH_DENSITY_OR_PRETENDED_TIME_INTEGRATION"])

 def test_immutability_negative_path(self):
  with tempfile.TemporaryDirectory() as z:
   target=Path(z)/"copy"
   shutil.copy2(m.SOURCES/"SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv",target)
   target.write_bytes(target.read_bytes()+b"\n")
   self.assertNotEqual(m.sha(target),m.SHA["SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv"])

 def test_original_46080_rows_physical_cone_and_data_binding(self):
  full=R/"results/R51_REI_F05_SAVIN_H_D_CX_46080.csv.gz"
  n=0
  with gzip.open(full,"rt",newline="") as f:
   reader=csv.DictReader(f)
   self.assertEqual(reader.fieldnames,m.FIELDS)
   for row in reader:
    self.assertEqual(int(row["node"]),n)
    n+=1
    x=float(row["original_xHII160"])
    y=float(row["CX_equilibrium_Dplus160"])
    ratio=float(row["CX_Dneutral_over_Hneutral160"])
    energy=float(row["CX_absolute_energy_ceiling_erg_per_H"])
    self.assertLess(0,x)
    self.assertLess(x,1)
    self.assertLessEqual(0,y)
    self.assertLessEqual(y,1)
    self.assertGreaterEqual(ratio,1-2e-15)
    self.assertAlmostEqual(energy,m.ETA_D*m.DELTA_E_ERG,delta=1e-32)
    self.assertLessEqual(abs(float(row["CX_heat_initial_Dneutral_160_erg_per_H"])),energy*(1+1e-12))
    self.assertLessEqual(abs(float(row["CX_heat_initial_Dplus_160_erg_per_H"])),energy*(1+1e-12))
    self.assertLessEqual(abs(float(row["CX_charge_conservation_residual_initial_Dneutral"])),4e-16)
    self.assertLessEqual(abs(float(row["CX_charge_conservation_residual_initial_Dplus"])),4e-16)
  self.assertEqual(n,m.NODES)
  self.assertEqual(RESULT["number_original_source_cells"],m.NODES)

 def test_original_REI_admission_not_promoted(self):
  self.assertEqual(RESULT["physical_source_state"]["tick160"],"OFFICIAL_ACCEPTED")
  self.assertEqual(RESULT["physical_source_state"]["tick161"],"UNAPPROVED_PREVIEW_ONLY")
  self.assertEqual(RESULT["DAG"]["WU"],"34/49")
  self.assertEqual(RESULT["DAG"]["REI_central"],"28/88")
  self.assertEqual(RESULT["DAG"]["new_canonical_nodes"],0)
  self.assertTrue(RESULT["claim_gate"]["NO_RATE_TIMES_COUNT_AS_DENSITY"])

 def test_actual_Savin_source_fit_artifact_vs_table(self):
  self.assertEqual(RESULT["counters"]["table_direction_order_conflicts"],0)
  self.assertGreater(RESULT["counters"]["fit_direction_order_conflicts"],0)
  self.assertEqual(RESULT["counters"]["source_table_T_in_range"],46080)

 def test_output_sha256(self):
  self.assertEqual(m.sha(R/"results"/RESULT["files"]["full_physical_csv"]),
                   RESULT["files"]["full_sha256"])

if __name__=="__main__":
 unittest.main()
