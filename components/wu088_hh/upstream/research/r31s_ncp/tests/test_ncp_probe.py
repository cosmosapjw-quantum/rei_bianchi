import importlib.util
from pathlib import Path
import pytest

P = Path(__file__).resolve().parents[1] / 'probe' / 'ncp_probe.py'

def module():
    s = importlib.util.spec_from_file_location('ncp_probe', P)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def test_no_cache_metadata_does_not_invent_physical_topology(tmp_path):
    m = module()
    rows = m.topology(tmp_path, [2, 8])
    assert rows['2']['l3_cpus'] is None
    assert rows['2']['core_id'] is None
    assert rows['8']['numa_nodes'] == []


@pytest.mark.parametrize('s,expected', [('0-3,8,10-11', [0,1,2,3,8,10,11]), ('', [])])
def test_parse_cpulist(s, expected):
    assert module().cpulist(s) == expected


@pytest.mark.parametrize('s', ['cpu0', '3-1', '-1', '2-a'])
def test_parse_invalid_cpulist(s):
    with pytest.raises(ValueError):
        module().cpulist(s)


def test_cgroup_ancestors_and_memory_headroom(tmp_path):
    root = tmp_path/'cg'
    child = root/'job'
    child.mkdir(parents=True)
    (root/'cpu.max').write_text('350000 100000')
    (child/'cpu.max').write_text('max 100000')
    (root/'memory.max').write_text('1000')
    (root/'memory.current').write_text('900')
    (child/'memory.max').write_text('800')
    (child/'memory.current').write_text('200')
    r = module().limits([child, root], mem_available=2000)
    assert r['quota_cpu_equivalents'] == 3.5
    assert r['memory_available_upper_bytes'] == 100


def test_v2_mount_resolution(tmp_path):
    root = tmp_path/'cg'
    (root/'job').mkdir(parents=True)
    mounts = f'1 2 0:1 /tenant {root} rw - cgroup2 cgroup rw\n'
    paths, warnings = module().cgroup_paths(mounts, '0::/tenant/job\n')
    assert paths == [root/'job', root]
    assert not warnings


def test_v1_no_silent_unlimited():
    paths, warnings = module().cgroup_paths('', '2:cpu:/user/job\n')
    assert paths == [] and warnings


def test_sixtyfour_budget_does_not_drop_outer_parallel_candidates():
    configs = module().candidates(64, 144)
    pairs = {(r['processes'], r['kernel_threads']) for r in configs}
    assert {(64,1),(32,2),(16,4),(8,8),(4,16),(2,32),(1,64)} <= pairs
    assert all(r['processes']*r['kernel_threads'] <= 64 for r in configs)
    assert next(r for r in configs if r['processes']==64)['legacy_12_pair_policy_eligible'] is False


def test_legacy_limit_not_silently_changed():
    assert all(r['legacy_12_pair_policy_eligible'] == (r['processes']<=12)
               for r in module().candidates(64, 144))


def test_quota_and_task_budget_limit():
    r = module().candidates(3, 2)
    assert all(x['processes']<=2 and x['processes']*x['kernel_threads']<=3 for x in r)
    assert module().candidates(0, 144)==[]


def test_malformed_discovered_quota_is_not_ignored(tmp_path):
    (tmp_path/'cpu.max').write_text('banana 100000')
    with pytest.raises(ValueError): module().limits([tmp_path], 1000)


def test_create_only_report(tmp_path):
    path = tmp_path/'report.json'
    m = module()
    m.save_report(path, {'a':1})
    with pytest.raises(FileExistsError): m.save_report(path, {'a':2})
    assert '"a": 1' in path.read_text()
