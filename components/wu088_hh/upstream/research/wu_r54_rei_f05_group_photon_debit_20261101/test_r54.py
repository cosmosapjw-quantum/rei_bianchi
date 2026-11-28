"""R54 original source 4-group DI photon-conserving perturbation scientific tests."""
from __future__ import annotations
import csv,gzip,hashlib,json,math,tempfile,shutil,unittest
from pathlib import Path
import numpy as np
import r54_group_photon_perturbation as m

class TestR54(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.v=m.load()
  cls.r=json.loads((m.ROOT/"results/R54_RESULTS.json").read_text())
  cls.n=cls.r["numeric"]
  with (m.ROOT/"results/R54_REI_F05_DI_PHOTON_GROUPS_4.csv").open() as f:
   cls.groups=list(csv.DictReader(f))
 def test_native_source_12_input_sha256(self):
  z=json.loads((m.ROOT/"SOURCE_CONTRACT.json").read_text())
  for k,h in z["source_sha256"].items():
   self.assertEqual(m.sha(m.INPUT/k),h,k)
  self.assertEqual(len(z["source_sha256"]),12)
 def test_original_source_four_group_edges_and_three_active(self):
  self.assertEqual(tuple(m.GROUPS),("G1","G2a","G2b","G3"))
  self.assertEqual(m.BOUNDS[0],(13.60,24.59))
  self.assertEqual(m.BOUNDS[-1],(54.42,100.))
  self.assertEqual(float(m.ETA_D),2.5e-5)
  self.assertEqual(float(m.CHI_D_PHYS_EV),13.6017)
  self.assertEqual(len(self.groups),4)
  self.assertEqual(float(self.groups[-1]["initial_neutral_DI_photo_event_count"]),0.)
 def test_all_native_17_knots_gamma_source_reconstruction(self):
  v=self.v
  pred=np.asarray(v["source_N"](v["times"]))@v["sigma"]*v["pref"]
  src=v["source_Gamma_samples"]
  self.assertLess(float(np.max(abs(pred-src)/src)),5e-12)
  self.assertEqual(self.n["parent_original_Gamma_HI_rebuilt_max_rel_at_17_native_nodes"],0.)
 def test_model_source_g3_zero_and_energy_means(self):
  v=self.v
  self.assertTrue(np.all(np.asarray(v["source_N"](v["times"]))[:,3]==0))
  self.assertTrue(np.all(np.asarray(v["source_A"](v["times"]))[:,3]==0))
  self.assertTrue(np.all(v["meanE"][:3]>m.CHI_D_PHYS_EV))
  self.assertTrue(np.all(v["sigma"][:3]>0))
 def test_original_h_nuclei_46080_and_volume_real(self):
  self.assertEqual(len(self.v["NH"]),m.N)
  self.assertTrue(np.all(self.v["nH"]>0))
  self.assertTrue(np.allclose(self.v["NH"],self.v["nH"]*self.v["V"],rtol=1e-14,atol=0))
  self.assertAlmostEqual(self.v["W"].sum(),1.,delta=2e-14)
  self.assertAlmostEqual(self.v["dt"],4871848749.16828,delta=.01)
 def test_original_WU_R53_zero_feedback_source_regression(self):
  self.assertLess(self.n["R53_zero_DI_feedback_max_abs_y_initial_neutral"],5e-12)
  self.assertLess(self.n["gamma_PCHIP_vs_group_PCHIP_max_rel_between160_161"],5e-7)
 def test_all_four_native_photon_group_budget_identity(self):
  for g in self.groups:
   pg=float(g["initial_neutral_DI_photo_event_count"])
   deficit=float(g["initial_neutral_DI_photon_reservoir_depletion"])
   displacement=float(g["initial_neutral_native_absorption_displaced"])
   self.assertGreaterEqual(pg,0)
   self.assertGreaterEqual(deficit,0)
   self.assertGreaterEqual(displacement,0)
   self.assertAlmostEqual(pg,deficit+displacement,delta=2e-13*max(pg,1))
   source=float(g["original_source_Nphotons_final"])
   if source:self.assertLess(deficit/source,1e-5)
 def test_true_group_photo_total_matches_source_46k(self):
  source=np.zeros(4)
  with gzip.open(m.ROOT/"results"/m.FILENAME,"rt") as f:
   for r in csv.DictReader(f):
    NH=float(r["original_H_N"])
    for i,g in enumerate(m.GROUPS):
     source[i]+=m.ETA_D*NH*float(r["DI_neutral_photon_"+g+"_per_D"])
  for i,g in enumerate(self.groups):
   val=float(g["initial_neutral_DI_photo_event_count"])
   self.assertAlmostEqual(source[i],val,delta=1e-12*max(val,1))
 def test_main_full_physical_data_46080_rows_and_charge_energy(self):
  p=m.ROOT/"results"/m.FILENAME
  n=0
  with gzip.open(p,"rt") as f:
   r=csv.DictReader(f)
   self.assertEqual(r.fieldnames,m.COLS)
   for x in r:
    self.assertEqual(int(x["node"]),n)
    n+=1
    self.assertGreater(float(x["proper_nH_cm3"]),0)
    self.assertGreaterEqual(float(x["DI_initial_neutral_y_final_group_coupled"]),0)
    self.assertLessEqual(float(x["DI_initial_neutral_y_final_group_coupled"]),1)
    self.assertLessEqual(float(x["DI_initial_neutral_delta_y_from_photon_debit"]),1e-13)
    self.assertLessEqual(abs(float(x["DI_neutral_photon_energy_bookkeeping_residual_erg_per_H"])),1e-27)
    self.assertLessEqual(abs(float(x["DI_neutral_charge_total_electron_residual_per_H"])),1e-13)
    self.assertGreaterEqual(float(x["DI_neutral_photoelectron_gross_heat_erg_per_H"]),0)
    self.assertGreaterEqual(float(x["DI_neutral_photo_latent_energy_erg_per_H"]),0)
    self.assertEqual(float(x["DI_neutral_photon_G3_per_D"]),0.)
  self.assertEqual(n,m.N)
 def test_group_256_native_depletion_trajectory(self):
  path=m.ROOT/"results/R54_GROUP_PHOTON_DEPLETION_TRAJECTORY_256.csv"
  with path.open() as f:
   rows=list(csv.DictReader(f))
  self.assertEqual(len(rows),64*4)
  self.assertEqual(sorted(set(x["group"] for x in rows)),list(m.GROUPS))
  for row in rows:
   self.assertGreaterEqual(float(row["DI_photon_deficit"]),0)
   self.assertGreaterEqual(float(row["neutral_D_nuclei_count_per_cMpc3"]),0)
   self.assertGreaterEqual(float(row["original_source_N"]),0)
  self.assertAlmostEqual(float(rows[-1]["normalized_time"]),1.,delta=2e-15)
 def test_sigma_D_shifted_threshold_diagnostic_is_distinct(self):
  sig=np.asarray(self.v["sigma"])
  alt=np.asarray(self.v["alt_sigma"])
  self.assertTrue(np.all(alt>0))
  self.assertLess(float(np.max(abs(alt/sig-1))),.01)
 def test_photo_chemistry_is_not_general_cosmic_claim(self):
  self.assertEqual(self.r["science_status"],"SOURCE_CONDITIONAL_REAL_46K_CELL_PHOTON_GROUP_CONSERVING_PERTURBATION_NOT_NATIVE_RT_OWNER")
  self.assertEqual(self.r["physical_conventions"]["full_coupled_Einstein_Boltzmann_four_group_RT"],"NOT_RUN")
  self.assertEqual(self.r["physical_conventions"]["true_photoheating_net_after_native_reassignment"],"NOT_COMPUTED")
  self.assertEqual(self.r["policy"]["canonical_delta"],0)
  self.assertEqual(self.r["policy"]["WU"],"34/49")
  self.assertEqual(self.r["policy"]["REI_central"],"28/88")
 def test_source_group_RK32_vs_RK64_and_max_delta_y(self):
  self.assertLess(self.n["RK32_vs64_max_abs_y_initial_neutral"],2e-7)
  self.assertLess(self.n["max_global_group_photon_conservation_residual_rel"],3e-13)
  self.assertLess(self.n["max_source_photon_depletion_fraction"],3e-6)
 def test_original_photon_energy_split_dimension_and_sum(self):
  self.assertLess(self.n["max_gas_photo_energy_partition_residual_erg_per_H"],1e-27)
  self.assertGreater(self.n["DI_source_photon_mean_energy_eV"],m.CHI_D_PHYS_EV)
  self.assertGreater(self.n["conditional_DI_photo_excess_heat_over_abs_F05_deltaU"]["median"],0.)
 def test_negative_mutated_source_not_bit_identical(self):
  key="canonical_time_resolved_forcing_nodes.csv"
  want=json.loads((m.ROOT/"SOURCE_CONTRACT.json").read_text())["source_sha256"][key]
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/key
   shutil.copy2(m.INPUT/key,p)
   p.write_bytes(p.read_bytes()+b"\n")
   self.assertNotEqual(m.sha(p),want)
 def test_reproducible_primary_SCIENCE_SHA(self):
  self.assertEqual(m.sha(m.ROOT/"results"/m.FILENAME),
                   self.r["files"]["full_csv_sha256"])

if __name__=="__main__":unittest.main()
