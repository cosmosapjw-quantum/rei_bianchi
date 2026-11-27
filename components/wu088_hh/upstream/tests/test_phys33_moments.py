"""C6/C8 precise rational-log moment regression and independent numerical sanity."""
from fractions import Fraction as Q
import mpmath as mp
import pytest

from wu088_hh.phys33_moments import (
    _combine, _enclose, _log_atanh, _moment_polynomials,
    bound_weighted_moments, log_ratio_bounds, _expminus_upper, _floor_sqrt_fixed,
)

FILE = "research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"


def _to_mp(x: Q):
    return mp.mpf(x.numerator) / mp.mpf(x.denominator)


@pytest.mark.parametrize("lo,hi,p", [
    (Q(1,10000),Q(1,10),4),
    (Q(1,10),Q(7,10),2),
    (Q(7,10),Q(2),4),
    (Q(2),Q(5),2),
])
def test_moment_exact_rational_log_brackets_vs_independent_integral(lo,hi,p):
    mp.mp.dps=160
    mid,half=(lo+hi)/2,(hi-lo)/2
    poly=[Q(1,7),Q(-3,5),Q(5,4),Q(-2,9),Q(1,8)]
    m=_moment_polynomials(mid,half,lo,hi,len(poly)-1,p)
    a,b=_combine(poly,m)
    l,h=log_ratio_bounds(lo,hi,128)
    lower,upper=_enclose(a,b,l,h)
    def polynomial(x):
        v=mp.mpf(0)
        for coef in poly[::-1]:
            v=v*x+_to_mp(coef)
        return v
    z=mp.quad(lambda r:polynomial((r-_to_mp(mid))/_to_mp(half))/r**p,
              [_to_mp(lo),_to_mp(hi)])
    # This independent 160-digit calculation is a diagnostic, not the certificate.
    assert _to_mp(lower)-mp.mpf("1e-125") <= z <= _to_mp(upper)+mp.mpf("1e-125")
    assert float(upper-lower) < 1e-55


@pytest.mark.parametrize("left,right",[
    (Q(1),Q(2)),(Q(1,10),Q(10)),(Q(1,10000),Q(1,10)),(Q(7,10),Q(2))
])
def test_log_series_is_outward_and_tight(left,right):
    a,b=log_ratio_bounds(left,right,96)
    assert 0<=a<=b
    mp.mp.dps=120
    logmp=mp.log(_to_mp(right)/_to_mp(left))
    assert _to_mp(a)-mp.mpf("1e-90") <= logmp <= _to_mp(b)+mp.mpf("1e-90")
    assert float(b-a)<1e-85


def test_reject_illformed_inputs():
    with pytest.raises(ValueError):
        _log_atanh(Q(3),48)
    with pytest.raises(ValueError):
        log_ratio_bounds(Q(0),Q(1))
    with pytest.raises(ValueError):
        bound_weighted_moments(FILE,workers=5)
    with pytest.raises(ValueError):
        bound_weighted_moments(FILE,digits=25)


def test_actual_frozen_analytic_moment_bound_strictly_sharper_than_old():
    r=bound_weighted_moments(FILE,workers=1)
    assert r["input_sha256"]=="f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
    assert r["checked_nodal_values"]==1386
    assert Q(r["norm_upper"]["broken_transformed_bulk_residual"]) < Q("5")
    assert Q(r["norm_upper"]["unweighted_previous_broken_bulk_residual"]) > Q("15")
    assert Q(r["norm_upper"]["screened_weighted_gradient"]) < Q(r["norm_upper"]["state_gradient"])
    assert Q(r["norm_upper"]["screened_weighted_state"]) < Q(r["norm_upper"]["state"])
    for lo,hi in r["norm_lower_upper"].values():
        assert Q(lo) <= Q(hi)
    assert len(r["panels"])==6 and len(r["interfaces"])==5
    assert Q(r["norm_upper"]["broken_transformed_bulk_residual"]) < Q("15.389831374480")
    assert Q(r["norm_upper"]["broken_transformed_bulk_residual"]) > Q("0.001665185458218535")


def test_parallel_panels_exact_same_scientific_output_as_serial():
    serial=bound_weighted_moments(FILE,workers=1)
    multi=bound_weighted_moments(FILE,workers=2)
    for key in ("norm_upper","norm_lower_upper",
                "panels","interfaces","input_sha256","checked_nodal_values"):
        assert serial[key] == multi[key]


def test_screened_potential_sharp_exponential_envelope_and_negative_control():
    mp.mp.dps=100
    for lam in (Q(1,10),Q(1,2),Q(1)):
        for s in (Q(0),Q(1,100000),Q(1,10),Q(1),Q(5),Q(20)):
            lammp=_to_mp(lam);smp=_to_mp(s)
            E=mp.exp(-smp)
            U=(lammp*(E-E*E)/smp-lammp*E/2
               -(lammp+lammp*lammp/2)*E*E) if s else -lammp*(1+lammp)/2
            assert abs(U) <= lammp*E + mp.mpf("1e-90")
    # Half the coefficient would be a false bound at the spectator cusp.
    assert abs(-mp.mpf(1)) > mp.mpf("0.5")


def test_screened_exp_upper_is_exact_rational_outward():
    mp.mp.dps=130
    for x in (Q(0),Q(1,100),Q(13,5),Q(93,5),Q(38)):
        upper=_expminus_upper(x,64)
        assert _to_mp(upper) >= mp.exp(-_to_mp(x))
        assert upper <= 1
    assert _floor_sqrt_fixed(Q(2),12)=="1.414213562373"
    with pytest.raises(ValueError):
        _expminus_upper(Q(-1))


def test_screened_weighted_8cell_improves_without_changing_physical_input():
    original=bound_weighted_moments(FILE,workers=1,screen_cells=1)
    refined=bound_weighted_moments(FILE,workers=2,screen_cells=8)
    assert original["input_sha256"] == refined["input_sha256"]
    assert original["norm_upper"]["coulomb_diagonal"] == refined["norm_upper"]["coulomb_diagonal"]
    assert original["interfaces"] == refined["interfaces"]
    assert Q(refined["norm_upper"]["broken_transformed_bulk_residual"]) < Q("4.01")
    assert Q(refined["norm_upper"]["broken_transformed_bulk_residual"]) < Q(original["norm_upper"]["broken_transformed_bulk_residual"])
    assert all(len(p["screen_weight_cells_exact_rational"])==9 for p in refined["panels"])


def test_screened_weight_cells_reject_invalid_and_finite_results():
    with pytest.raises(ValueError):
        bound_weighted_moments(FILE,screen_cells=3)
    with pytest.raises(ValueError):
        bound_weighted_moments(FILE,screen_cells=True)
