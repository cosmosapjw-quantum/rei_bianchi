#!/usr/bin/env python3
"""Checks claims in source-free published evidence. Not a full hidden-source rerun."""
import copy,csv,hashlib,json,math,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def raw(n):return (P/"results"/n).read_bytes()
def src(n):return json.loads(raw(n))
def sha(n):return hashlib.sha256(raw(n)).hexdigest()
def check_scope(j):
    if j.get("v2_canonical_accepted") is not False:raise AssertionError("FALSE_TICK161_ADMISSION")
    if j.get("central_DAG")!="28/88" or j.get("canonical_delta")!=0:raise AssertionError("FALSE_DAG_ADVANCE")
    if j.get("production")!="HOLD":raise AssertionError("FALSE_PRODUCTION")
    if j.get("original_v1_logT_upper",0)<=2e-4:raise AssertionError("HISTORICAL_V1_FAIL_ERASED")
    if j.get("original_v2_logT_upper",1)>=2e-4:raise AssertionError("V2_SHADOW_PHYSICAL_GATE")
    if j.get("candidate_vs_old_disjoint_physical_source_intervals",1)!=0:raise AssertionError("OLD_V2_SEMANTIC_DISJOINT")
class F05Evidence(unittest.TestCase):
    def test_original_science_source_and_scope(self):
        j=src("PHYSICS_RESULT.json")
        check_scope(j)
        self.assertEqual(j["original_source_tar_sha256"],"a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b")
        self.assertEqual(j["original_source_160_sha256"],"cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01")
        self.assertEqual(j["original_source_kernel_sha256"],"579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644")
        self.assertEqual(j["rec195_HEAD"],"0f1f6dbd33a654a3dd49bc2d9dbe8854b572d235")
        self.assertEqual(j["bass_he150_HEAD"],"f2d26ef196b50e69c1793cc4c29e96a248fe6c0b")
        self.assertEqual(j["accepted_source_material_rows"],184320)
        self.assertEqual(j["real_aligned_new_source_rows"],46080)
        self.assertEqual(j["physical_independent_realizations"],1)
    def test_live_physical_values_not_ode_error(self):
        j=src("PHYSICS_RESULT.json")
        g=j["global_physics"]
        self.assertLess(g["Bdot_net_160_erg_s"],0)
        self.assertLess(g["delta_B_160_161_v2_mid_erg"],0)
        self.assertLess(g["delta_Ne_160_161_v2_mid"],0)
        self.assertLess(g["delta_U_160_161_v2_mid_erg"],0)
        self.assertGreater(g["Bdot_photo_160_erg_s"],0)
        self.assertGreater(g["Bdot_collisional_160_erg_s"],0)
        self.assertLess(g["Bdot_OTS_chemical_160_erg_s"],0)
        self.assertTrue(math.isclose(g["Bdot_net_160_erg_s"],-7.693137946550566e39,rel_tol=1e-12))
        self.assertTrue(math.isclose(g["candidate_160_161_mid_secant_erg_s"],-7.686621502985467e39,rel_tol=1e-12))
        self.assertTrue(math.isclose(g["candidate_vs_source_rate_relative"],-0.0008470462391775291,rel_tol=1e-9))
        self.assertIn("continuous_ode_global_error_bound",j["not_equivalent_to"])
        self.assertEqual(j["new_46k_cell_sign_diagnostic"]["same_sign_v2_deltaB_vs_instant_source"],46050)
        self.assertEqual(j["new_46k_cell_sign_diagnostic"]["different_sign"],30)
    def test_hostile_independent_original_source(self):
        a=src("INDEPENDENT_AUDIT.json")
        self.assertEqual(a["source_cell_rows_checked"],46080)
        self.assertEqual(a["rec_original_rows_checked"],184320)
        self.assertEqual(a["discordant_sign_cells"],30)
        self.assertLess(a["max_relative_26event_stoich_residual"],1e-12)
        self.assertLess(a["max_relative_OTS_energy_identity_residual"],1e-12)
        self.assertLess(a["discordant_source_Bdot_absolute_weight_fraction"],3e-9)
        self.assertEqual(a["central_DAG"],"28/88")
        self.assertFalse(a["v2_official"])
    def test_real_physics_witness_subset(self):
        with (P/"results/ORIGINAL_SOURCE_OTS_24_PHYSICAL_WITNESSES.csv").open(newline="") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),24)
        self.assertEqual([int(x["cell"]) for x in rows],sorted({int(x["cell"]) for x in rows}))
        for r in rows:
            for k in ("B128_mid_erg","B160_mid_erg","B161V2_mid_erg","Ne160_mid","Ne161V2_mid",
                      "U160_mid_erg","U161V2_mid_erg"):
                self.assertGreater(float(r[k]),0)
            self.assertTrue(math.isclose(float(r["Bdot_160_erg_s"]),
              math.fsum([float(r["Bdot_photo_160_erg_s"]),
                         float(r["Bdot_collisional_160_erg_s"]),
                         float(r["Bdot_OTSchemical_160_erg_s"])]),rel_tol=3e-12))
    def test_bytes_and_intentional_negative(self):
        self.assertEqual(sha("PHYSICS_RESULT.json"),"a073b4053e941fdb2a4a3dad2a3e1607af43904d78b460476c100e2f7a0675af")
        self.assertEqual(sha("INDEPENDENT_AUDIT.json"),"3ddab662d020dee650d79454d925d287a0d36aea5bdac8e451213fe33a42ab4d")
        self.assertEqual(sha("ORIGINAL_SOURCE_OTS_24_PHYSICAL_WITNESSES.csv"),"965f59f2bbf6dc889155bf3a4454167e69d30bea17fa7dda64ca4f2c3529805d")
        corrupted=copy.deepcopy(src("PHYSICS_RESULT.json"))
        corrupted["v2_canonical_accepted"]=True
        with self.assertRaisesRegex(AssertionError,"FALSE_TICK161_ADMISSION"):
            check_scope(corrupted)
if __name__=="__main__":unittest.main()
