"""Abstract protocol tests only: no remote I/O, no scientific jobs."""
import importlib.util
from pathlib import Path
import random
import sys
import pytest
P=Path(__file__).resolve().parents[1]/'probe'/'credit_model.py'
spec=importlib.util.spec_from_file_location('credit_model',P)
model=importlib.util.module_from_spec(spec);sys.modules[spec.name]=model;spec.loader.exec_module(model)


def test_inflight_reserves_budget_not_just_finished_results():
    q=model.CreditLedger(2)
    q.reserve('a');q.reserve('b')
    with pytest.raises(RuntimeError,match='capacity'):q.reserve('c')
    assert q.outstanding==2


def test_one_provider_never_releases_credit():
    q=model.CreditLedger(1);q.reserve('a');q.local_complete('a','a'*64)
    q.verified_receipt('a','drive','a'*64)
    assert q.outstanding==1
    with pytest.raises(RuntimeError):q.reserve('b')
    q.verified_receipt('a','dropbox','a'*64)
    assert q.outstanding==0
    q.reserve('b')


def test_failure_retains_reserved_capacity():
    q=model.CreditLedger(1);q.reserve('a');q.fail('a')
    assert q.outstanding==1
    with pytest.raises(RuntimeError):q.reserve('b')


def test_receipt_sha_mismatch_does_not_release():
    q=model.CreditLedger(1);q.reserve('a');q.local_complete('a','a'*64)
    with pytest.raises(ValueError,match='identity'):q.verified_receipt('a','drive','b'*64)
    assert q.outstanding==1


def test_duplicate_job_or_unknown_provider_refused():
    q=model.CreditLedger(2);q.reserve('a')
    with pytest.raises(ValueError):q.reserve('a')
    q.local_complete('a','a'*64)
    with pytest.raises(ValueError):q.verified_receipt('a','somewhere','a'*64)


def test_duplicate_matching_receipt_idempotent():
    q=model.CreditLedger(1);q.reserve('a');q.local_complete('a','a'*64)
    for _ in range(3):q.verified_receipt('a','drive','a'*64)
    q.verified_receipt('a','dropbox','a'*64)
    q.verified_receipt('a','dropbox','a'*64)
    assert q.outstanding==0


def test_randomized_transition_bound():
    q=model.CreditLedger(8);rnd=random.Random(42)
    pending=[];created=0
    for _ in range(500):
        if q.outstanding<q.capacity and rnd.random()<.5:
            key=str(created);created+=1;q.reserve(key);q.local_complete(key,'a'*64);pending.append(key)
        elif pending:
            key=rnd.choice(pending);q.verified_receipt(key,rnd.choice(['drive','dropbox']),'a'*64)
            if q.states[key]=='ACKED':pending.remove(key)
        assert 0<=q.outstanding<=8
    assert created>8


def test_no_receipt_before_local_commit():
    q=model.CreditLedger(1);q.reserve('a')
    with pytest.raises(RuntimeError):q.verified_receipt('a','drive','a'*64)
