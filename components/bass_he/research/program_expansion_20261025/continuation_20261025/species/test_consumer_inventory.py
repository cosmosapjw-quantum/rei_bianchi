"""New input/type tests; no historical scientific suite or rate evaluation."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import consumer_inventory as ci


class ConsumerInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = Path(__file__).resolve().parents[1]/"sources"
        cls.registry = json.loads((Path(__file__).resolve().parent/"SPECIES_PROVIDER_REGISTRY.json").read_text())
        cls.wu = json.loads((cls.sources/"raw/wu_chem_fixtures.json").read_bytes())

    def test_actual_baseline_and_synthetic_extension_counts_are_separate(self):
        got = self.registry["summary"]
        self.assertEqual((got["initial_atomic_charge_states"], got["neutron_slots"],
                          got["electron_pool_slots"], got["synthetic_extensions"]), (20, 1, 2, 9))
        self.assertEqual(got["all_supplied_rows"], 32)
        self.assertEqual(got["source_qualified_full_differential_providers"], 0)

    def test_electron_pools_remain_distinct_and_fast_not_thermalized(self):
        rows = {r["supplier_species_id"]: r for r in self.registry["species"]}
        self.assertNotEqual(rows["e_th"]["full_identity_key"], rows["e_fast"]["full_identity_key"])
        self.assertIsNone(rows["e_fast"]["rec_population_crosswalk"]["index"])
        self.assertEqual(rows["e_fast"]["scalar_provider_ids"], [])

    def test_arbitrary_supplier_isomer_and_charge_preserved(self):
        sample = {"physical_qualification": "source pending", "species": {
            "X": {"composition": [{"Z": 4, "A": 7, "isomer": "m1", "count": 1}],
                  "charge": -1, "state": "selected", "pool": "material"}}}
        row = ci.project_wu_species(sample)[0]
        self.assertEqual(row["full_identity_key"], (((4, 7, "m1", 1),), -1, "selected", "material"))
        self.assertFalse(row["physical_source_admitted"])

    def test_duplicate_full_identity_and_boolean_charge_rejected(self):
        sample = copy.deepcopy(self.wu)
        sample["species"]["duplicate"] = copy.deepcopy(sample["species"]["H1"])
        with self.assertRaisesRegex(ci.IntakeError, "DUPLICATE_FULL_IDENTITY"):
            ci.project_wu_species(sample)
        sample = copy.deepcopy(self.wu)
        sample["species"]["H1"]["charge"] = True
        with self.assertRaisesRegex(ci.IntakeError, "NONINTEGER"):
            ci.project_wu_species(sample)

    def test_changed_source_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"changed.json"
            path.write_bytes(b"{}")
            with self.assertRaisesRegex(ci.IntakeError, "SOURCE_BLOB_MISMATCH"):
                ci.read_pinned(path, ci.INPUT_BLOBS["wu_chem_fixtures.json"])

    def test_scalar_rate_record_cannot_fill_differential_kernel(self):
        for row in self.registry["scalar_provider_records"]:
            with self.assertRaisesRegex(ci.IntakeError, "SOURCE_QUANTITY_UNAVAILABLE"):
                ci.require_quantity(row, "differential_dsigma_dOmega")
            self.assertIs(ci.require_quantity(row, row["available_quantities"][0]), row)

    def test_synthetic_molecule_is_not_promoted_from_HD_pointer(self):
        row = next(r for r in self.registry["species"] if r["supplier_species_id"] == "H1D")
        self.assertTrue(row["synthetic_extension"])
        with self.assertRaisesRegex(ci.IntakeError, "PHYSICAL_SPECIES_BINDING_PENDING"):
            ci.require_physical_species(row)
        hd = self.registry["REC_HD_owner_pointer"]
        self.assertFalse(hd["p_o_mix_performed"])
        self.assertFalse(hd["extrapolation_performed"])
        self.assertEqual(hd["target_and_colliders"]["collider_ids"], [2, 3])

    def test_no_default_or_missing_pair_substitution(self):
        xml = b'<collisions><defaults><charged><Q11 type="screened"/></charged></defaults><pair s1="Li" s2="e-"><Q11 type="unknown"/></pair></collisions>'
        parsed = ci.parse_collision_inventory(xml)
        self.assertEqual(parsed["records"], [])
        self.assertFalse(parsed["defaults_evaluated"])

    def test_hd_request_preserves_exact_node_and_collider_domain(self):
        contract = json.loads((self.sources/"raw/rec_hd_adapter_contract.json").read_text())
        request = ci.require_hd_source_node(contract, 2, 100)
        self.assertEqual(request["collider_id"], 2)
        self.assertFalse(request["rate_supplied"])
        for collider, temperature in ((2, 75), (2, 201), ("mixed", 100), (True, 100), (2.0, 100)):
            with self.assertRaises(ci.IntakeError):
                ci.require_hd_source_node(contract, collider, temperature)

    def test_isotope_alias_requires_explicit_scoped_assumption(self):
        row = next(r for r in self.registry["species"] if r["supplier_species_id"] == "D")
        with self.assertRaisesRegex(ci.IntakeError, "EXPLICIT_ISOTOPE_REUSE_ASSUMPTION_REQUIRED"):
            ci.require_isotope_alias_assumption(row, "H")
        with self.assertRaisesRegex(ci.IntakeError, "SOURCE_LABEL_MISMATCH"):
            ci.require_isotope_alias_assumption(row, "He")
        assumption = {"supplier_species_id": "D", "source_label": "H",
                      "approximation": "elemental_transport_reuse", "scope": "consumer_mapping_only"}
        accepted = ci.require_isotope_alias_assumption(row, "H", assumption)
        self.assertEqual(accepted["status"], "CONDITIONAL_ALIAS_ONLY")
        self.assertFalse(accepted["physical_source_admitted"])
        assumption["supplier_species_id"] = "T"
        with self.assertRaisesRegex(ci.IntakeError, "EXPLICIT_ISOTOPE_REUSE_ASSUMPTION_REQUIRED"):
            ci.require_isotope_alias_assumption(row, "H", assumption)

    def test_nested_quantity_and_coefficients_remain_typed(self):
        xml = b'<collisions><pair s1="H" s2="H+"><Q11 type="Murphy"><Q1 type="Bruno-Eq(11)">1 2 3 4 5 6 7</Q1><Q2 type="Bruno-Eq(17)">8 9 10</Q2></Q11></pair></collisions>'
        row = ci.parse_collision_inventory(xml)["records"][0]
        expr = row["expressions"][0]
        self.assertEqual(expr["attributes"]["type"], "Murphy")
        self.assertEqual(expr["children"][1]["coefficient_decimal_strings"], ["8", "9", "10"])
        self.assertFalse(row["energy_resolved_sigma_l"])
        self.assertFalse(row["physical_angular_law"])

    def test_duplicate_and_malformed_source_pair_are_rejected(self):
        xml = b'<collisions><pair s1="H" s2="He"/><pair s1="He" s2="H"/></collisions>'
        with self.assertRaisesRegex(ci.IntakeError, "DUPLICATE_EXPLICIT_PAIR"):
            ci.parse_collision_inventory(xml)
        bad = b'<collisions><pair s1="H" s2="He"><Q11 type="Bruno-Eq(11)">1 2 3</Q11></pair></collisions>'
        with self.assertRaisesRegex(ci.IntakeError, "COLLISION_FIT_ARITY"):
            ci.parse_collision_inventory(bad)


if __name__ == "__main__":
    unittest.main()
