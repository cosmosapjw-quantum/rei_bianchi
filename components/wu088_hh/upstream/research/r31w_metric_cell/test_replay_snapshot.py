"""Preserved-data checks. No native calculations or HH propagation."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import pytest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import replay_snapshot
INPUT=Path(os.environ.get('WU088_R31W_INPUT', HERE/'inputs/EXISTING_METRIC_INPUTS.npz'))

@pytest.fixture(scope='module')
def replay():
    return replay_snapshot.compute(INPUT)

def test_stored_hybrid_witness_and_claim_ceiling(replay):
    assert replay['hybrid_point']['eta_svd']==pytest.approx(.6007169417167524,rel=1.e-11)
    assert replay['direct_point']['eta_svd']<1.e-11
    assert replay['snapshot_changed'] is False
    assert replay['affine_cell_bound_instantiated'] is False
    assert replay['production_admitted'] is False
    assert replay['new_native_pair_evaluations']==0

def test_only_ionic_affine_cell_diagnostic(replay):
    cell=replay['ionic_affine_subblock']
    assert cell['uniform_eta_numeric']==pytest.approx(.03680954714134556,rel=1.e-11)
    assert cell['certified'] is False
    assert cell['full_HH_interval_bound'] is False
    assert cell['minimum_endpoint_overlap_eigenvalue']>.7

def test_tampered_input_rejected_before_numpy(tmp_path):
    p=tmp_path/'wrong.npz';p.write_bytes(b'not the frozen snapshot')
    with pytest.raises(ValueError,match='SHA-256 mismatch'):
        replay_snapshot.compute(p)

def test_existing_output_preserved_before_input_read(tmp_path):
    target=tmp_path/'out.json';target.write_text('keep me\n')
    p=subprocess.run([sys.executable,str(HERE/'replay_snapshot.py'),
       '--input',str(tmp_path/'missing.npz'),'--out',str(target)],capture_output=True,text=True)
    assert p.returncode!=0 and 'FileExistsError' in p.stderr
    assert target.read_text()=='keep me\n'
