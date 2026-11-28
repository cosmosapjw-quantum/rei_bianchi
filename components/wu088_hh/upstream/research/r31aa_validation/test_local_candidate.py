from pathlib import Path
import importlib.util
import numpy as np
import pytest

HERE=Path(__file__).resolve().parent
INPUT=HERE/'EXISTING_METRIC_INPUTS.npz'


def api():
    spec=importlib.util.spec_from_file_location('r31aa',HERE/'local_candidate.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def test_piecewise_cubic_linear_matches_fit_nodes_and_metric_identity():
    m=api(); d=m.replay(INPUT)
    assert d['max_O_node_error_2norm'] < 3e-14
    assert d['max_dotO_node_error_2norm'] < 3e-14
    assert d['max_D_col_node_error_2norm'] < 3e-14
    assert d['max_D_row_node_error_2norm'] < 3e-14
    assert d['max_metric_identity_grid_2norm'] < 5e-14


def test_locality_right_interval_is_independent_of_z0():
    m=api(); rng=np.random.default_rng(1)
    vals=[rng.normal(size=(2,1))+1j*rng.normal(size=(2,1)) for _ in range(3)]
    ders=[rng.normal(size=(2,1))+1j*rng.normal(size=(2,1)) for _ in range(3)]
    ks=[rng.normal(size=(2,1))+1j*rng.normal(size=(2,1)) for _ in range(3)]
    a=m.local_candidate(vals,ders,ks,8.,.75)
    vals2=[100*vals[0],vals[1],vals[2]];ders2=[100*ders[0],ders[1],ders[2]];ks2=[100*ks[0],ks[1],ks[2]]
    b=m.local_candidate(vals2,ders2,ks2,8.,.75)
    for x,y in zip(a,b):
        assert np.allclose(x,y,rtol=0,atol=1e-13)


def test_global_z3_diagnosis_connection_error_bounds():
    m=api()
    b=m.connection_error_bounds(0.07262393465956431,0.3073893478614785,0.3192667733603847)
    assert b['lower'] == pytest.approx(0.2829548060306026)
    assert b['upper'] == pytest.approx(0.313328060109316)
    assert b['lower_over_dotO'] == pytest.approx(3.89616463714058)
    assert b['connection_sector_dominates'] is True


def test_invalid_inputs_rejected():
    m=api()
    with pytest.raises(ValueError):m.connection_error_bounds(-1,2,3)
    with pytest.raises(ValueError):m.local_candidate([1,2],[1,2],[1,2],1,.5)
    with pytest.raises(ValueError):m.local_candidate([1,2,3],[1,2,3],[1,2,3],0,.5)


def test_claim_ceiling():
    m=api();d=m.replay(INPUT)
    assert d['z3_status']=='CONSUMED_DIAGNOSTIC_NOT_FUTURE_VALIDATION'
    assert d['z1_status']=='NEW_INDEPENDENT_VALIDATION_REQUIRED'
