"""F05 V2: bounded owner-scientific gate negative and positive controls."""
from __future__ import annotations
import importlib.util, pathlib, unittest
R=pathlib.Path(__file__).resolve().parents[1]
p=R/"owner_v2_shadow.py"
sp=importlib.util.spec_from_file_location("rei_f05_v2_scoped_test",p)
m=importlib.util.module_from_spec(sp)
sp.loader.exec_module(m)
KEYS=("H_nuclei","He_nuclei","stage_photon_identity","stage_total_energy",
      "stage_group_0_photon","stage_group_1_photon",
      "stage_group_2_photon","stage_group_3_photon",
      "final_photon_identity","final_total_energy",
      "final_group_0_photon","final_group_1_photon",
      "final_group_2_photon","final_group_3_photon")
class ActualShapeValidator:
    EXPECTED_LEDGER_KEYS=KEYS
    def _validate_post_map_metrics(self,row,classification,lane):
        if classification!="PASS" or set(row["public_widths"])!=set(m.FIELDS):
            raise ValueError("invalid owner post-map fields")
        if max(row["public_widths"].values())>=m.WIDTH_GATE:
            raise ValueError("original width not passed")
        if max(row["diagnostics"]["validated_local_error_bounds"].values())>=m.LOCAL_GATE:
            raise ValueError("original local bound not passed")
        if any(not v[0]<=0<=v[1] for v in row["set_ledgers"].values()):
            raise ValueError("original ledgers exclude zero")
def params():
    old={k:1e-6 for k in m.FIELDS}
    old["log_T"]=2.1245050576368385e-4
    new={k:1e-6 for k in m.FIELDS}
    width={k:0.0002 for k in m.FIELDS}
    raw={k:[-1.0,1.0] for k in KEYS}
    event={"any_event":False}
    return old,new,width,raw,event
class GateTests(unittest.TestCase):
    def test_new_proposal_passes_when_old_legacy_failure_is_preserved(self):
        r=m.check_old_new_gate(*params(),ActualShapeValidator())
        self.assertTrue(r["diagnostics"]["map_enclosed"])
        self.assertLess(r["diagnostics"]["maximum_validated_local_error"],m.LOCAL_GATE)
    def test_legacy_failure_cannot_be_erased(self):
        v=list(params());v[0]["log_T"]=1e-6
        with self.assertRaisesRegex(ValueError,"HISTORICAL"):m.check_old_new_gate(*v,ActualShapeValidator())
    def test_local_gate_strict_negative(self):
        v=list(params());v[1]["x_HII"]=m.LOCAL_GATE
        with self.assertRaisesRegex(ArithmeticError,"FROZEN_GATE"):m.check_old_new_gate(*v,ActualShapeValidator())
    def test_width_gate_strict_negative(self):
        v=list(params());v[2]["log_T"]=m.WIDTH_GATE
        with self.assertRaisesRegex(ArithmeticError,"FROZEN_GATE"):m.check_old_new_gate(*v,ActualShapeValidator())
    def test_ledger_nonzero_negative(self):
        v=list(params());v[3]["final_total_energy"]=[2.0,3.0]
        with self.assertRaisesRegex(ArithmeticError,"LEDGER_ZERO"):m.check_old_new_gate(*v,ActualShapeValidator())
    def test_missing_ledger_negative(self):
        v=list(params());v[3].pop("stage_group_0_photon")
        with self.assertRaisesRegex(ArithmeticError,"14_LEDGER"):m.check_old_new_gate(*v,ActualShapeValidator())
    def test_event_is_fail_closed(self):
        v=list(params());v[4]["any_event"]=True
        with self.assertRaisesRegex(ArithmeticError,"TABLE_EVENT"):m.check_old_new_gate(*v,ActualShapeValidator())
    def test_coordinate_missing_is_rejected(self):
        v=list(params());v[1].pop("x_HeII")
        with self.assertRaisesRegex(ValueError,"COORDINATE"):m.check_old_new_gate(*v,ActualShapeValidator())
    def test_original_state_is_not_written(self):
        content=p.read_text()
        self.assertNotIn("state_io.write_state(",content)
        self.assertNotIn("state_io.encode_state(",content)
        self.assertIn("SCOPED_V2_NATIVE_HHE_TICK161_PASS",content)
        self.assertIn("official_tick161_accepted",content)
        self.assertEqual(m.N,46080)
if __name__=="__main__":unittest.main()