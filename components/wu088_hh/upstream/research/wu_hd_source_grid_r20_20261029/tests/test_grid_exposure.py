from __future__ import annotations
import os
import json, math
from pathlib import Path
from fractions import Fraction
import numpy as np
import pytest
from scipy.integrate import solve_ivp
from research.wu_hd_source_bound_r18_20261029.src.native_rates import (
    PDF_SHA256, SourceContractError, load_native_grid, TEMPERATURES_K,
)
from research.wu_hd_nominal_exchange_r19_20261029.src.nominal_exchange import (
    ModelContractError, _extent_and_remainders,
)
from src.grid_exposure import (
    Segment, evolve_source_grid, rate_sensitivities, clock_from_hubble,
    cr_gl2_formula, _inverse_volume_clock, main, CR_CLOCK_SOURCE,
)
PDF = Path(os.environ.get('WU_R20_SOURCE_PDF', str(Path(__file__).resolve().parents[1] / 'parent/ORIGINAL_SOURCES/GL2022_CSIC_supplement.pdf')))

@pytest.fixture(scope='module')
def grid():
    return load_native_grid(PDF)


def test_original_source_ten_nodes(grid):
    assert grid.source_sha256 == PDF_SHA256
    assert len(TEMPERATURES_K) == 10
    assert grid.lookup(105).nominal_m3_s == Fraction(23,200000000000000000)
    assert grid.lookup(255).nominal_m3_s == Fraction(137,500000000000000000)


def test_two_temperature_equal_initial(grid):
    r=evolve_source_grid(grid,(1e6,1e6,0,0),[Segment(105,5e9),Segment(255,5e9)])
    assert r.exposure_m3 == pytest.approx(1.945e-6,rel=1e-15)
    assert r.final_state_m_minus3[0] == pytest.approx(1e6/(1+1e6*1.945e-6),rel=1e-14)
    assert r.final_state_m_minus3[2] == pytest.approx(1e6-r.final_state_m_minus3[0])
    assert r.as_json()['admission']['owner_HD_consumer'] is False
    assert r.as_json()['source']['thermal_spin_applied'] is False


def test_all_ten_source_nodes(grid):
    r=evolve_source_grid(grid,(1e6,2e6,0,0),[Segment(T,1000.) for T in TEMPERATURES_K])
    assert r.temperature_nodes_K == TEMPERATURES_K
    assert len(r.source_rates) == 10
    assert all(k>0 for k in r.source_rates)


def test_conserved_covectors_with_volume(grid):
    n0=np.array([2e6,3e6,1e5,4e5])
    r=evolve_source_grid(grid,n0,[Segment(105,3e9,2e-11),Segment(255,5e9,-1e-11)])
    n=np.array(r.final_state_m_minus3)*r.volume_ratio
    for cov in ([1,1,0,2],[0,1,1,0],[1,0,1,0]):
        assert float(np.dot(cov,n))==pytest.approx(float(np.dot(cov,n0)),rel=1e-13)


def test_positivity_for_asymmetric_states(grid):
    r=evolve_source_grid(grid,(1e5,4e6,8e5,2e5),[Segment(105,1e10),Segment(255,1e10)])
    assert all(v>=0 for v in r.final_state_m_minus3)
    assert r.extent_reference_m_minus3<=1e5


def test_semigroup_at_fixed_volume(grid):
    r=evolve_source_grid(grid,(1e6,2e6,0,0),[Segment(105,2e9),Segment(255,3e9)])
    a,b,c,d=1e6,2e6,0,0
    for e in r.segment_exposures_m3:
        x,aa,bb=_extent_and_remainders(a,b,1.0,e)
        a,b,c,d=aa,bb,c+x,d+x
    assert np.allclose([a,b,c,d],r.final_state_m_minus3,rtol=3e-14,atol=1e-7)


def test_permutation_at_fixed_volume(grid):
    a=Segment(105,3e9);b=Segment(255,8e9)
    r1=evolve_source_grid(grid,(1e6,1e6,0,0),[a,b])
    r2=evolve_source_grid(grid,(1e6,1e6,0,0),[b,a])
    assert r1.exposure_m3==pytest.approx(r2.exposure_m3,rel=1e-15)
    assert r1.final_state_m_minus3==pytest.approx(r2.final_state_m_minus3,rel=1e-14)


