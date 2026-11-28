import math
import numpy as np
import pytest
from bass_he_inner_boundary.core import ua_limit, radial_seed, ContractError, NumericalFailure, nuclear_scaling, match_pair


def test_UA_exact_quantities():
 a=ua_limit(branch='2p_sigma_to_1s_sigma')
 assert a is not None and a['E_lower_Eh']==-4.5 and a['E_upper_Eh']==-1.125
 assert a['gap_Eh']==27/8
 assert a['dipole_abs_a0']==pytest.approx(256/(729*math.sqrt(2)),rel=2e-15)
 assert a['V_regular_limit_Eh']==-5/8 and a['V_coulomb_coefficient']==2
 assert a['rate_coefficient'] is None and a['inner_matching_radius'] is None

@pytest.mark.parametrize('branch',[None,'n2_any','2s_sigma','HeHplus'])
def test_branch_required(branch):
 with pytest.raises(ContractError):ua_limit(branch=branch)

def test_nuclear_scaling():
 a=nuclear_scaling(mass_ratio=1000.,length_a0=1.)
 assert a is not None and a['energy_scale_Eh']==.0005
 assert a['coulomb_coefficient']==4000 and a['regular_UA_value']==-1250
 assert a['exact_isotope_selected'] is False

@pytest.mark.parametrize('ell',[0,2,20,48,64])
def test_free_zero_energy(ell):
 s=radial_seed(ell=ell,coulomb=0.,potential=[0.],width=[0.],energy=0.,radius=.01,order=48)
 assert s is not None
 assert s['log_derivative']['real']==pytest.approx((ell+1)/.01)
 assert s['log_derivative']['imag']==0
 assert s['inner_absorption']==0 and s['series_tail_absolute_bound']==0
 assert s['cross_section'] is None

@pytest.mark.parametrize('ell',[0,20,64])
def test_coulomb_zero_energy(ell):
 import mpmath as mp
 mp.mp.dps=60
 h=.001;a=6000.;s=radial_seed(ell=ell,coulomb=a,potential=[0.],width=[0.],energy=0.,radius=h,order=80)
 assert s is not None
 H=mp.mpf(h);A=mp.mpf(a);b=2*ell+2
 v=mp.hyp0f1(b,A*H);dv=A/b*mp.hyp0f1(b+1,A*H)
 oracle=float((ell+1)/H+dv/v)
 assert s['log_derivative']['real']==pytest.approx(oracle,rel=3e-14)
 assert s['series_tail_absolute_bound']<1e-40

@pytest.mark.parametrize('ell',[0,20,64])
def test_positive_inner_absorption(ell):
 s=radial_seed(ell=ell,coulomb=6000.,potential=[-1000.],width=[1e-22],energy=1.,radius=.001,order=80)
 assert s is not None and s['inner_absorption']>0
 assert s['log_derivative']['imag']==pytest.approx(-s['inner_absorption']/2,rel=1e-10,abs=0)
 assert s['finite_local_model_only'] and s['physical_accuracy_certified'] is False

@pytest.mark.parametrize('bad',[
 {'ell':-1},{'ell':True},{'ell':65},{'coulomb':-1},{'radius':0},{'radius':float('nan')},
 {'width':[-1.]},{'potential':[]},{'order':2},{'energy':float('inf')}, {'width':[1.,-300.]}
])
def test_bad_input(bad):
 kw=dict(ell=0,coulomb=2.,potential=[0.],width=[0.],energy=1.,radius=.01,order=64);kw.update(bad)
 with pytest.raises(ContractError):radial_seed(**kw)

def test_width_positive_despite_negative_power_coefficient():
 a=radial_seed(ell=0,coulomb=2.,potential=[0.],width=[1.,-1.],energy=1.,radius=.1,order=64)
 assert a is not None and a['inner_absorption']>0 and a['width_nonnegative_proof']=='EXACT_RATIONAL_BERNSTEIN_SUFFICIENT_TEST'

def test_match_preserves_loss_scaling():
 a=radial_seed(ell=2,coulomb=2.,potential=[0.],width=[.01],energy=1.,radius=.1,order=64)
 x=match_pair(a,amplitude=3+4j)
 assert x is not None and x['inner_absorption']==pytest.approx(25*a['inner_absorption'])
 assert complex(*x['u'])==3+4j
 L=complex(a['log_derivative']['real'],a['log_derivative']['imag'])
 assert complex(*x['du'])==pytest.approx((3+4j)*L)


def test_not_enough_series_rejected():
 with pytest.raises(NumericalFailure):
  radial_seed(ell=0,coulomb=1e5,potential=[1.],width=[0.],energy=0.,radius=1.,order=16)
