"""R49 focused formula, provenance and generated-evidence regression tests."""
import csv,hashlib,json,math,pathlib,unittest
import r49_materiality as m
ROOT=pathlib.Path(__file__).resolve().parent
R=json.loads((ROOT/"results/R49_RESULTS.json").read_text())
class TestR49(unittest.TestCase):
 def test_fiducial_formula(self):
  self.assertAlmostEqual(m.need(2e-19),8e-17,places=28)
 def test_smaller_HD_fraction_harder(self):
  self.assertAlmostEqual(m.need(2e-19,fmax=1e-6)/m.need(2e-19),25)
 def test_invalid_closure(self):
  for f,e in [(0,.01),(-1,.01),(.5,0),(.5,1.1)]:
   with self.subTest(f=f,e=e),self.assertRaises(ValueError):m.need(1.,frac=e,fmax=f)
 def test_quantiles(self):
  q=m.quant([4.,1.,2.,3.])
  self.assertEqual((q["min"],q["median"],q["max"]),(1.,2.5,4.))
 def test_rei_energy_ledger(self):
  x=R["experiment"]
  self.assertEqual(x["n"],46080)
  self.assertEqual(x["center_T_joint_native_window_n"],5616)
  self.assertLess(x["max_relative_photo_split_residual"],1e-12)
  self.assertLess(x["max_relative_native_rhs_residual"],1e-12)
  self.assertEqual(x["negative_thermal_gain"],46080)
 def test_provenance_mismatch_persisted(self):
  x=R["experiment"]
  self.assertEqual(len(x["WU_R48_five_witnesses"]),5)
  self.assertEqual(len({z["node"] for z in x["WU_R48_five_witnesses"]}),3)
  self.assertEqual(x["WU_REI_cross_archive_mismatch_count"],1)
  self.assertGreater(x["WU_REI_cross_archive_max_T_relative_difference"],1e-11)
  self.assertEqual(R["source"]["full_source_byte_or_numerical_equivalence"].split(";")[0],"NOT_ESTABLISHED")
 def test_data_rows_and_energy_identity(self):
  p=ROOT/"results/R49_REI_F05_HD_MATERIALITY_46080.csv"
  with p.open(newline="") as f:
   r=csv.DictReader(f);n=0
   for z in r:
    self.assertAlmostEqual(float(z["HD_1pct_required_erg_per_HD_DHfid"]),
      .01*abs(float(z["thermal_energy_gain_erg_per_H"]))/m.D_FID,
      delta=1e-12*float(z["HD_1pct_required_erg_per_HD_DHfid"]))
    n+=1
  self.assertEqual(n,46080)
 def test_dag_unchanged(self):
  self.assertEqual(R["admitted"],dict(WU="34/49",REI_central="28/88",REI_working="33/88",delta=0))
  self.assertFalse(R["governance"]["AUTO_NEXT_NODE"])
if __name__=="__main__":unittest.main()
