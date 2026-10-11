"""Pure serialization regression: AST dictionary only, no science import."""
import ast
import hashlib
import json
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent
UNIT = OUT.parent.parent
PINS = {
    "before": "9549de417a4055ce111f1973639b02bdb774b84998755703892bb3d78bbb5f2e",
    "after": "35d8415c67851cfdd1fbbb8ff292be63774d6f5266f83cacebdb1f95f6dad2d4",
}


def expression(path):
    tree = ast.parse(path.read_bytes(), filename=str(path))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
              and n.name == "endpoint_fixtures")
    calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Attribute) and n.func.attr == "append"
             and isinstance(n.func.value, ast.Name) and n.func.value.id == "rows"]
    assert len(calls) == 1 and len(calls[0].args) == 1
    node = calls[0].args[0]
    assert isinstance(node, ast.Dict)
    assert [ast.literal_eval(k) for k in node.keys] == [
        "atom", "threshold", "threshold_hex", "included"]
    return compile(ast.Expression(node), str(path), "eval")


def main():
    paths = {"before": UNIT / "evidence/serialization_r1/validate_selective.before.py",
             "after": UNIT / "validate_selective.py"}
    raw = {key: path.read_bytes() for key, path in paths.items()}
    hashes = {key: hashlib.sha256(data).hexdigest() for key, data in raw.items()}
    assert hashes == PINS
    needle = b"'included':active"
    assert raw["before"].count(needle) == 1
    assert raw["before"].endswith(b"\n\n")
    replaced = raw["before"].replace(needle, b"'included':bool(active)", 1)
    assert len(replaced) == 16448 and len(raw["after"]) == 16447
    assert replaced[:-1] == raw["after"]
    expressions = {key: expression(path) for key, path in paths.items()}
    rows = []
    for name, active in [("python_true", True), ("python_false", False),
                         ("numpy_true", np.bool_(True)), ("numpy_false", np.bool_(False))]:
        env = {"atom": 10.0, "threshold": 2.5, "active": active,
               "float": float, "bool": bool, "__builtins__": {}}
        before = eval(expressions["before"], env)
        if isinstance(active, np.bool_):
            try:
                json.dumps(before, allow_nan=False)
            except TypeError:
                original = "EXPECTED_TYPEERROR"
            else:
                raise AssertionError("NumPy bool unexpectedly serialized")
        else:
            assert json.loads(json.dumps(before, allow_nan=False))["included"] is active
            original = "PASS"
        repaired = eval(expressions["after"], env)
        assert type(repaired["included"]) is bool
        expected = {"atom": 10.0, "threshold": 2.5,
                    "threshold_hex": float(2.5).hex(), "included": bool(active)}
        assert json.loads(json.dumps(repaired, allow_nan=False)) == expected
        rows.append({"case": name, "original": original,
                     "repaired": "PASS", "included": bool(active)})
    return {"outcome": "SOURCE_REPAIR_SERIALIZATION_TEST_PASS_SCOPED",
            "source_sha256": hashes, "exact_source_relation": True, "cases": rows,
            "execution": {"test_process": 1, "native_process": 0, "SIGMA": 0,
                          "RHS": 0, "JAC": 0, "ODE": 0, "build": 0, "quadrature": 0}}


if __name__ == "__main__":
    try:
        result = main()
    except Exception as exc:
        result = {"outcome": "HOLD_SERIALIZATION_R2", "error_type": type(exc).__name__,
                  "error": str(exc)}
    with (OUT / "RESULT.json").open("x") as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps(result, allow_nan=False))
    raise SystemExit(0 if result["outcome"].startswith("SOURCE_REPAIR_") else 1)
