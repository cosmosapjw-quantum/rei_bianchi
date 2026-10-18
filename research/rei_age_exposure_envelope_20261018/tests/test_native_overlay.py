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
    old = BASE.decode()
    original='    cfg.transport_threads = 1;'
    replacement=('    cfg.transport_threads = std::env::var("REI_TRANSPORT_THREADS")\n'
                 '        .ok().and_then(|value| value.parse::<usize>().ok())\n'
                 '        .unwrap_or(1).clamp(1, 48);')
    assert old.count(original)==1
    assert rust.count(replacement)==1
    restored=rust.replace(replacement,original,1)
    addition=(ROOT/'src/native_refine.rs.inc').read_text()+'\n'
    assert restored.count(addition)==1
    restored=restored.replace(addition,'',1)
    arm='''        "native_refine" => {
            let levels = args.get(8).ok_or("missing common birth levels")?
                .split(',').map(str::parse::<usize>).collect::<Result<Vec<_>, _>>()?;
            let factor: usize = args.get(9).ok_or("missing time factor")?.parse()?;
            native_refine(q, Path::new(&args[3]), births, nmu, source, cells, &levels, factor)
        }
'''
    assert restored.count(arm)==1
    assert restored.replace(arm,'',1)==old
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
