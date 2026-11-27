"""PHYS52 finite physical screened high interface, exact rational Robin."""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import numpy as np
import pytest
from scipy.special import sph_harm_y
from wu088_hh.phys52_outgoing_glue import (
    finite_band_robin_certificate,signed_m_channels,unique_m_channels,
    PhysicalScreenBlocks,assembly_benchmark,
)
from wu088_hh.phys51_finite_outgoing import FROZEN_SHA

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"

@pytest.fixture(scope="module")
def cert():
    return finite_band_robin_certificate(SRC)

@pytest.fixture(scope="module")
def kernel():
    return PhysicalScreenBlocks(SRC,96)

def test_original_immutable_sha(cert):
    assert hashlib.sha256(SRC.read_bytes()).hexdigest()==FROZEN_SHA
    assert cert["source_sha256"]==FROZEN_SHA

def test_all_m_dim_and_exact_counts(cert):
    assert sum(len(x) for _,x in signed_m_channels())==400
    assert len(signed_m_channels())==57
    assert cert["entries_nonzero_signed_m_blocks"]==3032
    assert cert["entries_unique_nonnegative_m_blocks"]==1548
    assert cert["cubic_units_dense"]==64_000_000
    assert cert["cubic_units_unique_blocks"]==12048
    assert cert["max_block_dimension"]==8
    assert cert["unique_real_axisymmetric_m_blocks"]==29

def test_quantitative_current_lower_and_inverse(cert):
    import decimal
    with decimal.localcontext() as ctx:
        ctx.prec=55
        low=decimal.Decimal(cert["current_lower_per_Bohr"])
        upper=decimal.Decimal(cert["matched_Robin_inverse_norm_upper_Bohr"])
        assert decimal.Decimal("2e-15")<low<decimal.Decimal("4e-15")
        assert decimal.Decimal("3e14")<upper<decimal.Decimal("5e14")
        assert low*upper>=1  # outward bounds, never under-cover
    assert F(cert["finite_PHYS50_trace_X_to_Xdual_upper_exact"])==F(4849,16800)

def test_source_tamper_rejected(tmp_path):
    f=tmp_path/"wrong.npz"
    f.write_bytes(b"not-original")
    with pytest.raises(ValueError,match="immutable"):
        finite_band_robin_certificate(f)
    with pytest.raises(ValueError,match="immutable"):
        PhysicalScreenBlocks(f)

@pytest.mark.parametrize("m",[0,1,14,21,22,24,28,-28,-24,-1])
def test_spherical_orthogonality_and_negative_m_parity(kernel,m):
    assert kernel.gram_error(m)<3e-13
    assert np.allclose(kernel.matrix(m,27.0),
                       kernel.matrix(abs(m),27.0),rtol=1e-14,atol=0)

@pytest.mark.parametrize("m",[0,5,21,22,28])
def test_actual_two_centre_screen_psd_cauchy_and_scalar_parity(kernel,m):
    A=kernel.matrix(m,27.0)
    Q=kernel.matrix(m,27.0,"scalar")
    assert np.max(np.abs(A-Q))<=1e-13*max(np.max(np.abs(A)),1e-32)
    assert np.linalg.norm(A-A.T,ord=np.inf)<1e-36
    lam=np.linalg.eigvalsh(A)
    assert lam.min()>-1e-36
    assert lam.max()<=kernel.screen(27).max()*(1+2e-12)
    assert np.all(np.diag(A)>0)

def test_screen_genuinely_noncircular_and_offdiagonal(kernel):
    A=kernel.matrix(0,27.0)
    assert abs(A[0,1])>1e-28
    assert not np.allclose(A,np.diag(np.diag(A)),rtol=1e-14,atol=0)

@pytest.mark.parametrize("r",[27.0,30.0,43.0])
def test_screen_radius_and_envelope(kernel,r):
    s=kernel.screen(r)
    upper=(1+1/(r-0.7))*np.exp(-2*(r-0.7))
    assert np.all(s>0)
    assert s.max()<=upper*(1+3e-14)
    assert kernel.angular_certificate(r)["angular_unique_m_blocks"]==29

def test_independent_complex_spherical_harmonic_reference(kernel):
    mu=kernel.mu
    theta=np.arccos(mu)
    m=3; ells=dict(unique_m_channels())[m]
    sf=kernel.screen(27.0)
    Y=np.asarray([sph_harm_y(l,m,theta,np.zeros_like(theta))
                  for l in ells])
    independent=2*np.pi*(Y.conj()* (sf*kernel.weights)[None,:])@Y.T
    A=kernel.matrix(m,27.0)
    assert np.allclose(A,independent.real,rtol=5e-13,atol=1e-36)
    assert np.max(np.abs(independent.imag))<1e-36

def test_angular_resolution_parity(kernel):
    # n=192 has an observed quadrature-weight conditioning plateau; 256 is
    # an independent higher-resolution oracle with better Gram residual.
    alt=PhysicalScreenBlocks(SRC,256)
    for m in [0,1,21,28]:
        coarse=kernel.matrix(m,27.0)
        fine=alt.matrix(m,27.0)
        assert np.max(np.abs(coarse-fine))<3e-13*np.max(np.abs(fine))

def test_vectorized_scalar_benchmark_computational_contract(kernel):
    perf=assembly_benchmark(kernel,27.0,3)
    assert perf["scalar_29block_median_seconds"]>0
    assert perf["batched_29block_median_seconds"]>0
    assert perf["angular_nodes"]==96
    assert perf["matched_input_speedup_scalar_over_batched"]>0

def test_finite_hermitian_collar_plus_positive_outgoing_flux_algebra():
    # Independent finite-dimensional model of the exact argument.
    # LambdaTT Hermitian positive, Z=K+i J with J SPD.
    lam=np.diag([1.5,2.0,3.3])
    z=np.diag([-0.7+0.1j,-1.1+0.03j,-2.7+0.002j])
    M=lam-z
    jmin=np.min(np.imag(np.diag(z)))
    assert np.min(np.linalg.svd(M,compute_uv=False))>=jmin
    rhs=np.array([1+2j,-0.5j,3.0])
    g=np.linalg.solve(M,rhs)
    assert np.linalg.norm(M@g-rhs)<1e-13
    assert np.linalg.norm(g)<=np.linalg.norm(rhs)/jmin

@pytest.mark.parametrize("kwargs",[{"nodes":20},{"nodes":400}])
def test_invalid_quadrature_rejected(kwargs):
    with pytest.raises(ValueError):
        PhysicalScreenBlocks(SRC,**kwargs)

def test_invalid_band_rejected():
    with pytest.raises(ValueError):
        signed_m_channels(20,28)
