import pytest

from bass_he.spectral import find_exceptional_point
from bass_he.sturm_geometry import contour_geometry


def test_public_constructor_rejects_simple_fold_of_wrong_advertised_pair():
    with pytest.raises(RuntimeError, match='pair membership'):
        find_exceptional_point(
            (1,0,0),(2,0,0),
            1.2125718090356707+1.363814370435508j,
            depth=64,
        )


def test_constructor_attaches_pair_membership_certificate_for_source_control():
    ep=find_exceptional_point(
        (1,0,0),(2,1,0),
        1.2125718090356707+1.363814370435508j,
        depth=64,
    )
    cert=ep['pair_membership']
    assert cert['passed'] is True
    assert cert['max_scaled_matching_error'] < cert['tolerance']
    assert sorted(cert['permutation']) == [0,1]
    g=contour_geometry(ep,0.0,panels=8)
    assert g['delta'] > 0


def test_sturm_geometry_fails_closed_if_pair_membership_certificate_is_missing():
    ep=find_exceptional_point(
        (1,0,0),(2,1,0),
        1.2125718090356707+1.363814370435508j,
        depth=64,
    )
    ep=dict(ep); ep.pop('pair_membership')
    with pytest.raises(ValueError, match='pair membership'):
        contour_geometry(ep,0.0,panels=8)
