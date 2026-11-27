from pathlib import Path
import sys
import json
import os
import time
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from execution import atomic_json, run_process, manifest, verify_manifest


def test_atomic_create_only(tmp_path):
    p=tmp_path/'x.json';atomic_json(p,{'ok':True})
    with pytest.raises(FileExistsError):atomic_json(p,{'ok':False})
    assert json.loads(p.read_text())=={'ok':True}


def test_atomic_json_converts_numpy_bool_scalar(tmp_path):
    import numpy as np
    p=tmp_path/'numpy-bool.json'
    atomic_json(p,{'ok':np.bool_(True)})
    assert json.loads(p.read_text())=={'ok':True}


def test_nonfinite_refused(tmp_path):
    with pytest.raises(ValueError):atomic_json(tmp_path/'bad.json',{'x':float('nan')})
    assert not (tmp_path/'bad.json').exists()


def test_process_exit_record(tmp_path):
    r=run_process([sys.executable,'-c','print("done")'],tmp_path/'r',3.)
    assert r['returncode']==0 and not r['timed_out']
    assert (tmp_path/'r'/'stdout.log').read_text().strip()=='done'


def test_child_process_pins_numerical_thread_pools(tmp_path,monkeypatch):
    for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS',
                 'NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS'):
        monkeypatch.setenv(name,'64')
    code=('import os,json; print(json.dumps({k:os.environ.get(k) for k in '
          '"OMP_NUM_THREADS OPENBLAS_NUM_THREADS MKL_NUM_THREADS NUMEXPR_NUM_THREADS '
          'BLIS_NUM_THREADS OMP_DYNAMIC OMP_PLACES OMP_PROC_BIND".split()}))')
    r=run_process([sys.executable,'-c',code],tmp_path/'threads',3.)
    assert r['returncode']==0
    env=json.loads((tmp_path/'threads'/'stdout.log').read_text())
    assert all(env[k]=='1' for k in
               ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS',
                'NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS'))
    assert env['OMP_DYNAMIC']=='FALSE' and env['OMP_PLACES']=='cores' and env['OMP_PROC_BIND']=='close'


def test_timeout_process_group(tmp_path):
    code='import time; print("ready",flush=True); time.sleep(8)'
    r=run_process([sys.executable,'-c',code],tmp_path/'t',.7)
    assert r['timed_out'] and r['returncode']!=0
    assert (tmp_path/'t'/'RECEIPT.json').is_file()


def test_manifest_corruption(tmp_path):
    p=tmp_path/'source.py';p.write_text('a=1\n')
    data=manifest([p],tmp_path)
    verify_manifest(data,tmp_path)
    p.write_text('a=2\n')
    with pytest.raises(ValueError,match='SOURCE_IDENTITY'):
        verify_manifest(data,tmp_path)


def test_native_receipt_blocks_mismatched_binary(tmp_path):
    from he28_run import build_identity
    b=tmp_path/'binary';b.write_bytes(b'not a native binary')
    rec=tmp_path/'receipt.json';rec.write_text(json.dumps({'owner_source':'bad','binary_sha256':'bad'}))
    with pytest.raises(ValueError,match='NATIVE_BUILD_IDENTITY'):
        build_identity(b,rec)


def test_parent_manifest_real_sources():
    from he28_run import ROOT,REPO
    expected=json.loads((ROOT/'provenance/PARENT_SHA256.json').read_text())
    verify_manifest(expected,REPO)
    assert len(expected)>=10


def test_nonfinite_scientific_result_is_not_pass():
    from he28_run import check_result
    r={'number_defect':float('nan'),'energy_defect_ev':0.,'species_defect':[0.,0.,0.],
       'gas_positive':True,'min_photon':0.,'gas_final':[1e-5,1e-5,0.,.001],
       'temperature_K':8.}
    with pytest.raises(AssertionError):check_result(r)
