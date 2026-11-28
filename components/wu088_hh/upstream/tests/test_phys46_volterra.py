"""PHYS46 source-locked finite-21-channel Coulomb Volterra math and code."""
from __future__ import annotations
import copy
import hashlib
from fractions import Fraction as F
from pathlib import Path

import mpmath as mp
import pytest

from wu088_hh.phys46_volterra import (
    B,R,K,C,L_CAP,FROZEN_SHA256,
    exp_positive_rational_upper,q0_of_r,_energy_candidate,
    finite21_volterra_certificate,
)

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"


def test_exact_source_immutability_and_best_12_candidates():
    cert=finite21_volterra_certificate(SOURCE)
    assert cert["source_sha256"]==FROZEN_SHA256
    assert cert["angular_channel_count"]==21
    assert cert["T_energy_patch_a0"]==31
    assert cert["M_state_bound_integer"]==28
    assert cert["evaluated_patch_count"]==12
    assert cert["outgoing_Jost_B_invertible"] is True
    assert F(cert["selected_q_strict_upper"]) < F(1,100000)
    assert F(cert["selected_alpha_Jost_relative_error_upper"]) < F(1,100000)
    assert F(cert["selected_B_matrix_inverse_factor_upper"]) < F(100001,100000)
    assert cert["NOT_CERTIFIED"] and "infinite angular hierarchy" in cert["NOT_CERTIFIED"][0]
    vals=[F(x["q_upper"]) for x in cert["all_candidates_sorted_original_order"]]
    assert vals.index(min(vals))==2
    assert cert["selected_q_strict_upper"]==cert["all_candidates_sorted_original_order"][2]["q_upper"]


def test_exact_source_physical_patch_invariant_and_positive_rational_enclosure():
    z=_energy_candidate((31,72,24))
    assert F(z["energy_qmin_exact"])==F(11289,96100)
    assert F(z["qprime_total_variation_upper_exact"])==F(482,961)
    assert F(z["energy_exponent_exact"])==F(48200,11289)
    assert F(z["physical_radial_exponential1_exact"])==F(702,35)
    assert F(z["physical_radial_exponential2_exact"])==F(303,5)
    assert z["M_integer"]==28
    assert F(z["energy_state_squared_limit_upper"])<28**2
    assert z["strict_contraction"] and z["outgoing_boundary_Jost_invertible"]
    q=F(z["q_exact"])
    alpha=q/(1-q)
    assert F(z["Jost_boundary_relative_correction_upper"])>=alpha
    assert F(z["boundary_inverse_factor_upper"])>=1/(1-alpha)


@pytest.mark.parametrize("z,n",[(F(0),72),(F(48200,11289),72),
                                (F(1,100),48),(F(30,7),72)])
def test_exact_rational_positive_exponential_encloses_mpmath(z,n):
    up=exp_positive_rational_upper(z,n)
    with mp.workdps(100):
        truth=mp.exp(mp.mpf(z.numerator)/z.denominator)
        assert truth<=mp.mpf(up.numerator)/up.denominator
    if z:
        assert up>1


def test_green_ode_and_outgoing_wronskian_and_jump():
    with mp.workdps(57):
        k=mp.mpf(7)/10;eta=-1/k
        r=mp.mpf(20);t=mp.mpf('23.5')
        for ell in [0,5,15,20]:
            hp=lambda x:mp.coulombg(ell,eta,k*x)+1j*mp.coulombf(ell,eta,k*x)
            hm=lambda x:mp.conj(hp(x))
            hpt=hp(t);hmt=hm(t)
            G=lambda x:(hp(x)*hmt-hm(x)*hpt)/(2j*k)
            q=lambda x:k*k+2/x-ell*(ell+1)/(x*x)
            assert abs(mp.diff(G,r,2)+q(r)*G(r))<mp.mpf("1e-48")
            assert abs(G(t))<mp.mpf("1e-48")
            assert abs(mp.diff(G,t)-1)<mp.mpf("1e-48")
            assert abs(mp.im(mp.conj(hpt)*mp.diff(hp,t))-k)<mp.mpf("1e-48")
            assert mp.im(mp.conj(hpt)*mp.diff(hp,t))>0


@pytest.mark.parametrize("ell",[0,1,5,14,15,20])
def test_independent_true_CoulombH1_value_within_universal_rigorously_derived_weight(ell):
    with mp.workdps(58):
        k=mp.mpf(7)/10;eta=-1/k
        c=mp.mpf(59)/70
        tmatch=31
        M=28
        for r in [mp.mpf(20),mp.mpf(24),mp.mpf(29),mp.mpf(31),
                  mp.mpf(40),mp.mpf(80)]:
            H=lambda x:mp.coulombg(ell,eta,k*x)+1j*mp.coulombf(ell,eta,k*x)
            h=H(r)
            hp=mp.diff(H,r)
            state=mp.sqrt(abs(h)**2+abs(hp/k)**2)
            w=M*mp.exp(c*max(mp.mpf(0),tmatch-r))
            assert state<=w


def test_worker_parallel_source_math_identity():
    a=finite21_volterra_certificate(SOURCE,workers=1)
    b=finite21_volterra_certificate(SOURCE,workers=2)
    x=copy.deepcopy(a);y=copy.deepcopy(b)
    for d in (x,y):
        d.pop("elapsed_s")
        d.pop("workers")
    assert x==y


def test_invalid_geometry_and_original_byte_source_fail_closed(tmp_path):
    b=tmp_path/"mutated.npz"
    b.write_bytes(SOURCE.read_bytes()[:-1])
    with pytest.raises(ValueError,match="immutable frozen"):
        finite21_volterra_certificate(b)
    for cfg in ({"candidate_T":()}, {"candidate_T":(31,31)},
                {"candidate_T":(28,)},{"workers":7},
                {"terms":10},{"digits":25}):
        with pytest.raises(ValueError):
            finite21_volterra_certificate(SOURCE,**cfg)
    with pytest.raises(ValueError):
        q0_of_r(21,F(20))
    with pytest.raises(ValueError):
        exp_positive_rational_upper(F(-1),72)
    with pytest.raises(ValueError):
        exp_positive_rational_upper(F(3),1)
