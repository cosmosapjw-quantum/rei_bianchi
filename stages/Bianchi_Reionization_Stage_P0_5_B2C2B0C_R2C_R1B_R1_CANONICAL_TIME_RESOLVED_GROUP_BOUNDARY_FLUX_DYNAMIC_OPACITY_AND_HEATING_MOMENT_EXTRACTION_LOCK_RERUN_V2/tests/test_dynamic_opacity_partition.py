from __future__ import annotations
import importlib.util
from pathlib import Path
import numpy as np
SCRIPT=Path(__file__).parents[1]/'analysis/build_dynamic_opacity_partition.py'
spec=importlib.util.spec_from_file_location('partition',SCRIPT); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def test_shared_rn_lift_closes_both_moments_with_one_density():
    h=np.array([1.,2.,0.,4.]); q,k,j,phi=m.shared_rn_lift(h,7.0,21.0)
    assert np.all(q>=0); assert q[2]==0
    assert abs(q.sum()-1)<1e-15; assert abs(k.sum()-7)<1e-14; assert abs(j.sum()-21)<1e-14
    assert np.allclose(j[k>0]/k[k>0],phi)

def test_zero_support_rejects_nonzero_target():
    import pytest
    with pytest.raises(ValueError): m.shared_rn_lift(np.zeros(3),1.0,0.0)

def test_tv_is_bounded():
    assert 0<=m.tv([1,0],[0,1])<=1
