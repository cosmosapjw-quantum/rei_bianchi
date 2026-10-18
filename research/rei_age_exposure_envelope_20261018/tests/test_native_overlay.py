"""Behavioral tests for the opt-in overlay; NOT native compile/science tests."""
from pathlib import Path
import ast
import pytest
import build_refined_sources as m

ROOT=Path(__file__).resolve().parents[1]
BASE=(ROOT/'donors/pr171/positive_native.rs').read_bytes()
PYBASE=(ROOT/'donors/pr171/positive_solver.py').read_bytes()

def test_age64_has_explicit_shared_mesh_control():
    rust, py = m.overlay(BASE, PYBASE)
    assert '"native_refine"' in rust
    assert 'refinement_levels' in rust and 'time_factor' in rust
    assert 'trial_on_mesh_trace' in rust

def test_old_native_physics_functions_are_byte_preserved():
    rust, _ = m.overlay(BASE, PYBASE)
    old = BASE.decode().split('fn main() ->')[0]
    assert rust.startswith(old)
    assert '"matrix_native" => native(q, Path::new(&args[3]), births, nmu, source, cells, true)' in rust

def test_python_changes_resource_bounds_only():
    _, py = m.overlay(BASE, PYBASE)
    ast.parse(py)
    assert 'a.max_rhs' in py and 'a.max_wall_s' in py
    for line in PYBASE.decode().splitlines():
        if 'p=argparse.' in line or 'frozen RHS/time cap' in line or "solver_return.json" in line:
            continue
        assert line in py

def test_mismatched_donor_rejected():
    with pytest.raises(ValueError, match='DONOR_SHA'):
        m.overlay(BASE+b'\n', PYBASE)

def test_generation_is_deterministic():
    assert m.overlay(BASE,PYBASE)==m.overlay(BASE,PYBASE)
