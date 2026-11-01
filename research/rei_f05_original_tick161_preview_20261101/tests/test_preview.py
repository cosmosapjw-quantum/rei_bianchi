"""Exact source preview algebra, negative-physical and authority controls."""
import unittest,importlib.util,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("source_preview_audit_for_test",ROOT/"audit_preview.py")
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
def case():
    NH,HE=1000.,100.
    xH,xHeII,xHeIII=.8,.9,.1
    ne=NH*xH+HE*(xHeII+2*xHeIII)
    old_ne=ne+10.
    T0,T=10000.,9990.
    U=1.5*audit.KB*(NH+HE+ne)*T
    values={
      "source_H_nuclei_N":NH,"source_He_nuclei_N":HE,
      "tick160_xHII":.81,"tick161_preview_xHII":xH,
      "tick161_preview_xHeII":xHeII,"tick161_preview_xHeIII":xHeIII,
      "tick160_Tgas_K":T0,"tick161_preview_Tgas_K":T,
      "tick160_electron_count_N":old_ne,"tick161_preview_electron_count_N":ne,
      "tick161_preview_U_erg":U,"tick160_to_161_delta_logT":math.log(T/T0),
      "tick160_to_161_delta_electron_N":ne-old_ne}
    r={"node":"0"}
    for k,v in values.items():
        r[k+"_lower"]=str(v);r[k+"_upper"]=str(v)
    return r
class NativePhysicalPreviewTests(unittest.TestCase):
    def test_synthetic_physical(self):
        x=audit.check_row(case(),0)
        self.assertEqual(x["N_e_lower"],910.)
        self.assertEqual(x["dNe_lower"],-10.)
    def test_negative_charge_mismatch(self):
        r=case();r["tick161_preview_electron_count_N_lower"]="920"
        r["tick161_preview_electron_count_N_upper"]="920"
        with self.assertRaisesRegex(ValueError,"ELECTRON_COUNTS"):
            audit.check_row(r,0)
    def test_negative_he_fraction(self):
        r=case();r["tick161_preview_xHeIII_lower"]="1.1"
        r["tick161_preview_xHeIII_upper"]="1.1"
        with self.assertRaisesRegex(ValueError,"ION_FRACTION_CONE"):
            audit.check_row(r,0)
    def test_negative_temperature(self):
        r=case();r["tick161_preview_Tgas_K_lower"]="0"
        r["tick161_preview_Tgas_K_upper"]="0"
        with self.assertRaisesRegex(ValueError,"NONPOSITIVE"):
            audit.check_row(r,0)
    def test_negative_correlated_increment_disjoint(self):
        r=case();r["tick160_to_161_delta_electron_N_lower"]="5"
        r["tick160_to_161_delta_electron_N_upper"]="5"
        with self.assertRaisesRegex(ValueError,"CORRELATED_ELECTRON"):
            audit.check_row(r,0)
    def test_negative_wrong_node(self):
        r=case();r["node"]="4"
        with self.assertRaisesRegex(ValueError,"BAD_NODE_ORDER"):
            audit.check_row(r,0)
    def test_source_protection(self):
        code=(ROOT/"owner_tick161_preview.py").read_text()
        self.assertNotIn("state_io.write_state(",code)
        self.assertNotIn(".state\"",code)
        self.assertIn("NOT_ACCEPTED_OR_WRITTEN",code)
        self.assertEqual(audit.N,46080)
if __name__=="__main__":unittest.main()