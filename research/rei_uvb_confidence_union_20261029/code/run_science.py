"""One child invocation runs the new tests and only then serializes source output."""
import json
from pathlib import Path
import sys
import unittest

UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT / "tests"))
import test_confidence_union as checks
from confidence_union import build_result


def main():
    suite = unittest.defaultTestLoader.loadTestsFromModule(checks)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    payload = build_result(checks.SOURCE_MODEL, checks.EVIDENCE)
    (UNIT / "outputs/RESULT.json").write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    rows = ["provenance\tinterval_kind\tcoordinate\tlower\tupper\tq\tquantile_df\tinterpretation"]
    for label, intervals in payload["coordinate_intervals"].items():
        item = payload["quantiles"].get(label, {})
        interpretation = item.get("coverage", "deterministic nuisance image; no confidence level")
        for coordinate, (lower, upper) in zip(payload["coordinate_order"], intervals):
            rows.append("\t".join(map(str, ["source", label, coordinate, format(lower, ".17g"),
                format(upper, ".17g"), item.get("q", 0), item.get("degrees_of_freedom", "NA"), interpretation])))
    (UNIT / "outputs/intervals.tsv").write_text("\n".join(rows) + "\n")
    print("New algebraic, direct-residual, support, ellipse and analytic controls passed; source RESULT.json/intervals.tsv written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
