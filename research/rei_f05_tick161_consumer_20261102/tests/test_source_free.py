#!/usr/bin/env python3
"""Source-free reproducible REI F05 scientific owner contract, not full hidden replay."""
import copy,csv,hashlib,json,math,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def raw(n):return (P/"results"/n).read_bytes()
def j(n):return json.loads(raw(n))
def sha(n):return hashlib.sha256(raw(n)).hexdigest()
def gate(a):
    if a.get("official_tick161_accepted") is not False or a.get("official_tick162_accepted") is not False:raise ValueError("FALSE_OFFICIAL_TICK")
    if a.get("central_DAG")!="28/88" or a.get("canonical_delta")!=0:raise ValueError("FALSE_CANONICAL_DAG")
    if a.get("production")!="HOLD":raise ValueError("FALSE_PRODUCTION_STATE")
    if a.get("source_v2_tick161_parent_SHA256")!="c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823":raise ValueError("NONORIGINAL_PARENT")
    if a.get("source_v2_tick162_research_SHA256")!="35b1969ccd2bf16be94e1b9bcc7df9189c647b60c0aa2b00cb479a0d504a0e7b":raise ValueError("WRONG_F05_SOURCE_STATE")
    if max(a["source_versioned_V2_tick161_to162_errors"].values())>=2e-4:raise ValueError("ORIGINAL_F05_LOCAL_GATE")
    if max(a["source_versioned_V2_tick161_to162_widths"].values())>=2e-3:raise ValueError("ORIGINAL_F05_WIDTH_GATE")
    if a["original_14_ledger_includes_zero"]!="3_OF_3_LANES_PASS":raise ValueError("ORIGINAL_LEDGER")
class SourceEvidence(unittest.TestCase):
    def test_rei_original_state_identity_and_canonical_boundary(self):
        a=j("SCIENCE_RESULT.json");gate(a)
        self.assertEqual(a["source_original_F05_tar_SHA256"],"a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b")
        self.assertEqual(a["source_original_26event_kernel_SHA256"],"579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644")
        self.assertTrue(a["source_exact_three_lane_tick161_parent_bytes"])
        self.assertTrue(a["source_exact_three_lane_tick162_next_bytes"])
        self.assertEqual(a["source_original_physics_independent_realizations"],1)
        self.assertEqual(a["actual_original_source_cells"],46080)
        self.assertEqual(a["new_source_native_full_half_maps"],9)
        self.assertEqual(a["source_original_table_events"],0)
    def test_physical_next_tick_and_original_error_gate(self):
        a=j("SCIENCE_RESULT.json")
        self.assertGreater(a["source_old_V1_tick160_to161_logT_fail"],2e-4)
        self.assertLess(a["source_versioned_V2_tick160_to161_logT_upper"],2e-4)
        self.assertLess(a["source_versioned_V2_tick161_to162_errors"]["log_T"],2e-4)
        self.assertLess(a["source_versioned_V2_tick161_to162_widths"]["log_T"],2e-3)
        d=a["source_native_161_to162_physical_delta_outer_intervals"]
        m=a["source_native_161_to162_midpoint_changes"]
        self.assertEqual(set(d),{"Ne","B","U"})
        self.assertEqual(set(m),{"Ne","B","U"})
        for key in d:
            self.assertLessEqual(d[key][0],m[key])
            self.assertGreaterEqual(d[key][1],m[key])
        self.assertLess(m["Ne"],0);self.assertLess(m["B"],0);self.assertLess(m["U"],0)
        self.assertLess(d["B"][1],0)
        self.assertLess(d["U"][0],0);self.assertGreater(d["U"][1],0)
    def test_rust_native_real_46k_and_auditor(self):
        a=j("SCIENCE_RESULT.json");r=j("RUST_INDEPENDENT_AUDIT.json")
        self.assertEqual(a["original_source_electron_thermal_Rust_real_46080"]["rust_46k_cell_electron_interval_misses"],0)
        self.assertEqual(a["original_source_electron_thermal_Rust_real_46080"]["rust_46k_cell_thermal_interval_misses"],0)
        self.assertLess(r["rust_eos_source_full_46080_max_rel"],1e-14)
        self.assertEqual(r["source_rows"],46080)
        self.assertEqual(r["original_14_ledger_zero_inclusion"],"PASS")
        self.assertEqual(sum(r["rust_cell_electron_sign_classes"].values()),46080)
        self.assertEqual(r["source_next_tick162_SHA256"],a["source_v2_tick162_research_SHA256"])
        self.assertFalse(r["tick161_official"]);self.assertFalse(r["tick162_official"])
    def test_actual_source_witnesses(self):
        with (P/"results/REAL_24CELL_T161_T162_RUST_WITNESS.csv").open(newline="") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),24)
        self.assertEqual([int(x["cell"]) for x in rows],sorted(int(x["cell"]) for x in rows))
        for row in rows:
            for key in ["Ne161","Ne162","B161_erg","B162_erg","U161_erg","U162_erg"]:
                self.assertGreater(float(row[key]),0)
            self.assertTrue(math.isfinite(float(row["DeltaB_erg"])))
    def test_source_sha_and_mutated_official_negative(self):
        self.assertEqual(sha("SCIENCE_RESULT.json"),"44458ac677ace87d33a807422e8a4c692ea29563e57e81f88bc05aaad33d4b23")
        self.assertEqual(sha("RUST_INDEPENDENT_AUDIT.json"),"047b3faa26066af0f7acf46370bfc856cfcb54da4116cece3d1684d4c11ebfcb")
        self.assertEqual(sha("RUST_INPUT_LOCK.json"),"339fb83365b058f2dcf7bede6ffa3f2ad24b3a0a3254c3179756d734ffd6ff40")
        self.assertEqual(sha("REAL_24CELL_T161_T162_RUST_WITNESS.csv"),"02a85326d5549cdb40e99f3fdde2959652a501fee59e7b7e8429d43f9a1ad6be")
        bad=copy.deepcopy(j("SCIENCE_RESULT.json"))
        bad["official_tick161_accepted"]=True
        with self.assertRaisesRegex(ValueError,"FALSE_OFFICIAL_TICK"):gate(bad)
        bad=copy.deepcopy(j("SCIENCE_RESULT.json"))
        bad["source_v2_tick162_research_SHA256"]="0"*64
        with self.assertRaisesRegex(ValueError,"WRONG_F05_SOURCE_STATE"):gate(bad)
if __name__=="__main__":unittest.main()
