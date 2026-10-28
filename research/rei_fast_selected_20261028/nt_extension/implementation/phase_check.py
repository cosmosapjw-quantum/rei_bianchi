"""Run targeted presentation tests, then extract saved data in one bounded child."""

import json
import sys
import unittest

import test_projection
from project_saved import CASE, extract, write_outputs


def main():
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_projection)
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    data = extract()
    write_outputs(data)
    print(json.dumps({"case": CASE, "epochs": data["epoch_count"], "sample_checks": len(data["sample_checks"]), "tests": result.testsRun}))


if __name__ == "__main__":
    main()