def test_inverse_clock_positive_expansion():
    I,v=_inverse_volume_clock(1e10,2e-11,1.0)
    assert v==pytest.approx(math.exp(.2))
    assert I==pytest.approx(-math.expm1(-.2)/2e-11,rel=1e-15)


def test_inverse_clock_contraction():
    I,v=_inverse_volume_clock(1e10,-2e-11,1.0)
    assert v==pytest.approx(math.exp(-.2))
    assert I>1e10


def test_inverse_clock_theta_zero_and_small():
    I,v=_inverse_volume_clock(1e10,0.,1.0)
    assert I==1e10 and v==1
    I2,v2=_inverse_volume_clock(1e10,1e-24,1.0)
    assert I2==pytest.approx(I,rel=1e-14)


def test_rate_sensitivity_finite_difference(grid):
    n0=(1e6,1.7e6,0.,0.)
    r=evolve_source_grid(grid,n0,[Segment(105,5e9),Segment(255,5e9)])
    s=rate_sensitivities(r)
    delta=1e-21
    for i,I in enumerate(r.inverse_volume_seconds):
        plus=_extent_and_remainders(n0[0],n0[1],1.0,r.exposure_m3+delta*I)[0]
        minus=_extent_and_remainders(n0[0],n0[1],1.0,r.exposure_m3-delta*I)[0]
        assert (plus-minus)/(2*delta)==pytest.approx(s[i],rel=5e-8)


def test_source_state_and_off_grid_rejected(grid):
    with pytest.raises(SourceContractError):grid.lookup(100)
    with pytest.raises(SourceContractError):grid.lookup(105,initial_j=3)
    with pytest.raises(SourceContractError):evolve_source_grid(grid,(1,1,0,0),[Segment(100,1)])
    with pytest.raises(ModelContractError):evolve_source_grid(grid,(1,1,0,0),[])


def test_malformed_schedule_rejected(grid):
    with pytest.raises(ModelContractError):Segment(True,1)
    with pytest.raises(ModelContractError):Segment(105,-1)
    with pytest.raises(ModelContractError):Segment(105,1,float('nan'))
    with pytest.raises(ModelContractError):evolve_source_grid(grid,(1,1,0,0),[{'temperature_K':105}])
    with pytest.raises(ModelContractError):evolve_source_grid(grid,(1,-1,0,0),[Segment(105,1)])


def test_extreme_expansion_rejected(grid):
    with pytest.raises(ModelContractError):evolve_source_grid(grid,(1,1,0,0),[Segment(105,1e12,1e-9)])
    with pytest.raises(ModelContractError):evolve_source_grid(grid,(1,1,0,0),[Segment(105,1e12,-1e-9)])


def test_source_pdf_mutation_rejected(tmp_path):
    raw=bytearray(PDF.read_bytes());raw[100]^=1
    p=tmp_path/'mutated.pdf';p.write_bytes(raw)
    with pytest.raises(SourceContractError):load_native_grid(p)


def test_owner_clock_constant_H_and_FLRW_volume(grid):
    a0,a1,H=.1,.12,2e-18
    v=lambda a:(a/a0)**3
    c=clock_from_hubble(grid,105,a0,a1,0.,lambda a,q:H,v,nodes=16)
    expected=float(grid.lookup(105).nominal_m3_s)*(1-(a0/a1)**3)/(3*H)
    assert c.exposure_m3==pytest.approx(expected,rel=5e-14)
    assert c.proper_seconds_quadrature==pytest.approx(math.log(a1/a0)/H,rel=1e-14)
    assert c.owner_chemistry_bound is False


def test_owner_gl2_formula_matches_named_CR_signature(grid):
    class Model:
        def hubble(self,a,q):return 2e-18*(1+q*a)
    m=Model();a0,a1,q=.1,.11,.03
    ref=cr_gl2_formula(m,a0,a1,q)
    ours=clock_from_hubble(grid,105,a0,a1,q,m.hubble,lambda a:1.,nodes=2)
    assert ours.proper_seconds_quadrature==pytest.approx(ref,rel=1e-14)
    assert CR_CLOCK_SOURCE['function'].startswith('proper_dt(')


