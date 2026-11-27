"""Public-only unit regression for the third warm-cell staging and error carry."""
import importlib.util
import json
import tempfile
import unittest
from fractions import Fraction as F
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

class TestThirdCell(unittest.TestCase):
    def setUp(self):
        self.stage=load(ROOT/"src/stage_third_cell.py","stage_third")
        self.propagate=load(ROOT/"checks/propagate_third.py","propagate_third")
        self.verify=load(ROOT/"checks/verify_third.py","verify_third")

    def test_patch_source_identity_enforced(self):
        self.assertEqual(self.stage.subst_once("one alpha","alpha","beta","example"),"one beta")
        with self.assertRaisesRegex(ValueError,"PATCH_BASELINE_CHANGED"):
            self.stage.subst_once("alpha alpha","alpha","beta","example")
        with self.assertRaisesRegex(ValueError,"PATCH_BASELINE_CHANGED"):
            self.stage.subst_once("other","alpha","beta","example")

    def test_exponential_positive_alternating(self):
        for x in (F(0),F(1,1000),F(1,100),F(1,10)):
            lo=self.verify.pexp_below(x);hi=self.verify.pexp_above(x)
            self.assertLessEqual(lo,hi)
            self.assertGreaterEqual(lo,F(0))
            self.assertLess(hi,F(1) if x>0 else F(2))

    def test_full_length_exact_photon_carry(self):
        with tempfile.TemporaryDirectory() as d:
            t=Path(d);(t/"inputs").mkdir();(t/"results").mkdir()
            incoming={
                "photon_error_end_raw_exact":["1/10"]*2904,
                "gas_error_end_scaled":["1","2","3","4"],
                "source_interval_s":["6250000000","12500000000"]}
            raw=(json.dumps(incoming,indent=2)+"\n").encode()
            import hashlib
            (t/"inputs/ENDPOINT_MEMORY_R7.json").write_bytes(raw)
            (t/"inputs/STAGED_SOURCE_IDENTITY.json").write_text(json.dumps({
                "source_commit":"pin","adapted_carry_sha256":hashlib.sha256(raw).hexdigest(),
                "input_previous_end_sha256":"prepin"}))
            gas=[{"rational":str(x)} for x in (F(1,1),F(2,1),F(3,1),F(128,1))]
            (t/"results/CERTIFICATE.json").write_text(json.dumps({"gas_error_components":gas}))
            C=[["0","0","0","0"] for _ in range(2904)]
            C[-1][0]="1/6250000000"
            residual=[{"integral":"1/100"} for _ in range(2904)]
            (t/"results/RESIDUAL_COUPLING.json").write_text(json.dumps({
                "C_scaled":C,"photon":residual}))
            old_root=self.propagate.ROOT
            try:
                self.propagate.ROOT=t
                result=self.propagate.compute()
            finally:self.propagate.ROOT=old_root
            vals=list(map(F,result["outgoing_photon_error_end_raw_exact"]))
            self.assertEqual(len(vals),2904)
            self.assertEqual(vals[0],F(11,100))
            self.assertEqual(vals[-1],F(111,100))
            self.assertEqual(F(result["incoming_sum"]),F(2904,10))
            self.assertEqual(F(result["added_coupling_sum"]),F(1))
            self.assertEqual(F(result["added_residual_sum"]),F(2904,100))

    def test_real_consumer_rejects_negative_radius(self):
        with tempfile.TemporaryDirectory() as d:
            t=Path(d);(t/"inputs").mkdir();(t/"results").mkdir()
            incoming={"photon_error_end_raw_exact":["0"]*2904,
                "gas_error_end_scaled":["0"]*4}
            incoming["photon_error_end_raw_exact"][2903]="-1/100"
            raw=(json.dumps(incoming)+"\n").encode()
            import hashlib
            (t/"inputs/ENDPOINT_MEMORY_R7.json").write_bytes(raw)
            (t/"inputs/STAGED_SOURCE_IDENTITY.json").write_text(json.dumps({
                "adapted_carry_sha256":hashlib.sha256(raw).hexdigest(),
                "input_previous_end_sha256":"pin","source_commit":"pin"}))
            (t/"results/CERTIFICATE.json").write_text(json.dumps({
                "gas_error_components":[{"rational":"0"}]*4}))
            (t/"results/RESIDUAL_COUPLING.json").write_text(json.dumps({
                "C_scaled":[["0"]*4 for _ in range(2904)],
                "photon":[{"integral":"0"} for _ in range(2904)]}))
            original=self.propagate.ROOT
            try:
                self.propagate.ROOT=t
                with self.assertRaisesRegex(ValueError,"NEGATIVE_PHOTON_RADIUS"):
                    self.propagate.compute()
            finally:self.propagate.ROOT=original
if __name__=="__main__":unittest.main()
