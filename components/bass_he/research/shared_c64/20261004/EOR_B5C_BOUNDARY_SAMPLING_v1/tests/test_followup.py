"""Post-implementation evidence, invariance and arithmetic checks (not test-first)."""
import hashlib,json
from pathlib import Path
from fractions import Fraction as F
import pytest
from bass_he_optical_sampling.core import ContractError,hermite,load_R8,load_contract
from bass_he_prolate_variational import core as v
from bass_he_optical_sampling.cli import write_new
ROOT=Path(__file__).resolve().parents[1]

def read(name):return json.loads((ROOT/name).read_text())
@pytest.mark.parametrize('ell,expected',[(1,'9'),(2,'30')])
def test_response_exact_check(ell,expected):
 row=read('evidence/EXACT_FORMULAS.json')['radial_response'][ell-1]
 assert row['response_ODE_defect']=='0' and row['coefficient_ZB2']==expected

def test_unobserved_polynomial_counterexample():
 q=lambda x:x*x*(x-F(1,2))**2*(x-1)**2
 assert all(q(x)==0 for x in (F(0),F(1,2),F(1)))
 assert q(F(1,4))==F(9,4096)

def test_parent_scope_unchanged():
 with pytest.raises(ContractError):v.solve(10.,8,8,16.)

def test_five_registered_spectral_and_derivative_comparisons():
 d=read('data/SUMMARY.json')
 assert len(d['comparisons'])==5 and all(all(x['gates'].values()) for x in d['comparisons'])
 assert not d['physical_accuracy_certified'] and d['Eq55']=='NOT_RUN'

def test_sampling_resolution_outcomes_preserved():
 d=read('data/SUMMARY.json')['sampling_levels']
 assert d[0]['width']==.5 and not d[0]['all_midpoint_gates']
 assert d[1]['width']==.25 and d[1]['all_midpoint_gates']

def test_source_sequence_has_16_new_points():
 d=read('data/OPTICAL_SAMPLES.json')
 assert [x['R_a0'] for x in d]==[8+i/8 for i in range(17)]
 assert all(x['physical_accuracy_certified'] is False for x in d)

@pytest.mark.parametrize('loader,relative',[(load_R8,'parent/R8_ANCHOR.json'),(load_contract,'contract/PREREGISTRATION.json')])
def test_changed_parent_or_contract_bytes_rejected(loader,relative,tmp_path):
 p=tmp_path/'bad.json';p.write_bytes((ROOT/relative).read_bytes()+b'\n')
 with pytest.raises(ContractError):loader(p)

def test_output_symlink_not_overwritten(tmp_path):
 target=tmp_path/'real';target.write_bytes(b'keep');dest=tmp_path/'alias';dest.symlink_to(target)
 with pytest.raises(FileExistsError):write_new(dest,{'other':1})
 assert target.read_bytes()==b'keep'

def test_matrix_Hp_Sp_independent_synthetic_pencil():
 import numpy as np
 from scipy.linalg import eigh
 H0=np.array([[2.,.3],[.3,4.]]);D=np.array([[.2,.1],[.1,.5]])
 S0=np.array([[2.,.1],[.1,1.]]);Q=np.diag([.01,.02]);R=.7;h=1e-4
 H=H0+R*D;S=S0+R*Q;E,C=eigh(H,S,type=1,driver='gvx')
 deriv=np.array([c@(D-e*Q)@c for e,c in zip(E,C.T)])
 def vals(r):return eigh(H0+r*D,S0+r*Q,type=1,driver='gvx',eigvals_only=True)
 fd=(-vals(R+2*h)+8*vals(R+h)-8*vals(R-h)+vals(R-2*h))/(12*h)
 assert np.max(abs(fd-deriv))<1e-10

def test_no_uniform_error_or_tail_promoted():
 d=read('data/SUMMARY.json')
 assert d['uniform_interpolation_error_bound'] is None and d['tail_bound'] is None
