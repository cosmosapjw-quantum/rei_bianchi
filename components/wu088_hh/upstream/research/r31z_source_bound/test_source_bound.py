from pathlib import Path
import importlib.util, os
import numpy as np
import pytest
from scipy.linalg import norm

HERE=Path(__file__).resolve().parent
INPUT=Path(os.environ.get('WU088_R31Z_INPUT',HERE/'EXISTING_METRIC_INPUTS.npz'))

def api():
    spec=importlib.util.spec_from_file_location('r31z',HERE/'source_bound.py')
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def test_quintic_scalar_constraints():
    m=api(); T=3.7
    vals=[1.2,-.7,2.3]; ders=[.4,-.2,.8]
    for s,y,d in [(0,vals[0],ders[0]),(.5,vals[1],ders[1]),(1,vals[2],ders[2])]:
        p,dp=m.quintic_hermite(vals,ders,T,s)
        assert p==pytest.approx(y,abs=2e-14)
        assert dp==pytest.approx(d,abs=2e-14)

def test_quadratic_K_hits_nodes():
    m=api(); ks=[np.array([[1+2j]]),np.array([[-3j]]),np.array([[4-1j]])]
    for s,k in [(0,ks[0]),(.5,ks[1]),(1,ks[2])]:
        assert np.allclose(m.quadratic_three_nodes(ks,s),k,rtol=0,atol=2e-14)

def test_structure_preserving_identity_random():
    m=api();rng=np.random.default_rng(31)
    vals=[rng.normal(size=(3,2))+1j*rng.normal(size=(3,2)) for _ in range(3)]
    ders=[rng.normal(size=(3,2))+1j*rng.normal(size=(3,2)) for _ in range(3)]
    ks=[rng.normal(size=(3,2))+1j*rng.normal(size=(3,2)) for _ in range(3)]
    for s in np.linspace(0,1,17):
        o,dot=m.quintic_hermite(vals,ders,2.5,s)
        k=m.quadratic_three_nodes(ks,s)
        dc=dot/2+k; dr=(dot/2-k).conj().T
        assert norm(dot-dc-dr.conj().T,2)<3e-14

def test_curvature_lower_bounds_scalar_quadratic():
    m=api(); # f(t)=t^2 on [0,T], exact sup |f''|=2
    T=4.; f0=0.; f1=T*T; fm=(T/2)**2; d0=0.; d1=2*T
    b=m.curvature_lower_bounds(f0,fm,f1,d0,d1,T)
    assert b['endpoint0'] == pytest.approx(2.)
    assert b['endpoint1'] == pytest.approx(2.)
    assert b['midpoint'] == pytest.approx(2.)
    assert b['combined'] == pytest.approx(2.)

def test_bad_interval_rejected():
    m=api()
    with pytest.raises(ValueError): m.quintic_hermite([1,2,3],[1,2,3],0,.5)
    with pytest.raises(ValueError): m.curvature_lower_bounds(1,2,3,4,5,True)

def test_stored_affine_model_rejected_source_bound():
    m=api();d=m.replay(INPUT)
    a=d['source_bound_affine_rejection']
    assert a['midpoint_O_chord_error_2norm']==pytest.approx(1.1608909908205545,rel=1e-12)
    assert a['secant_minus_dotO_z0_2norm']==pytest.approx(0.5495713714162325,rel=1e-12)
    assert a['secant_minus_dotO_z2_2norm']==pytest.approx(0.2910484768338663,rel=1e-12)
    assert a['secant_minus_dotO_z4_2norm']==pytest.approx(0.33156843070467085,rel=1e-12)
    assert a['affine_O_compatible_with_source_nodes'] is False
    assert a['common_frozen_frame_authority']=='RECOVERED_SOURCE_AND_ARRAY_BOUND'

def test_stored_curvature_certificate():
    m=api();d=m.replay(INPUT);b=d['curvature_lower_bound']
    assert b['combined_per_ta2']==pytest.approx(0.1228983778317182,rel=1e-12)
    assert b['combined_per_a02']==pytest.approx(0.6143870602870756,rel=1e-12)
    assert b['certified_interval_arithmetic'] is False

def test_stored_quintic_reproduces_all_three_nodes():
    m=api();d=m.replay(INPUT);q=d['quintic_mixed_candidate']
    assert q['max_O_node_error_2norm']<3e-14
    assert q['max_dotO_node_error_2norm']<3e-14
    assert q['max_D_col_node_error_2norm']<3e-14
    assert q['max_D_row_node_error_2norm']<3e-14
    assert q['max_metric_compatibility_residual_grid_2norm']<5e-14
    assert q['validated_between_nodes'] is False

def test_two_endpoint_cubic_is_not_enough_for_direct_midpoint():
    m=api();d=m.replay(INPUT);h=d['two_endpoint_cubic_hermite']
    assert h['midpoint_O_error_2norm']==pytest.approx(0.7456046027649951,rel=1e-12)
    assert h['midpoint_dotO_error_2norm']==pytest.approx(0.15168609198173066,rel=1e-12)
    assert h['passes_direct_midpoint'] is False

def test_node_metric_compatibility_is_independently_present():
    m=api();d=m.replay(INPUT);n=d['node_metric_compatibility']
    assert max(n.values())<2e-13

def test_source_immutability_and_claim_ceiling():
    m=api();d=m.replay(INPUT)
    assert d['input_unchanged'] is True
    assert d['physical_source_affineness']=='NOT_ESTABLISHED'
    assert d['physical_source_nonaffineness_claimed'] is False
    assert d['full_cell_bound']==False
    assert d['production_admitted']==False
    assert d['native_evaluations']==0 and d['HH_trajectory_runs']==0
