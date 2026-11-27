"""PHYS39 C7B: global all-space source correction and arbitrary-r angular kernel."""
from fractions import Fraction as F
from pathlib import Path
import json, math

import mpmath as mp
import numpy as np
import pytest
from scipy.integrate import quad
from scipy.special import eval_legendre

from wu088_hh.phys33_source_global import (
    R,_jn_coefficients,jn_interval,factorial_tail,
    source_squared_certificate,improved_existing_broken_bound,
    improved_truncated_hminus1,
)
from wu088_hh.phys33_angular_kernel import (
    legendre_in_s2,power_exponential_moment,
    angular_multipole_element,angular_multipole_matrix,
)

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/"research/hh_phys36_20261015/results/C7_W4.json"
RESULTS=ROOT/"research/hh_phys39_20261015/results"


def test_closed_j2_reproduces_prior_exact_Ephi():
    from wu088_hh.phys33_coupled_source import exp_negative_bounds
    low,high=jn_interval(2)
    coeff=(3+6*R+4*R**2)/24
    a,b=exp_negative_bounds(2*R,192)
    assert low==coeff*a and high==coeff*b
    for n in (1,3,4,5,6):
        l,h=jn_interval(n)
        assert 0<l<=h<1


@pytest.mark.parametrize("n",[1,2,3,4,6,8])
def test_3d_exponential_moment_against_independent_scipy_numerical_integral(n):
    nr=float(R)
    def density(r):
        a=abs(r-nr);b=r+nr
        f=(1+n*a)*math.exp(-n*a)-(1+n*b)*math.exp(-n*b)
        return 2*r*math.exp(-2*r)/(n*n*nr)*f
    actual=quad(density,0,nr,epsabs=1e-12)[0]+quad(
        density,nr,35,epsabs=1e-12)[0]
    lo,hi=jn_interval(n)
    # This direct float quadrature is diagnostic, not an exact-endpoint witness.
    assert abs(actual-0.5*(float(lo)+float(hi)))<5e-13


def test_global_source_correction_32_term_rigorous_interval_and_numerical_match():
    r=source_squared_certificate(32,digits=15)
    assert r["squared_L2_lower"]=="0.061759400725986"
    assert r["squared_L2_upper"]=="0.061759400725987"
    assert r["norm_L2_upper"]=="0.248514387362155"
    assert float(r["factorial_tail_squared_bound"])<=1e-15
    # Independent SciPy integral over the original spectator distance.
    Rf=.7
    def inner(radius):
        a,b=abs(radius-Rf),radius+Rf
        inside=quad(lambda s:s*(-math.expm1(-math.exp(-s)))**2,
                    a,b,epsabs=1e-13,epsrel=1e-12)[0]
        return 2*radius*math.exp(-2*radius)/Rf*inside
    direct=quad(inner,0,Rf,epsabs=2e-12)[0]+quad(
        inner,Rf,24,epsabs=2e-12)[0]
    assert float(r["squared_L2_lower"])-5e-13<=direct<=float(
        r["squared_L2_upper"])+5e-13


def test_factorial_tail_and_accuracy_monotonically_improve():
    z=[source_squared_certificate(n,digits=15) for n in (8,16,32)]
    assert factorial_tail(32)<factorial_tail(16)<factorial_tail(8)
    widths=[float(s['squared_L2_upper'])-float(s['squared_L2_lower'])
            for s in z]
    assert widths[2]<widths[1]<widths[0]


def test_actual_frozen_parent_bound_improves_and_is_byte_locked():
    z=improved_existing_broken_bound(PARENT,32)
    assert z["input_sha256"]=="f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
    assert z["new_broken_bulk_bound"]=="2.516921964597611"
    assert F(z["new_broken_bulk_bound"])<F(z["previous_broken_bulk_bound"])
    assert z["admitted"]=="direct_allspace_two_centre_source"


def test_modified_parent_is_rejected(tmp_path):
    corrupted=tmp_path/"parent.json"
    corrupted.write_bytes(PARENT.read_bytes()+b" ")
    with pytest.raises(ValueError,match="SHA mismatch"):
        improved_existing_broken_bound(corrupted)
    with pytest.raises(ValueError):
        jn_interval(-1)
    with pytest.raises(ValueError):
        jn_interval(2,exp_terms=8)
    with pytest.raises(ValueError):
        _jn_coefficients(2)


