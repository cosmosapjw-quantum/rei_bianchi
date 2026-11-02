#!/usr/bin/env python3
"""Public source-free structural checks. Not the source-inclusive 9-map physics CI."""
import json,math,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def public_verdict(data):
    if data.get("schema")!="REI_F05_NEW_SOURCE_ONLY_VERSIONED_V2_RESEARCH_WORKER_V1":raise ValueError("SCHEMA")
    if data.get("original_native_map_evaluations")!=9:raise ValueError("NINE_ORIGINAL_MAPS")
    if data.get("official_accepted_161") is not False or data.get("production")!="HOLD":raise ValueError("FORGED_OFFICIAL_ADMISSION")
    if data.get("old_V1_error_gate")!="FAIL_UNCHANGED":raise ValueError("HISTORIC_V1")
    if data.get("DAG",{}).get("central")!="28/88" or data["DAG"].get("canonical_delta")!=0:raise ValueError("DAG")
    rows=data.get("physical_lanes",{})
    if len(rows)!=3:raise ValueError("LANES")
    keys=set();bodies=set()
    for lane,v in rows.items():
        if v["V1_old_logT_upper"]<=0.0002:raise ValueError("FALSE_V1_GATE")
        if v["V2_source_logT_upper"]>=0.0002 or v["V2_public_max_width"]>=0.002:raise ValueError("V2_FIXED_GATES")
        if v["source_native_14_ledgers"]!=14 or v["source_table_events"]!=0 or v["native_full_half_map_count"]!=3:raise ValueError("SOURCE_NATIVE_LEDGER_OR_MAP")
        if v["job_key"] in keys:raise ValueError("SAME_JOB_KEY")
        keys.add(v["job_key"]);bodies.add(v["state_body_sha256"])
        physics=v["physical_response"]
        if physics["delta_Ne"][1]>=0 or physics["delta_B_erg"][1]>=0:raise ValueError("CHEM_AND_ELECTRON_SIGN")
        if not physics["delta_U_gas_erg"][0]<0<physics["delta_U_gas_erg"][1]:raise ValueError("THERMAL_UNCERTAINTY")
    if len(bodies)!=1:raise ValueError("ONE_PHYSICAL_REALIZATION")
    return True
class PublicReadback(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((P/"results/VERSIONED_V2_SOURCE_WORKER_RESULT.json").read_text())
        cls.audit=json.loads((P/"results/INDEPENDENT_SOURCE_V2_WORKER_AUDIT.json").read_text())
    def test_original_source_three_lane_real_physics(self):
        self.assertTrue(public_verdict(self.data))
    def test_independent_source_audit_scoped(self):
        self.assertEqual(self.audit["result"],"PASS_SOURCE_SCOPED_NOT_OFFICIAL")
        self.assertTrue(self.audit["three_lanes_one_physical_body"])
        self.assertTrue(self.audit["three_versioned_distinct_job_keys"])
        self.assertFalse(self.audit["official_tick161"])
        self.assertEqual(self.audit["new_v2_native_map_executions"],9)
    def test_old_v1_failure_must_remain(self):
        tampered=json.loads(json.dumps(self.data))
        tampered["physical_lanes"]["LOCAL_NEUTRAL_HAZARD_PRIMARY"]["V1_old_logT_upper"]=0.0001
        with self.assertRaisesRegex(ValueError,"FALSE_V1_GATE"):public_verdict(tampered)
    def test_forged_official_admission_must_fail(self):
        tampered=json.loads(json.dumps(self.data))
        tampered["official_accepted_161"]=True
        with self.assertRaisesRegex(ValueError,"FORGED_OFFICIAL_ADMISSION"):public_verdict(tampered)
    def test_negative_gas_heat_sign_cannot_be_promoted(self):
        tampered=json.loads(json.dumps(self.data))
        tampered["physical_lanes"]["SCRIPT_SELF_SHIELDING_AUDITOR"]["physical_response"]["delta_U_gas_erg"]=[-8.4e49,-2.4e49]
        with self.assertRaisesRegex(ValueError,"THERMAL_UNCERTAINTY"):public_verdict(tampered)
if __name__=="__main__":unittest.main()
