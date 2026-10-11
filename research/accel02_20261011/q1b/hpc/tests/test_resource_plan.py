import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from resource_plan import GIB, plan, cgroup_remaining_bytes


def test_ncp_budget_and_conservative_default():
    assert plan(affinity_cpus=64, available_bytes=128 * GIB)['workers'] == 8
    full = plan(affinity_cpus=64, available_bytes=128 * GIB, requested_workers=64)
    assert full['workers'] == 48
    assert full['estimated_memory_gib'] + full['memory_reserve_gib'] <= 128
    assert set(full['thread_environment'].values()) == {'1'}


def test_scheduler_affinity_and_memory_are_limits():
    assert plan(affinity_cpus=6, available_bytes=128 * GIB, requested_workers=32)['workers'] == 4
    assert plan(affinity_cpus=64, available_bytes=19 * GIB, requested_workers=32)['workers'] == 3
    with pytest.raises(ValueError, match='INSUFFICIENT_MEMORY'):
        plan(affinity_cpus=64, available_bytes=16 * GIB)
    with pytest.raises(ValueError, match='INSUFFICIENT_CPU_HEADROOM'):
        plan(affinity_cpus=2, available_bytes=128 * GIB, reserve_cores=2)


@pytest.mark.parametrize('workers', [0, -1, True, 1.5])
def test_invalid_workers(workers):
    with pytest.raises(ValueError):
        plan(affinity_cpus=64, available_bytes=128 * GIB, requested_workers=workers)


def test_nested_cgroup_uses_tightest_ancestor_headroom(tmp_path):
    mount = tmp_path/'cgroup'; leaf = mount/'job'/'step'; leaf.mkdir(parents=True)
    for folder, maximum, current in [(mount, 'max', '0'), (mount/'job', '100', '80'), (leaf, '60', '10')]:
        (folder/'memory.max').write_text(maximum)
        (folder/'memory.current').write_text(current)
    membership = tmp_path/'membership'; membership.write_text('0::/slice/job/step\n')
    mounts = tmp_path/'mountinfo'; mounts.write_text(f'1 0 0:1 /slice {mount} rw - cgroup2 cgroup rw\n')
    assert cgroup_remaining_bytes(membership, mounts) == 20
