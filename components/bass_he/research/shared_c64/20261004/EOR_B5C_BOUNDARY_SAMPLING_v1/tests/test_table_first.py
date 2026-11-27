import json
from pathlib import Path
import pytest
from bass_he_optical_sampling.core import ContractError
from bass_he_optical_sampling.table import build_table,evaluate
ROOT=Path(__file__).resolve().parents[1]

def table():
 return build_table(json.loads((ROOT/'data/OPTICAL_SAMPLES.json').read_text()),json.loads((ROOT/'data/SAMPLING_DIAGNOSTICS.json').read_text()))

@pytest.mark.parametrize('R',[8.,8.5,9.,9.5,10.])
def test_knots_return_direct_values(R):
 t=table();o=evaluate(t,R,allow_midpoint_only=True)
 raw=next(x for x in t['nodes'] if x['R_a0']==R)
 assert o['V_entrance_Eh']==raw['V_entrance_Eh'] and o['A_ta_div_alpha3']==raw['A_ta_div_alpha3']
 assert not o['interpolated'] and o['cross_section'] is None

def test_interior_is_explicit_interpolant():
 out=evaluate(table(),8.125,allow_midpoint_only=True)
 assert out['interpolated'] and out['A_ta_div_alpha3']>0
 assert out['uniform_error_bound'] is None and not out['physical_accuracy_certified']

@pytest.mark.parametrize('R',[7.999,10.001,float('nan'),True])
def test_no_outside_or_invalid_inputs(R):
 with pytest.raises(ContractError):evaluate(table(),R,allow_midpoint_only=True)

def test_requires_explicit_empirical_contract():
 with pytest.raises(ContractError):evaluate(table(),9.125)

def test_production_rejected():
 with pytest.raises(ContractError):evaluate(table(),9.125,allow_midpoint_only=True,production=True)

def test_packet_change_detected():
 t=table();t['nodes'][0]['A_ta_div_alpha3']=0.
 with pytest.raises(ContractError):evaluate(t,8.,allow_midpoint_only=True)

def test_failed_midpoint_not_exported():
 samples=json.loads((ROOT/'data/OPTICAL_SAMPLES.json').read_text());d=json.loads((ROOT/'data/SAMPLING_DIAGNOSTICS.json').read_text())
 d[-1]['log_rate_midpoint_accept']=False
 with pytest.raises(ContractError):build_table(samples,d)
