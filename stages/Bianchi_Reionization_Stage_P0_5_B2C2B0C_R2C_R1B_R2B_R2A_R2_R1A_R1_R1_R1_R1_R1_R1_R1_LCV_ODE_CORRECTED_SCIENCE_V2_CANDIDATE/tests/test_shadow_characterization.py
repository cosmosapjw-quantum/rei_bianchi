from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


STAGE = Path(__file__).resolve().parents[1]
PROBE_PATH = STAGE / "tools/predecessor_red_probe.py"
SPEC = importlib.util.spec_from_file_location("n_shadow_predecessor_probe", PROBE_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(PROBE_PATH)
PROBE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PROBE
SPEC.loader.exec_module(PROBE)


class ShadowCharacterizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.observed = PROBE.collect()

    def test_predecessor_bytes_are_the_bound_red_preimage(self) -> None:
        self.assertEqual(
            self.observed["source_sha256"],
            {
                "adaptive_policy.py": (
                    "c648c0ae1e10bced3b159e96f92bdc5f2bd3c1031b9a13e6b947dbf102557aa9"
                ),
                "implicit_certificates.py": (
                    "197aee751933a9b80c97453e55ecb9f0a346f8c85198715841ea2255c4e1c185"
                ),
                "interval_arithmetic.py": (
                    "ea8383f8f4bc0d463d9908af9baa4743ad80e125b60d22991028b4d57a10ec22"
                ),
                "run_adaptive_history.py": (
                    "b26432ad582a8b01e9eb3b15585fb69df0d2a2fea26c7bd482020965c0fc233e"
                ),
            },
        )

    def test_exact_red_witnesses_remain_visible(self) -> None:
        self.assertFalse(self.observed["signed_sum"]["contains_exact"])
        for witness in self.observed["krawczyk"]:
            self.assertEqual(witness["certified"], [True])
            self.assertEqual(witness["contains_exact"], [False, False])
        self.assertNotEqual(
            self.observed["heii"]["current_double_factor"],
            self.observed["heii"]["number_density_single_factor"],
        )
        self.assertFalse(self.observed["terminal_fsm"]["terminal_absorbing"])
        self.assertTrue(
            self.observed["admission"]["accepted_without_all_new_predicates"]
        )

    def test_successor_is_not_routed_into_the_predecessor_controller(self) -> None:
        predecessor = PROBE.A_STAGE / "analysis/run_adaptive_history.py"
        text = predecessor.read_text(encoding="utf-8")
        self.assertNotIn("LCV_ODE_CORRECTED_SCIENCE_V2_CANDIDATE", text)
        self.assertNotIn("admission_contract", text)
        self.assertNotIn("terminal_fsm", text)


if __name__ == "__main__":
    unittest.main()
