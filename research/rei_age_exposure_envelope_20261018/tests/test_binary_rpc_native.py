"""Opt-in compiled native parity check: REI_NATIVE_PARITY_BINARY=/path/to/example.

The ordinary sandbox suite has no requirement to build the frozen Rust donor.
"""
import ast
import json
import os
import struct
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]

def exact_io_helpers():
    tree=ast.parse((ROOT/'src/binary_solver.py.inc').read_text())
    names={'_write_all','_read_exact'}
    helpers=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in names]
    assert {node.name for node in helpers}==names
    namespace={}
    exec(compile(ast.Module(body=helpers,type_ignores=[]),'<binary_rpc_helpers>','exec'),namespace)
    return namespace['_write_all'],namespace['_read_exact']


def test_compiled_binary_rhs_endpoint_and_ledger_parity(tmp_path):
    path = os.environ.get('REI_NATIVE_PARITY_BINARY')
    if not path:
        pytest.skip('set REI_NATIVE_PARITY_BINARY to an overlay-compiled positive_native')
    binary = Path(path).resolve()
    assert binary.is_file()
    write_all,read_exact=exact_io_helpers()
    processes = []
    try:
        for mode in ('server', 'server_binary64'):
            p = subprocess.Popen([str(binary),mode,'0','1','8','8','8'],
                                 stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,bufsize=0)
            processes.append(p)
        setup = [json.loads(p.stdout.readline()) for p in processes]
        assert setup[0] == setup[1]
        size = 4 + 2 * len(setup[0]['births']) * setup[0]['cells'] + setup[0]['extra']
        state = np.zeros(size,dtype='<f8')
        state[:4] = setup[0]['initial']
        x = setup[0]['x0']
        text, binary_rpc = processes
        write_all(text.stdin,(f'R 0 {x:.17e} '+' '.join(format(v,'.17e') for v in state)+'\n').encode())
        text.stdin.flush()
        rhs_text = np.fromstring(text.stdout.readline().decode(),sep=' ')
        write_all(binary_rpc.stdin,struct.pack('<cIdI',b'R',0,x,size)+state.tobytes())
        binary_rpc.stdin.flush()
        header = read_exact(binary_rpc.stdout,5)
        status,length = struct.unpack('<BI',header)
        assert status == 0 and length == size*8
        rhs_binary = np.frombuffer(read_exact(binary_rpc.stdout,length),dtype='<f8')
        assert np.array_equal(rhs_text,rhs_binary)
    finally:
        for p in processes:
            if p.poll() is None:
                p.stdin.close()
                p.wait(timeout=5)

    solver = binary.parents[5]/'positive_solver_refined.py'
    assert solver.is_file()
    for mode in ('text','binary64'):
        out=tmp_path/mode
        subprocess.run([sys.executable,str(solver),str(binary),str(out),
                        '--birth-panels','1','--transport-cells','8',
                        '--max-wall-s','60','--rpc-mode',mode],check=True,timeout=70)
    left,right=tmp_path/'text',tmp_path/'binary64'
    for name in ('endpoint.json','ledgers.json'):
        assert json.loads((left/name).read_text())==json.loads((right/name).read_text())
    lr=json.loads((left/'solver_return.json').read_text())
    rr=json.loads((right/'solver_return.json').read_text())
    assert lr['status']==rr['status']=='SCOPED_NUMERICAL_EXECUTION_COMPLETE'
    assert lr['calls']==rr['calls']
    for f in left.glob('accepted_coordinates_event*.npy'):
        assert np.array_equal(np.load(f),np.load(right/f.name))
