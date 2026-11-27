import copy
import unittest

from verify_sync import bind_selected_artifacts


class ArtifactScopeTests(unittest.TestCase):
    def setUp(self):
        self.path = "rust/rei_microphysics/src/lib.rs"
        self.expected = {self.path: "old", "certificate.json": "certificate"}
        self.observations = {self.path: {"sha256": "current"}, "certificate.json": {"sha256": "certificate"}}
        self.historical = {"commit": "6279036f06c9ba4d47574beab90b48fc2c6f9ba7", "path": self.path,
                           "sha256": "old", "matches_F04_top_level_artifact": True}

    def test_proven_library_snapshot_is_separate_from_new_certificate(self):
        matched, historical = bind_selected_artifacts(self.observations, self.expected, self.historical)
        self.assertEqual(matched, ["certificate.json"])
        self.assertEqual(historical[0]["snapshot_commit"], self.historical["commit"])
        self.assertEqual(historical[0]["current_sha256"], "current")

    def test_unknown_or_false_history_cannot_excuse_mismatch(self):
        for key, value in [("commit", "other"), ("sha256", "wrong"),
                           ("matches_F04_top_level_artifact", False)]:
            with self.subTest(key=key):
                historical = copy.deepcopy(self.historical)
                historical[key] = value
                with self.assertRaises(ValueError):
                    bind_selected_artifacts(self.observations, self.expected, historical)

    def test_certificate_corruption_cannot_be_excused_as_old_library(self):
        self.observations["certificate.json"]["sha256"] = "bad"
        with self.assertRaises(ValueError):
            bind_selected_artifacts(self.observations, self.expected, self.historical)


if __name__ == "__main__":
    unittest.main()
