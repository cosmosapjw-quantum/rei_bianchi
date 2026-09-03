from __future__ import annotations

import ast
import hashlib
import importlib.util
import inspect
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STAGE = ROOT / "stages" / "REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER"
BRIDGE = STAGE / "analysis" / "rust_source_bound_thermal.py"
INPUT_LOCK = STAGE / "INPUT_LOCK.json"
EXPECTED_BRIDGE_SHA256 = (
    "91fe316f1e8b81d64e9929d7a4814b77808fdf486e2ca67cd2f615e8617fce85"
)
EXPECTED_DECLARED_PATH_COUNT = 17


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_bridge():
    spec = importlib.util.spec_from_file_location("rei_ntpath_closure_bridge", BRIDGE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load bridge at {BRIDGE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _runtime_closure() -> dict[str, object]:
    lock = json.loads(INPUT_LOCK.read_text(encoding="utf-8"))
    closure = lock.get("runtime_closure")
    if not isinstance(closure, dict):
        raise AssertionError("runtime_closure is missing")
    return closure


class NtpathRuntimeClosureTests(unittest.TestCase):
    def test_01_pathlib_has_an_explicit_ntpath_dependency(self) -> None:
        import pathlib

        source_path = Path(inspect.getsourcefile(pathlib) or "")
        self.assertTrue(source_path.is_file())
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        imports = {
            alias.name.split(".", 1)[0]
            for node in tree.body
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        self.assertIn("ntpath", imports)

    def test_02_production_lock_declares_only_the_observed_stdlib_delta(self) -> None:
        closure = _runtime_closure()
        roots = closure["declared_import_roots"]
        self.assertIsInstance(roots, list)
        self.assertEqual(roots, sorted(set(roots)))
        self.assertIn("pathlib", roots)
        self.assertIn("ntpath", roots)
        self.assertEqual(closure["forbidden_import_roots"], ["jax", "jaxlib"])
        self.assertEqual(len(closure["declared_paths"]), EXPECTED_DECLARED_PATH_COUNT)
        self.assertEqual(_sha256(BRIDGE), EXPECTED_BRIDGE_SHA256)

    def test_03_cached_ntpath_import_is_observed_and_admitted(self) -> None:
        bridge = _load_bridge()
        result = bridge.validate_runtime_closure(
            repo=ROOT,
            stage_dir=STAGE,
            input_lock_path=INPUT_LOCK,
            invocation=lambda _capability: __import__("ntpath"),
        )
        self.assertEqual(result["status"], "PASS")
        self.assertGreaterEqual(result["observed_import_count"], 1)

    def test_04_unrelated_import_does_not_become_implicitly_allowed(self) -> None:
        closure = _runtime_closure()
        roots = set(closure["declared_import_roots"])
        self.assertNotIn("random", roots)
        self.assertNotIn("site", roots)
        self.assertNotIn("jax", roots)
        self.assertNotIn("jaxlib", roots)


if __name__ == "__main__":
    unittest.main()
