from pathlib import Path
import importlib.util,json,sys,types,pytest
spec=importlib.util.spec_from_file_location('cloud_cli',Path(__file__).resolve().parents[2]/'scripts/run_cloud_replay.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def test_missing_data_mount_precedes_run_creation(tmp_path,monkeypatch):
    from bass_he.cloud.resources import HostInventory
    monkeypatch.setattr(module,'inventory',lambda path:HostInventory(64,64,128*1024**3,0,False,()))
    out=Path('/srv/bass-he/runs/test-missing-mount')
    with pytest.raises(RuntimeError,match='BLOCKED_DATA_MOUNT'):module.admit_storage(out,{'storage_mode':'mounted_host','workers':1,'worker_rss_p95_bytes':1024})
    assert not out.exists()
def test_local_sandbox_caps_two(tmp_path):
    cap=module.admit_storage(tmp_path/'run',{'storage_mode':'local_sandbox','workers':32})
    assert cap(42)==2

def test_root_backed_host_is_explicit_mode():
    out=Path('/srv/bass-he/runs/test-root-backed')
    with pytest.raises(RuntimeError,match='BLOCKED_ROOT_STORAGE|BLOCKED_MEMORY_CALIBRATION'):
        module.admit_storage(out,{'storage_mode':'root_backed_host','workers':1})

def test_run_command_reaches_controller_without_local_import_shadow(tmp_path,monkeypatch,capsys):
    class FakeBinding:
        source_commit='test-commit'
    class FakeStore:
        def __init__(self,*args):pass
        def close(self):pass
    class FakeController:
        def __init__(self,*args,**kwargs):pass
        def run(self):return types.SimpleNamespace(status='PASS',stage='closeout',completed=0,failures={},scientific_PROMOTE='HOLD')
    profile=tmp_path/'profile.json'
    profile.write_text(json.dumps({'source_commit':'test-commit','backend':'python','storage_mode':'local_sandbox'}))
    monkeypatch.setattr(module,'binding',lambda root:FakeBinding())
    monkeypatch.setattr(module,'ResultStore',FakeStore)
    monkeypatch.setattr(module,'Controller',FakeController)
    monkeypatch.setattr(sys,'argv',['run_cloud_replay.py','run','--profile',str(profile),'--out',str(tmp_path/'run'),'--workers','1'])
    assert module.main()==0
    assert json.loads(capsys.readouterr().out)['status']=='PASS'
