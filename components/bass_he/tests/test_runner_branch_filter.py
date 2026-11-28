import importlib.util
from pathlib import Path


def runner():
    path=Path(__file__).resolve().parents[1]/'scripts'/'run_research.py'
    spec=importlib.util.spec_from_file_location('run_research_filter',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m


def test_requested_branches_can_restrict_sensitivity_to_s23_only():
    m=runner()
    assert [b.name for b in m.requested_branches(0.5)] == [b.name for b in m.BRANCHES]
    assert [b.name for b in m.requested_branches(0.5,{'S23'})] == ['S23']
    assert [b.name for b in m.requested_branches(2.0,{'S23'})] == []
