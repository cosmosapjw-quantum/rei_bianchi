"""One child process: manufactured controls, then one saved C7 calibration."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import unittest

from run_saved_caloric_branch import calibrate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).resolve().parent),
                                                  pattern="test_caloric_branch.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 2
    # Read the preserved source once, after independently specified fixtures.
    output = calibrate(args.input.read_bytes(), source_path=str(args.input.resolve()))
    output["manufactured_test_counts"] = {
        "run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
        "scope": "test counts are not physics progress"
    }
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(output, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
