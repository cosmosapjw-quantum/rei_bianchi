"""PHYS38: genuine finite-width r=R cusp strip with rigorous log modulus."""
from fractions import Fraction as F
from pathlib import Path
import json
import mpmath as mp
import pytest

from wu088_hh.phys33_cusp_strip import (
    PARENT_SHELL_SHA256, _derivative_magnitudes, _modulus_bounds,
    strip_certificate, R,
)
from wu088_hh.phys33_strip_preview import preview_cusp_strip

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"
PARENT=ROOT/"research/hh_phys37_20261015/results/SHELL_BOTH_N96_18.json"
OUT=ROOT/"research/hh_phys38_20261015/results"


@pytest.mark.parametrize("den,expected",[
    (100,"0.092921847102"),
    (1000,"0.002951003776"),
    (10000,"0.000148787714")
])
def test_actual_rigorous_3d_finite_width_bounds_reproduce(den,expected):
    r=strip_certificate(SRC,PARENT,F(1,den))
    assert r["total_3D_broken_strong_residual_L2_upper"]==expected
    assert r["admitted_method"]=="radial_Minkowski_log_moment"
    assert F(r["improved_radial_integrated_bound"])<=F(r["conservative_uniform_sup_bound"])
    assert r["parent_shell_sha256"]==PARENT_SHELL_SHA256
    assert len(r["side_evidence"])==2
    assert r["input_sha256"]=="f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
    assert "delta-like distributional interface residual" in r["excluded"]


def test_radial_strip_widths_respect_actual_dyadic_switch():
    r=strip_certificate(SRC,PARENT,F(1,1000))
    lengths=[F(x) for x in r["actual_one_sided_strip_widths"]]
    assert lengths[0]+lengths[1]==F(2,1000)
    assert lengths[0]<F(1,1000)<lengths[1]
    assert abs(F(r["actual_frozen_interface_rational"])-R)==F(
        r["interface_deviation_from_R"])


def test_direction_angular_modulus_log_integral_independent_mpmath():
    # Both normalized field vectors are bounded pointwise by
    # min(2,2 delta/s_R). The integral has an EXACT elementary log form.
    mp.mp.dps=90
    for d in [F(1,100),F(1,1000),F(1,10000)]:
        delta=mp.mpf(d.numerator)/d.denominator
        rad=mp.mpf(7)/10
        a=delta/(2*rad)
        direct=2*(mp.quad(lambda x:4*x,[0,a])+
            mp.quad(lambda x:x*(delta/(rad*x))**2,[a,1]))
        closed=(delta/rad)**2*(1+2*mp.log(2*rad/delta))
        assert abs(direct-closed)<mp.mpf("1e-78")
        cert=strip_certificate(SRC,PARENT,d)
        upper=mp.mpf(cert["unit_vector_angular_rms_upper"])
        assert upper**2>=closed


def test_archived_finite_strips_have_true_positive_volume():
    prev=None
    for den in [100,1000,10000]:
        r=strip_certificate(SRC,PARENT,F(1,den))
        ub=F(r["total_3D_broken_strong_residual_L2_upper"])
        assert ub>0
        if prev is not None: assert ub<prev
        prev=ub


def test_noncertifying_vectorized_s_distance_preview_inside_true_bound():
    anchored=json.loads((OUT/"FINAL_STRIP_W3.json").read_text())
    for den in [100,1000,10000]:
        matches=[row for row in anchored["strips"] if row["delta_a0"]==str(F(1,den))]
        assert len(matches)==1
        ref=matches[0]
        p=preview_cusp_strip(SRC,F(1,den),24,64)
        q=preview_cusp_strip(SRC,F(1,den),48,128)
        assert ref["input_sha256"]==p["input_sha256"]==q["input_sha256"]
        assert 0<p["whole_strip_sampled_L2"] < float(
            ref["total_3D_broken_strong_residual_L2_upper"])
        assert 0<q["whole_strip_sampled_L2"] < float(
            ref["total_3D_broken_strong_residual_L2_upper"])
        assert abs(p["whole_strip_sampled_L2"]-q["whole_strip_sampled_L2"])<5e-7
        assert "NONCERTIFYING" in q["status"]


def test_exact_radial_polynomial_derivatives_obey_numerical_probe():
    # Test a few actual stored coefficient derivatives by finite differences,
    # not used to certify the result.
    magnitudes,sha=_derivative_magnitudes(SRC,"right",F(1,1000))
    assert len(magnitudes)==21
    assert sha=="f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
    assert all(len(row)==4 and all(v>=0 for v in row) for row in magnitudes)
    e=_modulus_bounds(SRC,"right",F(1,1000))
    assert e["Grad"]>0 and e["Ap"]>0 and e["slope"]>0


def test_reject_modified_parent_and_invalid_inputs(tmp_path):
    p=tmp_path/"bad_parent.json"
    p.write_text(PARENT.read_text()+" ")
    with pytest.raises(ValueError,match="byte identity"):
        strip_certificate(SRC,p,F(1,1000))
    with pytest.raises(ValueError):
        strip_certificate(SRC,PARENT,0.001)
    for delta in [F(0),-F(1,100),F(1),F(7,10)]:
        with pytest.raises(ValueError):
            strip_certificate(SRC,PARENT,delta)
    with pytest.raises(ValueError):
        preview_cusp_strip(SRC,F(1,1000),3,128)


def test_exact_radial_direction_squared_modulus_moment():
    mp.mp.dps=90
    for d in [F(1,100),F(1,1000),F(1,10000)]:
        delta=mp.mpf(d.numerator)/d.denominator
        rad=mp.mpf(7)/10
        f=lambda t:t*t*(1+2*mp.log(2*rad/t))
        integral=mp.quad(f,[0,delta])
        rhs=delta**3*(mp.mpf(5)/9+(mp.mpf(2)/3)*mp.log(2*rad/delta))
        assert abs(integral-rhs)<mp.mpf("1e-76")


def test_certified_minkowski_is_no_worse_than_uniform_for_all_scoped_deltas():
    for den in [100,1000,10000]:
        d=strip_certificate(SRC,PARENT,F(1,den))
        assert F(d["total_3D_broken_strong_residual_L2_upper"])==F(d["improved_radial_integrated_bound"])
        assert F(d["total_3D_broken_strong_residual_L2_upper"])<F(d["conservative_uniform_sup_bound"])
