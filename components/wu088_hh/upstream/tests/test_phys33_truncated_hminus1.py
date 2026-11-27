"""Whole truncated annulus H^-1 direct sum, provenance and negative control."""
from fractions import Fraction as F
from pathlib import Path
import json
import pytest

from wu088_hh.phys33_truncated_hminus1 import truncated_distribution_certificate

ROOT=Path(__file__).resolve().parents[1]
BULK=ROOT/"research/hh_phys36_20261015/results/C7_W4.json"
INTERFACES=ROOT/"research/hh_phys38_20261015/results/INTERFACE_HMINUS1.json"
RESULT=ROOT/"research/hh_phys38_20261015/results/TRUNCATED_HMINUS1.json"


def test_same_physics_exact_composition_of_original_c7a_and_all_interfaces():
    r=truncated_distribution_certificate(BULK,INTERFACES)
    assert r['truncated_full_transformed_PDE_Hminus1_upper']=="2.603747132326180"
    assert r['test_space']=="(H_0^1(annulus), dimensionless a0 gradient) dual"
    assert F(r['bulk_L2_upper'])+F(r['five_interface_Ddelta_Hminus1_upper'])<=F(
        r['truncated_full_transformed_PDE_Hminus1_upper'])
    expected=json.loads(RESULT.read_text())
    assert r==expected
    assert not any('full scattering certified' in s for s in r['not_claimed'])


def test_refuse_modified_or_mismatched_parent(tmp_path):
    p=tmp_path/"parent.json"
    p.write_bytes(BULK.read_bytes()+b" ")
    with pytest.raises(ValueError,match="SHA256 mismatch"):
        truncated_distribution_certificate(p,INTERFACES)
    wrong=json.loads(INTERFACES.read_text())
    wrong['input_sha256']="a different model"
    y=tmp_path/"interfaces.json";y.write_text(json.dumps(wrong))
    with pytest.raises(ValueError,match="identities"):
        truncated_distribution_certificate(BULK,y)


def test_discontinuous_frozen_field_refused_before_hminus1(tmp_path):
    wrong=json.loads(INTERFACES.read_text())
    wrong['interfaces'][2]['field_value_jump_exact_zero']=False
    y=tmp_path/"field-discontinuous.json"
    y.write_text(json.dumps(wrong))
    with pytest.raises(ValueError,match="delta-prime"):
        truncated_distribution_certificate(BULK,y)
