from pathlib import Path
import importlib.util, hashlib
import numpy as np

HERE=Path(__file__).resolve().parents[1]/'authority_seed'
spec=importlib.util.spec_from_file_location('grid_seed',HERE/'grid_seed.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_authority_identity_chain():
    r=m.verify_authority()
    assert r['m2_model_seed_git_blob_sha1']=='43d5f2a79b8588e0844297dcf1c8ceb2df6b8ac0'
    assert r['source_frozen_inputs_sha256']=='8482d2854ab620c58bb1d7a7a45cf88eb71fd75081242263a9ef48927f0a282c'
    assert r['cp4_exact_weight_source_sha256']=='8ad5273551728a3608b5f8d43ea77f732aebeddc96bea767be0f79206fcc39eb'

def test_reconstructed_arrays_match_frozen_array_fingerprints():
    d=m.inputs()
    assert hashlib.sha256(d['C'].tobytes()).hexdigest()=='5952ccecafea867f83f1454bf8f338f494770fe0356c7e026eb7222b32067b96'
    assert hashlib.sha256(d['exponents'].tobytes()).hexdigest()=='9564bcdfab5fc900321ecc12441b420b723f02d2991e62b3886e40c759c998a5'
    assert hashlib.sha256(np.asarray(d['v']).tobytes()).hexdigest()=='918ad765b4ad0f17db43ad69b4df1292cd481eebabba8ef1e3770b5af8aae4ac'

def test_grid_shapes_for_m2_orders():
    for n in (160,192):
        d,t,W,gs,gw=m.grid(n,80)
        assert t.shape==(n,) and W.shape==(3,9,n,n)
        assert gs.shape==gw.shape==(80,)
        assert np.isfinite(t).all() and np.isfinite(W).all()
        assert d['exponents'].shape==(12,) and d['C'].shape==(9,9,9)
