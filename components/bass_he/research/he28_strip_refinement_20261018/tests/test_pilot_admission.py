"""Execution admission only; fixtures never certify native H/He physics."""
from pathlib import Path
from types import SimpleNamespace
import json
import sys
import threading
import time
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
import he28_run


def fixture(tmp_path, monkeypatch, *, table_nodes=512, result_hash='table-A', table_hash='table-A'):
    pilot = tmp_path/'pilot'; pilot.mkdir()
    identity = {'he28_sources': {'core': 'unchanged'}, 'binary_sha256': 'binary-A',
                'parent_sources': {'owner': 'pinned'}, 'owner_source': 'owner-A',
                'numerical_thread_environment': {'OPENBLAS_NUM_THREADS':'1'},
                'source_table_nodes': 512, 'spec': {'m': 4, 'strips': 2, 'angles': 4, 'q': 0.}, 'n': 16}
    result = {'status': 'SCOPED_NATIVE_COMPLETED', 'source_table_sha256': result_hash,
              'results': {'pilot_accuracy_pass': True}}
    (pilot/'IDENTITY.json').write_text(json.dumps(identity))
    (pilot/'RESULT.json').write_text(json.dumps(result))
    (pilot/'TABLE.json').write_text(json.dumps({'source_table_sha256': table_hash,
                        'diagnostics': {'nodes_per_long_interval': 512, 'spec': identity['spec']}}))
    monkeypatch.setattr(he28_run, 'build_identity', lambda *args: dict(identity))
    dispatched=[]
    def dispatch(*args):
        dispatched.append(args)
        return {'returncode': 0, 'timed_out': False}
    monkeypatch.setattr(he28_run, 'run_process', dispatch)
    args = SimpleNamespace(out=str(tmp_path/'study'), binary='fixture-binary',
        build_receipt='fixture-receipt', stage='study', pilot_result=str(pilot/'RESULT.json'),
        table_nodes=table_nodes, table_mb=2048, table_wall_s=600., case_wall_s=3600.)
    return args, dispatched, identity, pilot


def test_changed_table_resolution_cannot_inherit_pilot(tmp_path, monkeypatch):
    args, dispatched, _, _ = fixture(tmp_path, monkeypatch, table_nodes=256)
    with pytest.raises(ValueError, match='PILOT_TABLE_RESOLUTION_CHANGED'):
        he28_run.campaign(args)
    assert not dispatched


def test_changed_table_digest_cannot_inherit_pilot(tmp_path, monkeypatch):
    args, dispatched, _, _ = fixture(tmp_path, monkeypatch, result_hash='other-table')
    with pytest.raises(ValueError, match='PILOT_TABLE_IDENTITY'):
        he28_run.campaign(args)
    assert not dispatched


def test_matched_pilot_dispatches_only_six_declared_cases(tmp_path, monkeypatch):
    args, dispatched, _, _ = fixture(tmp_path, monkeypatch)
    he28_run.campaign(args)
    assert len(dispatched) == 6
    for command, _, _ in dispatched:
        assert command[command.index('--table-nodes')+1] == '512'


def test_study_parallelism_is_bounded_and_runs_only_declared_cases(tmp_path,monkeypatch):
    args,dispatched,_,_=fixture(tmp_path,monkeypatch)
    args.workers=3
    lock=threading.Lock();active=peak=0
    def dispatch(*call):
        nonlocal active,peak
        with lock:
            active+=1;peak=max(peak,active);dispatched.append(call)
        time.sleep(.02)
        with lock:active-=1
        return {'returncode':0,'timed_out':False}
    monkeypatch.setattr(he28_run,'run_process',dispatch)
    he28_run.campaign(args)
    assert len(dispatched)==6
    assert 1<peak<=3


@pytest.mark.parametrize('workers',[0,7,True])
def test_study_parallelism_rejects_invalid_worker_count(tmp_path,monkeypatch,workers):
    args,dispatched,_,_=fixture(tmp_path,monkeypatch)
    args.workers=workers
    with pytest.raises(ValueError,match='STUDY_WORKER_DOMAIN'):
        he28_run.campaign(args)
    assert not dispatched


@pytest.mark.parametrize('mutation,code', [
    ('missing_table','PILOT_TABLE_MISSING'),
    ('bad_table_nodes','PILOT_TABLE_IDENTITY'),
    ('wrong_owner','PILOT_SOURCE_CHANGED'),
    ('wrong_pilot_grid','PILOT_DESIGN_CHANGED'),
    ('wrong_thread_environment','PILOT_THREAD_ENVIRONMENT_CHANGED'),
    ('nonboolean_admission','PILOT_NOT_ADMITTED'),
])
def test_incomplete_or_mismatched_pilot_is_not_inherited(tmp_path,monkeypatch,mutation,code):
    args, dispatched, identity, pilot=fixture(tmp_path,monkeypatch)
    if mutation=='missing_table': (pilot/'TABLE.json').unlink()
    elif mutation=='bad_table_nodes':
        t=json.loads((pilot/'TABLE.json').read_text());t['diagnostics']['nodes_per_long_interval']=256
        (pilot/'TABLE.json').write_text(json.dumps(t))
    elif mutation=='nonboolean_admission':
        r=json.loads((pilot/'RESULT.json').read_text());r['results']['pilot_accuracy_pass']=1
        (pilot/'RESULT.json').write_text(json.dumps(r))
    else:
        i=json.loads((pilot/'IDENTITY.json').read_text())
        if mutation=='wrong_owner':i['owner_source']='another-owner'
        elif mutation=='wrong_pilot_grid':i['spec']['strips']=8
        else:i['numerical_thread_environment']={'OPENBLAS_NUM_THREADS':'64'}
        (pilot/'IDENTITY.json').write_text(json.dumps(i))
    with pytest.raises(ValueError,match=code):he28_run.campaign(args)
    assert not dispatched
