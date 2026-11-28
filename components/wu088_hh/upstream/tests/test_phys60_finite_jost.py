"""PHYS60 R5 scoped tests: actual physical source and Coulomb current."""
from pathlib import Path
import numpy as np
import mpmath as mp
import pytest
from wu088_hh.phys60_finite_jost import *
SRC=Path(__file__).resolve().parents[1]/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'
def test_original_sha():assert source_sha_guard(SRC)==FROZEN_SHA
def test_original_sha_failure(tmp_path):
 p=tmp_path/'bad.npz';p.write_bytes(b'x')
 with pytest.raises(ValueError,match='immutable'):source_sha_guard(p)
def test_original_exact_source_bound():assert 0<screen_delta_upper()<F(3,10**23)
def test_positive_original_energy():assert PHYSICAL_E==F(49,200) and ETA_C==F(-10,7)
@pytest.mark.parametrize('r',[27,30,43,60])
def test_screen_max_at_forward_axis(r):
 a=screen_at(r,np.array([-1.,0.,1.]));assert 0<a[0]<a[1]<a[2]
@pytest.mark.parametrize('m',[0,1,2,20,-1,-2])
def test_screen_matrix_real_symmetric_and_nonzero(m):
 q=angular_real_block(27.,(20,21),m,160)
 assert np.max(np.abs(q-q.T))<1e-35
 assert q[0,0]>0 and q[1,1]>0
 if abs(m)<=2:assert q[0,1]>0
 assert np.linalg.eigvalsh(q).min()>-1e-38
@pytest.mark.parametrize('m',[0,1,2,20])
def test_plusminus_m_same_screen(m):
 assert np.allclose(angular_real_block(27.,(20,21),m,128),angular_real_block(27.,(20,21),-m,128),rtol=1e-13,atol=0)
@pytest.mark.parametrize('ell',[0,20,21,28])
def test_positive_outgoing_wronskian_highprecision(ell):
 with mp.workdps(75):
  h=hplus(ell,27.,75); d=hplus_derivative(ell,27.,75)
  assert abs(mp.im(mp.conj(h)*d)-mp.mpf(7)/10)<mp.mpf('1e-55')
  z=d/h; assert mp.im(z)>0
@pytest.mark.parametrize('ell',[0,20,21])
def test_volterra_diagonal_kernel_is_zero(ell):
 z=volterra_kernel(ell,27.,27.,65)
 assert abs(z)<mp.mpf('1e-55')
def test_volterra_kernel_real_for_real_radius():
 z=volterra_kernel(20,27.,29.,65)
 assert abs(mp.im(z))<mp.mpf('1e-55')
@pytest.mark.parametrize('case',[(-1,(20,21),0,128),(27,(20,21),22,128),(27,(20,21),0,30)])
def test_guard_invalid_angular(case):
 with pytest.raises(ValueError):angular_real_block(*case)
