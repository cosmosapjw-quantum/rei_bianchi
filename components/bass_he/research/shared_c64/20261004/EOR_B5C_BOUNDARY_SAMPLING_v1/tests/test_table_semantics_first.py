import json
from pathlib import Path
import pytest
from bass_he_optical_sampling.table import build_table,evaluate,_hash
from bass_he_optical_sampling.core import ContractError
ROOT=Path(__file__).resolve().parents[1]
@pytest.mark.parametrize('mutation',['grid','tail','error','algorithm'])
def test_rehashed_wrong_contract_is_rejected(mutation):
 t=build_table(json.loads((ROOT/'data/OPTICAL_SAMPLES.json').read_text()),json.loads((ROOT/'data/SAMPLING_DIAGNOSTICS.json').read_text()))
 if mutation=='grid':t['nodes'][0]['R_a0']=7.9
 if mutation=='tail':t['tail_model']='minus9R4_as_exact'
 if mutation=='error':t['uniform_error_bound']=0.
 if mutation=='algorithm':t['V_interpolant']='linear'
 t['body_sha256']=_hash({k:v for k,v in t.items() if k!='body_sha256'})
 with pytest.raises(ContractError):evaluate(t,9.,allow_midpoint_only=True)
