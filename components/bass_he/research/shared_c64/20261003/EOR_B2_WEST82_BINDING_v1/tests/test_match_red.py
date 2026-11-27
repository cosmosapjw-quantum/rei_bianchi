import pytest
from bass_he_west82 import solve_partial_wave,NumericalFailure

@pytest.mark.filterwarnings("error")
def test_evanescent_free_exact_zero_no_incoming_square_overflow():
    r=solve_partial_wave(1.,48,[0.,.001],[0.],[[0.]])
    assert r['loss_probability']==0 and abs(complex(*r['S'])-1)<1e-12

@pytest.mark.filterwarnings("error")
def test_unrepresentably_small_positive_loss_is_explicit_failure():
    with pytest.raises(NumericalFailure):solve_partial_wave(1.,48,[0.,.001],[0.],[[1e-8]])
