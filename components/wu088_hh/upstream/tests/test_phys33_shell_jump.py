"""Interface residual jump is not the distributional interface defect."""
from fractions import Fraction as F
from pathlib import Path
import json

from wu088_hh.phys33_shell_jump import jump_certificate

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"
CERT=ROOT/"research/hh_phys37_20261015/results/JUMP_N96.json"


def test_certified_strong_residual_jump_does_not_imply_a_delta():
    result=json.loads(CERT.read_text())
    l,h=map(F,result["strong_residual_jump_l2_interval"])
    assert F("0.01047")<l<=h<F("0.01049")
    assert F(result["radial_field_value_jump_l2_upper"])<F(1,10**13)
    assert F(result["radial_first_derivative_jump_l2_upper"])<F(1,10**13)
    assert "no unproved distributional admission" in result["meaning"]


def test_fresh_lower_degree_jump_is_consistent_with_N96():
    reference=json.loads(CERT.read_text())
    probe=jump_certificate(SOURCE,n=64,digits=12)
    lo,hi=map(F,probe["strong_residual_jump_l2_interval"])
    rlo,rhi=map(F,reference["strong_residual_jump_l2_interval"])
    assert max(lo,rlo) <= min(hi,rhi)
    assert probe["input_sha256"]==reference["input_sha256"]
