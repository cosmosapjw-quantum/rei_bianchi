from wu088_hh.phys64_campaign import case_specs

def test_smoke_has_low_and_physical_cross_channel_cases():
    specs=case_specs('smoke')
    assert [s['ells'] for s in specs]==[[0,1],[20,21]]

import json
from pathlib import Path
import pytest
from wu088_hh.phys64_campaign import atomic_json,case_key,resumable,sha,preflight

def test_extended_profile_bounded_and_preserves_m():
    specs=case_specs('extended')
    assert len(specs)==18
    assert max(max(s['ells']) for s in specs)==64
    assert all(min(s['ells'])==abs(s['m']) for s in specs)
    assert {s['nodes'] for s in specs}=={128,192,256}

def test_unknown_profile_rejected():
    with pytest.raises(ValueError):case_specs('unknown')

def test_case_key_binds_code_and_configuration():
    s=case_specs('smoke')[0]
    assert case_key(s,'one')!=case_key(s,'two')
    assert case_key(s,'one')!=case_key(dict(s,nodes=256),'one')

def test_resume_requires_both_actual_payload_hashes(tmp_path):
    (tmp_path/'RESULT.json').write_text('{}')
    (tmp_path/'COEFFICIENTS.npz').write_bytes(b'explicit synthetic unit-test payload')
    d={'key':'k','status':'NUMERICAL_CASE_COMPLETE','payloads':{n:sha(tmp_path/n) for n in ('RESULT.json','COEFFICIENTS.npz')}}
    atomic_json(tmp_path/'SUCCESS.json',d)
    assert resumable(tmp_path,'k')
    assert not resumable(tmp_path,'other')
    (tmp_path/'COEFFICIENTS.npz').write_bytes(b'corruption')
    assert not resumable(tmp_path,'k')

def test_resume_rejects_path_escape(tmp_path):
    outside=tmp_path.parent/'outside';outside.write_bytes(b'x')
    atomic_json(tmp_path/'SUCCESS.json',{'key':'k','status':'NUMERICAL_CASE_COMPLETE','payloads':{'../outside':sha(outside),'missing':'0'}})
    assert not resumable(tmp_path,'k')

def test_atomic_json_rejects_nan_without_false_success(tmp_path):
    with pytest.raises(ValueError):atomic_json(tmp_path/'SUCCESS.json',{'result':float('nan')})
    assert not (tmp_path/'SUCCESS.json').exists()

def test_preflight_binds_original_and_all_dependencies():
    d=preflight()
    assert len(d['code_sha256'])==6
    assert len(d['fingerprint'])==64
    assert d['source_sha256'].startswith('f1bd3074')
