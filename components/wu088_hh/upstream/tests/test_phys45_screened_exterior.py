"""PHYS45 verified source-locked m0 two-centre exterior angular matrix tests."""
from __future__ import annotations
from decimal import Decimal
from fractions import Fraction as Q
from pathlib import Path
import json
import mpmath as mp
import pytest
import numpy as np

from wu088_hh.phys45_screened_exterior import (
    FROZEN_ID,R,_matrix_pairs,exterior_tail_envelopes,
    screened_coupling_matrix,
)
from wu088_hh.phys45_screened_preview import (
    preview_matrix,vectorized_vs_scalar,
)

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"


@pytest.fixture(scope="module")
def matrix():
    return screened_coupling_matrix(SOURCE,Q(20),20,320,24,1)


def test_original_21_modes_full_symmetric_matrix_source_locked(matrix):
    a=matrix
    assert a["original_source_sha256"]==FROZEN_ID
    assert a["evaluated_distinct_pairs"]==231
    assert a["lmax"]==20
    v=a["certified_V_matrix_interval"]
    assert len(v)==21 and all(len(r)==21 for r in v)
    assert all(v[l][m]==v[m][l] for l in range(21) for m in range(21))
    assert all(Q(v[l][l][0])>0 for l in range(21))
    assert all(Q(v[l][l][1])<=Q(a["finite_angular_compression_upper_eigen_bound"])
               for l in range(21))
    assert a["tails"]["Green_resolvent_norm"] is None
    assert "full noncentral screened outgoing Coulomb DtN and l>20 propagated wave" in a["NOT_CERTIFIED"]


@pytest.mark.parametrize("l,m",[(0,0),(0,1),(1,1),(5,5),(10,11),(20,20)])
def test_independent_high_precision_direct_mu_quadrature_inside_certified_brackets(matrix,l,m):
    """Independent Legendre(mu) quadrature, not an interval proof."""
    a=matrix["certified_V_matrix_interval"][l][m]
    with mp.workdps(70):
        r=mp.mpf(20)
        Rm=mp.mpf(7)/10
        def f(mu):
            ss=mp.sqrt(r*r+Rm*Rm-2*r*Rm*mu)
            return mp.legendre(l,mu)*mp.legendre(m,mu)*(1+1/ss)*mp.exp(-2*ss)
        v=mp.sqrt((2*l+1)*(2*m+1))*mp.quad(f,[-1,-mp.mpf('0.5'),0,mp.mpf('0.5'),1])/2
        low=mp.mpf(a[0]);high=mp.mpf(a[1])
        assert low<=v<=high


def test_positive_outer_operator_and_tighter_convex_angular_remainder(matrix):
    tails=matrix["tails"]
    whole=Q(tails["full_screened_plus_2V_radial_L1_upper"])
    off=Q(tails["full_plus_2V_off_central_diagonal_radial_L1_upper"])
    old=Q(tails["older_crude_lipschitz_tail_bound"])
    assert 0<off<whole<old
    assert off==Q(tails["ell_gt20_off_central_source_L1_operator_upper"])
    assert Q(tails["V_minus_central_diagonal_operator_pointwise_bound_at_B"])<whole
    assert Q(matrix["finite_angular_compression_lower_eigen_bound"])>0
    assert Q(matrix["finite_angular_compression_upper_eigen_bound"])>=whole
    assert Q(matrix["gershgorin_operator_norm_upper"])>=Q(matrix["all_angular_operator_norm_upper"])


def test_direct_float64_vectorized_512_symmetric_and_psd(matrix):
    p=preview_matrix(n=512,lmax=20)
    assert p["status"]=="NONCERTIFYING_FLOAT64_GAUSS"
    assert p["min_eigen_float"]>0
    assert p["max_symmetric_deviation_float"]<1e-31
    v=np.array(p["matrix_float64"])
    for l in range(21):
        for m in range(21):
            low,hi=map(float,matrix["certified_V_matrix_interval"][l][m])
            assert low<=v[l,m]<=hi


def test_exterior_input_validation_and_wrong_source_rejection(tmp_path):
    invalid=tmp_path/"spoofed.npz"
    invalid.write_bytes(SOURCE.read_bytes()[:-10])
    with pytest.raises(ValueError,match="source"):
        screened_coupling_matrix(invalid)
    for args in [
        {"radius":Q(7,10)},
        {"lmax":21},
        {"terms":192},
        {"terms":640},
        {"workers":5},
        {"digits":8},
    ]:
        with pytest.raises(ValueError):
            screened_coupling_matrix(SOURCE,**args)
    with pytest.raises(ValueError):
        exterior_tail_envelopes(Q(7,10))


def test_vectorization_science_parity_in_noncertifying_preview():
    a=vectorized_vs_scalar(n=128,lmax=10,iterations=3)
    assert a["max_matrix_abs_difference"]<1e-30
    assert a["status"].startswith("NONCERTIFYING")
    assert min(a["float64_eigenvalues"])>0
