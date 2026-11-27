"""Byte-pinned PHYS79 operator and saved controls; never execute old solvers."""
from pathlib import Path
import hashlib
import importlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
PROVENANCE = json.loads((ROOT / "vendor/PHYS79_PROVENANCE.json").read_text())
for relative, meta in PROVENANCE["files"].items():
    data = (ROOT / relative).read_bytes()
    if len(data) != meta["bytes"] or hashlib.sha256(data).hexdigest() != meta["sha256"]:
        raise RuntimeError("PHYS79_PIN_MISMATCH:" + relative)
sys.path.insert(0, str(ROOT / "vendor/phys79/source"))
def _checked_module(name):
    expected = (ROOT / "vendor/phys79/source" / (name+".py")).resolve()
    cached = sys.modules.get(name)
    if cached is not None and Path(getattr(cached, "__file__", "")).resolve() != expected:
        raise RuntimeError("PARENT_MODULE_CACHE_PATH_MISMATCH:" + name)
    module = importlib.import_module(name)
    if Path(module.__file__).resolve() != expected:
        raise RuntimeError("PARENT_MODULE_IMPORT_PATH_MISMATCH:" + name)
    return module

_bridge = _checked_module("phys78_bridge")
collisions = _checked_module("collisional")
parent_controls = _checked_module("run_controls")
atomic, lease_module = _bridge.atomic, _bridge.lease_module

CASES = {}
for path in sorted((ROOT / "inputs/phys79_cases").glob("*.json")):
    record = json.loads(path.read_text())
    if record["status"] != "COMPLETE":
        raise RuntimeError("PARENT_CONTROL_NOT_COMPLETE")
    CASES[record["task_id"]] = record
