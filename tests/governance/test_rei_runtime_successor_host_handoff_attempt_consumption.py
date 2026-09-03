from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
RUNNER = (
    ROOT
    / "handoff"
    / "rei_runtime_bridge_successor_host_20260903"
    / "successor_runtime_runner.py"
)


def load_runner():
    spec = importlib.util.spec_from_file_location(
        "rei_successor_attempt_consumption_test", RUNNER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("runner import unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SuccessorAttemptConsumptionTests(unittest.TestCase):
    def test_remote_reservation_consumes_attempt_before_native_dispatch(self) -> None:
        runner = load_runner()
        self.assertEqual(
            runner.remaining_attempts_after_stop(global_acquired=False), 1
        )
        self.assertEqual(
            runner.remaining_attempts_after_stop(global_acquired=True), 0
        )


if __name__ == "__main__":
    unittest.main()
