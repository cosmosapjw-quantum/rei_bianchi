import math
from fractions import Fraction
from pathlib import Path
import numpy as np
import pytest
from bass_he_optical_sampling.core import hermite,sampling_bounds,polarization,derivative_matrices,validate_path,load_R8,ContractError
from bass_he_prolate_variational.core import assemble

@pytest.mark.parametrize('t',[0.,.125,.25,.5,.875,1.])
def test_cubic_reproduced(t):
 x=8+2*t
 f=lambda z:z**3-2*z*z+z+1
 d=lambda z:3*z*z-4*z+1
 assert abs(hermite(8.,10.,f(8),f(10),d(8),d(10),x)-f(x))<2e-12

@pytest.mark.parametrize('x',[-1.,1.001,float('nan')])
def test_hermite_no_extrapolation(x):
 with pytest.raises(ContractError):hermite(0.,1.,0.,1.,1.,1.,x)

def test_conditional_remainder_formula():
 b=sampling_bounds(.5,M4=24.,M2=2.,node_error=1e-8,slope_error=2e-8)
 assert b['hermite_absolute']==pytest.approx(.5**4/16+1e-8+.5/4*2e-8)
 assert b['log_linear_absolute']==pytest.approx(2*.5**2/8+1e-8)
 assert b['physical_accuracy_certified'] is False

@pytest.mark.parametrize('key',['M4','M2','node_error','slope_error'])
def test_negative_majorant_rejected(key):
 kw=dict(M4=1.,M2=1.,node_error=0.,slope_error=0.);kw[key]=-1.
 with pytest.raises(ContractError):sampling_bounds(.5,**kw)

@pytest.mark.parametrize('R',[8.,9.,10.])
def test_polarization_coefficients(R):
 p=polarization(R)
 assert p['leading_C4']==9. and p['second_order_C6']==30.
 assert p['V_C4_Eh']==-9/R**4
 assert p['V_C4_C6_Eh']==pytest.approx(-9/R**4-30/R**6)
 assert p['remainder_bound'] is None

def test_fixed_scale_matrix_derivative():
 R=9.;h=1e-4
 Hp,Sp=derivative_matrices(R,6,5,12.)
 lo=assemble(R-h,6,5,12.);hi=assemble(R+h,6,5,12.)
 assert np.max(abs(Hp-(hi['H']-lo['H'])/(2*h)))<2e-7
 assert np.max(abs(Sp-(hi['S']-lo['S'])/(2*h)))<2e-6

@pytest.mark.parametrize('path',[[8.,8.25],[8.,8.125,8.125],[7.875,8.],[8.,8.125,10.],[8.,float('nan')]])
def test_path_rejected(path):
 with pytest.raises(ContractError):validate_path(path)

def test_exact_registered_path():
 assert validate_path([8+i/8 for i in range(17)])==[8+i/8 for i in range(17)]

def test_anchor_bound_to_bytes():
 root=Path(__file__).resolve().parents[1]
 states,phase=load_R8(root/'parent/R8_ANCHOR.json')
 assert len(states)==2 and all(s.R==8 for s in states) and len(phase)==2

@pytest.mark.parametrize('cfg',[(8.,28,28,16.),(10.,20,20,16.),(10.,28,28,20.)])
def test_unregistered_endpoint_rejected(cfg):
 from bass_he_optical_sampling.core import solve_R10
 with pytest.raises(ContractError):solve_R10(*cfg)
