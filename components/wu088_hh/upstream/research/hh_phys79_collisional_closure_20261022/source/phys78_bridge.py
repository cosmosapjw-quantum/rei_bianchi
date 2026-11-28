"""Load byte-pinned, unmodified PHYS78 components; never call its ODE runner."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROVENANCE = json.loads((ROOT/'vendor/PHYS78_PROVENANCE.json').read_text())

def _load(name, relative):
    path = ROOT/relative
    expected = PROVENANCE['files'][relative]['sha256']
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError('PINNED_PARENT_BYTES_CHANGED:'+relative)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

atomic = _load('phys79_parent_atomic', 'vendor/phys78/source/atomic_network.py')

def lease_module():
    """Only reuse LeasePool/observe_resources/release_lease, not run_cases."""
    return _load('phys79_parent_leases', 'vendor/phys78/source/run_pilot.py')