@pytest.mark.parametrize("radius",[F(1,2),F(7,10),F(1),F(2)])
def test_spectator_angular_kernel_n0_is_exact_legendre_orthogonality(radius):
    a=angular_multipole_matrix(radius,0,lmax=5,digits=15)
    for l in range(6):
        for m in range(6):
            expected=F(1,2*l+1) if l==m else F(0)
            lo,hi=map(F,a["interval_matrix"][l][m])
            assert lo<=expected<=hi
            assert hi-lo<=F(2,10**15)


@pytest.mark.parametrize("radius,n",[(F(1,2),2),(F(7,10),2),
                                        (F(1),2),(F(2),2),(F(1),4)])
def test_generic_r_cusp_aware_angular_multipoles_symmetric_and_float_valid(radius,n):
    mat=angular_multipole_matrix(radius,n,lmax=5,digits=15)
    rv=float(radius);R0=float(R)
    for l in range(6):
        for m in range(6):
            lo,hi=map(float,mat['interval_matrix'][l][m])
            slo,shi=map(float,mat['interval_matrix'][m][l])
            assert lo==slo and hi==shi
            direct=quad(
               lambda x:0.5*eval_legendre(l,x)*eval_legendre(m,x)*
                        math.exp(-n*math.sqrt(rv*rv+R0*R0-2*rv*R0*x)),
               -1,1,epsabs=3e-12,epsrel=1e-10)[0]
            # Independent float quadrature may drift on r=R cusp,
            # but always remains within 5e-11 of exact enclosure.
            assert lo-5e-11 <= direct<=hi+5e-11


def test_generic_r_l2_coupling_is_positive_and_offdiagonal():
    mat=angular_multipole_matrix(F(1),2,lmax=5)
    a=np.array([[(float(x[0])+float(x[1]))/2 for x in row]
                for row in mat["interval_matrix"]])
    assert np.min(np.linalg.eigvalsh(a))>0
    assert a[1,2]>0.02
    for l in range(6):
        assert a[l,l]>0


def test_angular_matrix_negative_controls():
    for radius in [F(0),F(-1)]:
        with pytest.raises(ValueError):
            angular_multipole_matrix(radius,2,5)
    with pytest.raises(ValueError):
        angular_multipole_matrix(F(1),2,50)
    with pytest.raises(ValueError):
        power_exponential_moment(2,3,F(1),F(1))
    with pytest.raises(ValueError):
        legendre_in_s2(41,F(1))


INTERFACES=ROOT/"research/hh_phys38_20261015/results/INTERFACE_HMINUS1.json"


def test_upgraded_transformed_annulus_Hminus1_is_original_model_and_more_precise():
    z=improved_truncated_hminus1(PARENT,INTERFACES)
    assert z["annulus_Hminus1_transformed_D_upper"]=="2.516921964597791"
    assert z["source_input_sha256"]=="f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
    assert F(z["annulus_Hminus1_transformed_D_upper"]) >= (
        F(z["broken_bulk_L2_upper"])+F(z["five_interface_Djump_Hminus1_upper"]))
    assert F(z["annulus_Hminus1_transformed_D_upper"])<F("2.603747132326180")


def test_upgraded_Hminus1_refuses_modified_interface(tmp_path):
    p=tmp_path/"tampered_interface.json"
    p.write_bytes(INTERFACES.read_bytes()+b" ")
    with pytest.raises(ValueError,match="interface receipt SHA mismatch"):
        improved_truncated_hminus1(PARENT,p)


def test_archived_fixed_radius_n2_proof_is_reproducible():
    p=RESULTS/"ANGULAR_r1_1_n2.json"
    z=angular_multipole_matrix(F(1),2,5,digits=15)
    old=json.loads(p.read_text())
    for k in ("schema","radius_a0","power_of_E","lmax","interval_matrix","normalization"):
        assert z[k]==old[k]
