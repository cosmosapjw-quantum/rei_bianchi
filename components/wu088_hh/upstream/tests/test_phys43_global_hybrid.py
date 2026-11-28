"""PHYS43: original all-radial-domain hybrid, cusp log patch and H^-1 sheets."""
from __future__ import annotations

from fractions import Fraction as F
from pathlib import Path
import json

import pytest

from wu088_hh.phys33_residual import load_frozen,dyadic,ceil_sqrt_fixed
from wu088_hh.phys33_panel_bernstein import upper_exp_minus
from wu088_hh.phys42_joint_interval import (
    prepare_radial_panel,_radial_ranges,certify_cell,
)
from wu088_hh.phys43_global_hybrid import (
    original_panel_ranges,positive_shell_square,global_hybrid,
    cusp_graded_cuts,FROZEN_ID
)

ROOT=Path(__file__).resolve().parents[1]
FROZEN=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"
CUSP=ROOT/"research/hh_phys37_20261015/results/SHELL_BOTH_N96_18.json"
JUMPS=ROOT/"research/hh_phys38_20261015/results/INTERFACE_HMINUS1.json"


@pytest.mark.parametrize("delta",[F(1,100),F(1,1000),F(1,10000)])
def test_original_every_panel_and_actual_binary64_cusp_seam(delta):
    panels,info=original_panel_ranges(FROZEN,delta)
    actual,_,digest=load_frozen(FROZEN,True)
    assert digest==FROZEN_ID
    assert len(panels)==6
    assert all(panels[j][0]==j for j in range(6))
    assert F(info["actual_cusp_panel_seam"])==dyadic(actual[1,-1])
    cover=[(F(a),F(b)) for a,b,_ in info["exact_cover"]]
    assert len(cover)==7
    assert cover[0][0]==dyadic(actual[0,0])
    assert cover[-1][1]==dyadic(actual[-1,-1])
    assert all(b==c for (_,b),(c,_) in zip(cover,cover[1:]))
    assert sum((b-a for a,b in cover),F(0))==cover[-1][1]-cover[0][0]


@pytest.mark.parametrize("near_right", [False,True])
def test_cusp_grading_preserves_every_original_cut_and_exact_cover(near_right):
    low,high=F(71,100),F(2)
    if near_right:
        low,high=F(1,10),F(69,100)
    base=[low+(high-low)*F(i,8) for i in range(9)]
    cuts=cusp_graded_cuts(low,high,F(1,100),near_right,8)
    assert cuts[0]==low and cuts[-1]==high
    assert set(base).issubset(set(cuts))
    assert len(cuts)>len(base)
    assert all(a<b for a,b in zip(cuts,cuts[1:]))
    assert sum((b-a for a,b in zip(cuts,cuts[1:])),F(0))==high-low
    if near_right:
        assert cuts[-1]-cuts[-2] <= F(1,100)
    else:
        assert cuts[1]-cuts[0] <= F(1,100)


def test_positive_and_signed_on_one_same_exact_non_cusp_tile():
    pre=prepare_radial_panel(FROZEN,2)
    a,b=F(1),F(101,100)
    r=_radial_ranges(pre,a,b)
    sq,shell=positive_shell_square(r,a,b)
    assert sq>=0 and shell>=0
    mus=[-F(1),-F(1,2),F(0),F(1,2),F(1)]
    signed=sum((certify_cell(pre,a,b,l,h,r)["_sq_exact"]
                for l,h in zip(mus,mus[1:])),F(0))
    assert signed>=0
    chosen=min(F(sq),F(signed))
    assert chosen<=sq and chosen<=signed
    assert F(ceil_sqrt_fixed(chosen,12))**2>=chosen


@pytest.fixture(scope="module")
def small_global():
    return global_hybrid(FROZEN,CUSP,JUMPS,delta=F(1,100),
                         pieces=(1,1,1,1,1,1),mu_bins=4,
                         signed_panels=(1,2),workers=1,digits=12)


def test_full_six_original_panels_and_complete_Hminus1_evidence(small_global):
    z=small_global
    assert z["source_sha256"]==FROZEN_ID
    assert len(z["radial_panels"])==6
    assert z["status"].startswith("CERTIFIED_TRUNCATED")
    assert F(z["broken_strong_L2_upper"])>0
    assert F(z["complete_truncated_annulus_Hminus1_upper"])>=F(z["broken_strong_L2_upper"])
    assert F(z["complete_truncated_annulus_Hminus1_upper"])>=F(z["cusp_log_strip_upper"])
    assert z["not_certified"] and "continuous low Schur inverse" in z["not_certified"]
    assert z["tighter_than_PHYS39"] == (
        F(z["complete_truncated_annulus_Hminus1_upper"]) <
        F(z["previous_accepted_PHYS39_Hminus1_upper"]))
    assert F(z["regular_sq_exact"]) + F(z["cusp_log_strip_upper"])**2 <= (
        F(z["broken_strong_L2_upper"])**2)
    assert (F(z["broken_strong_L2_upper"]) +
            F(z["five_interface_distribution_Hminus1_upper"]) <=
            F(z["complete_truncated_annulus_Hminus1_upper"]))
    for panel in z["radial_panels"]:
        cells=panel["cells"]
        assert sum((F(x["chosen_sq"]) for x in cells),F(0))==F(panel["chosen_sq_exact"])
        assert all(F(cell["chosen_sq"])<=F(cell["positive_sq"]) for cell in cells)
        assert all(F(x["radial"][1])==F(y["radial"][0]) for x,y in zip(cells,cells[1:]))
        for cell in cells:
            if cell["chosen"]=="signed":
                assert F(cell["chosen_sq"])<=F(cell["signed_sq"])
            else:
                assert cell["chosen_sq"]==cell["positive_sq"]
        assert cells[0]["radial"][0]==panel["clip_range"][0]
        assert cells[-1]["radial"][1]==panel["clip_range"][1]


def test_fail_closed_missing_physical_jumps(tmp_path):
    p=tmp_path/"wrong_jump.json"
    d=json.loads(JUMPS.read_text())
    d["input_sha256"]="deadbeef"
    p.write_text(json.dumps(d))
    with pytest.raises(ValueError,match="interface certificate SHA"):
        global_hybrid(FROZEN,CUSP,p,delta=F(1,100),
                      pieces=(1,1,1,1,1,1),mu_bins=4,
                      signed_panels=(),workers=1)


@pytest.mark.parametrize("bad_delta",[F(0),F(1,10),F(9,10)])
def test_reject_outside_cusp_delta(bad_delta):
    with pytest.raises(ValueError):
        original_panel_ranges(FROZEN,bad_delta)


def test_bad_config_rejected_before_science_compute():
    with pytest.raises(ValueError):
        global_hybrid(FROZEN,CUSP,JUMPS,pieces=(1,2),mu_bins=4)
    with pytest.raises(ValueError):
        global_hybrid(FROZEN,CUSP,JUMPS,pieces=(1,1,1,1,1,1),mu_bins=3)
    with pytest.raises(ValueError):
        global_hybrid(FROZEN,CUSP,JUMPS,pieces=(1,1,1,1,1,1),
                      mu_bins=4, signed_panels=(10,))
