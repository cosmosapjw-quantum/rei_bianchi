"""PHYS42 original two-centre signed (r,mu) interval proof regressions."""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path

import mpmath as mp
import pytest

from wu088_hh.phys42_joint_interval import (
    I,bernstein_range,_s_interval,_e_q_U_source,angular_ranges,
    _angular_polynomials,prepare_radial_panel,certify_cell,joint_strip,
)
from wu088_hh.phys33_residual import value
from wu088_hh.phys33_general_strip_preview import preview_general_strip

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"


def test_interval_arithmetic_corner_extrema():
    x=I(F(-2),F(3)); y=I(F(-4),F(-1))
    assert x*y==I(F(-12),F(8))
    assert x/y==I(F(-3),F(2))
    assert (x+F(1))==I(F(-1),F(4))
    assert -y==I(F(1),F(4))
    with pytest.raises(ZeroDivisionError):
        x/I(F(-1),F(1))


@pytest.mark.parametrize("rlo,rhi,mlo,mhi",[
    (F(99,100),F(101,100),F(-1),F(1)),
    (F(1,2),F(3,5),F(1,3),F(2,3)),
    (F(1,1000),F(2,1000),F(-3,4),F(-1,4)),
    (F(5),F(6),F(-9,10),F(-1,2)),
])
def test_s_interval_exact_rational_covers_all_grid_points(rlo,rhi,mlo,mhi):
    z=_s_interval(rlo,rhi,mlo,mhi)
    assert z.lo>=0 and z.hi>0
    for i in range(7):
        r=rlo+(rhi-rlo)*F(i,6)
        for j in range(7):
            mu=mlo+(mhi-mlo)*F(j,6)
            ss=r*r+F(49,100)-F(7,5)*r*mu
            assert z.lo*z.lo<=ss<=z.hi*z.hi


def test_angular_polynomial_signed_Bernstein_envelopes():
    ps,ts=_angular_polynomials()
    for ma,mb in [(F(-1),F(-7,8)),(F(-1,7),F(1,8)),(F(9,10),F(1))]:
        pb,tb=angular_ranges(ma,mb)
        for l in (0,1,5,11,20):
            for m in (ma,(ma+mb)/2,mb):
                assert pb[l].lo<=value(ps[l],m)<=pb[l].hi
                assert tb[l].lo<=value(ts[l],m)<=tb[l].hi


@pytest.mark.parametrize("rlo,rhi,mlo,mhi",[
    (F(99,100),F(101,100),F(0),F(1,4)),
    (F(1,2),F(51,100),F(7,8),F(15,16)),
    (F(5),F(51,10),F(-1),F(0)),
])
def test_coulomb_U_screen_monotonic_rational_enclosures(rlo,rhi,mlo,mhi):
    mp.mp.dps=70
    ri=I(rlo,rhi)
    si=_s_interval(rlo,rhi,mlo,mhi)
    E,U,src,corr=_e_q_U_source(ri,si)
    for r in [rlo,(rlo+rhi)/2,rhi]:
        for mu in [mlo,(mlo+mhi)/2,mhi]:
            s=mp.sqrt((mp.mpf(r.numerator)/r.denominator)**2+
                      mp.mpf('0.49')-mp.mpf('1.4')*
                      (mp.mpf(r.numerator)/r.denominator)*
                      mp.mpf(mu.numerator)/mu.denominator)
            e=mp.exp(-s)
            q=-mp.expm1(-s)/s
            uu=e*q-e/2-3*e**2/2
            ss=mp.mpf(298)/100*mp.exp(-mp.mpf(r.numerator)/r.denominator)
            cc=ss*(1-mp.exp(-e))
            for iv,actual in ((E,e),(U,uu),(src,ss),(corr,cc)):
                assert mp.mpf(iv.lo.numerator)/iv.lo.denominator <= actual+mp.mpf("1e-60")
                assert actual <= mp.mpf(iv.hi.numerator)/iv.hi.denominator+mp.mpf("1e-60")


def test_joint_covers_original_frozen_strip_and_float_original_operator():
    z=joint_strip(SRC,F(1),F(1,1000),radial_bins=2,mu_bins=8)
    assert z["source_sha256"]=="f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
    assert z["panel"]==2 and z["cells"]==16
    assert F(z["full_3D_broken_L2_upper"])>0
    ind=preview_general_strip(SRC,F(1),F(1,1000),nr=24,ns=64)
    assert ind["status"].startswith("NONCERTIFYING")
    assert ind["sampled_volume_L2"] < float(z["full_3D_broken_L2_upper"])


def test_bad_input_rejects_cusp_and_unsupported_panels():
    with pytest.raises(ValueError,match="cusp"):
        joint_strip(SRC,F(7,10),F(1,1000),1,8)
    with pytest.raises(ValueError):
        joint_strip(SRC,F(1),F(0),1,8)
    with pytest.raises(ValueError):
        joint_strip(SRC,F(1),F(1,1000),1,8,workers=7)
    with pytest.raises(ValueError,match="exactly one"):
        joint_strip(SRC,F(2),F(1,1000),1,8)
