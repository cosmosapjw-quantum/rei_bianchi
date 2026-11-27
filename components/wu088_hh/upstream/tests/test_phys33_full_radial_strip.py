"""PHYS40 exact finite noncoalescing strip and independent numeric tests."""
from fractions import Fraction as F
from pathlib import Path
import json
import pytest
from wu088_hh.phys33_full_radial_strip import local_strip_certificate
from wu088_hh.phys33_general_strip_preview import preview_general_strip

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"
DATA=ROOT/"research/hh_phys40_20261015/results"

@pytest.mark.parametrize("rho,delta,expected",[
 (F(1,2),F(1,100),"0.106268687735"),
 (F(1,2),F(1,1000),"0.003100658335"),
 (F(1,2),F(1,10000),"0.000097694613"),
 (F(1),F(1,100),"0.073268786787"),
 (F(1),F(1,1000),"0.002232635336"),
 (F(1),F(1,10000),"0.000071621782")
])
def test_original_frozen_strip_certification(rho,delta,expected):
    anchor=DATA/f"SHELL_Q64_r{rho.numerator}_{rho.denominator}_auto.json"
    actual=local_strip_certificate(SRC,anchor,delta)
    assert actual["full_3D_broken_strong_residual_L2_upper"]==expected
    assert actual["original_source_sha256"]=="f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
    assert actual["actual_frozen_panel"] in (1,2)

@pytest.mark.parametrize("rho,delta",[
 (F(1,2),F(1,1000)),(F(1,2),F(1,10000)),
 (F(1),F(1,1000)),(F(1),F(1,10000))
])
def test_independent_float_full_screened_3d_coupling_is_diagnostic(rho,delta):
    anchor=DATA/f"SHELL_Q64_r{rho.numerator}_{rho.denominator}_auto.json"
    cert=local_strip_certificate(SRC,anchor,delta)
    preview=preview_general_strip(SRC,rho,delta,48,128)
    assert preview["input_sha256"]==cert["original_source_sha256"]
    assert preview["sampled_volume_L2"]<float(cert["full_3D_broken_strong_residual_L2_upper"])
    assert preview["sampled_volume_L2"]>0
    assert preview["status"].startswith("NONCERTIFYING")

def test_reject_cusp_intersection_invalid_width_or_mismatched_input(tmp_path):
    anchor=DATA/"SHELL_Q64_r1_1_auto.json"
    with pytest.raises(ValueError,match="may not intersect"):
        local_strip_certificate(SRC,anchor,F(2,5))
    with pytest.raises(ValueError):
        local_strip_certificate(SRC,anchor,F(0))
    with pytest.raises(ValueError):
        local_strip_certificate(SRC,anchor,0.0001)
    d=json.loads(anchor.read_text())
    d["source_sha256"]="invalid"
    bad=tmp_path/"bad.json"
    bad.write_text(json.dumps(d))
    with pytest.raises(ValueError,match="frozen identity"):
        local_strip_certificate(SRC,bad,F(1,100))
    with pytest.raises(ValueError):
        preview_general_strip(SRC,F(1),F(1,10000),nr=5)
