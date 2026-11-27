"""PHYS51 certified all-m screened finite high band and Coulomb diagnostics."""
from __future__ import annotations
import hashlib
from fractions import Fraction as F
from pathlib import Path
import pytest
import mpmath as mp

from wu088_hh.phys51_finite_outgoing import (
    B,C,K,R,LOW,HIGH,FROZEN_SHA,SCHEMA, lognorm_max,
    _energy_patch,finite_band_screened_jost,coulomb_impedance_rows,
)
ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"

@pytest.fixture(scope="module")
def cert():
    return finite_band_screened_jost(ORIGINAL)

def test_source_lock_and_source_preservation(cert):
    assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()==FROZEN_SHA
    assert cert["source_sha256"]==FROZEN_SHA
    assert cert["schema"]==SCHEMA
    assert cert["angular_band_inclusive"]==[21,28]
    assert cert["n_channels"]==400 and cert["all_m"] is True
    assert cert["status"].startswith("RIGOROUS_FINITE_HIGH")

@pytest.mark.parametrize("ell", [21,22,24,27,28])
def test_logarithmic_norm_exact_endpoint(ell):
    # For each r in [27,50], 0<ell(ell+1)/r²-2/r and decreases.
    assert F(ell*(ell+1),B*B)-F(2,B)>0
    assert lognorm_max(21,ell,50)<=C
    assert C==F(4,5)

@pytest.mark.parametrize("T", [42,43,44,45,46])
def test_energy_patch_outward_rational_and_strict_contraction(T):
    row=_energy_patch(T,21,28,192)
    assert 0<row["qmin"]<K*K
    assert row["lognorm_max"]<C
    assert row["M"]**2>row["M2_required"]
    assert row["p1"]>0 and row["p2"]>0
    assert 0<row["q_upper_exact"]<F(1,2)

def test_best_rational_bound_and_terminology(cert):
    q=F(cert["screened_Volt_q_exact_rational_upper"])
    assert q>0 and q<F(1,10000000)
    assert cert["certified_patch_T_Bohr"] in [42,43,44,45,46]
    assert "xi=F*y-phi" in str(cert["not_certified"])
    assert "UNKNOWN" in cert["coupling_with_PHYS50"]
    assert cert["Jost_boundary_matrix_invertible"] is True
    assert len(cert["patch_comparison"])==5

@pytest.mark.parametrize("ell", [21,24,28])
def test_positive_coulomb_outgoing_flux_exact_normalization(ell):
    row=coulomb_impedance_rows((ell,),27,70)[0]
    assert mp.mpf(row["z_im_per_Bohr"])>0
    assert abs(mp.mpf(row["wronskian_Im_conjH_dH"])-1)<mp.mpf("1e-32")
    assert abs(mp.mpf(row["z_im_per_Bohr"])-mp.mpf(row["normal_current_k_over_H2"])) <mp.mpf("1e-32")

def test_independent_coulomb_derivative_for_ell21():
    with mp.workdps(58):
        k=mp.mpf(7)/10; eta=-1/k; rho=k*27; ell=21
        H=lambda z: mp.coulombg(ell,eta,z)+1j*mp.coulombf(ell,eta,z)
        direct=k*mp.diff(H,rho)/H(rho)
        z=coulomb_impedance_rows((ell,),27,70)[0]
        assert abs(mp.re(direct)-mp.mpf(z["z_re_per_Bohr"]))<mp.mpf("1e-32")
        assert abs(mp.im(direct)-mp.mpf(z["z_im_per_Bohr"]))<mp.mpf("1e-32")

@pytest.mark.parametrize("bad",[(20,28),(21,29)])
def test_out_of_scope_rejected(bad):
    with pytest.raises(ValueError):
        finite_band_screened_jost(ORIGINAL,lo=bad[0],hi=bad[1])

def test_source_tamper_rejected(tmp_path):
    f=tmp_path/"fake.npz"
    f.write_bytes(b"malformed-source")
    with pytest.raises(ValueError,match="immutable"):
        finite_band_screened_jost(f)

def test_patch_bad_inputs_rejected():
    with pytest.raises(ValueError):
        _energy_patch(75,21,28,192)
    with pytest.raises(ValueError):
        _energy_patch(43,21,28,10)
