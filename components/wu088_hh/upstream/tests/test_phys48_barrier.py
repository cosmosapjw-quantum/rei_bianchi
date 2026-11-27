"""PHYS48 original Coulomb turning-point and positive-action interval tests."""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import copy
import mpmath as mp
import pytest

from wu088_hh.phys48_barrier import (
    B,K2,SOURCE_SHA,barrier,turning_bracket,sqrt_floor,sqrt_ceil,
    mesh,adaptive_action,source_barrier_actions,
)

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"


@pytest.fixture(scope="module")
def analytic():
    return source_barrier_actions(SOURCE,n=256,grading="adaptive")


def test_original_source_rational_turn_and_barrier_identity(analytic):
    assert analytic["original_source_sha256"]==SOURCE_SHA
    assert analytic["sqrt_fixed_decimal_digits"]==18
    assert len(analytic["action_enclosures"])==11
    for x in analytic["action_enclosures"]:
        ell=x["ell"]
        lo,hi=turning_bracket(ell)
        if ell>0:
            assert barrier(lo,ell)>=0
            assert barrier(hi,ell)<=0
            assert lo<=hi
        assert x["action_lower"] and x["action_upper"]
        assert F(x["action_lower"])<=F(x["action_upper"])


@pytest.mark.parametrize("ell",[14,15,20,21,28,41,61,120])
def test_mpmath_75digit_independent_barrier_quadrature_within_certificate(analytic,ell):
    r=next(x for x in analytic["action_enclosures"] if x["ell"]==ell)
    with mp.workdps(75):
        k=mp.mpf(7)/10
        L=ell*(ell+1)
        rt=(mp.sqrt(1+k*k*L)-1)/(k*k)
        if rt<=20:
            exact=mp.mpf(0)
        else:
            width=rt-20
            def integrand(x):
                rad=20+width*(2*x-x*x)
                vv=L/rad**2-2/rad-k*k
                return 2*width*(1-x)*mp.sqrt(max(mp.mpf(0),vv))
            exact=mp.quad(integrand,[0,mp.mpf('.5'),mp.mpf('.9'),1])
        assert mp.mpf(r["action_lower"])<=exact<=mp.mpf(r["action_upper"])


@pytest.mark.parametrize("ell",[21,41,80,120])
def test_adaptive_progress_exact_nesting(ell):
    p=source_barrier_actions(SOURCE,ells=(ell,),n=32,grading="adaptive")
    q=source_barrier_actions(SOURCE,ells=(ell,),n=64,grading="adaptive")
    a=p["action_enclosures"][0]
    b=q["action_enclosures"][0]
    assert F(a["action_lower"])<=F(b["action_lower"])
    assert F(b["action_upper"])<=F(a["action_upper"])
    assert F(b["interval_width"])<=F(a["interval_width"])


def test_coarse_turning_sliver_corrected():
    d=source_barrier_actions(SOURCE,ells=(15,21,41),n=128)
    rows={x["ell"]:x for x in d["action_enclosures"]}
    assert F(rows[15]["action_lower"])>0
    for ell in (15,21,41):
        lo,hi=turning_bracket(ell)
        last=F(rows[ell]["integration_last"])
        assert lo>=last
        assert 0<=lo-last<=F(1,10**8)


def test_science_identity_between_cpu_worker_counts(analytic):
    other=source_barrier_actions(SOURCE,n=256,grading="adaptive",workers=2)
    a=copy.deepcopy(analytic)
    for d in (a,other):
        d.pop("workers")
        d.pop("elapsed_s")
    assert a==other


def test_fail_closed_wrong_original_bytes_and_bad_config(tmp_path):
    f=tmp_path/"mutated_source.npz"
    f.write_bytes(SOURCE.read_bytes()[:-1])
    with pytest.raises(ValueError,match="original"):
        source_barrier_actions(f)
    for kwargs in ({"ells":()},{"ells":(21,21)},{"ells":(-1,)},
                   {"n":3},{"grading":"fake"},{"digits":7},{"workers":7}):
        with pytest.raises(ValueError):
            source_barrier_actions(SOURCE,**kwargs)
    with pytest.raises(ValueError):sqrt_floor(F(-1))
    with pytest.raises(ValueError):sqrt_ceil(F(-1))
    with pytest.raises(ValueError):barrier(F(0),21)
