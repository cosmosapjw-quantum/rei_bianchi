"""Fast NumPy batched preview, deliberately NON-CERTIFYING."""
import json
from fractions import Fraction as Q
from pathlib import Path

import numpy as np
import pytest

from wu088_hh.phys33_preview import preview_components

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"


def test_vectorized_batch_preview_matches_rational_moments_with_finite_roundoff():
    ref=json.loads((ROOT/"research/hh_phys35_20261015/results/FINAL_SCREEN8_SAFE_W4.json").read_text())
    a=preview_components(SOURCE,quadrature_nodes=64)
    b=preview_components(SOURCE,quadrature_nodes=160)
    for key,cert in [('coulomb_diagonal','coulomb_diagonal'),
                     ('state_gradient','state_gradient'),('state','state')]:
        # Float preview is NOT an interval enclosure, so use a diagnostic discrepancy.
        assert abs(a["norms_sampled"][key]-float(ref["norm_upper"][cert]))<1e-9
        assert abs(b["norms_sampled"][key]-float(ref["norm_upper"][cert]))<1e-9
    assert abs(a["norms_sampled"]["coulomb_diagonal"]-b["norms_sampled"]["coulomb_diagonal"])<1e-10
    assert len(a["panels"])==6
    assert b["status"].endswith("NOT_CERTIFIED")
    assert a["input_sha256"]==b["input_sha256"]==ref["input_sha256"]


def test_vectorized_hotspot_screened_preview_is_not_promoted_to_certificate():
    r=preview_components(SOURCE,quadrature_nodes=96)
    parent=json.loads((ROOT/"research/hh_phys35_20261015/results/FINAL_SCREEN8_SAFE_W4.json").read_text())
    assert 0<r["norms_sampled"]["screened_broken_bulk_triangle"]<float(parent["norm_upper"]["broken_transformed_bulk_residual"])
    assert r["norms_sampled"]["screened_gradient"]<=r["norms_sampled"]["state_gradient"]
    with pytest.raises(ValueError):
        preview_components(SOURCE,quadrature_nodes=3)
    with pytest.raises(ValueError):
        preview_components(SOURCE,quadrature_nodes=1025)
