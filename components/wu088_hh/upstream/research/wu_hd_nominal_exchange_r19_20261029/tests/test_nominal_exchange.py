from __future__ import annotations
from fractions import Fraction
import json, math, os, subprocess, sys
from pathlib import Path
import numpy as np
import pytest
from scipy.integrate import solve_ivp
from research.wu_hd_source_bound_r18_20261029.src.native_rates import (
    NativeGrid, SourceContractError, load_native_grid, PDF_SHA256,
)
from research.wu_hd_nominal_exchange_r19_20261029.src.nominal_exchange import (
    T_SOURCE_K, K_PRINTED_SI, STATE_ORDER, NU, ModelContractError,
    _extent_and_remainders, _rate_si_from_verified_grid, flow_nominal,
    flow_constant_expansion, source_rhs, source_jacobian,
    conserved_totals, conditional_event_energy, nominal_rate_sensitivity,
)
ROOT = Path(__file__).resolve().parents[3]
PDF = Path(os.environ.get('WU_R19_SOURCE_PDF', ROOT/'ORIGINAL_SOURCES/GL2022_CSIC_supplement.pdf'))

@pytest.fixture(scope='module')
def grid():
    if not PDF.is_file():
        pytest.fail('R18 original PDF required: set WU_R19_SOURCE_PDF to source-locked 273554-byte PDF')
    return load_native_grid(PDF)

def test_01_source_immutable_identity_and_exact_105K(grid):
    assert grid.source_sha256 == PDF_SHA256
    assert T_SOURCE_K == 105
    assert _rate_si_from_verified_grid(grid) == K_PRINTED_SI == Fraction(23,200000000000000000)
    assert grid.lookup(105).original_token == '1.15(10)'
    assert STATE_ORDER == ('H+', 'HD(v=0,j=2)', 'D+', 'H2(v=0,j=1)')

def test_02_source_wrong_temperature_rejected(grid):
    with pytest.raises(SourceContractError): grid.lookup(100)
    with pytest.raises(SourceContractError): grid.lookup(105, initial_j=3)
    with pytest.raises(SourceContractError): grid.lookup(105, method='TIQM')

def test_03_no_unverified_grid_can_be_used():
    with pytest.raises(SourceContractError): NativeGrid(tuple(),PDF_SHA256,'0'*64)
    with pytest.raises(SourceContractError): flow_nominal(object(),(1,1,0,0),1)

def test_04_equal_reactants_exact_closed_form(grid):
    n0=1e6;t=1e10;k=float(K_PRINTED_SI)
    r=flow_nominal(grid,(n0,n0,0,0),t)
    expected=n0/(1+k*n0*t)
    assert r.state_m3[0] == pytest.approx(expected,rel=2e-15)
    assert r.state_m3[1] == pytest.approx(expected,rel=2e-15)
    assert r.state_m3[2] == pytest.approx(n0-expected,rel=2e-15)
    assert r.extent_m3 == pytest.approx(n0-expected,rel=2e-15)
    assert r.as_json()['source']['physical_uncertainty'] is None
    assert r.as_json()['admission']['physical_consumer'] is False

def test_05_unequal_reactants_and_swap(grid):
    a,b=1e6,2e6;t=1e10
    x=flow_nominal(grid,(a,b,0,0),t)
    y=flow_nominal(grid,(b,a,0,0),t)
    assert x.extent_m3 == y.extent_m3
    assert x.state_m3[:2] == y.state_m3[1::-1]
    z=math.exp(-float(K_PRINTED_SI)*(b-a)*t)
    xi=a*b*(1-z)/(b-a*z)
    assert x.extent_m3 == pytest.approx(xi,rel=2e-15)

def test_06_invariants_stoichiometric_and_positive(grid):
    n=(1e6,2e6,3e5,4e5)
    before=conserved_totals(n)
    for t in (0,1e5,1e9,1e10,1e11,1e12):
        r=flow_nominal(grid,n,t)
        after=conserved_totals(r.state_m3)
        assert all(v>=0 for v in r.state_m3)
        for name,val in before.items():
            assert after[name] == pytest.approx(val,rel=3e-15)
    assert sum(NU)==0

