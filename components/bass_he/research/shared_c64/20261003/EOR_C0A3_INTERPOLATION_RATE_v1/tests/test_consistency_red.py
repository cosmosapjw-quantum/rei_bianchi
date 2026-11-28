from pathlib import Path
from bass_he_liu import load_dataset, parse_csv, Dataset, ContractError
from bass_he_liu_interp import Interpolator
import pytest
ROOT=Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('initial',['1s','2s'])
def test_actual_linear_total_dominates_supplied_sum_at_all_union_knots(initial):
    d=load_dataset(ROOT/'raw',ROOT/'provenance/INPUT_LOCK.json')
    r=Interpolator(d,method='linear_E').capture_consistency(initial);assert r is not None
    assert r['order_holds_for_declared_interpolant']
    assert r['arithmetic']=='exact_rational_decimal_inputs'
    assert r['physical_certificate'] is False
    assert r['proof_domain'][1]=='196'

def test_different_knots_violate_order_between_common_samples():
    # Same CSV row does not bind the same energy for the 1s partial.
    s='keV/u,tot capture,,1s,,2s,2p,3s,3p,3d\n'
    s+='1,10,1,1,1,0,0,0,0,0\n'
    s+='3,10,2,12,3,0,0,0,0,0\n'
    s+=',,3,1,,,,,,\n'
    d=Dataset([parse_csv('H1s-Capture cross sections.csv',s.encode())])
    r=Interpolator(d,method='linear_E').capture_consistency('1s');assert r is not None
    assert not r['order_holds_for_declared_interpolant']
    assert r['worst_energy']=='2'
    assert r['minimum_margin_fraction']=={'numerator':-2,'denominator':1}

def test_non_linear_order_certificate_is_refused():
    d=load_dataset(ROOT/'raw',ROOT/'provenance/INPUT_LOCK.json')
    with pytest.raises(ContractError):Interpolator(d,method='loglog').capture_consistency('1s')
