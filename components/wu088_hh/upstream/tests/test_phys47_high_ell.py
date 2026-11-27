"""Source-locked PHYS47 analytic geometry tests."""
from __future__ import annotations
from fractions import Fraction as F
from decimal import Decimal as D
from pathlib import Path
import copy, hashlib
import pytest, mpmath as mp
from wu088_hh.phys47_high_ell import ellipse,high_ell_transfer,scientific_up,rho_prefactor,SOURCE_SHA,R,B
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"

@pytest.fixture(scope="module")
def full():
    return high_ell_transfer(SOURCE)

def test_original_and_high_l_source(full):
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    assert full["original_frozen_source_SHA256"]==SOURCE_SHA
    assert len(full["candidate_rhos"])==25
    assert len(full["best_bounds"])==10
    v={row["N"]:row for row in full["best_bounds"]}
    assert v[20]["first_output_ell"]==41
    assert v[20]["optimal_candidate_rho"]==18
    assert D(v[20]["radial_original_plus2S_P20_to_Q_high_ell_L1_upper"])<D("3.01e-37")
    assert v[40]["first_output_ell"]==61
    assert D(v[40]["radial_original_plus2S_P20_to_Q_high_ell_L1_upper"])<D("7.81e-64")

@pytest.mark.parametrize("rho",[4,10,14,18,20,24,28])
def test_exact_ellipse_geometry(rho):
    g=ellipse(rho)
    assert 0<g["branch_deviation"]<1
    assert g["sqrt_lower"]**2<=1-g["branch_deviation"]
    assert R<g["shift"]<B
    assert g["shift"]*(1+g["sqrt_lower"])>=2*R*g["chi"]+R*R/B
