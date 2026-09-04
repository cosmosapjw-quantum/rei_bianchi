#!/usr/bin/env python3
"""TDD contract for GitHub-normalized independent ruleset readback."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT
    / "docs"
    / "rei_runtime_bridge_03a3r3_independent_readback"
    / "independent_readback_audit_v2.py"
)
PATCHED_ADMIN_BLOB = "0b1b56d6dcaf2bc4ed68ba938ad20feeaeab0ecf"


def load_active_auditor():
    spec = importlib.util.spec_from_file_location(
        "rei_independent_readback_normalization", SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalized_live_state(module):
    details = json.loads(json.dumps(module.RULESET_PAYLOAD))
    details["id"] = 42
    details["rules"][0] = {"type": "update"}
    listed = [{"id": 42, "name": module.RULESET_NAME}]
    effective = [
        {"type": "update", "ruleset_id": 42},
        {"type": "deletion", "ruleset_id": 42},
        {"type": "non_fast_forward", "ruleset_id": 42},
    ]
    return listed, details, effective


class IndependentReadbackNormalizationContract(unittest.TestCase):
    def test_live_github_get_may_omit_update_parameters(self) -> None:
        module = load_active_auditor()
        listed, details, effective = normalized_live_state(module)
        snapshot = module.validate_live_snapshot(
            ruleset_list=listed,
            ruleset_details=details,
            effective_rules=effective,
            ref_http_status=404,
            expected_ruleset_id=42,
        )
        self.assertEqual(snapshot["ruleset_id"], 42)
        self.assertTrue(snapshot["global_ref_absent"])

    def test_active_auditor_pins_the_actual_patched_admin_generator(self) -> None:
        module = load_active_auditor()
        self.assertEqual(module.PARENT_ADMIN_BLOB, PATCHED_ADMIN_BLOB)


if __name__ == "__main__":
    unittest.main(verbosity=2)
