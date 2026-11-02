#!/usr/bin/env python3
"""Inspectable source-free original F05 V2 admission claim, no private worker rerun."""
import copy,hashlib,json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"results"
def blob(x):return (P/x).read_bytes()
def data(x):return json.loads(blob(x))
def h(x):return hashlib.sha256(blob(x)).hexdigest()
SOURCE="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
CANDIDATE="c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823"
NEXT="35b1969ccd2bf16be94e1b9bcc7df9189c647b60c0aa2b00cb479a0d504a0e7b"
def reject_official(j):
 if j["official_tick161"] is not False:raise ValueError("FALSE_V1_OFFICIAL_TICK161")
 if j["production"]!="HOLD" or j["canonical_delta"]!=0 or j["canonical_REI_DAG"]!="28/88":raise ValueError("FALSE_CANONICAL_PROGRESS")
 if j["v2_new_runtime_full_sha256"]==j["old_historical_v1_runtime_sha256"]:raise ValueError("FALSE_RUNTIME_BYTE_IDENTITY")
 if j["source_V2_tick161_real_NPZ_SHA256"]!=CANDIDATE or j["source_V2_tick162_next_NPZ_SHA256"]!=NEXT:raise ValueError("FALSE_SOURCE_STATE")
class OwnerSevenPin(unittest.TestCase):
 def test_exact_complete_runtime_contract(self):
  j=data("SEVEN_PIN_V2_OWNER_SCIENCE.json")
  b=data("VERSIONED_V2_FULL_RUNTIME_RESULT.json")
  full=b["runtime"]["complete_original_seven_pin_runtime"]
  self.assertTrue(j["all_seven_original_dependency_pins_matched"])
  self.assertEqual(set(full["new_full_runtime_contract"]["dependencies"]),set(("numpy","scipy","pandas","python-dateutil","pytz","tzdata","six")))
  self.assertEqual(full["original_runtime_changed_fields"],["git_head","numeric_fingerprint.numpy_runtime_sha256"])
  self.assertEqual(j["historical_runtime_difference"],full["original_runtime_changed_fields"])
  self.assertEqual(j["old_historical_v1_runtime_sha256"],"10ab5823e109f32d693c82d246b3369045ddecf5217fa30fc4013ab6d55c3810")
  reject_official(j)
 def test_original_three_lanes_unmodified_gates(self):
  j=data("SEVEN_PIN_V2_OWNER_SCIENCE.json")
  r=data("VERSIONED_V2_FULL_RUNTIME_RESULT.json")
  self.assertEqual(j["source_original_F05_TAR_SHA256"],SOURCE)
  self.assertEqual(r["original_native_map_evaluations"],9)
  self.assertEqual(len(r["physical_lanes"]),3)
  self.assertTrue(j["three_lane_original_V2SC1_body_byte_identical"])
  self.assertTrue(j["three_lane_distinct_job_keys"])
  self.assertEqual(j["three_lane_original_V2SC1_body_SHA256"],"fa71a11bf14326e3b2bf2303005917786af1e0e47c39003c07b28708b4e664e5")
  self.assertEqual(j["source_original_14_ledger_each_lane"],"3/3_PASS")
  self.assertGreater(j["source_V1_160_161_logT_failed_upper"],2e-4)
  self.assertLess(j["source_V2_160_161_logT_upper"],2e-4)
  self.assertEqual(j["source_original_local_gate"],2e-4)
  self.assertEqual(j["source_original_width_gate"],2e-3)
 def test_true_causal_next_map_source_and_physics(self):
  j=data("SEVEN_PIN_V2_OWNER_SCIENCE.json")
  self.assertEqual(j["source_V2_tick161_real_NPZ_SHA256"],CANDIDATE)
  self.assertEqual(j["source_V2_tick162_next_NPZ_SHA256"],NEXT)
  self.assertEqual(j["source_original_native_full_half_maps_t160_t161"],9)
  self.assertEqual(j["original_native_full_half_maps_t161_t162"],3)
  self.assertEqual(j["source_original_next_14_ledger"],"PASS")
  self.assertEqual(j["source_original_table_events"],0)
  self.assertLess(j["source_V2_161_162_logT_upper"],2e-4)
  self.assertLess(j["next_source_material_delta_midpoint"]["B"],0)
  self.assertLess(j["next_source_material_delta_midpoint"]["Ne"],0)
  self.assertLess(j["next_source_material_delta_outer"]["U"][0],0)
  self.assertGreater(j["next_source_material_delta_outer"]["U"][1],0)
 def test_source_disjoint_auditor_and_public_exact_identities(self):
  a=data("INDEPENDENT_FULL_RUNTIME_AUDIT.json")
  self.assertEqual(a["result"],"PASS_SOURCE_SCOPED_NOT_OFFICIAL")
  self.assertEqual(a["cells_per_lane"],46080)
  self.assertEqual(a["new_v2_native_map_executions"],9)
  self.assertTrue(a["three_lanes_one_physical_body"])
  self.assertTrue(a["three_versioned_distinct_job_keys"])
  self.assertEqual(h("VERSIONED_V2_FULL_RUNTIME_RESULT.json"),"908bf78993836b536e219ef8bd69837bde4bdec06ac6583ab799ab1a557504ae")
  self.assertEqual(h("INDEPENDENT_FULL_RUNTIME_AUDIT.json"),"304e8e0e28871fdbd92d090fc0004fbce0f8903c1ebddb385f290d1eb83876fa")
  self.assertEqual(h("SEVEN_PIN_V2_OWNER_SCIENCE.json"),"30ff550d15a3acb0a57906e3e21a284286092c6d8291fcaa9d04c7f6898edb32")
 def test_adversarial_wrong_official_admission_and_state_reject(self):
  old=data("SEVEN_PIN_V2_OWNER_SCIENCE.json")
  forged=copy.deepcopy(old);forged["official_tick161"]=True
  with self.assertRaisesRegex(ValueError,"FALSE_V1_OFFICIAL"):reject_official(forged)
  forged=copy.deepcopy(old);forged["source_V2_tick162_next_NPZ_SHA256"]="0"*64
  with self.assertRaisesRegex(ValueError,"FALSE_SOURCE_STATE"):reject_official(forged)
if __name__=="__main__":unittest.main()
