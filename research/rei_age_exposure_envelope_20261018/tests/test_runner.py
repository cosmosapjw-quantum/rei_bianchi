"""Orchestration checks use local fixture executables, never native-physics PASS."""
import json,sys,time
from pathlib import Path
import pytest
import run_refinement as r

def test_plan_separates_age_time_and_spectral_axes():
    cases=r.plan()
    assert set(cases)=={'age64','time8','time16','time32','spectral128'}
    assert cases['age64']['birth_panels']==64
    for k in ('time8','time16','time32'):
        assert cases[k]['birth_panels']==32
        assert cases[k]['transport_cells']==16
        assert cases[k]['common_birth_levels']==[8,16,32,64]
    assert cases['spectral128']['q']==.1
    assert cases['spectral128']['birth_panels']==8
    assert cases['spectral128']['transport_cells']==128

def test_native_argv_contains_shared_levels_and_factor():
    c={'name':'test','kind':'native','q':0.,'birth_panels':64,'n_mu':8,
       'source_subdivisions':8,'transport_cells':16,'common_birth_levels':[8,16,32,64],
       'time_factor':16}
    v=r.command(c,Path('/bin/native'),Path('/solver.py'),Path('/out'),30.,1000)
    assert len(v)>=2
    assert v[1]=='native_refine' and v[-2:]==['8,16,32,64','16']

def test_time_budget_terminates_a_real_child(tmp_path):
    result=r.run_process([sys.executable,'-c','import time; time.sleep(10)'],tmp_path, .10)
    assert result['exit_code']==124
    assert result['timed_out'] is True
    assert result['wall_s']<5

def test_child_failure_remains_failure(tmp_path):
    result=r.run_process([sys.executable,'-c','raise SystemExit(7)'],tmp_path,3)
    assert result['exit_code']==7

def test_changed_output_invalidates_reuse(tmp_path):
    p=tmp_path/'endpoint.json';p.write_text('{"N":1}')
    receipt={'status':'COMPLETE','fingerprint':'abc','outputs':{'endpoint.json':r.sha(p)}}
    assert r.reusable(receipt,'abc',tmp_path)
    p.write_text('{"N":2}')
    assert not r.reusable(receipt,'abc',tmp_path)

def test_failed_receipt_cannot_be_reused(tmp_path):
    assert not r.reusable({'status':'FAILED','fingerprint':'x','outputs':{}},'x',tmp_path)

def test_wrong_config_not_reused(tmp_path):
    assert not r.reusable({'status':'COMPLETE','fingerprint':'old','outputs':{}},'new',tmp_path)

def test_json_nan_is_rejected(tmp_path):
    p=tmp_path/'nan.json';p.write_text('{"N":NaN}')
    with pytest.raises(ValueError): r.read_json(p)

def test_failed_parent_does_not_leave_its_server_running(tmp_path):
    import os,signal
    pidfile=tmp_path/'server.pid'
    code="import subprocess,sys; p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(10)']); open(sys.argv[1],'w').write(str(p.pid)); raise SystemExit(7)"
    result=r.run_process([sys.executable,'-c',code,str(pidfile)],tmp_path/'run',3)
    pid=int(pidfile.read_text())
    def running():
        status=Path(f'/proc/{pid}/stat')
        return status.exists() and status.read_text().split()[2]!='Z'
    try:
        until=time.monotonic()+1
        while running() and time.monotonic()<until:time.sleep(.02)
        assert result['exit_code']==7 and not running()
    finally:
        if running():os.kill(pid,signal.SIGKILL)
