#!/usr/bin/env python3
"""Immutable source-free evidence: two real V2TX1 research accepted transactions.

These tests do not replay source-private original 26-event computation. A
separate full-source stdlib audit validates 46,080 actual source cell records.
"""
import copy,hashlib,json,unittest
from pathlib import Path

P=Path(__file__).resolve().parents[1]/"results"
SCIENCE="2fc21a98bf8054b4089f8444d2da2862e74863a344114f8dc6fd7c5b86811c5e"
AUDIT="b01bce22f08ead5ae1fd8da4f0c963ee8e905746fa7b6f9b553a1be93074e268"
L=["LOCAL_NEUTRAL_HAZARD_PRIMARY","RECOMBINATION_WEIGHTED_AUDITOR","SCRIPT_SELF_SHIELDING_AUDITOR"]
def sh(f):return hashlib.sha256((P/f).read_bytes()).hexdigest()
def read(f):return json.loads((P/f).read_text())
def source_gate(x):
    if x["research_V2_transaction_accepted_ticks"]!=[161,162]:raise ValueError("INVALID_V2_TWO_STEP_HISTORY")
    if x["original_legacy_V1_terminal_tick"]!=160 or x["distinct_original_canonical_acceptance"]!="HOLD_AT_T160":raise ValueError("FALSE_ORIGINAL_PRODUCTION")
    if x["canonical_DAG"]!="28/88" or x["canonical_delta"]!=0 or x["production"]!="HOLD":raise ValueError("FALSE_CANONICAL_DAG")
    if x["source_actual_t161_npz_SHA256"]!="c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823":raise ValueError("BAD_PARENT_SOURCE_SHA")
    if x["source_actual_t162_npz_SHA256"]!="35b1969ccd2bf16be94e1b9bcc7df9189c647b60c0aa2b00cb479a0d504a0e7b":raise ValueError("BAD_NEXT_SOURCE_SHA")
    if not x["all_14_original_ledgers_per_state"] or not x["source_original_V1_failure_is_preserved"]:raise ValueError("ORIGINAL_PHYSICAL_GATES_FALSE")
class ScientificEvidence(unittest.TestCase):
    def test_durable_science_result_and_original_boundary(self):
        x=read("TRANSACTION_RESULT.json");source_gate(x)
        self.assertEqual(sh("TRANSACTION_RESULT.json"),SCIENCE)
        self.assertEqual(x["source_original_26event_source_SHA256"],"a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b")
        self.assertEqual(x["real_native_source_node_count"],46080)
        self.assertEqual(x["real_native_source_original_maps_consumed_for_this_history"],18)
        self.assertEqual(x["research_V2_accepted_records"],2)
        self.assertTrue(x["single_IGM_realization"])
        self.assertTrue(x["no_automatic_t163"])
    def test_real_2_accepted_transactions_and_lane_state_digest(self):
        x=read("TRANSACTION_RESULT.json")
        self.assertEqual(x["transaction_first_SHA256"],"4fb800c67bd058ea71ce6501888e21a5c9c758ac92c430b2175a5b5c0c376cef")
        self.assertEqual(x["transaction_final_SHA256"],"456ad85673fa9d6cfcc6e545ada33b1d2169166c1c4732a185fc71d9cdf1a8f5")
        self.assertEqual(x["source_t161_full_physical_SHA256"],"fa71a11bf14326e3b2bf2303005917786af1e0e47c39003c07b28708b4e664e5")
        self.assertEqual(x["source_t162_full_physical_SHA256"],"18c4d53ee06ff4e455936062b33e211fa97c09770b80fbdbb6dcd866c79e33d4")
        self.assertEqual(set(x["source_t162_V2TX1_states_sha256"]),set(L))
        self.assertEqual(len(set(x["source_t162_V2TX1_states_sha256"].values())),3)
        self.assertEqual(x["full_private_transaction_control_SHA256"],"b297b3f5205ab0dfd28b9ffac113b5d752ebe26682fe144867b74d78e4bd4716")
    def test_blind_science_full_46k_and_nuclear_source_fix(self):
        a=read("INDEPENDENT_V2TX_HISTORY_AUDIT.json")
        self.assertEqual(sh("INDEPENDENT_V2TX_HISTORY_AUDIT.json"),AUDIT)
        self.assertEqual(a["actual_original_source_cells_checked"],46080)
        self.assertEqual(a["checkpoint_all_6_states_sha_and_job_keys"],"PASS")
        self.assertEqual(a["real_source_46080_HHe_cone_charge_B_U_checked"],"PASS")
        self.assertEqual(a["nuclear_inventory_semantics"],"TRUE_ORIGINAL_SOURCE_NH_NHE_NOT_INTERVAL_LOWER_ENDPOINT")
        self.assertLess(a["max_parent_normalized_summation_order_difference"],1e-14)
        self.assertEqual(a["source_legacy_tick160_original_record_sha256"],"59aed347bdf71fe788e3aee57742a78727971475d4b66ff935e4ca153ec90957")
        self.assertEqual(a["source_original_nuclear_inventory_csv_sha256"],"a27d8b0c4c98b112a42720570a8be77887d1170fb794383d525c7e2f10fa2176")
        self.assertEqual(a["next_source_chemothermal_delta_outer_independent"]["Ne"],[-1.912380653897397e60,-1.206634354240914e60])
        self.assertEqual(a["next_source_chemothermal_delta_outer_independent"]["B"],[-4.740796398061549e49,-2.7469572175665595e49])
        self.assertEqual(a["next_source_chemothermal_delta_outer_independent"]["U"],[-1.0342634990134474e50,4.2357434382538726e49])
    def test_original_fixed_gate_not_reinterpreted(self):
        x=read("TRANSACTION_RESULT.json")
        self.assertEqual(x["original_local_error_limit_unchanged"],0.0002)
        self.assertEqual(x["original_width_limit_unchanged"],0.002)
        self.assertTrue(x["source_original_V1_failure_is_preserved"])
        self.assertEqual(x["new_V2SC1_full_runtime_SHA256"],"97b00826f518aa7a2c258dae15d1e92918b44a04b6f928e2014241bbba2f0075")
        self.assertEqual(x["new_V2SC1_runtime_bound_SHA256"],"ce6cc44af3055b73553cfafd429d979190b80143cf512929e1ec3d78c038e4d7")
    def test_negative_forged_original_accepted_and_wrong_next_state(self):
        x=read("TRANSACTION_RESULT.json")
        fake=copy.deepcopy(x);fake["distinct_original_canonical_acceptance"]="OFFICIAL_ACCEPT"
        with self.assertRaisesRegex(ValueError,"FALSE_ORIGINAL_PRODUCTION"):source_gate(fake)
        fake=copy.deepcopy(x);fake["research_V2_transaction_accepted_ticks"]=[161,163]
        with self.assertRaisesRegex(ValueError,"INVALID_V2_TWO_STEP_HISTORY"):source_gate(fake)
        fake=copy.deepcopy(x);fake["source_actual_t162_npz_SHA256"]="0"*64
        with self.assertRaisesRegex(ValueError,"BAD_NEXT_SOURCE_SHA"):source_gate(fake)
if __name__=="__main__":unittest.main()
