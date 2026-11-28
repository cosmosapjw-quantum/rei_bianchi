"""Pinned dependencies and small loader shared by the HE31 entry points."""
from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys

UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
VENDOR = UNIT.parent / "he29_rei_pilot_20261021" / "vendor"
HE30_SRC = UNIT.parent / "he30_z2_continuation_20261021" / "src"


@lru_cache(maxsize=1)
def verify_baseline():
    manifest = json.loads((UNIT / "evidence/BASELINE_MANIFEST.json").read_text())
    for rel, expected in manifest["files"].items():
        if hashlib.sha256((REPO/rel).read_bytes()).hexdigest() != expected:
            raise RuntimeError("pinned dependency changed: " + rel)
    return manifest


def load_model():
    verify_baseline()
    for name in ("canonical_fv", "species_hierarchy", "lrs_boltzmann"):
        module = sys.modules.get(name)
        if module is not None and Path(module.__file__).resolve() != VENDOR/(name+".py"):
            raise RuntimeError("unexpected imported source for " + name)
    if str(VENDOR) in sys.path:
        sys.path.remove(str(VENDOR))
    sys.path.insert(0, str(VENDOR))
    from canonical_fv import CanonicalFVSpecies, CanonicalMomentumFV
    from lrs_boltzmann import SourceLock
    for name in ("canonical_fv", "species_hierarchy", "lrs_boltzmann"):
        if Path(sys.modules[name].__file__).resolve() != VENDOR/(name+".py"):
            raise RuntimeError("unexpected resolved source for " + name)
    return CanonicalFVSpecies, CanonicalMomentumFV, SourceLock


def load_runner():
    verify_baseline()
    resources = VENDOR/"resources"
    for item in ("c21k_scheduler", "bass_resources"):
        module = sys.modules.get(item)
        if module is not None and Path(module.__file__).resolve() != resources/(item+".py"):
            raise RuntimeError("unexpected resource module: " + item)
    # Distinct name prevents collision with another lane's shared_runner.py.
    import importlib.util
    name = "he31_reused_he30_runner"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, HE30_SRC/"shared_runner.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        for item in ("c21k_scheduler", "bass_resources"):
            if Path(sys.modules[item].__file__).resolve() != resources/(item+".py"):
                raise RuntimeError("unexpected resolved resource module: " + item)
    return sys.modules[name]


@lru_cache(maxsize=1)
def implementation_identity():
    dependencies = verify_baseline()
    # Plotting, campaign scheduling and packaging edits do not invalidate
    # completed physical cases. These four files implement the receiver.
    names = ("bindings.py", "receiver.py", "electron_donor.py", "prepared_moments.py")
    local = {name:hashlib.sha256((UNIT/"src"/name).read_bytes()).hexdigest() for name in names}
    physics_dependencies = {path:sha for path,sha in dependencies["files"].items()
                            if Path(path).parent == Path("research/he29_rei_pilot_20261021/vendor")}
    raw = json.dumps(dict(dependencies=physics_dependencies, implementation=local),
                     sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()
