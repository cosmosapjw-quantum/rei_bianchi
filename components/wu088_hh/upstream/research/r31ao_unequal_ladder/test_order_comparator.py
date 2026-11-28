"""Algebra/metadata fixtures only; no HH source arrays or kernels generated."""
import importlib.util
import json
from pathlib import Path
import numpy as np
import pytest

HERE=Path(__file__).resolve().parent
def load(name):
    s=importlib.util.spec_from_file_location(name,HERE/(name+'.py'))
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('compare_order_study');adapter=load('order_metadata_adapter');helper=load('unequal_order_ladder')

def fixture(value):
    a=np.zeros((47,2),np.clongdouble);a[0,0]=value;return a

def test_wide_spectral_norm_keeps_bits_below_binary64():
    delta=np.ldexp(np.longdouble(1),-60);v=np.longdouble(1)+delta
    a=fixture(v);a[1,1]=1
    assert m.wide_norms(a)['spectral_2']==v
    assert m.wide_norms(a.conj().T)['spectral_2']==v
    assert m.wide_norms(a)['max_abs']==v
    with pytest.raises(ValueError):m.wide_norms(a.astype(np.complex128))

def test_complex_correlated_columns_spectral_norm():
    a=fixture(1);a[0,1]=1j
    n=m.wide_norms(a)
    assert n['spectral_2']==np.sqrt(np.longdouble(2))
    assert n['frobenius']==np.sqrt(np.longdouble(2))
    assert n['max_abs']==1

def test_conditional_ladder_and_no_source_mutation():
    # Known scalar Q_n = C/n^2 with imaginary C preserves phase in raw deltas.
    arrays=[fixture(np.clongdouble(2j)/np.longdouble(n)**2) for n in (128,160,192)]
    before=[a.copy() for a in arrays]
    d12,d23,x=m.compare_raw_blocks(*arrays,helper)
    assert x['conditional']['status']=='CONDITIONAL_UNEQUAL_RATIO_ASYMPTOTIC_DIAGNOSTIC'
    assert x['conditional']['p_conditional']==pytest.approx(2,abs=1e-11)
    assert x['conditional']['E192_conditional']==pytest.approx(2/192**2,rel=1e-11)
    assert d12.dtype==d23.dtype==np.dtype(np.clongdouble)
    assert np.all(d12.imag<=0)
    assert all(np.array_equal(a,b) for a,b in zip(arrays,before))
    assert float(x['direction']['alignment'])==pytest.approx(1)
    assert x['conditional']['rigorous'] is False
    assert x['direction']['certification_threshold'] is None

def test_noncontracting_ratio_and_zero_increment_not_certified():
    _,_,x=m.compare_raw_blocks(fixture(0),fixture(1),fixture(2),helper)
    assert x['conditional']['status']=='POSITIVE_POWER_MODEL_INCOMPATIBLE_NORMWISE'
    _,_,x=m.compare_raw_blocks(fixture(1),fixture(1),fixture(1),helper)
    assert x['conditional']['status']=='INCREMENT_RATIO_UNDEFINED'
    assert x['conditional']['rigorous'] is False

def test_opposite_error_direction_has_no_positive_fit():
    x=m.direction_diagnostics(fixture(1j),fixture(-1j))
    assert float(x['alignment'])==pytest.approx(-1)
    assert x['best_positive_scalar_fit'] is None

def test_metadata_decimal_geometry_and_source_order_drift():
    contract={'orders':{'128':{'OD_identity':{'driver_sha256':'a','t_sha256':'b'},'JVP_identity':{'driver':'c','grid':'d'}}}}
    od={'n':128,'z':0.75,'driver_sha256':'a','t_sha256':'b','W_sha256':'f'*64}
    jvp={'n':128,'z':'0.750','driver':'c','grid':'d'}
    assert adapter.check_identities(json.dumps(od),json.dumps(jvp),128,contract)
    for key,bad in [('n',160),('n',True),('z','0.751'),('driver','bad'),('grid','bad')]:
        copy=dict(jvp);copy[key]=bad
        with pytest.raises(ValueError):adapter.check_identities(json.dumps(od),json.dumps(copy),128,contract)
    with pytest.raises(ValueError):adapter.parse('{"z":0.75,"z":"0.75"}')
    with pytest.raises(ValueError):adapter.parse('{"z":NaN}')

def test_parent_frozen_primary_secondary_rule_and_tradeoff():
    repo=HERE.parents[1]
    primary=m.module(repo/'research/r31ak_eight_node/compare_future_holdout.py','unit_primary')
    secondary=m.module(repo/'research/r31al_z075_gate/compare_secondary_refinement.py','unit_secondary')
    refinement=m.module(repo/'research/r31al_z075_gate/refinement_gain.py','unit_rule')
    truth={k:fixture(0) if k!='D_row' else fixture(0).T for k in m.FIELDS}
    def pred(k):
        z=fixture(0);x=fixture(k).astype(np.complex128)
        return z,z,x,-x.conj().T,x
    result=m.compare_frozen({'R31AK':pred(1),'R31Z':pred(3),'R31AD':pred(2)},truth,primary,secondary,refinement)
    assert result['primary_verdict']=='PARETO_SUPPORTED_AT_SELECTED_HOLDOUT'
    assert result['secondary_verdict']=='REFINED_PARETO_SUPPORTED_AT_Z075'
    assert result['weighted_score_used'] is False
    assert refinement.pareto_verdict((1,3),(2,2),1e-10)=='REFINEMENT_TRADEOFF_UNRESOLVED'
