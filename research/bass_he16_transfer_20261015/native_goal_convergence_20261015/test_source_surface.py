"""Regression of functional source identity across distinct compiled Rust epochs."""
import json
from pathlib import Path
import unittest


class SurfaceIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=json.loads((Path(__file__).parent/"results"/
                              "RUST_SOURCE_SURFACE_IDENTITY.json").read_text())

    def test_full_compiled_source_epochs_are_explicitly_distinct(self):
        x=self.result
        self.assertFalse(x["full_source_epochs_identical"])
        self.assertNotEqual(x["frozen_full_source_identity_sha256"],
                            x["rlib_full_source_identity_sha256"])

    def test_tested_rust_transport_functions_are_byte_equal(self):
        x=self.result
        self.assertEqual(x["source_function_count"],10)
        self.assertTrue(x["all_ten_tested_function_bytes_equal"])
        funcs={r["function"] for r in x["function_surfaces"]}
        for function in ("pub fn deposit(","pub fn geometry_map(","pub fn pullback(",
                         "fn scaled_components(","pub fn point_at_scale("):
            self.assertIn(function,funcs)
        for r in x["function_surfaces"]:
            self.assertTrue(r["matches_frozen_source"])
            self.assertTrue(r["matches_compiled_rlib_source"])


if __name__=="__main__":
    unittest.main()
