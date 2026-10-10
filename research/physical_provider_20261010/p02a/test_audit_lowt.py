import copy
import importlib.util
import math
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("audit_lowt", Path(__file__).with_name("audit_lowt.py"))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class LowTemperatureDiagnosticTests(unittest.TestCase):
    def test_unclipped_k1_and_exponential_ratios(self):
        expr = audit.unclipped_expressions()
        self.assertTrue(math.isclose(expr["k1"], 3.9858704414352813e-22, rel_tol=3e-12))
        self.assertTrue(math.isclose(1e-20 / expr["k1"], 25.088622791259308, rel_tol=3e-12))
        self.assertTrue(math.isclose(math.exp(473638 / 5000) / 1e30, 1.379348363443488e11, rel_tol=3e-12))
        self.assertTrue(math.isclose(math.exp(470000 / 5000) / 1e30, 6.663176216410912e10, rel_tol=3e-12))

    def test_primary_RR_comparator(self):
        values = audit.hg_rr()
        self.assertTrue(math.isclose(values["HII"], 6.975127812378202e-13, rel_tol=3e-12))
        self.assertTrue(math.isclose(values["HeII"], 6.647688939149075e-13, rel_tol=3e-12))

    def test_consumer_metadata_or_parity_cannot_be_promoted(self):
        rows = {n: {"rust": 1e-20, "unit": "cm3/s" if n.startswith("k") else
                    "erg*cm6/s" if n in ("ceHeI", "ciHeIS") else "erg*cm3/s",
                    "consumer_admission": False, "physical_support_resolved": False} for n in audit.NAMES}
        c = {n: 1e-20 for n in audit.NAMES}
        audit.validate_rows(copy.deepcopy(rows), c)
        rows["k1"]["consumer_admission"] = True
        with self.assertRaisesRegex(ValueError, "RAW_PROVIDER_METADATA"):
            audit.validate_rows(copy.deepcopy(rows), c)
        rows["k1"]["consumer_admission"] = False
        c["k1"] = 2e-20
        with self.assertRaisesRegex(ValueError, "C_PARITY"):
            audit.validate_rows(rows, c)

    def test_incomplete_probe_rejected(self):
        with self.assertRaisesRegex(ValueError, "RUST_PROBE_SCHEMA"):
            audit.parse_rust("k1_rate,1e-20,cm3/s,n_e*n_HI,false,false\n")


if __name__ == "__main__":
    unittest.main()
