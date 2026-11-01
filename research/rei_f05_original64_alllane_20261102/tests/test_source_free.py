#!/usr/bin/env python3
"""Source-free proof of published evidence scope, not the protected 46k replay."""
import hashlib,json,sys,tempfile,unittest
from pathlib import Path

P=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P))
from independent_alllane_audit import read_original_state
D=P/"results"
def raw(name):return (D/name).read_bytes()
def doc(name):return json.loads(raw(name))
def sha(name):return hashlib.sha256(raw(name)).hexdigest()
EXPECTED={
"LOCAL_NEUTRAL_HAZARD_PRIMARY":"aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425",
"RECOMBINATION_WEIGHTED_AUDITOR":"b9b1c383a3b697770528481f9cfa35989c61e17609c0100ef27b8c8cda337d9d",
"SCRIPT_SELF_SHIELDING_AUDITOR":"31a763fdca76eb4d0b3fb03276342733dd1618bc2c7df22c3b00ba80691604fa"}

class ScopedResults(unittest.TestCase):
    def test_parent_and_source_scope(self):
        j=doc("ALL_LANE_ORIGINAL64_SCIENCE.json")
        self.assertEqual(j["parent_HEAD"],"abf83d4d883d5f311426b7f02cb001e70138ceb4")
        self.assertEqual(j["original_source_tar_sha256"],"a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b")
        self.assertEqual(j["original_kernel_sha256"],"579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644")
        self.assertEqual(j["source_map_rows_per_lane"],46080)
        self.assertEqual(j["actually_new_native_lanes_recomputed"],2)
        self.assertEqual(j["new_source_map_stage_calls"],6)
        self.assertTrue(j["historical_all_lane_byte_identity"])
        self.assertEqual(j["canonical_DAG"],"28/88")
        self.assertEqual(j["candidate_tick161"],"NOT_ACCEPTED")
        self.assertEqual(j["production"],"HOLD")
    def test_three_original_lane_receipts_and_gates(self):
        j=doc("ALL_LANE_ORIGINAL64_SCIENCE.json")
        by={r["lane"]:r for r in j["lanes"]}
        self.assertEqual(set(by),set(EXPECTED))
        for lane,expect in EXPECTED.items():
            r=by[lane]
            self.assertEqual(r["replayed_state_sha256"],expect)
            self.assertEqual(r["original_state_sha256"],expect)
            self.assertTrue(r["byte_identical"])
            if lane=="LOCAL_NEUTRAL_HAZARD_PRIMARY":
                self.assertEqual(r["classification"],"REUSED_VERIFIED_ORIGINAL64_RUST_OWNER_PR363")
                continue
            self.assertEqual(r["source_rows"],46080)
            self.assertEqual(r["source_map_certification"],[True,True,True])
            self.assertEqual(len(r["ledger_keys"]),14)
            self.assertTrue(r["ledgers_all_include_zero"])
            self.assertEqual(r["table_events"],0)
            self.assertLess(max(r["replay_validated_local_bounds"].values()),2e-4)
            self.assertLess(max(r["replay_widths"].values()),2e-3)
            self.assertEqual(r["max_abs_local_difference"],0.0)
            self.assertEqual(r["max_abs_width_difference"],0.0)
            self.assertEqual(r["definite_ne_decrease"]+r["definite_ne_increase"]+r["uncertain_ne_sign"],46080)
            for key in ("physical_interval_delta_Ne","physical_interval_delta_B_erg","physical_interval_delta_U_erg"):
                lo,hi=r[key];self.assertLess(lo,hi);self.assertLess(hi,0)
    def test_independent_all_lane_readback(self):
        j=doc("INDEPENDENT_ALL_LANE_AUDIT.json")
        self.assertEqual(j["total_new_native_physical_rows_checked"],92160)
        self.assertEqual(j["physically_independent_realizations"],1)
        self.assertTrue(j["original_physical_state_byte_body_equal"])
        self.assertEqual(j["common_physical_body_sha256"],"011f264e01a9634db7766ce15fea136d1416e68c3e5a73725c17cf2bc7d43888")
        self.assertTrue(j["original_physical_source_csv_all_lane_byte_equal"])
        self.assertFalse(j["exact_runtime_contract_recreated"])
        self.assertFalse(j["new_source_owner_tick161_accepted"])
        for lane in j["lanes"]:
            if lane.get("reused_prior_source"):continue
            self.assertEqual(lane["source_rows"],46080)
            self.assertLess(lane["max_cell_relative_error"],1e-12)
    def test_result_content_identity(self):
        self.assertEqual(sha("ALL_LANE_ORIGINAL64_SCIENCE.json"),"155105338cf244fe54df0c67cd54173a8e403b6033afbcffe3aa6126e914fde1")
        self.assertEqual(sha("INDEPENDENT_ALL_LANE_AUDIT.json"),"5dac9faa410087a894e6d35d20815c709827d1d8d46b088338b6ec0688f48006")
    def test_bad_binary_rejected(self):
        with tempfile.TemporaryDirectory(prefix="rei64_bad_") as folder:
            p=Path(folder)/"bad.state";p.write_bytes(b"WRONG_STATE"+b"\0"*200)
            with self.assertRaises(AssertionError):read_original_state(p)
if __name__=="__main__":unittest.main()
