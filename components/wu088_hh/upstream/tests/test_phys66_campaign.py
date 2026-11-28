from pathlib import Path
import json
import pytest
from wu088_hh.phys66_campaign import (case_specs,case_key,resumable,sha,atomic_json,preflight,main)
ROOT=Path(__file__).resolve().parents[1]

def test_profiles_only_new_work():
    a=case_specs('longtail');assert len(a)==6
    assert sorted({s['outer'] for s in a})==[55.,65.,75.]
    assert sorted({max(s['ells']) for s in a})==[28,64]
    assert all(s['join']==39. and s['orders']==3 for s in a)
    assert len(case_specs('smoke'))==2
    with pytest.raises(ValueError):case_specs('extended')

def test_keys_bind_runtime_and_config():
    a=case_specs('smoke')[0]
    assert case_key(a,'A')!=case_key(a,'B')
    assert case_key(a,'A')!=case_key(dict(a,outer=46.),'A')

def test_resume_rejects_missing_and_corrupt_payload(tmp_path):
    key='aa';folder=tmp_path;attempt=folder/'attempt';attempt.mkdir()
    for n in ('RESULT.json','COEFFICIENTS.npz'):(attempt/n).write_bytes(b'manufactured')
    receipt=dict(key=key,status='NUMERICAL_CASE_COMPLETE',exit_code=0,
                 payloads={str(p.relative_to(folder)):sha(p) for p in attempt.iterdir()})
    atomic_json(folder/'SUCCESS.json',receipt)
    assert resumable(folder,key)
    (attempt/'RESULT.json').write_bytes(b'changed')
    assert not resumable(folder,key)

def test_resume_never_accepts_failed_exit(tmp_path):
    atomic_json(tmp_path/'SUCCESS.json',dict(key='a',status='NUMERICAL_CASE_COMPLETE',exit_code=2,payloads={}))
    assert not resumable(tmp_path,'a')

def test_resume_does_not_read_outside_case(tmp_path):
    outside=tmp_path/'outside';outside.write_text('x')
    folder=tmp_path/'case';folder.mkdir()
    atomic_json(folder/'SUCCESS.json',dict(key='k',status='NUMERICAL_CASE_COMPLETE',exit_code=0,
                 payloads={'../outside':sha(outside),'../../other':'0'*64}))
    assert not resumable(folder,'k')

def test_preflight_source_and_upstream_identity():
    p=preflight(ROOT)
    assert len(p['code_sha256'])==8
    assert p['source_sha256'].startswith('f1bd3074')
    assert p['fingerprint']

@pytest.mark.parametrize('args',[['--workers','0'],['--workers','8','--memory-gib','8'],['--timeout','5']])
def test_resource_limits_rejected_before_execution(args):
    with pytest.raises(SystemExit) as e:main(args)
    assert e.value.code==2

def test_json_write_rejects_nan(tmp_path):
    with pytest.raises(ValueError):atomic_json(tmp_path/'bad.json',{'x':float('nan')})
    assert not (tmp_path/'bad.json').exists()
