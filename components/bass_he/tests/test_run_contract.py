import importlib.util
from pathlib import Path
import pytest


def mod():
    path=Path(__file__).resolve().parents[1]/'scripts'/'run_contract.py'
    assert path.exists(), 'immutable research-run binding missing'
    spec=importlib.util.spec_from_file_location('run_contract',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def test_resume_requires_identical_binding_and_fresh_run_refuses_overwrite(tmp_path):
    m=mod();spec={'source':'abc','stage':'pilot','panels':32}
    m.bind_run(tmp_path,spec,resume=False)
    before=(tmp_path/'RUN_BINDING.json').read_bytes()
    with pytest.raises(FileExistsError):m.bind_run(tmp_path,spec,resume=False)
    m.bind_run(tmp_path,spec,resume=True)
    with pytest.raises(ValueError):m.bind_run(tmp_path,{**spec,'panels':64},resume=True)
    assert (tmp_path/'RUN_BINDING.json').read_bytes()==before


def test_resume_missing_run_refused(tmp_path):
    with pytest.raises(FileNotFoundError):mod().bind_run(tmp_path,{},resume=True)


def test_cached_geometry_snapshot_and_failure_attempts_are_durable(tmp_path):
    m=mod()
    assert hasattr(m,'snapshot_geometry'),'cache-only runs must write geometry evidence'
    rows=[{'branch':'Q12','rho':.3,'status':'SUCCESS','result':{'delta':1.}}]
    m.snapshot_geometry(tmp_path,rows)
    assert (tmp_path/'GEOMETRY_RESULTS.json').exists()
    failure={'branch':'Q12','rho':.4,'status':'FAILED','traceback':'exact failure witness'}
    m.snapshot_geometry(tmp_path,rows+[failure],attempt=failure)
    m.snapshot_geometry(tmp_path,rows)
    import json
    assert len(list((tmp_path/'attempts').glob('*.json')))==1
    assert json.loads(next((tmp_path/'attempts').glob('*.json')).read_text())==failure
