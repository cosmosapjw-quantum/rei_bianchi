from fractions import Fraction as F
import pytest
from src.thermal_projection import (ContractError, spin_factor,
    source_weights, target_weight_interval, conservative_target_cap,
    exact_aggregate, sharp_row_interval, printed_total_in_si)


def test_spin_factors_and_total_not_normalized():
    b = tuple(F(2*j+1) for j in range(9))  # SYNTHETIC all energies equal
    w = source_weights(b)
    assert len(w) == 90
    assert sum(w) == F(5)
    assert sum(w[j*10+r] for j in range(9) for r in range(0,10,2)) == F(5,4)
    assert sum(w[j*10+r] for j in range(9) for r in range(1,10,2)) == F(15,4)
    assert w[2*10+1] == F(5,108)
    with pytest.raises(ContractError): spin_factor(10)
    with pytest.raises(ContractError): source_weights([F(1)]*8)
    with pytest.raises(ContractError): source_weights([F(1)]*8+[F(0)])


def test_aggregate_one_printed_point_is_not_rate_row():
    w = source_weights(tuple(F(2*j+1) for j in range(9)))
    K = F(121,100)   # ARTICLE'S 205 K PRINTED AGGREGATE, synthetic weights
    a, b = 21, 0
    r1 = [F(0)]*90; r2 = [F(0)]*90
    r1[a] = K/w[a]; r2[b] = K/w[b]
    assert exact_aggregate(w, r1) == K == exact_aggregate(w, r2)
    assert r1[a] == F(3267,125)
    assert r2[a] == 0
    assert printed_total_in_si(K) == F(121, 10**18)


def test_box_projection_sharp():
    w = (F(1,4), F(3,4))
    lo, hi = sharp_row_interval(w,(F(0),F(0)),(F(3),F(1,3)),F(1,2),F(1,2),0)
    assert (lo,hi) == (F(1),F(2))
    # endpoints: x=1,y=1/3 and x=2,y=0
    assert w[0]*lo+w[1]*F(1,3)==F(1,2)
    assert w[0]*hi==F(1,2)
    with pytest.raises(ContractError):
        sharp_row_interval(w,(F(0),F(0)),(F(1),F(1,10)),F(1,2),F(1,2),0)


def test_unbounded_other_produces_zero_lower_and_finite_upper():
    lo,hi=sharp_row_interval((F(1,4),F(3,4)),(F(0),F(0)),(None,None),F(1,2),F(1,2),0)
    assert (lo,hi)==(F(0),F(2))


def test_negative_contracts():
    with pytest.raises(ContractError):
        exact_aggregate((F(1),),(F(-1),))
    with pytest.raises(ContractError):
        sharp_row_interval((F(1),), (F(0),), (None,),F(2),F(1),0)
    with pytest.raises(ContractError): printed_total_in_si(F(-1))


def test_interval_weights_and_conservative_cap():
    b = tuple(F(2*j+1) for j in range(9))
    base = source_weights(b)[21]
    lo,hi=target_weight_interval(b,b,2,1)
    assert (lo,hi)==(base,base)==(F(5,108),F(5,108))
    L=list(b);U=list(b);L[2]=F(4);U[4]=F(11)
    a,c=target_weight_interval(L,U,2,1)
    assert 0 < a < base == c
    # If the true factors equal b, the externally supplied box encloses them.
    assert a <= base <= c
    assert conservative_target_cap(F(121,100),a)>=F(3267,125)
    with pytest.raises(ContractError): target_weight_interval(L[:-1],U,2,1)
    with pytest.raises(ContractError): conservative_target_cap(F(1),F(0))
