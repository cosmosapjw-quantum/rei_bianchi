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
    restored=restored.replace(arm,'',1)
    binary=(ROOT/'src/binary_server.rs.inc').read_text()
    assert restored.count(binary)==1
    restored=restored.replace(binary,'',1)
    restored=restored.replace('    transport_cells: usize,\n    binary_rpc: bool,','    transport_cells: usize,',1)
    restored=restored.replace('let offset = if args[1] == "server" || args[1] == "server_binary64" { 3 } else { 4 };',
                              'let offset = if args[1] == "server" { 3 } else { 4 };',1)
    restored=restored.replace('"server" => server(q, births, nmu, source, cells, false),\n        "server_binary64" => server(q, births, nmu, source, cells, true),',
                              '"server" => server(q, births, nmu, source, cells),',1)
    assert restored==old
    assert '"matrix_native" => native(q, Path::new(&args[3]), births, nmu, source, cells, true)' in rust

def test_python_changes_resource_bounds_and_opt_in_rpc_only():
    _, py = m.overlay(BASE, PYBASE)
    ast.parse(py)
    assert 'a.max_rhs' in py and 'a.max_wall_s' in py
    for line in PYBASE.decode().splitlines():
        if any(x in line for x in ('p=argparse.','frozen RHS/time cap','solver_return.json',
            'server=subprocess.Popen','setup=json.loads','def send(','server.stdin.write',
            'line=server.stdout.readline','if not line:','return line.strip()',
            "if answer.startswith('ERR')",'result=np.fromstring(answer','import argparse,json')):
            continue
        assert line in py
    assert "choices=('text','binary64'),default='text'" in py
    assert "'server_binary64' if a.rpc_mode=='binary64' else 'server'" in py
    assert 'rtol=2e-11 if a.tight else 2e-10' in py
    assert 'abs(er)<=1e-8*eg and abs(nr)<=1e-8*ng' in py

def test_mismatched_donor_rejected():
    with pytest.raises(ValueError, match='DONOR_SHA'):
        m.overlay(BASE+b'\n', PYBASE)

def test_generation_is_deterministic():
    assert m.overlay(BASE,PYBASE)==m.overlay(BASE,PYBASE)

def test_binary_rpc_pipe_helpers_handle_fragmented_io():
    source=(ROOT/'src/binary_solver.py.inc').read_text()
    tree=ast.parse(source)
    helpers=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in ('_write_all','_read_exact')]
    namespace={}
    exec(compile(ast.Module(body=helpers,type_ignores=[]),'<binary_rpc_helpers>','exec'),namespace)
    class Fragmented:
        def __init__(self,data=b''):
            self.data=bytearray(data)
            self.written=bytearray()
        def read(self,size):
            take=min(size,2)
            result=bytes(self.data[:take]);del self.data[:take]
            return result
        def write(self,data):
            self.written.extend(data[:3])
            return min(len(data),3)
    stream=Fragmented(b'abcdefgh')
    assert namespace['_read_exact'](stream,8)==b'abcdefgh'
    namespace['_write_all'](stream,b'12345678')
    assert bytes(stream.written)==b'12345678'
    with pytest.raises(RuntimeError,match='TRUNCATED'):
        namespace['_read_exact'](Fragmented(b'abc'),4)