def test_07_zero_reactant_and_initial_time(grid):
    for n in ((0,2e6,0,0),(1e6,0,4,5)):
        r=flow_nominal(grid,n,1e12)
        assert r.extent_m3==0
        assert r.state_m3==tuple(float(x) for x in n)
    assert flow_nominal(grid,(1e6,2e6,3,4),0).state_m3==(1e6,2e6,3.0,4.0)

def test_08_extent_monotone_and_bounded(grid):
    n=(1e6,2e6,0,0)
    ext=[flow_nominal(grid,n,t).extent_m3 for t in (0,1e7,1e8,1e9,1e10,1e12)]
    assert ext==sorted(ext)
    assert ext[0]==0 and 0<ext[-1]<=1e6

def test_09_near_equal_stable_branch(grid):
    a=1e6;b=a*(1+1e-12);t=1e10
    r=flow_nominal(grid,(a,b,0,0),t)
    expected=a/(1+float(K_PRINTED_SI)*a*t)
    assert r.state_m3[0]==pytest.approx(expected,rel=1e-11)
    assert r.state_m3[1]-r.state_m3[0]==pytest.approx(b-a,rel=2e-4)

def test_10_large_exposure_no_negative_survivor(grid):
    r=flow_nominal(grid,(1e6,2e6,0,0),1e15)
    assert all(x>=0 for x in r.state_m3)
    assert r.state_m3[0]>=0 and r.state_m3[1]>0

def test_11_source_rhs_exact_stoichiometry(grid):
    n=(1e6,2e6,1e5,3e5)
    f=source_rhs(grid,n)
    J=float(K_PRINTED_SI)*n[0]*n[1]
    assert f==(-J,-J,J,J)
    assert source_rhs(grid,n,dt_ds_seconds=2.5)==tuple(2.5*x for x in f)

def test_12_source_jacobian_analytic_eigenvalues(grid):
    n=(1e6,2e6,1e5,3e5)
    jac=np.array(source_jacobian(grid,n),dtype=float)
    assert np.linalg.matrix_rank(jac,tol=1e-24)==1
    eig=np.linalg.eigvals(jac)
    assert np.min(eig.real)==pytest.approx(-float(K_PRINTED_SI)*(n[0]+n[1]),rel=1e-12)
    assert np.max(abs(eig.real[abs(eig.real)<1e-15]))<1e-15

def test_13_jacobian_finite_difference(grid):
    n=np.array((1e6,2e6,1e5,3e5),dtype=float)
    jac=np.array(source_jacobian(grid,n,dt_ds_seconds=1.7,expansion_theta_s=2e-12))
    for j in range(4):
        eps=1e-4
        a=n.copy();b=n.copy();a[j]+=eps;b[j]-=eps
        fd=(np.array(source_rhs(grid,a,1.7,2e-12))-np.array(source_rhs(grid,b,1.7,2e-12)))/(2*eps)
        assert np.allclose(fd,jac[:,j],rtol=1e-6,atol=2e-15)

def test_14_expansion_theta_zero_limit(grid):
    n=(1e6,2e6,1e5,3e5);t=1e10
    x=flow_constant_expansion(grid,n,t,0)
    y=flow_nominal(grid,n,t)
    assert x==y
    z=flow_constant_expansion(grid,n,t,1e-25)
    assert z.extent_m3==pytest.approx(y.extent_m3,rel=3e-14)

def test_15_prescribed_expansion_comoving_invariants(grid):
    n=(1e6,2e6,1e5,3e5);theta=1e-11;t=1e10
    r=flow_constant_expansion(grid,n,t,theta)
    assert r.volume_ratio==pytest.approx(math.exp(theta*t),rel=1e-15)
    assert r.effective_seconds==pytest.approx(-math.expm1(-theta*t)/theta,rel=1e-15)
    b=conserved_totals(n);a=conserved_totals(r.state_m3)
    for q in b:
        assert a[q]*r.volume_ratio==pytest.approx(b[q],rel=3e-15)

def test_16_prescribed_contraction_and_dilution(grid):
    n=(1e6,2e6,1e5,3e5);theta=-1e-11;t=1e10
    r=flow_constant_expansion(grid,n,t,theta)
    assert r.volume_ratio<1 and r.effective_seconds>t
    assert all(x>=0 for x in r.state_m3)
    with pytest.raises(ModelContractError): flow_nominal(grid,n,t,volume_ratio=1.1)

