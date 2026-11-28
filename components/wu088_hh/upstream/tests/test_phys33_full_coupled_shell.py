"""PHYS40 R5/C7B verified all-coupled angular residual at arbitrary r."""
from fractions import Fraction as F
from pathlib import Path
import json

import pytest

from wu088_hh.phys33_full_coupled_shell import (
    _center_exp,_exact_rational_log_integral,
    _series_bundle,full_coupled_angular_shell,
)
from wu088_hh.phys33_full_shell_preview import preview_fixed_r
from wu088_hh.phys33_coupled_source import exp_negative_bounds

ROOT=Path(__file__).resolve().parents[1]
FROZEN=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"
EVIDENCE=ROOT/"research/hh_phys40_20261015/results"


@pytest.mark.parametrize("x",[F(0),F(3,10),F(7,5),F(20)])
def test_quantized_exponential_center_remains_mathematically_outward(x):
    c,err=_center_exp(x,192)
    lo,hi=exp_negative_bounds(x,192)
    assert c-err<=lo<=hi<=c+err
    assert c.denominator<=10**48
    if x==0:assert c==1 and err==0


def test_all_three_screened_taylor_remainders_are_positive_and_vanish_at_cusp():
    z=_series_bundle(F(0),F(7,5),64,192)
    assert z["E"][0]==z["E2"][0]==1
    assert z["epsilon_E"]>0 and z["epsilon_E2"]>0
    assert 0<z["epsilon_E_over_s"]<z["epsilon_E"]
    assert z["epsilon_g"]>0


def test_weighted_rational_log_exact_manufactured_cases_and_cusp_refusal():
    for a,w in [(F(0),F(7,5)),(F(3,10),F(7,5)),(F(1),F(7,5))]:
        # numerator N(s)=s, so N²/s=s, ∫s ds exact
        poly=[a*a,2*a,F(1)]
        lo,hi=_exact_rational_log_integral(poly,a,w,128)
        expected=a*w+w*w/2
        assert lo<=expected<=hi
        assert hi-lo<F(1,10**20)
    with pytest.raises(ArithmeticError,match="not zero"):
        _exact_rational_log_integral([F(1),F(3)],F(0),F(1),128)


@pytest.mark.parametrize("radius,side,label",[
    (F(7,10),"left","r7_10_left"),
    (F(7,10),"right","r7_10_right"),
    (F(1,2),None,"r1_2_auto"),
    (F(1),None,"r1_1_auto"),
    (F(2),None,"r2_1_auto"),
])
def test_actual_full_screened_frozen_coupled_angular_certificate(radius,side,label):
    expected=json.loads((EVIDENCE/f"SHELL_Q64_{label}.json").read_text())
    current=full_coupled_angular_shell(FROZEN,radius,side,order=64,exp_terms=192,digits=12)
    for k in ("source_sha256","physical_r_a0","physical_s_interval","chosen_panel",
              "angular_norm_L2_lower","angular_norm_L2_upper",
              "rounding_and_Taylor_error_upper","degree_numerator"):
        assert current[k]==expected[k],k
    assert F(current["angular_norm_L2_upper"])-F(current["angular_norm_L2_lower"])<F(1,10**8)


def test_independent_genuine_full_PDE_float_s_coordinate_gauss_matches_directed_enclosure():
    for radius,side,label in [
        (F(7,10),"right","r7_10_right"),
        (F(7,10),"left","r7_10_left"),
        (F(1,2),None,"r1_2_auto"),
        (F(1),None,"r1_1_auto"),
        (F(2),None,"r2_1_auto")
    ]:
        cert=json.loads((EVIDENCE/f"SHELL_Q64_{label}.json").read_text())
        q=preview_fixed_r(FROZEN,radius,side,160)
        assert q["input_sha256"]==cert["source_sha256"]
        assert q["status"].startswith("NONCERTIFYING")
        assert F(cert["angular_norm_L2_lower"])-F(1,10**12)<=F(str(q["sampled_angular_L2"]))
        assert F(str(q["sampled_angular_L2"]))<=F(cert["angular_norm_L2_upper"])+F(1,10**12)


def test_original_PHYS37_cusp_shell_science_agrees_but_is_independent():
    parent=json.loads((ROOT/"research/hh_phys37_20261015/results/SHELL_BOTH_N96_18.json").read_text())
    for record in parent["results"]:
        side=record["side"]
        first=json.loads((EVIDENCE/f"SHELL_Q64_r7_10_{side}.json").read_text())
        assert abs(float(record["certified_true_shell_L2_upper"])-
                   float(first["angular_norm_L2_upper"]))<2e-8


def test_wrong_or_tampered_source_and_incorrect_inputs_are_refused(tmp_path):
    bad=tmp_path/"mismatched.npz"
    bad.write_bytes(FROZEN.read_bytes()+b" ")
    with pytest.raises(ValueError,match="identity"):
        full_coupled_angular_shell(bad,F(1),order=64)
    with pytest.raises(ValueError):
        full_coupled_angular_shell(FROZEN,F(0),order=64)
    with pytest.raises(ValueError):
        full_coupled_angular_shell(FROZEN,F(21),order=64)
    with pytest.raises(ValueError):
        full_coupled_angular_shell(FROZEN,F(1),order=15)
