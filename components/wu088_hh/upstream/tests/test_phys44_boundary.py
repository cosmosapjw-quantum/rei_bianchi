"""PHYS44: central Coulomb reference, exact origin/tail and original frozen trace."""
from __future__ import annotations

from fractions import Fraction as Q
from pathlib import Path
from decimal import Decimal
import json
import mpmath as mp
import pytest

from wu088_hh.phys44_boundary import (
    R,K,B,ORIG_SOURCE,regular_coulomb_origin,
    _exp_positive_tail,_exp_n_weighted_tail,
    _coulomb_piece,outward_coulomb_reference,boundary_reference,
)

ROOT=Path(__file__).resolve().parents[1]
FROZEN=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"
R0=Q(7378697629483821,73786976294838206464)


def test_frobenius_own_coefficients_residuals():
    ell=3;nmax=12
    a=[Q(1)]
    for n in range(1,nmax+1):
        a.append(-(2*a[n-1]+(K*K*a[n-2] if n>=2 else 0))/Q(n*(n+2*ell+1)))
    assert a[1]==-Q(1,ell+1)
    assert all(Q(n*(n+2*ell+1))*a[n]+2*a[n-1]+
               (K*K*a[n-2] if n>=2 else 0)==0 for n in range(1,nmax+1))
    assert all(abs(a[n])<=Q(2**n,__import__("math").factorial(n))
               for n in range(nmax+1))


@pytest.mark.parametrize("ell",[0,1,5,12,20])
def test_exact_regular_origin_brackets_contain_true_CoulombF_log_derivative(ell):
    a=regular_coulomb_origin(ell,R0,degree=14,digits=20)
    lo,hi=[Q(s) for s in a["reference_Coulomb_u_prime_over_u_per_a0_bracket"]]
    assert lo>0 and hi>=lo
    with mp.workdps(70):
        kk=mp.mpf(7)/10
        eta=-1/kk
        rho=kk*mp.mpf(R0.numerator)/R0.denominator
        f=mp.coulombf(ell,eta,rho)
        fn=mp.coulombf(ell+1,eta,rho)
        fp=((ell+1)/rho+eta/(ell+1))*f - mp.sqrt(1+(eta/(ell+1))**2)*fn
        z=kk*fp/f
        assert mp.mpf(lo.numerator)/lo.denominator <= z
        assert z <= mp.mpf(hi.numerator)/hi.denominator


@pytest.mark.parametrize("ell,ref_re,ref_im",[
    (0,"0.0021085016770721272267764605259492337","0.76799235802943506126924997255739292"),
    (1,"0.0019147274197442189230580319372675876","0.76474712999553541801916598799250391"),
    (4,"0.000015334115792523061037551539822978268","0.73492251295120085178910001560063235"),
    (20,"-0.61556379959797260127770768955617485","0.0016328469991963856173118323850662941"),
])
def test_independent_Wolfram_CoulombH1_reference_values(ell,ref_re,ref_im):
    z=_coulomb_piece(([ell],60))[0]
    with mp.workdps(58):
        rr=mp.mpf(z["outgoing_z_re_per_a0"])
        ii=mp.mpf(z["outgoing_z_im_per_a0"])
        assert abs(rr-mp.mpf(ref_re))<mp.mpf("4e-35")
        assert abs(ii-mp.mpf(ref_im))<mp.mpf("4e-35")
        assert ii>0


def test_positive_exponential_tail_majorizes_direct_exp():
    for z in [Q(0),Q(1,5000),Q(1,2),Q(3)]:
        for n in [5,10,16]:
            if z>=n+2:continue
            ub=_exp_positive_tail(z,n)
            p=sum((z**k/Q(__import__("math").factorial(k)) for k in range(n+1)),Q(0))
            with mp.workdps(65):
                actual=mp.exp(mp.mpf(z.numerator)/z.denominator) - mp.mpf(p.numerator)/p.denominator
                assert actual<=mp.mpf(ub.numerator)/ub.denominator + mp.mpf("1e-60")
    assert _exp_n_weighted_tail(Q(1,1000),16)>0


@pytest.fixture(scope="module")
def actual_original():
    return boundary_reference(FROZEN,dps=50,workers=1,origin_degree=16)


def test_original_1386_frozen_modes_outgoing_and_lift_scopes(actual_original):
    d=actual_original
    assert d["frozen_source_sha256"]==ORIG_SOURCE
    assert d["frozen_original_complex_mode_values"]==1386
    assert d["origin_radius_exact_binary64"]==str(R0)
    assert len(d["origin_regular_Coulomb_reference"])==21
    assert len(d["outer_Coulomb_reference_outgoing"])==21
    assert Decimal(d["certified_screened_h_potential_sup_r_ge20_upper"])<Decimal("2e-17")
    assert Decimal(d["certified_F_minus_one_sup_r_ge20_upper"])<Decimal("1e-8")
    assert Decimal(d["certified_eta_minus_y_surface_L2_upper"]) < Decimal(d["certified_xi_minus_y_surface_L2_upper"])
    assert Decimal(d["certified_radial_derivative_eta_minus_y_surface_L2_upper"]) < Decimal(d["certified_radial_derivative_xi_minus_y_surface_L2_upper"])
    assert d["certified_xi_angular_l_gt20_leakage_surface_L2_upper"]==d["certified_eta_minus_y_surface_L2_upper"]
    assert d["certified_radial_derivative_xi_angular_l_gt20_leakage_surface_L2_upper"]==d["certified_radial_derivative_eta_minus_y_surface_L2_upper"]
    assert Decimal(d["outer_reduced_u20_minus_zc_u20_L2_diagnostic"])>0
    assert "full physical two-centre screened outgoing DtN" in d["NOT_CERTIFIED"]


def test_reject_invalid_source_and_limits(tmp_path):
    src=tmp_path/"bad_frozen.npz"
    src.write_bytes(FROZEN.read_bytes()[:-4])
    with pytest.raises(ValueError,match="identity"):
        boundary_reference(src,dps=50)
    with pytest.raises(ValueError):
        regular_coulomb_origin(0,Q(0))
    with pytest.raises(ValueError):
        regular_coulomb_origin(-1,R0)
    with pytest.raises(ValueError):
        regular_coulomb_origin(2,Q(1,2))
    with pytest.raises(ValueError):
        outward_coulomb_reference(dps=20)
    with pytest.raises(ValueError):
        outward_coulomb_reference(workers=8)