def test_naive_midpoint_volume_not_exact(grid):
    a0,a1,H=.1,.2,2e-18
    k=float(grid.lookup(105).nominal_m3_s)
    proper=math.log(a1/a0)/H
    midpoint=math.sqrt(a0*a1)
    naive=k*proper/((midpoint/a0)**3)
    exact=k*(1-(a0/a1)**3)/(3*H)
    assert abs(naive-exact)/exact>0.03
    result=clock_from_hubble(grid,105,a0,a1,0.,lambda a,q:H,lambda a:(a/a0)**3,nodes=32)
    assert result.exposure_m3==pytest.approx(exact,rel=2e-14)


def test_clock_bad_inputs_rejected(grid):
    with pytest.raises(ModelContractError):clock_from_hubble(grid,105,.1,.1,0.,lambda a,q:1.,lambda a:1.)
    with pytest.raises(ModelContractError):clock_from_hubble(grid,105,.1,.2,0.,lambda a,q:-1.,lambda a:1.)
    with pytest.raises(ModelContractError):clock_from_hubble(grid,105,.1,.2,0.,lambda a,q:1.,lambda a:0.)
    with pytest.raises(ModelContractError):clock_from_hubble(grid,105,.1,.2,0.,lambda a,q:1.,lambda a:1.,nodes=1)


def test_scipy_piecewise_comoving_ode(grid):
    initial=np.array([1.2e6,2.1e6,1e5,3e5])
    segments=[Segment(105,1.5e9,2e-11),Segment(255,2e9,-1e-11),Segment(505,1e9,0.)]
    result=evolve_source_grid(grid,initial,segments)
    N=initial.copy();v=1.
    for seg in segments:
        k=float(grid.lookup(seg.temperature_K).nominal_m3_s)
        def ode(t,y):
            rate=k*math.exp(-seg.theta_s*t)/v*y[0]*y[1]
            return np.array([-rate,-rate,rate,rate])
        sol=solve_ivp(ode,(0.,seg.duration_s),N,method='DOP853',rtol=2e-12,atol=1e-7)
        assert sol.success
        N=sol.y[:,-1];v*=math.exp(seg.theta_s*seg.duration_s)
    assert np.allclose(N/v,result.final_state_m_minus3,rtol=2e-10,atol=5e-5)


def test_cli_create_only(grid,tmp_path):
    schedule=tmp_path/'schedule.json';schedule.write_text(json.dumps({
        'schema':'wu.r20.schedule.v1','segments':[{'temperature_K':105,'duration_s':1e10,'theta_s':0.}]}))
    target=tmp_path/'output.json'
    args=['--source-pdf',str(PDF),'--schedule-json',str(schedule),'--initial-m3','1e6','1e6','0','0','--output',str(target)]
    assert main(args)==0
    assert json.loads(target.read_text())['source']['temperature_nodes_K']==[105]
    assert main(args)==2


def test_bad_cli_schema(tmp_path):
    schedule=tmp_path/'schedule.json';schedule.write_text('{}')
    target=tmp_path/'out.json'
    args=['--source-pdf',str(PDF),'--schedule-json',str(schedule),'--initial-m3','1','1','0','0','--output',str(target)]
    assert main(args)==2
    assert not target.exists()


def test_zero_initial_reactant(grid):
    r=evolve_source_grid(grid,(0,1e6,2,3),[Segment(105,100.)])
    assert r.extent_reference_m_minus3==0
    assert r.final_state_m_minus3==(0,1e6,2,3)


def test_source_metadata_and_units(grid):
    r=evolve_source_grid(grid,(1e6,1e6,0,0),[Segment(105,1e10)])
    j=r.as_json()
    assert j['source']['uncertainty'] is None
    assert j['source']['rates_m3_s_exact'][0]=={'numerator':'23','denominator':'200000000000000000'}
    assert j['admission']['HH_R10']=='OFF'


def test_source_label_constructor_forgery_rejected():
    from src.grid_exposure import GridFlow,LogScaleClock
    with pytest.raises(SourceContractError):
        GridFlow((1.,1.,0.,0.),0.,0.,0.,1.,(),(),(),(),PDF_SHA256)
    with pytest.raises(SourceContractError):
        LogScaleClock(105,1.,1.,1.,16)
