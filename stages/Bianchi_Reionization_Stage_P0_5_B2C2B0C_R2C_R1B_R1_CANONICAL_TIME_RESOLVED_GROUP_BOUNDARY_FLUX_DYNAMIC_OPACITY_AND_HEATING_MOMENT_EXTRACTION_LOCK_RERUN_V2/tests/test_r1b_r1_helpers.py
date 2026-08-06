from __future__ import annotations
import importlib.util
from pathlib import Path
import numpy as np

SCRIPT=Path(__file__).parents[1]/"analysis/replay_canonical_bdf_dense.py"
spec=importlib.util.spec_from_file_location("replay_helpers",SCRIPT)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def test_clenshaw_curtis_weights_are_stable_and_integrate_polynomials():
    for n in (9,17,33,65):
        x,w=mod.clenshaw_curtis_nodes_weights(n)
        assert np.all(np.diff(x)>0)
        assert np.all(w>=0)
        assert abs(w.sum()-1.0)<2e-15
        assert np.linalg.norm(w,1)<1.00000000000001
        for degree in range(0,min(n,12)):
            assert abs(np.dot(w,x**degree)-1/(degree+1))<2e-13

def test_relative_scale_never_divides_by_zero():
    assert mod.relative(0.0,0.0)==0.0
    assert np.isfinite(mod.relative(1e-300,0.0))

def test_canonical_source_exposes_thermal_helper_via_direct_module_import():
    import sys
    source=Path(__file__).parents[1]/'inputs/canonical_b2c2a_r1_src'
    sys.path.insert(0,str(source))
    import primary_exact_zero_model
    assert callable(primary_exact_zero_model.thermal_components)