def test_17_scipy_independent_dop853_expansion(grid):
    n=np.array((1e6,2e6,1e5,3e5));theta=2e-11;tend=2e10
    analytic=np.array(flow_constant_expansion(grid,n,tend,theta).state_m3)
    sol=solve_ivp(lambda t,y: source_rhs(grid,y,expansion_theta_s=theta),
                  (0,tend),n,method='DOP853',rtol=2e-12,atol=1e-7)
    assert sol.success
    assert np.allclose(sol.y[:,-1],analytic,rtol=3e-11,atol=1e-5)

def test_18_independent_ode_no_expansion(grid):
    n=np.array((1e6,1e6,0,0));tend=1e11
    analytic=np.array(flow_nominal(grid,n,tend).state_m3)
    sol=solve_ivp(lambda t,y: source_rhs(grid,y),(0,tend),n,
                  method='Radau',rtol=3e-11,atol=1e-7)
    assert sol.success and np.allclose(sol.y[:,-1],analytic,rtol=1e-9,atol=2e-4)

def test_19_parameter_sensitivity_derivative(grid):
    n=(1e6,2e6,0,0);t=1e10;k=float(K_PRINTED_SI)
    r=nominal_rate_sensitivity(grid,n,t)
    eps=1e-5
    plus=_extent_and_remainders(n[0],n[1],k*(1+eps),t)[0]
    minus=_extent_and_remainders(n[0],n[1],k*(1-eps),t)[0]
    derivative=(plus-minus)/(2*eps*k)
    assert derivative==pytest.approx(r['d_extent_d_k_SI'],rel=1e-9)
    assert r['source_uncertainty'] is None

def test_20_formal_energy_ledger_no_physical_Q(grid):
    out=conditional_event_energy(5e5,1e-20)
    assert out['chemical_energy_change_J_per_reference_m3']==-5e-15
    assert out['bath_energy_change_J_per_reference_m3']==5e-15
    assert out['formal_total_J_per_reference_m3']==0
    assert out['physical_Q_admitted'] is False

def test_21_negative_nonfinite_and_clock_guards(grid):
    with pytest.raises(ModelContractError): flow_nominal(grid,(-1,1,0,0),1)
    with pytest.raises(ModelContractError): flow_nominal(grid,(1,1,0,0),float('nan'))
    with pytest.raises(ModelContractError): flow_nominal(grid,(1,1,0,0),1,volume_ratio=0)
    with pytest.raises(ModelContractError): flow_nominal(grid,(1,1,0,0),0,integrated_inverse_volume_seconds=1)
    with pytest.raises(ModelContractError): source_rhs(grid,(1,1,0,0),dt_ds_seconds=0)
    with pytest.raises(ModelContractError): flow_constant_expansion(grid,(1,1,0,0),1e10,1e-6)
    with pytest.raises(ModelContractError): conditional_event_energy(1,float('inf'))

def test_22_cli_output_exclusive_create(grid,tmp_path):
    out=tmp_path/'nested'/'result.json'
    module='research.wu_hd_nominal_exchange_r19_20261029.src.nominal_exchange'
    cmd=[sys.executable,'-m',module,'--source-pdf',str(PDF),'--initial-m3','1000000','1000000','0','0',
         '--proper-seconds','10000000000','--output',str(out)]
    first=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
    assert first.returncode==0,first.stderr
    data=json.loads(out.read_text())
    assert data['source']['rate_m3_s_exact']=={'numerator':'23','denominator':'200000000000000000'}
    assert data['admission']['production']=='NOT_ISSUED'
    second=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
    assert second.returncode==2 and 'FileExistsError' not in second.stderr

def test_23_no_thermal_spin_population_reweighting(grid):
    assert flow_nominal(grid,(1e6,1e6,0,0),1e10).rate_m3_s==K_PRINTED_SI
    assert float(K_PRINTED_SI)==pytest.approx(1.15e-16,rel=1e-15)

def test_24_dimensional_clock_and_flux(grid):
    n=(1e6,2e6,0,0)
    flux=float(K_PRINTED_SI)*n[0]*n[1]
    assert flux==pytest.approx(2.3e-4,rel=1e-15) # m^-3 s^-1
    assert flow_nominal(grid,n,1).extent_m3==pytest.approx(flux,rel=1e-12)
