"""Review-found numerical-range failures must be typed, not unhandled Python errors."""
import pytest
from bass_he_inner_boundary.core import nuclear_scaling,radial_seed,match_pair,NumericalFailure

@pytest.mark.parametrize('m,L',[(1e308,1e308),(1e-300,1e-300)])
def test_scaling_range_typed(m,L):
 with pytest.raises(NumericalFailure):nuclear_scaling(mass_ratio=m,length_a0=L)

def test_matching_amplitude_range_typed():
 s=radial_seed(ell=0,coulomb=2.,potential=[0.],width=[1.],energy=1.,radius=.1,order=64)
 with pytest.raises(NumericalFailure):match_pair(s,amplitude=1e308)
