"""Integration gates for the explicit Sturm anchor plus unchanged complex solver."""
import importlib.util
import math
import pytest
from bass_he.spectral import find_exceptional_point


def api():
    assert importlib.util.find_spec('bass_he.sturm_geometry') is not None, 'DR11E geometry adapter missing'
    from bass_he.sturm_geometry import contour_geometry
    return contour_geometry


@pytest.fixture(scope='module')
def eps():
    return {
      'q':find_exceptional_point((3,1,0),(4,2,0),7.9283658479841215+3.2285957034060395j,depth=160),
      's':find_exceptional_point((3,2,0),(4,2,0),1.9861101965857686+1.3649585042669394j,depth=160),
      'control':find_exceptional_point((1,0,0),(2,1,0),1.2125718090356707+1.363814370435508j,depth=160)
    }


def test_adapter_available():
    assert callable(api())


def test_q_action_not_silently_zero_from_collapsed_anchors(eps):
    r=api()(eps['q'],0.,panels=64)
    assert abs(r['delta']-.0921731875237374)<1e-7
    assert r['real_anchor']['distinct']
    assert r['minimum_normalized_sheet_gap']>1e-6


@pytest.mark.parametrize('branch,frac',[('s',.5),('q',.25)])
def test_formerly_blocked_rho_anchor_reaches_finite_action(eps,branch,frac):
    r=api()(eps[branch],frac*eps[branch]['R'].real,panels=32)
    assert math.isfinite(r['delta']) and r['delta']>0
    assert r['max_spectral_residual']<5e-9
    assert r['minimum_normalized_sheet_gap']>1e-6


def test_source_control_action_preserved(eps):
    r=api()(eps['control'],0.,panels=64)
    assert abs(r['delta']-1.42615)/1.42615<1e-4
    assert abs(r['delta']-1.4261134534642972)<1e-7
